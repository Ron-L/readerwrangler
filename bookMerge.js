// bookMerge.js — the ONE place a book's field-merge behavior is declared.
// v7.14.4 (2026-09-20). Loaded as a classic script before storage.js (browser),
// and required by test/bookMerge.test.js (Node). Depends on nothing.
//
// WHY THIS FILE EXISTS
// Two footguns kept going off in the import merge:
//   1. Clear-then-resurrect. A user clears a price goal / rating / tag / note. On the
//      next Import from Relay the cleared value came back, because the merge did
//      `incoming ?? local` and treated a cleared null as "absent — fall back to
//      incoming", where incoming is only a stale echo of the app's own past push.
//   2. Phantom field names. The merge preserved a field called `note` while the real
//      book field is `userNote` (and once `hidden` vs the real `isHidden`). The name
//      mismatch is invisible to JS — the wrong field is quietly created and the real
//      one quietly dropped. Notes were never actually preserved on import.
//
// THE MECHANISM
//   - BOOK_FIELD_OWNERSHIP names every merge-relevant field exactly ONCE, with its
//     class. The merge is DRIVEN by this map, so a field can't be missed and its name
//     can't drift between the setter's idea and the merge's idea.
//   - mergeBookFields() is a pure function → test/bookMerge.test.js locks it in the
//     pre-launch gate: every user field's clear must survive, and the merge must not
//     invent a key that exists on neither input (which is exactly what a phantom name
//     like `note` looks like). See PRINCIPLES.md Law 10.

