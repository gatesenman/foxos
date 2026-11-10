"""统一错误与退出码。

退出码约定（CLI 与工具接口共用，错误 code 字符串同样出现在 --json 输出与 MCP 结果里）：

  0  OK                  成功
  1  ERROR               未分类错误 / 内部错误
  2  USAGE               参数错误（缺参数、类型不对、取值不在枚举内）
  3  NOT_FOUND           文件、工作表、命令不存在
  4  PERMISSION_DENIED   路径越出工作空间、访问保留目录
  5  LOCKED              目标文件正被其他写入者锁定
  6  DEPENDENCY_MISSING  缺少外部依赖（如 LibreOffice）
  7  CONFLICT            目标已存在且未指定 --force 等冲突
  8  PAUSED              人工接管中：智能体的写操作被暂停
"""

from __future__ import annotations

EXIT_CODES = {
    "OK": 0,
    "ERROR": 1,
    "USAGE": 2,
    "NOT_FOUND": 3,
    "PERMISSION_DENIED": 4,
    "LOCKED": 5,
    "DEPENDENCY_MISSING": 6,
    "CONFLICT": 7,
    "PAUSED": 8,
}

EXIT_CODE_DOCS = {
    0: "OK：成功",
    1: "ERROR：未分类错误或内部错误",
    2: "USAGE：参数错误",
    3: "NOT_FOUND：文件、工作表或命令不存在",
    4: "PERMISSION_DENIED：路径越出工作空间或访问保留目录",
    5: "LOCKED：目标文件正被其他写入者锁定",
    6: "DEPENDENCY_MISSING：缺少外部依赖（如 LibreOffice）",
    7: "CONFLICT：目标已存在等冲突（可用 --force 覆盖时会提示）",
    8: "PAUSED：人工接管中，智能体的写操作被暂停",
}


class FoxError(Exception):
    """所有可预期错误。code 是稳定的机器可读字符串。"""

    def __init__(self, code: str, message: str, *, hint: str | None = None, details: dict | None = None):
        if code not in EXIT_CODES:
            code = "ERROR"
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.details = details or {}

    @property
    def exit_code(self) -> int:
        return EXIT_CODES[self.code]

    def to_dict(self) -> dict:
        d = {"code": self.code, "exit_code": self.exit_code, "message": self.message}
        if self.hint:
            d["hint"] = self.hint
        if self.details:
            d["details"] = self.details
        return d
