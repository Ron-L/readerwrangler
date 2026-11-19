# Screen test: the Reset App box hands you the backup — a Save Backup… button where it says to save one.
# tags: reset, backup, dialogs, tier 2
# covers: readerwrangler.js
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
#
# TODO "Reset App: a Save Backup… button where the box says to save a backup" (id 20261111-1104; Law 20 — hand them
# the action, not directions). Decided (Ron + Claude, 2026-11-11): the button runs the same save File → Save Backup runs,
# and the box stays open so they can then reset or cancel. A save that's cancelled or fails leaves the box open and
# resets nothing. ("To get everything back afterwards: File → Restore Backup…" stays as directions — test_reset_words.py.)
#
# The save's file picker is the computer's own window, which the driver can't answer — so each test puts a stand-in in
# its place (window.showSaveFilePicker, the one the app calls): it hands back a file that keeps what's written to it, or
# answers "cancelled" as a person closing the picker does, or a file that refuses to be written.
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import APP_TIMEOUT_MS, FIXTURE, LIMIT_MS, App   # noqa: E402

LIMIT_S = APP_TIMEOUT_MS // 1000   # every wait here is for a condition, under the driver's own generous limit (TESTING.md §3)
TIP = "Before you reset, save a backup"
CLEARED = r"info · STORE · Reset App: the library was cleared"    # readerwrangler.js confirmReset's last line
PICKER = """(mode) => {
    window._savedBackups = window._savedBackups || [];
    window.showSaveFilePicker = async (opts) => {
        if (mode === 'cancel') throw new DOMException('The user aborted a request.', 'AbortError');
        return { name: opts.suggestedName, createWritable: async () => {
            if (mode === 'fail') throw new Error('the disk refused the file (screen test)');
            const parts = [];
            return { write: async (b) => { parts.push(b); },
                     close: async () => { window._savedBackups.push(await new Blob(parts).text()); } };
        } };
    };
}"""


def since(app, n0, pattern):
    return [x for _, x in app.console[n0:] if re.search(pattern, x)]


