// Unit tests for bookMerge.js — run: node test/bookMerge.test.js
// The pre-launch gate for the import merge. These lock the two footguns that kept
// going off (see bookMerge.js header): clear-then-resurrect, and phantom field names.
const assert = require('assert');
const {
    BOOK_FIELD_OWNERSHIP,
    USER_OWNED_FIELDS,
    mergeBookFields,
    KNOWN_BOOK_FIELDS,
    FIELD_MERGE_CLASSES,
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

// ---- Tag-from-Collections wizard state survives import (the 7.16.0 wipe fix) ----
// collectionTags/collectionTagSeen are app/user-authored, but the fetcher never sets them
// AND the device-state push doesn't carry them — so incoming ALWAYS lacks them. As 'amazon'
// (incoming-wins) they were wiped on EVERY import; as 'user' (local-wins) they survive.
test('collectionTags / collectionTagSeen survive an import whose incoming lacks them', () => {
    const { local, incoming } = makePair();
    local.collectionTags = ['read', 'scifi'];
    local.collectionTagSeen = true;
    delete incoming.collectionTags;      // a fetch / device-state record never carries these
    delete incoming.collectionTagSeen;
    const merged = mergeBookFields(local, incoming);
    assert.deepStrictEqual(merged.collectionTags, ['read', 'scifi'],
        'collectionTags wiped by an import that lacked it');
    assert.strictEqual(merged.collectionTagSeen, true,
        'collectionTagSeen wiped by an import that lacked it');
});

// ---- orphanStatus: sticky by freshness (7.16.0 hardening — ORPHAN-CLEANUP §3) ----
test('orphanStatus: a stale echo or scan-less incoming cannot clear a flagged orphan', () => {
    let { local, incoming } = makePair();
    local.orphanStatus = 'orphan'; local.orphanCheckedDate = '2026-09-22T10:00:00Z';
    incoming.orphanStatus = 'verified'; incoming.orphanCheckedDate = '2026-09-20T10:00:00Z'; // older
    let merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.orphanStatus, 'orphan', 'an older incoming scan cleared a local orphan');
    // a lean fetcher run carrying NO scan at all also must not clear it
    ({ local, incoming } = makePair());
    local.orphanStatus = 'orphan'; local.orphanCheckedDate = '2026-09-22T10:00:00Z';
    delete incoming.orphanStatus; delete incoming.orphanCheckedDate;
    merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.orphanStatus, 'orphan', 'a scan-less incoming cleared a local orphan');
});

test('orphanStatus: a fresher scan wins (a returned book clears to verified)', () => {
    const { local, incoming } = makePair();
    local.orphanStatus = 'orphan'; local.orphanCheckedDate = '2026-09-20T10:00:00Z';
    incoming.orphanStatus = 'verified'; incoming.orphanCheckedDate = '2026-09-22T10:00:00Z'; // newer
    const merged = mergeBookFields(local, incoming);
    assert.strictEqual(merged.orphanStatus, 'verified', 'a fresher scan did not win');
    assert.strictEqual(merged.orphanCheckedDate, '2026-09-22T10:00:00Z');
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

// ---- Merge-completeness chokepoint (v7.16.0) ----
// The registry and the schema are now ONE list (KNOWN is derived from the registry).
// This asserts the bijection holds even if someone later un-derives KNOWN, and — the
// point — that EVERY book field carries an explicit merge decision (no silent
// incoming-wins default, the gap that let orphanStatus slip). Adding a field to one list
// but not the other fails here. See ORPHAN-CLEANUP.md §4.
test('merge-completeness: KNOWN_BOOK_FIELDS === BOOK_FIELD_OWNERSHIP keys (every field has a decision)', () => {
    const known = [...KNOWN_BOOK_FIELDS].sort();
    const registry = Object.keys(BOOK_FIELD_OWNERSHIP).sort();
    assert.deepStrictEqual(known, registry,
        'every book field must have exactly one explicit merge decision (no silent default)');
});

test('every registry field has a recognized merge class (catches class typos)', () => {
    const bad = Object.entries(BOOK_FIELD_OWNERSHIP)
        .filter(([, cls]) => !FIELD_MERGE_CLASSES.has(cls))
        .map(([f, cls]) => `${f}:${cls}`);
    assert.deepStrictEqual(bad, [],
        `registry field(s) with an unrecognized class: ${bad.join(', ')}`);
});

console.log(`\n${passed} bookMerge tests passed.`);
