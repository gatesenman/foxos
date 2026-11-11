"""模型：三个就够（2026-11 定）——DeepSeek 做规划（System 2）、TypeSafe Jev 做单步快决策（System 1，没有密钥时自动回退
DeepSeek JSON）、UI-TARS-1.5-7B 做可选的本机视觉定位（一键安装，默认不装）。

`foxos model catalog|install|run|stop|status|remove|use` 管本机模型；`foxos model provider list|add|remove|test` 管托管服务的密钥
（存在本地密钥库，不出现在输出和审计里）。
"""

from __future__ import annotations

from .. import secrets
from ..errors import FoxError
from ..i18n import tr
from ..kernel import Command, Context, Param, is_human, register, register_app

PROVIDERS = ("deepseek", "typesafe")


def model_catalog(ctx: Context) -> dict:
    from ..cu import models
    c = models.catalog()
    inst = {m["id"] for m in models.installed()}
    return {"models": [{**m, "installed": m["id"] in inst, "download_gb": round(sum(f["size"] for f in m["files"]) / 1e9, 2)}
                       for m in c["models"]], "runtime": c["llama_cpp"], "hardware": models.hardware()}


def model_install(ctx: Context, model: str, source: str = "auto", force: bool = False) -> dict:
    from ..cu import models
    return models.install(model, source=source, force=force)


def model_run(ctx: Context, model: str, backend: str = "auto", port: int | None = None, ctx_size: int = 8192, threads: int | None = None,
              use: bool = True) -> dict:
    from ..cu import models
    r = models.run(model, backend=backend, port=port, ctx_size=int(ctx_size), threads=threads)
    if use:
        r["registered"] = model_use(ctx, model)["grounding"]
    return r


def model_stop(ctx: Context, model: str) -> dict:
    from ..cu import models
    return models.stop(model)


def model_status(ctx: Context) -> dict:
    from ..cu import models
    return {"installed": models.installed(), "hardware": models.hardware(), "llama_server": str(models.server_bin() or "") or None}


def model_remove(ctx: Context, model: str) -> dict:
    from ..cu import models
    return models.remove(model)


def model_use(ctx: Context, model: str) -> dict:
    """把正在运行的本机模型设为视觉定位（computer model 的 grounding）。"""
    from ..cu import llm, models
    m = models.entry(model)
    st = models.endpoint(model)
    kind = "ui-tars" if m["coords"] in ("ui-tars", "pixel") else "vlm"
    cfg = llm.save({"grounding": {"kind": kind, "base_url": st["base_url"], "model": st["model"]}})
    return {"model": model, "grounding": cfg["grounding"], "message": tr("mdl.used", model, kind)}


def provider_list(ctx: Context) -> dict:
    from ..cu import llm, policy, typesafe
    cfg = llm.load()
    ds = {**llm.PROVIDERS["deepseek"]}
    k_ds = secrets.get(llm.key_name("deepseek")) or None
    k_ts = typesafe.api_key()
    pol = policy.active_policy(cfg).name
    return {"providers": [
        {"id": "deepseek", "role": "planner (System 2) + step-policy fallback", "base_url": ds["base_url"], "models": [ds["model"], "deepseek-flash"],
         "key": f"…{k_ds[-4:]}" if k_ds else None, "configured": bool(k_ds or llm.api_key({**cfg, "provider": "deepseek"}))},
        {"id": "typesafe", "role": "step policy (System 1, Jev)", "base_url": typesafe.BASE, "models": [typesafe.MODEL],
         "key": f"…{k_ts[-4:]}" if k_ts else None, "configured": bool(k_ts), "early_access": True}],
        "active_step_policy": pol}


def provider_add(ctx: Context, provider: str, key: str, base_url: str | None = None, model: str | None = None) -> dict:
    from ..cu import llm, typesafe
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("cu.model_human_only"))
    if provider == "typesafe":
        secrets.put(typesafe.KEY_NAME, key.strip())
        if model or base_url:
            llm.save({"typesafe": {k: v for k, v in (("model", model), ("base_url", base_url)) if v}})
    else:
        secrets.put(llm.key_name(provider), key.strip())
        if base_url or model:
            llm.save({"base_url": base_url, "model": model})
    return {"provider": provider, "key": f"…{key.strip()[-4:]}", "message": tr("mdl.provider_added", provider)}


def provider_remove(ctx: Context, provider: str) -> dict:
    from ..cu import llm, typesafe
    if not is_human(ctx.agent):
        raise FoxError("PERMISSION_DENIED", tr("cu.model_human_only"))
    removed = secrets.delete(typesafe.KEY_NAME if provider == "typesafe" else llm.key_name(provider))
    return {"provider": provider, "removed": removed}


