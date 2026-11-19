"""
test/ui/rw.py — the shared setup every screen test uses (docs/design/TESTING.md §2, §5, §7).

    with App() as app:                      # serve.py on a free port + a fresh, throwaway Chrome profile
        app.restore(FIXTURE)                # File → Restore Backup… through the real menu and file box
        app.reload(); app.wait_loaded()     # F5, then the library's load finished (folders set, or the critical box)
        app.wait_console(AFTER_CHECK, since=n0)   # the check after an Import / Restore has run (a condition, never a sleep)
        app.until(cond); app.heard(pattern, n0)   # the waits — one set, each under LIMIT_MS (also: caught_up, settled,
        app.toast(*words); app.amber_look(words)  #   held — the section "the waits" below; TESTING.md §4)
        app.left_count("All Books")         # the count the left pane shows for an entry
        app.unexpected_console()            # console errors / warnings / crashes not on the known-noise list
        app.violations                      # requests to a relay or to Amazon — the tests must make none
        app.shot("name")                    # a screenshot in the artifacts folder
        app.covered_scroll_boxes()          # scroll areas something else covers (the status bar)
        app.show_boxes(locator, "name")     # outline a box and every box around it, each in its own color (Law 19)
        app.stub_outside(page)              # window.open and the clipboard RECORDED, never a real mail program or web page
        app.open_broken_app()               # a tab whose app code is broken on purpose → the "Something went wrong" screen

    App(zoom=1.25, size=(1000, 900))        # a window of 1000 x 900 screen pixels at 125% browser zoom
    App(before_load=fn)                     # fn(context) before the first page loads — route or stub a request

    with App(relay=True) as app:            # the same, plus a LOCAL relay and a throwaway test channel (Cloud Sync on)
        app.upload_fetch(items)             # send books as the library fetcher does (one "books" run)
        app.import_from_relay()             # File → Import from Relay, through the real menu

Rules it enforces (TESTING.md §5, §7): a fresh browser profile every time (Playwright's default — nothing of Ron's);
serve.py started in a job of its own (tools/job.py) — at the end every process in it is stopped by the job's handle and
checked gone, its port free, anything left failing the file (Law 5); GoatCounter answered with an empty reply (tests
never touch the usage statistics); any request to a relay or to Amazon recorded as a violation; a data file carrying a
Cloud Sync Key refused. RW_HEADED=1 shows the browser (slowed down) for watching a test. Screenshots go to
RW_TEST_ARTIFACTS, else %TEMP%\\rw-test-artifacts — in a working copy (tools/copies.py) with "-<copy name>" added. The
browser is Chrome, the one Ron uses; RW_BROWSER=msedge runs Edge. Scrollbars are SHOWN: Playwright hides them in a
hidden browser by default, which hides exactly the bugs a person sees (the status bar covering the right pane's
scrollbar).

The local relay is Cloudflare's own emulator (`wrangler dev --local`) running relay-worker.js on this PC
with an empty store made for the run and deleted after — never the dev or production relay, which the request detector
still catches. It is the ONE relay launcher, tools/local_relay.py (Law 22): "ready" only when its own ready line names
its port and only processes in its job listen there (another run's relay can't answer for it); at the end every process
in its job is stopped and CHECKED gone, its ports free — anything left fails the file (Law 5).

The machine's or the browser's trouble is told from a test failure HERE, where it's known (tools/environment_trouble.py):
our web server or local relay didn't start, the browser didn't start, the page never loaded (the start screen still up
— with no error of the page's own; with one, it's a test failure naming it), the browser disconnected or a tab crashed,
a request to our own server failed for the machine's reasons (net::ERR_NO_BUFFER_SPACE, a refused connection…), and a
script or stylesheet the page loads from a
LIBRARY host (React from unpkg.com, the QR-code maker from cdnjs, the fonts from Google Fonts) that failed to download:
refused, cut, timed out, answered 5xx or with nothing; a start-up whose only errors are "<library> is not defined"
because its script never arrived is that trouble too — one whose library downloaded and then threw is not
(tools/environment_trouble.py). Each raises harness.EnvironmentTrouble or is noted with harness.environment(); the file
then exits 3 and the runner reruns it once, alone. The console check reports such a network error as that trouble,
never as a test failure. A failing test's screenshot is saved and named (on_failure).

Tabs: open_tab() opens a second tab IN FRONT, and Chrome slows the tabs behind it — under load a click on
the tab behind took 122-222 s (0.1 s in front). menu() and reload() bring the app's tab to the front first, as a person
switches to it; a test acting on another tab itself brings that one to the front (page.bring_to_front(); test_reset.py).
"""
import base64
import gzip
import json
import os
import re
import socket
import subprocess
import sys
import time

from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeout, sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_relay   # noqa: E402 — the local relay (LocalRelay); free ports, who listens on a port
import job           # noqa: E402 — tools/job.py: our web server in a job of its own
import copies       # noqa: E402 — tools/copies.py: a working copy keeps its screenshots apart
import environment_trouble   # noqa: E402 — tools/: which network errors are the machine's
import harness       # noqa: E402 — test/ui/harness.py: EnvironmentTrouble, environment(), on_failure()
FIXTURE = os.path.join(ROOT, "test", "fixtures", "small-fixture.json")
DEMO = os.path.join(ROOT, "readerwrangler-demo-library-ORGANIZED.json")
LARGE = os.path.join(ROOT, ".private", "test", "large-sample-private.json.gz")
# RW_TEST_ARTIFACTS, else %TEMP%\rw-test-artifacts — plus "-<copy name>" in a working copy (2026-11-16)
ARTIFACTS = copies.screenshots_folder(ROOT)

