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
(test/ui/rw.py App(relay=True), which adds `--var ALLOWED_ORIGINS:<its page's address>` through extra_args). Since
2026-11-18 (sprint 9) it starts and stops through tools/starter.py — the one starter for every process our tools start:
every process of the relay is on the starter's list (its id, start time, what it is, which run) from the moment it's
known until it's confirmed gone, and a crashed run's relay is named loudly at the next run's start. The process code
(the process list, start times, stopping by exact id, who listens on a port) moved there too; it is still reachable here
by its old names.

measure=True (the runner's tier 3 with a record, 2026-11-18 — TODO tooling 13.3): the relay runs in a Windows job of its
own (tools/test_costs.py), so what it cost — CPU, memory, I/O, processes — is measured like any test unit's (.measures,
.seconds after stop()); the runner records it and teaches this PC's averages with it.

"Ready" is proven against OUR process, not taken from whoever answers: the free port is chosen, then taken by wrangler a
moment later, and with tests in parallel another run's relay can take it in between (wrangler on a taken port dies:
"The Workers runtime failed to start", seen 2026-11-16 — while it starts, the port answers with the OTHER relay). So it
is ready only when wrangler's own ready line names our port AND everything listening there is a process we started
(Windows: by id). Another process on one of its ports — when it's ready, or when it stopped before it was ready (what a
taken port does to wrangler) — is judged as stopping is (Law 5: only what's PROVEN):
  - started BEFORE our relay → proven not ours (no process starts before its parent): left alone, and the relay is
    started again on new ports (3 tries in all; a wrangler that just stopped early is tried again too);
  - started after → it may be one of ours that escaped the tree, and each new try would leave another: fails loud,
    named by id, left running — never retried (and kept on the starter's list as unnamed, for the next run's banner).


Stopping (PRINCIPLES Law 5, Law 12 — 7.28.0: ending the shell that started a relay left workerd and three node
processes serving its port, caught only by checking the port): tools/starter.py Started.stop — every process it started,
each by its exact id (its start time checked; never `/T`, never by name or pattern), then CHECKED: each one gone, each
port no longer listening. Anything left is reported by id and name; a process we can't show we started isn't ours to stop.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import starter      # noqa: E402 — tools/starter.py: the one starter, its list, and the process code
# The process code's old names, kept: the runner's tests and others read them here (and patch free_port here).
from starter import free_port, listening, port_owners, processes, started_at, stop_one   # noqa: E402,F401

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
WHAT = "the local relay for the relay tests (tier 3)"


class RelayError(RuntimeError):
    pass


# --- the relay -------------------------------------------------------------------------------------------------------
class LocalRelay:
    """command: the program and its arguments ({port}, {inspector_port}, {store} filled in) — None = wrangler.
    The tests give a stand-in here (test/test_run_tests.py). extra_args: added after them, as given (the screen tests'
    `--var ALLOWED_ORIGINS:<address>`). what: what it is, in words, on the starter's list (None = the relay tests'
    relay). run: which run started it (None = the starter's run_label()). measure: run it in a job of its own and
    measure it (above)."""

    def __init__(self, command=None, cwd=RELAY_DIR, start_s=START_S, stop_s=STOP_S, extra_args=(), attempts=ATTEMPTS,
                 what=None, run=None, measure=False):
        self.command, self.cwd, self.start_s, self.stop_s = command, cwd, start_s, stop_s
        self.extra_args, self.attempts = list(extra_args), attempts
        self.what, self.run, self.measure = what or WHAT, run, measure
        self.started = None     # the latest try's starter.Started
        self.ports = []
        self.url = None
        self.args = None    # the command line of the latest try
        self._others = {}   # port -> ids of processes NOT ours found listening there (a try given up on): never "left"
        self._job, self._t0 = None, None
        self.measures, self.seconds = None, None    # what it cost, once stopped (measure=True)

    @property
    def proc(self):
        return self.started.proc if self.started else None

    @property
    def ours(self):
        """pid -> (start time, program name): every process seen in the latest try's tree (kept after the stop)."""
        return self.started.ours if self.started else {}

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
        self.started.note_tree()

    def start(self):
        """Start it; its address once it is PROVEN ready — its own ready line names our port and everything listening
        there is ours. A try that stopped before it was ready is followed by one on new ports; anything else that isn't
        proven ends it. RelayError, loud — with the end of its output — when no try works."""
        cmd = self.command or self._wrangler()
        self._t0 = time.monotonic()
        if self.measure and self._job is None:
            import test_costs
            ok, _ = test_costs.available()
            if ok:
                try:
                    self._job = test_costs._Job()
                    self._job.start_sampling()
                except Exception:   # noqa: BLE001 — measuring never stops the relay from starting
                    self._job = None
        tried = []
        for _ in range(max(1, self.attempts)):
            why, last_try = self._try(cmd)
            if why is None:
                return self.url
            tail = self.log()[-1500:].strip()
            left = self._stop_try()
            tried.append(why)
            if last_try or left or len(tried) == max(1, self.attempts):
                self._finish_job()
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
        self.started = starter.Started(self.what, ports=self.ports, run=self.run)
        with open(self.log_path, "w", encoding="utf-8") as log:
            self.started.start(self.args, job=self._job, cwd=self.cwd, stdout=log, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, start_new_session=(os.name != "nt"))
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
            names = processes()
            self.started.ledger.add_unnamed([      # for the next run's start banner too
                {"pid": o, "start": started_at(o), "name": names.get(o, (0, "?"))[1], "port": p, "of": self.what,
                 "run": self.started.run} for p, ids in unproven.items() for o in ids if started_at(o) is not None])
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

    def _stop_try(self):
        """Stop the latest try — everything it started — then check (starter.Started.stop); its store deleted."""
        if self.started is None or self.started.proc is None:
            return []
        left = self.started.stop(self.stop_s, ports=self.ports, not_ours=self._others)
        shutil.rmtree(self.store, ignore_errors=True)
        return left

    def _finish_job(self):
        """measure=True: what the relay cost, all its tries together — read from its job, which is then closed."""
        if self._t0 is not None and self.seconds is None:
            self.seconds = round(time.monotonic() - self._t0, 1)
        if self._job is not None:
            self.measures = self._job.finish()
            self._job = None

    def stop(self):
        """Stop everything we started, then check. Returns what's left, in words ([] = all gone, ports free). Measured:
        .measures and .seconds are set."""
        left = self._stop_try()
        self._finish_job()
        return left


def _indent(text):
    return "\n".join("    " + ln for ln in text.splitlines())


def _who(pids):
    names = processes()
    return ", ".join(f"process {p} ({names.get(p, (0, '?'))[1]})" for p in sorted(pids))
