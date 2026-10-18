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
  repo root + `relay/relay-worker.js` — `is_app_source()`, a rule not a list; widened 2026-10-08) each turn it prints the checklist and denies once; re-issuing the identical edit proceeds.
  **Whole-batch bounce** (2026-10-16): every other shipped-code edit in the SAME batch is refused too, so a batch never
  applies by halves — the bounced edit used to go missing while the rest landed (alpha.62; twice more on 7.21.2).
  "Same batch" = same assistant message id, looked up in the session transcript (`batch_of()`; Ron's idea). Probed: the
  hook gets `tool_use_id` + `transcript_path`, and the FIRST call of a message is NOT in the transcript when its own
  hook runs — but the bounced call is by the time a later one arrives. So: both found → same message id = same batch;
  bounced found + this one not = this one opens a NEW message = a re-send → allowed (fixed 2026-10-18, after the
  timer refused 7.22.0's re-sent edit). The 5-second window decides only when even the bounced call can't be found.
  The lookup reads the transcript's last 4 MB — fine live (the bounce is recent); old ids fall out of it. The
  checklist is **not** in the hook — it's pulled from the `GATE-CHECKLIST` block in `docs/PRINCIPLES.md`
  (single source). Unreadable → loud `CHECKLIST SOURCE MISSING` alarm + a minimal core.
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
  module `.js` files + `readerwrangler.css` → their `?v=` cache-buster in `readerwrangler.html`.
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
