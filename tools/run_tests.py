#!/usr/bin/env python3
"""
run_tests.py — the one test runner (docs/design/TESTING.md §4; Ron + Claude, 2026-11-04).

Finds every test file, reads its header, picks the ones asked for, runs each, and prints one summary.

    py tools/run_tests.py                     tier 1 (the default): the fast function tests
    py tools/run_tests.py --tier all          everything (tier 3 starts its own local relay — see below)
    py tools/run_tests.py --tier all --release   the release run: a SKIPPED file fails it, named with why — and so does
                                              a test still marked "differs today" (decided, not built), named
    py tools/run_tests.py --tag merge         by area — in every tier unless --tier says one
    py tools/run_tests.py --id MERGE-012      the file(s) holding that test ID — in every tier unless --tier says one
    py tools/run_tests.py --changed           the tests covering what changed (staged + unstaged) — the commit hook
    py tools/run_tests.py --list              show what would run, run nothing

Test files and their tiers:
    test/*.test.js        function tests (Node; test/harness.js)          tier from the header (normally 1)
    test/test_*.py        function tests in Python                         tier from the header (normally 1)
    test/ui/test_*.py     screen tests (the browser driver)                tier 2
    relay/test-*.mjs      relay tests                                      tier 3

Tier 3 starts its OWN local relay (tools/local_relay.py, 2026-11-12): relay-worker.js in wrangler's local emulator on a
free port with an empty, throwaway store; the relay files run against it; then every process it started is stopped by
exact id and CHECKED gone, and its ports checked free — anything left fails the run, named by id. Never the dev or
production relay. --relay-url <address> uses a relay you started instead (no start, no stop).

Every test file declares, in its first lines:   tags: <areas>, tier N     and     covers: <source files it tests>
A file without them is a failure ("headers are required") — the covers: lines are the one source for --changed.

In parallel (TODO "Faster sprints", item 1; 2026-11-16): tier 1 and tier 2 files run several at once — --jobs N, by
default the machine-wide limit — and every screen-test (tier 2) file holds one of the PC's test slots while it runs
(tools/test_slots.py: 4 in total for every run on this PC, whatever folder it's in; RW_TEST_SLOTS overrides). A run
waiting for a slot says so. Tier 3 stays one file at a time (its own local relay). One line per file as it finishes; a
failing file's details printed together; the same summary line at the end.

    py tools/run_tests.py --tier 2 --jobs 1   one file at a time, as before

One file split across processes (2026-11-16): a file whose header says `shards: N` (test/ui/test_cells.py) lists its
cells with `--list-cells` and runs as N processes at once — every Nth cell each, in RW_CELLS — each holding its own test
slot. It is still ONE file: passed only if every shard passed, one line with the counts summed (a failing shard's lines
under it, together, with its RW_CELLS to rerun just that shard), one entry in the record and the stamp. With RW_CELLS
already set (a narrow run) it runs as one process, as asked.

Results stamped with their commit (item 2): every run except --changed (the commit hook) and --list leaves a record —
the commit it ran on, anything uncommitted, what ran, the environment variables that change a run (RUN_ENV: RW_CELLS…),
each file's result, start and end — in git's own folder for this working copy (`git rev-parse --git-path
rw-test-results`: never in the working tree; a worktree has its own).

    py tools/run_tests.py --stamp [<commit>]  PROVEN (exit 0) only if tier 1 and tier 2 both ran in full on exactly that
                                              commit (default: HEAD) — not narrowed by --id, --tag or RW_CELLS — every
                                              file passed, nothing skipped, nothing uncommitted — else NOT PROVEN, and
                                              why (exit 1)

Double-clicked, the window stays open to show the results (pytools keepopen). Exit: 0 all passed · 1 a failure.
"""
import argparse
import concurrent.futures
import datetime
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_relay  # noqa: E402 — tools/local_relay.py, next to this file
import test_slots   # noqa: E402 — tools/test_slots.py: the machine-wide limit on screen tests at once

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Screen tests (tier 2) need Playwright, which lives in the project's venv (requirements-dev.txt) — never the system
# Python. Everything else runs with the Python that runs this script (the commit hook needs no venv).
VENV_PY = os.path.join(ROOT, ".venv", "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")
VENV_SETUP = "py -m venv .venv   then   .venv\\Scripts\\pip install -r requirements-dev.txt   (in the project folder)"
PATTERNS = ["test/*.test.js", "test/test_*.py", "test/ui/test_*.py", "relay/test-*.mjs"]
HEADER_LINES = 15


