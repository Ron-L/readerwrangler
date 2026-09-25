// bookFields.js — the ONE table for every book field, and the wire (de)serialization that reads it.
// v7.17.0. Loaded as a classic script AFTER uiHelpers.js (browser); required by test/bookFields.test.js
// and test/bookMerge.test.js (Node).
//
// WHY THIS FILE EXISTS
//   A book field's behavior used to live in TWO hand-kept lists that drifted apart: BOOK_FIELD_OWNERSHIP
//   (merge) in bookMerge.js and WIRE_FIELDS (pack/unpack) in serialization.js — that split is how
//   `genresAsOf` ended up in one and not the other. Now there is ONE table, `BOOK_FIELDS`: one row per
//   field, columns for BOTH merge behavior AND wire mapping. A field can't exist in one and not the other.
//   `KNOWN_BOOK_FIELDS` is the table's keys; bookMerge reads the merge column; serialize/deserialize (here)
//   read the wire column. See docs/design/BOOK-FIELDS-TABLE.md.
//
// Depends on uiHelpers (isWishlisted / normalizeBook / parsePrice): globals in the browser, require() in Node.
const _uih = (typeof module !== 'undefined' && module.exports) ? require('./uiHelpers.js') : null;
const _isWishlisted  = _uih ? _uih.isWishlisted  : isWishlisted;
const _normalizeBook = _uih ? _uih.normalizeBook : normalizeBook;
const _parsePrice    = _uih ? _uih.parsePrice    : parsePrice;

