# Series Page Bulk Import Design

**Status:** Research Complete, Ready for Implementation
**Priority:** P1 T7 (Top Personal Priority)
**Estimated Effort:** 6-10 hours
**Date:** 2026-01-10

## Overview

Bulk import all books from an Amazon series page as wishlist entries (isOwned: false). This enables users to quickly populate their wishlist with an entire book series without visiting each product page individually.

**Primary Use Case:** User wants to replace physical books with Kindle editions for a 100+ book series.

## Problem Statement

Adding books from a large series (e.g., 155 books) to wishlist currently requires:
1. Navigate to each product page
2. Click bookmarklet
3. Select "Add to Wishlist"
4. Use file picker to select JSON file
5. Repeat 155 times

This feature reduces that to a single bookmarklet click on the series page.

## API Discovery

### Series Page List Endpoint

**Endpoint:** `https://www.amazon.com/kindle-dbs/productPage/ajax/seriesAsinList`

**Method:** GET

**Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `asin` | Series ASIN | `B0D775V4W9` |
| `pageNumber` | Page number (1-indexed) | `1` |
| `pageSize` | Books per page (max unknown, 200 tested) | `200` |
| `binding` | Format filter | `kindle_edition` |

**Minimal Request:**
```javascript
fetch("https://www.amazon.com/kindle-dbs/productPage/ajax/seriesAsinList?asin=B0D775V4W9&pageNumber=1&pageSize=200&binding=kindle_edition", {
  headers: {
    "accept": "text/html,*/*",
    "x-requested-with": "XMLHttpRequest"
  }
}).then(r => r.text()).then(html => console.log(html));
```

**Response:** HTML fragment (not JSON) containing book cards. Each book is wrapped in a `<div class="series-childAsin-item">`.

### Response Size Testing

| pageSize | Response Size | Result |
|----------|---------------|--------|
| 20 | ~300KB | Default (what Amazon uses) |
| 200 | ~1.5MB | Works - returns all available books |

**Recommendation:** Use `pageSize=200` to minimize API calls. For series >200 books, paginate.

## HTML Parsing

Each book entry can be extracted using these selectors:

### Book Container
```css
.series-childAsin-item
```

### Data Extraction Selectors

| Field | Selector | Example Value |
|-------|----------|---------------|
| ASIN | `a.itemImageLink[href]` → extract from `/gp/product/BXXXXXXXXX` | `B0CHRKTWWL` |
| Title | `.itemBookTitle h3` | `Created, The Destroyer` |
| Cover URL | `img.asinImage[src]` | `https://m.media-amazon.com/images/I/51ZcbS9-4lL._SY300_.jpg` |
| Authors | `a.series-childAsin-item-details-contributor` (multiple) | `Warren Murphy`, `Richard Sapir` |
| Rating | `.a-icon-star-small span.a-icon-alt` → parse number | `4.3` |
| Review Count | `span[aria-label*="ratings"]` → parse number | `2218` |
| Series Position | `span.itemPositionLabel[aria-label]` → parse "Book N" | `1` |
| Kindle Price | `.formatTwister:has(a:contains("Kindle")) .a-text-bold` | `$6.99` |
| Description | `.collectionDescription span` | Full description text |

### Sample Parsing Code

