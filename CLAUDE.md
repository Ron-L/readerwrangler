# ReaderWrangler — Project-Specific Rules

> **Generic dev ground rules live in `../CLAUDE.md`** (the Projects root), auto-loaded *before* this
> file. This file holds only what's specific to ReaderWrangler — mechanics, file names, remotes, and
> its concrete checklists. Don't restate the generic rules here; add RW specifics and let the
> Projects-root file carry the rest. RW's distilled laws + war-stories: **`docs/PRINCIPLES.md`**.

---

## New dialog/modal/popup → build it on the overlay primitive (RW mechanism)

**Every new dialog, modal, menu or popup is built with `<Dialog>` (modal) or `<Popover>` (menu/popup;
add `fence` if it must block library keys; `anchorRef` for a button dropdown).** Esc (innermost-first,
consumed), the ✕ / backdrop / outside-click dismissal, the keystroke + undo fence, and stacking are then
STRUCTURAL — the overlay self-registers in `overlayRegistry.js`. **Never hand-roll a scrim, an Esc
listener, or a fence flag.** The imperative `showConfirmDialog`-style boxes (confirm / info / input / choice /
delete-warning / progress) keep their hand-built look but are layers in the SAME stack (since 7.18.0-alpha.68):
Esc, ✕, background click (press must start on it) and the fence come from their shared chrome
**`attachDialogDismiss`** (the progress box calls `pushLayer` + `onBackdropClick` itself). They register
**`detached: true`** — a box opened from a menu item sits above that menu and must survive the menu closing
(alpha.69). A new imperative box MUST go through `attachDialogDismiss`; better, build it as a `<Dialog>`
(rebuilding these as `<Dialog>`s is a low-priority TODO). `imperativeDialogsUp()` still detects them by DOM class.
**Popup buttons:** every button that opens a popup spreads **`{...popupTrigger(isOpen)}`** (optionally
`popupTrigger(isOpen, 'listbox' | 'dialog')`) — one bundle carrying the `data-popover-trigger` marker (a click on it
while ANY other popup is open switches in ONE click instead of the usual "an outside click only closes") plus the
accessibility pair (aria-haspopup / aria-expanded). Never hand-write those attributes. Ron, 2026-10-07/08; a dev-server
console warning flags an anchored popup whose button lacks it.

(History: earned 2026-09-16 when the Share dialog shipped with only Cancel+backdrop. The old hand-run
4-step checklist — register in `anyDialogOpen`, add to `handleModalEsc`, ✕, backdrop — was retired in
7.18.0-alpha.43 when both of those lists were deleted; design of record:
`docs/design/DIALOG-DISMISSAL-AUDIT.md`.)

---

## RW terminology & copy

* Backup terminology: **"Save/Restore"**, not "Import/Export".
* **"Toast"** = small floating text near the status bar, not an overlay dialog.
* Sync vocabulary exposed to users: **Relay, Credentials, Channel ID, Passphrase, bookmarklet,
  Import from Relay, Download Library/Collections, Data Status** — mirror these exact words (don't
  invent "Cloud Storage"); "cloud" appears once, only as the plain-English intro in SUPPORT-KB §1.

---

## Versioning — RW's constants

Follows the generic semver+alpha rules in `../CLAUDE.md`. RW's specific stamps:

- **ORGANIZER_VERSION** (`readerwrangler.js`) — bump in the same commit as each alpha iteration.
- **APP_VERSION** (`readerwrangler.html`) — the cache-buster; updated at release. Defined ONCE in
  HTML, read by JS via query param (no duplication). Does NOT bump during alphas (test alphas
  locally via http.server, never against readerwrangler.com).
- **MOBILE_VERSION** (`mobile.js`) — own X.Y.Z scheme, but any alpha commit that modifies mobile.js
  appends the SAME `-alpha.N` suffix as that commit's ORGANIZER_VERSION. Drop the suffix at release.
- **CSS cache-buster** (`readerwrangler.html`): `readerwrangler.css?v=X.Y.Z` must match
  ORGANIZER_VERSION on every commit that modifies `readerwrangler.css`.
- **index.html** Schema.org `softwareVersion` — update to match APP_VERSION at release.

---

