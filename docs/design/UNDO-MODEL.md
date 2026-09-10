# Undo Model — the three levels, the dialog fence, and what is deliberately NOT undoable

_Settled 2026-09-07 (Ron + UX review, ratified after full exploration — do not relitigate).
Extends the 7.6.0 "undo tells the truth" doctrine (undo-integrity trilogy) and the 6.13.1
forced-toast rule (every undo/redo shows a labeled toast)._

## The three levels of editing, and where undo lives

| Level | State | Undo mechanism | Why |
|---|---|---|---|
| 1. Within a field | Keystrokes (invisible once typed over) | **Browser-native text undo** (per input; edit fields stopPropagation so Ctrl+Z stays native) | Undo exists to recover state you can't see or directly reach |
| 2. Within the dialog, across fields | Form state — **fully visible and directly editable** | **None by design.** The form IS the undo UI (click the field, fix it); **Cancel** is the transaction rollback | Convention (Word/Photoshop dialogs, settings pages, web forms): transactional forms get per-input undo + Cancel, never a chronological multi-field stack. A chronological stack here would violate the visibility razor — in a form people think *per-field*, not *in edit order*; Ctrl+Z reverting "whichever field I touched last" is a hidden-order mutation inside a visible surface. Apps with stepwise micro-undo (Lightroom, Figma) get it by having NO form session — every tweak commits instantly to the global stack. RW's dialog is a transaction; Cancel is its undo |
| 3. Global (post-Save) | Committed changes | **Global undo stack.** One Save = **one atomic step** (all fields changed that session revert together — matches the transactional frame: Save is one decision, so undoing it is one) | Per-field popping post-save would leave half-reverted state you can't inspect from cover view |

**Residual gap in level 2, and its correct future fix**: overwrite a field, make other wanted
changes, then regret the overwrite without remembering the original — Cancel is too nuclear.
The fix, IF the sting is ever felt in practice, is **per-field revert** (↺ beside any field
differing from its saved value; VS Code-settings precedent) — order-free, targeted, visible.
NOT a chronological stack. Filed as optional polish, deliberately unbuilt (7 fields; Cancel +
retype covers nearly everything).

## The dialog undo fence (7.8.0-alpha.4)

**Principle** (the session's recurring razor): *undo must never mutate state you didn't
knowingly target* — and behind a modal, pre-dialog actions are exactly that. Same disease as
the discarded invisible-Reset proposal. A toast is narration, not visibility.

- **On dialog open** (null → book, one chokepoint): record undo AND redo stack depths — the fence.
- **While the dialog is open (view mode)**: Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y operate **only above
  the fence** — i.e., on actions taken during this book-viewing session. The open dialog updates
  live (EDIT_BOOK undo/redo already refresh modalBook).
- **◀ ▶ navigation resets the fence** (each book = a new session). A→B→A: A's earlier edits are
  unreachable in-dialog even though theoretically allowable — consistency beats cleverness.
  One rule: *the fence scopes undo to the current book-viewing session, period.*
- **Blocked key ≠ dead key**: below-fence Ctrl+Z shows an info toast — "Nothing to undo from
  this dialog — close it to undo earlier actions." (An affordance nobody can perceive isn't an
  affordance; a key that silently eats input reads as broken.)
- **Edit mode: global undo fully blocked** (Ctrl+Z belongs to text there; in-field native undo
  already works via stopPropagation).

## What survives dialog close: EVERYTHING (explored and settled 2026-09-07)

