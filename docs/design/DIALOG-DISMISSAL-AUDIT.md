# Dialog & Popover Dismissal — Audit + System Design

**Status:** Design proposal + audit of record. No code changed yet.
**Written:** 2026-09-16 (overnight deep-dive, feature/folder-ordering working tree).
**Decision pending (Ron):** tackle now vs. design-doc + TODO; and which primitive design.
**Origin:** the 7.14.0 Share dialog shipped unfenced/undismissable (a recurrence the 7.10.1 audit
should have prevented), and a proper mechanical comb then found the defect is a *class*, not a
handful of dialogs — including a live "orphaned popup" bug in Auto-Organize.

---

## 0. TL;DR

- The overlay layer has **three unrelated Esc mechanisms** and a **hand-maintained keystroke
  fence** (`anyDialogOpen` OR-chain). New overlays are born correct only if a human remembers a
  4-point checklist. That reliance has now failed twice in one release cycle.
- The comb found: **1 live orphan** (AutoOrg preview Esc leaves a child popup floating), **3
  modals outside the keystroke fence** (`restoreConfirm` the serious one — destructive + no Esc +
  no backdrop), **6 menus/dropdowns with no Esc at all**, and **latent close-drift** in the
  wizard and relay-setup families (masked today only by z-order).
- Root cause is structural: overlays are rendered as **state-gated siblings**, so a parent close
  cannot clean up its children, and every dismissal path hand-rolls its own state-clearing.
- **Recommended fix:** a minimal **overlay-layer registry** (a module-level stack) behind two
  primitives, `<Dialog>` (modal) and `<Popover>`/`<Menu>` (light-dismiss). Each self-registers on
  mount and deregisters on unmount, so the fence, Esc-ordering, backdrop, ✕, and cascade-close all
  become *structural* — a new overlay **cannot** be born non-compliant. This is exactly the shape
  every mature overlay library converged on (Radix `DismissableLayer`, React-Aria overlay stack,
  Headless UI nested-Dialog context).
- **Recommended sequencing:** ship a tiny **7.14.2** now that (a) fixes the one live orphan with a
  one-line change and (b) fences the 3 unfenced modals — immediate safety, near-zero risk. Then
  build the primitive as its **own branch**, migrating overlays incrementally. Do *not* big-bang
  ~40 overlays in one release.

---

## 1. Why this exists (the recurrence)

An **audit** fixes the instances that exist the day it runs; only a **rule** stops the class from
recurring; and a **rule is only as reliable as remembering to run it.** The CLAUDE.md "new dialog
checklist" (register in `anyDialogOpen`; add to `handleModalEsc`; ✕; backdrop) is prose — a
reminder, not a mechanism — and it was skipped when the Share dialog was built the same night it
was written. The durable fix is a **chokepoint that makes non-compliance impossible**, not a
better-remembered checklist. That is the whole motivation for a shared primitive.

---

## 2. Audit of record (mechanical comb, file:line evidence)

Anchors: registry `anyDialogOpen` = **6872** (consumed via `anyModalOpenRef` → `dialogUp()` at
**839**, gating book cut/copy/paste/delete, Ctrl+A, Alt-nav); layered Esc `handleModalEsc` =
**6898–6939**; blanket Esc `handleEscKey` = **4381–4399**; `closeBookModal` = **6617**;
`closeAutoOrgPreview` = **8725**.

### 2a. Full overlay table

