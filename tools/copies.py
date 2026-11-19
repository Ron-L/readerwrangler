#!/usr/bin/env python3
"""
copies.py — working copies of the project folder (TODO "Faster sprints", item 3; Ron's idea, 2026-11-15).

A working copy is a local clone of the main folder's repository (since 2026-11-19 — TODO "Working copies that can't break
each other", item 1): its own folder, on its own branch, with its OWN git settings and history — so a mistake in one
(2026-11-18: a test set the one shared repository to "bare", and git stopped working in every copy and the main folder for
13 minutes) damages only that copy. On the same drive git shares the stored history through file links (`git clone
--local`), so a copy costs almost no disk. The clone calls the main folder's repository `main-folder` (its remote — also
how a copy finds the main folder). One agent builds in one copy while Claude reviews and tests in another, and
independent tasks build at once. Copies made before are git worktrees (one shared repository): still listed and removed.

Getting the work back: the agent's commits live in the copy. tools/merge_branches.py (run in the main folder) fetches
each branch it merges from the copy that holds it (fetch_from_copies) — one place, at the one moment the work is needed;
nothing pushes into the main folder's repository behind its back.

    py tools/copies.py new <name> [--branch <b>] [--from <ref>]
        clone the main folder's repository into  ..\\ReaderWrangler-copies\\<name>, on branch <b> (default: <name>; made
        from <ref>, default HEAD, when the main folder hasn't got it), with the main folder's own settings (the commit
        checks on, its name and e-mail, its ignore list); link in what git doesn't hold, check out the submodule, then
        run tier 1 there — it's READY only if tier 1 passes (NOT READY says "not proven — the machine was too busy" when
        no test failed: exit 3). One copy per branch: a branch the main folder or another copy is on is refused.
    py tools/copies.py remove <name> [--force]
        refuse if the copy has anything uncommitted, or holds commits the main folder's repository doesn't have (its
        branches, its HEAD — a worktree copy: commits no other branch, tag or remote has) — --force removes it anyway, and
        says what it threw away. Removes the links FIRST, then the copy — and refuses, even with --force, while any
        folder in the copy can't be looked into (a link there would be missed)
    py tools/copies.py list            (also what a double-click shows)
        each copy: its branch, its commit, anything uncommitted, and its test stamp (run_tests.py --stamp there)
    py tools/copies.py report [--since YYYY-MM-DD]
        one row per removed copy (from its kept records): made, removed, wall time, test minutes and their share, runs
        full / narrow, passed / failed — and the totals. For a sprint's post-mortem.

Where a copy's time went (TODO tooling item 11.6; Ron, 2026-11-18: "Should the agents record where their time goes … so
we can analyze that?"): `new` notes when it made the copy (rw-copy.json in the copy's own git folder — it goes with the
copy). Before `remove` takes anything out, the copy's test-run records — and its failed files' kept outputs — are copied
into the main folder's records, in their own archive folder (rw-test-results/copies/<name>-<when removed>/, which the
runner never reads nor prunes), with time.json and time.txt: made → removed, its test runs (how many, their minutes —
overlapping runs counted once — full or narrow, passed or failed, reruns alone), its commits, and everything else. If
they can't be kept, nothing is removed (even with --force). The copy's own folder of them goes when git removes the copy.
The narrowed runs — the commit hook's --changed, --id, --tag, RW_CELLS — keep their records on the quick shelf
(rw-test-results/quick/, run_tests.py QUICK_SHELF, 2026-11-18): archived with the rest, counted, and labelled "quick".
The archive is kept bounded (2026-11-18): after each removal, the newest ARCHIVE_KEEP (100) copies' folders are kept, and
every one removed less than ARCHIVE_MIN_DAYS (30) days ago; the older rest is deleted, said (trim_archive).

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
main folder's linked folders are checked afterwards. A clone is then renamed aside (that fails, touching nothing, while a
program still has a file open there) and deleted.

Nothing here stops a process. Tested by test/test_copies.py.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import stat
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = (".venv", "node_modules", "tools/build/node_modules", "relay/node_modules")
RESULTS = "rw-test-results"      # run_tests.py RESULTS_NAME: a folder's records, in its own git folder
ARCHIVE = "copies"               # run_tests.py COPIES_ARCHIVE: removed copies' records, inside the main folder's (COPY-007)
QUICK = "quick"                  # run_tests.py QUICK_SHELF: the narrowed runs' records (--changed, --id…) — COPY-010
# The archive is kept bounded (TODO tooling 13.5, 2026-11-18): at each removal, the newest ARCHIVE_KEEP copies' folders
# are kept — and every one removed less than ARCHIVE_MIN_DAYS ago, however many; the older rest is deleted (trim_archive).
ARCHIVE_KEEP = 100
ARCHIVE_MIN_DAYS = 30
EXIT_NOT_PROVEN = 3              # run_tests.py's exit when no test failed but a file is NOT PROVEN (the machine too busy)
NOTE = "rw-copy.json"            # when `new` made the copy — in the copy's own git folder, gone with it
# A clone's name for the main folder's repository — how a copy finds the main folder (git-hooks/private_values.py reads
# it too, for the private note). (2026-11-19)
MAIN_REMOTE = "main-folder"
COPIED_SETTINGS = ("user.name", "user.email")    # the main folder's own settings a clone gets (it brings none)
MAIN_REFS = "refs/rw-main/"      # where `remove` fetches the main folder's branches and tags into a clone, to compare
NARROWING_ENV = ("RW_CELLS",)    # run_tests.py RUN_ENV's narrowing variables — COPY-007 checks they're the same
EVERYTHING_ELSE = "building, reading, thinking, waiting — the records can't tell these apart"
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


def main_url(folder):
    """The main folder a clone copy was made from (its MAIN_REMOTE), or '' — the main folder, a worktree, not a copy."""
    return git(folder, "config", "--get", f"remote.{MAIN_REMOTE}.url").stdout.strip()


def main_folder(repo=ROOT):
    """The main working folder: a clone copy's MAIN_REMOTE; else the one whose .git a worktree copy shares."""
    url = main_url(repo)
    if url:
        return os.path.normpath(url)
    common = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir", check=True).stdout.strip()
    common = os.path.normpath(common)
    if os.path.basename(common) != ".git":
        raise SystemExit(f"{repo}: its git folder ({common}) isn't a main folder's .git — not supported")
    return os.path.dirname(common)


