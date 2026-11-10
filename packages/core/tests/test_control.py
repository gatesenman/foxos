"""人工接管：暂停后智能体写操作被拒绝（PAUSED），读与人类写入不受影响。"""


def test_pause_blocks_agent_writes(fox, ws):
    fox.run("sheets", "create", "p.xlsx", agent="data-agent", check=0)
    code, out, _ = fox.run("control", "pause", "--reason", "我来改", agent="data-agent")
    assert code == 4  # 智能体不能自己发起接管
    fox.run("control", "pause", "--reason", "我来改", agent="human", check=0)
    code, out, _ = fox.run("control", "status", check=0)
    assert out["result"]["paused"] and out["result"]["state"]["reason"] == "我来改"

    code, out, _ = fox.run("sheets", "write", "p.xlsx", "A1=agent", agent="data-agent")
    assert code == 8 and out["error"]["code"] == "PAUSED"
    fox.run("sheets", "read", "p.xlsx", agent="data-agent", check=0)          # 读不受影响
    fox.run("sheets", "write", "p.xlsx", "A1=human", agent="human:desktop", check=0)  # 人可以写
    code, out, _ = fox.run("control", "resume", agent="data-agent")
    assert code == 4
    fox.run("control", "resume", agent="human", check=0)
    fox.run("sheets", "write", "p.xlsx", "A2=agent", agent="data-agent", check=0)

    paused = [e for e in fox.audit() if e.get("error", {}).get("code") == "PAUSED"]
    assert len(paused) == 1 and paused[0]["status"] == "denied"
