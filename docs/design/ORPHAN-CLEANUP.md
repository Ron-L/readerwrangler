# Orphan cleanup — durable "books no longer in your Amazon library"

**Feature**: surface books the fetcher's scan found gone from Amazon, and let the user remove them —
**as a durable library status, not a one-shot import-time moment.**
**Status**: DESIGN — for Ron's red pen (2026-09-22). Build = expanded 7.16.0 (branch
`feature/orphan-cleanup-dialog`).
**Supersedes**: `archive/ORPHAN-DETECTION-RECYCLE-BIN.md` (2026-01-07; its `loadId` detection was
replaced by the fetcher-side scan — but its **lifecycle model was lost in that swap**, which is the
root of the miss this doc corrects).

---

## 1. What went wrong (the scope miss, honestly)

7.16.0-alpha.1 shipped an orphan **dialog** that reads live `book.orphanStatus === 'orphan'` — correct
as far as it goes. But testing showed orphans are a **one-shot**: dismiss the dialog or re-import, and
they vanish. Two compounding causes:

1. **`orphanStatus` is not durable.** bookMerge.js declares (line 26): *anything not in the ownership
   registry defaults to incoming-wins.* `orphanStatus` isn't listed, so it silently defaulted to
   incoming-wins. The orphan flag lives only in the fetcher's transient follow-up run; once that run is
   consumed, the next import's incoming copy (plain canonical, no flag) **overwrites the local flag back
   to nothing.** A backup restore wipes it the same way. Same class as the clear-then-resurrect bug
   bookMerge.js was built to kill — a stale echo clobbering real state.
