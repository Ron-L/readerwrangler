# Book Recommendations Feature

**Date:** 2026-01-22
**Status:** Planned — **revised direction 2026-11-03** (TODO "Book recommendations: similar books you own, and ones you
don't have yet"). Probing showed: the list was never fetched (the request asks for Amazon tags only today); Amazon
already leaves out the books you own, so the "Owned badge" below rarely applies (pre-orders do come through); and only
a few books have Amazon tags yet. The TODO task now holds the plan: Amazon-tag coverage first, "similar books you own"
from Amazon tags, then Amazon's list with wishlist / pre-order badges, opening in the book window. This spec's UI below
predates that and is revised in the task.

## Summary

Display "Similar Books" recommendations in the book detail modal. Recommendations are already fetched during Phase 3 (tags) of library import but currently discarded.

## Data Source

The library fetcher's Amazon-tags request (step 3 of the library fetch) can return Amazon's "more like this" list too,
in the same request. **The request's shape, and what we learned probing it on 2026-11-03: see TODO notes.**

---

## Data Storage

### Per-Book Field

```json
"recommendations": [
  { "asin": "B0G3S65GF9", "title": "Out Law: A Dresden Files Novella", "coverUrl": "https://..." },
  { "asin": "B0B5H4N1WF", "title": "The Law: A Dresden Files Novella", "coverUrl": "https://..." }
]
```

### Storage Estimate

- ~100 bytes per recommendation
- ~10 recommendations per book
- ~1KB per book
- 1000 books = ~1MB additional storage

### Cover URL

Build from ASIN: `https://images-na.ssl-images-amazon.com/images/P/{ASIN}.01.LZZZZZZZ.jpg`

Or extract from API if available.

---

## UI Design

### Book Detail Modal

Add collapsible section at bottom of modal:

```
─────────────────────────────────────────────────
▶ Similar Books (10)                    [collapsed by default]
─────────────────────────────────────────────────
```

When expanded:

```
─────────────────────────────────────────────────
▼ Similar Books (10)
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│       │ │       │ │ OWNED │ │       │ │       │
│ cover │ │ cover │ │ cover │ │ cover │ │ cover │
│       │ │       │ │       │ │       │ │       │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘
  Title     Title     Title     Title     Title
                        ↑
                  "Owned" badge
─────────────────────────────────────────────────
```

### Interaction

| Action | Result |
|--------|--------|
| Hover on cover | Show full title in tooltip |
| Click on cover | Open Amazon product page in new tab |
| External link icon | Visual cue on hover indicating external link |

### Owned Badge

- Check recommendation ASIN against user's library at render time
- If owned: Show "Owned" badge overlay on cover
- Dynamic calculation (not stored) - stays current as library changes

### Amazon Links

- Build dynamically from ASIN: `https://www.amazon.com/dp/{ASIN}`
- Include Amazon Associate ID (same as wishlist book links)

---

## Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Show for owned & wishlist books? | Yes - both | Wishlist book rec might be affordable even if parent isn't |
| Filter out owned books? | No - show with badge | User may want to see the connection |
| Collapsible section? | Yes - collapsed by default | Keep modal compact; user can expand if interested |
| Confirmation dialog on click? | No | Users expect to learn more; external link icon signals behavior |
| Store Amazon link? | No | Build dynamically: `https://www.amazon.com/dp/{ASIN}` |

---

## Implementation Phases

### Phase 1: Fetcher (Extract Data)
- [ ] Modify Phase 3 in `amazon-library-fetcher.js` to extract `edges` array
- [ ] Build coverUrl from ASIN or extract from response
- [ ] Store as `recommendations` array on book object
- [ ] Only fetch for new books (same as tags behavior)

### Phase 2: UI (Display)
- [ ] Add collapsible "Similar Books" section to book detail modal
- [ ] Horizontal scrollable row of cover images
- [ ] Title tooltip on hover
- [ ] External link icon indicator
- [ ] Click opens Amazon product page

### Phase 3: Owned Badge
- [ ] At render time, check each recommendation ASIN against library
- [ ] Show "Owned" badge overlay if book is in library

---

## Files to Modify

| File | Changes |
|------|---------|
| `amazon-library-fetcher.js` | Extract recommendations from Phase 3 response |
| `readerwrangler.js` | Add Similar Books section to book modal |

---

## Open Questions

None - all design decisions resolved.

---

## Related Documents

- Amazon's side of the request: see TODO notes
- [SCHEMA-V2-UNIFIED-FILE.md](SCHEMA-V2-UNIFIED-FILE.md) - Book data model
