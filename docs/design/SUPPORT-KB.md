# Support Knowledge Base — the questions users ask, answered

_The raw material for the USER-GUIDE and the support GPT (docs/design/SUPPORT-GPT.md: "the real
asset is the docs"). Organized by feature area; entries are phrased as the questions a user
would ask. Two source pivots: (1) the **feature surface** — every menu item, tooltip, dialog,
and page implies a question; (2) **real usage** — the working-session transcript
(2026-05-10 → present), post-mortems, and design docs. Kept current by the standing rule:
**any support-shaped answer lands here (facts/fixes) or in WORKFLOW-PATTERNS.md (usage
patterns) in the same breath as answering.** The Release Checklist backstops it._

_**Up to date as of 2026-09-13 — all sections complete** (feature-surface pass: 140 UI
strings, all menus/dialogs/pages walked; plus the transcript/post-mortem mining pass).
Scrub rule (public repo): no channel IDs, tokens, cookies, emails, or user-identifying
data — facts only._

Companion docs: **WORKFLOW-PATTERNS.md** (usage patterns & trade-offs), **TERMINOLOGY.md**,
**SUGGESTED-ORGANIZING-PRINCIPLES.md** (the suggested method, in full).

---

## 1. What is ReaderWrangler?

**What does it do?** Amazon's Your Books page lists everything you own — as one endless,
sorted scroll. You can't group books, reorder them, or make lists of them. In short: you
can't *organize* them. ReaderWrangler pulls your library — covers, series, ratings,
descriptions, prices, your Kindle collections — into a page that lives in *your* browser,
and lets you arrange it your way: folders, tags, Book Lists, saved Searches, drag-and-drop,
and an Auto-Organize that files whole author backlogs in one preview. Its reason to exist:
**unbury your next great read.**

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
deletes) writes back to your Amazon account — all your organization lives in your browser,
on your computer.

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
   **Inbox**. (A just-finished fetch can take up to a minute to arrive — if Import says
   "up to date" too soon, wait a moment and try again.)
4. **Organize** — drag books into folders, tag them, build Book Lists — or right-click →
   Auto-Organize to file whole authors at once. Repeat steps 2–3 occasionally to pick up new
   purchases.

**What's the bookmarklet, and why one?** A bookmark that runs the fetcher on Amazon's page —
it's how your (already logged-in) browser session reads your own library. Nothing to install,
no password ever given to ReaderWrangler. Your ReaderWrangler relay credentials are baked
into it when you create it — if you ever regenerate credentials, drag a fresh bookmarklet
(the app detects mismatches and offers it).

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

**How do I keep it current?** Buy books as usual; every so often run the bookmarklet —
Download Library, plus Download Collections when your Kindle collections or read status
have changed — then Import from Relay. Incremental fetches are quick — they stop at the
newest book ReaderWrangler already knows.

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
  the common shape) — but nothing says they must *all* be authors: mix in catch-all shelves
  (*Various Authors*, *Non-Fiction*, *Comics*), or anything your imagination suggests.
- **Trash** — deleted books, still recoverable until you empty it. Just like your computer's
  recycle bin.

**Folders vs Book Lists vs tags — which do I use?** Three tools, three textures: **a folder
is a shelf** — where the book belongs, its home. **A Book List is a stack of index cards** —
any hand-picked set: a to-read queue, all your SF, your wife's books; tear up a card and the
book stays on its shelf. **A tag is a sticky note** — a label you filter by, in any
combination with everything else, for unlimited views of your collection. (Tags are the one
tool here without a sidebar section of their own — they live in the filter bar, and under
View → Manage Tags.) Book Lists and tags overlap on purpose — plenty of schemes work as
either, and which carries what is *your* preference. ReaderWrangler provides the tools; the
schema is yours. Proven patterns and their trade-offs: WORKFLOW-PATTERNS.md.

## 4. Views, columns & sorting

**Cover View vs List View** (View menu or the toolbar toggle): covers for browsing by eye —
with a width slider to size them — and List for data work: sortable columns, more fields
visible at once. Each folder remembers its own sort; series-grouped displays show group
headers you can collapse (and Collapse/Expand All Groups controls).

