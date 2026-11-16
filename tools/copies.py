#!/usr/bin/env python3
"""
copies.py — working copies of the project folder (TODO "Faster sprints", item 3; Ron's idea, 2026-11-15).

A working copy is a git worktree of this repository: its own folder, on its own branch, sharing one history with the main
folder. One agent builds in one copy while Claude reviews and tests in another, and independent tasks build at once.

    py tools/copies.py new <name> [--branch <b>] [--from <ref>]
        make  ..\\ReaderWrangler-copies\\<name>  on branch <b> (default: <name>; made from <ref>, default HEAD, when it
        doesn't exist yet), link in what git doesn't hold, check out the submodule, then run tier 1 there — it's READY
        only if tier 1 passes
    py tools/copies.py remove <name> [--force]
        refuse if the copy has anything uncommitted, or its branch has commits that exist nowhere else (no other branch,
        tag or remote) — --force removes it anyway; the BRANCH IS ALWAYS KEPT. Removes the links FIRST, then the copy.
    py tools/copies.py list            (also what a double-click shows)
        each copy: its branch, its commit, anything uncommitted, and its test stamp (run_tests.py --stamp there)

What a copy needs that git doesn't hold (proven 2026-11-16 — a copy without them fails tier 1: the build tests, the
parse and saved-reads checks, the screen-test runner tests — and tier 2 can't start at all):
    .venv                      Playwright for the screen tests (requirements-dev.txt)
    node_modules               the commit checks' Babel (check-names, parse-js, saved-reads-js)
    tools/build/node_modules   the build: Babel + Tailwind (dist/)
    relay/node_modules         wrangler — the local relay of tier 3 and of the screen tests that use Cloud Sync
Each is LINKED to the main folder's (a Windows directory junction: nothing copied, one install to keep up to date).
The pytools submodule (serve.py needs it) is checked out from the main folder's copy, not linked: a link breaks git —
its .git file points at the main folder's .git by a relative path. The private notes (.private/) aren't linked: the
commit check that needs them finds the main folder's (git-hooks/private_values.py).

Removing: `git worktree remove` deletes THROUGH a junction — tried 2026-11-16 on a throwaway: the files of the folder a
link pointed at were gone. So every link in the copy is removed first, by itself (never what it points at), and the
main folder's linked folders are checked afterwards.

Nothing here stops a process. Tested by test/test_copies.py.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = (".venv", "node_modules", "tools/build/node_modules", "relay/node_modules")
# git's location variables, set when git runs a hook: they'd point every command here at the folder that ran the hook
GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
                     "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX")


def _env():
    return {k: v for k, v in os.environ.items() if k not in GIT_LOCATION_VARS}


def git(cwd, *args, check=False):
    r = subprocess.run(["git", *args], cwd=cwd, env=_env(), capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}:\n{(r.stderr or r.stdout).strip()}")
    return r


def main_folder(repo=ROOT):
    """The main working folder — the one whose .git every copy shares."""
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir", check=True).stdout.strip()
    common = os.path.normpath(common)
    if os.path.basename(common) != ".git":
        raise SystemExit(f"{repo}: its git folder ({common}) isn't a main folder's .git — not supported")
    return os.path.dirname(common)


def copies_dir(main):
    """Where the copies live: beside the main folder — C:\\Users\\Ron\\Projects\\ReaderWrangler-copies (Ron, 2026-11-16)."""
    return main.rstrip("\\/") + "-copies"


def copy_name(root=ROOT):
    """The name of the working copy `root` is — its folder name when it's a git worktree (its .git is a FILE) — or None
    for the main folder. The screen tests use it to keep each copy's screenshots apart (test/ui/rw.py)."""
    return os.path.basename(os.path.normpath(root)) if os.path.isfile(os.path.join(root, ".git")) else None


def screenshots_folder(root=ROOT, environ=None):
    """Where the screen tests of the folder `root` save screenshots: RW_TEST_ARTIFACTS, else %TEMP%\\rw-test-artifacts —
    with "-<copy name>" added in a working copy, so two copies running the same test file don't overwrite each other's
    (2026-11-16). The main folder's stays as it was."""
    import tempfile
    env = os.environ if environ is None else environ
    base = env.get("RW_TEST_ARTIFACTS") or os.path.join(tempfile.gettempdir(), "rw-test-artifacts")
    name = copy_name(root)
    return f"{base}-{name}" if name else base


