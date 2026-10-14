<!-- TOC -->

- [TODO](#todo)
  - [🔝 Up next](#up-next)
    - [Cancelling a new folder that a filter hides should discard it](#cancelling-a-new-folder-that-a-filter-hides-should-discard-it)
    - [Start the local server automatically, without exposing private files](#start-the-local-server-automatically-without-exposing-private-files)
    - [Book details window: changes happen only when you click Save](#book-details-window-changes-happen-only-when-you-click-save)
    - [Drag any dialog out of the way](#drag-any-dialog-out-of-the-way)
    - [Relay Setup: smoother sections and clearer Esc / Help behavior](#relay-setup-smoother-sections-and-clearer-esc--help-behavior)
    - [✅ Ctrl+A in a dialog must never select the page behind it](#ctrla-in-a-dialog-must-never-select-the-page-behind-it)
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
      - [✅ Add "Watch Tutorials" to the Help menu](#add-watch-tutorials-to-the-help-menu)
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

In priority order as last set on 2026-09-16: the first three were "the stack", then the rest. Re-rank as we review.

### Cancelling a new folder that a filter hides should discard it

_Why it matters:_ A new folder can land hidden by your filters, and there's no clean way to back out. Cancel should just remove it.

**What you see**
- With filters active, create a folder. A notice says the filters are hiding it and it won't appear in the left pane.
- The notice has no Cancel, so the folder stays, hidden.

**Decided** (Ron, during 7.14.2 testing — Option A now, Option C later)
- The notice gets 4 buttons: **Clear All Filters** / **Show All Folders** / **Leave As Is** (keep it hidden) / **Cancel**.
- **Cancel** — and Esc, ✕, or a click on the background — deletes the just-created folder, undoably, with the message "New folder discarded".
- **Later (Option C, separate):** warn *before* creating the folder, so nothing is created on Cancel; and stop the rename box opening on a folder row that's hidden.

**How (technical)**
- The notice is `newFolderHiddenAlert`; give its payload the new `folderId` at the 3 places that raise it (search
  `setNewFolderHiddenAlert` — the line numbers recorded in September have drifted).
- Delete through the existing undoable create-folder step (`CREATE_FOLDER`).
- Option C would predict `hasActiveFilters` before creating.

### Start the local server automatically, without exposing private files

_Why it matters:_ After every reboot you hunt for the server command, and today's server also shows private files to other devices at home.

**What you'd get**
- A shortcut in Windows' Startup folder runs a small file kept in the project, which starts the local server in a **visible** window at logon.

**Decided** (Ron, 2026-10-06)
- **Keep the address `localhost:8000`.** Changing it (e.g. an Apache alias) would orphan everything the browser stores for ReaderWrangler — library, organization, relay credentials — and break phone testing.
- **Visible window**, not hidden or minimized.
- **Security fix:** today's plain server shows the WHOLE project folder — including `.private/` (secrets) and `.git/` — to any device on the home network. Can't restrict it to this PC alone (that breaks phone testing), so instead a tiny server script refuses those two folders.
- Use **`py`**, not `python`, in the file and docs (`py` → 3.14 on your PC; `python` → an older 3.13).

**Also**
- Update CONTRIBUTING.md's server lines, and drop its Python 2 line (dead since 2020).

**Status:** deferred by Ron 2026-10-06 until after the overlay branch (which shipped as 7.18.0).

**How (technical)**
- A versioned `serve.py`: standard `http.server` plus a handler that answers `/.private/…` and `/.git/…` with 404. Same port and origin.
- A versioned `.bat` launching it; a Startup-folder shortcut to the `.bat`.
- Don't use `--bind 127.0.0.1` (phone tests over the home network).

### Book details window: changes happen only when you click Save

_Why it matters:_ Today some fields save instantly and others wait for Save. One rule makes the window predictable, with one undo per Save.

**What you'd get**
- In the book details window, **Edit → Save is the only way anything changes** — one undo per Save. Cancel throws away everything you changed.
- Rating, price goal and tags stop being instant controls: they become read-only in view mode and editable in edit mode, saved with everything else. A new tag is created at Save.
- **Commands stay live in both modes:** Share, the Amazon link, Status History, ◀ ▶ (previous/next book).
- Outside the window, changes stay instant (one undo each).

**Quick access** (replaces the instant controls)
- In list view, click the Price Goal or My Rating cell to set it in place (preset goals / custom amount, or a row of stars).
- Decide during the build: should right-clicking a cover also offer a My Rating submenu?

**Steps**
1. **Classify every control** in the window as a field (saved by Save) or a command (acts now). Publish the table for your red pen **before** any code.
2. **Build** against the approved table — its own branch.

**Status:** ratified 2026-09-10. Version number assigned when the work starts (the old "7.14.0" label is stale).

**How (technical)**
- Rating / price goal / tags join `editBookFields` as staged fields; Save folds them into the one `EDIT_BOOK` undo step.
- Completes the edit-in-place pattern in OWNERSHIP-MODEL §4. Rationale and your context-keying principle: UNDO-MODEL.md, section "fully transactional".

### Drag any dialog out of the way

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

**Watch out**
- "Every dialog" covers two kinds: the standard dialogs, and the older message boxes (OK/Cancel, type-a-name, progress; about 45 places use them), which are built differently. Drag must work in both. The alternative is rebuilding the message boxes as standard dialogs first, which is its own task under "After launch".
- Today a click anywhere outside the top dialog closes it, including on a dialog showing through underneath. Point 5 changes that rule, so test it carefully.

**How (technical)**
- Build drag once in the shared `<Dialog>` (readerwrangler.js ~61) so every dialog gets it at once. The old per-dialog drag code (`dialogDrag`) is already gone.
- Message boxes share their window chrome in `attachDialogDismiss` (readerwrangler.js ~237); add drag there.
- A click on a lower dialog actually lands on the top dialog's full-window background layer (readerwrangler.js ~69–71). The background-click close must ignore clicks that fall over another dialog.
- New user feature, so it gets its own branch and release.

### Relay Setup: smoother sections and clearer Esc / Help behavior

_Why it matters:_ Its sections jump open so abruptly they look like new windows, and Esc behaves differently in a way you can't see.

**What you see** (File → Relay Setup)
1. **Sections jump.** Opening "Credentials" / "Enter Credentials Manually" or "Bookmarklet" / "Pairing" shoves everything up and down so hard it reads as "a new window appeared".
2. **A hidden level.** "Enter Credentials Manually" secretly counts as a level of its own: Esc backs out of it first instead of closing Relay Setup. Nothing shows you that.
3. **Help looks like a replacement.** Help opens exactly on top of Relay Setup, so it doesn't read as stacked on it.

**Ideas**
1. Animate the sections opening, so the eye can follow.
2. Either drop the hidden level (Esc just closes Relay Setup, like a background click), or make the level visible.
3. Draggable dialogs (above) fix it naturally — drag Help aside — or open Help slightly offset.

**Status:** noted 2026-09-28 during the overlay work; a separate, focused redesign pass.

**How (technical)**
- Item 2 is the `onClose` branch that handles `reason === 'esc'` specially in the Relay Setup dialog.

### ✅ Ctrl+A in a dialog must never select the page behind it

_Why it matters:_ A few controls inside dialogs could let Ctrl+A highlight the whole page behind the dialog.

**Status:** done — Ron confirmed 2026-10-14 (7.19.0 reworked Ctrl+A around "the area you last clicked"). Delete at the next release.

**History** (the original plan, for reference)
- Found and fixed in Bulk Edit's Series field (7.18.0-alpha.21); the page-level handler always blocks the browser's own select-all when a dialog is up (alpha.22), but only if the key reaches it.
- The plan was a two-way sweep for controls that stop the key, or one capture-phase guard at the page level that no control can bypass.

### Arrow keys should move through the Series suggestion lists

_Why it matters:_ You can't pick a series from the list with the keyboard — Down scrolls the window instead.

**What you see**
- In both Series fields — the book details window's edit mode (✏️), and Bulk Edit → Series… — open the list (type a letter or click ▼) and press Down.
- Nothing moves through the list. In the book details window, Down scrolls the whole window instead.
- Enter takes what you typed, not a highlighted row.

**What you'd get** (the standard pattern)
- Down / Up move a highlight through the list while the cursor **stays in the text field**, so you can keep typing.
- Enter picks the highlighted series. Esc closes the list (already works).
- While the list is open, Down / Up never scroll the window.

**The model already exists**
- The search box's "Recent searches" list works exactly this way today. Extract that and use **one implementation for all three type-ahead lists**: both Series fields and the search box.

**Status:** deferred by Ron 2026-10-06 (minor accessibility fix).

**How (technical)**
- Build it once in the shared list popup (`<Popover kind="list">` — both Series lists became that in 7.18.0-alpha.54), not per field.
- The working model is the `SearchInput` component's Down/Up/Enter/Esc handling. Stable copy "as it was": `git show 46a0cf6:readerwrangler.js`, search for `const SearchInput`.

### The "Save results" menu runs off the screen with many Book Lists

_Why it matters:_ With 20+ Book Lists, the lower ones are cut off and can't be reached.

**What you see**
- With a search or filter active, click the **💾 N results · Save ▾** button in the bar above the books.
- The menu lists every Book List. With about 20 or more, it's taller than the window and the bottom ones are cut off, with no way to scroll. A long flat list is also slow to scan.

**What you'd get**
- The menu opens on whichever side of its button (above or below) has more room, fits that space, and scrolls — the usual approach in modern menus.
- With more than ~10 lists, a filter box at the top — reuse the one the book right-click menu's "Move to" submenu already has.
- Check other menus that list your own items (Book Lists, folders) for the same problem while there.

**Watch out**
- This must **not** apply to right-click menus with fly-out submenus (Move to / Copy to): a scrolling menu would clip its own fly-outs.

**Status:** designed and deferred by Ron 2026-10-06.

**How (technical)**
- An opt-in option on `<Popover>` for button dropdowns: when it can't fit below, pick the roomier side, cap the height, scroll.
- Today it pins to the top of the window and hangs off the bottom. The fly-out rule is CursorPopup's "never add overflow".

### Removing a recent search should offer Undo

_Why it matters:_ One click deletes a recent search with no message and no way back.

**What you see**
- Click into the search box so "Recent searches" appears; click the × on a row.
- It's gone instantly: no message, no Undo, nothing in the 🕐 message history.
- By contrast, deleting a **saved** Search (left pane → SEARCHES → right-click → Delete Search) confirms, shows a message, and can be undone.

**Decided** (Ron + UX pass, 2026-10-07)
- Same treatment as a saved Search, **minus the confirmation**: remove at once, show "Removed · Undo", and log it in the 🕐 history.
- No "Are you sure?" — recents are automatic history, and a question per row would nag.

**Also**
- Route it through the shared undo/message path, not a one-off.
- Check what else still sits outside that path — tag and Search deletes were left out of it in 6.13.1.

### "Add Bibliography to Wishlist" is greyed out on an author's All Books tab

_Why it matters:_ The bookmarklet doesn't recognize that kind of author page, so the button can't be used there.

**What you see**
- On Amazon, click an author's name (e.g. John Marrs), open their author page's **All Books** tab, filter English + Kindle, then click the ReaderWrangler bookmarklet.
- The **⭐ Add Bibliography to Wishlist** button is disabled.
- Example address: `https://www.amazon.com/stores/author/B00F1CRG9U/allbooks?…`

**Likely cause** (found in the code, not yet tested live)
- The bookmarklet recognizes an author page only when its address contains the author's **name**: `/stores/John-Marrs/author/B00F1CRG9U`.
- The All Books tab's address has no name and adds `/allbooks`, so it isn't recognized.

**To do**
1. Accept both address shapes (name optional).
2. Then test the bibliography fetch itself on the All Books page — its layout may differ from the author home page, and the English/Kindle filters may change what's on screen.

**How (technical)**
- The check is in bookmarklet-nav-hub.js (~line 68): `/\/stores\/[^/]+\/author\/[A-Z0-9]{10}/i`.
- Fetcher / nav-hub change: bump their versions; test on the DEV bookmarklet first (a navigator change), then PROD.

### Dark theme: fix the unreadable bar and the light strips

_Why it matters:_ Some parts of the screen stay light in Dark mode, and one bar's text is unreadable.

**What you see** (View → Theme → Dark)
1. The bar under the menu bar reading **"📡 New library data available (uploaded …)"** keeps its light blue/purple background while its text turns near-white — unreadable.
2. A light strip shows under the **"🔍 Active: Search …"** bar, and wherever there's a gap between sections.
3. Not yet seen by you, same cause: light boxes in the Auto-Organize preview, and likely more.

**Why** (verified)
- Dark mode works by swapping a specific list of colors. Anything colored outside that list stays light.
- The relay bar's background is a fixed light gradient; the app's outer background is a gradient style that isn't on the list.

**To do**
- A sweep, not two spot fixes: find every fixed light color in the screens and move each onto the theme. Check each one in Dark afterwards.
- **Mechanism idea:** a commit-time check that flags new fixed light backgrounds, next to the existing name check.

**How (technical)**
- Dark remaps Tailwind classes in readerwrangler.css (`[data-theme="dark"] .bg-white {…}` etc.).
- Relay bar: inline `linear-gradient(135deg, #dbeafe, #ede9fe)` with `color: var(--text-primary)` (readerwrangler.js ~9360).
- Outer container: `bg-gradient-to-br from-blue-50 to-blue-100` (~8992) — gradient classes aren't remapped; the Active bar's `mb-4` gap shows it.
- Auto-Organize preview: `#f1f3f5`, `#fafafa`, `#e5e7eb` (~12009 / 12018 / 12046).
- Grep for inline `background: '#…'`, light `linear-gradient`, `from-*/to-*` classes and unmapped Tailwind colors; move them to CSS variables (e.g. `var(--bg-surface)`) or add them to the dark remap. The check could sit beside `scripts/check-names.js`.

### Book Lists and Searches: pin and sort them like Folders

_Why it matters:_ A long Book Lists column is hard to search; Folders already have pins and a Name / Manual sort.

**What you'd get**
- Book Lists and Searches in the left pane get **the same controls and words as Folders** (7.6.0): pins (a top tier) and a header sort control, **Manual ↔ Name**. No second ordering system three inches from the first.
- Pinning can be undone (list reordering already can).

**How you'd use it** (Ron, 2026-09-10)
- **Name to find** a list, then back to **Manual** for priority.
- Your top tier is the `New To Read - *` work lists (Prime clearing first); series To-Read lists below.
- Today you hunt with Ctrl+F, which costs a switch of thought.

**Status:** queued behind the book details window rework.

### Clearing a price goal doesn't fully clear it everywhere

_Why it matters:_ An old second price-goal field can keep a book counted as "has a goal" after you clear it.

**What happens**
- A few places treat a book as "has a goal" if **either** today's goal field **or** an older one is set: the Import's "kept their price goals" count, the fetcher's goal check, and the spreadsheet export.
- Clearing a goal in the app clears only today's field. A book still carrying the old one keeps "having a goal" in those places.

**To do**
1. First count whether any real book still has the old field set.
2. If so, move it into today's field once.
3. Retire the old field — one goal field, not two. Small.

**How (technical)**
- Today's field: `priceTrigger`. Old field: `targetPrice`.
- Readers: storage.js ~174 (import count), amazon-library-fetcher.js ~2286, the spreadsheet's `priceTrigger ?? targetPrice`; plus its row in bookFields.js.
- Found 2026-10-12.

### Find a book by its ASIN in the search box

_Why it matters:_ Handy for checking whether one specific book is in your library.

**What you'd get**
- Type a book's ASIN (e.g. `B08P52K2PZ`) into the search box at the top of the right pane, and it finds the book. Today the box matches only title, author and series.
- The box's placeholder and tooltip mention ASIN.

**Watch out**
- The matching rule exists in **three copies**: the live search, saved Searches, and the phone's search (which also matches notes and tags). Make it **one** shared rule that all three use.

**Status:** Ron, 2026-10-12 (came up testing removed books). Small.

**How (technical)**
- Copies: readerwrangler.js ~10044 (live filter), `bookMatchesFilters` ~2196 (saved Searches), mobile.js ~2289.
- One `bookMatchesText(book, term)` in uiHelpers, with ASIN as exact or prefix match, case-insensitive.

### A type-to-filter box for the left pane

_Why it matters:_ With many folders, Book Lists and Searches, typing a few letters is the fastest way to find one.

**What you'd get**
- One box that narrows **Folders + Book Lists + Searches** by name — the strongest pure "find" at scale. The bigger sibling of the pin/sort task above.

**Open questions**
- Where it sits: one box for the whole pane, or one per section?
- Keyboard: how you reach it (a shortcut?).
- Does it clear when you navigate somewhere?
- How it works with collapsed sections.

**Status:** Ron, 2026-09-10.

### Ctrl+X from a Book List or Search quietly copies instead of cutting

_Why it matters:_ You think you moved the book, but it never leaves the list.

**What happens**
- In a Book List or Search view, Ctrl+X a book, then paste it into a folder. It's added there, but stays in the list too.

**To do** (pick one)
- Refuse with an explanatory message (as All Books already does), **or**
- Make paste remove the book from the Book List it was cut from.

**How (technical)**
- Cut records the view as the source, but paste-cut only removes from **folders**. Found during alpha testing (alpha.7), filed not fixed.

### Faster back-to-back fetches: refresh everything at most once a day

_Why it matters:_ Grabbing one new book still re-prices and re-checks the whole library every time.

**What you see** (Ron, 2026-09-19, patching $0.99 series holes: buy → download → import, again and again)
- Each fetch re-prices every wishlist book, re-checks every book's details, and runs the full removed-books scan — wasteful when run back to back.

**Decided**
- **Always:** fetch what's new, and fill in the new books' details (series, cover, description) — you need them to file the books.
- **At most once a day:** the whole-library passes — re-pricing the wishlist, re-checking existing books, the removed-books scan. A day matches when prices start showing as stale (KB §16), so price-watching doesn't suffer.
- **When it skips, it says so** in the fetch's completion window, with one click to run them anyway: *"Skipped the full refresh (prices, details, removed-books check) — already done today. Do it now?"*
- **No Shift/Alt-click shortcut** for this — Windows reports those keys unreliably on clicks, and nobody would discover it.

**Before building**
- Check whether the fetcher already separates "fill in NEW books" from "re-price / re-check ALL". If they're tangled together, separating them is the real work.

**Also**
- Build together with "Fetch summary should report books you bought" (On hold section) — same completion window.
- When shipped, update SUPPORT-KB §16: "prices are as fresh as your last fetch" and "every wishlist book is re-priced each run" stop being true.

**How (technical)**
- Remember `lastFullPassAt` (relay, or browser storage on Amazon's site).
- A fetcher (bookmarklet) change, maybe with app/relay help for the stored time and the dialog.

### "Read in Kindle": open a book in the Kindle app or Cloud Reader

_Why it matters:_ Jump straight from ReaderWrangler to reading the book.

**What you'd get**
- A **Read** action on books you **own** (not wishlist or sample entries — those keep "Open in Amazon"):
  - **Phone:** opens the book in the Android Kindle app.
  - **Desktop:** opens Kindle Cloud Reader (read.amazon.com) at the book. Optionally also "Open in Kindle app" for Kindle-for-PC users (the browser asks "Open Kindle?").
- **Not** a built-in reader — you still read on the Paperwhite.

**Limits**
- **Tested and failed (2026-09-19):** opening a book in the Android app does **not** move it to the top of the Paperwhite's list. So it only helps people who read in the app or Cloud Reader; Paperwhite-only readers gain nothing. Prioritize accordingly.
- The links are **unofficial** — Amazon could break them. Keep a fallback to the book's Amazon page, and test per platform and app version.
- Needs the **Kindle edition's** ASIN; a print-only owned book won't open. Some titles can't be read in Cloud Reader at all, and there's no way to tell in advance.
- **Country matters:** non-US accounts need read.amazon.co.uk / .co.jp etc. Ask for the user's marketplace, or default to .com and rely on the fallback.

**How (technical)**
- Android (preferred, with fallback): `intent://book?action=open&asin=<ASIN>#Intent;scheme=kindle;package=com.amazon.kindle;S.browser_fallback_url=https%3A%2F%2Fwww.amazon.com%2Fdp%2F<ASIN>;end`
- Android bare form: `kindle://book?action=open&asin=<ASIN>` — must come from a tap (Chrome blocks it otherwise); behavior has shifted between app versions (may land on the details page instead of opening the book).
- Desktop: `https://read.amazon.com/?asin=<ASIN>` (opens if signed in; resumes at your last position).
- Fallback: `https://www.amazon.com/dp/<ASIN>`.
- Background research: the `reference_read_in_kindle` memory (Ron's 2026-09-19 research).

### Make sure an Import never wipes fields only ReaderWrangler sets

_Why it matters:_ Two fields were being wiped on every Import; check no other field has the same gap, and decide whether backups should keep them.

**Done so far** (7.16.0)
- The Tag from Collections wizard's two remembered settings were wiped on every Import. They're now protected, with a test locking that in.

**Still open**
1. **The general check:** any field the app sets that isn't sent along with your organization must be protected from Import, or Import silently wipes it. Walk the list of what's sent against the field table and check every field.
2. **Save / Restore and other devices still lose those two settings** — they aren't sent at all. If keeping the wizard's state across a backup matters, add them to what's sent and read back. Decide if it's in scope.

**How (technical)**
- Fields: `collectionTagSeen`, `collectionTags`; were incoming-wins (`'amazon'`), now local-wins (`'user'`) in the bookMerge registry, with a gate test.
- The rule: an app-written field missing from the device-state push payload must be `'user'`.
- Payload builder readerwrangler.js ~5560–5594; import parser ~6186 / ~6270. (2026-09-22)

### Turn more of our working rules into automatic checks (my tooling)

_Why it matters:_ Rules that depend on memory keep failing; automatic checks don't. This affects only how I work, not the app.

**The idea** (Ron, 2026-09-22, after "assuming bit us again")
- Go through docs/PRINCIPLES.md rule by rule and sort each one:
  - **Can become an automatic check** that blocks a commit or release — for example: run the tests before a commit; search for leftover TODO / REMOVE markers before release; version bumped when code changed; cache-busters match.
  - **Judgment only** (never assume, model the legal states, UX first). A hook can only *remind*, and reminders fade into rubber stamps. Give these teeth with a required artifact instead: e.g. every design doc must have an **"Assumptions (and how each was verified)"** section, which a hook can check exists when a design doc is written — catching assumptions at design time, not just at edit time.
- Guard against reminder bloat — the pre-build checklist is already 11 points.

**Open items**
1. ✅ The pre-build checklist only watched two files — widened to all app code on 2026-10-08.
2. **When an edit is bounced by the checklist inside a batch of edits, that one edit silently goes missing** (alpha.62 shipped half a fix). No obvious mechanism yet — a hook can't know which edits were intended. Needs design.
3. **My code safety check can be skipped by accident** (7.19.0 post-mortem). The checklist only fires for my normal editing tool; edits made with a find-and-replace command skip it. Make it fire for those too. Small.

**How (technical)**
- Item 3: the gate hooks only Edit / Write. Add a PreToolUse hook on Bash that spots `sed -i` or redirects onto a root `.js` or the relay worker, and runs the same once-per-turn checklist (reuse `is_app_source()`).

### Tag from Collections: clear up the checkbox vs. preview confusion

_Why it matters:_ Each row has two click targets that do different things, with nothing to tell them apart.

**What you see** (in the Tag from Collections wizard's left list)
- The **checkbox** means "include this collection when you Apply".
- Clicking the **name** means "show this collection's books on the right".
- Unchecking a box doesn't change the right side — only clicking a name does. And "checked" and "being shown" use the same row highlight, so you can't see the two states (it fooled you).

**Unsettled — don't prescribe a fix yet**
- First decide what the right side is **for**: a preview? the set Apply will use?
- Then make the two states look different — or unify them (the right side follows the checkboxes / your last action, with a header like "Viewing: X").
- Design pass before any code.

**Also** (Ron, 2026-09-22)
- A UX opinion wanted: should the wizard **also** be reachable from the Manage Tags menu — and where? Evaluate, don't just wire it in.

**How (technical)**
- The "shown" state is `tfcSelectedCollection`.

### Restore dialog calls yesterday's backup "today"

_Why it matters:_ A wrong date label can lead you to restore the wrong backup.

**What you see**
- A backup from 9/21 6:54 PM was labeled **"— today"** on 9/22. Not a time-zone effect: it was yesterday everywhere.

**Likely cause**
- "Within about 24 hours = today" instead of comparing calendar days — or a mix-up between UTC and local time.

**To do**
1. Verify first: find where the "— today" label is made.
2. Compare by calendar day in local time, and add "yesterday" and "N days ago".

### Phone: show which test build is running

_Why it matters:_ During testing you can't tell from the phone which build it's on.

**What you see**
- The phone's About shows "App v…" — the last **released** version, which by design doesn't change during testing — and "Mobile v…".
- The desktop shows the live test build (e.g. 7.16.0-alpha.6). The phone can't, since it's a different file. The mobile number does change with each test build, but the "App v" line looks stale.

**To do**
- Show a live build marker on the phone. Small display / version-plumbing fix.

**How (technical)**
- `APP_VERSION` (released, frozen during alphas) vs `ORGANIZER_VERSION` (live, desktop only) vs `MOBILE_VERSION` (moves per alpha).

## ⏸️ On hold: honest ownership changes (buying, samples, loans)

_Formerly: ⏸️ Ownership-honesty batch (ratified 2026-09-04, HELD — awaiting Ron's go; likely 7.8.0)_

When a book changes kind — wishlist → bought, sample → bought, a loan, a book in the Trash — ReaderWrangler should notice, show it, and never lose your settings. Ratified 2026-09-04; **held until you say go**. When it starts, **"Fetch should update books it already knows" goes first** (the old stack's note: "item 6 first").

**Already shipped from this batch**
- 7.7.2: Imports reclaim old upload storage. Proof outstanding: the first production Import on 7.7.2 or later should log "🧹 Reclaimed 7 absorbed bulk run(s)" (~124 MB). _(7.21.1 now does this on every save, so this proof may be moot.)_
- 7.8.0: the ownership dialog redesign, the undo fence, undo messages that name what they undo.
- 7.9.0: one unified Auto-Organize (two pieces deferred — the first two tasks below).
- 7.10.0: Save as Spreadsheet (CSV). _A reply to the user who asked for it is still owed (Ron's channel)._
- 7.11.0: item 11. (Item 12 was made unnecessary by the Auto-Organize rework.)

### Auto-Organize: let a misfiled book go back to the Inbox

_Why it matters:_ There's no way to send a book that Auto-Organize filed wrongly back to the Inbox.

**What you'd get**
- The Inbox as a "File under" choice in Auto-Organize, to take a misfiled book back out.

**How (technical)**
- Deferred from 7.9.0 on purpose (scope rule): it needs different commit machinery from ordinary filing.

### Auto-Organize: Shift-click ranges should follow what you see

_Why it matters:_ Shift-click selects by a hidden internal order that can differ from the order on screen.

**What you see**
- In Auto-Organize, Shift-click a range. In series mode, and in the grouped "Already filed" list, the selected range doesn't match the books between your two clicks on screen.

**How (technical)**
- The range follows the internal array order instead of the visual order. Deferred from 7.9.0.

### Fetch summary should report books you bought

_Why it matters:_ After buying 4 wishlist books, the summary says "0 new" — the upgrades only show in the developer console.

**What you'd get**
- The fetch's completion window lists ownership upgrades (wishlist / sample / loan → owned).

**Also**
- Build together with "Faster back-to-back fetches" (Up next) — same completion window.

**How (technical)**
- Today the upgrades are only logged as ⬆️ in the console.

### Import summary: count every ownership change, by kind

_Why it matters:_ Sample → owned upgrades are missed, and wishlist → sample could be mislabeled as owned.

**What you'd get**
- The Import summary counts every change, labeled by where the book ended up — e.g. "3 wishlist → owned", "1 wishlist → sample".
- The console line names the books (a missing title blocked a diagnosis on 2026-09-04).

**How (technical)**
- Since 6.17.2 the summary reports "N now owned", but it's keyed on the wishlist flag flipping. Key it on `ownershipType` transitions instead.

### Keep price goals when a book is bought, and say so

_Why it matters:_ Goals must never vanish silently; optionally offer a one-click "clear these goals".

**Decided** (Ron, 2026-09-04)
- **Keep** the goal when a book is bought — the old rule stands: never silently destroy.
- Add a receipt line (in the 🕐 history) saying which books kept their goals.
- Optional: a one-click **"Clear goals on these N"** in the Import summary. You pick during the build.

**Why that's enough**
- Bought books already need a manual visit to All Books to file them into reading lists, so clearing goals rides along on a trip you make anyway.

**Already there**
- Since 7.1.0 the Import summary says "N kept their price goals — clear if no longer wanted". The receipt line and the one-click clear are what's left.

### Keep the Import summary in the message history

_Why it matters:_ The summary disappears on refresh, leaving no record of what changed.

**What you'd get**
- The Import summary is also recorded in the 🕐 message history.

### Buying a book that's in the Trash should bring it back

_Why it matters:_ A book you just bought shouldn't stay hidden in the Trash.

**What you'd get**
- When a book in the Trash becomes owned, it comes out of the Trash automatically. (Ron: "YES! Include it.")

**How (technical)**
- Lives in storage.js (also listed under "Fetcher odds and ends" in Soon).

### Fetch should update books it already knows, not skip them

_Why it matters:_ A sample or loan of a wishlisted book is thrown away, so the change never shows.

**What happens**
- The fetcher skips any record whose ASIN it already knows. On 2026-09-04 a sample record for the wishlisted *Oath of Honor* was thrown away.
- For loans it's invisible **forever** — there's no other path that would catch it.

**What you'd get**
- A known book's record becomes an **update**: refresh its kind (owned / sample / loan…), purchase date and format from the record.
- wishlist → sample / loan becomes visible.

**Rules**
- **Never downgrade a purchased book** (full fetches include old sample records).
- The newest record wins: compare the record's date with the **stored** purchase date.
- Respect anything you edited yourself.
- Refreshing the purchase date also fixes a re-walk quirk in how the fetcher remembers where it stopped.
- The existing "past purchase" upgrade becomes just a backstop.

**How (technical)**
- amazon-library-fetcher.js (~1422–1425 when filed): `seenASINs` is seeded with every known ASIN, so known records are dup-skipped.
- Fields: `ownershipType`, `acquisitionDate`, binding; respect `userEdited`. The watermark re-walk quirk heals with the date refresh. `pastPurchase` demoted to backstop.

### Let library loans and Audible Plus books upgrade to owned

_Why it matters:_ Those two kinds can never become "owned" today, even after you buy the book.

**What happens**
- The fetcher's list of "temporary" kinds that can upgrade to owned was written for fetcher 4.11.8 and never updated for the kinds added in 5.2.0.
- So a library loan you later buy never upgrades, and loans without a price goal are skipped by the price check.

**How (technical)**
- Add `publicLibraryLending` and `audiblePlus` to `TEMP_OWNERSHIP` (amazon-library-fetcher.js ~2277; verified still missing 2026-10-14).

### Write the wishlist / ownership rules down in one design doc

_Why it matters:_ So the rules are settled once and never argued again.

**What you'd get**
- A design doc (a sibling of FORMAT-POLICY) holding the wishlist model and the table of which kind can change into which.

**History**
- A suspected "divider between Move to / Copy to" problem was cleared by the Inbox diagnosis below.

### Relay Import: only books in no folder should go to the Inbox

_Why it matters:_ A restore once copied the whole library into the Inbox.

**What happened** (diagnosed 2026-09-04)
- On Sep 3, Import from Relay ran as a restore against an emptied book store. Every book looked "new", so all 3,076 were copied into the Inbox — even though your folders still held them.
- Cleaned up the same day: you restored the 9/3 13:05 backup; only 4 genuinely double-filed books needed hand-fixing.

**The fix**
- The test for "goes to the Inbox" must be **"is in no folder"**, not "is new to the book store". Also skip deleted books.

**To do**
- Add "restore into an empty book store" to the pre-launch test suite (PRELAUNCH-TEST-GATE, suite 4).
- Retest after the fix: delete the book store, Import from Relay → the Inbox count is unchanged.

**How (technical)**
- Filter `newBookIds` through `getAllBookIdsInFolders()` and skip `isDeleted` (js ~4770 / ~4824 when filed).

## 🚦 Before public launch

_Formerly: 🚦 Pre-Launch (must-do before public launch)_

### Help, docs and onboarding

_Formerly: Docs & onboarding_

#### Security page: finish the high-contrast light theme

_Why it matters:_ The last bit of polish on the security page; low priority.

**Done already** (2026-09-09)
- The page's wrong statements were fixed, plus its navigation, and Dark / High-Contrast-Dark themes.

**Left**
- The High-Contrast-Light treatment.
- Optional: restyle it onto the site's shared styles instead of the current overrides.

#### Rewrite the User Guide around Searches, Book Lists and Folders

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

#### Rename "Relay" to "Cloud Sync" everywhere users see it

_Why it matters:_ "Relay" is an engineering word; renaming is free before launch and expensive after.

**What you'd get**
- "Cloud Sync Setup", "Import from Cloud", and the same in the status section, tooltips, the fetcher's screens and the recovery steps.
- About 20–40 phrases, plus README / features / tutorials pages.
- Internal names (code, files, the worker) stay as they are.

**Decided** (2026-08-28)
- "Cloud Relay" was considered and rejected — still jargon, and clunky.

**Watch out**
- CLAUDE.md currently tells me to use exactly "Relay", "Import from Relay" etc. in user-facing text. If this rename goes ahead, that rule changes with it.

**Also**
- Fold into the User Guide rewrite (above).

#### Update and record the sizzle reel

_Why it matters:_ The promo video shows the old way of organizing.

**To do**
1. Update the script for Book Lists and Searches.
2. Record and produce.

#### ✅ Add "Watch Tutorials" to the Help menu

_Why it matters:_ Makes the tutorials easy to find.

**Status:** done — verified 2026-10-14: Help → Watch Tutorials opens tutorials.html. Delete at the next release.

#### Refresh the landing page's before / after screenshot

_Why it matters:_ The "after" picture predates the redesign.

#### Create a FAQ page

_Why it matters:_ Common questions answered in one place.

**What you'd get**
- faq.html with sections: Security / Privacy, Data / Backup, Troubleshooting, Library, General.
- Linked from the Help menu, README, and the features and tutorials page footers.

#### Build the support assistant (custom GPT)

_Why it matters:_ Lets users get answers without waiting for you.

**What you'd get**
- A custom GPT that answers ReaderWrangler questions, linked from the Help menu.

**Spec:** docs/design/SUPPORT-GPT.md.

#### Document how to recover from disasters

_Why it matters:_ Users need clear steps when credentials or data are lost.

**Should cover**
- How to recover relay credentials.
- That backups include your credentials.

### Safety and data protection

_Formerly: Safety / data-integrity guards_

#### All the pre-launch data tests pass

_Why it matters:_ The core data rules must be proven before strangers rely on them.

**What it means**
- The test suites in docs/design/PRELAUNCH-TEST-GATE.md exist and pass: merging and edit protection, Import mapping, permanent-delete markers, load guards, relay behavior.
- Specified 2026-09-04 while those bugs were fresh. About 2–4 sessions when the time comes.
- **Blocks launch; blocks nothing else.**

#### Warn before uploading a much smaller library (demo safety)

_Why it matters:_ A leftover demo setting could replace a real library with a tiny one.

**What you'd get**
- A warning and confirmation before uploading a library dramatically smaller than the one on the relay.
- When the demo book list is active, a banner you can't miss.
- A guarantee that no demo setting can ship.

**How (technical)**
- Old review item 6f; the demo setting is the "demo whitelist".

#### A button to rebuild the library from Amazon

_Why it matters:_ Today a full reset needs the browser's developer tools.

**What you'd get**
- "Rebuild library from Amazon (full re-fetch)": clears the relay's library so the next fetch starts fresh.
- Goes with the demo-safety warning above.

**How (technical)**
- Old review item 6g.

#### Pin the exact versions of outside code libraries

_Why it matters:_ An unannounced update to one of them could break the app overnight.

**What you'd get**
- React and ReactDOM pinned to one exact 18.x version (today: "any 18" — readerwrangler.html ~128, checked 2026-10-14).
- Check every HTML page for the same.
- Tailwind's lasting fix is the "build the app ahead of time" task (After launch).

**How (technical)**
- Old review item 6h.

#### Find out why some books end up in no folder

_Why it matters:_ Rare reports of books in no folder at all; watch whether it still happens.

**What we know**
- One real user event on 6.11.5, and two more on 2026-09-03: books in the browser's book store that no folder refers to.
- 7.7.0 removed the leading suspect: a cold start reading an out-of-date folder list that didn't yet know the newest books.

**Next step**
- **Watch** for the event after releases before spending a session on it.

**How (technical)**
- The event is `integrity-homeless`; the suspect was a stale `FOLDERS_KEY`.

#### Stop cleanly when Amazon asks for a human check mid-fetch

_Why it matters:_ Today it shows confusing errors instead of saying what to do.

**What you'd get**
- When Amazon interrupts a fetch with a "are you human?" check, the fetcher stops and says: *"Amazon is asking for a human check. Open any Amazon page, complete it, then re-run — everything fetched so far is safe."*
- That last clause is true since 7.0: a stopped run is simply never committed.

**Status**
- The start of a fetch is already guarded; this covers a check appearing **partway through**. Never seen yet — cheap insurance before launch. (From an outside review, item 7.)

**How (technical)**
- In the fetchers' retry path, recognize check-shaped answers: HTML where JSON was expected, a validate-captcha redirect, a robot-check 503.

### Costs

_Formerly: Launch economics_

#### Move to Cloudflare's $5/month plan around launch

_Why it matters:_ The free plan supports only a handful of users.

**What we know** (RELAY-ECONOMICS.md, 2026-08-28)
- After 7.5.0's savings, the flat $5 plan covers about 250 users like you; the free plan about 6–10 — and it's shared between production and dev.
- So this is now just the act of upgrading at the right moment, at or shortly before launch.

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