# Console messages that are expected today — each with its reason. Anything else fails a test. These three go away
# with "Faster loading: build the app ahead of time" (the in-browser compiler and style builder leave).
KNOWN_NOISE = [
    (r"cdn\.tailwindcss\.com should not be used in production", "the in-browser style builder — leaves with the precompile"),
    (r"You are using the in-browser Babel transformer", "the in-browser compiler — leaves with the precompile"),
    (r"\[BABEL\] Note: The code generator has deoptimised the styling",
     "Babel's note on a file over 500 KB — leaves with the precompile"),
    (r"goatcounter: not counting because of: localhost", "GoatCounter declining localhost"),
    (r"status of 404 \(Not Found\) \[http://127\.0\.0\.1:\d+/(pointer|status)/",
     "a new, empty channel has no saved copy or status yet — the relay answers 404 and the browser itself prints it "
     "(not our code; every new user sees it today)"),
]
# The status bar, found by its own words (the full-width box around "As an Amazon Associate…") — not by its classes, so
# a layout test reads the same before and after a change to how the bar is placed. Opens a JS function body; callers
# append their own code and the closing brace.
_STATUS_BAR_JS = """() => {
    const say = (e) => !e ? 'nothing' : e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
        (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\\s+/).slice(0, 3).join('.') : '');
    const statusBar = () => {
        const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = w.nextNode())) if (n.nodeValue.includes('As an Amazon Associate')) break;
        let e = n && n.parentElement;
        while (e && e.getBoundingClientRect().width < innerWidth - 40) e = e.parentElement;
        return e;
    };
"""
FORBIDDEN_HOSTS = re.compile(r"workers\.dev|amazon\.|media-amazon|ssl-images-amazon")
APP_TIMEOUT_MS = 180_000     # generous: the app opens in ~0.5 s since 7.27.0 (it took ~50 s while it compiled in the browser)
# The check that runs after every Import or Restore that loaded books, once the screen has settled (readerwrangler.js,
# integrityCheckPending) — its own debug line, so it needs extra detail on (the driver's default; log=None turns it off).
# Its last step: a repair it makes is logged right after it. Wait for it with wait_console(AFTER_CHECK, since=…).
AFTER_CHECK = r"^debug · INTEG · After-Import check sees "
# THE one limit for a step's wait — every screen test's (Law 22). Generous: a step answers in well under a second, 2–5×
# slower on a loaded PC, so only a real failure reaches it — and far under the runner's 10-minute limit for a whole file
# (TESTING.md §4), so a wait that runs out is reported as the test failure it is, naming the step. The app OPENING has
# its own, APP_TIMEOUT_MS. The waits that use it: the section "the waits" in App, below.
LIMIT_MS = 60_000
LIMIT_S = LIMIT_MS // 1000
BROWSER = os.environ.get("RW_BROWSER", "chrome")

# The local relay's test channel: made up, existing only in the run's throwaway store. Credentials are planted at run
# time, never in a data file (test data never carries a key).
TEST_CHANNEL = "44444444-5555-4666-8777-888888888888"
TEST_PASSPHRASE = "screen-test-passphrase"


