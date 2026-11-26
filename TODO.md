<!-- TOC -->

- [TODO](#todo)
  - [🔝 Up next](#up-next)
    - [🚦 The launch gate — target: January 2027](#the-launch-gate--target-january-2027)
      - [Outside reviews before building: launch risks, security, data safety, a newcomer's first look](#outside-reviews-before-building-launch-risks-security-data-safety-a-newcomers-first-look)
      - [Re-review the TODO's order after the outside reviews: priorities and grouping](#re-review-the-todos-order-after-the-outside-reviews-priorities-and-grouping)
      - [Know whether the browser will keep your library: a status light, what to do, and back up before you leave](#know-whether-the-browser-will-keep-your-library-a-status-light-what-to-do-and-back-up-before-you-leave)
      - [Keep your tabs and browsers in step: catch up quietly, never overwrite newer changes](#keep-your-tabs-and-browsers-in-step-catch-up-quietly-never-overwrite-newer-changes)
      - [Book details window: one Save — nothing changes until you click it, and nothing is lost without asking](#book-details-window-one-save--nothing-changes-until-you-click-it-and-nothing-is-lost-without-asking)
      - [Import from Relay keeps the books the cloud doesn't have — it never removes an owned book silently](#import-from-relay-keeps-the-books-the-cloud-doesnt-have-it-never-removes-an-owned-book-silently)
      - [The "Something went wrong" screen: when the app didn't load, say so — never recommend a reset](#the-something-went-wrong-screen-when-the-app-didnt-load-say-so-never-recommend-a-reset)
      - [A saved organization that can't be read is kept aside, never replaced at the next start](#a-saved-organization-that-cant-be-read-is-kept-aside-never-replaced-at-the-next-start)
      - [A save that fails part-way is undone, not kept — a failed Restore leaves no fragment](#a-save-that-fails-part-way-is-undone-not-kept-a-failed-restore-leaves-no-fragment)
      - [Restore Backup asks whenever there's an organization, and shows what it will replace](#restore-backup-asks-whenever-theres-an-organization-and-shows-what-it-will-replace)
      - [Words from outside never become code on Amazon's page: the fetchers' message boxes, and the key's shape](#words-from-outside-never-become-code-on-amazons-page-the-fetchers-message-boxes-and-the-keys-shape)
      - [A Cloud Sync Key never changes hands without asking: the bookmarklet stays on Amazon, keys arrive only when you say so](#a-cloud-sync-key-never-changes-hands-without-asking-the-bookmarklet-stays-on-amazon-keys-arrive-only-when-you-say-so)
      - [What can reach production: a fresh review of Amazon-page changes, a daily foreign-push check, a production token kept off the PC](#what-can-reach-production-a-fresh-review-of-amazon-page-changes-a-daily-foreign-push-check-a-production-token-kept-off-the-pc)
      - [A one-day truth-and-safety release: small things that are false or unsafe today](#a-one-day-truth-and-safety-release-small-things-that-are-false-or-unsafe-today)
      - [Fetcher work, in build order](#fetcher-work-in-build-order)
        - [Fetcher odds and ends (progress figure, frozen timer, request pacing)](#fetcher-odds-and-ends-progress-figure-frozen-timer-request-pacing)
        - [The fetchers' own logging: levels and codes, a log on Amazon's site, problems shown in Diagnostics](#the-fetchers-own-logging-levels-and-codes-a-log-on-amazons-site-problems-shown-in-diagnostics)
        - [Stop cleanly when Amazon asks for a human check mid-fetch](#stop-cleanly-when-amazon-asks-for-a-human-check-mid-fetch)
        - [When Amazon stops a fetch: tell Ron, and show people it's a known problem](#when-amazon-stops-a-fetch-tell-ron-and-show-people-its-a-known-problem)
        - [A fetch made with the demo filter on says so, and never marks books as gone](#a-fetch-made-with-the-demo-filter-on-says-so-and-never-marks-books-as-gone)
        - [Faster fetches that report exactly how your library compares with Amazon](#faster-fetches-that-report-exactly-how-your-library-compares-with-amazon)
        - [Fetcher: give the library filter one name, in one place](#fetcher-give-the-library-filter-one-name-in-one-place)
        - [Fetcher: refresh ratings with the price check (books you might buy)](#fetcher-refresh-ratings-with-the-price-check-books-you-might-buy)
        - [Wishlist: record the real format when a book is added](#wishlist-record-the-real-format-when-a-book-is-added)
        - [A long fetch resumes after an interruption (a first fetch, or a full refresh)](#a-long-fetch-resumes-after-an-interruption-a-first-fetch-or-a-full-refresh)
        - [Refresh all books from Amazon — a choice in the fetcher, which the app can pre-select](#refresh-all-books-from-amazon--a-choice-in-the-fetcher-which-the-app-can-pre-select)
        - [A fetch from someone else's Amazon account stops before mixing two libraries](#a-fetch-from-someone-elses-amazon-account-stops-before-mixing-two-libraries)
      - [Fetch should update books it already knows, not skip them](#fetch-should-update-books-it-already-knows-not-skip-them)
      - [Restore checks every book, folder and list inside a backup — skip a bad one and say so](#restore-checks-every-book-folder-and-list-inside-a-backup--skip-a-bad-one-and-say-so)
      - [One backup writer: Save Backup and the copy sent to the relay are built twice and already differ](#one-backup-writer-save-backup-and-the-copy-sent-to-the-relay-are-built-twice-and-already-differ)
      - [Restore from Cloud Sync: your books and organization back from your cloud library, no backup file needed](#restore-from-cloud-sync-your-books-and-organization-back-from-your-cloud-library-no-backup-file-needed)
      - [Lock the Cloud Sync Key in backups with an optional key password](#lock-the-cloud-sync-key-in-backups-with-an-optional-key-password)
      - [Relay worker: one release of changes (backup alerter, clearer daily email, strict ID check)](#relay-worker-one-release-of-changes-backup-alerter-clearer-daily-email-strict-id-check)
      - [Cloud Sync: rename Relay, show one Cloud Sync Key, and 'make a new key' retires the old one](#cloud-sync-rename-relay-show-one-cloud-sync-key-and-make-a-new-key-retires-the-old-one)
        - [An anti-glossary: the words we don't show people, kept in a list and enforced at every commit](#an-anti-glossary-the-words-we-dont-show-people-kept-in-a-list-and-enforced-at-every-commit)
        - [Relay Setup: smoother sections and clearer Esc / Help behavior](#relay-setup-smoother-sections-and-clearer-esc--help-behavior)
        - [Relay Setup: disconnect, or reset credentials](#relay-setup-disconnect-or-reset-credentials)
      - [Reset App: one honest message in all four places (what's cleared, what's kept, how to come back)](#reset-app-one-honest-message-in-all-four-places-whats-cleared-whats-kept-how-to-come-back)
        - [What a reset clears: four resets, four different lists](#what-a-reset-clears-four-resets-four-different-lists)
      - [Relay Setup's connection test checks the wrong relay on dev](#relay-setups-connection-test-checks-the-wrong-relay-on-dev)
      - [Say plainly what ReaderWrangler works with: US Amazon, Kindle, English, Chrome](#say-plainly-what-readerwrangler-works-with-us-amazon-kindle-english-chrome)
      - [Safari deletes a library after 7 days without a visit: warn, and help people restore](#safari-deletes-a-library-after-7-days-without-a-visit-warn-and-help-people-restore)
      - [Landing page: "Open My Library" for returning users, and "Always free · No ads · No account needed" under the start button](#landing-page-open-my-library-for-returning-users-and-always-free--no-ads--no-account-needed-under-the-start-button)
      - [The Security & Privacy page made specific, and a terms page: what we send where, what we promise](#the-security--privacy-page-made-specific-and-a-terms-page-what-we-send-where-what-we-promise)
      - [An accessibility page: what works, and how to tell us what doesn't](#an-accessibility-page-what-works-and-how-to-tell-us-what-doesnt)
      - [Outside code libraries: exact versions, integrity checks, and a policy that keeps the page from sending your key anywhere](#outside-code-libraries-exact-versions-integrity-checks-and-a-policy-that-keeps-the-page-from-sending-your-key-anywhere)
      - [Move to Cloudflare's $5/month plan around launch](#move-to-cloudflares-5month-plan-around-launch)
      - [Ron's accounts: a second sign-in step on GitHub (it now guards the site, Cloud Sync and email)](#rons-accounts-a-second-sign-in-step-on-github-it-now-guards-the-site-cloud-sync-and-email)
      - [Dark theme: fix the unreadable bar and the light strips](#dark-theme-fix-the-unreadable-bar-and-the-light-strips)
        - [Site pages use the shared named colors, so all four themes work (the security page's high-contrast light first)](#site-pages-use-the-shared-named-colors-so-all-four-themes-work-the-security-pages-high-contrast-light-first)
      - [User Guide: rewrite it around Searches, Book Lists and Folders, as a page you can reach from Help](#user-guide-rewrite-it-around-searches-book-lists-and-folders-as-a-page-you-can-reach-from-help)
        - [A glossary page on the site, built from GLOSSARY.md](#a-glossary-page-on-the-site-built-from-glossarymd)
      - [Remind me when my last backup is getting old](#remind-me-when-my-last-backup-is-getting-old)
      - [A public demo library from Amazon's best-seller lists (nothing personal)](#a-public-demo-library-from-amazons-best-seller-lists-nothing-personal)
      - [Screen capture pass: the sizzle reel, the landing page's before / after, README's old video](#screen-capture-pass-the-sizzle-reel-the-landing-pages-before--after-readmes-old-video)
      - [All the pre-launch data tests pass](#all-the-pre-launch-data-tests-pass)
    - [High priority](#high-priority)
      - [Honest ownership changes: buying, samples, loans](#honest-ownership-changes-buying-samples-loans)
        - [Buying a book that's in the Trash should bring it back](#buying-a-book-thats-in-the-trash-should-bring-it-back)
        - [Fetch summary should report books you bought](#fetch-summary-should-report-books-you-bought)
        - [Import summary: every ownership change by kind, kept in the message history](#import-summary-every-ownership-change-by-kind-kept-in-the-message-history)
      - [Series positions: one Position dialog, and one book at several positions (omnibus)](#series-positions-one-position-dialog-and-one-book-at-several-positions-omnibus)
      - [Rebuild the old-style message boxes as standard dialogs](#rebuild-the-old-style-message-boxes-as-standard-dialogs)
      - [Drag any dialog out of the way](#drag-any-dialog-out-of-the-way)
      - [Drag a box to select covers](#drag-a-box-to-select-covers)
      - [Every edit rewrites the whole library in storage](#every-edit-rewrites-the-whole-library-in-storage)
      - [Search improvements](#search-improvements)
        - [Find a book by its ASIN in the search box](#find-a-book-by-its-asin-in-the-search-box)
        - [Search everywhere without leaving the current folder](#search-everywhere-without-leaving-the-current-folder)
      - [Phone: show which test build is running](#phone-show-which-test-build-is-running)
      - [The left pane, one release](#the-left-pane-one-release)
        - [Book Lists and Searches: pin and sort them like Folders](#book-lists-and-searches-pin-and-sort-them-like-folders)
        - [A type-to-filter box for the left pane](#a-type-to-filter-box-for-the-left-pane)
        - [Jump-to-top / bottom buttons by the scrollbar, in both panes](#jump-to-top--bottom-buttons-by-the-scrollbar-in-both-panes)
      - [Everyday organizing](#everyday-organizing)
        - [Folder dragging: where you drop decides pinned, and the level](#folder-dragging-where-you-drop-decides-pinned-and-the-level)
        - [Stray double spaces in author names create duplicate authors](#stray-double-spaces-in-author-names-create-duplicate-authors)
      - [Tag from Collections, round 2: clearer window, safer tags (decided 2026-10-20)](#tag-from-collections-round-2-clearer-window-safer-tags-decided-2026-10-20)
    - [Polish](#polish)
      - [A saved setting that reads fine but holds nonsense inside — check each value, not just the note](#a-saved-setting-that-reads-fine-but-holds-nonsense-inside--check-each-value-not-just-the-note)
      - ["N now owned" after an import: a Show them button, and each column reads its date from one place](#n-now-owned-after-an-import-a-show-them-button-and-each-column-reads-its-date-from-one-place)
      - [Phone: Report a problem in the ⋮ menu, like the desktop's Help](#phone-report-a-problem-in-the--menu-like-the-desktops-help)
      - [Buttons name their action: replace the remaining OK, Yes and No buttons](#buttons-name-their-action-replace-the-remaining-ok-yes-and-no-buttons)
      - [Move and copy books anywhere — folders, Book Lists, All Books, Searches](#move-and-copy-books-anywhere--folders-book-lists-all-books-searches)
      - [Retire two leftover book fields: the hidden "seen" flag and the old price-goal field](#retire-two-leftover-book-fields-the-hidden-seen-flag-and-the-old-price-goal-field)
      - [Remove code left over from older versions (hiding single copies, phone tag shelves, unused functions)](#remove-code-left-over-from-older-versions-hiding-single-copies-phone-tag-shelves-unused-functions)
      - [Moving and selecting](#moving-and-selecting)
        - [Delete a book from All Books (removes it everywhere)](#delete-a-book-from-all-books-removes-it-everywhere)
        - [Open one book's details without losing a multi-selection](#open-one-books-details-without-losing-a-multi-selection)
        - [Restore the previous selection after a stray click or Select All](#restore-the-previous-selection-after-a-stray-click-or-select-all)
      - [A folder or Book List you just created stays visible under filters](#a-folder-or-book-list-you-just-created-stays-visible-under-filters)
      - [Tag lists and long lists, one release](#tag-lists-and-long-lists-one-release)
        - [Long lists keep their actions in view (Manage…, Select All) while you scroll](#long-lists-keep-their-actions-in-view-manage-select-all-while-you-scroll)
        - [One shared tag picker: show all tags in your order (the right-click one silently stops at 10)](#one-shared-tag-picker-show-all-tags-in-your-order-the-right-click-one-silently-stops-at-10)
        - [The "Save results" menu runs off the screen with many Book Lists](#the-save-results-menu-runs-off-the-screen-with-many-book-lists)
        - [Arrow keys should move through every type-ahead list](#arrow-keys-should-move-through-every-type-ahead-list)
      - [Finish keyboard accessibility](#finish-keyboard-accessibility)
      - [Removing a recent search should offer Undo](#removing-a-recent-search-should-offer-undo)
      - ["Bake this order into Manual" for a folder's books and a Book List, from the Sort menu](#bake-this-order-into-manual-for-a-folders-books-and-a-book-list-from-the-sort-menu)
      - [Small fixes](#small-fixes)
        - [A new message glides in from the old one's spot instead of appearing where you clicked](#a-new-message-glides-in-from-the-old-ones-spot-instead-of-appearing-where-you-clicked)
        - [Tidy up the notes](#tidy-up-the-notes)
        - [Leave the affiliate tag off Amazon links on the test rig](#leave-the-affiliate-tag-off-amazon-links-on-the-test-rig)
        - [Switch the affiliate tag to "readerwrangler-20"](#switch-the-affiliate-tag-to-readerwrangler-20)
        - [Tooltips where they help: icon-only, disabled, non-obvious, cut-off](#tooltips-where-they-help-icon-only-disabled-non-obvious-cut-off)
        - [Menus keep their items in place: disable, don't hide](#menus-keep-their-items-in-place-disable-dont-hide)
        - [A book's hover popup stays up after the book is deleted](#a-books-hover-popup-stays-up-after-the-book-is-deleted)
        - [The Trash ignores the search and filters](#the-trash-ignores-the-search-and-filters)
        - [Show only hidden books](#show-only-hidden-books)
        - [Right-click: add "Copy ASINs" below Copy Titles / Copy Authors](#right-click-add-copy-asins-below-copy-titles--copy-authors)
        - [Bulk Edit hints that read like "you can type several values"](#bulk-edit-hints-that-read-like-you-can-type-several-values)
        - [With a filter on, the right pane still shows subfolders with no matching books](#with-a-filter-on-the-right-pane-still-shows-subfolders-with-no-matching-books)
        - [A missing book description: one quiet line, on the computer and the phone](#a-missing-book-description-one-quiet-line-on-the-computer-and-the-phone)
        - [The phone's cover copies: still worth it? And why wasn't the browser's own cache enough?](#the-phones-cover-copies-still-worth-it-and-why-wasnt-the-browsers-own-cache-enough)
        - [Relay Setup's Test connection always checks the production relay](#relay-setups-test-connection-always-checks-the-production-relay)
        - [F2 follows the Delete key's rule: what's selected, where you're working, and words when it can't](#f2-follows-the-delete-keys-rule-whats-selected-where-youre-working-and-words-when-it-cant)
      - [Auto-Organize: Shift-click ranges should follow what you see](#auto-organize-shift-click-ranges-should-follow-what-you-see)
      - [Folder right-click menu: add Auto-Organize](#folder-right-click-menu-add-auto-organize)
      - [A refused Restore shows a false "Restore Warning" box a minute later](#a-refused-restore-shows-a-false-restore-warning-box-a-minute-later)
      - [Share Library: a copy of your library for a friend, without your Cloud Sync Key](#share-library-a-copy-of-your-library-for-a-friend-without-your-cloud-sync-key)
      - [Deleted folders go to the Trash, like books](#deleted-folders-go-to-the-trash-like-books)
      - [The Import's 30-second limit really stops the Import](#the-imports-30-second-limit-really-stops-the-import)
      - [An open tab learns that a new version of ReaderWrangler is out](#an-open-tab-learns-that-a-new-version-of-readerwrangler-is-out)
      - [Phone: remove "Save Credentials to File"](#phone-remove-save-credentials-to-file)
  - [🗄️ After launch](#after-launch)
    - [Speed](#speed)
      - [Clicking between books lags slightly while a filter is on](#clicking-between-books-lags-slightly-while-a-filter-is-on)
      - [Save only the changed book to this browser's book store](#save-only-the-changed-book-to-this-browsers-book-store)
    - [Relay and sync](#relay-and-sync)
      - [Edit Kindle collections from ReaderWrangler](#edit-kindle-collections-from-readerwrangler)
      - [Smaller organization syncs (send only what changed in your folders, tags and lists)](#smaller-organization-syncs-send-only-what-changed-in-your-folders-tags-and-lists)
      - [One copy instead of two: the Fetched Copy and the Complete Copy as one](#one-copy-instead-of-two-the-fetched-copy-and-the-complete-copy-as-one)
      - [Bookmarklet: when your key no longer works, say so plainly — and never show the Channel ID in an error](#bookmarklet-when-your-key-no-longer-works-say-so-plainly--and-never-show-the-channel-id-in-an-error)
      - [Edits travel between computers: newest edit wins, per field](#edits-travel-between-computers-newest-edit-wins-per-field)
    - [Features](#features)
      - [Build the support assistant (custom GPT)](#build-the-support-assistant-custom-gpt)
      - ["Read in Kindle": open a book in the Kindle app or Cloud Reader](#read-in-kindle-open-a-book-in-the-kindle-app-or-cloud-reader)
      - [Amazon's official catalog API: prices, titles and covers without a bookmarklet, once eligible](#amazons-official-catalog-api-prices-titles-and-covers-without-a-bookmarklet-once-eligible)
      - [Book recommendations: similar books you own, and ones you don't have yet](#book-recommendations-similar-books-you-own-and-ones-you-dont-have-yet)
      - [Show who a book is shared with (Family Library)](#show-who-a-book-is-shared-with-family-library)
      - [Two-pane split view](#two-pane-split-view)
      - [Library statistics: your unread pile, books per year, top authors and series](#library-statistics-your-unread-pile-books-per-year-top-authors-and-series)
      - [Import book details from a list or spreadsheet; Goodreads / StoryGraph files in and out](#import-book-details-from-a-list-or-spreadsheet-goodreads--storygraph-files-in-and-out)
      - [Capture book ideas from your phone (Share → ReaderWrangler)](#capture-book-ideas-from-your-phone-share--readerwrangler)
      - [Notice when a Kindle edition appears for a print-only book](#notice-when-a-kindle-edition-appears-for-a-print-only-book)
      - [Phone: change Book Lists and tags](#phone-change-book-lists-and-tags)
    - [Technical clean-up](#technical-clean-up)
      - [A hand-over guide: how anyone can run ReaderWrangler on their own accounts](#a-hand-over-guide-how-anyone-can-run-readerwrangler-on-their-own-accounts)
      - [Split the main code file into modules](#split-the-main-code-file-into-modules)
      - [Test on Safari and iPhone](#test-on-safari-and-iphone)
      - [Our working names in the code and docs: Fetched Copy, Complete Copy, compact view, full view](#our-working-names-in-the-code-and-docs-fetched-copy-complete-copy-compact-view-full-view)
      - [Tests and tools run under a venv named for its Python, called by its path](#tests-and-tools-run-under-a-venv-named-for-its-python-called-by-its-path)
      - [A "machine's trouble" that repeats the same way, run alone, says it's probably not the machine](#a-machines-trouble-that-repeats-the-same-way-run-alone-says-its-probably-not-the-machine)
  - [👀 Watching](#watching)
    - [Turn more of our working rules into automatic checks (my tooling)](#turn-more-of-our-working-rules-into-automatic-checks-my-tooling)
    - [Generated test libraries: made-up books at any size, with their own covers](#generated-test-libraries-made-up-books-at-any-size-with-their-own-covers)
    - [Receipts reach the screen: one screen test per area, not only the log](#receipts-reach-the-screen-one-screen-test-per-area-not-only-the-log)
    - [Undo history sometimes empties by itself](#undo-history-sometimes-empties-by-itself)
    - [Find out why some books end up in no folder](#find-out-why-some-books-end-up-in-no-folder)
    - [A screen test that failed once: the File menu not found after the start-up test](#a-screen-test-that-failed-once-the-file-menu-not-found-after-the-start-up-test)
    - [A screen test that failed once: the logging script not loaded at start-up (Diagnostics)](#a-screen-test-that-failed-once-the-logging-script-not-loaded-at-start-up-diagnostics)
    - [A screen test that failed once: Reset's reload hung while a commit ran alongside](#a-screen-test-that-failed-once-resets-reload-hung-while-a-commit-ran-alongside)
    - [A screen test that failed once: ENV-006 named the wrong trouble on a squeezed PC](#a-screen-test-that-failed-once-env-006-named-the-wrong-trouble-on-a-squeezed-pc)
    - [Books just bought weren't at the top of All Books sorted by Date Added — once, not reproduced](#books-just-bought-werent-at-the-top-of-all-books-sorted-by-date-added--once-not-reproduced)
    - [Resend's email limits](#resends-email-limits)
  - [🧊 Someday](#someday)
    - [Formats other than Kindle: undo my Kindle-only preference](#formats-other-than-kindle-undo-my-kindle-only-preference)
    - [Find out whether reading progress can be fetched from Amazon](#find-out-whether-reading-progress-can-be-fetched-from-amazon)
    - [Support stores besides Amazon](#support-stores-besides-amazon)
    - [Several people on one installation](#several-people-on-one-installation)
    - [Animated drag-and-drop](#animated-drag-and-drop)
    - [Share a filtered, read-only copy of your library](#share-a-filtered-read-only-copy-of-your-library)

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

**The order is the order below — the top task in the launch gate is next**, then down the list: **the launch gate**,
then **High priority**, then **Polish**. The table of contents shows it (Ron, 2026-11-10: the table of contents is how
the order is read, so the tasks themselves sit in that order; a separate "order of work" list drifted). To change the
order, move the task.

### 🚦 The launch gate — target: January 2027

**Why a gate:** launching means strangers trust ReaderWrangler with their library. This gate is what must be true
first; everything else (the sections after it) is the project continuing after launch, as a retirement project should.
(Ron, 2026-11-19, after a cold review of this TODO — `.private/TODO-REVIEW-2026-11-19-REPORT.md`. Target January 2027:
Ron's call, for the timing of his own income that year.)

**Ready to launch means all four** (the review's definition, Ron agreed 2026-11-19):
1. **A stranger can't lose data by ordinary use** — a second tab, someone else's Amazon account, the browser clearing
   its storage, a fetch cut off part-way.
2. **Nothing public is false** — the site, the README, the guide, the landing page.
3. **The service survives a day of sign-ups** — the relay's plan and limits.
4. **The legal and disclosure basics exist** — a privacy page; what the app sends where; the affiliate notice.

**Law 23 applies inside these tasks:** several of them still plan a permanent commit check as part of the work (a
color check, a build-stamp check, an unpinned-script check, a guide-name check…). None is built unless its task first
states Law 23's three numbers — how often the failure happened, what it cost, what the check will cost to keep. (The
one with an earned case — a name used before it is defined — uses ESLint's ready-made rule, not a hand-written one.)

**Ron's hands are the scarce resource:** the fetcher work needs his Amazon account for testing, every relay deploy
needs his yes, the sizzle reel needs his taste, the outside reviews need his judgment — plan those into one or two
sprints rather than scatter them.

#### Outside reviews before building: launch risks, security, data safety, a newcomer's first look
<!-- id 20261023-1239 -->

_Why it matters:_ The one outside review we ran (Cloud Sync naming, 2026-10-23) broke our convergence on a weaker name,
predicted a checksum gap the test then confirmed, designed the safe order for retiring a key, and caught two false
claims of mine. Decisions made inside our long conversation can't see their own anchoring — and these four are the
expensive ones to get wrong after launch, so they go ahead of nearly all other work (Ron, 2026-10-23).

**The reviews, in this order** (an earlier one can change what a later one should look at): **review 1 alone first**
(it could reorder the backlog — Ron rules on it before the rest), **then 2, 3 and 4 at the same time** — they look at
different things (Ron, 2026-11-19). Each brief is read by Ron before its review runs (Ron, 2026-11-19).

**Review 1 done (2026-11-20):** the report and our decisions on each of its points are kept with the TODO notes. What
it changed here: new items in "A one-day truth-and-safety release", "Fetcher odds and ends", "Stop cleanly when Amazon
asks for a human check", "Relay worker: one release of changes" and "Move to Cloudflare's $5/month plan"; new tasks
"When Amazon stops a fetch: tell Ron, and show people it's a known problem", "Safari deletes a library after 7 days
without a visit: warn, and help people restore", "An accessibility page" and "Ron's accounts: a second sign-in step on
GitHub"; the privacy task became "The Security & Privacy page made specific, and a terms page"; a hand-over guide
(After launch); Resend's email limits (Watching).

1. **Launch risks we haven't thought of** — first, because it could reorder the backlog. Seeds: Amazon's terms for a
   tool that reads your Amazon pages (**start from the existing terms-and-strategy note — see TODO notes**; it predates
   the relay, so the review weighs it against today's architecture; and other companies that connect to people's
   Kindle libraries are precedent worth studying — see TODO notes; and **writing back** — "Edit Kindle collections from
   ReaderWrangler" would be the first feature to change a user's Amazon account, a bigger step than reading: weigh it
   explicitly); the Amazon Associates rules for the affiliate tag (a visible disclosure is
   required; self-purchases are a known pitfall); a privacy policy (including GoatCounter and the sync server's
   last-used date per cloud library — disclosed together, Ron 2026-11-04); Cloudflare's free-tier
   limits as users grow; **book covers on camera** (the sizzle reel and screenshots show real covers — Ron: fair use as
   he sees it, risk accepted, 2026-11-04); **iPhone at launch, or not** (every iPhone browser is Safari underneath — "Test on Safari and
   iPhone", 2026-11-04); support load with one person — including **a support inbox** (Resend Inboxes, announced
   2026-10: an address on our own domain, threads, agents connect through MCP; free up to 3 inboxes) that Claude
   sorts, drafts replies in for Ron to approve and send, and mines into the help notes. Needs web research.
2. **Security and privacy as a whole** — the relay design, the security page's claims, revoke / wipe, the
   bookmarklet's trust in Amazon's page. Two weaknesses turned up by accident during a rename; a dedicated look will
   likely find more.
3. **Data safety: "can a user ever lose their organization?"** — Save / Restore, merging, integrity repairs, undo.
   The pre-launch data tests check what we thought of; this attacks what we didn't.
4. **A newcomer's first look** — the landing page (including the hero button's words and the line under it — Before
   launch task "Landing page: 'Open My Library'…"), the setup steps, the User Guide's *outline* (its text gets a second
   look when it's written). The nearest substitute for the cold testers we don't have. **Weigh our setup against
   one-step imports** (2026-10-30): Readwise Books (an ebook store + reading app, invite-only beta Oct 2026) imports a
   Kindle library with "Connect your Kindle account"; RW needs a bookmarklet dragged to the bar plus Cloud Sync setup.
   We won't copy their way (it needs a server and accounts — our no-account design is deliberate), but a newcomer will
   compare: find the steps we can remove or merge. **Also try Impeccable** (2026-10-31; pbakaus/impeccable — design
   commands plus a 62-check detector for the tell-tale signs of AI-built pages): run its `critique` and `audit` on the
   site pages (index, features, tutorials) and judge it by what it finds; not its "bolder / delight / overdrive"
   commands — Ron is the designer. Read any skill fully before installing it (a skill is instructions that run with
   Claude's permissions).
(A fifth, "the big designs decided in conversation, before they're built" — "Move and copy books anywhere" — moved
into that task, 2026-11-19 (Ron): it isn't needed for launch, so its review runs when that task comes up.)

**How each runs** (decided Ron + Claude, 2026-10-23)
1. **I write a brief for a cold reader** — background, problems, constraints, questions; none of my verdicts. (Model:
   docs/design/CLOUD-SYNC-NAMING.md as first written.)
2. **A fresh agent, model Fable 5.1 at the highest effort** (Ron: "or whatever is the highest model and mode for
   toughest challenges"), its only input the brief, in **two phases**: (a) a cold answer from the brief alone, written
   down first; (b) then a check against the code and docs — each claim verified, and what changed in its view and why.
   Phase (a) keeps the independence that made the outside review valuable; (b) fixes the reviewer's blind spot (all four
   of Claude.ai's errors were facts about our code it couldn't see).
3. **Its report is saved as a file beside the brief** — Amazon-related parts in the TODO notes, not the public repo.
4. **I spot-check its code claims, then bring Ron a digest with my verdicts.** Ron decides; decided items get the
   anti-bounce rule (only evidence — a real user's misreading, a failing test — reopens them).
5. Claude.ai stays an option for a second opinion from outside our tools, when a verdict looks too comfortable.
6. **A progress file, and checks from outside** (Ron, 2026-11-22, after reviews 2–4 started without one): every brief
   asks the reviewer to add a dated line to a progress file beside its report at each step ("Phase 1 written",
   "reading the relay", "experiment 2 done") — for how far along it is. Staying within bounds is **not** judged from
   it — that's the reviewer reporting on itself. At each reviewer's finish, before its report is trusted: no project
   file changed but its own (git, in the project and the private notes), nothing it started still running, and the
   next nightly relay summary shows no writes it could have made.
7. **After the last outside review (review 4): re-review the TODO's ORDER** — its own task, right after this one:
   "Re-review the TODO's order after the outside reviews".

#### Re-review the TODO's order after the outside reviews: priorities and grouping
<!-- id 20261125-1435 -->

_Why it matters:_ Four outside reviews have filed and moved a lot of work. Before building resumes, the order should
reflect what we now know — and work that touches the same files, screens or stored formats should be grouped, so it
is done once instead of twice.

**Decided** (Ron, 2026-11-25 — asked as its own task, right after the outside reviews):
1. **Right after review 4.** Not another look at every item — just the ORDER: do the priorities still look right?
2. **Grouping:** which tasks share files, screens or stored formats (the cloud library's formats, the empty-library
   screen, Restore, the bookmarklet…) and should be built together.
3. **It settles "Restore from Cloud Sync"'s place** (Ron: "fairly high now" — the better recovery for every loss,
   outside review 3 Q7).
4. Proposed to Ron as a reordered list with the reasons; the order is his (Claude never reorders on its own).

#### Know whether the browser will keep your library: a status light, what to do, and back up before you leave
<!-- id 20261124-1330 -->

_Why it matters:_ By default a browser may delete a site's data **without asking** when the disk runs low, or when all
sites together pass what it will use (Chrome: 80% of the disk). It deletes the **least recently used site first, all
of its data at once** (MDN, "Storage quotas and eviction criteria", read 2026-11-24). A site the browser has agreed to
keep ("persistent") is skipped. A budget laptop with a 256 GB SSD that fills up, and a ReaderWrangler not opened for a
while, is the case — rare by Chrome's own research ("data is very rarely cleared automatically"), but the loss is total
for anyone without a backup. Today the app never asks, and never says. (Ron, 2026-11-24: "THAT IS A BIG DANGER.")

**The facts it rests on** (MDN; web.dev "Persistent storage", read 2026-11-24):
- The app can **check without any prompt** whether the browser keeps its data (`navigator.storage.persisted()`), and
  **ask** (`persist()`). Chrome and Edge decide by themselves, no prompt — the signals they name *include* how much the
  site is used, whether it is **bookmarked** or **installed** (as an app), and whether it may **show notifications**;
  a "no" can be asked again later and is judged again. **Firefox asks the person** with a popup. Safari decides by
  itself from "the user's history of interaction with the site".
- A newcomer will usually get "no" at first — the browser judges by history with the site.
- Deleting isn't tied to closing a tab; it happens when space runs short, least recently used site first. While you
  work, ReaderWrangler is the **most** recently used site, so every other site's data would go before it — the sound
  advice is "your work is safe while you work; Save Backup before you leave". (No source says an open site is never
  deleted; this is the order the sources give.)
- **Not covered by "keep":** a private window (truth-and-safety item 17); Safari deletes a site's data after 7 days
  of Safari use without visiting it, kept or not (MDN states no exemption) — in Safari, back up always, until "Restore
  from Cloud Sync" can bring the organization back (TODO "Safari deletes a library…"); someone clearing their own
  browsing data.

**Decided** (Ron, 2026-11-24 — high priority; replaces truth-and-safety item 3):
1. **A status light**, always visible in the status area: **green** = the browser keeps ReaderWrangler's data; **red**
   = it hasn't agreed yet. The app checks at start and after the person does something that may change the answer.
2. **Red, clicked → what it means and what to do,** plainly: *"Your browser hasn't agreed to keep ReaderWrangler's data
   yet. Until it does, it could delete it if your disk runs low. Your work is safe while you work — Save Backup before
   you leave."* Then **how to convince the browser**, per browser: Chrome / Edge — bookmark ReaderWrangler, or install it
   as an app, and keep using it; Firefox — answer **Allow** when it asks; then **Check again** (asks once more). Wording
   is Ron's at build time (GLOSSARY first).
3. **No blocking** (Law 18): organizing stays open while the light is red — a newcomer is red on day one. Instead, a
   **Save Backup reminder** that comes back while the light is red, and "back up before you leave" in the explanation.
4. **Ask at the right moment** (from item 3): `persist()` once there is a library worth keeping (after the first
   Import), again after a bookmark/install, never in a loop.
5. Words that promise the data is kept (index.html "Your data stays in your browser", the security page, the guide)
   are checked against this — truth-and-safety's job.
6. **An empty library may be a deleted one — in every browser** (Ron, 2026-11-24; moved from the Safari task, item 2,
   which was Safari-only): a browser that deletes a site to free space deletes ALL of it at once — books, organization
   and the Cloud Sync Key — so today the app shows the plain Welcome screen of a brand-new user (only a books-only
   loss gets the "your folders and lists are intact" screen, readerwrangler.js ~9923). The empty-library screen adds:
   *"If you've used ReaderWrangler in this browser before, your browser may have cleared it — restore your backup
   file"*; once "Restore from Cloud Sync" exists, that first.
   **And the books-only screen stops over-promising** (Ron, 2026-11-25, outside review 3 Q7): *"…bring your books back
   and everything falls into place"* is untrue for your own fields — Import from Relay brings the books back without
   their tags, ratings, notes and price goals (the reviewer's experiment: all 0). Say they come back only from a
   backup file (and, once built, from Restore from Cloud Sync).
7. **The bookmarklet is the breadcrumb — in every browser** (moved from the Safari task, item 3): it lives in your
   bookmarks, not in the site's storage, so it survives the deletion. Its "open ReaderWrangler" button adds a mark
   (after `#`) saying "this person has a bookmarklet" — never the key. An empty library plus that mark = the library
   was lost, for certain: say so plainly, with the restore buttons. And the bookmarklet can hand the key back (TODO
   "Restore from Cloud Sync", item 7).

#### Keep your tabs and browsers in step: catch up quietly, never overwrite newer changes
<!-- id 20260830-0000; merged 20260922-0000d -->

_Why it matters:_ A copy of ReaderWrangler working from an old state overwrites newer work — today, in two ways. Two
**tabs** share one browser's storage, and one innocent edit in an out-of-date tab writes its whole old organization
over everything done since it loaded (a real data-loss risk). Two **browsers or computers** on one Cloud Sync each
keep their own folders, which drift apart while nobody is told — and whichever sends last overwrites the Complete Copy
the phone shows. At launch the second case is ordinary, not a clever-user trick: plenty of people have a laptop and
a desktop.

**What you'd get**
- Every tab and every browser stays editable and keeps up with your latest changes on its own. Come back to one that
  is behind and it catches up: *"Caught up with changes from your other tab / browser"*, with **Undo**.
- Nothing ever overwrites a newer change. In the rare case both copies changed since they last matched, a banner (not
  a window — you keep working) offers **Use the other one's** / **Keep this one's**.

**Status**
- **Before launch — the tab half is "Tier 0", the real data-loss risk;** the cross-browser half comes second within
  this task. Its priority is weighed by outside review 3 (data safety) — it may move ahead of other Before-launch work.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review — merged from "Protect against editing in two tabs at once"
and "Warn when another browser has newer changes"; both earlier designs re-read through Law 18)
1. **One problem, one mechanism.** The four states are the same everywhere — in sync, behind, ahead, both changed:
   1. Each saved copy of the organization carries a version stamp (the saved organization already carries
      `savedAt`).
   2. **Compare before you overwrite**, at both places it's written: this browser's storage and the Complete Copy. A
      write says "I'm replacing the version I last saw"; if it has changed since, the write is refused.
   3. A refused write, or a newer copy noticed, gets the same responses everywhere: **behind with no changes of its
      own → catch up silently + toast + Undo; ahead or in sync → nothing; both changed → the banner**, and this copy
      sends nothing to the cloud until you choose.
2. **Only two things differ by place:**
   - **Tabs** hear at once, for free — the browser tells every other tab when stored data changes, and the app saves
     the organization on every change — and catch up by reloading from storage.
   - **Browsers** hear when you come back to one (one small read of the Complete Copy's version — the phone's freshness
     check already makes it) or when the cloud refuses a send, and catch up by taking the Complete Copy, which writes
     their storage — which brings their other tabs along. The layers stack.
   - **The phone page is one more browser, not an exception** (Ron, 2026-11-22, outside review 3 item 8). Its local
     save of the Complete Copy (mobile.js, the guest guard) follows the same rule — never replace a version you haven't
     seen — instead of today's newer-clock-wins comparison. Today, the phone page opening on a computer (a window
     under 768 pixels) can save another computer's newer copy over this one's library, silently. A phone that later
     writes ("Phone: change Book Lists and tags") is a writer under the same rule — the same copy, no special case.
   - **How the cloud enforces it: a Durable Object per cloud library holds its copies' pointers** (Ron + Claude, 2026-11-22,
     outside review 3 item 10 — Ron's design): compare-and-swap on the pointer; the parts stay in KV; the older
     version deleted ~10 minutes after it's replaced; the same object holds the exact write counter and the write key.
     **The design lives in `docs/design/MULTI-INSTANCE.md` §4 ("How the cloud enforces it — the pointer keeper"),
     drawn step by step in `docs/design/RELAY-FLOWS.html`, the Proposed group (P0–P4)** — moved there 2026-11-23.
   - **The relay itself can't skip, repeat or roll back** (Ron + Claude, 2026-11-26, outside review 2 item 9, choice 4):
     the combined copy's list of uploads already combined moves inside the encryption (so the relay can't make an
     Import skip an upload or combine one twice — an old reset combined again throws away everything since), and each
     computer remembers the newest version it has seen and refuses an older one. Built with the pointer keeper — the
     same rebuild of how versions are recorded.
3. **This retires both earlier designs' gatekeepers** — the read-only second tab (with "Edit here instead") and the
   cross-browser "soft lease" with its 15–30-second check. Neither blocks you any more, and the lease's record would
   have cost a cloud write every 15–30 seconds per active user (about 120 an hour, against ~1,000 a day on
   Cloudflare's free plan). Compare-before-overwrite costs no extra writes.
4. **Kept from the tab design: ❄ Freeze.** A tab can be frozen as a reference snapshot ("Frozen at 6:04 PM") — it
   stops catching up, and a frozen tab doesn't edit or send. Resume = catch up.
5. **Duplicate sends:** a tab sends to the cloud only when the stored version differs from the last one sent (recorded
   in the shared storage), so two in-step tabs don't both send as you leave them.
6. **Taking the Complete Copy is the real work** — the desktop has never applied one; today it reads the cloud
   organization only in the connection test (readerwrangler.js ~1845).
7. **Tested with the browser driver:** two real tabs (edit in A; B catches up with the toast; Undo; nothing lost; one
   send), then two throwaway browsers on one test channel (edit in A, return to B → caught up; edit both → banner,
   and no overwrite either way).
8. **Not a goal: live two-way sync** (two machines editing at once, merged) — rejected 2026-09-22: it needs push
   infrastructure and a merge engine for folders, the case where a merge bug silently corrupts everything. One person
   moves between machines; catching up at the switch is the need.

**Still to decide when building**
1. **Undo after catching up:** the tab's older undo steps refer to the state before the other copy's changes — undoing
   one then must not bring old state back. Lean: catching up starts a fresh undo history in that tab, with the
   catch-up itself as its one step. Check against docs/design/UNDO-MODEL.md first.
2. **Mid-gesture:** a tab in the middle of a drag, or with the book details window open, catches up when that ends.
3. **Books live in a second store** (written whole, apart from the organization): the compare must cover it too, or
   one stamp covers both.
4. **Dragging between tabs** stops being dangerous (both tabs are current) — allow it or not? Decided in "Two-pane split
   view" (2026-11-03): try two windows side by side first, including drag between them; build the in-app split only if
   that falls short.

**How (technical)**
- Tabs: the `storage` event (or BroadcastChannel) for the notice; a compare against the stored `savedAt` before each
  organization write. Cloud: an optional "expect" generation on the device-state pointer flip
  (relay/relay-worker.js `handlePutPointer`, ~812) — the worker refuses with 409 if the pointer has moved; the
  return check reads `getDeviceStatePointerGen`. Cloudflare's storage takes up to about a minute to agree everywhere,
  so this is a guard for one person moving between machines, not a lock. The worker part rides a relay release (Ron's
  yes before each deploy).
- Model the four states as one state machine, not flags.
- Design: docs/design/MULTI-INSTANCE.md §4 (rewritten 2026-11-02; the old §6 folded into it).


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

#### Import from Relay keeps the books the cloud doesn't have — it never removes an owned book silently
<!-- id 20261125-1430 -->

_Why it matters:_ An Import from Relay keeps only the books the Fetched Copy holds, plus wishlist books it lacks — so
every **owned** book the Fetched Copy doesn't hold is removed from this browser, with its own fields and its places in
folders, under the message "No new books found". No undo. Ways in: a new or different Cloud Sync Key, a first fetch cut
short, a Restore Backup on a second computer — and certain for anyone who makes a new key and adds a wishlist book
before fetching the library. Outside review 3, ranked item 3 (one of its two silent, total losses); checked in our code
2026-11-22 (`storage.js` 142-155).

**Decided** (Ron + Claude, 2026-11-22, outside review 3 — agreed that day, filed 2026-11-25)
1. **Keep the books the incoming set doesn't have**, as wishlist books already are kept; remove a book only when a
   deletion letter (tombstone) names it.
2. **Say it in the Import's message:** how many books the cloud didn't have (kept).
3. No question needed. **Before launch, and before "make a new key"** ships (it makes the case ordinary).
4. Test first: an Import whose Fetched Copy lacks an owned book keeps it, its fields and its folder places.

#### The "Something went wrong" screen: when the app didn't load, say so — never recommend a reset
<!-- id 20261125-1431 -->

_Why it matters:_ When the app's code simply didn't download (a dropped connection, a blocked script), the screen
recommends a reset — naming damaged data as the cause, and a reset erases everything in this browser. Many people will
see this screen sooner or later; some will follow it. Outside review 3, ranked item 4; checked 2026-11-22
(`readerwrangler.html` ~359).

**Decided** (Ron + Claude, 2026-11-22, outside review 3 — agreed that day, filed 2026-11-25)
1. **A script failed to load →** *"ReaderWrangler couldn't load — check your connection and reload"*, with no reset
   button.
2. **The app really broke →** put **"Save my data to a file first"** above Reset — a small page script that writes out
   the saved items and the book store, needing no app.
3. Wording is Ron's (GLOSSARY first). The planned reset-message task covers the words; this covers the cause.

#### A saved organization that can't be read is kept aside, never replaced at the next start
<!-- id 20261125-1432 -->

_Why it matters:_ When the saved organization can't be read, or has another shape (an older tab or page meeting a newer
format — the version 4 page was one), the next start replaces it: every folder, Book List, Search and the tag list, with
one box at most. Outside review 3, ranked item 6 (the reviewer's finding — not re-checked by me).

**Decided** (Ron + Claude, 2026-11-22, outside review 3 — agreed that day, filed 2026-11-25)
1. **Before anything is saved, copy the text that couldn't be used** to a second item under another name.
2. **While books exist and no folder list was found, keep saving closed** and say: *"don't save a backup — restore one,
   or send us this"* (Report a problem).
3. Before launch. Check the reviewer's paths in the code first.

#### A save that fails part-way is undone, not kept — a failed Restore leaves no fragment
<!-- id 20261125-1433 -->

_Why it matters:_ If writing the books fails part-way (a bad record), what was written so far is kept — part of the
library, and those books' places in folders, lost; the two boxes shown don't say anything was lost. Outside review 3,
ranked item 7 (the reviewer's finding — not re-checked by me).

**Decided** (Ron + Claude, 2026-11-22, outside review 3 — agreed that day, filed 2026-11-25)
1. **In the one save** (`storage.js` ~264-270), cancel the whole write on any error while adding books.
2. Then "Restore checks every book, folder and list inside a backup…" (already planned) refuses the bad record up front.
3. Before launch. Test first: a save with one bad record leaves the book store exactly as before.

#### Restore Backup asks whenever there's an organization, and shows what it will replace
<!-- id 20261125-1434 -->

_Why it matters:_ Restore Backup is what a person in trouble reaches for, and it reaches further than its question
shows: it replaces whatever is newer than the backup, and on a second computer its reset can lead to books removed at
the next Import (see "Import from Relay keeps the books the cloud doesn't have…"). Outside review 3, ranked item 9 (the
reviewer's finding — not re-checked by me).

**Decided** (Ron + Claude, 2026-11-22, outside review 3 — agreed that day, filed 2026-11-25)
1. **Ask whenever an organization exists**, not only when books do.
2. **Show the counts** — now and in the backup: books, folders, Book Lists, Searches — so the person sees what changes.
3. **Later:** keep one automatic copy of what a Restore replaces (until the next Restore).
4. Before launch for the question and counts; the automatic copy can follow. Wording is Ron's.

#### Words from outside never become code on Amazon's page: the fetchers' message boxes, and the key's shape
<!-- id 20261125-1600 -->

_Why it matters:_ The five fetchers run inside your signed-in Amazon page, where the bookmarklet also places your Cloud
Sync Key. The app itself is React, which shows every string as text; the fetchers' message boxes build HTML by hand, so
outside words placed in them are followed as instructions — including "run this code". Three ways in (outside review 2,
item 2; all checked in our code 2026-11-25): (1) the relay's reply to a failed request goes into the error message the
boxes show (`relay-client.js:673`) — a taken-over relay could run code on every fetcher user's Amazon page; (2) Amazon's
own page text — a series name, a title — goes into messages (e.g. `amazon-wishlist-fetcher.js:709`); (3) the key's two
values are stored unchecked (`readerwrangler.js:1930`) and pasted between quote marks into the bookmarklet's own code
(`:6163`) — a crafted key, from a stranger's backup file, runs at every click. Each unlikely; each the worst outcome
there is.

**Decided** (Ron, 2026-11-25, outside review 2 item 2 — before launch):
1. **The four older fetchers** (Download Library, Download Collections, Add Book to Wishlist, Add Series to Wishlist)
   show outside words in their message boxes **as text** — the `escapeHtml` the newest (Add Bibliography to Wishlist)
   already has, or `textContent`.
2. **A commit check** (Ron's word given 2026-11-25 — it touches `git-hooks/`) refuses pasting a variable into HTML in
   any file that runs on Amazon's page, so it can't come back.
3. **Refuse a key that isn't the expected shape** at every way in — typed, Load credentials from backup file, Restore
   Backup, the phone link. (Escaping isn't enough: the browser undoes it before running a bookmarklet.)
4. **Then correct `SECURITY.md`**: "a taken-over relay sees only encrypted blobs" becomes true only once (1) is fixed.
5. Tests first: a relay reply, a series name and a key value each carrying markup or a quote mark; nothing runs.

#### A Cloud Sync Key never changes hands without asking: the bookmarklet stays on Amazon, keys arrive only when you say so
<!-- id 20261125-1620 -->

_Why it matters:_ The Cloud Sync Key opens your cloud library — whoever has it can read and change your books and
organization. Outside review 2, item 3 (all checked in our code 2026-11-25): (1) **taking yours** — the bookmarklet's
first act, on whatever page it is clicked, is to place the key on that page, before anything checks where it is: a wrong
tab, or a page built to ask for the click, gets the key; (2) **giving you theirs, silently** — so your library and
organization then sync to a cloud library someone else can read: **Restore Backup** of someone else's file in a browser
that has no key yet (with a different key already here it asks — since 7.14.3, `readerwrangler.js` ~6251); **Load
credentials from backup file** (`:11829`, no question); **the phone pairing link** (`mobile.js` 2419-2435) — no
question, and it REPLACES a key already there; the compact view also opens in a computer window under 768 pixels, so a
link opened there swaps the computer's key, and the status light stays green.

**Decided** (Ron, 2026-11-25, outside review 2 item 3):
1. **The bookmarklet works only on Amazon's pages and ReaderWrangler's own** (the empty-page key hand-back needs
   ReaderWrangler's) — its very first statement checks; anywhere else it only offers to go to Amazon. **Built into the
   same new bookmarklet as the Cloud Sync rename** (Ron, 2026-11-25: grouped — that release already makes everyone drag
   a new one; changing the bookmarklet later means every user dragging again).
2. **Always ask before a key arrives** from Restore Backup into a key-less browser, Load credentials from backup file,
   or the phone link — with the support code: *"Use the Cloud Sync Key in this file (support code …7Q2K9)? It replaces
   yours."* The same "never adopted silently" rule as the bookmarklet hand-back (TODO "Restore from Cloud Sync", item
   7).
3. **The QR code carries the key as text, not a link** — it can't be forwarded and opened as a link.
4. Shares the key-shape check of "Words from outside never become code on Amazon's page…", item 3.
5. Before launch. Wording is Ron's (GLOSSARY first).

#### What can reach production: a fresh review of Amazon-page changes, a daily foreign-push check, a production token kept off the PC
<!-- id 20261126-1135 -->

_Why it matters:_ Nine files run inside every user's signed-in Amazon page — the bookmarklet's menu
(`bookmarklet-nav-hub.js`), the five fetchers, and three sync files (`relay-client.js`, `relay-crypto.js`,
`relay-compress.js`) — plus the one line in the app that writes the bookmarklet (`readerwrangler.js` ~6163). A change to
any of them reaches every user within ten minutes of a production push. Outside review 2, item 7: the PC and the agent
are part of that chain — Git's credential manager holds a token that can push to both repositories (anything running as
Ron could use it; the 2025 npm worm scanned for exactly such tokens), the agent writes the code and reads web pages, and
nothing reviews what changes in those nine files before they go live.

**Decided** (Ron, 2026-11-26, outside review 2 item 7):
1. **A fresh reviewer at "push to prod"** — when any of the nine files (or the bookmarklet line) changed since the last
   release, a separate agent, started cold, reads their diff against the CHANGELOG and the release commit message (which
   lists the changed files — Ron's idea; the user-facing CHANGELOG stays free of file names) and says whether every
   change has a stated reason. Not the agent that wrote it (Law 12). Releases that don't touch them pass straight
   through. Enforcement code (`.claude/`) — Ron's word given.
2. **A daily foreign-push check at session start** — `tools/sync_remotes.py` already reports what is "only there" on a
   remote; run it with the nightly relay check and say plainly if either repository holds a commit we didn't make.
3. **A production token kept off the PC** — try GitHub's fine-grained tokens: a dev token (pushes to the dev repository
   only) stored as today; a prod token (production repository only) NOT stored by Git, pasted at each production push.
   Find a low-friction way: Git's own sign-in window, or one ready-made command Ron runs in VS Code's terminal (the
   agent's commands have no keyboard). Where the prod token lives: **1st choice LastPass** (copy, paste); **2nd choice a
   Logitech keyboard macro** (plain text in Logitech's settings — not where token-scanning worms look, not labelled as a
   token; add a couple of decoys). Each production push request reminds Ron of the key combination / LastPass entry.
   Defeats the automated token-stealing worms; not a patient attacker already on the PC (nothing short of a separate
   machine does). Before launch.
4. **Install scripts off for the whole PC** (`ignore-scripts`, Ron's user npm setting — Ron: "YES"): the 2025 worm
   spread through scripts that run when a package installs. Apply it, then re-run each install here (`tools/build`,
   `relay`) and the full tests, and give a package that truly needs its script a one-line exception. Protects Ron's
   other projects too. Plus: update tools deliberately, preferring versions a few weeks old.
5. **The relay checks what the site serves — daily, low priority**: once a night with the summary, fetch the nine files
   as readerwrangler.com serves them and compare them with fingerprints the release stored ON THE RELAY (never read from
   GitHub — someone who changed the files could change those too); email only on a difference. Catches tampering that
   never went through us. Low priority now the domain is verified.
Dropped: an email on every push to production (Ron: noise he'd ignore); Ron reading diffs himself ("You write the
code… I trust you" — the fresh reviewer replaces it).

#### A one-day truth-and-safety release: small things that are false or unsafe today
<!-- id 20261119-1548 -->

_Why it matters:_ Each is small, and each is either untrue on the public site today or can quietly cost a person their
library. Found or confirmed by the cold review of this TODO (2026-11-19), every one checked in the code that day.

**Decided** (Ron agreed the review's list, 2026-11-19)
1. **"Tested browsers: Chrome, Edge, Firefox. Safari is untested."** (README.md and features.html) — only Chrome is
   tested (the screen tests run Chrome). Say what's true now; "Say plainly what ReaderWrangler works with" does the
   full pass later.
2. ✅ **Done in 7.31.1** (2026-11-22/25). **Remove the old version 4 app from the site** — it shares your library's storage (Polish → Small fixes, "Remove
   the old version 4 app from the site — it shares your library's storage": that item, built here).
3. **Moved 2026-11-24 to its own task, high in the launch gate** — "Know whether the browser will keep your library…"
   (Ron: "a BIG DANGER"). Was: **Ask the browser to keep the library's storage** (`navigator.storage.persist()`) — never asked today, so the
   browser may clear it when the disk is short (and Safari clears a site after 7 days unvisited). For anyone who never
   saved a backup, that is the whole organization. Ask once, at the right moment; say plainly if the browser says no.
   Not in the TODO before 2026-11-19.
4. **Hidden books start hidden.** A fresh browser (or after a Restore) starts with Show Hidden ticked
   (`showHidden: true // v4.8.0`, readerwrangler.js ~7119) — so what you hid shows. (Small fixes → "Show only hidden
   books", its item 3 "Settle the real default".)
5. **Reset's words** — a person resetting is told to "Use the Export button", which doesn't exist (the full rewrite is
   "Reset App: one honest message in all four places", below in this gate).
6. **Relay Setup's connection test is hard-wired to the production relay** (readerwrangler.js ~1953) — use the relay
   the app is set to ("Relay Setup's connection test checks the wrong relay on dev", below in this gate, item 1–2 only;
   its planned commit check falls under Law 23).
7. **Switch the affiliate tag to the app's own, "readerwrangler-20"** (Ron, 2026-11-19: before launch, so launch
   traffic is counted separately from his WordPress articles from day one) — the Polish → Small fixes item "Switch the
   affiliate tag to 'readerwrangler-20'", built here. It earns nothing by itself; only clicks do.

**Added by outside review 1** (Ron, 2026-11-20)
8. **README says the domain is at FreeDNS** — it's at Porkbun.
9. **"No cloud storage, no tracking"** — untrue since Cloud Sync and the visit counter; say what's true.
10. **features.html's "the only tool…"** — drop the claim (Ron: "hyperbole but we can change it anyway").
11. **security.txt expires 2026-12-31** (`.well-known/security.txt`) — set it six months ahead; the relay's reminder
    email keeps it current from then on ("Relay worker: one release of changes", item 14).
12. **"Not created or endorsed by Amazon"** in the app's About, as the site pages already say.
13. **The LICENSE's "Affiliate Attribution Condition"** puts Ron's tag on sites not listed in his Associates account
    (which its rules forbid). Replace it: public hosting needs Ron's written permission; **except** that if
    readerwrangler.com has been unavailable for 90 days, anyone may host a copy with their own services (so the app can
    outlive Ron). The Commons Clause stays. Ron's word on the exact wording first.
14. **The affiliate disclosure on the phone** — one line on the phone's book details screen, where the cover and the
    title open Amazon (mobile.js ~2103, ~2128); the phone has the links but no disclosure today.
15. **Ron's own purchases untagged** — Polish → Small fixes, "Leave the affiliate tag off Amazon links on the test rig"
    (widened 2026-11-20 to any browser Ron uses), built here: Associates pays nothing on your own purchases.
16. **Cloud Sync's description says how long your organization is kept** (outside review 3, item 10; Ron
    2026-11-22) — wherever Cloud Sync is described (the glossary's "your cloud library", Cloud Sync Setup, the security
    page, the guide): *"your organization is kept for 90 days after your last change; Save Backup is your backup."*
    Today "a backup of your books and organization" overstates it: the Complete Copy keeps two versions minutes apart
    and expires 90 days after the last send.
17. **Say that a private window throws the library away** (outside review 3, item 12.5; Ron 2026-11-24) — one
    sentence, always shown, no detection (browsers hide private mode on purpose; guessing is worse than saying it
    plainly): the Welcome screen, the User Guide, SUPPORT-KB. *"Your library is kept in this browser. A private window
    (Chrome's Incognito mode, Edge's InPrivate) throws it away when you close it — use a normal window, and Save Backup
    now and then."* Ron's rule: name each browser's own term, not only "private window". A Save Backup made in the
    private window survives it (Restore Backup brings everything back). **When "Know whether the browser will keep your library…" is built, update this sentence.**
    Note for item 3 (to check when building — not verified): Chrome may quietly answer "no" for any site not yet used
    much, so "say plainly if the browser says no" could reach every newcomer — time or word it so it doesn't.

#### Fetcher work, in build order

The fetchers (the bookmarklet's scripts on Amazon's pages) had about a dozen tasks spread over five
sections, though they depend on each other — the human-check stop needs the shared request wrapper, faster fetches
and the ownership batch share one completion window, resume and refresh are the same long run. Gathered 2026-11-04
(TODO scan, Ron + Claude) like the worker release: one build order, and fewer separate test rounds on Amazon (each
one a chance to trip its human check).

**Before launch (the launch gate, 2026-11-19):** "A fetch from someone else's Amazon account stops before mixing two
libraries" goes FIRST — it needs no wrapper (it reads the account name on the page) and its mix can't be undone; then
steps 1–3 and 6 below (a stranger's first hour). Steps 4–5 ("Faster fetches…", "Honest ownership changes…") can follow
launch.

**Build order**
1. The shared Amazon request wrapper — "Fetcher odds and ends…", item 3; then "The fetchers' own logging…" (its comb
   then sorts one wrapper's lines instead of many copies, and every later fetcher change leaves a trace).
2. "Stop cleanly when Amazon asks for a human check mid-fetch" — lives in that wrapper.
3. The "partial fetch" label — "A fetch made with the demo filter on says so…" (resume's stages use it too).
4. "Faster fetches that report exactly how your library compares with Amazon", with its riders: odds-and-ends items
   1–2, "Fetcher: give the library filter one name…", "Fetcher: refresh ratings with the price check…",
   "Wishlist: record the real format…".
5. "Honest ownership changes: buying, samples, loans" (the group right after this one) — its fetch summary shares
   step 4's completion window.
6. "A long fetch resumes after an interruption", then "Refresh all books from Amazon" (the same long run; its
   request note is in "Relay worker: one release…", item 8).
7. "A fetch from someone else's Amazon account stops before mixing two libraries".
- Stays elsewhere: "Bookmarklet: when your key no longer works…" (After launch).


##### Fetcher odds and ends (progress figure, frozen timer, request pacing)
<!-- id 20260903-0000a -->

_Why it matters:_ Small fetcher fixes that are each too minor to stand alone.

**The list**
1. Fix the "772%" figure in the details-filled ratio. (Seen again 2026-11-20: "Successfully enriched: 78/3
   (2600.00%)" — the count includes older books filled in that run, the divisor only the new ones,
   amazon-library-fetcher.js ~1942 / ~2723.)
2. The elapsed time freezes during the "Checking Relay" (both lines) and "Recovering" phases — it only repaints when the phase or progress changes. (Ron, 2026-09-03, twice.)
3. **One shared Amazon request wrapper for every fetcher** (corrected 2026-11-04 in the TODO scan — the pacing itself
   already exists: since 7.0.1 (2026-08-27) `amazonFetch` keeps a minimum gap of ~350 ms between request STARTS,
   set just below the measured round trip so it costs nothing today. But it's **copied into 3 fetchers** (library,
   collections, series), and the **bibliography fetcher bypasses it** with direct requests (`win.fetch`,
   author-bibliography-fetcher.js ~361 / ~396); the wishlist fetcher reads the page and makes none.) What's left —
   the decisions of 2026-10-22 (Ron + UX), still standing:
   1. **One copy, in one shared file the bookmarklet hub loads before any fetcher**; every fetcher uses it — a start
      gap across EVERY request to Amazon, whichever fetcher sends it.
   2. **Make bypassing it impossible:** inside OUR fetcher scripts `fetch` / `XMLHttpRequest` are shadowed by a local
      that throws *"Requests to Amazon go through amazonFetch"*; `amazonFetch` keeps the real one. **Never override the
      page's own `window.fetch`** (the page is Amazon's). Plus **a commit check** refusing a direct request in the
      fetcher files (it also catches an explicit `window.fetch`, and paths a test run never reached).
   3. **Visible if the floor ever waits** (Ron: "an excellent addition") — Amazon got faster than when we measured:
      say so in the fetch summary or console ("paced N requests to the safe rate").
   4. **Re-measure the floor** in one normal full fetch and write where the number came from beside the constant.
   5. It's also where the human-check stop lives ("Stop cleanly when Amazon asks for a human check mid-fetch").
   6. **Name ourselves to Amazon** (outside review 1, Ron 2026-11-20): every request carries
      `x-agent: Agent/ReaderWrangler`. Amazon's Conditions of Use ask software acting for a person to name itself;
      Chrome won't let a page change the User-Agent line itself, so this header is as close as a bookmarklet gets — the
      public explanation says so. **Tested by Ron 2026-11-20:** one request, then a whole library update plus the
      check for removed books, with the header on every request — all answered normally.
   7. **Drop the ±10% wobble** on the floor (`0.9 + Math.random() * 0.2`) — a fixed floor (Ron: "not much of a
      disguise. Drop it."). Amazon's terms ask agents not to imitate human timing.
4. **The collections fetcher's finish message names a file it no longer writes** (found 2026-11-11 by a sweep for
   amazon-library.json): it uploads to the relay (its console says so), then shows *"Updated amazon-library.json with N
   books' collections"* (amazon-collections-fetcher.js ~866, its `FILENAME` constant; the header comment's steps
   describe the old file too). Say what happened: the collections were sent to Cloud Sync. The wishlist and series
   fetchers only define the old name (`LIBRARY_FILENAME`, never used) — remove it ("Remove code left over…").

**Decided** (Ron + UX, 2026-10-22): items 1–2 as listed (the "772%" ratio can't exceed 100% — fix the formula; the
elapsed time redraws on a one-second tick while a fetch runs). **Item 3 comes first in "Fetcher work, in build
order"**; items 1–2 ride with "Faster fetches…" — same file, same test, and that task already rebuilds the timing
table.

**How (technical)**
- Item 3: `MIN_REQUEST_INTERVAL_MS` + `amazonFetch` (amazon-library-fetcher.js ~41–49; copies in the collections and
  series fetchers ~31); the collections fetcher still carries an unused `FETCH_DELAY_MS = 0` (~51). (Two items moved out 2026-10-20: the live ownership-upgrade test is now in "Fetch should
  update books it already knows", un-trash on upgrade is "Buying a book that's in the Trash should bring it back".)

##### The fetchers' own logging: levels and codes, a log on Amazon's site, problems shown in Diagnostics
<!-- id 20261110-1043 -->

_Why it matters:_ Since 7.26.0 every message in the app has a level, an area and a code, and lands in a kept log that
the Diagnostics window shows. The fetchers and the bookmarklet menu still print plain console lines on Amazon's pages,
where nobody is looking — so a fetch that went wrong leaves no trace support can read.

**Decided** (Ron + Claude, 2026-11-05 / 11-09 — moved here from "One logging module…", item 10, when the module
shipped; design of record docs/design/LOGGING.md §2b and §5 step 5.5)
1. **Their own comb**, like the app's: the fetchers' and bookmarklet menu's ~140 error and ~18 warning lines (counted
   2026-11-04) each get a level, an area and (warning and above) a code — or go as noise. **Published for Ron's red
   pen before any is switched.** Their ~430 progress lines stay: the step-by-step trail of a fetch support needs.
2. **The same two switches, stored on Amazon's site** (whose storage is separate from ours): set from the console, or
   a toggle in the bookmarklet menu's developer mode.
3. **Two logs, never the relay** (LOGGING.md §2b): the fetchers keep theirs on amazon.com; a fetch's warnings and
   errors ride inside its existing upload (no extra relay writes), and the app's Diagnostics window shows them as
   their own group, *"From your last fetch (date)"* — not mixed in by time, so two computers' clocks never need to
   agree (2026-11-09).
4. **The same cleaning:** no full Channel ID or passphrase in anything kept or shown — the app's form is logger.js
   `shortChannelId` (first 8 … last 4). The fetchers don't load logger.js (they do load relay-client.js), so how they
   share that one function is open — decide it with "Bookmarklet: when your key no longer works…", which needs it too.

**When:** right after the shared Amazon request wrapper (this group's build order, step 1).

##### Stop cleanly when Amazon asks for a human check mid-fetch
<!-- id 20261014-1030au -->

_Why it matters:_ Today it shows confusing errors instead of saying what to do.

**What you'd get**
- When Amazon interrupts a fetch with an "are you human?" check, the fetcher stops and says: *"Amazon is asking you to
  confirm you're human. Open any Amazon page, complete the check, then run the bookmarklet again. Nothing in your
  library was changed."* (wording revised 2026-11-02 — "nothing was changed" is what a worried person needs most).
- That last clause is literally true since 7.0: an unfinished run is never committed.

**Status**
- The start of a fetch is already guarded; this covers a check appearing **partway through**. Never seen yet — cheap insurance before launch. (From an outside review, item 7.)

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **Detect it in the ONE Amazon wrapper**, `amazonFetch` ("Fetcher odds and ends (progress figure, frozen timer,
   request pacing)", item 3 — every Amazon request goes through it, the fetcher scripts' own `fetch` disabled) — not in
   each fetcher's retry path. Every fetcher gets it, including later ones. Built right after that wrapper (this
   group's step 2).
2. **The long runs are the likeliest to trip it** — a new user's first big fetch, and "Refresh all books from Amazon".
   Seen 2026-11-03: Ron got a check after a few quick searches in Amazon's own search bar (not from our requests) — the
   first one he's ever had; quick repeated requests are what trips it, so pacing in `amazonFetch` matters.
   Once "A long fetch resumes after an interruption" exists, the message becomes "…then run it
   again — it continues where it stopped".

3. **Stop at Amazon's first refusal, whatever kind** (outside review 1, Ron 2026-11-20): a human check, a "too many
   requests" answer, an access refusal — the fetch stops there and never retries past it, and never touches a check
   itself. (Ordinary network hiccups keep their retries; a refusal is Amazon saying no.) Amazon's Conditions of Use ask
   agents not to bypass its checks.

**How (technical)**
- In `amazonFetch`, recognize check-shaped answers: HTML where JSON was expected, a validate-captcha redirect, a robot-check 503.

##### When Amazon stops a fetch: tell Ron, and show people it's a known problem
<!-- id 20261120-1700 -->

_Why it matters:_ If Amazon changes something or starts refusing the bookmarklet, every user hits it at once — and
today Ron would hear only if someone writes in, while each person thinks it's their own fault (outside review 1,
Risk 8 and Question 4; Ron, 2026-11-20).

**Decided** (Ron + Claude, 2026-11-20)
1. **Tell Ron:** when a fetch stops on a refusal or an answer it doesn't understand, the fetcher sends a GoatCounter
   event (as it already does for some failures, e.g. `fetch-phase0-endpoint-fail`) **and** asks the relay to email Ron
   — the bookmarklet can't hold Resend's key, so the relay sends it ("Relay worker: one release of changes", item 15),
   **at most one email a day per kind of problem**, so nobody can flood Ron's inbox through it.
2. **Tell people:** a "known problems" line on the site that the app (and the bookmarklet's stop message) shows when a
   fetch stops — so a person sees "Amazon changed something on <date>; we're working on it" instead of guessing. Ron
   updates it by hand.
3. **One sentence before a fetch** (outside review 1, Risk 8): what the bookmarklet does on Amazon's page, in the
   person's name — so a later Amazon question isn't a surprise. Ron's word on the wording first.

**When:** with "Stop cleanly when Amazon asks for a human check mid-fetch" (just above) — the same stop.

##### A fetch made with the demo filter on says so, and never marks books as gone
<!-- id 20261014-1030be -->

_Why it matters:_ A demo filter left on (it's used to record tutorials) makes a fetch send only a few dozen books.
Since 7.19 a fetch missing books flags them "no longer in your Amazon library" — so a forgotten filter would flag
~3,200 books as gone from Amazon and ask you to review them. Nothing is lost (Keep exists), but it's alarming and
wrong.

**What it does today** (checked 2026-11-01)
- The demo filter is a browser setting on Amazon's site (`readerwrangler-demo-whitelist-enabled` + its list), turned
  on by `tools/demo-library/demo-whitelist-loader.js` (moved from `tutorials/work-products/demo-library/` 2026-11-02); the library and collections fetchers then send
  only the listed books. Nothing in the shipped code turns it on — the old "no demo setting can ship" guarantee already
  holds by construction.

**Decided** (Ron + Claude, 2026-11-01, in the TODO review — Law 18: a stopping prompt is a block in a polite coat)
1. **The fetcher labels a filtered fetch** ("demo fetch" — a partial fetch). The app then never concludes from it that
   books left Amazon, and the import receipt says so: *"Demo fetch: 40 books (the demo filter is on) — nothing else
   changed."* A fact, not a guess from the size.
2. **A banner you can't miss in the fetcher while the filter is on** (the point of effect, Law 16).
3. **No "much smaller upload — are you sure?" confirmation.** For the demo case the label is better; for any other
   shrunken fetch (Amazon returning half a library), the 7.19 removed-books review is already the safety net — nothing
   is deleted, you're asked.
4. Build it with, or before, the screen capture pass (the launch gate) — that's when the demo filter gets used.
5. **The label is shared** with "A long fetch resumes after an interruption" (its stages are partial fetches too) —
   one "partial fetch" label, one rule in the app: never infer removals from a fetch that says it's partial.

**How (technical)**
- Old review item 6f; the demo setting is the "demo whitelist" (amazon-library-fetcher.js ~104 / ~995 / ~1662;
  amazon-collections-fetcher.js ~56). The "no longer in your Amazon library" inference: readerwrangler.js ~194 / ~5670
  (docs/design/ORPHAN-CLEANUP.md §2).

##### Faster fetches that report exactly how your library compares with Amazon
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

##### Fetcher: refresh ratings with the price check (books you might buy)
<!-- id 20261014-1030af -->

_Why it matters:_ Ratings are frozen at a book's first fetch — fine for owned books, a little stale for buying
decisions.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review — was "Now and then, refresh ratings for books you might buy",
After launch → Prices; moved here as a small fetcher change to ride along with the next one)
- **Ride along with the price check — no schedule.** The price step already asks Amazon about exactly these books on
  every fetch (books you could still buy, new books, owned books with a price goal — 30 per request, since 5.1). Add the
  rating and review count to that same request: ratings stay fresh on every fetch with **no extra requests** — no
  monthly sweep, no every-Nth-fetch counter. Safe to interrupt for free (the same run).
- Not the outside review's per-book adaptive timing — a fine solution to a scale problem we don't have.

**How (technical)**
- amazon-library-fetcher.js price step (`qvGetMediaMatrixProductsQuickView`, ~2316): add `customerReviewsSummary
  { rating { value } count { displayString } }` (as the enrichment request already asks, ~1482); store `rating` /
  `reviewCount` as the first fetch does (~1617). Bump FETCHER_VERSION. (Outside review item 3.)

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

##### A long fetch resumes after an interruption (a first fetch, or a full refresh)
<!-- id 20260821-0000 -->

_Why it matters:_ A 3,000-book fetch that dies near the end starts over from scratch — a new user's first fetch, and
now also every "Refresh all books from Amazon" run, the likeliest to trip Amazon's human check partway through.

**What happens**
- A long fetch fills in details for ~3,000 books with no resume point. If it dies at book 2,800, it starts over.

**What you'd get**
- The fetch sends its progress in stages, so a re-run skips what's already done. 7.0's upload design makes this natural.

**Status**
- (From the 2026-08-21 outside review, item 1.) Priority raised 2026-11-02 — it no longer "hits each user exactly
  once": "Refresh all books" makes long runs repeatable, and the human-check stop's message ("…it continues where it
  stopped") depends on this.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **Each stage says it's partial** — the same "partial fetch" label as "A fetch made with the demo filter on says so,
   and never marks books as gone". One concept, one label: a fetch that knows it's incomplete says so, and the app never
   concludes from it that books left Amazon. The final stage completes the set.
2. **Mind the write budget:** progress saved every few hundred books (≈ 6–8 stages for 3,000), not per book — every
   stage costs relay writes against the account's shared 1,000 a day.
3. **One cluster:** this, "Refresh all books from Amazon", and "Stop cleanly when Amazon asks for a human check
   mid-fetch" — all built on the `amazonFetch` wrapper — built together or back to back.

**How (technical)**
- Send enrichment progress as mailbox letters in stages, so a resumed run's skip-hint already knows what's done.

##### Refresh all books from Amazon — a choice in the fetcher, which the app can pre-select
<!-- id 20261014-1030 -->

_Why it matters:_ Fetches are incremental — they build on the books the Fetched Copy already holds, and only re-read
deeper when the counts disagree with Amazon. So book details that went stale or wrong (a cover, rating, description,
series Amazon later corrected — or a damaged record) are never re-read. Today the only way out is clearing the Fetched
Copy with the browser's developer tools. (Not a clean restart — that's Tools → Reset App, plus the Danger zone wipe for
the cloud library.)

**Decided** (Ron + Claude, 2026-11-01, in the TODO review)
1. **Name:** "Refresh all books from Amazon" — plain and exact. Not "integrity" (the app's integrity check is a
   different thing) and not "scan and fix" (it touches only book details from Amazon, never folders, tags or anything
   you organized).
2. **Delete nothing first.** The run re-reads every book (ignoring what the fetcher already knows) and imports like any
   fetch; a refresh that fails halfway leaves the old copy intact. (Law 18's explicit-verb rule — not destroy-then-
   rebuild.)
3. **The control lives in the fetcher; the app can pre-select it** (Ron): under "Send Library to ReaderWrangler", **☐
   Refresh every book (slower)** with a tooltip on when to use it ("if book details look wrong or out of date"). From
   the app, **Tools → Refresh all books from Amazon…** explains it and *requests* the refresh — the next fetch's box then
   starts ticked, with "requested in ReaderWrangler on <date>". Either side can override.
4. **When the request clears:** only after a refresh **finishes successfully** — a failure keeps it pending. Unticking
   in the fetcher means "not this time" (it says "Full refresh still pending — it'll be offered next time"); cancelling
   for good is done in the app (Cancel request).
5. **The pending state is never invisible** (Law 16): while waiting, the menu item reads "Refresh all books from
   Amazon… (requested — runs on your next fetch)". If a fetch arrives after the request and it's still pending, the app
   says so — "Your last fetch (<date>) didn't include the full refresh — it's still pending" (unticked, or an older
   bookmarklet). The import's fetch date is the evidence; no second "the fetcher knows this feature" flag needed.
6. **How they talk** — the app and the fetcher run on different sites and share no browser data; they share the cloud
   copy. The request is a **small note on the relay**: written by the app (encrypted with the key, a signed write),
   read by the fetcher at its start (one small extra read), deleted by the fetcher after a successful refresh (signed).
   Not inside the library copy (re-uploading it to flip a flag), not in device-state (~17 MB to read one flag), not a
   mailbox upload (those flow bookmarklet → app). **Build it as the general "requests from the app to the bookmarklet"
   channel** (2026-11-02) — this refresh request is its first user; "Edit Kindle collections from ReaderWrangler" (if it
   ever happens) would be another. One mechanism, not two.
7. **Ships in two independent parts** (Ron): the relay's small note route goes early — in "Relay worker: one release of
   changes" (idle until used; the signed-writes gate covers it). Then the app + fetcher together (they go out in the
   same push anyway); each fails safe — a fetcher that can't read the note just fetches normally, an app that can't
   write it says the refresh isn't available yet.
8. The library fetch only — collections are re-read in full each time (confirm when building). Same Amazon pacing
   (`amazonFetch`). **Pair it with "A long fetch resumes after an interruption"** — a full refresh of
   3,000+ books is that same long run.

**How (technical)**
- Old review item 6g. The fetcher's incremental start: `loadKnownBooks` (relay-client.js); the automatic fuller pass
  when counts disagree: SUPPORT-KB §14 item 3.

##### A fetch from someone else's Amazon account stops before mixing two libraries
<!-- id 20261103-1525 -->

_Why it matters:_ Nothing checks whose Amazon account a fetch comes from. On a shared computer, someone signed in to
*their* Amazon account who clicks *your* bookmarklet (it carries your Cloud Sync key) sends their books into your
library — and the fetch, comparing your library with "their" Amazon account, can flag your books as removed. Undo
doesn't reach that.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review — split out of "Several people on one installation")
1. **The library remembers which Amazon account it belongs to** (set on its first fetch). Amazon's pages already ask for
   the signed-in account's name, so the fetcher reads it with no extra request (Amazon's side: see TODO notes).
2. **A fetch from a different account stops before sending anything** and says plainly: *"You're signed in to Amazon as
   Dana, but this library belongs to Ron. Fetching would mix two people's books."* — with an escape for the rare real
   case: **"It's the same person — continue"**. A stopping prompt, which Law 18 normally rules out — justified here
   because the damage can't be undone (Ron, 2026-11-03).
3. **Same rule as the demo-filter task above:** a fetch that didn't see your real library never marks books as gone.
4. The better answer for a household: one browser profile per person (see "Several people on one installation").
5. **The same account name can guard Restore** (2026-11-04): a backup carrying "belongs to Dana" lets Restore say
   *"This backup belongs to Dana — restoring replaces your library."* before replacing anything.
6. **Where "the library remembers" lives** (Ron + Claude, 2026-11-23, outside review 3 item 11): the fetcher runs on
   Amazon's page and sees only your cloud library, never this browser's storage — so the owner's account name is stored
   **in the Fetched Copy** (encrypted like the rest) and in backups (item 5). A stored-format change: a design Ron sees
   first.
7. **The first fetch after this ships** (Ron + Claude, 2026-11-23): existing libraries have no owner recorded yet. If
   that first fetch were Dana's, the library would adopt Dana and then refuse its real owner. So when a library that
   already has books gets its owner set for the first time, ask once: *"This library will be marked as belonging to
   Dana — is that you?"* One question per library, ever.


#### Fetch should update books it already knows, not skip them
<!-- id 20260904-0000a; merged 20261014-1030ac -->

**Before launch (the launch gate, Ron 2026-11-19):** split out of "Honest ownership changes" — without it, a re-fetch leaves a book that changed kind (a sample you then bought, a loan returned) showing what's no longer true. The rest of that batch (the summaries) stays in High priority.

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

#### Restore checks every book, folder and list inside a backup — skip a bad one and say so
<!-- id 20261108-1800a -->

_Why it matters:_ Since 7.26.0 Restore checks that a backup has every part it needs, each of the right kind — but not
what's inside them. One book with no ID, a folder with no list of books, or a Search with no position can still crash
the restore part-way or leave a broken library.

**Found** (2026-11-08): each book needs an ID (its ASIN — the app's book ID is the ASIN; a book without one, or two
with the same, break the folders that hold them); each folder an ID, a name, a parent and a list of books; each Book
List an ID, a name and a list of books; each Search an ID and a number position (the restore computes
`Math.max` over the positions — a missing one makes it NaN); each tag-list entry a name.

**To decide first:** skip or refuse. Law 18 (don't block the user) says one bad book out of 3,000 shouldn't refuse
the whole backup. Claude's verdict: restore everything else, skip the bad items and say so with their titles —
*"Restored 3,295 books; skipped 1 that had no ID: 'Title'"* — and let the folders' integrity check tidy after it;
refuse only when what's left is unusable (Ron's rule for the parts, 2026-11-08: "if that makes it unusable, we reject
it"). The skipped items go in the log (BACKUP area), so support can see them.

**How:** the same one checking function as the parts check (backupCheck.js, 7.26.0), extended to the items, with its
function tests written first.

#### One backup writer: Save Backup and the copy sent to the relay are built twice and already differ
<!-- id 20261108-1800b -->

**In the launch gate (Ron, 2026-11-19):** built first — the restore from Cloud Sync below needs one way of building a backup.

_Why it matters:_ The backup file and the copy sent to the relay and the phone hold the same library, but each is put
together by its own code — and they already disagree: the Complete Copy carries the folder-list order (Manual / Name;
`folderListSort`) and when it was saved; the backup has neither, so a restore onto a new computer can't bring the
folder order back. Every new field has to be remembered twice (Law 4: two answers to one question).

**Found** (2026-11-08): `buildDeviceStatePayload` (readerwrangler.js ~6146, the relay and phone copy) and Save
Backup's own builder (~6271) each write `books`, `organization`, `collections`; a comment says the first is "shared
with exportBackup", but Save Backup builds its own. Differences: the Complete Copy has `savedAt` and
`explorerSettings.folderListSort`; Save Backup has `exportDate`, `theme`, `appVersion` and the Cloud Sync
credentials.

**How**
1. One builder; Save Backup adds only what a file needs (the credentials, the save date) and the Complete Copy only what
   it needs (`savedAt`).
2. The folder-list order joins the view settings it belongs to (a restore onto a computer with books keeps the view
   here — Ron, 2026-11-08: "restore changes organization, not views").
3. Then "Remove code left over from older versions…" (Polish) drops the dead parts from the one writer.
4. Test: a Save Backup → Restore round trip and a relay round trip produce the same organization.
5. **Build the backup from storage, not the screen** (medium — Ron, 2026-11-09). Save Backup reads the books from the
   book store but the folders, Book Lists and tags from what's on screen. When the start fails AFTER the books are
   readable (the organization store is never written by a failed start — F1), the screen is empty but storage still
   holds the whole library: a backup built from storage would be complete, one from the screen is missing its folders
   — and since 7.26.0 a restore from it gives exactly that. 7.26.0 refuses Save Backup until the library has loaded
   (the guard); with this, "save a backup now" becomes safe advice even after a failed start, and BOOT-01's critical box
   can say so again. Normally the screen and storage agree (the organization is saved on every change) — check that
   nothing pending is lost (a change still on its way to storage).

#### Restore from Cloud Sync: your books and organization back from your cloud library, no backup file needed
<!-- id 20261109-1700 -->

**In the launch gate (Ron, 2026-11-19):** a stranger who clears their browser data, or loses a computer with no recent backup, would otherwise lose all their organizing — while a full copy sits in the cloud.

_Why it matters:_ The worst case — a lost or wiped computer and no recent backup file — already has its cure sitting in
the cloud. With Cloud Sync on, the computer sends the relay the phone's copy (the code's "device-state") a few seconds
after each change: the whole library AND the organization (folders, Book Lists, Searches, tags), in a backup's shape. But
nothing on the computer reads it back; Import from Relay merges only the books the fetcher sent.

**Decided** (Ron + Claude, 2026-11-09)
1. **One restore, two readers.** A file reader and a relay reader each turn their source into the same backup-shaped
   data; from there ONE path — the backup check (backupCheck.js), the "restore?" box, the restore itself
   (performRestore / loadLibrary) — that can't tell where the data came from.
2. **Credentials:** the Complete Copy carries none, and needs none — reaching the relay already took yours. The restore
   keeps the current ones (as a backup file without credentials does).
3. **The new computer:** once built, the app tells the person that any backup FILE made since their current credentials
   were created brings them back — File → Relay Setup → Credentials → "Load credentials from backup file" (the label says
   "backup file" since 7.26.0, so it can't be mistaken for this).
4. **Two computers on one Cloud Sync:** the restore brings back whichever sent last — expected, no special handling
   (Ron).
5. **Until this is built, every recovery message offers only the backup file** (Ron: one option until then). When it's
   built, "Reset App: one honest message in all four places" (the launch gate) offers it as the second way
   back. The menu: one item, "Restore…", asking "from a backup file / from Cloud Sync" only when Cloud Sync is set up —
   otherwise straight to the file box (Claude's UX verdict; Ron to confirm when it's built).
- How current: as of the last send (seconds); a change made in the moments before a crash may be missing — say so in
  the "restore?" box ("your cloud library from 2 minutes ago").
6. **After a reset: one choice, and the cloud library held until it's made** (Ron + Claude, 2026-11-11, building
   7.27.1's reset words). What happens today, checked in the code: the reset itself sends nothing, and nothing is sent
   while the library is empty (the device-state push skips `books.length === 0`) — but as soon as books are back (a
   fetch + Import from Relay, which brings books without folders) any change sends a **full** copy (no deltas: every
   push is a whole new generation) that replaces the cloud's Complete Copy, the one with the folders; the relay keeps two, so one more
   push and the old organization is gone from the cloud. Decided:
   - **The first time the app opens after ANY reset** (Tools → Reset App, the emergency screen, the reset page, the
     phone — each sets one "just reset" mark), it asks once: *"You've reset ReaderWrangler. Bring your library back?
     [Restore from Cloud Sync] [Restore backup file…] [Start fresh]"* — the natural moment ("what next?"), part of the
     person's own action; "Start fresh" covers the early-days restart.
   - **Until a choice is made, nothing is sent to the cloud** — so the cloud library is guaranteed intact when they choose
     to restore from it. Closing the box keeps the hold and asks again next time.
   - **One case of a general rule** (Ron, 2026-11-22, outside review 3 item 10): the "just reset" mark is one case
     of "never replace a version you haven't seen" ("Keep your tabs and browsers in step") — which also covers a
     cleared browser, a new computer given the key by hand, and books brought back by a fetch without their folders.
   - **Ships with this task**, not before (Ron): until a restore from the cloud exists, the cloud library isn't a way back,
     so there's nothing to hold for — and a hold with no cloud restore to offer is a confusing mode. (The
     backup-file-only version of the choice could ship earlier on its own — Ron: wait; logged here.)
   - **Turned down:** a "last chance" prompt at the first push that would overwrite the cloud (it interrupts 60 s after
     an unrelated change or on leaving the tab — "a stopping prompt is still a block", Law 18 — and asks about a reset
     that may be an hour old).
7. **After the browser deleted everything, the key must come back first** (Ron, 2026-11-24 — a gap: item 2 assumed the
   key is still here). A browser that deletes a site to free space deletes the Cloud Sync Key with the library, so the
   restore first gets the key back, three ways: **typed in**; **from a backup file** (Relay Setup's "Load credentials
   from backup file" already does it); or **from the bookmarklet**, which holds it and survives in your bookmarks —
   click it while the (empty) ReaderWrangler page is open and it hands the key straight to the app. **Never through
   the address bar** (a link carrying the key lands in the browser's history, and its synced history on other
   devices). The bookmarklet's breadcrumb mark (the "keep your library" task, item 7) tells the app to offer this.
   **The plan, completed with Ron (2026-11-24):**
   1. **A page can't see your bookmarks** (only browser extensions can), so the app can't find the bookmarklet by
      itself. Arriving through the bookmarklet's "open ReaderWrangler" button brings the breadcrumb mark → the app
      KNOWS; arriving any other way, the empty screen ASKS: *"Used ReaderWrangler before? If you have its bookmarklet,
      click it now — it can bring back your Cloud Sync Key."*
   2. **The bookmarklet gets a ReaderWrangler-page case** — today its menu changes by page (bookmarklet-nav-hub.js ~63-71:
      Amazon's library, collections, book, series, author pages) but has none for a ReaderWrangler page (Ron: the menu
      "currently nothing on the menu relates to this scenario"). Clicked on a ReaderWrangler page, it runs inside that
      page, so the two talk directly: the app announces "ReaderWrangler, no key / no library"; the bookmarklet then
      shows **no menu** and hands the key straight to the app — one click. A page that already has its key: "already
      connected" (or the usual menu), nothing handed over. A test/dev bookmarklet on the live site (or the reverse):
      says so, hands nothing.
   3. **One box, the choices inside** (not two prompts): *"Found your Cloud Sync Key in your bookmarklet (support code
      …7Q2K9). Restore your library from Cloud Sync — books, folders, tags and notes, last saved 2 days ago?"*
      **[Restore] [Just the key] [Not now]** — never adopted silently, even from your own bookmarklet (outside review 2
      warned Restore and the phone link adopt keys silently); the support code shows it's yours. Before Restore from
      Cloud Sync exists, the box offers the key only: *"…Use this key? Then Import from Relay brings your books back;
      Restore Backup brings back your folders."* Wording is Ron's at build time.

#### Lock the Cloud Sync Key in backups with an optional key password
<!-- id 20261104-1024 -->

**In the launch gate (Ron, 2026-11-19):** a backup shared before this ships stays unlocked forever — adding the lock later doesn't protect files already sent.

_Why it matters:_ Every backup carries your Cloud Sync Key, and since 7.25 that key also signs changes — so whoever you
share a backup file with ("send your brother your ReaderWrangler file") can change or delete your cloud library. A family
member forwarding a file is far likelier than any attacker.

**Decided** (Ron + Claude, 2026-11-04)
1. **An optional "key password" locks only the key inside the backup** — books, folders and notes stay readable, so
   forgetting it costs a re-setup, never data. Not stored only in the browser instead: the backup exists for the day
   the PC dies (Ron). Words: **lock** (not "scramble" — sounds undoable by anyone; not "encrypt" — that's Cloud Sync's
   word) and **key password** (not "backup password", which reads as "protects the backup" or "a spare password").
2. **One optional line in the save step, never a pop-up (Law 18):** *"Lock the Cloud Sync Key in this backup with a
   password (optional) [______]  Why?"* + "Don't ask again". Shown only when Cloud Sync is set up. **Remembered in
   this browser**, so later backups lock automatically; **File → Key Password…** sets, changes or removes it.
3. **Why? / help text:** sharing an unlocked backup shares access to your cloud library (the recipient could change or
   delete your library and organization; you could recover from your last backup and make a new key); a password,
   even a simple one, makes sharing a backup harmless — *"but feel free to use a strong password and a password
   manager. We highly recommend password managers."* And: *"To look at someone else's backup, use a separate browser
   profile — never swap backups in your own."*
4. **The backup carries a "key locked" flag.** On restore, the wording adapts:
   - this browser already has a key: *"This backup's Cloud Sync Key is locked. Enter your key password to restore it
     too — or skip to keep using this browser's key (the usual case, if you haven't made a new one)."*
   - no key here (e.g. a new PC): *"…Enter your key password to reconnect Cloud Sync — or skip: you can enter your key
     later, or make a new one."*
5. **Restore never blocks:** a skipped or wrong password restores everything else, then says *"Cloud Sync wasn't
   reconnected — enter your Cloud Sync Key, or make a new one if you don't want to keep using your current cloud library
   (a new key means a new cloud library)."*
5a. **Remembered in this browser is safe** (Ron, 2026-11-26, outside review 2 item 6): this browser's storage already holds the key itself, unlocked (the
    app needs it to sync), so storing the password beside it exposes nothing new — its only job is the key inside files
    that leave this PC. Typed again only to restore on another computer. The field is a standard password field so a
    password manager can save and fill it — **test with Ron's LastPass.**
6. **Under the hood:** the same password-to-key method the relay already uses (relay-crypto), on one field of the
   backup. A weak password can be guessed by someone determined with the file — accepted for this threat (Ron).
7. **Ripples:** the Disconnect wording ("Relay Setup: disconnect…", part of the Cloud Sync rename) says the key is in your backups "locked
   with your key password, if you set one"; the private-values commit check still refuses an unlocked key in a
   backup-shaped file (a locked one holds only scrambled text).

#### Relay worker: one release of changes (backup alerter, clearer daily email, strict ID check)
<!-- id 20261024-1045 -->

**Before launch (the launch gate, 2026-11-19): items 3, 4 and 8 below** — 3, the strict ID check (an ID in the wrong
form silently opens a separate, empty cloud library); 4, the nightly email names cloud libraries by 6 characters, not 4 (with
many users, 4-character names collide); 8, a small "request" note per cloud library, which "Refresh all books from Amazon"
(in the fetcher work) needs. Ship 3 and 4 with the Cloud Sync rename, 8 with the fetcher work. **Also before launch:
items 10–15** (outside review 1, 2026-11-20 — the open door for strangers, the alert email's full ID, security.txt's
reminder, the "Amazon stopped a fetch" email). The rest can follow launch.

_Why it matters:_ Every relay change is a separate deploy, each needing Ron's yes; gathering them makes one worker
release. And two of them close real gaps today: the relay accepts IDs in a form that silently opens an empty
mailbox, and the Danger zone's wipe may not reach the full copies, which never expire (Ron, 2026-10-24: "I want to
close this out").

**Order of work:** where it sits in the launch gate — the order of the tasks is the one home for the order.

**What's in it**
1. **C — a shared notepad** for both relays (no user data) — the last step of the relay storage work (7.21.1–7.23.0):
   - dev becomes a **backup alerter** — it sends "[Dev] backup alert" if a limit crossing it has seen for over an
     hour has no production alert recorded;
   - a **"production is alive" check** — alert if production's daily summary is more than 26 hours old.
2. **The daily email counts copies, not just keys.** Today "library generations 4, device-state generations 12" are
   *key* counts — each copy's parts plus its manifest (`groupKeys`, relay-worker.js ~1236) — and device-state has no
   expected count. Say e.g. "library copies 2 (4 parts), device-state copies 4 (12 parts) — at most 2 per channel is
   expected". (Found 2026-10-24; the health judgment was right all along — the cleanup applies keep-2 to real copies.)
   **And no 🚨 on the routine summary** (Ron, 2026-10-30): today every email's subject gets it (`sendAlert`, relay-worker.js
   ~887, "🚨 Daily usage summary - …"), so a normal morning looks like an alarm — red in Gmail's web page. Keep 🚨 for
   real alerts only (threshold, auto-block, cron error); the summary becomes e.g. "Daily usage summary - 2026-10-29".
   **And every "Deleted" line gives the copy's time and age** (e.g. "…dc38, saved 14:27 UTC, 11 min old") — so the
   10-minute rule for unfinished copies can be checked from the email. Today it shows the date only (2026-10-30: Ron
   closed the tab ~5 s after an import; the push that closing triggers was torn after its first part, and the on-demand
   summary ~10 minutes later deleted it — correct, but unprovable from the email).
   **And how recently the cloud libraries were used** (Ron, 2026-11-04 — from item 9's last-used date): one line, e.g.
   *"Cloud libraries: 2 — used in the last day 1 · week 1 · month 2 · year 2 · idle over a month 0 · idle over a year 0
   (deleted tonight: 0)"* ("idle for a day" is just "not used in the last day" — not shown twice). Dev's test channels
   skew its counts; the dev email already marks test data.
3. **Strict ID check** — moved from the Cloud Sync task (item 4) because it's safe now and closes a gap today: the
   relay's one ID check ignores case while storage doesn't, so an ID in the wrong form opens a separate, empty mailbox.
   Drop the case-insensitive flag (`UUID_REGEX`, relay-worker.js ~45). Every real ID passes, and so does the test
   rig's `22222222-…`.
4. **The nightly email names mailboxes by 6 characters, not 4** (`shortId`, relay-worker.js ~1211) — moved from the
   Cloud Sync task (item 3); it becomes the support code that task shows beside the key. **One way everywhere:** today
   the email names a channel two ways — the last 4 characters (`…21fc`, `shortId`) and the FIRST 8 in the "Kept / not
   judged" and budget lines (`41e0e16f…`, `ch.slice(0, 8)`, ~1287 / ~1304). Use the 6-character support code in every
   line (found 2026-10-30).
5. **The test scripts clean up after themselves:** `relay/test-phase1.mjs` leaves one unimported run on the
   `22222222…` test channel each run (19 now; they expire after 90 days). And since 7.25.0 every run of
   `relay/test-signed-writes.mjs` / the harness leaves small PERMANENT keys for its throwaway channels — a write key, a
   block record, a proof, a first-used record (dev 2026-10-31: 8 write keys, 10 blocked channels, mostly tests). Let
   revoke also delete the channel's write key (the block record is enough), and keep the rest out of the way.
   **Run the tests locally by default** (`cd relay && npx wrangler dev --env dev --local`; `RELAY_URL=…`) and on dev only
   as a final check — the 10-31 release day's dev runs used 23.6% of the account's daily writes.
6. **Once:** compare dev's storage figure in the daily email with the Cloudflare dashboard (open since 2026-10-15).
7. **The daily summaries also go to a dedicated inbox Claude can read** (Resend Inboxes, through MCP), so Ron stops
   pasting them — and Claude reaches only that mail, not Ron's whole mailbox. Until then Claude reads them from Ron's
   Gmail, filtered to `from:alerts@readerwrangler.com subject:"Daily usage summary"` only (Ron, 2026-10-30 — "ReaderWrangler
   Relay - Daily Summary" is the body's first line, not the subject; if item 2 drops the 🚨, the filter still matches).
   Check Inboxes' pricing
   and whether it's still beta when building.
8. **A small "request" note per channel** for "Refresh all books from Amazon…" (the launch gate → "Fetcher work, in build order"): a route to write, read and
   delete one encrypted note (the app requests a full refresh; the fetcher reads it at start and deletes it after a
   successful refresh). Idle until the app + fetcher part ships; the signed-writes gate covers its writes. Name the new
   key kind in the daily email.
9. **Delete a cloud library nobody has used for a year** (Ron + Claude, 2026-11-04). **VERY low priority** (Ron, 2026-11-25: nothing
   is a year idle for 12 months yet; every version and mailbox run carries the relay's own time in its name, so once
   built, anything already a year idle goes at the next nightly run — nothing lost by waiting). Today a cloud library whose key was
   lost (so it can't be revoked) keeps its books forever — encrypted, harmless, but storage. The nightly cleanup deletes
   a channel's copies after a year with no activity. **Say so** in the app, on the security page and in the help notes:
   *"A cloud library nobody uses for a year is deleted. Your library stays safe in your browser and in your backups, and
   the next time you use ReaderWrangler it fills a cloud library again."* **The app must refill, never mistake "gone" for
   "your library is empty"** (the naming review's "silent empty mailbox" trap) — a returning user's next fetch and next
   change repopulate it. (Considered and rejected: emailing owners of idle copies — it would collect personal data,
   the "encrypted" address would be readable by the server anyway, and deletion-warning emails train users for
   phishing; "Remind me when my last backup is getting old" guards the real disaster instead.)
   **How "used" is known — a last-used date per channel** (Ron + Claude, 2026-11-04), unencrypted, beside the existing
   first-used record (`lifecycle:{id}:used`, relay-worker.js ~473/706): `lifecycle:{id}:last`, a date.
   - **Reading counts as use**, not just writing — someone who only browses on the phone for months must not lose the
     copy they're using.
   - **Written at most once a day per channel** (only when the stored date isn't today) — writes are the free plan's
     tight limit; a read costs only the cheap check.
   - **The year-old cleanup reads it, and also deletes the channel's other permanent leftovers** (its first-used and
     last-used records and its write key), or those pile up forever.
   - **Disclosed with GoatCounter, in the same places** (Ron): the security page's analytics bullet (security.html
     ~113) and the planned privacy policy (outside review 1) — e.g. *"The sync server records the date your cloud library
     was last used — never what's in it."*

**Added by outside review 1** (Ron + Claude, 2026-11-20) — all before launch. The problem: the relay takes any made-up
ID as a new cloud library, from anyone; its limits are per cloud library (200 writes an hour, relay-worker.js ~61–63), so
every made-up ID starts fresh, and anyone can register a write key on a made-up ID with one request (`handleRegister`,
first come wins). Even refused requests use part of the free plan's daily writes. Why, with no abuse seen (Ron): once
the big targets are locked down, people with ready-made attack scripts go after whatever is left, for bragging rights.
10. **No storing without a write key** — remove the path that accepts unsigned writes for a channel with no key (Ron:
    "We can definitely remove that acceptance of an unsigned write without the key"). Every current app version
    registers its key before its first write (relay-client.js ~96–114).
    **How** (Ron + Claude, 2026-11-26, outside review 2 item 10): **in the one gate** (`route()`, relay-worker.js
    ~232–246 — every non-read request naming a Channel ID passes it, revoke included), a cloud library with no write
    key → **refuse every write except registering** — today's line ~196 "no write key → let it through" becomes a
    refusal, so revoke, deletes, cleanup and "begin an upload" are covered, and so is any route added later. (Today
    revoke on a made-up ID writes two stored items that never expire, runs three storage listings and counts a
    "revoked" in GoatCounter — for free, from anyone.)
    1. Test first: on an ID with no write key, a revoke, a delete, a cleanup and a "begin an upload" are refused;
       registering still works.
    2. **It cuts off no one** (checked 2026-11-26, `.private/relay_inventory.py`): the only library without a write
       key that holds data is production's 58c1bfd7… (a Complete Copy saved Sep 8, never since; expires Dec 7) — dev's
       e9721301… is ours (expires Nov 30). Registering stays open, and every app since 7.25.0 registers before its
       first write; only a tab left open since before 7.25.0 is refused ("update the app"). **Before the deploy:
       re-run the inventory** on both relays.
11. **Cloudflare's "are you human" check (Turnstile) when a cloud library is created** — at Cloud Sync setup and "make a
    new key", once per person, never on fetches. The check hands the app a one-time ticket; the app sends it with the
    new write key; the relay asks Cloudflare whether the ticket is real before registering the key. With item 10, no
    ticket means nothing is ever stored, and skipping our code doesn't help (Ron: "People are used to the Are You a
    Human checkbox from Cloud Flare. We'll plan to go with it pre-launch."). An app change too (the setup screen); one
    line on the Security & Privacy page. Free; Cloudflare says it uses no cookies. Rejected: a per-person limit (the
    relay can't tell people apart), email sign-up (breaks "no account"), browser fingerprinting (unreliable,
    skippable, and it's tracking).
    **Where the check runs — decided 2026-11-25 (Ron, outside review 2 item 5):** NOT in the app's page. Cloudflare's
    script can't be pinned or copied ("Load `api.js` from the exact URL… Proxying or caching this file will cause
    Turnstile to fail") and would run where the key is readable. Instead:
    1. **The relay worker serves one small page** (its own code answers one address with a web page — not stored in
       KV); it's on the relay's address, a different site, so browsers keep its storage apart from readerwrangler.com's.
    2. The app opens it (a pop-up or a box); the person passes the check there; the page passes **only the ticket**
       back to the app (the browser's window-to-window message); the app sends it with its request as before.
    3. **The locks:** our widget's hostname list names only that page; the relay holds the secret key (a worker
       secret) and refuses a ticket whose answer says it was solved anywhere else (Cloudflare: "Validate the action and
       hostname"); the page puts a fingerprint of the new write key into the ticket's custom data (returned by
       Cloudflare), so a ticket works only for the one library it was solved for; and the relay remembers used
       tickets itself, exactly (the Durable Object — the pointer keeper), because Cloudflare's "token-reuse detection
       is eventually consistent" — one ticket could otherwise pass twice in its 5 minutes.
12. **The brakes** (the review's five, revised for item 11 — Ron, 2026-11-20). They catch what gets past the human
    check (checks solved by hand or by a paid service, or a real surge) and cap the one cost that grows, storage:
    1. **New cloud libraries are counted, never refused:** an email to Ron when a day's count reaches 5, then after 8
       more, 13 more, 21 more… (Ron: Fibonacci gaps) — at 5, 13, 26, 47, 81, 136, 225, 369, 602, 979: about ten
       emails for a thousand new copies, so a flood of alarms can't use up Resend's 100 emails a day and silence the
       nightly summary. Each email gives the day's count. Raise the start as normal days grow.
    2. **A size limit per cloud library, enforced by the relay:** 5 × what a copy of Ron's library *should* hold (Ron) —
       **200 MB** (agreed): at rest, two library versions of ~18 MB plus a small organization ≈ 40 MB; plus room for a
       week of fetches waiting to be imported (each a full library, ~18 MB). Ron's copy today, with its oversized
       organization and 4 waiting fetches, peaks near 144 MB — under it. Revisit after "Smaller organization syncs",
       item 4.
    3. **A storage ceiling of 10 GB** (about $5 a month over the paid plan's included 1 GB): past it, the relay refuses
       **new** cloud libraries — including "make a new key" — and emails Ron; existing cloud libraries keep syncing. Because the
       bookmarklet can't fetch without Cloud Sync, a refused newcomer can't bring in their library at all until it
       reopens — the words must say so, and give the reason, "full" (Ron: a reason earns forgiveness). The words (agreed, Ron 2026-11-20):
       *"Cloud Sync is full for new setups right now. We're aware of it and working on it — please try again in a day
       or two. Until then ReaderWrangler can't bring in your library from Amazon, because your books travel through
       Cloud Sync. Sorry for the wait."* and, for Make a new key: *"Cloud Sync is full right now, so it can't make the
       new cloud library a new key needs. Your current key keeps working, and nothing has changed. We're aware of it and
       working on it — please try again in a day or two."* **Try again, and a quiet retry** (Ron, 2026-11-20): the
       refused screen keeps a **Try again** button, and the next time the person opens ReaderWrangler, setup quietly
       tries again by itself and carries on if there's room — no email sign-up (it would need verification emails
       from a budget of 100 a day, and break "we don't have your email"). The site's "known problems" line says when
       Cloud Sync has room again. The storage alerts (25/50/75/90%, today measured
       against the free plan's 1 GB — `CF_LIMITS.kvStorageMB`) move to fractions of this ceiling at the upgrade.
    4. **No storing without a write key** — item 10.
    - **Two versions of each copy stay** (Ron, 2026-11-20, after asking why): the reader falls back to the previous
      version when the current one is missing or fails its check (relay-client.js `readCanonical`) — Cloudflare's
      storage can show the new "current" marker before the new version's data everywhere, and a bad save must never
      leave nothing to read. The cost is one extra version (~18 MB for a 3,270-book library).
    5. **No limit per internet address** — dropped: whole households, offices and phone carriers share one address.
13. **The full Channel ID out of the auto-block alert email** (relay-worker.js ~935) — it's half of a Cloud Sync Key;
    use the short form (first 8 … last 4) the logs use.
14. **security.txt's reminder:** the relay reads readerwrangler.com/.well-known/security.txt each night and sends its
    own email that stands out — weekly in the 4 weeks before the expiry date, daily in the last week (Ron). The date
    is set six months ahead each time.
15. **"Amazon stopped a fetch" emails** — the relay's half of "When Amazon stops a fetch: tell Ron…" (the fetcher work):
    a small request the bookmarklet can send; at most one email a day per kind of problem.
16. **Make the write limit real — or honest** (Ron, 2026-11-26, outside review 2 item 8). Today it doesn't work: only 1
    request in 5 updates the KV counter (since 7.5.0), and the count is saved only when a write is allowed — so it never
    passes 200, the automatic block at 2,000 can't happen, and past 200 four writes in five still go through (the
    reviewer: 4,016 of 5,000 allowed). The fix:
    1. **Count only signed writes** (traffic that proved itself) — since 7.25.0 only the key's holder can write.
    2. **Refuse every request over the limit**, not 1 in 5.
    3. **Never block for good on unproven traffic** — registering a write key is unsigned and counts first; a working
       block there would let anyone with just a Channel ID get a cloud library blocked forever.
    4. **Exact** once the pointer keeper (a Durable Object) exists — it was planned to hold the exact write counter.
    5. **Correct the worker's comments and the nightly email's line** "auto-blocked for abuse 0 — 0 is what is expected"
       (it reads 0 because the block can't happen). `SECURITY.md` was corrected 2026-11-26.
    - Not doing: an account-wide daily write budget ("conserve mode") — Cloudflare's paid plan at launch (Ron's intent)
      gives about a million writes a month; a per-library limit can't guard the shared allowance anyway.
17. **An upload's label can't be changed** (Ron + Claude, 2026-11-26, outside review 2 item 9). Today an upload's label
    (books, wishlist-add, collections, deletion, reset) sits beside the encrypted books in plain text, and an upload
    under 1 MB (one request — most uploads) is signed over its **size** only. So anyone who has seen the request
    (Cloudflare, an add-on watching requests, security software inspecting connections, a script on Amazon's page) can
    send it again within 5 minutes with "books" changed to "reset" — same size, accepted as a new upload — and the next
    Import empties the cloud's combined copy and its deletion records, and today removes the owned books it no longer
    has from the browser. The relay itself can change any upload's label. Checked 2026-11-26: `relay-client.js`
    ~699-704 (written) and ~792-797 (read), `relay-worker.js` 166 (the size-only list) and 592 (a new upload per
    request); the reset at `composeCanonical` ~1088.
    1. **The label and the fetch date sealed inside the encryption**, read only from there — neither a replayer nor the
       relay can change them. An upload with no label inside (stored before this) is read as an ordinary books upload,
       never a reset. In `relay-client.js` alone (the app and every bookmarklet button share it). A stored-format
       change: this is the design Ron has seen.
    2. **Every write signed over its contents** — the size-only list deleted (less code; it also closes a large
       upload's small hole: a piece overwritten with same-size junk before the closing request arrives, which loses that
       upload). Fingerprinting a 5–20 MB piece exceeds the free plan's 10 ms per request, so **this ships with
       Cloudflare's paid plan on** (Ron: "We go to paid plan when we implement your recommendations" — before launch if
       this is). Not doing: smaller pieces to fit the free plan — 5–20× the writes, against the free plan's 1,000 a day.
    3. **Import skips an exact repeat** — an upload whose fingerprint matches one already combined (two genuine uploads
       are never identical: the encryption starts each from a fresh random value). Closes the one harmful exact replay:
       a resent reset arriving after other uploads.
    4. **Correct `docs/design/RELAY-SECURITY-PLAN.md`'s note** "an exact replay is harmless… only begin/mint creates
       something new" — a one-request upload creates a new stored item too; and its table's "big upload parts" row.
    5. Test first: a relabeled upload fails to open; a size-only signature is refused; an exact repeat is skipped.
    - Choice 4 of the review (the relay itself skipping, repeating or rolling back) → the pointer keeper, in "Keep your
      tabs and browsers in step…".
18. **Know the cloud libraries — how many, how old, which format** (Ron + Claude, 2026-11-26, outside review 2 item
    10). Ron: collect as much as we can without touching privacy, and when a change like the write key ships, be able
    to tell how many libraries use it and how many don't. Today the nightly email gives totals only.
    1. **A format number per cloud library**, kept apart from the app's version. Format 1 = no write key, format 2 =
       a write key (the relay tells them apart — no stamping); **format 3 = item 17's sealed labels**, and every later
       change we need to track gets the next number. Item 17's rule "no label inside = an ordinary upload" becomes
       "format below 3"; when format 2's count stays at zero, its reading code can go.
    2. **Where:** with each save the app sends the format, the app version that wrote it and the date (signed); the
       relay puts them in the **small plain label Cloudflare lets each stored item carry** (up to 1 KB), on the
       library's "current version" marker — it comes back free with the listing the nightly already does, so no
       read per library (hundreds a night at launch). When the pointer keeper moves that marker, the label moves with
       it (designed then).
    3. **The nightly email's counting lines** — counts only, no library named: libraries last written within 7 / 30 /
       90 days and older; by format; by the app version of the last write; with no write key; browsers per library
       (1 / 2 / 3+); book counts in bands (under 500 / 500–2,000 / more).
    4. Nothing says who anyone is or which books; each new thing collected gets its line on the security page
       (outside review 2 item 12, the privacy lines).
    5. `.private/relay_inventory.py` (2026-11-26) is the one-off, per-library version of this (read-only; IDs shortened
       to 8 characters) — for Ron's checks, never the email.

**Watch out**
- **Turn on Cloudflare's paid plan before this release's relay deploy** (item 17.2 needs its computing allowance).
- One `WORKER_VERSION`; dev first, then production — **Ron's yes before each deploy**; alphas deploy from the branch,
  and both relays are redeployed from main at the release.
- **Never test with a temporary schedule** — Cloudflare's schedule incidents (2026-10-12/13/14) delayed changes by
  hours and a replaced test schedule kept mailing. Test with the on-demand summary instead (PowerShell; one email each;
  Resend allows 100 a day):
  `$k = Read-Host "TEST_ALERT_KEY"; Invoke-RestMethod -Method Post -Uri ("https://readerwrangler-relay-dev.readerwrangler.workers.dev/run-summary?key=" + [uri]::EscapeDataString($k))`
- Leave production channel `58c1bfd7…` alone — another user's data; it expires Dec 7.
- Relay tests: `node relay/test-signed-writes.mjs` and `RELAY_URL=… node relay/test-phase1.mjs` — both run against a
  local relay first (`cd relay && npx wrangler dev --env dev --local`), then dev; both refuse production.
- Inventory tool: `analyze-relay-keys.js` in the TODO notes' folder (key dumps hold channel IDs — credentials — delete
  them after use).
- The shared-numbers commit check must still pass (items 2 and 9 touch the cleanup's rules only if they change keep-2
  or the grace — they shouldn't). (The old item "the wipe reaches everything" was already true — checked 2026-10-31 in
  `handleRevoke`; removed 2026-11-04.)
- Relay tasks that are **app-side, not worker** stay where they are: "Relay Setup's connection test checks the wrong
  relay on dev" and "Relay Setup: disconnect, or reset credentials" (part of the Cloud Sync rename task), "Bookmarklet: when
  your key no longer works, say so plainly…" (After launch), "Keep your tabs and browsers in step…" (the launch gate), the
  Cloudflare $5 plan (the launch gate). The Cloud Sync task keeps its app-side work and the "make a new key" order.
- Tool survey 2026-11-03 (docs/design/TOOL-SURVEY.md): Cloudflare's official skills (`cloudflare/skills`) — the skills only, not the remote
  server with access to the Cloudflare account; the local Workers Vitest plugin for tests; `wrangler telemetry disable`.
- **Channel IDs in the emails in the app's short form** (2026-11-09): the daily summary says "channel 22222222…" (first
  8 only — relay-worker.js ~1383, ~1400); the app's log and Relay Setup now show `41e0e16f...726c` (first 8 … last 4,
  logger.js `shortChannelId`, Ron) so old and new keys read differently. The emails should match.

#### Cloud Sync: rename Relay, show one Cloud Sync Key, and 'make a new key' retires the old one
<!-- id 20260828-0000a -->

**Viewing your key — grouped with it** (Ron, 2026-11-26, outside review 2 item 6): show the current key in **Relay Setup → Credentials → Enter
Credentials Manually** (where people look — today it's visible only, by accident, in the phone-pairing section's "Or
enter manually on your phone", readerwrangler.js ~11941), and in the pairing section; both **hidden by default** with
**Show/Hide**, one shared setting **remembered** in this browser (Ron: never bothered at his own desk). Keeps the key
viewable now that backups lock it.

**Grouped with it** (Ron, 2026-11-25): its new bookmarklet also carries the check from "A Cloud Sync Key never changes
hands without asking…", item 1 — the bookmarklet works only on Amazon's pages and ReaderWrangler's own.

_Why it matters:_ "Relay", "Credentials", "Channel ID" and "Passphrase" are engineering words, and users juggle two
values that are really one secret. And today making new credentials doesn't retire the old ones: whoever holds an old
key can still read the whole cloud library (the Fetched Copy never expires) and write to or wipe it. Renaming is free before launch and
expensive after.

**The record: docs/design/CLOUD-SYNC-NAMING.md** — everything decided, why, what was rejected, and the check-character
test. Decided 2026-10-23 (Ron + UX, three outside-review rounds). **Anti-bounce rule:** only a real user's misreading
reopens a name, never a new argument.

**What you'd get** (details in the record)
1. **The words:** Cloud Sync · Cloud Sync Setup · Import from Cloud Sync · **Cloud Sync Key** (one key; "Credentials",
   "Channel ID", "Passphrase" leave the screens) · Save Key · Make a new key · the bookmarklet's buttons **Send Library
   to ReaderWrangler** / **Send Collections to ReaderWrangler** · "the sync server" on the security page ·
   **your cloud library** (what the key opens — was "your cloud copy", Ron 2026-11-23; it also replaces the app's "the
   relay's copy" and "temporary copy on the relay"). Data Status and "bookmarklet" stay. About 80+ places (app ~52,
   phone 3, bookmarklet screens ~22, site pages ~13), plus README, help notes and the User Guide.
2. **The name defined once, and a commit check** that refuses retired words in anything users see — now its own task,
   "An anti-glossary: the words we don't show people…" (below, part of this task — built before the rest of it). This rename
   sweeps its Retiring words to zero — Relay, Credentials, Channel ID, Passphrase, **and "fetcher"** (Ron, 2026-11-12:
   the tool is "the bookmarklet", the act "update your library from Amazon" — GLOSSARY.md) — then flips them to Banned.
   Old CHANGELOG entries, post-mortems and design records keep "Relay".
3. **One Cloud Sync Key:** `RW1-` + 13 groups of 5, Crockford's alphabet (no I, L, O, U; O read as 0, I/L as 1), the
   ID's 32 hex digits + a 31-character secret + 2 check characters (ISO 7064 pure, radix 32, modulus 1021). A 6-character
   support code beside it (the relay's nightly email moving to 6 is done in "Relay worker: one release…").
4. **One tidy step is the only way in** (strip, fold, check, split, rebuild the ID exactly as stored); the key-making
   code refuses anything else; **the relay refuses an untidy ID** (its one check made strict — done earlier, in "Relay
   worker: one release…"); a decrypt failure says
   "this key doesn't match", never "no data".
5. **Make a new key = change the locks:** save the new key and park the old one as "pending revoke" in one write, then
   block and delete the old mailbox (including the full copies and pointer — the relay's wipe is fixed earlier, in
   "Relay worker: one release…"), retry at next launch if that fails;
   backups carry the pending slot; an old backup's replaced key is named as such. The confirmation adds "Your books
   and folders stay as they are."
6. **Honest wording:** fix the "syncs automatically" message; the bar says what is true ("…ready — Import"); the help
   line about the bookmarklet containing the key; the security notes' statements (the record, "What we tell users").
7. **Tests:** the round-trip (ID → key → ID, byte for byte) and the check-character test kept as permanent checks.
8. **The log hides the key by its shape** (Ron, 2026-11-11, building 7.28.0): the logging kit's cleaner finds a secret
   only by its exact value — today the current passphrase — so an OLD key (from before a "Make a new key") or one pasted
   into any text would reach the log and Copy diagnostics. With the key's shape fixed, add "secret patterns" to the kit
   (`logkit/logger.js`: a list of patterns, each match replaced by the secret label), with a test that fails first, and
   give it the `RW1-` pattern in `logkit-settings.js`; its label becomes the key's word ("[passphrase]" today).

**Build together**
- With "Relay Setup: smoother sections and clearer Esc / Help behavior" (below, part of this task) — the same window,
  touched and re-tested once.
- Reconcile with "Relay Setup: disconnect, or reset credentials" (below, part of this task): its 6.9.0 "Danger zone → Revoke
  credentials & wipe relay" is what "Make a new key" reuses; its gentle Disconnect stays its own item.
- The User Guide rewrite (below) waits for this, so the new names land once.

**Watch out**
- **Your key:** today's passphrases use another alphabet and there's no legacy path (one user). After the build, make
  a new key once — then re-drag the bookmarklet (LOCAL, and the DEV and PROD ones) and re-pair the phone.
- **The relay changes** (strict ID check, nightly email's 6 characters, the wipe reaching the full copies) **moved
  2026-10-24 to "Relay worker: one release…"** (just above, in the launch gate), which ships first. Anything the key work still needs
  from the relay is a worker change — Ron's yes before every deploy; dev first.
- The bookmarklet's screens change the same way for all three bookmarklets → dev and prod together.
- When this ships, update the CLAUDE.md vocabulary rule to the new names (it describes today's screens until then;
  both trace to the 2026-08-28 decision).
- Sizing: a small feature (the key format and its tidy step, the change-the-locks order) plus a worker change plus an
  80-place rename — not a rename alone.

##### An anti-glossary: the words we don't show people, kept in a list and enforced at every commit
<!-- id 20261112-1431 -->

**Part of the Cloud Sync rename (Ron, 2026-11-19):** built before the rest of it — the rename sweeps this list's Retiring words to zero, then flips them to Banned (the rename's item 2).

_Why it matters:_ A retired word creeps back one message at a time ("the fetcher" was never decided and is all over the
help; "Relay" will be retired by the rename). A rule in someone's memory — or buried in a script — doesn't stop it; a
visible list that a commit check reads does, and adding a word to it takes seconds (Ron, 2026-11-12).

**Decided** (Ron + Claude, 2026-11-12)
1. **A file of its own** — `docs/design/ANTI-GLOSSARY.md` — not a section: the data the check reads, visible to anyone.
   The glossary's "Words users never see" section MOVES there (one home per word); the two files link to each other.
2. **Each row:** the word (word boundaries; case as listed), why, what to say instead, and a **status** — **Banned**
   (any use in what people see is refused) or **Retiring** (still on screen until a named task replaces it: the check
   refuses NEW uses only — the count can only go down — so it can be listed today without turning everything red).
   First rows: Import/Export (for backups, Banned), "Sync now" (Banned), IndexedDB / localStorage / JSON / tombstone
   (Banned — checked where they'd reach a person), Relay / Credentials / Channel ID / Passphrase (Retiring — the
   Cloud Sync rename), fetcher (Retiring — the same sweep; glossary: "update your library from Amazon").
3. **Where it looks** — only text people see: the messages and labels in the shipped scripts (string literals, not code
   names — `relay-client.js` keeps its name), the site's pages, README, the User Guide, the help pages. It skips the
   CHANGELOG's history, post-mortems, design notes and tests. The exclusions live in the same file, also visible.
4. **A commit check** (git-hooks/, like the others; tests first) reads the file — and refuses a malformed row, so the
   list can't silently stop working.

##### Relay Setup: smoother sections and clearer Esc / Help behavior
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
"Cloud Sync: rename Relay, show one Cloud Sync Key, and 'make a new key' retires the old one"** (the task this one is part of) — that
task changes this window's name, wording and key display; one pass touches and re-tests the window once.

**How (technical)**
- Item 2 is the `onClose` branch that handles `reason === 'esc'` specially in the Relay Setup dialog (readerwrangler.js
  ~11371 on 2026-10-21: `reason === 'esc' && relayManualCreds` closes only the section).

##### Relay Setup: disconnect, or reset credentials
<!-- id 20261014-1030am -->

_Why it matters:_ A clean way to stop syncing, or to start over with new credentials.

**Already done**
- 6.9.0: Relay Setup's "Danger zone → Revoke credentials & wipe relay" — clears the keys and reopens the step that makes new ones.

**Left**
- A gentle **Disconnect** that just stops syncing on this device, without revoking or wiping anything on the relay.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **The danger is losing the key, not data** — the key IS the access to the cloud library. The Disconnect window shows
   the key with a **Copy** button before you confirm: *"You'll need this key to reconnect — it's also in any backup
   you've saved (File → Save Backup), locked with your key password if you set one. Your bookmarklet and other devices
   keep syncing."* (Ron: backups carry it — true since 6.0.0; the lock: "Lock the Cloud Sync Key in backups…", the launch gate.) The one explicit, irreversible verb, with the remedy one click away inside it — not a guessing
   prompt (Law 18).
2. **Say exactly what stays:** this device's library — untouched; the cloud library — untouched; other devices and the
   bookmarklet — unaffected (the bookmarklet carries its own copy of the key, so the next fetch still reaches the
   cloud; this device just won't import until you reconnect).
3. **In the Cloud Sync words when they ship:** "Disconnect this device from Cloud Sync"; "key", not "credentials".
4. **Build it in one pass through the setup window** with "Cloud Sync: rename Relay, show one Cloud Sync Key…" and
   "Relay Setup: smoother sections and clearer Esc / Help behavior" — touched and tested once.

#### Reset App: one honest message in all four places (what's cleared, what's kept, how to come back)
<!-- id 20261030-1039 -->

**Built together with "What a reset clears: four resets, four different lists"** (just below — the same four places,
Ron 2026-11-19): what each reset clears, and what it says it clears, become one.

_Why it matters:_ Every reset message was written before Cloud Sync, so they talk about "files on disk" a user today
may never have had, point at a button that doesn't exist, and leave out the main way back — your cloud library.
Someone resetting is often already having a bad day (Ron, 2026-10-30, noticed the Tools → Reset App wording).

**The four places** (found 2026-10-30 — a class of sites)
1. **Tools → Reset App** (readerwrangler.js ~11784): "Your library/collections files on disk will NOT be deleted. You
   can reload them anytime." and **"💡 Tip: Use the Export button first"** — there is no Export button, and "Export"
   is retired (Save / Restore).
2. **The reset page's confirmation** (reset.js ~106): "Import backup file → Books + organization; Import
   amazon-library.json → Books only" — that file no longer exists for anyone setting up today.
3. **The emergency reset** (readerwrangler.html ~342 / ~361 — shown when the app can't start): "Your files on disk are
   safe — import your backup file after the reset…".
4. **The reset page's own text** (reset.html ~60): "Good news: … Your files on disk are safe. What you can recover:
   Import backup file → Restore EVERYTHING…".

**Decided** (Ron + UX, 2026-10-30)
1. **One message, defined once, used by all four** — so they can't drift again.
2. It says, in plain words:
   - **what's cleared:** everything ReaderWrangler keeps in **this browser** (books, folders, tags, settings);
   - **what's kept:** files you saved on your computer — backups (File → Save) and spreadsheets (File → Save
     Spreadsheet) — and **your cloud library**;
   - **how to come back:** restore a backup, or reconnect Cloud Sync and import.
   Ron's starting wording: "Your library/collections files on disk (backups, CSV files) will NOT be deleted. You can
   reload backups anytime."
3. **Build with "Cloud Sync: rename Relay…"** (just above) — the recovery words (Cloud Sync Key, Import from Cloud
   Sync) change there, so this is written once, in the new words.
4. **Verify before writing:** does Reset also clear the stored Cloud Sync Key? If it does, "reconnect" needs the key
   from a backup or another device — and the message must say so ("you'll need your Cloud Sync Key").
5. Then the help notes and the User Guide's "Starting over" section (User Guide task) say the same thing.
6. **Updates (2026-11-09):** the reset page's dead "Import amazon-library.json → Books only" bullet was deleted in
   7.26.0 (the library file was replaced by the relay in 6.0), and its other bullet says "Restore backup file"; checked —
   the emergency reset does NOT clear the stored Cloud Sync Key (item 4). Until "Restore from Cloud Sync…" (the launch
   gate) is built, the one way back offered is the backup file (Ron); once it is, offer that as
   the second.
7. **Update (2026-11-11, Ron found it):** item 6's fix reached only place 2 (reset.js's confirmation box) — place 4,
   the reset page's own panel, still offered "Import amazon-library.json" and "File → Export Backup" (fixed in
   7.27.0's branch: "Restore backup file → Books + organization", "File → Save Backup"). A sweep for
   amazon-library.json found nothing else a person sees in the app. Still open here: place 1 ("files on disk… reload
   them anytime", "Use the Export button") and place 3 ("Your files on disk are safe"), and the one shared message.


##### What a reset clears: four resets, four different lists
<!-- id 20261106-1715 -->

_Why it matters:_ "Reset" should mean the same thing everywhere. The app has four resets and each clears its own hand-kept
list of saved settings — so an Emergency Reset can leave things a Reset App clears, and old Book Lists may come back
(Law 4: four answers to one question = one missing list). Found 2026-11-06 while fixing F3 (all four now share ONE
delete of the book store, storage.js `deleteBookStore` — 7.25.1).

**What each clears today** (besides the book store; checked 2026-11-06)

| Saved setting | Tools → Reset App | "Erase and Reset" (app won't load) | Emergency Reset page | Phone's Reset |
|---|---|---|---|---|
| library state, cache, status, filters, view, folders | ✅ | ✅ | ✅ | ✅ |
| **Book Lists** (`readerwrangler-booklists`) | ✅ | ❌ | ❌ | ❌ |
| settings (`readerwrangler-settings`) | ❌ | ✅ | ✅ | ✅ |
| theme, phone preferences | ❌ | ✅ | ❌ | ✅ |
| Cloud Sync credentials + status | ❌ (kept) | ❌ (kept) | ❌ (kept) | ✅ (says so in its confirm) |
| wizard settings, search history, phone navigation, desktop mode | mixed — see the four lists |

- **Likely bug:** the library load falls back to the separate Book Lists entry when no saved organization exists
  (readerwrangler.js ~4489) — so after any reset but Reset App, the old Book Lists may reappear. Check with a test.
- Where: readerwrangler.js `confirmReset` (~6400); readerwrangler.html (the inline emergency reset, ~372); reset.js
  `STORAGE_KEYS`; mobile.js `handleReset` (~2815).

**To decide (Ron):** what a reset clears — everything, or everything but the Cloud Sync Key (the desktop keeps it, the
phone clears it — deliberate?) — then ONE list (with the delete, in storage.js), every reset calls it, and a test
compares the browser's storage after each reset.

**Test gaps from 7.25.1** (filed per TESTING.md §6): RESET-001–005 cover Tools → Reset App only. The emergency "Erase
and Reset" (needs the app made to fail its load), the phone's Reset (the phone page) and the Emergency Reset page each
use the shared delete but have no test of their own — including the "Close your other tabs" wait. Build them with this
task's storage-comparison test.

#### Relay Setup's connection test checks the wrong relay on dev
<!-- id 20261012-0000a -->

_Why it matters:_ On your local copy or the dev site it tests production, so its answer can be wrong.

**What you see**
- On your local copy or the dev site: File → Relay Setup → the connection test reports on the **production** relay, not the dev relay your copy actually uses. So "connected" / "revoked" there can be wrong for dev.

**Why it happened** (checked 2026-10-22): relay-client.js already has the wrapper — `relayFetch(path)` builds the
address from the one "which relay" answer — but it doesn't offer it to the app (not in `window.RWRelay`), so the test
called the browser's request function directly with a hard-written production address (readerwrangler.js ~1838). The
relay's addresses are written in **five** places: production in relay-client.js:13 (the default) and the buggy ~1838;
dev in readerwrangler.js:130, mobile.js:31 and bookmarklet-nav-hub.js:52.

**Decided — relay requests go only through relay-client** (Ron + UX, 2026-10-22)
1. **relay-client offers what the app needs** — a named `testConnection(channelId)` (better than exposing raw paths),
   so the app never builds relay addresses; the test uses it. This fixes the dev bug.
2. **Both addresses are written once, in relay-client.js.** The app, phone and bookmarklet hub only answer "am I on
   dev?" (each detects it its own way) — **callers never pass Dev or Prod**: a caller that chooses can choose wrong
   (that's this bug). The relay's own test scripts in `relay/` run outside the app and don't use this.
3. **Make bypassing it impossible** (Ron): the app page is ours, so its `window.fetch` gets a guard that **throws**
   for a request to a relay address not coming from relay-client (*"Relay requests go through RWRelay"*);
   everything else passes untouched. relay-client keeps the real one. An honest error, not a silent substitute.
4. **A commit check refuses a relay address written outside relay-client.js** (app, phone, bookmarklet files).
5. Test step: on localhost, Relay Setup's connection test names the **dev** relay.
6. **Say when the channel is empty** (Ron + Claude, 2026-11-05): today the test reports **connected** for a channel
   with nothing on it — and a mistyped Channel ID IS an empty channel, so a typo shows green at the very moment it
   should be caught. Report *"Connected — nothing sent with these credentials yet"* instead (the same two causes Import's
   "Nothing is on the relay for these credentials yet" names, 7.26.0-alpha.2). A screen test on the local relay
   (`test/ui/rw.py` `App(relay=True)`): an empty channel's test says so. The Cloud Sync Key's check characters later
   catch the typo as it's entered.

#### Say plainly what ReaderWrangler works with: US Amazon, Kindle, English, Chrome
<!-- id 20261018-1422b -->

_Why it matters:_ Assumptions baked into the product are nowhere stated — a UK reader, or someone expecting paperbacks, finds out only by failing.

**The facts** (each verified in the code or docs, 2026-10-16; facts 4–5 corrected 2026-11-01)
1. **Amazon's US store only.** Every fetcher talks to amazon.com only, and prices are read as US dollars (details: see
   TODO notes).
2. **Formats** — the library fetch brings in **everything** in your Amazon library, every format (Kindle purchases, samples, Prime, Kindle Unlimited, loans — and print, audio, even a DVD bought on Amazon); series and author adds take Kindle editions only; **the one-book Add Book to Wishlist takes any format** (deliberately — a paperback can hold a place until a Kindle edition exists). Undoing the Kindle-only preference: Someday task "Formats other than Kindle".
3. **The app is in English.** The books can be in any language.
4. **Browsers:** tested on **Chrome**. **Edge** should work (it's built on the same engine as Chrome) — and once the
   browser driver exists (High priority; it runs Edge) it becomes "tested by the automated tests" for real; say so
   then. **Firefox** was confirmed working once, long ago, but isn't regularly tested. Safari is untested. _(Today the
   docs contradict each other — and two of them are false: README / features page "Tested: Chrome, Edge, Firefox"
   (neither Edge nor Firefox is tested), User Guide "Firefox is also fully supported"; SUPPORT-KB "We only test
   Chrome" is right. Fix them all in ONE pass with this task — Ron, 2026-11-01: not a partial fix ahead of it; with
   essentially no visitors yet, nobody is relying on the claim.)_
5. **Fetching and organizing need a computer** (the bookmarklet runs on Amazon's site in a desktop browser). **The
   phone is read-only**: it shows your library and never writes changes (SUPPORT-KB "What is the mobile app?" —
   checked 2026-11-01; the old wording "the phone views and organizes" was wrong).

**Where it goes** (Ron, 2026-10-16; 2 and 5 revised 2026-11-01)
1. A short **"What ReaderWrangler works with"** section in the User Guide (written in the User Guide task, below).
2. **On the landing page, folded into the existing sub-tagline** — e.g. "Import your Kindle library from
   **Amazon.com** in minutes…" — not a new line: the "Open My Library" landing task already adds "Always free · No
   ads · No account needed" under the button, and a third line would crowd the hero. The features page says it once.
3. One question in SUPPORT-KB.
4. A developer list in docs/reference/ARCHITECTURE.md — every spot a future change (another country, another app language) would touch.
5. **Say it at the moment it matters (Law 16)** — when the bookmarklet runs on any Amazon site other than amazon.com,
   it says "ReaderWrangler works with Amazon.com (the US store) only, for now" instead of offering to send the user to
   amazon.com's library page (today's dead end for a UK account — details: see TODO notes). The docs explain it; the
   message catches the person who never read them. The same change for all three bookmarklets → dev and prod together.

Ron's word on the wording first.

#### Safari deletes a library after 7 days without a visit: warn, and help people restore
<!-- id 20261120-1700b -->

_Why it matters:_ Safari deletes everything a site saved — the whole library, folders, settings — after 7 days of
using Safari without visiting that site (WebKit's own page, checked 2026-11-20). Mac Safari users will try
ReaderWrangler whatever we say, and someone who opens it less than weekly loses their organizing (outside review 1,
Risk 10). Every iPhone and iPad browser is Safari underneath.

**Decided** (Ron: "Yes to all, especially the bookmarklet as a breadcrumb", 2026-11-20)
1. **A dialog on EVERY start of the full view in Safari** (Ron, 2026-11-24 — replaces the 11-20 one-line notice):
   the person at risk is the one who works a day or two, then stays away 7+ days — a reminder near the deadline never
   reaches them, and coming back resets the count; we can't tell who will leave, so everyone in Safari's full view is
   warned, every start, while they're here. A stopping box is allowed here by Law 18's exception (the damage can't be
   undone — as for the other-account fetch). **Advice split by device** (Ron): on a Mac — use Chrome, Edge or Firefox
   (their own engines; the 7-day rule is Safari's); on iPhone and iPad — every browser is WebKit, so the fix is **Add to
   Home Screen**, which Apple exempts ("We do not expect the first-party in such a web application to have its website
   data deleted" — webkit.org/blog/10218), and the Home Screen app starts empty, so you restore once. (A Mac "Add to
   Dock" web app: no source says it's exempt — don't promise it.) Against reading it blind (Ron agreed all three):
   - **the dialog does the fix** (Law 20): **[Save Backup now]**, the device's advice (switch browser / how to Add to
     Home Screen), then **[Continue]**;
   - **it shows what changes each time**, so it gets read: *"Your last backup: 3 days ago — 14 changes since."*;
   - **at the danger moment, leaving:** in Safari's full view, with changes since the last backup, closing the tab
     brings up the browser's own "Leave site?" question (its words can't be changed; it stops a casual close).
   Not shown in Safari from the Home Screen (detectable: the standalone flag). **Softens** only once "Restore from
   Cloud Sync" can bring the organization back from the Complete Copy. Facts read 2026-11-24: the 7 days count days
   of browser use; a tap, click or typing on the site resets them; on iPhone/iPad Apple's tracking prevention is on in
   every browser since iOS 14 (secondary sources: simoahava.com, cookiebees.io) — whether the 7-day count bites the
   same way outside Safari is unsettled (thinktecture.com), so treat it as yes. Ties to "Know whether the browser will
   keep your library…" (the status light is red in Safari permanently).
2. **Moved 2026-11-24 to "Know whether the browser will keep your library…", item 6 — now for every browser** (any
   browser may delete a site to free space). Was: **An empty library in Safari:** the getting-started words, plus *"If you've used ReaderWrangler in this browser
   before, Safari may have cleared it — restore your backup file"*; once "Restore from Cloud Sync" exists (in this
   gate), *"or restore from Cloud Sync"* — its copy is kept 90 days after its last update.
3. **Moved 2026-11-24 to "Know whether the browser will keep your library…", item 7 — every browser.** Was: **The
   bookmarklet is the breadcrumb.** It's made at Cloud Sync setup and holds the Cloud Sync Key. Its "open
   ReaderWrangler" button (bookmarklet-nav-hub.js ~381) opens the app with nothing extra today; it adds a mark to the
   address (after `#`, so it never leaves the browser) that says "this person has a bookmarklet" — **never the key**,
   which would land in the browser's history. An empty library plus that mark means the library was lost, for certain:
   say so plainly, with the restore buttons.
- Dropped: a cookie set by the relay to survive the deletion ("a reach" — Ron).
- Ron's word on the wording first. Placed beside "Say plainly what ReaderWrangler works with" (Ron: "OK to launch
  gate").

#### Landing page: "Open My Library" for returning users, and "Always free · No ads · No account needed" under the start button
<!-- id 20261030-1036 -->

_Why it matters:_ A returning user arriving at readerwrangler.com sees "Get Started — It's Free!", a sign-up-style
button, and has to hunt for the way in (the top bar's "Launch ReaderWrangler" is easy to miss — Ron: "My attention is
drawn to the center"). And what makes RW different — always free, no ads, no account — sits in a row further down.

**Decided** (Ron + UX, 2026-10-30)
1. **One adaptive hero button:** a returning user sees **"Open My Library →"**, a new visitor **"Get Started"**. Both
   go to the same app — only the words change, so nobody needs a way to "get" the other one (starting over is Tools →
   Reset App, not this button).
2. **How it knows:** the app writes a small "this browser has a library" marker when it loads one; the landing page
   checks only that the marker exists — locally, nothing sent, the same way it already picks your theme. It never looks
   at the Cloud Sync Key.
3. **Never redirect** a returning user into the app — some come back to read the page or share it (Ron: it "breaks our
   rules"). The top bar's "Launch ReaderWrangler" stays for both.
4. **One quiet line under the button:** "Always free · No ads · No account needed" — the button names the action;
   benefits read better beneath it.
5. **"Always free" is safe** (Ron, 2026-10-30): charging would mean a different product — RW runs in the user's
   browser, has no accounts to bill, and anyone can host it themselves. If hosting costs ever grow, the levers are fair
   limits on cloud storage, donations or hosting your own copy — never a paywall. Say so once in the FAQ.
6. **"No ads" stays honest** because the affiliate support stays disclosed (the "100% free" item's tooltip: "Supported
   by Amazon affiliate links"). That disclosure is also Amazon's requirement — see outside review 1.
7. **Align the trust row** below: "100% free" → "Always free", and consider a "No ads" item, so the two places say the
   same thing in the same words.
8. **Both buttons' tooltips** today read "The app walks you through setup — relay, bookmarklet, and first import":
   wrong for a returning user, and "relay" is a retired word. Give the returning-user button its own tooltip; the
   Cloud Sync task's commit check catches "relay".

**How (technical)**
- Buttons: index.html ~1278 (top bar) and ~1325 (hero, `.cta-buttons`); the trust row ~1424. The theme check near the
  top of index.html shows the pattern for reading the app's local setting. The marker: written by the app when a
  library loads (readerwrangler.js) — a tiny app change, so an alpha + version bump.

#### The Security & Privacy page made specific, and a terms page: what we send where, what we promise
<!-- id 20261119-1548a -->

_Why it matters:_ People's libraries are personal. Before launch the site must say plainly what leaves their computer:
today the security page discloses the visit counter (GoatCounter) but nothing says the app loads its fonts from Google
(Google sees each visitor's address), and the relay's planned "last used" date per cloud library isn't disclosed either.
Its blanket "No personal information collected" (security.html ~111) needs to become specific sentences that are each
literally true. It existed only as a sub-bullet of "Outside reviews before building" (cold review, 2026-11-19).

**Decided** (Ron + Claude, 2026-11-20, outside review 1 — Risks 4 and 5, Questions 8 and 9)
1. **The existing Security & Privacy page (security.html), made specific** — not a new page.
2. **A general statement, then links to theirs:** ReaderWrangler collects no personal information except counts of
   page visits and feature use (GoatCounter); the pages load fonts from Google and code from unpkg and cdnjs, which see
   your visit like any website. Link to each one's own privacy policy rather than describing it — it can't go out of
   date when they change theirs. E.g. *"ReaderWrangler doesn't collect personal information. We count page visits
   and which features get used, with GoatCounter (their privacy policy). The pages load fonts from Google and code
   libraries from unpkg and cdnjs; like any website, those see your visit (their policies)."*
3. **A short "what goes where" table** (Ron: "Yes. perfect"):
   | What | Where it goes |
   |---|---|
   | Your books, folders, tags, notes | Only your browser. With Cloud Sync, also an encrypted copy on our sync server that we can't read |
   | Your Cloud Sync Key | Your browser, your bookmarklet, your backup files. The secret part is never sent to us |
   | What the sync server knows about your copy | An ID, its size, when it was first used and last saved. Never its contents |
   | Your Amazon sign-in | Never leaves Amazon's page. The bookmarklet uses it there, in your browser |
   | Feature counts | GoatCounter: which page, which feature. No cookies |
   | Your email address | We don't have it |
4. **One line for Cloudflare's "are you human" check** at Cloud Sync setup ("Relay worker: one release…", item 11).
5. **A terms section** (Risk 4): what we promise and don't — your library lives in your browser, so a cleared browser
   without a backup loses it; a lost Cloud Sync Key can't be recovered by anyone; always free (Ron: "I might be forced
   to put out a coffee can. But that is still free."); offered for the United States — not without a good reason
   (Ron: "like a volunteer EU privacy expert or lawyer").
6. **The affiliate notice** stays as the footer says it ("As an Amazon Associate, I earn from qualifying purchases").

**Still open:** keep Google Fonts (disclosed) or serve the fonts ourselves (then nothing to disclose) — disclose now,
decide later.

#### An accessibility page: what works, and how to tell us what doesn't
<!-- id 20261120-1700a -->

_Why it matters:_ Ron (2026-11-20): "Handicap access (and accessibility) get short shrift." Keyboard work is in
progress (Polish, "Finish keyboard accessibility") but nothing tells a person what works or how to reach us when it
doesn't (outside review 1, Risk 15).

**Decided** (Ron, 2026-11-20): a quick page before launch — what works today (keyboard use, the themes including high
contrast), what doesn't yet, and an invitation to report accessibility problems **by email or by opening an issue on
GitHub**. Linked from the site's footer beside Security & Privacy. Ron's word on the wording first.

#### Outside code libraries: exact versions, integrity checks, and a policy that keeps the page from sending your key anywhere
<!-- id 20261014-1030ai -->

_Why it matters:_ Every outside script runs inside the page that holds your Cloud Sync Key — the key that, since
7.25.0, protects your cloud library. An unannounced update could break the app overnight; a tampered or malicious copy
could read the key and send it away.

**What's loaded today** (checked 2026-11-01 — six of nine unpinned)
| Library | Where | Pinned? |
|---|---|---|
| React, ReactDOM | the app (readerwrangler.html ~128–129) | `@18` — any 18.x |
| marked | changelog.html | no version at all — always the newest, even a new major |
| img-comparison-slider (script + style) | index.html | `@8` — any 8.x |
| qrcodejs 1.0.0, html5-qrcode 2.3.8 (phone, on demand — mobile.js ~2442) | the app, the phone | yes (no integrity) |
| GoatCounter's `count.js` | the app, the home page | no (outside review 2) |

**No longer loaded from outside (since 7.27, the app built ahead of time):** Babel and Tailwind run only in our build,
pinned exactly — `tools/build/package.json` (Babel 7.29.7, Tailwind 3.4.17) and its `package-lock.json` (each package's
download and fingerprint), installed once with `npm ci`, which installs exactly the lock file; the result (`dist/`)
is served from our own site. Ron asked (2026-11-25) whether a rebuild fetches the newest — it doesn't.

**Decided** (Ron + Claude, 2026-11-01/02, in the TODO review)
1. **Exact versions** for all six (Tailwind's CDN takes an exact version in its address). Its lasting fix stays the
   "Faster loading: build the app ahead of time" task (Before launch, right below — moved up 2026-11-03).
2. **Integrity checks** (`integrity` + `crossorigin` on every outside script and stylesheet, and on the phone's
   on-demand loader): the browser refuses any copy that differs from the one we checked. What they DON'T do (Ron): they
   can't prove the checked copy is safe — they protect against tampering *after* we pin (e.g. the 2024 polyfill.io
   takeover, which served malicious code to 100,000+ sites that had trusted that CDN for years).
3. **For the first copy** — the practical limit of what can be known: prefer old, widely used versions; check each
   exact version's security advisories; verify the copy matches the release npm recorded.
4. **A content security policy on our pages — corrected 2026-11-25 (outside review 2, item 5; Ron agreed): it does NOT
   keep a bad script from sending your key anywhere** — the relay (a script can write the key into a cloud library of
   its own) and GoatCounter (an event name is free text) take anything sent. Describe it honestly, here and in public:
   *"limits what an injected script can load and where it can send."* With every script served from our own site
   (item 6), the policy can say **"scripts only from here"** — its one strong, simple form. Originally: (a `<meta>` policy tag;
   GitHub Pages can't send headers): the page may contact ONLY the servers we list — our two relays, GoatCounter,
   Amazon's image servers, and the library CDNs — so a malicious library could read the key but couldn't send it
   anywhere (background requests, images, beacons, form posts are all refused). Tested with the browser driver
   (violations show in the console) so nothing legitimate breaks.
   - Its honest limits: while Babel compiles our code in the browser, the policy can't fully restrict which scripts
     run; and no policy stops a script from replacing the whole page with an outside address carrying the key — the
     `navigate-to` rule for that was dropped from the standard in 2022 and no browser supports it (Chrome had it only
     behind an experimental flag, then removed the code — checked 2026-11-02; so it's not included: it would do
     nothing). That attack is visible — the user sees ReaderWrangler vanish — a much worse deal for a thief than
     silent theft.
   - The bookmarklet (on Amazon's pages) can't use our policy — Amazon's page sets its own — but it loads only our own
     three scripts, no outside libraries. The relay uses no libraries (one self-contained file; `wrangler` is a deploy
     tool), serves data not pages, and never receives the passphrase.
5. **A commit check** — and, with self-hosting (Ron, 2026-11-26, review 2 item 7): **a change to a served library
   file needs a CHANGELOG line that explains it**, so an infected copy can't slip in unnoticed. Originally: refuse an
   outside script or stylesheet without an exact version and an integrity hash, and a
   page without the policy — so a new page can't quietly regress.
6. **REVERSED 2026-11-25 (Ron, outside review 2 item 5): serve every outside script from our own site** — React,
   ReactDOM, qrcodejs, html5-qrcode, the picture slider, marked, GoatCounter's `count.js` (GoatCounter supports it):
   seven files across four pages, each copied at an exact version and checked against npm's recorded release. New
   facts the 11-02 weighing didn't have: it's every page of the site, not one; each outside host sees every visitor's
   address — a privacy line to write and keep true; and it allows the "scripts only from here" policy. Exact versions
   and integrity values (items 1–2) still apply to anything left outside. **The human check (Turnstile) is the one
   script that can't be copied** — see "Cloudflare's 'are you human' check". Was: **No self-hosting** (considered and
   dropped, Ron 2026-11-02): it protects against later tampering no better than
   integrity checks; its gains — the app keeps loading if a CDN is down, and a CDN doesn't see visitors — are
   availability and privacy, not security, and don't justify maintaining copies of other people's files.
   (Evidence, 2026-11-17: in a deliberate load test, one page start failed because ReactDOM's download from unpkg.com
   didn't arrive — "ReactDOM is not defined", the app never opened. A test-machine effect, not a CDN outage; it doesn't
   reopen this decision, and the tests now treat a failed library download as the machine's trouble. Ron, 2026-11-17:
   "We've discussed it in the past" — already filed here.)
7. Show all of it to **outside review 2 (security)**.

**How (technical)**
- Old review item 6h. The servers the app talks to: both relay workers (`readerwrangler-relay*.readerwrangler.workers.dev`),
  GoatCounter (its script + endpoint), Amazon's image hosts (covers) — list them from the code when building, not from
  memory.

#### Move to Cloudflare's $5/month plan around launch
<!-- id 20260828-0000 -->

_Why it matters:_ The free plan supports only a handful of users.

**When (the launch gate, 2026-11-19): before the first public post, not "around launch"** — the free plan's 1,000
writes a day are shared by every user, and a handful of first fetches on launch day could stop sync for everyone; the
50% alert fires after that has already happened. (The cold review also noted anyone can open new cloud libraries — only a
per-copy limit exists today; outside review 1 put the fix in "Relay worker: one release of changes", items 10–12.)
**Outside review 1 (2026-11-20): before anyone outside the household has the link** — not just before the first post;
and **set Cloudflare's billing alert** when upgrading. On the paid plan, a flood of junk requests becomes a small bill
instead of an outage for everyone (1 million writes a month included, against the free plan's 1,000 a day).
**Storage can bind too (measured 2026-11-20):** a library of 3,270 books takes about 72 MB on the relay (four
versions of ~18 MB) — so the free plan's 1 GB holds only about 14 libraries that size, and item 1 below ("writes, not
storage, are the binding limit") may no longer hold. On the paid plan it's cheap: 1 GB included, then $0.50 per GB a
month.

**What we know** (RELAY-ECONOMICS.md, 2026-08-28)
- After 7.5.0's savings, the flat $5 plan covers about 250 users like you; the free plan about 6–10 — and it's shared between production and dev.
- So this is now just the act of upgrading at the right moment, at or shortly before launch.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review — the nightly trend file now gives real numbers)
1. **Upgrade at launch, or earlier when the numbers say so — whichever comes first:** the relay's threshold alerts
   (25/50/75/90%) already email; "the writes alert at 50% fires on two days in a week" is the trigger. Writes, not
   storage, are the binding limit (1,000 a day for the whole account).
2. **Re-check the "≈250 users on $5, 6–10 on free" estimate against the trend file** (`relay-trend.csv`, kept with
   the TODO notes, nightly since 2026-10-20) before upgrading — the August model predates the nightly cleanup's deletes,
   signed writes (one registration write per channel, a few extra reads) and "Refresh all books" (a heavy day).
3. **Dev shares the free limits** — release day 2026-10-31, the tests on dev used 23.6% of the account's daily writes in
   an afternoon; a test day plus a busy user day could hit the cap and stop production syncing for everyone. Until the
   upgrade, "run the relay tests locally by default" ("Relay worker: one release…", item 5) is what protects
   production.
4. **Check Cloudflare's current prices and limits when upgrading** — not the August numbers.

---

#### Ron's accounts: a second sign-in step on GitHub (it now guards the site, Cloud Sync and email)
<!-- id 20261120-1700c -->

_Why it matters:_ The bookmarklet loads its code from readerwrangler.com into each person's signed-in Amazon tab, so
whoever takes over the accounts behind the site could serve code there (outside review 1, Risk 6). Checked by Ron
2026-11-20: GitHub (hosts the site) — password only; Porkbun (the domain) — a code by email; Cloudflare (Cloud Sync)
and Resend (email) — both sign in **through GitHub**. So one GitHub password guards three of the four.

**Decided** (Ron, 2026-11-20): no passkeys or hardware keys (a passkey adds nothing while the account still recovers
by password). **Ron is holding off on a second step for now** — a slow text message at every sign-in is the cost; Claude
may keep reminding him ("You can continue to bug me (really - I'm giving you permission)"). The least-fuss option
when he's ready: GitHub Mobile's tap-to-approve on the phone. Meanwhile, Ron's own steps:
1. Save each service's recovery codes in the password manager.
2. Check that Porkbun's domain lock (the block on moving the domain to another registrar) is on.
3. The email account the services send codes to is the real master key — keep it protected.

**When:** before launch — the reminder lives here, not in anyone's memory.

#### Dark theme: fix the unreadable bar and the light strips
<!-- id 20261007-0000a; merged 20261014-1030ab -->

**In the launch gate (Ron, 2026-11-19):** if you've never picked a theme, the app follows the computer's dark setting (readerwrangler.html, the theme script at the top) — so every newcomer on a dark-mode computer starts in Dark, and after their first fetch meets the unreadable bar. Built with "Site pages use the shared named colors…" (below, part of this task).

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
4. **Shadows the same way — a few named levels** (Ron + Claude, 2026-11-04 — merged from "Leftover desktop polish: one
   shadow direction", whose origin was lost): e.g. menu, dialog, floating card, each defined once per theme, so the
   direction can't drift and the dark themes soften them in one place (a dark-on-dark shadow looks muddy). Today: ~57
   from Tailwind's ready-made set (all straight down — not the problem) and ~49 hand-written (26 in readerwrangler.js,
   23 in readerwrangler.css) — the commit check lists the hand-written ones as it does fixed colors.

**How (technical)**
- Dark remaps Tailwind classes in readerwrangler.css (`[data-theme="dark"] .bg-white {…}` etc.).
- Relay bar: inline `linear-gradient(135deg, #dbeafe, #ede9fe)` with `color: var(--text-primary)` (readerwrangler.js ~9360).
- Outer container: `bg-gradient-to-br from-blue-50 to-blue-100` (~8992) — gradient classes aren't remapped; the Active bar's `mb-4` gap shows it.
- Auto-Organize preview: `#f1f3f5`, `#fafafa`, `#e5e7eb` (~12009 / 12018 / 12046).
- The check (beside `git-hooks/check-names.js`, run from `git-hooks/pre-commit`): flag inline `background: '#…'`, light `linear-gradient`, `from-*/to-*` classes and Tailwind color classes with no theme mapping, in readerwrangler.js / mobile.js / readerwrangler.css and the site pages (index, features, tutorials, security,
  changelog, reset — decided 2026-10-22; NOT the fetchers / nav hub); and flag any `var(--name)` that isn't defined for all four `[data-theme]` values. Move each hit to a CSS variable (e.g. `var(--bg-surface)`); retire remap rules as their classes go.
- Themes: readerwrangler.css `[data-theme="dark"|"hc-light"|"hc-dark"]`; phone adds its own variables at mobile.js ~57–59.

##### Site pages use the shared named colors, so all four themes work (the security page's high-contrast light first)
<!-- id 20260909-0000 -->

_Why it matters:_ The site pages are a reader's first look at RW. Today each one fixes its themes with its own override
rules, so any color it misses stays wrong in some theme — and two pages have no themes at all.

**Done already** (2026-09-09)
- The security page's wrong statements were fixed, plus its navigation, and its Dark / High-contrast dark themes.

**Decided** (Ron, 2026-10-22, in the TODO review)
1. **Fix by naming colors, not by adding override rules** — the same decision as "Dark theme: fix the unreadable bar
   and the light strips" (Decided 3). The security page's High-contrast light is the first page done this way, not
   another override.
2. **All four themes on every site page** (Light, Dark, High-contrast light, High-contrast dark), computer and phone.
3. **The Dark theme task's commit-time color check covers the site pages too**, so a new fixed color on a site page
   is refused just like one in the app.

**What's there today** (checked 2026-10-22)
- index, features and tutorials: all four themes, each through its own page's override rules.
- security: Dark and High-contrast dark only (override rules); High-contrast light is missing.
- changelog and reset: no themes at all — they always show Light.

**How (technical)**
- Each page has its own inline `[data-theme=…]` rules and its own copy of the theme-picking script (reads
  `readerwrangler-theme`, falls back to the system's dark setting). Move both into one shared file the pages load:
  the named colors, defined once per theme, plus the one script. Each page then keeps only its layout.
- Whether that shared file is readerwrangler.css's color names or a small site file built from the same names:
  decide when building — the names must be the same ones the app uses.
- Pages: index, features, tutorials, security, changelog, reset (readerwrangler.html is the app — the Dark theme
  task).
- **Then write RW's own `DESIGN.md`** (2026-10-31, from the awesome-design-md idea — RW's own look, never another
  brand's): the named colors for each of the four themes, typography, components, do's and don'ts — one source for
  Claude, the outside reviewers and any future contributor. Keep it in step with the named colors (the commit check
  that verifies every name is defined in all four themes can verify DESIGN.md lists them too).

#### User Guide: rewrite it around Searches, Book Lists and Folders, as a page you can reach from Help
<!-- id 20260910-0000c; merged 20261014-1030bd, 20261014-1030o, 20261014-1030bg -->

_Why it matters:_ The guide never mentions Book Lists (checked 2026-10-22: 0 times in 455 lines), and no reader can
find it — it's on the site only as GitHub's plain, unthemed, unlinked copy (`readerwrangler.com/USER-GUIDE.html`); the
Help menu has How To Use, Watch Tutorials and Keyboard Shortcuts, but no guide. The same file is what the support
assistant will read, so it has to be complete and stay current.

**Decided** (Ron, 2026-10-22, in the TODO review — "go with your ideas all the way")
1. **One file: USER-GUIDE.md, for people, the support assistant and anyone pasting it into their own chatbot.** It
   stays Markdown: well-headed, self-contained sections suit the assistant (an HTML page would mix menus and theme code
   into what it reads).
2. **A themed page shows it:** `guide.html` loads USER-GUIDE.md and displays it, using the site pages' shared named
   colors ("Site pages use the shared named colors…", part of the Dark theme task), so all four themes work. Linked as **Help → User Guide** in the app, and from the site
   pages' links and README. How To Use stays as the short first-run version and links to the guide for more.
3. **One FAQ, inside the guide** — not a separate faq.html (merged the "Create a FAQ page" task). Sections: Security /
   Privacy, Data / Backup, Troubleshooting, Library, General; question-shaped entries (what users actually type). The
   footers and README link straight to it. Two FAQs would drift apart, as the browser claims already have.
4. **Every feature is covered — by a check, not by memory.** Every place a user reaches a feature carries a **guide
   section name** pointing at the guide (e.g. `guide="move-books"`) — a name, never text, so nothing is written twice:
   menu-bar items (20), popups including right-click menus (76), dialogs (40), the confirm-style boxes (~19), and the
   keyboard-shortcut list. A commit check refuses (a) any of those without a guide name — a place that truly needs
   none says so with a reason (e.g. a picker inside a dialog) — and (b) any guide name with no matching section in
   USER-GUIDE.md. It also reports guide sections nothing points at (a removed feature's leftovers). Counts from
   2026-10-22.
5. **The first run of that check is the sweep:** the list of places with no guide name is the rewrite's outline.
6. **A "?" in each dialog** opens the guide at its section — cheap once the names exist; real help where you are.
7. **Behavior with nothing to click** (a book leaving its last folder goes to the Inbox; the drag rules) can't be caught
   by the check. When the new guide ships, add to the release checklist: the help-notes comb also covers the guide —
   every CHANGELOG line gets a guide check.
8. **Build it last in Before launch** — it describes behavior still being decided or built. Wait for: "Cloud Sync:
   rename Relay, show one Cloud Sync Key, and 'make a new key' retires the old one" (so the new names land once), "Move and copy
   books anywhere — folders, Book Lists, All Books, Searches", and "The Delete key deletes the folder you're in — not
   the folders you selected".

**What it should cover**
- The four places: All Books / Searches / Book Lists / Folders — what each is for, and "when to use which".
- **"One book, many places"** (merged the "Wording pass: explain Book List shortcuts and Linked Copies" task): the
  same book can be in several folders and Book Lists — not a duplicate; **All Books and Searches are views** (Ron:
  nothing is put into or taken out of them); folders file books, Book Lists are free-form. Draft text and the facts
  behind it: docs/design/TERMINOLOGY.md. **No "shortcut", no "Linked Copies"** — both retired 2026-10-22 (why: same
  doc); the screens already say "Remove from this list", and stay as they are.
- **The Book List ↔ Folder pattern:** structure lives in Folders; to-read queues live in Book Lists.
- "Getting books out of the Inbox → use a folder, not a Book List."
- **Fields you can't filter by:** show the other way, e.g. List view → add that column → sort (merged task).
- **"What ReaderWrangler works with"** (from the "Say plainly…" task above).
- **Starting over** (Ron, 2026-10-30): Tools → Reset App — when to use it, what it clears and what it keeps; switching
  to a different Amazon account; clearing all books and organization to start from scratch. The old guide has a
  Reset App section and an FAQ entry; keep them, corrected.
- A glossary and a "what ReaderWrangler doesn't do (yet)" section (the support assistant plan's two best defenses
  against made-up answers).
- **FAQ: "How is ReaderWrangler different from Readwise Books, Goodreads or StoryGraph?"** (Ron, 2026-10-30). They are
  for *reading* (where you read, track sessions, rate, buy — Readwise Books sells ebooks); ReaderWrangler **organizes
  the Kindle library you already own** — nested folders, series, Book Lists, tags, Auto-Organize, wishlist prices — and
  never sells or displays books. No account; it runs in your browser. They can be used together. Also a line for the
  "doesn't do" section: RW doesn't open or read books.

**Sources**
- Examples of taming a backlog: docs/design/WORKFLOW-PATTERNS.md.
- Facts and FAQ: docs/design/SUPPORT-KB.md (mined 2026-09-10 from every session back to May, and kept current at each release).

**How (technical)**
- "Holds vs. points at" = the custodial vs. supplemental model.
- The live site serves the raw `USER-GUIDE.md` (checked 2026-10-22: `text/markdown`), so `guide.html` can fetch and
  display it with a Markdown library from a CDN (exact version, integrity check, inside the page's security policy —
  see "Outside code libraries: exact versions, integrity checks, and a policy…"). Prove that works on dev before
  relying on it. Decide then whether GitHub's automatic
  `USER-GUIDE.html` copy should be hidden or point at guide.html.
- The guide-name check sits beside `git-hooks/check-names.js`, run from `git-hooks/pre-commit`; the guide name is a
  prop on `MenuBarItem` / `<Dialog>` / `<Popover>`, an argument to the confirm-style boxes, and a field in the
  shortcut list. Section names = the guide's headings' anchors.

##### A glossary page on the site, built from GLOSSARY.md
<!-- id 20261112-1430 -->

**Part of the User Guide task (Ron, 2026-11-19):** small, and built from a file we already keep.

_Why it matters:_ People meet words like "Cloud Sync Key" and "Book List" with no one place that says what they mean;
and a page kept by hand beside GLOSSARY.md would drift from it. One source, shown prettily (Ron, 2026-11-12).

**Decided** (Ron + Claude, 2026-11-12)
1. **Built from the file:** `tools/build.py` turns GLOSSARY.md into a page (the way the app is built ahead of time since
   7.27.0) — nobody edits the page; the commit check refuses a stale copy, as it does for `dist/`.
2. **Only what's decided:** the Decided rows' term and meaning — not the proposed ones, the decision records or the
   words people never see.
3. **Styled like the other site pages** (the shared named colors, so every theme works), linked from Help and the site's
   footer.

#### Remind me when my last backup is getting old
<!-- id 20261104-1024a -->

_Why it matters:_ The one real disaster is a lost or wiped PC with no recent backup — and nothing reminds you today
(checked 2026-11-04). The cloud library isn't a full backup yet (see "Keep your tabs and browsers in step…").

**Decided** (Ron + Claude, 2026-11-04 — instead of emailing users about idle cloud libraries, which would have ended the
"the server holds nothing readable about you" promise)
1. When your last saved backup is more than about a month old, the status area shows a quiet note: *"Last backup: 47
   days ago — Save Backup"* — one click; never a pop-up (Law 18).
2. The app records when you last saved a backup (this browser); a Restore counts too.

#### A public demo library from Amazon's best-seller lists (nothing personal)
<!-- id 20261104-1613 -->

_Why it matters:_ The sizzle reel, the landing page's pictures and the User Guide's screenshots need believable books.
Today's demo library is made from Ron's own purchases — public by his choice, but it shows what he owns. Best sellers
and classics are recognizable, show off Auto-Organize (real series, authors with many books), and are nobody's
library.

**Decided** (Ron + Claude, 2026-11-04)
1. **Read the lists from the page Ron is viewing:** Amazon's best-seller pages (the NYT 2026 list — 7 pages — Kindle and
   Classics categories) carry each book's ASIN, title and author in the page itself. Ron opens a page and runs one
   **read-only console snippet** that collects them — no extra requests; next page, run again. (No saving pages.)
2. **Depth: "More like this"** (the recommendations request probed 2026-11-03) turns each book into ten more — together
   with the NYT pages, toward **~3,000 books** (Ron): also a selling point on camera ("your whole library, organized").
3. **Details in one paced run:** the fetcher's own batch lookup (30 books per request) fills in covers, descriptions and
   ratings; the snippet writes a file. Paced, with the human-check stop in mind — every request read-only, of a kind
   the fetcher already makes. Request details: see TODO notes when building.
4. **A generator on Claude's side** packs it into a demo backup — folders by author and series, Book Lists, a few books
   in the Trash and hidden — the same way the test libraries are generated.
   - **It must pass Restore's backup check** (backupCheck.js, 7.26.0; Ron's rules, 2026-11-08): Restore replaces
     everything but the Cloud Sync credentials (merged only after asking), so a part that's missing or empty becomes
     empty, and a backup is refused only when that leaves the library unusable. Required, each the right kind: the
     backup marker (`isBackup: true`), a `2.x` version stamp, the list of books (`books.items`, a list), and the tag
     list (`tagRegistry`, a table) whenever any book has a tag. Folders, Book Lists and Searches: write them (an empty
     list is fine) — a missing one restores as none (with no folders, every book lands in the Inbox). Any part that's
     written must be the right kind (collections' `items` a list, the view settings a table).
   - **Write every part today's Save Backup writes**, and none of the obsolete ones ("Remove code left over from older
     versions…", Polish: no `hiddenInstances`, `pinnedTagFolders`, `dataSource`, `lastSyncTime`).
   - **No Cloud Sync credentials** in the file (the private-values commit check refuses them; the old demo files' were
     revoked 2026-10-31).
   - **Each book**: what "Restore checks every book, folder and list inside a backup…" (the launch gate) will
     require — an ASIN, unique; each folder an ID, a name, a parent and a list of books.
   - **Test it the way a person would:** a screen test restores the generated file and checks the counts and folders.
5. **It replaces the demo library made from Ron's purchases** (`readerwrangler-demo-library*.json` and the demo filter's
   list in `tools/demo-library/`) — retire those once the reel no longer needs them.
6. **Covers:** real ones from Amazon on camera — thumbnails, plus one or two full size in a book window. Ron's call
   (2026-11-04): fair use as he sees it, and he accepts the risk of a cease-and-desist; listed for outside review 1 so
   it sees the whole picture.
- **Built before "Screen capture pass…"** (just below), which records with it.

#### Screen capture pass: the sizzle reel, the landing page's before / after, README's old video
<!-- id 20261014-1030bc; merged 20261014-1030al -->

_Why it matters:_ What the public sees of the app is stale: the landing page's before / after pictures predate the
redesign, and README links a walkthrough video (39 MB) of the old way of organizing. The sizzle reel (DEMO-LIBRARY-PLAN.md,
"Video 0": 20–30 s, rapid cuts, music, no voiceover) was planned but **never made** — Ron: "I think the sizzle reel
will be a seller."

**Decided** (Ron + UX, 2026-10-23, in the TODO review; merged "Refresh the landing page's before / after screenshot")
1. **One pass, one sitting:** the sizzle reel, the before / after pictures, the preview thumbnail — same demo library,
   same build. The User Guide's screenshots come from the same pass.
2. **Last in Before launch, with the User Guide** — nearly everything on screen is about to change (Cloud Sync names,
   drag labels, site-page themes, the Send buttons); recording sooner means recording twice.
   **Changed 2026-11-19 (Ron: the reel is needed AT launch; "I'm expecting you to be able to make the sizzle reel
   now"):** build the pipeline and a first draft EARLY, on today's screens — every take is scripted, so a screen
   change means re-running the script, not re-shooting by hand — and the final cut once the launch work has settled
   the screens. Ron picks a royalty-free music track; Claude cuts to it (Claude can't hear it or judge its license).
3. **If the outside newcomer review runs** ("Outside reviews before building", review 4), write the reel's script after
   it — it may change what the landing page needs to say, and the reel is the landing page's opening.
4. **README's old walkthrough video: remove it** (link and file), not replace it.
5. **Use the public demo library** — "A public demo library from Amazon's best-seller lists" (just above), built
   first; Ron's real library never appears on screen. (Until then: today's demo library and the fetcher's demo filter.)
6. **Keep the reel in the plan** — though Ron dreads making it (the tutorials were "super tedious", which is why they
   were cancelled; the support assistant replaces tutorials 2–8).

**Approach note** (Ron + Claude, 2026-11-03 — discussed, to confirm when this comes up; the answer to Ron's dread of
the tedious part)
1. **Scripted takes:** the browser driver ("Carry over the utilities project's improvements…") plays the shot list on
   the demo library — real clicks, drags and menus, identical every time; a UI change means re-running, not re-shooting.
   This tips that task's "Playwright or copy `drive_page.mjs`?" toward **Playwright**, which records video itself.
2. **Assembly by Claude:** FFmpeg (cuts, joins, fades, titles, captions, even sound levels) — or Remotion (video built
   from the same kind of code as the app, so title cards can use its real look). Claude can't watch video or hear
   sound directly, but can check cuts frame by frame as pictures.
3. **Sound placement: Earshot** (github.com/Leonxlnx/earshot, MIT, runs on the PC) turns audio into text Claude can
   read — what a sound is, exactly when events happen, whether sound lines up with picture — plus a bank of 201 sound
   effects. Its own limits: no taste, no licensing judgments. **Before using:** it was version 0.1.0 on 2026-11-03 and
   connects to Claude as a tool server — read it and pin an exact version (our outside-code rules); leave its optional
   critique (sends audio to Google's Gemini) off.
4. **Taste stays Ron's:** he watches drafts and says what's wrong.
5. **To decide then:** this mostly replaces DaVinci Resolve for assembly (Claude can't drive Resolve's screens).

**Spec:** docs/design/DEMO-LIBRARY-PLAN.md (Video 0 shot list, the demo library, the fetcher's demo filter);
docs/design/VIDEO-PRODUCTION-GUIDE.md (tools); the demo prep scripts: `tools/demo-library/`.
**Video work stays outside the repo** (e.g. `Documents\ReaderWrangler-video\`; decided 2026-11-02 when the old
`tutorials/` work files — 200+ MB of clips, narration, Resolve projects and a saved Amazon page with account details —
were deleted as out of date): one stray `git add` must never be able to commit them.
**Tool survey 2026-11-03** (docs/design/TOOL-SURVEY.md): takes with Playwright for Python's `page.screencast` (chapter cards, a visible
cursor, drives the installed Edge); assembly with FFmpeg or Remotion (free for individuals; render from the command
line — browser-side rendering reports usage); Earshot only after vetting and pinning a commit.

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

**Decided** (Ron + Claude, 2026-11-01, in the TODO review)
0. **Part of the regression library** (docs/design/TESTING.md, 2026-11-04): these suites are its pre-launch data gate,
   run by the same runner and tiers.
1. **Outside review 3 (data safety) comes first** — it attacks what we didn't think of; its findings become test cases,
   rather than writing suites 2–4 now and patching them after ("Outside reviews before building", High priority).
2. **The relay suite half-exists:** `relay/test-phase1.mjs` (59 checks: torn saves, fallback, cleanup guards…) and
   `relay/test-signed-writes.mjs` (22: signatures) count toward "relay behavior"; add only what's still uncovered.
3. **One command, in Python** (Ron's scripts rule) — e.g. `tools/run_tests.py`: the unit suites, then a LOCAL relay
   (`npx wrangler dev --env dev --local`) and both relay tests against it, then stop the relay by its exact process
   id (Law 5). Dev only as a final check (it spends the account's shared write limit).
4. **The fast suites become a commit check:** a commit staging `bookMerge.js`, `bookFields.js` or `organizeEngine.js`
   (and so on, module → its test file) runs that module's tests and refuses on a failure — seconds, every time; a
   suite that runs only when remembered is discipline, not a mechanism.
5. Option, not a requirement: once the browser driver exists (High priority), flows like Restore and Import mapping
   can also be tested through the real screens, not only the functions underneath.


### High priority

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

#### Rebuild the old-style message boxes as standard dialogs
<!-- id 20261014-1030ak -->

_Why it matters:_ "Drag any dialog out of the way" (next) must work for these boxes too — done after it, dragging gets
built and maintained twice (Law 5); done first, once, for everything. And every dialog gets one look.

**What's there** (counted 2026-11-02)
- The message boxes — OK/Cancel, type-a-name, progress, choice, "Owned Book" — are hand-built page elements, used in
  about 47 places (info 19, confirm 16, type-a-name 8, progress 5, choice 3, delete-warning 2).
- Since 7.18.0 they behave like every other dialog (Esc, ✕, key blocking), but keep their own hand-built look.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review — moved up from After launch / Dialog look)
1. **Option A:** one shared piece shows each request as a standard dialog; the ~47 call sites stay unchanged; removes
   about 300 lines of hand-built code. Costs a visual check of all 47 — the browser driver can open each and screenshot it.
2. **Before "Drag any dialog out of the way"**, and before the new boxes being designed (the Cloud Sync task's "Make a
   new Cloud Sync Key?", the Disconnect window, the Reset App message) — so they're standard dialogs from day one.
3. When it ships, update CLAUDE.md's dialog rule (it calls this "a low-priority TODO").

**How (technical)**
- `showInfoDialog`, `showConfirmDialog`, `showInputDialog`, `showProgressDialog`, `showChoiceDialog`, `showDeleteWarningDialog`, rendered as `<Dialog>`s by a React "dialog service"; callers keep `await showConfirmDialog(…)`.

#### Drag any dialog out of the way
<!-- id 20260928-0000 -->

_Why it matters:_ Dialogs sometimes cover what you need to see; dragging them aside is a habit from Quicken.

**Order:** after "Rebuild the old-style message boxes as standard dialogs" (above) — so dragging is built once, for
every dialog (2026-11-02).

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
- "Every dialog" covers two kinds: the standard dialogs, and the older message boxes (OK/Cancel, type-a-name, progress; about 45 places use them), which are built differently. Drag must work in both — or, as decided, the message boxes are rebuilt as standard dialogs first ("Rebuild the old-style message boxes as standard dialogs", just above), so drag is built once.
- Today a click anywhere outside the top dialog closes it, including on a dialog showing through underneath. Point 5 changes that rule, so test it carefully.

**How (technical)**
- Build drag once in the shared `<Dialog>` (readerwrangler.js ~61) so every dialog gets it at once. The old per-dialog drag code (`dialogDrag`) is already gone.
- Names from the 2026-09-28 decisions: a `cursor:move` affordance; the off-window opt-in is a `dragBounds:'free'` option.
- Message boxes share their window chrome in `attachDialogDismiss` (readerwrangler.js ~237); add drag there.
- A click on a lower dialog actually lands on the top dialog's full-window background layer (readerwrangler.js ~69–71). The background-click close must ignore clicks that fall over another dialog (`document.elementsFromPoint` under the layer).
- "Not selectable text" (point 6) reuses the 7.19 Ctrl+A area marks: `data-select-text` (text) and `data-select-items` (checklists) — readerwrangler.js ~55–60 — plus inputs, buttons, links, lists. No second list to keep in step.
- New user feature, so it gets its own branch and release.

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

#### Every edit rewrites the whole library in storage
<!-- id 20261110-1734 -->

**First, measure (the launch gate's review, 2026-11-19):** time one save with 10,000 books. If it takes more than about a second, this moves into the launch gate (a stranger's laptop would feel broken); if not, it stays here.

_Why it matters:_ Changing one book — a tag, a rating, a move — saves all 3,270 books again (the book store is cleared
and refilled each time, ~0.9 s on Ron's PC): slow work after every change, and a full rewrite is a needless chance
for something to go wrong. Found 2026-11-10 while fixing the load's save ("Faster loading").

**What to look into**
1. `saveBooksToIndexedDB(updated)` is called from more than 60 places with the whole list; it clears the store and
   adds every book (storage.js). The class needs a site map first.
2. Likely shape: one save that writes only the books that changed (the store keys books by id) — the same "compare
   with what's stored" idea as the load's `saveBooksIfChanged`, or the callers say which books they changed.
3. Keep the write lock and the one-transaction safety (no moment where a reader sees half a library).
4. **Discussed 2026-11-10 (Ron + Claude):** the save finds the delta itself — a changed book is a new copy (the app
   doesn't edit books in place), so "not the same copy as last saved" costs ~1 ms for 3,270; only those are written,
   removed ones deleted, in one transaction. Ron: **also change the 60 places once to call one common function** —
   most repeat the same pattern (`setBooks(prev => { const updated = …; saveBooksToIndexedDB(updated); return
   updated; })`), so one `updateBooks(change)` (the state update + the save, the delta inside it) is the chokepoint,
   and a new call site can't forget the save. Claude agrees: both together. First the site map (does every site make
   new copies?), a contributor-mode guard that compares by content now and then, and a test that edits and reloads.

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

#### The left pane, one release

Pins and sorting for Book Lists and Searches, a type-to-filter box, and the jump buttons all change
the left pane's chrome — decided as one release (2026-10-16 / 10-22) so it's designed once. Gathered here 2026-11-04
(TODO scan); the jump buttons came from Small fixes (and gained the right pane 2026-11-06, one shared component). Its
keyboard part is item 4 of "Finish keyboard accessibility".


##### Book Lists and Searches: pin and sort them like Folders
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

##### A type-to-filter box for the left pane
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

##### Jump-to-top / bottom buttons by the scrollbar, in both panes
<!-- id 20261014-1030aa -->

_Why it matters:_ They sit at the bottom left today, not where you'd look for them, and the right pane, the long
list of books, has none.

**What you see**
- Both jump buttons (to top / to bottom) sit at the bottom-left of the left pane. You expected top-at-top and bottom-at-bottom, by the scrollbar.
- They're pinned to the window, not to the folder list (readerwrangler.js ~18117, `fixed left-2 bottom-8`): they show
  on the Welcome screen, where there is no folder list, and their height above the status bar is a guess (checked
  2026-11-06, with the 7.25.1 status-bar fix; Law 19's corollary).
- The right pane (the books) has no jump buttons at all.

**Decided**
- No per-section jumps (Searches / Book Lists / Folders) — collapsing sections already handles that.
- (Ron + UX, 2026-10-22) **▲ at the top, ▼ at the bottom, both at the right edge by the scrollbar** — where scroll
  controls live everywhere else (Ron's own expectation). Not the single "back to top" option: the pane is long at both
  ends.
- **Floating over the pane's edge**, so they never push the list: ▲ shows when you're not at the top, ▼ when you're not
  at the bottom, neither when the pane doesn't scroll. (Not the menu rule's case — a floating helper shifts nothing,
  and a scroll button with nothing to scroll is clutter.)
- **Home / End do the same jumps** — overlaps "Finish keyboard accessibility" (Polish).
- (Ron, 2026-11-06) **The right pane gets them too**, by the same rules — it's the long list (3,270 books in Ron's
  library). There, ▲ sits just below the column headings (List View) and ▼ just above the horizontal scrollbar.
- **One floating component for any scroll area** (Claude, 2026-11-06): the left and right panes share one implementation
  and one placement rule, each button positioned inside its own pane (never against the window), so it appears only
  with that pane and never depends on the status bar's height.
- **Tests:** a layout test (`test/ui/test_layout.py`, with the driver's `covered_scroll_boxes()`): the buttons never
  cover a scrollbar or the column headings, at two zooms; ▲ / ▼ show and hide by scroll position; none on the Welcome
  screen.
- **Build with the left-pane release** (pins + the filter box + the section overview — "Book Lists and Searches: pin
  and sort them like Folders"), so the pane's chrome is decided once and the filter box and ▲ don't collide.

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
   comb and publish the list first. **Built with "Tag lists and long lists, one release"** (Polish).
5. **Retire the hidden "seen" field** (item 10) — moved 2026-10-20/21 into the Polish task "Retire two leftover book
   fields: the hidden 'seen' flag and the old price-goal field" (one data round for both).

### Polish

#### A saved setting that reads fine but holds nonsense inside — check each value, not just the note
<!-- id 20261113-1120 -->

_Why it matters:_ Since 7.29.1 every saved setting is read through `readSaved`, which checks the note's KIND (an object,
a list) — not each value inside it. So a damaged note that still reads (a number where the search text belongs, column
widths saved as text) gets past it into the app. The cases that crashed a screen were fixed then; the rest can still
show odd values (found by both sprint-3 agents, 2026-11-13).

**To do:** a per-setting shape for the notes whose inside matters (the filters, the view settings, the phone's settings
note) — each value checked against what it should be, a wrong one replaced by its default with the same one STORE-13
warning. Function tests first (a planted wrong value per field).

#### "N now owned" after an import: a Show them button, and each column reads its date from one place
<!-- id 20261112-1926 -->

_Why it matters:_ After buying wishlist or sample books, the import says "(4 now owned)" and offers to clear their price
goals — but there's no way to SEE which four, to put them in a Book List (Ron, 2026-11-12: he had to look them up on
Amazon's site; "RW is not making this easier"). Law 20: hand them the action.

**Decided** (Ron + Claude, 2026-11-12)
1. **Show them** on the import's finish message whenever books became owned — it puts exactly those books on screen,
   selected, ready for Add to Book List (the import already knows them: `upgradedGoalIds` and the "now owned" count).
   **First, count bought SAMPLES too** (found 2026-11-12 from Ron's log — four books bought, the import said "2 now
   owned"): `storage.js` counts only wishlist → owned (`isWishlisted(existing) && !isWishlisted(book)`), though its
   comment says "wishlist/sample → owned" — so a bought sample is in neither "now owned" nor "Clear those goals". A
   failing test first (a sample becoming purchased in an import), then count every temporary type → purchased
   (sample, and the borrow-like types the fetcher promotes).
2. **One value per column:** today the Date Added column's display, its sort and the filter / grouping each write their
   own expression for the date (they agree in practice — `dateAdded` is empty everywhere — but three copies is how they'd
   drift). Each column in `COLUMN_CONFIG` gets one function giving its value; showing, sorting, grouping and filtering
   all use it. The dead `dateAdded` field goes.
3. **"Date Added" = the date it became what it is now** (wishlisted, sampled, or bought) — already true. A separate
   "First Added" (never changes) was discussed and set aside: the original dates of books already bought were
   overwritten, so it could only start from the day it's built — optional, not part of this task.

#### Phone: Report a problem in the ⋮ menu, like the desktop's Help
<!-- id 20261112-1756 -->

_Why it matters:_ Since 7.29.0 the desktop has Help → Report a problem… (copy the diagnostics, then email us or report
on GitHub); the phone's ⋮ menu has only Copy diagnostics, so a phone reader has to find our address on their own.
Found while building it (sprint 2).

**To do:** a **Report a problem** item in the phone's ⋮ menu (beside Copy diagnostics), using `reportProblem.js`'s
words and flow (the phone page already loads it). A screen test at phone size first.

#### Buttons name their action: replace the remaining OK, Yes and No buttons
<!-- id 20261112-1241 -->

_Why it matters:_ "OK" under "Delete these 3 folders?" makes you read the question again to know what OK will do; a
button that says **Delete** doesn't. Law 21 (Ron, 2026-11-12): a button names what it does — never OK, Yes or No;
Cancel stays.

**To do**
1. **The comb first** (Law 5): every confirm / choice / info box and `<Dialog>` with an OK / Yes / No button — the
   imperative boxes (`showConfirmDialog`, `showChoiceDialog`, `showInfoDialog`, the delete warning) and their default
   button words included; publish the site map (file:line, today's words, the proposed verb) for Ron's red pen.
2. **Then one change:** the confirm routines take the action's word as a required argument (no "OK" default), so a new
   box can't be born with one — the mechanism, not a sweep that drifts back.
3. An information-only box (nothing to decide) may keep a single "OK"/"Got it" — say which in the site map.

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

**Before building: an outside review of this design** (moved here from "Outside reviews before building…", Ron
2026-11-19) — a big design decided in conversation; run it the same way (a cold brief Ron reads first, a fresh
reviewer in two phases, my spot-checks, a summary with my verdicts).

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
   yet". No dialog; the receipt says it: *"Moved 'Dune' from 'Fantasy' to 'Beach Reads'. It wasn't in any other folder,
   so it went to the Inbox."* (wording Ron + Claude 2026-11-06 — "no folder… in the Inbox" contradicted itself: the
   Inbox IS a folder). Undo if you didn't want that. **Re-checked 2026-11-06** (Ron asked, with the least-astonishment principle in mind:
   refuse instead?): keep it. Cut says "take it out of here", so leaving the folder is what the user predicted; the
   Inbox step can't be avoided, only made manual (Add to Book List >, then remove from the folder → the same Inbox);
   a command that doesn't do what it says is the bigger astonishment; and Ctrl+X is an explicit verb (Law 18 corollary
   4), unlike a plain drag. Only the LAST folder sends a book to the Inbox — a book filed elsewhere just leaves.
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

**The one table** (Ron + Claude, 2026-11-06): every gesture's move / copy / paste rule becomes a row of ONE table —
built in 7.30.0 for every gesture that existed then (`gestureTable.js`; docs/design/ONE-TABLE.md). These decisions are
its rows; the new gestures below read the same table.

**How (technical)**
- **Where "can books be pasted here?" is answered today — four lists that disagree** (found 2026-11-06, the logging
  comb's finding F1): Ctrl+V refuses All Books, the library view AND the Inbox (readerwrangler.js ~5255, and silently —
  only a console line); the book right-click menu's Paste refuses only All Books and the library view (~18936 — its
  comment: "v6.0.0-alpha.53 - Inbox is a real folder, allow Cut/Move/Paste", which Ctrl+V missed); two more lists at
  ~5404 (adds the Searches header) and ~18406 (adds `__my__`). None names a Book List, a Search or the Trash. Ctrl+V's
  paste is also hand-written (its own `setFolders`), not `moveItems` — the one move/copy operation the menu and drag use.
- Today: Ctrl+X is refused only in All Books / the library view (readerwrangler.js ~5223); in a Book List or Search it
  records the view as the source, but paste-cut only removes from **folders**, so the book stays in the list. (Still
  true for a cut from a Book List pasted into a FOLDER after 7.25.1; a cut from a Book List pasted into another Book List
  now leaves the first list — 7.25.1's Book List paste.) Found in
  7.10.1-alpha.7, filed not fixed.
- **7.30.0 (sprint 4) changed the ground under this task** — the one table answers every move / copy / paste of today's
  keys, menus and drags (`gestureTable.decide`, `placeByTable`, `dropItems`, `dropTreeFolders`; ONE-TABLE.md §7). The
  "How" lines above describe the code before it; decision 11's "say what happened" is done there. What's left here are
  the NEW gestures, plus these leftovers the sprint found (ONE-TABLE.md §7, alpha.2–8):
  1. **Fake drop signals** (decision 11): the move cursor shows, then the drop is refused or does something else — a
     Search entry (books), the "Book Lists" crumb (folders, books), the Folders header and the Inbox while Ctrl will
     copy; the edge line's colour for a left-pane folder drag in a sorted mode can show red where a move then happens.
  2. **A Ctrl-drag of a LEFT-pane folder doesn't copy** (the left pane's drag only allows a move).
  3. **The tree's "＋ New subfolder here" box says "inside this one"** — it means the folder next to the ＋, not the one
     you're in.
  4. On a right-pane folder row, a right-pane folder drag whose parent isn't the open folder does nothing and says
     nothing — reachable only if the right pane changes place mid-drag.
  5. During a left-pane folder drag, hovering a collapsed folder opens it after 500 ms (timing-dependent; it can shift
     the rows below the pointer).

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

#### Remove code left over from older versions (hiding single copies, phone tag shelves, unused functions)
<!-- id 20261108-1800 -->

_Why it matters:_ Code nothing can reach still has to be read, kept working and tested around — and some of it is
still written into every save, backup and sync. Less code, nothing for a person to see.

**Found** (2026-11-08, a survey of the live files for the logging work; each claim re-checked by grep). Line numbers
are approximate (readerwrangler.js unless named).
1. **Certainly dead:**
   1. **Hiding a single copy of a book** (v4): `hiddenInstances` + `book._instanceId` + the `HIDE_COPIES` undo / redo
      cases (state ~1536; set ~4657, ~7961, ~8520; read ~17059, ~17216, ~17679, ~17820; label ~7403) and mobile.js
      (~106, ~2429, ~2639). Nothing assigns `_instanceId` and nothing records `HIDE_COPIES`; hiding today is
      `book.isHidden` (a book field, so a restore brings it back). **Written into saved data** — the saved
      organization (~4798), the Complete Copy (~6206), Save Backup (~6314) — always empty: every backup of Ron's from
      2026-09-01 to 2026-11-06 holds `hiddenInstances: []`.
   2. **Pinned tag folders on the phone** (`pinnedTagFolders`, the `__tag_…__` shelves): mobile.js ~108, ~678,
      ~853-869, ~1517, ~1640-1660, ~1846-1875, ~2426, ~2636, ~3117, ~3177, ~3209. The desktop dropped it on purpose
      and never sends it; none of Ron's backups carry it (the old demo library has an empty one).
   3. **A drag value set but never read:** `explorerDragBookId` (~1562, 20 setters).
   4. **The startup collections merge** (`mergeCollectionsIntoBooks` ~6508, called once ~4680): it runs once at startup,
      before `collectionsData` can be set, so it always returns the books unchanged.
   5. **Never called:** `clearLibrary` (~6446), `getBooksInUserFolders` (~1896), `getRelativeTime` (~4507),
      `renderStatusIndicator` (~8948), `FolderIconSVG` (~6107), `coverRow` (~12459), mobile.js `IconFolderLarge`
      (~175); uiHelpers.js `SETTINGS_KEY` (~8; its key string stays in the reset lists).
2. **Obsolete by Ron's rule** (2026-11-08: "if my oldest backup doesn't contain these fields, consider them obsolete" —
   none of his backups do):
   1. `dataSource` and `lastSyncTime` — set and saved with the organization (and the phone's copy), never read.
   2. The three single-choice filters from v3.8 (`collectionFilter`, `ratingFilter`, `seriesFilter`; state ~1353,
      ~1411, ~1414; logic ~2565-2583, ~10229-10294; chips ~10859-10873): nothing on screen sets them; only a v3/v4-era
      saved filter could.
   3. The old cover cache (`CACHE_KEY` "enriched-cache", read ~6973): never written.
   4. The one-time moves from the pre-2026 storage (`FOLDERS_KEY` / `BOOKLISTS_KEY` reads ~4623, ~4634, mobile.js
      ~135) — first a console check that Ron's browser holds neither old key.
3. **Checked and alive** (don't remove): the refusal of very old files (`amazonData`, `type: 'collections'`), the
   `isHidden` backfill (uiHelpers.js ~95), `__views__`, the phone's own covers / list setting.

**How**
1. **With "One backup writer…"** (the launch gate), not before: three of these
   (`hiddenInstances`, `dataSource`, `lastSyncTime`) are written by both copies of the backup writer — one writer,
   then one change.
2. **Readers stay tolerant:** an old backup or a phone's old copy may still carry them — ignored, never an error (the
   backup check, 7.26.0, already ignores parts it doesn't know).
3. The test fixture (test/fixtures/make-small-fixture.js, small-fixture.json) mentions some of them — regenerate it.
4. Beside "Retire two leftover book fields…" (just above): the same clean-up, at the book level.

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

#### Tag lists and long lists, one release

The tag picker, the Tags filter, the "Save results" menu and every type-ahead list all sit on one
shared scrolling list — decided as one build, one test round (2026-10-22). Gathered here 2026-11-04 (TODO scan) from
Polish and Small fixes, in build order: the shared list first, then what moves onto it. "Tag from Collections, round
2" step 4 (High priority) — the shared tag-change function — is built with it.


##### Long lists keep their actions in view (Manage…, Select All) while you scroll
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
4. **Pair it with "One shared tag picker"** (this group, next) so both tag lists move onto the piece together.

**Related:** "The 'Save results' menu runs off the screen" (this group — the same list carries its fit-and-scroll
fix) and "One shared tag picker" (this group — it sits on this piece). Deferred from 7.22.1 by Ron, 2026-10-19
(no regression; scrolling down is the workaround).

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

##### The "Save results" menu runs off the screen with many Book Lists
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
(this group's first task): its **top slot** holds the filter box (always visible while the list scrolls), the **middle** scrolls your
Book Lists, its **bottom slot** an action like "New Book List…"; and the **fit-to-the-roomier-side** behavior lives in
that shared piece, so every long list gets it. This menu is its first user after the tag lists. The filter box is one
more type-ahead list for "Arrow keys should move through every type-ahead list". (The old line "check other menus
that list your own items" moved to the long-lists task's sweep.)

**How (technical)**
- In the shared list piece (a `<Popover>` option for button dropdowns): when it can't fit below, pick the roomier side,
  cap the height, scroll.
- Today it pins to the top of the window and hangs off the bottom. The fly-out rule is CursorPopup's "never add overflow".

##### Arrow keys should move through every type-ahead list
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
"One shared tag picker"** (this group) — it sits on this behavior; one pass covers both tag lists.

**Status:** deferred by Ron 2026-10-06 (minor accessibility fix).

**How (technical)**
- Build it once in the shared list popup (`<Popover kind="list">` — both Series lists became that in 7.18.0-alpha.54), not per field —
  the same arrow-key handler the right-click menus get in "Finish keyboard accessibility" (one handler for every
  `<Popover>` kind; whichever task is built first builds it).
- The working model is the `SearchInput` component's Down/Up/Enter/Esc handling. Stable copy "as it was": `git show 46a0cf6:readerwrangler.js`, search for `const SearchInput`.

#### Finish keyboard accessibility
<!-- id 20261014-1030v -->

_Why it matters:_ Everything should be usable without a mouse. Today Tab walks out of an open window into the library
behind it, you can't see where the keyboard is, and right-click menus have no arrow keys.

**Left** (checked 2026-11-03)
1. **Keep focus inside an open window** — every window says it's modal, but nothing keeps Tab inside it.
2. **A visible focus outline** for keyboard users — today only the note editor has a focus style.
3. **Keyboard access to the right-click menus** — Down / Up move, Enter runs, Esc closes (Esc already works).
4. **Keyboard navigation in the left pane** (moved here 2026-11-03 from "Leftover desktop polish") — including Home /
   End for its jumps to top and bottom ("Jump-to-top / bottom buttons by the scrollbar, in both panes").

**Decided** (Ron + Claude, 2026-11-03, in the TODO review)
1. **Moved up from After launch to Polish** — since 7.18 it's small: every window goes through one `<Dialog>`, every menu
   and list through one `<Popover>`, the old-style message boxes through `attachDialogDismiss` — so items 1 and 3 are
   each one change in the shared piece, not a sweep; item 2 is one style rule. Tab escaping a window is a defect, not a
   nicety (Rule 0); outside review 4 (a newcomer's first look) would flag it.
2. **One arrow-key handler for every `<Popover>` kind** — the menus here and the type-ahead lists in "Arrow keys should
   move through every type-ahead list" share it; whichever is built first builds it.
3. **Tested with the browser driver:** open a window, press Tab twenty times — focus never leaves it; right-click a
   book, Down, Down, Enter — the right item runs; the focus outline shows on Tab, not on a mouse click.
- Screen-reader labels for icon-only buttons come with the tooltips task ("Tooltips where they help…").

**How (technical)**
- Focus trap in `<Dialog>` and `attachDialogDismiss` (focus the first control on open, return focus on close);
  `:focus-visible` (outline on keyboard focus only); arrow keys in `<Popover>` (menu, list).
- **After "Rebuild the old-style message boxes as standard dialogs"** (High priority), the focus trap is one change in
  `<Dialog>` only — so build this after it.
- Tool survey 2026-11-03 (docs/design/TOOL-SURVEY.md): axe-core (`@axe-core/playwright`), run from the browser driver, checks contrast and
  labels automatically; focus order still needs scripted Tab walks.

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

##### A new message glides in from the old one's spot instead of appearing where you clicked
<!-- id 20261116-1234 -->

_Why it matters:_ A message appears just above where you clicked — but if the last one is still showing or flying to
the status bar, the same box is reused and slides there over a second (`transition: all 1.0s ease-in`), so the new
message glides in from the old spot or from the status bar. It reads as wrong, and for a second it's somewhere you
didn't look. Found by sprint 6's TOAST-006 (which now waits for a message to arrive); not changed there — it's visible
behavior. **How:** a new message starts where it belongs (no transition for the jump), then holds and flies as today.

##### Tidy up the notes
<!-- id 20261020-1448 -->

_Why it matters:_ Housekeeping — a few notes are in the wrong place. Details: see TODO notes.

##### Leave the affiliate tag off Amazon links on the test rig
<!-- id 20261021-1401 -->

_Why it matters:_ Ron's own testing clicks — and any purchase through them — count against RW's affiliate account,
muddying the stats, and Associates doesn't pay on your own purchases (repeated ones can draw a warning).

**What you see** (2026-10-21): every "View on Amazon" / Share link carries the tag on every build, localhost included
(`getAmazonUrl` in uiHelpers.js). The Associates dashboard showed 6 orders, 0 shipped, $0 — click spikes on Oct
12–16 match Ron's test sessions.

**Decided** (Ron + Claude, 2026-10-21)
- **Ask the existing central check — don't re-read the address:** leave the tag off when **`isTestingTraffic()`**
  is true (readerwrangler.html, 7.21.0: contributor mode — local server AND this browser's `readerwrangler-contributor`
  flag — or the dev site). Plain localhost is NOT enough: a self-hoster is localhost too and gets production behavior,
  tag included (the same split contributor mode already makes for the relay and the usage statistics).
- One place: `getAmazonUrl` asks it; nothing else builds a tagged link (verify with a search when building — the
  phone app and Share included).
- **Widened 2026-11-20 (outside review 1, Ron):** also off in any browser Ron uses day to day — a per-browser setting,
  `remove_affiliate_tag`, set once on his computer and his phone (so his own purchases never go through the tag). Built
  in "A one-day truth-and-safety release" (item 15), before launch. (The Associates summary of 2026-11-20 again showed
  items ordered and $0 earned — most likely Ron's own purchases.)

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
   "Finish keyboard accessibility", Polish).
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
   **Evidence (2026-11-04, the first screen test):** a fresh browser shows **"Show Hidden" ticked** — hidden books are
   shown by default.


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
3. ✅ **The receipt says "copied" only when it was** — done in 7.29.1 for every Copy in the app: they all go through the
   logging kit's one copy routine (`rwLog.copyText`), which waits and says "<what> couldn't be copied — the browser
   refused the clipboard" on a refusal (Ron chose those words in sprint 3). Copy ASIN(s) uses it too — and item 2's
   "one small helper" is largely that routine: each Copy item is one call now.

**How (technical)**
- Next to Copy Title(s) / Copy Author(s) in the book context menu (readerwrangler.js ~19535–19568 on 2026-10-22):
  `navigator.clipboard.writeText(...)` returns a promise — await it (catch the rejection) before the receipt.

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

##### With a filter on, the right pane still shows subfolders with no matching books
<!-- id 20261103-1651 -->

_Why it matters:_ The hiding was written but has never run — the left pane hides folders with no matches, the right
pane's subfolder list doesn't. Found 2026-11-03 by the precompile load test ("Faster loading: build the app ahead of
time").

**Why it happens**
- The right pane's subfolder list (readerwrangler.js ~3318, `explorerVisibleFolders`) asks "is a filter on?"
  (`hasActiveFilters`) — a name declared ~5,400 lines later (~8760). Modern JavaScript refuses that (the precompiled
  page crashed: "Cannot access 'hasActiveFilters' before initialization"); the browser's compiler turns `const` into the
  older `var`, where the read quietly gives `undefined` — so the answer is always "no filter".

**Decided** (Ron + Claude, 2026-11-03)
1. Fix it by moving the declaration above its first use (or computing it there).
2. **The chokepoint — a commit check:** the name lists at the end of `useMemo` / `useEffect` / `useCallback` blocks
   (`}, [a, b, c]);`) are read as the screen is drawn, so any name in one that is declared further down is this bug,
   guaranteed. Scan for exactly that (the same family as the name check); publish what it finds before fixing — there
   may be more.
3. **Build together with "A folder or Book List you just created stays visible under filters"** — once the right pane
   really hides empty folders, a new folder hides there too.
4. Test step: turn on a filter, open a folder with subfolders — only subfolders with matching books (or "show all
   folders") appear.
5. **Then drop the `const` / `let` → `var` conversion in the build** (moved here from "Faster loading", decided item 3,
   when 7.27.0 shipped it): `@babel/plugin-transform-block-scoping` in tools/build/compile.js — once item 2's check is
   clean, so the next such bug is a visible crash, not a silent "undefined".
- Tool survey 2026-11-03 (docs/design/TOOL-SURVEY.md): ESLint's `no-use-before-define` (+ `eslint-plugin-react-hooks`) in a commit check is
  the ready-made form of item 2 — expect tuning, since it also flags reads inside functions that only run later.

##### A missing book description: one quiet line, on the computer and the phone
<!-- id 20261014-1030ap -->

_Why it matters:_ So a missing description reads as known, not broken — and the phone says the same as the computer
(Ron, 2026-10-15: "Phone should match").

**Today** (checked 2026-11-04)
- The **computer**'s book details window shows a yellow ⚠️ box: "Description not available — This book may not have a
  description in Amazon's database, or the description wasn't captured during the library fetch." (readerwrangler.js
  ~14308; since v3.5).
- The **phone** hides the section entirely (mobile.js ~2236).

**Decided** (Ron + Claude, 2026-11-04, in the TODO review — moved here from After launch → Technical clean-up)
1. **A quiet, muted line, not a warning box** (Law 12 — many books simply have no description on Amazon; that's
   normal): *"No description from Amazon for this book."*
2. **A remedy only when there is one:** add *"A full refresh from Amazon may fill it in"* once "Refresh all books from
   Amazon…" exists; until then, just the plain line.
3. **Written once, used by both:** the wording lives in one shared place (uiHelpers) that the computer and the phone
   both use, so they can't drift apart again.

##### The phone's cover copies: still worth it? And why wasn't the browser's own cache enough?
<!-- id 20261110-1734a -->

_Why it matters:_ The desktop dropped its cover copies in 7.27.0 (it hadn't drawn from them since 5.0.0, and reading
them held every load back by seconds). The phone still reads every cover copy into memory at start — maybe the same
cost for little gain.

**What to look into**
1. Time the phone's start with and without its copies (mobile.js's load reads them before showing covers?).
2. Ron (2026-11-10): the copies were added in 4.14.0 for speed — "we were seeing speed issues and the cache helped" —
   and nobody remembers why the browser's own image cache wasn't enough then. Find out before removing them: the
   browser's cache is shared with every site and can drop images; Amazon's image server may ask the browser to check
   back; 3,270 images requested at once may have been the real cost.

##### Relay Setup's Test connection always checks the production relay
<!-- id 20261102-1503 -->

_Why it matters:_ In contributor mode (Ron's localhost, which uses the dev relay) **Test connection** asks the
production relay instead — so a revoked channel or an outage on dev can show the wrong answer (found 2026-11-02 in
the TODO review, not yet tested).

**Restored 2026-11-10:** filed 2026-11-02 15:03 and lost 27 minutes later — deleted by accident inside a large TODO
edit (commit dedc3ca, the two-tab tasks merge), with no word in its message; never fixed (checked 2026-11-10: the
address is still hard-coded). Found by the backlog report's audit of "dropped" tasks.

**How (technical)**
- readerwrangler.js ~1998 (the `'test'` case) fetches a hard-coded production worker address before calling
  `RWRelay.getDeviceState()`; use the one place that answers which relay this copy talks to (relay-client's
  `workerUrl()`) — comb for other hard-coded relay addresses in the same pass.

##### F2 follows the Delete key's rule: what's selected, where you're working, and words when it can't
<!-- id 20261115-1639 -->

_Why it matters:_ Two keys that act on "this" should agree on what "this" is. The Delete key reads the selection and
where you're working (7.28.1, ONE-TABLE.md §3); F2 still follows the older "the folder you're in" rule. 7.30.0 fixed
its worst case — F2 on a folder selected in the Folders view did nothing (RENAME-001) — and measured the rest
(RENAME-003–005, 2026-11-15):
1. **Nothing selected, last click in the right pane:** F2 renames the folder you're in; Delete does nothing.
2. **Several folders selected:** F2 renames the folder you're IN, not one you selected (Delete's pre-7.28.1 mistake).
3. **The Inbox** (open, or selected): F2 says nothing; Delete says "The Inbox can't be deleted." (Law 16).
4. **Cover View** (from the code, not seen): the right pane's rename box is drawn only in the List View's table
   (`rightPanelEditingId === folder.id`), so F2 or the right-click Rename on a folder in Cover View may show nothing.

**How (technical):** `pressF2` (readerwrangler.js ~5890) — give it the Delete key's shape (the table's `selectionWhat`
and the left-pane focus rule); F2 isn't a `gestureTable` verb yet. Tests: test/ui/test_rename_key.py.

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

#### A refused Restore shows a false "Restore Warning" box a minute later
<!-- id 20261118-1136 -->

_Why it matters:_ After a backup the app refuses part-way through Restore (e.g. an old Collections file), a minute
later a box says "Restore Warning — Library loaded but status check timed out. Please refresh the page." — untrue,
and it covers whatever the person is doing (found 2026-11-18 by sprint 8's test-waits work: during a long wait the box
covered the File menu and failed BACKUP-005).

**How (technical):** in `readerwrangler.js` Restore (~line 6308) starts a 60-second timer before `loadLibrary`; the
`catch` (~6334) closes the progress box but never clears the timer, so it fires and shows the box (and logs BACKUP-03).
Fix: clear it in the `catch` (or a `finally`) — a failing test first: Restore a file that's refused after loading
starts, wait past 60 s (or shorten the timer in the test), and check no box appears.
**When (Ron, 2026-11-18): "watch for an opportunistic time to include it in a sprint"** — it happens rarely (only a
very old backup, or something else already failing mid-restore; nothing in the library changes), so it rides along
with the next sprint that touches app code, as a small extra task.

#### Share Library: a copy of your library for a friend, without your Cloud Sync Key
<!-- id 20261122-1440 -->

**Stays in Polish; grouping for the order re-review** (Ron, 2026-11-26, outside review 2 item 6): a menu item right beside Save Backup; build it with "Lock
the Cloud Sync Key in backups…" (same menu, same reason — sharing safely) and "One backup writer…" (same file builder).
It is the safe tool for the one real key leak so far (a demo file made from a backup, public July 3 – Oct 31, 2026).

_Why it matters:_ Sending a friend your library today means Save Backup, then remembering to take your Cloud Sync Key
out by hand — and a backup carries the key, so whoever has the file can overwrite or wipe your cloud library. Readers
swap libraries ("Books I Want To Borrow From Ron"); a rule people must remember fails, a menu item doesn't.

**Decided** (Ron, 2026-11-22, during outside review 3):
1. **File → Share Library…**, right after Save Backup: the same writer as Save Backup (one writer — "One backup
   writer…"), **never the Cloud Sync Key**, named `readerwrangler-share-<date> <time>.json`.
2. **Your notes: a switch at every share, off by default** ("Include my notes") — notes can be private in a way
   folders aren't.
3. It carries **whose library it is** (the account name from "A fetch from someone else's Amazon account stops…"), so
   the friend's Restore can say whose library it replaces.
4. **The friend opens it with Restore, in a browser profile of their own** (help notes, with pictures) — until "Several
   people on one installation" is weighed again. The later, fuller version is "Share a filtered, read-only copy of
   your library" (Someday).

#### Deleted folders go to the Trash, like books
<!-- id 20261125-1440 -->

_Why it matters:_ A deleted folder is removed and its books go to its parent or the Inbox; only Undo brings it back, and
undo lives in memory (50 steps), gone at the next reload. Books go to the Trash; folders don't. Outside review 3, item
12 (the reviewer's finding: `readerwrangler.js` ~4392-4424, ~7671 — not re-checked by me).

**Decided** (Ron, 2026-11-22, outside review 3 — the report's "smaller, and can wait"; agreed that day, filed 2026-11-25)
1. **A deleted folder goes to the Trash with its shape** — its subfolders and which books it held — and Restore from the
   Trash puts it back where it was (Ron: "Keep the folder org in the trash? Doable I'd think").
2. Design first: what the Trash shows for a folder, and emptying it (a stored-format change — Ron sees it).

#### The Import's 30-second limit really stops the Import
<!-- id 20261125-1441 -->

_Why it matters:_ It is a race: after "Import timed out" the Import keeps running, while the mark that says "an Import
is running" is cleared — so a second Import or a Restore Backup can start on top of it. Outside review 3, item 12 (1b.5;
the reviewer's finding, read in code, not run: `readerwrangler.js` ~6049-6053, ~6151 — not re-checked by me).

**Decided** (Ron, 2026-11-22, outside review 3 — the report's "smaller, and can wait"; agreed that day, filed 2026-11-25)
1. **The running mark stays until the Import has really ended** (finished, failed or stopped) — the time limit only
   changes what the person is told.
2. Test first: a slow Import past 30 s; a second Import or a Restore meanwhile is refused with the existing "already
   running" words.

#### An open tab learns that a new version of ReaderWrangler is out
<!-- id 20261125-1442 -->

_Why it matters:_ Nothing notices a new version: an open tab keeps the old code and keeps writing the whole organization
and the whole book store. The reviewer found nothing lost by that today, but any future change of a stored shape would
meet an older tab (and see "A saved organization that can't be read is kept aside…"). Outside review 3, item 12 (1f).
Not the same as "Keep your tabs and browsers in step" — that is about your DATA's version; this is the APP's.

**Decided** (Ron, 2026-11-22, outside review 3 — the report's "smaller, and can wait"; agreed that day, filed 2026-11-25)
1. **When the site has a newer version**, the open tab says so and offers **Reload** (a banner, not a box — Law 18).
2. Low priority until a release changes a stored shape; then before that release.

#### Phone: remove "Save Credentials to File"
<!-- id 20261126-1050 -->

_Why it matters:_ The compact view's button writes your Cloud Sync Key as a plain file into the phone's Downloads
(`mobile.js` ~1006-1020), which cloud backup apps often copy. It's no longer needed: the computer's QR code re-pairs the
phone in seconds. Outside review 2, item 6.

**Decided** (Ron, 2026-11-26, outside review 2 item 6): remove it. Low priority.

## 🗄️ After launch

_Formerly: 🗄️ Backlog (post-launch)_

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
1. Measure one click with Chrome's performance tool, filter on vs. off. **Decided 2026-11-02: Claude does this with
   the browser driver** (High priority) on a throwaway copy of Ron's library (his backup, minus credentials) — a few
   hundred book-to-book clicks with a filter on and off, the browser's own timing for each — so it's numbers, and it
   either reproduces or it doesn't (the utilities project's Law 18: reproduce with real input before explaining). A
   natural second job for the driver, after the Delete key fix; the fix itself stays here (mild).
2. Remember whatever that bar recalculates.

**Note**
- Your first theory — "filter the current folder, not the whole library" — can't explain a lag on **selecting** (filtering doesn't re-run then). Still worth checking for the first filter's cost.

**How (technical)**
- The cached list is `explorerDisplayItems` (a useMemo); profile with DevTools Performance.

#### Save only the changed book to this browser's book store
<!-- id 20261125-1415 -->

_Why it matters:_ Every change to any book — one tag, one rating — clears this browser's whole book store and writes
all ~3,270 records again (about 51 million characters; `storage.js` ~267, `store.clear()` then every book). The
browser's database can replace a single record by its ID instead. Local only — nothing in the cloud changes.

**Decided** (Ron, 2026-11-25, outside review 3 Q7): **low priority — build it when it causes a problem** (edits feel
slow, or a save fails part-way); Law 23 — no evidence it costs anything today.

### Relay and sync

_Formerly: Relay / data robustness_

#### Edit Kindle collections from ReaderWrangler
<!-- id 20261014-1030r -->

_Why it matters:_ Change your Kindle collections without going to Amazon.

**Status: a big MAYBE** (Ron, 2026-11-02): it would be the first — maybe the only — feature that writes BACK to
Amazon.com. "Just from that perspective, maybe a no. Is it worth that to add 1 feature? TBD." And ReaderWrangler's undo
can't reach Amazon: a bug or an Amazon change could rearrange a user's real Kindle collections, beyond our reach to
put back. Decide only after outside review 1 (launch risks — Amazon's terms) has weighed writing vs. reading, and
only if users ask for it after launch; Tag from Collections already brings collections into RW, one way.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **Amazon's side lives in the TODO notes** — the spec's captured API (§4, incl. a real collection id of Ron's) and the
   Amazon names in §5–§9 were moved there 2026-11-02; the public spec keeps the design.
2. **One mechanism for "the app asks the bookmarklet to do something"** — the spec's `collection-pending` queue and
   "Refresh all books from Amazon"'s request note are the same direction and shape: build one small "requests from the
   app to the bookmarklet" channel on the relay; the refresh request is its first user, collection edits a later one
   (signed writes, `amazonFetch`'s pacing and the human-check stop then apply for free).
3. **A "Read next" collection kept from ReaderWrangler is a use case, not a reason** (2026-11-02, from the "Read in
   Kindle" review — it's the one way to put a book a tap away on a Paperwhite). Ron keeps one by hand today;
   automating it saves a few clicks.

**Spec:** docs/design/COLLECTION-EDITING.md (Amazon's side: see TODO notes).

#### Smaller organization syncs (send only what changed in your folders, tags and lists)
<!-- id 20261014-1030k -->

_Why it matters:_ Optional. Every push of your organization (device-state) sends the whole thing — roughly 17 MB per
copy by the 2026-10-15 measurements — when you leave the tab after a change, or after a minute idle; the phone
downloads the whole thing on every refresh.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **The library half is already done** — since 7.0 the bookmarklet sends each fetch and each wishlist add as its own
   small upload (a mailbox letter) and the app folds them in at import: the spec's delta model, for library changes.
   What's still sent in full is the organization.
2. **Remeasure first** (Ron: "Remeasure first."): how big a device-state push really is for Ron's library today, how
   often one happens in a normal session, and how long the phone's download takes — from the trend file and a browser
   driver session.
3. **Decide from the numbers:** build it only if pushes or the phone's download are noticeably slow; otherwise close
   it. The cost isn't money (a 17 MB push is one or two writes — writes are the binding free limit, and cheap on the $5
   plan); it's upload time and the phone's download, against real complexity (merge logic in the app AND the phone, plus
   occasional compaction).
4. **Measured 2026-11-20 (outside review 1's storage look):** on the relay an organization version is 17.9 MB — the
   same size as a library version (17.8 MB) for 3,270 books, compressed and encrypted. An organization that small in
   itself (folders, tags, lists) shouldn't be that big; it looks as if it carries the books too. **Check that first** —
   if so, leaving them out would roughly halve every user's storage and the phone's download, without any merge logic.

**Spec:** docs/design/RELAY-DELTA.md (written before 7.0 — its library half is superseded by the mailbox).

**Answered 2026-11-22 (outside review 3):** yes — the organization version carries the books, by design: it is the
Complete Copy (books, organization and your own fields together), written only by the app and read only by the
phone (RELAY-WRITE-REDESIGN.md §2b). Leaving the books out would break the phone. The real halving is "One copy
instead of two", below.

#### One copy instead of two: the Fetched Copy and the Complete Copy as one
<!-- id 20261122-1535 -->

_Why it matters:_ The relay keeps two copies of each person's library, one per flow: the **library copy** (fed by the
bookmarklet, read by Import — the books, without your organization) and the **phone's copy** (written by the app, read
by the phone — everything). The complete one is the one no computer can read, and the two together double the storage.

**Weighed** (Ron + Claude, 2026-11-22, during outside review 3 — Ron: "file to consider after launch"):
1. **For one copy:** one source of truth — "Restore from Cloud Sync" comes almost for free and Import gets your own
   fields; about half the storage (~36 MB instead of ~72 MB for a 3,270-book library, against the 200 MB cap per cloud
   copy); one set of rules; and **room for the phone to edit** (Ron: moving books in and out of Book Lists, Read tags —
   "Phone: change Book Lists and tags", below), which a one-way copy can't carry back.
2. **For two (today):** a fetch can never damage the organization in the cloud (it isn't in the copy fetches feed —
   the August 2026 reason, after a torn upload); the bookmarklet never needs to understand the organization.
3. **Against one copy:** the bookmarklet and the app write the same copy (the library copy's mailbox-and-merge pattern
   would extend to both — an extension, not an invention); a fetcher bug or a wrong-account fetch lands next to the
   organization; it changes the relay's stored format — a migration of existing cloud libraries, and a design Ron has seen
   first.
4. **Before launch instead:** "Restore from Cloud Sync" (reading the phone's copy) closes the gap that hurts people.

#### Bookmarklet: when your key no longer works, say so plainly — and never show the Channel ID in an error
<!-- id 20261018-1422 -->

_Why it matters:_ When a bookmarklet's key has been replaced or revoked, the fetch stops with a raw technical error that
also prints the full Channel ID on screen — exactly the kind of error people screenshot for support.

**What happens today** (checked 2026-11-02)
- **The timing is already right:** the fetcher's first step ("Checking Library") reads the pending uploads from the
  relay; on a revoked channel that read is refused, so the fetch stops before any Amazon request. (The library read
  before it quietly treats a refusal as "no library yet"; the mailbox read is the one that stops it.)
- **The words aren't:** the user sees e.g. `Relay GET /mail/<the full Channel ID>/list failed: HTTP 403
  {"error":"Channel revoked"}` — every relay error is built in one place (`relayFetch`, relay-client.js), so this
  affects the app too.

**Decided** (Ron + Claude, 2026-11-02, in the TODO review)
1. **A plain message for a revoked channel:** *"This bookmarklet's Cloud Sync Key no longer works — it was replaced or
   revoked. In ReaderWrangler, open Cloud Sync Setup and drag the new bookmarklet."* The same plain path covers 7.25.0's
   "this channel is claimed by a different key" refusal.
2. **No error message ever contains the Channel ID** — removed in the one place every relay error is built, so the app
   and the bookmarklet are fixed at once. The private-values commit check can't see runtime messages, so a test asserts
   it (a refused request's error text must not contain the id).
3. **No extra "ping before fetching"** (the old idea: `/status/{channelId}` first) — the existing first read already is
   the ping. Less code, not more.
4. **(Note added 2026-11-10) One short form for a Channel ID already exists** (7.26.0): logger.js `shortChannelId` — first 8 … last 4, as Relay
   Setup shows it — and the log's cleaner (`scrub`). Use that one function here, not a second copy; the fetchers' own
   logging needs it too ("The fetchers' own logging…", in "Fetcher work").

(Left over from "Ask before restoring when relay credentials don't match", shipped 7.14.3; Ron filed it on its own
2026-10-16. docs/design/RELAY-CRED-MISMATCH.md "Future" — superseded by the above.)

#### Edits travel between computers: newest edit wins, per field
<!-- id 20261123-1916 -->

_Why it matters:_ Today an ordinary edit (a title or series fixed, a tag, a note, a price goal) never leaves the
computer it was made on: the mailbox carries only fetches, permanent deletes and Restore Backups, and no full view reads
the Complete Copy. One person with two computers (work and home) on one Cloud Sync Key sees them drift apart. And when
both computers edited the same field, nothing can say which edit is newer.

**Decided to design** (Ron, 2026-11-23, outside review 3 item 12.3 — option 3; a design Ron sees before anything is
built — it changes stored formats):
1. **Every edit carries a time, per field:** the "edited" mark becomes a time (`title: true` → `title: <time>`); old
   marks read as "edited, time unknown" = oldest.
2. **The time is the relay's** (Ron's idea), without asking the relay per edit:
   - the offset to the relay's clock is relearned at **every** contact (sends, freshness checks, Imports) — the relay
     already stamps its own time into every run and version id;
   - between contacts the stamp is "relay time at the last contact + the browser's elapsed-time stopwatch" — immune to
     someone setting the clock by hand; the clock's time zone never matters (it counts in UTC underneath);
   - **"never older than what I've already seen"** (a hybrid logical clock): an edit's time is at least one tick after
     the newest time this computer has received — so one person on two computers is always ordered right, whatever
     the clocks say; only true simultaneous edits by two people fall back to the corrected time (a dead heat = a toss-up).
3. **How an edit travels:** a new mailbox run, "edit" — book, field, value, time — built like the tombstone, sent
   batched with the Complete Copy's send (one small write per batch); folding into the Fetched Copy keeps the newest
   time per field; Import from Relay's merge keeps the newest per field.
4. **Which fields:** the six editable Amazon fields for certain; whether your own fields (price goals, tags, notes,
   rating) travel too is part of the design — today they never cross ("local wins").
5. **Keep Amazon's original beside an edit** (Ron's idea, 2026-11-23): a book stores Amazon's value next to your edit,
   so a Restore Backup can send both, the app can show Amazon's title beside yours, and "back to Amazon's" is one click.
6. **Found 2026-11-24, building the 12.3 fix (read in code, not run):** when the Fetched Copy folds in a later library
   fetch (`relay-client.js` composeCanonical ~1057, `{...previous, ...fetched}`), Amazon's title / series… overwrite an
   edited value, but the "edited" mark carried in by a Restore Backup stays — so the Fetched Copy can hold Amazon's
   value marked as your edit, and a computer that never edited it takes it as an edit (no worse than before the fix,
   which locked its own old value instead). Per-field edit times settle it: an edit newer than the fetch stays, an
   older one gives way and drops its mark.
7. **Weigh against "Keep your tabs and browsers in step"** (Before launch): that task takes the whole Complete Copy when
   a browser is behind, with a banner when both changed; per-field newest-wins would make most of those banners
   unnecessary for book fields. The two designs are drawn together.

### Features

_Formerly: Features_

#### Build the support assistant (custom GPT)
<!-- id 20261014-1030i -->

**After launch (Ron, 2026-11-19):** it needs the finished User Guide, and real people's questions to tune it — and it adds an outside service.

_Why it matters:_ Lets users get answers without waiting for you.

**What you'd get**
- A custom GPT that answers ReaderWrangler questions, linked from the Help menu.

**Decided** (Ron, 2026-10-22)
- **It reads USER-GUIDE.md — the same file people read** (the User Guide task above); no separate manual.
- **The uploaded copy is the one thing that can drift.** A custom GPT keeps its own copy (believed not to re-read our
  site by itself — confirm when building). So: the guide carries an "up to date through release X" stamp, the
  assistant is told to quote it when asked, and the release checklist gets "re-upload the guide to the assistant".

**Decided** (Ron + Claude, 2026-11-01, in the TODO review)
1. **Choose the platform when building, from current facts** — the custom-GPT choice dates from July (Ron's ~$20/mo
   authoring seat; users need a ChatGPT account; free-account limits change). Compare then: a custom GPT, a Claude
   equivalent (the spec's own "evaluate" line), an assistant on our own site through an API (per-use cost, no outside
   account). Prices and limits move monthly — no recommendation ahead of time.
2. **It never asks for, or accepts, the Cloud Sync Key.** Support chats are where people paste secrets. Its
   instructions say never to request it, and to tell anyone who pastes it to make a new key; the User Guide's
   troubleshooting says "nobody needs your key to help you".
3. **A way out when it can't answer:** the support inbox, if launch-risk review 1 brings one ("email support@…"), else
   a link to report an issue — never a dead end.
4. (Not a change — the "one file" decision applied:) the help notes (SUPPORT-KB) aren't uploaded separately; their
   troubleshooting answers flow into the User Guide's FAQ and troubleshooting when the guide is written.

**Spec:** docs/design/SUPPORT-GPT.md.

#### "Read in Kindle": open a book in the Kindle app or Cloud Reader
<!-- id 20260919-0000 -->

_Why it matters:_ Jump straight from ReaderWrangler to reading the book — for people who read in the Kindle app or Cloud Reader.

**Placed here** (Ron, 2026-10-16): moved from High priority — it does nothing for Paperwhite reading, but it's the natural button for app / Cloud Reader readers.

**What you'd get** (decided Ron + Claude, 2026-11-02, in the TODO review)
1. **A "Read in Kindle" button, chosen by the device you're on** (the browser tells the app which platform it's on):
   - **Android:** opens the book in the Kindle app; with no app installed, the book's Amazon page.
   - **Computers, iPhone and iPad:** opens the book in Kindle Cloud Reader, in the browser (tooltip: "Read in Cloud
     Reader").
   - Not "Read" alone — ReaderWrangler already has a Read / Unread status, and a bare "Read" looks like "mark as read".
2. **Where:** next to **View on Amazon** — in the book details window, the book's right-click menu, and the phone's
   book card.
3. **Greyed out, not hidden** (Law 16), with a tooltip: wishlist books and samples — *"You don't own this book yet"*;
   an owned print-only book — *"No Kindle edition"*. A title Cloud Reader can't show can't be known in advance; it
   opens and Amazon's page says so.
4. **Not** a built-in reader.

**Tested** (Ron, 2026-09-19 and 2026-11-02 — details: see TODO notes)
1. **The Cloud Reader link opens the book** — from a cold start, in a private window (after signing in), and for a book
   never opened anywhere.
2. **The Kindle app on a computer can't be pointed at a book** — its link opens the app's library, not the book. Not
   offered.
3. **A Paperwhite can't be reached.** Nothing — not reading the book in the phone app, nor Amazon's own "Deliver to
   device" — opens a book on it or moves a downloaded book to the top of its list. Paperwhite-only readers gain
   nothing from this task; that's settled, not pending.

**Limits**
- The Android link is unofficial — Amazon could change it; it falls back to the book's Amazon page, and is tested per
  app version.
- Needs the book's Kindle edition. iPhone / iPad use Cloud Reader (no app link there is tested).
- Countries: not this task's problem — ReaderWrangler as a whole is US-store only today (see "Say plainly what ReaderWrangler works with").

**How (technical)**
- One helper picks the link from the platform (`navigator.userAgentData` / user agent) and the book's ownership and
  format; the desktop, the right-click menu and the phone call it. The links and what we learned about them: see TODO
  notes.

#### Amazon's official catalog API: prices, titles and covers without a bookmarklet, once eligible
<!-- id 20261021-1349 -->

_Why it matters:_ An official API can't be broken by a page redesign — a sturdier source for the prices behind price
goals. And it closes, for catalog facts, the gap that "the app can't ask Amazon for anything — only a bookmarklet on
Amazon's page can" keeps opening.

**What it is** (Ron + Claude, 2026-10-21): the **Creators API**, the successor to Amazon's Product Advertising API
(PA-API 5, retired). A **catalog** API — what Amazon sells (titles, prices, images by ASIN), never what *you* own — so
it can never replace the library fetch. RW never used PA-API (checked 2026-10-21), so nothing is broken today.

**What it would take**
1. **Eligibility:** an Amazon Associates account — RW already has one (its "View on Amazon" / Share links carry the
   affiliate tag) — with **10 qualifying sales in the past 30 days** (2026-10-21: 6 ordered, 0 shipped, $0 earned —
   none qualifying yet).
2. **A server for the credentials** — already there: the relay worker can hold them, look prices up 10 per request,
   and keep them only as long as Amazon allows.
3. **Only the generic catalog facts move.** Account-specific signals — "you bought this on ‹date›", Prime / Kindle
   Unlimited status — stay in the signed-in fetch.
4. **Signed lookups, with a daily cap** (2026-11-03): a relay that looks up Amazon prices is a new kind of service —
   unprotected, anyone could use it as a free price lookup and burn our Amazon allowance. Lookups take the same signed
   requests as writes (7.25) — only a real Cloud Sync channel can ask — plus a per-channel daily cap.

**Placed above the tasks that will use it** (Ron, 2026-11-03) — moved here from Prices. Both work without it, and are
better with it (title, price and cover by book number, asked by the relay, no bookmarklet):
- "Book recommendations…" — the book window for books you don't have yet (instead of prefetching their details);
- "Capture book ideas from your phone…" — a shared link becomes a complete wishlist entry on its own.

Details: see TODO notes.

#### Book recommendations: similar books you own, and ones you don't have yet
<!-- id 20261014-1030h -->

_Why it matters:_ "Unbury your next great read" — when you finish a book, see the similar ones already in your library
(unread first), and the ones you don't have yet. Amazon's own page mixes these together and doesn't know your
wishlist; ReaderWrangler can separate them.

**Found 2026-11-03** (Ron + Claude; details and the evidence: see TODO notes)
1. **The library fetch's Amazon-tags request can also return Amazon's "more like this" list** (10 per book, more with
   paging) at no extra request — but **Amazon already leaves out the books you own** (proven: a book shown in Amazon's
   web carousel as one you bought was missing from the list). Pre-orders do come through. Nothing we found brings your own
   books back.
2. **Amazon tags are rich but rare in your library:** each tagged book has ~15–18 (Coraline's run from "Magical
   Realism" to "Spine-Chilling Horror") — but only **27 of Ron's 2,799 books have them** (09-02 backup): the fetch adds
   Amazon tags to just 10 books per run.
3. The old spec's claim that the list was "already fetched, just discarded" was wrong — the request asks for Amazon tags
   only today.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review) — in build order
1. **Amazon-tag coverage first.** Every part below depends on it (and so would anything else built on Amazon tags).
   Decide how coverage catches up: more books per fetch (paced, with the human-check stop), catching up over several
   fetches, or as part of "Refresh all books from Amazon".
2. **"Similar books you own" — worked out in the app, no request to Amazon:** the books in your library sharing the
   most Amazon tags with this one, unread first. "Amazon tags" throughout — never confused with your own ReaderWrangler
   tags.
3. **"Books like this you don't have yet" — Amazon's list,** badged with what ReaderWrangler knows and Amazon's list
   doesn't show: **On your wishlist**, **Pre-ordered** (one shared helper badges any ownership kind, so nothing is
   special-cased).
4. **A click opens the book window either way** (Ron) — one experience regardless of ownership; the title and picture
   go to Amazon as they do today. **To decide in this task: prefetch the details of books you don't have, or not.** The
   app can't ask Amazon for anything itself (only the bookmarklet, on Amazon's site, can), so the window needs stored
   details. If prefetched:
   - the details include the **description** (Ron: the reviews are what make entries big — leave those out);
   - fetched as the fetcher's **last, optional step**, after the upload — like today's removed-books check ("Already
     saved — safe to close this tab"), so closing the tab only skips it;
   - a book recommended for many of yours is stored once;
   - the window then offers **Add to Wishlist** in one click (the price comes with the next wishlist price fetch).
   If not prefetched: books you don't have open their Amazon page instead — or, once eligible, the window is built from
   "Amazon's official catalog API…" (the task above), with no prefetching at all.
5. **Store book numbers for the lists**, not copies of the books.

**Spec:** docs/design/BOOK-RECOMMENDATIONS.md (its UI design predates these findings — revise it in this task; Amazon's
side: see TODO notes).

#### Show who a book is shared with (Family Library)
<!-- id 20261014-1030ar -->

_Why it matters:_ See sharing at a glance in the book window. Ron shares books with two family members through Amazon's
Family Library (2026-11-03), and today nothing in ReaderWrangler says which.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review)
1. **Cheap, and researched** (2026-01-08; Amazon's side: see TODO notes): two requests in the collections fetcher —
   your household, then the sharing of your **whole library** in one. Re-check them before building — the research is
   10 months old and predates Ron's second family member; its test script no longer exists.
2. **Books you shared out:** a **"Shared with: <name>"** line in the book window. No badge on covers (too noisy); a
   "Shared" filter only if asked.
3. **Books shared to you** already arrive with the library fetch, labeled **"Borrowed"** — but a Family Library book
   doesn't expire like a loan. Relabel them, e.g. **"Shared with you (Family Library)"**, in this task.
4. **Privacy — this stores other people's names** (in backups, which are plain files, and Cloud Sync, which is
   encrypted). The names **never go into anything you send out** (Share by Email, the Copy… outputs): the book-field
   table marks the field "never in shared text", so it's enforced in one place, not remembered.
5. **Sharing or unsharing from ReaderWrangler is out** — it would write to your Amazon account (the same big MAYBE as
   "Edit Kindle collections from ReaderWrangler").

#### Two-pane split view
<!-- id 20261014-1030bb -->

_Why it matters:_ Work with two folders side by side — the "10% case": put a book at an exact spot in another folder
without dropping it at the top and moving it again.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review)
1. **Two windows side by side comes first, nearly free:** once "Keep your tabs and browsers in step…" ships, every tab
   stays editable and current — open two windows, one folder each (the spec's option B, as a by-product). Copy and paste
   between them works.
2. **Then check dragging between the two windows.** The spec's "drag-and-drop does NOT work across browser tabs" isn't
   right in general: ReaderWrangler's drags use the browser's own drag-and-drop, which can cross windows. Unknown: whether
   a drop has enough to finish a move that started in another window (the app may hold the dragged books in its own
   memory, not in the drag). This is the tabs task's open question "Dragging between tabs — allow it or not?".
3. **Build the in-app split view (the spec's option A, 8–12 hours) only if that falls short** for the 10% case.

**Spec:** docs/design/archive/DUAL-PANE-SPLIT.md (options A and B; its decision note points here).

#### Library statistics: your unread pile, books per year, top authors and series
<!-- id 20261014-1030aj -->

_Why it matters:_ "Unbury your next great read" in numbers — how big your unread pile is, how old its oldest book is,
which series you started and never finished. (Was "Reading statistics".)

**Decided** (Ron + Claude, 2026-11-03, in the TODO review)
1. **Library statistics, not reading statistics:** there's no reading data beyond Read / Unread (no dates read — see
   "Find out whether reading progress can be fetched from Amazon", Someday). The library data is rich and all local, no
   request to Amazon: when each book was acquired, ownership kind, authors, series and positions, formats, Read /
   Unread, your rating and Amazon's, wishlist prices. (Not the price you paid — ReaderWrangler doesn't have it.)
2. **Candidates:** the unread pile (how many, the oldest still waiting); books acquired per year and how many of each
   year's are still unread; top authors and series, and series started but not finished; the ownership mix.
3. **Every number is clickable** — "412 unread" opens a Search showing those 412. That's what makes it a tool, not
   trivia.
4. **First step: Ron picks the 3–5 numbers he'd actually look at** — not a sprawling dashboard.

#### Import book details from a list or spreadsheet; Goodreads / StoryGraph files in and out
<!-- id 20261014-1030y; merged 20261014-1030n -->

_Why it matters:_ A way to bring in information from outside Amazon — and to share your library with the reading sites
people already use.

**What you'd get**
- Paste a list or load a spreadsheet (CSV); ReaderWrangler matches the rows to your books (by title or ASIN, with a
  review step — never applied blind).
- **Goodreads / StoryGraph exports in:** read status, your ratings, shelves as tags — the same shape as the spec's CSV
  tier.
- **Your library out, in Goodreads' spreadsheet format,** so Goodreads or StoryGraph can import your Kindle library in
  one go — a column layout for the existing Save as Spreadsheet (7.10), not a new feature.

**Decided** (Ron + Claude, 2026-11-03, in the TODO review — merged "Connect with Goodreads / StoryGraph")
- **Files, not a live connection:** Goodreads stopped giving out access to its connection service in December 2020 and
  has none today; StoryGraph has none either — both trade files (StoryGraph reads Goodreads' format).

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
   shows it in a short **"To look up"** list on the next Import. Links and ASINs show with **Open on Amazon**, where the
   Add Book to Wishlist bookmarklet does the full add; plain text you resolve with a click (search Amazon, add, put in a
   Book List). (Corrected 2026-11-03: a link can't become a complete wishlist entry by itself — neither the app nor
   the phone can ask Amazon for a title or price; only a bookmarklet on Amazon's page can. Later, the planned "requests
   from the app to the bookmarklet" channel — the one "Refresh all books from Amazon" uses — could fill them all in on
   the next fetch; or, once eligible, "Amazon's official catalog API…" (Features) completes each one as it arrives.)
3. A whole Claude answer can be shared at once and worked through on the desktop. Picking titles out of free text
   automatically stays human — too unreliable.

**Caveats**
- **The phone would write to the cloud for the first time** (2026-11-03). Today it only reads — "Reads the relay, never
  writes it" is a stated rule (MULTI-INSTANCE.md §1). Since 7.25 every write is signed with the key made from the
  passphrase; the phone already holds it (it decrypts), so it signs with the same signer as the desktop. Update the
  stated rule when this is built. The relay needs nothing new (it already takes single signed letters).
- Android / Chrome only (iPhone doesn't support web-app share targets). Plain-text items carry no book details until
  resolved. Medium-sized: a phone capture screen, a new relay letter kind, a desktop list.

**Status:** after launch (Ron, 2026-10-15: "there comes a time in every project where you have to shoot the engineer
and release it").

**How (technical)**
- Web Share Target (`share_target` in the phone app's manifest); a single-letter mailbox run (as the wishlist fetcher
  sends) carrying `{url|asin|text}`; the desktop's Import routes those letters to the "To look up" list.

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
- `formatWatch: 'kindle'` on print placeholders. The "slow refresh" it was to share became "Fetcher: refresh ratings with
  the price check" (Polish, 2026-11-03) — if the batch request reports other editions, this check can ride the price
  check the same way, with no schedule. (Outside review item 6.)

#### Phone: change Book Lists and tags
<!-- id 20261122-1536 -->

_Why it matters:_ Browsing on the phone is where you notice a book is finished or wanted — take a read book out of a
"To Read" Book List, put one in, add or remove the "Read" tag — and today the phone can only look (Ron, 2026-11-22).

**Wished** (Ron, 2026-11-22, during outside review 3: "I'd prefer if the design left room for the mobile to be a
writer"):
1. **Leave room now:** nothing built before this may assume the phone never writes. The stated rule "the phone reads
   the relay, never writes it" (MULTI-INSTANCE.md §1, RELAY-WRITE-REDESIGN.md §2b) is today's fact, not a design
   promise; "Keep your tabs and browsers in step" treats the phone as one more browser under "never replace a version
   you haven't seen".
2. **How it could travel:** the phone already holds the key and signs like the desktop ("Capture book ideas from your
   phone" — the same signed single letters); an edit letter the desktop applies at its next Import, or — simpler —
   through "One copy instead of two" (Relay and sync), where the phone writes the one copy like any browser.
3. Undecided: which edits (Book Lists and tags first; folders?), and what the phone shows when the desktop changed the
   same book.

### Technical clean-up

_Formerly: Tech / performance_

#### A hand-over guide: how anyone can run ReaderWrangler on their own accounts
<!-- id 20261120-1700d -->

_Why it matters:_ The code is open, but nobody else holds the accounts it runs on, and there's no named successor. If
Ron can't continue, the app should be able to outlive him (outside review 1, Risk 13 and Question 5).

**Decided** (Ron, 2026-11-20): a guide **for someone to repeat Ron's steps with their own accounts** — which accounts
(GitHub Pages, a domain, Cloudflare for Cloud Sync, Resend for email, GoatCounter, Amazon Associates if wanted), how
each is set up, and every place the app names the site or the relay, so a clone can be pointed at new ones. After
launch. The one before-launch piece is the LICENSE's continuity exception ("A one-day truth-and-safety release",
item 13).

#### Split the main code file into modules
<!-- id 20261014-1030at -->

_Why it matters:_ One very large file is harder to work in safely — and the real problem is inside it: one giant
component.

**Re-assessed 2026-11-03** (Ron + Claude, in the TODO review)
- The spec (August) describes a 3,862-line file and a 4–6 hour split. The file is now **20,455 lines** (1.65 MB), ~200
  pieces of state, most of it inside **one component** thousands of lines long. That's where bugs hide: "With a
  filter on, the right pane still shows subfolders…" (Small fixes) is a name used 5,400 lines before it's declared,
  in the same function. Splitting the file without splitting the component would only move the problem.

**Decided**
1. **No big-bang project** (the ground rule: refactor while you work; don't plan refactoring projects). Instead:
   - **A short map of the natural seams** — the left pane, the right pane, each big dialog, the menus — the pieces to
     lift out, each as its own component and file, **whenever work touches them anyway**. Write the map first (in
     the spec, replacing its old table).
2. **After "Faster loading: build the app ahead of time"** — with a build step, files can properly include each other
   instead of sharing global names; splitting is cleaner and safer then.
3. **Optional, decide when building — a ratchet so it can't creep back:** a commit check that refuses a *new* large
   component added to the main file (it goes in its own file). A ratchet, not a project.

**Spec:** docs/design/MODULE-SPLIT.md (superseded by this task until the seam map replaces it).
**Tool survey 2026-11-03** (docs/design/TOOL-SURVEY.md): the official typescript-lsp plugin (go-to-definition and find-references across
the big file) and ast-grep (structural search-and-replace) when lifting pieces out.

#### Test on Safari and iPhone
<!-- id 20261014-1030ax -->

_Why it matters:_ **Every browser on an iPhone is Safari underneath** (Apple requires it — Chrome on iPhone is Safari's
engine), so "works with Chrome" means "not on iPhone", phone view included — and many US Kindle readers carry
iPhones. Some Safari differences could break storage, installing as a phone app, or layout.

**Decided** (Ron + Claude, 2026-11-04, in the TODO review — moved up from Someday)
1. **First pass, cheap: run the browser driver's tests under Safari's engine on Windows** (Playwright's WebKit — not a
   real iPhone, but it catches most engine differences: storage, layout, the phone view). Once the driver exists.
2. **Outside review 1 (launch risks) weighs "iPhone at launch, or not"** — what we promise, and to whom; its answer
   sets the honest line in "Say plainly what ReaderWrangler works with…".
3. **Then a real iPhone check** — Ron has access to one (2026-11-04): the phone view, installing to the home screen,
   storage surviving a few days, Cloud Reader for "Read in Kindle".

**Risks to check**
- The browser's book storage (IndexedDB) — Safari clears a site's stored data after 7 days of Safari use without a
  visit to it, but exempts apps installed to the home screen (to verify when testing; it would make installing the
  phone view the recommended way on iPhone) — installing as a phone app (PWA), and styling.

#### Our working names in the code and docs: Fetched Copy, Complete Copy, compact view, full view
<!-- id 20261122-1608 -->

_Why it matters:_ Muddled names lead to muddled thinking (Ron, 2026-11-22): "device-state" is your whole library, not a
device's state, and "the phone page" also opens on a computer. The new names are decided (GLOSSARY.md, "Our working
names"); the code, comments and design docs still use the old ones.

**Decided** (Ron, 2026-11-22, during outside review 3):
1. **Fetched Copy** (was "canonical"), **Complete Copy** (was "device-state"), **compact view** (was "the phone page /
   mobile"), **full view** (was "the desktop app") — used in our talk and new writing from now on; Claude corrects the
   old names when they slip in.
2. **Not now:** renaming the code's names, comments and design docs is a sweep for a quiet time — a class-of-sites change
   (the comb), and the relay's stored key names (`relay:{id}:device-state`…) are a stored format: those stay, or
   change only with a migration and a design Ron has seen.
3. **When it migrates,** the old names go to the glossary's anti-list, so nothing new uses them.

#### Tests and tools run under a venv named for its Python, called by its path
<!-- id 20261123-1655 -->

_Why it matters:_ Which Python runs the tests must not depend on the path, the `py` launcher's default or how VS Code
started. On 2026-11-23 a test that passed on Nov 19 failed every time with no code changed: the commit check calls a
bare `python`, and since the 11-20 restart this session had the venv active, so `python` was a different interpreter.
A bare `python` or `py` gets whichever Python the path or the launcher happens to pick — and the global packages,
not the project's known-working versions.

**Decided** (Ron, 2026-11-23):
1. **A venv is named for its Python version** — `.venv314` for today's (3.14); another version gets its own
   (`.venv313`…), so several can sit side by side without confusion, and a tool that needs another version gets its
   own venv.
2. **Tests and tools run under the project's venv, never the global Python:** the commit check and every tool that
   starts Python call the venv's interpreter **by its path** (`.venv314\Scripts\python.exe`). Checked 2026-11-23: run
   that way, with nothing activated, Python uses the venv's packages and only those (`pyvenv.cfg` tells it);
   `activate` only puts `Scripts` first on the shell's path, sets `VIRTUAL_ENV` and changes the prompt. **No venv →
   stop loud** with the one command that makes it (`py -3.14 -m venv .venv314`, then `pip install -r
   requirements-dev.txt`).
3. **Launcher-safe:** a venv's `python.exe` on Windows starts the real interpreter as a second process, so nothing
   may assume a started program's process id is its own (RUN-057's fix, fc6bb79).
4. **A venv still leans on its base:** `pyvenv.cfg` points at the Python it was made from — uninstalling that Python
   breaks the venv. The versioned name says which base it needs.
5. **The sweep** (the comb — site-map before claiming coverage): `git-hooks/pre-commit` and every hook that calls
   Python; `tools/run_tests.py` (starts tests with its own interpreter); `tools/copies.py` (links the venv into each
   copy); `tools/merge_branches.py`; the double-click scripts (pytools `keepopen`); `.gitignore`; VS Code's interpreter
   setting; `docs/design/TESTING.md`, `SESSION-TOOLING.md`; `requirements-dev.txt`'s instructions.
6. **The Projects-root `CLAUDE-TOOLING.md`** gets the rule for every project — a venv named for its Python; hooks and
   tools call it by path, never a bare `python` / `py` — next to pytools' how-to.
7. Enforcement code (`git-hooks/`, `tools/run_tests.py`, `tools/merge_branches.py`, the CLAUDE files): its own branch,
   built with Ron's word.

#### A "machine's trouble" that repeats the same way, run alone, says it's probably not the machine
<!-- id 20261123-1656 -->

_Why it matters:_ On 2026-11-23 RUN-057 stalled at the same check four times, twice rerun alone with the whole PC to
itself, and each time the runner said "not proven — the machine was too busy". It was a real bug (the test's stand-in
under a venv launcher, fixed in fc6bb79). The label hid it for hours, blocked a commit, and sent us looking at Windows
updates and a crash.

**Decided** (Ron, 2026-11-23 — his word to change `tools/run_tests.py` for it):
1. When a file's rerun alone stops at the **same check, the same way** as its first run, the runner says so plainly —
   *"the same check stalled the same way twice, run alone: probably a real problem, not the machine"* — naming the
   check. Still "not proven" (the commit stays refused), but the words stop pointing at the PC.
2. Test first: a stand-in that stalls the same way every time must get the new words; one that stalls once and then
   passes keeps today's.
3. Enforcement code (`tools/run_tests.py`): its own branch.
4. **Sized 2026-11-23 — not a "do it now" fix** (Ron: do it now only if quick): it touches the rerun's record, its
   printed line, the summary and the stamp (`tools/run_tests.py` ~645, ~957, ~1189, ~1262); the runner's own tests
   already model "the same trouble twice, rerun alone" as the machine's (test/test_run_tests.py ~1342 — Ron's
   2026-11-17 design), so it changes tested behavior; and "the same reason twice" reads the same for a real bug and a
   truly slow PC — telling them apart (e.g. a reason that stalls at the same step every time vs. a slow start) is the
   design question.

---

## 👀 Watching

Not work to do — conditions to watch for. Each says what to check if it happens again. (Ron, 2026-10-15)

### Turn more of our working rules into automatic checks (my tooling)
<!-- id 20260922-0000c -->

**Parked in Watching 2026-11-19** (Ron's decision after the outside review — Law 23, "A mechanism has a cost"): no more tooling is built from this list unless a failure here actually recurs; then weigh it by Law 23 first.

_Why it matters:_ Rules that depend on memory keep failing; automatic checks don't. This affects only how I work, not the app.

**Already done**
- The pre-build checklist watches all app code (2026-10-08); a bounce refuses the whole batch of edits, so none goes
  missing (2026-10-16).
- Since then, more checks run on every commit: the undefined-names check, the version stamps (now incl. the relay worker), and the TODO table of contents.

**Left**
- Item 1 below, and the rule-by-rule sort of PRINCIPLES.md (items 3 and 4: ✅ 2026-11-12, in `main-prime` for review).

**The idea** (Ron, 2026-09-22, after "assuming bit us again")
- Go through docs/PRINCIPLES.md rule by rule and sort each one:
  - **Can become an automatic check** that blocks a commit or release — for example: run the tests before a commit; search for leftover TODO / REMOVE markers before release; version bumped when code changed; cache-busters match.
  - **Judgment only** (never assume, model the legal states, UX first). A hook can only *remind*, and reminders fade into rubber stamps. Give these teeth with a required artifact instead: e.g. every design doc must have an **"Assumptions (and how each was verified)"** section, which a hook can check exists when a design doc is written — catching assumptions at design time, not just at edit time.
- Guard against reminder bloat — the pre-build checklist is already 11 points.

**Open items**
1. ✅ **My code safety check can be skipped by accident** — done 2026-11-16 (sprint 6, after two agents moved version
   stamps with `sed` that week): the pre-build gate also fires for terminal commands that write shipped code — `sed -i`,
   `perl -i`, redirects, `tee`, `cp`/`mv`, PowerShell `Set-Content`/`Out-File`, python/node one-liners
   (`.claude/hooks/command_writes.py`; GATE-002–009). Not covered, by design: targets in variables or loops, scripts run
   from a file, `xargs`/`find -exec`, `patch` (see SESSION-TOOLING.md).
2. ✅ **The version check reads only readerwrangler.html's cache-busters** (found 2026-11-09, 7.26.0-alpha.20) — done
   in 7.27.0: every page's `?v=` stamps are read from the page itself (test/test_version_guard.py, VG-001–005).
3. ✅ **The relay tests start and stop their own local relay** (7.28.0 post-mortem) — done 2026-11-12 (autonomous
   trial): `tools/local_relay.py`; `run_tests.py --tier 3` with no `--relay-url` starts wrangler's local emulator on a
   free port, stops each process it proves it started (by exact id, never `/T`), and checks every port is free
   (RUN-016–021). ✅ Follow-up done 2026-11-16 (sprint 5): the screen tests' own relay starter (`test/ui/rw.py`
   `LocalRelay`, a second copy that stopped processes with `/T`) is gone — they use `tools/local_relay.py`, whose
   readiness is now proven against its own processes, retrying on new ports when another process holds one
   (RUN-052, 053, 057).
4. ✅ **A release run counts "skipped" as failed** (7.28.0 post-mortem) — done 2026-11-12: `run_tests.py --release`
   fails on any skipped file, naming it and why (RUN-022–024). The release checklist's line in CLAUDE.md names it
   (Ron, 2026-11-12).
5. ✅ **A test file can be set aside on purpose — a `skip:` line naming its TODO** — done 2026-11-16 (sprint 6): the
   runner doesn't run it and says so in every summary; the TODO id must exist; `--release` refuses while any file is set
   aside; the stamp counts such a run as not full (RUN-065–070). Use judiciously (Ron, 2026-11-12).
6. ✅ **`--id` narrows a file split into shards** — done 2026-11-16 (sprint 6): `--id TOAST-006` runs that one cell in
   one process (6 s, was all 132); RUN-060–062.
7. ✅ **`--id` picks a file only where it names the id as a test** — done 2026-11-16 (sprint 6): one lookup
   (`test_names()`) of test calls and table rows, comments dropped; `--id CELL-005` picks test_cells.py alone
   (RUN-063, 064). The stamp also shows tier 3 now (information only; RUN-071).
8. **Logging kit leftovers** (sprint 6): the bar's **Report this problem** copies the diagnostics without the bar's
   messages first (Copy now puts them first — one copy routine should); a one-line `codeOf` helper exists twice in
   logkit/logger.js (Law 22); the phone and the reset page don't hand the kit a report button or the diagnostics copy;
   the critical box still shows "(code …)" to everyone — **Ron's call** (asked 2026-11-16: the bar's rule, no code on
   screen for ordinary users?). Small.
9. ✅ **A failed test file's full output is kept; the machine's or the browser's trouble is rerun once, alone** — done
   2026-11-17 (sprint 7; Ron, 2026-11-16: "Detect that is what it is, back off and slow down and repeat"): every failed
   file's whole output (and its screenshot) is kept beside the run's record — the summary names the path; the
   screen-test driver says ENVIRONMENT with exit 3 when the page never loaded, the browser closed or crashed, our server
   or relay didn't start, or a request to our own server failed for the machine's reasons (e.g. `ERR_NO_BUFFER_SPACE`);
   such a file is rerun once, alone (every slot held), said loudly and noted on the stamp; a test failure is never
   rerun (RUN-072–082, ENV-001–004). (Its first fixed rule — under 4 GB of free memory 2 browsers, under 2 GB 1 — was
   replaced by item 10.)
10. ✅ **The runner chooses how many browsers to run at once by itself** — done 2026-11-17 (sprint 7; Ron's design,
   "similar to how TCP works"): 1 to 6, saved per PC; halved at once on the machine's trouble; one more after a clean
   full run; back down when one more gained nothing (then held for 5 runs); only fully passing runs count. Heavy tier-1
   files (`heavy: yes — why` in their header) take a test slot inside that number and back it off too; a library that
   failed to download from its site counts as the network's trouble, not a test failure. Checked with a load lab that
   squeezed the PC on purpose (Ron's idea): the number came down under load (5 → 2 → 1) and, once the load was gone,
   climbed back one step per clean run (2 → 3 → 4 → 5).
11. **Left over from sprint 7** (filed 2026-11-17):
   1. ✅ 79 fixed waits ("sleep 2 s") in 15 screen-test files (test_cells 25, test_delete_key 14, test_rename_key 9 …) —
      each one is a guess that a slow PC breaks; wait for the condition instead, as test_reset.py now does. — Done
      2026-11-18 (sprint 8, three agents by file): each now waits for the thing itself under a generous limit; the 11
      that prove a duration or that nothing happens stay, marked `# timed on purpose`; every file passed 3+ runs and
      failed when a condition was broken on purpose; no app bug was hiding behind them except the false Restore
      Warning (filed in Polish).
   2. ✅ No test runs a heavy tier-1 file end to end that exits with "the machine's trouble" and checks the number backs
      off and the stopped count is right (the pieces are tested; the whole path only by hand). — Done 2026-11-18
      (sprint 8): test_run_tests.py's ending is one shared routine (`environment_trouble.tally`), and RUN-093 runs a
      stand-in that ends the same way through the real runner: "1 stopped by the machine's trouble" and exit 3 → the
      level 4 → 2, saved in its own slots folder → rerun alone, passed → the summary's counts and the record checked.
      Shown failing with the path broken on purpose, on each side.
   3. ✅ A test file can lose a line by joining it onto a comment by accident and still pass — no check catches that.
      Done 2026-11-18 (sprint 8): the commit check `git-hooks/check-joined.py` (pre-commit step 11) refuses a staged
      test file whose comment ends in a complete line of code; `# not-joined: <why>` for one that does on purpose;
      `--all` checks every test file (JOIN-001–045).
   4. ✅ RUN-049 still waits a fixed 20 s for its partner file to start; under heavy load that can fail. — Done
      2026-11-18 (sprint 8): each file waits for the other's mark, up to 180 s (only a real failure gets there); a
      partner the runner started with it but the machine made slower than that is the machine's (`partner_late` in
      test_run_tests.py, beside `standin_late`; the check is stopped, the file rerun alone), a pair run one after the
      other is a failure (RUN-094). Shown first: the old RUN-049 failed with its partner 25 s late; the new one passes.
   5. With `--tier all`, heavy tier-1 files and screen tests compete for the same slots — not yet timed under load.
   6. ✅ A working copy's test-run records are deleted with the copy (`tools/copies.py remove`), so how long an agent's
      own test runs took can't be counted afterwards — keep them (move them into the main folder's records), and have
      the removal print where that copy's time went (Ron, 2026-11-18: "Should the agents record where their time
      goes … so we can analyze that?"): from the copy's start to its removal — its test runs (how many, minutes,
      passed or failed, full or narrow) and the rest (building), kept per copy for the sprint's post-mortem. — Done
      2026-11-18 (sprint 8): `copies.py remove` keeps them in `.git\rw-test-results\copies\<name>-<when>\` with
      `time.txt` (also printed), and `copies.py report [--since]` lists the removed copies (SESSION-TOOLING.md;
      COPY-007–009).
   7. ✅ A file that needs a rerun alone (the machine's trouble) two or three runs in a row is said loudly — it may truly
      need to run alone (Ron, 2026-11-18). So far it has never been the same file: five files, once each, all under
      the load lab, each passed alone. — Done 2026-11-18 (sprint 8): 2 whole runs of the file in a row (from the working
      copy's run records; a run that didn't run it, or only some of its cells, is passed over) → a loud line at the end
      of the run naming the file, how many runs, and each run's kept outputs; nothing about what runs changes
      (TESTING.md §4; RUN-092).
12. **Measure each test; schedule by what it uses, not by how many** (Ron, 2026-11-17 — being talked through; TCP
   counts its window in bytes, not packets): per file and per PC, keep a smoothed average and spread (TCP's own method
   for round-trip times) of its time, peak memory, CPU and disk; the browsers-at-once number becomes a budget (e.g. GB
   of memory) that each test is charged against, checked also against what's free on the PC right now; same halving and
   raising rules. Steps: (1) measure only, and see whether tests differ enough to matter; (2) the load lab squeezes one
   resource at a time, to learn which one breaks runs; (3) the budget; (4) longest-first and a "stuck" limit from the
   averages instead of a flat 10 minutes.
   1. ✅ **Step 1, measuring, built 2026-11-18** (sprint 8, `tools/test_costs.py`; TESTING.md §4): every test file (and
      each shard) is measured for all the processes it starts — time, memory committed, the RAM it adds (its private
      RAM, sampled), CPU, I/O — in each run's record; a running average and spread per PC, learned only from full runs
      that passed; `py tools/run_tests.py --costs` shows them, and whether the biggest screen test uses at least twice
      the RAM of the smallest. First look, three screen tests one at a time: 0.39–0.59 GB of private RAM each (1.5×
      apart) — not twice. A full run's averages answer it.
   2. ✅ **Step 4, longest first and a "stuck" limit from the averages, built 2026-11-18** (sprint 8; Ron's rule the same
      day: "longest first by each file's average, and a 'stuck' limit of average + 4 spreads (never above today's 10
      minutes): act once every file has at least 5 runs measured"; TESTING.md §4, §7): tests start longest first by
      their average on this PC; a test with 5+ runs gets a limit of average + 4 spreads, at least twice its average or a
      minute, at most 10 minutes (the 10 minutes stays for fewer runs and for narrowed runs). Past it, the test is
      stopped with everything it started, said plainly ("ran past its usual time"), the browsers at once halved, and it
      is rerun alone with the full 10 minutes — past that too, a failure. Its next runs keep the 10 minutes until one
      passes the first time (TCP keeps its backed-off timer the same way), so a test that truly got slower relearns its
      average instead of being stopped every run. Today's averages: test_backlog_report.py first (141 s → limit 283 s).
      (2026-11-18 lab: floor raised to 4× the average / 120 s; trouble beyond the rerun cap is 'not proven', never a
      failure)
13. **Found while building sprint 8** (filed 2026-11-18) — **sub-items 1–10, 12 and 13 done 2026-11-18 (sprint 9)**;
   11, 14 and 15 are notes to keep:
   1. ✅ A run of only the tests covering what changed (`--changed`, what the commit check runs) and a test file run
      directly write no record — so an agent's own test time lands in "everything else" in a copy's time report.
      Recording them would mean a record on every commit (more pruning, more kept output) — Ron's call.
   2. ✅ Two "write a file whole, retry if Windows refuses the swap" routines — `tools/build.py`'s and
      `browser_level.save` — should be one (Law 22).
   3. ✅ Tier 3's local relay runs outside each relay test's measurement, so tier-3 costs leave it out.
   4. ✅ A process still running after its test ends isn't reported; the test's measurement already knows how many are
      still running — a cheap leftover check (belongs with "One starter for every process our tools start").
   5. ✅ The copies' archive (`rw-test-results\copies\`) is never trimmed — small, but it grows forever.
   6. ✅ The joined-line check (commit check step 11) doesn't catch a comment line of dashes followed by one space and
      code, nor `'use strict'`; its glued-inside-a-word scan is slow on very long comments (fine today).
   7. ✅ The screen tests' new wait helpers live in several files (Law 22): `until`, `toast`, `LIMIT_MS` twice (the two
      key files); `caught_up`, `settled`, `heard`, `held`, `amber_look` in test_cells.py; `wait_loaded` in rw.py — move
      them into rw.py as one set, with one step limit for the library.
   8. ✅ test_cells.py still has ~39 condition waits with a 3-second limit (and 11 at 4–10 s) — not fixed waits, but the
      same "a slow PC breaks it" guess; give them the generous limit.
   9. ✅ `test/ui/harness.py`'s `done()` repeats what `environment_trouble.tally` now does (summary, stopped count, exit
      code, marked line) — one implementation (Law 22).
   10. ✅ The "rerun alone runs in a row" alert reads only the folder's own records — a file troubled in an agent's copy
      and then in the merge doesn't add up (the copies' archive isn't read). → Folded into "a file that can't be
      proven is held" (sub-item 13 below, decided 2026-11-18): the in-a-row count lives per PC.
   11. Found by the test_cells agent: after an Escape, Chrome gave the page no idle time for 3–5 s — so any future
      "wait until the page is idle" helper must not rely on idle callbacks (caught_up uses a task-queue flush).
   12. ✅ `tools/copies.py new` calls a tier-1 run that ended "not proven — the machine was too busy" (exit 3) "tier 1
      failed" — right to refuse, wrong words (the merge script already says "not proven").
   13. ✅ A file rerun alone that meets the machine's trouble AGAIN still counts as a failure (TESTING.md: "failed again,
      it's a failure") — by sprint 8's rule "the machine's trouble is never a test failure" it may better be "not
      proven". **Ron, 2026-11-18: "I think not proven. But we don't want to go into an infinite try loop if a file is
      never going to run under current resources and loading … Give up after say 3 failures of same file and report
      it and await instruction from me?"**
      **Decided (Ron approved the proposal, 2026-11-18): a file that can't be proven is held.**
      1. Within one run nothing changes in count: a file in the machine's trouble is rerun alone once; if the rerun
         meets the trouble again it is **"not proven"**, not failed. One run never retries more than once.
      2. Across runs: **3 runs in a row "not proven" for the same file → the file is held** — recorded per PC (in the
         slots folder, so runs in working copies and in the merge all count — this absorbs sub-item 10) and said loudly:
         "test_x couldn't be proven in 3 runs in a row on this PC — held for Ron's decision".
      3. Later runs don't run a held file: they report it "held — not run", so they can't be proven and nothing merges
         past it — that block IS the "await instruction"; in a sprint it goes to the review queue and its task parks.
      4. Ron's choices then: release it (try again), run it alone every time, or set it aside with a `skip:` line naming
         a TODO (the existing way).
   14. The commit check refuses a commit when its covering tests end "not proven" (a busy PC, no test failed) — right
      (not proof), but a busy PC can then block a commit; worth knowing, maybe saying so in the refusal.
   15. From the sprint 8 labs: when OTHER programs take the CPU, fewer browsers is slower (2 at once 1,687 s vs 3 at
      once 924 s) — halving on trouble costs time there; and memory squeezed to 0.7 GB free broke nothing. **Ron,
      2026-11-18 (Q-045): item 12 closes here; "File the CPU budgeting as a potential TODO if there are any
      indications that the current back off based on failures is not sufficient."** — so: watch for that sign (runs
      not proven, or backed off for long, on an ordinary working day); only then a CPU budget (each test's CPU seconds
      are already measured) and/or a gentler back-off when other programs hold the CPU.
14. **Found while building sprint 9** (filed 2026-11-18):
   1. ENV-007 (and ENV-002/004) start a small test run of their own; when THAT run meets real machine trouble (it did
      twice: "no network buffer space"), the outer test reports a failure — it should report the machine's trouble.
   2. Six test IDs exist twice: COPY-001–006 in both the screen test for copying and the working-copy tool's test —
      `--id COPY-001` runs both; renumber one.
   3. A few step waits still allow 180 s (test_boot, test_reset, and three files' `LIMIT_S`) — above the runner's
      2-minute "stuck" floor, so a failing wait there can be reported as the machine's trouble first. Sprint 8 chose
      them on purpose (test_reset was proven under load) — splitting each into a step wait and a load wait is a choice.
   4. Waits with no limit written still get the browser driver's own 30 s default in most screen-test files — one line
      when the app opens (`set_default_timeout`) would give the whole library the shared limit.
   5. When many cells fail in test_cells.py at once, each costs a full wait, so a shard can pass its stuck limit and
      be reported as the machine's trouble rather than as its failures.
   6. The relay's own process group could also stop children that escaped it (as each test now does); today a test
      decides that such a child is "left running" — a design choice.
   7. A test that leaves processes behind is only caught in runs that measure (every recorded run); a test file run
      directly isn't.
   8. The tools' own processes (the local relay, its helper) still inherit git's variables — only test processes are
      cleaned.
   9. A held file's notes point at output kept in a working copy's records; when the copy is removed those move to the
      archive and the paths go stale.
   10. Even with `--quiet`, the commit check prints the "waiting for a test slot" lines.
   11. Now that the commit check's own runs are recorded: in the runner agent's copy they took 3–6 minutes each
      (heavy tier-1 files covering run_tests.py) — the next speed-up target for commits.
   12. **Nothing checks that what the working copies share stays healthy** (the sprint 9 incident: a test set the real
      repository's git settings to "bare" and every copy broke). Proposed mechanism: the runner checks the shared git
      settings (not bare; the commit checks on) before and after each run, and says loudly — with the one command that
      repairs it — if a run changed them. Law 5's proposed line (sprint 9 post-mortem) — Ron decides. → **Now its own
      task: "Working copies that can't break each other: separate clones, plus a check on what they still share"**
      (Ron, 2026-11-19: "Yes to belt and suspenders"). ✅ Done in sprint 10.
   13. (Sprint 10.) The settings' "ask before pushing to prod" rule (`Bash(git push prod:*)`) has no PowerShell
      counterpart and may miss `git -C <path> push prod main` — outside autonomous mode those could run without a
      prompt. Inside a sprint the new prod guard covers them.


### Generated test libraries: made-up books at any size, with their own covers
<!-- id 20261104-1613a -->

**Parked in Watching 2026-11-19** (the cold review of the TODO; Law 23): test infrastructure, not app work — built only if the failure it guards against recurs.

_Why it matters:_ Test data with nothing personal can be committed and backed up anywhere, is identical every run (a
failure always reproduces), plants the awkward cases on purpose, and comes in any size — so the tests stop leaning on
Ron's real library (Ron, 2026-11-04: "it would be nice to migrate away").

**Decided** (Ron + Claude, 2026-11-04 — Claude's call, Ron's ideas)
1. **Generated, not real**, for tests: one generator (today's `test/fixtures/make-small-fixture.js`, grown) with a
   **size setting** — 23 books for exact checks, ~3,000 for scale, 10,000 for stress — and **seeded**, so the same
   "random" library every run.
2. **Titles from a little title machine** (Ron's rules): *The [X] of [Y]*, *Adjective + Noun*, *A [Court] of
   [Starlight] and [Shadow]* (fantasy), *-ing* openers, *Hook: subtitle* (nonfiction) — word lists per category,
   picked by the seeded random ("A Kingdom of Teacups and Regret"). **Lorem-ipsum descriptions.** Cases a test depends on
   keep fixed names (the series a Search looks for, the folder names).
3. **Organization generated too:** folders by author with series subfolders, Book Lists by Amazon tags, some books in
   the Trash, hidden, wishlisted with goals, every ownership kind — the planted cases, at scale.
4. **Covers generated, served by the repo itself** — no website: a small **SVG** per cover (a solid background by genre,
   the title on top — a tiny text file, no image library needed) in `test/fixtures/covers/`, which serve.py already
   serves to the tests on Ron's PC: no internet, nothing test-related on readerwrangler.com or the home server, identical
   every run. The scale library reuses a pool of ~50 rather than committing thousands. (The one path that built an
   Amazon image link from the ASIN — the old CSV loader — was dead code, deleted in 7.26.0-alpha.1; nothing in the
   app's code builds one now, checked 2026-11-05. The screen tests' request detector would catch a new one.)
5. **Ron's library snapshot stays, used rarely** (`.private/test/`): only for "does real data have a quirk we never
   thought to generate" checks — real data catches what nobody imagined.

**How (technical)**
- Packed with the app's own book packer (bookFields.js `packBook`), as the small fixture is. TESTING.md §5 gains the
  sizes and the covers when built.
- **First user — a load-time test at scale** (the 7.27.0 post-mortem's "bug no test would have caught"): Ron's books
  took ~7 s to show on 7.27.0-alpha.1 while every screen test (23 books, no cover copies) said under a second. With a
  generated ~3,000-book library committed, a LOAD test can time "folders on screen" at that scale with a full cover
  cache (as tools/time_load.py does with the private copy) and fail on a regression — with a bound loose enough that a
  slow moment can't fail it.

### Receipts reach the screen: one screen test per area, not only the log
<!-- id 20261110-1021 -->

**Parked in Watching 2026-11-19** (the cold review of the TODO; Law 23): test infrastructure, not app work — built only if the failure it guards against recurs.

_Why it matters:_ Since 7.26.0 every toast goes through the log (`rwLog.log(…, { toast: true })`). If an edit drops the
`{ toast: true }`, the log still records the line, and no check notices that the person no longer sees it. That
happened once in 7.26.0, to the tag-delete receipt: it was found and fixed during the build, but not by any test (the
post-mortem's "bug no test would have caught").

**Done already (2026-11-10, Ron's yes):** `test/ui/test_tags.py` — TAGS-001 (delete one tag) and TAGS-002 (delete
two ticked tags) check that the receipt is on screen, on top and readable. Both were seen to fail with the receipts'
`{ toast: true }` removed.

**The rest — the class:** one such check for each area's main confirmation (ORG: create, rename, delete a folder, Book
List or Search; EDIT: a book's details saved, Bulk Edit; MOVE: a move's receipt; UNDO: Undo / Redo; BACKUP: Save Backup;
SYNC: Import from Relay's summary; AUTO; SHARE…), through the same helper (a toast holding the words, reached by the
pointer). **When:** after "Faster loading" (each screen test then starts in about a second instead of ~35).

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
- **Read the kept diagnostics log** (since 7.26.0: Help → Diagnostics…, or Copy diagnostics): it records every page load
  with the browser's own answer to "was this tab discarded and reloaded?" (`document.wasDiscarded`) — which settles the
  TinySuspender question without guesswork (added 2026-11-04).

**Done 2026-11-04** (Ron): localhost and readerwrangler.com whitelisted in TinySuspender (a suspended ReaderWrangler
tab can also tear an upload when you leave it).

### Find out why some books end up in no folder
<!-- id 20260903-0000b -->

_Why it matters:_ Rare reports of books in no folder at all; watch whether it still happens.

**What we know**
- One real user event on 6.11.5, and two more on 2026-09-03: books in the browser's book store that no folder refers to.
- 7.7.0 removed the leading suspect: a cold start reading an out-of-date folder list that didn't yet know the newest books.

**Next step**
- **Watch** for the event after releases before spending a session on it.
- **First, the Import-order fix** (2026-11-04, Ron + Claude): "Import files new books once, before the integrity
  check…" (✅ done in 7.26.0, removed from this list at release): an Import now files its new books before the check, so any
  homeless book reported after it is a real one — and the logging module (7.26.0) makes it noticeable (the "auto-fixed
  during restore" message is an error). Watch from 7.26.0 on.
- **Two real causes found** (2026-11-13, sprint 4's measurement — CELL-007, CELL-037): a cut pasted back into its own
  folder, and a copy pasted back into the same folder followed by Ctrl+Z, each left the books in no folder until the
  next reload. Both fixed in 7.30.0. Catching the next cause as it happens: "A book left in no folder is caught the
  moment it happens…" (shipped in 7.31.0 — next item).
- From 7.31.0 the event is caught when it happens: every save checks for books in no folder, puts them in the Inbox and
  logs INTEG-08 (error) naming the last action (done, 'Undo: …' or 'Redo: …', with seconds since) and the books — on the
  red bar for every user, with Report this problem. Watch for INTEG-08 reports; each names its suspect action. The
  load-time INTEG-02/04/06 stay as a second net.

**How (technical)**
- The event is `integrity-homeless`; the suspect was a stale `FOLDERS_KEY`.

### A screen test that failed once: the File menu not found after the start-up test
<!-- id 20261111-1825 -->

_Why it matters:_ A test that fails now and then teaches everyone to ignore failures (TESTING.md §7) — so one that
failed once is watched, not forgotten. (Moved here from "Logging as its own module" at its release, 7.28.0 — Ron.)

**What happened**
- Once (2026-11-09): test_boot.py stopped outside any test — the browser driver couldn't find the File menu button
  (30 s) when restoring the test library right after BOOT-001. Not reproduced in the next 3 runs, nor in the 8 full
  screen-test runs of 2026-11-11.

**Next time it happens**
- **Read it before fixing it** (TESTING.md §7): what was on screen (the failure screenshot) — was the menu bar covered,
  or not yet drawn? (Since 2026-11-17 the run keeps its whole output and screenshot — the summary names the path; if it
  was the machine (exit 3), it was already rerun alone and the summary says so: read its first output.)
- **Set it aside the same day** (with a TODO) rather than re-run past it.

### A screen test that failed once: the logging script not loaded at start-up (Diagnostics)
<!-- id 20261113-2108 -->

_Why it matters:_ A test that fails now and then teaches everyone to ignore failures (TESTING.md §7) — and this one
looked like the page starting without its logging script, which on a real visit would mean no log and no messages.

**What happened**
- Once (2026-11-13, sprint 4, before 7.30.0-alpha.3): test_diagnostics.py failed at page start-up — the log said
  `UI-03 Uncaught ReferenceError: rwLog is not defined (readerwrangler.js:164)` (the app's first log call), then a 180 s
  wait for the screen timed out. The file passed alone (11/11) and in the full rerun on the same files; my own two full
  runs after it passed too.

**Next time it happens**
- **Read it before fixing it** (TESTING.md §7): did the logging script's request fail or arrive late (the failure's
  console and network), and was `serve.py` rebuilding `dist/` at that moment? (Since 2026-11-17 the run keeps its whole
  output and screenshot; a page that never loads is the machine's trouble — exit 3 — and is rerun alone, said loudly.)
- **Set it aside the same day** (with a TODO) rather than re-run past it.

### A screen test that failed once: Reset's reload hung while a commit ran alongside
<!-- id 20261113-2359 -->

_Why it matters:_ A test that fails now and then teaches everyone to ignore failures (TESTING.md §7) — and Reset is
the one place where a hang would leave a person stuck mid-reset.

**What happened**
- Once (2026-11-13 ~23:45, sprint 4, on 7.30.0-alpha.8): in a full tier-2 run, test_reset.py failed 5 of 7 — RESET-003
  "the reset tab reloads normally (it hung) and stays reset (the other tab's folders came back)", then RESET-004–006 and
  the session's log. **A commit (TODO.md only) ran its checks during that run.** The file passed alone (6/6) right
  after, and the full tier 2 passed again with nothing else running. (Since 2026-11-17 a failed file's whole output is
  always kept — the summary names the path.)

**Next time it happens**
- **Read it before fixing it** (TESTING.md §7): keep the run's full output; was anything else using the machine (a
  commit's checks, another test run, `serve.py` rebuilding)? Reset waits on the browser letting go of the book store —
  a slow machine may be enough.
- Meanwhile: **no commits during a test run** (Claude's practice from 2026-11-13).
- **A cousin, 2026-11-15** (on 7.30.0-alpha.13, after a day of full runs): RENAME-006 "no unexpected console messages"
  failed once on `net::ERR_NO_BUFFER_SPACE` loading icons/logo-transparent.png — Windows short of network buffers (659
  connections in TIME_WAIT, no leftover test servers or browsers). The file alone and the whole tier passed right
  after. Done 2026-11-17 (sprint 7): the console check now reports it as the machine's trouble (exit 3), and the file
  is rerun alone, said loudly.

### A screen test that failed once: ENV-006 named the wrong trouble on a squeezed PC
<!-- id 20261118-1402 -->

_Why it matters:_ ENV-006 checks that our trouble detector names a lost library ("the network lost a library the page
needs") — if the generic "the page never loaded after 8 s" alarm wins the race on a slow PC, the detector's own test
fails even though both answers are the machine's trouble (exit 3).

**What happened**
- Once (2026-11-18 12:30, sprint 8's resource lab, memory squeezed to ~1 GB free, 5 browsers): test_environment.py
  6 passed, 1 failed — ENV-006 "the same library answered with NOTHING … → exit 3, the library named" got exit 3 with
  "the page never loaded — the app's start screen was still up after 8 s". Every other run that day passed it. Full
  output kept in the lab copy's archive (`.git\rw-test-results\copies\s8-lab-…`).

**Next time it happens**
- Read the kept output first (TESTING.md §7). Likely cause: the detector checks for the start screen at a fixed 8 s
  before it looks at which library is missing — a fixed moment, the kind sprint 8 removed from the screen tests. The
  fix would be to name the missing library whenever the start screen times out with a library absent, whatever the
  timing.

### Books just bought weren't at the top of All Books sorted by Date Added — once, not reproduced
<!-- id 20261112-1925 -->

_Why it matters:_ "What did I just buy?" is answered by sorting by Date Added — if a fresh purchase isn't at the top, the
reader has to hunt for it on Amazon's site (Ron, 2026-11-12).

**What happened** (2026-11-12): four wishlist/sample books with price goals were bought; in All Books they weren't at the
top. The Date Added FILTER (this week) found them; an hour later All Books sorted by Date Added showed them at the top.

**What we know** (checked that evening): the column, the sort and the filter all read the same date in practice — the
acquisition date, which the library fetcher sets to the ORDER date when a sample or wishlist book is bought (v4.11.8);
`dateAdded` is empty on every book (Ron's 10-31 backup: 2,625 of 2,629 owned books carry an acquisition date, none a
`dateAdded`); organizing doesn't touch dates. **Candidates:** All Books' remembered sort wasn't Date Added at the time;
or the fetch that promoted them was imported between the first look and the filter (until then the app still had them
as wishlist / sample books with their old dates). **Ron's log (pasted that evening)** backs the second: the import at
6:42:06 made 2 wishlist books owned, and his Add to 'New To Read' of all 4 came at 6:43:19 — a look at All Books before
6:42 would have shown those two still as wishlist books. (The other two were likely samples, which the import doesn't
count — see the task "'N now owned' after an import…", item 1.) Ron: "pretty sure 2 were samples and 2 wishlists" — and
he may have been looking for a sample's title. The uncounted samples still got the order date as their date (the same
fetch), so the count bug can't hide them from the sort; but it means all four most likely arrived in that one import,
so before 6:42 none of them was owned or dated new. **Most likely explanation: he looked before the import.**

**Next time it happens**
- Note the folder's sort (the column header's arrow) before changing anything.
- Open Help → Diagnostics…: when was the last import (its "N now owned" line), against when you looked?

### Resend's email limits
<!-- id 20261120-1700e -->

_Why it matters:_ Every email the relay sends goes through Resend's free plan: 3,000 a month, at most 100 a day
(checked 2026-11-20). Today that's about 60 a month (the two nightly summaries); outside review 1 adds a few kinds
(security.txt's reminder, "Amazon stopped a fetch"), each limited to one a day. Support replies don't use it — the
contact address is a forwarder.

**If it grows:** Resend Pro is $20 a month for 50,000 emails. Check when the daily alerts start to add up, or if
replies ever need to come *from* the contact address (Gmail's "Send mail as" through Resend would count against it).
Resend's new inbox product ("Inboxes") isn't needed for support — the forwarder already receives (Ron + Claude,
2026-11-20); "Relay worker: one release…", item 7, still considers it for the daily summaries.

**Also watch: a forced move off Resend's legacy sending system** (Ron, 2026-11-25). Resend's dashboard says our domain
"still sends through our legacy infrastructure" and offers "Resend Forge" (faster, better deliverability). Nothing
needs it today — the relay's emails arrive. **If Resend announces it will retire the legacy system,** move before the
deadline: a change to the relay's email setup, so Ron's (an outside service), and test that the nightly summaries and
alerts still arrive.

---

## 🧊 Someday

_Formerly: 🧊 Icebox (no timeline)_

### Formats other than Kindle: undo my Kindle-only preference
<!-- id 20261018-1422a -->

_Why it matters:_ "Kindle only" is Ron's own preference baked into the series and author adds (Ron, 2026-10-16: "We took MY preference and baked it in") — other readers may want paperbacks, hardcovers or audiobooks; and the library fetch has no way to keep out formats you don't track.

**Placed here** (Ron, 2026-11-03): very speculative, low priority — the basic features come first, and for user 1
there's no drive (Kindle books and a handful of PDFs). **What's already in your library** (the ~80 gift items below):
sort All Books by Format and scroll past Kindle; if that proves insufficient, a Format filter in the right pane
(item 3) is the first piece to build, on its own.

**Today**
- The **series** and **author** adds take Kindle editions only; the **one-book Add Book to Wishlist** takes whatever format the page shows — keep that exception either way (Ron adds a paperback as a placeholder when there's no Kindle edition yet).
- **The library fetch already brings in EVERY format** (confirmed 2026-10-16 from Ron's library, Format column): ~80 non-Kindle items — 47 Board Book, ~12 Paperback, ~12 Mass Market Paperback, 4 Map, 2 Audio CD, 1 each CD-ROM, DVD, Product Bundle, Spiral-bound, and one "Shoes" (a board book Amazon mislabels). Mostly gifts Ron's wife bought. _(Corrected twice today: I first claimed Amazon's library was Kindle-only — it isn't; its default filter hides other things, not formats — see "Fetcher: give the library filter one name, in one place" and TODO notes.)_
- So the library has the **opposite** problem: things you don't track (gifts, a DVD) come in with no way to keep them out.

**Shape** (Ron + UX, 2026-10-16) — **someday, only if users ask**
1. **One "Formats I track" setting** — checkboxes (☑ Kindle ☐ Paperback ☐ Hardcover ☐ Audiobook …), saved with your sync settings so every fetcher obeys it. It works **both ways**: series / author adds bring in the formats you track (not just Kindle), and the library fetch leaves out the ones you don't (your gift board books, the DVD).
2. The author and series panels show it pre-checked; you can change it for that one run.
3. **A Format filter in ReaderWrangler's right pane** — books already carry a format (the editable Format field), so it has something to work from. Today the only way to see them is the Format column + sorting.
4. To decide when built: the default for new users, and what happens to already-fetched books in formats you then untick (hide them? leave them?).

**Watch out**
- **Author add — settled 2026-10-16: print works exactly like Kindle**, and "All languages" can be one request (a small
  win for the shipped fetcher). Details: AMAZON-AUTHOR-PAGES.md.
- Format words seen: `kindle`, `paperback` (author filter); Amazon's library filter lists Kindle Edition, Paperback, Hardcover, Board Book, Audible Audiobook.
- The series add asks Amazon for `binding=kindle_edition` (series-page-fetcher.js ~319).

### Find out whether reading progress can be fetched from Amazon
<!-- id 20261014-1030aq -->

_Why it matters:_ "See how far along you are" — in the book window and as a list column — is only possible if Amazon
shows a book's reading position somewhere ReaderWrangler can read it. Today nothing does: the only reading data we get
is Read / Unread, from your Kindle collections (checked 2026-11-03: no reading position in the book fields, the
fetchers or our Amazon notes).

**Decided** (Ron + Claude, 2026-11-03, in the TODO review — was "Show reading progress")
1. **This is research first:** find out whether Amazon shows reading position (the place the Paperwhite, the app and
   Cloud Reader resume from) anywhere the fetcher already reads, or could read with a request like the ones it already
   makes. Findings go in the TODO notes.
2. **Then decide:** a source found → a cheap build (a list column plus a line in the book window; it comes back out of
   Someday as its own task). None → close it.
3. **Off the public "Future Features" list** (README, features page) until a source is found — it promised something we
   don't know we can build.

### Support stores besides Amazon
<!-- id 20261014-1030aw -->

_Why it matters:_ For readers who buy elsewhere too.

**Placed here** (Ron + Claude, 2026-11-03, in the TODO review) — someday, only if users ask:
1. The formats decision again, only bigger: the basics come first, and user 1 has no need. Each store means its own
   fetchers, page changes, human checks and terms question.
2. ReaderWrangler is a Kindle library organizer — the bookmarklets, the Paperwhite workflow, "Read in Kindle", and the
   plain statement of what it works with ("Say plainly what ReaderWrangler works with…").
3. Nothing is lost by waiting: the spec's one structural idea — store-first file names (`amazon-library-fetcher.js`) —
   is already how the fetchers are named. Not on any public list (checked 2026-11-03).

**Spec:** docs/reference/MULTI-STORE-ARCHITECTURE.md.

### Several people on one installation
<!-- id 20261014-1030ao -->

_Why it matters:_ Separate libraries for several people in one copy of the app.

**Placed here** (Ron + Claude, 2026-11-03, in the TODO review): the workaround is better than this feature — **one
browser profile per person** (or another browser). Each profile is its own world: its own library, its own Cloud Sync
key, nothing shared (help notes, "One working tab…"). Swapping libraries with Save / Restore Backup, the old
workaround, is clumsy and easy to get wrong. The real hazard — someone else's Amazon account fetched into your library —
is its own task: "A fetch from someone else's Amazon account stops before mixing two libraries" (the launch gate, in the
fetcher work).

**Spec:** docs/design/archive/MULTI-USER-DESIGN.md.

**Weighed again (Ron, 2026-11-22, with "Share Library" — outside review 3):**
1. **The cost of profiles grows with friends:** five reader friends swapping libraries means five extra browser
   profiles — and the browser then asks which profile at every new window, where it never asked before. Weigh that
   against the work below.
2. **A friend's library is a different case from two people on one computer:** it is only looked at and organized
   (a "Books I Want To Borrow From Ron" Book List) — never fetched into, since it has no Cloud Sync Key and none would
   lead anywhere useful.
3. **The shape, if built** (Ron's): a library ID (a GUID) in the name of every saved item — the book database
   (`ReaderWrangler<ID>DB`), the simple-storage items, the session items — or one level under storage per library;
   **every read and write of a saved item goes through one function** that looks up the current library
   (`readSaved` is already the one reader for settings; the writes and the book database's name would join it); Restore
   of a share switches to its library; **File → Choose Library** (greyed out with one library).
4. **The same one function would give the phone page storage names of its own**, if that is ever wanted (outside
   review 3, item 8 — Ron prefers one copy, 2026-11-22); built for either, it makes the other a smaller change.

### Animated drag-and-drop
<!-- id 20261014-1030c -->

_Why it matters:_ Books slide aside live to show where a drop will land.

**Placed here** (Ron + Claude, 2026-11-03, in the TODO review) — only if the drop line proves hard to see:
1. Today a **line** marks where a drop lands — the standard, honest signal ("no fake drop signals", Law 18).
2. **The known trap:** books sliding aside move the spot under the pointer, so the target changes and they slide back —
   jitter at the edges between books. Solvable, but real work for polish. (Cost is not the worry: during a drag the
   app already hides rows out of view, so only the visible books would move.)
3. **Try first:** a bolder line or a small gap.

### Share a filtered, read-only copy of your library
<!-- id 20261104-1024b -->

_Why it matters:_ People may want to show someone their books — but a backup is the wrong thing to send: it carries the
whole organization and notes (and, unlocked, the Cloud Sync Key), and **Restore replaces the recipient's own library**.

**Placed here** (Ron + Claude, 2026-11-04) — someday, only if users ask; no real-world case yet (it came from exploring
how a key could leak — "Lock the Cloud Sync Key in backups…").
- **What it would be:** "Share a read-only copy" of the **current view** (e.g. All Books with the "Spicy" or "Political"
  tag filtered out), never with the key; the recipient **opens it as a separate guest view** that leaves their own
  library alone. A spreadsheet is a poor substitute (no covers, lists, tags, reviews — Ron).
- **Until then — profiles, not backup-swapping** (Ron): the brother-in-law who wants to browse your books opens your
  backup in **a separate browser profile** (its own key, its own library), picks the ones to borrow, and emails you —
  never restoring someone else's backup into his own and then restoring his own back. (With the key password, even a
  restore can't take over your cloud library — he can't unlock your key.)