// ---- Field-ownership registry — THE COMPLETE, AUTHORITATIVE FIELD CATALOG ------
// EVERY desktop book field appears here EXACTLY ONCE with an explicit merge decision.
// There is NO "unlisted → silent default" bucket any more — and that bucket is exactly
// how orphanStatus slipped through: it existed as a field, nobody ever DECIDED how it
// merges, so it fell into incoming-wins and a stale echo wiped the orphan flag (the
// 7.16.0 scope miss — see ORPHAN-CLEANUP.md §1/§4). KNOWN_BOOK_FIELDS is now DERIVED
// from these keys (below), so the schema validator and the merge registry are ONE list:
// a field added to a book but not classified here is flagged 'unknown' by
// unknownBookFields(). Adding a field without a merge decision is therefore
// unrepresentable — the mechanism, not a comment (Ron's "Strong" option 2026-09-22;
// PRINCIPLES legal-states).
//
// The classes:
//   'user'          USER-OWNED. The fetcher NEVER sets these, so a local CLEAR must
//                   survive import → local always wins. Cross-device propagation is a
//                   non-goal (mobile is read-only; two-desktops-one-channel is
//                   discouraged — MULTI-INSTANCE §5).
//   'edit'          USER-OVERRIDABLE. Both sides may set it; the user's edit wins only
//                   when userEdited[field] is flagged, otherwise incoming wins.
//   'edit-format'   binding: like 'edit', but an incoming BLANK never erases a known
//                   value (a lean fetch must not undo the scan's backfill). Special-cased.
//   'ride-wishlist' ownershipType: not its own decision — follows the onWishlist edit
//                   flag (one user decision, two fields). Special-cased.
//   'amazon'        AMAZON/FETCHER-OWNED metadata — incoming-wins (the {...incoming} base).
//                   The fetcher is the source of truth; the app never authors these.
//   'identity'      the merge key (id/asin/store) — carried by incoming, never contested.
//   'special'       handled explicitly in mergeBookFields with its own rule (see code):
//                   userEdited (union); lastAmazonOwnershipType / addedToWishlist (incoming ?? local).
//   'soft-delete'   isDeleted/deletedAt/deletedFromFolderIds — OR-merged (a delete on
//                   either side sticks). Special-cased in mergeBookFields.
//   'freshness'     orphanStatus/orphanCheckedDate — sticky by freshness: the copy with the
//                   NEWER orphanCheckedDate wins. A fresh scan (orphan OR verified) wins; a stale
//                   echo, or a fetcher run that carries no scan, can't clear a flagged orphan.
//                   Guest-guard stamp pattern (MULTI-INSTANCE §3). Special-cased in mergeBookFields.
//
// ⚠️ OWNERSHIP-AUDIT SUSPECTS (2026-09-22): a few 'amazon' entries CODIFY CURRENT
// BEHAVIOR but may actually be app/user-authored — the same latent class as orphanStatus.
// Flagged inline with `SUSPECT`; NOT changed here (each needs Ron's decision + a test).
// Tracked in the ownership-audit TODO.
const BOOK_FIELD_OWNERSHIP = {
    // IDENTITY — the merge key (same on both sides)
    id:    'identity',
    asin:  'identity',
    store: 'identity',

    // USER-OWNED — local always wins (a deliberate clear survives import)
    priceTrigger:   'user',   // the price goal
    priceAtGoalSet: 'user',   // price snapshot captured when the goal was set (rides the goal)
    priceGoalSetAt: 'user',   // when the goal was set (rides the goal)
    targetPrice:    'user',
    tags:           'user',
    userNote:       'user',   // NB: the real field is userNote — the backup wire calls it `note`
    myRating:       'user',
    // Tag-from-Collections wizard state — app/user-authored. The fetcher NEVER sets these AND the
    // device-state push (readerwrangler ~5560) doesn't carry them, so incoming ALWAYS lacks them →
    // they MUST be local-wins or every import silently wipes them (7.16.0 fix; were 'amazon' = wiped).
    collectionTags:    'user',   // RW tags created FROM Kindle collections; removal-detection needs them to persist
    collectionTagSeen: 'user',   // "user has processed this book in the wizard" — drives the "New books only" toggle

    // USER-OVERRIDABLE — userEdited flag decides, else incoming
    title:          'edit',
    author:         'edit',
    series:         'edit',
    seriesPosition: 'edit',
    onWishlist:     'edit',   // ownership toggle; ownershipType rides this same flag
    isHidden:       'edit',   // real field is isHidden (once mis-preserved as `hidden`)

    // SPECIAL-CASED in mergeBookFields (see the code + class doc above)
    binding:                 'edit-format',
    ownershipType:           'ride-wishlist',
    userEdited:              'special',      // union of both sides
    lastAmazonOwnershipType: 'special',      // incoming ?? local (fresh signal wins, keep local if absent)
    addedToWishlist:         'special',      // incoming ?? local
    isDeleted:               'soft-delete',
    deletedAt:               'soft-delete',
    deletedFromFolderIds:    'soft-delete',

    // AMAZON / FETCHER-OWNED — incoming-wins (the {...incoming} base)
    seriesTotal:     'amazon',
    coverUrl:        'amazon',
    description:     'amazon',
    topReviews:      'amazon',
    genres:          'amazon',
    publicationDate: 'amazon',
    rating:          'amazon',
    ratingCount:     'amazon',
    currentPrice:    'amazon',
    listPrice:       'amazon',
    priceFetchedAt:  'amazon',
    acquired:        'amazon',    // Amazon acquisition date
    dateAdded:       'amazon',    // set once from the wire; stable across fetches
    collections:     'amazon',    // Kindle collections — read-only from Amazon
    readStatus:      'amazon',    // refreshed from Amazon collections each fetch
    orphanStatus:      'freshness', // sticky: the newer orphanCheckedDate wins (special-cased below) — ORPHAN-CLEANUP §3
    orphanCheckedDate: 'freshness', // the freshness stamp orphanStatus rides
    hasEnrichedData:   'amazon',  // fetcher-set enrichment flag
};

const USER_OWNED_FIELDS = Object.keys(BOOK_FIELD_OWNERSHIP).filter(f => BOOK_FIELD_OWNERSHIP[f] === 'user');
const USER_OVERRIDABLE_FIELDS = Object.keys(BOOK_FIELD_OWNERSHIP).filter(f => BOOK_FIELD_OWNERSHIP[f] === 'edit');

// Copy every USER-OWNED field from `local` onto `target` (local wins, unconditionally
// — even undefined/null, so a cleared value is preserved rather than resurrected).
// Shared by every merge branch so the user-field NAME LIST lives in exactly one place.
const assignUserOwnedFields = (target, local) => {
    for (const f of USER_OWNED_FIELDS) target[f] = local[f];
    return target;
};

