# Wishlist & Hide Feature Design

**Date:** 2025-12-28
**Status:** Design Complete, Implementation Pending

## Summary

Add ability to track books user wants to purchase (wishlist) and hide books user doesn't want to see. These features are bundled because the primary use case for hiding is managing wishlist items (e.g., unwanted books from a series add).

---

## Feature Overview

### Wishlist
- Track books user wants to purchase but doesn't own yet
- Add from Amazon product pages (single book) or series pages (all books in series)
- Wishlist books appear in Unorganized column with visual distinction
- When purchased and library re-fetched, book "ungrays" in place

### Hide
- Soft-delete books user doesn't want to see
- Applies to both owned and wishlist books
- Recoverable via "Show Hidden" filter
- Use cases:
  - Remove unwanted wishlist books (series add added too many)
  - Hide owned books user doesn't want to track (samples, accidental purchases)

---

## Design Decisions

### Key Decisions Table

| Question | Decision | Rationale |
|----------|----------|-----------|
| Navigator placement | Context-aware button in existing Navigator | Consistent pattern, no new bookmarklet needed |
| Wishlist storage | In `books.items` with `isOwned: false` | Same array, visual distinction only |
| Series add behavior | Add ALL books in series | Simplicity; user can hide unwanted books |
| Duplicate handling | App Loader handles (owned overrides wishlist) | Single location for all duplicate logic |
| Deletion approach | Soft delete with `isHidden: true` | Recoverable, survives re-fetch |
| Hide scope | All books (owned and wishlist) | Users may want to hide owned "trash" books too |
| Data fetch method | Extract ASIN(s) from page, call Amazon API | Complete data, stable, same as library fetcher |
| File merge | Wishlist Fetcher merges into existing `amazon-library.json` | Single file, immediate result |

---

## Schema Changes

### New Book Fields

| Field | Type | Description |
|-------|------|-------------|
| `isOwned` | boolean | `true` for owned books, `false` for wishlist |
| `isHidden` | boolean | `true` if user has hidden this book |
| `addedToWishlist` | string (ISO date) | Date book was added to wishlist (stored but not displayed in v1) |

### Example Book Objects

**Owned book:**
```json
{
  "asin": "B08XYZ1234",
  "isOwned": true,
  "title": "Example Book",
  "author": "Author Name",
  "acquiredDate": "2024-06-15",
  "coverUrl": "https://...",
  "rating": 4.5,
  "pageCount": 320,
  "description": "..."
}
```

**Wishlist book:**
```json
{
  "asin": "B09ABC5678",
  "isOwned": false,
  "addedToWishlist": "2025-12-28",
  "title": "Wishlist Book",
  "author": "Another Author",
  "coverUrl": "https://...",
  "rating": 4.8
}
```

**Hidden book:**
```json
{
  "asin": "B07DEF9012",
  "isOwned": true,
  "isHidden": true,
  "title": "Hidden Book",
  ...
}
```

---

## Navigator Changes

### Context-Aware Button Detection

| Current Page | Detection | Button Shows |
|--------------|-----------|--------------|
| Product page | URL contains `/dp/` or `/gp/product/` | "Add to Wishlist" (single book) |
| Series page | URL contains `/dp/` AND series grid detected | "Add Series to Wishlist" (batch) |
| Library page | URL contains `/yourbooks` | "Fetch Library Data" |
| Collections page | URL contains `/hz/mycd/digital-console` | "Fetch Collections Data" |

### Series Page Detection

Series pages are product detail pages (`/dp/ASIN`) that contain a series book grid. Detection:
1. Check if URL matches `/dp/B[0-9A-Z]+` (ignore query params like `?binding=kindle_edition&ref=...`)
2. Look for series grid element in DOM (TBD: specific selector after testing)
3. If both match → show "Add Series to Wishlist"

**Note:** Amazon shows a "Shop this series" panel with "All X available" link that filters to unowned books. We intentionally do NOT use this because:
- Requires additional navigation
- Depends on Amazon's UI staying stable
- App Loader already handles duplicates (owned overrides wishlist)
- Simpler to add all series books and let App dedupe

