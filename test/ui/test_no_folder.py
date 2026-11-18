# Screen test: a book left in no folder is caught at the next save — put in the Inbox, saved there, logged as an error
# naming the last action and the books — and EVERY user sees the red bar for it; contributor mode turns the error bar on.
# tags: integrity, folders, logging, contributor, tier 2
# covers: readerwrangler.js, integrity.js, logkit/logger.js, logkit-settings.js, readerwrangler.html
# Run: py tools/run_tests.py --id NOFOLDER-001     (or --tier 2; or directly with the venv's Python)
#
# TODO "A book left in no folder is caught the moment it happens, naming the action that did it" (id 20261115-1239;
# decided Ron, 2026-11-16). The known causes are fixed (7.30.0), so a TEST HOOK leaves the books in no folder, as a broken
# action would: window._rwTestLeaveInNoFolder(ids) (readerwrangler.js — on a local server only, never on
# readerwrangler.com). Before it, a real action (a folder renamed with F2) so the error has an action to name.
# The fixture (test/fixtures/make-small-fixture.js): Science Fiction (3 books, Good Omens among them) ⊃ Space Opera ⊃
# Old Favorites; Fantasy ⊃ The Test Saga; Every Ownership Kind; An Empty Folder; the Inbox (2 books).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import APP_TIMEOUT_MS, FIXTURE, App   # noqa: E402

BANNER = "#rw-log-banner"
ONE = "'Good Omens' was in no folder — it's in the Inbox now. (That shouldn't happen; it's in the log.)"
SEVERAL = "3 books were in no folder — they're in the Inbox now. (That shouldn't happen; it's in the log.)"
RENAMED = "Rename folder 'Space Opera' to 'Space Westerns'"
SWITCHES = "() => window.rwLog.switches()"


def ids_of(app, titles):
    return app.page.evaluate("(ts) => ts.map(t => window.books.find(b => b.title === t).id)", titles)


def folders_holding(app, book_id):
    return app.page.evaluate("(id) => window.folders.filter(f => (f.bookIds || []).includes(id)).map(f => f.id)", book_id)


def leave_in_no_folder(app, titles):
    """The test hook: the books taken out of every folder (as a broken action would leave them)."""
    ids = ids_of(app, titles)
    app.page.evaluate("(ids) => window._rwTestLeaveInNoFolder(ids)", ids)
    return ids


def no_folder_errors(app):
    return app.page.evaluate("() => window.rwLog.entries().filter(e => e.code === 'INTEG-08')")


def bar_buttons(app):
    return [b.inner_text().strip() for b in app.page.locator(BANNER).locator("button").all()]


def bar_message(app):
    """The bar's words, without its buttons (7.31.0, Q-044: the kit's prefix only for a viewer who chose the bar)."""
    return app.page.locator(BANNER).locator("span").first.inner_text().strip()


def wait_bar(app, words):
    app.page.locator(BANNER).wait_for(timeout=5000)
    app.page.locator(BANNER).get_by_text(words, exact=False).wait_for(timeout=5000)
    return app.page.locator(BANNER).inner_text()


def dismiss(app):
    if app.page.locator(BANNER).count():
        app.click_reachable(app.page.locator(BANNER).get_by_text("Dismiss", exact=True))
        app.page.locator(BANNER).wait_for(state="detached", timeout=5000)