| Overlay (gate state) | Render | Type | In fence | Esc | Backdrop | ✕ | Input | Parent (today) |
|---|---|---|---|---|---|---|---|---|
| modalBook | 13520 | modal | ✅ | ✅ 6917→closeBookModal | ✅ | ✅ 13598 | ✅ edit | top |
| showBulkPriceModal | 13181 | modal | ✅ | ✅ 6922 | ✅ | ? | ✅ | top |
| showBulkEditModal | 13258 | modal | ✅ | ✅ 6921 | ✅ | ? | ✅ | top |
| tagManagementOpen | 17787 | modal | ✅ | ✅ 6923 | ✅ | ? | ✅ | top |
| wizardModalOpen | 11615 | modal | ✅ | ✅ 6924 | ✅ | ✅ 11627 | ✅ | top |
| wizardHelpOpen | 11830 | modal | ✅ | ✅ 6911 | ✅ | ? | — | wizard (sibling) |
| wizardPreviewMode | 11889 | modal | ✅ | ✅ 6910 | ✅ | ? | — | wizard (sibling) |
| wizardResultsOpen | 11965 | modal | ✅ | ✅ 6909 | ✅ | ? | — | wizard (sibling) |
| folderPropertiesDialog | 20335 | modal | ✅ | ✅ 6925 | ✅ | ? | ✅ | top |
| resetConfirmOpen | 11435 | modal | ✅ | ✅ 6931 | ✅ | ? | — | top |
| statusModalOpen | 10697 | modal | ✅ | ✅ 6932 | ✅ | ? | — | top |
| aboutDialogOpen | 11514 | modal | ✅ | ✅ blanket 4384 | ✅ | ? | — | top |
| shortcutsDialogOpen | 11540 | modal | ✅ | ✅ blanket 4385 | ✅ | ? | — | top |
| howToDialogOpen | 11585 | modal | ✅ | ✅ blanket 4386 | ✅ | ? | — | top |
| relayHelpOpen | 11373 | modal | ✅ | ✅ 6933 (guarded) | ✅ | ? | — | relaySetup (sibling) |
| lastCopyDialogData | 13415 | modal | ✅ | ✅ 6930 | **❌ no backdrop** | ? | — | top |
| autoOrgPreview | 12289 | modal | ✅ | ⚠️ 6907 **partial** | ✅→closeAutoOrgPreview | ✅ 12311 | — | top |
| toastHistoryOpen | 20537 | dropdown+scrim | ✅ | ✅ 6903 | ✅ | — | — | top |
| relaySetupOpen | 11038 | modal | ✅ | ✅ 6935 | ✅ | ✅ 11044 | ✅ | top |
| dupReviewOpen | 10969 | modal | ✅ | ✅ 6927 | ✅ | ? | — | top |
| tagFromCollectionsOpen | 12773 | modal | ✅ | ✅ 6928 | ✅ | ? | — | top |
| shareEmailChoice | 20449 | modal | ✅ | ✅ 6904 | ✅ | ✅ 20452 | — | modalBook▸share **or** top (dual) |
| **newFolderHiddenAlert** | 11476 | modal | **❌** | **❌** | **❌** | ✅ 11480 | — | top |
| **corruptionRecovery** | 12042 | modal | **❌** | **❌** | ✅ | ❌ | — | top |
| **restoreConfirm** | 12073 | modal | **❌** | **❌** | **❌** | ❌ | — | top |
| **autoOrgFileUnder** | 12552 | modal (child) | via parent | ⚠️ input-only 12560 | ✅ | ❌ | **✅ 12556** | autoOrgPreview (sibling) |
| **autoOrgSrcPopup** | 12602 | popover | via parent | **❌** | ✅ | ❌ | — | autoOrgPreview (sibling) |
| autoOrgMenu | 12645 | context-menu | via parent | ✅ 6906 | ✅ | ❌ | — | autoOrgPreview (sibling) |
| autoOrgHover | 12688 | tooltip | — | cleared by 6907 | n/a | — | — | autoOrgPreview (sibling) |
| shareDropdownOpen | 13556 | dropdown | via modalBook | ⚠️ over-closes book modal | ✅ | ❌ | — | modalBook |
| editBookSeriesDropdownOpen | (edit) | dropdown | via modalBook | ✅ 6913 | — | — | ✅ | modalBook (edit) |
| bulkEditSeriesDropdownOpen | (bulk) | dropdown | via bulkEdit | ✅ 6920 | — | — | ✅ | showBulkEditModal |
| **folderSortMenuOpen** | 14901 | dropdown | **❌** | **❌** | ✅ | ❌ | — | top |
| **folderSortPickerOpen** | 15921 | dropdown | **❌** | **❌** | ✅ | ❌ | — | top |
| **rightPaneContextMenu** | 18241 | context-menu | **❌** | **❌** | ✅ | ❌ | — | top |
| **folderContextMenu** | 18273+ | context-menu | **❌** | **❌** | ✅ | ❌ | — | top |
| **saveResultsMenuOpen** | 10596 | dropdown | **❌** | **❌** | ✅ | ❌ | — | top |
| relayManifest | 9383 | banner (non-modal) | — | — | n/a | — | — | top |
| bookTooltip | 18118 | tooltip | — | — | n/a | — | — | top |
| historyOpen (SearchInput) | 649 | dropdown | — | — | click-out | — | — | SearchInput |
| toolbar/filter dropdowns ×~12 | (4381 handler) | dropdowns | — | ✅ blanket 4381 close-all | click-out | — | some | top (menu bar) |

