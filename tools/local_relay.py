"""
local_relay.py — a local relay for the relay tests (tier 3) and the screen tests that use one: relay-worker.js in
Cloudflare's own emulator on this PC (`wrangler dev --env dev --local`), on a free port, with an empty store made for the
run and deleted after. Never the dev or production relay: the address is always http://127.0.0.1:<the port it chose>.

    relay = LocalRelay()                  # extra_args=[…] are added after wrangler's own (the screen tests' ALLOWED_ORIGINS)
    url = relay.start()                   # waits until it's PROVEN ready; RelayError (with the end of its output) if not
    ...                                   # run the tests against url
    left = relay.stop()                   # [] when everything it started is gone AND its ports are free — else what's left
    relay.measures, relay.seconds         # what it cost (tools/job.py), once stopped

It runs in a job of its own (tools/job.py): everything it starts is in the job, the stop ends them all by the job's handle,
and if the process that started it dies, Windows ends them too (kill-on-close).

"Ready" is proven against its OWN processes: the free port is chosen, then taken by wrangler a moment later, and another
run's relay or server can take it in between (wrangler on a taken port stops: "The Workers runtime failed to start"). So
it is ready only when wrangler's ready line names our port AND everything listening there is in its job. Anything else
on one of its ports is not ours — left alone — and the relay is started again on new ports (ATTEMPTS tries in all).

Also here, for the screen tests' web server (test/ui/rw.py): free_port(), port_owners(), listening() and
stop_and_check(job, ports) — end a job and check its ports are free.
"""
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import job          # noqa: E402 — tools/job.py: a job of its own, ended with it

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
START_S = 60    # wrangler is ready in ~2 s on Ron's PC
STOP_S = 10
ATTEMPTS = 3    # tries, each on new ports, when its port turns out taken


class RelayError(RuntimeError):
    pass


# --- ports -------------------------------------------------------------------------------------------------------------
def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def port_owners(port):
    """Ids of the processes listening on this port (Windows: netstat; 'listening' read from the 0.0.0.0:0 / [::]:0 remote
    address, not the state word, which Windows translates). Elsewhere: none named."""
    if os.name != "nt":
        return set()
    out = ""
    for proto in ("TCP", "TCPv6"):
        out += subprocess.run(["netstat", "-ano", "-p", proto], capture_output=True, text=True, errors="replace").stdout
    owners = set()
    for ln in out.splitlines():
        parts = ln.split()
        if (len(parts) == 5 and parts[0].upper().startswith("TCP") and parts[1].rsplit(":", 1)[-1] == str(port)
                and parts[2] in ("0.0.0.0:0", "[::]:0") and parts[4].isdigit()):
            owners.add(int(parts[4]))
    return owners


def listening(port):
    """Ids of what listens on the port — {0} when something answers but its owner can't be named (not Windows)."""
    owners = port_owners(port)
    if not owners and os.name != "nt":
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                owners = {0}
    return owners


def stop_and_check(j, ports, what, wait_s=STOP_S, not_ours=None):
    """End every process in the job `j` (by its handle), then check each port is free. not_ours: {port: ids} found there
    and not ours (never counted as left). What's left, in words ([] = all gone, ports free)."""
    left = [f"still running after the stop: process {pid} — {what}" for pid in j.end(wait_s)]
    deadline = time.monotonic() + wait_s
    while True:
        busy = {p: o for p in ports if (o := listening(p) - (not_ours or {}).get(p, set()))}
        if not busy or time.monotonic() > deadline:
            break
        time.sleep(0.2)
    for p, owners in sorted(busy.items()):
        left.append(f"port {p} is still in use by " + ", ".join("an unknown process" if o == 0 else f"process {o}"
                                                               for o in sorted(owners)) + f" — {what}")
    return left


