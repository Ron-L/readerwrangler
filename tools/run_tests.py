#!/usr/bin/env python3
"""
run_tests.py — the one test runner (docs/design/TESTING.md §4). Finds every test file, reads its header, runs the ones
asked for, and prints one summary.

    py tools/run_tests.py                       tier 1 (the default): the fast function tests
    py tools/run_tests.py --tier all            everything — tier 3 starts and stops its own local relay
    py tools/run_tests.py --tier all --release  the release run: a skipped or set-aside file, or a test still marked
                                                "differs today", fails it
    py tools/run_tests.py --tag merge           by area (every tier unless --tier says one)
    py tools/run_tests.py --id MERGE-012        the file(s) naming that test ID as a test (a sharded file: just those cells)
    py tools/run_tests.py --changed             the tests covering what changed (the commit hook)
    py tools/run_tests.py --list                what would run; runs nothing
    py tools/run_tests.py --stamp [<commit>]    PROVEN (exit 0) only if tiers 1 and 2 ran in full on exactly that commit,
                                                every file passed, nothing uncommitted — else NOT PROVEN and why (exit 1)
    py tools/run_tests.py --release-held <file> Ron's "try again" for a held file (below)
    py tools/run_tests.py --jobs 2              files at once (default 4)

Test files: test/*.test.js and test/test_*.py (function tests, tier from the header — normally 1), test/ui/test_*.py
(screen tests, tier 2), relay/test-*.mjs (relay tests, tier 3). Each declares in its first lines
`tags: <areas>, tier N` and `covers: <files it tests>` (the covers lines drive --changed); optional lines: `shards: N`
(run as N processes, each with a share of its cells), `heavy: yes` (a tier-1 file that starts many processes: it holds a
test slot like a screen test), `alone: yes — <why>` (runs only while it holds every test slot on the PC, after the
others), `skip: <TODO id> — <why>` (set aside: not run, said every run, refused by --release).

How it runs: 4 files at once (--jobs N); each screen test or heavy file holds one of the PC's test slots (tools/
test_slots.py), so every run on the PC together stays at 4 browsers at once. Longest first, by each file's time in this
working copy's latest record. Each file runs in a Windows job (tools/job.py): measured, and everything it started ended
with it — also if the runner itself is stopped. A file still running after 10 minutes is stopped: a failure.

The machine's trouble: a screen test (or heavy file) that exits 3 with an "ENVIRONMENT FAILURE: <reason>" line (tools/
environment_trouble.py) is rerun once, alone, after the others, holding every test slot; passed then, it passes (said).
Meeting the trouble again — or more files meeting it than MAX_RETRIES — is NOT PROVEN, never a failure. A file not
proven in 3 full runs in a row on this PC is HELD (tools/held_tests.py) until Ron releases it, marks it alone: yes, or
sets it aside. A test failure is never rerun.

Every run but --list leaves a record in git's own folder for this working copy (rw-test-results): the commit, anything
uncommitted, each file's result, time and what it cost; a failed file's whole output beside it. A narrowed run (--changed,
--id, --tag, RW_CELLS) goes on the quick shelf (rw-test-results/quick), never read by --stamp. Before and after each run
the repository's shared git settings are checked (not bare; the commit checks on) — a run that changed them is said
loudly, with the command that puts them back.

Exit: 0 all passed · 1 a failure · 3 nothing failed but a file is NOT PROVEN. Double-clicked, the window stays open.
"""
import argparse
import collections
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
import local_relay           # noqa: E402 — tools/local_relay.py: tier 3's own local relay
import test_slots            # noqa: E402 — tools/test_slots.py: the PC-wide limit on screen tests at once
import environment_trouble   # noqa: E402 — tools/environment_trouble.py: a screen test's "the machine failed, not me"
import job                   # noqa: E402 — tools/job.py: each file in a Windows job — measured, ended with it
import held_tests            # noqa: E402 — tools/held_tests.py: a file that can't be proven 3 full runs in a row is held

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Screen tests (tier 2) need Playwright, which lives in the project's venv (requirements-dev.txt) — never the system
# Python. Everything else runs with the Python that runs this script (the commit hook needs no venv).
VENV_PY = os.path.join(ROOT, ".venv", "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")
VENV_SETUP = "py -m venv .venv   then   .venv\\Scripts\\pip install -r requirements-dev.txt   (in the project folder)"
PATTERNS = ["test/*.test.js", "test/test_*.py", "test/ui/test_*.py", "relay/test-*.mjs"]
HEADER_LINES = 15

JOBS = 4                # files at once — and screen-test browsers at once (--jobs N, or RW_TEST_SLOTS, for one run)
TIME_LIMIT_S = 600      # a file (or shard) still running after this is stopped with everything it started: a failure
RETRY_WAIT_S = 10       # before a file is rerun alone: the others are done by then — this lets the machine settle too
MAX_RETRIES = 4         # files rerun alone at most per run; the ones past it are NOT PROVEN (that much trouble points at
#                         something broken — said loudly)
NOT_PROVEN = "not proven"   # a file's result: the machine's trouble, and no rerun left for it (or held)


def read_header(path):
    """{'tags', 'tier', 'covers', 'shards', 'skip': {todo, why}|None, 'heavy', 'alone', 'alone_why', 'problem'} from the
    file's first lines. That a skip: line's TODO id is a task in TODO.md is checked by check_set_aside."""
    tags, tier, covers, shards, bad_shards, skip, bad_skip = None, None, None, 1, None, None, None
    heavy, bad_heavy, alone, alone_why, bad_alone = False, None, False, None, None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = [next(f, "") for _ in range(HEADER_LINES)]
    except OSError as e:
        return {"tags": [], "tier": None, "covers": [], "shards": 1, "skip": None, "heavy": False, "alone": False,
                "alone_why": None, "problem": f"can't read it: {e}"}
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
        m = re.match(r"skip:\s*(.*?)\s*$", text)
        if m:
            s = re.fullmatch(TODO_ID + r"\s+(?:—|–|--?)\s+(\S.*)", m.group(1))
            if s:
                skip = {"todo": s.group(1), "why": s.group(2)}
            else:
                bad_skip = m.group(1)
        m = re.match(r"heavy:\s*(.*?)\s*$", text)
        if m:
            h = re.fullmatch(r"(yes|no)(?:\s+(?:—|–|--?)\s+\S.*)?", m.group(1))
            if h:
                heavy = h.group(1) == "yes"
            else:
                bad_heavy = m.group(1)
        m = re.match(r"alone:\s*(.*?)\s*$", text)
        if m:
            h = re.fullmatch(r"yes\s+(?:—|–|--?)\s+(\S.*)|no(?:\s+(?:—|–|--?)\s+\S.*)?", m.group(1))
            if h:
                alone, alone_why = bool(h.group(1)), h.group(1)
            else:
                bad_alone = m.group(1)
    problem = None
    if tags is None or covers is None:
        problem = "no header — every test file needs 'tags: <areas>, tier N' and 'covers: <files>' in its first lines"
    elif tier is None:
        problem = "its tags: line names no tier ('tier 1', 'tier 2' or 'tier 3')"
    elif bad_shards is not None:
        problem = f"its shards: line says {bad_shards!r} — a whole number of processes, 1 or more (e.g. 'shards: 3')"
    elif bad_skip is not None:
        problem = (f"its skip: line says {bad_skip!r} — a file is set aside with its TODO task's id and why: "
                   "'skip: <TODO id> — why' (e.g. 'skip: 20261116-0900 — fails one time in ten')")
    elif bad_heavy is not None:
        problem = (f"its heavy: line says {bad_heavy!r} — 'heavy: yes' (or 'heavy: yes — why') for a file that starts "
                   "many processes of its own, 'heavy: no' or no line for one that doesn't")
    elif bad_alone is not None:
        problem = (f"its alone: line says {bad_alone!r} — 'alone: yes — <why>' for a file that must run alone (it runs "
                   "only while it holds every test slot on the PC — the why is required), 'alone: no' or no line else")
    return {"tags": tags or [], "tier": tier, "covers": covers or [], "shards": shards, "skip": skip, "heavy": heavy,
            "alone": alone, "alone_why": alone_why, "problem": problem}


