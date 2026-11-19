# Screen test: the Delete key acts on what you SELECTED — never on the folder you happen to be in.
# tags: delete, folders, undo, keyboard, tier 2
# covers: readerwrangler.js, gestureTable.js
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
#
# TODO "The Delete key deletes the folder you're in — not the folders you selected" (id 20261014-1030ay), and the Delete
# rows of "the one table" (docs/design/ONE-TABLE.md §3). Until 7.28.1, Delete with no BOOKS selected deleted the folder you
# were INSIDE, whatever folders you had selected — and an empty one went with no question; in the Folders view it did
# nothing at all. Decided (Ron + UX, 2026-10-22): selected books; else the folders selected in the right pane; else — only
# when the left pane has your focus — the folder highlighted there; with nothing selected, nothing. Several folders: one
# confirmation listing them, one undo for the lot. The key and the right-click Delete use one operation.
# 7.28.1-alpha.2 (Ron, 2026-11-12, review queue Q-013): books AND folders selected → Delete takes both, in one confirmation
# and one undo, as File Explorer does (was: the books only) — DELKEY-009, 012–015.
# Real keys and real clicks throughout; every row that deletes is undone with Ctrl+Z and checked back.
# The fixture (test/fixtures/make-small-fixture.js): Science Fiction (3 books) ⊃ Space Opera (no books) ⊃ Old Favorites
# (2 books); Fantasy ⊃ The Test Saga; Every Ownership Kind; An Empty Folder; the Inbox (2 books).
# Waits (2026-11-18, sprint 8 — TESTING.md §3 "A test waits for a condition, never a moment"): every step waits for what
# it should have done — the folder opened, the rows selected, the box up or closed, the folder gone or back, the toast's
# words — under the library's one limit (rw.LIMIT_MS), which only a real failure reaches; through the shared waits
# (app.until, app.toast — rw.py, since sprint 9: they were this file's own). The few that prove NOTHING happens wait a
# fixed time on purpose, marked "timed on purpose". (Was: 14 fixed sleeps, ~6 s of them a run.)
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test      # noqa: E402
from rw import FIXTURE, LIMIT_MS, App       # noqa: E402

IDS = {"Science Fiction": "f-scifi", "Space Opera": "f-space", "Every Ownership Kind": "f-kinds",
       "An Empty Folder": "f-empty", "Fantasy": "f-fantasy"}


def exists(app, name):
    """Is the folder still in the left pane's tree? (Space Opera shows there: its parent is expanded.)"""
    return app.page.locator(f'[data-folder-id="{IDS[name]}"]').count() > 0


def opened(app, target):
    """Wait until the left pane shows `target` (its entry, a locator) as the place you're in — bg-blue-100, the same render
    that fills the right pane (as test_cells.py's go() waits)."""
    target.wait_for(state="attached")
    app.page.wait_for_function("el => !!el.closest('.bg-blue-100')", arg=target.element_handle(), timeout=LIMIT_MS)


def open_left(app, name):
    """Click a folder in the left pane — it opens there, and the left pane has your focus. (The pointer parked off the
    left pane first, as test_cells.py's go() does: a hovered subfolder row shows its buttons and can shift the rows.)"""
    app.page.mouse.move(900, 600)
    target = app.page.locator(f'[data-folder-id="{IDS[name]}"]').first
    app.click_reachable(target)
    opened(app, target)


def open_folders_view(app):
    """Click Folders in the left pane; open when it shows so (text-blue-600 — the same render that fills the right pane)."""
    target = app.page.locator("span.cursor-pointer", has_text=re.compile(r"^Folders$")).first
    app.click_reachable(target)
    app.page.wait_for_function("el => el.classList.contains('text-blue-600')", arg=target.element_handle(),
                               timeout=LIMIT_MS)


def select(app, *names):
    """Click the first row in the right pane, Ctrl+click the rest — the right pane has your focus. Waits until the screen
    shows exactly those rows selected (the keys read the selection through refs set in that same render)."""
    for i, n in enumerate(names):
        row = app.page.locator("tbody tr", has_text=n).first
        row.click(modifiers=["Control"] if i else None)
    app.page.wait_for_function("""names => {
        const rows = [...document.querySelectorAll('tbody tr.bg-blue-50')].map(r => r.innerText);
        return rows.length === names.length && names.every(n => rows.some(r => r.includes(n)));
    }""", arg=list(names), timeout=LIMIT_MS)


