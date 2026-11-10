# Tests for git-hooks/check-removed-tasks.py — a task never leaves TODO.md silently.
# tags: commit-checks, backlog, tier 1
# covers: git-hooks/check-removed-tasks.py, tools/backlog_report.py
# Run: python test/test_check_removed_tasks.py
#
# 2026-11-10 (the backlog report's audit): "Relay Setup's Test connection always checks the production relay" was filed
# 2026-11-02 15:03 and deleted by accident 27 minutes later inside a large TODO edit (dedc3ca), with no word in its
# message — the bug stayed, and the task was gone. The check: a commit that removes a task from TODO.md must show why —
# the task had a ✅, another task lists it as merged, or the message says `done <id>` or `dropped <id>`.
import datetime as dt
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("check_removed", os.path.join(ROOT, "git-hooks", "check-removed-tasks.py"))
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)
spec2 = importlib.util.spec_from_file_location("backlog_report", os.path.join(ROOT, "tools", "backlog_report.py"))
br = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(br)
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402


def todo(*tasks):
    out = ["# TODO", "", "## 🔝 Up next", ""]
    for header, tid, extra in tasks:
        words = " ".join(f"{header.lstrip('✅ ')} line {k} of its own reasons." for k in range(6))
        out += [f"#### {header}", f"<!-- id {tid}{extra} -->", "", f"_Why it matters:_ {words}", ""]
    return "\n".join(out)


A = ("Task A", "20261015-1000", "")
B = ("Task B", "20261015-1100", "")


def refused_silent():
    p = cr.removal_problems(todo(A, B), todo(B), "docs: tidy the TODO")
    check(len(p) == 1 and "Task A" in p[0] and "20261015-1000" in p[0], f"should name Task A and its ID: {p}")
test("RTASK-001", "a task removed with no ✅, no merge and no word in the message is refused (named, with its ID)",
     refused_silent)


def checkmarked_ok():
    p = cr.removal_problems(todo(("✅ Task A", "20261015-1000", ""), B), todo(B), "release prep: remove the ✅ tasks")
    check(not p, f"a ✅ task may be removed (the release sweep): {p}")
test("RTASK-002", "removing a ✅ task (the release sweep) passes", checkmarked_ok)


def merged_ok():
    p = cr.removal_problems(todo(A, B), todo(("Task B", "20261015-1100", "; merged 20261015-1000")), "merge A into B")
    check(not p, f"absorbed into Task B (listed as merged): {p}")
test("RTASK-003", "removing a task another task now lists as merged passes", merged_ok)


def declared_ok():
    for msg in ("docs: dropped 20261015-1000 — covered by Move to → Inbox",
                "docs(TODO): Done 20261015-1000 (shipped in 7.26.0 without a ✅)",
                "docs: dropped 20261014-0900, 20261015-1000 (both superseded)"):
        p = cr.removal_problems(todo(A, B), todo(B), msg)
        check(not p, f"the message declares it ({msg!r}): {p}")
    p = cr.removal_problems(todo(A, B), todo(B), "docs: dropped 20261015-1100")   # declares the WRONG task
    check(p, "declaring a different ID doesn't excuse Task A")
test("RTASK-004", "a message saying `done <id>` or `dropped <id>` (one or a list) excuses exactly those tasks", declared_ok)


def moved_ok():
    p = cr.removal_problems(todo(A, B), todo(B, A), "docs: Task A moves below Task B")
    check(not p, f"a moved task isn't removed: {p}")
test("RTASK-005", "moving a task (same ID elsewhere in the file) passes", moved_ok)


def real_lost_task():
    old = subprocess.run(["git", "show", "dedc3ca^:TODO.md"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout
    new = subprocess.run(["git", "show", "dedc3ca:TODO.md"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout
    msg = subprocess.run(["git", "log", "-1", "--format=%B", "dedc3ca"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8").stdout
    p = cr.removal_problems(old, new, msg)
    check(any("Test connection" in x and "20261102-1503" in x for x in p),
          f"dedc3ca lost 'Relay Setup's Test connection…' (20261102-1503) — it must be refused: {p}")
test("RTASK-006", "the real case: the commit that lost the Test connection task (dedc3ca) would have been refused",
     real_lost_task)


def squash_and_merge_skipped():
    with tempfile.TemporaryDirectory() as g:
        check(not cr.combining(g), "an ordinary commit is checked")
        open(os.path.join(g, "SQUASH_MSG"), "w").close()
        check(cr.combining(g), "a squash commit is skipped — the branch's commits were each checked")
    with tempfile.TemporaryDirectory() as g:
        open(os.path.join(g, "MERGE_HEAD"), "w").close()
        check(cr.combining(g), "a merge commit is skipped too")
test("RTASK-007", "squash and merge commits are skipped (each branch commit was already checked)", squash_and_merge_skipped)


def report_reads_declared_done():
    msgs = [("s1", dt.datetime(2026, 11, 10, 9), "docs: done 20261015-1000 (shipped without a ✅)"),
            ("s2", dt.datetime(2026, 11, 11, 9), "docs: dropped 20261015-1100 — superseded")]
    d = br.declared_done(msgs)
    check(d.get("id:20261015-1000") == dt.datetime(2026, 11, 10, 9), f"done 20261015-1000 on Nov 10: {d}")
    check("id:20261015-1100" not in d, f"a dropped task is not done: {d}")
test("RTASK-008", "the backlog report counts a task declared `done <id>` in a commit message as done", report_reads_declared_done)

done()