# --- a test file set aside on purpose -------------------------------------------------------------------------------------
TODO_PATH = os.path.join(ROOT, "TODO.md")
TODO_ID = r"(\d{8}-\d{4}[a-z]*)"        # a TODO task's id: when it was filed, a letter if that minute was taken


def todo_task_ids(path=TODO_PATH):
    """The ids of the tasks in TODO.md (each task's `<!-- id … -->` line) — read by tools/backlog_report.py's parse, the
    one reader of TODO's format. None if the file can't be read."""
    import backlog_report      # tools/, next to this file (on the path above); imported only when a file is set aside
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    return {t["id"] for t in backlog_report.parse(text) if t["id"]}


def check_set_aside(files, todo_path=None):
    """A file set aside must name a task in TODO.md — one that says how it gets fixed. A skip: line naming no task there
    makes it a header problem (the file fails, loud), never a quiet skip. TODO.md is read only when a file is set aside."""
    todo_path = todo_path or TODO_PATH
    aside = [f for f in files if f.skip and not f.problem]
    known = todo_task_ids(todo_path) if aside else set()
    for f in aside:
        if known is None:
            f.problem = f"its skip: line names TODO {f.skip['todo']}, but {todo_path} couldn't be read to check it"
        elif f.skip["todo"] not in known:
            f.problem = (f"its skip: line names TODO {f.skip['todo']}, which is no task in TODO.md — a test is set aside "
                         "only under the TODO task that fixes it (the id on the line under the task's header)")


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


# How a test file names its tests: by its ID as a whole quoted string, first in what follows it —
#   - the first argument of the call that runs it — test("ID", …) and t('ID', …) (test/harness.js, test/ui/harness.py),
#     differs_today("ID", …), add("ID", …) (test_cells.py), row("ID", …) / check("ID", …) (files with their own helper);
#   - the first item of its row in a table — ("ID", …) (test_check_parse.py, test_message_codes.py, test_layout.py).
# Comments are dropped first: a line that starts as one (#, //, /*, *) and a line's end after " # " or " // ".
COMMENT_LINE = re.compile(r"^\s*(?:#|//|/\*|\*)")
LINE_END_COMMENT = re.compile(r"\s(?:#|//)\s.*$")


