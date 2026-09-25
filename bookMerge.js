// bookMerge.js — the ONE place a book's field-merge behavior is IMPLEMENTED.
// v7.17.0. Loaded as a classic script AFTER bookFields.js, before storage.js (browser),
// and required by test/bookMerge.test.js (Node).
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
// THE MECHANISM (v7.17.0: the field catalog moved to bookFields.js — the ONE table)
//   - Every field's merge CLASS is declared once, in bookFields.js's BOOK_FIELDS table
//     (the `merge` column), alongside its wire mapping — so a field can't be classified
//     for merge but forgotten for serialization, or vice-versa (that split is how
//     `genresAsOf` drifted). This file reads USER_OWNED_FIELDS / USER_OVERRIDABLE_FIELDS
//     from that table and IMPLEMENTS the merge; the special classes are handled explicitly
//     below. See docs/design/BOOK-FIELDS-TABLE.md.
//   - mergeBookFields() is a pure function → test/bookMerge.test.js locks it in the
//     pre-launch gate: every user field's clear must survive, and the merge must not
//     invent a key that exists on neither input (which is exactly what a phantom name
//     like `note` looks like). See PRINCIPLES.md Law 10.

// The field catalog + its derived accessors live in bookFields.js (globals in the browser,
// require() in Node). Underscore-aliased so the browser globals aren't redeclared here.
const _bf = (typeof module !== 'undefined' && module.exports) ? require('./bookFields.js') : null;
const _USER_OWNED_FIELDS       = _bf ? _bf.USER_OWNED_FIELDS       : USER_OWNED_FIELDS;
const _USER_OVERRIDABLE_FIELDS = _bf ? _bf.USER_OVERRIDABLE_FIELDS : USER_OVERRIDABLE_FIELDS;

// Copy every USER-OWNED field from `local` onto `target` (local wins, unconditionally
// — even undefined/null, so a cleared value is preserved rather than resurrected).
// Shared by every merge branch so the user-field NAME LIST lives in exactly one place.
const assignUserOwnedFields = (target, local) => {
    for (const f of _USER_OWNED_FIELDS) target[f] = local[f];
    return target;
};

// Merge a book's LOCAL copy (what's on this device) with an INCOMING copy (a relay/
// Amazon record, or a same-payload duplicate). Default: incoming wins for every
// Amazon-owned field; the table's user classes below override for user fields.
// Pure function — no side effects, safe to unit-test.
const mergeBookFields = (local, incoming) => {
    const ue = { ...(incoming.userEdited || {}), ...(local.userEdited || {}) };  // union; local wins on conflict
    const merged = { ...incoming };                       // Amazon-owned fields default to incoming

    assignUserOwnedFields(merged, local);                 // user-owned: local wins (clear survives)
    for (const f of _USER_OVERRIDABLE_FIELDS) {           // overridable: user edit wins, else incoming
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

// Node export for unit tests (no-op in the browser classic-script context). The field
// catalog + schema validator now live in bookFields.js — import them from there.
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        assignUserOwnedFields,
        mergeBookFields,
    };
}
