// Unit tests for bookFields.js — run: node test/bookFields.test.js
// Locks the ONE table's wire round-trip (docs/design/BOOK-FIELDS-TABLE.md): nothing is lost or
// renamed wrong across pack→unpack, the idempotency self-check is stable, mobile safe-defaults
// behave, and the structural schema self-check is clean. (Was serialization.test.js pre-7.17.0.)
const assert = require('assert');
const {
    BOOK_FIELDS, KNOWN_BOOK_FIELDS, NON_WIRE_FIELDS,
    packBook, unpackBook, roundTripCheck, schemaSelfCheck,
} = require('../bookFields.js');

let passed = 0;
function test(name, fn) { fn(); passed++; console.log('  ✓ ' + name); }

// A fully-populated OWNED book with every field set (so nothing hides behind a default).
function ownedBook() {
    return {
        id: 'B1', asin: 'B1', store: 'Amazon',
        title: 'Local Title', author: 'Jane Doe', series: 'The Series', seriesPosition: 3,
        seriesTotal: 7, coverUrl: 'c.jpg', description: 'desc', topReviews: [{ r: 5 }],
        publicationDate: '2020-01-01', rating: 4.5, ratingCount: '1,234', genres: ['scifi'],
        hasEnrichedData: true, binding: 'Kindle Edition',
        currentPrice: 6.99, listPrice: 9.99, priceFetchedAt: '2026-09-20', targetPrice: 5.0,
        priceTrigger: 4.99, priceAtGoalSet: 9.99, priceGoalSetAt: '2026-01-01',
        onWishlist: false, ownershipType: 'purchased', lastAmazonOwnershipType: 'purchased',
        addedToWishlist: '', acquired: '2019-06-01', dateAdded: '2019-06-02', isHidden: false,
        tags: ['read'], userNote: 'my note', myRating: 5, userEdited: { title: true },
        orphanStatus: 'verified', orphanCheckedDate: '2026-09-21',
        collectionTags: ['read'], collectionTagSeen: true,
        isDeleted: false, deletedAt: null, deletedFromFolderIds: null,
    };
}

function corpus() {
    const owned = ownedBook();
    const wishlist = { ...ownedBook(), asin: 'B2', id: 'B2', onWishlist: true, ownershipType: 'wishlist',
                       acquired: '', addedToWishlist: '2026-05-01', orphanStatus: null, orphanCheckedDate: null };
    const sample = { ...ownedBook(), asin: 'B3', id: 'B3', ownershipType: 'sample' };
    const cleared = { ...ownedBook(), asin: 'B4', id: 'B4', tags: [], userNote: null, myRating: 0,
                      priceTrigger: null, targetPrice: undefined, collectionTags: [], collectionTagSeen: false };
    const trashed = { ...ownedBook(), asin: 'B5', id: 'B5', isDeleted: true, deletedAt: '2026-05-01',
                      deletedFromFolderIds: ['f1', 'f2'] };
    const orphan = { ...ownedBook(), asin: 'B6', id: 'B6', orphanStatus: 'orphan', orphanCheckedDate: '2026-09-22' };
    const hidden = { ...ownedBook(), asin: 'B7', id: 'B7', isHidden: true, userEdited: { isHidden: true } };
    return [owned, wishlist, sample, cleared, trashed, orphan, hidden];
}

console.log('bookFields tests:');

// ---- Idempotency: pack→unpack→pack is stable (the anti-drift self-check) ----
test('round-trip is stable for every book in the corpus (no field lost or altered)', () => {
    const fail = roundTripCheck(corpus());
    assert.strictEqual(fail, null,
        fail ? `round-trip drift on ${fail.asin}.${fail.field}: ${JSON.stringify(fail.first)} → ${JSON.stringify(fail.second)}` : '');
});

