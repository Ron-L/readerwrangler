#!/usr/bin/env python3
"""
starter.py — the ONE starter for every process our test tools start, and the list of what they started (TODO "One
starter for every process our tools start: a list of their ids, leftovers shown loudly", 20261112-1240 — Ron + Claude,
2026-11-12, review queue Q-020, Q-022, Q-024; built 2026-11-18, sprint 9). Grown from tools/local_relay.py, whose
process code moved here.

Who starts through it (Law 22 — one way): the relay tests' local relay (tools/run_tests.py --tier 3) and the screen
tests' own relay (test/ui/rw.py App(relay=True)) — both through tools/local_relay.py — and the screen tests' web server
(rw.App: serve.py).

    p = Started("the screen tests' web server (serve.py) for test_x.py", ports=[port])
    p.start([python, "serve.py", str(port)], cwd=ROOT, stdout=DEVNULL, stderr=DEVNULL)    # on the list at once
    p.note_tree()           # every process now running under it, each started after its parent — on the list too
    left = p.stop()         # [] = every process it started is gone AND its ports are free — else what's left, in words

1. THE LIST — a file of every process started (`started-processes.json` beside the test slots: %TEMP%\\rw-test-slots, or
   RW_TEST_SLOTS_DIR — so every working copy's runs share it). Each entry: its id, its START TIME (Windows has no real
   process label — the start time means an id Windows later gives another process is never taken for ours), its program,
   WHAT it is, WHICH RUN started it (RW_RUN_ID: the runner gives its label to every file it starts — else "<script> run
   directly"), the process that started it (its OWNER, with its start time), its ports and when. An entry leaves the
   list only when its process is CONFIRMED GONE — no process with that id and that start time (Ron: "keep a list of IDs
   as you create them, delete from list when confirmed dead"). The file outlives a crashed run. Several runs on this PC
   at once (working copies) each read, change and write it whole under the slots' own OS file lock
   (tools/test_slots.py locked — no second lock), written by browser_level.save (a temporary file put in place). A list
   that can't be updated never fails a test: it says so, loudly, on the error output.

2. STOPPING (PRINCIPLES Law 5, Law 12): every process in the tree — each by its EXACT id, its start time checked first
   (`taskkill /PID <id> /F`; never `/T`, which follows parent ids Windows reuses; never by name or pattern) — the children
   first, then the one started (by its own handle), and then CHECKED: each one gone, each port no longer listening.
   Anything ours still running stays on the list and is reported by id and name. Something on our port that the list
   doesn't name is REPORTED, never stopped (it isn't provably ours) — and kept on the list's "unnamed" side so the next
   run's start banner names it once more.

3. LEFTOVERS SHOWN LOUDLY (Ron: "draw my attention to it") — a banner (banner()), not a line in the slew:
   - at the START of a run (tools/run_tests.py, every run that runs tests — the commit hook's too): every listed process
     still running whose run has ended (its owner gone) — what it is, which run, since when, and the exact command to
     stop it; and what was found unnamed on our ports. A process whose run is still going (another working copy's) is
     not a leftover. The banner stops nothing;
   - at the END of the run that left them: every process that run started still running;
   - and one line starting `NEEDS YOUR ATTENTION:` — the line Claude reads for its "needs your attention" list when
     reporting to Ron.
   `py tools/starter.py` prints the same banner on its own (nothing run, nothing stopped).

A test unit's own leftovers (a process still running after the unit's process ended — in its job, so provably its own)
are found and stopped by tools/test_costs.py (its job's handle); the runner names them with the same loud lines.

Tested by test/test_starter.py (START-001–013); the relay's own rows in test/test_run_tests.py (RUN-016–021, 052, 053,
057).
"""
import datetime
import os
import socket
import subprocess
import sys
import time

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser_level    # noqa: E402 — tools/: its save() writes a file whole (a temporary file, then put in place)
import test_slots       # noqa: E402 — tools/: the slots' OS file lock (locked()) and their folder (slots_folder())