(`?` = ✕ presence unverified — not load-bearing for the design. `relayManualCreds` is a *section
inside* relaySetup (11093), not a separate overlay; it unmounts with the parent — no orphan risk.)

### 2b. The four findings

1. **CONFIRMED LIVE ORPHAN.** `autoOrgPreview`'s Esc branch (6907) hand-rolls
   `setAutoOrgPreview(null); setAutoOrgSel(...); setAutoOrgHover(null)` and **omits
   `autoOrgSrcPopup` and `autoOrgFileUnder`**. Pressing Esc while either child is open dismisses
   the preview and leaves the child floating on an empty library. The backdrop/✕/Cancel paths all
   correctly call `closeAutoOrgPreview()` (8725, which clears everything) — only Esc drifted.
   **One-line fix: Esc calls `closeAutoOrgPreview()`.**
2. **UNFENCED MODALS.** `restoreConfirm` (12073) — destructive (replaces the library), **no Esc,
   no backdrop, not in the fence**; Ctrl+X/Delete/Ctrl+A/undo leak beneath it. `newFolderHiddenAlert`
   (11476) and `corruptionRecovery` (12042) — informational, low severity.
3. **NO-ESC MENUS.** `folderContextMenu`, `rightPaneContextMenu`, `folderSortMenuOpen`,
   `folderSortPickerOpen`, `saveResultsMenuOpen` — click-outside only. `shareDropdownOpen`
   *over-closes* (Esc shuts the whole book dialog rather than just the dropdown).
4. **LATENT CLOSE-DRIFT.** The wizard family (`wizardModalOpen` → help/preview/results) and
   `relaySetupOpen` → `relayHelpOpen` have no encapsulated closer; parent close paths clear only
   the parent. Masked today by z-order, but a *programmatic* wizard close (~9016) with a sub-dialog
   open would orphan it.

---

## 3. The parent/child map (the tree the stack must model)

```
TOP-LEVEL MODALS (attention-capturing; must fence keystrokes)
  modalBook
    ├─ shareDropdownOpen (popover)         → (Email to a Friend) → shareEmailChoice*
    ├─ editBookSeriesDropdownOpen (dropdown, edit mode)
    └─ [context submenu]
  showBulkEditModal
    └─ bulkEditSeriesDropdownOpen
  showBulkPriceModal
  wizardModalOpen
    ├─ wizardHelpOpen        (currently siblings, not nested)
    ├─ wizardPreviewMode
    └─ wizardResultsOpen
  relaySetupOpen
    └─ relayHelpOpen         (currently sibling)
  autoOrgPreview
    ├─ autoOrgMenu   (context-menu)   (currently siblings, not nested)
    ├─ autoOrgSrcPopup (popover)      ← ORPHANS on Esc
    ├─ autoOrgFileUnder (dialog+input) ← ORPHANS on Esc
    └─ autoOrgHover  (tooltip)
  folderPropertiesDialog · tagManagementOpen · dupReviewOpen · tagFromCollectionsOpen
  statusModalOpen · resetConfirmOpen · lastCopyDialogData · toastHistoryOpen
  aboutDialogOpen · shortcutsDialogOpen · howToDialogOpen
  shareEmailChoice*  (top-level when opened from a multi-select; child of modalBook▸share otherwise)
  ❌ restoreConfirm · ❌ newFolderHiddenAlert · ❌ corruptionRecovery   (unfenced)

TOP-LEVEL LIGHT-DISMISS (no backdrop dimming; click-outside; no Esc today)
  folderContextMenu · rightPaneContextMenu · folderSortMenuOpen · folderSortPickerOpen
  saveResultsMenuOpen

TOOLBAR / FILTER DROPDOWNS (blanket close-all on Esc via handleEscKey 4381)
  openMenuBar · statusDropdownOpen · tagsDropdownOpen · typesDropdownOpen · morePanelOpen
  collectionsDropdownOpen · amazonRatingDropdownOpen · myRatingDropdownOpen · seriesDropdownOpen
  dateDropdownOpen · sortPickerOpen · SearchInput historyOpen

NON-INTERACTIVE (no dismissal concern)
  bookTooltip · autoOrgHover · relayManifest (banner has its own dismiss button)
```

