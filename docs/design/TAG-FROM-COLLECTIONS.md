# Tag from Collections — Design

_v2 design (Ron + UX, 2026-10-18), branch `fix/tfc-clarity`. Replaces the v1 layout (6.10.0, 2026-08 — see "History"
at the end; v1's full text is in git). The **data model is unchanged** from v1 and is restated below._

> **Status (2026-10-20): v2 SHIPPED in 7.24.0** — alphas 1–3 (§2.1–2.10: the window, exact-text tag names app-wide,
> removals opt-in, undo removes a created tag). Ron's alpha.3 test round was then decided topic by topic; that work is
> **round 2**, filed as the TODO task *"Tag from Collections, round 2: clearer window, safer tags"* in five steps. The
> build list below is its record of decisions (not built yet); the TODO is the plan.

**What it is:** a window (**Tools → Tag from Collections…**) that turns Kindle collections into ReaderWrangler tags.
Collections come from Amazon and can't be edited here; tags are yours. Each collection becomes a tag of the same name,
on the books in that collection. Re-run after new purchases: the right side shows only books that would change.

---

## Round 2 build list — agreed, not yet built (filed in the TODO; was "7.24.0 build list")

_2026-10-20: 7.22.1 grew into a minor release and 7.23.0 shipped first → v2 shipped as **7.24.0**, and these items moved
to a later release (Ron: "declare that part done and log the rest under the TODO"). "7.24.0" below means the release
these were first planned for; "At release" items 11–14 were done for 7.24.0 itself._

_The working plan (Ron + Claude, 2026-10-19). **A topic isn't closed until its line is here** — written in the same
breath as the agreement, so it survives a break or a compaction. ✅ = built in an alpha (say which). The test steps
(§5) are written from this list; the reasoning lives in the section each line points to._

**The window**
1. **Layout:** Select All | Some | None moves into the left pane's header; both checkboxes move into the right pane's
   header (on one line; the "click a chip…" hint goes into the column headers' tooltip); the top bar is removed.
   (Ron, 2026-10-19 — §2.11 item 1; Ron judges the right header's crowding when he sees it.)
2. **The removal answer lives in the status line at the bottom** (where "Will create 0 new tags and tag 7 books" is);
   the note at the end of the left list is removed (it scrolled out of sight). (Ron's proposal, alpha.3 feedback #1;
   wording agreed in topic 3, Ron + UX, 2026-10-20.) While "Remove tags…" is ticked the status line ALWAYS has a
   removal line:
   - something to remove: *"Will remove tags from 3 books"* (amber, as today — counted in books, §2.7);
   - nothing to remove: *"No tags to remove: no book tagged by Tag from Collections has left its collection."*;
   - unticked: no removal line. With nothing else changing, *"No changes to apply"* shows with the removal line under
     it (both true; the second explains the first).
   Why: the answer appears where you read "what will Apply do", right after the tick — its presence answers "did my
   tick do anything?". The old text's "this window" is gone (topic 2).
3. **The two checkboxes' wording** (topic 2 — Ron + UX, 2026-10-20; no "Also", no "wizard": the name stays **Tag from
   Collections** everywhere):
   - ☐ **Remove tags from books that left the collection on Kindle** — tooltip: *"Only tags added by Tag from
     Collections. A tag you added or renamed yourself is never removed."* (Not "to match Kindle collections" — that
     reads as a full sync, e.g. taking a hand-added "Read" off books outside the Read collection; it never does.)
   - ☐ **Show books already tagged** — the ✓ rows are every book that HAS the tag, however it got it (not only ones
     this tool tagged — limiting it would make hand-tagged books vanish from their collection).
   - In every tooltip and help note, call it **"Tag from Collections"**, never "this window" (Ron: "this window" can
     mean this one opening of it).
4. **Two kinds of "already has it", told apart by sight** (topic 2 follow-up — Ron's idea, 2026-10-20: a tooltip per
   row means remembering after 5 rows; a visible mark scans and sorts). One leading mark per state, same as + / −:
   - **↻ Read** — added by Tag from Collections (`book.collectionTags`): the "Remove tags…" option can take it off if
     the book leaves the collection. ↻ = "follows its Kindle collection".
   - **✓ Read** — yours (added by hand, renamed, or kept when offered for removal): never removed.
   - Each chip's tooltip says which; the column header's tooltip gives the legend. Each mark sorts as its own group
     (order settled in topic 5). A text symbol, not an emoji, so it takes the theme's text color; the difference never
     rests on color alone. Only in this tool — tag chips elsewhere don't change. (Options weighed: color, ☑/✅, ✗, (A),
     +, A-overlay, A✓/M✓, @ — §2.11 item 3.)
