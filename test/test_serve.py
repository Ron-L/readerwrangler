# Tests for serve.py — the local server's rebuild on demand when the new copy can't be swapped in.
# tags: build, tooling, copies, tier 1
# covers: serve.py, tools/build.py, tools/setup_check.py
# Run: python test/test_serve.py
#
# 2026-11-16 (TODO "Faster sprints" item 3): serve.py rebuilds a stale dist/ copy when it's asked for. With screen tests in
# parallel (each with its own serve.py) and working copies, another server can be reading the old copy at that moment,
# and Windows refuses the swap (PermissionError). It wasn't caught in send_head: the request died and the page didn't
# load. Now (after build.py's own retries) the existing copy is served and the server's log says so.
# Sprint 9 (2026-11-18): + the commit-checks warning at start-up and `--open` (SERVE-002–007).
import contextlib
import http.client
import http.server
import importlib.util
import io
import os
import socket
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402

SERVE = os.path.join(ROOT, "serve.py")


def load_serve():
    spec = importlib.util.spec_from_file_location("rw_serve", SERVE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def listening(port):
    try:
        socket.create_connection(("127.0.0.1", port), 0.5).close()
        return True
    except OSError:
        return False


def get(port, path):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    try:
        c.request("GET", path)
        r = c.getresponse()
        return r.status, r.read()
    except (OSError, http.client.HTTPException) as e:   # the request died — what happened before the fix
        return None, repr(e).encode()
    finally:
        c.close()


def busy_rebuild_serves_the_old_copy():
    serve = load_serve()
    log = []

    def refused(*_a, **_k):
        raise PermissionError(13, "The process cannot access the file because it is being used by another process")
    serve.build.build_if_stale = refused        # this module's own copy of build.py — nothing else sees the stand-ins
    serve.build.styles_if_stale = refused
    serve.Handler.log_message = lambda self, fmt, *a: log.append(fmt % a)
    server = serve.Server(("127.0.0.1", 0), serve.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        port = server.server_address[1]
        for rel in ("dist/readerwrangler.js", "dist/tailwind.css"):
            status, body = get(port, "/" + rel)
            with open(os.path.join(ROOT, rel), "rb") as f:
                check(status == 200 and body == f.read(), f"{rel}: the existing copy is served (got {status}, "
                                                          f"{body[:120]!r})")
            check(any("REBUILD NOT SWAPPED IN " + rel in ln for ln in log), f"and the log says so: {log}")
    finally:
        server.shutdown()
        server.server_close()
test("SERVE-001", "a rebuild Windows won't swap in (another server is reading the copy): the existing copy is served, "
     "and logged", busy_rebuild_serves_the_old_copy)


# Sprint 9 (TODO "Working-process safety net" item 1, and "The 'open' shortcut"): serve.py warns loudly, first thing,
# when this copy isn't set up for the commit checks; `serve.py --open` (what tools/shortcuts.py's shortcut runs) opens the
# page — starting the server first only if it isn't running. No browser is ever opened here: the opener is a stand-in.
class Opened(list):
    def __call__(self, url):
        self.append(url)
        return True


class NotOurs(http.server.BaseHTTPRequestHandler):
    """Another program on the port: answers, but not with the app."""
    def do_HEAD(self):
        self.send_response(404)
        self.end_headers()

    def log_message(self, *a):
        pass


def run_main(serve, argv):
    """serve.main(argv) with its printed lines captured; (exit code or SystemExit message, lines)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = serve.main(argv)
        except SystemExit as e:
            code = e.code
    return code, buf.getvalue().splitlines()


def a_server(server_class, handler):
    """A server on a free port, serving in a thread."""
    server = server_class(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def stop(server):
    server.shutdown()
    server.server_close()


def warns_first():
    serve = load_serve()
    serve.setup_check.hooks_path_problem = lambda root: "core.hooksPath isn't set"
    serve.webbrowser_open = Opened()
    server = a_server(serve.Server, serve.Handler)
    try:
        code, lines = run_main(serve, [str(server.server_address[1]), "--open"])
    finally:
        stop(server)
    check(code in (0, None), f"started fine ({code})")
    check(lines and set(lines[0]) == {"!"}, f"the first thing printed is the warning's frame: {lines[:3]}")
    text = "\n".join(lines)
    check("git config core.hooksPath git-hooks" in text and "OFF" in text, f"with the fix command:\n{text}")
    serve.setup_check.hooks_path_problem = lambda root: None
    server = a_server(serve.Server, serve.Handler)
    try:
        _code, lines = run_main(serve, [str(server.server_address[1]), "--open"])
    finally:
        stop(server)
    check(not any("!!!" in ln for ln in lines), f"set up: no warning ({lines})")
test("SERVE-002", "serve.py warns first thing, framed in '!', when this copy isn't set up for the commit checks — with "
     "the fix; set up: no warning", warns_first)


def whats_there():
    serve = load_serve()
    server = a_server(serve.Server, serve.Handler)
    try:
        check(serve.whats_on_port(server.server_address[1]) == "app", "our serve.py answers with the app's page: 'app'")
    finally:
        stop(server)
    other = a_server(http.server.ThreadingHTTPServer, NotOurs)
    try:
        check(serve.whats_on_port(other.server_address[1]) == "other", "another program on the port: 'other'")
    finally:
        stop(other)
    check(serve.whats_on_port(free_port()) is None, "nothing on the port: None")
test("SERVE-003", "whats_on_port: our server ('app'), another program ('other'), or nothing (None)", whats_there)


def open_when_running():
    serve = load_serve()
    serve.setup_check.hooks_path_problem = lambda root: None
    opened = serve.webbrowser_open = Opened()
    server = a_server(serve.Server, serve.Handler)
    started = []
    real = serve.Server
    serve.Server = lambda *a, **k: started.append(a) or real(*a, **k)
    port = server.server_address[1]
    try:
        code, lines = run_main(serve, [str(port), "--open"])
    finally:
        stop(server)
    check(code in (0, None), f"exits fine ({code}): the running server is left as it is")
    check(opened == [f"http://localhost:{port}/readerwrangler.html"], f"the page is opened once: {opened}")
    check(started == [], f"no second server is started: {started}")
    check(any("already running" in ln for ln in lines), f"and it says so: {lines}")
test("SERVE-004", "serve.py --open with the server already running: opens the page, starts nothing", open_when_running)


def open_starts_first():
    serve = load_serve()
    serve.setup_check.hooks_path_problem = lambda root: None
    port = free_port()
    seen = []
    serve.webbrowser_open = lambda url: seen.append((url, listening(port))) or True   # listening yet when opened?
    with contextlib.redirect_stdout(io.StringIO()):
        server = serve.start(port, open_page=True)
    try:
        check(seen == [(f"http://localhost:{port}/readerwrangler.html", True)],
              f"the page was opened once the server was listening: {seen}")
        threading.Thread(target=server.serve_forever, daemon=True).start()
        status, _body = get(port, "/readerwrangler.html")
        check(status == 200, f"and the server serves it ({status})")
    finally:
        stop(server)
    with contextlib.redirect_stdout(io.StringIO()):
        server = serve.start(free_port(), open_page=False)
    server.server_close()
    check(len(seen) == 1, "without --open, no page is opened")
test("SERVE-005", "serve.py --open with nothing running: starts the server, then opens the page (without --open: no "
     "page)", open_starts_first)


def open_when_port_taken():
    serve = load_serve()
    serve.setup_check.hooks_path_problem = lambda root: None
    opened = serve.webbrowser_open = Opened()
    other = a_server(http.server.ThreadingHTTPServer, NotOurs)
    port = other.server_address[1]
    try:
        code, _lines = run_main(serve, [str(port), "--open"])
    finally:
        stop(other)
    check(isinstance(code, str) and str(port) in code and "another program" in code,
          f"says another program has the port, naming it: {code!r}")
    check(opened == [], f"and opens nothing: {opened}")
test("SERVE-006", "serve.py --open when another program has the port: says so (naming the port), opens nothing",
     open_when_port_taken)


def arguments():
    serve = load_serve()
    check(serve.parse_args([]) == (8000, False), "no arguments: port 8000, no page")
    check(serve.parse_args(["8123"]) == (8123, False), "a port")
    check(serve.parse_args(["--open"]) == (8000, True) and serve.parse_args(["8123", "--open"]) == (8123, True),
          "--open, with or without a port")
test("SERVE-007", "serve.py's arguments: [port] [--open]", arguments)

done()
