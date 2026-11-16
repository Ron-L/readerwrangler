# Tests for tools/copies.py — working copies of the folder (git worktrees with the tools linked in).
# tags: copies, tooling, tier 1
# covers: tools/copies.py, git-hooks/private_values.py, test/ui/rw.py
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

done()