def _same(a, b):
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def worktrees(main):
    """git's list of working folders: [{path, head, branch (short name or None)}], the main folder first."""
    out, cur = [], None
    for ln in git(main, "worktree", "list", "--porcelain", check=True).stdout.splitlines():
        if ln.startswith("worktree "):
            cur = {"path": os.path.normpath(ln[9:]), "head": None, "branch": None}
            out.append(cur)
        elif ln.startswith("HEAD ") and cur:
            cur["head"] = ln[5:]
        elif ln.startswith("branch ") and cur:
            cur["branch"] = ln[7:].removeprefix("refs/heads/")
    return out


# --- links: a directory junction on Windows (no rights needed, unlike a symbolic link), a symbolic link elsewhere -----
def is_link(path):
    return os.path.islink(path) or (hasattr(os.path, "isjunction") and os.path.isjunction(path))


def make_link(link, target):
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", os.path.normpath(link), os.path.normpath(target)],
                           capture_output=True, text=True)
        if r.returncode or not is_link(link):
            raise SystemExit(f"couldn't link {link} → {target}: {(r.stderr or r.stdout).strip()}")
    else:
        os.symlink(target, link, target_is_directory=True)


def remove_link(path):
    """Remove the link itself — never what it points at. (A junction is removed like an empty folder: os.rmdir refuses a
    real folder that has anything in it, so a mistake here can't delete files.)"""
    if os.name == "nt" and not os.path.islink(path):
        os.rmdir(path)
    else:
        os.unlink(path)


def find_links(top):
    """Every link anywhere inside `top` (not followed into), outside .git."""
    found, stack = [], [top]
    while stack:
        d = stack.pop()
        try:
            entries = list(os.scandir(d))
        except OSError:
            continue
        for e in entries:
            if is_link(e.path):
                found.append(e.path)
            elif e.is_dir(follow_symlinks=False) and e.name != ".git":
                stack.append(e.path)
    return found


# --- new ----------------------------------------------------------------------------------------------------------------
def submodules(folder):
    """[(name, path, url)] from the folder's .gitmodules."""
    r = git(folder, "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$")
    out = []
    for ln in r.stdout.splitlines():
        key, _, path = ln.partition(" ")
        name = key[len("submodule."):-len(".path")]
        url = git(folder, "config", "-f", ".gitmodules", f"submodule.{name}.url").stdout.strip()
        out.append((name, path, url))
    return out