def copies_dir(main):
    """Where the copies live: beside the main folder — C:\\Users\\Ron\\Projects\\ReaderWrangler-copies (Ron, 2026-11-16)."""
    return main.rstrip("\\/") + "-copies"


def copy_name(root=ROOT):
    """The name of the working copy `root` is — its folder name when it's a clone copy (it names the main folder) or a
    worktree (its .git is a FILE) — or None for the main folder. The screen tests use it to keep each copy's screenshots
    apart (test/ui/rw.py)."""
    dot_git = os.path.join(root, ".git")
    is_copy = os.path.isfile(dot_git) or (os.path.isdir(dot_git) and main_url(root))
    return os.path.basename(os.path.normpath(root)) if is_copy else None


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


def git_path(folder, name):
    """The absolute path of `name` in the folder's own git folder (a copy's: .git/worktrees/<its name>/<name>)."""
    return os.path.normpath(git(folder, "rev-parse", "--path-format=absolute", "--git-path", name, check=True)
                            .stdout.strip())


def _now():
    return datetime.datetime.now().astimezone()


def _when(text):
    """A record's or note's time (ISO 8601, with its offset), or None."""
    try:
        t = datetime.datetime.fromisoformat(str(text))
    except (TypeError, ValueError):
        return None
    return t if t.tzinfo else t.astimezone()


def _write_json(path, data):
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(path + ".tmp", path)


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


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


