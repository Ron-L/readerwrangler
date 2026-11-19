# Screen test: nothing covers a scroll area or its scrollbar — at any zoom, whatever the status bar holds.
# tags: layout, statusbar, tier 2
# covers: readerwrangler.js, readerwrangler.css, readerwrangler.html
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
#
# 2026-11-06 (Ron): the right pane's horizontal scrollbar was a sliver at 125% browser zoom and gone at 150% — the status
# bar floated over the window's bottom edge, the panes left a fixed 24 px for it, and with Cloud Sync on its icon makes the
# bar 33 px tall, so it covered the panes' bottom 9 px (where the scrollbar is). The rows: zoom x the bar as it is / as
# tall as the Cloud Sync icon makes it, in List View (the wide table, so there is a horizontal scrollbar) and Cover View.
# A window of 1000 x 900 screen pixels, so the table is wider than the pane at every zoom here. On a failure the picture
# with every layer outlined (rw.show_boxes, PRINCIPLES Law 19) is saved and named.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import APP_TIMEOUT_MS, FIXTURE, App   # noqa: E402

RIGHT_PANE = ".overflow-auto.pb-16"      # the right pane's scroll area (readerwrangler.js, the dragVirtScrollRef box)


def nothing_covered(app, label):
    problems = app.covered_scroll_boxes()
    if problems:
        pic = app.show_boxes(app.page.locator(RIGHT_PANE).first, "LAYOUT-" + label)
        check(False, "\n".join(problems[:4]) + f"\n(every layer outlined: {pic})")


# One row per test — (its ID, zoom, what it checks), the ID first in its row: run_tests.py --id finds a test where its ID
# is named as one — the first argument of its call or the first item of its row (TESTING.md §4).
ROWS = [("LAYOUT-001", 1.0, "list"), ("LAYOUT-002", 1.0, "tall"), ("LAYOUT-003", 1.0, "covers"),
        ("LAYOUT-004", 1.0, "console"), ("LAYOUT-005", 1.25, "list"), ("LAYOUT-006", 1.25, "tall"),
        ("LAYOUT-007", 1.25, "console")]
for zoom in (1.0, 1.25):
    ids = {what: tid for tid, z, what in ROWS if z == zoom}
    pct = f"{round(zoom * 100)}%"
    with App(zoom=zoom, size=(1000, 900)) as app:
        app.restore(FIXTURE)
        app.menu("View", "List View").click()
        app.page.locator(RIGHT_PANE).first.wait_for()
        test(ids["list"], f"List View at {pct}: nothing covers a scroll area or its scrollbar",
             lambda: nothing_covered(app, f"list-{pct}"))

        untall = app.status_bar_taller(24)
        # the bar holds the tall item — the page lays it out the moment it's measured (before: a 0.3 s sleep)
        app.page.wait_for_function("() => document.getElementById('rw-test-tall').getBoundingClientRect().height >= 24",
                                   timeout=APP_TIMEOUT_MS)
        test(ids["tall"], f"List View at {pct}, the status bar as tall as the Cloud Sync icon makes it: still nothing covered",
             lambda: nothing_covered(app, f"list-tall-{pct}"))
        untall()

        if zoom == 1.0:
            app.menu("View", "Cover View").click()
            # Cover View is drawn: the list's table gone from the right pane, the grid of covers there, and every cover
            # picture in it loaded — one arriving changes the pane's height, so its scrollbars (the fixture's books have
            # none: blank tiles) (before: a 0.5 s sleep)
            app.page.wait_for_function("""(sel) => { const pane = document.querySelector(sel);
                return !!pane && !pane.querySelector('table') && !!pane.querySelector('.grid')
                    && [...pane.querySelectorAll('img')].every(i => i.complete); }""", arg=RIGHT_PANE, timeout=APP_TIMEOUT_MS)
            test(ids["covers"], "Cover View at 100%: nothing covers a scroll area or its scrollbar",
                 lambda: nothing_covered(app, "covers-100%"))

        test(ids["console"], f"no unexpected console messages at {pct}",
             lambda: check(not app.unexpected_console(), app.unexpected_console()))

done()
