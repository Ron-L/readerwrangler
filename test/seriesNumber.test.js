// Unit tests for THE reading of a series position (uiHelpers.js, 7.30.0) — run: node test/seriesNumber.test.js
// tags: series, sort, phone, tier 1
// covers: uiHelpers.js
//
// Bug (found by Ron 2026-11-13; "fix now" 2026-11-15): a book at series position 0 — a prequel, "Book 0" — was read as
// having NO position: `parseFloat(x) || Infinity` and `x || '?'` take 0 for "nothing", so it sorted last with the blanks
// and showed as blank (Ron's workaround: 0.0001). Now one reading for every sort and every display, desktop and phone:
// seriesNumber (the number a sort uses — 0 is a number), seriesPositionText (what a place shows — "0"), and ONE
// comparator, compareSeriesPositions (lower first, no number after every number), inside the one tiebreak both the
// book list and the phone use (bookOrderTiebreak). Positions arrive as text from Amazon ("3", "2.5"), as numbers from
// the book dialog and Set numbers, and as '' / null when there is none.
const assert = require('assert');
const { seriesNumber, seriesPositionText, compareSeriesPositions, bookOrderTiebreak } = require('../uiHelpers.js');
const { test: t, done } = require('./harness');

console.log('seriesNumber');

t('SERIES-001', 'seriesNumber: 0 is a number — as text and as a number', () => {
    assert.strictEqual(seriesNumber(0), 0);
    assert.strictEqual(seriesNumber('0'), 0);
    assert.strictEqual(seriesNumber(' 0 '), 0);
    assert.strictEqual(seriesNumber('0.0'), 0);
});

t('SERIES-002', 'seriesNumber: every other number reads as before (text as parseFloat reads it)', () => {
    const rows = [[0.5, 0.5], ['0.5', 0.5], [1, 1], ['1', 1], [2, 2], ['2', 2], ['2.5', 2.5], ['10', 10], [0.0001, 0.0001]];
    for (const [v, want] of rows) assert.strictEqual(seriesNumber(v), want, `seriesNumber(${JSON.stringify(v)})`);
});

t('SERIES-003', 'seriesNumber: blank, missing or not a number is null — never 0, never Infinity', () => {
    for (const v of [null, undefined, '', '   ', 'abc', '.', NaN, Infinity, true, {}]) {
        assert.strictEqual(seriesNumber(v), null, `seriesNumber(${String(v)})`);
    }
});

t('SERIES-004', 'seriesPositionText: 0 shows as "0"; a blank shows nothing', () => {
    assert.strictEqual(seriesPositionText(0), '0');
    assert.strictEqual(seriesPositionText('0'), '0');
    assert.strictEqual(seriesPositionText(2.5), '2.5');
    assert.strictEqual(seriesPositionText(' 3 '), '3');
    for (const v of [null, undefined, '', '  ', NaN]) assert.strictEqual(seriesPositionText(v), '', `text of ${String(v)}`);
});

t('SERIES-005', 'compareSeriesPositions: 0 before 1, lower first, blanks after every number, two blanks tie', () => {
    const input = ['2', null, 1, '', '0.5', 'abc', 0, undefined, '10', '2.5'];
    const sorted = [...input].sort(compareSeriesPositions);
    assert.deepStrictEqual(sorted.slice(0, 6), [0, '0.5', 1, '2', '2.5', '10'], `sorted: ${JSON.stringify(sorted)}`);
    for (const v of sorted.slice(6)) assert.strictEqual(seriesNumber(v), null, `a blank sorted among the numbers: ${JSON.stringify(sorted)}`);
    assert.ok(compareSeriesPositions(0, 1) < 0, '0 before 1');
    assert.ok(compareSeriesPositions('0', '1') < 0, '"0" before "1"');
    assert.ok(compareSeriesPositions(0, '') < 0, '0 before a blank');
    assert.ok(compareSeriesPositions(null, 0) > 0, 'a blank after 0');
    assert.strictEqual(compareSeriesPositions(null, ''), 0, 'two blanks tie (a number, not NaN — the next sort level decides)');
    assert.strictEqual(compareSeriesPositions('2', 2), 0, 'the same number as text and as a number ties');
});

t('SERIES-006', 'bookOrderTiebreak (the book list and the phone): within a series, Book 0 comes before Book 1', () => {
    const book = (asin, title, seriesPosition) => ({ asin, title, author: 'A. Writer', series: 'The Saga', seriesPosition });
    const books = [book('B3', 'Three', '3'), book('BX', 'Unnumbered', ''), book('B1', 'One', '1'),
                   book('B0', 'Prequel', '0'), book('B2', 'Two', 2)];
    assert.deepStrictEqual([...books].sort(bookOrderTiebreak).map(b => b.title), ['Prequel', 'One', 'Two', 'Three', 'Unnumbered']);
});

t('SERIES-007', 'bookOrderTiebreak: author, then series, then position, then title, then ASIN — as before', () => {
    const books = [
        { asin: 'B9', title: 'Zed', author: 'B', series: '', seriesPosition: '' },
        { asin: 'B8', title: 'Alpha', author: 'A', series: 'S2', seriesPosition: '1' },
        { asin: 'B7', title: 'Beta', author: 'A', series: 'S1', seriesPosition: '2' },
        { asin: 'B6', title: 'Same', author: 'A', series: 'S1', seriesPosition: '' },
        { asin: 'B5', title: 'Same', author: 'A', series: 'S1', seriesPosition: null },
    ];
    assert.deepStrictEqual([...books].sort(bookOrderTiebreak).map(b => b.asin), ['B7', 'B5', 'B6', 'B8', 'B9']);
});

done();