def test_names(tf, ids):
    """The ids this file names as tests (above) — how --id picks a file, and the one lookup for it. [] if unreadable."""
    try:
        text = open(tf.path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    code = "\n".join(LINE_END_COMMENT.sub("", ln) for ln in text.splitlines() if not COMMENT_LINE.match(ln))
    return [i for i in ids if re.search(r"\(\s*([\"'`])" + re.escape(i) + r"\1\s*,", code)]


def select(files, tier=None, tags=None, ids=None, changed=None, base=ROOT):
    """The files to run. tier: an int or 'all' (None = all); tags / ids: any match; changed: repo-relative paths —
    a file is picked when it covers one of them or is one of them. (A sharded file picked by --id is then narrowed to
    the cells named — narrow_by_id.)"""
    out = []
    for f in files:
        if tier not in (None, "all") and f.tier != tier:
            continue
        if tags and not set(tags) & set(f.tags):
            continue
        if ids and not test_names(f, ids):
            continue
        if changed is not None:
            ch = {c.replace("\\", "/") for c in changed}
            if not (set(f.covers) & ch or f.rel(base) in ch):
                continue
        out.append(f)
    return out


def default_tier(a):
    """The tier when none is given: --id or --tag → every tier (they name what to run); --changed → tier 1 (the commit
    hook: seconds, not minutes); nothing → tier 1."""
    return "all" if (a.id or a.tag) and not a.changed else 1


def skip_reason(tf):
    """Why this file won't run here — None = it runs. The ONE place a skip is decided. Nothing skips today (tier 3 brings
    its own relay; a missing tool fails loud). A reason added here is reported as skipped — and fails a --release run."""
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


def test_env(**extra):
    """The environment every process the runner starts for a test file gets — the runner's own, WITHOUT any GIT_*
    variable: under the commit hook they name the REAL repository, and a test once set it bare through them."""
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(PYTHONIOENCODING="utf-8", **extra)
    return env


def run_process(tf, relay_url=None, timeout=None, cells=None):
    """(exit code, its whole output — stdout, then stderr —, what it cost) — runs one test file from the repo root, in a
    job of its own (tools/job.py). Exit code None: it couldn't start, or ran past `timeout` (None: TIME_LIMIT_S) and was
    stopped with everything it started (what it printed until then is kept). cells: run only these (RW_CELLS)."""
    timeout = TIME_LIMIT_S if timeout is None else timeout
    cmd, why = command(tf)
    if cmd is None:
        return None, why, job.nothing("it couldn't start")
    env = test_env()
    if relay_url:
        env["RELAY_URL"] = relay_url
    if cells is not None:
        env["RW_CELLS"] = ",".join(cells)
    code, stdout, stderr, cost = job.run(cmd, timeout=timeout, cwd=ROOT, env=env)
    out = (stdout + stderr).decode("utf-8", "replace")
    if code is None:
        return None, out + f"\n✗ timed out after {timeout:g} s", cost
    return code, out, cost


def run_file(tf, relay_url=None, timeout=None, cells=None):
    """(passed?, output) — run_process, as passed or not."""
    code, out, _ = run_process(tf, relay_url=relay_url, timeout=timeout, cells=cells)
    return code == 0, out


def latest_times(records):
    """{file: (seconds, per shard?)} — each file's time in the latest of these records that has one (oldest first, as
    read_records gives them): a sharded file's longest shard (per shard: True), else the file's whole time."""
    last = {}
    for r in records:
        for x in r.get("files") or []:
            if x.get("seconds") is not None:
                each = [s["seconds"] for s in x.get("shards") or [] if s.get("seconds") is not None]
                last[x.get("file")] = (max(each), True) if each else (x["seconds"], False)
    return last


def estimate(u, last):
    """A unit's expected seconds — what orders a run, longest first. u: (file, shard number or None, of how many, its cells
    or None). Its time in this copy's latest record (latest_times: a shard → its file's longest shard then, or its file's
    time split n ways); else 60 s for a screen test, 5 s for any other."""
    f, k, n, _ = u
    t, per_shard = last.get(f.rel(), (60.0 if f.tier == 2 else 5.0, False))
    return t if k is None or per_shard else t / n


def slotted(tf):
    """Does this file hold one of the PC's test slots while it runs? A screen test (its browser), and a tier-1 file whose
    header says `heavy: yes`. Light tier-1 files run beside them, outside the slots; tier 3 runs on its own."""
    return tf.tier == 2 or (tf.tier == 1 and bool(getattr(tf, "heavy", False)))


def environment_reason(tf, code, out):
    """Why a file says the machine or the browser failed — its exit 3 AND its "ENVIRONMENT FAILURE:" line
    (tools/environment_trouble.py) — else None. Only a screen-test file or a heavy tier-1 file can say so; any other
    file's exit 3 is a failure like any other."""
    if not ((tf.tier == 2 and tf.path.endswith(".py")) or (tf.tier == 1 and getattr(tf, "heavy", False))):
        return None
    return environment_trouble.reason(code, out)


def screenshots_in(out):
    """The screenshots a file's output names ("screenshot: <path>")."""
    return re.findall(r"^\s*screenshot:\s*(\S.*?)\s*$", out or "", re.M)


def keep_output(folder, tf, text, shard=None, what=""):
    """Save a file's whole output in `folder` (the run's outputs, beside its record); its path, or None (no folder — the
    run leaves no record — or it couldn't be written)."""
    if not folder:
        return None
    name = re.sub(r"[^\w.-]+", "_", tf.rel()).strip("._")[-90:] + (f".shard-{shard}" if shard else "") \
        + (f".{what}" if what else "") + ".txt"
    try:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path
    except OSError:
        return None


# --- one file split across processes ----------------------------------------------------------------------------------
# A file whose header says `shards: N` answers `--list-cells` with its cell IDs (one a line, running nothing) and runs
# only the cells named in RW_CELLS. The runner runs it as N processes — every Nth cell each — each holding its own test
# slot; the file's result is theirs together: passed only if every shard passed, the counts summed, one line, one entry.
CELL_ID = re.compile(r"[A-Z][A-Z0-9]*-\d{3}")


def list_cells(tf, timeout=120):
    """(the file's cell IDs, in its order; None) — or (None, why they couldn't be listed)."""
    cmd, why = command(tf)
    if cmd is None:
        return None, why
    try:
        r = subprocess.run(cmd + ["--list-cells"], cwd=ROOT, env=test_env(),
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


def sharded(tf):
    """Is this file run as several processes? (`shards:` over 1 — tiers 1 and 2; tier 3 is always one file at a time)"""
    return tf.shards > 1 and tf.tier != 3


def narrow_by_id(files, ids, environ=None):
    """--id on a sharded file: it runs as ONE process with RW_CELLS = exactly the cells the ids name, in the file's order
    (its --list-cells); one whose cells the ids don't name (a test of it that isn't a cell — CELL-058, the console check
    every process runs) is left out, with a note saying so. RW_CELLS already set (a narrow run of the caller's own): the
    file runs as asked. Every other file is kept as select() picked it.
    Returns (files kept, {path: its cells}, {path: why its cells couldn't be listed}, notes)."""
    env = os.environ if environ is None else environ
    keep, cells_of, unlisted, notes = [], {}, {}, []
    for f in files:
        if not ids or not sharded(f) or env.get("RW_CELLS"):
            keep.append(f)
            continue
        cells, why = list_cells(f)
        if cells is None:
            keep.append(f)          # fails loud when the run reaches it, as an unlistable sharded file always does
            unlisted[f.path] = why
            continue
        mine = [c for c in cells if c in ids]
        if mine:
            keep.append(f)
            cells_of[f.path] = mine
        else:
            notes.append(f"· {f.rel()} names {', '.join(test_names(f, ids))}, but not as one of its cells (--list-cells) "
                         f"— left out")
    return keep, cells_of, unlisted, notes


def shares(cells, n):
    """The cells split n ways — every nth cell each (neighbors, often alike in cost, spread out); never an empty share."""
    n = max(1, min(n, len(cells)))
    return [cells[i::n] for i in range(n)]


def combine_shards(parts):
    """One file's (passed?, output) from its shards' [(number, of, cells, passed?, output, seconds)]: each shard's output
    under a heading saying which cells it ran, then one summary line with the counts summed (what the runner reads).
    passed? None: not proven — it met the machine's trouble with no rerun left — never called FAILED."""
    total, missing, lines = [0, 0, 0], [], []
    for k, n, cells, ok, out, took in sorted(parts, key=lambda p: p[0]):
        lines.append(f"── shard {k} of {n}: {len(cells)} cells ({cells[0]} … {cells[-1]}) — "
                     + (f"passed in {took:.0f} s" if ok else
                        f"NOT PROVEN in {took:.0f} s (the machine's trouble) — this shard alone: "
                        f"RW_CELLS={','.join(cells)}" if ok is None else
                        f"FAILED in {took:.0f} s — this shard alone: RW_CELLS={','.join(cells)}"))
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
    """The test IDs a file's output reports as "differs today" — the screen-test harness's `  ~ ID name` lines (a decided
    behavior the app doesn't have yet). --release refuses while any remain."""
    return re.findall(r"^\s*~ ([A-Z][A-Z0-9]*-\d{3}) ", out, re.M)


def changed_files():
    names = set()
    for args in (["git", "diff", "--cached", "--name-only"], ["git", "diff", "--name-only"]):
        out = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout or ""
        names |= {ln.strip() for ln in out.splitlines() if ln.strip()}
    return sorted(names)


def prebuild():
    """Each screen test starts its own serve.py, which rebuilds a stale dist/ copy on request — several servers at once
    would each rebuild the same files. Built here once instead, before the screen tests. The build's error, or None."""
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


# --- the repository's shared git settings ----------------------------------------------------------------------------
# Every working copy shares them; a test once set the repository bare through the commit hook's variables and git
# stopped working everywhere. Checked before and after each run: a run that changed one is said loudly, with the command
# that puts it back.
SHARED_SETTINGS = ("core.bare", "core.hooksPath")


def git_settings(repo=ROOT, config=None):
    """{'config': its config file, 'core.bare': …, 'core.hooksPath': …} of the repository `repo` belongs to (a worktree:
    the one it shares). Read straight from the config file (a repository set bare can still be read) — `config` when
    given, else found through git. None if git can't say where it is. Never with git's own variables (test_env)."""
    env = test_env()
    if config is None:
        r = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=repo, capture_output=True, text=True, env=env)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        config = os.path.normpath(os.path.join(repo, r.stdout.strip(), "config"))
    out = {"config": config}
    for k in SHARED_SETTINGS:
        r = subprocess.run(["git", "config", "--file", config, "--get", k], capture_output=True, text=True, env=env)
        out[k] = r.stdout.strip() if r.returncode == 0 else None
    return out


def settings_changed(before, after):
    """The loud lines for each shared git setting this run changed — each with the command that puts it back."""
    lines = []
    for k in SHARED_SETTINGS:
        if before and after and before[k] != after[k]:
            put_back = f"--unset {k}" if before[k] is None else f"{k} {before[k]}"
            lines.append(f"!! THIS RUN CHANGED THE REPOSITORY'S GIT SETTING {k}: {before[k]} → {after[k]} — every working "
                         f"copy shares it. Put it back:  git config --file \"{after['config']}\" {put_back}")
    return lines


# --- results stamped with their commit --------------------------------------------------------------------------------
RESULTS_NAME = "rw-test-results"
KEEP_RECORDS = 300          # the newest; older records are deleted as new ones are written
# Removed working copies' records, kept by tools/copies.py remove: a folder inside the records folder that read_records
# never reads (it reads only the folder's own .json files) and write_record's pruning never deletes.
COPIES_ARCHIVE = "copies"
# A NARROWED run (--changed, --id, --tag, a narrowing variable) leaves its record on the quick shelf: a folder inside the
# records folder that read_records (the stamp, the longest-first order) never reads, with its own keep-limit.
QUICK_SHELF = "quick"
KEEP_QUICK = 300

# The environment variables that change what a run does — each one set is noted in the record, with its value. A
# NARROWING one runs only part of what was asked, so the run counts no more than an --id / --tag run.
RUN_ENV = {     # name: (narrows?, what it does)
    "RW_CELLS": (True, "test/ui/test_cells.py runs only the cells it names (a sharded file then runs as one process)"),
    "RW_HEADED": (False, "the screen tests show the browser, slowed down — every test still runs (test/ui/rw.py)"),
    "RW_BROWSER": (False, "the screen tests' browser: chrome (the default) or msedge — every test still runs (rw.py)"),
    "RW_TEST_ARTIFACTS": (False, "where a failing screen test saves its screenshot (tools/copies.py)"),
    "RW_TEST_SLOTS": (False, "the PC's test slots, and this run's browsers at once (tools/test_slots.py)"),
    "RW_TEST_SLOTS_DIR": (False, "the folder of this PC's test state, instead of %LOCALAPPDATA%\\ReaderWrangler-tests "
                                 "(tools/test_slots.py)"),
    "RELAY_URL": (False, "tier 3 runs against that relay instead of starting its own local one"),
}


def run_env(environ=None):
    """{name: value} of RUN_ENV's variables that are set (not empty) — for the record."""
    env = os.environ if environ is None else environ
    return {k: env[k] for k in RUN_ENV if env.get(k)}


def narrowed_by(r, tier=None):
    """What narrowed this run to part of its tier, in words ([] = a full run): --tag, --id, a narrowing variable — and a
    file set aside (its skip: line), for that file's tier only (tier None: any tier)."""
    ran = r.get("ran") or {}
    return (["--changed"] if ran.get("changed") else []) \
        + ([f"--tag {', '.join(ran['tags'])}"] if ran.get("tags") else []) \
        + ([f"--id {', '.join(ran['ids'])}"] if ran.get("ids") else []) \
        + [f"{k}={v}" for k, v in (r.get("env") or {}).items() if RUN_ENV.get(k, (False,))[0]] \
        + [f"set aside: {f.get('file')} (TODO {f.get('todo')} — {f.get('why')})" for f in r.get("files") or []
           if f.get("result") == "set aside" and tier in (None, f.get("tier"))]


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


def record_id(rec):
    """A record's name (without .json) — also the name of the folder holding its run's kept outputs."""
    return rec.get("id") or f"{rec['started'][:19].replace(':', '')}-{(rec.get('commit') or 'nocommit')[:12]}-{os.getpid()}"


def write_record(rec, folder, keep=None):
    """Write the record in `folder` and keep the newest `keep` there (None: KEEP_RECORDS) — the full runs' folder, or
    the quick shelf (KEEP_QUICK): each shelf is pruned on its own."""
    keep = KEEP_RECORDS if keep is None else keep
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, record_id(rec) + ".json")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    os.replace(path + ".tmp", path)
    names = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
    for n in names[:-keep]:
        try:
            os.remove(os.path.join(folder, n))
        except OSError:
            pass
    # A run's kept outputs (a folder named as its record) go with its record — and so does any folder older than every
    # record kept (its run never wrote one). A newer folder may be a run still going: left alone. Never the archive, never
    # the quick shelf.
    oldest = names[-keep:][0][:-len(".json")] if names[-keep:] else None
    for n in os.listdir(folder):
        if oldest and n < oldest and n not in (COPIES_ARCHIVE, QUICK_SHELF) and os.path.isdir(os.path.join(folder, n)):
            shutil.rmtree(os.path.join(folder, n), ignore_errors=True)
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
            why.append(f"{f.get('file')} failed ({f.get('counts') or 'no summary'})"
                       + (f" — full output: {f['output']}" if f.get("output") else ""))
        elif f.get("result") == NOT_PROVEN:     # the machine's trouble beyond the reruns, or held: never a pass
            why.append(f"{f.get('file')} not proven — " + (str(f.get("not_proven")) if f.get("held") else
                                                            f"the machine was too busy: {f.get('not_proven') or 'no reason given'}")
                       + (f" — full output: {f['output']}" if f.get("output") else ""))
        elif f.get("result") == "skipped":
            why.append(f"{f.get('file')} was skipped — {f.get('why') or 'no reason given'}")
    why += list(r.get("problems") or [])
    if r.get("result") != "passed" and not why:
        why.append("the run failed")
    return why