// ---- Wire aliases: app name ↔ wire name ----
test('pack renames to the wire aliases', () => {
    const w = packBook(ownedBook());
    assert.strictEqual(w.note, 'my note', 'userNote → note');
    assert.strictEqual(w.authors, 'Jane Doe', 'author → authors');
    assert.strictEqual(w.reviewCount, '1,234', 'ratingCount → reviewCount');
    assert.strictEqual(w.acquisitionDate, '2019-06-01', 'acquired → acquisitionDate');
    assert.strictEqual(w.priceAsOf, '2026-09-20', 'priceFetchedAt → priceAsOf');
    assert.strictEqual(w.userNote, undefined, 'no app-name leakage (userNote)');
    assert.strictEqual(w.author, undefined, 'no app-name leakage (author)');
});

test('unpack restores from the wire aliases', () => {
    const b = unpackBook(packBook(ownedBook()));
    assert.strictEqual(b.userNote, 'my note');
    assert.strictEqual(b.author, 'Jane Doe');
    assert.strictEqual(b.ratingCount, '1,234');
    assert.strictEqual(b.acquired, '2019-06-01');
    assert.strictEqual(b.priceFetchedAt, '2026-09-20');
    assert.strictEqual(b.id, 'B1', 'id derived from asin');
    assert.strictEqual(b.store, 'Amazon', 'store always Amazon');
});

// ---- Derived ownership ----
test('onWishlist/ownershipType computed on pack', () => {
    assert.strictEqual(packBook(ownedBook()).onWishlist, false);
    const w = packBook({ ...ownedBook(), onWishlist: true, ownershipType: 'wishlist' });
    assert.strictEqual(w.onWishlist, true);
    assert.strictEqual(w.ownershipType, 'wishlist');
});

// ---- binding "Kindle eBook" → blank; normalizeBook maps "Kindle" → "Kindle Edition" ----
test('binding: "Kindle eBook" becomes blank; "Kindle" becomes "Kindle Edition"', () => {
    assert.strictEqual(unpackBook({ asin: 'X', binding: 'Kindle eBook' }).binding, undefined);
    assert.strictEqual(unpackBook({ asin: 'X', binding: 'Kindle' }).binding, 'Kindle Edition');
    assert.strictEqual(unpackBook({ asin: 'X', binding: 'Hardcover' }).binding, 'Hardcover');
});

// ---- The fields that Save/Restore used to drop must now survive pack→unpack ----
test('previously-lost fields survive the round trip', () => {
    const b = unpackBook(packBook(ownedBook()));
    assert.strictEqual(b.collectionTagSeen, true, 'collectionTagSeen (the original bug)');
    assert.deepStrictEqual(b.collectionTags, ['read'], 'collectionTags');
    assert.strictEqual(b.targetPrice, 5.0, 'targetPrice (was packed, never unpacked)');
    assert.strictEqual(b.dateAdded, '2019-06-02', 'dateAdded (was never unpacked)');
    assert.strictEqual(b.seriesTotal, 7, 'seriesTotal (was hard-blanked)');
    assert.strictEqual(b.publicationDate, '2020-01-01', 'publicationDate (was never packed)');
    assert.strictEqual(b.hasEnrichedData, true, 'hasEnrichedData (was never packed)');
    assert.strictEqual(b.orphanStatus, 'verified', 'orphanStatus');
    assert.strictEqual(b.orphanCheckedDate, '2026-09-21', 'orphanCheckedDate');
});

test('trash state survives (restore must NOT resurrect a trashed book)', () => {
    const t = corpus().find(b => b.isDeleted);
    const b = unpackBook(packBook(t));
    assert.strictEqual(b.isDeleted, true);
    assert.strictEqual(b.deletedAt, '2026-05-01');
    assert.deepStrictEqual(b.deletedFromFolderIds, ['f1', 'f2']);
});