// ---- THE TABLE ----------------------------------------------------------------
// Keyed by APP field name (== KNOWN_BOOK_FIELDS membership). Each row:
//   merge : the merge class — 'user' | 'edit' | 'edit-format' | 'ride-wishlist' | 'amazon' | 'identity'
//           | 'special' | 'soft-delete' | 'freshness'. Consumed by bookMerge.js's mergeBookFields.
//   wire  : the wire mapping, or `null` for fields that never ride the book wire item (they travel in a
//           separate collections sub-list). Sub-keys, all optional:
//             name     wire alias (default = the field name)
//             def      unpack default (desktop)
//             safeDef  mobile non-undefined default (used only with { safeDefaults }; falls back to def)
//             pack(book) / unpack(item)   custom transforms (derived/computed fields)
//             packSkip true = never written to the wire (unpack-only, e.g. id/store)
// This is the two former lists zipped by key, plus the `safeDef` column. Nothing invented.
const BOOK_FIELDS = {
    // identity — the merge key (same on both sides)
    asin:  { merge: 'identity', wire: {} },
    id:    { merge: 'identity', wire: { packSkip: true, unpack: i => i.asin } },   // derived = asin
    store: { merge: 'identity', wire: { packSkip: true, unpack: () => 'Amazon' } },

    // user-owned — local always wins (a deliberate clear survives import)
    priceTrigger:      { merge: 'user', wire: { def: null } },
    priceAtGoalSet:    { merge: 'user', wire: { def: null } },
    priceGoalSetAt:    { merge: 'user', wire: { def: null } },
    targetPrice:       { merge: 'user', wire: {} },
    tags:              { merge: 'user', wire: { safeDef: [] } },
    userNote:          { merge: 'user', wire: { name: 'note' } },   // wire alias
    myRating:          { merge: 'user', wire: { def: 0 } },
    collectionTags:    { merge: 'user', wire: { def: [] } },        // Tag-from-Collections wizard state
    collectionTagSeen: { merge: 'user', wire: { def: false } },

    // user-overridable — userEdited flag decides, else incoming
    title:          { merge: 'edit', wire: { def: 'Unknown' } },
    author:         { merge: 'edit', wire: { name: 'authors', def: 'Unknown' } },
    series:         { merge: 'edit', wire: { def: '' } },
    seriesPosition: { merge: 'edit', wire: { def: '' } },
    onWishlist:     { merge: 'edit', wire: { pack: b => _isWishlisted(b) } }, // unpack via normalizeBook
    isHidden:       { merge: 'edit', wire: { def: false } },

    // special-cased in mergeBookFields (see bookMerge.js)
    binding:                 { merge: 'edit-format', wire: { unpack: i => (i.binding === 'Kindle eBook' ? undefined : i.binding) || undefined } },
    ownershipType:           { merge: 'ride-wishlist', wire: { pack: b => b.ownershipType || (_isWishlisted(b) ? 'wishlist' : 'purchased') } },
    userEdited:              { merge: 'special', wire: { safeDef: {} } },
    lastAmazonOwnershipType: { merge: 'special', wire: {} },
    addedToWishlist:         { merge: 'special', wire: { def: '' } },
    isDeleted:               { merge: 'soft-delete', wire: { def: false } },
    deletedAt:               { merge: 'soft-delete', wire: { def: null } },
    deletedFromFolderIds:    { merge: 'soft-delete', wire: { def: null } },

    // orphan scan — sticky by freshness (newer orphanCheckedDate wins; special-cased in mergeBookFields)
    orphanStatus:      { merge: 'freshness', wire: { def: null } },
    orphanCheckedDate: { merge: 'freshness', wire: { def: null } },

    // amazon / fetcher-owned — incoming wins
    seriesTotal:     { merge: 'amazon', wire: { def: '' } },
    coverUrl:        { merge: 'amazon', wire: { safeDef: '' } },
    description:     { merge: 'amazon', wire: { def: '' } },
    topReviews:      { merge: 'amazon', wire: { def: [] } },
    genres:          { merge: 'amazon', wire: { def: [] } },
    publicationDate: { merge: 'amazon', wire: { def: '' } },
    rating:          { merge: 'amazon', wire: { def: 0 } },
    ratingCount:     { merge: 'amazon', wire: { name: 'reviewCount', def: '' } },  // wire alias
    currentPrice:    { merge: 'amazon', wire: { unpack: i => _parsePrice(i.currentPrice) } },
    listPrice:       { merge: 'amazon', wire: { unpack: i => _parsePrice(i.listPrice) } },
    priceFetchedAt:  { merge: 'amazon', wire: { name: 'priceAsOf',
                        pack:   b => b.priceFetchedAt || b.priceAsOf,
                        unpack: i => i.priceFetchedAt || i.priceAsOf || null } },
    acquired:        { merge: 'amazon', wire: { name: 'acquisitionDate', def: '' } },  // wire alias
    dateAdded:       { merge: 'amazon', wire: { def: '' } },
    hasEnrichedData: { merge: 'amazon', wire: { def: true } },
    collections:     { merge: 'amazon', wire: null },   // travels in the separate collections sub-list
    readStatus:      { merge: 'amazon', wire: null },   // travels in the separate collections sub-list
};

// ---- Derived accessors (single source: the table) -----------------------------
const KNOWN_BOOK_FIELDS = new Set(Object.keys(BOOK_FIELDS));
const FIELD_MERGE_CLASSES = new Set([
    'user', 'edit', 'edit-format', 'ride-wishlist', 'amazon', 'identity', 'special', 'soft-delete', 'freshness',
]);
const USER_OWNED_FIELDS = Object.keys(BOOK_FIELDS).filter(f => BOOK_FIELDS[f].merge === 'user');
const USER_OVERRIDABLE_FIELDS = Object.keys(BOOK_FIELDS).filter(f => BOOK_FIELDS[f].merge === 'edit');

// ---- Serialize / deserialize (read the wire column) ---------------------------
// Pack one app book → a wire item (schema 2.x).
const packBook = (book) => {
    const wire = {};
    for (const [app, spec] of Object.entries(BOOK_FIELDS)) {
        const w = spec.wire;
        if (!w || w.packSkip) continue;
        const name = w.name || app;
        const v = w.pack ? w.pack(book) : (book[app] ?? w.def);
        if (v !== undefined) wire[name] = v;   // omit undefined (matches JSON-on-the-wire)
    }
    return wire;
};

