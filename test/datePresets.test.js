// Unit tests for the shared "Date Added" presets (uiHelpers.js, v7.21.2) — run: node test/datePresets.test.js
// Fixed "today" values so the tests never drift with the calendar.
const assert = require('assert');
const { datePresetRange, datePresetLabel, datePresetOptions } = require('../uiHelpers.js');

let n = 0;
const t = (name, fn) => { fn(); n++; console.log('  ✓ ' + name); };
const day = (s) => new Date(s + 'T12:00:00');

console.log('datePresets');

t('rolling windows end today', () => {
    assert.deepStrictEqual(datePresetRange('last30', day('2026-10-16')), { from: '2026-09-16', to: '2026-10-16' });
    assert.deepStrictEqual(datePresetRange('lastYear', day('2026-10-16')), { from: '2025-10-16', to: '2026-10-16' });
});

t('This year / Last year ROLL with the calendar (Ron, 2026-10-16)', () => {
    assert.deepStrictEqual(datePresetRange('thisYear', day('2026-06-01')), { from: '2026-01-01', to: '2026-12-31' });
    assert.deepStrictEqual(datePresetRange('thisYear', day('2027-06-01')), { from: '2027-01-01', to: '2027-12-31' });
    assert.deepStrictEqual(datePresetRange('prevYear', day('2027-06-01')), { from: '2026-01-01', to: '2026-12-31' });
    assert.strictEqual(datePresetLabel('thisYear', day('2027-06-01')), 'This year (2027)');
    assert.strictEqual(datePresetLabel('prevYear', day('2027-06-01')), 'Last year (2026)');
});

t('a fixed year (incl. every saved Search from before) stays that year, labeled plainly', () => {
    assert.deepStrictEqual(datePresetRange('year2025', day('2030-01-01')), { from: '2025-01-01', to: '2025-12-31' });
    assert.strictEqual(datePresetLabel('year2025'), '2025'); // was printed raw as "year2025" in two places
});

t('none / custom → no preset range; custom labeled', () => {
    assert.strictEqual(datePresetRange(''), null);
    assert.strictEqual(datePresetRange('custom'), null);
    assert.strictEqual(datePresetLabel('custom'), 'Custom range');
});

t('the menu: rolling + This/Last year, then only EARLIER years the library has, newest first', () => {
    const ms = (s) => String(Date.parse(s + 'T12:00:00Z'));
    const books = [{ acquired: ms('2019-03-01') }, { acquired: ms('2023-05-01') }, { acquired: ms('2023-07-01') },
                   { acquired: ms('2026-02-01') }, { acquired: ms('2025-02-01') }, { acquired: 'junk' }, {}];
    const opts = datePresetOptions(books, day('2026-10-16'));
    assert.deepStrictEqual(opts.map(o => o.value),
        ['last30', 'last90', 'lastYear', 'thisYear', 'prevYear', 'year2023', 'year2019']);
    assert.strictEqual(opts[3].label, 'This year (2026)');
    assert.strictEqual(opts[5].label, '2023');
});

console.log(`${n} passed`);