// Merge a book's LOCAL copy (what's on this device) with an INCOMING copy (a relay/
// Amazon record, or a same-payload duplicate). Default: incoming wins for every
// Amazon-owned field; the registry rules below override for user fields.
// Pure function — no side effects, safe to unit-test.
const mergeBookFields = (local, incoming) => {
    const ue = { ...(incoming.userEdited || {}), ...(local.userEdited || {}) };  // union; local wins on conflict
    const merged = { ...incoming };                       // Amazon-owned fields default to incoming

    assignUserOwnedFields(merged, local);                 // user-owned: local wins (clear survives)
    for (const f of USER_OVERRIDABLE_FIELDS) {            // overridable: user edit wins, else incoming
        merged[f] = ue[f] ? local[f] : incoming[f];
    }

    // ownershipType rides the onWishlist edit flag (one decision, two fields)
    merged.ownershipType = ue.onWishlist ? local.ownershipType : incoming.ownershipType;
    // format: an edited binding wins; else take incoming, but an incoming BLANK never
    // erases a known binding (a lean fetch must not undo the scan's backfill)
    merged.binding = ue.binding ? local.binding : (incoming.binding ?? local.binding);
    // Amazon-ownership snapshot: fresh Amazon signal wins, keep local if incoming lacks it
    merged.lastAmazonOwnershipType = incoming.lastAmazonOwnershipType ?? local.lastAmazonOwnershipType;
    merged.addedToWishlist = incoming.addedToWishlist ?? local.addedToWishlist;
    // orphanStatus: sticky by freshness — the copy with the newer orphanCheckedDate wins. A fresh scan
    // (orphan OR verified) wins so a returned book clears; a stale echo, or a fetcher run carrying no
    // scan (no orphanCheckedDate), can't clear a flagged orphan. {...incoming} already took incoming's
    // pair; override only when LOCAL is strictly fresher. Guest-guard stamp (MULTI-INSTANCE §3).
    {
        const localOCD = local.orphanCheckedDate ? new Date(local.orphanCheckedDate).getTime() : 0;
        const incomingOCD = incoming.orphanCheckedDate ? new Date(incoming.orphanCheckedDate).getTime() : 0;
        if (incomingOCD < localOCD) {
            merged.orphanStatus = local.orphanStatus;
            merged.orphanCheckedDate = local.orphanCheckedDate;
        }
    }
    // soft-delete: OR-merge (a delete on either side sticks; survives relay imports)
    merged.isDeleted = local.isDeleted || incoming.isDeleted || false;
    merged.deletedAt = local.deletedAt || incoming.deletedAt || null;
    merged.deletedFromFolderIds = local.deletedFromFolderIds || incoming.deletedFromFolderIds || null;
    // userEdited: union (inherit another device's edit-markers, keep local)
    merged.userEdited = ue;

    return merged;
};

// ---- Field-schema validator (v7.15.3; UNIFIED with the registry v7.16.0) --------
// KNOWN_BOOK_FIELDS is now DERIVED from the ownership registry keys — ONE source of
// truth for "what fields a desktop book legitimately has." A key on a stored/merged
// book that is NOT here is a phantom, a misnamed field, or a wire-name alias that leaked
// in (the `note`/`userNote`, `hidden`/`isHidden` class) — OR a real new field someone
// forgot to classify in BOOK_FIELD_OWNERSHIP (now the SAME thing: no classification,
// no membership). DELIBERATELY EXCLUDED (never in the registry, so never "known"):
// wire/backup aliases (authors, note, reviewCount, acquisitionDate, priceAsOf, seriesNum,
// collectionList) and dead/vestigial fields (isDeal, purchaseDate, coverUrlHiRes,
// recovered, genresAsOf) — any of those on a real book gets FLAGGED, which is the point.
// Validate DESKTOP-shape books only (merge output / loaded books), NEVER raw fetcher/wire records.
const KNOWN_BOOK_FIELDS = new Set(Object.keys(BOOK_FIELD_OWNERSHIP));

// The recognized merge classes — every registry value MUST be one of these. A typo like
// 'usr' would otherwise silently fall through to incoming-wins (a bug the completeness
// map exists to kill). Gate-tested in bookMerge.test.js.
const FIELD_MERGE_CLASSES = new Set([
    'user', 'edit', 'edit-format', 'ride-wishlist', 'amazon', 'identity', 'special', 'soft-delete',
    'freshness',
]);

// Return the keys on `book` that are NOT known legitimate desktop fields — phantoms / misnamed /
// wire-alias fields that leaked onto a stored book. Empty array = clean. DESKTOP-shape books only.
const unknownBookFields = (book) => {
    if (!book || typeof book !== 'object') return [];
    return Object.keys(book).filter(k => !KNOWN_BOOK_FIELDS.has(k));
};

// Node export for unit tests (no-op in the browser classic-script context).
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BOOK_FIELD_OWNERSHIP,
        USER_OWNED_FIELDS,
        USER_OVERRIDABLE_FIELDS,
        assignUserOwnedFields,
        mergeBookFields,
        KNOWN_BOOK_FIELDS,
        FIELD_MERGE_CLASSES,
        unknownBookFields,
    };
}
