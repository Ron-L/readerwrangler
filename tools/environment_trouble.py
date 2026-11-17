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

Tested by test/test_run_tests.py (RUN-080, 082) and test/ui/test_environment.py (ENV-001–004).
"""
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
