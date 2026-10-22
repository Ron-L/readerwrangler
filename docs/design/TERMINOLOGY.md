# Terminology — one book, many places (no "shortcuts", no "Linked Copies")

_Moved verbatim from TODO.md during the 6.12.0 TODO restructure (2026-08-03). FINAL decision 2026-07-07; **reversed
2026-10-22** (below)._

---

## Current decision (Ron + UX, 2026-10-22, in the TODO review)

**Neither term is used — not on screen, not in the User Guide.** Users get one idea instead of two nouns: *the same
book can be in many places.* The screens keep their plain verbs — **Move**, **Copy**, **Remove from "‹list›"** — and the
receipts say "Added", "Moved", "removed from" (never "deleted from": deleted = the Trash).

**Why the 2026-07-07 plan was reversed**
1. **"Shortcut" teaches the internal model the app no longer enforces.** On 2026-10-21 (Law 18, the Prime Directive)
   folders and Book Lists took the same verbs — "an icon is an icon… there is no wrong way" (TODO: "Move and copy
   books anywhere"). "Remove shortcut" would be a second word for "Remove from this list", which is already clear.
2. **"Linked Copies" collides with the Copy command.** "Copy to" adds the *same* book to another place; calling folder
   entries "copies" too makes the word mean two things, and suggests a duplicate — the very misunderstanding to avoid.
3. Ron considered "like a shortcut" once more — it's accurate only as a *hard link*, which most users don't know — and
   took it back.
4. **All Books is a view, not where a book lives** (Ron). The old anchor model said "All Books is where the book truly
   lives"; wrong. All Books, like a Search, shows books wherever they're filed — which is why nothing can be moved or
   copied into it, and why it sits above Searches.

**Anchor model for the User Guide** ("One book, many places" — a draft; Ron's word on the final wording):

> A book can be in several folders and Book Lists at once — the same book each time, not a duplicate: change its tags
> or rating anywhere and every place shows it. Every book is filed in at least one folder; the Inbox holds the ones
> not filed yet. **All Books and Searches are views**: they show books wherever they're filed, so nothing is put into
> them or taken out of them. Removing a book from a Book List, or from one of several folders, leaves it everywhere
> else. Deleting it from its last folder — or from All Books or a Search — sends it to the Trash.

Facts behind it (checked in the code 2026-10-22):
- Delete in All Books / a Search = the book itself: out of every folder, into the Trash (since 7.10.1).
- Delete in a book's only folder → the Trash, after a warning. A *move* out of its last folder → the Inbox (decided
  2026-10-21, "Move and copy books anywhere", decision 3).
- Cut from All Books is refused today; decided 2026-10-21 to become a re-file (paste into a folder → it leaves its
  other folders).

Then say what really differs: **folders file books** (every book in at least one, they nest, Auto-Organize fills them);
**Book Lists are free-form** (your own order, a to-read queue, never required).

---

## Companion doc note — Book List ↔ Folder workflow pattern (for the User Guide / support assistant)

Ron's real usage: author/series *structure* lives in **Folders** (with hierarchy, e.g. `New To Read/Old Free Stuff` for dubious early-Kindle freebies); reading-order / "to-read" *queues* live in **Book Lists** (`<Series> — To Read`; remove each book from the list as it's finished). Two equivalent flows: (a) file in a folder now + put it on a "New To Read" list up-front, or (b) keep in a staging folder and move to `Various Authors` once read. Folders give sub-category hierarchy that Book Lists can't. Teach this as the canonical organizing pattern. (Also: "get books out of Inbox → use a folder, not a Book List.")

---

## History — the 2026-07-07 decision (reversed 2026-10-22)

Book List items = "shortcuts" (deletable pointers; the book stays). Folder items = "Linked Copies" — explain ONCE in
the manual, then just "Copies" (edits propagate across all, co-equal, no primary). Rejected "shortcut for folders"
(implies a primary + soft-links) and "Magic Copies" (gimmicky); "Linked" chosen over "Synchronized". The work was to
be: "shortcut" language in Book List toasts + menus ("remove shortcut", "add shortcut"), and "Linked Copies" explained
once in the manual. Its anchor model: *All Books is where the book truly lives; Folders hold Linked Copies of it; Book
Lists hold shortcuts to it.* Never shipped — the app never used either word on screen.
