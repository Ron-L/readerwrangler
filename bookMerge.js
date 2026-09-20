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

// ---- Field-ownership registry -------------------------------------------------
// Anything NOT listed here is Amazon-owned metadata and defaults to incoming-wins
// (title/description/price/covers/genres/…). Only fields the USER can author or
// override need a rule.
//
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
const BOOK_FIELD_OWNERSHIP = {
    // USER-OWNED — local always wins (a deliberate clear survives import)
    priceTrigger:   'user',   // the price goal
    priceAtGoalSet: 'user',   // price snapshot captured when the goal was set (rides the goal)
    priceGoalSetAt: 'user',   // when the goal was set (rides the goal)
    targetPrice:    'user',
    tags:           'user',
    userNote:       'user',   // NB: the real field is userNote — the backup wire calls it `note`
    myRating:       'user',

    // USER-OVERRIDABLE — userEdited flag decides, else incoming
    title:          'edit',
    author:         'edit',
    series:         'edit',
    seriesPosition: 'edit',
    onWishlist:     'edit',   // ownership toggle; ownershipType rides this same flag
    isHidden:       'edit',   // real field is isHidden (once mis-preserved as `hidden`)

    // Special-cased in mergeBookFields (documented above)
    binding:        'edit-format',
    ownershipType:  'ride-wishlist',
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
    // soft-delete: OR-merge (a delete on either side sticks; survives relay imports)
    merged.isDeleted = local.isDeleted || incoming.isDeleted || false;
    merged.deletedAt = local.deletedAt || incoming.deletedAt || null;
    merged.deletedFromFolderIds = local.deletedFromFolderIds || incoming.deletedFromFolderIds || null;
    // userEdited: union (inherit another device's edit-markers, keep local)
    merged.userEdited = ue;

    return merged;
};

// Node export for unit tests (no-op in the browser classic-script context).
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BOOK_FIELD_OWNERSHIP,
        USER_OWNED_FIELDS,
        USER_OVERRIDABLE_FIELDS,
        assignUserOwnedFields,
        mergeBookFields,
    };
}
