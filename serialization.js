// serialization.js — the ONE place a book is packed to / unpacked from "the wire".
// v7.16.0. Loaded as a classic script AFTER uiHelpers.js (browser), required by
// test/serialization.test.js (Node). "The wire" = the schema-2.x data format used by BOTH
// the backup file AND the device-state push (phone/relay).
//
// WHY THIS FILE EXISTS
//   Several hand-written packers/unpackers drifted apart and silently dropped fields on
//   Save/Restore (confirmed live: collectionTags 964→0). See docs/design/SERIALIZATION.md.
//   Fix: ONE master field list drives ONE packer + ONE unpacker, so a field added to one
//   direction is added to both — drift becomes impossible. A round-trip self-check
//   (pack→unpack→pack must be stable) is the mechanism that proves it, in the dev test AND
//   in a localhost/version-gated in-app check.
//
// Depends on uiHelpers (isWishlisted / normalizeBook / parsePrice): globals in the browser,
// require() in Node.
const _uih = (typeof module !== 'undefined' && module.exports) ? require('./uiHelpers.js') : null;
const _isWishlisted  = _uih ? _uih.isWishlisted  : isWishlisted;
const _normalizeBook = _uih ? _uih.normalizeBook : normalizeBook;
const _parsePrice    = _uih ? _uih.parsePrice    : parsePrice;

// ---- The master field list ----------------------------------------------------
// One entry per wire field. Default behavior:
//   pack:   wire[wire] = book[app] ?? def
//   unpack: book[app]  = item[wire] ?? def
// Asymmetries live as per-field rules (Ron's design): `wire` (rename), `def` (shared
// default), `pack(book)` / `unpack(item)` overrides, `packSkip` (unpack-only field).
// `app` defaults the wire name; omit `wire` when they match.
const WIRE_FIELDS = [
    // identity
    { app: 'asin' },
    // bibliographic / Amazon metadata
    { app: 'title', def: 'Unknown' },
    { app: 'author', wire: 'authors', def: 'Unknown' },
    { app: 'series', def: '' },
    { app: 'seriesPosition', def: '' },
    { app: 'seriesTotal', def: '' },                 // was hard-blanked on unpack; now round-trips
    { app: 'coverUrl' },
    { app: 'description', def: '' },
    { app: 'topReviews', def: [] },
    { app: 'publicationDate', def: '' },             // was never packed; now travels
    { app: 'rating', def: 0 },
    { app: 'ratingCount', wire: 'reviewCount', def: '' },
    { app: 'genres', def: [] },
    // NB: genresAsOf is intentionally NOT here — it's vestigial (nothing populates/reads it on desktop;
    // excluded from KNOWN_BOOK_FIELDS in 7.15.3). Producing it would trip the field-schema validator.
    { app: 'hasEnrichedData', def: true },           // was never packed; now travels
    // binding: incoming "Kindle eBook" (the app's pre-7.7 invented default) means blank;
    // normalizeBook (post-unpack) additionally maps "Kindle" → "Kindle Edition".
    { app: 'binding', unpack: (i) => (i.binding === 'Kindle eBook' ? undefined : i.binding) || undefined },
    // pricing
    { app: 'currentPrice', unpack: (i) => _parsePrice(i.currentPrice) },
    { app: 'listPrice', unpack: (i) => _parsePrice(i.listPrice) },
    { app: 'priceFetchedAt', wire: 'priceAsOf',
      pack:   (b) => b.priceFetchedAt || b.priceAsOf,
      unpack: (i) => i.priceFetchedAt || i.priceAsOf || null },
    { app: 'priceTrigger', def: null },
    { app: 'priceAtGoalSet', def: null },
    { app: 'priceGoalSetAt', def: null },
    { app: 'targetPrice' },                          // was packed but never unpacked; now round-trips
    // ownership (onWishlist/ownershipType: computed on pack, normalized on unpack via normalizeBook)
    { app: 'onWishlist', pack: (b) => _isWishlisted(b) },
    { app: 'ownershipType', pack: (b) => b.ownershipType || (_isWishlisted(b) ? 'wishlist' : 'purchased') },
    { app: 'lastAmazonOwnershipType' },
    { app: 'addedToWishlist', def: '' },
    { app: 'acquired', wire: 'acquisitionDate', def: '' },
    { app: 'dateAdded', def: '' },                   // was never unpacked; now round-trips
    { app: 'isHidden', def: false },
    { app: 'store', packSkip: true, unpack: () => 'Amazon' },  // always "Amazon"; never on the wire
    // user-authored
    { app: 'tags' },
    { app: 'userNote', wire: 'note' },
    { app: 'myRating', def: 0 },
    { app: 'userEdited' },
    // orphan scan
    { app: 'orphanStatus', def: null },
    { app: 'orphanCheckedDate', def: null },
    // tag-from-collections wizard state (was omitted from backup → wiped; the bug that started this)
    { app: 'collectionTags', def: [] },
    { app: 'collectionTagSeen', def: false },
    // soft-delete (trash)
    { app: 'isDeleted', def: false },
    { app: 'deletedAt', def: null },
    { app: 'deletedFromFolderIds', def: null },
];
// NB: readStatus + collections are NOT here — they travel in a separate collections sub-list,
// merged in by the caller after unpack. Book-item schema only.

// Pack one app book → a wire item (schema 2.x).
const packBook = (book) => {
    const wire = {};
    for (const f of WIRE_FIELDS) {
        if (f.packSkip) continue;
        const name = f.wire || f.app;
        const v = f.pack ? f.pack(book) : (book[f.app] ?? f.def);
        if (v !== undefined) wire[name] = v;   // omit undefined (matches JSON-on-the-wire)
    }
    return wire;
};

// Unpack one wire item → an app book (schema 2.x only; legacy v1.x is refused upstream).
const unpackBook = (item) => {
    const book = {};
    for (const f of WIRE_FIELDS) {
        const name = f.wire || f.app;
        book[f.app] = f.unpack ? f.unpack(item) : (item[name] ?? f.def);
    }
    book.id = item.asin;                       // stable id = asin
    return _normalizeBook(book);               // onWishlist/ownershipType/binding-synonym/isHidden
};

// ---- Round-trip self-check ----------------------------------------------------
// The anti-drift invariant is IDEMPOTENCY, not naive equality (a few fields are healed on the
// first pack): pack → unpack → pack again must produce an identical wire form. Returns null if
// stable, else { field, first, second } for the first differing wire field. `books` may be one
// book or an array; returns the first failure (or null).
const _deepEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const roundTripCheck = (books) => {
    const list = Array.isArray(books) ? books : [books];
    for (const raw of list) {
        // Heal first (userEdited/onWishlist/binding backfill) WITHOUT a round-trip, so the check
        // tolerates legitimate first-pass healing yet still catches real field loss (which happens
        // inside pack/unpack, not in normalizeBook). Real library books are already normalized.
        const book = _normalizeBook(raw);
        const w1 = JSON.parse(JSON.stringify(packBook(book)));      // simulate the wire (drops undefined)
        const w2 = JSON.parse(JSON.stringify(packBook(unpackBook(w1))));
        if (_deepEqual(w1, w2)) continue;
        const keys = new Set([...Object.keys(w1), ...Object.keys(w2)]);
        for (const k of keys) {
            if (!_deepEqual(w1[k], w2[k])) {
                return { asin: book.asin, field: k, first: w1[k], second: w2[k] };
            }
        }
        return { asin: book.asin, field: '(unknown)', first: w1, second: w2 };
    }
    return null;
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WIRE_FIELDS, packBook, unpackBook, roundTripCheck };
}