## Release Checklist (RW-specific — the generic discipline is in `../CLAUDE.md`)

- `git add` specific files only.
- `grep -rn "TODO" *.js *.html`.
- Drop the pre-release suffix from all file versions; update **APP_VERSION** and index.html
  **softwareVersion**.
- Update **CHANGELOG.md** (Ron's "word" on the copy first), **README.md** (and its mirror index.html)
  "Recent Features" / "Coming Soon"; **sync those two lists into features.html**.
- Re-align "Coming Soon" with the actual TODO priorities (public promises track the real queue).
- **Sweep support-shaped material** into `docs/design/SUPPORT-KB.md` (facts/fixes) and
  `WORKFLOW-PATTERNS.md` (usage patterns). The sweep is a COMB: grep the KB for every term the
  release touched (renamed labels, changed behaviors, new UI) and update each hit; bump the KB's
  "up to date as of" stamp.
- **TODO.md**: delete all checked `- [x]` items (now recorded in CHANGELOG) — TODO is future-only.
- (Then the generic: PM always → update PRINCIPLES.md + memory, per `../CLAUDE.md`.)

---

## Git Workflow — RW specifics

Follows the always-branch → squash → tag `vX.Y.Z` → keep-branch pattern in `../CLAUDE.md`. RW's
particulars:

- **Remotes:** `dev` (testing) / `prod` (production) — no `origin`.
- **Navigator/bookmarklet link changes:** Dev first → test on GitHub Pages → then Prod. Otherwise,
  don't push to dev for routine local testing (test locally first).

| User says | Do |
|-----------|-----|
| "push" or "proceed" | Ask: navigator changes or ready to share? |
| "push to prod" | Squash-merge to main, tag `vX.Y.Z`, then `git push prod main --tags` (keep the branch) |
| "release" | Clarify which |

---

## RW session tooling (`.claude/`, local, gitignored)

- **Pre-build gate** — a `PreToolUse` hook (`.claude/hooks/gate-check.py`) denies the first edit of
  `readerwrangler.js`/`mobile.js` each turn with a checklist (mechanism, not memory). Consider it, then
  re-issue the edit. `Stop`/`SessionStart` re-arm it per turn. The checklist is the **single source** in
  `docs/PRINCIPLES.md` (the `GATE-CHECKLIST` block); the hook just pulls + prints it and **fails LOUD** if
  it can't reach it. Full local tooling + the pattern: **`docs/design/SESSION-TOOLING.md`**.
- **`/sitemap`** (`.claude/commands/sitemap.md`) — mechanizes the class-of-sites comb.
- **Version-guard** — a `pre-commit` hook (`.claude/hooks/version-guard.py`) refuses a commit that stages
  shipped code without moving its version stamp. Bypass: `git commit --no-verify`.
- **Name check** — the same `pre-commit` hook runs **`scripts/check-names.js`** (versioned) whenever a `.js`/`.html`
  is staged: refuses app code that uses a name nothing defines (a syntax check can't see that — 7.18.0-alpha.55's
  "shareBtnRef is not defined" crash), and any `readerwrangler.html` inline script that doesn't parse. Page-level
  names are derived from `readerwrangler.html`'s scripts, so new modules need no upkeep. Needs
  `npm i --no-save @babel/core @babel/preset-react` (fails loud if missing).
- **Timestamp stamp hook is GLOBAL, not RW-local** — it is `C:/Users/Ron/Projects/stamp.py`, wired in
  `~/.claude/settings.json` (`UserPromptSubmit`), injecting the live time each turn for **all** projects.
  See the Projects-root **`CLAUDE-TOOLING.md`**. (Corrected 2026-09-30 — the old `.claude/hooks/stamp.py`
  path was wrong and cost a chase; its absence there is *not* a sign it's missing.)

---

## Reference

**Folders:** `docs/api/` (Amazon library API — check before fetcher changes), `docs/design/`,
`post-mortems/`.

**`docs/PRINCIPLES.md`** — the distilled laws from all RW post-mortems (with enforcements). Consult
when debugging stalls, before refactors/releases, and when a lesson feels familiar. New principles
land there same-day via the post-mortem → memory step.

**No version increment:** README, CHANGELOG, TODO, `*.md` docs, `.bat` files.
