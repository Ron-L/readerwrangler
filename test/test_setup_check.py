# Tests for tools/setup_check.py and the session-start hook .claude/hooks/setup-check.py — a copy of the project that
# isn't set up for the commit checks says so, loudly (TODO "Working-process safety net", item 1; sprint 9).
# tags: tooling, copies, tier 1
# covers: tools/setup_check.py, .claude/hooks/setup-check.py, .claude/settings.json
# Run: python test/test_setup_check.py
#
# The commit checks (git-hooks/) run only when git's local setting core.hooksPath says "git-hooks" — a setting a clone
# never brings. A copy without it commits with no checks at all, silently. serve.py (every contributor runs it) and
# Claude's session start now print a warning that can't be missed, with the one command that fixes it.
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile

# NEVER inherit git's own variables (2026-11-18, sprint 9 — a real incident): while the commit hook runs this test,
# GIT_DIR / GIT_INDEX_FILE point at the REAL repository's git folder. The first version of this file ran `git init` in a
# temporary folder with them inherited — git re-initialised the real git folder and wrote core.bare = true into the
# shared config, breaking every working copy. So they're removed from this process before anything else, and where a
# test needs them present (to prove the check ignores them) they point at a DECOY temporary repository made here.
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import setup_check   # noqa: E402

HOOK = os.path.join(ROOT, ".claude", "hooks", "setup-check.py")
FIX = "git config core.hooksPath git-hooks"
CLEAN_ENV = dict(os.environ)          # no GIT_* (removed above)


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True, env=CLEAN_ENV)


def new_repo(tmp, hooks_path=None, name="copy"):
    repo = os.path.join(tmp, name)
    os.makedirs(repo)
    git(repo, "init", "-q")
    if hooks_path is not None:
        git(repo, "config", "core.hooksPath", hooks_path)
    return repo


def decoy(tmp):
    """A temporary repository that IS set up, and git's variables as a commit hook would set them for it — so a check
    that wrongly followed GIT_DIR would answer "set up" for the decoy instead of the repository asked about. Also the
    hash of its config, to show nothing wrote there."""
    repo = new_repo(tmp, "git-hooks", name="decoy")
    git_dir = os.path.join(repo, ".git")
    return {"GIT_DIR": git_dir, "GIT_INDEX_FILE": os.path.join(git_dir, "index")}, config_hash(git_dir)


def config_hash(git_dir):
    with open(os.path.join(git_dir, "config"), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@contextlib.contextmanager
def environ_with(extra):
    os.environ.update(extra)
    try:
        yield
    finally:
        for k in extra:
            os.environ.pop(k, None)


def problem_found():
    with tempfile.TemporaryDirectory(prefix="rw-setup-") as tmp:
        repo = new_repo(tmp)
        p = setup_check.hooks_path_problem(repo)
        check(p and "isn't set" in p, f"not set: said so ({p!r})")
        decoy_env, before = decoy(tmp)
        with environ_with(decoy_env):                       # as inside a commit hook — pointing at the DECOY
            p = setup_check.hooks_path_problem(repo)
        check(p and "isn't set" in p, f"git's variables (a hook's) are ignored: it answers for the folder asked ({p!r})")
        check(config_hash(decoy_env["GIT_DIR"]) == before, "and nothing wrote to the repository they point at")
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


def run_hook(project_dir, git_env):
    """The hook, as a session would start it — with git's variables pointing at a DECOY temporary repository (never the
    real one), so it's proven to ignore them."""
    env = dict(CLEAN_ENV, CLAUDE_PROJECT_DIR=project_dir, **git_env)
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"session_id": "t", "hook_event_name": "SessionStart"}),
                       capture_output=True, text=True, env=env, timeout=60)
    return r


def hook_warns():
    with tempfile.TemporaryDirectory(prefix="rw-setup-") as tmp:
        repo = new_repo(tmp)
        decoy_env, before = decoy(tmp)
        r = run_hook(repo, decoy_env)
        check(r.returncode == 0, f"the hook never fails the session (exit {r.returncode}, {r.stderr})")
        out = json.loads(r.stdout)
        check(FIX in out.get("systemMessage", ""), f"Ron sees it, with the fix command: {out}")
        ctx = out.get("hookSpecificOutput", {})
        check(ctx.get("hookEventName") == "SessionStart" and FIX in ctx.get("additionalContext", ""),
              f"and Claude is told, to say it to Ron: {ctx}")
        git(repo, "config", "core.hooksPath", "git-hooks")
        r = run_hook(repo, decoy_env)
        check(r.returncode == 0 and r.stdout.strip() == "", f"set up: the hook says nothing ({r.stdout!r})")
        check(config_hash(decoy_env["GIT_DIR"]) == before, "nothing wrote to the repository git's variables point at")
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
