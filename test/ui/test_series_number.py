# Screen test: a book at series position 0 (a prequel, "Book 0") is a book with a number — the book dialog keeps and
# shows it, and the book list sorts it before Book 1 and shows its "#0".
# tags: series, sort, book dialog, tier 2
# covers: readerwrangler.js, uiHelpers.js
# Run: py tools/run_tests.py --id SERIES-010     (or --tier 2; or directly with the venv's Python)
#
# Bug (found by Ron 2026-11-13; "fix now" 2026-11-15): 0 was read as "no position" — `parseFloat(x) || Infinity` in the
# book list's sorts and `x || '?'` / `x ? … : …` in its displays — so Book 0 sorted last with the blanks, showed "-" in
# the "#" column and "#?" as its group, and the book dialog showed no "Book 0". Ron's workaround was 0.0001. Now every
# sort and display reads a position through one helper (uiHelpers.js: seriesNumber / seriesPositionText /
# compareSeriesPositions — function tests SERIES-001–007, which also cover the phone's sort).
#
# The fixture's series (test/fixtures/make-small-fixture.js), in the folder Fantasy › The Test Saga:
#   Book One (1), Book Two (2), Between the Books (2.5), Book Three (3). The test makes Between the Books Book 0
#   through the book dialog — the way a person would — then sorts the folder.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import check, done, test   # noqa: E402
from rw import FIXTURE, App              # noqa: E402

ONE, TWO, THREE = "The Test Saga, Book One", "The Test Saga, Book Two", "The Test Saga, Book Three"
ZERO = "The Test Saga: Between the Books"     # 2.5 in the fixture; Book 0 after SERIES-010
TITLES = [ONE, TWO, THREE, ZERO]

# What the list shows: each row in order — a group header's words, or a book's title and its "#" cell.
ROWS_JS = """() => {
    const heads = [...document.querySelectorAll('thead th')].map(th => th.textContent.trim());
    const hash = heads.findIndex(t => /^#/.test(t));
    return { hash, rows: [...document.querySelectorAll('tbody tr')].map(tr => {
        const cells = [...tr.children].map(td => td.textContent.trim());
        return cells.length === 1 ? { header: cells[0] } : { text: tr.textContent, num: hash >= 0 ? cells[hash] : null };
    }) };
}"""


def show_saga(app, sort, group=False):
    """The Test Saga folder in List View, sorted by `sort`, the "#" column shown — set in the saved view settings, then
    the page reloaded (the column chooser and the header clicks aren't what this test is about)."""
    app.page.evaluate("""([sort, group]) => {
        const key = 'readerwrangler-explorer';
        let d = {};
        try { d = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (e) {}
        d.selectedFolderId = 'f-saga'; d.explorerView = 'list'; d.explorerSort = sort;
        d.folderSortSettings = { ...(d.folderSortSettings || {}), 'f-saga': sort };
        d.visibleColumns = { ...(d.visibleColumns || {}), seriesNum: true };
        d.explorerGroupOn = group;
        localStorage.setItem(key, JSON.stringify(d));
    }""", [sort, group])
    app.reload()
    app.page.locator("tbody tr", has_text=ONE).first.wait_for(timeout=30_000)


def saga_rows(app):
    got = app.page.evaluate(ROWS_JS)
    check(got["hash"] >= 0, "setup: the '#' column isn't showing")
    out = []
    for r in got["rows"]:
        if "header" in r:
            out.append(("header", r["header"]))
            continue
        names = [t for t in TITLES if t in r["text"]]
        if names:
            out.append((max(names, key=len), r["num"]))
    check(sum(1 for kind, _ in out if kind != "header") == 4, f"setup: not the saga's four books: {out}")
    return out


def book_order(rows):
    return [kind for kind, _ in rows if kind != "header"]


