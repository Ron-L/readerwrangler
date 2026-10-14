<!-- TOC -->

- [TODO](#todo)
  - [🔝 Up next](#up-next)
    - [Cancelling a new folder that a filter hides should discard it](#cancelling-a-new-folder-that-a-filter-hides-should-discard-it)
    - [Start the local server automatically, without exposing private files](#start-the-local-server-automatically-without-exposing-private-files)
    - [Book details window: changes happen only when you click Save](#book-details-window-changes-happen-only-when-you-click-save)
    - [Drag any dialog out of the way](#drag-any-dialog-out-of-the-way)
    - [Relay Setup: smoother sections and clearer Esc / Help behavior](#relay-setup-smoother-sections-and-clearer-esc--help-behavior)
    - [Ctrl+A in a dialog must never select the page behind it](#ctrla-in-a-dialog-must-never-select-the-page-behind-it)
    - [Arrow keys should move through the Series suggestion lists](#arrow-keys-should-move-through-the-series-suggestion-lists)
    - [The "Save results" menu runs off the screen with many Book Lists](#the-save-results-menu-runs-off-the-screen-with-many-book-lists)
    - [Removing a recent search should offer Undo](#removing-a-recent-search-should-offer-undo)
    - ["Add Bibliography to Wishlist" is greyed out on an author's All Books tab](#add-bibliography-to-wishlist-is-greyed-out-on-an-authors-all-books-tab)
    - [Dark theme: fix the unreadable bar and the light strips](#dark-theme-fix-the-unreadable-bar-and-the-light-strips)
    - [Book Lists and Searches: pin and sort them like Folders](#book-lists-and-searches-pin-and-sort-them-like-folders)
    - [Clearing a price goal doesn't fully clear it everywhere](#clearing-a-price-goal-doesnt-fully-clear-it-everywhere)
    - [Find a book by its ASIN in the search box](#find-a-book-by-its-asin-in-the-search-box)
    - [A type-to-filter box for the left pane](#a-type-to-filter-box-for-the-left-pane)
    - [Ctrl+X from a Book List or Search quietly copies instead of cutting](#ctrlx-from-a-book-list-or-search-quietly-copies-instead-of-cutting)
    - [Faster back-to-back fetches: refresh everything at most once a day](#faster-back-to-back-fetches-refresh-everything-at-most-once-a-day)
    - ["Read in Kindle": open a book in the Kindle app or Cloud Reader](#read-in-kindle-open-a-book-in-the-kindle-app-or-cloud-reader)
    - [Make sure an Import never wipes fields only ReaderWrangler sets](#make-sure-an-import-never-wipes-fields-only-readerwrangler-sets)
    - [Turn more of our working rules into automatic checks (my tooling)](#turn-more-of-our-working-rules-into-automatic-checks-my-tooling)
    - [Tag from Collections: clear up the checkbox vs. preview confusion](#tag-from-collections-clear-up-the-checkbox-vs-preview-confusion)
    - [Restore dialog calls yesterday's backup "today"](#restore-dialog-calls-yesterdays-backup-today)
    - [Phone: show which test build is running](#phone-show-which-test-build-is-running)
  - [⏸️ On hold: honest ownership changes (buying, samples, loans)](#on-hold-honest-ownership-changes-buying-samples-loans)
    - [Auto-Organize: let a misfiled book go back to the Inbox](#auto-organize-let-a-misfiled-book-go-back-to-the-inbox)
    - [Auto-Organize: Shift-click ranges should follow what you see](#auto-organize-shift-click-ranges-should-follow-what-you-see)
    - [Fetch summary should report books you bought](#fetch-summary-should-report-books-you-bought)
    - [Import summary: count every ownership change, by kind](#import-summary-count-every-ownership-change-by-kind)
    - [Keep price goals when a book is bought, and say so](#keep-price-goals-when-a-book-is-bought-and-say-so)
    - [Keep the Import summary in the message history](#keep-the-import-summary-in-the-message-history)
    - [Buying a book that's in the Trash should bring it back](#buying-a-book-thats-in-the-trash-should-bring-it-back)
    - [Fetch should update books it already knows, not skip them](#fetch-should-update-books-it-already-knows-not-skip-them)
    - [Let library loans and Audible Plus books upgrade to owned](#let-library-loans-and-audible-plus-books-upgrade-to-owned)
    - [Write the wishlist / ownership rules down in one design doc](#write-the-wishlist--ownership-rules-down-in-one-design-doc)
    - [Relay Import: only books in no folder should go to the Inbox](#relay-import-only-books-in-no-folder-should-go-to-the-inbox)
  - [🚦 Before public launch](#before-public-launch)
    - [Help, docs and onboarding](#help-docs-and-onboarding)
      - [Security page: finish the high-contrast light theme](#security-page-finish-the-high-contrast-light-theme)
      - [Rewrite the User Guide around Searches, Book Lists and Folders](#rewrite-the-user-guide-around-searches-book-lists-and-folders)
      - [Rename "Relay" to "Cloud Sync" everywhere users see it](#rename-relay-to-cloud-sync-everywhere-users-see-it)
      - [Update and record the sizzle reel](#update-and-record-the-sizzle-reel)
      - [Add "Watch Tutorials" to the Help menu](#add-watch-tutorials-to-the-help-menu)
      - [Refresh the landing page's before / after screenshot](#refresh-the-landing-pages-before--after-screenshot)
      - [Create a FAQ page](#create-a-faq-page)
      - [Build the support assistant (custom GPT)](#build-the-support-assistant-custom-gpt)
      - [Document how to recover from disasters](#document-how-to-recover-from-disasters)
    - [Safety and data protection](#safety-and-data-protection)
      - [All the pre-launch data tests pass](#all-the-pre-launch-data-tests-pass)
      - [Warn before uploading a much smaller library (demo safety)](#warn-before-uploading-a-much-smaller-library-demo-safety)
      - [A button to rebuild the library from Amazon](#a-button-to-rebuild-the-library-from-amazon)
      - [Pin the exact versions of outside code libraries](#pin-the-exact-versions-of-outside-code-libraries)
      - [Find out why some books end up in no folder](#find-out-why-some-books-end-up-in-no-folder)
      - [Stop cleanly when Amazon asks for a human check mid-fetch](#stop-cleanly-when-amazon-asks-for-a-human-check-mid-fetch)
    - [Costs](#costs)
      - [Move to Cloudflare's $5/month plan around launch](#move-to-cloudflares-5month-plan-around-launch)
  - [🔧 Relay follow-ups](#relay-follow-ups)
    - [Relay Setup's connection test checks the wrong relay on dev](#relay-setups-connection-test-checks-the-wrong-relay-on-dev)
    - [Relay storage: stop leftovers piling up, and report usage correctly (in progress)](#relay-storage-stop-leftovers-piling-up-and-report-usage-correctly-in-progress)
    - [Let a new user's first big fetch resume after an interruption](#let-a-new-users-first-big-fetch-resume-after-an-interruption)
    - [Keep the settings the app and relay share in step](#keep-the-settings-the-app-and-relay-share-in-step)
  - [💰 Price checking](#price-checking)
    - [Notice when a Kindle edition appears for a print-only book](#notice-when-a-kindle-edition-appears-for-a-print-only-book)
    - [Now and then, refresh ratings for books you might buy](#now-and-then-refresh-ratings-for-books-you-might-buy)
  - [🔜 Soon](#soon)
    - [Undo, deleting and multiple windows](#undo-deleting-and-multiple-windows)
      - [Finish routing every change through one shared path, with undo](#finish-routing-every-change-through-one-shared-path-with-undo)
      - [The Delete key should delete the folders you've selected](#the-delete-key-should-delete-the-folders-youve-selected)
      - [Keep reading the old save format (a standing decision, not a task)](#keep-reading-the-old-save-format-a-standing-decision-not-a-task)
      - [Protect against editing in two tabs at once](#protect-against-editing-in-two-tabs-at-once)
      - [Warn when another browser has newer changes](#warn-when-another-browser-has-newer-changes)
    - [Book List menus and undo history](#book-list-menus-and-undo-history)
      - [Book List menu: remove Move / Copy, and block dragging onto folders](#book-list-menu-remove-move--copy-and-block-dragging-onto-folders)
      - [Undo history sometimes empties by itself](#undo-history-sometimes-empties-by-itself)
    - [Ideas from the August 2026 library clean-up](#ideas-from-the-august-2026-library-clean-up)
      - [Auto-Organize preview: show which Book Lists a book is in](#auto-organize-preview-show-which-book-lists-a-book-is-in)
      - [See an author's other books without leaving your spot](#see-an-authors-other-books-without-leaving-your-spot)
      - [Open one book's details without losing a multi-selection](#open-one-books-details-without-losing-a-multi-selection)
      - [User Guide: explain workarounds for fields you can't filter by](#user-guide-explain-workarounds-for-fields-you-cant-filter-by)
      - [Drag between Folders and Book Lists](#drag-between-folders-and-book-lists)
      - [Search everywhere without leaving the current folder](#search-everywhere-without-leaving-the-current-folder)
    - [Other follow-ups](#other-follow-ups)
      - [Wording pass: explain Book List shortcuts and Linked Copies](#wording-pass-explain-book-list-shortcuts-and-linked-copies)
      - [Stray double spaces in author names create duplicate authors](#stray-double-spaces-in-author-names-create-duplicate-authors)
      - [Fetcher: re-apply two lost improvements](#fetcher-re-apply-two-lost-improvements)
      - [Hide returned loans and borrows](#hide-returned-loans-and-borrows)
      - [A management view for Book Lists](#a-management-view-for-book-lists)
      - [Delete a book from All Books (removes it everywhere)](#delete-a-book-from-all-books-removes-it-everywhere)
      - [Drag a box to select covers](#drag-a-box-to-select-covers)
      - [Show only hidden books](#show-only-hidden-books)
      - [Fetch: report exactly how your library compares with Amazon](#fetch-report-exactly-how-your-library-compares-with-amazon)
      - [Fetcher odds and ends (progress figure, frozen timer, request pacing)](#fetcher-odds-and-ends-progress-figure-frozen-timer-request-pacing)
      - [Tooltips in the book details window](#tooltips-in-the-book-details-window)
      - [Wishlist: record the real format when a book is added](#wishlist-record-the-real-format-when-a-book-is-added)
      - [Import book details from a pasted list or spreadsheet](#import-book-details-from-a-pasted-list-or-spreadsheet)
      - [Set different series numbers on several books at once ("2, 4")](#set-different-series-numbers-on-several-books-at-once-2-4)
      - [One book in several series positions (omnibus, anthology, MegaPack)](#one-book-in-several-series-positions-omnibus-anthology-megapack)
      - [Folder menu: Move to Top / Move to Bottom](#folder-menu-move-to-top--move-to-bottom)
      - [Dragging a subfolder to the top level drops it in the wrong place](#dragging-a-subfolder-to-the-top-level-drops-it-in-the-wrong-place)
      - [Book Lists: arrange by series number](#book-lists-arrange-by-series-number)
      - [Left pane: put the jump-to-top / bottom buttons by the scrollbar](#left-pane-put-the-jump-to-top--bottom-buttons-by-the-scrollbar)
  - [🗄️ After launch](#after-launch)
    - [Dialog look](#dialog-look)
      - [Rebuild the old-style message boxes as standard dialogs](#rebuild-the-old-style-message-boxes-as-standard-dialogs)
    - [Speed](#speed)
      - [Clicking between books lags slightly while a filter is on](#clicking-between-books-lags-slightly-while-a-filter-is-on)
    - [Relay and data safety](#relay-and-data-safety)
      - [Safer relay saves (the relay redesign)](#safer-relay-saves-the-relay-redesign)
      - [Deleted books that stay deleted](#deleted-books-that-stay-deleted)
      - [Edit Kindle collections from ReaderWrangler](#edit-kindle-collections-from-readerwrangler)
      - [Cheaper small syncs (send only what changed)](#cheaper-small-syncs-send-only-what-changed)
      - [Relay Setup: disconnect, or reset credentials](#relay-setup-disconnect-or-reset-credentials)
      - [Ask before restoring when relay credentials don't match](#ask-before-restoring-when-relay-credentials-dont-match)
    - [Features](#features)
      - [Finish keyboard accessibility](#finish-keyboard-accessibility)
      - [Show reading progress](#show-reading-progress)
      - [Book recommendations](#book-recommendations)
      - [Show who a book is shared with (Family Library)](#show-who-a-book-is-shared-with-family-library)
      - [Auto-Organize: file co-written books under each author](#auto-organize-file-co-written-books-under-each-author)
      - [Two-pane split view](#two-pane-split-view)
      - [Support stores besides Amazon](#support-stores-besides-amazon)
      - [Several people on one installation](#several-people-on-one-installation)
      - [Smart collections (rule-based)](#smart-collections-rule-based)
      - [More ways to filter by Kindle collections](#more-ways-to-filter-by-kindle-collections)
      - [Reading statistics](#reading-statistics)
      - [More export options (printable list)](#more-export-options-printable-list)
      - [Connect with Goodreads / StoryGraph](#connect-with-goodreads--storygraph)
      - [Animated drag-and-drop](#animated-drag-and-drop)
    - [Technical clean-up](#technical-clean-up)
      - [Faster loading: build the app ahead of time](#faster-loading-build-the-app-ahead-of-time)
      - [Split the main code file into modules](#split-the-main-code-file-into-modules)
      - [Show a notice when book descriptions are missing](#show-a-notice-when-book-descriptions-are-missing)
      - [Tooltip review: Tag from Collections wizard](#tooltip-review-tag-from-collections-wizard)
      - [Clean up developer console messages](#clean-up-developer-console-messages)
      - [Check nothing was lost between versions 4 and 5](#check-nothing-was-lost-between-versions-4-and-5)
      - [Leftover desktop polish (left-pane keyboard, shadows)](#leftover-desktop-polish-left-pane-keyboard-shadows)
  - [🧊 Someday](#someday)
    - [Test on Safari (desktop and iPhone)](#test-on-safari-desktop-and-iphone)

<!-- /TOC -->



# TODO

> **This file is FUTURE work only.** Each task is a header in short, plain words, so the table of contents above
> reads as the whole list. The first line under a header says why it matters; the details follow. When a task is
> done, put ✅ at the front of its header; **delete every ✅ section at each release** (after the CHANGELOG sweep).
> The past lives in **CHANGELOG.md**, design rationale in **docs/design/**, retrospectives in **post-mortems/**.
>
> When you promote/descope a task, **move** its section — never leave a stub. When you agree a bug/task mid-session,
> add a section (header + one line) before moving on. The table of contents is rebuilt by the VS Code extension
> "Auto Markdown TOC" when the file is saved in VS Code; a pre-commit check refuses a stale one
> (`scripts/check-toc.js`). Headers: about 80 characters, 132 at most, no internal names.

---

## 🔝 Up next

_Formerly: 🔝 TOP OF STACK (Ron 2026-09-09/10; stack state updated 2026-09-16)_

_(Done 2026-09-16: 7.13.1 mobile dev-relay-worker fix + 7.13.2 relay worker+storage visibility —
both shipped to prod; dev confirmed, prod verify in progress.)_

**THE CURRENT STACK (pop in this order):**
(The numbered stack items are the sections right below, in order; then the rest of this section.)

Then the queued items below (left-pane parity, filter box, Ctrl+X-from-list fix, ownership
batch — item 6 first).

### Cancelling a new folder that a filter hides should discard it

_Why it matters:_ A new folder can land hidden by your filters, and there is no clean way to back out — Cancel should just remove it.

**New-folder "discard on cancel" (Option A) — its own small release (~7.14.3).** Discovered during
7.14.2 testing (unrelated). `newFolderHiddenAlert` should get 4 buttons: Clear All Filters / Show
All Folders / Leave As Is (keep hidden) / **Cancel** (discard). Cancel + Esc + ✕ + backdrop →
delete the just-created folder via the existing undoable CREATE_FOLDER machinery + toast **"New
folder discarded"**. Add `folderId` to the alert payload at the 3 trigger sites (js 14972 / 15560 /
18451). LATER polish (Option C, separate): warn BEFORE creating (predict `hasActiveFilters`) so
nothing is created on cancel, and fix the inline-rename that currently happens in the hidden sidebar
row. Ron chose A now, C deferred.

### Start the local server automatically, without exposing private files

_Why it matters:_ After every reboot you hunt for the server command, and today's server also shows private files to other devices at home.

**Auto-start the local RW server (dev convenience, addressed in RW).** Pain point: after every
reboot Ron hunts the `python -m http.server` line in developers.md. **Fix = Option 3 (rec): a
Startup-folder shortcut to a versioned `.bat` in the repo** — `python -m http.server 8000 --directory
C:\Users\Ron\Projects\ReaderWrangler`, started minimized. Keeps the **`localhost:8000` origin**
(critical — the Apache-alias option would change the origin and orphan ALL of RW's localStorage:
library, organization, relay credentials; plus breaks root-relative paths + phone testing). Do NOT
add `--bind 127.0.0.1` (phone tests over the LAN). Option 2 (scheduled task at logon) = headless
alternative if a console window isn't wanted.
**Updates (Ron 2026-10-06):** (a) the server must run in a **VISIBLE window** (not minimized/headless) — so
Option 2 is out and the shortcut opens normal. (b) **Security finding:** plain `python -m http.server` serves the
WHOLE project folder — including `.private/` (API key notes, the private repo's own `.git`) and `.git/` — to any
device on the home network that can reach port 8000. Since `--bind 127.0.0.1` would break phone testing, the
fix is a tiny versioned **`serve.py`** in the repo (stdlib `http.server` + a handler that refuses `/.private/…` and
`/.git/…` with 404), launched by the `.bat`. Same port and origin, phone still works, secrets never served.
Then update CONTRIBUTING.md's server lines (and drop its Python 2 `SimpleHTTPServer` line — EOL since 2020).
(c) Use **`py`**, not `python`, in the .bat and docs: since Python 3.14 the new Python Install Manager provides
`py` (Ron's habit). On Ron's PC 2026-10-06: `py` → 3.14.7, but `python` → 3.13 (older install first on PATH).
(d) Deferred by Ron 2026-10-06 ("save the fixes for later") — do after the overlay branch.

### Book details window: changes happen only when you click Save

_Why it matters:_ Today some fields save instantly and others wait for Save; one rule makes the window predictable, with one undo per Save.

**Book dialog goes fully transactional (7.14.0 — NEXT UP, ratified 2026-09-10; renumbered thrice: 7.11.0=audit, 7.12.0=price snapshot, 7.13.0=copy chips)**:
in the dialog, Edit/Save is the ONLY way anything changes (one undo per Save); everywhere else changes are
instant commands (one undo each). Rating / price goal / tags leave view mode (read-only displays) and join
`editBookFields` as staged fields — Cancel discards, Save folds them into the one atomic EDIT_BOOK step;
new-tag creation happens at Save. Finishes the OWNERSHIP-MODEL §4 edit-in-place pattern (instant controls
were the anomaly). Commands stay live in both modes (Share, Amazon link, Status History, ◀▶) — build starts
with an enumeration pass classifying every dialog control field-vs-command (explicit, not vibes).
**Quick access replaces dialog instant-set**: line-view cell popups for Price Goal + My Rating (click cell →
preset goals/custom, or star row); decide during build whether cover right-click gains a My Rating submenu.
UNDO-MODEL.md §"fully transactional" has the rationale + Ron's context-keying principle.

Steps (from the stack):

**Transactional book-dialog enumeration pass** — the field-vs-command classification table for
every book-dialog control, published for Ron's red pen BEFORE any transactional surgery (the
copy-chips work that opened its branch shipped as 7.13.0; transactional gets a fresh branch).
_Version number assigned when the work is taken up — not pre-planned._
**Transactional book-dialog build** against the approved table (number assigned at pickup).

### Drag any dialog out of the way

_Why it matters:_ Dialogs sometimes cover what you need to see; dragging them aside is a habit from Quicken.

**Draggable dialogs — bake drag into the `<Dialog>` primitive (Ron 2026-09-28; SEPARATE feature AFTER the overlay migration ships)**.
Ron often needs to move a dialog to see what's under it (Quicken habit). Add drag to `<Dialog>` so ALL dialogs become
draggable at once (retires the old per-dialog `dialogDrag`; **folderPropertiesDialog is being converted WITHOUT drag
during the migration — this feature restores it, universally**). Decisions (Ron 2026-09-28): (1) grab from **anywhere
on the panel except interactive controls** (input/textarea/button/a/select), with a `cursor:move` affordance;
(2) **bounds** default = keep a grabbable strip always on-screen (never lose a dialog), but support a
**`dragBounds:'free'` option to drag fully off-window** (Ron finds off-window useful in Quicken — Search Results /
Reconciliation; keep the capability even if most default to constrained) — prove free/off-window works with one test
dialog; (3) **position** = centered on each open, then draggable (not remember-last). New user functionality → its OWN
branch/release, keeping the overlay branch a pure refactor (Ron's Option A).

### Relay Setup: smoother sections and clearer Esc / Help behavior

_Why it matters:_ Its sections jump open so abruptly they look like new windows, and Esc behaves differently in a way you can't see.

**relaySetup UX polish (Ron 2026-09-28, surfaced during the overlay migration; NOT part of the migration)**.
Relay Setup's internal accordion sections shove content up/down so hard the expansion reads as "a new
dialog appeared." Items: (1) **slow/animate the expansions** (a height transition) so the eye can track
Credentials/Enter-Manually and Bookmarklet/Pairing expanding rather than jumping; (2) **"Enter Credentials
Manually" isn't perceivable as a level** — users can't tell it from just expanding a section, so its special
"Esc backs out one level first" behavior (the smart onClose reason==='esc' branch) is invisible/confusing —
reconsider whether manual-creds should be a distinct level at all, or just have Esc close relaySetup like the
backdrop; (3) **stacked Help clarity** — Help covers relaySetup exactly so it reads as a replacement, not a
stack; the draggable-dialogs feature (drag Help aside) is the natural fix, or a slight offset. All relaySetup-
internal redesign, separate focused pass.

### Ctrl+A in a dialog must never select the page behind it

_Why it matters:_ A few controls inside dialogs can still let Ctrl+A highlight the whole page behind the dialog.

❓ May already be done — check before working on it.

**Ctrl+A leak sweep — non-input controls that swallow select-all in modals (Ron 2026-09-29; two-pivot sweep)**.
A non-input focusable control inside a dialog that calls `stopPropagation()` on Ctrl+A bypasses the dialog-aware
select-all guard, so the browser's NATIVE select-all fires and highlights the whole page BEHIND the modal (the
faded backdrop doesn't stop text selection). Found + fixed in the bulkEdit Series field (▼ button + dropdown rows,
7.18.0-alpha.21), and the document handler always preventDefaults (never leaks) then scope-selects the top dialog's
text whenever any dialog is open (7.18.0-alpha.22) — but only when the key REACHES it, so any OTHER non-input control
that stopPropagations Ctrl+A can still leak. Sweep: TWO pivots — (1) grep `onKeyDown=...stopPropagation` (~19 inline
hits + multi-line) and classify by element: input/textarea = OK (native field-select), button/div/li/a = SUSPECT;
(2) walk each dialog's focusable non-text controls. Diff the two, post the file:line table, then fix (let Ctrl+A
bubble on non-input controls). STRUCTURAL alternative worth weighing: a CAPTURE-phase Ctrl+A guard at the document
(scope-select the top dialog's text when a dialog is up and focus isn't in a text field) — one chokepoint inner
stopPropagation can't defeat — folding in autoOrgPreview's book-select once it's converted to declare its own semantics.

### Arrow keys should move through the Series suggestion lists

_Why it matters:_ You can't pick a series from the list with the keyboard — Down scrolls the window instead.

**Arrow keys do nothing in the Series suggestion lists (Ron 2026-09-29; re-confirmed 2026-10-06, minor a11y)**.
WHAT YOU SEE: in BOTH Series fields — the book details window's edit mode (✏️) and Bulk Edit → Series… — open the
list (type a letter or click ▼) and press Down arrow: nothing moves through the list. In the book details window the
Down arrow instead SCROLLS THE WHOLE WINDOW (that window scrolls; Bulk Edit doesn't, so there it does nothing). Enter
takes the typed text, not a highlighted row.
DO (standard combobox pattern): Down/Up move a highlight through the list while the cursor STAYS IN THE TEXT FIELD
(so you can keep typing); Enter picks the highlighted series; Esc closes the list (already works); a list that's
open consumes Down/Up so the window no longer scrolls. Build it ONCE in the shared `<Popover kind="list">` (both
lists became that in 7.18.0-alpha.54) — not per field. Deferred by Ron 2026-10-06 (after the overlay branch's
remaining groups).
THE MODEL ALREADY EXISTS (found 2026-10-07): the search box's recent-searches list — the `SearchInput` component's
Down/Up/Enter/Esc handling (highlight index, keeps typing in the field) — is exactly this pattern, working today.
EXTRACT that into the shared list popup and use the ONE implementation for all three type-ahead lists (both Series
fields AND the search box). Stable reference for "as it was": commit 46a0cf6 (`git show 46a0cf6:readerwrangler.js`,
search for `const SearchInput`).

### The "Save results" menu runs off the screen with many Book Lists

_Why it matters:_ With 20+ Book Lists the lower ones are cut off and can't be reached.

**"💾 N results · Save ▾" menu runs off the screen when you have many Book Lists (Ron 2026-10-06)**.
WHAT YOU SEE: with a search or filter active, click the "💾 N results · Save ▾" button in the bar above the books.
The menu lists every Book List; with ~20+ lists it's taller than the window, so the lower lists are cut off at the
bottom with no way to scroll to them (and a long flat list is slow to scan).
DO: give it a max height + scrolling, and — past ~10 lists — the same filter box the book right-click menu's
"Move to" submenu already has (reuse that, don't build a second one). Check the other menus that list user items
(Book Lists, folders) for the same problem while there. Not overlay-branch work.
PREFERRED MECHANISM (designed 2026-10-06): an opt-in `<Popover>` option for BUTTON dropdowns — when the menu can't
fit below its button, open on whichever side (above/below) has MORE room, cap its height to that space, and scroll
(the standard "size to fit" approach of modern menu libraries). Today it pins to the top of the window and hangs off
the bottom. Must NOT apply to the right-click menus with fly-out submenus (Move to / Copy to) — a scrolling menu would
clip its own fly-outs (CursorPopup's "never add overflow" rule). The filter box stays a useful extra. Deferred by Ron
2026-10-06 (wait in TODO).

### Removing a recent search should offer Undo

_Why it matters:_ One click deletes a recent search with no message and no way back.

**Removing a recent search (the × on a row) can't be undone and leaves no trace (Ron 2026-10-07)**.
WHAT YOU SEE: click into the search box so "Recent searches" appears, click the × on a row — it's gone instantly,
with no toast, no Undo, and nothing in the 🕐 message history. Deleting a SAVED Search (left pane → SEARCHES →
right-click → Delete Search) does confirm, toast and undo.
DECIDED (Ron + UX pass): give recents removal the same treatment MINUS the confirmation — remove immediately, show a
toast with Undo, record it in the 🕐 history (a recent is automatic history; "Are you sure?" per row would nag —
standard "Removed · Undo" pattern). Route it through the shared undo/toast operation path, not a one-off. Related:
memory notes "tag/search delete" was left off the shared undo system in the 6.13.1 operations refactor — check what
else is still outside it while there.

### "Add Bibliography to Wishlist" is greyed out on an author's All Books tab

_Why it matters:_ The bookmarklet doesn't recognize that kind of author page, so the button can't be used there.

**"⭐ Add Bibliography to Wishlist" button is greyed out on an author's "All Books" tab (Ron 2026-10-07)**.
WHAT YOU SEE: on Amazon, click an author's name (e.g. John Marrs), open the author page's **All Books** tab, filter
English + Kindle, then click the ReaderWrangler bookmarklet — the "⭐ Add Bibliography to Wishlist" button is
disabled. Example URL: `https://www.amazon.com/stores/author/B00F1CRG9U/allbooks?…`.
LIKELY CAUSE (verified in code, not yet live-tested): the nav hub's author-page check
(bookmarklet-nav-hub.js ~68: `/\/stores\/[^/]+\/author\/[A-Z0-9]{10}/i`) requires an author-NAME segment —
`/stores/John-Marrs/author/B00F1CRG9U` — but the All Books tab uses `/stores/author/B00F1CRG9U/allbooks` (no name
segment, extra `/allbooks`), so the page isn't recognized. DO: accept both URL shapes (name segment optional), then
TEST the bibliography fetcher itself on the All Books page — its page structure may differ from the author home
page, and the English/Kindle filters Ron applies may change what's on screen. Fetcher/nav-hub change → bump their
versions; DEV bookmarklet first (navigator change), then PROD.

### Dark theme: fix the unreadable bar and the light strips

_Why it matters:_ Some parts of the screen stay light in Dark mode, and one bar's text is unreadable.

**Dark theme: unreadable "New library data available" bar + light strips around the filter area (Ron 2026-10-07)**.
WHAT YOU SEE (View → Theme → Dark): (1) the bar under the menu bar reading "📡 New library data available (uploaded …)"
keeps its LIGHT blue/purple background while its text turns near-white — unreadable; (2) a light strip shows under
the "🔍 Active: Search …" bar (and anywhere there's a gap between sections).
WHY (verified): dark mode works by REMAPPING specific Tailwind color classes in readerwrangler.css
(`[data-theme="dark"] .bg-white {…}` etc.); anything colored outside that list stays light. (1) the relay bar's
background is a hard-coded inline gradient `linear-gradient(135deg, #dbeafe, #ede9fe)` (readerwrangler.js ~9360) with
`color: var(--text-primary)` text; (2) the app's outermost container uses `bg-gradient-to-br from-blue-50 to-blue-100`
(~8992) — the GRADIENT classes aren't remapped (only plain bg-blue-50/100 are), and the Active bar's `mb-4` gap shows it.
ALSO FOUND (same class, not yet seen by Ron): hard-coded light boxes in the Auto-Organize Preview (`#f1f3f5`, `#fafafa`,
`#e5e7eb` ~12009/12018/12046), and likely more.
DO: a COMB, not two spot fixes — grep every hard-coded light color in JSX (inline `background: '#…'` / light
`linear-gradient`, `from-*/to-*` gradient classes, unmapped Tailwind colors) and move each onto the theme (CSS
variables like `var(--bg-surface)`, or add the class to the dark remap). Check each in Dark after. MECHANISM idea:
add a "no hard-coded light backgrounds in JSX" check to scripts/check-names.js's sibling tooling so new ones get
flagged at commit time.

### Book Lists and Searches: pin and sort them like Folders

_Why it matters:_ A long Book Lists column is hard to search; Folders already have pins and a Name / Manual sort.

**Left-pane ordering parity for Book Lists + Searches** (Ron 2026-09-10, queued behind the transactional dialog):
pins (top tier) + header sort control (Manual ↔ Name), the FOLDERS 7.6.0 vocabulary and controls verbatim —
no second ordering system three inches from the first. List reorder already undoable (7.10.1-alpha.6); pin
toggle joins undo. Motivation: hunting a series list in a long Book Lists column (Ctrl+F works but costs a
thought-process switch). Expected usage: **Name to FIND, back to Manual for priority** — Ron's top tier =
the `New To Read - *` work lists (mobile-filter surrogates, Prime clearing first), series To-Reads below.

### Clearing a price goal doesn't fully clear it everywhere

_Why it matters:_ An old second price-goal field can keep a book counted as "has a goal" after you clear it.

**Old price-goal field `targetPrice` still lingers (found 2026-10-12)**. WHAT: a few code paths treat a book as
"has a goal" if EITHER `priceTrigger` (today's goal) OR the older `targetPrice` is set — the import's "kept their
price goals" count (storage.js ~174), the fetcher's goal check (amazon-library-fetcher.js ~2286), and the spreadsheet
(`priceTrigger ?? targetPrice`). But clearing a goal in the app only clears `priceTrigger`. So a book that still
carries an old `targetPrice` keeps "having a goal" in those places after you clear it. DO: first check whether any
real book still has `targetPrice` set (console count); if so, migrate it into `priceTrigger` once, then retire the
field (bookFields row + the three readers) — one goal field, not two. Small.

### Find a book by its ASIN in the search box

_Why it matters:_ Handy for checking whether one specific book is in your library.

**Search by ASIN in the search box (Ron 2026-10-12)**. WHAT: typing a book's ASIN (e.g. `B08P52K2PZ`) into the
search box at the top of the right pane ("Title, author or series...") finds that book — today it only matches title,
author and series. Useful for checking a specific book exists (came up testing the removed-books feature).
WHERE (three copies of the same match rule — make it ONE): the live search filter (`readerwrangler.js` ~10044), the
saved-Search matcher `bookMatchesFilters` (~2196), and the phone's search (`mobile.js` ~2289, which also matches notes
+ tags). DO: one shared `bookMatchesText(book, term)` (uiHelpers) with ASIN added (exact or prefix, case-insensitive),
called by all three — then update the box's placeholder/tooltip to mention ASIN. Small.

### A type-to-filter box for the left pane

_Why it matters:_ With many folders, Book Lists and Searches, typing a few letters is the fastest way to find one.

**Left-pane type-to-filter box** (Ron 2026-09-10, companion/escalation to the above): one box narrowing
**Folders + Book Lists + Searches** by name — the strongest pure "find" at scale. Design questions for the
build: placement (whole-pane vs per-section), keyboard focus/shortcut, clear-on-navigate, interaction with
the accordion collapse.

### Ctrl+X from a Book List or Search quietly copies instead of cutting

_Why it matters:_ You think you moved the book, but it never leaves the list.

**Ctrl+X from a Book List / Search view silently degrades to copy** (found during alpha.7, filed not fixed):
cut records the view id as source, but paste-cut removes from FOLDERS only — the book never leaves the list.
Fix: refuse with the explanatory toast (like All Books) or make paste-cut honor Book List sources.

### Faster back-to-back fetches: refresh everything at most once a day

_Why it matters:_ Grabbing one new book still re-prices and re-checks the whole library every time.

**Fetcher: throttle the full-library passes on back-to-back fetches** (Ron 2026-09-19, felt while
patching $0.99 series holes — buy → download → import, repeatedly). Grabbing 1 new book still re-prices
EVERY wishlist book, re-enriches, and runs the full orphan scan — wasteful back-to-back. Design:
- **Always** run the incremental fetch + **enrich the NEW books** (series/cover/description — needed to
  file them; never skip this).
- **Throttle only the FULL-LIBRARY passes** — re-price-all-wishlist, re-enrich-existing, orphan-scan —
  to at most **once per ~24h**. Principled interval: matches the existing price-staleness threshold
  (prices dim at ~24h, KB §16), so throttling doesn't degrade price-watching.
- **State:** `lastFullPassAt` (relay, or localStorage on the Amazon origin).
- **Override at the point of effect** (Law 16): when the fetcher skips the full passes, its completion
  dialog says so and offers one click — *"Skipped the full refresh (prices, re-enrichment, orphan scan)
  — already done today. Do it now?"* Gives "full twice today" without a 2nd bookmarklet. **Do NOT** use a
  Shift/Alt-click modifier (PRINCIPLES/Browser: Windows drag/click events lie about modifiers —
  unreliable + undiscoverable).
- **ANALYSIS FIRST (before building):** does the fetcher already separate "enrich NEW" from
  "re-price/re-enrich ALL" in its phases (titles → enrichment → tags → prices)? If entangled, splitting
  them is the real work. Read the fetcher (bookmarklet) code first. Fetcher-side change (+ maybe app/relay
  coordination for the state + the override dialog) — separate codebase from the app.
- **Cross-ref:** Ownership-honesty batch **item #1** ("Fetcher completion dialog reports ownership
  upgrades") touches the SAME fetcher completion dialog — build them together.
- **KB update on ship (Ron 2026-09-21):** once full re-pricing is throttled to ~once/24h, §16's answers
  *"How fresh are prices? As fresh as your last fetch"* and *"every wishlist-priced book is re-priced each
  run"* become inaccurate — update them (prices refresh at most ~once/day by default; the override forces a
  fresh pass).

### "Read in Kindle": open a book in the Kindle app or Cloud Reader

_Why it matters:_ Jump straight from ReaderWrangler to reading the book.

**"Read in Kindle" — jump from RW to the book in a Kindle reader** (Ron 2026-09-20; RW has become
his primary library organizer and he keeps wanting to open a book straight from RW mobile). **NOT a
built-in reader** (he still reads on the Paperwhite; too much scope). Instead, a per-book **Read**
action for OWNED books:
- **Mobile RW → Android Kindle app** via a deep link by ASIN (Kindle app URI scheme / Android App Link).
- **Desktop RW → Kindle Cloud Reader** (`read.amazon.com`, opened to the ASIN).
- **Owned-only:** show it only for owned books — you can't read a wishlist/sample entry (those keep
  "Open in Amazon" / the product page).
- **Known dead-end (tested 2026-09-19, FAILED):** opening a book in the Android Kindle app does NOT bump
  it to the top of the Uncollected collection on the Paperwhite (the hoped-for cross-device surfacing).
  So the value is limited to people who read in the **Android app or Cloud Reader** — Paperwhite-only
  users gain nothing. Priority accordingly.
- **Deep-link specifics (Ron's research 2026-09-19; all UNOFFICIAL/undocumented — Amazon could break
  them, so best-effort with a fallback, and TEST per platform/version):**
  - **Android → intent URL with fallback** (preferred over the bare scheme):
    `intent://book?action=open&asin=<ASIN>#Intent;scheme=kindle;package=com.amazon.kindle;S.browser_fallback_url=https%3A%2F%2Fwww.amazon.com%2Fdp%2F<ASIN>;end`
    — falls back to the Amazon product page if the app isn't installed. Bare form:
    `kindle://book?action=open&asin=<ASIN>`. **Must be a user tap** (Chrome blocks otherwise); owned
    books only; behavior has shifted across app versions (may land on the detail page instead of
    opening to read).
  - **Desktop → Kindle Cloud Reader:** `https://read.amazon.com/?asin=<ASIN>` (opens the book if
    signed in; resumes at last position via Whispersync). Optional secondary "Open in Kindle app"
    using the same `kindle://…` scheme for **Kindle-for-PC** users (browser shows an "Open Kindle?"
    prompt).
- **Caveats:** use the **Kindle-edition ASIN** (not print) — fine for owned Kindle books (RW's ASINs
  come from the Kindle library), but a print-only owned book won't open. Not every title is
  Cloud-Reader-readable (some restricted → "download the app" prompt, undetectable in advance) → keep
  the `amazon.com/dp/<ASIN>` fallback. **Marketplace matters** — non-US accounts need
  `read.amazon.co.uk` / `.co.jp` / etc.; RW may need the user's marketplace or default to `.com` + rely
  on fallback. (Backstory link: `reference_read_in_kindle` memory.)

### Make sure an Import never wipes fields only ReaderWrangler sets

_Why it matters:_ Two fields were being wiped on every Import; check no other field has the same gap, and decide whether backups keep them.

**bookMerge ownership audit — the deeper invariant the chokepoint surfaced (2026-09-22)**.
DONE so far (7.16.0-alpha.3): `collectionTagSeen` + `collectionTags` were silently `'amazon'`
(incoming-wins) and WIPED on every import — the fetcher never sets them AND the device-state push
(readerwrangler ~5560-5594) doesn't carry them, so incoming ALWAYS lacks them. Reclassified to `'user'`
(local-wins) + a gate test locking it. **The general invariant to sweep for:** any book field the APP
writes but the device-state push payload does NOT include must be `'user'` (local-wins), or import
silently wipes it. Walk the payload vs the registry and check every field lands right.
**SECOND HALF — still OPEN (separate, wire-schema):** those two fields are also absent from the push
payload, so **Save/Restore and cross-device still lose them** (local-wins only saves them from the IMPORT
merge, not from a restore that replaces wholesale). If preserving wizard state across backup/restore
matters, ADD both to the payload builder (~5560) + the import parser (~6186/6270). Decide if in scope.

### Turn more of our working rules into automatic checks (my tooling)

_Why it matters:_ Rules that depend on memory keep failing; automatic checks don't. Affects only how I work, not the app.

**Principle-to-hook audit — can each distilled law be MECHANIZED, not just remembered? (Ron 2026-09-22)**
Motivated by "assuming bit us again" (orphanStatus durability, a DESIGN-time assumption the edit-time gate
never saw). Walk `docs/PRINCIPLES.md` law by law and classify each: **(a) reducible to a deterministic gate**
(a script/test a hook runs + BLOCKS on red — real teeth: e.g. run the test suite before commit; grep TODO/
REMOVE before release; version-bump-when-.js-changed; cache-buster-matches; the merge-completeness test)
vs **(b) judgment-only** (NEVER ASSUME, model-legal-states, UX-first — a hook can only REMIND, and reminders
decay to rubber-stamps). For (b), the leverage is giving reminders *teeth via a required artifact*: e.g. a
design-doc **`## Assumptions (and how each was verified)`** section a PreToolUse hook can check EXISTS on a
`docs/design/*` write — the content is judgment but the visibility is enforced, and it fires at DESIGN time
(where this assumption slipped), not just edit time. Guard against reminder-bloat (the gate is already 11
points; more dilutes). Meta-principle recursion: prefer converting a law to a check over adding another tap.
**From the 7.18.0 PM (2026-10-08):** ~~(1) gate watched only readerwrangler.js/mobile.js~~ DONE same day — widened
to a rule (any root `.js` + relay worker). (2) STILL OPEN: a gate bounce inside a parallel batch silently drops
that one edit (alpha.62 half-fix) — no obvious mechanism yet (a hook can't know which edits were intended); design.
**(3) My code safety-check can be skipped by accident (7.19.0 PM, 2026-10-12).** The checklist that pops up before
I change app code only fires when I use my normal editing tool; edits I make with a find-and-replace command skip it.
Fix: have the check fire for those edits too. Affects only my tooling, not the app. Small.
(Technical: the gate hooks only Edit/Write; add a PreToolUse hook on Bash that spots `sed -i` / redirects onto a
root `.js` or the relay worker and runs the same once-per-turn checklist — reuse `is_app_source()`.)

### Tag from Collections: clear up the checkbox vs. preview confusion

_Why it matters:_ Each row has two click targets that do different things, with nothing to tell them apart.

**Tag-from-Collections wizard: right-pane vs checkbox confusion (UNSETTLED — 2026-09-22)**. The
left-pane row has TWO hit-targets doing different things with no cue: the **checkbox** = "include in Apply";
clicking the **name text** = "show this collection's books in the right pane" (`tfcSelectedCollection`).
Unchecking a box doesn't change the right pane — only a text-click does; and "checked" vs "being viewed"
share the same row highlight, so the two models are invisible (fooled Ron). **UNSETTLED — the goal of the
right pane isn't even clear (preview? the apply-set?); do NOT prescribe a fix yet.** When taken up: first
pin down what the right pane is FOR, then make the two states distinct (or unify: right pane follows the
checkbox / last action; header "Viewing: X"). Design pass before any code.
**Also (Ron 2026-09-22): UX-Expert opinion wanted on whether AND where to ALSO surface the
Tag-from-Collections wizard from the Manage Tags menu / sub-menu** (in addition to its current launch
point) — a discoverability/placement question; evaluate, don't just wire it in.

### Restore dialog calls yesterday's backup "today"

_Why it matters:_ A wrong date label can lead you to restore the wrong backup.

**Restore dialog mislabels a backup's relative date (2026-09-22)**: a backup from **9/21 6:54 PM** was
labeled **"— today"** while the real date was 9/22 (Ron: NOT a timezone artifact — it was yesterday
everywhere). The "today"/relative-date logic is wrong — likely a "within ~24h = today" heuristic instead of
a calendar-day compare, or a UTC/local mismatch. VERIFY first (grep the "— today" string / the label code),
then compare by calendar day in local time + add yesterday / N-days-ago cases.

### Phone: show which test build is running

_Why it matters:_ During testing you can't tell from the phone which build it's on.

**Mobile: show a live BUILD marker, not just the released `APP_VERSION` (Ron 2026-09-22)**. Mobile's
About shows `App v{APP_VERSION}` (the last *released* version, which by design doesn't bump during alphas)
+ `Mobile v{MOBILE_VERSION}`. During alpha testing the desktop surfaces the live `ORGANIZER_VERSION`
(e.g. 7.16.0-alpha.6) but mobile can't (it's a different file). Surface a live build marker on mobile so a
tester can tell which build the phone is actually running (MOBILE_VERSION already moves per alpha, but the
"App v" line reads stale-looking). Small UI/version-plumbing polish.

## ⏸️ On hold: honest ownership changes (buying, samples, loans)

_Formerly: ⏸️ Ownership-honesty batch (ratified 2026-09-04, HELD — awaiting Ron's go; likely 7.8.0)_

Shipped so far: item 0 + ownership-dialog redesign + undo fence + undo-toast naming → **7.8.0** (2026-09-08);
item 10 → **7.7.2** (2026-09-07; prod proof outstanding — first prod import on ≥7.7.2 should log
`🧹 Reclaimed 7 absorbed bulk run(s)`, ~124MB).
**Unified Auto-Organize SHIPPED as 7.9.0** (2026-09-09; 9 soak-tested alphas in 2 days — the soak-as-test-rig
model at full speed). Two §9/§2 pieces deliberately deferred (explicitly, per the scope rule):
Then batch 1-9 (item 11 SHIPPED in 7.11.0). (Item 12 — mooted by the unification.)

Save as Spreadsheet (CSV): **SHIPPED as 7.10.0** (2026-09-09 — requested 09-08, shipped next day).
Reply to the user still owed (Ron's channel).

### Auto-Organize: let a misfiled book go back to the Inbox

_Why it matters:_ There's no way to send a book that Auto-Organize filed wrongly back to the Inbox.

**Inbox as a File-under target** (demote a mis-filed book back out) — different commit machinery

### Auto-Organize: Shift-click ranges should follow what you see

_Why it matters:_ Shift-click selects by a hidden internal order that can differ from the order on screen.

**Shift-click ranges follow VISUAL order** — still internal-array order; diverges in series mode + grouped Already-filed

### Fetch summary should report books you bought

_Why it matters:_ After buying 4 wishlist books the summary says "0 new" — the upgrades only show in the developer console.

**1. Fetcher completion dialog reports ownership upgrades** (today: console-only ⬆️; dialog says "0 new" after you buy 4 books) — **cross-ref:** the "Fetcher: throttle the full-library passes" item in the TOP-OF-STACK queued list also lives in this completion dialog; build them together.

### Import summary: count every ownership change, by kind

_Why it matters:_ Sample → owned upgrades are missed, and wishlist → sample could be mislabeled as owned.

**2. Import summary counts ALL ownership promotions, labeled by destination** — "3 wishlist → owned", "1 wishlist → sample" — keyed on ownershipType transitions (today: onWishlist-flip only ⇒ misses sample→owned AND would mislabel wishlist→sample as owned). Also: name the titles in the console line (the 🎉-line-has-no-title gap that blocked diagnosis 2026-09-04).

### Keep price goals when a book is bought, and say so

_Why it matters:_ Goals must never vanish silently; optionally offer a one-click "clear these goals".

**3. Goals on promotion: KEEP (old rule stands — never silently destroy)** + receipt line; optional one-click "Clear goals on these N" in the import summary (Ron to pick during build). Rationale: promoted books already require a manual All-Books visit to file into reading lists, so clearing rides a trip he makes anyway (Ron 2026-09-04).

### Keep the Import summary in the message history

_Why it matters:_ The summary disappears on refresh, leaving no record of what changed.

**4. Import summary echoed into 🕐 toast history** (receipts gap: dialog evidence vanishes on refresh)

### Buying a book that's in the Trash should bring it back

_Why it matters:_ A book you just bought shouldn't stay hidden in the Trash.

**5. Un-trash on ownership upgrade** (buying a trashed book should resurrect it — Ron: "YES! Include it")

### Fetch should update books it already knows, not skip them

_Why it matters:_ A sample or loan of a wishlisted book is thrown away, so the change never shows.

**6. Known-ASIN walked records become UPDATE events, not dup-skip discards** ([fetcher:1422-1425](../amazon-library-fetcher.js) seeds seenASINs with all known ASINs; live sample record for wishlisted Oath of Honor was thrown away 2026-09-04) — refresh ownershipType/acquisitionDate/binding from the record; wishlist→sample/borrow becomes visible (today invisible FOREVER for borrows — no pastPurchase backstop); never downgrade purchased (stale sample records in full fetches); newest-record-wins = record date vs STORED acquisitionDate; respect userEdited; acquisitionDate refresh also heals the watermark re-walk quirk. pastPurchase upgrade demoted to backstop.

### Let library loans and Audible Plus books upgrade to owned

_Why it matters:_ Those two kinds can never become "owned" today, even after you buy the book.

**7. `TEMP_OWNERSHIP` gains `publicLibraryLending` + `audiblePlus`** (list written v4.11.8, never updated for v5.2.0's new types — loan→purchase can never upgrade; no-goal loans skipped by price phase)

### Write the wishlist / ownership rules down in one design doc

_Why it matters:_ So the rules are settled once and never argued again.

**8. Docs**: wishlist model + transition matrix into a design doc (FORMAT-POLICY sibling) — never relitigate. ~~Divider between Move to / Copy to~~ (suspect exonerated by item 9's diagnosis).

### Relay Import: only books in no folder should go to the Inbox

_Why it matters:_ A restore once copied the whole library into the Inbox.

**9. Relay-import Inbox placement: predicate must be "in no folder", not "new to the books DB"** (DIAGNOSED 2026-09-04: Ron's whole library — Inbox count 3076 — got Inbox-copied when Relay Import ran as a restore against the deleted books store on Sep-3; every book was "new to the DB" while the folders blob still filed them; js:4770/4824. Fix: filter newBookIds through getAllBookIdsInFolders() + skip isDeleted). Add restore-into-empty-DB to PRELAUNCH-TEST-GATE suite 4. ~~One-shot cleanup~~ RESOLVED 2026-09-04: Ron restored the 9/3 13:05 backup; count script showed only 4 genuine dual-filed stragglers (hand-cleaned). Retest this path after the fix (books-blob delete + relay restore ⇒ Inbox count unchanged).

## 🚦 Before public launch

_Formerly: 🚦 Pre-Launch (must-do before public launch)_

### Help, docs and onboarding

_Formerly: Docs & onboarding_

#### Security page: finish the high-contrast light theme

_Why it matters:_ The last bit of polish on the security page; low priority.

**security.html: residual polish** (2026-09-09: content lies FIXED same-day + nav + theme via Tailwind-override sheet — dark/hc-dark done): remaining = hc-light treatment, and optionally a real restyle onto the site's shared CSS instead of utility-class overrides. Low priority now.

#### Rewrite the User Guide around Searches, Book Lists and Folders

_Why it matters:_ The guide predates today's way of organizing.

USER-GUIDE.md + GPT manual — rewrite around the new mental model (All Books / Searches / Book Lists / Folders; custodial vs supplemental; "when to use which"), **including the Book List ↔ Folder workflow pattern** (structure lives in Folders; to-read queues live in Book Lists) and "get books out of Inbox → use a folder, not a Book List". Draw the backlog-wrangling examples from **docs/design/WORKFLOW-PATTERNS.md** and the facts/FAQ from **docs/design/SUPPORT-KB.md** (mined 2026-09-10 from the full session transcript back to May; kept current by the same-breath rule + release-checklist sweep)

#### Rename "Relay" to "Cloud Sync" everywhere users see it

_Why it matters:_ "Relay" is an engineering word; a rename is free before launch and expensive after.

**Rename user-facing "Relay" → "Cloud Sync"** (Cloud Sync Setup / Import from Cloud; status section, tooltips, fetcher overlays, recovery steps) — kills the engineering term that leaked into the UI; "Cloud Relay" considered and rejected as jargon-plus-clunk (2026-08-28). Internal names (`RWRelay`, filenames, worker) unchanged. Pure copy-pass, ~20-40 strings + README/features/tutorials. **Fold into the USER-GUIDE rewrite** so the new names bake into the docs in one motion. Renames are free pre-launch and expensive forever after.

#### Update and record the sizzle reel

_Why it matters:_ The promo video shows the old way of organizing.

Sizzle reel — update the script for Book Lists/Searches, then record + produce

#### Add "Watch Tutorials" to the Help menu

_Why it matters:_ Makes the tutorials easy to find.

Add "Watch Tutorials" to the app Help menu

#### Refresh the landing page's before / after screenshot

_Why it matters:_ The "after" picture predates the redesign.

Refresh the landing-page before/after screenshot (post-redesign "after")

#### Create a FAQ page

_Why it matters:_ Common questions answered in one place.

FAQ page — faq.html (Security/Privacy, Data/Backup, Troubleshooting, Library, General); link from Help, README, features/tutorials footers

#### Build the support assistant (custom GPT)

_Why it matters:_ Lets users get answers without waiting for you.

Custom GPT support assistant — build + link from Help menu → see docs/design/SUPPORT-GPT.md (spec)

#### Document how to recover from disasters

_Why it matters:_ Users need clear steps when credentials or data are lost.

Disaster Recovery documentation (relay credential recovery paths; backups include creds)

### Safety and data protection

_Formerly: Safety / data-integrity guards_

#### All the pre-launch data tests pass

_Why it matters:_ The core data rules must be proven before strangers rely on them.

**Test gate green** — the data-layer characterization suites in docs/design/PRELAUNCH-TEST-GATE.md (merge/edit-protection, import mapping, tombstones, load guards, relay semantics) exist and pass. Spec'd 2026-09-04 while the bug classes were fresh; ~2-4 sessions at gate time. Blocks launch, nothing else.

#### Warn before uploading a much smaller library (demo safety)

_Why it matters:_ A leftover demo setting could replace a real library with a tiny one.

Demo-whitelist footgun guard (6f) — warn/confirm before uploading a library dramatically smaller than the relay's; make the active-whitelist banner unmissable; ensure no demo state can ship

#### A button to rebuild the library from Amazon

_Why it matters:_ Today a full reset needs the browser's developer tools.

"Rebuild library from Amazon (full re-fetch)" affordance (6g) — clear the relay library without DevTools; pairs with the demo-whitelist guard

#### Pin the exact versions of outside code libraries

_Why it matters:_ An unannounced update to one of them could break the app overnight.

Pin remaining CDN deps (6h) — React/ReactDOM to an exact 18.x; audit all HTML entry points (Tailwind's durable fix is the precompile step below)

#### Find out why some books end up in no folder

_Why it matters:_ Rare reports of books in no folder at all; watch whether it still happens.

`integrity-homeless` investigation — real user event in v6.11.5 + 2 more field events 2026-09-03; books in IndexedDB with no folder refs. F1 (7.7.0) removed the leading suspected cause (stale-FOLDERS_KEY cold boot referencing nothing for newest books) — WATCH the event post-release before investing a session

#### Stop cleanly when Amazon asks for a human check mid-fetch

_Why it matters:_ Today it shows confusing errors instead of saying what to do.

**Mid-sweep challenge detection** — classify challenge-shaped responses (HTML where JSON expected, validate-captcha redirect, robot-check 503) in the fetchers' retry path and halt with an honest message: "Amazon is asking for a human check. Open any Amazon page, complete it, then re-run — everything fetched so far is safe." (That last clause is TRUE post-7.0: a halted run is uncommitted and invisible.) Phase 0 already guards startup; this covers a challenge appearing mid-run, which today reads as generic API errors. Never observed yet — cheap pre-launch hardening. (External review item 7 kernel.)

### Costs

_Formerly: Launch economics_

#### Move to Cloudflare's $5/month plan around launch

_Why it matters:_ The free plan supports only a handful of users.

Flip to Workers Paid ($5/mo) at or shortly before public launch — analysis DONE (RELAY-ECONOMICS.md, 2026-08-28): post-7.5.0 levers, flat $5 covers ~250 Ron-like users; free tier is ~6-10 and SHARED. This is now just the act of upgrading the Cloudflare plan at the right moment.

## 🔧 Relay follow-ups

_Formerly: 🔧 7.0.0 follow-ups (relay)_

### Relay Setup's connection test checks the wrong relay on dev

_Why it matters:_ On your local copy or the dev site it tests production, so its answer can be wrong.

**Relay Setup's connection test always checks the PROD relay, even on localhost / the dev site (found 2026-10-12)**.
WHAT YOU SEE: on your local copy or the dev site, File → Relay Setup → the connection test reports on the *production*
relay, not the dev relay your copy actually uses — so "connected"/"revoked" there can be wrong for dev. WHY:
`readerwrangler.js` (the `case 'test':` branch, ~line 1685) hard-codes `https://readerwrangler-relay.readerwrangler.workers.dev`
instead of using the dev-aware worker URL (`window._RW_RELAY_WORKER_URL`, set at ~line 90 for localhost + the dev repo).
DO: read the same worker URL every other relay call uses (one accessor, not a second hard-coded string). Small.

### Relay storage: stop leftovers piling up, and report usage correctly (in progress)

_Why it matters:_ Leftovers eat into the free storage limit, and the daily email was reporting the wrong total.

**Relay storage keeps climbing ~18 MB per Restore, and the daily usage email shows the wrong number** (found 2026-10-03/04; full write-up + fix design in **docs/design/RELAY-WRITE-REDESIGN.md §14a**). Real total ≈572 MB (56% of the 1 GB free tier) while emails showed 219.7/326/0 — each email reports ONE bucket (prod or dev), never the sum, and "no data" prints as 0. ~265 MB is recoverable leftovers. Three fixes, one "relay storage" side-fix branch (Ron: after the overlay branch unless urgency changes): (1) Restore never deletes the package it absorbs → move cleanup INTO `commitGeneration` (+ dedupe `absorbedRuns`); (2) usage email: per-bucket query + sum, "no data" not 0, `keyCount` cross-check; (3) worker-side daily sweep for torn/extra/absorbed leftovers, report-only first, then deleting. Leave prod channel `58c1bfd7…` alone (another user; expires Dec 7). Inventory tool: `.private/analyze-relay-keys.js`.
**B1 DONE in 7.21.1 (2026-10-13):** cleanup inside `commitGeneration` + dedupe — proven on dev (a same-content Restore → "🧹 Reclaimed 1 absorbed bulk run(s)"; inventory: 0 multi-part runs left, 2 library + 2 device-state gens). Prod's old leftovers get reclaimed on prod's next save (or by the B2 sweep).
**B2 STATUS + REVISED PLAN (Ron, 2026-10-14) — branch `feature/relay-worker-b2`, alpha.4 `e753679` deployed to DEV ONLY (prod still runs the old worker):**
- Built: combined usage email from both relays (dev's subject "[Dev]"), threshold alerts on the total (prod only), report-only storage check, key check (Cloudflare's key count = the day's HIGHEST, so live ≤ it is "consistent"), every email also as HTML, worker events labeled prod-/dev-, `WORKER_VERSION` in every email (version-guard enforces the bump).
- Learned the hard way: Cloudflare cron incidents (2026-10-12, 10-13, 10-14) delayed schedule changes by HOURS — the replaced 10-minute test schedule kept mailing. Now each schedule runs only its own job (matched by the schedule's text, so a late run still counts); any other schedule does nothing and is counted in RED at the top of the next summary. **Never test with a temporary schedule again** — test with the on-demand summary: PowerShell `$k = Read-Host "TEST_ALERT_KEY"; Invoke-RestMethod -Method Post -Uri ("https://readerwrangler-relay-dev.readerwrangler.workers.dev/run-summary?key=" + [uri]::EscapeDataString($k))` (one email each; Resend allows 100/day).
- **(1) TONIGHT 6:55 PM:** exactly ONE prod email (old format — settles the 10-13 duplicate) + the "[Dev]" summary, opening with the red section if the stray 10-minute schedule still fired. Also check dev's storage figure vs the Cloudflare dashboard.
- **(2) In a day or two: deploy report-only to PROD** (asks Ron) — prod has the REAL leftovers, so its report is the real test of the rules: expect "would delete" the interrupted save `…21fc`, and "kept" the never-imported Restore `…3560` (10-13 inventory). Possibly one storage-band alert on its first threshold check.
- **(3) After a few days of both reports being right: release 7.22.0 (report-only)** — update RELAY-WRITE-REDESIGN §14a (fix 2 + 3 built report-only; its two open questions are answered: each relay checks its own storage; Cloudflare's key count is a daily max), CHANGELOG (Ron's word), squash/tag/push both, PM.
- **(4) Deleting = the NEXT release, own branch:** needs a per-run budget (a free-plan run gets 50 subrequests and every storage call counts — one 18-part leftover alone is 19 deletes; spread big cleanups over days). Test on dev with DELIBERATELY PLANTED leftovers on the test channel `22222222…` (dev has none of its own), confirm it removes exactly those, a few days on dev, then prod.
- **(5) Then C** (below).
**PLAN AGREED 2026-10-13 (Ron):** fresh read-only inventory done — prod unchanged since Sep 9 (torn chunk `…21fc`, unabsorbed Restore `…3560`, legacy device-state); dev's ~160 MB of Restore packages were reclaimed by the 2026-10-12 Imports (Import retries cleanup of earlier absorbed runs — so the Restore leak is permanent only on a channel that never imports, like prod); dev showed 7 device-state copies (F2). The Sep 27 dev runs are imported — that hold is lifted. ORDER: (A) 7.21.0 contributor mode (prereq); (B1) app-side: cleanup inside `commitGeneration` + dedupe; ~~then Send to Production~~ — considered and REJECTED 2026-10-13 (see docs/design/SEND-TO-PRODUCTION.md); (B2) worker update — a `RELAY_ENV` prod/dev setting; BOTH workers send the COMBINED usage email (prod + dev + total vs the account-wide free limits), dev's subject says "Dev"; worker statistics labeled prod-/dev-; daily cleanup REPORT-ONLY; dev gets a schedule (summary + cleanup); only prod sends threshold alerts for now. Deploy to DEV first (`npx wrangler deploy --env dev`), ~~~1 week of correct reports, then deletion on for dev, then the same for prod~~ (order REVISED 2026-10-14 — see B2 STATUS above: report-only to prod next, release, then deletion as its own release) — every deploy asks Ron first (the pre-approved prod deploy was removed from local permissions). (C, later) a tiny SHARED notepad storage bound to both workers (no user data): dev = backup alerter (sends "[Dev] backup alert" if a crossing it has seen for >1 h has no prod alert recorded since — timestamps, no cross-deletes) + a "prod is alive" check (alert if prod's daily summary is >26 h old).

### Let a new user's first big fetch resume after an interruption

_Why it matters:_ A first 3,000-book fetch that dies near the end starts over from scratch.

**Checkpoint the cold (first-time) fetch** — a ~3,000-book initial enrichment has no resume; die at book 2,800, start over. 7.0 makes it natural: send enrichment progress as mailbox letters in stages so a resumed run's skip-hint already knows what's done. Bites each user exactly once — low priority, pre-launch nice-to-have. (From the 2026-08-21 external sync review, item 1's salvageable kernel.)

### Keep the settings the app and relay share in step

_Why it matters:_ Two settings are copied by hand in two places — fine for now; revisit if more appear.

**Worker/client protocol-constant drift note** — `LETTER_TTL` (worker, seconds) and `LETTER_TTL_MS` (client) are mirrored by hand; same for the minted-id format. Fine at 2 constants with cross-reference comments; revisit a shared protocol-constants module if a third appears. (Worker is the same language — JS — different runtime; sharing is possible, low value today.)

## 💰 Price checking

_Formerly: 💰 Price sweep scoping + staleness display (agreed 2026-08-21, from external sync review item 2)_

### Notice when a Kindle edition appears for a print-only book

_Why it matters:_ So you can switch to the Kindle edition without losing its folders, lists and tags.

**Format watch (LOW priority)** — `formatWatch: 'kindle'` on print-edition placeholders; slow-lane detection of a Kindle edition appearing; on hit, OFFER (never auto) a swap to the new ASIN carrying folder/Book List/tags/price goal (cousin of the wishlist→owned upgrade). KEY VERIFY first: does the batch enrichment API expose sibling editions for a print ASIN, or does detection need per-book product-page fetches? LOW because the live cases are mostly covered: Amazon author-follow notifies on new-format releases (Heinlein), and for withdrawn-Kindle books already recorded as Kindle, the price REAPPEARING in the normal price sweep is itself the availability signal (The Destroyer's 18 withdrawn titles) — the only uncovered gap is print-placeholder→Kindle detection. (External review item 6.)

### Now and then, refresh ratings for books you might buy

_Why it matters:_ Ratings are frozen at the first fetch — fine for owned books, a little stale for buying decisions.

**Optional "slow lane": occasional re-enrichment of buyable books** (ratings/review counts — frozen at first fetch today, which is fine for owned books but mildly stale for purchase decisions). Monthly-ish or every-Nth-fetch, reusing item-2's scoped list + batch calls. 7.0 letters make it interruption-safe: results go out as a run; tab closes, so be it — nothing torn, resumes next time. NOT the per-book adaptive-TTL machinery from the external review (a beautiful solution to a scale problem we don't have). Likely shared mechanism with the format watch above. (External review item 3 kernel.)

## 🔜 Soon

_Formerly: 🔜 Next (6.12.x follow-ups)_

### Undo, deleting and multiple windows

#### Finish routing every change through one shared path, with undo

_Why it matters:_ A few actions — deleting tags or Searches, renaming — still can't be undone.

**Operations single-source-of-truth — remaining bits** — CORE shipped in **6.13.1**: folder delete (`deleteFolder`), book move/copy (all menu + drag → `moveItems`), folder reparent (menu/cut-paste/drag → `reparentFolder`), Book List create/delete, and forced undo/redo toasts (every action stamped with a label). Still un-consolidated (lower priority, less drift-prone): **tag** delete, **Search** delete, folder/Book-List **rename** (make undoable), the folder-copy **redo** TODO (js~6398, in `COPY_PASTE_FOLDER`), and optionally folding `moveItems`' folder-reparent into `reparentFolder`. → docs/design/OPERATIONS-REFACTOR.md. Feeds MODULE-SPLIT.

#### The Delete key should delete the folders you've selected

_Why it matters:_ Today it only deletes the folder you're inside.

**DEL deletes the folder(s) selected in the right-pane list / Folders overview** — today the DEL key only deletes the folder you're *inside* (`selectedFolderId`), not a right-pane row selection (`getSelectedFolderIds()`). Wire single-select via `deleteFolder`, multi-select via a batch confirm + one compound undo (best once the ops layer has a `deleteFolders(folders)` primitive — don't ship single-only, it's more confusing than neither). Surfaced during ops refactor #1.

#### Keep reading the old save format (a standing decision, not a task)

_Why it matters:_ Some users update late; these reads are cheap. Recorded so nobody removes them on a schedule.

**Legacy FOLDERS_KEY/BOOKLISTS_KEY migration reads: KEEP INDEFINITELY** (Ron 2026-09-04: field users update on their own schedule — GoatCounter shows real users; the reads are cheap and dated comments explain them). Revisit only with adoption evidence, never on a release-count schedule.

#### Protect against editing in two tabs at once

_Why it matters:_ Two open tabs can overwrite each other's work — a real data-loss risk.

**Multi-tab hardening — Web-Locks read-only second tab (MEDIUM priority)** + reload-then-promote +
live/freeze viewer → designed in docs/design/MULTI-INSTANCE.md §4. This is **Tier 0**: the real data-loss
footgun (two tabs share ONE localStorage, so a stale tab's edit clobbers the other's work). Fully designed
and ratified 2026-08-30; unbuilt. (Queue note "after 7.7.0" is stale — 7.7.0 shipped long ago; this just
hasn't been picked up.)

#### Warn when another browser has newer changes

_Why it matters:_ Two browsers on one account can drift apart without anyone noticing.

**Cross-browser sequential coherence — check-on-activation + soft relay lease (LOW priority)** →
designed in docs/design/MULTI-INSTANCE.md **§6** (added 2026-09-22). This is **Tier 1**: closes the
restore-to-sync footgun (two browsers on one channel via a copied backup) *without* live sync or a merge.
On idle→in-use, the browser compares the relay's serialized-state stamp to its own; if behind, offers
**Catch up & edit here / Just view / Leave as-is** (adopt the relay org blob + optionally claim the soft
lease). Real work = giving the desktop a device-state **adopt** path (today `getDeviceState` on desktop is
only a connection test, readerwrangler.js:1246) + the per-channel lease record. Builds on Tier 0's writer-state
(one "am I the editor?" concept, Web Locks in-browser + soft relay lease cross-browser). Live two-way concurrent
sync (Tier 2) is REJECTED on the ratio (needs push infra + an org CRDT) — see §6 non-goal.

### Book List menus and undo history

_Formerly: Auto-Organize ergonomics_

#### Book List menu: remove Move / Copy, and block dragging onto folders

_Why it matters:_ Moving a Book List entry into a folder makes no sense, and once caused a membership mess.

**Book List right-click menu — drop Move/Copy + block Book-List→folder drag (A)** — a Book List entry is a shortcut; Move/Copy of a shortcut INTO a folder is incoherent. When viewing a Book List, remove those two menu items (keep Add-to-Book-List, Remove-from-list, Edit, reorder); block plain AND Ctrl drag from a Book List onto a folder. (Ron, 2026-08-08 — the muddled Book-List→Inbox "move" that created the Inbox+folder+list triple-membership mess.)

#### Undo history sometimes empties by itself

_Why it matters:_ Losing undo mid-session is alarming; the cause is still unknown.

**Undo stack clears mid-session unexpectedly (D)** — twice (2026-08-07/08) the undo stack emptied with no user undo/redo. **NARROWED 2026-09-01, not solved**: the sweep proved NO code path clears the stack (in-memory only; MAX_UNDO trims oldest only) — so SOME invisible reload is the only mechanism on the table. Candidates: TinySuspender discard-and-restore (a reload the user never sees) — but Ron's config argues against it for those incidents (60-min idle timeout, he was actively bouncing tabs; localhost/rw.com NOT whitelisted, so possible but improbable) — or a forgotten manual reload. Watch: next sighting, check console history + Data Status "last checked" (a discard clears both). PROPHYLACTIC regardless: whitelist localhost + readerwrangler.com in TinySuspender (a suspended RW tab also risks torn flush-on-leave pushes — swept now, but still wasteful).

### Ideas from the August 2026 library clean-up

_Formerly: 2026-08-10 library-cleanup findings (Ron)_

#### Auto-Organize preview: show which Book Lists a book is in

_Why it matters:_ You see a book's folders but not its Book Lists while deciding where it goes.

**Auto-Organize preview should show Book List membership** too (alongside the folder neighborhood).

#### See an author's other books without leaving your spot

_Why it matters:_ Today it takes All Books + a filter + finding your way back.

**"Other books by this author" quick-view** — from a book/folder, see the author's other books without jumping to All Books + filter + back.

#### Open one book's details without losing a multi-selection

_Why it matters:_ Lets you identify a book mid-scan and carry on with your selection.

**Right-click "Open" a book while multi-selecting** — opens the book detail WITHOUT clearing the selection; normal flow opens the whole selection as a shelf (nav). Lets you ID a book mid-scan and resume. (Name per UX.)

#### User Guide: explain workarounds for fields you can't filter by

_Why it matters:_ There's usually another way, e.g. add the column in List view and sort.

**USER-GUIDE/GPT note: "can't filter by field X" → tell them the workaround** (e.g. List view → add that column → sort). More than one way to skin a cat.

#### Drag between Folders and Book Lists

_Why it matters:_ Natural gestures for filling Book Lists, plus honest messages about what a drop did.

**Cross-section drag: Folders ↔ Book Lists** (DECIDED 2026-08-29) — honesty fixes (Added-not-Moved toast/undo from list views; kill fake drop affordances incl. the blanket left-pane preventDefault; undoable list reorder; toast over-count; Trash leak) + the two gestures: folder **ON** a list row = add its books; folder/books **BETWEEN** rows = create new list(s) there, named `<folder name> - To Read` for folders / engine-named for books (grabbed-noun principle, Beach-Reads example); right-click New gains current-folder-name fallback → docs/design/CROSS-SECTION-DRAG.md (spec). **On ship: update SUPPORT-KB §8/§6** (they document current behavior only)

#### Search everywhere without leaving the current folder

_Why it matters:_ Answers "is this book in my library?" without losing your place.

**Search everywhere — scope toggle + zero-result nudge** (Ron, 2026-08-29) — answers "is this book in my library?" WITHOUT losing your spot. Search box stays folder-scoped by default; while searching, show a scope toggle **This folder | Everywhere** (Finder/Explorer search-in-place convention). "Everywhere" shows all-library matches in the right pane as a temporary view (reuse the view-folder filter-stash plumbing); clearing the search returns to the folder + scroll position untouched. **Discoverability engine**: the empty-result state offers *"No matches in ‹folder› — Search everywhere?"* as a one-click link (Gmail/Amazon convention). Result rows pair with the existing "see where a book lives" popup — the answer arrives with locations.

### Other follow-ups

#### Wording pass: explain Book List shortcuts and Linked Copies

_Why it matters:_ Those terms confuse people unless they're explained once, clearly.

**Terminology copy pass** (6.12.1) — "shortcut" language in Book List toasts/menus; explain "Linked Copies" once in manual/GPT → see docs/design/TERMINOLOGY.md (spec)

#### Stray double spaces in author names create duplicate authors

_Why it matters:_ An author can split in two, making a series look incomplete.

**Author/Series whitespace hygiene** — collapse runs of internal whitespace + trim on fetch/import/edit so "Jodi  Taylor" (double space) can't split from "Jodi Taylor" (silently creates a duplicate author + orphan series in Auto-Organize). Add a **one-time cleanup sweep** for existing data. (Ron hit this on Jodi Taylor / Time Police — 2 of 7 books mis-authored, series looked incomplete in the Auto-Organize preview.)

#### Fetcher: re-apply two lost improvements

_Why it matters:_ Two small fetcher changes were lost in an older version and never put back.

❓ May already be done — check before working on it.

**Fetcher `ee6d83c` re-apply** on v4.11.10 — `LIBRARY_EXCLUDE_TAGS` named-constant/doc + delisted-book (`product=null`) count+notice adapted to coexist with null-product recovery (count only when recovery also fails)

#### Hide returned loans and borrows

_Why it matters:_ Returned Prime, Kindle Unlimited and library loans clutter the library.

**Returned / expired borrows — filter & hide** — Prime/KU/library loans that were returned still clutter the library. Fetcher flags borrow nodes with `activeBorrow === false`; app adds a **"Returned" ownership filter, hidden-by-default** (toggle to show), bulk move-to-folder for keepers. **NOT** via the ASIN exclusion list (would block re-borrows). → docs/design/RETURNED-BORROWS.md

#### A management view for Book Lists

_Why it matters:_ One place to organize and order your Book Lists.

**Book Lists management view** + generic orderable-left-pane-section ordering (Folders/Views/Book Lists uniform) → see docs/design/FOLDER-ORDERING.md (spec)

#### Delete a book from All Books (removes it everywhere)

_Why it matters:_ Today you have to remove a book from each folder and list separately.

Delete from All Books — soft-delete to Trash, removing from ALL folders + Book Lists at once (reuse membership snapshot; confirm dialog discloses count)

#### Drag a box to select covers

_Why it matters:_ Faster than clicking covers one by one.

Rectangle/Lasso selection in cover view (extends `explorerSelectedItems`)

#### Show only hidden books

_Why it matters:_ Answers "what have I hidden?" — today you have to hunt for them.

**Hidden books: 3-state control** (ratified 2026-09-03) — Show Hidden is a visibility toggle, not a finder ("find the 2 hidden among 337" is impractical). Hide hidden / Show all / **Only hidden** — the third state answers "what have I hidden?"

#### Fetch: report exactly how your library compares with Amazon

_Why it matters:_ So the fetch can honestly say "your library matches Amazon exactly", or list the differences.

**Fetcher: discrepancy-accounting redesign** (spec'd via live investigation 2026-09-03; supersedes the count-triggered sweep). THE INVARIANT the design must be able to report: Ron's library matches Amazon EXACTLY — 2801 = 2801 unique owned ASINs — once the units are right. Rules: (1) compare UNIQUE-ASIN SETS only, same filtered universe both sides — RW side excludes wishlist (337); Amazon side deduped (Amazon's `totalCount` counts acquisition RECORDS, not titles: 15 sample-then-purchase pairs in Ron's data; use totalCount only as a progress estimate). (2) KEEP Amazon's stock NOT-hash filters everywhere — probed live: hash `858f501de…` tags exactly the 13 product-null husks (unfetchable dead records, likely deleted-sample corpses), hash `222711ade…` currently tags nothing; the maps/physical items are NOT filter-hidden (present in the filtered walk). Log the filtered-vs-unfiltered count delta each fetch (13 today) as a reclassification tripwire. (3) Retire the 🩹 count sweep (its trigger compared titles+wishlist against records — structurally never equal); replace with set-exact differences in the orphan scan: amazon − local = missing owned books → refetch by ASIN → small follow-up run write; local − amazon = orphan CANDIDATES → verify absence before flagging (re-check just the candidate set). (4) User-facing output = Ron's two-directional "Removed-books check" report (each direction suppressed at 0; "orphan" jargon out; ℹ️ notes "still safe in ReaderWrangler"); the success line "Your library matches Amazon exactly" is now actually achievable. Exonerated by the investigation: API pagination (30- and 50-page walks returned identical complete sets; 101 tie-timestamp clusters covering 279 books, harmless), Amazon deletions (zero). The false-orphan bug itself (BOOK_BINDINGS skip inside the verification loop) is fixed separately in fetcher v5.2.7.

#### Fetcher odds and ends (progress figure, frozen timer, request pacing)

_Why it matters:_ Small fetcher fixes that are each too minor to stand alone.

Fetcher follow-ups: ownership-**upgrade** live positive test; un-trash on ownership upgrade (storage.js); fix the "772%" enriched ratio; elapsed-time display frozen during "Checking Relay" (both lines) / "Recovering" phases (timer repaints only on phase/progress updates — Ron 2026-09-03 ×2); **minimum request throttle floor** (~400ms) — FETCH_DELAY_MS is 0 today because network RTT throttles naturally, but if Amazon's backend ever speeds up we'd hammer them; Ron recalled this decision 2026-09-04 and it was never recorded — now it is

#### Tooltips in the book details window

_Why it matters:_ E.g. that Collections are read-only and come from Amazon.

Book detail dialog tooltips (esp. Collections = read-only-from-Amazon)

#### Wishlist: record the real format when a book is added

_Why it matters:_ Today the format is only known after the next full fetch.

Wishlist fetcher — capture real binding on add (product-page `bindingInformation`), not only after enrichment

#### Import book details from a pasted list or spreadsheet

_Why it matters:_ A way to bring in information from outside Amazon.

Metadata import (paste-list / CSV) + matching → see docs/design/Metadata-Import.md

#### Set different series numbers on several books at once ("2, 4")

_Why it matters:_ Needed when you own scattered volumes of a series.

Comma-separated series-position multi-edit ("2, 4" mapped to selected books in display order) — **needed for David Drake / Raj Whitehall** (ownership gaps that "renumber by current order" can't handle)

#### One book in several series positions (omnibus, anthology, MegaPack)

_Why it matters:_ A collection should appear at each place it belongs in its series.

**Multi-position series books: omnibus AND anthology (B)** — ONE record holding MULTIPLE series
positions, **rendered once at EACH position in series-sorted views**. Two cases, one mechanism
(ratified direction 2026-09-15): the omnibus that IS volumes 1–3 (`1-3` / `1,2,3`; Raj Whitehall
"789" workaround); the anthology whose stories interleave the series (`2.5, 4.5, 4.6, 5.5` —
Dresden Side Jobs pattern; today Ron files it at first occurrence with the story map in the Note).
Design points: `seriesPosition` becomes parseable list/range → sort-time expansion into display
instances (the `_instanceId` render-layer concept — NOT duplicate book records; ASIN-suffixed
pseudo-books REJECTED 2026-09-15: they'd fight ASIN-keyed merge, orphan scan would flag them every
fetch, dup detection/upgrades/CSV all need special cases). Repeats need a visible cue ("also at
4.5" / ⟳ badge — Law 16: deliberate duplication must read as intentional). **Manual order shows the
book ONCE** (manual slots are id-based; multi-slot belongs to series-sorted views). Interplay to
spec: Number-by-Current-Order, the comma-separated multi-edit above, CSV export (one row, list in
the column). The no-duplicates-per-folder invariant stays untouched.
**EXTENSION — multiple SERIES per record (MegaPacks, Ron 2026-09-20):** a public-domain MegaPack can
hold scattered volumes of *several* series at once (one ASIN = Skylark 1,4 + Lensman 2,4; possibly
cross-author). Generalize `seriesPosition` → **`seriesMemberships: [{series, positions:[…]}]`** (a
normal book = one entry, one position — uniform data; the UI compacts it). **Progressive-disclosure
UI** (don't tax the common case): ONE series → the existing series field + a **ranges/lists number
field** (`1-3, 5`); a **"+ add series"** affordance reveals the structured multi-row editor (series +
ranges per row) ONLY for the multi-series outlier. Filter matches if ANY membership matches; sort uses
the min position. **Per-work notes: OUT OF SCOPE** — user tags notes free-form (Ron already does this;
per-series notes would need context-tagged notes — not worth it). **Open rendering decision:** a
scattered list (`1, 4`) fills each slot (the gap-filling point), but a big contiguous range (`1-3`)
may collapse to ONE labeled/spanning entry to avoid N duplicate covers — settle against a real
MegaPack. **LUID / duplicate records stay REJECTED** (see above) — the memberships list handles
multi-series without touching ASIN identity. (Multi-author MegaPacks: the compound-author gap is a
separate, pre-existing concern, not solved here.)

#### Folder menu: Move to Top / Move to Bottom

_Why it matters:_ Quicker than dragging a folder a long way.

Folder "Move to Top / Move to Bottom" context items (D)

#### Dragging a subfolder to the top level drops it in the wrong place

_Why it matters:_ It lands near the bottom instead of where you dropped it.

Fix drag-subfolder→root drop-position (**confirmed still broken 2026-08-03**, annoying) — dropping a subfolder at root lands it alphabetical-ish near the bottom instead of at the drop target; shares a root cause with new-folder alphabetical insert + Move-to stale position

#### Book Lists: arrange by series number

_Why it matters:_ Put a list in series order once, then adjust it by hand.

Book Lists: **"Arrange by series #"** — in Manual mode, bake the series-number order into the list's manual order (persistent, then hand-tweak). The Book-List analog of folder sort-then-bake; a one-time rearrange, not a live sort mode. (Distinct from the existing "Number by current order," which sets each book's *position value*, not the list's order.)

#### Left pane: put the jump-to-top / bottom buttons by the scrollbar

_Why it matters:_ They sit at the bottom left today, not where you'd look for them.

**Left-pane jump-to-top/bottom placement** — both chevrons now ship, but they sit at the **bottom-left**, not at the two **scrollbar ends** as originally intended (Ron expected top-at-top / bottom-at-bottom). Scroll affordances conventionally live by the scrollbar (right). Reconsider: move the pair to the right near the scrollbar (spatial mapping), or adopt the single context-aware "back to top" that appears on scroll-down. **Per-section jump** (Searches / Book Lists / Folders): skip — the collapsible sections already handle that navigation.

## 🗄️ After launch

_Formerly: 🗄️ Backlog (post-launch)_

### Dialog look

_Formerly: Dialog look (LOW priority — Ron 2026-10-08)_

#### Rebuild the old-style message boxes as standard dialogs

_Why it matters:_ Low priority — only worth doing if we want every dialog to share one look.

**The confirm-style dialogs are hand-built page elements, not React `<Dialog>`s** — the message / OK-Cancel /
type-a-name / progress / choice / "Owned Book" boxes (showInfoDialog, showConfirmDialog, showInputDialog,
showProgressDialog, showChoiceDialog, showDeleteWarningDialog; ~45 call sites). 7.18.0 plugged them into the overlay
system (Esc, ✕, key blocking all shared) but kept their hand-built look. OPTION A (deferred): one React "dialog
service" rendering each request as a `<Dialog>`, call sites unchanged (`await showConfirmDialog(…)`) — removes ~300
lines of hand-built DOM and gives every dialog one look; costs a visual check of all ~45. Only worth it if a dialog
redesign is wanted.

### Speed

_Formerly: Responsiveness_

#### Clicking between books lags slightly while a filter is on

_Why it matters:_ A small but noticeable delay on every click while searching or filtering.

**Clicking a different book feels slightly laggy while a filter or search is active** (Ron 2026-10-06). WHAT YOU
SEE: with any filter/search active — even inside a small folder — click from one book to another; there's a small
but noticeable delay before the old book un-highlights and the new one highlights. With NO filter active it's
instant. Chrome's DevTools Console sometimes shows `[Violation] 'click' handler took ~270ms` (couldn't reproduce on
demand after a refresh). Severity: mild; "live with it on All Books" is acceptable. LIKELY CAUSE (hypothesis, not
verified): the filtered book list itself is already cached (`explorerDisplayItems` useMemo — it does NOT re-filter
on a selection change), so the extra per-click cost is probably the ACTIVE-FILTER BANNER, which re-renders on every
click and recomputes the "💾 N results · Save ▾" count, the "✓ Search: …" match check and the chips. DO: profile one
click with DevTools Performance (filter on vs off), then cache whatever the banner recomputes. (Ron's first theory —
"filter the current folder, not the whole library" — can't explain a SELECTION-click lag, since filtering isn't
re-run on selection; still worth checking for the initial filter cost.)

### Relay and data safety

_Formerly: Relay / data robustness_

#### Safer relay saves (the relay redesign)

_Why it matters:_ Saves that can't be half-written.

❓ May already be done — check before working on it.

Relay write redesign (atomic commit-pointer + app-owned key + wishlist-delta) → see docs/design/RELAY-WRITE-REDESIGN.md (spec)

#### Deleted books that stay deleted

_Why it matters:_ A permanently deleted book shouldn't come back on the next fetch.

❓ May already be done — check before working on it.

Tombstone delete (durable purge + smart resurrect) → see docs/design/TOMBSTONE-DELETE.md (spec)

#### Edit Kindle collections from ReaderWrangler

_Why it matters:_ Change your Kindle collections without going to Amazon.

Edit Kindle collections from WR → see docs/design/COLLECTION-EDITING.md

#### Cheaper small syncs (send only what changed)

_Why it matters:_ Optional: smaller uploads for small changes.

Relay delta-append for cheap incremental sync (OPTIONAL) → see docs/design/RELAY-DELTA.md (spec)

#### Relay Setup: disconnect, or reset credentials

_Why it matters:_ A clean way to stop syncing or start over.

Relay Disconnect / Reset credentials in Relay Setup

#### Ask before restoring when relay credentials don't match

_Why it matters:_ A backup from another account shouldn't silently mix data.

❓ May already be done — check before working on it.

Relay credential mismatch — safe restore (prompt on cred mismatch) → see docs/design/RELAY-CRED-MISMATCH.md (spec)

### Features

_Formerly: Features_

#### Finish keyboard accessibility

_Why it matters:_ Everything should be usable without a mouse.

Keyboard accessibility completion (focus trapping, `:focus-visible`, context-menu keys)

#### Show reading progress

_Why it matters:_ See how far along you are, in the book window and as a column.

Reading progress visualization (dialog + column)

#### Book recommendations

_Why it matters:_ Suggestions based on your library.

Book recommendations → see docs/design/BOOK-RECOMMENDATIONS.md

#### Show who a book is shared with (Family Library)

_Why it matters:_ See sharing at a glance in the book window.

Family sharing info (shared-with in book dialog)

#### Auto-Organize: file co-written books under each author

_Why it matters:_ Today a co-written book appears under only one author.

Auto-Organize: aggregate co-authored books under each author → see docs/design/AUTO-ORGANIZE-COAUTHORS.md (spec)

#### Two-pane split view

_Why it matters:_ Work with two folders side by side.

V2 dual-pane split → see docs/design/archive/DUAL-PANE-SPLIT.md

#### Support stores besides Amazon

_Why it matters:_ For readers who buy elsewhere too.

Multi-store architecture → see docs/reference/MULTI-STORE-ARCHITECTURE.md

#### Several people on one installation

_Why it matters:_ Low priority — Save / Restore Backup already works around it.

Multi-user support (low priority; Backup/Restore workaround exists) → see docs/design/archive/MULTI-USER-DESIGN.md

#### Smart collections (rule-based)

_Why it matters:_ Lists that fill themselves from rules you set.

Smart Collections (rule-based)

#### More ways to filter by Kindle collections

_Why it matters:_ Filter by read status, collection name, or "in no collection".

Collections filtering enhancements (read status / collection name / uncollected)

#### Reading statistics

_Why it matters:_ A dashboard of your reading.

Reading stats dashboard

#### More export options (printable list)

_Why it matters:_ Spreadsheet export exists; a print-friendly list doesn't.

❓ May already be done — check before working on it.

Enhanced export options (CSV, print-friendly list)

#### Connect with Goodreads / StoryGraph

_Why it matters:_ Share data with the reading sites people already use.

Third-party integrations (Goodreads / StoryGraph)

#### Animated drag-and-drop

_Why it matters:_ Books slide aside to show where a drop will land.

Live reflow drag-and-drop animation

### Technical clean-up

_Formerly: Tech / performance_

#### Faster loading: build the app ahead of time

_Why it matters:_ The app compiles itself in the browser on every load today.

Precompile build step (Babel + Tailwind → static) — removes in-browser Babel/Tailwind; the durable load-time + CDN-pin fix → see docs/design/PRECOMPILE.md (spec)

#### Split the main code file into modules

_Why it matters:_ One very large file is harder to work in safely.

Refactor readerwrangler.js into modules (re-assess — uiHelpers/storage/integrity already split) → see docs/design/MODULE-SPLIT.md (spec)

#### Show a notice when book descriptions are missing

_Why it matters:_ So a missing description reads as known, not broken.

Phase 3 UI error handling (missing-description banners)

#### Tooltip review: Tag from Collections wizard

_Why it matters:_ Make sure every control explains itself.

Tooltip audit — Tag from Collections wizard (6e)

#### Clean up developer console messages

_Why it matters:_ About 70 of them: keep, hide or remove each.

console.log audit (~70 statements — keep/gate/remove)

#### Check nothing was lost between versions 4 and 5

_Why it matters:_ A feature-by-feature comparison.

v4 → v5 feature-parity audit

#### Leftover desktop polish (left-pane keyboard, shadows)

_Why it matters:_ Small finishing touches.

Deferred desktop polish (left-pane keyboard nav; directional shadow consistency)

## 🧊 Someday

_Formerly: 🧊 Icebox (no timeline)_

### Test on Safari (desktop and iPhone)

_Why it matters:_ Some Safari differences could break storage or layout.

Safari browser testing (desktop + iOS; IndexedDB / PWA / CSS risk)
