"""Workspace-confined coding tools for the local agent."""

import subprocess
from pathlib import Path

from strands import tool

ROOT = Path.cwd().resolve()
AUTO_APPROVE = False


def set_root(path: str, auto_approve: bool = False) -> None:
    global ROOT, AUTO_APPROVE
    ROOT, AUTO_APPROVE = Path(path).resolve(), auto_approve


def _p(path: str) -> Path:
    p = (ROOT / path).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"{path} is outside the workspace {ROOT}")
    return p


def _confirm(what: str) -> None:
    if AUTO_APPROVE:
        return
    if input(f"\n[approve] {what} [y/N] ").strip().lower() != "y":
        raise PermissionError("User declined")


@tool
def list_files(path: str = ".") -> str:
    """List files under a workspace directory (recursive, skips .git/node_modules/venv)."""
    skip = {".git", "node_modules", "venv", ".venv", "__pycache__"}
    out = [str(f.relative_to(ROOT)) for f in sorted(_p(path).rglob("*"))
           if f.is_file() and not skip & set(f.relative_to(ROOT).parts)]
    return "\n".join(out[:500]) or "(empty)"


@tool
def read_file(path: str) -> str:
    """Read a UTF-8 text file from the workspace."""
    return _p(path).read_text()


@tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file in the workspace."""
    p = _p(path)
    _confirm(f"write {len(content)} chars to {path}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {path}"


@tool
def edit_file(path: str, old: str, new: str) -> str:
    """Replace one exact, unique occurrence of `old` with `new` in a file."""
    p = _p(path)
    text = p.read_text()
    if text.count(old) != 1:
        return f"error: `old` must match exactly once (found {text.count(old)})"
    _confirm(f"edit {path}")
    p.write_text(text.replace(old, new))
    return f"edited {path}"


@tool
def run_command(command: str, timeout: int = 60) -> str:
    """Run a shell command in the workspace root and return combined output."""
    _confirm(f"run: {command}")
    try:
        r = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"error: timed out after {timeout}s"
    return f"exit={r.returncode}\n{(r.stdout + r.stderr)[-8000:]}"


TOOLS = [list_files, read_file, write_file, edit_file, run_command]
