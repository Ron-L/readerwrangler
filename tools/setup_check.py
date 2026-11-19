"""
setup_check.py — is this copy of the project set up for the commit checks? (TODO "Working-process safety net", item 1;
decided Ron + UX 2026-10-22, built sprint 9, 2026-11-18.)

The commit checks (git-hooks/) run only when git's LOCAL setting core.hooksPath says "git-hooks" — a setting a clone never
brings (the hooks travel with the repo; turning them on doesn't). A copy without it commits with no checks at all, and
nothing says so. So two places everyone passes through check it and warn LOUDLY, with the one command that fixes it:
  1. serve.py's start-up — every contributor runs it to test locally (Ron at logon), Claude Code or not;
  2. Claude's session start (.claude/hooks/setup-check.py).
A working copy (tools/copies.py — a git worktree) shares the main folder's setting, so it's covered when the main is.

hooks_path_problem(root) is the one rule; warning_lines(problem) the one wording. Tested by test/test_setup_check.py
(SETUP-001–004) and test/test_serve.py (SERVE-002).
"""
import os
import posixpath
import subprocess
import sys

FIX = "git config core.hooksPath git-hooks"
WIDTH = 100


def hooks_path_problem(root):
    """None when `root`'s copy runs the commit checks; otherwise what's wrong, in words."""
    # git's own variables (GIT_DIR…, set while a git hook runs) would answer for THAT repository, not root's
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=root, capture_output=True, text=True,
                           timeout=10, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"couldn't ask git whether they're on ({e})"
    value = r.stdout.strip()
    if r.returncode == 1 or not value:
        return "git's setting core.hooksPath isn't set"
    if r.returncode != 0:
        return f"couldn't ask git whether they're on ({r.stderr.strip() or 'exit ' + str(r.returncode)})"
    if posixpath.normpath(value.replace("\\", "/")) == "git-hooks":
        return None
    return f"git's setting core.hooksPath is \"{value}\", not \"git-hooks\""


def warning_lines(problem):
    """The warning: framed in full lines of '!', plain ASCII (a Windows console garbles a dash)."""
    bar = "!" * WIDTH
    return [bar,
            "!!  WARNING: the commit checks are OFF in this copy of ReaderWrangler - every commit skips them.",
            f"!!  Why: {problem}.",
            "!!  Fix it once, in the project folder:",
            f"!!      {FIX}",
            bar]


def red(text):
    """text in red on a console — plain text where the console can't show colors (or isn't a console)."""
    try:
        if not sys.stdout.isatty():
            return text
    except (AttributeError, ValueError):
        return text
    if os.name == "nt":
        try:   # Windows consoles show color codes only once asked to (ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            import ctypes
            k, mode = ctypes.windll.kernel32, ctypes.c_uint32()
            handle = k.GetStdHandle(-11)
            if not (k.GetConsoleMode(handle, ctypes.byref(mode)) and k.SetConsoleMode(handle, mode.value | 0x0004)):
                return text
        except Exception:
            return text
    return f"\033[91m{text}\033[0m"
