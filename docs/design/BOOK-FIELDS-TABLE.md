# The book-fields table — one row per field, every behavior a column

**Status**: ✅ IMPLEMENTED — shipped in **7.17.0** (2026-09-25). This doc is now the design record.
`bookFields.js` holds `BOOK_FIELDS` (the one table) + serialize/deserialize + the schema validator;
`bookMerge.js` reads the merge column; `serialization.js` was retired; mobile's `mapBackupBook` folded
onto `unpackBook(item, { safeDefaults: true })`. Desktop verified (3186 books round-trip clean) + mobile
verified in the simulator. The §5 staging below is the plan that was followed — kept for the record.

## 1. Why

Today a book field's behavior is split across two hand-kept lists:
- **`BOOK_FIELD_OWNERSHIP`** (bookMerge.js) — how it *merges* on import.
- **`WIRE_FIELDS`** (serialization.js) — how it *packs/unpacks* to the wire.

They must agree but can drift — that's how `genresAsOf` ended up in one and not the other. The §5
cross-check test *catches* that; **one table makes it unrepresentable**: a field is one row, or it doesn't
exist. `KNOWN_BOOK_FIELDS` becomes the table's keys, so the schema, the merge, and the wire can't disagree.

## 2. The table

`bookFields.js` exports **`BOOK_FIELDS`** — keyed by **app field name**, one entry per field:

```js
const BOOK_FIELDS = {
  // identity
  asin:  { merge: 'identity', wire: {} },
  id:    { merge: 'identity', wire: { packSkip: true, unpack: i => i.asin } }, // derived from asin
  store: { merge: 'identity', wire: { packSkip: true, unpack: () => 'Amazon' } },

  // user-owned (local wins; a clear survives import)
  userNote:  { merge: 'user', wire: { name: 'note' } },
  tags:      { merge: 'user', wire: { safeDef: [] } },
  targetPrice:{ merge: 'user', wire: {} },
  myRating:  { merge: 'user', wire: { def: 0 } },

  // user-overridable (userEdited flag decides)
  title:  { merge: 'edit', wire: { def: 'Unknown' } },
  author: { merge: 'edit', wire: { name: 'authors', def: 'Unknown' } },
  isHidden:{ merge: 'edit', wire: { def: false } },

  // amazon-owned (incoming wins)
  ratingCount: { merge: 'amazon', wire: { name: 'reviewCount', def: '' } },
  currentPrice:{ merge: 'amazon', wire: { unpack: i => parsePrice(i.currentPrice) } },
  priceFetchedAt:{ merge: 'amazon', wire: { name: 'priceAsOf',
                    pack: b => b.priceFetchedAt || b.priceAsOf,
                    unpack: i => i.priceFetchedAt || i.priceAsOf || null } },
  readStatus: { merge: 'amazon', wire: null }, // travels in the separate collections list, not the book item

  // derived / special (documented, handled in code)
  onWishlist:    { merge: 'edit',          wire: { pack: b => isWishlisted(b) } }, // unpack via normalizeBook
  ownershipType: { merge: 'ride-wishlist', wire: { pack: b => b.ownershipType || (isWishlisted(b) ? 'wishlist' : 'purchased') } },
  binding:       { merge: 'edit-format',   wire: { unpack: i => (i.binding === 'Kindle eBook' ? undefined : i.binding) || undefined } },
  orphanStatus:  { merge: 'freshness',     wire: { def: null } },
  isDeleted:     { merge: 'soft-delete',   wire: { def: false } },
  userEdited:    { merge: 'special',       wire: {} },
  // …one row for every field currently in either list (~44)
};
```

**The columns:**
- **key** = app field name (== `KNOWN_BOOK_FIELDS` membership).
- **`merge`** = the class the current `BOOK_FIELD_OWNERSHIP` already uses (`user` / `edit` / `edit-format`
  / `ride-wishlist` / `amazon` / `identity` / `special` / `soft-delete` / `freshness`).
- **`wire`** = the current `WIRE_FIELDS` mapping, or **`null`** for fields that never ride the book wire
  item (`readStatus`, `collections`). Sub-keys: `name` (wire alias, default = the key), `def` (unpack
  default), `safeDef` (mobile non-undefined default; falls back to `def`), `pack(book)` / `unpack(item)`
  (derived), `packSkip` (unpack-only).

Nothing new is invented — this is the two existing lists **zipped by key**, plus the one new `safeDef`
column for mobile.

### The full field table (all 44)

Zipped from `BOOK_FIELD_OWNERSHIP` + `WIRE_FIELDS` as they stand today. **Wire** blank = same as the field
name; **`(none)`** = never on the book wire item (rides the separate collections list). **Default** is the
unpack default. **safeDef** = the extra mobile non-undefined default (blank = use Default).