# --- the relay ---------------------------------------------------------------------------------------------------------
class LocalRelay:
    """command: the program and its arguments ({port}, {inspector_port}, {store} filled in) — None = wrangler. The tests
    give a stand-in here (test/test_run_tests.py). extra_args: added after them, as given."""

    def __init__(self, command=None, cwd=RELAY_DIR, start_s=START_S, stop_s=STOP_S, extra_args=(), attempts=ATTEMPTS):
        self.command, self.cwd, self.start_s, self.stop_s = command, cwd, start_s, stop_s
        self.extra_args, self.attempts = list(extra_args), attempts
        self.job, self.proc = None, None
        self.ours = set()       # every process id seen in its job (kept after the stop)
        self.ports, self.url, self.args = [], None, None
        self._others = {}       # port -> ids of processes NOT ours found listening there: never "left"
        self._t0 = None
        self.measures, self.seconds = None, None

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

    def _note(self):
        self.ours.update(self.job.running())
        return self.ours

    def start(self):
        """Start it; its address once it is PROVEN ready. A try whose port turns out taken is followed by one on new
        ports; anything else that isn't proven ends it. RelayError, loud — with the end of its output — when no try
        works."""
        cmd = self.command or self._wrangler()
        self._t0 = time.monotonic()
        self.job = job.new()
        tried = []
        for _ in range(max(1, self.attempts)):
            why, last_try = self._try(cmd)
            if why is None:
                return self.url
            tail = self.log()[-1500:].strip()
            left = self._stop_try()
            tried.append(why)
            if last_try or left or len(tried) == max(1, self.attempts):
                self._finish()
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
            self.proc, _ = self.job.launch(self.args, cwd=self.cwd, stdout=log, stderr=subprocess.STDOUT,
                                           stdin=subprocess.DEVNULL)
        self.url = f"http://127.0.0.1:{self.port}"
        deadline = time.monotonic() + self.start_s
        said_ready = False
        try:
            while True:
                m = READY.search(self.log())
                if m:
                    said_ready = True
                    self._note()
                    if int(m.group(1)) != self.port:
                        return f"said it was ready on port {m.group(1)}, not on its own port {self.port}", True
                    taken = self._taken([self.port])
                    if taken:
                        return taken, False
                    if port_owners(self.port) or os.name != "nt":   # Windows: ours listen there (and only ours)
                        return None, False
                if self.proc.poll() is not None:
                    why = f"stopped before it was ready (exit code {self.proc.returncode})"
                    taken = self._taken(self.ports)
                    return (f"{why} — {taken}" if taken else why), False
                if time.monotonic() > deadline:
                    return ((f"said it was ready, but nothing listened on its port {self.port} within {self.start_s} s"
                             if said_ready else f"didn't say it was ready within {self.start_s} s"), True)
                time.sleep(0.2)
        except BaseException:          # Ctrl+C while waiting: still stop what we started
            self.stop()
            raise

    def _taken(self, ports):
        """Processes listening on these ports that aren't in its job — not ours: left alone (and never counted as left by
        the stop). None when there are none; else why, in words (a new try on new ports may follow)."""
        ours = self._note()
        others = {p: o for p in ports if (o := port_owners(p) - ours)}
        for p, o in others.items():
            self._others.setdefault(p, set()).update(o)
        if not others:
            return None
        return ("found its port taken by a process it didn't start (left alone) — "
                + "; ".join(f"{p}: " + ", ".join(f"process {o}" for o in sorted(ids)) for p, ids in sorted(others.items())))

    def _stop_try(self):
        """Stop the latest try — everything in its job — then check its ports; its store deleted."""
        if self.job is None or self.proc is None:
            return []
        self._note()
        left = stop_and_check(self.job, self.ports, "the local relay", self.stop_s, self._others)
        self.proc = None
        shutil.rmtree(self.store, ignore_errors=True)
        return left

    def _finish(self):
        """What it cost, all its tries together — read from its job, which is then closed."""
        if self._t0 is not None and self.seconds is None:
            self.seconds = round(time.monotonic() - self._t0, 1)
        if self.job is not None:
            self.measures = self.job.finish()
            self.job = None

    def stop(self):
        """Stop everything it started, then check. Returns what's left, in words ([] = all gone, ports free); its
        .measures and .seconds are set."""
        left = self._stop_try()
        self._finish()
        return left


def _indent(text):
    return "\n".join("    " + ln for ln in text.splitlines())
