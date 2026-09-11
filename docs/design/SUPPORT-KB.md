# Support Knowledge Base — mined behavior facts & Q&A

_The raw material for the USER-GUIDE and the support GPT (docs/design/SUPPORT-GPT.md: "the real
asset is the docs"). Every entry is a fact a user needs, a symptom worth explaining, or a concept
worth teaching — mined from real sessions, then kept current by the standing rule: **any
support-shaped answer lands here (or in WORKFLOW-PATTERNS.md for usage patterns) in the same
breath as answering.** The Release Checklist backstops it._

_**Up to date as of 2026-09-10.** Sources swept: the full working-session transcript
(2026-05-10 → 2026-09-10), all post-mortems, design docs (OWNERSHIP-MODEL, UNDO-MODEL,
FORMAT-POLICY, TOMBSTONE-DELETE, MULTI-INSTANCE, AUTO-ORGANIZE-UNIFIED, DATA-DURABILITY),
TERMINOLOGY.md, WORKFLOW-PATTERNS.md, TODO's scattered "GPT note" lines. Older sessions survive
only through those artifacts; anything they didn't capture is gone — future material is captured
live._

Companion docs: **WORKFLOW-PATTERNS.md** (usage patterns & trade-offs), **TERMINOLOGY.md**,
**SUGGESTED-ORGANIZING-PRINCIPLES.md** (prescriptive rules).

---

## A. Core concepts (the mental model, in user words)

1. **Folders are custodial; Book Lists are supplemental.** A folder is a book's *home*; a Book
   List is a set of *linked copies* — like a library card catalog: destroy the index card and
   the book stays on the shelf. Adding/removing from a list never moves, tags, hides, or deletes
   the book. Folders nest; Book Lists are flat.
2. **Searches are saved filter presets, not destinations.** Clicking one sets the active filters
   on whatever you're currently viewing (folder, list, All Books) — exactly as if you'd clicked
   the filter buttons by hand. Setting matching filters by hand highlights the saved Search.
   Filters persist as you click between folders; an "empty" folder usually means a filter is on.
3. **The RW Wishlist is NOT your Amazon account wishlist.** "Add to Wishlist" is a bookmarklet
   run on an Amazon product or series page that adds those books *directly to ReaderWrangler*.
   Amazon keeps no copy — which is why deleting a wishlist book from RW is permanent (nothing at
   Amazon to re-fetch it from), unlike owned books.
4. **Amazon's facts vs your states (ownership).** Amazon reports what you hold (Purchased,
   Sample, Prime, Borrowed…). You may manually set only two *states*: **Owned** ("I have it,
   Amazon's record is stale") and **Wishlist** ("I want it"). A manual override is protected
   from fetch overwrite, and Amazon's original value stays available behind "Reset to Amazon's
   value" in the same dropdown. (Full model: OWNERSHIP-MODEL.md.)
5. **The Inbox is where pending decisions live** — new arrivals land there; organizing means
   moving them to homes. All Books / My Library / Searches are aggregate *views*; deleting from
   them means deleting the book everywhere (v7.11), while cut/move need a real source folder.

## B. Behavior facts users will ask about

**Loading & syncing**
1. **First load takes ~15–25 seconds** (the app compiles in your browser) and Chrome may show
   "Page Unresponsive" — the loading screen says so; don't panic, don't reset.
2. **A fetch you just pushed can take up to ~a minute to be importable** (cloud storage
   propagates gradually). If Import says "up to date" right after a fetch, wait a minute and
   import again. Not a bug.
3. **The library fetcher runs in phases**; after "fetch complete" a **full-library orphan scan**
   runs in the background with its own progress bar — closing the tab early skips it (the dialog's
   ℹ️ explains). The orphan scan is what notices books you removed on Amazon's side.
4. **Incremental fetches stop at the newest already-known book** — old books aren't re-walked
   (a recovery sweep fires when counts disagree with Amazon's). Withdrawn/delisted books that
   Amazon half-reports are flagged, never silently dropped.
5. **Mobile is a viewer.** It mirrors the desktop's data *and order* (refresh the page to pick
   up the latest push; a freshness banner nudges when newer data exists). Mobile can't filter —
   the pattern is to pre-filter on desktop into Book Lists (see WORKFLOW-PATTERNS).

**Deleting — the most misunderstood area**
6. **A deleted owned book comes back on the next fetch, by design** — it's still in your Amazon
   library, and a fresh sighting revives it (tombstones only block *stale pre-delete* data from
   echoing back). The delete warning steers you to **Hide** for owned books because Hide sticks.
7. **Wishlist deletes stick** (RW-owned data, no Amazon backstop). **Samples are in-between**:
   the sample lives in your Amazon content library forever, so a deleted sample returns on
   fetch — the truth path is deleting the sample at Amazon (Manage Your Content) first
   (full sequence in WORKFLOW-PATTERNS "Correcting ownership").
8. **Re-adding a wishlist book you deleted requires Empty Trash first** — until the Trash copy
   is purged, the ASIN is still "known" and the add is skipped as a duplicate.
9. **Never delete to correct ownership** — use the Ownership dropdown (Edit mode). Delete means
   "I don't want this record."

**Buying books you tracked**
10. **Buying a wishlist/sample book upgrades it in place** (same ASIN): same folders, tags, and
    price goal — that's why homing wishlist books early costs nothing. But **publishers sometimes
    re-issue under a new ASIN**: then the purchase arrives as a *new* Inbox book and your old
    wishlist copy remains — resolve the duplicate by hand (delete the old wishlist copy).
11. **Upgraded books stay where you filed them** — they do NOT jump to the Inbox. To round up
    recent purchases: All Books, sort by Date Added. (Import summaries counting upgrades
    properly — "3 wishlist → owned" — are a queued improvement.)

**Editing & undo**
12. **Everything you do is undoable** (7.11): moves, renames (folders/tags/Searches/Book Lists),
    tag edits, price goals, ratings, reorders, Search create/delete. Undo/redo toasts always name
    what they reverted. Not undoable, by decision: view state (sorting, collapse, filters) and
    permanent deletes (confirmed dialogs). A backup restore clears undo history (pre-restore
    actions would lie).
13. **In the book dialog**: instant controls commit one undo step each; Edit-mode Save commits
    everything as ONE step. (7.12 makes the dialog fully transactional: Edit/Save will be the
    only way anything changes there.)
14. **Cut marks, paste moves.** Ctrl+X marks books (dashed "marching ants") — nothing moves
    until you paste. Esc cancels a pending cut from anywhere; navigating doesn't.
15. **Author strings are never parsed or merged.** "Larry Niven, Jerry Pournelle" is its own
    author; "Kevin J Anderson" (no period) is a different author than "Kevin J. Anderson" and
    will auto-organize into a separate folder — fix by editing the author field on the books.
    Auto-Organize's *File under…* handles co-author books into the folder you choose.
16. **Format can be wrong at the source** (Amazon has reported formats as absurd as "shoes") —
    that's why Format is editable free-text; blank = honest unknown. (FORMAT-POLICY.md.)

**Filters, counts, columns**
17. **"My folder is empty!"** — check the active filters (folder counts read N/M when a filter
    hides books) and the Show Hidden toggle. Clearing filters restores the world.
18. **"I can't filter by field X"** — more than one way to skin a cat: List view → add the
    column (column picker) → sort by it. ASIN, Format, publication date, price date etc. are
    all available as columns.
19. **Hidden books are counted honestly**: "3134 of 3136 (2 hidden by user)" — the hidden filter
    has three states so you can see just the hidden ones.

**Prices**
20. **Prices are as fresh as your last fetch** — each shows its "as of" date and dims after ~24h.
    Some books legitimately have no price (delisted, or only an audiobook edition is sold).
    Prime/KU books can show a buy-price even while borrowable — ownership shows Prime, price
    shows what buying costs.

**Backups & credentials**
21. **Restore returns you to the backup's state** — with guarded prompts if current Book Lists /
    Searches would be lost. Presentation settings (cover/list view, columns, theme) are
    deliberately NOT part of a backup. **Your sync channel is never changed by a restore** — if
    you've regenerated credentials since the backup, remake the bookmarklet (the app detects the
    mismatch and offers the new bookmarklet to drag).