2. **The lifecycle was never modeled.** The archived design had `isKeptOrphan` (accept an orphan, never
   re-prompt), Keep/Delete/**Ignore**, and an explicit **"Re-prompt? Never / Next load"** column — i.e.
   it modeled an orphan as a *persistent status with transitions*. When detection moved to the fetcher
   scan, that lifecycle didn't come along, and alpha.1 was built from the one-line TODO ("orphan-cleanup
   step **at import**") + the current code, not from the historical design. Import-centric framing +
   an unverified assumption that the field persisted = a transient where a durable status was needed.

**The mechanisms that prevent recurrence** (not a promise — a structure): §3 (durability by freshness),
§4 (the merge-completeness chokepoint that forces a decision for every field), and modeling the
lifecycle as states here in §2 (Ron's legal-states principle).

---

## 2. The orphan lifecycle (model the states, not a moment)

```
                 fresh scan: ASIN absent
   verified  ────────────────────────────▶  orphan (detected)
      ▲                                         │
      │ fresh scan: ASIN present again          ├─ user: Keep  ──▶ kept-orphan (accepted; never re-prompt)
      │ (book returned to Amazon)               ├─ user: Delete ─▶ trashed ──▶ permanently deleted
      └─────────────────────────────────────────┘  (also clears if it returns)
```

- **verified / orphan** — set only by a fresh fetcher scan (carries `orphanCheckedDate`).
- **kept-orphan** — the user accepts it (a returned book they still want organized). A **user-owned**
  decision: never re-nag, survives import. (Revived from the archive's `isKeptOrphan`.)
- **trashed / permanently deleted** — existing trash + `permanentlyDeleteBooks`.
- A book that **returns to Amazon** (fresh scan sees the ASIN) goes back to `verified` and drops out of
  the orphan surfaces automatically.

---

## 3. Durability model — sticky by freshness

`orphanStatus`/`orphanCheckedDate` become a **special-cased pair** in `mergeBookFields` (like `binding`):
the copy with the **newer `orphanCheckedDate` wins**; a missing date sorts oldest.

- Fresh scan (orphan *or* verified) always wins → a returned book clears correctly.
- A stale re-import or same-payload echo (older/absent date) **cannot downgrade** a flagged orphan.
- This is the guest-guard monotone-stamp pattern (MULTI-INSTANCE §3) applied to one more field.

`isKeptOrphan` is added to `BOOK_FIELD_OWNERSHIP` as **`'user'`** (local always wins — the user's
acceptance survives every import, and a fetch can't un-accept it).

**Rejected alternative — a separate top-level orphan/ASIN list.** Survives even a full restore, but it's
a parallel structure that drifts from the book records (a book deleted while still in the list). The
sticky flag is less code and can't drift; a re-fetch re-discovers orphans after a restore anyway.

---

## 4. The structural fix — merge-completeness chokepoint (Ron's "Strong" option)

**Why this field slipped through:** `orphanStatus` is in `KNOWN_BOOK_FIELDS` (the schema validator) but
not in `BOOK_FIELD_OWNERSHIP` (the merge registry). The registry lists only fields needing a
non-default rule; everything else **falls into incoming-wins with no one ever deciding it.** That's a
fail-open default — the one field you forget gets silent (often wrong) behavior. Exactly the loose-state
antipattern the legal-states principle warns about.

**The fix:** every field in `KNOWN_BOOK_FIELDS` must carry an **explicit merge decision** — including an
explicit `'amazon'` (incoming-wins) class, and `'identity'` / `'special'` / `'soft-delete'` for the
fields handled outside the per-field loop. Then a **gate test asserts the two sets are identical**
(bijection): a field added to the schema without a merge decision fails the build; a decision for a
field not in the schema fails too. Adding a book field without deciding how it merges becomes
**unrepresentable** — the mechanism, not a comment.

- **Weak option (a reminder comment) is rejected** — documentation doesn't prevent recurrence (the
  meta-principle). Only the completeness test does.
- Open question for Ron: ship this chokepoint **with** 7.16.0 (it's what makes the fix trustworthy), or
  as its own small bookMerge-hardening release just before? It touches every field's classification, so
  it wants its own careful pass + gate test either way.

---

## 5. Entry points (deal now **and** later — Ron's "both-ish", ratified as UX)

Two moments, two surfaces, one shared dialog (the alpha.1 dialog, unchanged in shape):

1. **Deal now — import-done summary.** The import dialog gains a line + button:
   *"N books are no longer in your Amazon library — [Review]"*, and text: *"Review now, or find them any
   time under File → Removed books."*
2. **Deal later — persistent, live-count-driven.**
   - The 🧹 nudge is driven off the **live orphan count**, not a one-shot boolean: it self-appears when
     orphans exist, self-clears when none remain (dealt with, kept, or returned). No stale banner.
   - A **menu item** opens the dialog any time: **File → Removed books…** (short form; the dialog title
     stays "Books no longer in your Amazon library"). Open question: File vs a Library menu.

**Copy rule:** never the word "orphan" in the UI (internal jargon) — "removed" / "no longer in your
Amazon library". The dialog already complies.

**Dialog additions:** a **Keep** action per book/group (sets `isKeptOrphan`, drops it from the surfaces
without deleting) alongside the existing permanent-delete. Kept books are reachable later via the normal
filters, not the removed-books surfaces.

---

## 6. Scope & non-goals — SPLIT into two releases (revised 2026-09-22)

This design is delivered in **two** parts, because the merge/durability pieces are data-integrity
HARDENING while the rest is orphan UI. (The split was decided when testing revealed the original dialog
was a one-shot and the root cause lived in the merge — see §1.)

**A. 7.16.0 — data-integrity / merge hardening** (branch `feature/orphan-cleanup-dialog`, in flight):
the merge-completeness chokepoint (§4, shipped alpha.2); the collectionTags/collectionTagSeen ownership fix
(alpha.3) + its push-payload second half; **sticky `orphanStatus`** (§3, freshness-guard); the 🛡️ merge-log
→ summary line (Option C). The orphan **dialog** (built as alpha.1) is REVERTED off this branch before
merge — it's an unfinished feature, not hardening.

**B. Later — orphan cleanup FEATURE** (its own branch, ~7.17.0): the dialog (rebuilt from the reverted
alpha.1 + this doc), `isKeptOrphan` revival (§2/§5), the live-count nudge, File → Removed books entry, and
the import-summary line + Review button (§5). Builds ON part A — durable `orphanStatus` is the foundation
the UI needs, which is exactly why it goes in the hardening first.

**Out of both (for now):** a Recycle-Bin virtual column (the app already has Trash); cross-device
propagation of `isKeptOrphan` (user-owned = local-wins, MULTI-INSTANCE §5); auto-empty policies.

---

## 7. Test invariants (pre-launch gate — bookMerge.test.js)

- **Stale echo can't clear an orphan:** merge(local orphan @ t2, incoming verified @ t1<t2) → stays orphan.
- **Fresh scan clears a returned book:** merge(local orphan @ t1, incoming verified @ t2>t1) → verified.
- **Kept survives import:** merge(local isKeptOrphan, incoming without it) → kept.
- **Completeness (§4):** `Set(KNOWN_BOOK_FIELDS) === Set(merge-decision map keys)` — the chokepoint.

---

## 8. Related

- `bookMerge.js` — the merge registry + the new special-case + completeness map.
- `readerwrangler.js` — nudge (live count), dialog (Keep action), import summary, File menu.
- `amazon-library-fetcher.js` — sets `orphanStatus`/`orphanCheckedDate` (unchanged; the dev injector is
  temporary, stripped before release).
- `docs/design/MULTI-INSTANCE.md` §3 — the guest-guard freshness pattern this reuses.
- `docs/PRINCIPLES.md` — legal-states (model the lifecycle) + Law 10 (merge ownership).