FILE_NAME = "started-processes.json"
RUN_VAR = "RW_RUN_ID"       # which run a process belongs to: the runner sets it for every file it starts
LOCK_LIMIT_S = 30.0         # the list waits this long at most for another run's change
STOP_S = 10.0               # how long a stop waits for everything to be gone and the ports free
ATTENTION = "NEEDS YOUR ATTENTION:"


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# --- processes, by exact id (moved here from local_relay.py) ---------------------------------------------------------
if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _k32.OpenProcess.restype = wintypes.HANDLE
    _INVALID = wintypes.HANDLE(-1).value
    _QUERY = 0x1000          # PROCESS_QUERY_LIMITED_INFORMATION
    _STILL_ACTIVE = 259

    class _Entry(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                    ("szExeFile", ctypes.c_wchar * 260)]

    def processes():
        """{pid: (parent pid, program name)} for every process on this PC right now."""
        snap = _k32.CreateToolhelp32Snapshot(0x2, 0)       # TH32CS_SNAPPROCESS
        if snap == _INVALID:
            raise OSError(ctypes.get_last_error(), "can't list the processes")
        out = {}
        try:
            e = _Entry()
            e.dwSize = ctypes.sizeof(_Entry)
            ok = _k32.Process32FirstW(snap, ctypes.byref(e))
            while ok:
                out[e.th32ProcessID] = (e.th32ParentProcessID, e.szExeFile)
                ok = _k32.Process32NextW(snap, ctypes.byref(e))
        finally:
            _k32.CloseHandle(snap)
        return out

    def started_at(pid):
        """The process's start time (an opaque number), or None if it isn't running (or can't be asked)."""
        h = _k32.OpenProcess(_QUERY, False, pid)
        if not h:
            return None
        try:
            code = wintypes.DWORD()
            if not _k32.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != _STILL_ACTIVE:
                return None
            times = [wintypes.FILETIME() for _ in range(4)]
            if not _k32.GetProcessTimes(h, *[ctypes.byref(t) for t in times]):
                return None
            return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
        finally:
            _k32.CloseHandle(h)

    def stop_one(pid):
        # One process, by its exact id — never /T: taskkill /T follows recorded PARENT ids, and Windows reuses ids, so an
        # older, unrelated process whose dead parent's id our process happened to get would be taken too (review,
        # 2026-11-12). The tree is ours to walk (Started.note_tree checks each start time); stop_one stops one.
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)

    def port_owners(port):
        """Ids of the processes listening on this port (netstat; 'listening' read from the 0.0.0.0:0 / [::]:0 remote
        address, not the state word, which Windows translates)."""
        out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True, errors="replace").stdout
        out += subprocess.run(["netstat", "-ano", "-p", "TCPv6"], capture_output=True, text=True, errors="replace").stdout
        owners = set()
        for ln in out.splitlines():
            parts = ln.split()
            if (len(parts) == 5 and parts[0].upper().startswith("TCP") and parts[1].rsplit(":", 1)[-1] == str(port)
                    and parts[2] in ("0.0.0.0:0", "[::]:0") and parts[4].isdigit()):
                owners.add(int(parts[4]))
        return owners
