// Unit tests for bookMerge.js — run: node test/bookMerge.test.js
// The pre-launch gate for the import merge. These lock the two footguns that kept
// going off (see bookMerge.js header): clear-then-resurrect, and phantom field names.
const assert = require('assert');
const {
    BOOK_FIELD_OWNERSHIP,
    USER_OWNED_FIELDS,
    mergeBookFields,
    KNOWN_BOOK_FIELDS,
    unknownBookFields,
} = require('../bookMerge.js');

let passed = 0;
function test(name, fn) { fn(); passed++; console.log('  ✓ ' + name); }

// A realistic, fully-populated pair. `local` = this device (with user edits);
// `incoming` = a stale relay echo of the same book (Amazon metadata refreshed).
function makePair() {
    const local = {
        asin: 'A1', id: 'b1', title: 'Local Title', author: 'Local Author',
        series: 'Local Series', seriesPosition: 3, binding: 'Hardcover',
        onWishlist: false, ownershipType: 'purchased', lastAmazonOwnershipType: 'purchased',
        addedToWishlist: '2024-01-01', isHidden: false,
        priceTrigger: 4.99, priceAtGoalSet: 9.99, priceGoalSetAt: '2024-01-01',
        targetPrice: 5.0, tags: ['scifi'], userNote: 'my note', myRating: 5,
        currentPrice: 9.99, description: 'local desc', coverUrl: 'local.jpg',
        isDeleted: false, deletedAt: null, deletedFromFolderIds: null,
        userEdited: {},
    };
    const incoming = {
        asin: 'A1', id: 'b1', title: 'Amazon Title', author: 'Amazon Author',
        series: 'Amazon Series', seriesPosition: 1, binding: 'Kindle Edition',
        onWishlist: false, ownershipType: 'purchased', lastAmazonOwnershipType: 'purchased',
        addedToWishlist: '2024-01-01', isHidden: false,
        priceTrigger: 7.99, priceAtGoalSet: 12.99, priceGoalSetAt: '2023-06-01',
        targetPrice: 8.0, tags: ['stale'], userNote: 'stale note', myRating: 2,
        currentPrice: 6.99, description: 'fresh amazon desc', coverUrl: 'amazon.jpg',
        isDeleted: false, deletedAt: null, deletedFromFolderIds: null,
        userEdited: {},
    };
    return { local, incoming };
}

console.log('bookMerge tests:');

// ---- Invariant 1: the merge never invents a field name (the phantom-field guard) ----
// A phantom like `note` (real field: userNote) shows up as a key present on the OUTPUT
// but on neither INPUT. This is the test that would have caught note/userNote and
// hidden/isHidden the moment they appeared.
test('never invents a key absent from both inputs (phantom-field guard)', () => {
    const { local, incoming } = makePair();
    const merged = mergeBookFields(local, incoming);
    const allowed = new Set([
        ...Object.keys(local),
        ...Object.keys(incoming),
        ...Object.keys(BOOK_FIELD_OWNERSHIP), // registry names are, by definition, real fields
    ]);
    const invented = Object.keys(merged).filter(k => !allowed.has(k));
    assert.deepStrictEqual(invented, [], `merge invented field(s): ${invented.join(', ')}`);
});

// ---- Invariant 2: a deliberate CLEAR of any user-owned field survives import ----
test('every user-owned field: a local CLEAR survives a stale incoming value', () => {
    for (const field of USER_OWNED_FIELDS) {
        const { local, incoming } = makePair();
        // user cleared it locally; incoming still carries the old value
        const cleared = field === 'tags' ? [] : (field === 'userNote' ? undefined : null);
        local[field] = cleared;
        const merged = mergeBookFields(local, incoming);
        assert.deepStrictEqual(merged[field], cleared,
            `cleared user field "${field}" was resurrected from incoming`);
    }
});

test('every user-owned field: a local VALUE wins over a different incoming value', () => {
    for (const field of USER_OWNED_FIELDS) {
        const { local, incoming } = makePair();
        const merged = mergeBookFields(local, incoming);
        assert.deepStrictEqual(merged[field], local[field],
            `user field "${field}" did not take the local value`);
    }
});

// ---- Overridable fields: userEdited flag decides ----
test('overridable field with userEdited flag → local wins', () => {
    const { local, incoming } = makePair();
    local.userEdited = { title: true, series: true };
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.title, 'Local Title');
    assert.strictEqual(merged.series, 'Local Series');
});

test('overridable field WITHOUT flag → incoming wins', () => {
    const { local, incoming } = makePair();
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.title, 'Amazon Title');
    assert.strictEqual(merged.author, 'Amazon Author');
    assert.strictEqual(merged.seriesPosition, 1);
});