with App() as app:
    page = app.page
    app.restore(FIXTURE)
    all_books = app.left_count("All Books")
    stored = page.evaluate("() => loadBooksFromIndexedDB().then(b => b.length)")

    def reset_box():
        return page.locator('[role="dialog"]', has=page.locator("#modal-reset-confirm"))

    def open_reset_box():
        app.menu("Tools", "Reset App").click()
        reset_box().wait_for(timeout=LIMIT_MS)

    def save_button():
        return reset_box().get_by_role("button", name="Save Backup…", exact=True)

    def nothing_reset(what):
        check(page.get_by_text("Welcome to ReaderWrangler").count() == 0, f"{what}: the app was reset")
        check(app.left_count("All Books") == all_books,
              f"{what}: All Books shows {app.left_count('All Books')}, was {all_books}")

    def button_in_the_tip():
        open_reset_box()
        check(save_button().count() == 1, "the Reset App box has no Save Backup… button")
        tip = reset_box().locator("div", has_text=TIP).last
        check(tip.get_by_role("button", name="Save Backup…", exact=True).count() == 1,
              "the Save Backup… button isn't in the tip that says to save a backup")
        check(save_button().is_enabled(), "the Save Backup… button is greyed out with books in the library")
        app.hover(save_button())   # refuses a covered or zero-size button
    test("RSAVE-001", "the Reset App box has a Save Backup… button in its tip, where a person can reach it",
         button_in_the_tip)

    def save_runs_box_stays():
        page.evaluate(PICKER, "save")
        n0 = len(app.console)
        app.click_reachable(save_button())
        # the receipt is the save's last step — logged after the file is closed and the progress box removed
        # (readerwrangler.js, the backup save), so both are final when it arrives (before: then a 0.3 s sleep)
        app.wait_console(r"^info · BACKUP · Backup saved — ", timeout_s=LIMIT_S)
        saved = page.evaluate("() => window._savedBackups")
        check(len(saved) == 1, f"{len(saved)} backup file(s) written, should be 1")
        backup = json.loads(saved[0])
        check(backup.get("isBackup") is True, "the file written isn't a backup")
        check(len(backup["books"]["items"]) == stored,
              f"the backup holds {len(backup['books']['items'])} books, the library {stored}")
        check(len(backup["organization"]["folders"]) > 1, "the backup holds no folders")
        check(since(app, n0, r"^info · BACKUP · Backup saved — .* → readerwrangler-backup-"), "no receipt naming the file")
        check(reset_box().is_visible(), "the Reset App box closed after the save")
        check(page.locator(".rw-imperative-overlay").count() == 0, "the save's progress box is still up")
        nothing_reset("after the save")
    test("RSAVE-002", "Save Backup… runs File → Save Backup's save (the whole library, the receipt) and the box stays open",
         save_runs_box_stays)

    def esc_still_closes():
        check(reset_box().is_visible(), "the Reset App box isn't open to close")   # the setup, before the outcome
        page.keyboard.press("Escape")
        reset_box().wait_for(state="detached", timeout=LIMIT_MS)
        nothing_reset("Esc after the save")
    test("RSAVE-003", "after the save, Esc still closes the Reset App box — and resets nothing", esc_still_closes)

    def cancelled_save():
        open_reset_box()
        page.evaluate(PICKER, "cancel")
        before = page.evaluate("() => window._savedBackups.length")
        n0 = len(app.console)
        app.click_reachable(save_button())
        # the save stops right there: the cancel's line is its last step (before: then a 0.3 s sleep)
        app.wait_console(r"^info · BACKUP · Backup cancelled — nothing saved", timeout_s=LIMIT_S)
        check(page.evaluate("() => window._savedBackups.length") == before, "a file was written though the save was cancelled")
        check(not since(app, n0, r"Backup saved"), "a receipt says saved")
        check(reset_box().is_visible(), "the Reset App box closed when the save was cancelled")
        nothing_reset("a cancelled save")
    test("RSAVE-004", "a cancelled save leaves the Reset App box open and resets nothing", cancelled_save)

    def failed_save():
        app.expect("BACKUP-05")   # caused on purpose: the stand-in file refuses to be written
        page.evaluate(PICKER, "fail")
        app.click_reachable(save_button())
        # 7.29.0-alpha.2: the box said "Export Error — Failed to export library." (the retired word for backups)
        page.get_by_text("Backup Error", exact=True).wait_for(timeout=LIMIT_MS)
        error_text = page.locator(".rw-imperative-overlay").inner_text()
        check("Failed to save the backup." in error_text and "xport" not in error_text,
              f"the failure box doesn't say the backup wasn't saved, or still says Export: {error_text!r}")
        error_box = page.locator(".rw-imperative-overlay")
        error_box.get_by_role("button", name="OK", exact=True).click()
        error_box.wait_for(state="detached", timeout=LIMIT_MS)
        check(reset_box().is_visible(), "the Reset App box closed when the save failed")
        nothing_reset("a failed save")
    test("RSAVE-005", "a failed save says so above the box; closing that leaves the Reset App box open, nothing reset",
         failed_save)

    def cancel_closes():
        reset_box().get_by_role("button", name="Cancel", exact=True).click()
        reset_box().wait_for(state="detached", timeout=LIMIT_MS)
        page.wait_for_timeout(300)   # timed on purpose: proves Cancel resets nothing — a window from the box's closing
        nothing_reset("Cancel")
    test("RSAVE-006", "Cancel still closes the Reset App box without resetting", cancel_closes)

    def save_then_reset():
        open_reset_box()
        page.evaluate(PICKER, "save")
        before = page.evaluate("() => window._savedBackups.length")
        app.click_reachable(save_button())
        page.wait_for_function(f"() => window._savedBackups.length > {before}", timeout=LIMIT_MS)
        page.locator(".rw-imperative-overlay").wait_for(state="detached", timeout=LIMIT_MS)
        n0 = len(app.console)
        app.click_reachable(reset_box().get_by_role("button", name="Reset App", exact=True))
        page.get_by_text("Welcome to ReaderWrangler").wait_for(timeout=LIMIT_S * 1000)
        app.wait_console(CLEARED, LIMIT_S, since=n0)     # the reset ran to its end (RSAVE-008 starts from it)
    test("RSAVE-007", "after saving, Reset App in the same box resets the app", save_then_reset)

    def empty_library():
        # (before: a 0.5 s sleep — RSAVE-007 now waits for the reset's own last line)
        open_reset_box()
        check(save_button().count() == 1, "the button is gone with an empty library (it should stay, greyed out)")
        check(save_button().is_disabled(), "Save Backup… isn't greyed out with nothing to save (File → Save Backup is)")
        check(save_button().get_attribute("title"), "the greyed-out button doesn't say why")
        reset_box().get_by_role("button", name="Cancel", exact=True).click()
        reset_box().wait_for(state="detached", timeout=LIMIT_MS)
    test("RSAVE-008", "with an empty library the button stays in place, greyed out, saying why (as File → Save Backup)",
         empty_library)

    # RSAVE-005 makes a save fail ON PURPOSE, so its BACKUP-05 line is expected here.
    test("RSAVE-009", "no unexpected console messages (RSAVE-005's deliberate BACKUP-05 excepted)",
         lambda: check(not [x for x in app.unexpected_console() if "BACKUP-05" not in x],
                       [x for x in app.unexpected_console() if "BACKUP-05" not in x]))

done()
