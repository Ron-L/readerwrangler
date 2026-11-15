// Unit tests for how the fetchers read a book's series and number — run: node test/fetcherSeries.test.js
// tags: series, fetcher, tier 1
// covers: amazon-library-fetcher.js, author-bibliography-fetcher.js
//
// Bug (owner, 2026-11-15): a book numbered 0 in its series ("Book 0", a prequel) lost its number in the fetchers —
// `position || null` drops a numeric 0; the title fallback (a dead edition with no series record) refused 0 and threw
// the series NAME away with it ("(Digger Book 0)"), and capped every number at 400 (Perry Rhodan passed 3,300). Decided:
// keep a 0 wherever a position is read (blank or missing is still nothing); in a title, "Book N" and "#N" accept 0 up to
// 9999, while a bare number after a comma — where years sit, "(Collected Stories, 2019)" — keeps 1–400 ("wrong is worse
// than none"). The records below are made up, shaped like the product records the fetchers read
// (product.title.displayString, product.bookSeries.singleBookView.series.{title, position}; the bibliography's
// product.bookSeriesInfo.{seriesTitle, position}). Nothing here talks to Amazon.
const assert = require('assert');
const { parseSeriesFromTitle, seriesFromLibraryProduct } = require('../amazon-library-fetcher.js');
const { seriesFromBibliographyProduct } = require('../author-bibliography-fetcher.js');
const { test: t, done } = require('./harness');

// A library product record: a title, and a series record only when `series` is given (a dead edition has none).
const product = (title, series) => ({
    asin: 'B000TEST01',
    title: { displayString: title },
    ...(series !== undefined && { bookSeries: { singleBookView: { series } } }),
});

console.log('fetcher series');

t('FSERIES-001', 'title fallback: "(Digger Book 0)" keeps the series and the 0', () => {
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Digging (Digger Book 0)'), { series: 'Digger', seriesPosition: '0' });
    const s = seriesFromLibraryProduct(product('Fictitious Digging (Digger Book 0)'));
    assert.strictEqual(s.series, 'Digger');
    assert.strictEqual(s.seriesPosition, '0');
    assert.strictEqual(s.fromTitle, true);
    assert.strictEqual(s.positionSentAs, null, 'no series record — nothing to count');
});

t('FSERIES-002', 'title fallback: "Book N" and "#N" go up to 9999 — Perry Rhodan Book 3300', () => {
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Return (Perry Rhodan Book 3300)'), { series: 'Perry Rhodan', seriesPosition: '3300' });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious End (Perry Rhodan Book 9999)'), { series: 'Perry Rhodan', seriesPosition: '9999' });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Saga (Long Run #401)'), { series: 'Long Run', seriesPosition: '401' });
});

t('FSERIES-003', 'title fallback: "(Saga #0)" keeps the 0', () => {
    assert.deepStrictEqual(parseSeriesFromTitle('First Light (Saga #0)'), { series: 'Saga', seriesPosition: '0' });
    assert.deepStrictEqual(parseSeriesFromTitle('First Light (Ember Saga # 0)'), { series: 'Ember', seriesPosition: '0' });
});

t('FSERIES-004', 'title fallback: a number after a comma stays 1–400 — a year is not a series number', () => {
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Tales (Collected Stories, 2019)'), { series: null, seriesPosition: null });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Tales (Collected Stories, 401)'), { series: null, seriesPosition: null });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Tales (Collected Stories, 0)'), { series: null, seriesPosition: null });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Tales (Collected Stories, 400)'), { series: 'Collected Stories', seriesPosition: '400' });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Tales (Collected Stories, 3)'), { series: 'Collected Stories', seriesPosition: '3' });
});

t('FSERIES-005', 'title fallback: "Book 12000" is past 9999 — no series, no number', () => {
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Omnibus (Huge Run Book 12000)'), { series: null, seriesPosition: null });
    assert.deepStrictEqual(parseSeriesFromTitle('Fictitious Omnibus (Huge Run Book 10000)'), { series: null, seriesPosition: null });
    const s = seriesFromLibraryProduct(product('Fictitious Omnibus (Huge Run Book 12000)'));
    assert.strictEqual(s.series, null);
    assert.strictEqual(s.seriesPosition, null);
    assert.strictEqual(s.fromTitle, false);
});