// Unpack one wire item → an app book (schema 2.x only; legacy v1.x is refused upstream).
// opts.safeDefaults (mobile): use each field's safeDef (non-undefined) so rendering never hits undefined.map().
const unpackBook = (item, opts = {}) => {
    const book = {};
    for (const [app, spec] of Object.entries(BOOK_FIELDS)) {
        const w = spec.wire;
        if (!w) continue;                       // wire:null → not on the book wire item
        if (w.unpack) { book[app] = w.unpack(item); continue; }
        const name = w.name || app;
        const dflt = (opts.safeDefaults && w.safeDef !== undefined) ? w.safeDef : w.def;
        book[app] = item[name] ?? dflt;
    }
    return _normalizeBook(book);                 // onWishlist/ownershipType/binding-synonym/isHidden
};

// ---- Round-trip self-check (idempotency; tolerates first-pass healing) ---------
const _deepEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const roundTripCheck = (books) => {
    const list = Array.isArray(books) ? books : [books];
    for (const raw of list) {
        const book = _normalizeBook(raw);        // heal first (no round-trip), then check idempotency
        const w1 = JSON.parse(JSON.stringify(packBook(book)));
        const w2 = JSON.parse(JSON.stringify(packBook(unpackBook(w1))));
        if (_deepEqual(w1, w2)) continue;
        const keys = new Set([...Object.keys(w1), ...Object.keys(w2)]);
        for (const k of keys) {
            if (!_deepEqual(w1[k], w2[k])) return { asin: book.asin, field: k, first: w1[k], second: w2[k] };
        }
        return { asin: book.asin, field: '(unknown)', first: w1, second: w2 };
    }
    return null;
};

// ---- Field-schema validator ---------------------------------------------------
// A key on a stored/merged book NOT in the table is a phantom / misnamed / wire-alias leak. Desktop-shape
// books only (merge output / loaded books), never raw fetcher/wire records.
const unknownBookFields = (book) => {
    if (!book || typeof book !== 'object') return [];
    return Object.keys(book).filter(k => !KNOWN_BOOK_FIELDS.has(k));
};

// ---- Structural schema self-check (the old build-time cross-check, now table-internal) ----
// When merge + wire were TWO lists, a field could exist in one and not the other; the cross-check
// test guarded that. With one table that split is unrepresentable — but a NEW failure mode replaces
// it: a field added with wire:null (or packSkip and no unpack) would be silently dropped on Save.
// This is that guard, as a pure function so it runs BOTH in the Node gate (test/bookFields.test.js)
// AND in the localhost/version-gated in-app self-check, alongside roundTripCheck. Returns [] = clean.
const NON_WIRE_FIELDS = new Set(['collections', 'readStatus']); // travel in the separate collections sub-list
const schemaSelfCheck = () => {
    const problems = [];
    for (const [f, spec] of Object.entries(BOOK_FIELDS)) {
        if (!FIELD_MERGE_CLASSES.has(spec.merge)) problems.push(`${f}: unrecognized merge class "${spec.merge}"`);
        const w = spec.wire;
        if (w === null) {
            if (!NON_WIRE_FIELDS.has(f)) problems.push(`${f}: wire:null but not a known separately-carried field (would be dropped on Save)`);
            continue;
        }
        if (w.packSkip && !w.unpack) problems.push(`${f}: packSkip with no unpack → unrecoverable on load`);
    }
    return problems;
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BOOK_FIELDS, KNOWN_BOOK_FIELDS, FIELD_MERGE_CLASSES, NON_WIRE_FIELDS,
        USER_OWNED_FIELDS, USER_OVERRIDABLE_FIELDS,
        packBook, unpackBook, roundTripCheck, unknownBookFields, schemaSelfCheck,
    };
}
