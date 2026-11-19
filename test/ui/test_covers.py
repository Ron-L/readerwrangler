# Screen test: the desktop keeps no cover copies of its own — covers come from their normal address.
# tags: covers, load, tier 2
# covers: readerwrangler.js, storage.js
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
#
# 2026-11-10 (TODO "Faster loading"; Ron counted ~7 s to his books on 7.27.0-alpha.1): every desktop load read all
# 3,270 covers out of the app's own cover copies ("rw-covers"), one by one into memory, before setting the folders —
# and on a fresh browser fetched them all in the background. Since 5.0.0 the desktop grid and list draw covers from
# their normal address (the browser's own cache); the copies served only the book details window. alpha.2 skipped the
# step as an experiment (folders 4.4 s → 2.3 s measured; Ron: ~3 s to folders, ~4 s to every cover); alpha.3 removes it
# and clears the copies a desktop browser still holds — ONCE (they count against the same storage space as the
# library). The phone keeps its copies (its own load path).
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import APP_TIMEOUT_MS, FIXTURE, App   # noqa: E402

HAS = "caches.keys().then(k => k.includes('rw-covers'))"
CLEARED = "readerwrangler-desktop-covers-cleared"

with App() as app:
    page = app.page
    app.restore(FIXTURE)

    def old_copies_cleared_once():
        page.evaluate("""caches.open('rw-covers').then(c => c.put('https://example.invalid/cover.jpg',
                         new Response('x', { headers: { 'Content-Type': 'image/jpeg' } })))""")
        page.evaluate(f"localStorage.removeItem('{CLEARED}')")   # a browser from before
        check(page.evaluate(HAS), "setup: the old cover copies are there before the load")
        app.reload()
        app.wait_loaded()       # the load starts the clearing, and remembers it once the copies are gone
        # polled (evaluate awaits the answer; wait_for_function wouldn't await a promise) until both are done, under the
        # driver's generous limit — a condition, not a count of tries (before: at most 50 x 0.2 s)
        deadline = time.time() + APP_TIMEOUT_MS / 1000
        while (page.evaluate(HAS) or page.evaluate(f"localStorage.getItem('{CLEARED}')") is None) \
                and time.time() < deadline:
            page.wait_for_timeout(200)
        check(not page.evaluate(HAS), "the old cover copies are gone after the load")
        check(page.evaluate(f"localStorage.getItem('{CLEARED}')") is not None,
              "the clearing is remembered, so it happens once")
    test("COVERS-001", "a desktop load clears the cover copies a browser still holds, once", old_copies_cleared_once)

    def nothing_recreates_them():
        app.reload()
        app.wait_loaded()
        # timed on purpose: proves nothing builds them — the old background filler started right after the load, so the
        # window is measured from the load's end (before: from the start screen leaving)
        page.wait_for_timeout(3000)
        check(not page.evaluate(HAS), "after another load there are still no cover copies — nothing builds them now")
    test("COVERS-002", "a desktop load builds no cover copies (the browser's own cache serves the covers)",
         nothing_recreates_them)

done()