def find_copies(main):
    """Every working copy beside the main folder: [{name, path, kind, head, branch}], by name — kind "clone" (made since
    2026-11-19: its own repository, naming this main folder) or "worktree" (made before: git lists it)."""
    home = copies_dir(main)
    found = {}
    for w in worktrees(main):
        if _same(os.path.dirname(w["path"]), home):
            found[os.path.normcase(w["path"])] = dict(w, name=os.path.basename(w["path"]), kind="worktree")
    for e in sorted(os.scandir(home), key=lambda e: e.name) if os.path.isdir(home) else []:
        # (a name starting with "." is a removal's leftover — remove renames a clone aside before deleting it)
        if (e.name.startswith(".") or os.path.normcase(e.path) in found or is_link(e.path)
                or not os.path.isdir(os.path.join(e.path, ".git")) or not _same(main_url(e.path) or "-", main)):
            continue
        found[os.path.normcase(e.path)] = {
            "name": e.name, "path": os.path.normpath(e.path), "kind": "clone",
            "head": git(e.path, "rev-parse", "--verify", "--quiet", "HEAD").stdout.strip() or None,
            "branch": git(e.path, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip() or None}
    return sorted(found.values(), key=lambda c: c["name"])


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


class Unscannable(Exception):
    """Folders find_links couldn't look into — a link inside one would be missed (2026-11-16)."""

    def __init__(self, folders):
        self.folders = folders
        super().__init__("couldn't look into: " + "; ".join(f"{d} ({why})" for d, why in folders))


def find_links(top):
    """Every link anywhere inside `top` (not followed into), outside .git. A folder it can't look into isn't skipped: a
    link in it would be missed, and `git worktree remove` would delete through it — so it raises Unscannable, naming
    every such folder (after looking through all the others)."""
    found, stack, unread = [], [top], []
    while stack:
        d = stack.pop()
        try:
            entries = list(os.scandir(d))
        except OSError as err:
            unread.append((d, err.strerror or type(err).__name__))
            continue
        for e in entries:
            if is_link(e.path):
                found.append(e.path)
            elif e.is_dir(follow_symlinks=False) and e.name != ".git":
                stack.append(e.path)
    if unread:
        raise Unscannable(unread)
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
    # One copy per branch (a worktree had it from git; two clones on one branch would each move it their own way)
    if git(main, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip() == branch:
        raise SystemExit(f"the main folder is on {branch} — a copy builds on a branch of its own (--branch)")
    taken = [c["name"] for c in find_copies(main) if c["branch"] == branch]
    if taken:
        raise SystemExit(f"branch {branch} is being built in the copy {taken[0]} — one copy per branch")
    exists = git(main, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0
    if exists and a.from_ref:
        raise SystemExit(f"branch {branch} already exists — --from is only for a new branch (or name another --branch)")
    if exists:
        switch = ["switch", "-q", branch]
        made = f"on the existing branch {branch}"
    else:
        start = git(repo, "rev-parse", "--verify", "--quiet", f"{a.from_ref or 'HEAD'}^{{commit}}").stdout.strip()
        if not start:
            raise SystemExit(f"{a.from_ref!r} isn't a commit here")
        switch = ["switch", "-q", "-c", branch, start]
        made = f"on a new branch {branch}, from {a.from_ref or 'HEAD'} ({start[:12]})"
    os.makedirs(copies_dir(main), exist_ok=True)
    # Its own repository: the history shared through file links (same drive), every setting its own (2026-11-19)
    r = git(main, "clone", "--quiet", "--local", "--no-checkout", "--origin", MAIN_REMOTE, main, dest)
    if r.returncode == 0:
        r = git(dest, *switch)
    if r.returncode:
        raise SystemExit(f"git couldn't make the copy:\n{(r.stderr or r.stdout).strip()}"
                         + (f"\n(what it made is in {dest} — look, then delete it)" if os.path.exists(dest) else ""))
    for other in git(dest, "for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split():
        if other != branch:                  # the clone's starting branch: one branch per copy
            git(dest, "branch", "-q", "-D", other)
    for key in COPIED_SETTINGS:
        value = git(main, "config", "--local", "--get", key).stdout.strip()
        if value:
            git(dest, "config", key, value, check=True)
    git(dest, "config", "core.hooksPath", "git-hooks", check=True)      # the commit checks on
    exclude = git_path(main, "info/exclude")                            # the main folder's own ignore list
    if os.path.isfile(exclude):
        os.makedirs(os.path.dirname(git_path(dest, "info/exclude")), exist_ok=True)
        shutil.copyfile(exclude, git_path(dest, "info/exclude"))
    print(f"· made {dest} — its own clone of the main folder's repository, {made}")
    note_path = git_path(dest, NOTE)
    note = {"name": a.name, "branch": branch, "made": _now().isoformat(timespec="seconds"),
            "start": git(dest, "rev-parse", "HEAD").stdout.strip() or None}
    _write_json(note_path, note)

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

    print("· tier 1 in the copy (py tools/run_tests.py --tier 1) …", flush=True)
    code = subprocess.run([sys.executable, os.path.join(dest, "tools", "run_tests.py"), "--tier", "1"], cwd=dest,
                          env=_env()).returncode
    # Runs that began before this are the copy's making, not its work (where its time went, at removal).
    _write_json(note_path, {**note, "ready": _now().isoformat(timespec="seconds"), "ready_passed": code == 0})
    if code == EXIT_NOT_PROVEN:     # no test failed — the machine was too busy to prove it (TODO tooling 13.12)
        print(f"NOT READY — tier 1 not proven in {dest} — the machine was too busy (no test failed; above). Run it again "
              f"there when the PC is quieter (py tools/run_tests.py --tier 1), or  py tools/copies.py remove {a.name} "
              "--force  removes it.")
        return 1
    if code:
        print(f"NOT READY — tier 1 failed in {dest} (above). It's left as it is for a look; "
              f"py tools/copies.py remove {a.name} --force  removes it.")
        return 1
    print(f"READY — {dest}, branch {branch}. Its commits stay in the copy until the merge fetches them (py "
          f"tools/merge_branches.py {branch}, in the main folder); then:  py tools/copies.py remove {a.name}")
    return 0


# --- where a copy's time went (TODO tooling item 11.6, 2026-11-18) ------------------------------------------------------
def narrowed(rec):
    """What narrowed a run to part of its tier, in words ([] = a full run) — as run_tests.py narrowed_by judges what was
    ASKED: --changed (the commit hook), --tag, --id, a narrowing variable."""
    ran = rec.get("ran") or {}
    return (["--changed"] if ran.get("changed") else []) \
        + ([f"--tag {', '.join(ran['tags'])}"] if ran.get("tags") else []) \
        + ([f"--id {', '.join(ran['ids'])}"] if ran.get("ids") else []) \
        + [f"{k}={v}" for k, v in (rec.get("env") or {}).items() if k in NARROWING_ENV and v]


def covered_seconds(spans):
    """The seconds the spans [(start, end)] cover together — overlapping spans counted once."""
    total, cur = 0.0, None
    for s, e in sorted(sp for sp in spans if sp[1] > sp[0]):
        if cur and s <= cur[1]:
            cur[1] = max(cur[1], e)
            continue
        if cur:
            total += (cur[1] - cur[0]).total_seconds()
        cur = [s, e]
    return total + ((cur[1] - cur[0]).total_seconds() if cur else 0.0)


def made_estimate(dest):
    """When git made the copy's own folder — the made time of a copy that has no note (made before `new` wrote one)."""
    try:
        return datetime.datetime.fromtimestamp(os.stat(git_path(dest, "commondir")).st_mtime).astimezone()
    except (OSError, SystemExit):
        return None


def commits_since(copy, head, note, made):
    """[{hash, when, subject}] — the commits on the copy's own line since it was made (oldest first). Asked of the copy
    itself: a clone's commits may be nowhere else."""
    fmt = "--format=%h%x09%cI%x09%s"
    if note.get("start") and head:
        r = git(copy, "log", "--first-parent", "--reverse", fmt, f"{note['start']}..{head}")
    elif made and head:
        r = git(copy, "log", "--first-parent", "--reverse", fmt, f"--since={made.isoformat()}", head)
    else:
        return []
    return [dict(zip(("hash", "when", "subject"), ln.split("\t", 2))) for ln in r.stdout.splitlines() if ln.strip()]


def where_time_went(name, branch, note, made, estimated, records, commits, removed):
    """The summary kept as time.json (and said as time.txt)."""
    ready = _when(note.get("ready"))
    runs, spans = [], []
    for r in sorted(records, key=lambda x: str(x.get("started", ""))):
        s, e = _when(r.get("started")), _when(r.get("ended"))
        if s and not e and isinstance(r.get("seconds"), (int, float)):
            e = s + datetime.timedelta(seconds=r["seconds"])
        why = narrowed(r)
        if s and e:
            spans.append((max(s, made) if made else s, min(e, removed)))
        runs.append({"id": r.get("id"), "started": r.get("started"), "ended": r.get("ended"),
                     "seconds": round((e - s).total_seconds()) if s and e else None,
                     "tier": str((r.get("ran") or {}).get("tier") or "?"), "full": not why, "narrowed_by": why,
                     "quick": bool(r.get("_quick")),
                     "result": r.get("result") or "unknown",
                     "reruns_alone": sum(len(f.get("retried") or []) for f in r.get("files") or []),
                     "readiness": bool(ready and s and s < ready and not why)})
    wall = max(0.0, (removed - made).total_seconds()) if made else None
    tests = covered_seconds(spans)
    return {"name": name, "branch": branch, "made": made.isoformat(timespec="seconds") if made else None,
            "made_estimated": estimated, "removed": removed.isoformat(timespec="seconds"),
            "wall_seconds": None if wall is None else round(wall), "test_seconds": round(tests),
            "everything_else_seconds": None if wall is None else round(max(0.0, wall - tests)),
            "everything_else_is": EVERYTHING_ELSE,
            "counts": {"runs": len(runs), "full": sum(r["full"] for r in runs),
                       "narrow": sum(not r["full"] for r in runs), "quick": sum(r["quick"] for r in runs),
                       "passed": sum(r["result"] == "passed" for r in runs),
                       "failed": sum(r["result"] != "passed" for r in runs),
                       "reruns_alone": sum(r["reruns_alone"] for r in runs),
                       "readiness": sum(r["readiness"] for r in runs)},
            "runs": runs, "commits": commits}


def minutes(seconds):
    if seconds is None:
        return "?"
    m = seconds / 60
    return f"{m:.1f} min" if m < 10 else f"{m:.0f} min" if m < 60 else f"{int(m // 60)} h {int(m % 60):02d} min"


def share(part, whole):
    return f"{100 * part / whole:.0f}%" if whole else "?"


def time_text(s, kept):
    """time.txt — and what the removal prints."""
    n, wall, tests = s["counts"], s["wall_seconds"], s["test_seconds"]
    made = (s["made"] or "?")[:19].replace("T", " ")
    lines = [f"Where the time of copy {s['name']} (branch {s['branch'] or '(detached)'}) went:",
             f"  made {made}" + (" (estimated — when git made its folder; made before copies.py noted the time)"
                                 if s["made_estimated"] else "")
             + f" → removed {s['removed'][:19].replace('T', ' ')}: {minutes(wall)}",
             f"  test runs: {n['runs']} — {minutes(tests)} ({share(tests, wall)} of it; runs that overlapped counted once)",
             f"      {n['full']} full" + (f" ({n['readiness']} of them the tier 1 that `new` ran to make it ready)"
                                         if n["readiness"] else "")
             + f", {n['narrow']} narrow"
             + (f" ({n.get('quick', 0)} quick — on the quick shelf: the commit hook's --changed and other narrowed runs)"
                if n.get("quick") else "")
             + f" · {n['passed']} passed, {n['failed']} failed"
             + f" · {n['reruns_alone']} file(s) rerun alone after the machine's or the browser's trouble"]
    for r in s["runs"]:
        lines.append(f"      {str(r['started'] or '?')[11:19]}  {minutes(r['seconds']):>9}  tier {r['tier']:<3}  "
                     f"{r['result']:<7} " + ("full" + (" (making it ready)" if r["readiness"] else "")
                                             if r["full"] else ("quick: " if r.get("quick") else "narrow: ")
                                             + "; ".join(r["narrowed_by"]))
                     + (f" · {r['reruns_alone']} rerun alone" if r["reruns_alone"] else ""))
    lines.append(f"  everything else: {minutes(s['everything_else_seconds'])} ({share(s['everything_else_seconds'] or 0, wall)}"
                 f") — {s['everything_else_is']}")
    lines.append(f"  commits on its branch since it was made: {len(s['commits'])}")
    lines += [f"      {c['hash']}  {c['when'][:16].replace('T', ' ')}  {c['subject'][:90]}" for c in s["commits"]]
    lines.append(f"  kept: {kept}  (its run records, failed outputs, time.json, time.txt — py tools/copies.py report)")
    return "\n".join(lines)


def keep_records(main, dest, name, branch, head):
    """Copy the copy's test-run records (and kept outputs) into the main folder's archive, with its time summary — BEFORE
    anything is removed. Returns (archive folder, the summary's text). Anything fails: the partial archive is taken back
    and the removal stops (SystemExit) — records are never lost silently."""
    src = git_path(dest, RESULTS)
    home = os.path.join(git_path(main, RESULTS), ARCHIVE)
    removed = _now()
    note = _read_json(git_path(dest, NOTE)) or {}
    made, estimated = _when(note.get("made")), False
    if made is None:
        made, estimated = made_estimate(dest), True
    target = os.path.join(home, f"{name}-{removed:%Y%m%d-%H%M}")
    k = 2
    while os.path.lexists(target):
        target = os.path.join(home, f"{name}-{removed:%Y%m%d-%H%M}-{k}")
        k += 1
    try:
        os.makedirs(home, exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, target)
        else:
            os.makedirs(target)
        missing = [os.path.relpath(os.path.join(d, f), src) for d, _, fs in os.walk(src) for f in fs
                   if not os.path.exists(os.path.join(target, os.path.relpath(os.path.join(d, f), src)))]
        if missing:
            raise OSError(f"not copied: {', '.join(missing[:5])}")
        records = [r for r in (_read_json(os.path.join(target, f)) for f in os.listdir(target) if f.endswith(".json"))
                   if r is not None]
        shelf = os.path.join(target, QUICK)         # the narrowed runs' records (--changed, --id…): counted, labelled
        records += [dict(r, _quick=True) for r in (_read_json(os.path.join(shelf, f)) for f in
                    (os.listdir(shelf) if os.path.isdir(shelf) else []) if f.endswith(".json")) if r is not None]
        summary = where_time_went(name, branch, note, made, estimated, records,
                                  commits_since(dest, head, note, made), removed)
        text = time_text(summary, target)
        _write_json(os.path.join(target, "time.json"), {**summary, "note": note})
        with open(os.path.join(target, "time.txt"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
    except (OSError, shutil.Error) as e:
        if os.path.isdir(target):
            shutil.rmtree(target, ignore_errors=True)
        raise SystemExit(f"NOT REMOVED — nothing was touched: the copy's test-run records couldn't be kept in "
                         f"{target}:\n  {e}\nThey're still in {src}. Fix that (or move them by hand), then run this "
                         "again.")
    return target, text


def trim_archive(home, keep=None, min_days=None, now=None):
    """Keep the archive bounded (TODO tooling 13.5 — it grew forever): the newest `keep` copies' folders (ARCHIVE_KEEP)
    are kept, and EVERY one removed less than `min_days` (ARCHIVE_MIN_DAYS) ago, however many; the older rest is deleted.
    A folder's age is its time.json's "removed" — else the folder's own time. Files there are left alone. Returns the
    names deleted."""
    keep = ARCHIVE_KEEP if keep is None else keep
    min_days = ARCHIVE_MIN_DAYS if min_days is None else min_days
    now = now or _now()
    dated = []
    for name in os.listdir(home) if os.path.isdir(home) else []:
        folder = os.path.join(home, name)
        if not os.path.isdir(folder) or is_link(folder):
            continue
        when = _when((_read_json(os.path.join(folder, "time.json")) or {}).get("removed"))
        if when is None:
            try:
                when = datetime.datetime.fromtimestamp(os.stat(folder).st_mtime).astimezone()
            except OSError:
                continue            # can't be dated: kept
        dated.append((when, name))
    dated.sort(reverse=True)
    gone = []
    for when, name in dated[keep:]:
        if (now - when).total_seconds() < min_days * 86400:
            continue
        shutil.rmtree(os.path.join(home, name), ignore_errors=True)
        if not os.path.exists(os.path.join(home, name)):
            gone.append(name)
    return gone


# --- getting the work back (tools/merge_branches.py, before it merges) --------------------------------------------------
def fetch_from_copies(folder, branches):
    """Bring each branch being built in a clone copy into `folder`'s repository (the main folder, where the merge runs):
    fetched from the copy that has it, fast-forward only. Already here (the copy's tip is in this folder's branch):
    nothing. Returns (lines said, problems) — a problem: the branch moved on BOTH sides, or it is this folder's own
    branch; nothing is changed for that branch. Worktree copies share this repository already: nothing to fetch."""
    main = main_folder(folder)
    here = git(folder, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
    clones = [c for c in find_copies(main) if c["kind"] == "clone" and not _same(c["path"], folder)]
    said, problems = [], []
    for b in branches:
        for c in clones:
            tip = git(c["path"], "rev-parse", "--verify", "--quiet", f"refs/heads/{b}^{{commit}}").stdout.strip()
            if not tip:
                continue
            ours = git(folder, "rev-parse", "--verify", "--quiet", f"refs/heads/{b}^{{commit}}").stdout.strip()
            if ours and git(folder, "merge-base", "--is-ancestor", tip, ours).returncode == 0:
                continue                                 # already here
            if b == here:
                problems.append(f"{b} is this folder's own branch, and the copy {c['name']} has commits on it this "
                                "folder hasn't got — a copy builds on a branch of its own")
                continue
            r = git(folder, "fetch", "--quiet", "--no-tags", c["path"], f"refs/heads/{b}:refs/heads/{b}")
            if r.returncode:
                problems.append(f"{b} has moved on both in the copy {c['name']} and here — look at both before "
                                f"merging:\n    {(r.stderr or r.stdout).strip()}")
            else:
                said.append(f"· {b}: fetched from the copy {c['name']} ({tip[:12]})")
    return said, problems


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


def missing_from_main(main, dest):
    """How many commits a clone copy holds — on any of its branches or its HEAD — that the main folder's repository
    doesn't (on a branch or tag there). The main folder's branches and tags are fetched fresh into the clone to compare
    (its own refs, under MAIN_REFS — the clone is about to go); nothing in the main folder changes."""
    git(dest, "fetch", "--quiet", "--no-tags", "--prune", main, f"+refs/heads/*:{MAIN_REFS}heads/*",
        f"+refs/tags/*:{MAIN_REFS}tags/*", check=True)
    r = git(dest, "rev-list", "--count", "HEAD", "--branches", "--not", f"--glob={MAIN_REFS}*", check=True)
    return int(r.stdout.strip() or 0)


def move_aside(dest):
    """Rename a clone copy out of the way before taking it apart — Windows refuses that while a program has a file open
    in it, so a busy copy is left whole, never half-deleted. The new name starts with "." (find_copies skips it). Returns
    it, or None when the rename was refused."""
    aside = os.path.join(os.path.dirname(dest), f".removing-{os.path.basename(dest)}-{_now():%Y%m%d-%H%M%S}")
    try:
        os.rename(dest, aside)
    except OSError:
        return None
    return aside


def delete_folder(top):
    """Delete a folder that holds no link any more (find_links, then each removed). git's stored files are read-only on
    Windows: made writable, then deleted. Returns True when it's gone."""
    def writable_then_retry(func, path, _exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    try:
        shutil.rmtree(top, onexc=writable_then_retry)
    except OSError:
        pass
    return not os.path.exists(top)


def cmd_remove(a, repo):
    main = main_folder(repo)
    dest = os.path.join(copies_dir(main), a.name)
    wt = next((c for c in find_copies(main) if _same(c["path"], dest)), None)
    if wt is None:
        raise SystemExit(f"{dest} isn't a working copy of this repository (py tools/copies.py list)")
    if _same(repo, dest) or _same(os.getcwd(), dest):
        raise SystemExit("run this from another folder — not from inside the copy being removed")
    clone = wt["kind"] == "clone"
    where = f"branch {wt['branch']}" if wt["branch"] else f"a detached HEAD ({(wt['head'] or '')[:12]})"
    thrown = 0                                       # a clone's commits the main folder hasn't got (--force throws them)
    if not a.force:
        dirty = [ln for ln in git(dest, "status", "--porcelain", "--untracked-files=normal", check=True).stdout
                 .splitlines() if ln.strip()]
        if dirty:
            raise SystemExit(f"NOT REMOVED — {dest} has uncommitted changes:\n  " + "\n  ".join(dirty[:10])
                             + (f"\n  (+{len(dirty) - 10} more)" if len(dirty) > 10 else "")
                             + "\nCommit them, or --force to throw them away.")
        n = missing_from_main(main, dest) if clone else unique_commits(main, wt)
        if n and clone:
            raise SystemExit(f"NOT REMOVED — the copy holds {n} commit(s) the main folder's repository doesn't have "
                             f"(on {where} or another of its branches). Merge them first — py tools/merge_branches.py "
                             f"{wt['branch'] or '<branch>'}, in the main folder, fetches the branch from the copy — or "
                             "--force throws them away with the copy.")
        if n:
            raise SystemExit(f"NOT REMOVED — {where} has {n} commit(s) that exist nowhere else (no other branch, tag "
                             "or remote). Merge them first — or --force: the copy goes, the branch stays.")
    elif clone:
        try:
            thrown = missing_from_main(main, dest)
        except SystemExit:
            thrown = "an unknown number of"
    held = {rel: sorted(os.listdir(os.path.join(main, rel))) for rel in LINKS if os.path.isdir(os.path.join(main, rel))}
    # The links FIRST — `git worktree remove` would delete the main folder's files through them (see the top). Every
    # folder must be looked into before anything is removed: one that can't be might hold a link (even --force stops).
    try:
        links = find_links(dest)
    except Unscannable as e:
        raise SystemExit(f"NOT REMOVED — nothing was touched: these folders in the copy can't be looked into, so a link "
                         f"inside one would be missed and git's remove would delete what it points at:\n  "
                         + "\n  ".join(f"{d} ({why})" for d, why in e.folders)
                         + "\nMake them readable again (or remove each link in them by hand), then run this again.")
    # Its test-run records kept, with where its time went — before anything is taken out (a failure stops here).
    kept, time_said = keep_records(main, dest, a.name, wt["branch"], wt["head"])
    top = dest
    if clone:
        top = move_aside(dest)
        if top is None:
            shutil.rmtree(kept, ignore_errors=True)    # the records are still in the copy — kept again next time
            raise SystemExit(f"NOT REMOVED — nothing was touched: a program still has a file open in {dest} (an editor, "
                             "a server, a terminal in it?). Close it and run this again. (Its test-run records stay in "
                             "the copy; the archive made for them was taken back.)")
    for link in sorted(links, key=len, reverse=True):
        link = os.path.join(top, os.path.relpath(link, dest))
        remove_link(link)
        if os.path.lexists(link):
            if clone:
                os.rename(top, dest)                   # back where it was, so `remove` can be run again
            raise SystemExit(f"couldn't remove the link {link} — stopped before removing the copy")
        print(f"· unlinked {os.path.relpath(link, top)}")
    if clone:
        if not delete_folder(top):
            print(f"!! the copy is out of the way, but some of its files couldn't be deleted — what's left is in {top} "
                  "(no links in it any more: safe to delete by hand)")
        said = (f"!! thrown away with it: {thrown} commit(s) the main folder's repository didn't have" if thrown
                else "every commit in it is in the main folder's repository")
    else:
        r = git(main, "worktree", "remove", "--force", dest)
        if r.returncode or os.path.exists(dest):
            shutil.rmtree(kept, ignore_errors=True)    # the records are still in the copy — kept again next time
            raise SystemExit(f"git couldn't remove {dest} (a program still using a file there?):\n"
                             f"{(r.stderr or r.stdout).strip()}\n(Its test-run records stay in the copy; the archive "
                             "made for them was taken back.)")
        said = f"{where} kept"
    # Checked, not assumed: each linked folder of the main folder still holds what it held before.
    lost = [rel for rel, names in held.items() if not os.path.isdir(os.path.join(main, rel))
            or not set(names) <= set(os.listdir(os.path.join(main, rel)))]
    if lost:
        print(f"REMOVED {dest} — {said}.\n!! THE MAIN FOLDER LOST FILES in {', '.join(lost)} — set them up again "
              "(docs/design/TESTING.md §4) and report this: the links were supposed to be removed first.")
        print(time_said)
        return 1
    print(f"REMOVED {dest} — {said}. The main folder's {', '.join(held)} still hold everything they held.")
    print(time_said)
    gone = trim_archive(os.path.dirname(kept))
    if gone:
        print(f"· the archive trimmed: {len(gone)} older copies' records deleted ({', '.join(sorted(gone)[:5])}"
              + (" …" if len(gone) > 5 else "") + f") — kept: the newest {ARCHIVE_KEEP}, and every one removed less "
              f"than {ARCHIVE_MIN_DAYS} days ago")
    return 0


# --- report -------------------------------------------------------------------------------------------------------------
def cmd_report(a, repo):
    """One row per removed copy whose records were kept (rw-test-results/copies/*/time.json), then the totals."""
    since = None
    if a.since:
        try:
            since = datetime.date.fromisoformat(a.since)
        except ValueError:
            raise SystemExit(f"--since {a.since!r}: a date, YYYY-MM-DD")
    home = os.path.join(git_path(main_folder(repo), RESULTS), ARCHIVE)
    rows, unread = [], []
    for d in sorted(os.listdir(home)) if os.path.isdir(home) else []:
        s = _read_json(os.path.join(home, d, "time.json"))
        if s is None:
            unread.append(d)
            continue
        removed = _when(s.get("removed"))
        if since and removed and removed.date() < since:
            continue
        rows.append(s)
    rows.sort(key=lambda s: str(s.get("removed")))
    head = ("copy", "branch", "made", "removed", "wall", "tests", "share", "runs full/narrow", "passed/failed")

    def cells(name, branch, made, removed, wall, tests, n):
        return (name, branch, made, removed, minutes(wall), minutes(tests), share(tests, wall),
                f"{n['runs']}: {n['full']}/{n['narrow']}", f"{n['passed']}/{n['failed']}")
    table = [cells(s.get("name", "?"), s.get("branch") or "(detached)",
                   (s.get("made") or "?")[:16].replace("T", " ") + ("~" if s.get("made_estimated") else ""),
                   str(s.get("removed", "?"))[:16].replace("T", " "), s.get("wall_seconds"), s.get("test_seconds", 0),
                   s.get("counts") or {}) for s in rows]
    if not rows:
        print(f"No removed copies' records kept{f' since {since}' if since else ''} (in {home}).")
    else:
        keys = ("runs", "full", "narrow", "passed", "failed")
        total = {k: sum((s.get("counts") or {}).get(k, 0) for s in rows) for k in keys}
        walls = [s.get("wall_seconds") for s in rows if s.get("wall_seconds") is not None]
        tests = sum(s.get("test_seconds") or 0 for s in rows if s.get("wall_seconds") is not None)
        table.append(cells(f"total ({len(rows)} copies)", "", "", "", sum(walls), tests, total))
        widths = [max(len(str(r[i])) for r in [head] + table) for i in range(len(head))]
        for i, r in enumerate([head] + table):
            if i == len(table):          # (the totals row, after a rule)
                print("  ".join("-" * w for w in widths))
            print("  ".join(str(c).ljust(w) for c, w in zip(r, widths)).rstrip())
        print(f"(tests = the minutes its test runs covered, overlaps once; the rest of the wall time is {EVERYTHING_ELSE}"
              f". ~ = made time estimated. Each copy's runs: {os.path.join(home, '<copy>-<when>', 'time.txt')})")
    for d in unread:
        print(f"! {os.path.join(home, d)}: no readable time.json")
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
    found = find_copies(main)
    here = {"name": "(main folder)", "path": main, "kind": None,
            "branch": git(main, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip() or None}
    for w in [here] + found:
        dirty = git(w["path"], "status", "--porcelain", "--untracked-files=normal").stdout.splitlines()
        subject = git(w["path"], "log", "-1", "--format=%h %s").stdout.strip()
        kind = {"clone": "  (its own clone)", "worktree": "  (a worktree — made before 2026-11-19)"}.get(w["kind"], "")
        print(f"{w['name']}  —  {w['path']}{kind}\n    branch {w['branch'] or '(detached)'}: {subject[:100]}"
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
    ap = argparse.ArgumentParser(description="Working copies of the project folder (local clones with the tools "
                                             "linked in). Docs: docs/design/SESSION-TOOLING.md.")
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("new", help="make a copy, link the tools, run tier 1 there")
    n.add_argument("name")
    n.add_argument("--branch", help="its branch (default: the name); an existing branch is checked out")
    n.add_argument("--from", dest="from_ref", help="where a NEW branch starts (default: HEAD)")
    r = sub.add_parser("remove", help="remove a copy (links first) — refused while it holds work found nowhere else")
    r.add_argument("name")
    r.add_argument("--force", action="store_true", help="even with uncommitted changes or commits the main folder "
                                                        "hasn't got (thrown away, said)")
    sub.add_parser("list", help="each copy, its branch and its test stamp")
    p = sub.add_parser("report", help="where each removed copy's time went: wall, test minutes, runs — and totals")
    p.add_argument("--since", help="only copies removed on or after this day (YYYY-MM-DD)")
    a = ap.parse_args(argv)
    if a.cmd == "new":
        return cmd_new(a, repo)
    if a.cmd == "remove":
        return cmd_remove(a, repo)
    if a.cmd == "report":
        return cmd_report(a, repo)
    return cmd_list(a, repo)          # "list", or nothing (a double-click)


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)   # the pytools submodule lives at the repo root
    try:
        from pytools.keepopen import run
    except ImportError:
        sys.exit(main())
    run(main, pause="always")
