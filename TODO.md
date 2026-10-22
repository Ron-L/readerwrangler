<!-- TOC -->

- [TODO](#todo)
  - [🔝 Up next](#up-next)
    - [High priority](#high-priority)
      - [🚧 Relay storage: stop leftovers piling up, and report usage correctly](#relay-storage-stop-leftovers-piling-up-and-report-usage-correctly)
        - [Numbers the app and relay must agree on: add a check that they match](#numbers-the-app-and-relay-must-agree-on-add-a-check-that-they-match)
      - [Turn more of our working rules into automatic checks (my tooling)](#turn-more-of-our-working-rules-into-automatic-checks-my-tooling)
      - [Trim the always-loaded rules: one home per rule, history out, a lean memory index](#trim-the-always-loaded-rules-one-home-per-rule-history-out-a-lean-memory-index)
      - [Drag any dialog out of the way](#drag-any-dialog-out-of-the-way)
      - [Search improvements](#search-improvements)
        - [Find a book by its ASIN in the search box](#find-a-book-by-its-asin-in-the-search-box)
        - [Search everywhere without leaving the current folder](#search-everywhere-without-leaving-the-current-folder)
      - [Dark theme: fix the unreadable bar and the light strips](#dark-theme-fix-the-unreadable-bar-and-the-light-strips)
      - [Series positions: one Position dialog, and one book at several positions (omnibus)](#series-positions-one-position-dialog-and-one-book-at-several-positions-omnibus)
      - [Phone: show which test build is running](#phone-show-which-test-build-is-running)
      - [Drag a box to select covers](#drag-a-box-to-select-covers)
      - [Faster fetches that report exactly how your library compares with Amazon](#faster-fetches-that-report-exactly-how-your-library-compares-with-amazon)
      - [Book Lists and Searches: pin and sort them like Folders](#book-lists-and-searches-pin-and-sort-them-like-folders)
      - [A type-to-filter box for the left pane](#a-type-to-filter-box-for-the-left-pane)
      - [Everyday organizing](#everyday-organizing)
        - [Folder dragging: where you drop decides pinned, and the level](#folder-dragging-where-you-drop-decides-pinned-and-the-level)
        - [Stray double spaces in author names create duplicate authors](#stray-double-spaces-in-author-names-create-duplicate-authors)
      - [Tag from Collections, round 2: clearer window, safer tags (decided 2026-10-20)](#tag-from-collections-round-2-clearer-window-safer-tags-decided-2026-10-20)
      - [Restore dialog calls yesterday's backup "today"](#restore-dialog-calls-yesterdays-backup-today)
      - [Honest ownership changes: buying, samples, loans](#honest-ownership-changes-buying-samples-loans)
        - [Fetch should update books it already knows, not skip them](#fetch-should-update-books-it-already-knows-not-skip-them)
        - [Relay Import: only books in no folder should go to the Inbox](#relay-import-only-books-in-no-folder-should-go-to-the-inbox)
        - [Buying a book that's in the Trash should bring it back](#buying-a-book-thats-in-the-trash-should-bring-it-back)
        - [Fetch summary should report books you bought](#fetch-summary-should-report-books-you-bought)
        - [Import summary: every ownership change by kind, kept in the message history](#import-summary-every-ownership-change-by-kind-kept-in-the-message-history)
    - [Polish](#polish)
      - [Move and copy books anywhere — folders, Book Lists, All Books, Searches](#move-and-copy-books-anywhere--folders-book-lists-all-books-searches)
      - [Retire two leftover book fields: the hidden "seen" flag and the old price-goal field](#retire-two-leftover-book-fields-the-hidden-seen-flag-and-the-old-price-goal-field)
      - [Moving and selecting](#moving-and-selecting)
        - [Delete a book from All Books (removes it everywhere)](#delete-a-book-from-all-books-removes-it-everywhere)
        - [Open one book's details without losing a multi-selection](#open-one-books-details-without-losing-a-multi-selection)
        - [Restore the previous selection after a stray click or Select All](#restore-the-previous-selection-after-a-stray-click-or-select-all)
      - [A folder or Book List you just created stays visible under filters](#a-folder-or-book-list-you-just-created-stays-visible-under-filters)
      - [Book details window: one Save — nothing changes until you click it, and nothing is lost without asking](#book-details-window-one-save--nothing-changes-until-you-click-it-and-nothing-is-lost-without-asking)
      - [Relay Setup: smoother sections and clearer Esc / Help behavior](#relay-setup-smoother-sections-and-clearer-esc--help-behavior)
      - [Arrow keys should move through every type-ahead list](#arrow-keys-should-move-through-every-type-ahead-list)
      - [The "Save results" menu runs off the screen with many Book Lists](#the-save-results-menu-runs-off-the-screen-with-many-book-lists)
      - [Long lists keep their actions in view (Manage…, Select All) while you scroll](#long-lists-keep-their-actions-in-view-manage-select-all-while-you-scroll)
      - [Removing a recent search should offer Undo](#removing-a-recent-search-should-offer-undo)
      - ["Bake this order into Manual" for a folder's books and a Book List, from the Sort menu](#bake-this-order-into-manual-for-a-folders-books-and-a-book-list-from-the-sort-menu)
      - [Small fixes](#small-fixes)
        - [Tidy up the notes](#tidy-up-the-notes)
        - [Leave the affiliate tag off Amazon links on the test rig](#leave-the-affiliate-tag-off-amazon-links-on-the-test-rig)
        - [Switch the affiliate tag to "readerwrangler-20"](#switch-the-affiliate-tag-to-readerwrangler-20)
        - [Tooltips where they help: icon-only, disabled, non-obvious, cut-off](#tooltips-where-they-help-icon-only-disabled-non-obvious-cut-off)
        - [Menus keep their items in place: disable, don't hide](#menus-keep-their-items-in-place-disable-dont-hide)
        - [A book's hover popup stays up after the book is deleted](#a-books-hover-popup-stays-up-after-the-book-is-deleted)
        - [The Trash ignores the search and filters](#the-trash-ignores-the-search-and-filters)
        - [Show only hidden books](#show-only-hidden-books)
        - [One shared tag picker: show all tags in your order (the right-click one silently stops at 10)](#one-shared-tag-picker-show-all-tags-in-your-order-the-right-click-one-silently-stops-at-10)
        - [Right-click: add "Copy ASINs" below Copy Titles / Copy Authors](#right-click-add-copy-asins-below-copy-titles--copy-authors)
        - [Wishlist: record the real format when a book is added](#wishlist-record-the-real-format-when-a-book-is-added)
        - [Left pane: put the jump-to-top / bottom buttons by the scrollbar](#left-pane-put-the-jump-to-top--bottom-buttons-by-the-scrollbar)
        - [Bulk Edit hints that read like "you can type several values"](#bulk-edit-hints-that-read-like-you-can-type-several-values)
      - [Auto-Organize: Shift-click ranges should follow what you see](#auto-organize-shift-click-ranges-should-follow-what-you-see)
      - [Folder right-click menu: add Auto-Organize](#folder-right-click-menu-add-auto-organize)
      - [Fetcher housekeeping](#fetcher-housekeeping)
        - [Fetcher: give the library filter one name, in one place](#fetcher-give-the-library-filter-one-name-in-one-place)
        - [Fetcher odds and ends (progress figure, frozen timer, request pacing)](#fetcher-odds-and-ends-progress-figure-frozen-timer-request-pacing)
      - [Relay Setup's connection test checks the wrong relay on dev](#relay-setups-connection-test-checks-the-wrong-relay-on-dev)
      - [Finish routing every change through one shared path, with undo](#finish-routing-every-change-through-one-shared-path-with-undo)
      - [The Delete key should delete the folders you've selected](#the-delete-key-should-delete-the-folders-youve-selected)
      - [Working-process safety net: three small follow-ups](#working-process-safety-net-three-small-follow-ups)
  - [🚦 Before public launch](#before-public-launch)
    - [Help, docs and onboarding](#help-docs-and-onboarding)
      - [Security page: finish the high-contrast light theme](#security-page-finish-the-high-contrast-light-theme)
      - [Rewrite the User Guide around Searches, Book Lists and Folders](#rewrite-the-user-guide-around-searches-book-lists-and-folders)
      - [User Guide: explain workarounds for fields you can't filter by](#user-guide-explain-workarounds-for-fields-you-cant-filter-by)
      - [Wording pass: explain Book List shortcuts and Linked Copies](#wording-pass-explain-book-list-shortcuts-and-linked-copies)
      - [Rename "Relay" to "Cloud Sync" everywhere users see it](#rename-relay-to-cloud-sync-everywhere-users-see-it)
      - [Update and record the sizzle reel](#update-and-record-the-sizzle-reel)
      - [Refresh the landing page's before / after screenshot](#refresh-the-landing-pages-before--after-screenshot)
      - [Create a FAQ page](#create-a-faq-page)
      - [Say plainly what ReaderWrangler works with: US Amazon, Kindle, English, Chrome](#say-plainly-what-readerwrangler-works-with-us-amazon-kindle-english-chrome)
      - [Build the support assistant (custom GPT)](#build-the-support-assistant-custom-gpt)
    - [Safety and data protection](#safety-and-data-protection)
      - [All the pre-launch data tests pass](#all-the-pre-launch-data-tests-pass)
      - [Warn before uploading a much smaller library (demo safety)](#warn-before-uploading-a-much-smaller-library-demo-safety)
      - [A button to rebuild the library from Amazon](#a-button-to-rebuild-the-library-from-amazon)
      - [Pin the exact versions of outside code libraries](#pin-the-exact-versions-of-outside-code-libraries)
      - [Stop cleanly when Amazon asks for a human check mid-fetch](#stop-cleanly-when-amazon-asks-for-a-human-check-mid-fetch)
      - [Protect against editing in two tabs at once](#protect-against-editing-in-two-tabs-at-once)
      - [Let a new user's first big fetch resume after an interruption](#let-a-new-users-first-big-fetch-resume-after-an-interruption)
      - [Relay Setup: disconnect, or reset credentials](#relay-setup-disconnect-or-reset-credentials)
    - [Costs](#costs)
      - [Move to Cloudflare's $5/month plan around launch](#move-to-cloudflares-5month-plan-around-launch)
  - [🗄️ After launch](#after-launch)
    - [Dialog look](#dialog-look)
      - [Rebuild the old-style message boxes as standard dialogs](#rebuild-the-old-style-message-boxes-as-standard-dialogs)
    - [Speed](#speed)
      - [Clicking between books lags slightly while a filter is on](#clicking-between-books-lags-slightly-while-a-filter-is-on)
    - [Relay and sync](#relay-and-sync)
      - [Edit Kindle collections from ReaderWrangler](#edit-kindle-collections-from-readerwrangler)
      - [Cheaper small syncs (send only what changed)](#cheaper-small-syncs-send-only-what-changed)
      - [Bookmarklet: warn before fetching if your Channel ID no longer works](#bookmarklet-warn-before-fetching-if-your-channel-id-no-longer-works)
      - [Warn when another browser has newer changes](#warn-when-another-browser-has-newer-changes)
    - [Features](#features)
      - ["Read in Kindle": open a book in the Kindle app or Cloud Reader](#read-in-kindle-open-a-book-in-the-kindle-app-or-cloud-reader)
      - [Formats other than Kindle: undo my Kindle-only preference](#formats-other-than-kindle-undo-my-kindle-only-preference)
      - [Finish keyboard accessibility](#finish-keyboard-accessibility)
      - [Show reading progress](#show-reading-progress)
      - [Book recommendations](#book-recommendations)
      - [Show who a book is shared with (Family Library)](#show-who-a-book-is-shared-with-family-library)
      - [Two-pane split view](#two-pane-split-view)
      - [Support stores besides Amazon](#support-stores-besides-amazon)
      - [Several people on one installation](#several-people-on-one-installation)
      - [Reading statistics](#reading-statistics)
      - [Connect with Goodreads / StoryGraph](#connect-with-goodreads--storygraph)
      - [Animated drag-and-drop](#animated-drag-and-drop)
      - [Import book details from a pasted list or spreadsheet](#import-book-details-from-a-pasted-list-or-spreadsheet)
      - [Capture book ideas from your phone (Share → ReaderWrangler)](#capture-book-ideas-from-your-phone-share--readerwrangler)
    - [Prices](#prices)
      - [Wishlist prices through Amazon's official affiliate catalog API, once eligible](#wishlist-prices-through-amazons-official-affiliate-catalog-api-once-eligible)
      - [Notice when a Kindle edition appears for a print-only book](#notice-when-a-kindle-edition-appears-for-a-print-only-book)
      - [Now and then, refresh ratings for books you might buy](#now-and-then-refresh-ratings-for-books-you-might-buy)
    - [Technical clean-up](#technical-clean-up)
      - [Faster loading: build the app ahead of time](#faster-loading-build-the-app-ahead-of-time)
      - [Split the main code file into modules](#split-the-main-code-file-into-modules)
      - [Show a notice when book descriptions are missing](#show-a-notice-when-book-descriptions-are-missing)
      - [Clean up developer console messages](#clean-up-developer-console-messages)
      - [Check nothing was lost between versions 4 and 5](#check-nothing-was-lost-between-versions-4-and-5)
      - [Leftover desktop polish (left-pane keyboard, shadows)](#leftover-desktop-polish-left-pane-keyboard-shadows)
  - [👀 Watching](#watching)
    - [Undo history sometimes empties by itself](#undo-history-sometimes-empties-by-itself)
    - [Find out why some books end up in no folder](#find-out-why-some-books-end-up-in-no-folder)
  - [🧊 Someday](#someday)
    - [Test on Safari (desktop and iPhone)](#test-on-safari-desktop-and-iphone)

<!-- /TOC -->



# TODO

> **This file is FUTURE work only.** Each task is a header in short, plain words, so the table of contents above
> reads as the whole list. The first line under a header says why it matters; the details follow. A task being worked on gets
> 🚧 and sits at the top of its section (after any ✅ ones). When a task is
> done, put ✅ at the front of its header; **delete every ✅ section at each release** (after the CHANGELOG sweep).
> The past lives in **CHANGELOG.md**, design rationale in **docs/design/**, retrospectives in **post-mortems/**.
>
> When you promote/descope a task, **move** its section — never leave a stub. When you agree a bug/task mid-session,
> add a section (header + one line) before moving on. The table of contents is rebuilt by the VS Code extension
> "Auto Markdown TOC" when the file is saved in VS Code; a pre-commit check refuses a stale one
> (`git-hooks/check-toc.js`). Headers: about 80 characters, 132 at most, no internal names.

---

## 🔝 Up next

_Formerly: 🔝 TOP OF STACK (Ron 2026-09-09/10; stack state updated 2026-09-16)_

In priority order (Ron re-ranked 2026-10-14). **High priority**, then **Polish**.

### High priority

#### 🚧 Relay storage: stop leftovers piling up, and report usage correctly
<!-- id 20261003-0000 -->

_Why it matters:_ Leftovers eat into the free storage limit, and the daily email was reporting the wrong total.

**The problem** (found 2026-10-03/04; full write-up: docs/design/RELAY-WRITE-REDESIGN.md §14a)
- Each Restore left an ~18 MB package behind on the relay.
- The daily usage email showed **one** relay's storage (production or dev), never the sum, and printed "no data" as 0. The real total was ~572 MB — 56% of the 1 GB free limit — while emails said 219.7 / 326 / 0.
- About 265 MB was recoverable leftovers.

**The plan** (agreed 2026-10-13, revised 2026-10-14)
- ✅ **A — contributor mode** (7.21.0): a prerequisite.
- ✅ **B1 — the app cleans up after every save** (7.21.1): the package a save absorbed is deleted inside the save itself, and duplicates are removed. Proven on dev. Production's old leftovers go on its next save, or via the B2 cleanup.
- ~~Send to Production~~ — considered and rejected 2026-10-13 (docs/design/SEND-TO-PRODUCTION.md).
- 🔨 **B2 — the relay worker** (branch `feature/relay-worker-b2`, alpha.4 running on **dev only**; production still runs the old worker). Built so far:
  - Both relays send the daily email, covering **production + dev + the total** against the account-wide free limits. Dev's subject starts "[Dev]".
  - Threshold alerts compare the total (production only sends them).
  - A daily storage check that **reports** what a cleanup would delete, and deletes nothing.
  - A key-count check: Cloudflare's count is the day's **highest**, so "live ≤ it" reads as consistent.
  - Every email also arrives as formatted HTML. Worker statistics are labeled prod- / dev-.
  - The worker's version is in every email (the pre-commit check enforces the bump).
  - Each schedule runs only its own job. Any other schedule does nothing and is counted **in red** at the top of the next summary.
- ⏭️ **C — a shared notepad** for both relays (no user data): dev becomes a backup alerter (sends "[Dev] backup alert" if a limit crossing it has seen for over an hour has no production alert recorded), plus a "production is alive" check (alert if production's daily summary is more than 26 hours old).

**Next steps**
1. ✅ **The 2026-10-14 6:55 PM checks** (Ron, 2026-10-15):
   - Exactly **one** production email — the 10-13 duplicate was a one-off during Cloudflare's schedule incident.
   - The "[Dev]" summary arrived (the new daily schedule works) with the red section: the stray 10-minute schedule
     fired **12 times**, 10:00–11:50 AM, then stopped — Cloudflare applied the 6:36 AM change ~5 hours late. The
     stray fires cost no emails.
   - Still open: compare dev's storage figure with the Cloudflare dashboard.
2. ✅ **The report-only worker is on production** — deployed 2026-10-15 9:18 AM (Ron's go; version `3e2d7d39`, code =
   B2 alpha.4; checked: no open Cloudflare incident first). Production has the **real** leftovers, so its first
   report was the real test — **✅ verified 2026-10-15** (Ron ran the on-demand summary on production):
   - "Would delete": the interrupted save `…21fc` ✅. "Kept": 1 multi-part run not yet imported (`…3560`) ✅.
   - Key check 53 = 53 (current). No storage alert. Total storage 372.9 MB (37.3%).
   - Watch: dev's storage fell 197.2 → 142.5 MB in a day — probably dev data expiring; see whether it keeps moving.
   - 2026-10-15 evening: after a day of fetches + Imports, dev rose to **288.9 MB** (total 519.3 = 51.9% → the 50%
     storage alert fired, as designed). Dev's check flagged **3 extra device-state generations from that day** (~17 MB
     each) — the one-hour grace kept them because the last saves came within the hour (design §14a F2); the next save
     after they age, or the coming deleting step, removes them. The rest was the day's peak (keys 262 at the high
     point, 248 at report time). No leak.
3. ✅ **Released 7.22.0 (report-only), 2026-10-18** — both reports right 10-14 → 10-17; production's 27 "other" keys identified (all by design); worker version `7.22.0` (same code as alpha.4) — redeployed to both relays after the release with Ron's yes for each. The original plan for this step:
   **After a few days of both reports being right (~2026-10-17/18): release 7.22.0 (report-only).**
   **FIRST: merge main into `feature/relay-worker-b2`** — the branch predates `git-hooks/` (2026-10-15), and with
   `core.hooksPath git-hooks` a commit there would run NO checks, silently. Resolve the doc conflicts (TODO.md,
   CLAUDE.md, SESSION-TOOLING.md) in main's favor. Then: drop "-alpha" from `WORKER_VERSION`, update RELAY-WRITE-REDESIGN §14a (fixes 2 and 3 built as report-only; its two open questions are answered — each relay checks its own storage, and Cloudflare's key count is a daily maximum), CHANGELOG (your word on the copy), squash / tag / push to both, post-mortem.
4. ✅ **Released 7.23.0 (deleting), 2026-10-20** — both relays delete leftovers nightly (keep the newest 2 finished
   copies, no grace; unfinished copies 10 minutes; ≤20 keys per run), and the app applies the same rule at each save
   (relay-client.js; the commit check `git-hooks/check-shared-numbers.js` keeps the two in step). Proven on dev
   10-18 → 10-19 (planted test keys; three real extras); production switched 2026-10-20. Every key kind is named in the
   email with its expected count. Why two cleaners: RELAY-WRITE-REDESIGN §14a.
   - **Still open:** confirm production's first deleting night deletes exactly `…21fc` (the Sep 9 torn save).
   - Small follow-up: `relay/test-phase1.mjs` leaves one unimported run on the `22222222…` test channel each run (17 → 18
     on 10-18); they expire after 90 days — make the test clean up after itself.
5. **Then C.**

**Lessons learned**
- Cloudflare had three schedule incidents (2026-10-12, 10-13, 10-14) that delayed schedule changes by **hours** — the replaced 10-minute test schedule kept mailing.
- **Never test with a temporary schedule again.** Test with the on-demand summary instead (PowerShell; one email each; Resend allows 100 a day):
  `$k = Read-Host "TEST_ALERT_KEY"; Invoke-RestMethod -Method Post -Uri ("https://readerwrangler-relay-dev.readerwrangler.workers.dev/run-summary?key=" + [uri]::EscapeDataString($k))`
- ~~Never deploy the relay from main until B2 merges~~ — lifted 2026-10-18: B2 merged in 7.22.0, main carries the current worker.

**Rules**
- Every deploy asks you first (the pre-approved production deploy was removed from local permissions).
- Leave production channel `58c1bfd7…` alone — another user's data; it expires Dec 7.

**Background** (the 2026-10-13 inventory)
- Production unchanged since Sep 9: the interrupted save `…21fc`, the unabsorbed Restore `…3560`, an old-format device-state copy.
- Dev's ~160 MB of Restore packages were reclaimed by the 2026-10-12 Imports (an Import retries cleaning earlier absorbed runs — so the leak was permanent only on a channel that never imports, like production). Dev had 7 device-state copies.
- The Sep 27 dev runs have been imported — that hold is lifted.

**How (technical)**
- Inventory tool: `analyze-relay-keys.js` (key dumps hold channel IDs — credentials — so delete them after use).
- B1 lives in `commitGeneration` (relay-client.js) with `absorbedRuns` deduped.
- Deploy dev: `npx wrangler deploy --env dev`, from `relay/` on the B2 branch.
- B2 alpha.4 = commit `e753679`. The deployment is named by `RELAY_ENV` (prod / dev) in wrangler.toml; the worker's version is `WORKER_VERSION`; the key check compares Cloudflare's `keyCount`.

##### Numbers the app and relay must agree on: add a check that they match
<!-- id 20261014-1030ag -->

_Why it matters:_ The same rules are typed separately in two programs; change one and forget the other, and things quietly go wrong.

_Part of the relay storage work above — build it with B2 (decided 2026-10-14)._

**What this is about**
- ReaderWrangler is two separate programs: **the app** (in your browser) and **the relay** (on Cloudflare).
- A few numbers and rules must be **identical in both**, but each is typed separately in each program's code. Nothing
  complains if they differ.

**Shared today**
1. **How long an upload waits on the relay: 90 days.** The relay deletes an upload after 90 days; the app uses the same
   90 days to decide when it can forget which uploads it already imported. If the relay kept uploads longer but the app
   weren't changed, the app could forget it imported an old upload and **import it again** — re-applying old changes.
2. **The format of upload IDs.** The relay builds each ID from a time, the device and a random part (like
   `1760500000000-dRon-ab12`); the app reads the time back out of it.

**Three more arrive with the relay storage work** (branch `feature/relay-worker-b2`)
- The relay's daily storage check must judge leftovers by **exactly** the app's own cleanup rules: the 1-hour grace
  period, "keep the newest 2 copies", and reading the time out of an ID.
- If they differ, the check would report the app's normal copies as leftovers — and once deleting is on, could delete them.

**Decided** (Ron, 2026-10-14) — option (c)
- A **commit check** reads both programs and refuses a commit when any pair differs. Same style as the table-of-contents
  check; about 30 lines; nothing changes in how either program loads.
- Rejected: (a) leave it to comments and memory; (b) one shared file both load — cleanest in principle, but it means
  restructuring how the app loads its relay code.
- **Build it with the relay storage work (B2)**, where the three new copies come from. It lives in `git-hooks/` (see
  "Save our working process in git").

**How (technical)**
- Pairs: `LETTER_TTL` (worker, seconds) ↔ `LETTER_TTL_MS` (relay-client.js); the minted-ID format (`MINTED_ID_REGEX` /
  `mintId` in the worker ↔ `idTimestamp` in relay-client.js); B2's `SWEEP_GRACE_MS` ↔ `GC_GRACE_MS`, `SWEEP_KEEP_GENS`
  ↔ `KEEP_GENS`, and the worker's `idTimestamp` ↔ the client's.
- Units differ (seconds vs ms) — the check must compare values, not text.

#### Turn more of our working rules into automatic checks (my tooling)
<!-- id 20260922-0000c -->

_Why it matters:_ Rules that depend on memory keep failing; automatic checks don't. This affects only how I work, not the app.

**Already done**
- Item 1: the pre-build checklist now watches all app code (2026-10-08).
- Since then, more checks run on every commit: the undefined-names check, the version stamps (now incl. the relay worker), and the TODO table of contents.

**Left**
- Item 3 below, and the rule-by-rule sort of PRINCIPLES.md.

**The idea** (Ron, 2026-09-22, after "assuming bit us again")
- Go through docs/PRINCIPLES.md rule by rule and sort each one:
  - **Can become an automatic check** that blocks a commit or release — for example: run the tests before a commit; search for leftover TODO / REMOVE markers before release; version bumped when code changed; cache-busters match.
  - **Judgment only** (never assume, model the legal states, UX first). A hook can only *remind*, and reminders fade into rubber stamps. Give these teeth with a required artifact instead: e.g. every design doc must have an **"Assumptions (and how each was verified)"** section, which a hook can check exists when a design doc is written — catching assumptions at design time, not just at edit time.
- Guard against reminder bloat — the pre-build checklist is already 11 points.

**Open items**
1. ✅ The pre-build checklist only watched two files — widened to all app code on 2026-10-08.
2. ✅ **When an edit is bounced by the checklist inside a batch of edits, that one edit silently goes missing** (alpha.62 shipped half a fix; tried twice more on 7.21.2). Done 2026-10-16: the bounce now refuses the WHOLE batch, so the batch is re-sent as a whole. "Same batch" is read from the session's own record (every edit sent together shares one message), not guessed from a timer — Ron's idea, after the first version's 5-second timer refused a quick re-send.
3. **My code safety check can be skipped by accident** (7.19.0 post-mortem). The checklist only fires for my normal editing tool; edits made with a find-and-replace command skip it. Make it fire for those too. Small.

**How (technical)**
- Item 3: the gate hooks only Edit / Write. Add a PreToolUse hook on Bash that spots `sed -i` or redirects onto a root `.js` or the relay worker, and runs the same once-per-turn checklist (reuse `is_app_source()`).

#### Trim the always-loaded rules: one home per rule, history out, a lean memory index
<!-- id 20261021-1332 -->

_Why it matters:_ The more always-on text there is, the less each rule stands out — and a rule kept in two or three
files drifts (the single-source lesson behind the gate's design).

**Baseline** (measured 2026-10-21) — loaded into EVERY turn: the Projects-root CLAUDE.md 11.5 K chars + ReaderWrangler's
CLAUDE.md 10.8 K + the memory index (MEMORY.md) 12.4 K = **~35 K chars ≈ 9 K tokens**. On demand only: the gate
checklist 3.5 K (first app edit of a turn), 68 memory files (388 KB, read when relevant), PRINCIPLES 43 K, TODO 154 K.
Tokens aren't the problem (well under what crowds out work); **weight and duplication are.**

**Targets** (Ron + UX, 2026-10-21)
1. **The memory index** (a third of the always-loaded text): its 26-line "Releases" list is history (6.12 → 7.24),
   not how to work — keep the last ~3, move the rest to an "older releases" index file; make every index line the
   one short hook the format calls for (several are paragraphs).
2. **Both CLAUDE.md files:** move history and rationale ("earned when…", "retired in alpha.43…") to PRINCIPLES / the
   docs; CLAUDE.md states the rule and points.
3. **One home per rule:** find rules that live in two or three of root CLAUDE.md, RW CLAUDE.md, PRINCIPLES and memory;
   keep each in one place and point from the others.

**Safety rule:** every removed line is either **moved to its one home** or **listed as deliberately retired, with Ron's
yes** — never silently dropped. Publish the before / after list of moved and retired lines before committing; re-measure
after.

#### Drag any dialog out of the way
<!-- id 20260928-0000 -->

_Why it matters:_ Dialogs sometimes cover what you need to see; dragging them aside is a habit from Quicken.

**What you'd get**
- Drag any dialog by grabbing it anywhere except its controls (buttons, fields, links, lists). The pointer turns into a move cursor to show it.
- Folder Properties used to be draggable on its own; it lost that in 7.18.0 and gets it back here.

**Decided** (Ron, 2026-09-28 and 2026-10-14)
1. **Stays on screen.** By default you can't drag a dialog so far that you lose it; a strip you can grab always stays visible. A dialog can opt in to dragging fully off the window (as Quicken's Search Results and Reconciliation do); prove that with one dialog.
2. **Where dialogs open:**
   - A first dialog opens centered in the window.
   - A dialog opened from another dialog opens centered over the one that opened it, wherever you dragged it. If you moved a dialog aside to read the app, what it opens appears beside it too.
   - Never "wherever it was last time".
3. **Dialogs underneath are frozen for use.** Their buttons and fields do nothing until the top dialog closes, because the top one may be mid-change.
4. **But every dialog can be dragged, including the ones underneath.** Moving a window changes nothing, so it's always safe. Windows doesn't allow this: you have to close back down, move the first window, and rebuild the stack.
5. **Clicking a frozen dialog does nothing.** Above all, it must not close the top dialog. Only a click on empty background closes it. A brief flash of the top dialog is an optional hint.
6. **Where you can grab it: anywhere that isn't a control or text you might select** (Ron left this to me, 2026-10-16). Pressing on text and moving the mouse must keep selecting text — you copy from descriptions, reviews and notes. So you drag by the title bar, headings, labels, margins and empty space; the move cursor shows only there.
7. **Points 4 and 5 are built together:** a click on the background layer first checks whether a dialog lies under the pointer — if so it's a drag (on its grab areas) or nothing, never a close. Dialogs underneath show the move cursor on the same grab areas as the top one.
8. **Stays on screen when the window shrinks too:** a dialog left off screen is pulled back so its grab strip shows.
9. **Computer only.** On the phone dialogs fill the screen, so no dragging there.

**Watch out**
- "Every dialog" covers two kinds: the standard dialogs, and the older message boxes (OK/Cancel, type-a-name, progress; about 45 places use them), which are built differently. Drag must work in both. The alternative is rebuilding the message boxes as standard dialogs first, which is its own task under "After launch".
- Today a click anywhere outside the top dialog closes it, including on a dialog showing through underneath. Point 5 changes that rule, so test it carefully.

**How (technical)**
- Build drag once in the shared `<Dialog>` (readerwrangler.js ~61) so every dialog gets it at once. The old per-dialog drag code (`dialogDrag`) is already gone.
- Names from the 2026-09-28 decisions: a `cursor:move` affordance; the off-window opt-in is a `dragBounds:'free'` option.
- Message boxes share their window chrome in `attachDialogDismiss` (readerwrangler.js ~237); add drag there.
- A click on a lower dialog actually lands on the top dialog's full-window background layer (readerwrangler.js ~69–71). The background-click close must ignore clicks that fall over another dialog (`document.elementsFromPoint` under the layer).
- "Not selectable text" (point 6) reuses the 7.19 Ctrl+A area marks: `data-select-text` (text) and `data-select-items` (checklists) — readerwrangler.js ~55–60 — plus inputs, buttons, links, lists. No second list to keep in step.
- New user feature, so it gets its own branch and release.

#### Search improvements

The right pane's search box: one shared matching rule (incl. ASIN), and searching everywhere without losing your place. Build both parts together — they answer the same question: "is this book in my library?"

##### Find a book by its ASIN in the search box
<!-- id 20261012-0000 -->

_Why it matters:_ Handy for checking whether one specific book is in your library.

**What you'd get**
- Type a book's ASIN (e.g. `B08P52K2PZ`) into the search box at the top of the right pane, and it finds the book. Today the box matches only title, author and series.
- The box's placeholder and tooltip say what it searches: "Title, author, series, notes, tags or ASIN".

**Decided** (Ron, 2026-10-16)
1. **One shared matching rule everywhere** — the search box and saved Searches, on the computer and the phone.
2. **It matches title, author, series, your notes and tag names** (as the phone's search box already does), **plus an exact ASIN**: only a complete 10-character ASIN, any case. No partial ASINs — almost every Kindle ASIN starts with "B0", so "B0" would match nearly everything.
3. Known side effect, accepted: an existing saved Search may pick up a few extra books whose notes or tag names contain its word.
4. **Build together with "Search everywhere without leaving the current folder"** (next task): a complete ASIN searches Everywhere automatically.

**Bug this fixes** (found 2026-10-16): the rule exists in **four** copies that disagree — computer search box and saved Searches: title/author/series; phone saved Searches: title/author only (**no series**); phone search box: title/author/series/notes/tags. So a saved Search for a series name finds the books on the computer and nothing on the phone.

**Status:** Ron, 2026-10-12 (came up testing removed books). Small.

**How (technical)**
- Copies: readerwrangler.js ~10020 (live filter), `bookMatchesFilters` ~2269 (saved Searches), mobile.js ~343 (`bookMatchesFilters`, saved Searches), mobile.js ~2287 (search box).
- One `bookMatchesText(book, term, tagLabel)` in uiHelpers (tag names need the tag list — pass a lookup); ASIN = exact match of a 10-character term, case-insensitive.

##### Search everywhere without leaving the current folder
<!-- id 20260829-0000a; merged 20261014-1030an -->

_Why it matters:_ Answers "is this book in my library?" without losing your place.

**What you'd get** (Ron, 2026-08-29)
- The search box still searches the current folder by default. While searching, a toggle shows: **This folder | Everywhere** (as in Finder / Explorer).
- "Everywhere" shows matches from the whole library in the right pane, temporarily. Clearing the search returns you to the folder, scroll position untouched.
- **Discoverability:** when nothing matches, offer *"No matches in ‹folder› — Search everywhere?"* as a one-click link (as Gmail and Amazon do).
- Results work with the existing "where does this book live" popup, so the answer arrives with locations.

**Decided** (Ron + UX, 2026-10-16) — moved here from "Everyday organizing"
- **Build together with "Find a book by its ASIN in the search box"** (above): both answer "is this book in my library?"
- **A complete ASIN searches Everywhere automatically** — an ASIN is unique, so "this folder only" is never what you mean. The toggle shows **Everywhere** so you can see why.

**A third way in: "More by ‹author›"** (Ron + UX, 2026-10-21 — merged from "See an author's other books without
leaving your spot": "Today it takes All Books + a filter + finding your way back")
1. **Right-click a book → More by ‹author›** fills the search with the book's **whole author text** and switches to
   **Everywhere**; clearing it returns you to your spot, scroll untouched (the step above). Author text is **never
   parsed** (AUTO-ORGANIZE-UNIFIED.md): from "Jodi Taylor" it also finds her co-authored books (the search matches text
   anywhere in the field); from "Larry Niven, Jerry Pournelle" it finds that combination — type "Niven" for just him.
2. **Right-click a folder → More by ‹author›** when the author comes from data, not a guess: the folder's **name exactly
   matches an author** in the library (Auto-Organize's author folders, e.g. "Jodi Taylor"), or **every book in it shares
   one author** (a series folder like "Time Police"). Answers "what else of hers do I have outside this folder?" —
   Inbox, wishlist, other folders.
3. **Always in the folder menu, in the same place — disabled, not hidden, when it doesn't apply**: then it reads
   **More by this author**, with the tooltip *"This folder holds books by several authors — right-click one of its
   books."* (the menu rule: "Menus keep their items in place", Polish → Small fixes). On a book's menu it's always
   enabled.

**How (technical)**
- Reuse the view-folder filter-stash plumbing for the temporary view.
- Folder case: the "common author" check Auto-Organize already uses when naming.

#### Dark theme: fix the unreadable bar and the light strips
<!-- id 20261007-0000a -->

_Why it matters:_ Some parts of the screen stay light in Dark mode, and one bar's text is unreadable.

**What you see** (View → Theme → Dark)
1. The bar under the menu bar reading **"📡 New library data available (uploaded …)"** keeps its light blue/purple background while its text turns near-white — unreadable.
2. A light strip shows under the **"🔍 Active: Search …"** bar, and wherever there's a gap between sections.
3. Not yet seen by you, same cause: light boxes in the Auto-Organize preview, and likely more.

**Why** (verified)
- Dark mode works by swapping a specific list of colors. Anything colored outside that list stays light.
- The relay bar's background is a fixed light gradient; the app's outer background is a gradient style that isn't on the list.

**Decided** (Ron, 2026-10-16)
1. **Four themes, two screens.** The computer and the phone both have Light, Dark, High-contrast light and High-contrast dark. A fixed light color breaks High-contrast dark exactly like Dark — check Dark **and** High-contrast dark, on the computer **and** the phone.
2. **The commit-time check comes first and produces the list.** Run once over today's code, it lists every fixed color (15 hard-coded backgrounds/gradients in readerwrangler.js alone, plus color classes the dark theme doesn't cover) — that list *is* the sweep. Fix everything on it; from then on the same check refuses new ones. It covers the app's own screens only: the bookmarklet's panels run on Amazon's pages, outside our themes, so their fixed colors are right.
3. **Fix by naming colors, not by adding override rules** ("excellent idea" — Ron). Today Dark overrides a list of 76 specific style classes, and anything missing from the list silently stays light; that list only grows. Instead, each color gets a name defined once per theme ("surface background", "info bar"...) and the screens use the name. A name missing from a theme then shows up in every theme as soon as it's used (no background at all), not just in Dark — and the commit check can verify that every name used is defined in all four themes.

**How (technical)**
- Dark remaps Tailwind classes in readerwrangler.css (`[data-theme="dark"] .bg-white {…}` etc.).
- Relay bar: inline `linear-gradient(135deg, #dbeafe, #ede9fe)` with `color: var(--text-primary)` (readerwrangler.js ~9360).
- Outer container: `bg-gradient-to-br from-blue-50 to-blue-100` (~8992) — gradient classes aren't remapped; the Active bar's `mb-4` gap shows it.
- Auto-Organize preview: `#f1f3f5`, `#fafafa`, `#e5e7eb` (~12009 / 12018 / 12046).
- The check (beside `git-hooks/check-names.js`, run from `git-hooks/pre-commit`): flag inline `background: '#…'`, light `linear-gradient`, `from-*/to-*` classes and Tailwind color classes with no theme mapping, in readerwrangler.js / mobile.js / readerwrangler.css (NOT the fetchers / nav hub); and flag any `var(--name)` that isn't defined for all four `[data-theme]` values. Move each hit to a CSS variable (e.g. `var(--bg-surface)`); retire remap rules as their classes go.
- Themes: readerwrangler.css `[data-theme="dark"|"hc-light"|"hc-dark"]`; phone adds its own variables at mobile.js ~57–59.

#### Series positions: one Position dialog, and one book at several positions (omnibus)
<!-- id 20260915-0000 -->

_Why it matters:_ Three menu items do nearly the same job under different names (Ron couldn't find the one he needed), and a collection should appear at each place it belongs in its series.

**Today's confusion** (found 2026-10-16) — the book right-click menu's **Edit ▸** submenu has **Position...** (one number for every selected book), **Number by current order...** (1, 2, 3… in the order shown, plus an optional series name) and, three items further down, **Set numbers (13, 13.5, 14…)...** (a comma list, one number per book). Ron tried "1, 4" and "1-3" in **Position...** and the box blocked the comma and dash — while its hint text reads "e.g., 1, 1.5", which looks like a list. Each feature was added at a different time as a new menu item; nobody looked at the whole submenu.

**Decided — one Position dialog** (Ron + UX, 2026-10-16)
1. **Edit ▸ Position... is the only one.** Number by current order... and Set numbers... leave the menu; Edit ▸ becomes Author..., Series..., Position..., Format...
2. **It takes a list; each item maps to one selected book, in the order shown.** `13, 13.5, 14` = three books, one number each. A range `7-15` = 9 items (7, 8 … 15), one per book. **Brackets put several positions on one book:** `(4-6)` = an omnibus. Example: `1,2,3,4,(4-6),7-15` = 14 items for 14 books, the 5th being the omnibus. The same number on two books is fine (Ron owns #4 alone *and* the 4–6 omnibus, bought on sale).
3. **Live preview in the dialog:** each selected book by title with the number(s) it will get, updated as you type. A count mismatch is said plainly ("14 numbers for 15 books — one short") and **Apply** stays off until the counts match.
4. **"Fill 1, 2, 3… in the order shown"** is a button in the dialog that writes `1-N` into the box, ready to edit — not a separate feature.
5. **One book selected:** whatever you type is that book's positions — `1-3` is the omnibus — and `(1-3)` works too (Ron: don't punish what the multi-book form taught you). **The book details window's Position field uses the same rule** — one parser everywhere.
6. **One number with several books selected** (`3`, 5 books) gives them all that number, as today; the preview shows "All 5 books → 3".
7. **No series name in this dialog** (Ron + UX): Series... sits right beside it. If the selected books have no series name, the preview adds one line: "These books have no series name — set it with Edit ▸ Series...".
8. **All of it ships together, omnibus included** (Ron): no in-between version to learn.
9. **Showing an omnibus in a series sort: one entry per unbroken run.** `7-9` shows once, labeled "7–9", at 7 — not three identical covers. `1, 4` shows at 1 **and** 4. `1-3, 5` shows twice ("1–3", "5"). *Side Jobs* `2.5, 4.5, 4.6, 5.5` → three entries ("2.5", "4.5–4.6", "5.5"), each between the right volumes.

**Watch out**
- Amazon's fetch also writes series and position. A hand-entered list (`7-9`) must survive later fetches — the "your edit beats Amazon's" protection hand-edited fields have — or the next library refresh quietly undoes it. Verify when built.
- Until this ships, the Position... hint "e.g., 1, 1.5" keeps inviting a list it blocks (readerwrangler.js ~13365).

**What you'd get**
- **One** book record holding **several** series positions, shown once at **each** position when sorted by series.
- An omnibus that **is** volumes 1–3 (`1-3` or `1,2,3`; today's Raj Whitehall "789" workaround).
- An anthology whose stories fall between volumes (`2.5, 4.5, 4.6, 5.5` — the Dresden *Side Jobs* pattern; today you file it at its first position with the story map in the Note).
- A visible cue on the repeats ("also at 4.5", or a ⟳ badge) — deliberate duplication must look intentional.
- **A folder's manual order shows the book once** (manual positions are per book; repeats belong to series-sorted
  views). **A Book List is different — revised 2026-10-21 (Ron):** it's a reading order, so it holds **one entry per
  run** (*"Side Jobs — 2.5"*, *"Side Jobs — 4.5"*), created when a series sort is baked into it — see "Bake this order
  into Manual…" (Polish), which is built after this task.

**Extension: several series in one book** (MegaPacks, Ron 2026-09-20)
- A public-domain MegaPack can hold scattered volumes of several series at once (e.g. Skylark 1, 4 + Lensman 2, 4), possibly by several authors.
- **Keep the common case simple:** one series → the existing Series field plus a numbers field that takes ranges and lists (`1-3, 5`). A **"+ add series"** link reveals a multi-row editor (series + numbers per row) only for the rare multi-series book.
- Filtering matches if **any** of its series match; sorting uses the lowest position.

**Decided**
- **No duplicate book records**, and no fake ASIN-suffixed books (rejected 2026-09-15): they'd fight ASIN-keyed merging, the removed-books scan would flag them every fetch, and duplicate detection, upgrades and CSV would all need special cases.
- **Per-story notes: out of scope** — you already tag notes free-form.
- The rule "no duplicates in a folder" is untouched.

**Open**
- To spec: CSV export (one row, the list in the column). (Settled 2026-10-16 above: how runs display, and "Number by current order" / "Set numbers" folding into the Position dialog.)
- Multi-author MegaPacks: the compound-author problem is separate and pre-existing — not solved here.

**How (technical)**
- `seriesPosition` becomes a parseable list / range, expanded at sort time into display instances (the `_instanceId` render-layer idea — not duplicate records).
- Generalized: `seriesMemberships: [{series, positions:[…]}]` — a normal book is one entry with one position (uniform data; the UI compacts it).
- Ratified direction 2026-09-15.

#### Phone: show which test build is running
<!-- id 20260922-0000 -->

_Why it matters:_ During testing you can't tell from the phone which build it's on.

**What you see**
- The phone's About shows "App v…" — the last **released** version, which by design doesn't change during testing — and "Mobile v…".
- The desktop shows the live test build (e.g. 7.16.0-alpha.6). The phone can't, since it's a different file. The mobile number does change with each test build, but the "App v" line looks stale.

**The real gap** (found 2026-10-16): the phone's "Mobile v…" moves only when the phone's own file changes, but the phone also runs the shared pieces (date presets, storage, sync). A test build that changes only those leaves **both** phone numbers unchanged — 7.21.2's alpha.1 → .3 all showed "Mobile v1.10.1-alpha.1".

**Decided** (Ron, 2026-10-16)
1. **One live build number for both screens, defined once** — a "Build" stamp in readerwrangler.html, which both load. Both About boxes show it the same way: "Version 7.21.3 · Build 7.22.0-alpha.2".
2. **The commit check refuses any app-code commit that doesn't move it**, so it can't go stale. It retires two hand-kept stamps: the desktop's own build number (`ORGANIZER_VERSION`) and the rule that the phone number copies the desktop's "-alpha.N" ending. "Mobile v" can stay as a plain release number, or go. Update CLAUDE.md's versioning section when this ships.
3. **Tell the installs apart on the home screen** (Ron, 2026-10-15): production keeps its icon and name; the **dev** install gets the icon with a red "DEV" overlay and the name "RW Dev"; and plan now for a **local** install (the PC's server over home Wi-Fi — not used yet, but don't close it off): its own overlay ("LOCAL") and name "RW Local".

**How (technical)**
- `APP_VERSION` (released, frozen during alphas) vs `ORGANIZER_VERSION` (live, desktop only) vs `MOBILE_VERSION` (moves per alpha).
- Home-screen icon + name come from the **web app manifest** (`manifest.json`, linked at readerwrangler.html ~14);
  Android wraps it into a "WebAPK" on install. The dev site serves the SAME files as production, so the manifest
  must be picked at run time: `manifest-dev.json` and `manifest-local.json` (own icon + name each) and a line in the
  startup script that points the `<link rel="manifest">` at the right one via `isDevSite()` / `isLocalServer()`
  (readerwrangler.html ~190). Needs the icon images made (192/512 px, DEV and LOCAL). Reinstall after the change for
  the new icon to appear. Watch out: a local install's address is the PC's home-network address, which can change.
- Build stamp: the version-guard (`git-hooks/version-guard.py`) already knows which staged files are app code
  (`shipped_code_staged`) — require the Build stamp line to change whenever that's true, narrowed to what the app
  itself loads (not pages like security.html or the fetchers, which have their own versions).

#### Drag a box to select covers
<!-- id 20261014-1030q -->

_Why it matters:_ Faster than clicking covers one by one.

**What you'd get**
- In cover view, drag a box to select the covers inside it — the way Windows Explorer does.

**Decided** (Ron + UX, 2026-10-16)
1. **Start the box on empty space only** — the gaps between covers, the margins, below the last row. Pressing on a cover and dragging still moves the book, exactly as today.
2. **Plain drag replaces the selection; Ctrl+drag adds to it** (the same split as click vs Ctrl+click).
3. **Live:** covers highlight as the box passes over them. **Esc** cancels the box and puts back the selection you had before.
4. **Auto-scroll:** dragging past the top or bottom edge scrolls the library, so a box can cover more than one screen.
5. **A rectangle, no lasso.** It can span group headers (e.g. two series groups). Computer only — on the phone, dragging is scrolling.
6. **Looks like Explorer's:** a see-through light-blue fill with a thin **solid** border — never dashed (a dashed outline is the "marching ants" on cut books). Its colors are named per theme (see the Dark theme task): in Dark / High-contrast dark, a brighter see-through blue that stays visible.

**How (technical)**
- Extends `explorerSelectedItems`.
- The library hides off-screen rows during a drag to stay fast with 10,000+ books (drag virtualization, readerwrangler.js ~1530) — so work out which books the box covers from the grid's layout (row/column positions), not from what's drawn; otherwise auto-scroll misses books.

#### Faster fetches that report exactly how your library compares with Amazon
<!-- id 20260919-0000a; merged 20260903-0000 -->

_Why it matters:_ Every fetch makes you wait about a minute before you can import, even to grab one new book — most of it a full-library scan that runs twice. And the fetch still can't honestly say "your library matches Amazon exactly", or list the differences.

_Merged 2026-10-20 (Ron + UX) with "Fetch: report exactly how your library compares with Amazon" (spec'd 2026-09-03): the
same full-library pass gives both the speed and the report — one task, two build steps, in order._

**What you see** (Ron, 2026-09-19, patching $0.99 series holes: buy → download → import, again and again)
- Each fetch takes ~1 minute before its books are uploaded, then keeps going with the removed-books check.

**Why** (measured 2026-10-16 from Ron's fetch log: 3,251 books in ReaderWrangler, 2,860 in Amazon's library)
1. **The timing table hides most of the wait.** Its steps add to 14 s (prices 9 s, genres 3 s, the rest ~1 s); the total is 1 min 6 s. The missing ~52 s is the **"🩹 Recovery sweep"** — a full scan of the Amazon library (~96 pages), **before** the upload, not in the table.
2. **The sweep runs on every fetch by mistake.** It should fire only when ReaderWrangler's book count differs from Amazon's, but the count includes wishlist books, which Amazon's library list never has (3,251 vs 2,860) — so they never match.
3. **The removed-books check then scans the same full library again**, after the upload. Every fetch reads the whole library twice. (The code's own comment: "ideally folded into the orphan scan, which already does a full pass.")
- The fetcher already keeps "new books" apart from the rest: new titles are incremental, details only for new books + the few still missing a description, genres only where missing, prices only for books whose price matters.

**Step 1 — one pass, at most once a day: the speed** (decided Ron, 2026-10-16)
1. **One full-library pass instead of two, after the upload.** One scan answers both questions: books Amazon has that we're missing (recover them) and books we have that Amazon no longer lists (removed books). Your new books are uploaded before it starts — the wait before you can import drops from ~1 minute to ~15 seconds.
2. **It compares sets of books, not counts** (the count-based sweep compared things that can never be equal — retire it):
   - on Amazon but not here → missing books → fetch them by ASIN, upload as a small follow-up run;
   - here but not on Amazon → **candidates** for "removed" → re-check just those before flagging.
3. **Then at most once a day** for that pass and the wishlist re-pricing. A day matches when prices start showing as stale (KB §16), so price-watching doesn't suffer. **Always:** new books and their details (series, cover, description) — you need them to file the books.
4. **When it skips, it says so** in the fetch's completion window, with one click to run them anyway: *"Skipped the full refresh (prices, removed-books check) — already done today. Do it now?"*
5. **The timing table lists every step**, the full-library pass included — it hid 52 of 66 seconds.
6. **No Shift/Alt-click shortcut** for this — Windows reports those keys unreliably on clicks, and nobody would discover it.

**Step 2 — the honest report, built on that pass** (spec'd 2026-09-03 by live investigation)
- **The goal:** your library matches Amazon **exactly** — 2,801 = 2,801 unique owned books — once both sides are counted the same way.
1. **Same scope on both sides, unique books.** ReaderWrangler's side excludes the wishlist (337). Amazon's side is de-duplicated: Amazon's total counts **purchase records**, not books (15 sample-then-buy pairs in your data), so use it only as a progress estimate.
2. **Keep Amazon's standard filters everywhere.** Log the filtered-vs-unfiltered difference each fetch (13 today) as an early warning if Amazon reclassifies things.
3. **What you see** (in the same completion window as step 1): a two-way "Removed-books check" report — each direction hidden when it's 0, no "orphan" jargon, an ℹ️ note that they're "still safe in ReaderWrangler". When both are 0: *"Your library matches Amazon exactly."*

**Already done** (toward the report)
- 7.7.0 (2026-09-04) stopped the false alarms: 13 "removed" books were physical items (maps, a DVD, "Shoes") the scan wouldn't count.
- The false-orphan bug itself was fixed in fetcher v5.2.7.
- Two other suspects were checked and ruled out (see TODO notes).

**Also**
- Build together with "Fetch summary should report books you bought" (in "Honest ownership changes", below) — same
  completion window.
- When shipped, update SUPPORT-KB §16: "prices are as fresh as your last fetch" and "every wishlist book is re-priced each run" stop being true.

**How (technical)**
- Recovery sweep: amazon-library-fetcher.js ~1728–1790 (`shouldSweep` compares `existingBooks.length + newBooks.length`, wishlist included, with `stats.libraryTotalCount`). Orphan scan (Phase 5): ~2780. Fold the sweep into Phase 5: one ASIN listing → recover (Amazon has, we don't) + orphans (we have, Amazon doesn't). Recovered books then go in the follow-up run Phase 5 already sends.
- Timing: add the full-library pass to `stats.timing` and the ⏱️ TIMING table.
- Remember `lastFullPassAt` in the relay (shared by all your computers), not browser storage.
- A fetcher (bookmarklet) change, same for all three bookmarklets.
- Comparison details (filters, totals): see TODO notes.

#### Book Lists and Searches: pin and sort them like Folders
<!-- id 20260910-0000a; merged 20261014-1030b -->

_Why it matters:_ A long Book Lists column is hard to search; Folders already have pins and a Name / Manual sort.

**What you'd get**
- Book Lists and Searches in the left pane get **the same controls and words as Folders** (7.6.0): pins (a top tier) and a header sort control, **Manual ↔ Name**. No second ordering system three inches from the first.
- Pinning can be undone (list reordering already can, since 7.10.1-alpha.6).

**How you'd use it** (Ron, 2026-09-10)
- **Name to find** a list, then back to **Manual** for priority.
- Your top tier is the `New To Read - *` work lists (Prime clearing first); series To-Read lists below.
- Today you hunt with Ctrl+F, which costs a switch of thought.

**Decided** (Ron, 2026-10-16)
- **Build together with "A type-to-filter box for the left pane"** (next task) as one left-pane release: pins for **priority**, the filter box for **finding** (it fixes the Ctrl+F hunt more directly than a Name sort), Name / Manual sort for scanning.
- The old "queued behind the book details window rework" line is dropped — no known dependency (Ron).

**Last step: one shared section overview for Searches AND Book Lists** (Ron + UX, 2026-10-21 — merged from "A
management view for Book Lists", spec docs/design/FOLDER-ORDERING.md: clicking a section's name shows its items as
rows in the right pane — name, book count — sortable and reorderable, the way a folder parent shows its folders).
- **One shared piece, same look and abilities for both** (Ron: "make it common code that works for both").
- **Book Lists: clicking "Book Lists" does nothing today** — a dead click (Law 16); this is its fix. It's also the roomy
  place for actions on several lists (delete, rename).
- **Searches: the overview exists but is broken** (Ron's screenshot, 2026-10-21): the header still says "Views" (the
  old name); 3 of the 5 rows have **blank names**; **every count is 0** (the left pane shows 42 / 1742 / 971 / 27); the
  rows wear 🏷️ tag icons and only "Prime" shows a name. Unverified guess: it still uses the pre-6.12 model where a view
  was a tag (looks the name up as a tag — only "Prime" exists as one — and counts that tag's books). Confirm when
  building.

#### A type-to-filter box for the left pane
<!-- id 20260910-0000 -->

_Why it matters:_ With many folders, Book Lists and Searches, typing a few letters is the fastest way to find one.

**What you'd get**
- One box that narrows **Folders + Book Lists + Searches** by name — the strongest pure "find" at scale. The bigger sibling of the pin/sort task above.

**Decided** (Ron + UX, 2026-10-16) — built together with the pin/sort task above
1. **Where:** one box at the top of the left pane, filtering Folders, Book Lists and Searches at once; matches stay under their own section headings (you don't always know which section a name is in).
2. **Collapsed sections:** while filtering, a section with a match opens and a section with none hides; clearing the box puts every section back as you had it.
3. **Keyboard:** **/** jumps into the box, **Esc** clears it. Ctrl+F stays the browser's own find.
4. **It doesn't clear when you navigate** (find one list, open it, then the next) — but while active it stays **visible**: the box shows your text with a ✕, so a narrowed pane never looks like missing lists (the same rule as the right pane's filters).
5. **A matching nested folder shows with its parent folders** (dimmed), so you see where it lives.

**Status:** Ron, 2026-09-10; design settled 2026-10-16.

#### Everyday organizing

Things that trip you up while working through the Inbox backlog.

##### Folder dragging: where you drop decides pinned, and the level
<!-- id 20260803-0000 -->

_Why it matters:_ Folders land somewhere other than where the guide line showed, and sorting reshuffles folders you arranged by hand.

**What you see** (Ron, 2026-10-14)
1. **Wrong level at an expanded folder's edge.** Drag a folder to just above a top-level folder that sits below an
   *expanded* folder: it lands **inside** the expanded folder (after its last subfolder), not at the top level.
2. **Dropped into the pins, placed below them.** Drag a folder (a subfolder of a pinned folder, or an unpinned
   top-level folder) into the pinned area: it lands **below** the pinned folders, unpinned. _(That's the August
   "wall" rule working as designed — now reversed, see Decided.)_
3. **Sorting reorders a pinned folder's subfolders.** Switch to Name A→Z / Z→A: subfolders inside a pinned folder
   re-sort. And they show no 📌, so you can't tell whether they're pinned.

**Decided** (Ron + UX, 2026-10-14 — design of record: docs/design/FOLDER-ORDERING.md, "drag decides pinning")
1. **Where you drop decides.** Dropping among the pins **pins** it (at that spot); dragging a pinned folder below
   the pins **unpins** it. A **divider** under the last pinned folder marks the edge; the guide line shows a **📌** in
   the pinned zone; **one undo** and a message ("Pinned 'X'"). Right-click Pin / Unpin stays.
2. **Sorted mode, dragged out of the pins:** lands at its sorted position; its manual position becomes the **top,
   just below the pins** (the existing rule for every new arrival).
3. **Pinned means hand-arranged, all the way down.** A pinned folder's subfolders (and theirs) keep their manual
   order in every sort mode; new or dropped subfolders inside are placed by hand (new ones at the top). Each shows a
   **faded, non-clickable 📌** with the tooltip "Kept in manual order because 'X' is pinned". The parent's 📌 stays
   the real, clickable control.
4. **The level at an expanded folder's edge:** top half of the next top-level row → **top level** (full-width guide
   line); bottom half of the last subfolder row → **inside** (indented guide line). If nesting is deeper there, add
   horizontal pointer position to pick the level (the outliner convention).
5. **Existing pins inside a pinned folder** (Ron + UX, 2026-10-16): a subfolder that already has its own real pin
   inside a pinned folder becomes **faded like its siblings**, and today's order is kept as its manual order — nothing
   moves on screen. One real pin per branch is the control.
6. **The drop always decides, never memory** (Ron): drag a subfolder to the top level's pinned area → it gets a real
   pin; drag a top-level folder into a pinned folder → it gets the faded pin. No folder remembers an earlier pin
   setting — "where you drop decides" stays the one rule.

**History**
- Replaces "Dragging a subfolder to the top level drops it in the wrong place" (2026-08-03): Ron suspects that one is
  fixed (7.6.0 moved new folders to the top); case 1 above is what's left.

**How (technical)**
- Pins are per level today: `f.pinned` on any folder; each parent's children are pins-first, then the global sort
  (readerwrangler.js ~3052–3087). Rule 3 changes that for children of a pinned ancestor; existing per-child pins
  there migrate per Decided 5 (clear the child's `pinned`, keep its current order as its manual position).
- Drag-to-pin / unpin needs the drop handlers to stop snapping at the boundary (the "wall"), and the drop position to
  set or clear `pinned` as one undo step.
- Check how the drop target's level is computed today before changing it (case 1 suggests row halves are ignored
  at that edge).

##### Stray double spaces in author names create duplicate authors
<!-- id 20261014-1030av -->

_Why it matters:_ An author can split in two, making a series look incomplete.

**What happened**
- "Jodi  Taylor" (two spaces) and "Jodi Taylor" became two authors: 2 of 7 Time Police books were mis-authored, and the series looked incomplete in the Auto-Organize preview.

**Decided** (Ron + UX, 2026-10-16)
- Collapse repeated spaces and trim author names **once, in the shared book clean-up every book passes through on load and arrival** (`normalizeBook` in uiHelpers.js — the same step that fixes "Kindle" → "Kindle Edition"). One line covers fetch, Import, edit, Restore and the phone.
- That also makes the **one-time cleanup** automatic: existing books are fixed the next time they load — no separate tool.
- Only spaces are tidied — a name is never split or reordered (the "never parse authors" rule stands).

#### Tag from Collections, round 2: clearer window, safer tags (decided 2026-10-20)
<!-- id 20261020-1409 -->

_Why it matters:_ 7.24.0 fixed the confusing window; testing it surfaced smaller rough edges — and one real gap: a tag
the tool added stays the tool's even after you remove and re-add it by hand.

**Where it stands:** 7.24.0 shipped the redesigned window (all changes at once, exact-text tag names app-wide, removals
opt-in, undo removes a created tag). Ron's test round on it produced ten topics, all decided 2026-10-20. The decisions
and their reasoning are the **build list** at the top of docs/design/TAG-FROM-COLLECTIONS.md (items 1–10) — read it
before building; this task is the plan. One concern per alpha (Law 6), smallest reach first:

1. **The window** (build list items 1–5) — Select All | Some | None into the left pane's header, both checkboxes into
   the right pane's header; the "No tags to remove…" answer in the status line; checkbox wording ("Remove tags from
   books that left the collection on Kindle" / "Show books already tagged" — no "Also", no "wizard"); **↻ Read** (added
   by Tag from Collections) vs **✓ Read** (yours); how to see only the removals. **When the labels change, update
   everything that quotes them, together** (Ron, 2026-10-21): the greyed-collection tooltip ("tick 'Also show books
   that already have their tag'…", readerwrangler.js ~13066), the two code comments naming the label (~1292, ~12895),
   and the help notes §9 — or the tooltip names a checkbox that no longer exists.
2. **One shared sort, here AND in the list view** (item 6) — click / again reverses / third click off; Shift-click adds
   up to 3 keys; tag columns sort by mark. Changes the list view too (third click turns a sort off).
3. **The checkbox tree + undo inside the window** (item 7) — unchecking a collection clears its skips; a partial box
   (▬) while some are skipped; Ctrl+Z / Ctrl+Y undo the window's choices; the status line names what a bulk click
   erased.
4. **Tag changes confirm themselves; touching a tag by hand makes it yours** (items 8–9) — one shared tag-change
   function shows the confirmation from the same text as its undo (*Created tag "zzz" and added it to 'Title'*); any
   hand change of a tag drops it from the tool's record. Touches every tag change in the app: run the class-of-sites
   comb and publish the list first.
5. **Retire the hidden "seen" field** (item 10) — moved 2026-10-20/21 into the Polish task "Retire two leftover book
   fields: the hidden 'seen' flag and the old price-goal field" (one data round for both).

#### Restore dialog calls yesterday's backup "today"
<!-- id 20260922-0000a -->

_Why it matters:_ A wrong date label can lead you to restore the wrong backup.

**What you see**
- A backup from 9/21 6:54 PM was labeled **"— today"** on 9/22. Not a time-zone effect: it was yesterday everywhere.

**Verified in code** (2026-10-20): the age is counted in 24-hour blocks — `Math.floor((now − backup) / 86400000)`,
readerwrangler.js ~12228 — so a backup from 6:54 PM yesterday reads "today" until 6:54 PM today. The class (every
day-count in the app): the restore dialog = **the bug**; `formatRelativeTime` in uiHelpers.js has the same bug but
**nothing calls it** (dead code); `getRelativeTime` ("3h ago", "2d ago") and the freshness thresholds are elapsed time,
not calendar words — fine.

**Decided** (Ron + UX, 2026-10-20) — a 7.24.x fix on its own `fix/` branch, not done during the review (Ron: "let's not
fall for the quickie trap again")
1. **Calendar days, local time.** Ron: *at 12:01 AM, a backup from 2 minutes earlier (11:59 PM) is "yesterday".*
2. **One shared helper in uiHelpers.js** that counts local calendar days between two dates (through local midnights, so
   a 23- or 25-hour day at a clock change doesn't miscount) and gives the label: today / yesterday / N days ago / N
   weeks ago. The restore dialog calls it.
3. **Delete the dead `formatRelativeTime`** so nobody reuses the buggy copy.
4. **An automated test** across midnight (11:59 PM vs 12:01 AM) and a daylight-saving date. Ron's check: any backup
   file saved yesterday reads "yesterday".

#### Honest ownership changes: buying, samples, loans
<!-- id 20261014-1700 -->

_Why it matters:_ When a book changes kind — bought, a sample, a loan, a book in the Trash — ReaderWrangler should notice, tell you, and never lose your settings.

**What this is**
- One batch, ratified 2026-09-04 (formerly its own section, "⏸️ On hold: honest ownership changes"). **Status: queued**
  (Ron, 2026-10-20 — no longer on hold). Its tasks are below, **in build order**: the rules doc and the foundation
  first, then the data fixes, then the summaries (the polish end — there's nothing honest to report until the fetch
  notices changes). **"Fetch should update books it already knows" goes first.**

**Already shipped from this batch**
- 7.7.2 (2026-09-07): Imports reclaim old upload storage. Its outstanding proof is **settled**: 7.21.1 reclaims on every
  save, and since 7.23.0 (2026-10-20) production's nightly storage check confirms nothing is left over.
- 7.8.0 (2026-09-08): the ownership dialog redesign, the undo fence, undo messages that name what they undo.
- 7.9.0: one unified Auto-Organize. Two pieces were deferred on purpose: "Auto-Organize: Shift-click ranges should
  follow what you see" (a task, Polish) and "let a misfiled book go back to the Inbox" (dropped 2026-10-22 — right-click
  → Move to → Inbox and Ctrl+Z already cover it).
- 7.10.0: Save as Spreadsheet (CSV) — the user who asked for it was sent a reply (no response).
- 7.11.0: item 11. (Item 12 was made unnecessary by the Auto-Organize rework.)

##### Fetch should update books it already knows, not skip them
<!-- id 20260904-0000a; merged 20261014-1030ac -->

_Why it matters:_ A sample or loan of a wishlisted book is thrown away, so the change never shows.

_The foundation — the summaries below depend on it._

**What happens**
- The fetcher skips any record whose ASIN it already knows. On 2026-09-04 a sample record for the wishlisted *Oath of Honor* was thrown away.
- For loans it's invisible **forever** — there's no other path that would catch it.
- **Live case (Ron, 2026-10-14/15):** three *Time Traveler's Passport* stories wishlisted months ago, then borrowed
  through **Prime** — a fresh fetch + Import still shows them as **Wishlist**. The Prime records are skipped as
  "🔁 Duplicate ASIN detected … (skipping)". (Fixed by hand with a console snippet for now.)
- Why buying is different: the price check's "you bought this on ‹date›" backstop catches purchases every run; a
  borrow has no such evidence, only the library record — the one that's skipped.

**Decided** (Ron, 2026-10-15) — **one place for every ownership rule**
- Today the rules are scattered: wishlist → owned lives in the price check, "never downgrade Owned" in the Import
  merge, the list of temporary kinds in a third spot. Put the **whole transition matrix** (OWNERSHIP-MODEL.md §3) in
  **one function** — "given what we have and Amazon's new evidence, what is the book now?" — called by every path
  (the library walk, the purchase backstop, the Import merge), with tests locking it in (like the book-merge tests).
- The ranking it implements: **Wishlist** (bottom — any real Amazon record replaces it) < the **temporary kinds**
  (sample, Prime, Kindle Unlimited, borrowed, library loan, Audible Plus — peers: the **newest record wins**) <
  **Owned** (top — a fetch never downgrades it). Manual Owned / Wishlist choices stay protected. A loan that ends is
  Removed books' job (7.19.0).
- A manual "Other… (Prime, KU…)" choice in the book window was considered and **not** wanted: once the fetch notices
  these on its own, Amazon's facts arrive by themselves — revisit only if cases remain after the fix.
- Details of the rules (merged 2026-10-20 from this task's old "Rules" list): **never downgrade Owned** — full fetches
  include old sample records; "newest record wins" compares the record's date with the **stored** purchase date; your
  own edits are respected. Refreshing the purchase date also fixes a re-walk quirk in how the fetcher remembers where it
  stopped. The existing "past purchase" upgrade becomes just a backstop.
- **Absorbs the old task "Let library loans and Audible Plus books upgrade to owned"** (Ron + UX, 2026-10-20): today
  those two kinds can never become Owned, even after you buy the book — the fetcher's list of temporary kinds
  (`TEMP_OWNERSHIP`, amazon-library-fetcher.js ~2277; written for fetcher 4.11.8, never updated for the kinds added in
  5.2.0; verified still missing 2026-10-14) lacks them, so a bought library loan never upgrades, and loans without a
  price goal are skipped by the price check. The one function, with library loan and Audible Plus in its temporary
  rank, replaces that list — fixing it separately would patch a list this task deletes.

**What you'd get**
- A known book's record becomes an **update**: refresh its kind (owned / sample / loan…), purchase date and format from the record.
- wishlist → sample / loan becomes visible; a library loan or Audible Plus book you then buy becomes Owned.

**How it's tested** (added 2026-10-20 — Ron's live case was fixed by hand, so it's gone)
- **Automated:** the one function gets a test for every row of the transition matrix (OWNERSHIP-MODEL.md §3).
- **Live:** the next real sample or borrow of a wishlisted book should show its new kind after one fetch + Import —
  wait for one, or arrange one (borrow a wishlisted Prime / Kindle Unlimited book).

**How (technical)**
- amazon-library-fetcher.js (~1422–1425 when filed): `seenASINs` is seeded with every known ASIN, so known records are dup-skipped.
- Fields: `ownershipType`, `acquisitionDate`, binding; respect `userEdited`. The watermark re-walk quirk heals with the date refresh. `pastPurchase` demoted to backstop.

##### Relay Import: only books in no folder should go to the Inbox
<!-- id 20260904-0000e -->

_Why it matters:_ A restore once copied the whole library into the Inbox.

**A backstop** (Ron asked, 2026-10-20: "what is an example of a book that is new but already in a folder?"). In normal
use the two rules agree — a book a fetch brings is new AND in no folder. They differ only when your books and your
folders get out of step: the app keeps them in two separate browser stores (books in one, folders and lists in
another), so if the books store is emptied or lost while the folders survive, every book looks "new" to Import. That's
a recovery moment — exactly when a mess in the Inbox hurts most.

**What happened** (diagnosed 2026-09-04)
- On Sep 3, Import from Relay ran as a restore against an emptied book store. Every book looked "new", so all 3,076
  were copied into the Inbox — even though your folders still held them.
- Cleaned up the same day: you restored the 9/3 13:05 backup; only 4 genuinely double-filed books needed hand-fixing.

**Decided** (tidied 2026-10-20: its "Left", "The fix" and "To do" said the same two things three times)
1. **"Goes to the Inbox" = in no folder (and not deleted)** — not "new to the book store". Deleted books are already
   left out (readerwrangler.js ~6638); the folder check is what's missing (still true 2026-10-20: Import adds every book
   new to the store, ~5603).
2. **Add "Import into an empty book store → the Inbox is unchanged" to the pre-launch tests** (PRELAUNCH-TEST-GATE.md
   suite 4 — it covers a cold start with no books, not this Import case).
3. **Test safely:** the automated test is the main check. A by-hand retest ("empty the book store, Import from Relay →
   the Inbox count is unchanged") starts with **File → Save** (a backup) and runs only when no fetch is waiting to be
   imported — it works on your real library.
4. **Independent of the batch's foundation** ("Fetch should update books it already knows") — it's about where Import
   puts books, not what kind they are; build it whenever convenient.
5. **Say it's a backstop, in the code and when it fires** (Ron, 2026-10-20): a comment at the check explaining why it
   exists (books and folders kept in two stores can get out of step — the Sep 3 case), and a console message when it
   actually keeps books out of the Inbox, e.g. *"Inbox backstop: 3,076 books new to the book store are already in
   folders — not added to the Inbox"* — so a real out-of-step event is visible, not silent.

**How (technical)**
- Filter the Import's `newBookIds` (readerwrangler.js ~5603) to books in no folder. The `getAllBookIdsInFolders()`
  named when this was filed no longer exists (checked 2026-10-20) — build the set from the folders at that point.

##### Buying a book that's in the Trash should bring it back
<!-- id 20261014-1030j -->

_Why it matters:_ A book you just bought shouldn't stay hidden in the Trash.

**What you'd get**
- When a book in the Trash becomes owned, it comes out of the Trash automatically. (Ron: "YES! Include it.")

**Decided** (Ron + UX, 2026-10-20)
1. **Built right after "Fetch should update books it already knows", on the same path:** once one function decides
   "this book is now Owned", leaving the Trash is what follows from that answer — every route to Owned (library walk,
   purchase backstop, Import merge) gets it, with nothing extra to remember.
2. **It goes back where it lived before the Trash** — what Trash → Restore already does (since 7.11) — and the
   fetch / Import summary says so: *"1 book you bought was in the Trash — restored to 'Sci-Fi'"* (see the two summary
   tasks below).
3. **Not the emptied-Trash case:** a book permanently deleted and then bought again is the permanent-delete rule's job
   (docs/design/TOMBSTONE-DELETE.md: it comes back if the new purchase is later than the deletion).

**How (technical)**
- Lives in storage.js (the Import merge), via the one ownership function.

##### Fetch summary should report books you bought
<!-- id 20261014-1030t -->

_Why it matters:_ After buying 4 wishlist books, the summary says "0 new" — the upgrades only show in the developer console.

_Polish end of the batch; after "Fetch should update books it already knows". Build together with "Faster fetches that
report exactly how your library compares with Amazon" — same completion window._

**What you'd get**
- The fetch's completion window lists **every ownership change, by kind** — not only upgrades to Owned: e.g.
  "3 wishlist → owned, 1 wishlist → sample, 1 wishlist → Prime loan" (once the fetch notices samples and loans).
- **One count for both summaries** (Ron + UX, 2026-10-20): this window and the app's Import summary describe the same
  changes at two moments; both come from the one ownership function ("Fetch should update books it already knows"),
  so they can never disagree.

**How (technical)**
- Today the upgrades are only logged as ⬆️ in the console.

##### Import summary: every ownership change by kind, kept in the message history
<!-- id 20260904-0000b; merged 20260904-0000c, 20261014-1030z -->

_Why it matters:_ Sample → owned upgrades are missed, wishlist → sample could be mislabeled as owned, and the summary
disappears on refresh, leaving no record of what changed — including which books kept their price goals.

_Polish end of the batch; after "Fetch should update books it already knows". Merged 2026-10-20 (Ron + UX) from three
tasks: "Import summary: count every ownership change, by kind", "Keep the Import summary in the message history",
"Keep price goals when a book is bought, and say so"._

**What you'd get**
1. **Every change counted by kind**, labeled by where the book ended up — e.g. "3 wishlist → owned", "1 wishlist →
   sample" — from the one ownership function (the same count as the fetch's window). The console line names the books
   (a missing title blocked a diagnosis on 2026-09-04).
2. **The whole summary is also recorded in the 🕐 message history**, including its "N kept their price goals" line,
   **naming which books** — so a refresh doesn't erase what changed. (Today only "Cleared N price goals" is logged, and
   only after the click.)

**Already done** (the price-goal part)
- Goals are kept when a book is bought — the rule stands: never silently destroy (Ron, 2026-09-04). Bought books
  already need a visit to All Books to file them, so clearing goals rides along on a trip you make anyway.
- 7.1.0: the Import summary says "N kept their price goals — clear if no longer wanted".
- 7.19.0: "Clear those N goals" clears them in one click (undoable).

**How (technical)**
- Since 6.17.2 the summary reports "N now owned", but it's keyed on the wishlist flag flipping. Key it on
  `ownershipType` transitions instead (the one function's result).

### Polish

#### Move and copy books anywhere — folders, Book Lists, All Books, Searches
<!-- id 20261014-1030ad; merged 20260808-0000, 20260829-0000 -->

_Why it matters:_ Today a cut from a Book List or Search quietly copies instead of moving, and Book Lists were going to
block moves altogether — the app enforcing its internal model instead of doing what you asked.

**The principle** (Ron, 2026-10-21): **don't block the user — honor the intent.** "Not all users will share the same
mental model, nor use RW the same way… there is no wrong way." An icon is an icon: if you move it from here to there,
or duplicate it, across the folder / Book List boundary, do it. Merged from "Ctrl+X from a Book List or Search quietly
copies instead of cutting" and **reverses** "Book List menu: remove Move / Copy, and block dragging onto folders"
(2026-08). That task's evidence — the 2026-08-08 "move" that left books in the Inbox, a folder AND the list — was a
half-done move, not a bad gesture: the cure is complete moves, not forbidding them.

**Decided** (Ron + UX, 2026-10-21)
1. **A move is a true move:** out of the source, into the destination, exactly once, one undo step — every gesture
   (right-click Move to / Copy to, drag / Ctrl-drag, Ctrl+X / Ctrl+C + paste).
2. **A cut takes the book out of the container it was cut from:**
   - from a **folder** → it leaves that folder;
   - from a **Book List** → it leaves that list;
   - from **All Books or a Search** (no container) → pasted into a **folder** it is *re-filed*: it leaves its other
     folders (ask first, listing them, if there are 2+); pasted into a **Book List** it is just added (lists don't file
     books). Book Lists are never touched by a move — only Delete reaches them.
3. **A book that leaves its last folder goes to the Inbox** — "every book is in at least one folder" is a design rule
   the app enforces (integrity.js: books with no folder are repaired into the Inbox), and the Inbox means "not filed
   yet". No dialog; the receipt says it: *"Moved 'Dune' to 'Beach Reads' — it's no longer in any folder, so it's in the
   Inbox."* Undo if you didn't want that.
4. **Copy works everywhere** — it only adds the book to the destination. Book Lists keep **Move to** and **Copy to** in
   their right-click menu.
5. **One rule, asked by every gesture** (menu, drag, keyboard) — a class of sites: list them with two independent
   searches before building, so a fourth gesture can't drift.

**Dragging** (Ron + UX, 2026-10-21 — File Explorer's convention: a plain drag moves on the same drive and copies to a
different one; Ctrl always copies, Shift always moves)
6. **A plain drag within the same kind moves** (folder → folder, Book List → Book List); **a plain drag between a
   folder and a Book List copies — both directions.** Why copy across kinds: dropping "Sci-Fi" (300 books) on a list as
   a move would empty the folder tree and send its only-there books to the Inbox — users would be SURPRISED; and when
   the intent is ambiguous (file a book from "To Read" — done with it on the list, or not?), the default should lose
   nothing (Del in a Book List removes it from that list in one key).
7. **Shift-drag = move, Ctrl-drag = copy, always.** So nothing is blocked: a move across kinds is one key away (Ron:
   "SHIFT drag solves that. Yay!"). The verbs that SAY move still move — Ctrl+X → paste, right-click **Move to**,
   Shift-drag — with decisions 2–3 (a move leaves its source container; last folder → Inbox). Explicit verbs do what
   they say; only a plain drag guesses, and it guesses safe.
8. **The drag says what it will do, live:** the drag label reads *"Copy to 'Sci-Fi' — hold Shift to move"* /
   *"Move to 'Sci-Fi'"* and switches as you press Shift / Ctrl (Explorer's "+ Copy to" / "→ Move to"; Law 16) — the
   default is a visible choice, not a hidden one. (Ron: "the labels are a great idea. I think that seals the deal.")
9. **The receipts:** a Book List moved onto a folder (Shift-drag): *"Moved 12 books from 'Beach Reads' to 'Sci-Fi' (3
   were already there). 'Beach Reads' is now empty."* — several lists: *"…from 3 Book Lists…"*; the emptied list stays
   (deleting a list is its own act); "removed from", never "deleted from" (deleted = the Trash). A plain drag (copy):
   *"Added 12 books from 'Beach Reads' to 'Sci-Fi' (3 were already there)."* No duplicates in the destination.

**From "Drag between Folders and Book Lists"** (merged in 2026-10-21; spec docs/design/CROSS-SECTION-DRAG.md, decided
2026-08-29, its rules 2–3 revised 2026-10-21 to match the above)
10. **Two new drag gestures** (still as decided): drop a folder **on** a Book List's entry in the left pane → adds the
    folder's books to that list; drop a folder or books **between** two Book List entries in the left pane → creates a
    new list there, named "‹folder name› - To Read" for a folder, or by the naming engine for books (e.g. "Beach
    Reads"). Right-click → New also falls back to the current folder's name. (Spec rules 4–7 and its naming rule.)
11. **Honesty fixes:** say what happened (Moved for a move, Added for a copy — was "always say Added from a list
    view"); **no fake "you can drop here" signals** — a target that won't take the drop must not light up (Law 18
    leaves far fewer such targets), including the left pane's blanket drop handling; fix the over-count in the
    message and the leak into the Trash; make Book List reordering undoable. _Verify these three against today's code
    when building — reordering the Book Lists themselves has been undoable since 7.10.1 (`REORDER_BOOKLISTS`), so the
    last may be done._
12. **On ship:** update SUPPORT-KB §8 and §6 (they describe today's behavior).

**How (technical)**
- Today: Ctrl+X is refused only in All Books / the library view (readerwrangler.js ~5223); in a Book List or Search it
  records the view as the source, but paste-cut only removes from **folders**, so the book stays in the list. Found in
  7.10.1-alpha.7, filed not fixed.

#### Retire two leftover book fields: the hidden "seen" flag and the old price-goal field
<!-- id 20261012-0000b -->

_Why it matters:_ Clearing a price goal doesn't fully clear it everywhere, and every save, backup and sync still carries
a hidden field nothing uses any more.

_One data-layer round for both (Ron + UX, 2026-10-21) — the same mechanism and the same kind of test. Merged from
"Clearing a price goal doesn't fully clear it everywhere" and step 5 of "Tag from Collections, round 2"._

**1. The old price-goal field** (`targetPrice`; today's is `priceTrigger`)
- A few places treat a book as "has a goal" if **either** field is set: the Import's "kept their price goals" count
  (storage.js ~176), the fetcher's goal check (amazon-library-fetcher.js ~2286) and the spreadsheet export
  (`priceTrigger ?? targetPrice`, readerwrangler.js ~6305); plus its row in bookFields.js. Clearing a goal clears only
  today's field, so a book still carrying the old one keeps "having a goal" there. Found 2026-10-12; readers
  re-verified 2026-10-20.
- **Counted 2026-10-21 (Ron's library): 0 books carry the old field** (and 0 without a current goal). Keep the one-line
  move-across anyway (an old backup could still carry it): in the shared book clean-up, a book with the old field and
  no current goal gets it moved across once; then the old field is dropped.

**2. The hidden "seen" flag** (`collectionTagSeen`)
- Tag from Collections' "New books only" used it; unused since 7.24.0 removed that option. Every save, backup and sync
  still carries it. Design of record: docs/design/TAG-FROM-COLLECTIONS.md (§2.8, round 2 build list item 10).

**How (both)**
1. **Strip in the shared book clean-up** (`normalizeBook`, on every load and arrival — fetch, Import, Restore, the
   phone), not with a one-off snippet: a returning user or an old backup would bring them back.
2. **Remove both rows from the field table** (bookFields.js), so saves, backups and syncs stop carrying them; then the
   readers above drop them, and test/bookFields.test.js's round-trip cases (which assert both fields survive) change
   to assert they're gone.
3. **Order for the fetcher:** it reads books as stored on the relay, where old copies keep the old goal field until
   their next save — the app's clean-up ships first, the fetcher's `targetPrice` check is removed after.
4. Its own test round (data layer).

#### Moving and selecting

##### Delete a book from All Books (removes it everywhere)
<!-- id 20261014-1030p -->

_Why it matters:_ Today you have to remove a book from each folder and list separately.

**Already done**
- 7.11.0: Delete works from All Books (DEL or right-click) — removes the book from every folder and puts it in the Trash; restoring puts it back in its folders. (Re-confirmed by Ron 2026-10-21 — "can't delete from All Books" had outlived its fix in memory.)

**Left**
- The confirmation doesn't say where the book lives.
- Book Lists aren't in the restore snapshot — their entries are only hidden while the book is deleted.

**What you'd get** (Ron, 2026-10-21: "The intent when I delete from All Books is to delete all copies")
- Delete from All Books moves the book to the Trash, removing it from **every** folder and Book List at once.
- **The confirmation lists every place it lives** (folders and Book Lists).
- **One operation:** a single Undo restores every instance, Book Lists included.

**How (technical)**
- Reuse the membership snapshot, so restoring puts it back everywhere.

##### Open one book's details without losing a multi-selection
<!-- id 20261014-1030ah -->

_Why it matters:_ Lets you identify a book mid-scan and carry on with your selection.

**What you see** (checked in code 2026-10-21)
- The book's right-click menu offers **Edit…** (opens its details) with one book selected; with several, the same spot
  becomes **Edit ▶** (bulk edit). So there's no way to just *look at* one book while several are selected — and a
  plain click on it replaces the selection with that one book.

**Decided** (Ron + UX, 2026-10-21)
1. **A "Details…" item on the book menu** opens **the book you right-clicked**, in the normal view (not edit mode), and
   **leaves the selection exactly as it was**. "Details" matches the window's name (the book details window).
2. **Always there, in the same place** — one book or many selected — so the menu doesn't shift (the rule in "Menus
   keep their items in place").
3. **‹ › inside steps through your selection** when the right-clicked book is part of it — today's "shelf", no longer
   forced.
4. **Pairs with "Restore the previous selection"** (below): this is the safe way to look; that one is the safety net
   when a click wipes the selection anyway.
5. Verify when building (not before): how a double-click on a cover treats a multi-selection today — the old note
   "opening from a multi-selection opens the whole selection as a shelf you step through" came from that.

##### Restore the previous selection after a stray click or Select All
<!-- id 20261020-1239 -->

_Why it matters:_ A careful multi-selection (Ctrl-click by Ctrl-click) is lost to one stray click, Ctrl+A, Esc or a
folder switch — and nothing brings it back.

**What you'd get** (Ron + UX, 2026-10-20)
1. **Restore previous selection** — brings back the selection you had just before it was replaced or cleared. One
   level (the one just lost), like Photoshop's **Select → Reselect**.
2. Reachable from the right-click menu and a keyboard shortcut (pick one that's free when built).
3. **Not part of Undo.** Ctrl+Z stays for changes to your library; selection is view state, and putting every click
   into undo would make Ctrl+Z step through clicks before reaching a real change — the ratified rule in
   docs/design/UNDO-MODEL.md ("view state … not undoable").

**Why now** (2026-10-20): Tag from Collections gets undo for its own choices in its round 2 (its checkboxes are a
draft of what Apply will do — docs/design/TAG-FROM-COLLECTIONS.md, build list item 7; it did not ship in 7.24.0). Ron asked for the same safety "everywhere
(in a folder for instance)" — this is that, in the convention that fits a selection.

#### A folder or Book List you just created stays visible under filters
<!-- id 20261014-1030a -->

_Why it matters:_ With filters on, a new folder is hidden the moment you create it (it has no matching books) — the
app filtering something you obviously didn't mean to filter.

**What you see**
- With filters active, create a folder. A notice says the filters are hiding it and it won't appear in the left pane.
  The notice has no Cancel, so the folder stays, hidden — and its rename box can open on a row you can't see.

**Decided** (Ron + UX, 2026-10-21 — replaces the 7.14.2 decision: a 4-button notice now, "warn before creating"
later; both added an interruption around a rule that shouldn't apply — Law 18)
1. **A folder you just created stays visible, whatever the filters, until the filters change** (Excel's rule: a row you
   just added stays visible under a filter until you re-apply it). It appears where you made it, rename box open as
   usual.
2. **A quiet marker explains it** when its count is 0 — e.g. *"new — no matches for your filters"* (Law 16).
3. As soon as you change or clear the filters, it follows the normal rule.
4. **No notice, no buttons, nothing to cancel** — Ctrl+Z undoes the creation, as for any folder. The old notice
   (`newFolderHiddenAlert`) goes.
5. **The same for a Book List you just created** — the left pane hides Book Lists under filters by the same rule
   (`blHiding`, readerwrangler.js ~14719). When building, list every "just created, then hidden" path (two independent
   searches) before claiming coverage.

**How (technical)**
- The notice is raised from 3 places (search `setNewFolderHiddenAlert`); remove them with it.
- Keep a "just created" id set that the filtered folder / Book List lists always include; clear it when the filters
  change.

#### Book details window: one Save — nothing changes until you click it, and nothing is lost without asking
<!-- id 20260910-0000b; merged 20261015-1644, 20261014-1030ba -->

_Why it matters:_ Today some fields save instantly and others wait for Save; Save is enabled even when nothing changed;
and every way out of edit mode throws your changes away without a word. One rule makes the window predictable, with
one undo per Save. (Public promise: README's Coming Soon — "A calmer book editor".)

_Merged 2026-10-21 (Ron + UX) from "Book details window: changes happen only when you click Save" (ratified
2026-09-10) and "…Save only when something changed; offer Save before closing with unsaved changes" (2026-10-15) —
they share one "what changed?" check. Two steps, in order: step 1 is smaller and works on today's fields._

**Step 1 — Save only when something changed; ask before losing changes** (decided Ron + UX, 2026-10-15)

What you see (Ron, 2026-10-15):
1. Open a book → **Edit**: **Save** is enabled even though nothing has changed.
2. Change something, then **Cancel** — or Esc, ✕, or a click on the background (all four do the same): the changes are
   gone, with no warning.

Decided:
1. **Save is disabled until something changes**, with a tooltip "No changes to save". Enter with nothing changed just
   leaves edit mode.
2. **With unsaved changes, every exit asks** — Cancel, Esc, ✕, background click, ◀ ▶ to another book, closing:
   > **Save your changes to "‹title›"?**  **[Save]** · [Discard changes] · [Keep editing]
   1. **Save is the default** (Enter) — the common case is an accidental exit, and a saved edit can be undone;
      discarded changes can't.
   2. "**Discard changes**", never the default, so no keystroke picks it by accident.
   3. **Esc in this dialog = Keep editing** (back out of the question).
   4. Only when something changed — otherwise exits just close, as now.
   5. The same one dialog for the explicit Cancel button too (uniform beats two variants).
3. **One "what changed?" check** drives both — the comparison Save already makes. Step 2's fields join it.
4. (2026-10-21, gate item 13) The exit question passes Law 18 — a confirmation for a genuinely destructive case (losing
   unsaved edits), with Save as the default guessing the likely intent.

**Step 2 — changes happen only when you click Save** (ratified 2026-09-10)
1. In the book details window, **Edit → Save is the only way anything changes** — one undo per Save. Cancel throws
   away everything you changed (after step 1's question).
2. Rating, price goal and tags stop being instant controls: they're saved with everything else. A new tag is created at
   Save.
3. **Click-to-edit, so no click is dead** (2026-10-21 — the 2026-09-10 decision said "read-only in view mode", which
   predates Laws 16 and 18: a star you can't click would be a dead control refusing a clear intent). **Clicking any field
   in view mode switches to edit mode right there:** the 4th star → edit mode with 4 stars staged; the price goal →
   edit mode with its box focused. Still nothing saved until Save.
4. **Commands stay live in both modes:** Share, the Amazon link, Status History, ◀ ▶ (previous/next book).
5. Outside the window, changes stay instant (one undo each).
6. **Quick access** (replaces the instant controls): in list view, click the Price Goal or My Rating cell to set it in
   place (preset goals / custom amount, or a row of stars). Decide during the build: should right-clicking a cover also
   offer a My Rating submenu?
7. **First, classify every control** in the window as a field (saved by Save) or a command (acts now) — **with a
   tooltip column**: each control's tooltip wording where it isn't self-explanatory (e.g. Collections: "Read-only:
   comes from your Kindle collections on Amazon"). Merged 2026-10-21 from "Tooltips in the book details window" — one
   pass through the window covers behavior and wording. Publish the table for Ron's red pen **before** any code. Its own branch; version number assigned when the work starts (the old
   "7.14.0" label is stale).

**How (technical)**
- `enterEditMode` / `cancelEditMode` / `saveEditMode` (readerwrangler.js ~7022–7160 on 2026-10-21); `saveEditMode`
  already diffs `editBookFields` against `modalBook` — extract that into one `bookEditChanges()` used by Save's enabled
  state and by the exit guard. The dialog's onClose in edit mode routes to `cancelEditMode`.
- The confirmation is a `<Dialog>` (overlay system) — not a hand-built box.
- Step 2: rating / price goal / tags join `editBookFields` as staged fields; Save folds them into the one `EDIT_BOOK`
  undo step. Completes the edit-in-place pattern in OWNERSHIP-MODEL §4. Rationale and Ron's context-keying principle:
  UNDO-MODEL.md, section "fully transactional".

#### Relay Setup: smoother sections and clearer Esc / Help behavior
<!-- id 20260928-0000a -->

_Why it matters:_ Its sections jump open so abruptly they look like new windows, and Esc behaves differently in a way you can't see.

**What you see** (File → Relay Setup)
1. **Sections jump.** Opening "Credentials" / "Enter Credentials Manually" or "Bookmarklet" / "Pairing" shoves everything up and down so hard it reads as "a new window appeared".
2. **A hidden level.** "Enter Credentials Manually" secretly counts as a level of its own: Esc backs out of it first instead of closing Relay Setup. Nothing shows you that.
3. **Help looks like a replacement.** Help opens exactly on top of Relay Setup, so it doesn't read as stacked on it.

**Decided** (Ron + UX, 2026-10-21)
1. **Animate the sections opening and closing** (~150–200 ms), so the eye can follow what moved; respect the system's
   "reduce motion" setting.
2. **Drop the hidden level: Esc closes Relay Setup**, like a background click — a section folding open isn't a layer
   (the overlay system's Esc closes the innermost *layer*). If the manual-credentials fields hold typed-but-unsaved
   text, closing asks the same *Save / Discard / Keep editing* question as the book details window — ideally the same
   shared piece, so "ask before losing what you typed" works alike in every window with a form.
3. **Open Help slightly offset** (~24 px down and right, like stacked windows) so it reads as on top of Relay Setup,
   not replacing it; "Drag any dialog out of the way" (High priority) adds the full fix later.

**Status:** noted 2026-09-28 during the overlay work; a separate, focused redesign pass. **Build it together with
"Rename 'Relay' to 'Cloud Sync' everywhere users see it"** (Before launch) — that rename changes this window's name and
wording; one pass touches and re-tests the window once.

**How (technical)**
- Item 2 is the `onClose` branch that handles `reason === 'esc'` specially in the Relay Setup dialog (readerwrangler.js
  ~11371 on 2026-10-21: `reason === 'esc' && relayManualCreds` closes only the section).

#### Arrow keys should move through every type-ahead list
<!-- id 20260929-0000 -->

_Why it matters:_ You can't pick a series from the list with the keyboard — Down scrolls the window instead — and the
same is likely true of most of the app's type-ahead lists.

**What you see**
- In both Series fields — the book details window's edit mode (✏️), and Bulk Edit → Series… — open the list (type a letter or click ▼) and press Down.
- Nothing moves through the list. In the book details window, Down scrolls the whole window instead.
- Enter takes what you typed, not a highlighted row.

**What you'd get** (the standard pattern)
- Down / Up move a highlight through the list while the cursor **stays in the text field**, so you can keep typing.
- Enter picks the highlighted series. Esc closes the list (already works).
- While the list is open, Down / Up never scroll the window.

**The model already exists**
- The search box's "Recent searches" list works exactly this way today. Extract that and use **one implementation for
  every type-ahead list**.

**Every type-ahead list, not three** (Ron + UX, 2026-10-21) — "Down moves, Enter picks" must work in all of them, or
people learn it works in some places and stop trying. Found 2026-10-21 by their prompt text (a start, not proof):
recent searches (the search box, ~1170 — the working model); Series in book details (~13825) and in Bulk Edit
(~13475); Tags "Type to search or create" in book details (~14162) and right-click → Tags (~19790); "Type to filter
your folders" (~12734); "Filter authors by name…" (~12064); and the planned filter box in the "Save results" menu.
**When building, find them with two independent searches**
(by prompt text and by the shared list popup) and publish the list before claiming coverage. **Build together with
"One shared tag picker"** (Small fixes) — it sits on this behavior; one pass covers both tag lists.

**Status:** deferred by Ron 2026-10-06 (minor accessibility fix).

**How (technical)**
- Build it once in the shared list popup (`<Popover kind="list">` — both Series lists became that in 7.18.0-alpha.54), not per field.
- The working model is the `SearchInput` component's Down/Up/Enter/Esc handling. Stable copy "as it was": `git show 46a0cf6:readerwrangler.js`, search for `const SearchInput`.

#### The "Save results" menu runs off the screen with many Book Lists
<!-- id 20261006-0000b -->

_Why it matters:_ With 20+ Book Lists, the lower ones are cut off and can't be reached.

**What you see**
- With a search or filter active, click the **💾 N results · Save ▾** button in the bar above the books.
- The menu lists every Book List. With about 20 or more, it's taller than the window and the bottom ones are cut off, with no way to scroll. A long flat list is also slow to scan.

**What you'd get**
- The menu opens on whichever side of its button (above or below) has more room, fits that space, and scrolls — the usual approach in modern menus.
- With more than ~10 lists, a filter box at the top — reuse the one the book right-click menu's "Move to" submenu already has.

**Watch out**
- This must **not** apply to right-click menus with fly-out submenus (Move to / Copy to): a scrolling menu would clip its own fly-outs.

**Status:** designed and deferred by Ron 2026-10-06.

**Build on the shared scrolling list** (Ron + UX, 2026-10-21) — the one from "Long lists keep their actions in view"
(below): its **top slot** holds the filter box (always visible while the list scrolls), the **middle** scrolls your
Book Lists, its **bottom slot** an action like "New Book List…"; and the **fit-to-the-roomier-side** behavior lives in
that shared piece, so every long list gets it. This menu is its first user after the tag lists. The filter box is one
more type-ahead list for "Arrow keys should move through every type-ahead list". (The old line "check other menus
that list your own items" moved to the long-lists task's sweep.)

**How (technical)**
- In the shared list piece (a `<Popover>` option for button dropdowns): when it can't fit below, pick the roomier side,
  cap the height, scroll.
- Today it pins to the top of the window and hangs off the bottom. The fly-out rule is CursorPopup's "never add overflow".

#### Long lists keep their actions in view (Manage…, Select All) while you scroll
<!-- id 20261019-2015 -->

_Why it matters:_ An action at the end of a long list scrolls out of sight — it looks missing, so it's never used.

**What you see** (Ron, 2026-10-19)
1. The **Tags** filter in the bar above the books: "Manage Tags…" seemed to be missing. It's there — at the very
   bottom; the whole menu scrolls as one piece, so with a dozen tags it sits below the cut-off. "Select All / Clear
   All" at the top scrolls away the same way.
2. Right-click a book → **Tags** does it right: only the tag rows scroll; "Manage Tags…" stays put below them.

**The rule** (Ron + UX, 2026-10-19) — sort what sits at the top or bottom of a list into three kinds:
1. **Actions on the whole list** ("Manage Tags…", "Create…", Select All / Clear All): **always visible** — fixed
   above or below the scrolling part.
2. **Notes about the list** ("No tags to remove…"): **not** pinned — a fixed note costs a line forever and stops
   being read. Put it where people look for status (e.g. a window's status line).
3. **Ordinary rows** that happen to be first or last: scroll normally.

**The mechanism, not a cleanup:** ONE shared scrolling list with a fixed top slot and a fixed bottom slot. Fixing
each list by hand doesn't stop the next new list from repeating it; with one shared piece, every new list gets it.
1. **Build the piece**, then move every list with top/bottom actions onto it.
2. **Known places so far** (found 2026-10-19 — a start, not the full list):
   1. **The Tags filter** (bar above the books) — **broken:** the whole menu scrolls as one piece (capped at 300px,
      readerwrangler.js ~9868–9877), taking "Select All / Clear All" (top, ~9906) and "Manage Tags…" (bottom, ~9977)
      out of sight. It also has two copies of the "Manage Tags…" link (no tags ~9900 / some tags ~9977) — make one.
   2. **Right-click a book → Tags** — **already right, the model:** only the tag rows scroll (~19857); "Manage Tags…"
      sits below them (~19933).
   3. **Tag from Collections' "No tags to remove…" note** — handled in "Tag from Collections, round 2" (its design's
      build list item 2), not here: it's a note, so it moves to the window's status line rather than being pinned.
   4. **Auto-Organize's preview — "File under… / Choose folder"** (Ron, 2026-10-22) — **broken:** it sits at the
      bottom of the scrolling preview, so you scroll to the end to find it ("not discoverable"). It's an action on the
      selection → pin it below the scrolling part.
3. **Find the rest with the comb** — two independent searches (lists that scroll; trailing "Manage…" / "Create…" / "…"
   items) plus a walk of every menu, right-click menu, dropdown and dialog list. Publish the list of places before
   calling it done. **Include menus that list your own items** (Book Lists, folders) and **run off the screen** —
   moved here 2026-10-21 from "The 'Save results' menu runs off the screen", whose menu is the piece's first user
   after the tag lists; the piece also owns fit-to-the-roomier-side.
4. **Pair it with "One shared tag picker"** (Small fixes) so both tag lists move onto the piece together.

**Related:** "The 'Save results' menu runs off the screen" (above — the same list could carry its fit-and-scroll
fix) and "One shared tag picker" (Small fixes — it would sit on this piece). Deferred from 7.22.1 by Ron, 2026-10-19
(no regression; scrolling down is the workaround).

#### Removing a recent search should offer Undo
<!-- id 20261007-0000b -->

_Why it matters:_ One click deletes a recent search with no message and no way back.

**What you see**
- Click into the search box so "Recent searches" appears; click the × on a row.
- It's gone instantly: no message, no Undo, nothing in the 🕐 message history.
- By contrast, deleting a **saved** Search (left pane → SEARCHES → right-click → Delete Search) confirms, shows a message, and can be undone.

**Decided** (Ron + UX pass, 2026-10-07; re-checked 2026-10-21 — still true in code: `removeRecent` just filters and
saves; passes Laws 16 and 18)
- Same treatment as a saved Search, **minus the confirmation**: remove at once, show a message that names it —
  *"Removed 'jodi taylor' from recent searches · Undo"* — and log it in the 🕐 history.
- No "Are you sure?" — recents are automatic history, and a question per row would nag.
- Route it through the shared undo/message path (the one tag and Search deletes use since 7.11.0), not a one-off.

#### "Bake this order into Manual" for a folder's books and a Book List, from the Sort menu
<!-- id 20261014-1030g -->

_Why it matters:_ Put a folder or a Book List in series (or any) order once, then adjust it by hand — today that's only
possible for the folder tree, from a menu you wouldn't look in.

**What you see** (Ron, 2026-10-21): the command exists — **"Bake this order into Manual…"** — but only in the left
pane's **FOLDERS → Name ▾** menu, and it orders the folder **tree**, not the books in a folder. Ron looked for it in the
right pane's Sort menu ("I'd expect it in the Sort menu") and couldn't find it. It also **appears only when the sort
isn't Manual** (readerwrangler.js `bakeOrderToManual`, ~3595; menu ~15947).

**Decided** (Ron + UX, 2026-10-21 — widened from "Book Lists: arrange by series number")
1. **One shared "Bake this order into Manual…" in the right pane's Sort menu**, for whatever the pane shows — a
   folder's books or a Book List. Arranging a Book List by series is then: sort by series, Bake.
2. **Always in the menu, in the same place; disabled (with a tooltip) when the sort is already Manual** — the menu rule
   ("Menus keep their items in place"). The left pane's existing one gets the same disabled-not-hidden fix.
3. **A multi-position book in a Book List gets one entry per run** (Ron: a Book List "is my reading order"): baking a
   series sort creates them, labeled with the run — *"Side Jobs — 2.5"*, *"Side Jobs — 4.5"* (the same "one entry per
   unbroken run" rule as series sorting); after that each moves independently; removing one entry removes only that
   occurrence. **Folders keep "once"** (manual order there is where a book is placed). These are list entries, not
   duplicate book records. This revises one line of "Series positions…" (High priority) — **build after it.**

**Not to confuse with:** "Number by current order", which sets each book's series **number** (it folds into the one
Position dialog — see "Series positions…").

#### Small fixes

##### Tidy up the notes
<!-- id 20261020-1448 -->

_Why it matters:_ Housekeeping — a few notes are in the wrong place. Details: see TODO notes.

##### Leave the affiliate tag off Amazon links on the test rig
<!-- id 20261021-1401 -->

_Why it matters:_ Ron's own testing clicks — and any purchase through them — count against RW's affiliate account,
muddying the stats, and Associates doesn't pay on your own purchases (repeated ones can draw a warning).

**What you see** (2026-10-21): every "Open in Amazon" / Share link carries the tag on every build, localhost included
(`getAmazonUrl` in uiHelpers.js). The Associates dashboard showed 6 orders, 0 shipped, $0 — click spikes on Oct
12–16 match Ron's test sessions.

**Decided** (Ron + Claude, 2026-10-21)
- **Ask the existing central check — don't re-read the address:** leave the tag off when **`isTestingTraffic()`**
  is true (readerwrangler.html, 7.21.0: contributor mode — local server AND this browser's `readerwrangler-contributor`
  flag — or the dev site). Plain localhost is NOT enough: a self-hoster is localhost too and gets production behavior,
  tag included (the same split contributor mode already makes for the relay and the usage statistics).
- One place: `getAmazonUrl` asks it; nothing else builds a tagged link (verify with a search when building — the
  phone app and Share included).

##### Switch the affiliate tag to "readerwrangler-20"
<!-- id 20261021-1401a -->

_Why it matters:_ A tracking ID just for the app (created by Ron 2026-10-21) separates ReaderWrangler's clicks and
sales from Ron's WordPress articles in the Associates reports (today they're combined).

**To do**
- Change the one definition: `AMAZON_AFFILIATE_TAG` in uiHelpers.js (verified 2026-10-21: the only place in the code;
  the old tag `rclewent-20` stays on the WordPress articles). Bump uiHelpers.js's cache-buster.
- Update the examples in docs/design/SHARE-BOOK-FEATURE.md (they show the old tag); post-mortems stay as history.
- Pairs with "Leave the affiliate tag off Amazon links on the test rig" — same function, build together.

##### Tooltips where they help: icon-only, disabled, non-obvious, cut-off
<!-- id 20261021-1608; merged 20261014-1030az -->

_Why it matters:_ A control that doesn't explain itself gets skipped or misused — but a tooltip on every control is
noise that teaches people to ignore the ones that matter.

**The rule** (Ron + UX, 2026-10-21 — not "every control": a Save button whose tooltip says "Save" is noise; ~190
tooltips exist today). A tooltip is **required** on:
1. **Every icon-only control** (✕, 💾, 🗑, ⚙ …) — no words at all; it also needs a screen-reader label (overlaps
   "Finish keyboard accessibility", After launch).
2. **Every disabled control — saying why** (the rule in "Menus keep their items in place").
3. **Any control whose effect isn't obvious from its label** (Collections is read-only; "Bake this order into Manual").
4. **Text that gets cut off** — the tooltip shows it in full.
Everything else: no tooltip, deliberately.

**To do**
1. **First, a commit check for rule 1** (mechanical, so it can't decay): refuse an icon-only button with no tooltip or
   screen-reader label.
2. **Then the sweep** for rules 2–4 (judgment): two independent searches plus a walk of every dialog and menu; publish
   the list of places first.
- Absorbs "Tooltip review: Tag from Collections wizard" (After launch, one line — "Make sure every control explains
  itself"); that window's new tooltips (the ↻ / ✓ legend) are also written in its round 2. The book details window's
  tooltips are a column in "Book details window: one Save…" step 2.

##### Menus keep their items in place: disable, don't hide
<!-- id 20261021-1131 -->

_Why it matters:_ People find menu items by position as much as by word — an item that appears and disappears shifts
everything below it, and the click lands on the wrong thing (Ron, 2026-10-21: "menus that shift around [are]
confusing. Often I go by position almost as much as the word").

**The rule** (Ron + UX, 2026-10-21 — PRINCIPLES Law 16)
1. An item that **can** apply to this kind of thing stays in its place, **disabled** when it doesn't apply right now,
   with a tooltip saying why.
2. An item that can **never** apply to this kind of thing isn't in that menu at all (a book's menu has no "Empty
   Trash") — no shifting, because that menu always has the same items.
3. The test is "can this kind of object ever use it?", not "does it apply this moment?"

**To do:** check every menu (the menu bar's menus, every right-click menu, dropdowns) for items that come and go by
the current situation; make each one stay and disable instead. Publish the list of places first (two independent
searches, plus a walk of every menu). New items follow the rule from now on (e.g. "More by ‹author›" on a folder).

##### A book's hover popup stays up after the book is deleted
<!-- id 20261021-1026 -->

_Why it matters:_ It goes on describing a book that's gone — and could describe the wrong book.

**What you see** (Ron, 2026-10-21)
- In All Books, hover a book (the popup shows its folder), press **Del**: the book goes to the Trash and the covers
  shift over one, but the popup stays, now saying "Was in (before Trash): Folder X · Found in Trash". Moving the mouse
  slightly brings up the new book's popup.

**Decided** (Ron + UX)
- The popup closes when its book leaves the view. It's tied to the cursor's position, not to the book still being
  there; being right about the deleted book is luck — a shift could put a different book under the cursor.
- "Moved from Folder X" belongs in the Trash receipt instead: name the folder there.

##### The Trash ignores the search and filters
<!-- id 20261021-1026a -->

_Why it matters:_ With a filter on, every other place narrows to the matches — the Trash doesn't, which surprises.

**What you see** (Ron, 2026-10-21)
- With a filter on, the left pane shows Inbox as "0/956" (matching / total) but Trash as "(36)" — all of it. Opening
  the Trash shows every trashed book, not the matches.

**Decided** (Ron + UX)
1. **Inbox and Trash stay visible at 0 matches** — they're landmarks; fixed entries appearing and disappearing as you
   type is disorienting.
2. **The Trash follows the filter like Inbox:** its count reads matching / total ("0/36"), and opening it shows only the
   matching books.

**How (technical)**
- `trashCount` counts every deleted book with no filter (readerwrangler.js ~2492). No recorded reason found — an
  oversight. Check whether the Trash's *contents* skip the filter by design when building.

##### Show only hidden books
<!-- id 20260903-0000c -->

_Why it matters:_ Answers "what have I hidden?" — today you have to hunt for them.

**What you'd get** (ratified 2026-09-03)
- "Show Hidden" becomes three choices: **Hide hidden** / **Show all** / **Only hidden**.
- Today it only shows or hides them, so finding the 2 hidden books among 337 is impractical.

**Decided** (Ron + UX, 2026-10-21 — still a plain on/off in code: `showHidden`)
1. **A "Hidden ▾" filter button like its neighbors** (Read Status ▾, Tags ▾, Ownership ▾) instead of the checkbox:
   nothing new to learn, it lights up when not at the default, and its list shows the count — **"Only hidden (2)"**.
2. **Saved Searches keep working:** they store the old on/off (`filters.showHidden`, readerwrangler.js ~4057) — *off*
   becomes **Hide hidden**, *on* becomes **Show all**. The phone app has its own Show Hidden (mobile.js
   `filterBooks`): it gets the three choices too, or at least reads them.
3. **Settle the real default:** the app starts with hidden books hidden, but one place says
   `showHidden: true, // Default to showing all books` (~6688). Decide which is right so a new user isn't surprised.


##### One shared tag picker: show all tags in your order (the right-click one silently stops at 10)
<!-- id 20261015-1717 -->

_Why it matters:_ A tag you use constantly ("Read", 964 books) can be missing from the list with no hint why — and the two tag pickers disagree on what to show.

**What you see** (Ron, 2026-10-15)
1. Right-click a book → **Tags**: "Read" isn't in the dropdown. Typing "Read" in "Type to search or create…" finds it,
   with 964 books.

**Why** (verified in code)
1. There are **two separate tag pickers** that have drifted apart:
   1. **Right-click → Tags** shows only the **first 10** tags, in your custom order from Manage Tags — a silent cut-off
      (the code even says `// Limit to 10`). "Read" is past the 10th, so it's hidden until you type.
   2. **The book details window → Tags** shows **all** tags, but **A→Z** — ignoring your custom order — in a short
      scrolling box.
2. Same class as the three copies of the search rule ("Find a book by its ASIN"): one control, copied, drifting.

**Decided** (Ron + UX, 2026-10-15)
1. **One shared tag picker**, used in both places (and anywhere else tags are picked) — one implementation.
2. It shows **all** tags, in **your custom tag order** (Manage Tags), in a scrolling list.
3. The search box stays at the top to narrow it ("Type to search or create…"), as the "Move to" submenu's filter box does.
4. **No silent limit.** If a cap is ever needed, it says so: "…23 more — type to filter".
5. Keeps what both have today: tags already on the book(s) aren't offered again (re-confirmed 2026-10-20, Tag from
   Collections round 2 topic 8); **"Create ‹name›" appears unless a tag with EXACTLY that name exists** — capitals
   count since 7.24.0 — with the capitals prompt for a near-twin ("A similar tag exists"). Don't rebuild the old
   capital-blind check.

**Decided — tag order everywhere follows Manage Tags** (Ron + UX, 2026-10-18; recorded in
docs/design/TAG-FROM-COLLECTIONS.md §7 as "added to this task" but it never arrived — added 2026-10-22). Ron's alpha.3
note: the Tags filter and right-click → Tags aren't in Manage Tags order (book details is A→Z).
1. Manage Tags' hidden header-click order cycle becomes a visible **Order: A→Z | Most used | Manual**.
2. **Every tag list follows it:** the Tags filter (bar above the books), right-click → Tags, book details → Tags.
3. Drag handles appear only in **Manual**, and the manual order changes only in Manual — viewing A→Z never touches a
   saved manual order.

**Build as one "tag lists" release** (Ron + UX, 2026-10-22) with the tasks that change the same lists — one build,
one test round of them instead of four: "Long lists keep their actions in view" (the shared scrolling list; pins
"Manage Tags…"; fixes the Tags filter), "Arrow keys should move through every type-ahead list" (the picker's search
box), and "Tag from Collections, round 2" step 4 (the shared tag-change function: confirmations, "touching a tag by
hand makes it yours").

**Workaround until then:** Tools → Manage Tags → drag "Read" into your top 10.

**How (technical)**
- Right-click picker: readerwrangler.js ~19890–19898 (`tagOrderIdx` sort, `.slice(0, 10)`, multi-book aware via
  `tagsOnAllBooks`). Book window picker: ~14104–14115 (`localeCompare` A→Z, single book). Extract one component taking
  the selected book ids; both call sites become thin. `tagOrderedNames()` is the order source.
- Build it on the overlay system's list popup if it opens as a popup.

##### Right-click: add "Copy ASINs" below Copy Titles / Copy Authors
<!-- id 20261015-1710 -->

_Why it matters:_ Getting the ASINs of several books today means opening each one; the list view's ASIN column can't be selected or copied.

**What you see** (Ron, 2026-10-15 — gathering ASINs to hand to Claude)
1. Add the ASIN column in list view: the values can't be selected, and Ctrl+C copies the books themselves (for
   pasting into folders), not text.
2. The book right-click menu already has **📝 Copy Title(s)** and **👤 Copy Author(s)** for a selection.

**What you'd get**
- **Copy ASIN(s)** right below them: the selected books' ASINs, one per line, in display order (same pattern).

**Decided** (Ron + UX, 2026-10-22)
1. **Flat, right after Copy Author(s), always present** (every book has an ASIN); receipt *"3 ASINs copied"*. Not a
   "Copy ▸" submenu — Copy Title is used often, and a submenu adds a hop to every use.
2. **One shared copy action:** Copy Title(s) and Copy Author(s) are near-duplicates today (build text → clipboard →
   receipt → close menu); a third copy is the moment to make one small helper — "copy these values, with this
   receipt" — so all three are one line each (Authors keeps its de-duplication). Same commit, under 20 lines.
3. **The receipt says "copied" only when it was:** today both items announce "Title copied!" without waiting for the
   clipboard, which a browser can refuse (Law 12). The helper waits; on refusal: *"Couldn't copy — your browser
   blocked the clipboard."* Fixes all three at once.

**How (technical)**
- Next to Copy Title(s) / Copy Author(s) in the book context menu (readerwrangler.js ~19535–19568 on 2026-10-22):
  `navigator.clipboard.writeText(...)` returns a promise — await it (catch the rejection) before the receipt.

##### Wishlist: record the real format when a book is added
<!-- id 20261014-1030bf -->

_Why it matters:_ Today the format is only known after the book's details are filled in.

**Already done** (checked 2026-10-22)
- 6.12.0: adding a single book from its page records the format.
- 7.21.3: **Add Bibliography to Wishlist** takes Kindle books only and records "Kindle Edition" on each
  (author-bibliography-fetcher.js ~462).

**Left — one line** (Ron + UX, 2026-10-22)
- **Add Series to Wishlist** asks Amazon for Kindle editions only, so every book it adds is Kindle — but it never writes
  that onto the book (series-page-fetcher.js, the book built ~464), so the app falls back to its default. Set the
  format to **"Kindle Edition"** (FORMAT-POLICY's spelling, as the bibliography fetcher does).
- A fetcher change shared by all three bookmarklets: dev and prod together.

##### Left pane: put the jump-to-top / bottom buttons by the scrollbar
<!-- id 20261014-1030aa -->

_Why it matters:_ They sit at the bottom left today, not where you'd look for them.

**What you see**
- Both jump buttons (to top / to bottom) sit at the bottom-left of the left pane. You expected top-at-top and bottom-at-bottom, by the scrollbar.

**Decided**
- No per-section jumps (Searches / Book Lists / Folders) — collapsing sections already handles that.
- (Ron + UX, 2026-10-22) **▲ at the top, ▼ at the bottom, both at the right edge by the scrollbar** — where scroll
  controls live everywhere else (Ron's own expectation). Not the single "back to top" option: the pane is long at both
  ends.
- **Floating over the pane's edge**, so they never push the list: ▲ shows when you're not at the top, ▼ when you're not
  at the bottom, neither when the pane doesn't scroll. (Not the menu rule's case — a floating helper shifts nothing,
  and a scroll button with nothing to scroll is clutter.)
- **Home / End do the same jumps** — overlaps "Leftover desktop polish (left-pane keyboard, shadows)" (After launch).
- **Build with the left-pane release** (pins + the filter box + the section overview — "Book Lists and Searches: pin
  and sort them like Folders"), so the pane's chrome is decided once and the filter box and ▲ don't collide.

##### Bulk Edit hints that read like "you can type several values"
<!-- id 20261015-1219 -->

_Why it matters:_ Two hints in the multi-book Edit boxes are easy to misread as "type more than one value here".

**What you see** (Ron, 2026-10-15)
1. Select 2 books with **different** series → right-click → Edit ▸ → **Series…**: the box shows **"Mixed (2 values)"**.
   It means "these books currently have 2 different series", but it reads like "enter 2 values" — Ron took it that way
   while looking for the "2, 4" feature (which is Edit ▸ → "Set numbers…").
2. The same "Mixed (N values)" appears in **Author…**, **Position…** and **Format…** — but only when the selected books
   currently differ. Ron's 2 books had the same position, so Position showed its normal hint instead…
3. …**"e.g., 1, 1.5"** — two example numbers separated by a comma, which looks like "a list is allowed". The box takes
   only **one** number (it applies the same position to every selected book).
4. (For reference: the book details window's Position also takes one number — a book has one position until
   "Series positions: one Position dialog, and one book at several positions" is built.)

**Decided** (Ron + UX, 2026-10-22 — the Position half is overtaken: the next day "Series positions…" (High priority)
made Position take a list (`13, 13.5, 14`, ranges) with a live preview, and removes "Set numbers…" from the menu — so
"e.g., 1, 1.5" becomes accurate, and that task already covers the hint until it ships)
1. **"Mixed" says what it means:** e.g. *"2 different series now — type one to use for all"* — in Author…, Series…,
   Format… (and Position… until the new dialog's preview replaces it).
2. **Show which values, not just how many:** a tooltip on the box — *"Now: Dune · Foundation"* — knowing which ones
   are mixed is usually the point of looking (Law 16).

**How (technical)**
- `Mixed (${uniqueValues.size} values)` in the bulk-edit dialog (readerwrangler.js ~13396), shared by Author / Series /
  Position / Format.

#### Auto-Organize: Shift-click ranges should follow what you see
<!-- id 20261014-1030d -->

_Why it matters:_ Shift-click selects by a hidden internal order that can differ from the order on screen.

**What you see**
- In Auto-Organize, Shift-click a range. In series mode, and in the grouped "Already filed" list, the selected range doesn't match the books between your two clicks on screen.
- **Confirmed still broken in "Already filed"** (Ron, 2026-10-14).

**How to make a test case**
- A normal Inbox has few or no "Already filed" books. To get a useful list: **copy several books from organized folders into the Inbox** (books from more than one series), then open Auto-Organize on the Inbox.
- Click a book in the "Already filed" section, then Shift-click one further down in it: only the books between them on screen should toggle.

**How (technical)**
- 6.16.0 rebuilt the range to follow display order (`getPreviewOrderedBooks`, readerwrangler.js ~9213–9246) — correct for the books being moved, but it pushes the **already-filed** books in their stored order (`preview.alreadyFiled`), not their on-screen grouping. Also check series mode against what's drawn. Deferred from 7.9.0.
- **One shared rule, not an Auto-Organize-only fix** (Ron + UX, 2026-10-22): "a Shift-click range = what's between
  your two clicks on screen" for every list with Shift-click — the main view, Tag from Collections, Removed books.
  When building, check they all use the same on-screen-order helper, so this bug can't live in one list but not another.

#### Folder right-click menu: add Auto-Organize
<!-- id 20261014-1714 -->

_Why it matters:_ Auto-Organize works on a folder, so right-clicking the folder is a natural place to look for it.

**What you see**
- Auto-Organize… is on the right-click menu of a **book** and of the **Inbox**, but not of an ordinary folder.

**What you'd get**
- "✨ Auto-Organize…" on the folder right-click menu, in its "where things go" group (Move to / Top / Bottom / Pin).
  It opens the preview for that folder.
- **Always there, in the same place** (the menu rule, 2026-10-22): in an empty folder it's disabled, with the tooltip
  *"Nothing to organize — this folder has no books."*

**Status:** Ron, 2026-10-14 (noticed while comparing right-click menus with the menu bar); re-confirmed 2026-10-22
("I thought I could right-click a folder and AO. I can't").

**How (technical)**
- Folder menu: readerwrangler.js ~18443 (`folderContextMenu`). The Inbox menu's entry (~18348) and the book menu's
  (~19292) show how to open it scoped to a folder.

#### Fetcher housekeeping

Small code-and-safety fixes; "odds and ends" includes a minimum pause between requests to Amazon.

##### Fetcher: give the library filter one name, in one place
<!-- id 20261014-1030u -->

_Why it matters:_ An unexplained code string is repeated in four places; one named setting is safer to change.

**Background** (checked 2026-10-14)
- An old fetcher fix (`ee6d83c`, June 2026) had two parts. Both were lost when the fetcher was later rewritten.
  1. **A notice for books Amazon has delisted — done.** Since fetcher v4.11.0, the end of a fetch shows a banner:
     "recovered N previously-missing book(s); M unavailable/delisted (see console)".
  2. **Name and explain the library filter — still missing.** This task.

**Removed vs. delisted — two different cases**
- **Removed books** have **left** your Amazon library: a returned loan, a sample you deleted. They're no longer in the
  list Amazon sends. These are what **Tools → Removed books** (7.19.0) handles.
- **Delisted books** were withdrawn from Amazon's **catalog**, but you still own them. They're **still in** your Amazon
  library list, just with no title, author or cover attached. The removed-books check deliberately counts them as
  present, so they never reach the Removed books dialog. A delisted book that can't be filled in at all is what the
  end-of-fetch banner (part 1 above) reports.

**What the filter is**
- When the fetcher asks for your library it applies the same default filter Amazon's own Your Books page applies.
  Today that filter is a long code string pasted into **4 places** in the fetcher (re-counted 2026-10-22) — changing
  it means editing all 4 identically, with nothing saying what it is. What it hides: see TODO notes.

**To do** (Ron + UX, 2026-10-22 — per the notes rule: the code keeps what it needs, explanations stay private)
- Put the whole filter in **one** named constant, used in all 4 places. No change in behavior. Small.
- **Its code comment stays neutral** — e.g. "the default filter Amazon's own Your Books page applies" — the meaning of
  each part lives in Amazon-Reference.md (shipped code is public; the 2026-10-14 draft comment explained Amazon's tags).

**How (technical)**
- The 4 queries: amazon-library-fetcher.js ~1040 (start-up test), ~1449 (main fetch), ~1748 (recovery sweep),
  ~2805 (removed-books check).
- Delisted = "product-null" in the code: the removed-books check adds those ASINs as present (~2869–2878).
- A fetcher change: bump `FETCHER_VERSION`.

##### Fetcher odds and ends (progress figure, frozen timer, request pacing)
<!-- id 20260903-0000a -->

_Why it matters:_ Small fetcher fixes that are each too minor to stand alone.

**The list**
1. Fix the "772%" figure in the details-filled ratio.
2. The elapsed time freezes during the "Checking Relay" (both lines) and "Recovering" phases — it only repaints when the phase or progress changes. (Ron, 2026-09-03, twice.)
3. **Never request faster than today's proven-safe pace** (rewritten 2026-10-22, Ron + UX — the original idea, whose
   details had been lost: a fixed "~400 ms" pause *added after* each answer would stack on Amazon's own response time,
   cost ~40 s on a full pass and protect nothing today). Today it's 0 (`FETCH_DELAY_MS = 0`); if Amazon's servers ever
   got faster, we'd hammer them.
   1. **A minimum gap between request STARTS** — a speed limit, not a delay: before sending, if less than the floor has
      passed since the previous request started, wait the difference; otherwise send at once. Only the start time
      matters, so there's no "just sent" step. If several requests go out at once, each takes the next free slot (last
      start + floor), so they still leave one floor apart.
   2. **Across EVERY request to Amazon**, whatever its kind and whichever fetcher sends it — not per kind.
   3. **The floor = today's measured pace**, so the **net effect today is zero**: record each request's duration in one
      normal full fetch, set the floor just below the typical time, and write where the number came from next to the
      constant.
   4. **Visible if it ever kicks in** (Ron: "an excellent addition"): when the floor actually has to wait, Amazon got
      faster than when we measured — say so in the fetch summary or console ("paced N requests to the safe rate").
   5. **One wrapper — `amazonFetch(…)` — that every request to Amazon goes through,** not a call each site must
      remember (Ron's alternative "about to send" would work too, but can be forgotten). The fetchers are plain
      scripts on Amazon's page, so wrapping the browser's request call is simple. **Lives in one shared file the
      bookmarklet hub loads before any fetcher** — not copied into each. **A commit check refuses a direct request to
      Amazon in the fetcher files that bypasses it.**

**Decided** (Ron + UX, 2026-10-22): items 1–2 as listed (the "772%" ratio can't exceed 100% — fix the formula; the
elapsed time redraws on a one-second tick while a fetch runs). **Build all three with "Faster fetches…"** (High
priority) — same file, same test, and that task already rebuilds the timing table.

**How (technical)**
- Item 3: replaces `FETCH_DELAY_MS` (amazon-library-fetcher.js ~67). (Two items moved out 2026-10-20: the live ownership-upgrade test is now in "Fetch should
  update books it already knows", un-trash on upgrade is "Buying a book that's in the Trash should bring it back".)

#### Relay Setup's connection test checks the wrong relay on dev
<!-- id 20261012-0000a -->

_Why it matters:_ On your local copy or the dev site it tests production, so its answer can be wrong.

**What you see**
- On your local copy or the dev site: File → Relay Setup → the connection test reports on the **production** relay, not the dev relay your copy actually uses. So "connected" / "revoked" there can be wrong for dev.

**To do**
- Use the same relay address every other relay call uses — one place that answers "which relay", not a second fixed address. Small.

**How (technical)**
- readerwrangler.js ~1774 (the `case 'test':` branch) fetches a fixed `https://readerwrangler-relay.readerwrangler.workers.dev/…` (verified 2026-10-14).
- Use the dev-aware `window._RW_RELAY_WORKER_URL` (set near the top of readerwrangler.js for localhost and the dev site). Found 2026-10-12.

#### Finish routing every change through one shared path, with undo
<!-- id 20261014-1030w -->

_Why it matters:_ A few actions — deleting tags or Searches, renaming — still can't be undone.

**Already done**
- 7.11.0: deleting tags, the whole rename family (folders, tags, Searches, Book Lists), and saving / deleting a Search all joined the shared path with undo.

**Left**
- Redo for copying a folder (today: "Cannot redo copy operation", readerwrangler.js ~8276).
- Optional: fold the folder-move part of moving items into the one folder-move operation.

**Done** (6.13.1)
- Folder delete, book move / copy (every menu and drag), folder moves (menu, cut-paste, drag), Book List create / delete, and an undo message for every action.

**Left** (lower priority — less likely to drift)
- Deleting a **tag**, deleting a **Search**.
- Renaming a folder or a Book List — make it undoable.
- Redo for copying a folder (a TODO in the code).
- Optional: fold the folder-move part of moving items into the one folder-move operation.

**How (technical)**
- Shared operations: `deleteFolder`, `moveItems`, `reparentFolder`. The redo TODO is in `COPY_PASTE_FOLDER`. Design: docs/design/OPERATIONS-REFACTOR.md; feeds MODULE-SPLIT.

#### The Delete key should delete the folders you've selected
<!-- id 20261014-1030ay -->

_Why it matters:_ Today it only deletes the folder you're inside.

**What you see**
- Select folders in the right pane's list (e.g. the Folders view) and press Delete: nothing happens to them — only the folder you're *inside* is deleted.

**What you'd get**
- One selected folder → deleted, as from its menu.
- Several → one confirmation, and one undo for the lot.
- **Don't ship single-only** — that's more confusing than neither.

**How (technical)**
- Today it uses `selectedFolderId` instead of `getSelectedFolderIds()`. Single via `deleteFolder`; several via a batch confirm and one compound undo — best once there's a `deleteFolders(folders)` operation. Surfaced during the operations refactor.

#### Working-process safety net: three small follow-ups
<!-- id 20261015-1917 -->

_Why it matters:_ Closes the last gaps left after "Save our working process in git" (done 2026-10-15).

**To do**
1. **Fail loud when a copy isn't set up:** the session-start hook warns "commit checks are not active" if `core.hooksPath` isn't `git-hooks`.
2. Back up the global timestamp wiring (`~/.claude/settings.json`'s hook entry) — e.g. into the Projects repo.
3. Decide whether memory is backed up **automatically** (e.g. a step in the release checklist, or a hook) rather than by hand.

**How (technical)**
- Item 1: the SessionStart hook already runs `gate-reset.py`; have it (or a sibling) check `git config core.hooksPath`
  and print a loud warning when it isn't `git-hooks`.
- Memory backup today: copy `~/.claude/projects/c--Users-Ron-Projects-ReaderWrangler/memory/*.md` into
  `claude-backup/memory/`, commit, push (see that folder's README).

## 🚦 Before public launch

_Formerly: 🚦 Pre-Launch (must-do before public launch)_

### Help, docs and onboarding

_Formerly: Docs & onboarding_

#### Security page: finish the high-contrast light theme
<!-- id 20260909-0000 -->

_Why it matters:_ The last bit of polish on the security page; low priority.

**Done already** (2026-09-09)
- The page's wrong statements were fixed, plus its navigation, and Dark / High-Contrast-Dark themes.

**Left**
- The High-Contrast-Light treatment.
- Optional: restyle it onto the site's shared styles instead of the current overrides.

#### Rewrite the User Guide around Searches, Book Lists and Folders
<!-- id 20260910-0000c -->

_Why it matters:_ The guide predates today's way of organizing.

**What it should cover**
- The four places: All Books / Searches / Book Lists / Folders — what each is for, and "when to use which".
- Folders hold your books; Book Lists are shortcuts that point at them.
- **The Book List ↔ Folder pattern:** structure lives in Folders; to-read queues live in Book Lists.
- "Getting books out of the Inbox → use a folder, not a Book List."

**Sources**
- Examples of taming a backlog: docs/design/WORKFLOW-PATTERNS.md.
- Facts and FAQ: docs/design/SUPPORT-KB.md (mined 2026-09-10 from every session back to May, and kept current at each release).

**Also**
- Do the "Relay → Cloud Sync" rename (next task) in the same pass, so the new names land in the docs in one go.
- The same rewrite covers the GPT support assistant's manual.

**How (technical)**
- "Holds vs. points at" = the custodial vs. supplemental model.

#### User Guide: explain workarounds for fields you can't filter by
<!-- id 20261014-1030bd -->

_Why it matters:_ There's usually another way, e.g. add the column in List view and sort.

**To do**
- In the User Guide and the GPT manual: when someone can't filter by a field, show the workaround (e.g. List view → add that column → sort).

#### Wording pass: explain Book List shortcuts and Linked Copies
<!-- id 20261014-1030bg -->

_Why it matters:_ Those terms confuse people unless they're explained once, clearly.

**To do**
- Use "shortcut" language in Book List messages and menus.
- Explain "Linked Copies" once, in the manual and the GPT manual.

**Spec:** docs/design/TERMINOLOGY.md. (Filed for 6.12.1.)

#### Rename "Relay" to "Cloud Sync" everywhere users see it
<!-- id 20260828-0000a -->

_Why it matters:_ "Relay" is an engineering word; renaming is free before launch and expensive after.

**What you'd get**
- "Cloud Sync Setup", "Import from Cloud", and the same in the status section, tooltips, the fetcher's screens and the recovery steps.
- About 20–40 phrases, plus README / features / tutorials pages.
- Internal names (`RWRelay`, file names, the worker) stay as they are.

**Decided** (2026-08-28)
- "Cloud Relay" was considered and rejected — still jargon, and clunky.

**Watch out**
- When the rename is done, update the CLAUDE.md vocabulary rule to the new names. (No conflict today: that rule says
  how to write with the names currently on screen; this task is the planned pre-launch change. Checked 2026-10-14:
  both trace to the same 2026-08-28 decision in the 7.0.1–7.4.0 post-mortem.)

**Also**
- Fold into the User Guide rewrite (above).

#### Update and record the sizzle reel
<!-- id 20261014-1030bc -->

_Why it matters:_ The promo video shows the old way of organizing.

**To do**
1. Update the script for Book Lists and Searches.
2. Record and produce.

#### Refresh the landing page's before / after screenshot
<!-- id 20261014-1030al -->

_Why it matters:_ The "after" picture predates the redesign.

#### Create a FAQ page
<!-- id 20261014-1030o -->

_Why it matters:_ Common questions answered in one place.

**What you'd get**
- faq.html with sections: Security / Privacy, Data / Backup, Troubleshooting, Library, General.
- Linked from the Help menu, README, and the features and tutorials page footers.

#### Say plainly what ReaderWrangler works with: US Amazon, Kindle, English, Chrome
<!-- id 20261018-1422b -->

_Why it matters:_ Assumptions baked into the product are nowhere stated — a UK reader, or someone expecting paperbacks, finds out only by failing.

**The facts** (each verified in the code or docs, 2026-10-16)
1. **Amazon's US store only.** Every fetcher talks to amazon.com (library: `amazon.com/kindle-reader-api`; collections: `amazon.com/hz/mycd/digital-console/ajax`; series: Amazon's series list); the bookmarklet menu checks `amazon.com/yourbooks`; prices are read as US dollars.
2. **Formats** — the library fetch brings in **everything** in your Amazon library, every format (Kindle purchases, samples, Prime, Kindle Unlimited, loans — and print, audio, even a DVD bought on Amazon); series and author adds take Kindle editions only; **the one-book Add Book to Wishlist takes any format** (deliberately — a paperback can hold a place until a Kindle edition exists). Undoing the Kindle-only preference: After launch task "Formats other than Kindle".
3. **The app is in English.** The books can be in any language.
4. **Browsers:** tested on **Chrome**. **Edge** should work (it's built on the same engine as Chrome). **Firefox** was confirmed working once, long ago, but isn't regularly tested. Safari is untested. _(Today the docs contradict each other: User Guide "Firefox is also fully supported", README / features page "Tested: Chrome, Edge, Firefox", SUPPORT-KB "We only test Chrome" — make them all say the above.)_
5. **Fetching needs a computer** (the bookmarklet runs on Amazon's site in a desktop browser); the phone views and organizes. Verify the exact phone limits before writing them.

**Where it goes** (Ron, 2026-10-16)
1. A short **"What ReaderWrangler works with"** section in the User Guide.
2. One line on the landing page and features page ("For Kindle readers using Amazon.com").
3. One question in SUPPORT-KB.
4. A developer list in docs/reference/ARCHITECTURE.md — every spot a future change (another country, another app language) would touch.

Ron's word on the wording first.

#### Build the support assistant (custom GPT)
<!-- id 20261014-1030i -->

_Why it matters:_ Lets users get answers without waiting for you.

**What you'd get**
- A custom GPT that answers ReaderWrangler questions, linked from the Help menu.

**Spec:** docs/design/SUPPORT-GPT.md.

### Safety and data protection

_Formerly: Safety / data-integrity guards_

#### All the pre-launch data tests pass
<!-- id 20260904-0000 -->

_Why it matters:_ The core data rules must be proven before strangers rely on them.

**Already done**
- Suite 1 (merging and edit protection) exists: test/bookMerge.test.js ("the pre-launch gate for the import merge") and test/bookFields.test.js.

**Left**
- Suites 2 (Import mapping), 3 (permanent-delete markers) and 4 (load guards) from PRELAUNCH-TEST-GATE.md.
- One command that runs them all.

**What it means**
- The test suites in docs/design/PRELAUNCH-TEST-GATE.md exist and pass: merging and edit protection, Import mapping, permanent-delete markers, load guards, relay behavior.
- Specified 2026-09-04 while those bugs were fresh. About 2–4 sessions when the time comes.
- **Blocks launch; blocks nothing else.**

#### Warn before uploading a much smaller library (demo safety)
<!-- id 20261014-1030be -->

_Why it matters:_ A leftover demo setting could replace a real library with a tiny one.

**What you'd get**
- A warning and confirmation before uploading a library dramatically smaller than the one on the relay.
- When the demo book list is active, a banner you can't miss.
- A guarantee that no demo setting can ship.

**How (technical)**
- Old review item 6f; the demo setting is the "demo whitelist".

#### A button to rebuild the library from Amazon
<!-- id 20261014-1030 -->

_Why it matters:_ Today a full reset needs the browser's developer tools.

**What you'd get**
- "Rebuild library from Amazon (full re-fetch)": clears the relay's library so the next fetch starts fresh.
- Goes with the demo-safety warning above.

**How (technical)**
- Old review item 6g.

#### Pin the exact versions of outside code libraries
<!-- id 20261014-1030ai -->

_Why it matters:_ An unannounced update to one of them could break the app overnight.

**What you'd get**
- React and ReactDOM pinned to one exact 18.x version (today: "any 18" — readerwrangler.html ~128, checked 2026-10-14).
- Check every HTML page for the same.
- Tailwind's lasting fix is the "build the app ahead of time" task (After launch).

**How (technical)**
- Old review item 6h.

#### Stop cleanly when Amazon asks for a human check mid-fetch
<!-- id 20261014-1030au -->

_Why it matters:_ Today it shows confusing errors instead of saying what to do.

**What you'd get**
- When Amazon interrupts a fetch with a "are you human?" check, the fetcher stops and says: *"Amazon is asking for a human check. Open any Amazon page, complete it, then re-run — everything fetched so far is safe."*
- That last clause is true since 7.0: a stopped run is simply never committed.

**Status**
- The start of a fetch is already guarded; this covers a check appearing **partway through**. Never seen yet — cheap insurance before launch. (From an outside review, item 7.)

**How (technical)**
- In the fetchers' retry path, recognize check-shaped answers: HTML where JSON was expected, a validate-captcha redirect, a robot-check 503.

#### Protect against editing in two tabs at once
<!-- id 20260830-0000 -->

_Why it matters:_ Two open tabs can overwrite each other's work — a real data-loss risk.

**What happens**
- Two ReaderWrangler tabs share one browser storage, so an out-of-date tab's edit overwrites the other tab's work.

**What you'd get**
- A second tab opens **read-only**, with an offer to reload and take over editing; it can show live or frozen.

**Status**
- **Medium priority — "Tier 0": the real data-loss risk.** Fully designed and ratified 2026-08-30; not built. (Its old "after 7.7.0" note is stale.)

**How (technical)**
- Web Locks for the read-only second tab, reload-then-promote, live / freeze viewer. Design: docs/design/MULTI-INSTANCE.md §4.

#### Let a new user's first big fetch resume after an interruption
<!-- id 20260821-0000 -->

_Why it matters:_ A first 3,000-book fetch that dies near the end starts over from scratch.

**What happens**
- A new user's first fetch fills in details for ~3,000 books with no resume point. If it dies at book 2,800, it starts over.

**What you'd get**
- The fetch sends its progress in stages, so a re-run skips what's already done. 7.0's upload design makes this natural.

**Status**
- Hits each user exactly once — low priority; nice to have before launch. (From the 2026-08-21 outside review, item 1.)

**How (technical)**
- Send enrichment progress as mailbox letters in stages, so a resumed run's skip-hint already knows what's done.

#### Relay Setup: disconnect, or reset credentials
<!-- id 20261014-1030am -->

_Why it matters:_ A clean way to stop syncing, or to start over with new credentials.

**Already done**
- 6.9.0: Relay Setup's "Danger zone → Revoke credentials & wipe relay" — clears the keys and reopens the step that makes new ones.

**Left**
- A gentle **Disconnect** that just stops syncing on this device, without revoking or wiping anything on the relay.

### Costs

_Formerly: Launch economics_

#### Move to Cloudflare's $5/month plan around launch
<!-- id 20260828-0000 -->

_Why it matters:_ The free plan supports only a handful of users.

**What we know** (RELAY-ECONOMICS.md, 2026-08-28)
- After 7.5.0's savings, the flat $5 plan covers about 250 users like you; the free plan about 6–10 — and it's shared between production and dev.
- So this is now just the act of upgrading at the right moment, at or shortly before launch.

---

## 🗄️ After launch

_Formerly: 🗄️ Backlog (post-launch)_

### Dialog look

_Formerly: Dialog look (LOW priority — Ron 2026-10-08)_

#### Rebuild the old-style message boxes as standard dialogs
<!-- id 20261014-1030ak -->

_Why it matters:_ Low priority — only worth doing if we want every dialog to share one look.

**What's there**
- The message boxes — OK/Cancel, type-a-name, progress, choice, "Owned Book" — are hand-built page elements, used in about 45 places.
- Since 7.18.0 they behave like every other dialog (Esc, ✕, key blocking), but keep their own hand-built look.

**Option A** (deferred)
- One shared piece that shows each request as a standard dialog; the 45 call sites stay unchanged.
- Removes about 300 lines of hand-built code and gives every dialog one look. Costs a visual check of all 45.

**Related**
- "Drag any dialog out of the way" (Up next) must also work for these boxes — doing this first would make that simpler.

**How (technical)**
- `showInfoDialog`, `showConfirmDialog`, `showInputDialog`, `showProgressDialog`, `showChoiceDialog`, `showDeleteWarningDialog`, rendered as `<Dialog>`s by a React "dialog service"; callers keep `await showConfirmDialog(…)`.

### Speed

_Formerly: Responsiveness_

#### Clicking between books lags slightly while a filter is on
<!-- id 20261006-0000 -->

_Why it matters:_ A small but noticeable delay on every click while searching or filtering.

**What you see** (Ron, 2026-10-06)
- With any filter or search active — even inside a small folder — click from one book to another. There's a short delay before the old book un-highlights and the new one highlights.
- With no filter, it's instant.
- Chrome's console sometimes shows "[Violation] 'click' handler took ~270ms" (not reproducible on demand after a refresh).
- Mild — "live with it on All Books" is acceptable.

**Likely cause** (a guess, not verified)
- The filtered list itself is already remembered, so it isn't re-filtered on a click.
- The extra cost is probably the **active-filter bar**: it redraws on every click and recounts "💾 N results · Save ▾", the "✓ Search: …" check and the chips.

**To do**
1. Measure one click with Chrome's performance tool, filter on vs. off.
2. Remember whatever that bar recalculates.

**Note**
- Your first theory — "filter the current folder, not the whole library" — can't explain a lag on **selecting** (filtering doesn't re-run then). Still worth checking for the first filter's cost.

**How (technical)**
- The cached list is `explorerDisplayItems` (a useMemo); profile with DevTools Performance.

### Relay and sync

_Formerly: Relay / data robustness_

#### Edit Kindle collections from ReaderWrangler
<!-- id 20261014-1030r -->

_Why it matters:_ Change your Kindle collections without going to Amazon.

**Spec:** docs/design/COLLECTION-EDITING.md.

#### Cheaper small syncs (send only what changed)
<!-- id 20261014-1030k -->

_Why it matters:_ Optional: smaller uploads for small changes.

**Spec:** docs/design/RELAY-DELTA.md.

#### Bookmarklet: warn before fetching if your Channel ID no longer works
<!-- id 20261018-1422 -->

_Why it matters:_ A fetch can take minutes; if the relay won't accept your Channel ID (revoked or deleted), you should hear that before the fetch, not after.

**The idea** (left over from "Ask before restoring when relay credentials don't match", shipped 7.14.3; Ron filed it on its own 2026-10-16)
- Before fetching, the bookmarklet quickly asks the relay whether your channel is still good. If not, it says so plainly and points you to **Relay Setup**, instead of fetching first.

**Check first:** what the bookmarklet does today when the channel is revoked — at which point it finds out, and what it tells you. Not yet checked.

**How (technical)**
- docs/design/RELAY-CRED-MISMATCH.md "Future": ping `/status/{channelId}` before fetching; warn on 403/404.

#### Warn when another browser has newer changes
<!-- id 20260922-0000d -->

_Why it matters:_ Two browsers on one account can drift apart without anyone noticing.

**What happens**
- Copy a backup into a second browser and both now use one relay. Each edits its own copy and nothing tells you.

**What you'd get**
- When a browser becomes active again, it compares itself with the relay. If it's behind, it offers: **Catch up & edit here** / **Just view** / **Leave as-is**.

**Decided**
- **Low priority — "Tier 1".** Builds on the two-tab task above (one idea of "who's the editor": in-browser between tabs, across browsers via the relay).
- **Live two-way sync is rejected** — it would need push infrastructure and a merge engine for organization.

**How (technical)**
- Compare the relay's serialized-state stamp; adopt the relay's organization; an optional soft relay lease.
- The real work: give the desktop a way to **adopt** device-state (today `getDeviceState` on desktop is only a connection test), plus a per-channel lease record.
- Design: docs/design/MULTI-INSTANCE.md §6 (2026-09-22).

### Features

_Formerly: Features_

#### "Read in Kindle": open a book in the Kindle app or Cloud Reader
<!-- id 20260919-0000 -->

_Why it matters:_ Jump straight from ReaderWrangler to reading the book — for people who read in the Kindle app or Cloud Reader.

**Placed here** (Ron, 2026-10-16): moved from High priority — it does nothing for Paperwhite reading, but it's the natural button for app / Cloud Reader readers.

**What you'd get**
- A **Read** action on books you **own** (not wishlist or sample entries — those keep "Open in Amazon"):
  - **Phone:** opens the book in the Android Kindle app.
  - **Desktop:** opens Kindle Cloud Reader (read.amazon.com) at the book. Optionally also "Open in Kindle app" for Kindle-for-PC users (the browser asks "Open Kindle?").
- **Not** a built-in reader — you still read on the Paperwhite.

**Limits**
- **Tested and failed (2026-09-19):** opening a book in the Android app does **not** move it to the top of the Paperwhite's list. So it only helps people who read in the app or Cloud Reader; Paperwhite-only readers gain nothing.
- The **phone** link is **unofficial** — Amazon could break it. Keep a fallback to the book's Amazon page, and test per app version. The **computer** link is Amazon's own: its author-page data carries a "Read Now" link of the form `https://read.amazon.com?asin=…` (seen 2026-10-16).
- Needs the **Kindle edition's** ASIN; a print-only owned book won't open. Some titles can't be read in Cloud Reader at all, and there's no way to tell in advance.
- Countries: not this task's problem — ReaderWrangler as a whole is US-store only today (see "Say plainly what ReaderWrangler works with").

**How (technical)**
- Android (preferred, with fallback): `intent://book?action=open&asin=<ASIN>#Intent;scheme=kindle;package=com.amazon.kindle;S.browser_fallback_url=https%3A%2F%2Fwww.amazon.com%2Fdp%2F<ASIN>;end`
- Android bare form: `kindle://book?action=open&asin=<ASIN>` — must come from a tap (Chrome blocks it otherwise); behavior has shifted between app versions (may land on the details page instead of opening the book).
- Desktop: `https://read.amazon.com/?asin=<ASIN>` (opens if signed in; resumes at your last position).
- Fallback: `https://www.amazon.com/dp/<ASIN>`.
- Background research: the `reference_read_in_kindle` memory (Ron's 2026-09-19 research).

#### Formats other than Kindle: undo my Kindle-only preference
<!-- id 20261018-1422a -->

_Why it matters:_ "Kindle only" is Ron's own preference baked into the series and author adds (Ron, 2026-10-16: "We took MY preference and baked it in") — other readers may want paperbacks, hardcovers or audiobooks; and the library fetch has no way to keep out formats you don't track.

**Today**
- The **series** and **author** adds take Kindle editions only; the **one-book Add Book to Wishlist** takes whatever format the page shows — keep that exception either way (Ron adds a paperback as a placeholder when there's no Kindle edition yet).
- **The library fetch already brings in EVERY format** (confirmed 2026-10-16 from Ron's library, Format column): ~80 non-Kindle items — 47 Board Book, ~12 Paperback, ~12 Mass Market Paperback, 4 Map, 2 Audio CD, 1 each CD-ROM, DVD, Product Bundle, Spiral-bound, and one "Shoes" (a board book Amazon mislabels). Mostly gifts Ron's wife bought. _(Corrected twice today: I first claimed Amazon's library was Kindle-only — it isn't; its default filter hides other things, not formats — see "Fetcher: give the library filter one name, in one place" and TODO notes.)_
- So the library has the **opposite** problem: things you don't track (gifts, a DVD) come in with no way to keep them out.

**Shape** (Ron + UX, 2026-10-16) — **after launch, depending on demand**
1. **One "Formats I track" setting** — checkboxes (☑ Kindle ☐ Paperback ☐ Hardcover ☐ Audiobook …), saved with your sync settings so every fetcher obeys it. It works **both ways**: series / author adds bring in the formats you track (not just Kindle), and the library fetch leaves out the ones you don't (your gift board books, the DVD).
2. The author and series panels show it pre-checked; you can change it for that one run.
3. **A Format filter in ReaderWrangler's right pane** — books already carry a format (the editable Format field), so it has something to work from. Today the only way to see them is the Format column + sorting.
4. To decide when built: the default for new users, and what happens to already-fetched books in formats you then untick (hide them? leave them?).

**Watch out**
- **Author add — settled 2026-10-16: print works exactly like Kindle**, and "All languages" can be one request (a small
  win for the shipped fetcher). Details: AMAZON-AUTHOR-PAGES.md.
- Format words seen: `kindle`, `paperback` (author filter); Amazon's library filter lists Kindle Edition, Paperback, Hardcover, Board Book, Audible Audiobook.
- The series add asks Amazon for `binding=kindle_edition` (series-page-fetcher.js ~319).

#### Finish keyboard accessibility
<!-- id 20261014-1030v -->

_Why it matters:_ Everything should be usable without a mouse.

**Left**
- Keeping focus inside an open dialog.
- A visible focus outline for keyboard users.
- Keyboard access to the right-click menus.

**How (technical)**
- Focus trapping, `:focus-visible`, context-menu keys.

#### Show reading progress
<!-- id 20261014-1030aq -->

_Why it matters:_ See how far along you are — in the book window, and as a list column.

#### Book recommendations
<!-- id 20261014-1030h -->

_Why it matters:_ Suggestions based on your own library.

**Spec:** docs/design/BOOK-RECOMMENDATIONS.md.

#### Show who a book is shared with (Family Library)
<!-- id 20261014-1030ar -->

_Why it matters:_ See sharing at a glance in the book window.

#### Two-pane split view
<!-- id 20261014-1030bb -->

_Why it matters:_ Work with two folders side by side.

**Spec:** docs/design/archive/DUAL-PANE-SPLIT.md (filed as "V2").

#### Support stores besides Amazon
<!-- id 20261014-1030aw -->

_Why it matters:_ For readers who buy elsewhere too.

**Spec:** docs/reference/MULTI-STORE-ARCHITECTURE.md.

#### Several people on one installation
<!-- id 20261014-1030ao -->

_Why it matters:_ Low priority — Save / Restore Backup already works around it.

**Spec:** docs/design/archive/MULTI-USER-DESIGN.md.

#### Reading statistics
<!-- id 20261014-1030aj -->

_Why it matters:_ A dashboard of your reading.

#### Connect with Goodreads / StoryGraph
<!-- id 20261014-1030n -->

_Why it matters:_ Share data with the reading sites people already use.

#### Animated drag-and-drop
<!-- id 20261014-1030c -->

_Why it matters:_ Books slide aside live to show where a drop will land.

#### Import book details from a pasted list or spreadsheet
<!-- id 20261014-1030y -->

_Why it matters:_ A way to bring in information from outside Amazon.

**What you'd get**
- Paste a list or load a CSV; ReaderWrangler matches the rows to your books.

**Spec:** docs/design/Metadata-Import.md.

#### Capture book ideas from your phone (Share → ReaderWrangler)
<!-- id 20261015-1714 -->

_Why it matters:_ Recommendations you meet on your phone (a Claude.ai answer, a review) can't reach ReaderWrangler until you're back at the desktop — today you email yourself.

**What you see** (Ron, 2026-10-15)
- Reading in bed, Claude.ai suggested books like *Cronus* (P. Djèlí Clark); nothing on the phone could add them to the
  wishlist or a Book List. A bookmarklet on phone Chrome technically works but is far too clumsy for a dozen links.

**What you'd get**
1. **Share → ReaderWrangler** in Android's share sheet (the phone version installed to the home screen registers as a
   share target): one tap from Claude.ai, the Amazon app, an article.
2. What you share — a link, an ASIN, or plain text — travels through the **relay** like a wishlist add, and the desktop
   shows it in a short **"To look up"** list on the next Import: links/ASINs become wishlist entries; plain text you
   resolve with a click (search Amazon, add, put in a Book List).
3. A whole Claude answer can be shared at once and worked through on the desktop. Picking titles out of free text
   automatically stays human — too unreliable.

**Caveats**
- Android / Chrome only (iPhone doesn't support web-app share targets). Plain-text items carry no book details until
  resolved. Medium-sized: a phone capture screen, a new relay letter kind, a desktop list.

**Status:** after launch (Ron, 2026-10-15: "there comes a time in every project where you have to shoot the engineer
and release it").

**How (technical)**
- Web Share Target (`share_target` in the phone app's manifest); a single-letter mailbox run (as the wishlist fetcher
  sends) carrying `{url|asin|text}`; the desktop's Import routes those letters to the "To look up" list.

### Prices

_Formerly: 💰 Price checking (Price sweep scoping + staleness display, agreed 2026-08-21, from external sync review item 2)_

#### Wishlist prices through Amazon's official affiliate catalog API, once eligible
<!-- id 20261021-1349 -->

_Why it matters:_ An official API can't be broken by a page redesign — a sturdier source for the prices behind price
goals.

**What it is** (Ron + Claude, 2026-10-21): the **Creators API**, the successor to Amazon's Product Advertising API
(PA-API 5, retired). A **catalog** API — what Amazon sells (titles, prices, images by ASIN), never what *you* own — so
it can never replace the library fetch. RW never used PA-API (checked 2026-10-21), so nothing is broken today.

**What it would take**
1. **Eligibility:** an Amazon Associates account — RW already has one (its "Open in Amazon" / Share links carry the
   affiliate tag) — with **10 qualifying sales in the past 30 days** (2026-10-21: 6 ordered, 0 shipped, $0 earned —
   none qualifying yet).
2. **A server for the credentials** — already there: the relay worker can hold them, look prices up 10 per request,
   and keep them only as long as Amazon allows.
3. **Only the generic price moves.** Account-specific signals — "you bought this on ‹date›", Prime / Kindle Unlimited
   status — stay in the signed-in fetch.

Details: see TODO notes.

#### Notice when a Kindle edition appears for a print-only book
<!-- id 20261014-1030ae -->

_Why it matters:_ So you can switch to the Kindle edition without losing its folders, lists and tags.

**What you'd get**
- A print book you're waiting on can be marked "watch for Kindle".
- An occasional slow check notices when a Kindle edition appears, and **offers** (never forces) to swap to it, carrying over its folders, Book Lists, tags and price goal — a cousin of the wishlist → owned upgrade.

**Low priority, because most cases are already covered**
- Amazon's author-follow emails announce new formats (e.g. Heinlein).
- For Kindle books Amazon withdrew, the price **reappearing** in the normal price check is itself the signal (The Destroyer's 18 withdrawn titles).
- The only uncovered gap: a print placeholder → a new Kindle edition.

**Check first**
- Does the batch lookup report other editions of a print ASIN, or does this need a product-page visit per book?

**How (technical)**
- `formatWatch: 'kindle'` on print placeholders; likely shares a mechanism with the slow refresh below. (Outside review item 6.)

#### Now and then, refresh ratings for books you might buy
<!-- id 20261014-1030af -->

_Why it matters:_ Ratings are frozen at the first fetch — fine for owned books, a little stale for buying decisions.

**What you'd get**
- Optional: about monthly (or every Nth fetch), refresh ratings and review counts for books you could still buy.
- Safe to interrupt: results are sent as an upload run, so a closed tab tears nothing — it carries on next time.

**Not this**
- The outside review's per-book adaptive refresh timing — a fine solution to a scale problem we don't have.

**How (technical)**
- Reuse the scoped list from the price-sweep work and batch calls. (Outside review item 3.)

### Technical clean-up

_Formerly: Tech / performance_

#### Faster loading: build the app ahead of time
<!-- id 20261014-1030s -->

_Why it matters:_ Today the app compiles itself in the browser on every load.

**What you'd get**
- The app's code is prepared once, ahead of time, instead of in the browser each load. Faster loading — and the lasting fix for pinning outside code versions.

**Spec:** docs/design/PRECOMPILE.md.

**How (technical)**
- Precompile Babel + Tailwind to static files; removes in-browser Babel and Tailwind.

#### Split the main code file into modules
<!-- id 20261014-1030at -->

_Why it matters:_ One very large file is harder to work in safely.

**Status**
- Re-assess first — uiHelpers, storage and integrity are already split out.

**Spec:** docs/design/MODULE-SPLIT.md.

#### Show a notice when book descriptions are missing
<!-- id 20261014-1030ap -->

_Why it matters:_ So a missing description reads as known, not broken.

**Already done**
- Desktop: the book details window shows "⚠️ Description not available" with an explanation (since v3.5).

**Left**
- The **phone** just hides the description section — show the same notice there (Ron, 2026-10-15: "Phone should match").

**How (technical)**
- "Phase 3 UI error handling" — missing-description banners.

#### Clean up developer console messages
<!-- id 20261014-1030m -->

_Why it matters:_ About 70 of them: keep, hide behind a switch, or remove each.

#### Check nothing was lost between versions 4 and 5
<!-- id 20261014-1030l -->

_Why it matters:_ A feature-by-feature comparison of the two versions.

#### Leftover desktop polish (left-pane keyboard, shadows)
<!-- id 20261014-1030ab -->

_Why it matters:_ Small finishing touches.

**Left**
- Keyboard navigation in the left pane.
- Consistent shadow direction.

---

## 👀 Watching

Not work to do — conditions to watch for. Each says what to check if it happens again. (Ron, 2026-10-15)

### Undo history sometimes empties by itself
<!-- id 20260807-0000 -->

_Why it matters:_ Losing undo mid-session is alarming; the cause is still unknown.

**What happened**
- Twice (2026-08-07 and 08), the undo history emptied with no undo or redo by you.

**What we know** (2026-09-01)
- No code path clears it — it lives only in memory and only drops its oldest steps at the limit. So **some invisible page reload** is the only explanation.
- Suspect: the TinySuspender extension discarding and restoring the tab. Your settings argue against it for those two times (60-minute idle timeout; you were actively switching tabs). A forgotten manual reload is the other possibility.

**Next time it happens**
- Check the console history and Data Status's "last checked" — a discarded tab clears both.

**Do now regardless**
- Whitelist localhost and readerwrangler.com in TinySuspender. A suspended ReaderWrangler tab can also tear an upload when you leave it.

### Find out why some books end up in no folder
<!-- id 20260903-0000b -->

_Why it matters:_ Rare reports of books in no folder at all; watch whether it still happens.

**What we know**
- One real user event on 6.11.5, and two more on 2026-09-03: books in the browser's book store that no folder refers to.
- 7.7.0 removed the leading suspect: a cold start reading an out-of-date folder list that didn't yet know the newest books.

**Next step**
- **Watch** for the event after releases before spending a session on it.

**How (technical)**
- The event is `integrity-homeless`; the suspect was a stale `FOLDERS_KEY`.

---

## 🧊 Someday

_Formerly: 🧊 Icebox (no timeline)_

### Test on Safari (desktop and iPhone)
<!-- id 20261014-1030ax -->

_Why it matters:_ Some Safari differences could break storage, the phone install, or layout.

**Risks to check**
- The browser's book storage (IndexedDB), installing as a phone app (PWA), and styling.
