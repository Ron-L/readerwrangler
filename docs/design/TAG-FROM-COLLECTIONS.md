# Tag from Collections — Design

_v2 design (Ron + UX, 2026-10-18) for 7.22.1, branch `fix/tfc-clarity`. Replaces the v1 layout (6.10.0, 2026-08 —
see "History" at the end; v1's full text is in git). The **data model is unchanged** from v1 and is restated below._

**What it is:** a window (**Tools → Tag from Collections…**) that turns Kindle collections into ReaderWrangler tags.
Collections come from Amazon and can't be edited here; tags are yours. Each collection becomes a tag of the same name,
on the books in that collection. Re-run after new purchases: the right side shows only books that would change.

---

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
4. **Help notes:** to remove a tag from many books, use **All Books → filter by the tag → select → right-click → Tags**
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

## 3. Data model (unchanged from v1)

- ~~`book.collectionTagSeen`~~ — **retired** (2.8; stripped from data in 7.22.1-alpha.4). It was set for every book **shown** in the wizard when Apply is clicked (checked or not):
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

## 7. Related, filed separately (not in 7.22.1)

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