class App:
    def __init__(self, headed=None, relay=False, zoom=1.0, size=(1400, 900), log=True, before_load=None):
        self.headed = os.environ.get("RW_HEADED") == "1" if headed is None else headed
        self.want_relay = relay
        self.relay = None
        self.before_load = before_load      # fn(context), before the first page loads (test_environment.py)
        self._closing = False               # our own close of the browser isn't the browser's trouble
        self._own_errors = {}               # page -> the errors that page reported of its own (pageerror, console)
        self._library_requests = []         # (page, request): every script / stylesheet asked of a library host
        self._off_failure = None
        # Browser zoom Z on a window of W x H screen pixels = a page of W/Z x H/Z CSS pixels, each drawn Z screen pixels
        # wide. (An emulation: the browser's own scrollbars scale with it, which real zoom doesn't do.)
        self.zoom, self.size = zoom, size
        self.console, self.crashes, self.violations = [], [], []
        # LOGGING.md §5 step 6 (switches since 5.1): every session runs with BOTH logging switches on — the banner and the
        # extra detail — set before the page's scripts, ONCE per browser profile (a test that turns one off keeps it off
        # across reloads), and its end fails the file on any error or critical message the test didn't declare with
        # expect(). log=None: the page's own defaults, both off (the switches' own tests).
        self.log_switches = bool(log)
        self.expected_codes = set()

    def expect(self, *codes):
        """Declare error / critical messages this test causes ON PURPOSE (e.g. 'BOOT-01') — the end-of-session log check
        lets exactly these through."""
        self.expected_codes.update(codes)

    # --- start / stop -------------------------------------------------------------------------------------------
    def __enter__(self):
        # Screen tests run in parallel (tools/run_tests.py --jobs, 2026-11-16): the free port is chosen here and taken by
        # serve.py a moment later, so another file's server can take it in between. Then ours can't start — and a plain
        # "does the port answer?" would be answered by the OTHER server (this file's pages from a server that stops when
        # that file ends). So the port must be served by OUR serve.py; if it isn't, try another port.
        # serve.py — and the real Python the venv's python.exe starts as its child — runs in a job of its own
        # (tools/job.py): what listens on the port is ours only if it is in that job.
        for _ in range(3):
            self.port = local_relay.free_port()
            self.server_job = job.new()
            self.server, _ = self.server_job.launch([sys.executable, "serve.py", str(self.port)], cwd=ROOT,
                                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                                    stderr=subprocess.DEVNULL)
            if self._server_is_ours():
                break
            left = self.server_job.end()       # the port is another run's: only our own processes are stopped
            self.server_job.close()
            if left:
                print(f"  ! our web server's failed start left processes {left} running", flush=True)
        else:
            raise harness.EnvironmentTrouble("our web server (serve.py) didn't start — 3 ports tried")
        try:
            return self._start_browser()
        except BaseException:
            self.__exit__()
            raise

    def _start_browser(self):
        if self.want_relay:
            # The worker answers only listed pages: --var lists this test's page for this run, wrangler.toml untouched.
            # Kept before start(), so __exit__ stops whatever it started even if starting fails.
            self.relay = local_relay.LocalRelay(extra_args=["--var", f"ALLOWED_ORIGINS:http://localhost:{self.port}"])
            try:
                self.relay.start()
            except local_relay.RelayError as e:
                raise harness.EnvironmentTrouble(f"our local relay didn't start: {str(e).splitlines()[0]}") from e
        self.pw = sync_playwright().start()
        try:
            self.browser = self.pw.chromium.launch(channel=BROWSER, headless=not self.headed,
                                                   slow_mo=250 if self.headed else 0,
                                                   ignore_default_args=["--hide-scrollbars"])
        except PlaywrightError as e:
            raise harness.EnvironmentTrouble(f"the browser didn't start: {str(e).splitlines()[0]}") from e
        self.browser.on("disconnected", self._disconnected)
        w, h = self.size
        self.ctx = self.browser.new_context(viewport={"width": round(w / self.zoom), "height": round(h / self.zoom)},
                                            device_scale_factor=self.zoom)
        self.ctx.route(lambda u: "goatcounter" in u or "gc.zgo.at" in u,
                       lambda r: r.fulfill(status=204, body=""))
        # Ron's rule — screen tests never touch Amazon or a real relay — is ENFORCED here, not just recorded
        # (2026-11-10: a real library's cover addresses were fetched from Amazon's image server during load timing).
        # A cover gets a small stand-in image (so the cover cache fills as it does for a person); anything else to those
        # hosts is refused. The request is still recorded (violations), so a test that asserts "no requests" still sees it.
        self.ctx.route(lambda u: bool(FORBIDDEN_HOSTS.search(u.split("/")[2] if "://" in u else "")), self._block)
        if self.log_switches:
            self.ctx.add_init_script("""try { if (!localStorage.getItem('rw-test-log-switches-set')) {
                localStorage.setItem('readerwrangler-log-banner', 'on'); localStorage.setItem('readerwrangler-log-detail', 'on');
                localStorage.setItem('rw-test-log-switches-set', '1'); } } catch (e) {}""")
        if self.relay:
            # Before the app's own scripts on every load: point it at the local relay, and give a fresh profile the test
            # channel (only when none is set, so a reload keeps whatever the app has done since).
            creds = json.dumps({"channelId": TEST_CHANNEL, "passphrase": TEST_PASSPHRASE})
            self.ctx.add_init_script(f"""window._RW_RELAY_WORKER_URL = {json.dumps(self.relay.url)};
                try {{ if (!localStorage.getItem('readerwrangler-relay'))
                           localStorage.setItem('readerwrangler-relay', {json.dumps(creds)}); }} catch (e) {{}}""")
        self.ctx.on("requestfailed", self._request_failed)
        self.ctx.on("request", self._note_library_request)
        self.ctx.on("response", self._library_response)
        if self.before_load:
            self.before_load(self.ctx)
        self.page = self.ctx.new_page()
        self._watch_page(self.page)
        self.page.on("console", self._record_console)
        self.page.on("pageerror", lambda e: self.crashes.append(str(e)))
        self.page.on("request", self._watch_request)
        self._off_failure = harness.on_failure(self._failure_shot)
        self._open(self.page, f"http://localhost:{self.port}/readerwrangler.html")
        return self

    # --- the machine's or the browser's trouble, told from the app's (2026-11-17, TODO tooling item 9) ---------------
    def _open(self, page, url=None, reload=False):
        """Load the app in `page` (or reload it) and wait until it's up. A page that never loads — its start screen still
        up after APP_TIMEOUT_MS — is the machine's trouble when the page reported no error of its own (EnvironmentTrouble);
        with one, it's a test failure naming it (AssertionError). A screenshot of the screen either way. A load our own
        server didn't answer (a refused connection…) is the machine's trouble too. Only errors from THIS load count (a
        reload late in a session isn't judged by what the page reported earlier)."""
        before = len(self._own_errors.get(page, []))
        try:
            if reload:
                page.reload(timeout=APP_TIMEOUT_MS)
            else:
                page.goto(url, timeout=APP_TIMEOUT_MS)
            page.wait_for_selector("#splash", state="detached", timeout=APP_TIMEOUT_MS)
        except PlaywrightTimeout:
            shot = self._shot_quietly(page, "start")
            if shot:
                print(f"      screenshot: {shot}", flush=True)
            own = self._own_errors.get(page, [])[before:]
            lost = self._libraries_lost(page)
            names = environment_trouble.library_not_defined(own, list(lost))
            if names:       # its only errors: a library's name missing, because its script never arrived (2026-11-17)
                raise harness.EnvironmentTrouble(
                    f"a library the page needs didn't download — {'; '.join(lost.values())} — so "
                    f"{' and '.join(names)} {'was' if len(names) == 1 else 'were'} not defined and the app never "
                    "opened") from None
            if own:
                raise AssertionError(f"the app didn't open within {APP_TIMEOUT_MS // 1000} s — and the page reported "
                                     "errors of its own:\n" + "\n".join(x[:200] for x in own[:6])
                                     + "\n" + self._libraries_said(page)) from None
            raise harness.EnvironmentTrouble(f"the page never loaded — the app's start screen was still up after "
                                             f"{APP_TIMEOUT_MS // 1000} s, and the page reported no error of its own") \
                from None
        except PlaywrightError as e:
            m = re.search(r"net::(ERR_[A-Z_]+)", str(e))
            name = m and environment_trouble.net_error(m.group(0), page.url if reload else url, self._app_hosts())
            if name:
                raise harness.EnvironmentTrouble(f"the page couldn't load from our own web server: {name}") from None
            raise

    def _app_hosts(self):
        return [f"localhost:{self.port}", f"127.0.0.1:{self.port}"]

    def _relay_hosts(self):
        return [environment_trouble.host_of(self.relay.url)] if self.relay and getattr(self.relay, "url", None) else []

    def _watch_page(self, page):
        """Note what a page reports of its own (its errors — what makes a start-up timeout the app's, not the machine's),
        and a tab that crashes (the browser's trouble)."""
        own = self._own_errors.setdefault(page, [])
        page.on("pageerror", lambda e: own.append(f"crash: {e}"))
        page.on("console", lambda m: own.append(f"error: {m.text}") if m.type == "error" and not self._is_noise(m)
                else None)
        page.on("crash", lambda *_: harness.environment("a tab of the browser crashed"))

    def _is_noise(self, m):
        """A console message that is no error of the page's own: known noise, a request to our own server that failed
        for the machine's reasons, or a library the page loads that failed to download (the network's or its host's)."""
        url = (m.location or {}).get("url", "") if m.text.startswith("Failed to load resource") else ""
        return any(re.search(p, m.text) for p, _ in KNOWN_NOISE) or bool(self._machine_net_error(m.text, url)) \
            or bool(environment_trouble.library_failure_in_console(m.text, url))

    # --- a library the page loads, lost on the way (2026-11-17; tools/environment_trouble.py) ------------------------
    def _note_library_request(self, req):
        if req.resource_type in ("script", "stylesheet") and environment_trouble.is_library(req.url):
            try:
                page = req.frame.page
            except Exception:   # noqa: BLE001 — a request with no page of its own
                page = None
            self._library_requests.append((page, req))

    def _library_response(self, resp):
        """A library host answering 5xx for a script or stylesheet: the host's trouble, noted as it happens."""
        req = resp.request
        why = environment_trouble.library_download_failed(req.url, req.resource_type, status=resp.status)
        if why:
            harness.environment(f"a library the page loads didn't download: {why}")

    def _libraries_lost(self, page):
        """{address: why} — the library scripts and stylesheets `page` asked for that didn't download: failed, answered
        5xx, or answered with nothing (the body is read only here, after the fact)."""
        lost = {}
        for p, req in self._library_requests:
            if p is not None and p is not page:
                continue
            try:
                failure, resp = req.failure, req.response()
                status = resp.status if resp else None
                size = len(resp.body()) if resp and 200 <= status <= 299 else None
            except Exception:   # noqa: BLE001 — what the browser can't say counts as nothing lost
                continue
            why = environment_trouble.library_download_failed(req.url, req.resource_type, failure, status, size)
            if why:
                lost[req.url] = why
        return lost

    def _libraries_said(self, page):
        """What happened to each library download of `page`, in words — under a start-up failure, for the next reader."""
        out = []
        for p, req in self._library_requests:
            if p is not None and p is not page:
                continue
            try:
                resp = req.response() if not req.failure else None
                said = req.failure or (f"{resp.status}, {len(resp.body())} bytes" if resp else "no answer")
            except Exception as e:      # noqa: BLE001
                said = f"(couldn't be read: {type(e).__name__})"
            out.append(f"  library {req.url.split('?')[0]}: {said}")
        return "the libraries it asked for:\n" + "\n".join(out) if out else "it asked for no library"

    def _machine_net_error(self, text, url):
        """The network error's name if `text` (the browser's words) says a request to our own server failed for the
        machine's reasons — else None."""
        m = re.search(r"net::ERR_[A-Z_]+", text)
        return m and environment_trouble.net_error(m.group(0), url, self._app_hosts(), self._relay_hosts())

    @staticmethod
    def _console_url(line):
        """The address _record_console adds to a "Failed to load resource" line ("… [http://…]") — '' if none."""
        m = re.search(r" \[(\S+)\]$", line)
        return m.group(1) if m else ""

    def _request_failed(self, req):
        name = environment_trouble.net_error(req.failure or "", req.url, self._app_hosts(), self._relay_hosts())
        if name:
            harness.environment(f"a request to our own server failed: {name} ({req.url.split('?')[0]})")
        why = environment_trouble.library_download_failed(req.url, req.resource_type, failure=req.failure)
        if why:
            harness.environment(f"a library the page loads didn't download: {why}")

    def _disconnected(self, *_):
        if not self._closing:
            harness.environment("the browser closed or crashed (it disconnected)")

    def _shot_quietly(self, page, name):
        """A screenshot of `page` in the artifacts folder, named after this test file — its path, or None if the browser
        can't give one (a screenshot is a help, never a second failure)."""
        stem = os.path.splitext(os.path.basename(sys.argv[0] or "screen-test"))[0]
        try:
            os.makedirs(ARTIFACTS, exist_ok=True)
            p = os.path.join(ARTIFACTS, re.sub(r"[^\w.-]+", "_", f"{stem}-{name}") + ".png")
            page.screenshot(path=p, timeout=10_000)
            return p
        except Exception:   # noqa: BLE001
            return None

    def _failure_shot(self, label):
        """harness.on_failure: what the page showed when a test failed."""
        return self._shot_quietly(self.page, label) if getattr(self, "page", None) else None

    def logged_failures(self):
        """Every error / critical message in this session's console (the logging module's "level · CODE · text" lines)
        that the test didn't declare with expect() — lines a test planted on purpose (marked TEST) excepted."""
        out = []
        for _, x in self.console:
            m = re.match(r"^(error|critical) · ([A-Z]+(?:-\d+)?)(-!TEST!)? · ", x)
            if m and not m.group(3) and m.group(2) not in self.expected_codes:
                out.append(x[:220])
        return out

    def __exit__(self, *exc):
        if not exc or exc[0] is None:
            found = self.logged_failures()
            if found:
                from harness import fail_after   # (test/ui is on the path — every screen test imports harness first)
                fail_after("the session's log", "error / critical messages the tests didn't expect:\n" + "\n".join(found))
        if self._off_failure:
            self._off_failure()
        self._closing = True
        try:
            if getattr(self, "browser", None):
                self.browser.close()
            if getattr(self, "pw", None):
                self.pw.stop()
        finally:
            try:
                left = self.relay.stop() if self.relay else []
                if left:     # a process it started still running, or its port still in use: never quietly (Law 5)
                    from harness import fail_after
                    fail_after("the local relay", "not everything it started was stopped:\n" + "\n".join(left))
            finally:
                self._stop_server()

    def _server_is_ours(self, wait_s=10):
        """True once our serve.py answers on self.port — False if it stopped (the port was taken) or never answered. On
        Windows the listener is checked by process id: one in its job (the venv's python.exe starts the real Python as a
        child)."""
        deadline = time.time() + wait_s
        while time.time() < deadline:
            if self.server.poll() is not None:
                return False
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.2).close()
            except OSError:
                time.sleep(0.1)
                continue
            if os.name != "nt":
                return True
            if local_relay.port_owners(self.port) & set(self.server_job.running()):
                return True
            time.sleep(0.1)          # someone else answers there: ours either takes it or stops
        return False

    def _stop_server(self):
        """Stop our web server — every process in its job, by the job's handle — then check they're gone and its port
        is free. What's left is never quiet: it fails the file (Law 5). A second call does nothing."""
        if getattr(self, "server_job", None) is None:
            return
        left = local_relay.stop_and_check(self.server_job, [self.port], "our web server (serve.py)")
        self.server_job.close()
        self.server_job = None
        if left:
            from harness import fail_after
            fail_after("our web server (serve.py)", "not everything it started was stopped:\n" + "\n".join(left))

    def _record_console(self, m):
        # A "Failed to load resource" line names no address in its text — add the one the browser reports, so a
        # failure says which request it was.
        url = (m.location or {}).get("url", "") if m.text.startswith("Failed to load resource") else ""
        self.console.append((m.type, m.text + (f" [{url.split('?')[0]}]" if url else "")))

    STAND_IN_COVER = base64.b64decode(   # a 1x1 grey PNG
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mN89+7dfwAJ0wPaTqk7wQAAAABJRU5ErkJggg==")

    @staticmethod
    def _block(route):
        url = route.request.url.split("?")[0].lower()
        if route.request.resource_type == "image" or url.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            route.fulfill(status=200, content_type="image/png", body=App.STAND_IN_COVER,
                          headers={"Access-Control-Allow-Origin": "*"})
        else:
            route.abort()

    def _watch_request(self, req):
        host = req.url.split("/")[2] if "://" in req.url else ""
        if FORBIDDEN_HOSTS.search(host):
            self.violations.append(req.url.split("?")[0])

    # --- actions ------------------------------------------------------------------------------------------------
    def menu(self, top, item):
        """Click a menu-bar menu, then one of its items (by the start of its words). The app's tab is brought to the front
        first, as a person switches to it: with a second tab open (open_tab), Chrome slows the tabs behind — under load
        the Tools click on the tab behind took 122-222 s, 0.1 s in front (2026-11-17, test_reset.py)."""
        self.page.bring_to_front()
        self.page.get_by_role("button", name=re.compile(r"^\s*" + re.escape(top))).first.click()
        return self.page.get_by_role("button", name=re.compile(re.escape(item))).first

    def restore(self, path, expect="Backup Restored"):
        """File → Restore Backup… with this file, through the real menu and file box. Refuses a file carrying a key.
        Onto a library that has books, answers the "restore?" box with Restore, as a person would. Waits for the box
        titled `expect` (a refused file: "Restore Error"); returns its text and closes it."""
        raw = gzip.open(path).read() if path.endswith(".gz") else open(path, "rb").read()
        relay = json.loads(raw).get("relay") or {}
        if relay.get("channelId") or relay.get("passphrase"):
            raise RuntimeError(f"{os.path.basename(path)} carries a Cloud Sync Key — test data never may")
        item = self.menu("File", "Restore Backup")
        with self.page.expect_file_chooser() as fc:
            item.click()
        name = os.path.basename(path)[:-3] if path.endswith(".gz") else os.path.basename(path)
        fc.value.set_files(files=[{"name": name, "mimeType": "application/json", "buffer": raw}])
        dialog = self.page.get_by_text(expect, exact=True)
        confirm = self.page.get_by_role("button", name="Restore", exact=True)
        deadline = time.time() + 120
        while not dialog.first.is_visible():
            if time.time() > deadline:
                raise AssertionError(f"no {expect!r} box within 120 s")
            if confirm.count() and confirm.first.is_visible():
                confirm.first.click()
            self.page.wait_for_timeout(100)
        box = dialog.first.locator("xpath=ancestor::*[.//button][1]")
        text = box.inner_text()
        box.get_by_role("button", name="OK").click()
        return text

    def reload(self):
        """Reload the page the way a person would (F5 — in the tab in front: brought there first, as menu() does) and wait
        until the app is up again (a page that never loads: _open)."""
        self.page.bring_to_front()
        self._open(self.page, reload=True)

    def empty_book_store(self):
        """Empty the browser's book store (storage.js: ReaderWranglerDB → books) and leave the folders alone — the two live
        in separate stores and can get out of step (TODO "Import files new books once…", part 2: the Sep 3 case). Takes
        effect at the next reload()."""
        self.page.evaluate("""() => new Promise((resolve, reject) => {
            const r = indexedDB.open('ReaderWranglerDB');
            r.onerror = () => reject(r.error);
            r.onsuccess = () => {
                const db = r.result, tx = db.transaction(['books'], 'readwrite');
                tx.objectStore('books').clear();
                tx.oncomplete = () => { db.close(); resolve(); };
                tx.onerror = () => reject(tx.error);
            };
        })""")

    # --- the waits: ONE set for every screen test (2026-11-18, sprint 9 — TESTING.md §3, §4; Law 22) ----------------------
    # A test waits for a condition, never a moment, each under LIMIT_MS (the app opening: APP_TIMEOUT_MS). Until sprint 9
    # they lived in the files that first needed them: until / toast in test_delete_key.py and test_rename_key.py (each with
    # its own LIMIT_MS), caught_up / settled / heard / held / amber_look in test_cells.py. A wait that proves something
    # does NOT happen is the exception — a fixed window, said in its line: "# timed on purpose: …".
    def wait_console(self, pattern, timeout_s=LIMIT_S, since=0):
        """Wait until a console line matching `pattern` has appeared (a condition, never a fixed sleep — §7). since: only
        lines from that many on (len(app.console) taken before the action — so an earlier line can't answer). Lines the
        page logged in the same moment as it (a repair right after the check that found it) are in app.console too when
        it returns: one round trip to the page first — the browser's messages arrive in order (2026-11-18)."""
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            hit = next((x for _, x in self.console[since:] if re.search(pattern, x)), None)
            if hit:
                self.page.evaluate("0")
                return hit
            self.page.wait_for_timeout(100)
        raise AssertionError(f"no console line matching {pattern!r} within {timeout_s} s")

    def wait_loaded(self, page=None, timeout_ms=APP_TIMEOUT_MS):
        """Wait until the app's start-up LOAD has finished (2026-11-18 — a condition, never a fixed sleep: TESTING.md §3).
        reload() and the first load return once the start screen is gone — the app is drawn, but the library loads after
        it. Finished = its folders are set (every finished load has at least the Inbox; readerwrangler.js loadData sets
        them last, in the same step that ends "loading" — window.folders mirrors them), or the critical box is up (a load
        that failed — BOOT-01 — or a critical message on its way). By then whatever the load did before — its warnings,
        its save of the books — has happened."""
        (page or self.page).wait_for_function(
            "() => (window.folders || []).length > 0 || !!document.getElementById('rw-log-critical')", timeout=timeout_ms)

    def console_matching(self, pattern, since=0):
        return [x for _, x in self.console[since:] if re.search(pattern, x)]

    def heard(self, pattern, since=0):
        """wait_console that never raises: True once a line matching `pattern` (from line `since` on) has come, False when
        none came within LIMIT_S — so the checks after it still run and say what went wrong, in their own words (as they
        did when the wait was a fixed moment; test_cells.py's words() and undo)."""
        try:
            self.wait_console(pattern, LIMIT_S, since=since)
            return True
        except AssertionError:
            return False

    def until(self, cond, limit_ms=LIMIT_MS):
        """Wait until cond() is true, or limit_ms has passed — a condition, never a moment. Raises nothing: the check after
        it says what's wrong, in its own words. (Python's Playwright has no expect.poll; this is it, on the page's own
        clock.) For a condition the page answers in one expression, page.wait_for_function is the same, and raises."""
        deadline = time.monotonic() + limit_ms / 1000
        while not cond() and time.monotonic() < deadline:
            self.page.wait_for_timeout(50)   # a poll's step, not a wait for a moment

    # The page has run every task queued before now: a timer task, a message task (React's scheduler runs a render's
    # effects in message tasks — the left pane's scroll to the open folder, the saves, window.folders), a timer task. NOT
    # requestIdleCallback, on purpose: after an Escape, Chrome gave the page no idle time for 3–5 s with nothing to do
    # (measured 2026-11-18; after a click, ~0.3 s) — a wait for "idle" would wait that long for nothing.
    CAUGHT_UP_JS = """() => new Promise(r => setTimeout(() => { const c = new MessageChannel();
        c.port1.onmessage = () => setTimeout(r, 0); c.port2.postMessage(null); }, 0))"""

    def caught_up(self, page=None):
        """Wait until the page has done what the last step started: every task it queued has run — React's effects after
        its render, and any message they say. A condition the page answers (CAUGHT_UP_JS), not a moment."""
        (page or self.page).evaluate(self.CAUGHT_UP_JS)

    def settled(self, read_js, page=None):
        """read_js's reading (a JS function's source, returning anything JSON can hold) once the page has settled: two
        readings with the page caught up between them are the same. Still changing at LIMIT_MS: a failure."""
        got = (page or self.page).evaluate(f"""async (limit) => {{
            const read = {read_js};
            const caughtUp = {self.CAUGHT_UP_JS};
            const end = performance.now() + limit;
            let last = JSON.stringify(read());
            for (;;) {{
                await caughtUp();
                const now = JSON.stringify(read());
                if (now === last) return {{ ok: true, value: JSON.parse(now) }};
                if (performance.now() > end) return {{ ok: false, value: JSON.parse(now) }};
                last = now;
            }}
        }}""", LIMIT_MS)
        if not got["ok"]:
            raise AssertionError(f"the page's reading never settled within {LIMIT_S} s (it was still changing)")
        return got["value"]

    def toast(self, *words):
        """The toast's words — waiting (LIMIT_MS) for a toast holding every one of `words` (an earlier toast may still be
        up); if none comes, whatever toast is up ("" for none): no such toast is an answer too, said by the check after."""
        t = self.page.locator(".clipboard-toast")
        for w in words:
            t = t.filter(has_text=w)
        try:
            t.first.wait_for(state="visible", timeout=LIMIT_MS)
            return t.first.inner_text()
        except PlaywrightTimeout:
            up = self.page.locator(".clipboard-toast")
            return up.first.inner_text() if up.count() else ""

    # The toast holding `words` ('' = the toast on screen): its look once it has reached amber — or once it's leaving (its
    # .animating flight to the status bar) or gone, never amber: then the check after says so with what it was.
    AMBER_JS = """words => {
        const el = [...document.querySelectorAll('.clipboard-toast')].find(t => t.innerText.includes(words));
        const probe = document.createElement('div');
        probe.style.backgroundColor = 'var(--toast-warning-bg)';
        document.body.appendChild(probe);
        const amber = getComputedStyle(probe).backgroundColor;
        probe.remove();
        if (!el) return { cls: '(no toast)', bg: '(no toast)', amber };
        const look = { cls: el.className, bg: getComputedStyle(el).backgroundColor, amber };
        return look.bg === amber || el.classList.contains('animating') ? look : null;
    }"""

    def amber_look(self, words=""):
        """The look of a toast that should be a warning — {cls, bg, amber} — once it has reached amber: a toast fades to its
        colors (.clipboard-toast's 1 s transition) — read too soon, it's still part-way (2026-11-17, a loaded PC:
        rgba(254, 243, 199, 0.557)). Waited for each frame (AMBER_JS)."""
        return self.page.wait_for_function(self.AMBER_JS, arg=words, timeout=LIMIT_MS).json_value()

    # Timed on purpose — a DURATION is what's tested ("a warning stays ~4 s where it appeared, others 1.5 s"): `ms` after
    # the app was told to show the toast whose words are `text` (its log entry's time — the toast's own hold timers start
    # in that same moment), is a toast holding `words` ('' = any) still where it appeared (not .animating)? Waited IN the
    # page, on the page's clock: the app's hold timers and this one share one queue, so under any load this one (due
    # first) runs before a later-due hold ends — no lag between our clock and the browser's can move the answer.
    HELD_JS = """async ([text, words, ms]) => {
        const e = window.rwLog.entries().reverse().find(x => x.text && text.includes(x.text));
        if (!e) return 'no log entry for the toast';
        await new Promise(r => setTimeout(r, Math.max(0, e.time + ms - Date.now())));   // timed on purpose (above)
        return [...document.querySelectorAll('.clipboard-toast:not(.animating)')].some(t => t.innerText.includes(words));
    }"""

    def held(self, text, words, ms):
        """True if, `ms` after the toast saying `text` was shown, a toast holding `words` is still where it appeared
        (HELD_JS — timed on purpose: a duration is what's tested)."""
        still = self.page.evaluate(self.HELD_JS, [text, words, ms])
        if not isinstance(still, bool):
            raise AssertionError(f"can't time the toast {text!r}: {still}")
        return still
    # --- (end of the waits) --------------------------------------------------------------------------------------------

    # --- Cloud Sync, against the local relay (App(relay=True)) --------------------------------------------------------
    def upload_fetch(self, items):
        """Send books to the cloud copy exactly as the library fetcher does: one "books" run through the page's own
        relay-client (amazon-library-fetcher.js's writeRun call), with the fetcher's payload shape."""
        if not self.relay:
            raise RuntimeError("upload_fetch needs App(relay=True)")
        return self.page.evaluate("""async (items) => {
            const payload = { schemaVersion: '2.3', books: { fetchDate: new Date().toISOString(),
                              fetcherVersion: 'screen-test', totalBooks: items.length, items } };
            const res = await window.RWRelay.writeRun(JSON.stringify(payload), 'books', () => {});
            return { runId: res.runId, parts: res.seqCount };
        }""", items)

    def import_from_relay(self):
        """File → Import from Relay through the real menu; returns the finished dialog's text and closes it."""
        self.menu("File", "Import from Relay").click()
        # The progress box (readerwrangler.js showProgressDialog) gains its OK button only when the import has finished.
        ok = self.page.locator(".rw-imperative-overlay").get_by_role("button", name="OK", exact=True)
        ok.wait_for(timeout=120_000)
        text = ok.locator("xpath=ancestor::div[contains(@class, 'rw-imperative-overlay')]").inner_text()
        ok.click()
        return text

    # --- reaching things the way a person would (PRINCIPLES Law 8, from the utilities project's Law 21) -------------
    class Unreachable(Exception):
        """A target a person couldn't reach: covered by something else, or with no size."""

    def hover(self, target):
        """Move the REAL pointer to the middle of `target` (a locator) and report what is actually under it:
        {'under': description, 'title': its tooltip, 'width', 'height'}. Refuses (App.Unreachable) a target with no
        size, or one covered by something else — naming what covers it. Reading an attribute proves a thing exists,
        not that anyone can get to it."""
        target.scroll_into_view_if_needed(timeout=LIMIT_MS)
        box = target.bounding_box()
        if not box or box["width"] < 1 or box["height"] < 1:
            raise App.Unreachable(f"the target has no size ({box}) — nobody can point at it")
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        target.page.mouse.move(x, y)   # the target's own tab (a second tab: the emergency screen, the reset page)
        info = target.evaluate("""(el, pt) => {
            const top = document.elementFromPoint(pt.x, pt.y);
            const say = (e) => !e ? 'nothing' : e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
                (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).slice(0, 2).join('.') : '') +
                (e.textContent ? ' "' + e.textContent.trim().slice(0, 40) + '"' : '');
            // Reached: the pointer lands on the target, inside it, or on the element that CONTAINS it — a click-through
            // label (pointer-events:none) passes the click to its row, which is the real target. A cover laid over
            // the page never contains the target, so it's still caught (DRV-002).
            return { reached: !!top && (top === el || el.contains(top) || top.contains(el)), under: say(top), self: say(el),
                     title: el.getAttribute('title') || '' };
        }""", {"x": x, "y": y})
        if not info["reached"]:
            raise App.Unreachable(f"{info['self']} is covered — the pointer lands on {info['under']}")
        return {"under": info["under"], "title": info["title"], "width": box["width"], "height": box["height"]}

    def click_reachable(self, target):
        """hover() first (refusing a covered or zero-size target), then a real click where the pointer is."""
        info = self.hover(target)
        target.page.mouse.down()
        target.page.mouse.up()
        return info

    def seen(self, target):
        """A thing shown only to be READ — a message (toast), which lets clicks pass through it (7.31.0) — is on screen:
        it has a size and nothing is laid over its middle (a dialog above it, say). Refuses (App.Unreachable) otherwise,
        naming what covers it. hover() can't judge it: the browser's "what's under the pointer" skips a thing that lets
        clicks through, so it would name what's underneath. Here the target counts for that one question (its own
        pointer-events put back at once); the pointer isn't moved."""
        target.scroll_into_view_if_needed(timeout=LIMIT_MS)
        box = target.bounding_box()
        if not box or box["width"] < 1 or box["height"] < 1:
            raise App.Unreachable(f"the target has no size ({box}) — nobody can see it")
        info = target.evaluate("""(el, pt) => {
            const was = el.style.pointerEvents;
            el.style.pointerEvents = 'auto';
            const top = document.elementFromPoint(pt.x, pt.y);
            el.style.pointerEvents = was;
            const say = (e) => !e ? 'nothing' : e.tagName.toLowerCase() +
                (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).slice(0, 2).join('.') : '') +
                (e.textContent ? ' "' + e.textContent.trim().slice(0, 40) + '"' : '');
            return { seen: !!top && (top === el || el.contains(top)), under: say(top), self: say(el) };
        }""", {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2})
        if not info["seen"]:
            raise App.Unreachable(f"{info['self']} is covered — on top of its middle: {info['under']}")
        return {"width": box["width"], "height": box["height"]}

    # --- the world outside the page: never really reached ----------------------------------------------------------
    # 7.29.0 (Report a problem): a test must never open a real mail program or a real web page, and the clipboard is the
    # computer's, not the test's. stub_outside() replaces both IN THE PAGE with recorders — window.open(...) calls land in
    # window._opened (each call's arguments, as text), clipboard writes in window._copied — so a test asserts what WOULD
    # have opened or been copied. refuse_clipboard=True: the browser says no, as it may (an insecure page, a denied
    # permission). Call it again to change that; what was recorded stays.
    STUB_OUTSIDE_JS = """(refuse) => {
        window._opened = window._opened || []; window._copied = window._copied || [];
        window._refuseClipboard = !!refuse;
        Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async (t) => {
            if (window._refuseClipboard) throw new DOMException('Write permission denied (screen test).', 'NotAllowedError');
            window._copied.push(String(t)); } } });
        window.open = (...a) => { window._opened.push(a.map(x => String(x))); return null; };
    }"""

    def stub_outside(self, page=None, refuse_clipboard=False):
        (page or self.page).evaluate(self.STUB_OUTSIDE_JS, refuse_clipboard)

    def opened(self, page=None):
        """Every window.open(...) the page made since stub_outside(), oldest first: [[url, target, features], ...]."""
        return (page or self.page).evaluate("() => window._opened")

    def copied(self, page=None):
        """Every text the page wrote to the clipboard since stub_outside(), oldest first."""
        return (page or self.page).evaluate("() => window._copied")

    def open_broken_app(self, body="this is not javascript {"):
        """A second tab whose app code fails to load ON PURPOSE (the way 7.27.1's screenshots reached it): the built
        dist/readerwrangler.js is answered with `body` (by default a syntax error, as a damaged or half-updated copy would
        be), so the app never starts and the page's own "Something went wrong" screen appears. That screen waits 15 s for
        the app (readerwrangler.html) — the tab's clock is moved past it, not waited for. Returns (page, its console)."""
        page = self.ctx.new_page()
        log = []
        page.on("console", lambda m: log.append((m.type, m.text)))
        page.on("pageerror", lambda e: log.append(("crash", str(e))))
        page.route(lambda u: "/dist/readerwrangler.js" in u,
                   lambda r: r.fulfill(status=200, content_type="application/javascript", body=body))
        page.clock.install()
        page.goto(f"http://localhost:{self.port}/readerwrangler.html")
        page.clock.fast_forward(16_000)
        page.get_by_text("Something went wrong", exact=True).wait_for(timeout=LIMIT_MS)
        return page, log

    # --- reading the screen -------------------------------------------------------------------------------------
    def left_count(self, label):
        """The (N) the left pane shows beside an entry, e.g. left_count("Inbox") → 2."""
        row = self.page.get_by_text(label, exact=True).first.locator("xpath=ancestor::*[contains(., '(')][1]")
        m = re.search(r"\((\d+)\)", row.inner_text())
        return int(m.group(1)) if m else None

    def unexpected_console(self):
        """Console errors and warnings not on KNOWN_NOISE, plus page crashes. Lines a test planted on purpose — marked
        with the logging module's test marker, read from the page (defined once, in logger.js) — don't count. A request
        to our own server that failed for the machine's reasons (net::ERR_NO_BUFFER_SPACE…, 2026-11-15) is the machine's
        trouble, not the app's: it raises harness.EnvironmentTrouble, naming it — never a test failure."""
        machine = [x for t, x in self.console if t == "error" and self._machine_net_error(x, self._console_url(x))]
        if machine:
            raise harness.EnvironmentTrouble("the browser couldn't load from our own server — " + "; ".join(
                x[:160] for x in machine[:3]) + (f" (+{len(machine) - 3} more)" if len(machine) > 3 else ""))
        lost = [x for t, x in self.console
                if t == "error" and environment_trouble.library_failure_in_console(x, self._console_url(x))]
        if lost:        # (2026-11-17) the network's or the library host's — not the app's
            raise harness.EnvironmentTrouble("a library the page loads didn't download — " + "; ".join(
                x[:160] for x in lost[:3]) + (f" (+{len(lost) - 3} more)" if len(lost) > 3 else ""))
        try:
            mark = self.page.evaluate("() => (window.rwLog && window.rwLog.TEST_MARK) || null")
        except Exception:
            mark = None
        out = [f"{t}: {x[:200]}" for t, x in self.console
               if t in ("error", "warning") and not any(re.search(p, x) for p, _ in KNOWN_NOISE)
               and not (mark and mark in x)]
        return out + [f"crash: {c[:200]}" for c in self.crashes]

    def open_tab(self, path="readerwrangler.html", wait_for_app=True):
        """A second tab in the same browser — it shares the book store and the saved settings with the first, exactly as
        two of Ron's tabs do (2026-11-06, the Reset tests). Returns (page, its console lines)."""
        page = self.ctx.new_page()
        self._watch_page(page)
        log = []
        page.on("console", lambda m: log.append((m.type, m.text)))
        page.on("pageerror", lambda e: log.append(("crash", str(e))))
        if wait_for_app:
            self._open(page, f"http://localhost:{self.port}/{path}")
        else:
            page.goto(f"http://localhost:{self.port}/{path}")
        return page, log

    # --- layout (2026-11-06: the status bar covered the right pane's scrollbar when the Cloud Sync icon made it taller) ---
    def covered_scroll_boxes(self):
        """Every scroll area (outside dialogs and the status bar) must end at or above the status bar's top, and where
        it shows a horizontal scrollbar, the scrollbar must be what's under the pointer. Returns the problems, in words."""
        return self.page.evaluate(_STATUS_BAR_JS + """
            const problems = [];
            const bar = statusBar(), barTop = bar ? bar.getBoundingClientRect().top : innerHeight;
            for (const el of document.querySelectorAll('body *')) {
                const cs = getComputedStyle(el);
                if (!/(auto|scroll)/.test(cs.overflowX + cs.overflowY)) continue;
                if ((bar && bar.contains(el)) || el.closest('[role=dialog], .rw-imperative-overlay')) continue;
                const r = el.getBoundingClientRect();
                if (r.width < 2 || r.height < 2 || cs.visibility === 'hidden') continue;
                if (r.bottom > barTop + 0.5)
                    problems.push(`${say(el)} ends at ${r.bottom.toFixed(1)}, below the status bar's top ` +
                                  `(${barTop.toFixed(1)}): the bar covers its bottom ${(r.bottom - barTop).toFixed(1)} px`);
                const hBar = el.offsetHeight - el.clientHeight - parseFloat(cs.borderTopWidth) - parseFloat(cs.borderBottomWidth);
                if (el.scrollWidth > el.clientWidth + 1 && hBar > 0) {
                    const y = r.bottom - parseFloat(cs.borderBottomWidth) - hBar / 2;
                    for (const x of [r.left + r.width * 0.25, r.left + r.width * 0.5]) {
                        const t = document.elementFromPoint(x, y);
                        if (!(t && (t === el || el.contains(t))))
                            problems.push(`${say(el)}: its horizontal scrollbar is covered at (${x | 0}, ${y | 0}) by ${say(t)}`);
                    }
                }
            }
            return problems;
        }""")

    def show_boxes(self, target, name):
        """PRINCIPLES Law 19: outline `target` (a locator) and every box around it, each layer in its own color, with a
        label saying where each one ends; save a screenshot; remove the outlines. Outline, not border: an outline takes no
        space, so the edges stay where they are. Returns the screenshot's path."""
        target.evaluate("""(el) => {
            const colors = ['#e11d48', '#2563eb', '#16a34a', '#d97706', '#9333ea', '#0891b2', '#db2777', '#65a30d'];
            let e = el, i = 0;
            while (e && e !== document.body) {
                const c = colors[i % colors.length], r = e.getBoundingClientRect();
                e.dataset.rwBoxOutline = e.style.outline || ' ';
                e.style.outline = `2px solid ${c}`; e.style.outlineOffset = '-2px';
                const tag = document.createElement('div');
                tag.className = 'rw-box-label';
                tag.textContent = `${i}: ${e.tagName.toLowerCase()}.${String(e.className).trim().split(/\\s+/).slice(0, 3).join('.')}  ends ${r.bottom.toFixed(1)}`;
                Object.assign(tag.style, { position: 'fixed', left: `${Math.max(0, r.left) + 4 + i * 14}px`,
                    top: `${Math.min(innerHeight - 14, r.bottom - 14)}px`, font: '10px monospace', color: '#fff',
                    background: c, padding: '0 3px', zIndex: 2147483647, pointerEvents: 'none' });
                document.body.appendChild(tag);
                e = e.parentElement; i++;
            }
        }""")
        try:
            return self.shot(name)
        finally:
            self.page.evaluate("""() => {
                document.querySelectorAll('.rw-box-label').forEach(t => t.remove());
                document.querySelectorAll('[data-rw-box-outline]').forEach(e => {
                    e.style.outline = e.dataset.rwBoxOutline.trim(); e.style.outlineOffset = '';
                    delete e.dataset.rwBoxOutline; });
            }""")

    def status_bar_taller(self, px=24):
        """Put a `px`-tall item in the status bar, as the Cloud Sync icon does (24 px) — returns a function that takes it
        out again. Lets a layout test check "whatever the bar holds" without turning Cloud Sync on."""
        self.page.evaluate(_STATUS_BAR_JS + """
            const s = document.createElement('span');
            s.id = 'rw-test-tall'; s.style.cssText = `display:inline-block; width:1px; height:${arguments[0]}px`;
            statusBar().appendChild(s);
        }""".replace("arguments[0]", str(int(px))))
        return lambda: self.page.evaluate("() => document.getElementById('rw-test-tall')?.remove()")

    def shot(self, name):
        os.makedirs(ARTIFACTS, exist_ok=True)
        p = os.path.join(ARTIFACTS, name + ".png")
        self.page.screenshot(path=p)
        return p