def read_header(path):
    """{'tags': [...], 'tier': int|None, 'covers': [...], 'shards': int, 'problem': str|None} from the file's first
    lines. `shards: N` (optional, 2026-11-16) — run the file as N processes, each with its share of its cells."""
    tags, tier, covers, shards, bad_shards = None, None, None, 1, None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = [next(f, "") for _ in range(HEADER_LINES)]
    except OSError as e:
        return {"tags": [], "tier": None, "covers": [], "shards": 1, "problem": f"can't read it: {e}"}
    for line in head:
        text = re.sub(r"^\s*(//+|#+|\*|/\*\*?)\s?", "", line).strip()
        m = re.match(r"tags:\s*(.*)$", text)
        if m:
            parts = [p.strip() for p in m.group(1).split(",") if p.strip()]
            tags = [p for p in parts if not re.fullmatch(r"tier\s*\d", p)]
            t = [int(re.search(r"\d", p).group()) for p in parts if re.fullmatch(r"tier\s*\d", p)]
            tier = t[0] if t else None
        m = re.match(r"covers:\s*(.*)$", text)
        if m:
            covers = [p.strip() for p in m.group(1).split(",") if p.strip()]
        m = re.match(r"shards:\s*(.*?)\s*$", text)
        if m:
            if re.fullmatch(r"[1-9]\d*", m.group(1)):
                shards = int(m.group(1))
            else:
                bad_shards = m.group(1)
    problem = None
    if tags is None or covers is None:
        problem = "no header — every test file needs 'tags: <areas>, tier N' and 'covers: <files>' in its first lines"
    elif tier is None:
        problem = "its tags: line names no tier ('tier 1', 'tier 2' or 'tier 3')"
    elif bad_shards is not None:
        problem = f"its shards: line says {bad_shards!r} — a whole number of processes, 1 or more (e.g. 'shards: 3')"
    return {"tags": tags or [], "tier": tier, "covers": covers or [], "shards": shards, "problem": problem}


class TestFile:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.__dict__.update(read_header(self.path))
        if self.path.endswith(".mjs") and self.tier is None:
            self.tier = 3

    def rel(self, base=ROOT):
        return os.path.relpath(self.path, base).replace("\\", "/")


def discover(root=ROOT):
    paths = sorted({p for pat in PATTERNS for p in glob.glob(os.path.join(root, pat))})
    return [TestFile(p) for p in paths]


def select(files, tier=None, tags=None, ids=None, changed=None, base=ROOT):
    """The files to run. tier: an int or 'all' (None = all); tags / ids: any match; changed: repo-relative paths —
    a file is picked when it covers one of them or is one of them."""
    out = []
    for f in files:
        if tier not in (None, "all") and f.tier != tier:
            continue
        if tags and not set(tags) & set(f.tags):
            continue
        if ids:
            try:
                text = open(f.path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if not any(re.search(r"\b" + re.escape(i) + r"\b", text) for i in ids):
                continue
        if changed is not None:
            ch = {c.replace("\\", "/") for c in changed}
            if not (set(f.covers) & ch or f.rel(base) in ch):
                continue
        out.append(f)
    return out


def default_tier(a):
    """The tier when none is given (2026-11-12): --id or --tag → every tier (they name what to run — a screen test's ID
    said "No tests match" when tier 1 was applied first); --changed → tier 1 (the commit hook: seconds, not minutes);
    nothing → tier 1."""
    return "all" if (a.id or a.tag) and not a.changed else 1


def skip_reason(tf):
    """Why this file won't run here — None = it runs. The ONE place a skip is decided. Nothing skips today: tier 3 brings
    its own relay (2026-11-12) and a missing tool fails loud (RUN-015). A reason added here is reported as skipped — and
    fails a --release run (7.28.0: "31 passed, 2 skipped" read as a pass)."""
    return None


def command(tf):
    """(the command that runs this file, None) — or (None, why it can't run here)."""
    if tf.path.endswith(".py") and tf.tier == 2:
        if not os.path.exists(VENV_PY):
            return None, f"screen tests need the project's venv (Playwright) — not found at {VENV_PY}.\n  Set it up: {VENV_SETUP}"
        return [VENV_PY, tf.path], None
    if tf.path.endswith(".py"):
        return [sys.executable, tf.path], None
    node = shutil.which("node")
    if not node:
        return None, "node isn't on the PATH"
    return [node, tf.path], None


def run_file(tf, relay_url=None, timeout=600, cells=None):
    """(passed?, output) — runs one test file from the repo root. cells: run only these (RW_CELLS — one shard)."""
    cmd, why = command(tf)
    if cmd is None:
        return False, why
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if relay_url:
        env["RELAY_URL"] = relay_url
    if cells is not None:
        env["RW_CELLS"] = ",".join(cells)
    try:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout} s"
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode == 0, out


