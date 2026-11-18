# Tests for tools/copies.py — working copies of the folder (git worktrees with the tools linked in).
# tags: copies, tooling, tier 1
# covers: tools/copies.py, tools/run_tests.py, git-hooks/private_values.py, test/ui/rw.py
# heavy: yes — ~400 processes a run, up to 9 at once: git worktrees, submodules, their hooks' shells (counted 2026-11-17)
# Run: python test/test_copies.py
#
# TODO "Faster sprints", item 3 (2026-11-16). Each test builds a throwaway "main folder" in %TEMP% — a real git
# repository with the real tools/copies.py in it, a stand-in test runner, a submodule, and the four untracked tool folders
# (each holding a file that must survive) — and drives copies.py there as Claude would, from the command line.
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

COPIES = os.path.join(ROOT, "tools", "copies.py")
LINKS = (".venv", "node_modules", "tools/build/node_modules", "relay/node_modules")
# git's own variables (GIT_DIR, GIT_INDEX_FILE…) point every git command at THIS repository while the commit hook runs
# (RUN-044) — everything here runs without them.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
# …and so does what runs in THIS process (COPY-005's private_values.note_path): in a commit hook run from a working copy,
# GIT_DIR names the copy's own git folder, and git then answered for it instead of the throwaway (2026-11-16).
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]
FAKE_URL = "https://invalid.example/pytools.git"     # never reachable: the submodule must come from the main folder

# The stand-in runner: tier 1 "passes" only if the linked .venv is reachable from the copy; --stamp is never proven.
RUNNER = '''import os, sys
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--stamp" in sys.argv:
    print("Test results for HEAD\\n  ✗ tier 1: no full tier 1 run recorded on this commit\\nNOT PROVEN — see above.")
    sys.exit(1)
ok = os.path.exists(os.path.join(here, ".venv", "sentinel.txt"))
print(f"stand-in tier 1 in {here}: venv {'seen' if ok else 'MISSING'}")
print("Tests: 1 file(s) passed, 0 failed" if ok else "Tests: 0 file(s) passed, 1 failed")
sys.exit(0 if ok else 1)
'''


def git(cwd, *args, ok=True):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "protocol.file.allow=always", *args],
                       cwd=cwd, env=CLEAN_ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if ok and r.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