**Columns are yours to shape** (List View): **Choose Columns** picks which show (Title,
Author, Series, #, Ownership, Format, ASIN, ratings, prices, price date, dates, Amazon
link…), drag headers to reorder, drag edges to resize. **Click a header to sort; click again
to reverse; Shift+Click another column for a secondary key** (e.g. Series, then #). This is
also the answer to "I can't filter by X" — add the column and sort.

**Badges on covers**: non-purchased ownership shows as a badge (SAMPLE, PRIME…); wishlist
books render dimmed; a cut book wears "marching ants"; hidden books dim further.

**Number by Current Order** (right-click, with books selected): stamps series positions to
match the current display order — arrange 32 unrelated Heinleins by publication date, select,
number them once.

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
the toast confirms which happened (and the 🕐 button by the status bar keeps a history of
recent messages, in case one faded before you read it). Right-click → **Move to ▸ / Copy to ▸** offers the folder
tree as a menu (in your sidebar's order), including "New folder…" targets. Cut/copy/paste
works too: Ctrl+X marks books with a dashed "marching ants" border — **nothing moves until
you paste** into the destination folder (Esc cancels a pending cut from anywhere).

**Can a book be in two folders?** Yes — a deliberate copy (Ctrl+drag or Copy to) gives it two
homes; both show the same book. Hover a cover to see everywhere it lives ("Found in… / On
Book Lists…"). But a book can't appear twice in the *same* folder — dropping it on a folder
that already holds it says "Book already in folder" rather than making a duplicate.

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

**When do I use one instead of a folder — or a tag?** For any hand-picked set that isn't the book's
*home*: all your SF, your wife's books, gift ideas — and the classic, *to-read queues*
(`<Series> - To Read`, a shared `New To Read`: finish a book → delete it from the list; its
folder home never churns). Folders are for where a book belongs and they nest; lists are
flat and disposable by design. Many schemes work as either a Book List or a tag — your
preference decides. Full patterns: WORKFLOW-PATTERNS.md.

**How do I make and fill one?** ➕ on the Book Lists header (name it in place — Escape keeps
the suggested name); or select books anywhere → right-click → **Add to Book List** (existing
list or "New Book List…" — the suggested name knows the series/author: `<Series> - To Read`);
or save filter results as a snapshot list; or drag books onto a list row. From the
Auto-Organize preview you can add straight to a list mid-organize.

**Drag rules**: book(s) → list row *adds* (dedup, book stays put). List → list *moves* the
shortcut; **Ctrl+drag copies** it. Reordering the lists themselves: drag (undoable).

**Deleting**: DEL inside a list removes the selected shortcuts from *that list only*. ✕ on
the list row deletes the list (confirmation only if it isn't empty) — the books are
untouched. Both genuinely undoable: undo brings a deleted list back with its contents and
its place in the sidebar.

**Do Book Lists sync to mobile?** Yes — and since mobile can't filter, pre-filtering into
lists is *the* mobile pattern: filter on desktop, save the results as lists like `New To
Read`, `New To Read - Prime`, `New To Read - Samples`, `<Series> - To Read`, then read them
from the phone ("Book Lists as mobile filters", WORKFLOW-PATTERNS).

## 9. Tags & Tag-from-Collections

**What are tags for?** The sticky note of the toolkit (§3's triad): cross-cutting labels
that overlay your folder structure without touching it — kind/genre/mood slices (`Time
Travel`, `Non-Fiction`, `Classics`) you filter by, in any combination. A book takes any
number of sticky notes.

**How do I tag books?** Select → right-click → **Tags ▸**: check/uncheck existing tags, or
type to create a new one. View → **Manage Tags…** is the registry: create, rename, delete,
multi-select, and **drag to reorder** — that order drives the right-click Tags menu.

**What happens when I rename a tag?** The label changes everywhere at once — on every book,
in the filter bar, in the Tags menu. Nothing needs re-tagging, and saved Searches built on
the tag keep working (they follow the tag, not its spelling). Undoable, with a receipt.

**What happens when I delete a tag?** It's removed from every book carrying it, from the
active filter, and any saved Search that depended on it is removed too — the receipt spells
out the fallout, and one undo reverses all of it.

**What's Tag from Collections?** File → **Tag from Collections…** turns your Kindle
Collections into RW tags in one reviewed pass — pick which collections become tags and apply.
On later runs, "New books only" limits the pass to books that joined collections since last
time, and the wizard also flags books whose collection membership *ended* so their
collection-tags can be retired.

**Why would I want that, if I can already filter by Collections?** Because collections are
*Amazon-side* data: read-only in ReaderWrangler, editable only on your Kindle (see §14).
Converting them to tags takes the curation you already did on the device and makes it
*yours* — editable here (add/remove books without touching the Kindle), renameable,
splittable, combinable with every other filter, and permanent even if the collection later
changes or disappears on Amazon's side. TFC is the bridge from curation you rent to curation
you own.

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

## 11. The book dialog

**What's in it?** Double-click a book (or right-click → the book's name): cover, title
(linked to Amazon), author, series & position, format, ownership, Amazon rating & reviews,
**My Rating** stars, current price with its "as of" date, **price goal** (preset "Buy at"
amounts or a custom target), tags, Kindle Collections, description, and your note. **◀ ▶
arrows (or ← →) walk the current folder's books** without closing the dialog — great for
reviewing a series in order.

**How do I edit?** The ✏️ pencil enters edit mode: title, author, series name & number,
format, ownership, note. **Save commits everything as one step** (one undo reverses the whole
save); Cancel discards; Enter saves, Escape cancels. _(Planned next: the dialog goes fully
transactional — rating/goal/tags will also stage until Save.)_

**Ownership — what am I allowed to change?** The dropdown shows Amazon's actual state
(*Sample (from Amazon)*, Prime, Borrowed…) and offers only what's genuinely yours to declare:
**Owned** ("I have it — Amazon's record is stale") and **Wishlist** ("I want it"). After an
override it also offers **Reset to Amazon's value (…)**. Your override is protected — future
fetches won't flip it back. And never *delete* to correct ownership (see §12).

**Why is Format editable?** Because Amazon sometimes gets it wrong (real values observed
include "shoes"). Free text with suggestions from your library's vocabulary; **blank = honest
unknown**.

**Why can't I select/copy the title text?** It's a link (it opens Amazon) — use right-click →
**Copy Title** from the book's context menu instead.

**What's Share?** Copy the Amazon link (affiliate-tagged), or build an email with up to 20
selected books' titles and links — copied to paste into your mail app.

## 12. Hide, Trash & delete

**The golden rule: match the tool to the goal.**
- *"I own it but never want to see it"* (gifts bought for others, kids' books, maps) →
  **Hide**.
- *"Remove this record"* (stale wishlist entries, rejected samples — after deleting the
  sample at Amazon) → **Delete** (Trash).
- *"Amazon's label is wrong"* → **Ownership override** (§11) — never delete.

**Hide.** Right-click → Hide Book(s) (or the delete-warning's "Hide Instead"). Hidden books
dim and drop out of normal views; the **Show Hidden** filter has three states (hide them /
show all / *only* hidden — that last one is how you review what's hidden). Counts stay honest
("2 hidden by user"). Unhide from the same menu. Hide sticks across fetches — it's the right
tool for owned books precisely because deletes don't stick on them (below). A book that
appears twice (e.g. once solo and once inside a series shelf) can have a single *copy* hidden
from the dialog without hiding the book.

**Delete = Trash first.** Deleting from a **folder** removes the book from *that folder* —
it only goes to Trash if that was its last home (copies elsewhere live on). Deleting from
**All Books / My Library / a Search** means "delete the book": it's removed from every folder
and trashed. In a **Book List**, DEL just removes shortcuts from the list. Deleting an
**owned** book gets a warning first — "it will reappear next fetch; consider Hide instead"
(Hide Instead / Delete Anyway / Cancel).

**Trash view.** Deleted books wait here, recoverable. Hover one to see **"Was in (before
Trash)"** — its former homes. **Restore** (right-click) returns it to all its former folders,
and it reappears on its Book Lists (list membership survives a trip through Trash). Dragging
a book *out* of Trash restores it to wherever you dropped it. DEL inside Trash — or
right-click the Trash row → **Empty Trash** — deletes permanently, with confirmation
("cannot be undone", Book-List fallout disclosed).

**Why did my deleted book come back?** It's owned or sampled — it's still in your Amazon
library, and a fresh fetch legitimately re-lists it (permanent-delete tombstones stop *stale*
data from resurrecting it, not Amazon's live report). Owned → Hide it. Sample → delete the
sample at Amazon first (Manage Your Content), then the truth-path sequence in
WORKFLOW-PATTERNS. **Wishlist books are the exception: their deletes stick** (they're
ReaderWrangler-native; Amazon holds no copy) — though re-*adding* one requires **Empty
Trash** first, or the add is skipped as a duplicate of the trashed copy.

## 13. Undo

**What can I undo?** Everything you do to your data: moves, copies, paste, delete/restore,
hide/unhide, renames (folders, tags, Book Lists, Searches), tag edits, price goals, ratings,
edits, reorders, Search and Book List create/delete, Auto-Organize passes (one click = one
undo). **Every undo/redo toast names its target** — "Undone: Delete 'A People's History…'
from 'Folder A'" — so you always know what just reverted. **Ctrl+Z** undoes; **Ctrl+Y or
Ctrl+Shift+Z** redoes.

**Deliberately NOT undoable**: view state (sort modes, collapse/expand, filters, selection)
and explicitly-confirmed permanent deletes (Empty Trash). Cut/copy to the clipboard isn't an
action yet — the paste is.

**Undo in dialogs is scoped.** While any dialog is open, Ctrl+Z reaches only what happened
since it opened (rename a tag in Manage Tags, undo it right there); otherwise the app says
"Nothing to undo from this dialog — close it to undo earlier actions" rather than silently
reverting something you can't see. In the book dialog, instant controls are one step each and
an Edit-mode Save is ONE atomic step; in edit mode Ctrl+Z is native text-undo for the field
you're typing in.

**When history resets**: a backup restore clears the undo history (entries from before the
restore would lie about the state they'd return you to).

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
   **Just bought part of a series? Add-Series-to-Wishlist is still safe** — it skips books the
   Amazon page shows as owned (which includes purchases made seconds ago), so only the ones
   you don't own become wishlist entries. Order doesn't matter; one import reconciles all.
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

## 16. Price watching & deals

**How do I watch for a sale?** Give a book a **price goal**: right-click → Set Price Goal
(preset amounts or a custom target), or the "Buy at" buttons in its dialog. Then **Deals
Only** (View menu / filter bar) shows every book at or below its goal — check it after a
fetch and buy. Wishlist and sample books are the natural targets: track the book, name your
price, wait.

**How fresh are prices?** As fresh as your last fetch — every wishlist-priced book is
re-priced each run. Each price shows its "as of" date and **dims once it's stale (~24h)** so
a sale you're seeing might already be over — fetch before you buy.

**Why does this book show no price?** Usually honest: delisted from the Kindle store, or only
a non-Kindle edition (e.g. audiobook) is on sale. A **Prime/KU book showing a price** means
"free to borrow, $X to buy" — ownership says Prime, price says what buying costs.

**Do goals survive buying the book?** Yes — promotion keeps your data (you'll visit the book
anyway to file/queue it; clear the goal then if you like).

## 17. Mobile

**What is the mobile app?** A phone-sized *viewer* of your library — browse your folders,
lists, and Searches; it deliberately doesn't edit or organize (that's desktop work). Install
it as a home-screen app or just open readerwrangler.com on your phone.

**How do I set it up?** Relay Setup on desktop → pair your phone with the **QR code**. The
phone pulls your library from the relay — same encryption, key delivered by the QR, nothing
readable in the cloud.

**Does it match my desktop?** Yes — books, folders, Book Lists, Searches, **and your order**,
pins included (the desktop is the ordering authority; there's no reordering on the phone).
The drawer (hamburger) is the sidebar's twin for jumping between sections; sections collapse;
color spines mark Searches / Book Lists / Folders.

**Why is my phone showing older data?** It shows the library as of its last refresh — a
banner nudges when the relay holds something newer; refresh to pull it. Desktop-side changes
reach the relay shortly after you make them.

**How do I filter on mobile?** You don't — you *pre-filter on desktop into Book Lists* and
read the lists on the phone ("Book Lists as mobile filters", WORKFLOW-PATTERNS). Sorting
within a shelf cycles like the desktop's sorts; hidden-book counts can be tapped to reveal.

## 18. Keyboard shortcuts & mouse tricks

The app's own list: Help → **Keyboard Shortcuts**. The core set:

| Keys | Action |
|---|---|
| Ctrl+Z / Ctrl+Y (or Ctrl+Shift+Z) | Undo / Redo (toasts name the target) |
| Ctrl+A | Select all in the current view |
| Ctrl+X / Ctrl+C / Ctrl+V | Cut (marks) / Copy / Paste books into the current folder |
| Ctrl+Click / Shift+Click | Multi-select / range-select |
| DEL | Delete selection (context-aware — see §12) |
| Esc | Close dialog · cancel pending cut · clear selection |
| ← → (book dialog) | Previous / next book |
| Alt+← / Alt+→ | Back / Forward through your navigation history |
| F2 | Rename the selected folder |

Mouse tricks worth knowing: **Ctrl+drag = copy**; Shift+Click a column header = secondary
sort key; hover a cover = "where does this book live" popup; double-click = open the book;
right-click *everything* — books, folders, lists, Searches, tags, blank space, even the Trash
row — the menus are where the power hides.

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
- Site-page finding (2026-09-13, RESOLVED same day): the demo-library load instruction was
  tooltip-only on the Step 2 button — a visible Step 3 ("Restore a backup → pick the file")
  now appears on both index.html and tutorials.html.
- Pending-feature note: CROSS-SECTION-DRAG (decided, unbuilt) will change §8's drag rules —
  the spec and TODO both carry an update-the-KB-on-ship note.