def provider_test(ctx: Context, provider: str) -> dict:
    import time
    from ..cu import llm, typesafe
    t0 = time.time()
    if provider == "typesafe":
        c = typesafe.Client()
        r = c.ask("The user asks to save the open document.", {"intent": typesafe.choice("Which UI action fits?", {
            "save": "Save the document", "close": "Close the window", "print": "Print the document"})})
        a = r["answers"]["intent"]
        return {"provider": provider, "ok": a["choice"] == "save", "choice": a["choice"], "confidence": a.get("confidence"),
                "model": r["model"], "seconds": round(time.time() - t0, 3)}
    cfg = {**llm.load(), "provider": "deepseek", "base_url": llm.PROVIDERS["deepseek"]["base_url"]}
    r = llm.chat([{"role": "user", "content": "Reply with the single word: pong"}], cfg=cfg, model="deepseek-flash",
                 extra={"thinking": {"type": "disabled"}})
    return {"provider": provider, "ok": "pong" in (r["message"].get("content") or "").lower(), "model": r["model"], "seconds": r["seconds"]}


register_app("model", tr("mdl.title"), tr("mdl.summary"))
M = Param("model", "string", tr("mdl.p_model"), required=True, positional=True, metavar="MODEL", enum=["ui-tars-1.5-7b"])
P = Param("provider", "string", tr("mdl.p_provider"), required=True, positional=True, metavar="PROVIDER", enum=list(PROVIDERS))
register(Command("model", "catalog", tr("mdl.c_catalog"), model_catalog, examples=["foxos model catalog --json"], permission="read", audited=False))
register(Command("model", "install", tr("mdl.c_install"), model_install,
                 params=[M, Param("source", "string", tr("mdl.p_source"), enum=["auto", "hf", "hf-mirror", "modelscope"], default="auto"),
                         Param("force", "boolean", tr("mdl.p_force"), default=False)],
                 examples=["foxos model install ui-tars-1.5-7b", "foxos model install ui-tars-1.5-7b --source modelscope"],
                 limits=[tr("mdl.l_install")], permission="run"))
register(Command("model", "run", tr("mdl.c_run"), model_run,
                 params=[M, Param("backend", "string", tr("mdl.p_backend"), enum=["auto", "llama.cpp", "vllm"], default="auto"),
                         Param("port", "integer", tr("mdl.p_port")), Param("ctx_size", "integer", tr("mdl.p_ctx"), default=8192),
                         Param("threads", "integer", tr("mdl.p_threads")), Param("use", "boolean", tr("mdl.p_use"), default=True)],
                 examples=["foxos model run ui-tars-1.5-7b"], limits=[tr("mdl.l_run")], permission="run"))
register(Command("model", "stop", tr("mdl.c_stop"), model_stop, params=[M], examples=["foxos model stop ui-tars-1.5-7b"], permission="run"))
register(Command("model", "status", tr("mdl.c_status"), model_status, examples=["foxos model status --json"], permission="read", audited=False))
register(Command("model", "remove", tr("mdl.c_remove"), model_remove, params=[M], examples=["foxos model remove ui-tars-1.5-7b"],
                 permission="modify"))
register(Command("model", "use", tr("mdl.c_use"), model_use, params=[M], examples=["foxos model use ui-tars-1.5-7b"], permission="modify"))
register(Command("model", "provider list", tr("mdl.c_provider_list"), provider_list, examples=["foxos model provider list --json"],
                 permission="read", audited=False))
register(Command("model", "provider add", tr("mdl.c_provider_add"), provider_add,
                 params=[P, Param("key", "string", tr("mdl.p_key"), required=True, secret=True, cli_stdin=True),
                         Param("base_url", "string", tr("cu.p_base_url")), Param("model", "string", tr("cu.p_model"))],
                 examples=["foxos model provider add typesafe --key-stdin < typesafe.key", "foxos model provider add deepseek --key-stdin < deepseek.key"],
                 limits=[tr("cu.l_human_only")], permission="modify"))
register(Command("model", "provider remove", tr("mdl.c_provider_remove"), provider_remove, params=[P],
                 examples=["foxos model provider remove typesafe"], limits=[tr("cu.l_human_only")], permission="modify"))
register(Command("model", "provider test", tr("mdl.c_provider_test"), provider_test, params=[P],
                 examples=["foxos model provider test deepseek", "foxos model provider test typesafe"], permission="read"))
