"""同一文件单写者锁：冲突时返回 LOCKED，读不受影响，并发写不丢更新。"""

import json
import threading
import time

import openpyxl

from foxos import locks
from foxos.workspace import Workspace


def test_write_rejected_while_another_writer_holds_lock(fox, ws):
    fox.run("sheets", "create", "shared.xlsx", check=0)
    w = Workspace(ws)
    lock = locks.acquire(w, "shared.xlsx", owner="doc-agent")  # 模拟另一个智能体正在写
    try:
        code, out, _ = fox.run("sheets", "write", "shared.xlsx", "A1=from-data-agent", agent="data-agent")
        assert code == 5
        assert out["error"]["code"] == "LOCKED"
        assert out["error"]["details"]["holder"]["owner"] == "doc-agent"
        # 读可以并行
        fox.run("sheets", "read", "shared.xlsx", check=0)
        # 写其他文件不受影响
        fox.run("sheets", "create", "other.xlsx", check=0)
    finally:
        locks.release(lock)
    assert openpyxl.load_workbook(ws / "shared.xlsx").active["A1"].value is None
    denied = [e for e in fox.audit() if e["status"] == "denied"]
    assert len(denied) == 1 and denied[0]["agent"] == "data-agent" and denied[0]["error"]["code"] == "LOCKED"
    # 锁释放后可以写
    fox.run("sheets", "write", "shared.xlsx", "A1=ok", check=0)
    assert not any(w.locks_dir.iterdir())


def test_lock_wait_succeeds_after_release(fox, ws):
    fox.run("sheets", "create", "w.xlsx", check=0)
    w = Workspace(ws)
    lock = locks.acquire(w, "w.xlsx", owner="slow-agent")
    threading.Timer(1.0, locks.release, args=[lock]).start()
    t0 = time.monotonic()
    fox.run("sheets", "write", "w.xlsx", "A1=after-wait", "--lock-wait", "15", check=0)
    assert time.monotonic() - t0 >= 0.9
    assert openpyxl.load_workbook(ws / "w.xlsx").active["A1"].value == "after-wait"


def test_concurrent_writers_do_not_lose_updates(fox, ws):
    fox.run("sheets", "create", "race.xlsx", check=0)
    n = 8
    procs = [fox.popen("sheets", "write", "race.xlsx", f"A{i}=agent-{i}", "--lock-wait", "60", agent=f"agent-{i}")
             for i in range(1, n + 1)]
    results = [p.communicate(timeout=120) for p in procs]
    for p, (out, err) in zip(procs, results):
        assert p.returncode == 0, err
        assert json.loads(out)["ok"]
    sh = openpyxl.load_workbook(ws / "race.xlsx").active
    assert [sh[f"A{i}"].value for i in range(1, n + 1)] == [f"agent-{i}" for i in range(1, n + 1)]
    writes = [e for e in fox.audit() if e["command"] == "sheets.write"]
    assert len(writes) == n and all(e["status"] == "ok" for e in writes)


def test_stale_lock_from_dead_process_is_reclaimed(fox, ws):
    fox.run("sheets", "create", "stale.xlsx", check=0)
    w = Workspace(ws)
    lock = locks._lock_file(w, "stale.xlsx")
    lock.write_text(json.dumps({"path": "stale.xlsx", "owner": "crashed", "pid": 2 ** 22 + 12345, "host": locks._host()}))
    fox.run("sheets", "write", "stale.xlsx", "A1=recovered", check=0)
    assert not lock.exists()