| Field (app) | Merge | Wire name | Default | safeDef | Notes |
|---|---|---|---|---|---|
| `id` | identity | *(packSkip)* | | | derived `= item.asin` on unpack |
| `asin` | identity | | | | the merge key |
| `store` | identity | *(packSkip)* | `"Amazon"` | | unpack always "Amazon" |
| `priceTrigger` | user | | `null` | | the price goal |
| `priceAtGoalSet` | user | | `null` | | |
| `priceGoalSetAt` | user | | `null` | | |
| `targetPrice` | user | | | | |
| `tags` | user | | | `[]` | |
| `userNote` | user | **`note`** | | | alias |
| `myRating` | user | | `0` | | |
| `collectionTags` | user | | `[]` | | wizard state |
| `collectionTagSeen` | user | | `false` | | wizard state |
| `title` | edit | | `'Unknown'` | | |
| `author` | edit | **`authors`** | `'Unknown'` | | alias |
| `series` | edit | | `''` | | |
| `seriesPosition` | edit | | `''` | | |
| `onWishlist` | edit | | | | pack `isWishlisted(b)`; unpack via `normalizeBook` |
| `isHidden` | edit | | `false` | | |
| `binding` | edit-format | | | | unpack: "Kindle eBook"→blank; `normalizeBook` maps "Kindle"→"Kindle Edition" |
| `ownershipType` | ride-wishlist | | | | pack derives; unpack via `normalizeBook` |
| `userEdited` | special | | | `{}` | merge: union of both sides |
| `lastAmazonOwnershipType` | special | | | | merge: `incoming ?? local` |
| `addedToWishlist` | special | | `''` | | merge: `incoming ?? local` |
| `isDeleted` | soft-delete | | `false` | | merge: OR (a delete on either side sticks) |
| `deletedAt` | soft-delete | | `null` | | |
| `deletedFromFolderIds` | soft-delete | | `null` | | |
| `orphanStatus` | freshness | | `null` | | newer `orphanCheckedDate` wins |
| `orphanCheckedDate` | freshness | | `null` | | the freshness stamp |
| `seriesTotal` | amazon | | `''` | | |
| `coverUrl` | amazon | | | `''` | |
| `description` | amazon | | `''` | | |
| `topReviews` | amazon | | `[]` | | |
| `genres` | amazon | | `[]` | | |
| `publicationDate` | amazon | | `''` | | |
| `rating` | amazon | | `0` | | |
| `ratingCount` | amazon | **`reviewCount`** | `''` | | alias — **mobile renders this** (→ becomes `ratingCount`) |
| `currentPrice` | amazon | | | | unpack: `parsePrice` |
| `listPrice` | amazon | | | | unpack: `parsePrice` |
| `priceFetchedAt` | amazon | **`priceAsOf`** | `null` | | alias; pack/unpack fall back across both names |
| `acquired` | amazon | **`acquisitionDate`** | `''` | | alias |
| `dateAdded` | amazon | | `''` | | |
| `hasEnrichedData` | amazon | | `true` | | fetcher-set flag |
| `collections` | amazon | **`(none)`** | | | separate collections list, merged in after unpack |
| `readStatus` | amazon | **`(none)`** | `'UNKNOWN'` | | separate collections list |

(Vestigial `genresAsOf` is deliberately absent — see §6 / SERIALIZATION.md. `id`/`store` never travel as
wire values; `collections`/`readStatus` ride the separate collections list.)

## 3. Consumers (thin; the table is the single source)

- **`KNOWN_BOOK_FIELDS`** = `new Set(Object.keys(BOOK_FIELDS))`.
- **bookMerge.js** derives `USER_OWNED_FIELDS`/`USER_OVERRIDABLE_FIELDS`… by filtering on the `merge`
  column; `mergeBookFields` is unchanged in logic — it just reads classes from the table.
- **serialization.js** `packBook`/`unpackBook` iterate entries with `wire !== null`, using
  `name`/`def`/`safeDef`/`pack`/`unpack`/`packSkip`; `unpackBook` still runs `normalizeBook` after the loop.
- The **field-schema validator** uses `KNOWN_BOOK_FIELDS` (now the table keys) — so the §5 cross-check
  becomes true *by construction* (keep it as a cheap guard, or retire it — decide at build).

## 4. Module boundary (decided 2026-09-25)