5. **Seeing the removals — no new control** (topic 4, Ron + UX, 2026-10-20). Already in alpha.3: a tag being removed
   shows as **"− Read"** (amber) in its column (click = keep, shown struck through), and with "Show books already
   tagged" off the right side lists only rows with a change. Two ways to isolate removals, both from agreed pieces:
   - **sorting:** each mark sorts as its own group (item 4) — proposed order **−, +, struck through, ↻, ✓, blank**
     (removals first: the riskiest change); settled in topic 5 → item 6;
   - **the left checkboxes:** **None** for the collections, removal tags left ticked → the right side shows only the
     books losing a tag (works today: the right side is built from whatever is ticked). Said in the column headers'
     tooltip and the help notes (item 13), not a new button.
   - **Test with a real case** (Ron has none): on the Kindle / Manage Your Content, take one book Tag from Collections
     tagged out of its collection → Download Collections → Import → it shows "− Tag"; afterwards put it back and fetch
     again. Real data, reversible, nothing planted by hand. (→ §5.)

6. **Sorting — ONE shared behavior for this tool AND the list view** (topic 5, Ron chose option (a), 2026-10-20).
   - **Mechanism:** the list view's header-click rules (readerwrangler.js ~16384) move into ONE shared helper; both
     places call it — learned once, can't drift.
   - **Rules (the list view's today, plus a third state):** click = that column becomes the only key; click again =
     reversed; **third click = off**. Shift-click = add as the next key (up to 3); Shift-click again = reversed; third
     Shift-click = that key removed. Headers show ▲ / ▼ with a small 2 / 3 on later keys; header tooltip: "Click to
     sort • Shift+Click to add a sort key".
   - **"Off" falls back to the view's default:** here Title A–Z; in the list view whatever that view starts with today
     (All Books: Date Added, newest first; the library / Searches area: Name A–Z; a folder: Manual order). The list
     view's ✕ "Return to Manual Order" stays.
   - **This changes the list view:** today a third click there just flips the direction again; now it turns the sort
     off. (Ron accepted the scope: one behavior beats two.)
   - **A tag column sorts by its marks**, ascending: **− → + → struck through → ↻ → ✓ → blank** (removals first —
     the riskiest change); descending reverses. Title: A–Z / Z–A. (Order as proposed; Ron judges it in testing.)
   - Fixes Ron's test-2 notes: the arrow now reverses; any key can be turned off; Shift-click Title keeps the tag key
     (a plain click replacing the sort is the spreadsheet rule — said in the tooltip).

7. **Unchecking a collection clears its skips; a partly-skipped collection shows a partial box** (topic 6, Ron + UX,
   2026-10-20). The left list is a checkbox TREE (collection = parent, its books = children), so it follows the tree
   convention: uncheck the parent → its skips are cleared; check it → all its books. A checked collection with
   skipped books shows the standard **partial mark (▬)** instead of ✓ — skips are visible without scrolling; clicking
   a partial box unchecks it. Same rule for the removal section (unchecking a removal tag clears its "kept" choices;
   ▬ while some are kept). **Select All** = every collection with all its books (earlier skips go — Ctrl+Z
   brings them back: next bullet). Mechanism: a collection's skips live INSIDE its "checked" entry (one map, checked = has an
   entry), not in a second list — unchecking deletes the entry, so stale skips can't exist (Law 17).
   - **Undo inside the window** (Ron, 2026-10-20: "Select All erasing selections you made… are there conventions for
     making it undoable?"). The main undo leaves selection out — the convention everywhere and our ratified rule
     (UNDO-MODEL: view state isn't undoable). But this window's choices aren't just a selection: they're **the plan
     Apply will carry out — a draft**, and a draft's edits get undo. So: **Ctrl+Z / Ctrl+Y inside Tag from
     Collections undo / redo its choices** (checks, skips, All / None, the removal choices); the history lives and
     dies with the window; the library's undo is untouched (the fence already blocks it here — today Ctrl+Z only
     shows the "nothing to undo here" toast). Precedent: UNDO-MODEL's scoped undo for dialogs that record their own
     changes (book details, Manage Tags). **Findable:** when a bulk click erases choices, the status line says so with
     a link — *"Select All un-skipped 20 books — Undo (Ctrl+Z)"*. Cost: the history is a list of earlier versions of
     the one choices map. (Elsewhere — selected books in a folder — is a separate TODO, "Restore the previous
     selection", Photoshop's Reselect convention.)

8. **Tag changes confirm themselves — one message, used for the confirmation AND its undo** (topic 7, Ron + UX,
   2026-10-20). Found: of 9 places that change a book's tags, only right-click add / remove (existing tag) confirm;
   right-click **create** (Enter and the Create row), book details (add ×2, create, remove) and Tag from Collections'
   Apply don't — while every undo does (one place). **Mechanism:** the shared tag-change function (`recordTagChange`)
   shows the confirmation itself from the same text it records for undo (RW's move chokepoint already "pays double",
   readerwrangler.js ~3894) — action and undo always match, and no call site can forget. **Wording** — the result,
   with the word "tag": *Added tag "Read" to 'Title'* (undo: *Undone: Added tag "Read" to 'Title'*); *Created tag
   "zzz" and added it to 'Title'* (or "to 3 books"); *Removed tag "Read" from 3 books*; Apply: *Tag from Collections:
   tagged 7 books, created 1 tag* (+ *", removed a tag from 2"*). **Exception — book details:** no confirmation (RW's
   rule "a change you just watched needs no receipt": the chip appears / disappears where you clicked); its undo text
   uses the new wording. **Completeness:** at build time, a two-pivot search for every tag-changing site (e.g. Bulk
   Edit) with the list published before claiming coverage.

9. **Touching a tag by hand makes it yours** (topic 8, Ron + UX, 2026-10-20). Found in code: only Tag from
   Collections' Apply changes `book.collectionTags` — removing a tag by hand left it on that record, so remove +
   re-add by hand kept it the tool's (still offered for removal; would show ↻). The help's "two ways round it" would
   have been false. **Rule:** any change of a tag on a book that doesn't come from Tag from Collections — adding it,
   removing it, from any menu, including picking "Read" after typing "read" or **Add "Read" instead** in the capitals
   prompt — drops it from that book's record (same principle as "renaming a tag makes it yours"). Only books that
   actually change are affected (a selected book that already had it ↻ keeps it). **Mechanism:** in the shared
   tag-change function (item 8), so every hand path gets it; undo restores the record with the tag. **The right-click
   list stays as is** (tags already on the book aren't offered — the "One shared tag picker" decision; offering one
   would look like a button that does nothing). Ways to make a tool tag yours: remove and re-add by hand (works with
   this fix), or keep it (click its − chip) when it's offered for removal. Help notes: the ↻ / ✓ legend, this rule and
   both ways (item 13). (Ron's "silent read → Read" check, 2026-10-20: he was on a 7.23.0 build, which predates the
   capitals prompt; on 7.24.0-alpha.4 the prompt appears.)

**Data (its own alpha — it touches the data layer and its tests, so it gets its own test round)**
10. **Retire the hidden "seen" field** (`collectionTagSeen`): stripped in the shared book clean-up on every load and
   arrival (old backups included) and removed from the field table. (Ron + UX, 2026-10-19 — §2.8 item 5.)

**At release**
11. Merge main into the branch first (done once 2026-10-20 at `b7c871c`; repeat for anything main gains after).
12. CHANGELOG (Ron's word on the copy) — includes the list view's sorting change (item 6: a third click turns a sort
   off).
13. SUPPORT-KB: how to remove a tag from many books — All Books → filter by the tag → select → right-click → Tags
   (§2.5, help notes) — plus the ↻ / ✓ legend, the two checkboxes' meaning (items 3–4) and how to see only the
   removals (item 5), and sorting's third click (item 6 — grep the KB's sorting answers in §4). The commit check now
   refuses the release unless the help notes' stamp says "through release 7.24.0".
14. TODO.md (main): the task "Tag from Collections: clear up the checkbox vs. preview confusion" gets ✅, then is
   deleted with the release's ✅ sweep.

**Checked and NOT in 7.24.0**
- The double-spaces-in-author-names fix — its own TODO ("Stray double spaces in author names create duplicate
  authors"); it only shares the place in code with item 10. Verified in the session record 2026-10-19: never agreed for
  this release.
- The shared scrolling list with fixed top/bottom, and the Tags filter's "Manage Tags…" — deferred to the TODO (§7).

## alpha.3 feedback — topics still to discuss, in this order

_Ron's alpha.3 test notes (2026-10-19), grouped and ordered by Claude so each decision builds on the one before; "your
N" / "test N" are the numbers in Ron's notes. Topic 1 (layout) is agreed → build list item 1. When a topic is agreed,
its outcome goes into the build list and the topic is struck out here. My position on each is given when we reach it._

2. ~~**Wording: the two checkboxes, the "Also"s, "wizard" in the name** (your 2, 4, 5).~~ **Agreed 2026-10-20 → build
   list items 3–4.** (Ron's notes: the removal checkbox took three reads; shorten the show checkbox; is "Also"
   useful; "wizard" in the name — which came from reading the show checkbox as limited to tool-added tags, like the
   removal one is.)
3. ~~**The "No tags to remove" message** (your 1).~~ **Agreed 2026-10-20 → build list item 2.** (Ron: at the end of
   the left list it's subtle — the only clue is the scrollbar changing a little; put it in the status line.)
4. ~~**Seeing the removals** (your 3).~~ **Agreed 2026-10-20 → build list item 5.** (Ron: show a "− Tag"; with the
   show-tagged box off, only pluses and minuses; sort +TagA and −TagA apart.)
5. ~~**Sorting: multiple keys, three-state cycle, Shift-click** (test 2).~~ **Agreed 2026-10-20 → build list item 6.**
   (Ron: the arrow didn't reverse; the label sort couldn't be turned off; Title replaced the label sort; wants off /
   ascending / descending per column and Shift-click for the next key, like the list view.)
6. ~~**Skips remembered after unchecking and re-checking a collection** (test 2).~~ **Agreed 2026-10-20 → build list
   item 7.** (Ron: the earlier skips survived an uncheck + re-check; he expected a reset, as they can hide at the
   bottom.) Follow-up agreed the same day: **undo inside the window** → item 7; the folder case → TODO.
7. ~~**Toasts for create + apply, and "tag" in the undo text** (test 4).~~ **Agreed 2026-10-20 → build list item 8.**
   (Ron: tagging showed no toast but its undo did; one combined "Created tag xyz and added it to…"; put the word
   **tag** before the name — a tag, collection, folder and Book List can all be called "Read".)
8. ~~**The right-click Tags list hides tags already on the book** (test 5).~~ **Agreed 2026-10-20 → build list item
   9.** (Ron: he couldn't re-apply a wizard-added tag by hand to make it his; should the menu offer it, or should the
   help describe the 2 ways round it? Checking it found the remove + re-add way didn't work — now fixed by rule.)
9. ~~**Tag order in the filter and the right-click list** (your note).~~ **Agreed 2026-10-20: nothing new in 7.24.0
   — already filed** (§7; TODO "One shared tag picker"). Confirmed in code: the filter and right-click use the saved
   manual order; book details sorts A→Z; Manage Tags OPENS sorted A→Z by name (`tagSortColumn` 'name'), so what you
   see there matches book details while the other two follow a manual order it isn't showing. The filed fix — one
   visible Order: A→Z | Most used | Manual, followed by every tag list — is exactly this.
10. ~~**Tooltips running into Chrome's developer tools** (a note, developers only).~~ **Agreed 2026-10-20: no
    action.** All 11 tooltips in this window are the browser's own (`title`); Chrome places them on the screen, not
    the page, so the app can't keep them inside a pane — same on every site. Only a hand-built tooltip could; not
    worth it for a developer-only effect.

**All ten topics closed (2026-10-20).** Build order (Ron agreed):
1. **7.24.0-alpha.5 — the window:** build list items 1–9 (layout, status line, wording, ↻ / ✓, removals, the shared
   sort, the checkbox tree + undo inside the window, confirmations, touching a tag by hand makes it yours) — plus the
   "7.22.1" → "7.24.0" sweep of code comments and this doc. Ends with test steps (§5) written from the list.
2. **7.24.0-alpha.6 — the data change:** item 10 (retire the hidden "seen" field), its own test round.
3. Then the release (items 11–14).

## 1. Why v2

1. **Two click targets per row, nothing to tell them apart.** In v1 each collection row has a **checkbox** ("use this
   collection when you Apply") and a **name** ("show its books on the right"). Unchecking a box didn't change the right
   side; "checked" and "being shown" looked alike. It fooled Ron (2026-10-14, again 2026-10-18 on 7.22.1-alpha.1).
2. **The right side showed one collection at a time**, so you never saw everything Apply would do.
3. **The wizard matches collections to tags by a computed internal key, not by name** (found 2026-10-18 with Ron's
   data). "Non fiction" (a Kindle collection) and "Non-Fiction" (Ron's own, unrelated tag) both make the key
   `non-fiction`, so: the summary (which compares names) said *"Will create 1 new tag"*, while **Apply (which compares
   keys) would have put Ron's "Non-Fiction" tag on 39 books**, and books with Non-Fiction showed as "already tagged" in
   the Non fiction collection. Summary and Apply disagreed about whether a tag exists — two copies again.
   (A first theory — capital letters in keys — was checked against Ron's data and ruled out: all 11 of his keys are
   lowercase, no duplicate names. Reading the code confirmed it: every creation site lowercases the key. The real flaw
   is that DIFFERENT names can make the SAME key — "Non fiction" / "Non-Fiction", "Read" / "read" — fixed by giving
   every tag its own key, 2.6.)
4. **A tag could be created with no books on it**, just because its collection was checked.
5. **Removals of tags were pre-checked** — one click on Apply removed them.

## 2. The design

### 2.1 Layout

_As built in alpha.3. Build list item 1 changes it: the top bar goes; its controls move into the two pane headers._

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🏷️ Tag from Collections                                                      [×] │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Select: [All|Some|None]   ☐ Also show books that already have their tag          │
│                           ☐ Also remove tags whose book left                     │
│                                                that collection on Kindle         │
├──────────────────────────┬───────────────────────────────────────────────────────┤
│ Kindle collections       │ Changes Apply will make                               │
│ each becomes a tag       │ Title ▾                  Read (7)   Sci-Fi (2)        │
│                          │ ───────────────────────────────────────────────────── │
│ ☑ Read (7 new)           │ A Darker Shade of Magic  [+ Read]                     │
│ ☑ Sci-Fi (2 new)         │ Dune                     [+ Read]   [✓ Sci-Fi]        │
│ ☐ Favorites (3 new)      │ Project Hail Mary        [+ Read]   [+ Sci-Fi]        │
│ ☐ Mystery (0 new)  grey  │ The Martian                         [+ Sci-Fi]        │
│                          │ Uprooted                 [skip]  ← clicked: skipped   │
├──────────────────────────┴───────────────────────────────────────────────────────┤
│ Will tag 9 books (2 tags)                    [Cancel]  [Tag 9 books from 2 collections] │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Left: "Kindle collections — each becomes a tag"

**THE matching rule (Ron + UX, 2026-10-18), shown as one line under the header:**
> *Each collection goes onto the tag with exactly its name (capitals included); if there's none, a new tag is created.*

It looks only at names as they are **right now** — no memory of history, internal keys play no part. So: rename tag
A → A1, and a new book in collection A is offered **"A → new tag A"**; rename back to A and collection A feeds A again;
rename A → B and C → A, and collection A goes onto **tag A (formerly C)**. **Renaming a tag makes it yours** — the
wizard no longer ties it to a collection (see 2.5).

1. **One click target per row.** Clicking anywhere on a row (box or name) toggles its checkbox. There is no "being
   shown" state and no row highlight — the right side shows all checked collections at once.
2. Each row: checkbox, the collection name, its count — "(7 to tag of 971)" — and **where it
   lands**: **"→ tag Read"** (exists) or **"→ new tag Comics"**. If a tag differing only in capitals exists, the row
   adds *"(a tag 'Comics' also exists — a separate tag)"* so a near-twin is never a surprise.
3. **A collection with nothing to show** (every book already has its tag, and "Also show…" is off) is **greyed out, its checkbox disabled, and
   kept in its alphabetical place** — hiding it would make collections seem to vanish; moving it would reshuffle the
   list when "Also show…" flips. Tooltip: *"Every book here already has the tag — tick 'Also show books that already have their tag' to see them."*
4. "(tag exists)" becomes the "→ tag X" / "→ new tag X" destination above, decided by the matching rule.
5. **Select: All | Some | None** works as today (over the enabled rows).

### 2.3 Right: "Changes Apply will make"

1. **Every book in every checked collection, one row each** — the complete list of what Apply will do.
2. **One column per checked collection that has a change**, with the tag name as a **header that stays visible while
   you scroll**, and its count: *Read (7)*. Columns are aligned (an invisible grid — no lines).
3. **The chip in each cell** — a small tag shape:
   - **"+ Read"** — Apply will add this tag to this book.
   - **"✓ Read"** (grey) — the book already has it; nothing happens. (7.24.0: split into **↻ Read** = added by Tag
     from Collections / **✓ Read** = yours — build list item 4.)
   - **"+ Read" struck through** (grey, outlined) — skipped: you clicked the "+" chip, so this one tag won't go on this
     one book. Click again to restore. It keeps its mark and name — never blank (blank means "not in this
     collection", and a blank couldn't be clicked back). (This is v1's per-book unchecking, now per book × tag.)
     _Corrected 2026-10-20: this line used to call the chip "skip", which isn't what it shows._
   - **"− Sci-Fi"** (amber) — only when removals are switched on (2.5). **"− Sci-Fi" struck through** = kept (click
     again to remove after all).
   - Empty cell — the book isn't in that collection.
4. **Sorting:** click **Title** for A–Z (the default); click a **tag header** to bring the books with a change in that
   column to the top. Spreadsheet behavior, nothing new to learn.
5. **No filter on the right** — the left checkboxes already ARE the column filter. A second filter would be two
   controls for one job.
6. **Wide or long:** past about 6 columns the right side scrolls sideways with titles staying put; a first-ever run
   can list hundreds of rows — fine to scroll; later runs list only what changed since.
7. Titles keep their click-to-open-details link (7.19.0).

### 2.4 The Apply button and summary

1. The button carries the total, live: **"Tag 9 books from 2 collections"** ("Apply" when there's nothing to do).
2. **A tag is created only if at least one book will get it.** A checked collection with nothing to add does nothing.
3. Summary line counts only real changes: new tags actually created, books tagged, (removals if on).

### 2.5 Removing tags — off by default

1. **What it is:** tags *this wizard added* because a book was in a Kindle collection, where the book has since left
   that collection on Kindle. **Tags you made yourself are never touched** — the wizard keeps its own list per book
   (`collectionTags`, below).
2. **Off unless you tick** *"Also remove tags whose book left that collection on Kindle"* in the top bar. Then those
   tags appear as amber rows at the bottom of the left list ("Removed from Kindle", as in v1) and as **"− Tag"** chips on
   the right; clicking a "−" chip keeps that one.
3. Ron (2026-10-18) uses tags for much more than collections; removing them should never happen by one Apply click.
   Kept (opt-in) for people who mirror their Kindle collections as tags.
4. **A renamed tag is never offered for removal** — it's yours now (2.2). A candidate is a wizard-added tag whose
   **current name exactly matches a collection** the book is no longer in. (Today the removal check compares computed
   keys, readerwrangler.js ~7382 and ~12808 — switch both to the exact-name rule.) Nothing here limits deleting or
   renaming tags in Manage Tags.
5. **Help notes:** to remove a tag from many books, use **All Books → filter by the tag → select → right-click → Tags**
   — goes into SUPPORT-KB (it feeds the help assistant).

### 2.6 Tag identity — exact text, everywhere in the app (Ron + UX, 2026-10-18)

One rule app-wide, not a wizard rule plus a limitation elsewhere (today Manage Tags refuses "read" if "Read" exists):

1. **"Is this the same tag?" = exact text, capitals included.** "Read" and "read" are two tags. Never grouped, never
   renamed for you — capitals may mean something to you, and grouping is hard to undo.
2. **"Find a tag as I type" ignores capitals** (the tag pickers' search, the phone's search): typing "read" finds both.
   Finding forgiving, identity exact.
3. **A safeguard, not a refusal:** typing a new tag that differs from an existing one only in capitals asks once —
   *"A tag 'Read' already exists. Create 'read' as a separate tag?"* **Create** / **Use 'Read'** (catches a Caps Lock
   slip). In the wizard the row's note (2.2) does this job instead of a prompt.
4. **A→Z ignores capitals**, so near-twins sit side by side (already true — `localeCompare`; keep it).
5. **Every tag gets its own internal key**, unique even when two names differ only in capitals (one shared "find or
   create a tag" function guarantees it). Existing keys are never renamed (that would touch every book and Search).
6. **Renaming to a name that already exists exactly is refused** ("A tag named 'Read' already exists") — two tags with
   the same exact name would make "the tag with exactly its name" ambiguous. Today rename has no such check.
7. **Duplicate check done 2026-10-18:** Ron's 11 tags have no names matching each other even ignoring capitals.

**Site map** (the class-of-sites sweep, 2026-10-18 — two independent searches: every write to the tag list, and every
comparison of tag names; they agree). Line numbers on branch `fix/tfc-clarity` at `6574d32`.

| # | Screen | Creates / renames at | Name check today | Becomes |
|---|--------|----------------------|------------------|---------|
| A | Book details → Tags, Enter | ~14064 | ~14040 (lowercase compare) | shared find-or-create + safeguard |
| B | Book details → Tags, pick "create" | ~14120 | ~14101 (lowercase) | same |
| C | Right-click → Tags → Add Tag, Enter | ~19847 | ~19821 (lowercase) | same |
| D | Right-click → Tags list, "create" | ~19913 | ~19904 (lowercase) | same |
| E | Manage Tags → Create new tag… | ~18080 | ~18083 (lowercase, refuses) | same |
| F | Tag from Collections → Apply | ~13192 | ~12853, ~12946 (by computed key) | exact-name rule (2.2) |
| G | Manage Tags → rename | `renameTag` ~2065 (callers ~17994, ~18002) | none | refuse an exact duplicate (6) |
| H | Removal candidates (wizard) | ~7382, ~12808 (computed keys) | — | exact-name rule (2.5) |

Not creation or renaming (checked): first load ~4446, Reset ~6313, Restore ~6660, undo/redo ~7789–8377, drag order
~1447, deletes ~17910 / ~18043, the phone app (load only, mobile.js ~2635). Finding-as-you-type stays capital-blind:
~14043, ~14105, ~19897, mobile.js ~2293.

### 2.7 Counts (Ron, 2026-10-19)

- The right side's heading: **"Tagging 7 of 48 books shown (1 collection)"** — 48 = the rows you can see (set by the
  left checkboxes and "Also show books that already have their tag"), skipped ones included; 7 = books that will get
  a tag. Counted in **books**, not tags (a book getting two tags is one line). The button: **"Tag 7 books from 1
  collection"**.

### 2.8 "New books only" — removed (Ron + UX, 2026-10-19)

1. It worked through a hidden per-book "seen" flag (`collectionTagSeen`) you could neither see nor reset — and it
   confused Ron in testing. v2's per-collection checkboxes express the real decisions visibly.
2. **Replaced by:** the right side shows **only changes** by default; a visible checkbox **"Also show books that already
   have their tag"** adds the ✓ rows (e.g. all 48 Non fiction books).
3. **The window opens with nothing checked** — without the hidden memory, everything-checked would offer the 504
   "+ 2BRead Fiction / Classics…" chips Ron always declines. You check what you came for.
4. A book you skip inside a collection you use is offered again next time — honest and visible.
5. **The stored field is retired in code (alpha.4)**, not by a one-off snippet (a returning user would bring it back):
   stripped in the shared book clean-up (`normalizeBook`, on every load and arrival — old backups included) and removed
   from the field table, so saves, backups and syncs stop carrying it.

### 2.9 Undo removes a tag the action created (Ron + UX, 2026-10-19 — reverses 7.10.1's "unused = harmless")

- Undoing "create a tag and put it on books" (any creation path, and the wizard's Apply) also removes the tag — **if no
  book carries it after the undo** (if you've put it on another book meanwhile, it stays). Redo recreates it. Nothing
  is lost (it has no books); the tag lists aren't left littered by an action you took back.
- Mechanism: the undo record of a tag change (`SET_BOOK_FIELDS`) carries `createdTags`.

### 2.10 The capitals prompt words its buttons by context (Ron + UX, 2026-10-19)

- **Tagging books** (right-click, book details): **Add "Read" instead** / **Create "read"** — both do something.
- **Manage Tags** (nothing to tag): **Cancel** / **Create "read"** — "Use 'Read'" promised an action that didn't exist.

### 2.11 alpha.3 test round — the reasoning behind the decisions (Ron + UX, 2026-10-19 evening)

_The outcomes are in the build list at the top; the open topics, with Ron's notes, are listed just below it._

1. **Layout — controls sit with what they change (agreed):** Select All | Some | None moves into the LEFT pane's header
   (it only changes the left checkboxes — across the top it read as global, misleading now that the right side has
   its own per-book clicks); both checkboxes move into the RIGHT pane's header (both change what the right side
   shows); the top bar disappears. Keep the right header compact (checkboxes on one line; the "click a chip…" hint
   into the column headers' tooltip) — Ron judges it when he sees it.
2. **A list's actions stay visible (agreed, refined with Ron's yes the same evening):**
   1. **Found in the code:** the Tags **filter** already HAS "Manage Tags…" at its bottom — the whole menu scrolls
      as one piece (capped at 300px), so with ~a dozen tags it sits below the cut-off and looks missing; "Select All /
      Clear All" at its top scrolls away too. Right-click → Tags does it right (only the tag rows scroll).
   2. **The rule — three kinds:** actions on the whole list (Manage…, Create…, Select All / Clear All) are **always
      visible**, fixed above/below the scrolling part; **notes** about the list are NOT pinned (a fixed note costs a
      line forever and stops being read — put it where status is read); ordinary rows scroll.
   3. **In 7.24.0 — only this window's "No tags to remove…" note.** It's part of this window, so it doesn't wait for
      the sweep; by the rule it's a note, not an action, so it isn't pinned — it moves to the bottom status line
      (Ron's own proposal; exact words in topic 3).
   4. **Deferred to the TODO (Ron, same evening):** the mechanism — ONE shared scrolling list with a fixed top slot and
      a fixed bottom slot — and the Tags filter's fix with it. The filter has always scrolled this way (no regression;
      scrolling down is the workaround), building the piece now would grow this release again, and it pairs with
      "One shared tag picker", so both tag lists move onto it together. TODO.md (Polish): "Long lists keep their
      actions in view (Manage…, Select All) while you scroll".
3. **Telling "added by Tag from Collections" from "yours" (2026-10-20).** The two checkboxes work on different sets —
   removal touches only tags this tool added; "show already tagged" shows every book that has the tag — and nothing on
   screen said so (that asymmetry is what made "wizard" in the name seem needed). Ron's case for a visible mark: a
   tooltip per row is a memory task after ~5 rows; a mark is scanned, and sorting groups it. Options weighed against
   three tests — readable without color (color-blind, light/dark), no clash with this window's marks, a hint of the
   meaning: color alone fails the first; ☑ vs ✓ too alike; ✅ is an emoji (ignores the theme); ✗ means "no"; "+"
   already means "will add"; (A) is noisy in a long column; an "A" over ✓ is too small; A✓/M✓ works but nobody calls
   their own tags "manual"; @ works and sorts but reads as "at" / a mention. **↻** chosen (Claude's suggestion, Ron:
   "would need to be learned as well, but that's fine") — it frames the real distinction, *tied to its Kindle
   collection* vs *yours*, which is exactly what decides whether removal can touch it. 🔗 says it better but is an
   emoji.

## 3. Data model (unchanged from v1)

- ~~`book.collectionTagSeen`~~ — **retired** (2.8; stripped from data in 7.24.0 — build list item 10). It was set for every book **shown** in the wizard when Apply is clicked (checked or not):
  you saw it, so it isn't "new" next time. Internal, not shown, not editable.
- `book.collectionTags = ["read", …]` — tag keys **this wizard** assigned. Removal candidates come only from here; a
  declined removal drops the key from `collectionTags` only (the tag becomes yours).
- `book.collections = [{ name }]` — from the Kindle collections fetch, read-only, replaced on each import.
- With 2.2 / 2.6, `collectionTags` holds the key of the tag actually used (found by exact name), not a computed key.

## 4. Apply (what happens)

1. For each checked collection with ≥1 "+" chip: find-or-create its tag (2.6); add it to each "+" book (and to that
   book's `collectionTags`).
2. Removals (only if switched on): each "−" chip removes the tag from `tags` and `collectionTags`; a kept one drops it
   from `collectionTags` only.
3. (Removed 7.22.1-alpha.3: no more "seen" marking — see §2.8.)
4. One undoable step (as today); a toast names what was done.
5. **One calculation** decides "which books will get which tag" — used by the chips, the header counts, the button and
   Apply itself (7.22.1-alpha.1 already merged v1's two copies).

## 5. Verification (test steps for the alpha)

1. Ron's **Read** collection (7 newly read books): None → check Read → row says "→ tag Read", 7 "+ Read" chips, header
   *Read (7)*, button *"Tag 7 books from 1 collection"*; Apply → the books get the **existing** "Read" tag (no second
   tag); Ctrl+Z undoes.
1a. **"Non fiction"**: row says **"→ new tag Non fiction"** (NOT Ron's "Non-Fiction"); no book
   shows "already tagged" because of Non-Fiction; Apply would create a separate "Non fiction" tag. (Don't apply it —
   Ron has his own plan for these books.)
1b. Exact text elsewhere: Manage Tags → create "read" while "Read" exists → the safeguard asks; **Create** makes a
   separate tag, **Use 'Read'** doesn't. Rename "Next" to "Read" → refused.
2. Check a second collection → its column appears; a book in both shows two chips; the total adds up.
3. Click a "+" chip → "skip"; total drops by 1; Apply leaves that book without that tag.
4. Click a tag header → books with a change in that column come first; click Title → A–Z.
5. A collection whose books all have the tag is greyed and can't be checked; tick "Also show books that already have their tag" → it's enabled and its ✓ rows appear.
6. Removals off (default) → no amber rows or "−" chips anywhere; tick the box → they appear.
7. A collection whose books all already have the tag → no column, no tag created, button unchanged.
8. Manage Tags → "Create tags from your Kindle collections…" opens this window.
9. After Apply: Manage Tags shows no duplicate names.

## 6. Settled questions (Ron, 2026-10-18)

1. **No "skip all in this column"** on the headers — unchecking the collection does that; one control per job.
2. **Chips reuse the app's existing tag-chip style** ("ABSOLUTELY") — a tag looks the same here as everywhere else.

## 7. Related, filed separately (not in 7.24.0)

- **One shared scrolling list with fixed top/bottom, then every list moves onto it** so its actions stay in view
  (Ron, 2026-10-19) — TODO.md (Polish): "Long lists keep their actions in view (Manage…, Select All) while you
  scroll". Starts with the Tags filter; right-click → Tags is the model. Only this window's note is in 7.24.0
  (build list item 2).

- **Tag order everywhere follows Manage Tags** (Ron + UX, 2026-10-18): the Tags filter and every tag list show tags in
  the order Manage Tags is set to; the hidden header-click cycle becomes a visible **Order: A→Z | Most used | Manual**;
  drag handles appear only in Manual; the manual order changes only in Manual view (viewing A→Z never touches a saved
  manual order). → added to the TODO task "One shared tag picker: show all tags in your order".

## History

- **v1 (6.10.0, 2026-08):** two panes — collections with checkboxes on the left; click a name to see that ONE
  collection's books on the right, each with a checkbox; "Removed from Kindle" section pre-checked; File menu (moved to
  Tools in 7.20.0). Full v1 text: `git log -- docs/design/TAG-FROM-COLLECTIONS.md`.
- **7.22.1-alpha.1 (2026-10-18):** an interim polish of v1 (heading per collection, total on the button, Manage Tags
  link, one shared calculation) — tested by Ron, which led to v2.