```javascript
function parseSeriesBooks(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const books = [];

    doc.querySelectorAll('.series-childAsin-item').forEach(item => {
        const asinLink = item.querySelector('a.itemImageLink');
        const asinMatch = asinLink?.href.match(/\/gp\/product\/([A-Z0-9]+)/);

        const book = {
            asin: asinMatch?.[1] || '',
            title: item.querySelector('.itemBookTitle h3')?.textContent?.trim() || '',
            coverUrl: item.querySelector('img.asinImage')?.src || '',
            authors: [...item.querySelectorAll('a.series-childAsin-item-details-contributor')]
                .map(a => a.textContent.replace(/\s*\(Author\)\s*,?\s*/g, '').trim())
                .filter(Boolean),
            rating: parseFloat(item.querySelector('.a-icon-star-small .a-icon-alt')?.textContent?.match(/[\d.]+/)?.[0]) || null,
            reviewCount: parseInt(item.querySelector('span[aria-label*="ratings"]')?.getAttribute('aria-label')?.replace(/[^\d]/g, '')) || 0,
            seriesPosition: parseInt(item.querySelector('.itemPositionLabel')?.getAttribute('aria-label')?.match(/\d+/)?.[0]) || null,
            kindlePrice: item.querySelector('.formatTwister a[href*="storeType=ebooks"]')
                ?.closest('.formatTwister')?.querySelector('.a-text-bold')?.textContent?.trim() || null,
            description: item.querySelector('.collectionDescription span')?.textContent?.trim() || '',
            isOwned: false,  // Wishlist entry
            source: 'series-import'
        };

        if (book.asin) books.push(book);
    });

    return books;
}
```

## Known Limitations

### Amazon Series Metadata Gaps

**Root Cause:** Amazon's series tagging is incomplete. Books exist in the Kindle store but aren't tagged as belonging to the series.

**Evidence:**
| Series | Reported | Actual Range | Missing |
|--------|----------|--------------|---------|
| The Destroyer | "103 books" | 1-155+ | 101-149 (not in series metadata) |
| The Hardy Boys | "117 books" | 1-190 | 59-108, 113-135 |

**Investigation Results:**
- Series page header shows Amazon's count (e.g., "103 books")
- Individual missing books exist in Kindle store but lack series metadata
- Example: Destroyer #101 (B0CNS2VV2Y) exists but product page doesn't list series
- Amazon search CAN find missing books: `warren murphy the destroyer #101`
- Gap boundaries suspiciously align with multiples of 50 (coincidence or batch processing?)

**Mitigation:**
1. Parse `seriesPosition` from each book
2. Detect gaps by comparing max position to book count
3. Warn user: "Found 106 books, but series numbering goes to 155. Books 101-149 not tagged in Amazon's series metadata."

### Gap-Filling: Core Feature (Not Optional)

**UX Rationale:** Gap-filling MUST be part of the core Series Import feature, not a separate enhancement.

**Why this matters:**
1. **Frustration transfer** - Users chose ReaderWrangler to escape Amazon's chaos. If we deliver incomplete data without helping, we become "part of the problem."
2. **Target use case is large series** - Nobody uses bulk import for 5-book series. The feature attracts users with 50-200 book series - exactly where gaps hurt most.
3. **First impression** - If their first series import is missing 49 books with no path forward, they may abandon the feature (or the app).
4. **Competitive differentiation** - Solving Amazon's mess IS our value prop.

**Technical approach:**
Missing books can be found via Amazon search: `"author name" "series name" #N`

The gap-filling feature will:
1. Detect gap ranges from series page import
2. Search Amazon for each missing book number
3. Parse search results to get ASINs
4. Fetch product page data for each found book
5. Merge into the import results

### Detection Logic

```javascript
function detectGaps(books) {
    const positions = books.map(b => b.seriesPosition).filter(Boolean).sort((a,b) => a-b);
    const maxPosition = Math.max(...positions);
    const actualCount = positions.length;

    if (maxPosition > actualCount) {
        const missing = [];
        for (let i = 1; i <= maxPosition; i++) {
            if (!positions.includes(i)) missing.push(i);
        }
        return {
            hasGaps: true,
            expected: maxPosition,
            actual: actualCount,
            missingPositions: missing
        };
    }
    return { hasGaps: false };
}
```

## Implementation Plan

### Architecture Decision: Bundled Gap-Filling

Gap-filling is bundled into the Series Import feature (not a separate operation) because:
- **Best UX** - User does one operation, gets complete result
- **2-3 minute wait is acceptable** for a one-time import of 150 books
- Avoids user confusion about "why is my import incomplete?"

