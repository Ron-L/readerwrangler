"""
local_relay.py — a local relay for the relay tests (tier 3): relay-worker.js in Cloudflare's own emulator on this PC
(`wrangler dev --env dev --local`), on a free port, with an empty store made for the run and deleted after
(docs/design/TESTING.md §3; TODO "Turn more of our working rules into automatic checks", item 3; 2026-11-12).

    relay = LocalRelay()
    url = relay.start()     # waits for wrangler's "Ready on …" line; RelayError (loud, with the end of its output) if not
    ...                     # run the tests against url
    left = relay.stop()     # [] when everything it started is gone AND its ports are free — else what's left, in words

Never the dev or production relay: the address is always http://127.0.0.1:<the port it chose>.

The ONE relay launcher (2026-11-16, Law 22): the relay tests' (run_tests.py --tier 3) and the screen tests'
(test/ui/rw.py App(relay=True), which adds `--var ALLOWED_ORIGINS:<its page's address>` through extra_args).

"Ready" is proven against OUR process, not taken from whoever answers: the free port is chosen, then taken by wrangler a
moment later, and with tests in parallel another run's relay can take it in between (wrangler on a taken port dies:
"The Workers runtime failed to start", seen 2026-11-16 — while it starts, the port answers with the OTHER relay). So it
is ready only when wrangler's own ready line names our port AND everything listening there is a process we started
(Windows: by id). Another process on one of its ports — when it's ready, or when it stopped before it was ready (what a
taken port does to wrangler) — is judged as stopping is (Law 5: only what's PROVEN):
  - started BEFORE our relay → proven not ours (no process starts before its parent): left alone, and the relay is
    started again on new ports (3 tries in all; a wrangler that just stopped early is tried again too);
  - started after → it may be one of ours that escaped the tree, and each new try would leave another: fails loud,
    named by id, left running — never retried.


Stopping (PRINCIPLES Law 5, Law 12 — 7.28.0: ending the shell that started a relay left workerd and three node
processes serving its port, caught only by checking the port): every process it started is listed by exact id — with
its start time, so a reused id is never taken for ours — each is stopped by its exact id (`taskkill /PID <id> /F`; never
`/T`, which follows parent ids that Windows reuses; never by name or pattern), and then it is CHECKED: each listed
process gone, each port no longer listening.
Anything left is reported by id and name and never stopped here — a process we can't show we started isn't ours to stop.
"""
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELAY_DIR = os.path.join(ROOT, "relay")
WRANGLER = os.path.join(RELAY_DIR, "node_modules", "wrangler", "bin", "wrangler.js")
# wrangler from relay/node_modules (relay/package.json) — the same one `npx wrangler` finds there, without npx's extra
# command-shell layer. {port}, {inspector_port} and {store} are filled in at start.
WRANGLER_ARGS = ["dev", "--env", "dev", "--local", "--ip", "127.0.0.1", "--port", "{port}",
                 "--inspector-port", "{inspector_port}", "--persist-to", "{store}",
                 "--show-interactive-dev-session=false"]
READY = re.compile(r"\bReady on http://[^\s/]*:(\d+)")      # the port it says it serves
ANSI = re.compile(r"\x1b\[[0-9;]*m")
START_S = 60    # wrangler is ready in ~2 s on Ron's PC (2026-11-12)
STOP_S = 10
ATTEMPTS = 3    # tries, each on new ports, when wrangler stops before it's ready (a taken port)


class RelayError(RuntimeError):
    pass


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# --- processes, by exact id ------------------------------------------------------------------------------------------
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
        # older, unrelated process whose dead parent's id our relay happened to get would be taken too (review,
        # 2026-11-12). The tree is ours to walk (LocalRelay._note_tree checks each start time); stop_one stops one.
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


