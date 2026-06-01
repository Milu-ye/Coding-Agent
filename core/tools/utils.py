import pathlib
from enum import StrEnum

from core.tools.decision import Decision


def safe_path(workdir: pathlib.Path | str,path: str):
    if isinstance(workdir,str):
        workdir = pathlib.Path(workdir)
    path = (workdir / path).resolve()
    if not path.is_relative_to(workdir):
        raise ValueError(f"Path escapes workspace: {path}")
    return path


def ask_user(reason: str) -> Decision:
    print(f"\n[!] {reason}")
    choice = input("   Allow? [Y/N] ").strip().lower()
    return Decision.ALLOW if choice in ("y", "yes") else Decision.DENY