# --- one file split across processes (2026-11-16, TODO "Faster sprints") ------------------------------------------------
# test_cells.py alone set tier 2's time (~5½ min; the other files finished alongside it). A file whose header says
# `shards: N` answers `--list-cells` with its cell IDs (one a line, running nothing) and runs only the cells named in
# RW_CELLS. The runner runs it as N processes — every Nth cell each — each holding its own test slot; the file's result
# is theirs together: passed only if every shard passed, the counts summed, one line, one entry in the record.
CELL_ID = re.compile(r"[A-Z][A-Z0-9]*-\d{3}")


def list_cells(tf, timeout=120):
    """(the file's cell IDs, in its order; None) — or (None, why they couldn't be listed)."""
    cmd, why = command(tf)
    if cmd is None:
        return None, why
    try:
        r = subprocess.run(cmd + ["--list-cells"], cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING="utf-8"),
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, f"listing its cells (--list-cells) timed out after {timeout} s"
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    ids = [ln.strip() for ln in out.splitlines() if CELL_ID.fullmatch(ln.strip())]
    if r.returncode or not ids:
        tail = "\n".join(out.strip().splitlines()[-6:])
        return None, (f"✗ its header says shards: {tf.shards}, but its cells couldn't be listed (--list-cells: exit "
                      f"{r.returncode}, {len(ids)} cell IDs)" + (f":\n      {tail}" if tail else ""))
    twice = sorted({i for i in ids if ids.count(i) > 1})
    if twice:
        return None, f"✗ its cell list (--list-cells) names some cells twice: {', '.join(twice)}"
    return ids, None


def shares(cells, n):
    """The cells split n ways — every nth cell each (neighbors, often alike in cost, spread out); never an empty share."""
    n = max(1, min(n, len(cells)))
    return [cells[i::n] for i in range(n)]


def combine_shards(parts):
    """One file's (passed?, output) from its shards' [(number, of, cells, passed?, output, seconds)]: each shard's output
    under a heading saying which cells it ran, then one summary line with the counts summed (what the runner reads)."""
    total, missing, lines = [0, 0, 0], [], []
    for k, n, cells, ok, out, secs in sorted(parts, key=lambda p: p[0]):
        lines.append(f"── shard {k} of {n}: {len(cells)} cells ({cells[0]} … {cells[-1]}) — "
                     + (f"passed in {secs:.0f} s" if ok else
                        f"FAILED in {secs:.0f} s — this shard alone: RW_CELLS={','.join(cells)}"))
        lines += out.rstrip("\n").splitlines()
        m = None
        for ln in reversed(out.splitlines()):
            m = re.search(r"(\d+) passed, (\d+) failed(?:, (\d+) differ today)?", ln)
            if m:
                break
        if m:
            total = [total[0] + int(m.group(1)), total[1] + int(m.group(2)), total[2] + int(m.group(3) or 0)]
        else:
            missing.append(str(k))
    ok = all(p[3] for p in parts)
    lines.append(f"{total[0]} passed, {total[1]} failed" + (f", {total[2]} differ today (as measured)" if total[2] else "")
                 + f" — {len(parts)} shards" + (f" (no summary from shard {', '.join(missing)})" if missing else ""))
    return ok, "\n".join(lines)


def differs_today_ids(out):
    """The test IDs a file's output reports as "differs today" — the screen-test harness's `  ~ ID name` lines
    (test/ui/harness.py differs_today: a decided behavior the app doesn't have yet). --release refuses while any remain."""
    return re.findall(r"^\s*~ ([A-Z][A-Z0-9]*-\d{3}) ", out, re.M)


def changed_files():
    names = set()
    for args in (["git", "diff", "--cached", "--name-only"], ["git", "diff", "--name-only"]):
        out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout or ""
        names |= {ln.strip() for ln in out.splitlines() if ln.strip()}
    return sorted(names)