Key structural fact: **every "child" above is rendered as a state-gated *sibling*, not nested
inside its parent's JSX.** That single fact is the root cause of both the orphan class and the
close-drift class.

---

## 4. Design options, mapped to React

Ron's framing (from OOP generalities): each overlay is an object that *contains* its one child;
the "destructor" cleans up the child; constructors register the keystroke/Esc handlers; and
"containment is a stack" — but we should not hand-build the wheel React already provides.

Three ways to realize "innermost-Esc-first + cascade cleanup" in React 18 (UMD, hooks, no
bundler, in-browser Babel):

### Option 1 — Context "handler shadowing" (Ron's registerer-as-member)
Each `<Dialog>` provides, via React **context**, "the current Esc handler = mine, chaining to the
parent's." A child inherits the parent's handler as its context value (the "saved scalar"),
installs its own, and on unmount the context reverts automatically — React's tree *is* the
save/restore. **Correct only under strict LIFO teardown**, which containment guarantees (React
runs child effect-cleanups before parents'). Survives portals (context flows through the React
tree, not the DOM). *This is Ron's option 1, made idiomatic — the tree holds the scalar, so there
is no global mutable to corrupt (and it is StrictMode-safe, unlike a hand-rolled register/deregister).*

### Option 2 — DOM event bubbling + focus trap (Ron's "exceptions, flipped")
Attach the Esc handler to each overlay's DOM node, nest them in the DOM, trap focus in the
innermost; a keydown bubbles from the focused element outward, the innermost handles-and-stops.
The browser gives "innermost first" for free. **But:** requires real DOM nesting *and* focus
management, and **breaks under portals** — the whole reason the mature libraries use a JS stack
instead of DOM bubbling for Esc. Most work, least portable. Not recommended as the ordering
mechanism (though a focus trap is a good *accessibility* addition later).

### Option 3 — One root listener over a layer registry (Ron's single-child walk, generalized)
A module-level **layer registry** (a small ordered array). Each `<Dialog>`/`<Popover>`
`useEffect`-registers `{ id, close, kind }` on mount and removes it on unmount. **One** global
keydown listener (installed once) closes the **topmost** layer on Esc. Derived state
`anyModalOpen = registry has a modal` replaces the hand-maintained OR-chain. Cascade: closing any
layer also closes everything **above** it (stack order = the implicit hierarchy — literally
"containment is a stack"). Incrementally adoptable: wrap one existing overlay at a time; Esc
ordering and fencing work globally for whatever's migrated, while un-migrated overlays keep
running. **This is what the ecosystem actually ships.**

---

## 5. What the precedents teach

Every serious React overlay library solved this exact problem, and they agree:

- **Radix UI** (`@radix-ui/react-dialog` etc.) is built on **`DismissableLayer`**, which keeps a
  **module-level array (stack) of layers**; only the **topmost** layer reacts to
  `escapeKeyDown`/outside-pointer. Focus via a **`FocusScope` stack** with focus restoration.
  Overlays render through **portals** to `document.body`.
