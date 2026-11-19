# Tests for tools/setup_check.py and the session-start hook .claude/hooks/setup-check.py — a copy of the project that
# isn't set up for the commit checks says so, loudly (TODO "Working-process safety net", item 1; sprint 9).
# tags: tooling, copies, tier 1
# covers: tools/setup_check.py, .claude/hooks/setup-check.py, .claude/settings.json
# Run: python test/test_setup_check.py
#
# The commit checks (git-hooks/) run only when git's local setting core.hooksPath says "git-hooks" — a setting a clone
# never brings. A copy without it commits with no checks at all, silently. serve.py (every contributor runs it) and
# Claude's session start now print a warning that can't be missed, with the one command that fixes it.
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import setup_check   # noqa: E402

HOOK = os.path.join(ROOT, ".claude", "hooks", "setup-check.py")
FIX = "git config core.hooksPath git-hooks"
# git's own variables (GIT_DIR, GIT_INDEX_FILE…) point every git command at THIS repository while the commit hook runs
# the test — the throwaway repositories here must not see them (as test/test_copies.py).
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True, env=CLEAN_ENV)


def new_repo(tmp, hooks_path=None):
    repo = os.path.join(tmp, "copy")
    os.makedirs(repo)
    git(repo, "init", "-q")
    if hooks_path is not None:
        git(repo, "config", "core.hooksPath", hooks_path)
    return repo


def problem_found():
    with tempfile.TemporaryDirectory(prefix="rw-setup-") as tmp:
        repo = new_repo(tmp)
        p = setup_check.hooks_path_problem(repo)
        check(p and "isn't set" in p, f"not set: said so ({p!r})")
        git(repo, "config", "core.hooksPath", ".git/hooks")
        p = setup_check.hooks_path_problem(repo)
        check(p and ".git/hooks" in p, f"set to something else: names what it is ({p!r})")
        for ok in ("git-hooks", "./git-hooks", "git-hooks/", "git-hooks\\"):
            git(repo, "config", "core.hooksPath", ok)
            check(setup_check.hooks_path_problem(repo) is None, f"{ok!r} is set up: no problem")
        p = setup_check.hooks_path_problem(os.path.join(tmp, "not-a-repo-at-all"))
        check(p and "git" in p, f"no repository there (or no git): said, never silent ({p!r})")
test("SETUP-001", "core.hooksPath not set, or set to anything but git-hooks, is a problem in words; git-hooks is not",
     problem_found)


def loud_lines():
    lines = setup_check.warning_lines("core.hooksPath isn't set")
    text = "\n".join(lines)
    check(FIX in text, f"the one command that fixes it is in the warning:\n{text}")
    check("OFF" in text and "core.hooksPath isn't set" in text, f"says the checks are OFF and why:\n{text}")
    check(lines[0] == lines[-1] and set(lines[0]) == {"!"} and len(lines[0]) >= 60,
          f"framed by full lines of '!' — can't be missed:\n{text}")
    check(all(ord(c) < 128 for c in text), "plain ASCII (a Windows console garbles a dash or a quote mark)")
test("SETUP-002", "the warning is loud (framed in '!'), says the checks are OFF and why, and gives the fix command",
     loud_lines)


def run_hook(project_dir):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project_dir)   # GIT_* left in on purpose: the check must ignore them
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"session_id": "t", "hook_event_name": "SessionStart"}),
                       capture_output=True, text=True, env=env, timeout=60)
    return r


def hook_warns():
    with tempfile.TemporaryDirectory(prefix="rw-setup-") as tmp:
        repo = new_repo(tmp)
        r = run_hook(repo)
        check(r.returncode == 0, f"the hook never fails the session (exit {r.returncode}, {r.stderr})")
        out = json.loads(r.stdout)
        check(FIX in out.get("systemMessage", ""), f"Ron sees it, with the fix command: {out}")
        ctx = out.get("hookSpecificOutput", {})
        check(ctx.get("hookEventName") == "SessionStart" and FIX in ctx.get("additionalContext", ""),
              f"and Claude is told, to say it to Ron: {ctx}")
        git(repo, "config", "core.hooksPath", "git-hooks")
        r = run_hook(repo)
        check(r.returncode == 0 and r.stdout.strip() == "", f"set up: the hook says nothing ({r.stdout!r})")
test("SETUP-003", "the session-start hook: not set up → a message Ron sees and Claude is told (with the fix); set up → "
     "silent", hook_warns)


def wired():
    s = json.load(open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8"))
    cmds = [h.get("command", "") for e in s["hooks"].get("SessionStart", []) for h in e.get("hooks", [])]
    check(any("setup-check.py" in c and "$CLAUDE_PROJECT_DIR" in c for c in cmds),
          f"settings.json runs .claude/hooks/setup-check.py at session start: {cmds}")
    check(any("gate-reset.py" in c for c in cmds), "beside gate-reset.py (still there)")
test("SETUP-004", "settings.json wires setup-check.py at SessionStart, beside gate-reset.py", wired)

done()
