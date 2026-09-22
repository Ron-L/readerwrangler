# Serialization: one field list, one packer, one unpacker (wire + backup)

**Status**: DESIGN — for Ron's red pen (2026-09-22). Part of the 7.16.0 data-integrity hardening
(branch `feature/orphan-cleanup-dialog`).
**Problem owner**: the library's save/sync format ("the wire") is packed and unpacked by *several*
hand-maintained functions that have drifted apart, silently dropping fields on Save/Restore.

---

## 1. The problem (with evidence)

When a book is saved to a backup file, pushed to the phone/relay (device-state), or read back on
import/restore, it is converted to a plain data format ("the wire") and back. Today that conversion
is done by **multiple hand-written functions that were supposed to match but drifted**:

- **Packers (book → wire):** `buildDeviceStatePayload` (device-state push) **and** `exportBackup`
  (backup file) each build their own book list. `exportBackup` fell behind by **eight** fields.
- **Unpackers (wire → book):** `loadLibrary`'s `processedBooks` (import + restore, two branches) and
  `mobile.js`'s `mapBackupBook` (phone, read-only).

**Confirmed data loss (live bisect, 2026-09-22):** after a Save→Restore, `collectionTagSeen` went
**1470 → 0** and `collectionTags` **964 → 0**. Tracing showed `exportBackup` also omits `dateAdded`,
`orphanStatus`, and the trash triple (`isDeleted`/`deletedAt`/`deletedFromFolderIds`) — so restore
silently loses trash state (would *resurrect* trashed books), date-added, and orphan flags too. And
the unpacker reads fields the packer never writes (`publicationDate`, `seriesTotal`, `hasEnrichedData`)
(and the packer wrote a vestigial `genresAsOf` that nothing reads — dropped from the schema, not carried). So Save/Restore silently drops the real ones.

This is the drift the merge-completeness chokepoint (alpha.2) was built to kill, one layer out.

---

## 2. Current site-map (the comb, identity-key pivot)

| Direction | Function | Location | Used by |
|---|---|---|---|
| pack | `buildDeviceStatePayload` | readerwrangler ~5557 | device-state push (phone/relay) |
| pack | `exportBackup` (own copy) | readerwrangler ~5704 | Save backup to file **(drifted)** |
| pack | collections sub-list ×2 | ~5601 / ~5742 | `asin/readStatus/collections` (its own dup pair) |
| unpack | `loadLibrary` → `processedBooks` | readerwrangler ~6182 (new-format + legacy) | import **and** restore |
| unpack | `mapBackupBook` | mobile.js ~62 | phone (read-only) |

Upstream and separate: the **fetchers** turn Amazon's API into book records; they legitimately don't
carry user fields and are not part of this round-trip.

---

## 3. Goal