# --- dist/ built once, before the screen tests start their servers (2026-11-16) -----------------------------------------
def prebuild():
    """Each screen test starts its own serve.py, and serve.py rebuilds a stale dist/ copy on request — several servers
    at once would each rebuild the same files into the same place. Built here once instead, so every server finds dist/
    fresh (its rebuild is then a no-op). Returns the build's error in words, or None."""
    spec = importlib.util.spec_from_file_location("rw_build", os.path.join(ROOT, "tools", "build.py"))
    build = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(build)
        for name in build.SOURCES:
            build.build_if_stale(name)
        build.styles_if_stale()
    except Exception as e:      # noqa: BLE001 — a build that fails is reported (the screen tests then show it too)
        return f"{type(e).__name__}: {e}"
    return None


# --- results stamped with their commit (TODO "Faster sprints", item 2; 2026-11-16) --------------------------------------
RESULTS_NAME = "rw-test-results"
KEEP_RECORDS = 300          # the newest; older records are deleted as new ones are written

# The environment variables that change what a run does — each one set is noted in the record, with its value
# (2026-11-16: a run with RW_CELLS set ran a few cells and --stamp counted it as a full tier 2). A NARROWING one runs only
# part of what was asked, so the run counts no more than an --id / --tag run. Found by searching the test files, their
# helpers (test/ui/rw.py, test/harness.js) and the runner for os.environ / process.env; a new one is added here.
RUN_ENV = {     # name: (narrows?, what it does)
    "RW_CELLS": (True, "test/ui/test_cells.py runs only the cells it names (a sharded file then runs as one process)"),
    "RW_HEADED": (False, "the screen tests show the browser, slowed down — every test still runs (test/ui/rw.py)"),
    "RW_BROWSER": (False, "the screen tests' browser: chrome (the default) or msedge — every test still runs (rw.py)"),
    "RW_TEST_ARTIFACTS": (False, "where a failing screen test saves its screenshot (tools/copies.py)"),
    "RW_TEST_SLOTS": (False, "the PC's limit on screen tests at once (tools/test_slots.py)"),
    "RELAY_URL": (False, "tier 3 runs against that relay instead of starting its own local one"),
}


def run_env(environ=None):
    """{name: value} of RUN_ENV's variables that are set (not empty) — for the record."""
    env = os.environ if environ is None else environ
    return {k: env[k] for k in RUN_ENV if env.get(k)}


def narrowed_by(r):
    """What narrowed this run to part of its tier, in words ([] = a full run): --tag, --id, a narrowing variable."""
    ran = r.get("ran") or {}
    return ([f"--tag {', '.join(ran['tags'])}"] if ran.get("tags") else []) \
        + ([f"--id {', '.join(ran['ids'])}"] if ran.get("ids") else []) \
        + [f"{k}={v}" for k, v in (r.get("env") or {}).items() if RUN_ENV.get(k, (False,))[0]]