// ---- ownershipType rides the onWishlist flag ----
test('ownershipType rides the onWishlist edit flag (flagged → keep local)', () => {
    const { local, incoming } = makePair();
    local.onWishlist = true; local.ownershipType = 'wishlist';
    local.userEdited = { onWishlist: true };
    incoming.onWishlist = false; incoming.ownershipType = 'purchased';
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.onWishlist, true);
    assert.strictEqual(merged.ownershipType, 'wishlist');
});

test('ownershipType follows incoming when onWishlist is not user-edited', () => {
    const { local, incoming } = makePair();
    local.onWishlist = true; local.ownershipType = 'wishlist';   // stale local
    incoming.onWishlist = false; incoming.ownershipType = 'purchased'; // Amazon now owns it
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.onWishlist, false);
    assert.strictEqual(merged.ownershipType, 'purchased');
});

// ---- binding blank-guard ----
test('binding: incoming BLANK never erases a known local binding', () => {
    const { local, incoming } = makePair();
    incoming.binding = undefined; // a lean fetch
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.binding, 'Hardcover');
});

test('binding: incoming value replaces when not user-edited; local wins when flagged', () => {
    let { local, incoming } = makePair();
    let merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.binding, 'Kindle Edition', 'unflagged → incoming');
    ({ local, incoming } = makePair());
    local.userEdited = { binding: true };
    merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.binding, 'Hardcover', 'flagged → local');
});

// ---- Amazon-owned metadata: incoming wins ----
test('Amazon-owned metadata (price, description, cover) takes incoming', () => {
    const { local, incoming } = makePair();
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.currentPrice, 6.99);
    assert.strictEqual(merged.description, 'fresh amazon desc');
    assert.strictEqual(merged.coverUrl, 'amazon.jpg');
});

// ---- soft-delete OR-merge ----
test('soft-delete OR-merges (a delete on either side sticks)', () => {
    const { local, incoming } = makePair();
    local.isDeleted = true; local.deletedAt = '2024-05-01';
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.isDeleted, true);
    assert.strictEqual(merged.deletedAt, '2024-05-01');
});

// ---- userEdited union ----
test('userEdited unions both sides (local wins on conflict)', () => {
    const { local, incoming } = makePair();
    local.userEdited = { title: true };
    incoming.userEdited = { author: true };
    const merged = mergeBookFields(local, incoming);
    assert.deepStrictEqual(merged.userEdited, { title: true, author: true });
});

// ---- lastAmazonOwnershipType: fresh signal wins, keep local if incoming lacks it ----
test('lastAmazonOwnershipType: incoming wins, falls back to local when absent', () => {
    let { local, incoming } = makePair();
    incoming.lastAmazonOwnershipType = 'wishlist';
    let merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.lastAmazonOwnershipType, 'wishlist', 'fresh signal wins');
    ({ local, incoming } = makePair());
    incoming.lastAmazonOwnershipType = undefined;
    merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.lastAmazonOwnershipType, 'purchased', 'kept local when incoming absent');
});

// ---- Field-schema validator (v7.15.3) ----
test('mergeBookFields output contains no unknown fields (merge stays within the schema)', () => {
    const { local, incoming } = makePair();
    const merged = mergeBookFields(local, incoming);
    assert.deepStrictEqual(unknownBookFields(merged), [],
        'merge produced field(s) not in KNOWN_BOOK_FIELDS');
});

test('unknownBookFields flags a phantom / wire-alias field on a book', () => {
    const { local } = makePair();
    local.note = 'wire alias of userNote';   // the exact 7.14.4 phantom
    local.hidden = true;                       // the 6.12.0 F4 phantom
    const flagged = unknownBookFields(local);
    assert.ok(flagged.includes('note'), 'should flag phantom `note`');
    assert.ok(flagged.includes('hidden'), 'should flag phantom `hidden`');
});

test('unknownBookFields is clean on a fully-populated legitimate book', () => {
    const { local } = makePair();
    assert.deepStrictEqual(unknownBookFields(local), [],
        'a realistic book should have no unknown fields (extend KNOWN_BOOK_FIELDS if this trips)');
});

test('every BOOK_FIELD_OWNERSHIP field is also in KNOWN_BOOK_FIELDS (registry ⊆ schema)', () => {
    const missing = Object.keys(BOOK_FIELD_OWNERSHIP).filter(f => !KNOWN_BOOK_FIELDS.has(f));
    assert.deepStrictEqual(missing, [],
        `registry fields missing from the schema: ${missing.join(', ')}`);
});

console.log(`\n${passed} bookMerge tests passed.`);