class World:
    """A throwaway main folder (and the -copies folder beside it), removed at the end."""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp(prefix="rw-copies-test-")
        self.main = os.path.join(self.tmp, "RW")
        sub = os.path.join(self.tmp, "pytools-origin")
        write(os.path.join(sub, "keep.txt"), "a submodule\n")
        git(sub, "init", "-q", "-b", "main")
        git(sub, "add", "keep.txt")
        git(sub, "commit", "-q", "-m", "sub")
        m = self.main
        write(os.path.join(m, ".gitignore"), ".venv/\nnode_modules/\n__pycache__/\n")
        write(os.path.join(m, "tools", "copies.py"), open(COPIES, encoding="utf-8").read())
        write(os.path.join(m, "tools", "run_tests.py"), RUNNER)
        write(os.path.join(m, "tools", "build", "compile.js"), "// x\n")
        write(os.path.join(m, "relay", "relay-worker.js"), "// x\n")
        write(os.path.join(m, "git-hooks", "pre-commit"), '#!/bin/sh\necho "pre-commit ran in $(pwd)"\nexit 1\n')
        write(os.path.join(m, "app.js"), "// app\n")
        git(m, "init", "-q", "-b", "main")
        git(m, "submodule", "add", "-q", sub, "pytools")
        git(m, "config", "-f", ".gitmodules", "submodule.pytools.url", FAKE_URL)
        git(m, "config", "submodule.pytools.url", FAKE_URL)        # as on Ron's PC: the real address, here unreachable
        git(m, "add", ".gitignore", ".gitmodules", "tools/copies.py", "tools/run_tests.py", "tools/build/compile.js",
            "relay/relay-worker.js", "git-hooks/pre-commit", "app.js")
        git(m, "commit", "-q", "-m", "start")
        git(m, "config", "core.hooksPath", "git-hooks")
        for rel in LINKS:                               # the untracked tool folders, each with a file that must survive
            write(os.path.join(m, rel, "sentinel.txt"), f"the main folder's {rel}\n")
        self.precious = os.path.join(self.tmp, "precious")
        write(os.path.join(self.precious, "deep", "keep.txt"), "never deleted through a link\n")
        return self

    def copies(self, *args):
        r = subprocess.run([sys.executable, os.path.join(self.main, "tools", "copies.py"), *args], cwd=self.main,
                           env=CLEAN_ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout + r.stderr

    def copy(self, name):
        return os.path.join(self.tmp, "RW-copies", name)

    def sentinels(self):
        return all(os.path.exists(os.path.join(self.main, rel, "sentinel.txt")) for rel in LINKS)

    def __exit__(self, *exc):
        remove_tree(self.tmp)                           # links removed first, never followed


def load_copies():
    spec = importlib.util.spec_from_file_location("copies_mod", COPIES)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def new_links_and_tests():
    with World() as w:
        code, out = w.copies("new", "one", "--from", "main")
        c = w.copy("one")
        check(code == 0 and "READY" in out, f"new says READY (exit {code}):\n{out}")
        check(git(c, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "one", "on its own branch, named for it")
        for rel in LINKS:
            p = os.path.join(c, rel)
            check(os.path.isjunction(p) or os.path.islink(p), f"{rel} is a link")
            check(os.path.samefile(p, os.path.join(w.main, rel)), f"{rel} is the main folder's")
        check("stand-in tier 1 in " + c in out and "venv seen" in out, f"tier 1 ran IN the copy, through the link:\n{out}")
        check(os.path.exists(os.path.join(c, "pytools", "keep.txt")),
              "the submodule is checked out (from the main folder's — its real address is unreachable)")
        check(git(c, "status", "--porcelain").stdout.strip() == "", "and the copy is clean: links and submodule unseen")
        code, out = w.copies("new", "one")
        check(code != 0 and "already exists" in out, f"a second copy of the same name is refused: {out}")
        code, out = w.copies("new", "two", "--branch", "one")
        check(code != 0, f"a branch already checked out in another copy is refused (git's rule): {out}")
        code, out = w.copies("new", "../x")
        check(code != 0 and "a copy's name" in out, f"a name that isn't a plain folder name is refused: {out}")
test("COPY-001", "new: a worktree beside the main folder, its own branch, the four tool folders linked, the submodule "
     "checked out, tier 1 run there", new_links_and_tests)


def remove_refuses_and_keeps_the_branch():
    with World() as w:
        w.copies("new", "one")
        c = w.copy("one")
        write(os.path.join(c, "draft.txt"), "not committed\n")
        code, out = w.copies("remove", "one")
        check(code != 0 and "uncommitted" in out and "draft.txt" in out and os.path.isdir(c),
              f"uncommitted work: refused, named, the copy kept:\n{out}")
        git(c, "add", "draft.txt")
        git(c, "commit", "-q", "--no-verify", "-m", "work")      # (the throwaway's own hook refuses every commit)
        code, out = w.copies("remove", "one")
        check(code != 0 and "1 commit(s) that exist nowhere else" in out and os.path.isdir(c),
              f"a commit on no other branch: refused:\n{out}")
        git(w.main, "branch", "keep-it", "one")
        code, out = w.copies("remove", "one")
        check(code == 0 and "REMOVED" in out and not os.path.exists(c), f"once another branch has it: removed:\n{out}")
        check(git(w.main, "rev-parse", "--verify", "--quiet", "refs/heads/one").returncode == 0, "its branch is kept")
        w.copies("new", "two")
        c2 = w.copy("two")
        write(os.path.join(c2, "x.txt"), "x\n")
        code, out = w.copies("remove", "two", "--force")
        check(code == 0 and not os.path.exists(c2), f"--force removes a copy with uncommitted work:\n{out}")
        check(git(w.main, "rev-parse", "--verify", "--quiet", "refs/heads/two").returncode == 0,
              "and still keeps the branch")
test("COPY-002", "remove: refuses uncommitted work and commits found nowhere else; --force removes anyway; the branch "
     "is always kept", remove_refuses_and_keeps_the_branch)


def removing_never_deletes_through_a_link():
    with World() as w:
        # The danger, shown first on a plain worktree: git's own remove deletes the files a link points at.
        bare = os.path.join(w.tmp, "plain")
        git(w.main, "worktree", "add", "-q", "-b", "plain", bare)
        victim = os.path.join(w.tmp, "victim")
        write(os.path.join(victim, "file.txt"), "x\n")
        copies = load_copies()
        copies.make_link(os.path.join(bare, "node_modules"), victim)
        git(w.main, "worktree", "remove", bare, ok=False)
        print(f"      (git worktree remove on a copy holding a link, links not removed first: the folder it pointed at "
              f"{'LOST its files' if not os.path.exists(os.path.join(victim, 'file.txt')) else 'kept its files'})")
        w.copies("new", "one")
        c = w.copy("one")
        copies.make_link(os.path.join(c, "relay", "extra"), w.precious)     # a link someone made by hand, deeper in
        code, out = w.copies("remove", "one")
        check(code != 0 and "relay/extra" in out, f"(a link made by hand is uncommitted work — refused:\n{out})")
        code, out = w.copies("remove", "one", "--force")
        check(w.sentinels(), f"every one of the main folder's linked folders still has its files:\n{out}")
        check(os.path.exists(os.path.join(w.precious, "deep", "keep.txt")), "and so does a folder linked by hand")
        check(code == 0 and not os.path.exists(c), f"removed with --force:\n{out}")
        check(f"unlinked {os.path.normpath('relay/extra')}" in out, f"the hand-made link was unlinked first:\n{out}")
        for rel in LINKS:
            check(f"unlinked {os.path.normpath(rel)}" in out, f"{rel} was unlinked first:\n{out}")
test("COPY-003", "remove takes every link out first — the main folder's .venv and node_modules (and anything linked by "
     "hand) keep their files", removing_never_deletes_through_a_link)


def list_shows_each_copy():
    with World() as w:
        w.copies("new", "one")
        code, out = w.copies("list")
        check(code == 0 and "(main folder)" in out and "one" in out and "branch one" in out, f"each copy listed:\n{out}")
        check("test stamp: NOT PROVEN" in out, f"with its stamp (run_tests.py --stamp there):\n{out}")
        w.copies("remove", "one")
        code, out = w.copies("list")
        check("No working copies" in out, f"none left: {out}")
test("COPY-004", "list: each copy with its branch, its commit and its test stamp", list_shows_each_copy)


def a_copy_knows_itself():
    copies = load_copies()
    pv_spec = importlib.util.spec_from_file_location("pv", os.path.join(ROOT, "git-hooks", "private_values.py"))
    pv = importlib.util.module_from_spec(pv_spec)
    pv_spec.loader.exec_module(pv)
    with World() as w:
        w.copies("new", "one")
        c = w.copy("one")
        check(copies.copy_name(w.main) is None and copies.copy_name(c) == "one", "the copy's name; none for the main")
        base = os.path.join(tempfile.gettempdir(), "rw-test-artifacts")
        check(copies.screenshots_folder(w.main, {}) == base, "the main folder's screenshots stay where they were")
        check(copies.screenshots_folder(c, {}) == base + "-one", "a copy's go to a folder named for it")
        check(copies.screenshots_folder(c, {"RW_TEST_ARTIFACTS": r"C:\shots"}) == r"C:\shots-one",
              "RW_TEST_ARTIFACTS too gets the copy's name")
        note = os.path.join(w.main, ".private", "Secrets.txt")
        write(note, "made-up value abc123def456ghi789\n")
        check(os.path.samefile(pv.note_path(c), note), "the private-values check in a copy reads the main folder's note")
        r = git(c, "commit", "--allow-empty", "-m", "x", ok=False)
        check(r.returncode != 0 and "pre-commit ran in" in r.stdout + r.stderr and "one" in r.stdout + r.stderr,
              f"the commit checks (core.hooksPath git-hooks) run in the copy, from the copy: {r.stdout}{r.stderr}")
        w.copies("remove", "one", "--force")
test("COPY-005", "in a copy: its name, its own screenshots folder, the main folder's private note, the commit checks",
     a_copy_knows_itself)


def lock_listing(folder, locked):
    """Make `folder` one this user can't list (locked=True) — or listable again (False). Windows: a "deny list folder"
    entry for this user (icacls); elsewhere: no permissions. Returns the command's complaint, '' when it worked."""
    if os.name == "nt":
        user = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
        args = (["icacls", folder, "/deny", f"{user}:(RD)"] if locked else ["icacls", folder, "/remove:d", user])
        r = subprocess.run(args, capture_output=True, text=True, errors="replace")
        return "" if r.returncode == 0 else (r.stderr or r.stdout).strip()
    os.chmod(folder, 0 if locked else 0o755)
    return ""


def remove_refuses_what_it_cant_look_into():
    copies = load_copies()
    with World() as w:
        w.copies("new", "one")
        c = w.copy("one")
        locked = os.path.join(c, "relay", "locked")
        os.makedirs(locked)
        copies.make_link(os.path.join(locked, "hidden-link"), w.precious)   # a link inside a folder no one can list
        problem = lock_listing(locked, True)
        try:                    # unlocked whatever happens — a locked folder can't be cleaned up
            try:
                os.listdir(locked)
                can_list = True
            except OSError:
                can_list = False
            check(not problem and not can_list, f"(setup: the folder must be unlistable — {problem or 'it still lists'})")
            try:
                copies.find_links(c)
            except copies.Unscannable as e:
                check(os.path.normpath(locked) in str(e), f"find_links names the folder it couldn't look into: {e}")
            else:
                raise AssertionError("find_links skipped a folder it couldn't look into instead of refusing")
            code, out = w.copies("remove", "one", "--force")
            check(code != 0 and "NOT REMOVED" in out and os.path.normpath(locked) in out,
                  f"remove refuses — even with --force — naming the folder it couldn't look into (exit {code}):\n{out}")
            check(os.path.isdir(c) and "unlinked" not in out, f"…before removing anything — no link taken out:\n{out}")
            print("      (the refusal: " + " / ".join(ln.strip() for ln in out.strip().splitlines()[-3:]) + ")")
            check(all(os.path.isjunction(os.path.join(c, rel)) or os.path.islink(os.path.join(c, rel)) for rel in LINKS),
                  "the copy's links are all still there")
            check(os.path.exists(os.path.join(w.precious, "deep", "keep.txt")) and w.sentinels(),
                  "nothing a link points at lost a file")
        finally:
            lock_listing(locked, False)
        code, out = w.copies("remove", "one", "--force")
        check(code == 0 and not os.path.exists(c), f"once it can be looked into, the copy is removed:\n{out}")
        check(f"unlinked {os.path.normpath('relay/locked/hidden-link')}" in out, f"…the link in it taken out first:\n{out}")
        check(os.path.exists(os.path.join(w.precious, "deep", "keep.txt")) and w.sentinels(),
              "and nothing it pointed at lost a file")
test("COPY-006", "remove REFUSES (even with --force) while any folder in the copy can't be looked into — a link in it "
     "would be missed, and git's remove would delete through it; named, nothing removed", remove_refuses_what_it_cant_look_into)


# --- a removed copy keeps its test-run records and says where its time went (TODO tooling item 11.6; Ron, 2026-11-18) ---
def load_runner():
    spec = importlib.util.spec_from_file_location("run_tests_for_copies", os.path.join(ROOT, "tools", "run_tests.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def the_archive_is_never_read_nor_pruned():
    import json
    copies, rt = load_copies(), load_runner()
    check(copies.ARCHIVE == rt.COPIES_ARCHIVE, f"one archive name: copies.py {copies.ARCHIVE!r}, run_tests.py "
          f"{rt.COPIES_ARCHIVE!r}")
    narrowing = {k for k, (narrows, _) in rt.RUN_ENV.items() if narrows}
    check(set(copies.NARROWING_ENV) == narrowing, f"copies.py's narrowing variables {sorted(copies.NARROWING_ENV)} are "
          f"run_tests.py's ({sorted(narrowing)}) — a run it calls 'full' must be one the stamp would")
    folder = tempfile.mkdtemp(prefix="rw-copies-archive-")
    saved = rt.KEEP_RECORDS
    try:
        kept = os.path.join(folder, copies.ARCHIVE, "one-20261118-1200")
        write(os.path.join(kept, "old-run.json"), json.dumps({"started": "2026-01-01T00:00:00+00:00",
                                                              "ended": "2026-01-01T00:01:00+00:00", "result": "passed"}))
        write(os.path.join(kept, "old-run", "test_x.py.txt"), "a kept output\n")
        rt.KEEP_RECORDS = 2
        # named so the archive's name sorts BEFORE the oldest record kept — pruning by name order alone would take it
        for n in range(1, 5):
            rt.write_record({"id": f"zz-{n}", "started": f"2026-11-18T12:0{n}:00+00:00",
                             "ended": f"2026-11-18T12:0{n}:30+00:00", "result": "passed"}, folder)
            os.makedirs(os.path.join(folder, f"zz-{n}"), exist_ok=True)     # each run's kept outputs
        rt.write_record({"id": "zz-5", "started": "2026-11-18T12:05:00+00:00", "ended": "2026-11-18T12:05:30+00:00",
                         "result": "passed"}, folder)
        left = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
        check(left == ["zz-4.json", "zz-5.json"], f"(setup: the newest records kept, the rest pruned — {left})")
        check(not os.path.exists(os.path.join(folder, "zz-1")), "(setup: an old run's outputs pruned with its record)")
        check(os.path.exists(os.path.join(kept, "old-run.json")) and os.path.exists(os.path.join(kept, "old-run",
              "test_x.py.txt")), "pruning (the newest N kept) never deletes the archived copies' records")
        got = [r.get("id") for r in rt.read_records(folder)]
        check(got == ["zz-4", "zz-5"], f"read_records (the stamp, longest-first) reads only the folder's own records, "
              f"never the archive's: {got}")
    finally:
        rt.KEEP_RECORDS = saved
        remove_tree(folder)
test("COPY-007", "the archive of removed copies' records (rw-test-results/copies/) is never read by the runner (stamps, "
     "longest-first) and never pruned; copies.py and run_tests.py agree on its name and on what narrows a run",
     the_archive_is_never_read_nor_pruned)


def plant(folder, rec, output=None):
    """A test-run record in a copy's records folder (the stand-in runner writes none) — and a failed file's kept output."""
    import json
    write(os.path.join(folder, rec["id"] + ".json"), json.dumps(rec))
    if output:
        write(os.path.join(folder, rec["id"], "test_x.py.txt"), output)


def removal_keeps_records_and_says_where_the_time_went():
    import datetime
    import json
    copies = load_copies()
    with World() as w:
        w.copies("new", "one")
        c = w.copy("one")
        note_path = git(c, "rev-parse", "--path-format=absolute", "--git-path", copies.NOTE).stdout.strip()
        check(os.path.exists(note_path), f"new notes when it made the copy, in the copy's own git folder: {note_path}")
        note = json.load(open(note_path, encoding="utf-8"))
        made = datetime.datetime.fromisoformat(note["made"])
        now = datetime.datetime.now().astimezone()
        check(abs((now - made).total_seconds()) < 120 and note.get("branch") == "one" and note.get("start")
              and note.get("ready"), f"…with the time, the branch, the commit it started at, when it was ready: {note}")
        # Pretend it was made two hours ago: four runs planted around that, in the copy's own records folder.
        t = now - datetime.timedelta(minutes=120)

        def at(minutes):
            return (t + datetime.timedelta(minutes=minutes)).isoformat(timespec="seconds")
        note.update(made=at(0), ready=at(2))
        with open(note_path, "w", encoding="utf-8") as f:
            json.dump(note, f)
        recs = git(c, "rev-parse", "--path-format=absolute", "--git-path", "rw-test-results").stdout.strip()
        plant(recs, {"id": "r0", "started": at(0), "ended": at(2), "result": "passed", "ran": {"tier": "1"}})
        plant(recs, {"id": "r1", "started": at(10), "ended": at(20), "result": "passed",
                     "ran": {"tier": "2", "tags": None, "ids": None}})
        plant(recs, {"id": "r2", "started": at(15), "ended": at(25), "result": "failed",
                     "ran": {"tier": "1", "ids": ["COPY-007"]},
                     "files": [{"file": "test/x.py", "result": "failed", "retried": [{"reason": "the machine's trouble"}]}]},
              output="the whole failed output\n")
        plant(recs, {"id": "r3", "started": at(60), "ended": at(65), "result": "passed", "ran": {"tier": "2"},
                     "env": {"RW_CELLS": "CELL-005"}})
        write(os.path.join(c, "work.txt"), "built\n")
        git(c, "add", "work.txt")
        git(c, "commit", "-q", "--no-verify", "-m", "the work")
        git(w.main, "branch", "keep-one", "one")
        code, out = w.copies("remove", "one")
        check(code == 0 and "REMOVED" in out and not os.path.exists(c), f"removed:\n{out}")
        print("      (the removal said:\n        " + "\n        ".join(out.strip().splitlines()[-12:]) + ")")
        home = os.path.join(w.main, ".git", "rw-test-results", copies.ARCHIVE)
        kept = [os.path.join(home, d) for d in os.listdir(home)] if os.path.isdir(home) else []
        check(len(kept) == 1 and os.path.basename(kept[0]).startswith("one-"),
              f"its records kept in the main folder's records, in their own archive folder named for it: {kept}")
        k = kept[0]
        check(all(os.path.exists(os.path.join(k, f"r{n}.json")) for n in range(4))
              and open(os.path.join(k, "r2", "test_x.py.txt"), encoding="utf-8").read() == "the whole failed output\n",
              f"every record and the kept failed output moved there: {os.listdir(k)}")
        check(not [n for n in os.listdir(os.path.join(w.main, ".git", "rw-test-results")) if n.endswith(".json")],
              "none of them among the main folder's own records (its stamp and estimates never see them)")
        check(not os.path.exists(os.path.dirname(recs)), "the copy's git folder is gone, as before")
        s = json.load(open(os.path.join(k, "time.json"), encoding="utf-8"))
        check(abs(s["wall_seconds"] - 7200) < 180, f"wall time: made → removed ≈ 2 h: {s['wall_seconds']}")
        check(s["test_seconds"] == 22 * 60, f"test minutes: 2 + (10..25 = 15, the overlap counted once) + 5 = 22 min: "
              f"{s['test_seconds'] / 60}")
        check(abs(s["everything_else_seconds"] - (s["wall_seconds"] - s["test_seconds"])) < 1, "everything else = wall − tests")
        n = s["counts"]
        check((n["runs"], n["full"], n["narrow"], n["passed"], n["failed"], n["reruns_alone"], n["readiness"])
              == (4, 2, 2, 3, 1, 1, 1), f"runs 4: full 2 (1 the readiness run new made), narrow 2, passed 3, failed 1, "
              f"1 rerun alone: {n}")
        check(len(s["commits"]) == 1 and s["commits"][0]["subject"] == "the work", f"its commits: {s['commits']}")
        text = open(os.path.join(k, "time.txt"), encoding="utf-8").read()
        for want in ("test runs: 4", "22 min", "everything else", "building, reading, thinking, waiting",
                     "--id COPY-007", "RW_CELLS=CELL-005", "commits on its branch since it was made: 1", k):
            check(want in text and want in out, f"the printout and time.txt say {want!r}:\n{out}\n---\n{text}")

        # A copy made before copies.py noted the time: its git folder's own time stands in, and says so.
        w.copies("new", "two")
        c2 = w.copy("two")
        os.remove(git(c2, "rev-parse", "--path-format=absolute", "--git-path", copies.NOTE).stdout.strip())
        code, out = w.copies("remove", "two")
        check(code == 0 and "estimated" in out, f"no note: the made time is estimated, and says so:\n{out}")

        code, out = w.copies("report")
        print("      (the report:\n        " + "\n        ".join(out.strip().splitlines()) + ")")
        rows = [ln for ln in out.splitlines() if ln.startswith(("one ", "two "))]
        check(code == 0 and len(rows) == 2 and "total" in out.lower() and "22" in rows[0] and "{" not in out,
              f"report: one row per removed copy, then the totals:\n{out}")
        tomorrow = (now + datetime.timedelta(days=1)).date().isoformat()
        code, out = w.copies("report", "--since", tomorrow)
        check(code == 0 and not [ln for ln in out.splitlines() if ln.startswith(("one ", "two "))],
              f"--since leaves out copies removed before that day:\n{out}")
test("COPY-008", "remove keeps the copy's test-run records (and failed outputs) in the main folder's records, in their own "
     "archive folder, and says where its time went — wall, test minutes (overlaps once), runs full / narrow, passed / "
     "failed, reruns alone, commits, everything else; report lists the removed copies",
     removal_keeps_records_and_says_where_the_time_went)


def removal_stops_when_records_cant_be_kept():
    copies = load_copies()
    with World() as w:
        w.copies("new", "one")
        c = w.copy("one")
        recs = git(c, "rev-parse", "--path-format=absolute", "--git-path", "rw-test-results").stdout.strip()
        plant(recs, {"id": "r0", "started": "2026-11-18T10:00:00+00:00", "ended": "2026-11-18T10:01:00+00:00",
                     "result": "passed", "ran": {"tier": "1"}})
        write(os.path.join(w.main, ".git", "rw-test-results", copies.ARCHIVE), "a FILE where the archive folder goes\n")
        code, out = w.copies("remove", "one", "--force")
        check(code != 0 and "NOT REMOVED" in out and "records" in out, f"the records can't be kept: refused, said:\n{out}")
        check(os.path.isdir(c) and os.path.exists(os.path.join(recs, "r0.json")), "the copy and its records are untouched")
        check(all(os.path.isjunction(os.path.join(c, rel)) or os.path.islink(os.path.join(c, rel)) for rel in LINKS),
              "…its links too (nothing was taken out)")
test("COPY-009", "remove stops — even with --force — when the copy's records can't be kept, and says so (never lost "
     "silently); nothing touched", removal_stops_when_records_cant_be_kept)

done()
