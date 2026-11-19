# Commit checks — what each refuses, and why

_Moved verbatim from CLAUDE.md on 2026-11-19 (the rule trim, approved by Ron); CLAUDE.md keeps one line per check and points here._


Every check runs from **`git-hooks/pre-commit`**. One-time setup per copy of the project:
**`git config core.hooksPath git-hooks`** (moved here from the unsaved `.git/hooks` + `.claude/hooks` on 2026-10-15).
Bypass (Ron's call only): `git commit --no-verify`.

- **Version-guard** (`git-hooks/version-guard.py`) refuses a commit that stages shipped code without moving its
  version stamp — and a release commit (one that moves `APP_VERSION`) unless the help notes' stamp
  (`docs/design/SUPPORT-KB.md`) says "through release <that version>" (2026-10-20).
- **Name check** (`git-hooks/check-names.js`), whenever a `.js`/`.html`
  is staged: refuses app code that uses a name nothing defines (a syntax check can't see that — 7.18.0-alpha.55's
  "shareBtnRef is not defined" crash), and any `readerwrangler.html` inline script that doesn't parse. Page-level
  names are derived from `readerwrangler.html`'s scripts, so new modules need no upkeep; a global published under a
  computed name is declared where the name is chosen (`/* page-global: rwLog */` in logkit-settings.js). It checks
  readerwrangler.js, mobile.js and the Diagnostics window's source (`logkit/diagnostics-window.js`). Needs
  `npm i --no-save @babel/core @babel/preset-react` (fails loud if missing).
- **Shared-numbers check** (`git-hooks/check-shared-numbers.js`), when `relay-client.js` or `relay/relay-worker.js` is
  staged: refuses a commit where the app and the worker disagree on the 90-day upload life, keep-2, the unfinished-copy
  grace, or the id-time format — the worker's nightly cleanup deletes by those rules (7.23.0; decided Ron 2026-10-14).
- **Private-values check** (`git-hooks/check-private.py` + `git-hooks/commit-msg`, one shared check
  `git-hooks/private_values.py`), on every commit: refuses added lines or a commit message holding a value from the
  private secrets note, and Cloud Sync credentials by their shape — a `.json` with `relay.channelId` + `passphrase` (a
  backup, or a demo file made from one), a pasted bookmarklet, the Copy text's passphrase. Names where, never prints a
  value. `python git-hooks/private_values.py --list` shows what it refuses (masked); `--scan-history` scans every
  commit (2026-10-31: one find — the organized demo library carried a credential pair from 2026-07-03; revoked on both
  relays and removed).
- **Parse check** (`git-hooks/check-parse.py` → `parse-js.js`), whenever a `.js`/`.mjs`/`.py` is staged: refuses a staged
  script that doesn't parse — the fetchers, the bookmarklet menu, the relay worker and every Python file included
  (2026-11-04; tests: `test/test_check_parse.py`).
- **Tier-1 tests for what changed** (`tools/run_tests.py --changed`, pre-commit step 7): the function tests whose
  `covers:` header names a changed file run on every commit; silent when none apply. The whole library:
  `py tools/run_tests.py --tier all` (docs/design/TESTING.md).
- **Logging rules + the message-code table** (`tools/message_codes.py --check`, pre-commit step 8 — RW's layer on the
  logging kit's general `logkit/check_messages.py`, 7.28.0; the kit's guide: `logkit/README.md`), when an app script,
  either checker or the table is staged: every `rwLog.log(level, code, text…)` call has a known level, a code `AREA` or
  `AREA-NN` from logkit-settings.js's areas (RW's settings for the logging kit), a numbered code for warning and above,
  each numbered code at ONE call — and
  `docs/design/MESSAGE-CODES.md` (generated, never edited) matches the code. Fix: `py tools/message_codes.py` and stage
  the table (2026-11-07; docs/design/LOGGING.md §6). It also refuses a direct `showToast(` (a toast is
  `rwLog.log(…, { toast: true })`, so it reaches the log with its area) and a dialog call without its area FIRST
  (`showInfoDialog('BACKUP', title, message)` — the dialog logs what it showed there) (2026-11-09).
- **TODO table-of-contents check** (`git-hooks/check-toc.js`), when
  `TODO.md` is staged: refuses a table of contents that doesn't match the headers. The table is built by the VS Code
  extension "Auto Markdown TOC" only on a VS Code save — edits made any other way leave it stale. Fix: Ron saves the
  file in VS Code, or Claude corrects the listed entries. TODO format: one header per task (plain words, ~80 chars,
  132 max), a "why it matters" first line, ✅ in front when done (Ron, 2026-10-14), 🚧 in front while in progress —
  kept at the top of its section, after any ✅ ones (Ron, 2026-10-15). **Every task has an ID line right under its
  header** — `<!-- id YYYYMMDD-HHMM -->`, the time it was filed (the stamp hook's time; a letter suffix only when that
  minute is taken) — and a task that absorbs others lists them: `<!-- id … ; merged <id>, <id> -->`. The same check
  refuses a missing or repeated ID; `tools/backlog_report.py` follows tasks by them (Ron, 2026-10-21).
- **The built app** (`tools/build.py --check-staged`, pre-commit step 9; 7.27.0): the page loads `dist/readerwrangler.js`
  and `dist/mobile.js` (and, since 7.28.0, the logging kit's `dist/logkit/diagnostics-window.js`), compiled ahead of time
  by `tools/build.py` (`SOURCES`; Babel 7.29.7 pinned in `tools/build/`; once: `cd tools/build && npm ci`), and the app,
  reset and security pages link `dist/tailwind.css` — the styles built from every tracked SHIPPED page and script,
  folders included (Tailwind 3.4.17, what the in-browser builder served). Restart `serve.py` after `SOURCES` changes (it
  reads the list once). When a source, a page, a script or a
  built copy is staged, the staged copy must be exactly the build of the staged files. `serve.py` rebuilds on demand, so
  the local loop is still edit → refresh. **Never edit `dist/`.** A changed `dist/tailwind.css` moves its `?v=` stamp in
  every page that links it (the version guard reads the pages).
  Load time: `.venv\Scripts\python tools/time_load.py [--large]` (was ~50 s; 0.7 s to the app, 1.3 s to 3,270 books).
- **Saved-value reads** (`git-hooks/check-saved-reads.py` → `saved-reads-js.js`, pre-commit step 10; 7.29.1): in the
  scripts that can call `readSaved` (uiHelpers.js), refuses a bare `JSON.parse` of a localStorage / sessionStorage read —
  a damaged setting must fall back, not blank a screen; a read that truly can't use it says `// not-readSaved: <why>`;
  `--all` lists them (Ron, 2026-11-13).
- **No task leaves TODO.md silently** (`git-hooks/check-removed-tasks.py`, from `git-hooks/commit-msg` — it needs the
  message): a commit that removes a task must show why — it had a ✅, another task lists it as merged
  (`<!-- id … ; merged <id> -->`), or the message says **`done <id>`** (finished, shipped without a ✅ — the backlog
  report counts it done) or **`dropped <id>`** (and why). Squash and merge commits are skipped (each branch commit was
  checked). Earned 2026-11-10: a task filed 11-02 was deleted by accident 27 minutes later inside a big TODO edit.
  The backlog report also finds a task's ✅ on any branch (squashes hide it from main).

---
