"""
environment_trouble.py — telling the MACHINE's or the BROWSER's trouble from a TEST failure (TODO tooling item 9;
2026-11-17). One place for what both sides read: the screen-test harness (test/ui/harness.py, test/ui/rw.py) says so,
and the runner (tools/run_tests.py) acts on it.

Five one-time screen-test failures in one week (2026-11-09…15) each passed when rerun, all while the PC was busy — a page
that never loaded, a network error from the browser to our own server (net::ERR_NO_BUFFER_SPACE). An ENVIRONMENT failure
is recognized where it happens — by the screen-test driver, which knows: the page never loaded (and the page reported no
error of its own), the browser crashed or closed, our own web server or relay didn't come up, a network error on the way
to our own server — never by guessing at a file's output afterwards. The file then exits with EXIT_CODE, which an
assertion never gives (the harness's done() exits 0 or 1, an uncaught error 1), and prints a line starting with MARK and
the reason. The runner reruns such a file once, alone; a test failure is never rerun (TESTING.md §7).

Who can say so (2026-11-17): a screen test (through rw.py and harness.py) and a HEAVY tier-1 file (its header says
`heavy: yes` — tools/run_tests.py), which knows its own machine trouble: test/test_run_tests.py's stand-in relay not
ready within its time. Both decide their exit code by exit_code() below — one rule.

A library the page loads from its host (React from unpkg.com, the QR-code maker from cdnjs, the fonts' stylesheet from
Google Fonts) that failed to DOWNLOAD is the network's — or the host's — trouble too (2026-11-17: a lab run's start-up
failed on "ReactDOM is not defined"): library_download_failed() and library_failure_in_console() judge a request,
library_not_defined() a start-up whose only errors are a library's missing name. One that downloaded and then threw is
never the network's.

Tested by test/test_run_tests.py (RUN-080, 082, 090, 091, 093) and test/ui/test_environment.py (ENV-001–007).
"""
import re

EXIT_CODE = 3
MARK = "ENVIRONMENT FAILURE:"

# The browser's words for a request the machine couldn't carry: short of network buffers (Windows, 2026-11-15: 659
# connections waiting to close) or of memory. On the way to our web server OR our local relay, these are never the code's.
MACHINE_ERRORS = ("ERR_NO_BUFFER_SPACE", "ERR_INSUFFICIENT_RESOURCES", "ERR_OUT_OF_MEMORY")
# A connection that failed. Our web server (serve.py) only serves files, so on the way to IT these are the machine's (or
# our tooling's) trouble; on the way to the relay they may be the relay code under test — so never counted there.
CONNECTION_ERRORS = ("ERR_CONNECTION_REFUSED", "ERR_CONNECTION_RESET", "ERR_CONNECTION_ABORTED", "ERR_CONNECTION_CLOSED",
                     "ERR_CONNECTION_FAILED", "ERR_CONNECTION_TIMED_OUT", "ERR_TIMED_OUT", "ERR_EMPTY_RESPONSE",
                     "ERR_SOCKET_NOT_CONNECTED", "ERR_ADDRESS_UNREACHABLE")


def host_of(url):
    """'localhost:8123' from 'http://localhost:8123/x?y' — '' if it has no host."""
    return url.split("/")[2].lower() if "://" in url else ""


def net_error(error, url, app_hosts=(), relay_hosts=()):
    """The error's name (e.g. 'ERR_NO_BUFFER_SPACE') when a browser request to one of OUR OWN servers failed for the
    machine's reasons — else None. error: the browser's words ('net::ERR_…'); url: the request's address; app_hosts /
    relay_hosts: 'host:port' of our web server and our local relay. A request a test refuses on purpose (route.abort →
    ERR_FAILED), one a page change cut short (ERR_ABORTED), and one to anywhere else are never the machine's."""
    name = (error or "").strip().split()[0] if (error or "").strip() else ""
    name = name[len("net::"):] if name.startswith("net::") else name
    host = host_of(url or "")
    if name in MACHINE_ERRORS and host in {h.lower() for h in list(app_hosts) + list(relay_hosts)}:
        return name
    if name in CONNECTION_ERRORS and host in {h.lower() for h in app_hosts}:
        return name
    return None


def reason(code, out):
    """The reason a screen test gave for an environment failure — only when it exited with EXIT_CODE AND printed a line
    starting with MARK (both: neither a stray exit code nor a printed word alone makes one). Else None."""
    if code != EXIT_CODE:
        return None
    for ln in (out or "").splitlines():
        if ln.startswith(MARK):
            return ln[len(MARK):].strip() or "no reason given"
    return None


def exit_code(events, stopped=0):
    """A test file's exit code from what happened, in order — events: [("fail", what) | ("env", reason)]; stopped: how
    many tests the machine's trouble stopped. 0 when nothing failed and nothing was stopped (trouble that failed nothing
    is only noted); EXIT_CODE when the machine's trouble came before any failure; 1 when a failure came first (it failed
    while the machine was fine). The one rule — test/ui/harness.py and test/test_run_tests.py both use it."""
    kinds = [k for k, _ in events]
    if "fail" not in kinds and not stopped:
        return 0
    if "env" in kinds and ("fail" not in kinds or kinds.index("env") < kinds.index("fail")):
        return EXIT_CODE
    return 1


