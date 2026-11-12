# Screen test: Manage Tags — deleting a tag tells you so, on screen, where you can see it.
# tags: tags, toast, logging, tier 2
# covers: readerwrangler.js, logkit/logger.js, logkit-settings.js
# Run: py tools/run_tests.py --tier 2     (or directly with the venv's Python)
#
# 2026-11-10 (the 7.26.0 post-mortem's "bug no test would have caught"): while the toasts were switched to go through
# the log (rwLog.log(…, { toast: true })), the tag-delete receipt lost its { toast: true } in an edit — the log still
# recorded the line, so nothing noticed that the person no longer saw it. These tests delete tags the way a person does
# (Tools → Manage Tags…, the row's trash button, or tick two and the trash button above them) and check the receipt is
# on screen, on top, with its words. The fixture has no tags, so each test makes its own in the dialog's
# "Create new tag..." box (whose receipt is checked too).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import FIXTURE, App              # noqa: E402


def toast_says(app, words):
    """Wait for the toast holding `words`; check a person can see it (a size, not covered — the pointer lands on it)."""
    toast = app.page.locator(".clipboard-toast", has_text=words).first
    try:
        toast.wait_for(state="visible", timeout=5000)
    except Exception:   # noqa: BLE001 — say what WAS on screen
        shown = app.page.locator(".clipboard-toast")
        now = shown.first.inner_text() if shown.count() else "no toast at all"
        raise AssertionError(f"no toast saying {words!r} — on screen: {now!r}")
    app.hover(toast)    # refuses a toast that is covered (e.g. under the dialog) or has no size
    return toast.inner_text()


def create_tag(app, name):
    box = app.page.get_by_placeholder("Create new tag...")
    box.fill(name)
    box.press("Enter")
    toast_says(app, f'Created tag "{name}"')


def confirm(app, title):
    check(app.page.get_by_text(title, exact=True).first.is_visible(), f"the {title!r} box didn't appear")
    app.click_reachable(app.page.get_by_role("button", name="OK", exact=True).first)


def row(app, name):
    return app.page.locator("tr", has_text=name).first


with App() as app:
    page = app.page
    app.restore(FIXTURE)
    page.wait_for_timeout(1000)
    app.click_reachable(app.menu("Tools", "Manage Tags"))
    page.get_by_placeholder("Create new tag...").wait_for(timeout=5000)

    def delete_one():
        create_tag(app, "Delete Me")
        app.click_reachable(row(app, "Delete Me").get_by_title("Delete", exact=True))
        confirm(app, "Delete Tag")
        words = toast_says(app, 'Deleted tag "Delete Me"')
        check(row(app, "Delete Me").count() == 0, f"the tag is still listed after the delete (toast: {words!r})")
    test("TAGS-001", "deleting one tag (its row's trash button) shows its receipt on screen", delete_one)

    def delete_selected():
        create_tag(app, "First Of Two")
        create_tag(app, "Second Of Two")
        for name in ("First Of Two", "Second Of Two"):
            app.click_reachable(row(app, name).locator("input[type=checkbox]"))
        app.click_reachable(page.get_by_title("Delete 2 selected", exact=True))
        confirm(app, "Delete Tags")
        words = toast_says(app, "Deleted 2 tags")
        left = [n for n in ("First Of Two", "Second Of Two") if row(app, n).count()]
        check(not left, f"still listed after the delete: {left} (toast: {words!r})")
    test("TAGS-002", "deleting two ticked tags (the trash button above them) shows one receipt on screen", delete_selected)

done()
