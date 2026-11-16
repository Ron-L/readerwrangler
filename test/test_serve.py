# Tests for serve.py — the local server's rebuild on demand when the new copy can't be swapped in.
# tags: build, tooling, copies, tier 1
# covers: serve.py, tools/build.py
# Run: python test/test_serve.py
#
# 2026-11-16 (TODO "Faster sprints" item 3): serve.py rebuilds a stale dist/ copy when it's asked for. With screen tests in
# parallel (each with its own serve.py) and working copies, another server can be reading the old copy at that moment,
# and Windows refuses the swap (PermissionError). It wasn't caught in send_head: the request died and the page didn't
# load. Now (after build.py's own retries) the existing copy is served and the server's log says so.
import http.client
import importlib.util
import os
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

done()