### Phase 1: Series Page Fetcher (Bookmarklet Script)

**New file:** `series-page-fetcher.js`

**Step 1: Series Page Detection & Initial Fetch**

1. **Detect series page:**
   - URL pattern: `amazon.com/dp/BXXXXXXXXX` with series indicator
   - Or presence of `.series-childAsin-item` elements

2. **Extract series metadata:**
   - Series ASIN from URL
   - Series name from page title
   - Author name(s) for gap-filling searches

3. **Fetch all books from series page:**
   ```javascript
   async function fetchSeriesBooks(seriesAsin) {
       const url = `https://www.amazon.com/kindle-dbs/productPage/ajax/seriesAsinList?asin=${seriesAsin}&pageNumber=1&pageSize=200&binding=kindle_edition`;
       const response = await fetch(url, {
           headers: {
               "accept": "text/html,*/*",
               "x-requested-with": "XMLHttpRequest"
           }
       });
       return response.text();
   }
   ```

4. **Parse HTML to book objects** (see parsing code above)

**Step 2: Gap Detection**

5. **Analyze series positions:**
   ```javascript
   function detectGaps(books) {
       const positions = books.map(b => b.seriesPosition).filter(Boolean);
       const maxPosition = Math.max(...positions);
       const missing = [];
       for (let i = 1; i <= maxPosition; i++) {
           if (!positions.includes(i)) missing.push(i);
       }
       return { maxPosition, found: positions.length, missing };
   }
   ```

6. **If gaps detected, show Gap Detection Dialog** (see UI mockups above)

**Step 3: Gap-Filling (if user opts in)**

7. **For each missing book number, search Amazon:**
   ```javascript
   async function searchForMissingBook(author, seriesName, bookNumber) {
       const query = encodeURIComponent(`${author} ${seriesName} #${bookNumber}`);
       const url = `https://www.amazon.com/s?k=${query}&i=digital-text`;
       // Fetch search results page, parse first Kindle result
   }
   ```

8. **Parse search results to extract ASIN:**
   - First result matching pattern is likely correct
   - Verify title contains book number

9. **Fetch product page data for each found ASIN:**
   - Reuse existing product page parsing (from Wishlist Fetcher)

10. **Show progress during gap-filling** (see UI mockups above)

**Step 4: Output**

11. **Merge all books (series page + gap-filled)**

12. **Filter out already-owned books:**
    - Compare ASINs against existing library (IndexedDB or localStorage)

13. **Generate final JSON:**
    ```javascript
    {
        books: [...],
        metadata: {
            source: 'series-import',
            seriesAsin: 'B0D775V4W9',
            seriesName: 'The Destroyer',
            importDate: '2026-01-10T...',
            totalInSeries: 155,
            fromSeriesPage: 106,
            fromGapFill: 47,
            notFound: [107, 142],
            gapFillUsed: true
        }
    }
    ```

14. **Final Summary Dialog** (see UI mockups above)

15. **Download JSON or merge directly**

### Phase 2: Integration with Navigator

Add "Import Series" option to Navigator bookmarklet when on a series page.

### Phase 3: Organizer Support

1. **Display series metadata** in import summary
2. **Show gap-fill results** if applicable
3. **Filter by source** to show series-imported books

## User Flow

### Basic Flow (No Gaps)

1. Navigate to Amazon series page (e.g., https://www.amazon.com/dp/B0D775V4W9)
2. Click Navigator bookmarklet
3. Select "Import Series to Wishlist"
4. See progress: "Fetching series data..."
5. See summary: "Found 50 books. 12 already owned, 38 added to wishlist."
6. Download JSON or merge directly

### Flow with Gap Detection and Filling

1. Navigate to Amazon series page
2. Click Navigator bookmarklet → "Import Series to Wishlist"
3. Fetcher detects gaps in series
4. **Gap Detection Dialog:**
```
┌─────────────────────────────────────────────────────────────┐
│  📚 Series Import Complete                                   │
│                                                              │
│  The Destroyer (155 books)                                   │
│  ✓ 106 books found on series page                           │
│  ✗ 49 books missing from Amazon's series list (101-149)     │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Amazon's series page is incomplete. We can search for   ││
│  │ the missing books individually.                         ││
│  │                                                          ││
│  │ This will take ~2-3 minutes for 49 books.               ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  [Skip - Import 106 books only]  [Find Missing Books]        │
└─────────────────────────────────────────────────────────────┘
```

5. **If user clicks "Find Missing Books":**
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Searching for missing books...                          │
│                                                              │
│  Searching: "warren murphy the destroyer #103"               │
│  Progress: 12 of 49                                          │
│  Found: 11  |  Not Found: 1                                  │
│                                                              │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  24%              │
│                                                              │
│  [Cancel]                                                    │
└─────────────────────────────────────────────────────────────┘
```

