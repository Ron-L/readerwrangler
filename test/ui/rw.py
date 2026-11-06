"""
test/ui/rw.py — the shared setup every screen test uses (docs/design/TESTING.md §2, §5, §7; 2026-11-04).

    with App() as app:                      # serve.py on a free port + a fresh, throwaway Chrome profile
        app.restore(FIXTURE)                # File → Restore Backup… through the real menu and file box
        app.left_count("All Books")         # the count the left pane shows for an entry
        app.unexpected_console()            # console errors / warnings / crashes not on the known-noise list
        app.violations                      # requests to a relay or to Amazon — the tests must make none
        app.shot("name")                    # a screenshot in the artifacts folder
        app.covered_scroll_boxes()          # scroll areas something else covers (the status bar, 2026-11-06)
        app.show_boxes(locator, "name")     # outline a box and every box around it, each in its own color (Law 19)

    App(zoom=1.25, size=(1000, 900))        # a window of 1000 x 900 screen pixels at 125% browser zoom

Rules it enforces (TESTING.md §5, §7): a fresh browser profile every time (Playwright's default — nothing of Ron's);
serve.py stopped by its exact process (Law 5); GoatCounter answered with an empty reply (tests never touch the usage
statistics); any request to a relay or to Amazon recorded as a violation; a data file carrying a Cloud Sync Key
refused. RW_HEADED=1 shows the browser (slowed down) for watching a test. Screenshots go to RW_TEST_ARTIFACTS, else
%TEMP%\\rw-test-artifacts. The browser is Chrome, the one Ron uses (2026-11-06); RW_BROWSER=msedge runs Edge. Scrollbars
are SHOWN: Playwright hides them in a hidden browser by default, which hides exactly the bugs a person sees (the status
bar covering the right pane's scrollbar, 2026-11-06).
"""
import gzip
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE = os.path.join(ROOT, "test", "fixtures", "small-fixture.json")
DEMO = os.path.join(ROOT, "readerwrangler-demo-library-ORGANIZED.json")
LARGE = os.path.join(ROOT, ".private", "test", "large-sample-private.json.gz")
ARTIFACTS = os.environ.get("RW_TEST_ARTIFACTS") or os.path.join(tempfile.gettempdir(), "rw-test-artifacts")