with App() as app:
    page = app.page
    app.restore(FIXTURE)
    show_saga(app, [{"column": "seriesNum", "direction": "asc"}], group=True)

    def position(title):
        return page.evaluate("(t) => { const b = window.books.find(x => x.title === t); return b ? b.seriesPosition : 'missing'; }",
                             title)

    def open_book(title):
        page.locator("tbody tr", has_text=title).first.dblclick()
        page.get_by_role("button", name="Edit book fields").wait_for(timeout=5000)

    def close_book():
        page.keyboard.press("Escape")
        page.get_by_role("button", name="Edit book fields").wait_for(state="detached", timeout=5000)

    def dialog_round_trip():
        check(position(ZERO) == "2.5", f"setup: Between the Books isn't at 2.5: {position(ZERO)!r}")
        open_book(ZERO)
        try:
            page.get_by_role("button", name="Edit book fields").click()
            field = page.get_by_placeholder("e.g., 1, 1.5")
            field.fill("0")
            page.get_by_role("button", name="✓ Save").click()
            field.wait_for(state="detached", timeout=5000)
            page.wait_for_function("(t) => window.books.find(x => x.title === t).seriesPosition === 0", arg=ZERO, timeout=5000)
            check(position(ZERO) == 0, f"typing 0 didn't save 0: {position(ZERO)!r}")
            shown = page.get_by_text("Book 0: The Test Saga", exact=True)
            check(shown.count() == 1, "after saving 0, the dialog doesn't say 'Book 0: The Test Saga'")
        finally:
            close_book()
        open_book(ZERO)
        try:
            check(page.get_by_text("Book 0: The Test Saga", exact=True).count() == 1,
                  "reopened, the dialog doesn't say 'Book 0: The Test Saga'")
            page.get_by_role("button", name="Edit book fields").click()
            value = page.get_by_placeholder("e.g., 1, 1.5").input_value()
            check(value == "0", f"reopened for editing, the position field holds {value!r}, not '0'")
            check(page.get_by_role("button", name="Remove from Series").count() == 1,
                  "with 0 in the field, 'Remove from Series' isn't offered (0 read as no position)")
            page.get_by_role("button", name="Cancel", exact=True).click()
        finally:
            close_book()
        check(position(ZERO) == 0, f"after Cancel the position changed: {position(ZERO)!r}")
    test("SERIES-010", "the book dialog: typing 0 as the position saves 0, says 'Book 0', and holds 0 when reopened",
         dialog_round_trip)

    def sorted_by_number():
        rows = saga_rows(app)
        problems = []   # every difference at once — the order, the cell and the group are three separate places
        if book_order(rows) != [ZERO, ONE, TWO, THREE]:
            problems.append(f"sorted by '#': {book_order(rows)}")
        nums = dict(r for r in rows if r[0] != "header")
        if nums.get(ZERO) != "0":
            problems.append(f"Book 0's '#' cell shows {nums.get(ZERO)!r}, not '0'")
        heads = [h.lstrip("▾▸ ") for kind, h in rows if kind == "header"]   # a header reads "▾#0(1)": arrow, name, count
        if not any(h.startswith("#0(") for h in heads) or any(h.startswith("#?") for h in heads):
            problems.append(f"the groups: {heads} — Book 0's should be '#0', never '#?'")
        check(not problems, "\n".join(problems))
    test("SERIES-011", "sorted by '#', Book 0 comes first — before Book 1 — and shows #0 (its cell and its group)",
         sorted_by_number)

    def sorted_by_number_down():
        show_saga(app, [{"column": "seriesNum", "direction": "desc"}])
        check(book_order(saga_rows(app)) == [THREE, TWO, ONE, ZERO], f"sorted by '#', highest first: {book_order(saga_rows(app))}")
    test("SERIES-012", "sorted by '#' highest first, Book 0 comes last — after Book 1, not at the top with the blanks",
         sorted_by_number_down)

    def sorted_by_series():
        show_saga(app, [{"column": "series", "direction": "asc"}])
        check(book_order(saga_rows(app)) == [ZERO, ONE, TWO, THREE], f"sorted by Series: {book_order(saga_rows(app))}")
    test("SERIES-013", "sorted by Series, the books of a series are in reading order with Book 0 first", sorted_by_series)

    # Found on the way (the same save line): the dialog compared the typed position (a number) with Amazon's (text), so
    # "1" and 1 differed — every Save of the dialog, even with nothing changed, rewrote the position and marked it as
    # YOUR edit, after which Amazon could no longer correct it. Now they're compared as numbers.
    def unchanged_save():
        edited = "(t) => { const b = window.books.find(x => x.title === t); return [b.seriesPosition, !!(b.userEdited || {}).seriesPosition]; }"
        check(page.evaluate(edited, ONE) == ["1", False], f"setup: Book One isn't Amazon's '1': {page.evaluate(edited, ONE)}")
        open_book(ONE)
        try:
            page.get_by_role("button", name="Edit book fields").click()
            check(page.get_by_placeholder("e.g., 1, 1.5").input_value() == "1", "setup: the field doesn't hold 1")
            page.get_by_role("button", name="✓ Save").click()
            page.get_by_role("button", name="Edit book fields").wait_for(timeout=5000)   # out of edit mode: the save ran
            # the save's book change and the dialog's exit render together; window.books follows in the effect after —
            # wait one frame and a task so a wrong write has landed before it's read
            page.evaluate("() => new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)))")
        finally:
            close_book()
        got = page.evaluate(edited, ONE)
        check(got == ["1", False], f"Save with nothing changed rewrote the position or marked it yours: {got}")
    test("SERIES-014", "the book dialog's Save with the position unchanged leaves Amazon's position as it was — not "
         "rewritten, not marked as your edit", unchanged_save)

done()