**Ron's case (leans B, on principle):** there should be ONE serialization module with a clean
`serialize(book)` / `deserialize(item, opts)` API, where `opts` carries the *defining property* of the
target — **not** a `"mobile"` label but the actual distinguishing need, i.e. `{ safeDefaults: true }`.
Packing and unpacking are the same family of book-field transforms, so co-locating them (with the table)
is the cohesive "one thing": fewer files, one import surface, and — the real point — hardest to re-drift,
because a future editor sees the whole book-field story in one place.

**The counter (mine):** the *table* is the thing that drifted; unifying THAT is the chokepoint, and it's
met however the functions are arranged. `serialize`/`deserialize` are one lifecycle (book↔wire) and belong
together — agreed. But **`mergeBookFields` is a different operation** (combine two in-memory books on
import), not a wire transform; folding it into the "serialization" module trades a real single-
responsibility boundary — and `bookMerge`'s isolated 22-test suite — for mere proximity.

**Final call — a hybrid that honors the core of B:**
- **`bookFields.js`** = the master **table** + **`serialize(book)`** + **`deserialize(item, { safeDefaults })`**
  + `roundTripCheck` + the schema validator. This *is* Ron's one serialization module with the
  defining-property param — now also owning the table. (serialization.js's guts move here.)
- **`bookMerge.js`** keeps `mergeBookFields`, **importing the table** from `bookFields.js`. One table
  (no drift), but merge stays a separate, single-responsibility, independently-tested consumer.

So: **B for the wire** (table + serialize/deserialize together, param = `safeDefaults`), and merge stays a
thin satellite reading the same table. If after reading you'd rather fold merge in too (full B), it's a
fine build — say so; but my call is the hybrid.

Helpers (`isWishlisted`/`normalizeBook`/`parsePrice`) **stay in uiHelpers**; `bookFields.js` depends on it
(clean layering). See §7.3 on `normalizeBook`.

## 5. Migration staging (tests green at every step)

1. **Build `bookFields.js`** by zipping the two current lists key-by-key + the `safeDef` column; export
   `BOOK_FIELDS` + derived accessors + `KNOWN_BOOK_FIELDS`. Node-testable, no consumer changes yet.
2. **Re-source `bookMerge.js`** from the table (classes from the `merge` column). Run the **22 merge
   tests** — must stay green (characterization).
3. **Re-source `serialization.js`** from the table (`wire` column). Run the **11 serialization tests** —
   must stay green. Retire/replace the now-tautological cross-check.
4. **Mobile fold** (§11): `mapBackupBook → unpackBook(item, { safeDefaults: true })` + merge
   readStatus/collections; change the one `reviewCount`→`ratingCount` render; drop dead `priceAsOf`/
   `genresAsOf`; **audit mobile field-reads**; **dev-deploy mobile test**.

The existing 33 tests are the safety net: if merge + serialization keep passing after re-sourcing, the
refactor is behavior-preserving. Steps 1–3 are desktop-only + fully test-guarded; step 4 is the only one
needing a live (mobile) test.

## 6. Assumptions (and how verified)

- **The two lists zip cleanly by key** — every `WIRE_FIELDS.app` is already a `KNOWN_BOOK_FIELD` (the §5
  cross-check passes today), and `BOOK_FIELD_OWNERSHIP` keys ⊆ `KNOWN_BOOK_FIELDS`. So the union is the
  table. *Verify at build: list any key in one list but not the other (expected: none but `readStatus`/
  `collections`/`id`, which are the `wire:null` / derived rows).*
- **No consumer reads the raw list objects** beyond the accessors we control — *grep before moving.*
- **Mobile's only rendered wire-name quirk is `reviewCount`** — verified 2026-09-22 (grep: `priceAsOf`/
  `genresAsOf` set-but-unread).

## 7. Decisions (2026-09-25)
1. **Module boundary — RESOLVED (§4):** the hybrid — `bookFields.js` (table + serialize/deserialize with
   `{ safeDefaults }`) + `bookMerge.js` (merge, imports the table).
2. **Cross-check test — KEEP (Ron).** It's *different* from the localhost self-check: the cross-check is a
   **build-time, structural** test (do the wire list and the schema agree?), run in the Node suite; the
   self-check is a **runtime, real-data** round-trip over the actual library on localhost. After the one
   table the cross-check goes near-tautological (both sides ARE the table) — its remaining value is
   catching a future *re-split*, so it stays as a cheap guard. **And per Ron: also run it on localhost**
   (same localhost+version gate as the round-trip self-check), so a structural break surfaces there too,
   not only in the manually-run Node suite.
3. **`normalizeBook` — leave in uiHelpers** (my judgment, since #1 didn't go full-B). It's used on load and
   in the merge's previousBook normalization, not just by deserialize — a shared helper. Revisit only if
   it ever becomes serialization-only.