Discard-on-close was proposed (cover view can't show fields reverting) and **rejected**:
- It removes the safety net entirely from the app's primary edit path — the user who realizes
  the mistake after closing has no recourse.
- Post-close Ctrl+Z undoes exactly the action the user knows they just did — self-initiated
  recovery of a *known* action. The fence already solved the real danger (popping past a
  context boundary unknowingly).
- The visibility bar it applies is one bulk edits (equally cover-invisible, always undoable)
  have never met — applied consistently it dismantles the whole undo system.
- Convention is lopsided: document apps (Word/Photoshop/Figma) land dialog commits as one
  undoable step on the global stack; the famous discard-style example is Excel's stack-clearing
  dialogs — a widely-hated anti-pattern, not a convention.
- 7.6.0 doctrine: history dies when it would LIE (purged books, replaced libraries) — not when
  it's inconvenient to visualize.

## Toast naming: every undo/redo names its target (alpha.4/5); action toasts = batch item 11

- Single-book actions: the book title ("Undone: edit to 'Bitter Gold Hearts'").
- Bulk actions: honest aggregate ("Undid price goal for 4 books").
- Folder/list actions: the folder/list name.

**Scope note (2026-09-08)**: Ron's original ask was ALL toasts, everywhere. Undo/redo toasts
shipped first (the recordAction chokepoint made them one auditable pass — alpha.4, completed by
a mechanical zero-missing audit in alpha.5 after a missed second TOGGLE_HIDE site). The ACTION
toasts (scattered showToast calls, no chokepoint) are deliberately deferred, NOT dropped —
**filed as ownership-honesty batch item 11**: single-target action toasts name the target,
bulk keep counts, explanatory clauses survive (e.g. the load-bearing "purchased" in the
hide-instead toast). This split was originally made silently — caught, analyzed, and turned
into the scope-narrowing rule (memory: feedback_scope_narrowing).

## The universal dialog fence — DIALOG_POLICY registry (7.10.1-alpha.6, ratified 2026-09-09)

Ron's Tag Manager rename (Adult→Mainstream, Ctrl+Z undid an earlier BOOK action instead)
exposed that the fence covered only the book dialog; every other dialog silently forwarded
Ctrl+Z to the global stack — the outlawed third state.

**The rule — keystroke scope consistency (Ron's formulation)**: *while a dialog is open, every
keystroke applies to the dialog or to nothing.* Ctrl+C copying dialog text while Ctrl+Z reaches
the world behind it is two scopes on adjacent keys — rejected. This also collapsed the proposed
fence/block/allow taxonomy to ONE policy:

- **Every dialog is fenced.** The fence stamps when the first dialog opens (rising edge of the
  registry), undo/redo refuse to pop below it. A dialog that records actions while open (book
  detail, Tag Manager) gets scoped undo above the fence for free; one that records nothing
  (Status History, bulk pickers, confirms) yields the info toast. No categories to pick = no
  policy to get wrong when adding a dialog.
- **The registry** (`anyDialogOpen`, readerwrangler.js) is THE list of dialogs; `dialogUp()` =
  registry ∪ imperative overlays. It drives: the fence, book cut/copy/paste/Delete guards,
  Ctrl+A, Alt+←/→ nav, and Esc's selection/clipboard clearing (Esc that closes a dialog no
  longer wipes the cut clipboard underneath). Audit additions: relaySetupOpen, dupReviewOpen,
  tagFromCollectionsOpen were missing; imperative overlays (showConfirm/Input/Info/Choice/
  Progress/DeleteWarning) are detected by DOM class `rw-imperative-overlay` and block undo/redo
  outright (they stamp no fence).
- Nested dialogs keep the outer fence (same away-from-main-view session); book-dialog ◀▶ nav
  still re-stamps.

## Coverage doctrine (7.10.1-alpha.6): gaps, not coverage, cause mis-undo

The feared scenario "user hits Ctrl+Z, something OLDER than expected reverts" happens exactly
when the most recent gesture was NOT recorded — undo reaches past it. Total coverage of data
mutations is therefore the fix, not the risk. Convention split (ratified): **data mutations
all undoable; view state (selection, scroll, collapse, filters, theme) and explicitly-confirmed
permanent deletion are not.**

- **Renames** (the class that bit): folder (inline ×4 + Properties dialog), tag, Search,
  Book List — all route through ops-layer chokepoints (`renameFolder`/`renameTag`/
  `renameSearch`/`renameBookList`/`editFolderProps`), each undoable + receipt toast.
  Naming a just-created folder/list folds into its CREATE record (Finder convention: one
  undo removes the named thing). Inline editors double-fire Enter+blur from the same stale
  render — absorbed by a 500ms keyed guard, not state comparison.
- **Searches**: create (SEARCH_CREATE) and delete (SEARCH_DELETE, 2 sites → `deleteSearch`)
  undoable with receipts, matching Book Lists.
- **Reorders** (tags / Searches / Book Lists): undoable and SILENT — REORDER_FOLDER convention,
  a drag you just watched needs no receipt.
- Tag creation leaving an unused registry entry on undo remains the ratified alpha.4 decision
  (harmless).

## The dialog goes FULLY transactional (ratified 2026-09-10; build queued as 7.11.0)

**Defect found (Ron)**: during edit mode, the instant controls (rating stars, Buy-at price-goal
buttons, tag input) stayed live, intermixed with staged form fields — two commit semantics in
one surface, indistinguishable to the user.

**Decision — Ron's model, adopted after genuine pushback**: *inside the dialog, Edit/Save is
the only way anything changes (one undo per Save); everywhere else, changes are instant
commands (one undo each).*

- Dialog view mode: rating / price goal / tags become read-only displays. Edit mode: they join
  `editBookFields` as staged fields — Cancel discards, Save commits all as the one atomic
  EDIT_BOOK step. New-tag creation happens at Save.
- Fields vs commands: only DATA FIELDS join the form; commands stay live in both modes (Share,
  Amazon link, Status History, ◀▶ nav). Build begins with an enumeration pass classifying every
  interactive dialog control — explicit, not vibes.
- Quick access replaces dialog instant-set: line-view cell popups for Price Goal and My Rating
  (click the cell → preset goals/custom, or the star row); right-click menus unchanged
  (instant, atomic, undoable each).

**Why the counter-proposal (freeze instant controls only during edit mode) lost**:
1. **Context-keying (Ron's principle, now doctrine)**: users build commit semantics from the
   interaction CONTEXT — "right-click menu" vs "form with Save/Cancel" — not from field
   identity. Same-field-different-surface is not a real inconsistency; mixed semantics within
   one surface is. Don't apply the formal per-field consistency test to cross-surface flows.
2. **Precedent alignment**: OWNERSHIP-MODEL.md §4 already made Ownership and Format
   edit-in-place staged fields. The instant controls were the anomaly in the dialog's own
   newest pattern; this finishes that design rather than fighting it.

This supersedes the level-1/2/3 table's premise that some dialog fields commit instantly —
once built, level 2 covers EVERY field and the "three levels" collapse to: native text undo
in-field, Cancel/Save as the transaction, one global undo step per Save.