# Console messages that are expected today — each with its reason. Anything else fails a test. These three go away
# with "Faster loading: build the app ahead of time" (the in-browser compiler and style builder leave).
KNOWN_NOISE = [
    (r"cdn\.tailwindcss\.com should not be used in production", "the in-browser style builder — leaves with the precompile"),
    (r"You are using the in-browser Babel transformer", "the in-browser compiler — leaves with the precompile"),
    (r"\[BABEL\] Note: The code generator has deoptimised the styling",
     "Babel's note on a file over 500 KB — leaves with the precompile"),
    (r"goatcounter: not counting because of: localhost", "GoatCounter declining localhost"),
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
APP_TIMEOUT_MS = 180_000     # the in-browser compile takes ~50 s on a cold profile today
BROWSER = os.environ.get("RW_BROWSER", "chrome")


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class App:
    def __init__(self, headed=None, zoom=1.0, size=(1400, 900)):
        self.headed = os.environ.get("RW_HEADED") == "1" if headed is None else headed
        # Browser zoom Z on a window of W x H screen pixels = a page of W/Z x H/Z CSS pixels, each drawn Z screen pixels
        # wide. (An emulation: the browser's own scrollbars scale with it, which real zoom doesn't do.)
        self.zoom, self.size = zoom, size
        self.console, self.crashes, self.violations = [], [], []

    # --- start / stop -------------------------------------------------------------------------------------------
    def __enter__(self):
        self.port = _free_port()
        self.server = subprocess.Popen([sys.executable, "serve.py", str(self.port)], cwd=ROOT,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            self._stop_server()
            raise RuntimeError("serve.py didn't start")
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(channel=BROWSER, headless=not self.headed,
                                               slow_mo=250 if self.headed else 0,
                                               ignore_default_args=["--hide-scrollbars"])
        w, h = self.size
        self.ctx = self.browser.new_context(viewport={"width": round(w / self.zoom), "height": round(h / self.zoom)},
                                            device_scale_factor=self.zoom)
        self.ctx.route(lambda u: "goatcounter" in u or "gc.zgo.at" in u,
                       lambda r: r.fulfill(status=204, body=""))
        self.page = self.ctx.new_page()
        self.page.on("console", lambda m: self.console.append((m.type, m.text)))
        self.page.on("pageerror", lambda e: self.crashes.append(str(e)))
        self.page.on("request", self._watch_request)
        self.page.goto(f"http://localhost:{self.port}/readerwrangler.html")
        self.page.wait_for_selector("#splash", state="detached", timeout=APP_TIMEOUT_MS)
        return self

    def __exit__(self, *exc):
        try:
            self.browser.close()
            self.pw.stop()
        finally:
            self._stop_server()

    def _stop_server(self):
        self.server.terminate()          # the exact process we started (Law 5) — never a pattern
        try:
            self.server.wait(10)
        except subprocess.TimeoutExpired:
            self.server.kill()

    def _watch_request(self, req):
        host = req.url.split("/")[2] if "://" in req.url else ""
        if FORBIDDEN_HOSTS.search(host):
            self.violations.append(req.url.split("?")[0])

    # --- actions ------------------------------------------------------------------------------------------------
    def menu(self, top, item):
        """Click a menu-bar menu, then one of its items (by the start of its words)."""
        self.page.get_by_role("button", name=re.compile(r"^\s*" + re.escape(top))).first.click()
        return self.page.get_by_role("button", name=re.compile(re.escape(item))).first

    def restore(self, path):
        """File → Restore Backup… with this file, through the real menu and file box. Refuses a file carrying a key.
        Returns the confirmation's text and closes it."""
        raw = gzip.open(path).read() if path.endswith(".gz") else open(path, "rb").read()
        relay = json.loads(raw).get("relay") or {}
        if relay.get("channelId") or relay.get("passphrase"):
            raise RuntimeError(f"{os.path.basename(path)} carries a Cloud Sync Key — test data never may")
        item = self.menu("File", "Restore Backup")
        with self.page.expect_file_chooser() as fc:
            item.click()
        name = os.path.basename(path)[:-3] if path.endswith(".gz") else os.path.basename(path)
        fc.value.set_files(files=[{"name": name, "mimeType": "application/json", "buffer": raw}])
        dialog = self.page.get_by_text("Backup Restored", exact=True)
        dialog.wait_for(timeout=120_000)
        box = dialog.locator("xpath=ancestor::*[.//button][1]")
        text = box.inner_text()
        box.get_by_role("button", name="OK").click()
        return text

    # --- reaching things the way a person would (PRINCIPLES Law 8, from the utilities project's Law 21) -------------
    class Unreachable(Exception):
        """A target a person couldn't reach: covered by something else, or with no size."""

    def hover(self, target):
        """Move the REAL pointer to the middle of `target` (a locator) and report what is actually under it:
        {'under': description, 'title': its tooltip, 'width', 'height'}. Refuses (App.Unreachable) a target with no
        size, or one covered by something else — naming what covers it. Reading an attribute proves a thing exists,
        not that anyone can get to it."""
        target.scroll_into_view_if_needed(timeout=10_000)
        box = target.bounding_box()
        if not box or box["width"] < 1 or box["height"] < 1:
            raise App.Unreachable(f"the target has no size ({box}) — nobody can point at it")
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        self.page.mouse.move(x, y)
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
        self.page.mouse.down()
        self.page.mouse.up()
        return info

    # --- reading the screen -------------------------------------------------------------------------------------
    def left_count(self, label):
        """The (N) the left pane shows beside an entry, e.g. left_count("Inbox") → 2."""
        row = self.page.get_by_text(label, exact=True).first.locator("xpath=ancestor::*[contains(., '(')][1]")
        m = re.search(r"\((\d+)\)", row.inner_text())
        return int(m.group(1)) if m else None

    def unexpected_console(self):
        """Console errors and warnings not on KNOWN_NOISE, plus page crashes."""
        out = [f"{t}: {x[:200]}" for t, x in self.console
               if t in ("error", "warning") and not any(re.search(p, x) for p, _ in KNOWN_NOISE)]
        return out + [f"crash: {c[:200]}" for c in self.crashes]

    def console_matching(self, pattern):
        return [x for _, x in self.console if re.search(pattern, x)]

    def open_tab(self, path="readerwrangler.html", wait_for_app=True):
        """A second tab in the same browser — it shares the book store and the saved settings with the first, exactly as
        two of Ron's tabs do (2026-11-06, the Reset tests). Returns (page, its console lines)."""
        page = self.ctx.new_page()
        log = []
        page.on("console", lambda m: log.append((m.type, m.text)))
        page.on("pageerror", lambda e: log.append(("crash", str(e))))
        page.goto(f"http://localhost:{self.port}/{path}")
        if wait_for_app:
            page.wait_for_selector("#splash", state="detached", timeout=APP_TIMEOUT_MS)
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