6. **Final Summary:**
```
┌─────────────────────────────────────────────────────────────┐
│  ✅ Series Import Complete                                   │
│                                                              │
│  The Destroyer                                               │
│  • 106 from series page                                      │
│  • 47 found via search (2 not found as Kindle)              │
│  • 153 total added to wishlist                               │
│                                                              │
│  Books not found: #107, #142 (may not have Kindle editions) │
│                                                              │
│  [Download JSON]  [Close]                                    │
└─────────────────────────────────────────────────────────────┘
```

### UI Design Principles

1. **Acknowledge the problem clearly** - "Amazon's series page is incomplete" (blame Amazon, not us)
2. **Offer a solution immediately** - Don't make users figure it out themselves
3. **Set expectations** - "~2-3 minutes" so users know it's not instant
4. **Allow skip** - Some users just want what's easy; don't force the longer operation
5. **Show progress** - Long operations need visual feedback
6. **Report what couldn't be found** - Transparency builds trust; list specific book numbers

## Data Model

### Wishlist Book Entry (from series import)

```typescript
interface SeriesImportedBook {
    asin: string;
    title: string;
    authors: string[];
    coverUrl: string;
    rating: number | null;
    reviewCount: number;
    seriesPosition: number | null;
    kindlePrice: string | null;  // e.g., "$6.99"
    description: string;
    isOwned: false;
    source: 'series-import';
    seriesAsin: string;
    seriesName: string;
    importDate: string;
}
```

## Edge Cases

1. **User not logged in:** API may return different data or error
2. **Series with no Kindle editions:** Empty response
3. **Series with mixed formats:** Only Kindle editions returned (binding=kindle_edition)
4. **Duplicate ASINs:** Some books may appear multiple times (omnibus editions)
5. **Price changes:** Kindle price is snapshot at import time (relates to P1 T6 Price Tracking)

## Related Features

- **P1 T6: Wishlist Price Tracking** - After series import, user wants to track prices
- **P3 T5: Series Gap Detection** - Enhanced version could auto-detect missing books across all owned series

## Files to Create/Modify

| File | Changes |
|------|---------|
| `series-page-fetcher.js` | New bookmarklet script |
| `bookmarklet-nav-hub.js` | Add "Import Series" option |
| `readerwrangler.js` | Handle series import JSON format |
| `docs/design/SERIES-PAGE-BULK-IMPORT.md` | This document |
| `TODO.md` | Update with implementation task |

## Test Series

**The Destroyer series (155 books):**
- URL: https://www.amazon.com/dp/B0D775V4W9?binding=kindle_edition
- Known gap: Books 101-149 missing from Kindle catalog
- Good stress test for large series

---

## Appendix: Raw API Captures

Captured from Chrome DevTools Network tab on 2026-01-10.

### Series List Request