### Updated Navigator Dialog

```
┌─────────────────────────────────────┐
│              📚                      │
│        ReaderWrangler               │
│                                      │
│  [➕ Add to Wishlist]          ← NEW (product page)
│  [➕ Add Series to Wishlist]   ← NEW (series page)
│  [📖 Go to Library Fetcher...]      │
│  [📚 Go to Collections Fetcher...]  │
│  [🎯 Launch App]                    │
│  [ℹ️ Launch Intro for Help]         │
│                                      │
│              v1.2.0                  │
└─────────────────────────────────────┘
```

---

## Wishlist Fetcher

### New File: `amazon-wishlist-fetcher.js`

Loaded by Navigator when user clicks "Add to Wishlist" or "Add Series to Wishlist".

### Flow: Single Book (Product Page)

1. Extract ASIN from URL (`/dp/B001Q9J4QA` → `B001Q9J4QA`)
2. Get CSRF token (same method as library fetcher)
3. Call Amazon `getProducts` API with ASIN
4. Build book object with `isOwned: false`, `addedToWishlist: today`
5. Prompt user to select existing `amazon-library.json` (File System Access API)
6. Read file, check for duplicate ASIN:
   - If exists with `isOwned: true` → show "You already own this book" message, no change
   - If exists with `isOwned: false` → show "Already in wishlist" message, no change
   - If not exists → prepend to `books.items`
7. Write updated file back (same handle) or download if Firefox/Safari
8. Show success toast: "Added [Book Title] to wishlist"

### Flow: Series (Series Page)

1. Extract series container ASIN from URL
2. Wait for series grid to load (DOM observation)
3. Extract all book ASINs from series grid
4. Get CSRF token
5. Batch call `getProducts` API (30 ASINs per call, same as library fetcher)
6. Build book objects with `isOwned: false`, `addedToWishlist: today`
7. Prompt user to select existing `amazon-library.json`
8. Read file, filter out duplicates (skip any ASIN already in file)
9. Prepend new books to `books.items`
10. Write updated file back
11. Show success toast: "Added X books to wishlist (Y already in library)"

### Progress UI

Reuse the same progress overlay pattern as library fetcher:
- Phase indicator
- Progress bar for series (X of Y books)
- Elapsed time
- Abort button

### Error Handling

| Scenario | Behavior |
|----------|----------|
| Not on Amazon page | Show error: "Please navigate to an Amazon book page" |
| No ASIN in URL | Show error: "Could not detect book. Try a different page." |
| API call fails | Retry with backoff (same as library fetcher) |
| File picker cancelled | Abort gracefully, no changes |
| File read error | Show error with details |

---

## App Changes

### Wishlist Display

**Visual distinction for wishlist books (`isOwned: false`):**

1. **Gray-out effect**: Reduced opacity (e.g., `opacity: 0.6`) on cover and title
2. **"Wishlist" badge**: Small overlay badge on book card (purple/blue to match app theme)
3. **Click behavior**: Opens Amazon product page (instead of detail modal) for easy purchase

**CSS approach:**
```css
.book-card.wishlist {
  opacity: 0.7;
}
.book-card.wishlist .wishlist-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}
```

### Hide Feature

**Right-click context menu addition:**

Current menu:
```
Open in Amazon
Copy Title
─────────────
Hide Book        ← NEW
```

If book is already hidden:
```
Open in Amazon
Copy Title
─────────────
Unhide Book      ← Shows instead
```

**Filter addition:**

Add checkbox to filter bar:
```
[Status ▼] [Rating ▼] [Author ▼] ... [☐ Show Hidden]
```

When "Show Hidden" is checked:
- Hidden books appear with visual distinction (strikethrough on title? faded red tint?)
- Right-click shows "Unhide Book" option

**Hidden book visual:**
```css
.book-card.hidden {
  opacity: 0.4;
  border: 1px dashed #ccc;
}
.book-card.hidden .title {
  text-decoration: line-through;
}
```

### Duplicate Handling (App Loader)

When loading library file, handle duplicates **in memory** (do not modify JSON file):

