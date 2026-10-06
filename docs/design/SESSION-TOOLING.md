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

## RW's local hooks (`.claude/hooks/`, gitignored; wired in `.claude/settings.local.json`)

- **`gate-check.py`** (PreToolUse) — the **pre-build gate**. On the first `readerwrangler.js`/`mobile.js`
  edit each turn it prints the checklist and denies once; re-issuing the identical edit proceeds. The
  checklist is **not** in the hook — it's pulled from the `GATE-CHECKLIST` block in `docs/PRINCIPLES.md`
  (single source). Unreadable → loud `CHECKLIST SOURCE MISSING` alarm + a minimal core.
- **`gate-reset.py`** (Stop/SessionStart) — re-arms the gate's per-turn flag (a temp-dir file keyed by
  session id) so the checklist lands exactly once, at the planning→build boundary.
- **`version-guard.py`** (pre-commit, `.git/hooks/pre-commit` → this script) — refuses a commit that stages
  shipped code without moving its version stamp: `readerwrangler.js`→`ORGANIZER_VERSION`,
  `mobile.js`→`MOBILE_VERSION`, and the module `.js` files + `readerwrangler.css` → their `?v=` cache-buster
  in `readerwrangler.html`. Bypass (Ron's call): `git commit --no-verify`.
- **`scripts/check-names.js`** (pre-commit, called from `.git/hooks/pre-commit` when any `.js`/`.html` is staged;
  the script itself is VERSIONED in the repo — the hook is the thin caller) — Babel scope analysis of
  `readerwrangler.js` + `mobile.js`: refuses any identifier that is neither bound in scope, a browser/CDN global, nor
  defined by `readerwrangler.html` (its inline scripts + every local `<script src>`, derived automatically). Also
  refuses an inline script that doesn't parse. Earned 2026-10-06: an edit joined `const shareBtnRef = …` into a `//`
  comment — it parsed, then crashed the book details window; the first run also found a `readerwrangler.html` inline
  script broken since 7.4.0 (raw line break in a string — the load-error capture had never run). Needs
  `npm i --no-save @babel/core @babel/preset-react`; exits 2 (loud) if missing.
- **`/sitemap`** (`.claude/commands/`) — mechanizes the class-of-sites comb (two independent pivots).

## Related
- The gate's checklist content + the debugging law it now carries: `docs/PRINCIPLES.md` (Laws + the
  `GATE-CHECKLIST` block).
- Global (cross-project) tooling: `CLAUDE-TOOLING.md` at the Projects root.
