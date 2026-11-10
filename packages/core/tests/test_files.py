"""文件命令：列目录、读写文本（乐观并发）、新建、重命名、删除到回收站与恢复。全部受工作空间约束并审计。"""

import subprocess
import sys

from conftest import _env


def test_list_write_read_rename_delete_restore(fox, ws):
    fox.run("files", "mkdir", "notes", check=0)
    code, out, _ = fox.run("files", "write", "notes/todo.md", "--content", "# 待办\n- 写报告\n", agent="doc-agent", check=0)
    mtime = out["result"]["modified"]
    assert (ws / "notes" / "todo.md").read_text(encoding="utf-8") == "# 待办\n- 写报告\n"

    code, out, _ = fox.run("files", "list", check=0)
    assert [(e["name"], e["type"]) for e in out["result"]["entries"]] == [("notes", "dir")]
    code, out, _ = fox.run("files", "list", "notes", check=0)
    assert out["result"]["entries"][0]["path"] == "notes/todo.md"
    code, out, _ = fox.run("files", "read", "notes/todo.md", check=0)
    assert out["result"]["content"].startswith("# 待办")

    # 乐观并发：别人改过之后，带旧 mtime 的保存被拒绝
    fox.run("files", "write", "notes/todo.md", "--content", "agent edit\n", agent="data-agent", check=0)
    code, out, _ = fox.run("files", "write", "notes/todo.md", "--content", "stale\n", "--expect-mtime", str(mtime))
    assert code == 7 and out["error"]["code"] == "CONFLICT"
    assert (ws / "notes" / "todo.md").read_text(encoding="utf-8") == "agent edit\n"

    fox.run("files", "rename", "notes/todo.md", "notes/done.md", check=0)
    assert (ws / "notes" / "done.md").exists() and not (ws / "notes" / "todo.md").exists()
    code, out, _ = fox.run("files", "delete", "notes", check=0)
    tid = out["result"]["trash_id"]
    assert not (ws / "notes").exists()
    code, out, _ = fox.run("files", "trash", check=0)
    assert out["result"]["items"][0]["path"] == "notes"
    fox.run("files", "restore", tid, check=0)
    assert (ws / "notes" / "done.md").read_text(encoding="utf-8") == "agent edit\n"

    cmds = [(e["command"], e["status"]) for e in fox.audit()]
    assert ("files.delete", "ok") in cmds and ("files.write", "error") in cmds


def test_stdin_content_and_limits(fox, ws, core_env):
    big = "第一行\n" + "x" * 200000 + "\n"
    p = subprocess.run([sys.executable, "-m", "foxos", "-w", str(ws), "files", "write", "big.txt", "--content-stdin", "--json"],
                       input=big.encode("utf-8"), capture_output=True, env=_env())
    assert p.returncode == 0, p.stderr
    assert (ws / "big.txt").read_text(encoding="utf-8") == big
    (ws / "bin.dat").write_bytes(b"\x00\x01\x02")
    code, out, _ = fox.run("files", "read", "bin.dat")
    assert code == 2
    code, out, _ = fox.run("files", "delete", "../x")
    assert code == 4
    code, out, _ = fox.run("files", "rename", "big.txt", "../stolen.txt")
    assert code == 4 and (ws / "big.txt").exists()
    code, out, _ = fox.run("files", "restore", "../../etc")
    assert code == 3
    code, out, _ = fox.run("files", "read", ".foxos/audit.jsonl")
    assert code == 4