def _git(args, root=ROOT):
    r = subprocess.run(["git", "--no-optional-locks"] + args, cwd=root, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else None


def results_dir(root=ROOT):
    """Where this working copy's records live: git's own folder for it (a worktree has its own) — never the working tree.
    None if git can't say (not a git folder)."""
    p = _git(["rev-parse", "--git-path", RESULTS_NAME], root)
    return os.path.normpath(os.path.join(root, p)) if p else None


def head_commit(root=ROOT):
    return _git(["rev-parse", "HEAD"], root)


def uncommitted(root=ROOT):
    """What isn't committed: changed tracked files and untracked files git doesn't ignore — git status's short lines."""
    out = _git(["status", "--porcelain", "--untracked-files=normal"], root)
    return ["(git status failed)"] if out is None else [ln for ln in out.splitlines() if ln.strip()]


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def write_record(rec, folder):
    os.makedirs(folder, exist_ok=True)
    name = f"{rec['started'][:19].replace(':', '')}-{(rec.get('commit') or 'nocommit')[:12]}-{os.getpid()}.json"
    path = os.path.join(folder, name)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(path + ".tmp", path)
    old = sorted(n for n in os.listdir(folder) if n.endswith(".json"))[:-KEEP_RECORDS]
    for n in old:
        try:
            os.remove(os.path.join(folder, n))
        except OSError:
            pass
    return path


def read_records(folder):
    """Every readable record in the folder, oldest first (by when it ended)."""
    out = []
    if folder and os.path.isdir(folder):
        for n in os.listdir(folder):
            if n.endswith(".json"):
                try:
                    with open(os.path.join(folder, n), encoding="utf-8") as f:
                        r = json.load(f)
                except (OSError, ValueError):
                    continue
                if isinstance(r, dict):
                    out.append(r)
    return sorted(out, key=lambda r: str(r.get("ended", "")))


def record_problems(r):
    """Why this record proves nothing, in words ([] = it proves its tiers)."""
    why = []
    if r.get("commit_after") != r.get("commit"):
        why.append(f"a commit was made while it ran (HEAD moved to {str(r.get('commit_after'))[:12]})")
    dirty = list(dict.fromkeys((r.get("uncommitted") or {}).get("before", []) + (r.get("uncommitted") or {}).get("after", [])))
    if dirty:
        why.append("not committed while it ran: " + ", ".join(dirty[:6]) + (f" (+{len(dirty) - 6} more)" if len(dirty) > 6 else ""))
    files = r.get("files") or []
    for f in files:
        if f.get("result") == "failed":
            why.append(f"{f.get('file')} failed ({f.get('counts') or 'no summary'})")
        elif f.get("result") == "skipped":
            why.append(f"{f.get('file')} was skipped — {f.get('why') or 'no reason given'}")
    why += list(r.get("problems") or [])
    if r.get("result") != "passed" and not why:
        why.append("the run failed")
    return why


def judge(records, commit):
    """(proven?, lines) — does the record prove `commit` (a full id)? Tier 1 and tier 2 each need a FULL run (not narrowed
    by --id / --tag or a narrowing variable such as RW_CELLS — narrowed_by; --tier all counts for both) on exactly this
    commit; the LATEST such run of each tier is the one that counts (a later failure isn't outvoted by an earlier pass),
    and it must hold no failure, no skip, nothing uncommitted."""
    lines, proven, shown = [], True, {}
    for tier in (1, 2):
        runs = [r for r in records if r.get("commit") == commit
                and str((r.get("ran") or {}).get("tier")) in (str(tier), "all")]
        full = [r for r in runs if not narrowed_by(r)]
        if not full:
            proven = False
            lines.append(f"  ✗ tier {tier}: no full tier {tier} run recorded on this commit")
            if runs:
                lines.append(f"      its latest tier {tier} run ({str(runs[-1].get('started', '?'))[:19].replace('T', ' ')})"
                             f" was narrowed by {'; '.join(narrowed_by(runs[-1]))} — only part of it ran, so it doesn't count")
            continue
        r = full[-1]
        mine = [f for f in r.get("files") or [] if f.get("tier") == tier]
        why = record_problems(r) + ([] if mine else [f"no tier {tier} file ran"])
        ok = not why
        proven = proven and ok
        passed = sum(1 for f in mine if f.get("result") == "passed")
        lines.append(f"  {'✓' if ok else '✗'} tier {tier}: {passed} of {len(mine)} file(s) passed — run "
                     f"{str(r.get('started', '?'))[:19].replace('T', ' ')} → {str(r.get('ended', '?'))[11:19]} "
                     f"(--tier {(r.get('ran') or {}).get('tier')}"
                     + "".join(f"; {k}={v}" for k, v in (r.get("env") or {}).items()) + ")")
        if id(r) not in shown:          # one 'all' run serves both tiers: its problems are listed once
            shown[id(r)] = True
            lines += [f"      {w}" for w in why]
    return proven, lines


def show_stamp(commit_arg, folder):
    commit = _git(["rev-parse", "--verify", "--quiet", f"{commit_arg}^{{commit}}"])
    if not commit:
        print(f"NOT PROVEN — {commit_arg!r} isn't a commit here.")
        return 1
    subject = _git(["log", "-1", "--format=%s", commit]) or ""
    print(f"Test results for {commit[:12]} ({subject[:70]})  — records: {folder}")
    proven, lines = judge(read_records(folder), commit)
    print("\n".join(lines))
    if proven:
        print("PROVEN — tier 1 and tier 2 passed in full on exactly this commit, with nothing uncommitted.")
        return 0
    print("NOT PROVEN — see above. (Only a full run on a clean tree proves a commit: py tools/run_tests.py --tier 1, "
          "then --tier 2 — or --tier all.)")
    return 1


def main(argv=None, files=None, relay=None, results=None, slots=None):
    """files: the test files to choose from (None = every one in the repo); relay: makes the local relay for tier 3
    (None = the real one); results: the folder for the run's record (None = this working copy's, and only when `files` is
    None — the runner's own sample runs leave no record); slots: the machine-wide limit (None = test_slots.Slots()) — all
    for the runner's own tests (test/test_run_tests.py)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Run ReaderWrangler's tests (docs/design/TESTING.md).")
    ap.add_argument("--tier", default=None, choices=["1", "2", "3", "all"],
                    help="default: 1 — but --id / --tag with no --tier look in every tier (a screen test's ID is tier 2); "
                         "--changed stays tier 1 (the commit hook)")
    ap.add_argument("--tag", action="append", default=[])
    ap.add_argument("--id", action="append", default=[])
    ap.add_argument("--changed", action="store_true", help="only tests covering what changed (staged + unstaged)")
    ap.add_argument("--relay-url", default=os.environ.get("RELAY_URL"),
                    help="a relay you started, for tier 3 (default: the runner starts and stops its own local relay)")
    ap.add_argument("--list", action="store_true", help="show what would run, run nothing")
    ap.add_argument("--quiet", action="store_true", help="print only failures and the summary (the commit hook)")
    ap.add_argument("--release", action="store_true",
                    help="a release run: a skipped file, or a test still marked 'differs today', FAILS the run (the "
                         "release checklist: py tools/run_tests.py --tier all --release)")
    ap.add_argument("--jobs", type=int, default=None,
                    help="test files at once (tiers 1 and 2; tier 3 is always one at a time) — default: the machine-wide "
                         "limit on screen tests (RW_TEST_SLOTS, else 4), which every screen-test file also holds a slot of")
    ap.add_argument("--stamp", nargs="?", const="HEAD", default=None, metavar="COMMIT",
                    help="say whether the recorded runs PROVE this commit (default HEAD): tiers 1 and 2 in full, every file "
                         "passed, nothing skipped, nothing uncommitted. Runs nothing. Exit 0 proven, 1 not")
    a = ap.parse_args(argv)

    if a.stamp is not None:
        return show_stamp(a.stamp, results if results is not None else results_dir())

    started, t_start = _now(), time.monotonic()
    tier = default_tier(a) if a.tier is None else ("all" if a.tier == "all" else int(a.tier))
    real = files is None          # the repo's own test files (not the runner's samples): a record, and dist/ built first
    files = discover() if real else files
    broken = [f for f in files if f.problem]
    chosen = select([f for f in files if not f.problem], tier=tier, tags=a.tag or None, ids=a.id or None,
                    changed=changed_files() if a.changed else None)

    if a.list:
        for f in chosen:
            print(f"  tier {f.tier}  {f.rel():40}  tags: {', '.join(f.tags)}"
                  + (f"  · {f.shards} shards" if f.shards > 1 else ""))
        for f in broken:
            print(f"  ✗ {f.rel()}: {f.problem}")
        print(f"{len(chosen)} file(s) would run")
        return 0

    count = {"passed": 0, "failed": 0}
    for f in broken:
        count["failed"] += 1
        print(f"✗ {f.rel()}: {f.problem}")
    if not chosen and not broken:
        if not a.quiet:   # the commit hook stays silent when no test covers the change (Law 12: no noise on the normal path)
            print("No tests cover these changes." if a.changed else "No tests match.")
        return 0
    # The record (item 2): every run but the commit hook's --changed (and --list, above). Taken BEFORE anything runs —
    # the commit and what's uncommitted — and again at the end, so a change made during the run is caught too.
    record_to = None if a.changed else (results if results is not None else (results_dir() if real else None))
    rec = None
    if record_to:
        rec = {"commit": head_commit(), "uncommitted": {"before": uncommitted()},
               "ran": {"tier": str(tier), "tags": a.tag, "ids": a.id, "release": a.release, "jobs": None},
               "env": run_env(),
               "files": [{"file": f.rel(), "tier": f.tier, "result": "failed", "counts": f.problem} for f in broken],
               "problems": [], "started": started}
    skipped = [(f, why) for f, why in ((f, skip_reason(f)) for f in chosen) if why]
    chosen = [f for f in chosen if not any(f is s for s, _ in skipped)]
    if not a.quiet or a.release:
        for f, why in skipped:
            print(f"- {f.rel()}: skipped — {why}")
    if rec:
        rec["files"] += [{"file": f.rel(), "tier": f.tier, "result": "skipped", "why": why} for f, why in skipped]

    differ = []   # (file, [test IDs]) — tests still marked "differs today" (test/ui/harness.py differs_today)
    problems = []  # failures that belong to no one file (the build, the local relay) — for the record
    say_lock = threading.Lock()   # one file's lines are printed together, never interleaved with another's

    def say(text):
        with say_lock:
            print(text, flush=True)

    def report(f, ok, out, seconds=None, waited=0.0, shards=None):
        """One file's result: its line (and a failure's details, together) and its entry in the record. shards: a file
        run as several processes — [{cells, seconds, waited, result}] — reported as the one file it is."""
        ids = differs_today_ids(out)
        summary = next((ln for ln in reversed(out.splitlines()) if re.search(r"\bpassed\b", ln)), "")
        wait = f", waited {waited:.0f} s for a slot" if waited >= 1 else ""
        each = f"; shards {', '.join(str(round(s['seconds'])) for s in shards)} s" if shards else ""
        took = "" if seconds is None else f"  ({seconds:.0f} s{each}{wait})"
        lines = []
        if ok:
            if not a.quiet:
                lines.append(f"✓ {f.rel()}  {summary.strip()}{took}")
        else:
            lines.append(f"✗ {f.rel()}  {summary.strip()}{took}")
            for ln in out.splitlines():
                if "✗" in ln or "Error" in ln or "FAIL" in ln or ln.startswith("      "):
                    lines.append("    " + ln)
        with say_lock:
            if ids:
                differ.append((f, ids))
            count["passed" if ok else "failed"] += 1
            if rec:
                rec["files"].append({"file": f.rel(), "tier": f.tier, "result": "passed" if ok else "failed",
                                     "counts": summary.strip(), "seconds": None if seconds is None else round(seconds, 1),
                                     "waited": round(waited, 1), "differ": ids, **({"shards": shards} if shards else {})})
            if lines:
                print("\n".join(lines), flush=True)

    def run_and_report(f, relay_url):
        t0 = time.monotonic()
        ok, out = run_file(f, relay_url=relay_url)
        report(f, ok, out, time.monotonic() - t0)

    # Tiers 1 and 2 in parallel (item 1): --jobs files at once; each screen-test (tier 2) file holds one of the PC's test
    # slots for as long as it runs, so every run on this PC together stays within the limit. Tier 3 runs after, one file
    # at a time (below). A file with `shards: N` is N units of work, each in its own process with its own slot (a narrow
    # run — RW_CELLS already set — stays one process, as asked). Longest first — by each file's time in this copy's latest
    # record (a shard: its file's longest shard then, or its file's time split N ways) — so the long ones don't finish
    # last on their own.
    slots = slots or test_slots.Slots()
    jobs = max(1, a.jobs or slots.count)
    if rec:
        rec["ran"]["jobs"] = jobs
    pooled = [f for f in chosen if f.tier != 3]
    if any(f.tier == 2 for f in pooled) and real:
        err = prebuild()
        if err:
            count["failed"] += 1
            problems.append(f"the build (dist/) failed: {err}")
            print(f"✗ build: dist/ couldn't be built before the screen tests — {err}")
    units = []          # (file, shard number or None, of how many, its cells or None)
    for f in pooled:
        if f.shards > 1 and not os.environ.get("RW_CELLS"):
            cells, why = list_cells(f)
            if cells is None:
                report(f, False, why)
                continue
            split = shares(cells, f.shards)
            units += [(f, k, len(split), c) for k, c in enumerate(split, 1)]
        else:
            units.append((f, None, None, None))
    if units:
        last = {}
        for r in read_records(record_to or (results_dir() if real else None)):
            for x in r.get("files") or []:
                if x.get("seconds") is not None:
                    each = [s["seconds"] for s in x.get("shards") or [] if s.get("seconds") is not None]
                    last[x.get("file")] = (max(each), True) if each else (x["seconds"], False)

        def estimate(u):
            f, k, n, _ = u
            t, per_shard = last.get(f.rel(), (60.0 if f.tier == 2 else 5.0, False))
            return t if k is None or per_shard else t / n
        units.sort(key=lambda u: -estimate(u))
    sharded = {}        # file path -> the shards finished so far
    shard_lock = threading.Lock()

    def run_unit(u):
        f, k, n, cells = u
        label = f.rel() + (f" (shard {k} of {n})" if k else "")
        slot = slots.acquire(f"{ROOT} · {label}", on_wait=say) if f.tier == 2 else None
        t0 = time.monotonic()
        try:
            ok, out = run_file(f, relay_url=a.relay_url, cells=cells)
        except Exception as e:      # noqa: BLE001 — a runner error is that file's failure, never a lost thread
            ok, out = False, f"✗ the runner couldn't run it: {type(e).__name__}: {e}"
        finally:
            if slot:
                slot.release()
        t1, waited = time.monotonic(), slot.waited if slot else 0.0
        if k is None:
            report(f, ok, out, t1 - t0, waited)
            return
        with shard_lock:          # the file is reported once, when its last shard is done
            done = sharded.setdefault(f.path, [])
            done.append((k, n, cells, ok, out, t0, t1, waited))
            if len(done) < n:
                return
        f_ok, f_out = combine_shards([(k, n, c, o, x, b - s) for k, n, c, o, x, s, b, _ in done])
        report(f, f_ok, f_out, max(p[6] for p in done) - min(p[5] for p in done), sum(p[7] for p in done),
               shards=[{"cells": len(c), "first": c[0], "seconds": round(b - s, 1), "waited": round(w, 1),
                        "result": "passed" if o else "failed"} for k, n, c, o, x, s, b, w in sorted(done)])

    if units:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(jobs, len(units))) as pool:
            for fut in concurrent.futures.as_completed([pool.submit(run_unit, u) for u in units]):
                fut.result()

    # Tier 3 with no --relay-url: the runner starts its OWN local relay around the relay files, then stops it and checks
    # everything it started is gone and its ports are free (local_relay.py). A given --relay-url is used as is.
    own_relay = [f for f in chosen if f.tier == 3] if not a.relay_url else []
    for f in chosen:
        if f.tier == 3 and f not in own_relay:
            run_and_report(f, a.relay_url)
    if own_relay:
        r = (relay or local_relay.LocalRelay)()
        if not a.quiet:
            print("· starting a local relay for the relay tests (wrangler dev --local, on a free port)…")
        try:
            url = r.start()
        except local_relay.RelayError as e:
            count["failed"] += 1
            problems.append(f"the local relay didn't start — not run: {', '.join(f.rel() for f in own_relay)}")
            print(f"✗ local relay: {e}\n    not run: " + ", ".join(f.rel() for f in own_relay))
        else:
            try:
                for f in own_relay:
                    run_and_report(f, url)
            finally:
                left = r.stop()
            if left:
                count["failed"] += 1
                problems.append("the local relay: not everything it started was stopped — " + "; ".join(left))
                print("✗ local relay: not everything it started was stopped —\n    " + "\n    ".join(left))
            elif not a.quiet:
                print(f"✓ local relay stopped — every process it started is gone, ports {', '.join(map(str, r.ports))} free")
    print(f"Tests: {count['passed']} file(s) passed, {count['failed']} failed"
          + (f", {len(skipped)} skipped" if skipped else ""))
    refused = False
    if a.release and skipped:    # a release needs every file to have RUN — skipped is not passed (7.28.0)
        print(f"✗ release run: {len(skipped)} file(s) skipped — a release needs every file to run:\n    "
              + "\n    ".join(f"{f.rel()} — {why}" for f, why in skipped))
        refused = True
    if a.release and differ:     # a decided behavior not built yet is fine while building, never in a release (7.30.0)
        n = sum(len(ids) for _, ids in differ)
        print(f"✗ release run: {n} test(s) still differ from what was decided (marked 'differs today') — build them, or "
              f"take the decision back to Ron, before a release:\n    "
              + "\n    ".join(f"{f.rel()}: {', '.join(ids)}" for f, ids in differ))
        refused = True
        problems.append(f"release run: {n} test(s) still marked 'differs today'")
    code = 1 if refused or count["failed"] else 0
    if rec:
        rec.update({"commit_after": head_commit(), "problems": problems, "ended": _now(),
                    "seconds": round(time.monotonic() - t_start), "result": "passed" if code == 0 else "failed"})
        rec["uncommitted"]["after"] = uncommitted()
        try:
            write_record(rec, record_to)
            if not a.quiet:
                dirty = rec["uncommitted"]["before"] or rec["uncommitted"]["after"]
                narrow = narrowed_by(rec)
                print(f"· recorded for {str(rec['commit'])[:12]}" + (" — with uncommitted changes, so it proves nothing"
                      if dirty else "") + (f" — narrowed by {'; '.join(narrow)}, so it isn't a full run of its tier"
                      if narrow else "") + f"; took {rec['seconds'] // 60} min {rec['seconds'] % 60} s "
                      "(py tools/run_tests.py --stamp)")
        except OSError as e:
            print(f"✗ the run's record couldn't be written to {record_to}: {e}")
    return code


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)   # the pytools submodule lives at the repo root
    try:
        from pytools.keepopen import run
    except ImportError:
        sys.exit(main())
    run(main, pause="always")