- **React-Aria** (`@react-aria/overlays`, `useOverlay`) keeps a **module-level stack of open
  overlays**; Escape closes the top; `ariaHideOutside` hides siblings for screen readers;
  `FocusScope` restores focus to the trigger on close.
- **Headless UI** (`@headlessui/react` `Dialog`) uses a **nested-Dialog hierarchy via context**
  (a child Dialog knows its depth from the parent), plus a focus trap — this is Ron's *containment*
  realized directly.

Three durable lessons for RW:
1. **A small stack for Esc-ordering is not a wheel-reinvention gone wrong — it is the converged
   answer.** Even Radix, which is deeply context/tree-based, keeps a layer stack for dismissal
   ordering. The "residue of a stack" I flagged is unavoidable and universal; the mistake would be
   building a *second* one instead of using the component tree for cascade and a *minimal* stack
   for ordering.
2. **Portals argue for the JS-stack (Option 1/3) over DOM bubbling (Option 2).** Once overlays
   portal to `body` (which we'll likely want, to escape `overflow`/`z-index` traps), DOM nesting
   is gone and only a JS stack or React context can order Esc.
3. **Focus restoration is a whole dimension RW ignores today.** The primitive is the natural home
   for it later (restore focus to the trigger on close, trap Tab inside) — a real accessibility
   win, but *not* required for the dismissal fix and explicitly out of scope for the first cut.

---

## 6. Recommended design

**Build a minimal layer registry + two primitives. Use React's tree for cascade (Option 1's
containment) and a minimal module stack for Esc-ordering/fence (Option 3). This is the Radix/
React-Aria shape, hand-rolled to ~100–150 lines because we can't `npm install` under in-browser
Babel.**

### 6a. The registry (the one wheel we keep, minimal)
```
// module scope
const layers = [];                 // ordered; [0] = outermost, [n-1] = topmost
function pushLayer(rec)  { layers.push(rec); notify(); }   // rec = {id, close, kind}
function removeLayer(id) {          // remove id AND everything above it (cascade)
  const i = layers.findIndex(l => l.id === id);
  if (i >= 0) layers.splice(i).forEach(l => l.id !== id && l.close?.());
  notify();
}
function topLayer()      { return layers[layers.length - 1]; }
function hasModal()      { return layers.some(l => l.kind === 'modal'); }
// ONE listener, installed once:
window.addEventListener('keydown', e => {
  if (e.key === 'Escape' && topLayer()) { e.stopPropagation(); topLayer().close(); }
});
```

### 6b. The hook + primitives
- `useOverlayLayer({ close, kind })` — `useEffect(() => { const id = pushLayer({id, close, kind});
  return () => removeLayer(id); }, [])`. Registration/deregistration is the "constructor/destructor."
- `<Dialog onClose title>` — portals to `body`, renders backdrop (onClick → onClose), a baked-in
  **✕**, and children; calls `useOverlayLayer({ close: onClose, kind: 'modal' })`. **A dialog built
  with this cannot be unfenced, un-Esc-able, or un-dismissable — the checklist is now structural.**
- `<Popover>` / `<Menu>` — light-dismiss variant (`kind: 'popover'|'menu'`, positioned, no scrim,
  outside-click closes); same registration, so Esc-ordering and cascade span modals *and* popovers
  (the orphan was a popover under a modal — both must live in one stack).

### 6c. How it satisfies every requirement
- **Keystroke fence** → `dialogUp()` reads `hasModal()` (plus the existing imperative-overlay
  bridge); the hand-maintained OR-chain at 6872 is deleted.
- **Esc innermost-first** → one listener, topmost layer. No per-overlay Esc branches; `handleModalEsc`
  and the modal half of `handleEscKey` collapse into the registry.
- **Cascade / no orphans** → two independent guarantees: (1) children nested in the parent's JSX
  unmount with it (React), auto-removing from the registry; (2) `removeLayer` closes everything
  above the closed layer (stack order). Belt and suspenders.
