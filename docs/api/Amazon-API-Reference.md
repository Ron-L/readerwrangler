# Amazon API Reference

Reference documentation for Amazon APIs used by ReaderWrangler fetcher scripts.

## Overview

ReaderWrangler uses two Amazon API endpoints:

| API | Endpoint | Format | Purpose |
|-----|----------|--------|---------|
| Kindle Reader API | `/kindle-reader-api` | GraphQL | Library titles, enrichment (descriptions, reviews) |
| Digital Console API | `/hz/mycd/digital-console/ajax` | Form-urlencoded | Collections, read status |

---

## 1. Kindle Reader API (GraphQL)

**Endpoint:** `https://www.amazon.com/kindle-reader-api`

**Method:** POST

**Headers:**
```
accept: application/json, text/plain, */*
content-type: application/json
anti-csrftoken-a2z: <csrf-token>
x-client-id: your-books
```

**Authentication:** CSRF token from `<meta name="anti-csrftoken-a2z">` tag

### 1.1 getCustomerLibrary

Fetches library book titles with pagination.

**Our Usage:** Library fetcher Pass 1 (titles)
**Amazon UI Usage:** Your Books page (`/yourbooks`)

**Query:**
```graphql
query ccGetCustomerLibraryBooks {
    getCustomerLibrary {
        books(
            after: "<cursor>",
            first: 30,
            sortBy: {sortField: ACQUISITION_DATE, sortOrder: DESCENDING},
            selectionCriteria: {tags: [], query: "NOT (222711ade9d0f22714af93d1c8afec60 OR 858f501de8e2d7ece33f768936463ac8)"},
            groupBySeries: false
        ) {
            pageInfo {
                hasNextPage
                endCursor
            }
            totalCount {
                number
                relation
            }
            edges {
                node {
                    asin
                    relationshipType
                    relationshipSubType
                    relationshipCreationDate
                    product {
                        asin
                        title { displayString }
                        images {
                            images {
                                hiRes { physicalId, extension }
                                lowRes { physicalId, extension }
                            }
                        }
                        customerReviewsSummary {
                            count { displayString }
                            rating { fullStarCount, hasHalfStar, value }
                        }
                        byLine {
                            contributors {
                                name
                                contributor {
                                    author {
                                        profile {
                                            displayName
                                            contributorPage { url }
                                        }
                                    }
                                }
                            }
                        }
                        bindingInformation {
                            binding { displayString, symbol }
                        }
                        bookSeries {
                            singleBookView {
                                series { title, position, link { url } }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `pageInfo.hasNextPage` | boolean | More pages available |
| `pageInfo.endCursor` | string | Cursor for next page |
| `totalCount.number` | int | Total books in library |
| `edges[].node.asin` | string | Book ASIN |
| `edges[].node.relationshipCreationDate` | timestamp | Acquisition date (epoch ms) |
| `edges[].node.product.title.displayString` | string | Book title |
| `edges[].node.product.byLine.contributors[].name` | string | Author name |
| `edges[].node.product.images.images[0].hiRes` | object | High-res cover image |
| `edges[].node.product.customerReviewsSummary.rating.value` | float | Average rating (e.g., 4.5) |
| `edges[].node.product.bookSeries.singleBookView.series` | object | Series info (title, position) |
| `edges[].node.product.bindingInformation.binding.displayString` | string | Format (e.g., "Kindle Edition") |

**Pagination:**
- First page: `after: ""`
- Subsequent pages: `after: "<endCursor from previous response>"`
- Page size: `first: 30` (our default)

---

### 1.2 getProducts (Enrichment)

Fetches detailed book information including descriptions and reviews.

**Our Usage:** Library fetcher Pass 2 (enrichment) - currently ONE ASIN per call
**Amazon UI Usage:** Quick View dialog, product detail page

**Query:**
```graphql
query enrichBook {
    getProducts(input: [{asin: "<ASIN>"}]) {
        asin
        title { displayString }
        byLine {
            contributors {
                name
                contributor {
                    author {
                        profile { displayName }
                    }
                }
            }
        }
        images {
            images {
                hiRes { physicalId, extension }
                lowRes { physicalId, extension }
            }
        }
        customerReviewsSummary {
            count { displayString }
            rating { value }
        }
        bookSeries {
            singleBookView {
                series { title, position }
            }
        }
        bindingInformation {
            binding { displayString }
        }
        description {
            sections(filter: {types: PRODUCT_DESCRIPTION}) {
                content
            }
        }
        auxiliaryStoreRecommendations(recommendationTypes: ["AI_SUMMARIES"]) {
            recommendations {
                recommendationType
                sharedContent {
                    contentAbstract { textAbstract }
                }
            }
        }
        customerReviewsTop {
            reviews {
                contentAbstract { textAbstract }
                contributor {
                    publicProfile {
                        publicProfile {
                            publicName { displayString }
                        }
                    }
                }
                title
                stars
            }
        }
        overview {
            sectionGroups {
                name { id }
                sections {
                    attributes {
                        label { id }
                        granularizedValue {
                            displayContent
                        }
                    }
                }
            }
        }
    }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asin` | string | Book ASIN |
| `description.sections[0].content` | string/object | Product description (may be nested fragments) |
| `auxiliaryStoreRecommendations.recommendations[]` | array | AI summaries (if available) |
| `customerReviewsTop.reviews[]` | array | Top customer reviews |
| `customerReviewsTop.reviews[].stars` | int | Review star rating (1-5) |
| `customerReviewsTop.reviews[].title` | string | Review title |
| `customerReviewsTop.reviews[].contentAbstract.textAbstract` | string | Review text |
| `overview.sectionGroups[]` | array | Product detail sections (TechSpec, DetailBullets, RichProductInfo) |
| `overview.sectionGroups[].sections[].attributes[]` | array | Key-value attributes including publication date |

**Description Content Extraction:**

The `description.sections[0].content` field has multiple possible structures:

1. **Simple string:** `"Description text"`
2. **Object with text:** `{text: "Description text"}`
3. **Object with paragraph:** `{paragraph: {text: "Description text"}}`
4. **Object with fragments:** `{fragments: [{text: "Part 1"}, {text: "Part 2"}]}`
5. **Nested fragments:** `{paragraph: {fragments: [{semanticContent: {content: {text: "..."}}}]}}`

Our fetcher uses a recursive `extractTextFromFragments()` function to handle all cases.

**Publication Date Extraction:**

The publication date is found in the `overview.sectionGroups` field:

- **Label ID:** `book_details-publication_date`
- **Path:** `overview.sectionGroups[*].sections[*].attributes[*]` where `label.id === "book_details-publication_date"`
- **Value:** `granularizedValue.displayContent` (raw Object type)
- **Format:** Human-readable (e.g., "August 26, 2014") - parsed to ISO format ("2014-08-26")

The date appears in 3 section groups (TechSpec, DetailBullets, RichProductInfo) - we use the first match.

Note: `displayContent` is a GraphQL leaf type (Object!) and cannot have subselections. The raw object is returned and parsed client-side.

**Batching Potential:**

The `input` parameter accepts an array: `[{asin: "A"}, {asin: "B"}, ...]`

**Current:** 1 ASIN per call = 2000 calls for 2000 books (~2 hours)
**Potential:** 30 ASINs per call = 67 calls for 2000 books (~4 minutes)

⚠️ **Needs testing** - see `diag-03-batch-enrichment.js`

---

### 1.3 getProduct (Singular - Amazon UI Only)

Amazon's Quick View dialog uses `getProduct` (singular) for single-book enrichment.

**Endpoint:** Same `/kindle-reader-api`

**Differences from getProducts:**
- Input: `{asin: "..."}` (object) vs `[{asin: "..."}]` (array)
- Response: Direct product object vs array of products

**Our Usage:** Not currently used - we use `getProducts` (plural)

---

## 2. Digital Console API (Form-urlencoded)

**Endpoint:** `https://www.amazon.com/hz/mycd/digital-console/ajax`

**Method:** POST

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
Accept: application/json, text/plain, */*
```

**Authentication:** CSRF token from `window.csrfToken`

### 2.1 GetContentOwnershipData

Fetches book ownership data including collections and read status.

**Our Usage:** Collections fetcher
**Amazon UI Usage:** "Manage Your Content and Devices" page

**Request Body (form-urlencoded):**
```
activity=GetContentOwnershipData
activityInput=<JSON string>
clientId=MYCD_WebService
csrfToken=<token>
```

**activityInput JSON:**
```json
{
    "contentType": "Ebook",
    "contentCategoryReference": "booksAll",
    "itemStatusList": ["Active", "Expired"],
    "excludeExpiredItemsFor": [
        "KOLL", "Purchase", "Pottermore", "FreeTrial",
        "DeviceRegistration", "KindleUnlimited", "Sample",
        "Prime", "ComicsUnlimited", "Comixology"
    ],
    "originTypes": [
        "Purchase", "PublicLibraryLending", "PersonalLending",
        "Sample", "ComicsUnlimited", "KOLL", "RFFLending",
        "Pottermore", "Prime", "Rental", "DeviceRegistration",
        "FreeTrial", "KindleUnlimited", "Comixology"
    ],
    "showSharedContent": true,
    "fetchCriteria": {
        "sortOrder": "DESCENDING",
        "sortIndex": "DATE",
        "startIndex": 0,
        "batchSize": 25,
        "totalContentCount": -1
    },
    "surfaceType": "Tablet"
}
```

**Response Structure:**
```json
{
    "GetContentOwnershipData": {
        "numberOfItems": 2000,
        "items": [
            {
                "asin": "B00ABC123",
                "title": "Book Title",
                "readStatus": "READ",
                "collectionList": [
                    {
                        "collectionId": "abc123",
                        "collectionName": "Favorites"
                    }
                ]
            }
        ]
    }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `numberOfItems` | int | Total books in library |
| `items[].asin` | string | Book ASIN |
| `items[].title` | string | Book title |
| `items[].readStatus` | string | "READ", "UNREAD", or "UNKNOWN" |
| `items[].collectionList[]` | array | Collections containing this book |
| `items[].collectionList[].collectionId` | string | Collection ID |
| `items[].collectionList[].collectionName` | string | Collection name |

**Pagination:**
- Uses `startIndex` (0-based) instead of cursor
- Page size: `batchSize: 25` (our default)
- Stop when: `items.length === 0` or `items.length >= numberOfItems`

---

## Rate Limiting

### Current Settings

| API | Delay | Reason |
|-----|-------|--------|
| Library pages (`getCustomerLibrary`) | 2000ms | Conservative initial setting |
| Enrichment (`getProducts`) | 3000ms | Conservative initial setting |
| Collections (`GetContentOwnershipData`) | 2000ms | Conservative initial setting |

### Observed Behavior

- No 429 errors observed at current delays
- Rate limiting appears to be HTTP-level, not API-specific
- Same rate limit likely applies to both endpoints on same domain

### Potential Optimization

1. **Reduce delays** - Binary search to find minimum safe delay
2. **Batch enrichment** - Multiple ASINs per `getProducts` call
3. **Adaptive rate limiting** - Slow down 15% on 429, track statistics

See diagnostic scripts:
- `diag-01-rate-limit-graphql.js` - Test GraphQL endpoint rate limits
- `diag-02-rate-limit-collections.js` - Test Collections endpoint rate limits
- `diag-03-batch-enrichment.js` - Test multi-ASIN batching

---

## Error Handling

### HTTP Errors

| Code | Meaning | Action |
|------|---------|--------|
| 401/403 | Session expired | Prompt user to refresh page |
| 429 | Rate limited | Exponential backoff |
| 500+ | Server error | Retry with backoff |

### GraphQL Errors

GraphQL may return HTTP 200 with `errors` array:

```json
{
    "errors": [{"message": "Error message", "path": ["getProducts", 0]}],
    "data": {"getProducts": [...]}
}
```

**Partial errors:** May have errors AND data - extract what we can.

### Our Retry Strategy

```javascript
const MAX_RETRIES = 3;
const RETRY_DELAYS_MS = [5000, 10000, 20000]; // Exponential backoff
```

On failure after all retries: Try once more with fresh CSRF token.

---

## Version History

| Date | Change |
|------|--------|
| 2026-01-04 | Added `overview` field for publication date extraction |
| 2024-12-11 | Initial documentation from code analysis |