**Why filter in memory, not modify JSON:**
- Simpler - no file modification logic needed
- Safer - can't corrupt the JSON file
- Fast enough - deduping 2400 books by ASIN is milliseconds
- Append-only fetchers - fetchers stay simple (just add books)

The "duplicates in file" downside is minimal - file size grows slightly, but the data is small per book and the file is already local.

```javascript
// Pseudocode for merge logic - runs on every load, doesn't modify file
function deduplicateBooks(booksArray) {
  const seen = new Map(); // ASIN → book object

  for (const book of booksArray) {
    const existing = seen.get(book.asin);
    if (existing) {
      // Duplicate - owned always wins over wishlist
      if (book.isOwned && !existing.isOwned) {
        seen.set(book.asin, { ...existing, ...book, isOwned: true });
      }
      // Otherwise keep existing (first in file wins for same ownership status)
    } else {
      seen.set(book.asin, book);
    }
  }

  return Array.from(seen.values()); // Deduplicated in memory only
}
```

### Wishlist → Owned Transition

When library fetcher runs and finds a book that exists as wishlist:

1. Library Fetcher adds book with `isOwned: true`
2. App Loader detects duplicate (same ASIN)
3. Owned overrides wishlist: `isOwned: false` → `isOwned: true`
4. `acquiredDate` is added
5. `addedToWishlist` can be preserved (nice to know when you first wanted it)
6. Book **stays in current column** (organization preserved)
7. Visual: Book "ungrays" - no longer shows wishlist styling

---

## Implementation Phases

### Phase 1: Hide Feature (App-only)
- [ ] Add `isHidden` field support to book schema
- [ ] Add "Hide Book" / "Unhide Book" to right-click context menu
- [ ] Add "Show Hidden" filter checkbox
- [ ] Add hidden book visual styling
- [ ] Update App Loader to preserve `isHidden` on reload

**Rationale:** Hide can be implemented and tested independently. Sets foundation for wishlist cleanup.

### Phase 2: Navigator Updates
- [ ] Add product page detection (`/dp/`, `/gp/product/`)
- [ ] Add series page detection (URL + DOM check)
- [ ] Add "Add to Wishlist" button (product pages)
- [ ] Add "Add Series to Wishlist" button (series pages)
- [ ] Update NAV_HUB_VERSION

### Phase 3: Wishlist Fetcher - Single Book
- [ ] Create `amazon-wishlist-fetcher.js`
- [ ] Implement ASIN extraction from URL
- [ ] Implement single-book API fetch
- [ ] Implement file read/merge/write flow
- [ ] Add progress UI (simple toast for single book)
- [ ] Handle duplicate detection

### Phase 4: Wishlist Fetcher - Series
- [ ] Implement series grid ASIN extraction
- [ ] Implement batch API fetch
- [ ] Add progress UI with progress bar
- [ ] Handle partial failures gracefully

### Phase 5: App Wishlist Display
- [ ] Add wishlist visual styling (gray-out, badge)
- [ ] Change click behavior for wishlist books (→ Amazon)
- [ ] Update App Loader duplicate handling (owned overrides wishlist)
- [ ] Test wishlist → owned transition

---

## File Changes Summary

| File | Changes |
|------|---------|
| `bookmarklet-nav-hub.js` | Add page detection, wishlist buttons |
| `amazon-wishlist-fetcher.js` | NEW - fetcher for wishlist books |
| `readerwrangler.js` | Hide feature UI, wishlist display styling, duplicate handling |
| `docs/design/SCHEMA-V2-UNIFIED-FILE.md` | Reference this doc for wishlist fields |

---

## Open Questions

| Question | Status |
|----------|--------|
| Series grid DOM selector | TBD - need to inspect live series page |
| Exact badge design/position | TBD - visual design during implementation |
| Toast notification library vs custom | TBD - may use existing pattern from fetchers |

---

## Related Documents

- [SCHEMA-V2-UNIFIED-FILE.md](SCHEMA-V2-UNIFIED-FILE.md) - Base schema (references wishlist)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Storage architecture rationale