def press_delete(app):
    """The Delete key. The caller waits for what it should do (a box, a folder gone, a toast) — or, where it should do
    nothing, waits a fixed time on purpose."""
    app.page.keyboard.press("Delete")


def box(app):
    """The confirmation's words, or None when no box is up."""
    ov = app.page.locator(".rw-imperative-overlay")
    return ov.first.inner_text() if ov.count() else None


def ask(app):
    """The confirmation's words once it's up — waiting for it (LIMIT_MS) — or None if none came."""
    app.until(lambda: box(app) is not None)
    return box(app)


def answer(app, label):
    """Click a button of the box, and wait until that box has closed."""
    button = app.page.locator(".rw-imperative-overlay").get_by_role("button", name=label, exact=True)
    handle = button.element_handle(timeout=LIMIT_MS)
    button.click()
    handle.wait_for_element_state("hidden", timeout=LIMIT_MS)


def undo(app, back):
    """Ctrl+Z, then wait until back() — what the undo should have put back (the check after it says if it didn't)."""
    app.page.keyboard.press("Control+z")
    app.until(back)


def redo(app, done_again):
    """Ctrl+Y, then wait until done_again() — what the redo should have done again."""
    app.page.keyboard.press("Control+y")
    app.until(done_again)


def right_rows(app):
    rows = app.page.locator("tbody tr")
    return [rows.nth(i).inner_text() for i in range(rows.count())]


def state(app):
    """The library's exact state, read from the app (window.folders / window.books): each folder's books in order, its
    parent, the folders' order, and which books are in the Trash or hidden — for "back exactly as it was" checks."""
    return app.page.evaluate("""() => ({
        order: window.folders.map(f => f.id),
        folders: Object.fromEntries(window.folders.map(f => [f.id, { parent: f.parentId || null, books: [...(f.bookIds || [])] }])),
        trashed: window.books.filter(b => b.isDeleted).map(b => b.id).sort(),
        hidden: window.books.filter(b => b.isHidden).map(b => b.id).sort(),
    })""")


def differences(a, b):
    """What differs between two state() readings, in words (empty = the same)."""
    out = []
    for k in ("order", "trashed", "hidden"):
        if a[k] != b[k]:
            out.append(f"{k}: {a[k]} → {b[k]}")
    for fid in sorted(set(a["folders"]) | set(b["folders"])):
        if a["folders"].get(fid) != b["folders"].get(fid):
            out.append(f"{fid}: {a['folders'].get(fid)} → {b['folders'].get(fid)}")
    return out


def both_gone(s):
    """In a state() reading: the books-and-folders delete has landed — Space Opera gone, Good Omens out of Science
    Fiction (DELKEY-013, 017, 018). (window.folders follows the screen a moment later: read it, don't assume it.)"""
    return "f-space" not in s["folders"] and "TST0000005" not in s["folders"]["f-scifi"]["books"]


def omens_out_favorites_in(rows):
    """The right pane's rows after DELKEY-009's delete: Good Omens gone, Old Favorites' books arrived."""
    return not any("Good Omens" in r for r in rows) and any("Deep in the Folders" in r for r in rows)


def answer_landed(s):
    """In a state() reading: DELKEY-014/015's answer is in — Space Opera gone, the book trashed or hidden."""
    return "f-space" not in s["folders"] and "TST0000018" in s["trashed"] + s["hidden"]


def nothing_selected_now(app):
    return app.page.locator("tbody tr.bg-blue-50").count() == 0


def calm(app):
    """Between rows: close any box, clear the selection (Esc) — waiting until nothing is selected."""
    if box(app):
        answer(app, "Cancel")
    app.page.keyboard.press("Escape")
    app.until(lambda: nothing_selected_now(app))
    # (No waiting for the last toast to run its course, on purpose: until 7.28.1 an older toast's timers hid a NEWER toast
    # early — an Undo, then a Delete a second later, and the Delete's receipt vanished. DELKEY-011 caught it.)


ALL = ["Science Fiction", "Space Opera", "Every Ownership Kind", "An Empty Folder", "Fantasy"]

