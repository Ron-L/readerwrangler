# Tag from Collections — Design

_v2 design (Ron + UX, 2026-10-18) for 7.22.1, branch `fix/tfc-clarity`. Replaces the v1 layout (6.10.0, 2026-08 —
see "History" at the end; v1's full text is in git). The **data model is unchanged** from v1 and is restated below._

**What it is:** a window (**Tools → Tag from Collections…**) that turns Kindle collections into ReaderWrangler tags.
Collections come from Amazon and can't be edited here; tags are yours. Each collection becomes a tag of the same name,
on the books in that collection. Re-run after new purchases: "New books only" shows just the books you haven't seen.

---

## 1. Why v2

1. **Two click targets per row, nothing to tell them apart.** In v1 each collection row has a **checkbox** ("use this
   collection when you Apply") and a **name** ("show its books on the right"). Unchecking a box didn't change the right
   side; "checked" and "being shown" looked alike. It fooled Ron (2026-10-14, again 2026-10-18 on 7.22.1-alpha.1).
2. **The right side showed one collection at a time**, so you never saw everything Apply would do.
3. **A data bug (found 2026-10-18): the wizard misses existing tags whose name has capitals.** Tags get their internal
   key two ways — the book details window and the bulk editor keep capitals ("Read" → key `Read`, readerwrangler.js
   ~14064, ~14120, ~19847, ~19913), Manage Tags and this wizard lowercase it (`read`, ~18080). So the wizard looks up
   `read`, misses your `Read`, says "will create a new tag" — and **Apply would create a second "Read" tag** and put the
   books on that one. That breaks v1's own rule ("same name exists → add to it, don't create a duplicate").
4. **A tag could be created with no books on it**, just because its collection was checked.
5. **Removals of tags were pre-checked** — one click on Apply removed them.

## 2. The design

### 2.1 Layout

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🏷️ Tag from Collections                                                      [×] │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Select: [All|Some|None]   ☑ New books only   ☐ Also remove tags whose book left  │
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

1. **One click target per row.** Clicking anywhere on a row (box or name) toggles its checkbox. There is no "being
   shown" state and no row highlight — the right side shows all checked collections at once.
2. Each row: checkbox, the collection name, its count — "(7 new)" with New books only, "(12)" without.
3. **A collection with nothing to show** (0 books under "New books only") is **greyed out, its checkbox disabled, and
   kept in its alphabetical place** — hiding it would make collections seem to vanish; moving it would reshuffle the
   list when "New books only" flips. Tooltip: *"No new books here — turn off 'New books only' to see all of its books."*
4. "(tag exists)" stays, now correct (see 2.6).
5. **Select: All | Some | None** works as today (over the enabled rows).

### 2.3 Right: "Changes Apply will make"

1. **Every book in every checked collection, one row each** — the complete list of what Apply will do.
2. **One column per checked collection that has a change**, with the tag name as a **header that stays visible while
   you scroll**, and its count: *Read (7)*. Columns are aligned (an invisible grid — no lines).
3. **The chip in each cell** — a small tag shape:
   - **"+ Read"** — Apply will add this tag to this book.
   - **"✓ Read"** (grey) — the book already has it; nothing happens.
   - **"skip"** (struck through) — you clicked the "+" chip: this one tag won't go on this one book. Click again to
     restore. (This is v1's per-book unchecking, now per book × tag.)
   - **"− Sci-Fi"** (amber) — only when removals are switched on (2.5).
   - Empty cell — the book isn't in that collection.
4. **Sorting:** click **Title** for A–Z (the default); click a **tag header** to bring the books with a change in that
   column to the top. Spreadsheet behavior, nothing new to learn.
5. **No filter on the right** — the left checkboxes already ARE the column filter. A second filter would be two
   controls for one job.
6. **Wide or long:** past about 6 columns the right side scrolls sideways with titles staying put; a first-ever run
   (everything new) can list hundreds of rows — fine to scroll; later "New books only" runs are small.
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
4. **Help notes:** to remove a tag from many books, use **All Books → filter by the tag → select → right-click → Tags**
   — goes into SUPPORT-KB (it feeds the help assistant).

### 2.6 Tag identity — one way to find or make a tag

1. **One shared function: find the tag with this name, ignoring capitals; create it only if none exists.** All six
   places that create tags use it (book details ×2, bulk editor ×2, Manage Tags, this wizard), so "Read" and "read"
   can never become two tags again.
2. Existing keys are not renamed (that would touch every book and every Search) — lookups go by name.
3. **Duplicate check before building:** list any existing tags whose names match ignoring capitals (an earlier wizard run
   may already have made a pair). If any exist, Ron decides what to do with them before the fix ships (merging is its
   own small task).

## 3. Data model (unchanged from v1)

- `book.collectionTagSeen = true` — set for every book **shown** in the wizard when Apply is clicked (checked or not):
  you saw it, so it isn't "new" next time. Internal, not shown, not editable.
- `book.collectionTags = ["read", …]` — tag keys **this wizard** assigned. Removal candidates come only from here; a
  declined removal drops the key from `collectionTags` only (the tag becomes yours).
- `book.collections = [{ name }]` — from the Kindle collections fetch, read-only, replaced on each import.
- With 2.6, `collectionTags` holds the key of the tag actually used (the existing `Read` if it exists), not a computed
  lowercase key.

## 4. Apply (what happens)

1. For each checked collection with ≥1 "+" chip: find-or-create its tag (2.6); add it to each "+" book (and to that
   book's `collectionTags`).
2. Removals (only if switched on): each "−" chip removes the tag from `tags` and `collectionTags`; a kept one drops it
   from `collectionTags` only.
3. Every shown book gets `collectionTagSeen = true`.
4. One undoable step (as today); a toast names what was done.
5. **One calculation** decides "which books will get which tag" — used by the chips, the header counts, the button and
   Apply itself (7.22.1-alpha.1 already merged v1's two copies).

## 5. Verification (test steps for the alpha)

1. Ron's **Read** collection (7 newly read books): None → check Read → 7 "+ Read" chips, header *Read (7)*, button
   *"Tag 7 books from 1 collection"*; Apply → the books get the **existing** "Read" tag (no second tag); Ctrl+Z undoes.
2. Check a second collection → its column appears; a book in both shows two chips; the total adds up.
3. Click a "+" chip → "skip"; total drops by 1; Apply leaves that book without that tag.
4. Click a tag header → books with a change in that column come first; click Title → A–Z.
5. "New books only" on → a collection with 0 new books is greyed and can't be checked; off → it's enabled.
6. Removals off (default) → no amber rows or "−" chips anywhere; tick the box → they appear.
7. A collection whose books all already have the tag → no column, no tag created, button unchanged.
8. Manage Tags → "Create tags from your Kindle collections…" opens this window.
9. After Apply: Manage Tags shows no duplicate names.

## 6. Open questions

1. Should a column header also allow "skip all in this column"? (Unchecking the collection does nearly the same.)
   Proposed: no — keep one control per job.
2. Chip look: reuse the app's existing tag-chip style, so a tag looks the same here as everywhere else.

## History

- **v1 (6.10.0, 2026-08):** two panes — collections with checkboxes on the left; click a name to see that ONE
  collection's books on the right, each with a checkbox; "Removed from Kindle" section pre-checked; File menu (moved to
  Tools in 7.20.0). Full v1 text: `git log -- docs/design/TAG-FROM-COLLECTIONS.md`.
- **7.22.1-alpha.1 (2026-10-18):** an interim polish of v1 (heading per collection, total on the button, Manage Tags
  link, one shared calculation) — tested by Ron, which led to v2.