else:   # Ron's PC is Windows; this branch keeps the module usable elsewhere (a contributor's Mac or Linux) — less tested.
    import signal

    def processes():
        out = subprocess.run(["ps", "-A", "-o", "pid=,ppid=,comm="], capture_output=True, text=True).stdout
        procs = {}
        for ln in out.splitlines():
            parts = ln.split(None, 2)
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                procs[int(parts[0])] = (int(parts[1]), parts[2])
        return procs

    def started_at(pid):   # a date string: compared for equality only
        out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
        return out or None

    def stop_one(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

    def port_owners(port):
        return set()


def listening(port):
    """Ids of what listens on the port — {0} when something answers but its owner can't be named. On Windows netstat
    alone: it names the owner, and a test connection to a closed local port takes Windows ~1 s to refuse."""
    owners = port_owners(port)
    if not owners and os.name != "nt":
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                owners = {0}
    return owners


def still_ours(pid, start):
    """Is this exact process still running — this id AND this start time (an id reused since is not ours)?"""
    return start is not None and started_at(pid) == start


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_label():
    """Which run this process belongs to: RW_RUN_ID (set by the runner for every file it starts), else this process —
    a test file or a tool run directly."""
    return os.environ.get(RUN_VAR) or \
        f"{os.path.basename(sys.argv[0] or 'python') or 'python'} run directly (process {os.getpid()})"


def new_run(root):
    """A run's label — what its files are given as RW_RUN_ID, and what the list says started a process."""
    return f"the test run of {_now()} in {root} (process {os.getpid()})"


# --- 1. the list ------------------------------------------------------------------------------------------------------
def list_path(folder=None):
    return os.path.join(folder or test_slots.slots_folder(), FILE_NAME)


def _fresh():
    return {"version": 1, "processes": [], "unnamed": []}


def _say(text):
    """A problem with the list itself — loud, on the error output; never a test failure."""
    print(f"! the list of started processes: {text}", file=sys.stderr, flush=True)


class Ledger:
    """The list in a file (see the top). Every read and change is made under the slots' OS file lock."""

    def __init__(self, path=None):
        self.path = path or list_path()

    def _load(self):
        import json
        try:
            with open(self.path, encoding="utf-8") as f:
                s = json.load(f)
        except FileNotFoundError:
            return _fresh()
        except (OSError, ValueError) as e:
            _say(f"{self.path} couldn't be read ({type(e).__name__}) — starting it again")
            return _fresh()
        if not isinstance(s, dict) or not isinstance(s.get("processes"), list):
            _say(f"{self.path} was damaged — starting it again")
            return _fresh()
        s.setdefault("unnamed", [])
        return s

    def _change(self, fn, write=True):
        """fn(state) under the lock — read, changed, written whole. (True, fn's result), or (False, None) when the lock
        or the file failed (said loudly)."""
        try:
            with test_slots.locked(self.path + ".lock", limit_s=LOCK_LIMIT_S) as got:
                if not got:
                    _say(f"another run held its lock for {LOCK_LIMIT_S:g} s — not updated ({self.path})")
                    return False, None
                state = self._load()
                result = fn(state)
                if write:
                    err = browser_level.save(self.path, state)
                    if err:
                        _say(err)
                        return False, result
                return True, result
        except OSError as e:
            _say(f"{self.path}: {e}")
            return False, None

    def entries(self):
        """Every process on the list, as it is (nothing tidied)."""
        return self._change(lambda s: list(s["processes"]), write=False)[1] or []

    def unnamed(self):
        return self._change(lambda s: list(s["unnamed"]), write=False)[1] or []

    def add(self, entries):
        """Put these on the list (the same entry already there — id, start time and what — is replaced)."""
        def key(e):
            return e.get("pid"), e.get("start"), e.get("what")

        def fn(s):
            keys = {key(e) for e in entries}
            s["processes"] = [e for e in s["processes"] if key(e) not in keys] + list(entries)
        if entries and not self._change(fn)[0]:
            _say("not listed: " + ", ".join(f"process {e['pid']} ({e.get('what')})" for e in entries))

    def add_unnamed(self, found):
        """Something found on a port of ours that the list doesn't name — kept for the next run's start banner."""
        def fn(s):
            keys = {(u["pid"], u["start"]) for u in found}
            s["unnamed"] = [u for u in s["unnamed"] if (u.get("pid"), u.get("start")) not in keys] + list(found)
        if found:
            self._change(fn)

    def drop_gone(self, pids):
        """Take off the list each of these that is CONFIRMED gone (no process with its id and start time)."""
        def fn(s):
            s["processes"] = [e for e in s["processes"]
                              if e.get("pid") not in pids or still_ours(e.get("pid"), e.get("start"))]
        if pids:
            self._change(fn)

    def review(self, run=None):
        """What needs saying, the list tidied on the way (every entry confirmed gone leaves it):
        {"leftovers": [entry…], "unnamed": [{pid, name, port, of, run}…]}.
        run None — a run's START: leftovers = processes on the list still running whose run has ENDED (their owner
        gone); a process of a run still going (another working copy's) is none. unnamed = what's on a port of such an
        entry (still running or just confirmed gone) that the list doesn't name, plus what a stop found earlier — each
        said once, then dropped (it isn't ours to keep track of).
        run given — that run's END: every process it started still running, and what its stops found unnamed."""
        names = {}

        def name_of(pid):
            if not names:
                names.update({p: n for p, (_, n) in processes().items()})
            return names.get(pid, "?")

        def fn(s):
            leftovers, check, keep = [], [], []
            for e in s["processes"]:
                live = still_ours(e.get("pid"), e.get("start"))
                owner = e.get("owner") or {}
                ended = not still_ours(owner.get("pid"), owner.get("start"))
                mine = run is not None and e.get("run") == run
                if live:
                    keep.append(e)
                    if mine or (run is None and ended):
                        leftovers.append(e)
                        check.append(e)
                elif mine or (run is None and ended):
                    check.append(e)         # just confirmed gone: is something else on its port now?
            s["processes"] = keep
            listed = {e["pid"] for e in keep}
            unnamed = []
            for e in check:
                for port in e.get("ports") or []:
                    for o in sorted(port_owners(port) - listed - {0}):
                        unnamed.append({"pid": o, "start": started_at(o), "name": name_of(o), "port": port,
                                        "of": e.get("what"), "run": e.get("run")})
            earlier = [u for u in s["unnamed"] if still_ours(u.get("pid"), u.get("start"))
                       and (run is None or u.get("run") == run)]
            seen = {(u["pid"], u["port"]) for u in unnamed}
            unnamed += [u for u in earlier if (u["pid"], u.get("port")) not in seen]
            # said once (at a start, or at the end of its own run), then dropped; others' stay for their turn
            said = {(u["pid"], u.get("start")) for u in earlier}
            s["unnamed"] = [u for u in s["unnamed"] if (u.get("pid"), u.get("start")) not in said
                            and still_ours(u.get("pid"), u.get("start"))]
            return {"leftovers": leftovers, "unnamed": unnamed}
        return self._change(fn)[1] or {"leftovers": [], "unnamed": []}


# --- 3. the loud lines ------------------------------------------------------------------------------------------------
BAR = "!! " + "═" * 110


def banner(review, at="start"):
    """The banner for what review() found — [] when there's nothing to say. at: "start" (leftovers of earlier runs) or
    "end" (left running by this run)."""
    left, unnamed = review.get("leftovers") or [], review.get("unnamed") or []
    if not left and not unnamed:
        return []
    out = [BAR]
    if left:
        out.append(f"!! LEFTOVER PROCESSES — {len(left)} started by "
                   + ("an earlier test run on this PC" if at == "start" else "THIS run")
                   + " and still running:")
        for e in left:
            out.append(f"!!   process {e['pid']} ({e.get('name') or '?'}) — {e.get('what')}"
                       + (f", port {', '.join(map(str, e['ports']))}" if e.get("ports") else ""))
            out.append(f"!!       started {e.get('since')} by {e.get('run')}"
                       + (" — that run has ended" if at == "start" else ""))
            out.append(f"!!       stop it:  taskkill /PID {e['pid']} /F")
    if unnamed:
        out.append(f"!! ON OUR PORTS, NOT ON THE LIST — {len(unnamed)} process(es) the tools can't show they started: "
                   "reported, never stopped by the tools:")
        for u in unnamed:
            out.append(f"!!   process {u['pid']} ({u.get('name') or '?'}) on port {u.get('port')} — a port of "
                       f"{u.get('of')} ({u.get('run')})")
            out.append(f"!!       if it's a leftover, stop it by its id:  taskkill /PID {u['pid']} /F")
    out.append(BAR)
    said = []
    if left:
        said.append(f"{len(left)} leftover process(es) "
                    + ("from an earlier test run" if at == "start" else "left running by this test run") + " — "
                    + "; ".join(f"process {e['pid']} ({e.get('name') or '?'}): taskkill /PID {e['pid']} /F" for e in left))
    if unnamed:
        said.append(f"{len(unnamed)} process(es) on our ports not on the list (not provably ours) — "
                    + "; ".join(f"process {u['pid']} ({u.get('name') or '?'}) on port {u.get('port')}"
                                for u in unnamed))
    out.append(f"{ATTENTION} " + " · ".join(said))
    return out


def job_leftover_lines(found):
    """The loud lines for test units that left processes running after they ended (tools/test_costs.py stopped them by
    their job's handle): found = [(the unit's name, [{pid, name, stopped}])]. [] when none."""
    if not found:
        return []
    out = [BAR, "!! LEFT RUNNING AFTER ITS TEST ENDED — still running when its file's own process ended; in its job, so "
                "started by it: stopped by its job's handle:"]
    for label, procs in found:
        for p in procs:
            out.append(f"!!   {label}: process {p['pid']} ({p.get('name') or '?'}) — "
                       + ("stopped by its job, checked gone" if p.get("stopped") else
                          f"stopped by its job, but STILL RUNNING — stop it:  taskkill /PID {p['pid']} /F"))
    out.append(BAR)
    out.append(f"{ATTENTION} " + "; ".join(
        f"{label} left {len(procs)} process(es) running after it ended ("
        + ", ".join(f"{p['pid']} {p.get('name') or '?'}" for p in procs) + ") — stopped by its job; a leak in the test "
        "or a tool it uses" for label, procs in found))
    return out


# --- 2. one started process and its tree ------------------------------------------------------------------------------
class Started:
    """One process we start — and every process of its tree we see — each on the list from the moment it's known, off
    it only when confirmed gone. what: what it is, in words (the list and the banners say it). ports: the ports it is
    to serve — checked free at the stop. ledger: the list (None = this PC's). run: which run (None = run_label())."""

    def __init__(self, what, ports=(), ledger=None, run=None):
        self.what, self.ports = what, list(ports)
        self.ledger = ledger or Ledger()
        self.run = run or run_label()
        self.proc = None
        self.ours = {}      # pid -> (start time, program name): every process seen in our tree
        self.args = None

    def start(self, args, job=None, **popen_kw):
        """Start it — listed at once. job: a tools/test_costs.py job to start it in (measured, from its first
        instruction); None = none. popen_kw: as subprocess.Popen's. Returns the Popen."""
        self.args = list(args)
        if job is not None:
            import test_costs      # (imported here: test_costs uses this module's process list)
            self.proc, why = test_costs.launch(self.args, job, **popen_kw)
            if why:
                _say(f"{self.what} runs outside its job — {why}")
        else:
            self.proc = subprocess.Popen(self.args, **popen_kw)
        self.ours = {self.proc.pid: (started_at(self.proc.pid), os.path.basename(self.args[0]))}
        self._list([self.proc.pid])
        return self.proc

    def _list(self, pids):
        owner = {"pid": os.getpid(), "start": started_at(os.getpid())}
        self.ledger.add([{"pid": p, "start": self.ours[p][0], "name": self.ours[p][1], "what": self.what,
                          "run": self.run, "owner": owner, "ports": self.ports if p == self.proc.pid else [],
                          "since": _now()} for p in pids if self.ours[p][0] is not None])

    def note_tree(self):
        """Add every process now running under ours (by parent id; a child must have started after its parent, so a
        reused id is never adopted) — and list each new one."""
        if self.proc is None:
            return
        procs = processes()
        todo, new = list(self.ours), []
        while todo:
            parent = todo.pop()
            for pid, (ppid, name) in procs.items():
                if ppid == parent and pid not in self.ours:
                    t, pt = started_at(pid), self.ours[parent][0]
                    if t is not None and not (isinstance(t, int) and isinstance(pt, int) and t < pt):
                        self.ours[pid] = (t, name)
                        todo.append(pid)
                        new.append(pid)
        self._list(new)

    def alive(self):
        """{pid: name} of the processes of ours still running."""
        return {pid: name for pid, (t, name) in self.ours.items() if still_ours(pid, t)}

    def stop(self, stop_s=STOP_S, ports=None, not_ours=None):
        """Stop everything we started, then check. ports: the ports to check free (None = its own); not_ours: {port: ids}
        of processes known to be there and not ours (not "left" — e.g. found there when a start was given up on).
        Returns what's left, in words ([] = all gone, ports free). Each gone process leaves the list; one still running
        stays on it; something unnamed on a port is reported and kept for the next run's start banner."""
        if self.proc is None:
            return []
        ports = self.ports if ports is None else list(ports)
        not_ours = not_ours or {}
        if self.proc.poll() is None:
            self.note_tree()
        # Every process proven ours (its start time checked as it was adopted, and again now), each by its exact id —
        # the children first, then the one we started (by its own handle), so nothing is left to start new ones
        root = self.proc.pid
        for pid, (t, _) in self.ours.items():
            if pid != root and still_ours(pid, t):
                stop_one(pid)
        try:
            self.proc.kill()
        except OSError:
            pass
        try:
            self.proc.wait(stop_s)
        except subprocess.TimeoutExpired:
            pass
        deadline = time.monotonic() + stop_s
        while True:
            alive = self.alive()
            owners = {p: listening(p) - not_ours.get(p, set()) for p in ports}
            ours_on = {p: o & set(alive) for p, o in owners.items() if o & set(alive)}     # ours, still serving
            on_ports = {p: o - set(self.ours) for p, o in owners.items() if o - set(self.ours)}     # not on the list
            if (not alive and not on_ports) or time.monotonic() > deadline:
                break
            time.sleep(0.2)
        self.ledger.drop_gone([p for p in self.ours if p not in alive])
        names = processes()
        left = [f"still running after the stop: process {pid} ({name}) — {self.what}; stop it:  taskkill /PID {pid} /F"
                for pid, name in sorted(alive.items())]
        for p, owners in sorted(ours_on.items()):
            left.append(f"port {p} is still in use by " + ", ".join(f"process {o}" for o in sorted(owners))
                        + " (above)")
        unnamed = []
        for p, owners in sorted(on_ports.items()):
            who = ", ".join("an unknown process" if o == 0 else f"process {o} ({names.get(o, (0, '?'))[1]})"
                            for o in sorted(owners))
            ids = [o for o in sorted(owners) if o]
            left.append(f"port {p} is still in use by {who}" + (
                " — not one the tools can show they started, so it was left running. Stop it by its id: "
                + "  ".join(f"taskkill /PID {o} /F" for o in ids) if ids else ""))
            unnamed += [{"pid": o, "start": started_at(o), "name": names.get(o, (0, "?"))[1], "port": p,
                         "of": self.what, "run": self.run} for o in ids]
        self.ledger.add_unnamed([u for u in unnamed if u["start"] is not None])
        self.proc = None
        return left


def main():
    """`py tools/starter.py` — what's on the list now: the leftovers of runs that have ended, and anything unnamed found
    on our ports — the start banner, on its own. Nothing is started or stopped."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:       # noqa: BLE001
        pass
    lines = banner(Ledger().review())
    print("\n".join(lines) if lines else
          f"Nothing our test tools started is left running (the list: {list_path()}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