def mark_line(events):
    """The line the runner reads: MARK and the FIRST trouble's reason."""
    return f"{MARK} {next((r for k, r in events if k == 'env'), 'no reason given')}"


def tally(results, events, trouble="the machine's trouble"):
    """(a test file's last lines, its exit code) from its rows — results: [(id, name, ok, detail)], ok None for a check the
    machine's trouble stopped (neither passed nor failed); events: as exit_code's. The summary line ("N passed, M failed,
    K stopped by <trouble>"), then the marked line when the exit is EXIT_CODE. How test/test_run_tests.py — a heavy
    tier-1 file with its own row helper — ends; RUN-093 runs a stand-in that ends the same way through the runner, the
    whole path (TODO tooling 11.2)."""
    failed = sum(1 for r in results if r[2] is False)
    held = sum(1 for r in results if r[2] is None)
    lines = [f"{len(results) - failed - held} passed, {failed} failed" + (f", {held} stopped by {trouble}" if held else "")]
    code = exit_code(events, stopped=held)
    return lines + ([mark_line(events)] if code == EXIT_CODE else []), code


# --- a library the page loads, lost on the way (2026-11-17) -----------------------------------------------------------
# The hosts the app's pages load scripts and stylesheets from (readerwrangler.html, reset.html — RUN-091 checks every
# such host of theirs is here), and each library's global — the name the page uses once its script ran — with a piece of
# its script's address. GoatCounter's script isn't here: the screen-test driver answers it itself.
LIBRARY_HOSTS = ("unpkg.com", "cdnjs.cloudflare.com", "cdn.jsdelivr.net", "fonts.googleapis.com")
LIBRARY_GLOBALS = {"React": "/react@", "ReactDOM": "/react-dom@", "QRCode": "/qrcodejs/"}
# The browser's words for a request that was NOT lost by the network: cut short by a page change, refused by a test on
# purpose (route.abort), or blocked by the browser itself.
NOT_THE_NETWORK = ("ERR_ABORTED", "ERR_FAILED", "ERR_BLOCKED_BY_CLIENT")


def is_library(url):
    """Is this an address on one of the library hosts?"""
    host = host_of(url or "")
    return any(host == h or host.endswith("." + h) for h in LIBRARY_HOSTS)


def library_download_failed(url, kind, failure=None, status=None, body_size=None):
    """Why a script or stylesheet from a library host didn't download — in words — else None. kind: the browser's
    resource type ('script', 'stylesheet'); failure: its words for a failed request ('net::ERR_…'); status: the answer's
    status; body_size: the answer's size in bytes. Lost: the request failed (anything but NOT_THE_NETWORK), the host
    answered 5xx, or answered 2xx with NOTHING in it — the only loss that reproduced the 2026-11-17 lab's "ReactDOM is not
    defined" with no failed request in the console. Never: a 4xx (a wrong address is ours), a redirect, an image or a
    font, a request to any other host (our own server's: net_error)."""
    if kind not in ("script", "stylesheet") or not is_library(url):
        return None
    where = (url or "").split("?")[0]
    if status is not None and 500 <= status <= 599:
        return f"{where} answered {status}"
    name = (failure or "").strip().split()[0] if (failure or "").strip() else ""
    name = name[len("net::"):] if name.startswith("net::") else name
    if name and name not in NOT_THE_NETWORK:
        return f"{where}: {name}"
    if status is not None and 200 <= status <= 299 and body_size == 0:
        return f"{where} answered with nothing"
    return None


def library_failure_in_console(text, url):
    """The same, from the console's words for it ("Failed to load resource: net::ERR_…" / "…a status of 503 (…)") with
    the address the browser gives — the console can't say what kind of resource it was, so any from a library host."""
    if not is_library(url) or not (text or "").startswith("Failed to load resource"):
        return None
    m = re.search(r"net::(ERR_[A-Z_]+)", text) or re.search(r"status of (5\d\d)\b", text)
    if not m or m.group(1) in NOT_THE_NETWORK:
        return None
    return f"{(url or '').split('?')[0]}: {m.group(1)}"


def library_not_defined(errors, lost_urls):
    """The library names behind a start-up's errors when EVERY one of them is "<Name> is not defined" for a library whose
    script didn't download (its address among lost_urls) — else None: an error of the page's own (one that downloaded
    and then threw, say) is the app's to answer for."""
    names = []
    for e in errors or []:
        m = re.search(r"\b([A-Za-z_$][\w$]*) is not defined\b", e)
        part = LIBRARY_GLOBALS.get(m.group(1)) if m else None
        if not part or not any(part in (u or "") for u in lost_urls or []):
            return None
        names.append(m.group(1))
    return sorted(set(names)) or None
