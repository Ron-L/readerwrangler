# Screen test: the app opens, and the made-up library restores and shows correctly (the base every screen test uses).
# tags: app, restore, tier 2
# covers: readerwrangler.html, readerwrangler.js, storage.js, bookFields.js, integrity.js
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import FIXTURE, App              # noqa: E402

with App() as app:
    test("APP-001", "a fresh app opens cleanly — no unexpected console messages, no requests to a relay or Amazon",
         lambda: (check(not app.unexpected_console(), app.unexpected_console()),
                  check(not app.violations, app.violations)))

    restored = {}

    def restore_fixture():
        restored["text"] = app.restore(FIXTURE)
        check("23 books restored" in restored["text"], restored["text"])
    test("APP-002", "File → Restore Backup… restores the made-up library (23 books)", restore_fixture)

    # The fixture's shape (test/fixtures/make-small-fixture.js): 22 live books + 1 in the Trash.
    EXPECTED = {"All Books": 22, "Inbox": 2, "Fantasy": 5, "The Test Saga": 4, "Science Fiction": 4,
                "Space Opera": 2, "Every Ownership Kind": 11, "An Empty Folder": 0, "Trash": 1,
                "The Saga": 4, "Tagged Read": 2, "Read Next": 3, "An Empty Book List": 0}

    def counts_match():
        got = {k: app.left_count(k) for k in EXPECTED}
        wrong = {k: (got[k], v) for k, v in EXPECTED.items() if got[k] != v}
        check(not wrong, "left pane (shown, expected): " + str(wrong))
    test("APP-003", "the left pane shows every folder, Book List and Search with the right counts", counts_match)

    test("APP-004", "after the restore: still no unexpected console messages and no requests to a relay or Amazon",
         lambda: (check(not app.unexpected_console(), app.unexpected_console()),
                  check(not app.violations, app.violations)))

    print("    screenshot:", app.shot("APP-restored"))

done()
