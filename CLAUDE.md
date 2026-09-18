# ReaderWrangler — Project-Specific Rules

> **Generic dev ground rules live in `../CLAUDE.md`** (the Projects root), auto-loaded *before* this
> file. This file holds only what's specific to ReaderWrangler — mechanics, file names, remotes, and
> its concrete checklists. Don't restate the generic rules here; add RW specifics and let the
> Projects-root file carry the rest. RW's distilled laws + war-stories: **`docs/PRINCIPLES.md`**.

---

## New dialog/modal → the checklist (RW mechanism)

Every new dialog/modal, without exception:
1. Register in `anyDialogOpen` (the keystroke-guard + undo-fence registry — else Ctrl+X/Delete leak
   to the library beneath).
2. Add to `handleModalEsc` (Esc closes it, innermost-first).
3. A ✕ close button.
4. Backdrop-click close.

(Earned 2026-09-16: the Share dialog shipped with only Cancel+backdrop — the exact class the 7.10.1
audit fixed but never made a *rule*.) **Durable chokepoint (in progress):** the self-registering
`<Dialog>`/`<Popover>` primitive in `docs/design/DIALOG-DISMISSAL-AUDIT.md` will make this checklist
structural (and unnecessary) — until it ships, follow the four steps by hand.

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
  `readerwrangler.js`/`mobile.js` each turn with an 11-point checklist (mechanism, not memory).
  Consider the checklist, then re-issue the edit. `Stop`/`SessionStart` re-arm it per turn.
- **`/sitemap`** (`.claude/commands/sitemap.md`) — mechanizes the class-of-sites comb.
- **Timestamp stamp hook** — a `UserPromptSubmit` hook (`.claude/hooks/stamp.py`) injects the live
  time each turn so the `📋` response-start stamp stops depending on memory.

---

## Reference

**Folders:** `docs/api/` (Amazon library API — check before fetcher changes), `docs/design/`,
`post-mortems/`.

**`docs/PRINCIPLES.md`** — the distilled laws from all RW post-mortems (with enforcements). Consult
when debugging stalls, before refactors/releases, and when a lesson feels familiar. New principles
land there same-day via the post-mortem → memory step.

**No version increment:** README, CHANGELOG, TODO, `*.md` docs, `.bat` files.
