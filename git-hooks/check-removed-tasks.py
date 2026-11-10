#!/usr/bin/env python
"""check-removed-tasks.py — a task never leaves TODO.md silently (2026-11-10).

WHY: "Relay Setup's Test connection always checks the production relay" was filed 2026-11-02 15:03 and deleted by
accident 27 minutes later inside a large TODO edit (dedc3ca) — no word in its message, the bug never fixed. Found only
eight days later, by the backlog report's audit of "dropped" tasks. A big hand edit can lose a task; a check can't
miss one.

THE RULE: a commit that removes a task (its ID gone from TODO.md) must show why, one of:
  1. the task had a ✅ (finished — the release sweep removes those);
  2. another task now lists its ID as merged:  <!-- id … ; merged <its id> -->;
  3. the commit message says so:  `done <id>` (finished and shipped without a ✅ — tools/backlog_report.py counts it
     done) or `dropped <id>` (with why). A list works too: `dropped 20261014-1030f, 20261015-0900`.
Squash and merge commits are skipped — every commit on the branch was checked as it was made.

Run from git-hooks/commit-msg (it needs the message), on the STAGED TODO.md against HEAD's. Tested by
test/test_check_removed_tasks.py. What a task is comes from tools/backlog_report.py's parse — one reader.
"""
import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("backlog_report", os.path.join(ROOT, "tools", "backlog_report.py"))
_br = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_br)

SCISSORS = "# ------------------------ >8"   # commit --verbose: the diff below it is not part of the message


def removal_problems(old_text, new_text, message):
    """One line per task that left TODO.md with no reason shown (see the top)."""
    old = {t['id']: t for t in _br.parse(old_text) if t['id']}
    new = _br.parse(new_text)
    still = {t['id'] for t in new if t['id']} | {m for t in new for m in t['merged']}
    said = _br.declared(message)                  # the report reads the same words: one reader
    return [f'  "{t["header"]}"  (id {tid})' for tid, t in old.items()
            if tid not in still and not t['done'] and tid not in said]


def combining(git_dir):
    """A squash (git merge --squash leaves SQUASH_MSG) or a merge (MERGE_HEAD) — skipped: the branch was checked."""
    return any(os.path.exists(os.path.join(git_dir, f)) for f in ("SQUASH_MSG", "MERGE_HEAD"))


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


def main(msg_path):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")   # a hook's output is a pipe: ✅ and … print as ✅
    code, staged = git("diff", "--cached", "--name-only", "--diff-filter=MD")
    if "TODO.md" not in staged.split():
        return 0
    _, git_dir = git("rev-parse", "--git-dir")
    if combining(os.path.join(ROOT, git_dir.strip())):
        return 0
    code, old = git("show", "HEAD:TODO.md")
    if code != 0:
        return 0                                  # no TODO.md before this commit: nothing can be removed
    _, new = git("show", ":TODO.md")              # empty if the file itself is being deleted
    with open(msg_path, encoding="utf-8", errors="replace") as f:
        message = f.read().split(SCISSORS)[0]
    message = "\n".join(ln for ln in message.splitlines() if not ln.startswith("#"))
    problems = removal_problems(old, new, message)
    if problems:
        print("check-removed-tasks: this commit removes TODO tasks without saying why:\n" + "\n".join(problems) +
              "\n  Fix: if it was removed by accident, put it back. Otherwise mark it ✅ first, list it in the task that"
              "\n  absorbed it (<!-- id … ; merged <id> -->), or say in the commit message `done <id>` (finished,"
              "\n  shipped without a ✅) or `dropped <id>` (and why).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