def judge(records, commit):
    """(proven?, lines) — does the record prove `commit` (a full id)? Tier 1 and tier 2 each need a FULL run (not narrowed
    — narrowed_by; --tier all counts for both) on exactly this commit; the LATEST such run of each tier is the one that
    counts (a later failure isn't outvoted by an earlier pass), and it must hold no failure, no skip, nothing uncommitted.
    Tier 3 gets a line too (tier3_lines) — information only, never part of the verdict."""
    lines, proven, shown = [], True, {}
    for tier in (1, 2):
        runs = [r for r in records if r.get("commit") == commit
                and str((r.get("ran") or {}).get("tier")) in (str(tier), "all")]
        full = [r for r in runs if not narrowed_by(r, tier)]
        if not full:
            proven = False
            lines.append(f"  ✗ tier {tier}: no full tier {tier} run recorded on this commit")
            if runs:
                lines.append(f"      its latest tier {tier} run ({str(runs[-1].get('started', '?'))[:19].replace('T', ' ')})"
                             f" was narrowed by {'; '.join(narrowed_by(runs[-1], tier))} — only part of it ran, so it "
                             "doesn't count")
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
        lines += retried_lines(mine)
    return proven, lines + tier3_lines(records, commit)


def retried_lines(files):
    """A note for each file of the run that was rerun alone after the machine's or the browser's trouble — passed on its
    rerun, it still proves the commit, but the stamp says so. Starts with '·', never '✗'."""
    out = []
    for f in files:
        for t in f.get("retried") or []:
            out.append(f"      · {f.get('file')}" + (f" (shard {t['shard']})" if t.get("shard") else "")
                       + f" was rerun alone after {t.get('reason')} — {t.get('rerun') or '?'} — its first output: "
                       f"{t.get('first_output') or '(not kept)'}")
    return out


def held_outcome(entry, tried):
    """A file's result in one run, in held_tests' words — 'passed' (the first time), 'rerun alone' (passed on its rerun
    after the machine's trouble), 'not proven', 'failed' — with why and its kept outputs (the first rerun note's)."""
    t = (tried or [{}])[0]
    result = entry.get("result")
    outcome = NOT_PROVEN if result == NOT_PROVEN else "failed" if result != "passed" else \
        "rerun alone" if tried else "passed"
    return {"outcome": outcome, "why": t.get("reason") or entry.get("not_proven"), "shard": t.get("shard"),
            "rerun": t.get("rerun"), "first_output": t.get("first_output") or entry.get("output"),
            "rerun_output": t.get("rerun_output")}


def tier3_lines(records, commit):
    """Tier 3's latest run on this commit, as a line — passed / failed / not run. Information only: tier 3 needs a relay
    and isn't part of every review, so PROVEN stays tiers 1 and 2. Starts with '·', never '✗' (tools/copies.py lists a
    NOT PROVEN's '✗' lines as its why)."""
    note = "information only — the stamp proves tiers 1 and 2"
    runs = [r for r in records if r.get("commit") == commit and str((r.get("ran") or {}).get("tier")) in ("3", "all")]
    if not runs:
        return [f"  · tier 3: not run on this commit ({note})"]
    r = runs[-1]
    mine = [f for f in r.get("files") or [] if f.get("tier") == 3 and f.get("result") != "set aside"]  # (named in extra)
    relay = [p for p in r.get("problems") or [] if "local relay" in p]     # the runner's own relay (main(), below)
    bad = [f for f in mine if f.get("result") != "passed"]
    state = "failed" if bad or relay else "passed" if mine else "not run"
    passed = sum(1 for f in mine if f.get("result") == "passed")
    extra = narrowed_by(r, 3) + (["with uncommitted changes"] if any((r.get("uncommitted") or {}).values()) else [])
    out = [f"  · tier 3: {state} — {passed} of {len(mine)} file(s) passed — run "
           f"{str(r.get('started', '?'))[:19].replace('T', ' ')} → {str(r.get('ended', '?'))[11:19]} "
           f"(--tier {(r.get('ran') or {}).get('tier')}" + (" --release" if (r.get("ran") or {}).get("release") else "")
           + "".join(f"; {x}" for x in extra) + f") — {note}"]
    out += [f"      {f.get('file')} {f.get('result')} ({f.get('counts') or f.get('why') or 'no summary'})" for f in bad]
    out += [f"      {p}" for p in relay]
    return out


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


