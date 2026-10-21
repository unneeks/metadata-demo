"""Coding tools for the agent: workspace-confined file ops, search, command execution, background processes.

Configuration (env):
  CODER_WORKSPACE   directory the agent works in (default: current directory)
  CODER_READONLY    "1" disables write_file/edit_file/run_command/start_process
  CODER_TIMEOUT     default run_command timeout in seconds (default 120)

File tools are confined to the workspace. run_command/start_process are NOT a sandbox: a denylist blocks
obvious foot-guns, but commands run with your user's permissions. Run in a container for untrusted work.
"""

import atexit
import difflib
import os
import re
import signal
import subprocess
import tempfile
from pathlib import Path

from strands import tool

MAX_OUT = 12000
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
DENY = re.compile(
    r"(\bsudo\b|\bmkfs\b|\bshutdown\b|\breboot\b|\bdd\s+if=|:\(\)\s*\{|rm\s+-[a-z]*r[a-z]*f?[a-z]*\s+(/|~|\$HOME)(\s|$)"
    r"|(curl|wget)[^|;]*\|\s*(ba|z)?sh|>\s*/dev/sd|git\s+push\s+.*--force|git\s+reset\s+--hard\s+origin)"
)

_procs: dict[str, tuple[subprocess.Popen, str]] = {}


def root() -> Path:
    return Path(os.environ.get("CODER_WORKSPACE", ".")).resolve()


def _readonly() -> bool:
    return os.environ.get("CODER_READONLY") == "1"


def _p(path: str) -> Path:
    r = root()
    p = (r / path).resolve()
    if p != r and r not in p.parents:
        raise ValueError(f"{path} is outside the workspace {r}")
    return p


def _guard_write() -> None:
    if _readonly():
        raise PermissionError("workspace is read-only (CODER_READONLY=1)")


def _clip(s: str) -> str:
    return s if len(s) <= MAX_OUT else s[: MAX_OUT // 2] + "\n...[truncated]...\n" + s[-MAX_OUT // 2:]


def _check_cmd(cmd: str) -> None:
    _guard_write()
    if DENY.search(cmd):
        raise PermissionError(f"command blocked by safety denylist: {cmd}")


@tool
def list_files(path: str = ".") -> str:
    """List files under a workspace directory (recursive; skips .git, node_modules, venvs, caches). Max 500."""
    base, r = _p(path), root()
    out = []
    for dp, dns, fns in os.walk(base):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        out += [str((Path(dp) / f).relative_to(r)) for f in sorted(fns)]
        if len(out) >= 500:
            break
    return "\n".join(out[:500]) or "(empty)"


@tool
def read_file(path: str, start_line: int = 1, end_line: int = 0) -> str:
    """Read a text file with line numbers. Use start_line/end_line (1-based, end 0 = to end) for big files."""
    lines = _p(path).read_text(errors="replace").splitlines()
    end = end_line or len(lines)
    body = "\n".join(f"{i}\t{l}" for i, l in enumerate(lines[start_line - 1:end], start_line))
    return _clip(body) or "(empty file)"


@tool
def search(pattern: str, path: str = ".", glob: str = "") -> str:
    """Regex search file contents under a path (like grep -rn). Optional glob such as '*.py'."""
    rx, r, out = re.compile(pattern), root(), []
    for dp, dns, fns in os.walk(_p(path)):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            fp = Path(dp) / f
            if glob and not fp.match(glob):
                continue
            try:
                for n, line in enumerate(fp.read_text().splitlines(), 1):
                    if rx.search(line):
                        out.append(f"{fp.relative_to(r)}:{n}: {line.strip()[:200]}")
            except (UnicodeDecodeError, OSError):
                continue
            if len(out) >= 200:
                return "\n".join(out) + "\n...[200 match limit]"
    return "\n".join(out) or "no matches"


@tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file (parent dirs are created). Prefer edit_file for changes to existing files."""
    _guard_write()
    p = _p(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"wrote {path} ({len(content.splitlines())} lines)"


@tool
def edit_file(path: str, old: str, new: str) -> str:
    """Replace one exact, unique occurrence of `old` with `new`. Returns a diff. Fails if no/multiple matches."""
    _guard_write()
    p = _p(path)
    text = p.read_text()
    n = text.count(old)
    if n != 1:
        return f"error: `old` must match exactly once, found {n}. Re-read the file and include more context."
    updated = text.replace(old, new)
    p.write_text(updated)
    diff = difflib.unified_diff(text.splitlines(), updated.splitlines(), path, path, lineterm="", n=2)
    return _clip("\n".join(diff))


@tool
def run_command(command: str, timeout: int = 0) -> str:
    """Run a shell command in the workspace (tests, linters, builds, git). Returns exit code and output.
    Use start_process for servers or anything that does not exit."""
    _check_cmd(command)
    timeout = timeout or int(os.environ.get("CODER_TIMEOUT", "120"))
    proc = subprocess.Popen(command, shell=True, cwd=root(), text=True, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, _ = proc.communicate()
        return f"error: timed out after {timeout}s (killed)\n{_clip(out or '')}"
    return f"exit={proc.returncode}\n{_clip(out)}"


@tool
def git_diff(staged: bool = False) -> str:
    """Show uncommitted changes in the workspace (git diff, or --staged)."""
    r = subprocess.run(["git", "diff", *(["--staged"] if staged else [])], cwd=root(), capture_output=True, text=True)
    return _clip(r.stdout + r.stderr) or "(no changes)"


@tool
def start_process(name: str, command: str) -> str:
    """Start a long-running process (dev server, watcher) in the background under a name. Read output with
    process_logs and stop it with stop_process."""
    _check_cmd(command)
    if name in _procs and _procs[name][0].poll() is None:
        return f"error: '{name}' is already running"
    log = tempfile.NamedTemporaryFile("w+", prefix=f"coder-{name}-", suffix=".log", delete=False)
    proc = subprocess.Popen(command, shell=True, cwd=root(), stdin=subprocess.DEVNULL, stdout=log,
                            stderr=subprocess.STDOUT, start_new_session=True)
    _procs[name] = (proc, log.name)
    return f"started '{name}' pid={proc.pid}; check with process_logs"


@tool
def process_logs(name: str, tail: int = 60) -> str:
    """Show status and the last `tail` log lines of a background process (use to verify a server is up)."""
    if name not in _procs:
        return f"error: no process '{name}'. Known: {list(_procs) or 'none'}"
    proc, logf = _procs[name]
    rc = proc.poll()
    lines = Path(logf).read_text(errors="replace").splitlines()[-tail:]
    return f"status={'running' if rc is None else f'exited({rc})'}\n" + _clip("\n".join(lines))


@tool
def stop_process(name: str) -> str:
    """Stop a background process started with start_process."""
    if name not in _procs:
        return f"error: no process '{name}'"
    proc, _ = _procs.pop(name)
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
    return f"stopped '{name}'"


@atexit.register
def _cleanup() -> None:
    for proc, _ in _procs.values():
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass


TOOLS = [list_files, read_file, search, write_file, edit_file, run_command, git_diff,
         start_process, process_logs, stop_process]