// ---- Prices parse from strings (fetcher input) but pass through numbers (app input) ----
test('prices: string wire → number; number → number', () => {
    assert.strictEqual(unpackBook({ asin: 'X', currentPrice: '$6.99' }).currentPrice, 6.99);
    assert.strictEqual(unpackBook({ asin: 'X', currentPrice: 6.99 }).currentPrice, 6.99);
});

// ---- Cleared user fields don't get resurrected into junk ----
test('cleared user fields stay cleared through the round trip', () => {
    const c = corpus().find(b => b.asin === 'B4');
    const b = unpackBook(packBook(c));
    assert.deepStrictEqual(b.tags, [], 'empty tags stays empty');
    assert.strictEqual(b.collectionTagSeen, false);
    assert.deepStrictEqual(b.collectionTags, []);
    assert.strictEqual(b.myRating, 0);
});

// ---- Mobile safe-defaults (the { safeDefaults } deserialize option that folds in mapBackupBook) ----
// Mobile renders straight off unpacked books and must never hit undefined.map()/Object.keys(undefined).
// With { safeDefaults }, absent tags/userEdited/coverUrl come back as [] / {} / '' — NOT undefined.
// Desktop (no option) must be unchanged: those absent fields stay undefined (no invented keys on save).
test('safeDefaults gives mobile non-undefined tags/userEdited/coverUrl for a sparse item', () => {
    const sparse = { asin: 'M1', title: 'Mobile Book' };
    const b = unpackBook(sparse, { safeDefaults: true });
    assert.deepStrictEqual(b.tags, [], 'tags → []');
    assert.deepStrictEqual(b.userEdited, {}, 'userEdited → {}');
    assert.strictEqual(b.coverUrl, '', 'coverUrl → ""');
});

test('desktop (no safeDefaults) leaves the same absent fields undefined', () => {
    const sparse = { asin: 'M1', title: 'Mobile Book' };
    const b = unpackBook(sparse);
    assert.strictEqual(b.tags, undefined, 'tags stays undefined on desktop');
    assert.strictEqual(b.coverUrl, undefined, 'coverUrl stays undefined on desktop');
    // userEdited is undefined coming out of the wire loop; normalizeBook only adds it for a hidden book.
    assert.strictEqual(b.userEdited, undefined, 'userEdited stays undefined on desktop');
});

// ---- Structural schema self-check (replaces the two-list cross-check; now table-internal) ----
// With merge + wire in ONE table a field can't exist in one and not the other. The failure mode that
// replaces the old drift: a field added with wire:null (or packSkip and no unpack) is silently dropped
// on Save. schemaSelfCheck() is that guard, run here AND in the localhost in-app self-check.
test('schemaSelfCheck is clean (every field serialized, derived, or a known non-wire field)', () => {
    const problems = schemaSelfCheck();
    assert.deepStrictEqual(problems, [], `schema self-check problems:\n  ${problems.join('\n  ')}`);
});

test('a book field is serialized, derived on unpack, or a known separately-carried field', () => {
    const dropped = Object.entries(BOOK_FIELDS).filter(([f, spec]) => {
        const w = spec.wire;
        if (w === null) return !NON_WIRE_FIELDS.has(f);   // wire:null must be a known separate-list field
        if (w.packSkip) return !w.unpack;                  // packSkip must be recoverable on unpack
        return false;                                      // has a wire mapping → serialized
    }).map(([f]) => f);
    assert.deepStrictEqual(dropped, [],
        `book field(s) silently dropped on Save (add a wire mapping or list as non-wire): ${dropped.join(', ')}`);
});

test('every table key is a KNOWN_BOOK_FIELD (schema is the table keys)', () => {
    const strays = Object.keys(BOOK_FIELDS).filter(f => !KNOWN_BOOK_FIELDS.has(f));
    assert.deepStrictEqual(strays, [], `table key(s) missing from KNOWN_BOOK_FIELDS: ${strays.join(', ')}`);
});

console.log(`\n${passed} bookFields tests passed.`);