def cmd_new(a, repo):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", a.name):
        raise SystemExit(f"{a.name!r}: a copy's name is letters, digits, '.', '_' and '-' (it names a folder)")
    main = main_folder(repo)
    dest = os.path.join(copies_dir(main), a.name)
    if os.path.lexists(dest):
        raise SystemExit(f"{dest} already exists — pick another name, or remove that copy first")
    branch = a.branch or a.name
    exists = git(main, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0
    if exists and a.from_ref:
        raise SystemExit(f"branch {branch} already exists — --from is only for a new branch (or name another --branch)")
    if exists:
        args = ["worktree", "add", dest, branch]
        made = f"on the existing branch {branch}"
    else:
        start = git(repo, "rev-parse", "--verify", "--quiet", f"{a.from_ref or 'HEAD'}^{{commit}}").stdout.strip()
        if not start:
            raise SystemExit(f"{a.from_ref!r} isn't a commit here")
        args = ["worktree", "add", "-b", branch, dest, start]
        made = f"on a new branch {branch}, from {a.from_ref or 'HEAD'} ({start[:12]})"
    os.makedirs(copies_dir(main), exist_ok=True)
    r = git(main, *args)
    if r.returncode:
        raise SystemExit(f"git couldn't make the copy:\n{(r.stderr or r.stdout).strip()}")
    print(f"· made {dest} {made}")

    missing = []
    for rel in LINKS:
        target, link = os.path.join(main, rel), os.path.join(dest, rel)
        if not os.path.isdir(target):
            missing.append(rel)
            continue
        if not os.path.isdir(os.path.dirname(link)):
            print(f"· not linked: {rel} — this branch has no {os.path.dirname(rel)}/ folder")
            continue
        make_link(link, target)
        print(f"· linked {rel} → the main folder's")
    for rel in missing:
        print(f"! the main folder has no {rel} — what needs it will fail in the copy too (docs/design/TESTING.md §4)")

    for name, path, url in submodules(dest):
        source = os.path.join(main, path)
        if not os.path.exists(os.path.join(source, ".git")):
            print(f"! submodule {path}: the main folder hasn't checked it out — not set up in the copy")
            continue
        # from the main folder's own copy of it — no network; the copy's submodule still names the real address
        r = git(dest, "-c", "protocol.file.allow=always", "-c", f"url.{source.replace(os.sep, '/')}.insteadOf={url}",
                "submodule", "update", "--init", "--", path)
        if r.returncode:
            print(f"! submodule {path} couldn't be checked out: {(r.stderr or r.stdout).strip()}")
        else:
            print(f"· submodule {path} checked out (from the main folder's)")

    hooks = git(dest, "config", "core.hooksPath").stdout.strip()
    if hooks != "git-hooks":
        print(f"! the commit checks are OFF here: core.hooksPath is {hooks or 'not set'} — once, in the main folder: "
              "git config core.hooksPath git-hooks")

    print("· tier 1 in the copy (py tools/run_tests.py --tier 1) …", flush=True)
    code = subprocess.run([sys.executable, os.path.join(dest, "tools", "run_tests.py"), "--tier", "1"], cwd=dest,
                          env=_env()).returncode
    if code:
        print(f"NOT READY — tier 1 failed in {dest} (above). It's left as it is for a look; "
              f"py tools/copies.py remove {a.name} --force  removes it (the branch stays).")
        return 1
    print(f"READY — {dest}, branch {branch}. When done:  py tools/copies.py remove {a.name}")
    return 0


# --- remove -------------------------------------------------------------------------------------------------------------
def unique_commits(main, wt):
    """How many commits this copy's branch (or detached HEAD) has that no other branch, tag or remote has."""
    if wt["branch"]:     # --exclude names the branch as --branches sees it (no refs/heads/), and applies to it alone
        args = ["rev-list", "--count", f"refs/heads/{wt['branch']}", "--not",
                f"--exclude={wt['branch']}", "--branches", "--tags", "--remotes"]
    else:
        args = ["rev-list", "--count", wt["head"], "--not", "--branches", "--tags", "--remotes"]
    r = git(main, *args, check=True)
    return int(r.stdout.strip() or 0)


def cmd_remove(a, repo):
    main = main_folder(repo)
    dest = os.path.join(copies_dir(main), a.name)
    wt = next((w for w in worktrees(main) if _same(w["path"], dest)), None)
    if wt is None:
        raise SystemExit(f"{dest} isn't a working copy of this repository (py tools/copies.py list)")
    if _same(repo, dest) or _same(os.getcwd(), dest):
        raise SystemExit("run this from another folder — not from inside the copy being removed")
    where = f"branch {wt['branch']}" if wt["branch"] else f"a detached HEAD ({(wt['head'] or '')[:12]})"
    if not a.force:
        dirty = [ln for ln in git(dest, "status", "--porcelain", "--untracked-files=normal", check=True).stdout
                 .splitlines() if ln.strip()]
        if dirty:
            raise SystemExit(f"NOT REMOVED — {dest} has uncommitted changes:\n  " + "\n  ".join(dirty[:10])
                             + (f"\n  (+{len(dirty) - 10} more)" if len(dirty) > 10 else "")
                             + "\nCommit them, or --force to throw them away.")
        n = unique_commits(main, wt)
        if n:
            raise SystemExit(f"NOT REMOVED — {where} has {n} commit(s) that exist nowhere else (no other branch, tag "
                             "or remote). Merge them first — or --force: the copy goes, the branch stays.")
    held = {rel: sorted(os.listdir(os.path.join(main, rel))) for rel in LINKS if os.path.isdir(os.path.join(main, rel))}
    # The links FIRST — `git worktree remove` would delete the main folder's files through them (see the top).
    for link in sorted(find_links(dest), key=len, reverse=True):
        remove_link(link)
        if os.path.lexists(link):
            raise SystemExit(f"couldn't remove the link {link} — stopped before removing the copy")
        print(f"· unlinked {os.path.relpath(link, dest)}")
    r = git(main, "worktree", "remove", "--force", dest)
    if r.returncode or os.path.exists(dest):
        raise SystemExit(f"git couldn't remove {dest} (a program still using a file there?):\n"
                         f"{(r.stderr or r.stdout).strip()}")
    # Checked, not assumed: each linked folder of the main folder still holds what it held before.
    lost = [rel for rel, names in held.items() if not os.path.isdir(os.path.join(main, rel))
            or not set(names) <= set(os.listdir(os.path.join(main, rel)))]
    if lost:
        print(f"REMOVED {dest} — {where} kept.\n!! THE MAIN FOLDER LOST FILES in {', '.join(lost)} — set them up again "
              "(docs/design/TESTING.md §4) and report this: the links were supposed to be removed first.")
        return 1
    print(f"REMOVED {dest} — {where} kept. The main folder's {', '.join(held)} still hold everything they held.")
    return 0


# --- list ---------------------------------------------------------------------------------------------------------------
def stamp_line(folder):
    """The test stamp of the folder's HEAD, in a line: 'PROVEN' or 'NOT PROVEN — why'."""
    runner = os.path.join(folder, "tools", "run_tests.py")
    if not os.path.exists(runner):
        return "no test runner on this branch"
    r = subprocess.run([sys.executable, runner, "--stamp"], cwd=folder, env=_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    if r.returncode == 0:
        return "PROVEN (tier 1 + tier 2 passed on this commit)"
    why = [ln for ln in lines if ln.startswith("✗")]
    return "NOT PROVEN — " + ("; ".join(why) if why else (lines[-1] if lines else "no answer"))


def cmd_list(_a, repo):
    main = main_folder(repo)
    home = copies_dir(main)
    found = 0
    for w in worktrees(main):
        is_main = _same(w["path"], main)
        if not is_main and not _same(os.path.dirname(w["path"]), home):
            continue
        found += not is_main
        name = "(main folder)" if is_main else os.path.basename(w["path"])
        dirty = git(w["path"], "status", "--porcelain", "--untracked-files=normal").stdout.splitlines()
        subject = git(w["path"], "log", "-1", "--format=%h %s").stdout.strip()
        print(f"{name}  —  {w['path']}\n    branch {w['branch'] or '(detached)'}: {subject[:100]}"
              + (f"\n    {len(dirty)} uncommitted change(s)" if dirty else "")
              + f"\n    test stamp: {stamp_line(w['path'])}")
    if not found:
        print(f"No working copies in {home}.  Make one:  py tools/copies.py new <name> [--branch <b>] [--from <ref>]")
    return 0


def main(argv=None, repo=ROOT):
    for stream in (sys.stdout, sys.stderr):      # a refusal (SystemExit) prints to stderr: "—" garbled there too
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Working copies of the project folder (git worktrees with the tools "
                                             "linked in). Docs: docs/design/SESSION-TOOLING.md.")
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("new", help="make a copy, link the tools, run tier 1 there")
    n.add_argument("name")
    n.add_argument("--branch", help="its branch (default: the name); an existing branch is checked out")
    n.add_argument("--from", dest="from_ref", help="where a NEW branch starts (default: HEAD)")
    r = sub.add_parser("remove", help="remove a copy (links first); its branch is kept")
    r.add_argument("name")
    r.add_argument("--force", action="store_true", help="even with uncommitted changes or commits found nowhere else")
    sub.add_parser("list", help="each copy, its branch and its test stamp")
    a = ap.parse_args(argv)
    if a.cmd == "new":
        return cmd_new(a, repo)
    if a.cmd == "remove":
        return cmd_remove(a, repo)
    return cmd_list(a, repo)          # "list", or nothing (a double-click)


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)   # the pytools submodule lives at the repo root
    try:
        from pytools.keepopen import run
    except ImportError:
        sys.exit(main())
    run(main, pause="always")
