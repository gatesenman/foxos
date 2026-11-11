"""工作空间：所有文件操作都被约束在工作空间根目录内。

- 相对路径相对于工作空间根目录解析；绝对路径必须位于根目录之内。
- 先做 realpath（解析 .. 与符号链接）再判断，防止 ../ 和符号链接逃逸。
- `.foxos/` 是保留目录（审计日志、锁、版本记录），智能体命令不能直接读写。

注意：这是应用层约束，不是操作系统级沙箱；详见 docs/architecture.md。
"""

from __future__ import annotations

from foxos.i18n import tr
import os
from pathlib import Path

from .errors import FoxError

RESERVED_DIR = ".foxos"


def default_root() -> Path:
    env = os.environ.get("FOXOS_WORKSPACE")
    if env:
        return Path(env)
    return Path.home() / "FoxOS" / "workspace"


def _norm(p: str) -> str:
    return os.path.normcase(os.path.realpath(p))


class Workspace:
    def __init__(self, root: str | os.PathLike | None = None):
        root_path = Path(root) if root else default_root()
        root_path.mkdir(parents=True, exist_ok=True)
        self.root = Path(os.path.realpath(root_path))
        self.data_dir = self.root / RESERVED_DIR
        for sub in ("", "locks", "versions"):
            (self.data_dir / sub).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def resolve(self, user_path: str) -> Path:
        """把用户/智能体给出的路径解析为工作空间内的绝对路径，越界则拒绝。"""
        if not isinstance(user_path, str) or not user_path.strip():
            raise FoxError("USAGE", tr("workspace.the_path_cannot_be_empty"))
        if "\x00" in user_path:
            raise FoxError("USAGE", tr("workspace.the_path_contains_invalid_characters"))
        candidate = Path(user_path).expanduser()
        if not candidate.is_absolute():
            candidate = self.root / candidate
        real = _norm(str(candidate))
        root = _norm(str(self.root))
        try:
            inside = os.path.commonpath([root, real]) == root
        except ValueError:  # Windows 上不同盘符
            inside = False
        if not inside:
            raise FoxError(
                "PERMISSION_DENIED",
                tr("workspace.path_is_outside_the_workspace", user_path),
                hint=tr("workspace.only_files_inside_workspace_can_be", self.root),
                details={"path": user_path, "workspace": str(self.root)},
            )
        rel_parts = Path(os.path.relpath(real, root)).parts
        if rel_parts and os.path.normcase(rel_parts[0]) == os.path.normcase(RESERVED_DIR):
            raise FoxError(
                "PERMISSION_DENIED",
                tr("workspace.is_reserved_for_foxos_and_cannot_be", RESERVED_DIR, user_path),
                details={"path": user_path},
            )
        return Path(os.path.realpath(candidate))

    def rel(self, path: Path) -> str:
        r = os.path.relpath(os.path.realpath(path), self.root)
        return Path(r).as_posix()

    @property
    def audit_path(self) -> Path:
        return self.data_dir / "audit.jsonl"

    @property
    def locks_dir(self) -> Path:
        return self.data_dir / "locks"

    @property
    def versions_dir(self) -> Path:
        return self.data_dir / "versions"
