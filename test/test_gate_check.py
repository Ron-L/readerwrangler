# Tests for the pre-build gate (.claude/hooks/gate-check.py) — which edits it stops, in the main folder AND in a working
# copy (tools/copies.py: a git worktree in another folder).
# tags: gate, tooling, copies, tier 1
# covers: .claude/hooks/gate-check.py, git-hooks/shipped_paths.py
# Run: python test/test_gate_check.py
#
# 2026-11-16 (TODO "Faster sprints", item 3): the gate judged every path against the session's own folder
# (CLAUDE_PROJECT_DIR), so an edit to readerwrangler.js in a working copy — outside that folder — counted as "outside
# this repo" and went through unchecked (seen live: an edit in a copy passed while the gate was armed). Now it finds the
# working copy that holds the file and asks THAT copy's shipped-code rule.
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

GATE = os.path.join(ROOT, ".claude", "hooks", "gate-check.py")
SESSION = "gate-test-session"
# git's own variables (GIT_DIR, GIT_INDEX_FILE…) point every git command at THIS repository while the commit hook runs
# (RUN-044) — the throwaway repositories get an environment without them.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(cwd, *args):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, env=CLEAN_ENV,
                       capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def make_repo(tmp):
    """A main folder with the shipped-code rule committed, and a working copy of it (a real git worktree) beside it —
    laid out as tools/copies.py lays them out. Returns (main, copy)."""
    main = os.path.join(tmp, "RW")
    os.makedirs(os.path.join(main, "git-hooks"))
    shutil.copy(os.path.join(ROOT, "git-hooks", "shipped_paths.py"), os.path.join(main, "git-hooks"))
    for name in ("readerwrangler.js", "tools/x.js"):
        os.makedirs(os.path.dirname(os.path.join(main, name)), exist_ok=True)
        open(os.path.join(main, name), "w").write("// x\n")
    git(main, "init", "-q", "-b", "main")
    git(main, "add", "git-hooks/shipped_paths.py", "readerwrangler.js", "tools/x.js")
    git(main, "commit", "-q", "-m", "start")
    copy = os.path.join(tmp, "RW-copies", "one")
    git(main, "worktree", "add", "-q", "-b", "one", copy)
    return main, copy


def ask(path, project_dir, tmp):
    """Run the gate as Claude Code does (the edit as JSON on stdin), ARMED for a session; True = it refused."""
    # the gate's state files go in tmp — TMPDIR too: Python reads it first, and git's shell sets it (the commit hook
    # runs this test there; with only TEMP/TMP set it failed only under the hook)
    env = dict(CLEAN_ENV, CLAUDE_PROJECT_DIR=project_dir, TMPDIR=tmp, TEMP=tmp, TMP=tmp)
    for state in ("pending", "refusing"):
        f = os.path.join(tmp, f"rw-gate-{state}-{SESSION}.flag")
        if os.path.exists(f):
            os.remove(f)
    open(os.path.join(tmp, f"rw-gate-pending-{SESSION}.flag"), "w").close()     # ARMED
    data = {"session_id": SESSION, "tool_name": "Edit", "tool_input": {"file_path": path}}
    r = subprocess.run([sys.executable, GATE], input=json.dumps(data), capture_output=True, text=True, env=env)
    return '"deny"' in r.stdout


def gate_in_a_copy():
    tmp = tempfile.mkdtemp(prefix="rw-gate-test-")
    try:
        main, copy = make_repo(tmp)
        check(ask(os.path.join(main, "readerwrangler.js"), main, tmp), "the main folder's app script: stopped")
        check(ask(os.path.join(copy, "readerwrangler.js"), main, tmp),
              "the SAME script in a working copy (a session started in the main folder): stopped")
        check(ask(os.path.join(copy, "newmodule.js"), main, tmp), "a new script at the copy's root: stopped")
        check(ask(os.path.join(copy, "readerwrangler.js"), copy, tmp), "a session started in the copy itself: stopped")
        check(not ask(os.path.join(copy, "tools", "x.js"), main, tmp), "a tool script in the copy (tools/): not stopped")
        check(not ask(os.path.join(copy, "notes.md"), main, tmp), "a document in the copy: not stopped")
        outside = os.path.join(tmp, "elsewhere", "app.js")
        os.makedirs(os.path.dirname(outside))
        check(not ask(outside, main, tmp), "a script in no RW folder: not stopped")
    finally:
        remove_tree(tmp)
test("GATE-001", "the gate stops the first shipped-code edit in a working copy, judged by the copy's own rule",
     gate_in_a_copy)

done()
