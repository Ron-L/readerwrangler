#!/usr/bin/env python3
"""
copies.py — working copies of the project folder (TODO "Faster sprints", item 3; Ron's idea, 2026-11-15).

A working copy is a git worktree of this repository: its own folder, on its own branch, sharing one history with the main
folder. One agent builds in one copy while Claude reviews and tests in another, and independent tasks build at once.

    py tools/copies.py new <name> [--branch <b>] [--from <ref>]
        make  ..\\ReaderWrangler-copies\\<name>  on branch <b> (default: <name>; made from <ref>, default HEAD, when it
        doesn't exist yet), link in what git doesn't hold, check out the submodule, then run tier 1 there — it's READY
        only if tier 1 passes (NOT READY says "not proven — the machine was too busy" when no test failed: exit 3)
    py tools/copies.py remove <name> [--force]
        refuse if the copy has anything uncommitted, or its branch has commits that exist nowhere else (no other branch,
        tag or remote) — --force removes it anyway; the BRANCH IS ALWAYS KEPT. Removes the links FIRST, then the copy —
        and refuses, even with --force, while any folder in the copy can't be looked into (a link there would be missed)
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
main folder's linked folders are checked afterwards.

Nothing here stops a process. Tested by test/test_copies.py.
"""
import argparse
import datetime
import json
import os
import re
import shutil
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

    hooks = git(dest, "config", "core.hooksPath").stdout.strip()
    if hooks != "git-hooks":
        print(f"! the commit checks are OFF here: core.hooksPath is {hooks or 'not set'} — once, in the main folder: "
              "git config core.hooksPath git-hooks")

    print("· tier 1 in the copy (py tools/run_tests.py --tier 1) …", flush=True)
    code = subprocess.run([sys.executable, os.path.join(dest, "tools", "run_tests.py"), "--tier", "1"], cwd=dest,
                          env=_env()).returncode
    # Runs that began before this are the copy's making, not its work (where its time went, at removal).
    _write_json(note_path, {**note, "ready": _now().isoformat(timespec="seconds"), "ready_passed": code == 0})
    if code == EXIT_NOT_PROVEN:     # no test failed — the machine was too busy to prove it (TODO tooling 13.12)
        print(f"NOT READY — tier 1 not proven in {dest} — the machine was too busy (no test failed; above). Run it again "
              f"there when the PC is quieter (py tools/run_tests.py --tier 1), or  py tools/copies.py remove {a.name} "
              "--force  removes it (the branch stays).")
        return 1
    if code:
        print(f"NOT READY — tier 1 failed in {dest} (above). It's left as it is for a look; "
              f"py tools/copies.py remove {a.name} --force  removes it (the branch stays).")
        return 1
    print(f"READY — {dest}, branch {branch}. When done:  py tools/copies.py remove {a.name}")
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


def commits_since(main, head, note, made):
    """[{hash, when, subject}] — the commits on the copy's own line since it was made (oldest first)."""
    fmt = "--format=%h%x09%cI%x09%s"
    if note.get("start") and head:
        r = git(main, "log", "--first-parent", "--reverse", fmt, f"{note['start']}..{head}")
    elif made and head:
        r = git(main, "log", "--first-parent", "--reverse", fmt, f"--since={made.isoformat()}", head)
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
                                  commits_since(main, head, note, made), removed)
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
    for link in sorted(links, key=len, reverse=True):
        remove_link(link)
        if os.path.lexists(link):
            raise SystemExit(f"couldn't remove the link {link} — stopped before removing the copy")
        print(f"· unlinked {os.path.relpath(link, dest)}")
    r = git(main, "worktree", "remove", "--force", dest)
    if r.returncode or os.path.exists(dest):
        shutil.rmtree(kept, ignore_errors=True)        # the records are still in the copy — kept again next time
        raise SystemExit(f"git couldn't remove {dest} (a program still using a file there?):\n"
                         f"{(r.stderr or r.stdout).strip()}\n(Its test-run records stay in the copy; the archive made "
                         "for them was taken back.)")
    # Checked, not assumed: each linked folder of the main folder still holds what it held before.
    lost = [rel for rel, names in held.items() if not os.path.isdir(os.path.join(main, rel))
            or not set(names) <= set(os.listdir(os.path.join(main, rel)))]
    if lost:
        print(f"REMOVED {dest} — {where} kept.\n!! THE MAIN FOLDER LOST FILES in {', '.join(lost)} — set them up again "
              "(docs/design/TESTING.md §4) and report this: the links were supposed to be removed first.")
        print(time_said)
        return 1
    print(f"REMOVED {dest} — {where} kept. The main folder's {', '.join(held)} still hold everything they held.")
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