def held_name(given, root=ROOT):
    """A file named on the command line as the records name it — its path in the repository, with forward slashes."""
    g = given.replace("\\", "/")
    if os.path.isabs(given) or os.path.exists(given):
        g = os.path.relpath(os.path.abspath(given), root).replace("\\", "/")
    return g


def release_held(names, path):
    """--release-held: Ron's "try again" — each file's hold and streak on this PC cleared (held_tests.release). Exit 0
    when every one was held and is released; 1 when any wasn't held (said, with what is) or couldn't be saved."""
    code = 0
    for given in names:
        name = held_name(given)
        hold, held, err = held_tests.release(path, name)
        if err:
            print(f"✗ {name}: not released — {err}")
            code = 1
        elif hold:
            print(f"released: {name} — held since {str(hold.get('since', '?'))[:16].replace('T', ' ')}; its streak "
                  f"starts over and the next run runs it ({path})")
        else:
            print(f"{name} isn't held on this PC ({path}) — "
                  + (f"held: {', '.join(sorted(held))}" if held else "no file is held"))
            code = 1
    return code


def parse_args(argv):
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
                    help="a release run: a skipped file, a file set aside (its skip: line), or a test still marked "
                         "'differs today' FAILS the run (the release checklist: py tools/run_tests.py --tier all --release)")
    ap.add_argument("--jobs", type=int, default=None,
                    help=f"test files at once, and screen-test browsers at once (tiers 1 and 2; tier 3 is always one at a "
                         f"time) — default {JOBS}")
    ap.add_argument("--stamp", nargs="?", const="HEAD", default=None, metavar="COMMIT",
                    help="say whether the recorded runs PROVE this commit (default HEAD): tiers 1 and 2 in full, every file "
                         "passed, nothing skipped or set aside, nothing uncommitted; tier 3's latest run shown, for "
                         "information. Runs nothing. Exit 0 proven, 1 not")
    ap.add_argument("--release-held", action="append", default=[], metavar="FILE",
                    help="Ron's 'try again' for a test file HELD on this PC (it couldn't be proven in 3 full runs in a row "
                         "— tools/held_tests.py): its hold and its streak cleared, so the next run runs it. Runs nothing")
    return ap.parse_args(argv)


