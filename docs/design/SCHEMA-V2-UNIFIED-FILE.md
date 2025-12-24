# Schema v2.0: Unified File Format

**Date:** 2025-12-24
**Status:** Design Complete, Implementation Pending

## Summary

Replace the current two-file system (`amazon-library.json` + `amazon-collections.json`) with a single unified file. Also adds wishlist support with books distinguished by an `isOwned` flag.

---

## Motivation

### Current Pain Points

1. **Two files to manage** - Users must load library JSON, then separately load collections JSON
2. **Easy to mismatch** - Loading wrong collections file against a library
3. **UX burden** - "Which file do I pick?" confusion
4. **Orphaned data** - Fresh library fetch doesn't carry forward wishlist items

### Why Merge Now?

- N=1 user currently (developer only)
- Breaking changes are cheap now, expensive later
- Wishlist feature requires schema changes anyway - good time to consolidate

---

## Design Decisions

### Key Decisions Table

| Question | Decision | Rationale |
|----------|----------|-----------|
| File structure | Merge library + collections into single file | Simpler UX, prevents mismatch |
| Wishlist storage | In `books.items` with `isOwned: false` | Same array, visual distinction only |
| Field naming | `isOwned` (boolean) | Follows `is*` naming convention |
| Fetcher naming | "Wish Fetcher" | Consistent with Library/Collections Fetcher |
| Duplicate handling | ASIN-merge (update existing, preserve location) | Wishlist→Owned transition is seamless |
| Default column for wishlist | Unorganized column | No special column needed |
| Fresh fetch behavior | In-app option with warning dialog | Don't offload to file system navigation |
| Fetcher order | Order independent - all are additive | No "Library must be first" constraint |

---

## Schema v2.0 Structure

```json
{
  "schemaVersion": "2.0",
  "books": {
    "fetchDate": "2025-12-24T10:30:00Z",
    "fetcherVersion": "1.2.0",
    "items": [
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
      },
      {
        "asin": "B09ABC5678",
        "isOwned": false,
        "title": "Wishlist Book",
        "author": "Another Author",
        "addedToWishlist": "2025-12-24",
        "coverUrl": "https://...",
        "rating": 4.8
      }
    ]
  },
  "collections": {
    "fetchDate": "2025-12-24T10:35:00Z",
    "fetcherVersion": "1.0.0",
    "items": {
      "B08XYZ1234": ["Currently Reading", "Sci-Fi"],
      "B09ABC5678": []
    }
  },
  "organization": {
    "columns": [
      {
        "id": "col-1",
        "name": "To Read",
        "items": ["B08XYZ1234", "div-1", "B09ABC5678"]
      }
    ],
    "columnOrder": ["col-1", "col-2"]
  }
}
```

### Section Breakdown

| Section | Purpose | Metadata |
|---------|---------|----------|
| `books` | All book items (owned + wishlist) | `fetchDate`, `fetcherVersion` |
| `collections` | Amazon's collection assignments | `fetchDate`, `fetcherVersion` |
| `organization` | User's column layout and order | None (user-managed) |

### Book Item Fields

| Field | Type | Owned Books | Wishlist Books |
|-------|------|-------------|----------------|
| `asin` | string | ✅ Required | ✅ Required |
| `isOwned` | boolean | `true` | `false` |
| `title` | string | ✅ | ✅ |
| `author` | string | ✅ | ✅ |
| `coverUrl` | string | ✅ | ✅ |
| `rating` | number | ✅ | ✅ |
| `acquiredDate` | string | ✅ | ❌ |
| `addedToWishlist` | string | ❌ | ✅ |
| `pageCount` | number | ✅ | Optional |
| `description` | string | ✅ | Optional |

---

## Fetcher Behavior

### Three Fetchers

1. **Library Fetcher** - Scrapes owned books from Amazon library page
2. **Collections Fetcher** - Scrapes Amazon collection assignments
3. **Wish Fetcher** - Scrapes current book page (single book) or wishlist page

### Order Independence

Any fetcher can run first. All fetchers are **additive**:

