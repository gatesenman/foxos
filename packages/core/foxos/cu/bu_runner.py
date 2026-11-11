"""在 browser-use 的独立虚拟环境里运行（不导入 foxos）：stdin 一个 JSON 任务，stdout 最后一行一个 JSON 结果。"""

import asyncio
import json
import os
import sys


async def main() -> None:
    req = json.loads(sys.stdin.read())
    from browser_use import Agent, Browser, ChatOpenAI

    key = os.environ.get("FOXOS_MODEL_API_KEY")
    llm = ChatOpenAI(model=req["model"], base_url=req["base_url"], api_key=key)
    browser = Browser(cdp_url=req["cdp_url"], keep_alive=True)
    kw = {}
    try:
        import inspect
        if "use_vision" in inspect.signature(Agent.__init__).parameters:
            kw["use_vision"] = bool(req.get("vision"))
    except (TypeError, ValueError):
        pass
    agent = Agent(task=req["task"], llm=llm, browser=browser, **kw)
    hist = await agent.run(max_steps=int(req.get("max_steps") or 25))
    res = {"status": "done" if hist.is_done() else "max_steps", "success": bool(hist.is_successful()), "answer": hist.final_result(),
           "steps": len(hist.history) if hasattr(hist, "history") else None,
           "urls": [u for u in (hist.urls() if hasattr(hist, "urls") else []) if u][-5:],
           "errors": [str(e)[:300] for e in (hist.errors() if hasattr(hist, "errors") else []) if e][-3:]}
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