def main(argv=None, files=None, relay=None, results=None, slots=None, todo=None, retry_wait=None, free_memory=None,
         repo=None):
    """For the runner's own tests: files — the test files to choose from (None = every one in the repo); relay — makes
    the local relay for tier 3 (None = the real one); results — the folder for the run's record (None = this working
    copy's, and only when `files` is None: the runner's own sample runs leave no record); slots — the PC's test slots
    (None = test_slots.Slots()); todo — the TODO file a skip: line's task must be in; retry_wait — seconds before a file
    is rerun alone; free_memory — reads the free memory in bytes; repo — the repository whose shared git settings are
    checked (None = this one)."""
    retry_wait = RETRY_WAIT_S if retry_wait is None else retry_wait
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = parse_args(argv)
    if a.stamp is not None:
        return show_stamp(a.stamp, results if results is not None else results_dir())
    if a.release_held:
        return release_held(a.release_held, held_tests.path_in((slots or test_slots.Slots()).folder))

    started, t_start = _now(), time.monotonic()
    tier = default_tier(a) if a.tier is None else ("all" if a.tier == "all" else int(a.tier))
    real = files is None          # the repo's own test files (not the runner's samples): a record, and dist/ built first
    files = discover() if real else files
    check_set_aside(files, todo)       # a skip: line naming no TODO task is a header problem
    broken = [f for f in files if f.problem]
    chosen = select([f for f in files if not f.problem], tier=tier, tags=a.tag or None, ids=a.id or None,
                    changed=changed_files() if a.changed else None)
    aside = [f for f in chosen if f.skip]          # set aside on purpose (skip: <TODO id> — why): not run, said so
    chosen = [f for f in chosen if not f.skip]
    chosen, id_cells, id_unlisted, id_notes = narrow_by_id(chosen, a.id)
    # A file that can't be proven is HELD on this PC: not run, "held — not run", counted as not proven — until Ron
    # releases it (--release-held), says it runs alone (alone: yes — that lifts a hold taken beside others), or sets it
    # aside (skip:).
    slots = slots or test_slots.Slots()      # every slot on the PC — a file rerun alone holds them all
    held_path = held_tests.path_in(slots.folder)
    on_hold = held_tests.holds(held_tests.read(held_path)[0])
    lifted, held = [], []       # (file, its hold)
    for f in chosen:
        hold = on_hold.get(f.rel())
        if hold and f.alone and not hold.get("alone"):
            lifted.append((f, hold))
        elif hold:
            held.append((f, hold))
    chosen = [f for f in chosen if not any(f is h for h, _ in held)]

    def aside_line(f):
        return f"set aside: {f.rel()} — {f.skip['todo']} — {f.skip['why']}"

    def held_line(f, hold):
        return f"? {f.rel()}  {held_tests.not_run_reason(hold)}"

    if a.list:
        for n in id_notes:
            print(n)
        for f in chosen:
            print(f"  tier {f.tier}  {f.rel():40}  tags: {', '.join(f.tags)}"
                  + (f"  · only {', '.join(id_cells[f.path])} (--id), one process" if f.path in id_cells else
                     f"  · {f.shards} shards" if sharded(f) else "")
                  + ("  · heavy (holds a test slot)" if f.tier == 1 and f.heavy else "")
                  + (f"  · alone (every test slot, after the others — {f.alone_why})" if f.alone else ""))
        for f in aside:
            print(f"  - tier {f.tier}  {aside_line(f)}")
        for f, hold in held:
            print(f"  {held_line(f, hold)}")
        for f in broken:
            print(f"  ✗ {f.rel()}: {f.problem}")
        print(f"{len(chosen)} file(s) would run" + (f", {len(aside)} set aside" if aside else "")
              + (f", {len(held)} held — not run" if held else ""))
        return 0
    for f, hold in lifted:          # Ron's "run it alone every time": the hold taken beside others no longer applies
        _, _, err = held_tests.release(held_path, f.rel())
        print(f"! {f.rel()} was held (it couldn't be proven in {held_tests.HOLD_AFTER} runs in a row beside others, since "
              f"{str(hold.get('since', '?'))[:16].replace('T', ' ')}) — its header now says 'alone: yes — "
              f"{f.alone_why}': the hold is lifted and its streak starts over; it runs alone"
              + (f" — ✗ but the hold couldn't be cleared: {err}" if err else ""))

    # ONE entry per file — its result (passed / failed / not proven / skipped / set aside) and what goes with it; the
    # counts, the end's lines and the record are all read from these.
    entries = [{"file": f.rel(), "tier": f.tier, "result": "failed", "counts": f.problem} for f in broken]
    for f in broken:
        print(f"✗ {f.rel()}: {f.problem}")
    if not a.quiet:
        for n in id_notes:
            print(n)
    if not chosen and not broken and not aside and not held:
        if not a.quiet:   # the commit hook stays silent when no test covers the change (Law 12: no noise on the normal path)
            print("No tests cover these changes." if a.changed else "No tests match.")
        return 0
    shared_before = git_settings(repo or ROOT)
    # What narrowed this run, in words ([] = a full run): its record goes on the quick shelf, and the held streaks pass
    # it over.
    narrowing = (["--changed"] if a.changed else []) + ([f"--tag {', '.join(a.tag)}"] if a.tag else []) \
        + ([f"--id {', '.join(a.id)}"] if a.id else []) + [f"{k}={v}" for k, v in run_env().items() if RUN_ENV[k][0]]
    # The record: the commit and what's uncommitted taken BEFORE anything runs, and again at the end.
    shelf = results if results is not None else (results_dir() if real else None)   # the full runs' records
    record_to = os.path.join(shelf, QUICK_SHELF) if shelf and narrowing else shelf
    rec = None
    if record_to:
        rec = {"commit": head_commit(), "uncommitted": {"before": uncommitted()},
               "ran": {"tier": str(tier), "tags": a.tag, "ids": a.id, "changed": bool(a.changed), "release": a.release,
                       "jobs": None},
               "env": run_env(), "files": entries, "problems": [], "started": started}
        rec["id"] = record_id(rec)
    out_dir = os.path.join(record_to, rec["id"]) if rec else None   # failed files' whole outputs, beside the record
    skipped = [(f, why) for f, why in ((f, skip_reason(f)) for f in chosen) if why]
    chosen = [f for f in chosen if not any(f is s for s, _ in skipped)]
    if not a.quiet or a.release:
        for f, why in skipped:
            print(f"- {f.rel()}: skipped — {why}")
    entries += [{"file": f.rel(), "tier": f.tier, "result": "skipped", "why": why} for f, why in skipped]
    entries += [{"file": f.rel(), "tier": f.tier, "result": "set aside", **f.skip} for f in aside]

    broke = []          # failures that belong to no one file (the build, the local relay) — each fails the run
    say_lock = threading.Lock()   # one file's lines are printed together, never interleaved with another's
    outcomes = {}       # {file: its outcome in held_tests' words} — a full run adds them to this PC's held streaks

    def say(text):
        with say_lock:
            print(text, flush=True)

    def report(f, ok, out, seconds=None, waited=0.0, shards=None, cells=None, tried=None, measures=None, unproven=None):
        """One file's result: its line (and a failure's details, together — ending with where its whole output was kept)
        and its entry. shards: a file run as several processes — [{cells, seconds, waited, result, measures}]. cells: a
        sharded file narrowed by --id to these cells (one process). tried: the reruns alone after the machine's trouble.
        measures: what its process tree cost (tools/job.py). unproven: it met the machine's trouble with no rerun left
        ({why, met: how many files of the run met it}) or again on its rerun alone ({why, detail}): NOT PROVEN, never a
        failure — its line starts '?', its output is kept."""
        ids = differs_today_ids(out)
        summary = next((ln for ln in reversed(out.splitlines()) if re.search(r"\bpassed\b", ln)), "")
        wait = f", waited {waited:.0f} s for a slot" if waited >= 1 else ""
        each = f"; shards {', '.join(str(round(s['seconds'])) for s in shards)} s" if shards else ""
        only = f"; only {', '.join(cells)} (--id)" if cells else ""
        again = f"; rerun alone after {tried[0]['reason']}" if tried else ""
        took = "" if seconds is None else f"  ({seconds:.0f} s{each}{only}{wait}{again})"
        unproven = None if ok or not unproven else \
            (unproven["why"], unproven.get("detail") or
             f"{unproven['met']} file{'s' if unproven['met'] != 1 else ''} met its trouble this run; "
             f"only {MAX_RETRIES} {'is' if MAX_RETRIES == 1 else 'are'} rerun")
        output = None if ok else keep_output(out_dir, f, out)
        result = "passed" if ok else NOT_PROVEN if unproven else "failed"
        lines = []
        if ok:
            if not a.quiet:
                lines.append(f"✓ {f.rel()}  {summary.strip()}{took}")
        elif unproven:
            lines.append(f"? {f.rel()}  not proven — the machine was too busy ({unproven[1]}) — {unproven[0]}{took}")
            if output:
                lines.append(f"    full output: {output}")
        else:
            lines.append(f"✗ {f.rel()}  {summary.strip()}{took}")
            for ln in out.splitlines():
                if "✗" in ln or "Error" in ln or "FAIL" in ln or ln.startswith("      "):
                    lines.append("    " + ln)
            if output:
                lines.append(f"    full output: {output}")
        entry = {"file": f.rel(), "tier": f.tier, "result": result,
                 **({"not_proven": f"{unproven[0]} — {unproven[1]}"} if unproven else {}),
                 "counts": summary.strip(), "seconds": None if seconds is None else round(seconds, 1),
                 **({"measures": measures} if measures is not None else {}),
                 "waited": round(waited, 1), "differ": ids, **({"shards": shards} if shards else {}),
                 **({"heavy": True} if f.tier == 1 and f.heavy else {}),
                 **({"alone": True} if f.alone else {}),
                 **({"cells": cells} if cells else {}),
                 **({"output": output, "screenshots": screenshots_in(out)} if output else {}),
                 **({"retried": tried} if tried else {})}
        with say_lock:
            entries.append(entry)
            outcomes[f.rel()] = dict(held_outcome(entry, tried), where=os.path.basename(ROOT),
                                     record=rec["id"] if rec else None, alone=f.alone)
            if lines:
                print("\n".join(lines), flush=True)

    # Held on this PC (above): not run — "held — not run", NOT PROVEN, its line starts '?'; the record notes the hold.
    for f, hold in held:
        print(held_line(f, hold), flush=True)
        entries.append({"file": f.rel(), "tier": f.tier, "result": NOT_PROVEN,
                        "not_proven": held_tests.not_run_reason(hold), "held": hold})

    def run_and_report(f, relay_url):
        t0 = time.monotonic()
        code, out, m = run_process(f, relay_url=relay_url)
        report(f, code == 0, out, time.monotonic() - t0, measures=m)

    # Tiers 1 and 2 in parallel: `jobs` files at once; each screen test (or heavy tier-1 file) holds one of the first
    # `browsers` of the PC's test slots while it runs, so every run on this PC together stays within that. Tier 3 runs
    # after, one file at a time (below). A file with `shards: N` is N units of work, each in its own process with its own
    # slot. Longest first, by each unit's time in this copy's latest record.
    pooled = [f for f in chosen if f.tier != 3]
    screen = [f for f in pooled if f.tier == 2]
    heavy = [f for f in pooled if f.tier == 1 and f.heavy]
    browsers = max(1, a.jobs) if a.jobs else (test_slots.slot_count() if os.environ.get("RW_TEST_SLOTS") else JOBS)
    jobs = max(1, a.jobs) if a.jobs else max(JOBS, browsers)
    if rec:
        rec["ran"]["jobs"] = jobs
    if screen or heavy:
        free = (free_memory or test_slots.free_memory)()
        free_gb = None if free is None else round(free / 2 ** 30, 1)
        if not a.quiet:
            print(f"· browsers at once: {browsers}" + (f" · {free_gb} GB of memory free" if free_gb is not None else "")
                  + (f" · heavy tier-1 files hold a test slot too: {', '.join(f.rel() for f in heavy)}" if heavy else ""))
        if rec:
            rec["memory"] = {"free_gb": free_gb}
    if screen and real:
        err = prebuild()
        if err:
            broke.append(f"the build (dist/) failed: {err}")
            print(f"✗ build: dist/ couldn't be built before the screen tests — {err}")
    units = []          # (file, shard number or None, of how many, its cells or None)
    for f in pooled:
        if f.path in id_unlisted:
            report(f, False, id_unlisted[f.path])
        elif f.path in id_cells:        # --id named some of its cells: one process, RW_CELLS = exactly those
            units.append((f, None, None, id_cells[f.path]))
        elif sharded(f) and not os.environ.get("RW_CELLS"):
            cells, why = list_cells(f)
            if cells is None:
                report(f, False, why)
                continue
            split = shares(cells, f.shards)
            units += [(f, k, len(split), c) for k, c in enumerate(split, 1)]
        else:
            units.append((f, None, None, None))
    if units:
        last = latest_times(read_records(shelf))        # the full runs' records — never the quick shelf
        units.sort(key=lambda u: -estimate(u, last))
    shards_done = {}    # file path -> the shards finished so far
    shard_lock = threading.Lock()
    to_rerun = []       # (unit, reason, its first output's path, seconds, its first cost)
    over_cap = []       # (unit, output, t0, t1, waited, cost, reason) — the machine's trouble with no rerun left
    troubles = []       # each first run that met the machine's or the browser's trouble (reruns not counted)

    def label_of(u):
        f, k, n, _ = u
        return f.rel() + (f" (shard {k} of {n})" if k else "")

    def run_one(u):
        """(exit code, output, what it cost) — one unit's process; a runner error reported as its failure, never a lost
        thread."""
        f, _, _, cells = u
        try:
            return run_process(f, relay_url=a.relay_url, cells=cells)
        except Exception as e:      # noqa: BLE001
            return None, f"✗ the runner couldn't run it: {type(e).__name__}: {e}", job.nothing("it didn't run")

    def finish(u, ok, out, t0, t1, waited, tried=None, cost=None, unproven=None):
        """A unit is done: a whole file is reported; a shard waits until its file's last shard is done. A file of shards
        is failed if any shard failed; else not proven if any shard was; else passed."""
        f, k, n, cells = u
        if k is None:
            report(f, ok, out, t1 - t0, waited, cells=cells, tried=[tried] if tried else None, measures=cost,
                   unproven=unproven)
            return
        with shard_lock:          # the file is reported once, when its last shard is done
            done = shards_done.setdefault(f.path, [])
            done.append((k, n, cells, ok, out, t0, t1, waited, tried, cost, unproven))
            if len(done) < n:
                return
        done = sorted(done, key=lambda p: p[0])
        f_ok, f_out = combine_shards([(k, n, c, o or (None if np else False), x, b - s)
                                      for k, n, c, o, x, s, b, _, _, _, np in done])
        failed_shard = any(not p[3] and not p[10] for p in done)
        report(f, f_ok, f_out, max(p[6] for p in done) - min(p[5] for p in done), sum(p[7] for p in done),
               shards=[{"cells": len(c), "first": c[0], "seconds": round(b - s, 1),
                        **({"measures": m} if m is not None else {}), "waited": round(w, 1),
                        "result": "passed" if o else NOT_PROVEN if np else "failed", **({"retried": t} if t else {})}
                       for k, n, c, o, x, s, b, w, t, m, np in done],
               tried=[p[8] for p in done if p[8]] or None,
               measures=job.combine([p[9] for p in done]),
               unproven=None if failed_shard else next((p[10] for p in done if p[10]), None))

    # Who runs next: `jobs` workers, each taking the FIRST unit in order (longest first) that may start now — a light
    # one always; a slotted one only while one of the first `browsers` slots on the PC is free. A file whose header says
    # `alone: yes — why` isn't among them: it runs after the others, holding EVERY test slot on the PC.
    pending = [u for u in units if not u[0].alone]
    alone_units = [u for u in units if u[0].alone]
    turn = threading.Condition()       # a worker waits here for room; a unit ending wakes it
    waiting_since = {}                  # id(unit) -> when it first found every slot it may use taken

    def take():
        """(unit, its slot or None) — the next unit this worker may start; None when none is left. Waits while only
        slotted units remain and there's no free slot for them."""
        while True:
            with turn:
                if not pending:
                    return None
                full = False            # no slot this time round: only light ones are looked at
                for u in list(pending):
                    if not slotted(u[0]):
                        pending.remove(u)
                        return u, None
                    if full:
                        continue
                    slot = slots.try_acquire(f"{ROOT} · {label_of(u)}", upto=browsers)
                    if slot is None:
                        full = True
                        if id(u) not in waiting_since:      # said once for it, naming the holders
                            waiting_since[id(u)] = time.monotonic()
                            say(slots.wait_message(f"{ROOT} · {label_of(u)}", browsers))
                        continue
                    pending.remove(u)
                    slot.waited = time.monotonic() - waiting_since.pop(id(u), time.monotonic())
                    return u, slot
                turn.wait(0.5)          # (another run's slot freeing is seen within half a second)

    def worker():
        while True:
            got = take()
            if got is None:
                return
            try:
                run_unit(*got)
            finally:
                with turn:
                    turn.notify_all()

    def run_unit(u, slot):
        f, k, _, _ = u
        try:
            t0 = time.monotonic()
            code, out, cost = run_one(u)
            t1 = time.monotonic()
            why = environment_reason(f, code, out)
        finally:
            if slot:
                slot.release()
        waited = slot.waited if slot else 0.0
        if not why:
            finish(u, code == 0, out, t0, t1, waited, cost=cost)
            return
        with say_lock:      # the machine's or the browser's trouble: rerun once, alone, when the others are done
            troubles.append(label_of(u))
            rerun = len(to_rerun) < MAX_RETRIES
            if rerun:
                to_rerun.append((u, why, keep_output(out_dir, f, out, k, "first"), t1 - t0, cost))
        if rerun:
            say(f"! {label_of(u)}: the machine's or the browser's trouble — {why} — it will be rerun once, alone, "
                "when the others are done")
            return
        # No rerun left: NOT PROVEN, never a failure — reported when the others are done, once the run knows how many
        # met the trouble.
        say(f"! {label_of(u)}: {why} — the machine's trouble, but {MAX_RETRIES} file(s) of this run are already rerun — "
            "not rerun: it will be reported NOT PROVEN, not failed")
        out += (f"\n! not rerun: {MAX_RETRIES} file(s) of this run were already taken for a rerun after the machine's "
                "or the browser's trouble — that many points at something broken, not a passing hiccup — so this "
                "file is NOT PROVEN (not failed)")
        with say_lock:
            over_cap.append((u, out, t0, t1, waited, cost, why))

    if pending:
        workers = min(jobs, len(pending))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            for fut in concurrent.futures.as_completed([pool.submit(worker) for _ in range(workers)]):
                fut.result()
    for u in alone_units:       # alone: yes — one at a time, each holding every test slot on the PC
        say(f"· {label_of(u)} runs alone (its header: alone: yes — {u[0].alone_why}): holding every test slot on this PC "
            f"({slots.count})")
        run_unit(u, slots.acquire_all(f"{ROOT} · {label_of(u)} (alone: yes)", on_wait=say))
    for u, out, t0, t1, waited, cost, why in over_cap:
        finish(u, False, out, t0, t1, waited, cost=cost, unproven={"why": why, "met": len(troubles)})
    # The reruns, ALONE: every other file of this run is done; after a wait, each holds EVERY test slot on the PC. Rerun
    # once: passed → passed (noted); the machine's trouble AGAIN → NOT PROVEN, never a failure; any other failure →
    # failed.
    for u, why, first, first_secs, first_cost in to_rerun:
        f, k, _, _ = u
        say(f"! rerunning {label_of(u)} alone — after {why}: waiting {retry_wait:g} s, then holding every test slot on "
            f"this PC ({slots.count})")
        time.sleep(retry_wait)
        group = slots.acquire_all(f"{ROOT} · {label_of(u)} (rerun alone)", on_wait=say)
        t0 = time.monotonic()
        try:
            code, out, cost = run_one(u)
        finally:
            group.release()
        t1 = time.monotonic()
        again = environment_reason(f, code, out)
        tried = {"shard": k, "reason": why, "first_output": first, "first_seconds": round(first_secs, 1),
                 "first_measures": first_cost,
                 "rerun": "passed" if code == 0 else f"not proven — the machine's trouble again: {again}" if again
                 else "failed", "rerun_output": keep_output(out_dir, f, out, k, "rerun")}
        finish(u, code == 0, f"! rerun alone after {why} — its first output: {first or '(not kept: no record)'}\n" + out,
               t0, t1, group.waited, tried, cost=cost,
               unproven={"why": again, "detail": "it met its trouble again on its rerun alone — one rerun a run"}
               if again and code != 0 else None)

    # Tier 3 with no --relay-url: the runner starts its OWN local relay around the relay files (in a job of its own),
    # then stops it and checks everything it started is gone and its ports are free. A given --relay-url is used as is.
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
            broke.append(f"the local relay didn't start — not run: {', '.join(f.rel() for f in own_relay)}")
            print(f"✗ local relay: {e}\n    not run: " + ", ".join(f.rel() for f in own_relay))
        else:
            try:
                for f in own_relay:
                    run_and_report(f, url)
            finally:
                left = r.stop()
            if left:
                broke.append("the local relay: not everything it started was stopped — " + "; ".join(left))
                print("✗ local relay: not everything it started was stopped —\n    " + "\n    ".join(left))
            elif not a.quiet:
                print(f"✓ local relay stopped — every process it started is gone, ports {', '.join(map(str, r.ports))} free")
        if rec and getattr(r, "measures", None) is not None:
            rec["relay"] = {"seconds": r.seconds, "measures": r.measures}

    n = collections.Counter(e["result"] for e in entries)
    failed = n["failed"] + len(broke)
    held_n = sum(1 for e in entries if e.get("held"))
    print(f"Tests: {n['passed']} file(s) passed, {failed} failed"
          + (f", {n[NOT_PROVEN]} not proven (the machine's trouble"
             + (f" — {held_n} held, not run" if held_n else "") + ")" if n[NOT_PROVEN] else "")
          + (f", {n['skipped']} skipped" if n["skipped"] else "") + (f", {n['set aside']} set aside" if n["set aside"] else ""))
    if over_cap:                 # loudly: not a test failure — but that much trouble is worth a look at the machine
        print(f"! {len(troubles)} file{'s' if len(troubles) != 1 else ''} met the machine's or the browser's trouble this "
              f"run — only {MAX_RETRIES} "
              f"{'is' if MAX_RETRIES == 1 else 'are'} rerun alone; that many points at something broken, not a passing "
              f"hiccup — look at what else the PC is doing (TESTING.md §7). NOT PROVEN, not failed: "
              + ", ".join(dict.fromkeys(label_of(u) for u, *_ in over_cap)))
    for f in aside:              # plainly, every run — the commit hook's too: a set-aside test is work owed
        print(aside_line(f))
    for e in entries:            # loudly, never silent: a rerun is read, not taken on trust (TESTING.md §7)
        for t in e.get("retried") or []:
            print(f"! 1 file retried after {t['reason']} — its first output: {t['first_output'] or '(not kept: no record)'}"
                  f"\n    {e['file']}" + (f" (shard {t['shard']})" if t.get("shard") else "") + f" — rerun alone: {t['rerun']}"
                  + (f" — the rerun's output: {t['rerun_output']}" if t.get("rerun_output") else ""))
    # This PC's held streaks (tools/held_tests.py): a FULL run's outcomes are added; a file met by the machine's trouble
    # 2 full runs in a row is said loudly, one NOT PROVEN 3 in a row is HELD — said.
    if not narrowing and outcomes:
        troubled, newly, err = held_tests.note_run(held_path, outcomes)
        if err:
            print(f"· the held tests' streaks not saved — {err}")
        for name, streak in troubled.items():
            if name in newly:
                print("\n".join(held_tests.held_lines(name, {"runs": streak[-held_tests.HOLD_AFTER:]})))
            elif len(streak) >= held_tests.SAID_AFTER:
                print("\n".join(held_tests.streak_lines(name, streak)))
    for f, hold in held:         # loudly, every run: a held file is waiting for Ron
        print(f"! held — not run: {f.rel()} — it couldn't be proven in {held_tests.HOLD_AFTER} runs in a row on this PC "
              f"(since {str(hold.get('since', '?'))[:16].replace('T', ' ')}). {held_tests.ways_out(f.rel())}")
    for e in entries:
        if e.get("output"):
            unproven = e["result"] == NOT_PROVEN
            print(f"{'? ' if unproven else '✗ '}{e['file']} — " + ("not proven (the machine's trouble) — " if unproven
                                                                   else "") + f"full output: {e['output']}")
    problems = list(broke)
    refused = False
    if a.release and skipped:    # a release needs every file to have RUN — skipped is not passed
        print(f"✗ release run: {len(skipped)} file(s) skipped — a release needs every file to run:\n    "
              + "\n    ".join(f"{f.rel()} — {why}" for f, why in skipped))
        refused = True
    if a.release and aside:      # set aside on purpose still blocks the next release until it's fixed
        print(f"✗ release run: {len(aside)} file(s) set aside — a set-aside test blocks the release until its TODO task "
              "fixes it and its skip: line is gone:\n    "
              + "\n    ".join(f"{f.rel()} — {f.skip['todo']} — {f.skip['why']}" for f in aside))
        refused = True
        problems.append(f"release run: {len(aside)} file(s) set aside")
    differ = [(e["file"], e["differ"]) for e in entries if e.get("differ")]
    if a.release and differ:     # a decided behavior not built yet is fine while building, never in a release
        count = sum(len(ids) for _, ids in differ)
        print(f"✗ release run: {count} test(s) still differ from what was decided (marked 'differs today') — build them, "
              f"or take the decision back to Ron, before a release:\n    "
              + "\n    ".join(f"{name}: {', '.join(ids)}" for name, ids in differ))
        refused = True
        problems.append(f"release run: {count} test(s) still marked 'differs today'")
    changed = settings_changed(shared_before, git_settings(config=shared_before["config"]) if shared_before else None)
    if changed:                  # loudly, quiet or not: every working copy shares these
        print("\n".join(changed), flush=True)
    # 1 for a failure (it wins); 3 — the machine's trouble — when nothing failed but a file is NOT PROVEN; else 0.
    code = 1 if refused or failed else environment_trouble.EXIT_CODE if n[NOT_PROVEN] else 0
    if rec:
        rec.update({"commit_after": head_commit(), "problems": problems, "ended": _now(),
                    "seconds": round(time.monotonic() - t_start),
                    "result": "passed" if code == 0 else NOT_PROVEN if code == environment_trouble.EXIT_CODE else "failed"})
        rec["uncommitted"]["after"] = uncommitted()
        if changed:
            rec["git_settings_changed"] = changed
        try:
            write_record(rec, record_to, keep=KEEP_QUICK if narrowing else KEEP_RECORDS)
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