```javascript
fetch("https://www.amazon.com/kindle-dbs/productPage/ajax/seriesAsinList?asin=B0D775V4W9&pageNumber=1&pageSize=200&binding=kindle_edition", {
  "headers": {
    "accept": "text/html,*/*",
    "x-requested-with": "XMLHttpRequest"
  }
}).then(r => r.text()).then(html => {
  const count = (html.match(/series-childAsin-item/g) || []).length;
  console.log(`Found ${count} books`);
});
```

### Sample Book HTML Structure

```html
<div id="series-childAsin-item_1" class="a-section a-spacing-none a-padding-none series-childAsin-item">
    <div class="a-fixed-left-grid a-spacing-medium">
        <div class="a-fixed-left-grid-inner" style="padding-left:170px">
            <div class="a-fixed-left-grid-col series-num-book-col a-col-left">
                <div class="a-row">
                    <a class="a-size-base-plus a-link-normal itemImageLink"
                       title="Created, The Destroyer"
                       href="/gp/product/B0CHRKTWWL?ref_=dbs_m_mng_rwt_calw_tkin_0&storeType=ebooks">
                        <img alt="Created, The Destroyer"
                             src="https://m.media-amazon.com/images/I/51ZcbS9-4lL._SY300_.jpg"
                             class="a-dynamic-image asinImage"/>
                    </a>
                </div>
            </div>
            <div class="a-fixed-left-grid-col a-col-right">
                <div class="a-section a-spacing-micro series-childAsin-count">
                    <span aria-label="Book 1" class="a-size-large a-color-secondary itemPositionLabel a-text-bold">
                        1
                    </span>
                </div>
                <div class="a-section a-spacing-micro">
                    <a class="a-size-medium a-link-normal itemBookTitle" href="/gp/product/B0CHRKTWWL">
                        <h3 class="a-text-normal">Created, The Destroyer</h3>
                    </a>
                </div>
                <div class="a-section a-spacing-micro">
                    <span class="series-childAsin-item-details-by-line">by</span>
                    <a class="a-link-normal series-childAsin-item-details-contributor" href="/Warren-Murphy/e/B000APEJD4">
                        Warren Murphy (Author),
                    </a>
                    <a class="a-link-normal series-childAsin-item-details-contributor" href="/Richard-Sapir/e/B001IOBP5Q">
                        Richard Sapir (Author)
                    </a>
                </div>
                <div class="a-section a-spacing-none">
                    <span class="a-size-base">4.3</span>
                    <a class="a-size-base a-link-normal" href="/product-reviews/B0CHRKTWWL">
                        <i class="a-icon a-icon-star-small a-star-small-4-5">
                            <span class="a-icon-alt">4.3 out of 5 stars</span>
                        </i>
                        <span aria-label="2218 ratings" class="a-size-base">2,218</span>
                    </a>
                </div>
                <div class="a-section a-spacing-none a-padding-none collectionDescription">
                    <span>Sentenced to death for a crime he didn't commit...</span>
                </div>
                <div class="a-section a-spacing-none">
                    <ul class="a-unordered-list formatTwisterList">
                        <li class="formatTwister otherFormatTwister">
                            <a class="a-size-base a-link-normal" href="/gp/product/B0CHRKTWWL?storeType=ebooks">
                                Kindle
                            </a>
                            <span class="a-size-base a-color-base a-text-bold">$6.99</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Pagination Test Results

| Page | pageNumber | Expected Books | Actual Books | Notes |
|------|------------|----------------|--------------|-------|
| 1 | 1 | 1-20 | 1-20 | OK |
| 2 | 2 | 21-40 | 21-40 | OK |
| 3 | 3 | 41-60 | 41-60 | OK |
| 4 | 4 | 61-80 | 61-80 | OK |
| 5 | 5 | 81-100 | 81-100 | OK |
| 6 | 6 | 101-120 | **150-155** | Gap! |

**Single request with pageSize=200:** Returns 106 books (1-100, 150-155). Same gap.

**Conclusion:** Gap is in Amazon's database, not pagination logic.
