# Screen test: F2 renames the folder you SELECTED in the right pane — wherever you are: a folder, the Inbox, or the
# Folders view.
# tags: rename, folders, undo, keyboard, tier 2
# covers: readerwrangler.js
# Run: py tools/run_tests.py --id RENAME-001     (or --tier 2; or directly with the venv's Python)
#
# Bug (one of the three harmful cells found while building the Delete key — TODO "One table for every move, copy, paste
# and delete", ONE-TABLE.md §7 alpha.13): F2 on a folder selected in the right pane while the Folders view was open did
# nothing. F2 looked up the place you're in first, and the Folders view isn't a folder, so it gave up before its "rename
# the selected folder" step. Decided: F2 renames what's selected, the same rule as the Delete key — a folder selected in
# the right pane is renamed wherever you are. The other cases are kept as they were (RENAME-003–005 guard them).
# Real keys and real clicks throughout; every rename is undone with one Ctrl+Z and checked back.
# The fixture (test/fixtures/make-small-fixture.js): Science Fiction (3 books, Good Omens among them) ⊃ Space Opera ⊃
# Old Favorites; Fantasy ⊃ The Test Saga; Every Ownership Kind; An Empty Folder; the Inbox (2 books).
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import FIXTURE, App              # noqa: E402

IDS = {"Science Fiction": "f-scifi", "Space Opera": "f-space", "An Empty Folder": "f-empty", "Inbox": "__inbox__"}


def name_of(app, fid):
    return app.page.evaluate("id => (window.folders.find(f => f.id === id) || {}).name || null", fid)


def open_left(app, name):
    """Click a folder in the left pane — it opens there. (The Inbox's entry carries no folder id: found by its name.)"""
    app.page.mouse.move(900, 600)
    target = (app.page.locator("[data-left-pane]").get_by_text("Inbox", exact=True) if name == "Inbox"
              else app.page.locator(f'[data-folder-id="{IDS[name]}"]'))
    app.click_reachable(target.first)
    # Open when its left-pane entry shows it (bg-blue-100), as test_cells.py's go() waits
    app.page.wait_for_function("el => !!el.closest('.bg-blue-100')", arg=target.first.element_handle(), timeout=3000)
    app.page.wait_for_timeout(100)


def open_folders_view(app):
    app.page.mouse.move(900, 600)
    app.click_reachable(app.page.locator("[data-left-pane] span.cursor-pointer", has_text=re.compile(r"^Folders$")).first)
    app.page.locator("tbody tr", has_text="An Empty Folder").first.wait_for(timeout=3000)
    app.page.wait_for_timeout(100)


def select(app, name):
    """Click the row in the right pane — the right pane has your focus."""
    app.page.locator("tbody tr", has_text=name).first.click()
    app.page.wait_for_function("() => document.querySelectorAll('tbody tr.bg-blue-50').length === 1", timeout=3000)
    app.page.wait_for_timeout(50)


def press_f2(app):
    app.page.keyboard.press("F2")
    app.page.wait_for_timeout(300)


def right_box(app):
    """The right pane's rename box (a text box in a row), or None."""
    box = app.page.locator("tbody tr input[type=text]")
    return box.first if box.count() else None


def left_box(app):
    """The left pane's rename box, or None."""
    box = app.page.locator("[data-left-pane] input[type=text][class*='border-blue']")
    return box.first if box.count() else None


def toast(app):
    """The toast's words — waiting (up to 3 s) for one to be on screen (TESTING.md §7)."""
    t = app.page.locator(".clipboard-toast")
    try:
        t.first.wait_for(state="visible", timeout=3000)
    except Exception:   # noqa: BLE001 — no toast is an answer too ("")
        return ""
    return t.first.inner_text()


def undo(app):
    app.page.keyboard.press("Control+z")
    app.page.wait_for_timeout(600)


def calm(app):
    """Between rows: close any rename box (Esc leaves the name as it was), clear the selection (Esc)."""
    app.page.keyboard.press("Escape")
    app.page.wait_for_timeout(150)
    app.page.keyboard.press("Escape")
    app.page.wait_for_timeout(150)


