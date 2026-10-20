# RW Session Tooling & the single-source hook pattern

_ReaderWrangler's project-**local** Claude Code tooling (`.claude/`, gitignored) and the reusable
**pattern** behind it. Global tooling (e.g. the per-turn timestamp stamp) lives at the Projects root —
see `CLAUDE-TOOLING.md` there. Established 2026-09-30._

## The pattern (worth considering for any project)

**A hook is a thin mechanism; the human-readable content it enforces lives in a versioned single source,
and the hook PULLS it at run time.** And **a hook that can't reach its source must fail LOUD** — announce
the break — never silently degrade, because a silent fallback lets the mechanism rot unnoticed.

Why: content duplicated between a hook and the docs *drifts*. Earned 7.18.0 — the pre-build checklist had
drifted across three copies (the hook, the PRINCIPLES intro, and each Law's enforcement line). We made
`docs/PRINCIPLES.md` the one source (a `GATE-CHECKLIST` block) and turned the hook into a dumb printer that
pulls that block; edit the checklist once and the gate auto-syncs. If the block/file/markers break, the
gate prints a loud `SOURCE MISSING` alarm instead of a stale checklist.

## RW's session hooks (`.claude/hooks/`, saved in git; wired in `.claude/settings.json`)

- **`gate-check.py`** (PreToolUse) — the **pre-build gate**. On the first edit of shipped code (any `.js` at the
  repo root + `relay/relay-worker.js` — `is_app_source()`, a rule not a list; widened 2026-10-08) each turn it prints the checklist and refuses that batch's app edits; re-sending them (the next batch) proceeds.
  **Whole-batch refusal — a three-state switch moved by real signals** (2026-10-19, Ron + Claude): **ARMED** (set by
  `gate-reset.py` at each turn's end / session start) → the first app edit flips it to **REFUSING** and gets the
  checklist; **every** app edit while REFUSING is refused, however the batch streams or is timed → **`gate-batch-end.py`
  on PostToolBatch** (fires once a whole batch has finished, before the next model call — probed 2026-10-19) flips it
  to **CLEAR**, so the re-send (the next batch) goes through. The reset also clears a leftover REFUSING. Why: refusing
  only the first edit let the rest of a batch land (alpha.62; twice on 7.21.2). Two earlier fixes GUESSED where a batch
  ends — a 5-second timer, then the session transcript's message ids — and both failed (7.23.0-alpha.2, 7.22.1-alpha.3)
  because edits stream in and are written with unpredictable timing; that guessing code is deleted. A hook can't
  "hold" an edit while Claude thinks (Claude only sees a hook's message in a call's result), so the checklist must
  arrive by refusing — the switch makes the refusal whole. The
  checklist is **not** in the hook — it's pulled from the `GATE-CHECKLIST` block in `docs/PRINCIPLES.md`
  (single source). Unreadable → loud `CHECKLIST SOURCE MISSING` alarm + a minimal core.
- **`gate-batch-end.py`** (PostToolBatch) — REFUSING → CLEAR once the refused batch is over (2026-10-19).
- **`gate-reset.py`** (Stop/SessionStart) — re-arms the gate's per-turn flag (a temp-dir file keyed by
  session id) so the checklist lands exactly once, at the planning→build boundary.
- **`/sitemap`** (`.claude/commands/`) — mechanizes the class-of-sites comb (two independent pivots).

## RW's commit checks (`git-hooks/` — run BY GIT, saved in the repo)

Moved 2026-10-15 from `.git/hooks/` (git never saves its own hooks folder) + `.claude/hooks/` (gitignored): before
that, losing this PC — or a fresh clone — silently lost every commit check. **One-time setup per copy of the project:
`git config core.hooksPath git-hooks`.** `git-hooks/pre-commit` is the thin wiring; each check is its own script.
Bypass (Ron's call): `git commit --no-verify`.

- **`version-guard.py`** — refuses a commit that stages
  shipped code without moving its version stamp: `readerwrangler.js`→`ORGANIZER_VERSION`,
  `mobile.js`→`MOBILE_VERSION`, `relay/relay-worker.js`→`WORKER_VERSION` (shown in the relay's emails), and the
  module `.js` files + `readerwrangler.css` → their `?v=` cache-buster in `readerwrangler.html`. **A release sweeps the
  help notes** (2026-10-20): a commit that moves `APP_VERSION` is refused unless `docs/design/SUPPORT-KB.md`'s stamp says
  "through release <that version>" — the stamp used to be a promise nothing checked (7.21.3 went unswept for 4 days).
- **`check-toc.js`** (when `TODO.md` is staged; checks the STAGED copy) — refuses a
  `TODO.md` whose table of contents (between `<!-- TOC -->` markers, built by the VS Code extension "Auto Markdown
  TOC" on save) doesn't match its headers by text and depth. Link targets aren't compared (the extension owns them).
  Earned 2026-10-14 when the TODO became one header per task: edits that don't go through a VS Code save leave it stale.
- **`check-names.js`** (when any `.js`/`.html` is staged) — Babel scope analysis of
  `readerwrangler.js` + `mobile.js`: refuses any identifier that is neither bound in scope, a browser/CDN global, nor
  defined by `readerwrangler.html` (its inline scripts + every local `<script src>`, derived automatically). Also
  refuses an inline script that doesn't parse. Earned 2026-10-06: an edit joined `const shareBtnRef = …` into a `//`
  comment — it parsed, then crashed the book details window; the first run also found a `readerwrangler.html` inline
  script broken since 7.4.0 (raw line break in a string — the load-error capture had never run). Needs
  `npm i --no-save @babel/core @babel/preset-react`; exits 2 (loud) if missing.

## Related
- The gate's checklist content + the debugging law it now carries: `docs/PRINCIPLES.md` (Laws + the
  `GATE-CHECKLIST` block).
- Global (cross-project) tooling: `CLAUDE-TOOLING.md` at the Projects root.