```
User has: Empty file
Runs: Wish Fetcher → adds 1 wishlist book
Runs: Library Fetcher → adds 100 owned books
Runs: Collections Fetcher → adds collection mappings
Result: 101 books with collections
```

```
User has: 100 owned books
Runs: Wish Fetcher on a book they already own
Result: No change (duplicate detected by ASIN, silent no-op)
```

### ASIN-Based Merge Logic

When adding a book:

```
if (books.items.find(b => b.asin === newBook.asin)) {
  // Book exists - update fields but preserve location
  // If wishlist book becomes owned: set isOwned = true, add acquiredDate
} else {
  // New book - add to items array
}
```

### Wishlist → Owned Transition

When user purchases a wishlist book and re-fetches library:

1. Library Fetcher finds book with matching ASIN
2. Updates `isOwned: false` → `isOwned: true`
3. Adds `acquiredDate` field
4. Book **stays in current column** (doesn't move to Unorganized)
5. Visual effect: "ungrays" in place

---

## App Behavior

### File Loading

1. User clicks "Load Library" (single button, not two)
2. File picker opens
3. App reads file, checks `schemaVersion`
4. If v1.x: Show migration dialog, convert to v2.0
5. If v2.0: Load directly

### Fresh Fetch Option

When user wants to start completely fresh:

1. App shows warning dialog:
   - "This will replace your current library with a fresh fetch"
   - "Existing organization and wishlist items will be lost"
   - "Are you sure?" [Cancel] [Proceed]
2. If proceed: Clear current state, run Library Fetcher
3. User is **not** asked to navigate file system or delete files manually

### Wishlist Display

- Wishlist books (`isOwned: false`) appear in Unorganized column initially
- User can drag to any column
- Visual distinction:
  - Gray-out effect on cover/title
  - "Wishlist" badge overlay
  - Click opens Amazon purchase page (instead of detail modal)

---

## Migration Path

### v1.x → v2.0 Conversion

When app detects old file format:

1. Detect by: absence of `schemaVersion` field, or presence of top-level `books` array (not object)
2. Show migration dialog explaining the change
3. Convert in memory:
   - Wrap `books` array in `books.items`
   - Add `books.fetchDate`, `books.fetcherVersion` (from file metadata or "unknown")
   - Add `schemaVersion: "2.0"`
   - Create empty `collections` section if not present
   - Preserve `organization` section as-is
4. Save as new file (don't overwrite old file automatically)

### Backwards Compatibility

- App can read v1.x files and auto-migrate
- App always saves in v2.0 format
- No backwards-writing to v1.x format

---

## File Naming

| Scenario | Filename |
|----------|----------|
| Default export | `amazon-library.json` |
| Backup | `amazon-library-backup-YYYY-MM-DD.json` |
| Old v1.x files | Still loadable, migrated on load |

Note: `amazon-collections.json` becomes obsolete. Collections data is now embedded in the unified file.

---

## Implementation Phases

### Phase 1: Schema v2.0 Core
- [ ] Update file save to v2.0 format
- [ ] Update file load to parse v2.0 format
- [ ] Add v1.x migration on load
- [ ] Remove separate collections file loading

### Phase 2: Wishlist Feature
- [ ] Create Wish Fetcher bookmarklet
- [ ] Add `isOwned` field handling
- [ ] Add wishlist visual styling (gray-out, badge)
- [ ] Add Amazon purchase link behavior

### Phase 3: Fetcher Updates
- [ ] Update Library Fetcher for unified file
- [ ] Update Collections Fetcher for unified file
- [ ] Implement ASIN-merge logic
- [ ] Handle wishlist→owned transitions

---

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Separate wishlist array vs. flag in items? | Flag in items (`isOwned: false`) |
| Special wishlist column? | No, use Unorganized column |
| What happens to wishlist on fresh fetch? | Lost (with warning), user's choice |
| Order of fetcher execution? | Order independent |
| User navigation to file system? | Never required - all in-app |

---

## Related Documents

- [MULTI-USER-DESIGN.md](MULTI-USER-DESIGN.md) - Future multi-user support
- [MULTI-STORE-ARCHITECTURE.md](MULTI-STORE-ARCHITECTURE.md) - Future non-Amazon support