**One master field list → one packer + one unpacker, both driven by that list.** Adding a field means
one entry; both directions get it; drift becomes impossible. (Ron's design, 2026-09-22.)

---

## 4. The master field list

A single ordered list; each entry describes one wire field:

```
{ app: 'userNote', wire: 'note', default: undefined }      // simple rename
{ app: 'tags', default: undefined }                        // wire name == app name
{ app: 'onWishlist', pack: b => isWishlisted(b),           // computed on the way out
                     unpack: (item, book) => …normalize }  // normalized on the way in
{ app: 'store', packSkip: true, default: 'Amazon' }        // unpack-only (never written)
```

- Default entry behavior: pack copies `book[app] → wire[wire]`; unpack copies `wire[wire] → book[app]`
  falling back to `default`.
- **Per-field rules carry the asymmetries as data** (Ron's insight — this is what keeps the list, not
  the code, in charge):
  - **renames (wire aliases):** `note`↔`userNote`, `authors`↔`author`, `reviewCount`↔`ratingCount`,
    `acquisitionDate`↔`acquired`, `priceAsOf`↔`priceFetchedAt`.
  - **computed / normalized:** `onWishlist` (packed via `isWishlisted`), `ownershipType` (fallback +
    normalize on unpack).
  - **unpack-only:** `store` (always "Amazon"), the ancient `isOwned` legacy format.
  - **special unpack:** `binding` ("Kindle eBook" → blank, the FORMAT-POLICY filter), price strings →
    numbers (`parsePrice`).
- **Fields this restores that Save/Restore drops today:** `dateAdded`, `orphanStatus`,
  `orphanCheckedDate`, `collectionTags`, `collectionTagSeen`, `isDeleted`/`deletedAt`/
  `deletedFromFolderIds`, `publicationDate`, `seriesTotal`, `hasEnrichedData`.

**Backup is lossless:** every app-authored *and* Amazon-sourced field is packed, so a restore is
complete without needing a re-fetch. (This corrects an earlier framing — Amazon-sourced fields are
NOT excluded from the backup.)

The small **collections sub-list** (`asin/readStatus/collections`, currently duplicated at ~5601/~5742)
is unified the same way — its own tiny field list, or folded in as a sub-section.

---

## 5. Testing — the round-trip, two callers

The invariant is **idempotency**, not naive equality (a few fields are *healed* on the first pack — a
stale wishlist flag gets corrected — so "pack→unpack == original" would false-alarm):

> pack → unpack → pack again ⇒ the two packed forms are identical.

Healing happens once; the second pass must be stable. This catches any lost or altered field without
crying wolf.

- **Developer test** (`test/serialization.test.js`, Node): a sample corpus covering every combination
  (owned / wishlist / sample; `userEdited` set vs not; cleared-null user fields; trash state; orphan
  flags; collection tags; every rename) — idempotency + a few exact-value assertions, and an
  old-vs-new equivalence check for fields that must not change value.
- **In-app self-check** (Ron 2026-09-22): on **localhost only, once per version change**
  (`ORGANIZER_VERSION` moved), run the idempotency check over the **real library** and, on any
  mismatch, a loud console error + a localhost popup naming the book/field (same style as the
  field-schema validator). This is the *mechanism* — it runs itself, on real data, without anyone
  remembering to run the dev test (RW has no CI). Ships inert off-localhost.
- **Both callers share one `roundTripCheck(book)` function** in the module.

---

## 6. Module & dependencies

- New shared classic-script module **`serialization.js`** (Node-exportable, like `bookMerge.js`), loaded
  before `readerwrangler.js` and `mobile.js` so both can use the one list.
- It needs three helpers that live in `uiHelpers.js` — `isWishlisted`, `normalizeBook`, `parsePrice` —
  which currently have **no Node export**. Add an export guard to `uiHelpers.js` (browser-safe, matches
  `bookMerge`/`organizeEngine`) so the module and its test can reach them.

---

## 7. Staging (commits on this branch)

1. **The module, unwired** — master list + packer + unpacker + `wireRoundTripCheck` + the developer
   test. No app changes; get the test green first (characterization before change).
2. **Wire the packer in** — `exportBackup` and `buildDeviceStatePayload` both call the packer (collapse
   to one packer; **fixes the Save/Restore data loss**). Verify with a real Save→Restore.
3. **Wire the unpacker in** — `loadLibrary` uses it; the legacy v1.x `amazonData` branch and the
   legacy-file handling are **removed** in favor of one top-level unsupported-file guard (§10).
   Add the localhost/version-gated in-app self-check.
4. **Mobile** — `mapBackupBook` adopts the shared unpacker.

Each step verified with the pack→unpack round-trip (the repro→fix→verify rhythm we've been using).

---

## 8. Relationship to the alpha.2–5 hardening already shipped on this branch

- alpha.2 merge-completeness chokepoint, alpha.3 collectionTags user-owned, alpha.4 sticky
  `orphanStatus` — all stand (they're about the *merge*, a different layer).
- alpha.5 added `collectionTags`/`collectionTagSeen`/`orphanCheckedDate` to `buildDeviceStatePayload` +
  the parser as an ad-hoc fix. This wire-schema work **subsumes** that ad-hoc addition into the single
  list — alpha.5 stays as-is until step 2/3 replace those hand-edits with the list-driven packer/unpacker.

---

## 9. Assumptions (and how each was verified) — dogfooding the principle-to-hook idea

- **`buildDeviceStatePayload` is the more-complete packer** — verified by reading both packers and
  diffing the field sets (it has the 8 `exportBackup` lacks).
- **`loadLibrary` handles both import and restore** — verified: `isBackupRestore = organizationFromFile
  !== null` (~6373) selects merge vs save-as-is; both go through `processedBooks`.
- **The Save/Restore loss is real** — verified live (collectionTagSeen 1470→0), not inferred.
- **`isWishlisted`/`normalizeBook`/`parsePrice` live in `uiHelpers.js`** — verified by grep.
- **`uiHelpers.js` lacks a Node export** — verified (no `module.exports`; only `bookMerge` and
  `organizeEngine` have one). ⇒ add one.
- **UNVERIFIED, to confirm during build:** the exact unpack default for every field (some are `''`, some
  `null`, some `[]`), and whether `mapBackupBook` maps to the same book shape as the desktop unpacker or
  a mobile subset. The round-trip test is what pins these.

---

## 10. Decisions (resolved 2026-09-22)

- **Legacy Amazon-API format (v1.x)** = the `else` branch of the unpacker (a *code* branch, not git):
  ancient files — from **before schema 2.0 (v4.0.0, ~Dec 2025), before the V4 "Column App", and before
  Book Explorer (V5, ~early 2026)**: ReaderWrangler's *original* v1.x format, predating essentially all
  of the current architecture — where each item carried a raw Amazon GraphQL blob (`item.amazonData`),
  fields dug from nested paths
  (`amazonData.data.getProduct.title.displayString`). Verified: **no current code writes `amazonData`**
  (only the reader + the dead `v4/` archive), and per GoatCounter there's no realistic holder of such a
  file. **Decision (Ron 2026-09-22): don't adapt it — remove the legacy per-item branch AND the
  legacy-v1.x-file handling entirely, and add ONE top-level guard:** if a loaded file isn't schema 2.x
  (or any item carries `amazonData`), refuse with an honest, jargon-free message —
  *"This file was saved by a very old, unsupported version of ReaderWrangler and can't be restored."*
  No re-save-in-old-version advice (there's no version picker on GitHub Pages, and old data wouldn't
  survive current code). The master-list unpacker then handles only the current schema — clean.
- **Mobile:** fold `mapBackupBook` into the shared unpacker **now** (step 4). ✓
- **In-app self-check:** gated on **localhost AND version-change** (both); no extra Save/Restore
  trigger. ✓
- **Naming:** **"serialization"** — it covers the wire *and* the backup file. This doc =
  `SERIALIZATION.md`, module = `serialization.js`. ✓