with App() as app:
    app.restore(FIXTURE)
    app.menu("View", "List View").click()

    def rename_selected(where, folder, new_name):
        """Select `folder` in the right pane, F2 → its rename box, type a name, Enter → renamed; one Ctrl+Z → back."""
        fid = IDS[folder]
        try:
            check(name_of(app, fid) == folder, f"setup: {folder!r} isn't named so: {name_of(app, fid)!r}")
            where()
            select(app, folder)
            press_f2(app)
            box = right_box(app)
            check(box is not None, f"F2 on {folder!r} selected in the right pane opened no rename box")
            check(box.input_value() == folder, f"the rename box should hold {folder!r}: {box.input_value()!r}")
            check(left_box(app) is None, "F2 opened a rename box in the left pane too")
            app.page.keyboard.press("Control+a")
            app.page.keyboard.type(new_name)
            app.page.keyboard.press("Enter")
            app.page.wait_for_timeout(400)
            check(name_of(app, fid) == new_name, f"Enter didn't rename it: {name_of(app, fid)!r}")
            said = toast(app)
            check(f"Renamed folder '{folder}' to '{new_name}'" in said, f"the receipt: {said!r}")
            undo(app)
            check(name_of(app, fid) == folder, f"one Ctrl+Z should give it back its name: {name_of(app, fid)!r}")
        finally:
            calm(app)
            if name_of(app, fid) != folder:
                undo(app)

    test("RENAME-001", "the Folders view, a folder selected in the right pane, F2: its rename box opens; a new name + "
         "Enter renames it; one Ctrl+Z gives the old name back (was: F2 did nothing)",
         lambda: rename_selected(lambda: open_folders_view(app), "An Empty Folder", "A Renamed Folder"))

    test("RENAME-002", "inside a folder, a subfolder selected in the right pane, F2: the SUBFOLDER's rename box (not the "
         "folder you're in); renamed; one Ctrl+Z (a guard: it worked before)",
         lambda: rename_selected(lambda: open_left(app, "Science Fiction"), "Space Opera", "Space Westerns"))

    def book_selected():
        try:
            open_left(app, "Science Fiction")
            select(app, "Good Omens")
            press_f2(app)
            check(right_box(app) is None, "F2 with a book selected opened a rename box in the right pane")
            box = left_box(app)
            check(box is not None and box.input_value() == "Science Fiction",
                  "F2 with a book selected: the left pane's rename box for the folder you're in, as before — "
                  f"got {box.input_value() if box else None!r}")
        finally:
            calm(app)
            check(name_of(app, "f-scifi") == "Science Fiction", "Esc should leave the name as it was")
    test("RENAME-003", "a book selected, F2: the left pane's rename box for the folder you're in — kept as it was",
         book_selected)

    def nothing_selected():
        try:
            open_left(app, "Science Fiction")
            app.page.mouse.click(900, 600)        # the right pane's empty area: nothing selected, your focus there
            app.page.wait_for_timeout(200)
            press_f2(app)
            box = left_box(app)
            check(box is not None and box.input_value() == "Science Fiction",
                  "F2 with nothing selected: the left pane's rename box for the folder you're in, as before — "
                  f"got {box.input_value() if box else None!r}")
        finally:
            calm(app)
    test("RENAME-004", "nothing selected (focus in the right pane), F2: the left pane's rename box for the folder you're "
         "in — kept as it was", nothing_selected)

    def the_inbox():
        try:
            open_folders_view(app)
            select(app, "Inbox")
            press_f2(app)
            check(right_box(app) is None and left_box(app) is None, "F2 on the selected Inbox opened a rename box")
            calm(app)
            open_left(app, "Inbox")
            press_f2(app)
            check(right_box(app) is None and left_box(app) is None, "F2 in the Inbox opened a rename box")
            check(name_of(app, "__inbox__") == "Inbox", f"the Inbox's name changed: {name_of(app, '__inbox__')!r}")
        finally:
            calm(app)
    test("RENAME-005", "the Inbox can't be renamed: F2 on it selected (the Folders view), or with it open, opens no "
         "rename box — kept as it was", the_inbox)

    test("RENAME-006", "no unexpected console messages",
         lambda: check(not app.unexpected_console(), app.unexpected_console()))

done()