t('FSERIES-006', 'title fallback, as before: no parentheses, no marker, a blank name, no title → nothing', () => {
    for (const title of [null, undefined, '', 'Plain Title', 'Fictitious (A Novel)', 'Fictitious (Book 3)', 'Unknown Title']) {
        assert.deepStrictEqual(parseSeriesFromTitle(title), { series: null, seriesPosition: null }, `title ${JSON.stringify(title)}`);
    }
    // only the LAST parenthetical counts; "A … novel" trimmed as before
    assert.deepStrictEqual(parseSeriesFromTitle('Where (Not This Book 9) Now? (A Gideon Sable novel Book 5)'), { series: 'Gideon Sable', seriesPosition: '5' });
});

t('FSERIES-007', 'series record: a position of 0 as a number is kept — as a number', () => {
    const s = seriesFromLibraryProduct(product('Fictitious Prequel', { title: 'Digger', position: 0 }));
    assert.deepStrictEqual(s, { series: 'Digger', seriesPosition: 0, fromTitle: false, positionSentAs: 'number' });
});

t('FSERIES-008', 'series record: a position of "0" as text is kept — as text', () => {
    const s = seriesFromLibraryProduct(product('Fictitious Prequel', { title: 'Digger', position: '0' }));
    assert.deepStrictEqual(s, { series: 'Digger', seriesPosition: '0', fromTitle: false, positionSentAs: 'text' });
});

t('FSERIES-009', 'series record: an empty, null or absent position is no number (the series stays)', () => {
    const rows = [
        [{ title: 'Digger', position: '' }, 'blank'],
        [{ title: 'Digger', position: null }, 'missing'],
        [{ title: 'Digger' }, 'missing'],
    ];
    for (const [record, sentAs] of rows) {
        const s = seriesFromLibraryProduct(product('Fictitious Middle', record));
        assert.deepStrictEqual(s, { series: 'Digger', seriesPosition: null, fromTitle: false, positionSentAs: sentAs }, JSON.stringify(record));
    }
});

t('FSERIES-010', 'series record: other numbers come through exactly as Amazon sent them', () => {
    assert.strictEqual(seriesFromLibraryProduct(product('X', { title: 'S', position: '3' })).seriesPosition, '3');
    assert.strictEqual(seriesFromLibraryProduct(product('X', { title: 'S', position: '2.5' })).seriesPosition, '2.5');
    assert.strictEqual(seriesFromLibraryProduct(product('X', { title: 'S', position: 7 })).seriesPosition, 7);
    assert.strictEqual(seriesFromLibraryProduct(product('X', { title: 'S', position: 7 })).positionSentAs, 'number');
});

t('FSERIES-011', 'a series record wins: the title is read only when the record has no series name', () => {
    // a record with a name but no number does NOT take the title's number
    const kept = seriesFromLibraryProduct(product('Fictitious (Digger Book 4)', { title: 'Digger', position: '' }));
    assert.deepStrictEqual(kept, { series: 'Digger', seriesPosition: null, fromTitle: false, positionSentAs: 'blank' });
    // a record with no name (or none at all) falls back to the title
    const fell = seriesFromLibraryProduct(product('Fictitious (Digger Book 0)', { title: null, position: null }));
    assert.deepStrictEqual(fell, { series: 'Digger', seriesPosition: '0', fromTitle: true, positionSentAs: 'missing' });
    const none = seriesFromLibraryProduct(product('Fictitious (Digger Book 0)', null));
    assert.deepStrictEqual(none, { series: 'Digger', seriesPosition: '0', fromTitle: true, positionSentAs: null });
    // no product title at all
    assert.deepStrictEqual(seriesFromLibraryProduct({ asin: 'B000TEST02' }), { series: null, seriesPosition: null, fromTitle: false, positionSentAs: null });
});

t('FSERIES-012', 'bibliography fetcher: a position of 0 (number or text) is kept; blank or missing is no number', () => {
    const bib = (info) => ({ asin: 'B000TEST03', title: { displayString: 'Fictitious' }, ...(info !== undefined && { bookSeriesInfo: info }) });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger', position: 0 })), { series: 'Digger', seriesPosition: 0 });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger', position: '0' })), { series: 'Digger', seriesPosition: '0' });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger', position: 3 })), { series: 'Digger', seriesPosition: 3 });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger', position: '' })), { series: 'Digger', seriesPosition: null });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger', position: null })), { series: 'Digger', seriesPosition: null });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib({ seriesTitle: 'Digger' })), { series: 'Digger', seriesPosition: null });
    assert.deepStrictEqual(seriesFromBibliographyProduct(bib(undefined)), { series: null, seriesPosition: null });
});

done();