def rename_space_opera(app):
    """A real action with an undo step: Science Fiction open, Space Opera selected in the right pane, F2, a new name."""
    page = app.page
    page.mouse.move(900, 600)
    target = page.locator('[data-folder-id="f-scifi"]').first
    app.click_reachable(target)
    page.wait_for_function("el => !!el.closest('.bg-blue-100')", arg=target.element_handle(), timeout=3000)
    page.locator("tbody tr", has_text="Space Opera").first.click()
    page.wait_for_function("() => document.querySelectorAll('tbody tr.bg-blue-50').length === 1", timeout=3000)
    page.keyboard.press("F2")
    page.locator("tbody tr input[type=text]").first.wait_for(timeout=3000)
    page.keyboard.press("Control+a")
    page.keyboard.type("Space Westerns")
    page.keyboard.press("Enter")
    page.wait_for_function("() => window.folders.find(f => f.id === 'f-space').name === 'Space Westerns'", timeout=3000)
    page.keyboard.press("Escape")
    # Esc clears the selection (readerwrangler.js, the main view's Esc): no row selected (before: a 0.15 s sleep)
    page.wait_for_function("() => document.querySelectorAll('tbody tr.bg-blue-50').length === 0", timeout=APP_TIMEOUT_MS)


# ---- An ordinary user: no contributor mode, both logging switches off (the page's defaults) ----
with App(log=None) as app:
    page = app.page
    app.expect("INTEG-08")   # caused on purpose — the end-of-session log check lets exactly this through
    app.restore(FIXTURE)
    app.menu("View", "List View").click()
    app.stub_outside()

    def one_book():
        check(page.evaluate(SWITCHES) == {"errorBanner": False, "logDetail": False}, "setup: the switches should be off")
        rename_space_opera(app)
        # timed on purpose: proves the rename reports nothing — a window from the rename having landed (the check at
        # every save runs a moment after the change; rename_space_opera waited for the new name)
        page.wait_for_timeout(300)
        check(no_folder_errors(app) == [], "a rename that leaves every book in a folder was reported")
        [gid] = leave_in_no_folder(app, ["Good Omens"])
        text = wait_bar(app, ONE)
        check(ONE in text, f"the bar says: {text!r}")
        check(bar_message(app) == ONE, f"an ordinary user's bar should say just the message — no 🐞, level or code (Q-044): "
                                       f"{bar_message(app)!r}")
        check(folders_holding(app, gid) == ["__inbox__"], f"Good Omens should be in the Inbox now: {folders_holding(app, gid)}")
        errs = no_folder_errors(app)
        check(len(errs) == 1 and errs[0]["level"] == "error", f"one error, INTEG-08: {errs}")
        data = errs[0].get("data") or {}
        check(data.get("lastAction") == RENAMED, f"the error should name the last action ({RENAMED!r}): {data}")
        check(data.get("books") == [{"id": gid, "title": "Good Omens"}], f"the error should name the book: {data}")
        check(bar_buttons(app) == ["Copy", "Report this problem", "Dismiss"],
              f"the bar's buttons (no 'Turn off this banner' — the switch didn't raise it): {bar_buttons(app)}")
        toasts = [t.inner_text() for t in page.locator(".clipboard-toast").all()]
        check(not any("no folder" in t for t in toasts), f"a separate toast for it (the bar says it): {toasts}")
    test("NOFOLDER-001", "an ordinary user (banner switch off): a book left in no folder is in the Inbox at the next save, "
         "the red bar says so in the one-book words alone (no code), with Copy, Report this problem, Dismiss; the log names "
         "the last action", one_book)

    def copy_names_the_action():
        n0 = len(app.copied())
        # the log's lines before the bar's message (the page load, the rename…), as Copy diagnostics has them
        earlier = page.evaluate("""() => { const es = window.rwLog.entries();
                                           const i = es.findIndex(e => e.code === 'INTEG-08');
                                           return es.slice(0, i).map(e => window.rwLog.format(e)); }""")
        app.click_reachable(page.locator(BANNER).locator("button").first)
        page.locator(BANNER).get_by_text("Copied", exact=True).wait_for(timeout=3000)
        copied = app.copied()[n0:]
        check(len(copied) == 1, f"the bar's Copy should copy once: {copied}")
        lines = copied[0].split("\n") if copied else [""]
        check("error · INTEG-08 · " + ONE in lines[0], f"the bar's message, with its code, should be at the top: {lines[:3]}")
        check(RENAMED in lines[1], f"its details (the last action) on the line below it: {lines[:3]}")
        title = next((i for i, x in enumerate(lines) if x.startswith("ReaderWrangler diagnostics — ")), -1)
        check(title > 0 and lines[title + 1].startswith("Desktop app "),
              f"then the diagnostics, as Copy diagnostics has them (the app's build line under the title): "
              f"{lines[title:title + 2] if title >= 0 else lines[:8]}")
        check(earlier and all(x in copied[0] for x in earlier),
              f"the copy should hold the log's earlier lines: missing {[x for x in earlier if x not in copied[0]]}")
    test("NOFOLDER-002", "the bar's Copy copies the full diagnostics (the kept log) with the bar's message and its details "
         "at the top", copy_names_the_action)

    def report_opens_the_dialog():
        n0 = len(app.copied())
        app.click_reachable(page.locator(BANNER).get_by_text("Report this problem", exact=True))
        box = page.locator('[role="dialog"]', has=page.get_by_text("Report a problem", exact=True))
        box.wait_for(timeout=5000)
        page.get_by_text("Diagnostics copied — paste them into your message to us.").wait_for(timeout=5000)
        for name in ("Email us", "Report on GitHub"):
            check(box.get_by_role("button", name=name, exact=True).count() == 1, f"the dialog has no {name} button")
        copied = app.copied()[n0:]
        check(len(copied) == 1 and "INTEG-08" in copied[0] and RENAMED in copied[0],
              f"Report this problem should copy the diagnostics, the error and its details in them: {[c[:200] for c in copied]}")
        check(app.console_matching(r"^info · UI · Diagnostics copied \(the error banner\)"), "the copy isn't in the log")
        page.keyboard.press("Escape")
        box.wait_for(state="detached", timeout=5000)
        dismiss(app)
    test("NOFOLDER-003", "the bar's Report this problem opens the Report a problem window (as Help → Report a problem… "
         "does), the diagnostics copied", report_opens_the_dialog)

    def several_books():
        page.keyboard.press("Control+z")   # undo the rename — the last action is now that undo
        page.wait_for_function("() => window.folders.find(f => f.id === 'f-space').name === 'Space Opera'", timeout=3000)
        titles = ["The Test Saga, Book One", "The Test Saga, Book Two", "Owned as sample"]
        ids = leave_in_no_folder(app, titles)
        text = wait_bar(app, SEVERAL)
        check(SEVERAL in text, f"the bar says: {text!r}")
        for t, i in zip(titles, ids):
            check(folders_holding(app, i) == ["__inbox__"], f"{t!r} should be in the Inbox now: {folders_holding(app, i)}")
        errs = no_folder_errors(app)
        data = errs[-1].get("data") or {}
        check(sorted(b["title"] for b in data.get("books", [])) == sorted(titles), f"the error should name all three: {data}")
        check(data.get("lastAction") == "Undo: " + RENAMED, f"the last action is the undo: {data}")
        dismiss(app)
    test("NOFOLDER-004", "several books: the plural words, all three in the Inbox and named; an undo is named as the last action",
         several_books)

    def saved_there():
        titles = ["Good Omens", "The Test Saga, Book One", "The Test Saga, Book Two", "Owned as sample"]
        ids = ids_of(app, titles)
        saved_inbox = page.evaluate("""() => JSON.parse(localStorage.getItem('readerwrangler-state')).organization.folders
                                             .find(f => f.id === '__inbox__').bookIds""")
        check(all(i in saved_inbox for i in ids), f"the saved organization's Inbox doesn't hold them: {saved_inbox}")
        before = len(no_folder_errors(app))
        app.reload()
        app.wait_loaded()   # the library loaded — window.folders read below (found 2026-11-18: read right after the reload)
        for t, i in zip(titles, ids):
            check(folders_holding(app, i) == ["__inbox__"], f"after a reload {t!r} should still be in the Inbox: "
                                                            f"{folders_holding(app, i)}")
        # the load's own check (integrity.js) found nothing in no folder — its results are saved as it runs
        fixed = page.evaluate("() => JSON.parse(localStorage.getItem('readerwrangler-integrity') || '{}').autoFixed || []")
        check(not [f for f in fixed if f.get("type") == "homeless"], f"the load had to repair books in no folder: {fixed}")
        check(len(no_folder_errors(app)) == before, f"reported again after the reload: {no_folder_errors(app)}")
        check(page.locator(BANNER).count() == 0, "the bar came back after a reload")
    test("NOFOLDER-005", "the repair is saved: after a reload the book is still in the Inbox, nothing repaired or reported again",
         saved_there)

    test("NOFOLDER-006", "no unexpected console messages (INTEG-08, caused on purpose, excepted)",
         lambda: check(not [x for x in app.unexpected_console() if "INTEG-08" not in x],
                       [x for x in app.unexpected_console() if "INTEG-08" not in x]))