# --- the relay -------------------------------------------------------------------------------------------------------
class LocalRelay:
    """command: the program and its arguments ({port}, {inspector_port}, {store} filled in) — None = wrangler.
    The tests give a stand-in here (test/test_run_tests.py). extra_args: added after them, as given (the screen tests'
    `--var ALLOWED_ORIGINS:<address>`)."""

    def __init__(self, command=None, cwd=RELAY_DIR, start_s=START_S, stop_s=STOP_S, extra_args=(), attempts=ATTEMPTS):
        self.command, self.cwd, self.start_s, self.stop_s = command, cwd, start_s, stop_s
        self.extra_args, self.attempts = list(extra_args), attempts
        self.proc = None
        self.ours = {}      # pid -> (start time, program name): every process seen in our tree
        self.ports = []
        self.url = None
        self.args = None    # the command line of the latest try
        self._others = {}   # port -> ids of processes NOT ours found listening there (a try given up on): never "left"

    def _wrangler(self):
        node = shutil.which("node")
        if not node:
            raise RelayError("the relay tests need Node — it isn't on the PATH")
        if not os.path.exists(WRANGLER):
            raise RelayError("the relay tests need wrangler — not found in relay/node_modules.\n"
                             "  Set it up once:  cd relay  then  npm ci")
        return [node, WRANGLER] + WRANGLER_ARGS

    def log(self):
        try:
            with open(self.log_path, encoding="utf-8", errors="replace") as f:
                return ANSI.sub("", f.read())
        except (OSError, AttributeError):
            return ""

    def _note_tree(self):
        """Add every process now running under ours (by parent id; a child must have started after its parent, so a
        reused id is never adopted)."""
        procs = processes()
        todo = list(self.ours)
        while todo:
            parent = todo.pop()
            for pid, (ppid, name) in procs.items():
                if ppid == parent and pid not in self.ours:
                    t, pt = started_at(pid), self.ours[parent][0]
                    if t is not None and not (isinstance(t, int) and isinstance(pt, int) and t < pt):
                        self.ours[pid] = (t, name)
                        todo.append(pid)

    def start(self):
        """Start it; its address once it is PROVEN ready — its own ready line names our port and everything listening
        there is ours. A try that stopped before it was ready is followed by one on new ports; anything else that isn't
        proven ends it. RelayError, loud — with the end of its output — when no try works."""
        cmd = self.command or self._wrangler()
        tried = []
        for _ in range(max(1, self.attempts)):
            why, last_try = self._try(cmd)
            if why is None:
                return self.url
            tail = self.log()[-1500:].strip()
            left = self.stop()
            tried.append(why)
            if last_try or left or len(tried) == max(1, self.attempts):
                said = why if len(tried) == 1 else (f"couldn't start in {len(tried)} tries: "
                                                    + "; ".join(f"{i}) {w}" for i, w in enumerate(tried, 1)))
                raise RelayError(f"the local relay {said}." + (f"\n  Its output ended:\n{_indent(tail)}" if tail else "")
                                 + ("\n  " + "\n  ".join(left) if left else ""))

    def _try(self, cmd):
        """One try, on new ports: (None, _) when ready and proven ours — else (why, no_more_tries)."""
        self.port, inspector = free_port(), free_port()
        self.ports = [self.port, inspector]
        self.store = tempfile.mkdtemp(prefix="rw-test-relay-")
        self.log_path = os.path.join(self.store, "relay.log")
        self.args = [a.format(port=self.port, inspector_port=inspector, store=os.path.join(self.store, "state"))
                     for a in cmd] + self.extra_args
        with open(self.log_path, "w", encoding="utf-8") as log:
            self.proc = subprocess.Popen(self.args, cwd=self.cwd, stdout=log, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, start_new_session=(os.name != "nt"))
        self.ours = {self.proc.pid: (started_at(self.proc.pid), os.path.basename(self.args[0]))}
        self.url = f"http://127.0.0.1:{self.port}"
        deadline = time.monotonic() + self.start_s
        said_ready = False
        try:
            while True:
                m = READY.search(self.log())
                if m:
                    said_ready = True
                    self._note_tree()
                    if int(m.group(1)) != self.port:
                        return f"said it was ready on port {m.group(1)}, not on its own port {self.port}", True
                    taken = self._taken([self.port])
                    if taken:
                        return taken
                    if port_owners(self.port) or os.name != "nt":   # Windows: ours listen there (and only ours)
                        return None, False
                if self.proc.poll() is not None:
                    why = f"stopped before it was ready (exit code {self.proc.returncode})"
                    taken = self._taken(self.ports)
                    return (f"{why} — {taken[0]}", taken[1]) if taken else (why, False)
                if time.monotonic() > deadline:
                    return ((f"said it was ready, but nothing listened on its port {self.port} within {self.start_s} s"
                             if said_ready else f"didn't say it was ready within {self.start_s} s"), True)
                time.sleep(0.2)
        except BaseException:          # Ctrl+C while waiting: still stop what we started
            self.stop()
            raise

    def _taken(self, ports):
        """Other processes listening on these ports of ours, judged (see the top) — None when there are none; else
        (why, no_more_tries). One that started BEFORE our relay is proven not ours: left alone (and never counted as
        left by stop()), and a new try may follow. Any other can't be told from an escaped child of ours: the end."""
        root_t = self.ours.get(self.proc.pid, (None, ""))[0]
        older, unproven = {}, {}
        for p in ports:
            for o in port_owners(p) - set(self.ours):
                t = started_at(o)
                proven = isinstance(t, int) and isinstance(root_t, int) and t < root_t
                (older if proven else unproven).setdefault(p, set()).add(o)
        for p, o in list(older.items()) + list(unproven.items()):
            self._others.setdefault(p, set()).update(o)     # not ours to stop, and not "left" by this run
        if unproven:
            return (f"wasn't alone on its port{'s' if len(unproven) > 1 else ''} "
                    + "; ".join(f"{p}: {_who(o)}" for p, o in sorted(unproven.items()))
                    + " listened there too — not a process it can show it started (another run's relay or server that "
                    "took the port in between, or one of its own that escaped its tree), so it was left running. If "
                    "it's a leftover, stop it by its id: "
                    + "  ".join(f"taskkill /PID {o} /F" for ids in unproven.values() for o in sorted(ids))), True
        if older:
            return ("found its port taken by a process older than itself (so not one of its own; left alone) — "
                    + "; ".join(f"{p}: {_who(o)}" for p, o in sorted(older.items()))), False
        return None

    def stop(self):
        """Stop everything we started, then check. Returns what's left, in words ([] = all gone, ports free)."""
        if self.proc is None:
            return []
        if self.proc.poll() is None:
            self._note_tree()
        # Every process proven ours (its start time checked as it was adopted, and again now), each by its exact id —
        # the children first, then the one we started, so nothing is left to start new ones
        root = self.proc.pid
        for pid, (t, _) in [(p, v) for p, v in self.ours.items() if p != root] + [(root, self.ours.get(root, (None, '')))]:
            if pid == root or (t is not None and started_at(pid) == t):
                stop_one(pid)
        try:
            self.proc.wait(self.stop_s)
        except subprocess.TimeoutExpired:
            pass
        deadline = time.monotonic() + self.stop_s
        while True:
            alive = {pid: name for pid, (t, name) in self.ours.items() if t is not None and started_at(pid) == t}
            # (a process that isn't ours, found on a port when a try was given up on, was there before — not "left")
            ports = {p: listening(p) - self._others.get(p, set()) for p in self.ports}
            ports = {p: o for p, o in ports.items() if o}
            if (not alive and not ports) or time.monotonic() > deadline:
                break
            time.sleep(0.2)
        names = processes()
        left = [f"still running after the stop: process {pid} ({name})" for pid, name in sorted(alive.items())]
        for p, owners in sorted(ports.items()):
            who = ", ".join("an unknown process" if o == 0 else f"process {o} ({names.get(o, (0, '?'))[1]})"
                            for o in sorted(owners))
            ids = [o for o in sorted(owners) if o and o not in alive]
            left.append(f"port {p} is still in use by {who}" + (
                " — not one the runner can show it started, so it was left running. Stop it by its id: "
                + "  ".join(f"taskkill /PID {o} /F" for o in ids) if ids else ""))
        self.proc = None
        shutil.rmtree(self.store, ignore_errors=True)
        return left


def _indent(text):
    return "\n".join("    " + ln for ln in text.splitlines())


def _who(pids):
    names = processes()
    return ", ".join(f"process {p} ({names.get(p, (0, '?'))[1]})" for p in sorted(pids))