- **Backdrop + ✕** → baked into `<Dialog>`.
- **Ron's parent pointer** → the `rec` can carry `parentId` for debugging (and the JSX nesting is
  the parent link); cheap to keep, invaluable when an orphan reappears.

---

## 7. Migration plan (incremental — no big bang)

1. **7.14.2 stopgap (small, low-risk, do first):**
   - Orphan: `autoOrgPreview` Esc (6907) → call `closeAutoOrgPreview()`. One line.
   - Fence + Esc + (backdrop where missing) for `restoreConfirm`, `newFolderHiddenAlert`,
     `corruptionRecovery` by the *current* mechanism (add to 6872 + 6898-chain). Small, contained.
   - Optionally add the 6 menus to a close-on-Esc path. (Lower priority.)
   This buys immediate safety independent of the big refactor, and it's testable in minutes.
2. **Primitive on its own branch** (`feature/overlay-system`): build the registry + `<Dialog>`/
   `<Popover>` with no callers; unit-exercise by converting **one** low-risk leaf overlay
   (e.g. `newFolderHiddenAlert`) end-to-end. Prove the pattern.
3. **Migrate outward-in, one family per alpha**, keeping the legacy OR-chain as a bridge until the
   last modal is converted (derived `hasModal()` OR legacy chain during transition). Suggested
   order: leaf alerts → the AutoOrg family (kills the orphan structurally + proves nesting) →
   wizard family (proves nested sub-dialogs) → the rest → menus/dropdowns → finally delete the
   OR-chain, `handleModalEsc`, and the modal half of `handleEscKey`.
4. **Retire the CLAUDE.md checklist** once `<Dialog>` is the only way to make one — the rule
   becomes unnecessary because the structure enforces it.

---

## 8. Risk / reward (for the morning decision)

**Reward:** retires the entire §2 table at the root; future overlays are correct by construction;
unifies three Esc regimes and two fence sources into one; deletes a hand-maintained OR-chain;
opens the door to real focus management/a11y; makes the recurring "new dialog forgot the fence"
class impossible.

**Cost / risk:** touching ~40 overlays across a 20k-line single component is major surgery.
Specific hazards: z-index/stacking changes when moving to portals; backdrop/scrim behavior
differences; the imperative-overlay bridge (`rw-imperative-overlay` + `attachDialogDismiss`) must
be reconciled with the registry; React StrictMode double-invokes effects (registration must be
idempotent); **RW has no automated tests and ships via in-browser Babel, so a subtle regression
ships silently.** Mitigated by: incremental migration behind a coexisting registry, one family per
alpha, commit-before-each-test, start at low-risk leaves.

**Recommendation:** **split it.** Do the §7.1 stopgap now as 7.14.2 (immediate safety, minutes to
test). Keep this document as the design of record + a TODO for the primitive, and build the
primitive deliberately on its own branch when there's appetite for a multi-alpha refactor — not
wedged into a patch release. The stopgap removes all *live* harm; the primitive removes the
*class*. They are separable, and separating them is the low-regret path.

---

## 9. Open questions for Ron

1. **Portals?** Rendering overlays to `document.body` fixes latent `z-index`/`overflow` clipping
   and is what the libraries do — but it's a behavioral change worth a conscious yes. (It also
   settles Option 1-vs-2: portals rule out DOM-bubbling Esc.)
2. **Do the light-dismiss menus want Esc?** Standard UX says yes (Esc closes a context menu). Any
   reason to keep them click-outside-only?
3. **Scope of the first migration cut:** modals only, or modals + popovers + menus together? (The
   orphan spanned a popover under a modal, so a *complete* fix needs both in one stack — but the
   first *branch* could prove modals alone.)
4. **Focus management in scope now or later?** Recommend later (separate, larger, a11y-focused
   pass); the dismissal fix stands alone.
5. **`shareEmailChoice`'s dual parentage** (child of the book-dialog share dropdown vs. top-level
   from a multi-select) — fine under the registry (it just registers wherever it mounts), but worth
   noting the nesting isn't fixed.