def plant_error(app, text):
    """An ordinary error, planted (marked TEST, so the session's log check ignores it) — the switch decides the bar."""
    app.page.evaluate("(t) => window.rwLog.log('error', 'UI-03', t, null, { test: true })", text)


# ---- A contributor: contributor mode on this browser, the banner switch never touched ----
with App(log=None) as app:
    page = app.page
    app.expect("INTEG-08")
    app.restore(FIXTURE)
    page.evaluate("() => localStorage.setItem('readerwrangler-contributor', 'on')")
    app.reload()

    def contributor_default_on():
        check(page.evaluate("() => localStorage.getItem('readerwrangler-log-banner')") is None,
              "setup: the banner switch should never have been touched")
        check(page.evaluate(SWITCHES) == {"errorBanner": True, "logDetail": False},
              f"a contributor who never touched the switch should have the error bar on: {page.evaluate(SWITCHES)}")
        plant_error(app, "an ordinary error")
        wait_bar(app, "an ordinary error")
        check(bar_message(app) == "🐞 error · UI-03-!TEST! · an ordinary error",
              f"a viewer with the bar on (a contributor) keeps the kit's prefix: {bar_message(app)!r}")
        check(bar_buttons(app)[-1] == "Turn off this banner",
              f"the switch raised this bar — its link should be there: {bar_buttons(app)}")
        check("Report this problem" in bar_buttons(app), f"the report button should be on every bar: {bar_buttons(app)}")
        dismiss(app)
    test("NOFOLDER-007", "a contributor who never touched the banner switch: it's on — an ordinary error raises the bar",
         contributor_default_on)

    def contributor_turned_off():
        plant_error(app, "an error to turn off")
        wait_bar(app, "an error to turn off")
        app.click_reachable(page.locator(BANNER).get_by_text("Turn off this banner", exact=True))
        page.locator(BANNER).wait_for(state="detached", timeout=5000)
        app.reload()
        app.wait_loaded()   # the books are there for leave_in_no_folder below (found 2026-11-18: used right after the reload)
        check(page.evaluate(SWITCHES)["errorBanner"] is False, f"a contributor's off should stay off: {page.evaluate(SWITCHES)}")
        plant_error(app, "an error after turning off")
        page.wait_for_timeout(800)   # timed on purpose: proves no bar appears — a window from the error being logged
        check(page.locator(BANNER).count() == 0, "a bar appeared with the switch turned off")
        leave_in_no_folder(app, ["Good Omens"])
        wait_bar(app, ONE)
        check(bar_buttons(app) == ["Copy", "Report this problem", "Dismiss"],
              f"the no-folder bar shows anyway, without the switch's link: {bar_buttons(app)}")
        check(bar_message(app) == ONE, f"the bar turned off: just the message, as an ordinary user sees it: {bar_message(app)!r}")
        dismiss(app)
    test("NOFOLDER-008", "a contributor who turned the switch off: off (after a reload too) — the no-folder bar still shows",
         contributor_turned_off)

done()