22. **Backups are yours, in files you keep.** For spreadsheets: File → Save Spreadsheet (CSV) —
    one row per book with tags, folder paths, and Book Lists joined in; book ids are ASINs.
23. **A "channel revoked" notice** means relay credentials were revoked (usually deliberately, in
    Relay Setup). Regenerate credentials + remake bookmarklets to resume syncing.
24. **One working tab.** Running a second RW tab (or the mobile view) against the same browser
    profile risks the copies overwriting each other's organization — the app guards against the
    known cases (MULTI-INSTANCE.md), but the rule of thumb is: organize in one tab.

**Kindle-side data**
25. **Collections and read status come FROM the Kindle/Amazon side** — RW displays them (fetch
    Collections to refresh) but they're edited on your Kindle/Amazon, not in RW. Note Amazon's
    automatic "read" status (fires at ~99%) is separate from any collection you name "Read".

## C. Troubleshooting shapes (symptom → explanation → fix)

| Symptom | Explanation | Fix |
|---|---|---|
| Deleted book reappeared after a fetch | It's owned/sampled — Amazon still lists it; revive-on-sighting is by design | Hide it (owned), or delete the sample at Amazon first (truth path) |
| New purchase missing after import | Import raced the push (wait ~1 min), or it was an *upgrade* of a tracked book (didn't count as "new", stayed in its folder) | Re-import; check All Books by Date Added |
| Can't re-add a deleted wishlist book | Trash copy still holds the ASIN | Empty Trash, then add |
| Folder looks empty / counts look wrong | A filter (or Show Hidden) is active | Clear filters |
| Same book twice, one wishlist one owned | Publisher re-issued under a new ASIN | Delete the stale wishlist copy |
| Series mixes Sample and Wishlist states | Historical accretion (sampled before adopting the wishlist habit) | Override to Wishlist, or the truth path; then keep one habit |
| App shows an old version after update | Browser cache | Hard refresh (Ctrl+Shift+R); verify in Help/About |
| "Sync data check failed / checksum mismatch" | A cloud write was interrupted (rare since v7's sealed-packet sync) | Follow the dialog: full fetch rebuilds, then import — local data is intact |
| Slow first "Checking pending additions" | First fetch after new relay data does extra accounting | Let it run; subsequent fetches are quick |

## D. Meta

- **Scrub rule (public repo):** entries never contain channel IDs, tokens, cookies, emails, or
  any user-identifying data. Facts only.
- **Add here** when an answer is a *fact or fix*; add to **WORKFLOW-PATTERNS.md** when it's a
  *way of using RW*. Distill both into USER-GUIDE at launch; the GPT is loaded from these files.
