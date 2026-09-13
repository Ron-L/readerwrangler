# Support Knowledge Base — the questions users ask, answered

_The raw material for the USER-GUIDE and the support GPT (docs/design/SUPPORT-GPT.md: "the real
asset is the docs"). Organized by feature area; entries are phrased as the questions a user
would ask. Two source pivots: (1) the **feature surface** — every menu item, tooltip, dialog,
and page implies a question; (2) **real usage** — the working-session transcript
(2026-05-10 → present), post-mortems, and design docs. Kept current by the standing rule:
**any support-shaped answer lands here (facts/fixes) or in WORKFLOW-PATTERNS.md (usage
patterns) in the same breath as answering.** The Release Checklist backstops it._

_**Up to date as of 2026-09-13** (structure + §1–2, §19–21 complete; sections marked
"pending" are being filled in batches). Scrub rule (public repo): no channel IDs, tokens,
cookies, emails, or user-identifying data — facts only._

Companion docs: **WORKFLOW-PATTERNS.md** (usage patterns & trade-offs), **TERMINOLOGY.md**,
**SUGGESTED-ORGANIZING-PRINCIPLES.md** (the suggested method, in full).

---

## 1. What is ReaderWrangler?

**What does it do?** ReaderWrangler organizes your Amazon Kindle library — the one Amazon
gives you no real tools to organize. It pulls in your books (covers, series, ratings,
descriptions, prices, your Kindle collections), and lets you arrange them your way: folders,
tags, Book Lists, saved Searches, drag-and-drop, and an Auto-Organize that files whole author
backlogs in one preview. Its reason to exist: *unbury your next great read* from a backlog
Amazon shows you only as an endless recency scroll.

**Do I install anything?** No. It runs entirely in your browser at readerwrangler.com — no
install, no account, no sign-up. (The one thing you drag to your bookmarks bar is a
bookmarklet used on Amazon's own pages to fetch your library.)

**Where is my data? Who can see it?** Your library lives in *your browser* on your machine.
Syncing between your devices travels through a relay in the cloud, but everything stored
there is encrypted with a key only your devices hold — the relay (and its operator) cannot
read your library. Details: the Security & Privacy page.

**Does it cost anything?** No.

**Does it change anything on Amazon?** No. Fetching reads your library via the same requests
Amazon's own "Your Books" page makes. Nothing you do in ReaderWrangler (folders, tags,
deletes) writes back to your Amazon account.

**Does it work for non-Kindle books?** Its data source is your Amazon content library, which
includes print books Amazon knows you bought, samples, borrows (Prime/KU), and wishlist adds
you make via the bookmarklet from any product page — print editions included.

## 2. Getting started

**The whole path, in order** (also in the app under Help → How To Use):
1. **Set up sync** — File → Relay Setup: generate your credentials, **drag the bookmarklet to
   your bookmarks bar**, and optionally pair your phone with the QR code.
2. **Fetch** — go to Amazon (your Books page), click the bookmarklet, choose Download
   Library (and Download Collections for your Kindle collections/read status). Let it finish —
   including the background orphan scan after "fetch complete."
3. **Import** — back in ReaderWrangler: File → Import from Relay. Your books appear in the
   **Inbox**.
4. **Organize** — drag books into folders, tag them, build Book Lists — or right-click →
   Auto-Organize to file whole authors at once. Repeat steps 2–3 occasionally to pick up new
   purchases.

**What's the bookmarklet, and why one?** A bookmark that runs the fetcher on Amazon's page —
it's how your (already logged-in) browser session reads your own library. Nothing to install,
no password ever given to ReaderWrangler. Your relay credentials are baked into it when you
create it — if you ever regenerate credentials, drag a fresh bookmarklet (the app detects
mismatches and offers it).

**Do I need an Amazon account to try it? (The Demo Library.)** No — download the demo library
(100+ classic books) from the home or Tutorials page, open ReaderWrangler, and load the file:
on a fresh install the Welcome screen offers **Restore a backup** — choose the downloaded
`readerwrangler-demo-library.json`. (Same path later: File → Restore Backup….) Every feature
works on it: folders, tags, filters, Auto-Organize.

**What's the Welcome screen telling me?** It appears when the app finds no books. If you're
genuinely new, it walks you through setup. If you're a returning user whose browser data was
cleared (or a new machine), it says so — *"Your folders and lists are intact"* — and lists
recovery options best-first: Import from Relay (your library is still in the cloud), Restore
a backup, or fetch fresh then import. It never means your organization is gone.

**How do I keep it current?** Buy books as usual; every so often run the bookmarklet
(Download Library) and then Import from Relay. Incremental fetches are quick — they stop at
the newest book ReaderWrangler already knows.

## 3. The sidebar: what all those sections are

_(Concepts below; per-feature details in their own sections.)_

- **All Books** — every unique book in your library, organized or not. A view, not a folder:
  you browse, filter, edit, and (since 7.11) delete here, but books can't be *moved* from
  here (there's no single "from").
- **Searches** — saved filter presets. Clicking one applies its filters to whatever you're
  viewing. They're live: results change as your library does.
- **Book Lists** — flat, hand-curated lists of *linked copies* (shortcuts). Adding/removing a
  book from a list never moves, tags, hides, or deletes the book itself — like a library card
  catalog: destroy the index card and the book stays on the shelf.
- **Inbox** — where newly imported books land, awaiting a decision. Drag them into folders
  (or Auto-Organize) to file them.
- **Folders** — your hierarchy; a folder is a book's *home*. Folders nest (author → series is
  the common shape).
- **Trash** — deleted books, still recoverable until you empty it.

**Folders vs Book Lists — which do I use?** Folders hold *where a book belongs* (stable,
set once); Book Lists hold *transient status* like "still to read" (cheap to add, cheap to
delete from when done). The full patterns: WORKFLOW-PATTERNS.md.

## 4. Views, columns & sorting — _(pending: batch 5)_

Seed facts:
- **"I can't filter by field X."** More than one way to skin a cat: List View → column picker
  (Choose Columns) → add the column (Format, ASIN, publication date, price date…) → sort by it.
- **Shift+Click a column header** sets a secondary sort key (e.g. Series, then #).
- Cover size slider in Cover View; Grid/List toggle in the View menu and toolbar.

## 5. Search box & filters

**What does the search box match?** Title, author, or series — anywhere in the field, as you
type. Recent filter combos live in its dropdown (apply, save, or remove them).

**What can I filter by?** Ownership type (Owned / Wishlist / Sample / Prime…), read status,
tags, Kindle Collections, series, Amazon rating, your rating, date added — plus **Show
Hidden** (a three-state control: hide hidden / show all / *only* hidden) and **Deals Only**
(books at or below your price goal). Filters combine.

**Why does my folder look empty?!** A filter is almost certainly active — filters *persist*
as you click between folders (that's what makes them useful), and folder counts switch to
"matching/total" (e.g. 3/41) while one is on. The Active-filters banner names what's applied;
**Clear All** restores the world. Hidden books are always counted honestly ("3134 of 3136 —
2 hidden by user").

**Can't filter by some field?** More than one way to skin a cat: List View → Choose Columns →
add the field (Format, ASIN, publication date, price date…) → sort by it.

**Do folders with no matches disappear while filtering?** They're hidden to reduce noise —
the "Show all" control at the top of the sidebar brings them back (sticky until you change
it).

## 6. Folders & organizing by hand

**How do I move books into folders?** Drag them (multi-select first if you like: click,
Ctrl+click, Shift+click for ranges, Ctrl+A for all). Plain **drag moves; Ctrl+drag copies** —
the toast confirms which happened. Right-click → **Move to ▸ / Copy to ▸** offers the folder
tree as a menu (in your sidebar's order), including "New folder…" targets. Cut/copy/paste
works too: Ctrl+X marks books with a dashed "marching ants" border — **nothing moves until
you paste** into the destination folder (Esc cancels a pending cut from anywhere).

**Can a book be in two folders?** Yes — a deliberate copy (Ctrl+drag or Copy to) gives it two
homes; both show the same book. Hover a cover to see everywhere it lives ("Found in… / On
Book Lists…"). Dropping a book on a folder that already holds it says "Book already in
folder" rather than making a duplicate.

**How do folders themselves get organized?** Folders nest (drag one into another; a folder
can't be dropped into its own subtree, and the Inbox can't be moved). The FOLDERS list has
**one order, mirrored everywhere it appears** — sidebar, the Folders view in the right pane,
and the Move/Copy menus:
- **Sort modes**: Manual (drag to reorder), Name, or book Count — pick via the FOLDERS-header
  control (sidebar) or column headers (right pane, where clicking cycles ascending/descending).
- **Drag-reorder works only in Manual** — in a sorted mode the app says so instead of
  silently ignoring you; Move to Top / Move to Bottom likewise explain when they can't apply.
- **Your Manual order survives sort excursions**: flip to Name to find something, flip back
  to Manual and nothing has moved. Like a sorted order enough to keep it? **Bake** it — the
  sorted order becomes your new Manual order.
- **📌 Pin folders to the top** (right-click → Pin to top): pinned folders float in their own
  small hand-ordered zone above whatever sort is active — how "Various Authors / New To Read"
  stay on top of an alphabetized author list. The pin boundary is a wall for drags in both
  directions.
- **New folders land at the top** (below pins) so you can see what you just made; a batch of
  new folders (one Auto-Organize pass) lands as an alphabetized block.

**Where do subfolder books show up?** A folder's count includes its subtree; in sorted modes
a parent row shows "N matching in subfolders" when a filter matches deeper down.

**Each folder remembers its own book sort** (title, author, series, date…, or Manual), and
returning to that folder restores it. Series sorting uses series then # — Shift+Click a
column header for your own secondary key.

## 7. Auto-Organize

**What does it do?** Files books into `Author` folders (and `Author/Series` subfolders) for
you — the cure for a thousand-book Inbox. Two entry points, one engine:
- **Right-click a book → Auto-Organize ▸ By Author / By Series** — acts on the chosen
  authors' books.
- **File → Auto-Organize…** — the wizard: pick multiple authors at once (filter box,
  All/Some/None, minimum-books slider), then the same preview.

**The preview is the contract.** It shows *everything* by the chosen authors, wherever it
lives: books from the folder you launched in and the Inbox arrive pre-checked (they'll move);
strays living elsewhere are visible but unchecked (they stay unless you check them); books
already in their destination show small and gray, labeled **home**. **The checkboxes are the
scope** — the button counts what will actually move ("Organize 4 books"), and nothing you
left unchecked is touched. Every cover carries a caption saying where it lives now; click it
for the plain-words breakdown ("moves from Wishlist · stays in Non-Fiction") with per-folder
checkboxes for copies that should stay put.

**What's the ⚙ Options strip?** Live controls inside the preview: the series-folder threshold
(how many books a series needs before it earns its own subfolder — below it, books file
directly under the author), and related knobs. Adjust and watch the preview reorganize.

**Will it undo my existing organization?** No — two guards. Books already filed elsewhere are
never pulled without your checkbox, and Auto-Organize refuses to *flatten* an existing author
tree (running By Author on a folder that already has series subfolders won't dissolve them).

**Co-authors and name variants.** Author strings are **never parsed**: "Larry Niven, Jerry
Pournelle" is its own author, and "Kevin J Anderson" (no period) is a different author from
"Kevin J. Anderson" — variants file into separate folders until you edit the books' author
field to match. For co-author books, right-click in the preview → **File under…**: send them
to another group or pick any folder by name — creating a new folder is always an explicit
➕ choice in the picker, never the accident of a typo.

**Handy inside the preview**: multi-select covers (Ctrl/Shift/Ctrl+A) and right-click → Add
to Book List (e.g. select the unread ones → `<Series> - To Read` — the suggested name knows
the series); double-click a cover to open its book dialog; group headers take File under…
for the whole group. One Organize click = one undo.

## 8. Book Lists

**What exactly is a Book List?** A flat, hand-curated list of *shortcuts* to books. The
anchor model: **All Books is where the book truly lives; Folders hold Linked Copies of it;
Book Lists hold shortcuts to it.** Delete a copy → the book leaves that folder; delete a
shortcut → it leaves that list; the book itself survives until you trash it. Adding or
removing from a list never moves, tags, hides, or deletes the book.

**When do I use one instead of a folder?** For *transient status* — above all, to-read
queues: `<Series> - To Read`, a shared `New To Read`. Finish a book → delete it from the
list; its folder home never churns. (Folders are for *where a book belongs*; they nest, lists
don't.) Full patterns: WORKFLOW-PATTERNS.md.

**How do I make and fill one?** ➕ on the Book Lists header (name it in place — Escape keeps
the suggested name); or select books anywhere → right-click → **Add to Book List** (existing
list or "New Book List…" — the suggested name knows the series/author: `<Series> - To Read`);
or save filter results as a snapshot list; or drag books onto a list row. From the
Auto-Organize preview you can add straight to a list mid-organize.

**Drag rules**: book(s) → list row *adds* (dedup, book stays put). List → list *moves* the
shortcut; **Ctrl+drag copies** it. Reordering the lists themselves: drag (undoable).

**Deleting**: DEL inside a list removes the selected shortcuts from *that list only*. ✕ on
the list row deletes the list (confirmation only if it isn't empty) — the books are
untouched. Both undoable.

**Do Book Lists sync to mobile?** Yes — and since mobile can't filter, pre-filtering into
lists is *the* mobile pattern ("Book Lists as mobile filters", WORKFLOW-PATTERNS).

## 9. Tags & Tag-from-Collections

**What are tags for?** Cross-cutting labels that overlay your folder structure without
touching it — kind/genre/mood slices (`Time Travel`, `Non-Fiction`, `Classics`) you filter
by. A book takes any number of tags.

**How do I tag books?** Select → right-click → **Tags ▸**: check/uncheck existing tags, or
type to create a new one. View → **Manage Tags…** is the registry: create, rename, delete,
multi-select, and **drag to reorder** — that order drives the right-click Tags menu.

**What happens when I delete a tag?** It's removed from every book carrying it, from the
active filter, and any saved Search that depended on it is removed too — the receipt spells
out the fallout, and one undo reverses all of it.

**What's Tag from Collections?** File → **Tag from Collections…** turns your Kindle
Collections into RW tags in one reviewed pass — pick which collections become tags and apply.
On later runs, "New books only" limits the pass to books that joined collections since last
time, and the wizard also flags books whose collection membership *ended* so their
collection-tags can be retired. (Collections themselves remain Amazon-side data — see §14.)

## 10. Saved Searches

**What is a saved Search?** A saved *filter preset*. Clicking one sets the active filters on
whatever you're currently viewing — folder, list, or All Books — exactly as if you'd pressed
the filter buttons yourself. It doesn't navigate anywhere, and it stays applied as you browse
until you clear it.

**Live, not snapshot.** A Search's results change as your library does ("Wishlist" always
means *current* wishlist). Want the frozen version? Save the results as a **Book List**
instead — the results bar offers both: *Search (live filter) or Book List (snapshot)*.

**How do I make one?** Set up filters, then Save via the results bar (name optional — an
unnamed Search shows its filter chips as its label). Hand-building the same filters later
highlights the matching saved Search automatically.

**Managing them**: rename inline (or right-click), drag to reorder, delete via hover-✕ or
right-click — "your books and tags are not affected," and it's undoable. Searches are
read-only presets: you can't drop books "into" one.

## 11. The book dialog — _(pending: batch 4)_

Seed facts:
- **Ownership** shows Amazon's actual state (Sample, Prime, Borrowed…) and offers only what's
  yours to set: **Owned** ("I have it; Amazon's record is stale") and **Wishlist** ("I want
  it") — plus **Reset to Amazon's value** after an override. Overrides survive fetches.
- **Format is editable** (free text, blank = honest unknown) because Amazon sometimes gets it
  wrong — real formats observed include "shoes."
- ◀ ▶ arrows walk the books of the current folder without closing the dialog.

## 12. Hide, Trash & delete — _(pending: batch 4)_

Seed facts (the most misunderstood area — full entries coming):
- **A deleted owned book comes back on the next fetch, by design** — it's still in your
  Amazon library. **Hide** is the tool for owned books you never want to see.
- **Wishlist deletes stick** (ReaderWrangler-native data; Amazon holds no copy). **Samples**
  return unless you delete the sample at Amazon first (Manage Your Content) — the "truth
  path" sequence is in WORKFLOW-PATTERNS.
- **Re-adding a deleted wishlist book requires Empty Trash first** (until then the book is
  still "known" and the add is skipped as a duplicate).
- **Never delete to correct ownership** — use the Ownership dropdown.
- Delete works from All Books / My Library / Searches (removes from every folder and
  trashes); from a folder, delete removes from *that folder* and trashes only if it was the
  book's last home; in a Book List, DEL just removes from the list.

## 13. Undo — _(pending: batch 4)_

Seed facts:
- **Everything you do is undoable** (moves, renames, tags, goals, ratings, reorders, Search
  create/delete), and every undo/redo toast names its target. Not undoable, by decision: view
  state (sorting, collapse, filters) and confirmed permanent deletes. Ctrl+Z / Ctrl+Y or
  Ctrl+Shift+Z.
- In the book dialog: instant controls are one undo step each; an Edit-mode Save is ONE
  atomic step. While any dialog is open, undo reaches only what happened in that dialog.
- A backup restore clears undo history (pre-restore entries would lie).

## 14. Sync, fetching & importing

1. **A fetch you just pushed can take up to ~a minute to be importable** (cloud storage
   propagates gradually). If Import says "up to date" right after a fetch, wait a minute and
   try again. Not a bug.
2. **The fetcher runs in phases** (titles → enrichment → tags → prices), and after "fetch
   complete" a **full-library orphan scan** runs in the background with its own progress bar.
   Closing the tab early skips it (the dialog's ℹ️ explains). The orphan scan is what notices
   books you removed on Amazon's side.
3. **Incremental fetches stop at the newest already-known book**; a recovery sweep fires when
   counts disagree with Amazon's. Withdrawn/delisted books Amazon half-reports are flagged,
   never silently dropped.
4. **Buying a tracked book upgrades it in place** (same ASIN): folders, tags, and price goal
   survive; the book stays where you filed it (find recent purchases via All Books sorted by
   Date Added). If the publisher re-issued under a **new ASIN**, the purchase arrives as a new
   Inbox book and your old wishlist copy remains — delete the stale copy by hand.
5. **The Data Status ball** (File menu / status bar) tracks freshness; it turns red when the
   relay holds newer data than you've imported.
6. **A "channel revoked" notice** means relay credentials were revoked (usually deliberately,
   in Relay Setup). Regenerate credentials and remake bookmarklets to resume syncing.
7. **One working tab.** Running a second ReaderWrangler tab (or the mobile view) in the same
   browser profile risks the copies overwriting each other's organization — organize in one
   tab (guards exist for the known cases; MULTI-INSTANCE.md).
8. **Collections and read status come FROM the Kindle/Amazon side** — fetch Collections to
   refresh them; they're edited on your Kindle/Amazon, not in RW. Amazon's automatic "read"
   status (fires around 99%) is separate from any collection you happen to name "Read".

## 15. Backups & spreadsheet

1. **Backups are yours, in files you keep** (File → Save Backup…). Restore returns you to the
   backup's state, with guarded prompts if current Book Lists/Searches would be lost.
2. **Presentation settings** (cover/list view, columns, theme) are deliberately NOT part of a
   backup — restoring your books shouldn't restyle your screen.
3. **Your sync channel is never changed by a restore.** If you regenerated credentials since
   the backup, remake the bookmarklet — the app detects the mismatch and hands you the new
   bookmarklet to drag.
4. **File → Save Spreadsheet (CSV)…** exports one row per book — tags, folder paths, and Book
   Lists included — and opens directly in Excel. Book ids are ASINs.

## 16. Price watching & deals — _(pending: batch 5)_

Seed facts:
- Set a goal from the book dialog or right-click → Set Price Goal (presets or custom);
  **Deals Only** filters to books at or below goal.
- Prices are as fresh as your last fetch; each shows its "as of" date and dims after ~24h.
  Some books legitimately have no price (delisted, or only an audiobook edition is sold);
  Prime/KU books can show a buy-price while borrowable.

## 17. Mobile — _(pending: batch 5)_

Seed facts:
- Mobile is a **viewer**: it mirrors the desktop's data and order (refresh to pick up the
  latest push; a freshness banner nudges when newer data exists). Pair via the QR code in
  Relay Setup.
- Mobile can't filter — the pattern is to pre-filter on desktop into Book Lists
  (WORKFLOW-PATTERNS: "Book Lists as mobile filters").

## 18. Keyboard shortcuts & mouse tricks — _(pending: batch 5; the app's Help → Keyboard Shortcuts is the authority)_

## 19. Troubleshooting (symptom → explanation → fix)

| Symptom | Explanation | Fix |
|---|---|---|
| Deleted book reappeared after a fetch | It's owned/sampled — Amazon still lists it; revive-on-sighting is by design | Hide it (owned), or delete the sample at Amazon first (truth path) |
| New purchase missing after import | Import raced the push (wait ~1 min), or it was an *upgrade* of a tracked book (didn't count as "new", stayed in its folder) | Re-import; check All Books by Date Added |
| Can't re-add a deleted wishlist book | Trash copy still holds the ASIN | Empty Trash, then add |
| Folder looks empty / counts look wrong | A filter (or Show Hidden) is active | Clear filters |
| Same book twice, one wishlist one owned | Publisher re-issued under a new ASIN | Delete the stale wishlist copy |
| Series mixes Sample and Wishlist states | Historical accretion (sampled before adopting the wishlist habit) | Override to Wishlist, or the truth path; then keep one habit |
| App shows an old version after update | Browser cache | Hard refresh (Ctrl+Shift+R); verify in Help → About |
| First load feels stuck / "Page Unresponsive" | The app compiles in your browser (~15–25s); the loading screen says so | Wait it out — don't reset |
| "Sync data check failed / checksum mismatch" | A cloud write was interrupted (rare since v7's sealed-packet sync) | Follow the dialog: full fetch rebuilds, then import — local data is intact |
| Slow first "Checking pending additions" | First fetch after new relay data does extra accounting | Let it run; later fetches are quick |
| Bookmarklet fetches the wrong library / mismatch warning | Bookmarklet carries older credentials than the app | Recreate the bookmarklet from Relay Setup |

## 20. A suggested way to organize (one of many)

The full method is **SUGGESTED-ORGANIZING-PRINCIPLES.md**; the patterns and trade-offs are
**WORKFLOW-PATTERNS.md**. The one-paragraph version:

> Give every book a stable **folder home** (author folders, series subfolders — Auto-Organize
> builds these for you; a catch-all like *Various Authors* for one-offs). Track *what's left
> to read* on **Book Lists** you delete from as you finish (`<Series> - To Read`, a shared
> `New To Read` for one-offs). Home wishlist books immediately in their future folders —
> purchase day is then zero work. Slice by kind with **tags**; keep self-maintaining views
> (Wishlist, Read/Unread) as **saved Searches**, never hand-maintained lists. There's no
> single right way — these are compositions of the same primitives.

## 21. Meta

- **Add here** when an answer is a *fact or fix*; add to **WORKFLOW-PATTERNS.md** when it's a
  *way of using RW*. Distill both into USER-GUIDE at launch; the GPT is loaded from these
  files.
- Site-page finding (2026-09-13): index.html and tutorials.html demo-library sections stop at
  "Step 2: Open ReaderWrangler" without saying how to load the file (Welcome screen → Restore
  a backup). Consider adding a Step 3 to both pages.
