#!/usr/bin/env python3
"""生成电脑操控模型目录 packages/core/foxos/data/cu-models.json。

从 Hugging Face API 读取每个 GGUF 文件的大小与 sha256（LFS oid），并检查 ModelScope 上是否有同名镜像仓库。
目录只收 UI-TARS-1.5-7B（可选的本机视觉定位模型），见 docs/computer-use-research.md。
用法：python scripts/gen_model_catalog.py [--offline]（--offline 只校验现有文件格式）
"""
import json
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "packages/core/foxos/data/cu-models.json"

# 只有一个可选的本机视觉模型（2026-11 Sarah 定：少而精）。默认不安装；`foxos model install ui-tars-1.5-7b` 一键装。
# id, 标题, 原始仓库, 许可, GGUF 仓库, 模型文件, mmproj 文件, 坐标格式, 基准, 参数量(B), 备注
MODELS = [
    ("ui-tars-1.5-7b", "UI-TARS-1.5-7B (ByteDance Seed)", "ByteDance-Seed/UI-TARS-1.5-7B", "Apache-2.0",
     "Mungert/UI-TARS-1.5-7B-GGUF", "UI-TARS-1.5-7B-q4_k_m.gguf", "UI-TARS-1.5-7B-q8_0.mmproj",
     "ui-tars", {"screenspot_pro": 49.6, "osworld": 27.4}, 7,
     "optional local vision grounding for apps without accessibility; ByteDance card (Holo2 card measures ScreenSpot-Pro 39.0)"),
]
DECISION: list = []


def hf_tree(repo: str) -> dict:
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/tree/main", timeout=60) as r:
        return {f["path"]: f for f in json.load(r)}


def ms_has(repo: str) -> bool:
    try:
        with urllib.request.urlopen(f"https://modelscope.cn/api/v1/models/{repo}/repo/files?Revision=master", timeout=30) as r:
            return json.load(r).get("Code") == 200
    except Exception:  # noqa: BLE001
        return False


def main() -> int:
    if "--offline" in sys.argv:
        d = json.loads(OUT.read_text())
        assert [m["id"] for m in d["models"]] == ["ui-tars-1.5-7b"] and all(f["sha256"] for m in d["models"] for f in m["files"])
        print("ok", OUT)
        return 0
    out = []
    for rank, (mid, title, src, lic, repo, mfile, proj, coords, bench, params, note) in enumerate(MODELS + DECISION, 1):
        kind = "grounding" if rank <= len(MODELS) else "decision"
        tree = hf_tree(repo)
        files = []
        for role, name in (("model", mfile), ("mmproj", proj)):
            if not name:
                continue
            f = tree[name]
            files.append({"role": role, "name": name, "size": f["size"], "sha256": f["lfs"]["oid"]})
        ms = ms_has(repo)
        out.append({"id": mid, "kind": kind, "rank": rank if kind == "grounding" else None, "title": title, "source_repo": src, "license": lic, "gguf_repo": repo,
                    "modelscope": repo if ms else None, "files": files, "coords": coords, "benchmarks": bench,
                    "params_b": params, "quant": "Q4_K_M", "note": note,
                    "ram_gb": round(sum(f["size"] for f in files) / 1e9 * 1.3 + 1.0, 1),
                    "vram_gb_vllm_bf16": round(params * 2.4 + 2, 1)})
        print(mid, sum(f["size"] for f in files) // 1_000_000, "MB", "modelscope" if ms else "")
    doc = {"generated": "2026-11-12", "policy": "one optional local vision model; default stack is agent-desktop + Jev (DeepSeek fallback)",
           "jev": "TypeSafe Jev is a hosted System One API (no open weights): `foxos model provider add typesafe --key-stdin`",
           "llama_cpp": {"tag": "b12284", "license": "MIT", "assets": {
               "cpu-x64": ["llama-b12284-bin-ubuntu-x64.tar.gz", "50b5f85d45f8ddc7179d1b9b65de6534fbb18dc075942413238cb3471570123f"],
               "vulkan-x64": ["llama-b12284-bin-ubuntu-vulkan-x64.tar.gz", "94bfdf9ad9ab4e5544acc71d8699942fe8013b6c3b39f24570262782619de707"],
               "cuda-x64": ["llama-b12284-bin-ubuntu-cuda-13.5-x64.tar.gz", "d6ede56000c0da12e040334ea7532680d8a11a82cce2ee137c704d066cdbe80c"],
               "cpu-arm64": ["llama-b12284-bin-ubuntu-arm64.tar.gz", "88cd4ac318056bcbcc05d92613481c303eecb03b6ded77367cbd5711aaba4435"]}},
           "models": out}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