with App() as app:
    app.page.set_default_timeout(LIMIT_MS)      # every Playwright wait and action here too (its own is 30 s)
    app.restore(FIXTURE)
    app.menu("View", "List View").click()

    def baseline():
        app.until(lambda: all(exists(app, n) for n in ALL))
        check(all(exists(app, n) for n in ALL), f"setup: a folder is missing before the row: "
                                                f"{[n for n in ALL if not exists(app, n)]}")

    def one_subfolder():
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Space Opera")
            press_delete(app)
            words = ask(app)
            check(words is not None, "no confirmation came up for a folder with a subfolder and books")
            check('Delete "Space Opera"' in words and 'Delete "Science Fiction"' not in words,
                  f"the confirmation should name the SELECTED folder, Space Opera — it said: {words!r}")
            answer(app, "Delete")
            app.until(lambda: not exists(app, "Space Opera"))
            check(not exists(app, "Space Opera"), "Space Opera is still there after Delete")
            check(exists(app, "Science Fiction"), "Science Fiction — the folder you were in — was deleted")
            app.until(lambda: any("Deep in the Folders" in r for r in right_rows(app)))
            rows = right_rows(app)
            check(any("Deep in the Folders" in r for r in rows),
                  "Old Favorites' books should have returned to Science Fiction (the folder you're in)")
            undo(app, lambda: exists(app, "Space Opera"))
            check(exists(app, "Space Opera"), "Ctrl+Z didn't bring Space Opera back")
        finally:
            calm(app)
    test("DELKEY-001", "one subfolder selected in the right pane: the confirmation names IT (not the folder you're in); "
         "Delete removes only it, its books return to the folder you're in; Ctrl+Z brings it back", one_subfolder)

    def nothing_selected():
        try:
            baseline()
            open_left(app, "An Empty Folder")
            app.page.mouse.click(900, 600)        # a click in the right pane's empty area: your focus is there now
            app.until(lambda: nothing_selected_now(app))
            press_delete(app)
            app.page.wait_for_timeout(500)        # timed on purpose: proves NOTHING happens after the key (no box, no delete)
            check(box(app) is None, f"a box came up with nothing selected: {box(app)!r}")
            check(exists(app, "An Empty Folder"),
                  "the empty folder you were IN was deleted with no question — nothing was selected")
        finally:
            if not exists(app, "An Empty Folder"):
                undo(app, lambda: exists(app, "An Empty Folder"))
            calm(app)
    test("DELKEY-002", "nothing selected, focus in the right pane: Delete does nothing — not even to the empty folder "
         "you're in (was: deleted with no question)", nothing_selected)

    def left_focus():
        try:
            baseline()
            open_left(app, "An Empty Folder")      # the left pane has your focus; the folder is highlighted there
            press_delete(app)
            app.until(lambda: not exists(app, "An Empty Folder") or box(app) is not None)   # gone — or a box asks
            check(box(app) is None, f"an empty folder asks nothing (nothing to lose; Ctrl+Z): {box(app)!r}")
            check(not exists(app, "An Empty Folder"), "Delete with the left pane's focus didn't delete its folder")
            said = app.toast('Deleted "An Empty Folder"')
            check('Deleted "An Empty Folder"' in said, f"the receipt: {said!r}")
            undo(app, lambda: exists(app, "An Empty Folder"))
            check(exists(app, "An Empty Folder"), "Ctrl+Z didn't bring it back")
        finally:
            if not exists(app, "An Empty Folder"):
                undo(app, lambda: exists(app, "An Empty Folder"))
            calm(app)
    test("DELKEY-003", "the left pane has your focus: Delete deletes the folder highlighted there (an empty one with no "
         "question, and says so); Ctrl+Z brings it back", left_focus)

    def both_back():
        """Every Ownership Kind and An Empty Folder both there (DELKEY-004, 007)."""
        return exists(app, "Every Ownership Kind") and exists(app, "An Empty Folder")

    def several():
        try:
            baseline()
            open_folders_view(app)
            select(app, "Every Ownership Kind", "An Empty Folder")
            press_delete(app)
            words = ask(app)
            check(words is not None, "no confirmation for several folders (in the Folders view Delete did nothing)")
            check("Every Ownership Kind" in words and "An Empty Folder" in words,
                  f"the confirmation should list both folders: {words!r}")
            answer(app, "Delete")
            app.until(lambda: not exists(app, "Every Ownership Kind") and not exists(app, "An Empty Folder"))
            check(not exists(app, "Every Ownership Kind") and not exists(app, "An Empty Folder"),
                  "both folders should be gone")
            check(exists(app, "Fantasy") and exists(app, "Science Fiction"), "an unselected folder went too")
            undo(app, both_back)                   # ONE Ctrl+Z for the lot
            check(exists(app, "Every Ownership Kind") and exists(app, "An Empty Folder"),
                  "one Ctrl+Z should bring BOTH folders back")
        finally:
            for _ in range(2):
                if not both_back():
                    undo(app, both_back)
            calm(app)
    test("DELKEY-004", "several folders selected (the Folders view): one confirmation listing them, Delete removes them "
         "all, one Ctrl+Z brings them all back", several)

    def cancel():
        try:
            baseline()
            open_folders_view(app)
            select(app, "Every Ownership Kind", "An Empty Folder")
            press_delete(app)
            check(ask(app) is not None, "no confirmation came up")
            answer(app, "Cancel")
            app.page.wait_for_timeout(500)         # timed on purpose: proves NOTHING is deleted once Cancel closed the box
            check(all(exists(app, n) for n in ALL), "Cancel still deleted something")
        finally:
            calm(app)
    test("DELKEY-005", "Cancel at the confirmation changes nothing", cancel)

    def inbox():
        try:
            baseline()
            open_folders_view(app)
            select(app, "Inbox")
            press_delete(app)
            said = app.toast("The Inbox can't be deleted")    # (the key's answer: the toast — or, wrongly, a box)
            check(box(app) is None, f"a box came up for the Inbox: {box(app)!r}")
            check("The Inbox can't be deleted" in said, f"the Inbox alone: the toast should say why — {said!r}")
            calm(app)
            select(app, "Inbox", "An Empty Folder")
            press_delete(app)
            app.until(lambda: not exists(app, "An Empty Folder") or box(app) is not None)
            check(not exists(app, "An Empty Folder"), "the folder selected with the Inbox wasn't deleted")
            check(any("Inbox" in r for r in right_rows(app)), "the Inbox is gone from the Folders view")
            said = app.toast("The Inbox stays")
            check("The Inbox stays" in said, f"the receipt should say the Inbox stays: {said!r}")
            undo(app, lambda: exists(app, "An Empty Folder"))
            check(exists(app, "An Empty Folder"), "Ctrl+Z didn't bring it back")
        finally:
            if not exists(app, "An Empty Folder"):
                undo(app, lambda: exists(app, "An Empty Folder"))
            calm(app)
    test("DELKEY-006", "the Inbox is never deleted: alone, Delete says why; with a folder, the folder goes and the "
         "receipt says the Inbox stays", inbox)

    def menu_delete():
        try:
            baseline()
            open_folders_view(app)
            select(app, "Every Ownership Kind", "An Empty Folder")
            app.page.locator("tbody tr", has_text="An Empty Folder").first.click(button="right")
            item = app.page.get_by_role("menuitem", name=re.compile(r"Delete Folder"))
            item.first.wait_for(timeout=LIMIT_MS)
            label = item.first.inner_text()
            check("(2)" in label, f"the menu item should say it acts on the 2 selected folders: {label!r}")
            item.first.click()
            words = ask(app)
            check(words and "Every Ownership Kind" in words and "An Empty Folder" in words,
                  f"the menu's Delete should ask about BOTH selected folders, as the key does: {words!r}")
            answer(app, "Delete")
            app.until(lambda: not exists(app, "Every Ownership Kind") and not exists(app, "An Empty Folder"))
            check(not exists(app, "Every Ownership Kind") and not exists(app, "An Empty Folder"), "not both deleted")
            undo(app, both_back)
            check(exists(app, "Every Ownership Kind") and exists(app, "An Empty Folder"), "one Ctrl+Z, both back")
        finally:
            for _ in range(2):
                if not both_back():
                    undo(app, both_back)
            calm(app)
    test("DELKEY-007", "the right-click Delete on one of several selected folders acts on all of them, through the same "
         "confirmation as the key (one operation for every way in)", menu_delete)

    def restore_variant():
        """A variant of the fixture where "A Book With No Description" (TST0000018) is in Space Opera too — it is already
        in Science Fiction, Space Opera's parent. (Restored from a file: a copy-paste would also trip the second keyboard
        handler's folder clipboard — TODO "One table…", the survey's 2026-11-06 finding.)"""
        data = json.load(open(FIXTURE, encoding="utf-8"))
        space = next(f for f in data["organization"]["folders"] if f["id"] == "f-space")
        space["bookIds"] = ["TST0000018"]
        folder = tempfile.mkdtemp(prefix="rw-delkey-")
        variant = os.path.join(folder, "delkey-variant.json")
        with open(variant, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        try:
            app.restore(variant)
        finally:
            shutil.rmtree(folder, ignore_errors=True)
        app.menu("View", "List View").click()

    def undo_keeps_parent_books():
        try:
            restore_variant()
            baseline()
            open_left(app, "Space Opera")
            app.until(lambda: any("A Book With No Description" in r for r in right_rows(app)))
            check(any("A Book With No Description" in r for r in right_rows(app)), "setup: the book in Space Opera")
            open_left(app, "Science Fiction")
            app.until(lambda: any("A Book With No Description" in r for r in right_rows(app)))
            check(any("A Book With No Description" in r for r in right_rows(app)), "setup: the book in Science Fiction")
            select(app, "Space Opera")
            press_delete(app)
            ask(app)
            answer(app, "Delete")
            app.until(lambda: not exists(app, "Space Opera"))    # deleted — before the Ctrl+Z that takes it back
            undo(app, lambda: exists(app, "Space Opera"))
            check(exists(app, "Space Opera"), "Ctrl+Z didn't bring Space Opera back")
            open_left(app, "Science Fiction")
            app.until(lambda: any("A Book With No Description" in r for r in right_rows(app)))
            check(any("A Book With No Description" in r for r in right_rows(app)),
                  "after Ctrl+Z the book left Science Fiction — it was there BEFORE the delete (the undo took out every "
                  "book the deleted folder held, not just the ones the delete had added)")
        finally:
            calm(app)
            app.restore(FIXTURE)                   # back to the plain fixture for the rows after
            app.menu("View", "List View").click()
    test("DELKEY-008", "Ctrl+Z after deleting a subfolder leaves the folder you're in as it was — a book that was in "
         "both stays", undo_keeps_parent_books)

    def back_to_fixture(before):
        """After a books-and-folders row: if anything is left changed, restore the plain fixture for the rows after."""
        calm(app)
        if differences(before, state(app)):
            app.restore(FIXTURE)
            app.menu("View", "List View").click()

    # "Good Omens" (TST0000005) is in Fantasy too, so leaving Science Fiction isn't its last folder (no Trash, no
    # owned-book question). Space Opera holds a subfolder (Old Favorites, 2 books).
    def books_and_folders():
        before = state(app)
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Space Opera", "Good Omens")
            press_delete(app)
            words = ask(app)
            check(words is not None, "no confirmation came up — with books AND folders selected, Delete should ask once, "
                                     "naming both (was: the books went, the folder stayed)")
            check("Space Opera" in words and "Good Omens" in words,
                  f"the confirmation should name the folder and the book: {words!r}")
            answer(app, "Delete")
            app.until(lambda: not exists(app, "Space Opera"))
            check(not exists(app, "Space Opera"), "the selected folder is still there after Delete")
            app.until(lambda: omens_out_favorites_in(right_rows(app)))
            rows = right_rows(app)
            check(not any("Good Omens" in r for r in rows), "the selected book didn't leave the folder")
            check(any("Deep in the Folders" in r for r in rows),
                  "Old Favorites' books should have returned to Science Fiction (the folder you're in)")
            said = app.toast("Space Opera", "Good Omens")
            check("Space Opera" in said and "Good Omens" in said, f"the receipt should say both went: {said!r}")
        finally:
            back_to_fixture(before)
    test("DELKEY-009", "books and folders selected in a folder: ONE confirmation naming both, Delete removes both "
         "(the folder's books return to the folder you're in), the receipt says both (was: the books only)",
         books_and_folders)

    def books_and_folders_cancel():
        before = state(app)
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Space Opera", "Good Omens")
            press_delete(app)
            check(ask(app) is not None, "no confirmation came up for books and folders selected together")
            answer(app, "Cancel")
            app.page.wait_for_timeout(500)         # timed on purpose: proves NOTHING changes once Cancel closed the box
            changed = differences(before, state(app))
            check(not changed, f"Cancel changed the library: {changed}")
        finally:
            back_to_fixture(before)
    test("DELKEY-012", "books and folders selected: Cancel at the confirmation changes nothing", books_and_folders_cancel)

    def books_and_folders_undo():
        before = state(app)
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Space Opera", "Good Omens")
            press_delete(app)
            check(ask(app) is not None, "no confirmation came up for books and folders selected together")
            answer(app, "Delete")
            app.until(lambda: both_gone(state(app)))
            after = state(app)
            check("f-space" not in after["folders"] and "f-old" not in after["folders"],
                  "Space Opera and its subfolder should be gone")
            check("TST0000005" not in after["folders"]["f-scifi"]["books"], "Good Omens is still in Science Fiction")
            undo(app, lambda: not differences(before, state(app)))      # ONE Ctrl+Z for the lot
            changed = differences(before, state(app))
            check(not changed, f"one Ctrl+Z should put everything back exactly — still different: {changed}")
            # and Ctrl+Y does it all again — the book leaves THIS folder only
            redo(app, lambda: not differences(after, state(app)))
            redone = differences(after, state(app))
            check(not redone, f"Ctrl+Y should redo the delete exactly as it was done — different: {redone}")
            undo(app, lambda: not differences(before, state(app)))
            changed = differences(before, state(app))
            check(not changed, f"after Ctrl+Y, one more Ctrl+Z should put everything back — still different: {changed}")
        finally:
            back_to_fixture(before)
    test("DELKEY-013", "books and folders deleted: ONE Ctrl+Z puts everything back exactly (the book where it was, the "
         "folders with their books, nothing extra); Ctrl+Y redoes exactly the same", books_and_folders_undo)

    # §6 item 9 (decided 2026-11-13): the right-click Delete with books AND folders selected — one item naming both,
    # "Delete 1 Book and 1 Folder", in the book menu AND the folder menu, through the key's operation (one confirmation,
    # one undo). Was: the book menu's "Delete" took the books only; the folder menu's "Delete Folder" the folder only.
    def menu_delete_both(right_click_on):
        before = state(app)
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Space Opera", "Good Omens")
            app.page.locator("tbody tr", has_text=right_click_on).first.click(button="right")
            menu = app.page.get_by_role("menu", name=re.compile(r"^(Book|Folder) options$"))
            menu.first.wait_for(timeout=LIMIT_MS)
            item = menu.first.get_by_role("menuitem").filter(has_text=re.compile(r"Delete"))
            labels = [item.nth(i).inner_text() for i in range(item.count())]
            check(any("Delete 1 Book and 1 Folder" in x for x in labels),
                  f"the menu should offer ONE Delete naming both — \"Delete 1 Book and 1 Folder\"; its Delete items: {labels!r}")
            both = item.filter(has_text="Delete 1 Book and 1 Folder").first
            check("Del" in both.inner_text().replace("Delete", ""), f"the item should show its key (Del): {both.inner_text()!r}")
            both.click()
            words = ask(app)
            check(words and "Space Opera" in words and "Good Omens" in words,
                  f"the item should ask the key's ONE confirmation, naming both: {words!r}")
            answer(app, "Delete")
            app.until(lambda: both_gone(state(app)))
            after = state(app)
            check("f-space" not in after["folders"], "the selected folder is still there")
            check("TST0000005" not in after["folders"]["f-scifi"]["books"], "the selected book didn't leave Science Fiction")
            undo(app, lambda: not differences(before, state(app)))      # ONE Ctrl+Z for the lot, as the key
            changed = differences(before, state(app))
            check(not changed, f"one Ctrl+Z should put everything back exactly — still different: {changed}")
        finally:
            back_to_fixture(before)
    test("DELKEY-017", "books and folders selected, right-click a BOOK → one item \"Delete 1 Book and 1 Folder\" (with its "
         "key), the key's confirmation naming both, one Ctrl+Z (§6 item 9)", lambda: menu_delete_both("Good Omens"))
    test("DELKEY-018", "the same from the FOLDER's right-click menu: one item naming both, not \"Delete Folder\" (§6 item 9)",
         lambda: menu_delete_both("Space Opera"))

    def book_inside_the_folder(choice):
        try:
            restore_variant()
            baseline()
            before = state(app)
            open_left(app, "Science Fiction")
            select(app, "Space Opera", "A Book With No Description")
            press_delete(app)
            words = ask(app)
            check(words is not None, "no confirmation came up for books and folders selected together")
            check("Space Opera" in words and "A Book With No Description" in words, f"the confirmation: {words!r}")
            check("Amazon library" in words,
                  f"the book goes to the Trash and is owned: the one confirmation should say it comes back from Amazon "
                  f"and offer to hide it instead: {words!r}")
            answer(app, choice)
            app.until(lambda: answer_landed(state(app)))   # which way, and where the book is: checked below
            after = state(app)
            check("f-space" not in after["folders"], "Space Opera is still there")
            in_folders = [fid for fid, f in after["folders"].items() if "TST0000018" in f["books"]]
            if choice == "Delete":
                # The folders go first, then the book: in no other folder now, it goes to the Trash. (Books first, the
                # folder's delete would have put it straight back into Science Fiction.)
                check("TST0000018" in after["trashed"] and not in_folders,
                      f"the book should be in the Trash and in no folder — trashed: {'TST0000018' in after['trashed']}, "
                      f"in folders: {in_folders}")
            else:
                check("TST0000018" in after["hidden"] and "TST0000018" not in after["trashed"] and in_folders == ["f-scifi"],
                      f"Hide Instead: the book should be hidden and stay in Science Fiction — hidden: "
                      f"{'TST0000018' in after['hidden']}, trashed: {'TST0000018' in after['trashed']}, in: {in_folders}")
            undo(app, lambda: not differences(before, state(app)))
            changed = differences(before, state(app))
            check(not changed, f"one Ctrl+Z should put everything back exactly — still different: {changed}")
        finally:
            calm(app)
            app.restore(FIXTURE)                   # back to the plain fixture for the rows after
            app.menu("View", "List View").click()
    test("DELKEY-014", "a selected book that is ALSO inside the selected folder, and in no other folder: the folder goes, "
         "the book goes to the Trash (the one confirmation says it's owned); one Ctrl+Z puts both back exactly",
         lambda: book_inside_the_folder("Delete"))
    test("DELKEY-015", "the same, answered Hide Instead: the folder goes, the owned book is hidden and stays in the folder "
         "you're in; one Ctrl+Z puts both back exactly", lambda: book_inside_the_folder("Hide Instead"))

    def book_redo():
        before = state(app)
        try:
            baseline()
            open_left(app, "Science Fiction")
            select(app, "Good Omens")       # in Fantasy too: Delete takes it out of Science Fiction only
            press_delete(app)
            app.until(lambda: "TST0000005" not in state(app)["folders"]["f-scifi"]["books"])
            after = state(app)
            check("TST0000005" not in after["folders"]["f-scifi"]["books"]
                  and "TST0000005" in after["folders"]["f-fantasy"]["books"],
                  "setup: Delete should take Good Omens out of Science Fiction and leave it in Fantasy")
            undo(app, lambda: "TST0000005" in state(app)["folders"]["f-scifi"]["books"])   # back in Science Fiction
            redo(app, lambda: not differences(after, state(app)))
            redone = differences(after, state(app))
            check(not redone, f"Ctrl+Y should redo the delete exactly as it was done — different: {redone}")
        finally:
            back_to_fixture(before)
    test("DELKEY-016", "a book deleted from one folder, Ctrl+Z, Ctrl+Y: it leaves that folder again — and only that one "
         "(was: Ctrl+Y took it out of every folder)", book_redo)

    def book_list():
        try:
            app.page.mouse.move(900, 600)
            read_next = app.page.get_by_text("Read Next", exact=True).first
            app.click_reachable(read_next)
            opened(app, read_next)
            app.until(lambda: app.page.locator("tbody tr").count() > 0)
            before = right_rows(app)
            check(len(before) > 0, "setup: Read Next has books")
            title = before[0].split("\n")[1] if "\n" in before[0] else before[0]
            app.page.locator("tbody tr").first.click()
            app.page.wait_for_function("() => document.querySelectorAll('tbody tr.bg-blue-50').length === 1")
            press_delete(app)
            app.until(lambda: app.page.locator("tbody tr").count() == len(before) - 1)
            check(len(right_rows(app)) == len(before) - 1, "the book didn't leave the Book List")
            said = app.toast("Removed", "Read Next")
            check("Removed" in said and "Read Next" in said,
                  f"Delete in a Book List should say what it did, as the menu's Remove does: {said!r} "
                  f"(log: {app.console_matching(r' · (MOVE|ORG) · ')[-2:]})")
            undo(app, lambda: app.page.locator("tbody tr").count() == len(before))
            check(len(right_rows(app)) == len(before), f"Ctrl+Z didn't put {title!r} back on the list")
        finally:
            calm(app)
    test("DELKEY-011", "Delete in a Book List takes the book off that list only, says so (was: silent), Ctrl+Z puts it back",
         book_list)

    test("DELKEY-010", "no unexpected console messages",
         lambda: check(not app.unexpected_console(), app.unexpected_console()))

done()
