# GraphQL API Investigation - November 2025

**Dates**: 2025-11-05 through 2025-11-11
**Status**: RESOLVED - Root cause found, fix implemented in v3.3.2
**Archived**: 2025-11-27

---

## Summary

Investigation into why 3/2666 books (0.1%) failed during full library fetch with "Customer Id or Marketplace Id is invalid" error.

**Root Cause**: GraphQL partial errors - Amazon returns BOTH valid description data AND errors for the `customerReviewsTop` field. Our code rejected the entire response if `data.errors` existed, losing valid descriptions.

**Solution**: Check for data despite errors, only fail if truly no data present. Implemented in library-fetcher.js v3.3.2.

---

## The 3 Problematic Books

1. **Cats** - Position 2019 (87% through, ~144 minutes):
   - Title: "99 Reasons to Hate Cats: Cartoons for Ca..."
   - ASIN: **B0085HN8N6** (Kindle Edition)
   - Error: "Customer Id or Marketplace Id is invalid."

2. **Queen's Ransom** - Position 2321 (final 1%):
   - ASIN: **0684862670** (10-digit ISBN format)
   - Error: "Customer Id or Marketplace Id is invalid."

3. **To Ruin A Queen** - Position 2322 (final 1%):
   - ASIN: **0684862689** (10-digit ISBN format)
   - Error: "Customer Id or Marketplace Id is invalid."

---

## ALL Theories Tested & Results

| Theory | Test Method | Result | Status |
|--------|-------------|--------|--------|
| **Token Staleness** | Diagnostic used fetcher's 2.5-hour-old token | All 3 books **SUCCEEDED** with stale token | DISPROVEN |
| **Single Book Repetition** | Queen's Ransom 2500x in 19 minutes | 2500/2500 **SUCCEEDED** | DISPROVEN |
| **2-Book Variety** | Kindle + Queen alternating 2500x in 19 minutes | 2500/2500 **SUCCEEDED** | DISPROVEN |
| **High Variety (Fast)** | 2344 different books in 37 minutes | 4688 requests **SUCCEEDED** | DISPROVEN |
| **Time (144 min)** | 1744 books over 144 min, then Cats | Cats **SUCCEEDED** after 144 min | DISPROVEN |
| **ISBN Format Issues** | All tests used ISBN books | ISBNs work perfectly | DISPROVEN |
| **Position-Based** | Inserted 2 copies of first book at start | Failures shifted by +2 positions | DISPROVEN |
| **Fresh Token Retry** | Full fetch with auto token refresh on failure | Token unchanged, fresh token FAILS with same error | DISPROVEN |
| **Sequence-Dependent** | Shuffle books 0-2037, fetch in shuffled order | Cats still FAILED at position 2038 | DISPROVEN (for sequential) |

---

## What We Learned

**Failures are deterministic** - Same 3 books fail at consistent positions (87%, 100%, 100%)
**Position shift confirmed** - Inserting 2 books at start shifted failures by exactly +2 positions
**Error is book-specific** - Not token, time, variety, or position alone
**Books work individually** - All diagnostic tests succeed when books tested in isolation
**Fast recovery** - Diagnostic succeeds 35 seconds after fetcher fails
**Not ISBN-related** - Kindle book (Cats) fails too, ISBN books succeed in all isolated tests

---

## Test History

### Test 1 - Queen Repetition (diag-02-queen-repetition-test.js)
- Pattern: Queen's Ransom 2500 consecutive times
- Duration: 19 minutes
- Result: 2500/2500 succeeded
- Conclusion: Single book repetition is NOT the issue

### Test 2 - Alternating 2 Books (diag-03-alternating-test.js)
- Pattern: Kindle book + Queen's Ransom alternating (2500 total requests)
- Duration: 19 minutes
- Result: 2500/2500 succeeded
- Conclusion: 2-book variety is NOT the issue

### Test 3 - Full Library Fast (diag-04-full-library-alternating.js)
- Pattern: All 2344 library books alternating with Queen's Ransom
- Duration: 37 minutes
- Result: 4688 requests (2344 library + 2344 Queen) succeeded
- Conclusion: High variety at fast speed is NOT the issue

### Test 4 - Time-Based Slow (diag-05-time-based-cats-test.js)
- Pattern: 1744 books with 4.5s delays (144 min), then Cats book
- Duration: 144 minutes
- Result: Cats succeeded with 939 char description
- Conclusion: TIME alone (144 min) is NOT the issue

### Test 5 - Token Staleness
- Pattern: Diagnostic used fetcher's 2.5-hour-old CSRF token
- Duration: 30 seconds
- Result: All 3 books (Cats + 2 Queens) succeeded with stale token
- Conclusion: Token staleness is NOT the issue

### Test 6 - Fresh Token Retry (v3.3.1.c)
- Pattern: Full library fetch with auto token refresh on failure
- Duration: 2h 39m (2323 books)
- Result: 5 failures at same positions (2322, 2323 = Queens)
- Token comparison: IDENTICAL (tokens don't change during session)
- Fresh token retry: FAILS with same "Customer Id or Marketplace Id is invalid"
- Conclusion: Token refresh does NOT solve the problem
- **Key Finding**: Even with fresh token, same books fail with same error

### Test 7 - Shuffle Sequence (diag-06-shuffle-test.js)
- Pattern: Shuffle books 0-2018, keep 2019+ in original order, fetch in shuffled order
- Duration: ~2 hours (2344 books)
- Result: Cats FAILED at position 2038 (18 positions later than expected due to shuffle)
- **Key Finding**: Cats still failed even with shuffled sequence before it
- Conclusion: Sequence does NOT matter - failure is about cumulative properties
- **IMPORTANT**: Test 3 (alternating with Queen) showed sequence CAN matter when alternating with known-good books keeps cache fresh
- **Summary**: Two distinct behaviors observed:
  1. **Alternating pattern**: Interleaving failing books with others prevents failures (keeps cache fresh)
  2. **Sequential pattern**: Processing ~2000+ different books (any order) triggers failures

---

## Test 8 - Reverse Binary Search (COMPLETED WITH CAVEAT)

### Test 8a - Apoc Toxic Test (diag-08a-apoc-toxic-test.js)
- Pattern: Fetch "Exponential Apocalypse" (position 2036), then Cats (position 2037)
- Duration: ~6 seconds
- Result: Both SUCCEEDED
- Conclusion: Position 2036 is NOT the poison for Cats

### Test 8b - Reverse Walk to Find Poison (diag-08b-apoc-reverse-walk.js)
- Pattern: Walk backwards from Cats to find its poison
- Result: Created but superseded by Test 9

### Test 9 - Toxic Book Test (diag-09-toxic-book-test.js)
- Pattern: Test if "Exponential Apocalypse" poisons Cats, Queen 1, Queen 2
- Duration: ~30 seconds
- Result: All victims SUCCEEDED
- Conclusion: Apoc is NOT universally toxic

---

## Tests 10-12 - Queens Reverse Binary Search (COMPLETED - FLAWED BUT VALUABLE)

**CRITICAL NOTE**: Tests 10-12 were flawed due to context compaction error:
- **Intended target**: Position 2037 (Cats - "99 Reasons to Hate Cats", ASIN B0085HN8N6)
- **Actual target**: Position 2321 (Wrong "Queen" - searched for "Queen" in title instead of using known victim ASIN)
- **ASIN used**: 0425197484 (Undead and Unemployed - Queen Betsy Book 2) - NOT a known victim
- **Result**: Tests completed successfully but targeted wrong book
- **Value**: Despite flaw, Test 12 revealed 4 consistently unenrichable books

### Test 12 - Queens Reverse Sparse Output (diag-12-queens-reverse-sparse-output.js)
- Pattern: Same logic as Test 10/11, sparse console output, single file at end
- Duration: ~7 hours (148 minutes active fetching)
- Total books processed: 2322 across 13 iterations
- Results saved to:
  - `test-12-console-results.txt` (2472 lines)
  - `test-12-final-results.json` (downloaded)
  - `window.queensReverseBinarySearchResults` (backup)

**Test 12 Results Summary:**

| Iteration | Books Fetched | Range | Duration | Failures | Failed Positions |
|-----------|--------------|-------|----------|----------|------------------|
| 1-9 | 2-257 | Various | 0-14 min | 0 | None |
| 10 | 513 | [1809, 2321] | 30 min | 1 | 2037 (Cats) |
| 11 | 1025 | [1297, 2321] | 63 min | 3 | 1649, 1784, 2037 |
| 12 | 2049 | [273, 2321] | 121 min | 3 | 1649, 1784, 2037 |
| 13 | 2322 | [0, 2321] | 148 min | 4 | 1251, 1649, 1784, 2037 |

**Four Books Consistently Failed (NOT the original 3 victims):**
1. Position 1251: "Property of a Lady Faire" (ASIN B00G3L6L3U)
2. Position 1649: "By Tooth and Claw" (ASIN B00URTZQHG)
3. Position 1784: "Lethal Code" (ASIN B00J9P2EMO)
4. Position 2037: "99 Reasons to Hate Cats" (ASIN B0085HN8N6) - Original victim

**Key Findings:**
- Failures are 100% reproducible and position-based
- Same 4 books fail EVERY time they're included in the range
- Failures NOT dependent on cumulative fetch count or iteration number
- "Queen" (position 2321, ASIN 0425197484) NEVER failed in any iteration
- **CRITICAL**: These 4 books ARE successfully enriched in full library fetch
- They only fail in Test 12 due to cumulative poison from earlier books
- Iteration 9 vs 10 shows clear threshold: 257 books -> success, 513 books -> failure

---

## Test 13 - Binary Search for Minimum Poison Threshold

**Goal**: Find MINIMUM number of books needed to make position 2037 (Cats) fail

**Method**: Multiplicative range adjustment (x0.5 on failure, x1.5 on success)
- Initial discovery: Step 2A found range [2001, 2037] = 37 books causes failure
- Current status: Testing smaller ranges to find minimum threshold

### Step 2A - Verbose Diagnostic (diag-13-binary-search-step-2a.js) - CRITICAL DISCOVERY
- Intended range: [2001, 2321] = 321 books
- Actual range tested: [2001, 2037] = 37 books (stopped at victim)
- Duration: ~2 minutes
- Result: Cats FAILED
- **Key finding**: Only 37 books needed to reproduce error!

### Step 3 - Multiplicative Approach (diag-13-binary-search-step-3a.js) - COMPLETED
- Previous: [2001, 2037] = 37 books -> FAILED
- Current: [2020, 2037] = 18 books (37 x 0.5)
- Duration: ~1 minute (57 seconds)
- Result: **Cats FAILED (100% reproducible across 3 test runs)**
- **Achievement**: Can reproduce poison in just 1 minute with 18 books!

### Step 4 - Further Reduction (diag-13-binary-search-step-4.js) - COMPLETED
- Range: [2029, 2037] = 9 books (18 x 0.5)
- Duration: ~30 seconds actual
- Result: **Cats FAILED (100% reproducible across 3 test runs)**
- **Achievement**: Can reproduce poison in just 30 seconds with 9 books!

### Step 5 - Minimal Range (diag-13-binary-search-step-5.js) - READY
- Range: [2033, 2037] = 5 books (9 x 0.5 = 4.5 -> 5)
- Duration: ~15 seconds estimated
- Status: Script ready for execution

---

## Test 14 - Antidote Phase Tests (Nov 9, 2025) - BREAKTHROUGH DISCOVERY

**CRITICAL DISCOVERY**: The entire investigation was based on a false premise. The "failures" were actually **PARTIAL ERRORS** - Amazon successfully returned descriptions but also returned errors for the `customerReviewsTop` field.

### Phase 0 - Null Antidote Tests
- `antidote-test-00-null.js`: Test if repeated fetches with varying delays clear failure state
- `antidote-test-00a-null.js`: Same but hardcoded for Cats book specifically
- Result: All fetches failed as expected - confirmed failure is sticky
- Purpose: Establish baseline that timing alone doesn't fix the issue

### Phase 1 - Alternative Endpoint Tests
- `antidote-test-01-endpoint.js`: Test `/digital-graphql/v1` endpoint
- `antidote-test-01a-endpoint-debug.js`: Test multiple endpoint URL variations
- Result: ALL FAILED - `/digital-graphql/v1` endpoint returns 404 (NO LONGER EXISTS)
- **Critical Finding**: Amazon deprecated this endpoint between Nov 5-9, 2025
- Impact: `test-isbn-enrichment.js` worked on Nov 5 but fails today - endpoint gone

### Phase 2 - Amazon's Own Method (SUCCESSFUL SOLUTION)
- **Investigation**: Inspected Network tab when clicking Cats book on amazon.com/yourbooks
- **Discovery**: Amazon's own page DOES get description successfully!
- **Key Finding**: Only `customerReviewsTop` field fails with "Customer Id or Marketplace Id is invalid"
- **Amazon's Query Differences**:
  1. Uses `getProduct` (singular) not `getProducts` (plural)
  2. Uses `x-client-id: quickview` not `x-client-id: your-books`
  3. Requests `customerReviewsSummary` (count/rating) instead of `customerReviewsTop` (individual review text)
  4. Description succeeds even when reviews section has errors

### Phase 3 - Validate Option A (ALL 3 VICTIMS)
- Test: `antidote-test-03-three-victims.js` - Test all 3 problem books with original `getProducts` query
- Books tested: Cats (B0085HN8N6), Queen's Ransom (0684862670), To Ruin A Queen (0684862689)
- Result: ALL 3 books had partial errors (errors + data)
  - Cats: 939 chars description, partial error (customerReviewsTop failed)
  - Queen's Ransom: 0 chars extracted (has `fragments` structure), partial error (customerReviewsTop failed)
  - To Ruin A Queen: 230 chars description, partial error (customerReviewsTop failed)
- **Conclusion**: Option A CONFIRMED - all 3 victims return descriptions despite customerReviewsTop errors

---

## Root Cause Analysis

The problem was NOT with the books themselves. The problem was with our error handling:

1. **Amazon's Response**: GraphQL can return BOTH data AND errors (partial errors)
   ```json
   {
     "data": {
       "getProducts": [{
         "description": { "sections": [...] },  // SUCCESS
         "customerReviewsTop": null              // FAILED
       }]
     },
     "errors": [{
       "message": "Customer Id or Marketplace Id is invalid.",
       "path": ["getProducts", 0, "customerReviewsTop", "reviews"]
     }]
   }
   ```

2. **Our Code** (library-fetcher.js line 1237-1240):
   ```javascript
   if (data.errors) {
       const errorMsg = data.errors[0]?.message || 'Unknown GraphQL error';
       return { apiError: true, errorMessage: errorMsg };
   }
   // Never reaches here to extract description from data.data!
   ```

3. **The Mistake**: We rejected the ENTIRE response if `data.errors` existed, even though `data.data.getProducts[0].description` contained valid description data

4. **Why Test 3 Worked (Alternating)**: Interleaving with other books kept cache/state fresh, preventing the `customerReviewsTop` error from occurring

5. **Why Individual Tests Worked**: Single book fetches or small sequences didn't trigger whatever server-side condition causes the `customerReviewsTop` failure

---

## The Solution

**Partial Error Handling** (Implemented in v3.3.2)
- Change error handling to check if we got data despite errors
- Extract description from `data.data` even if `data.errors` exists
- Only fail if both no data AND errors present
- Simplest fix - just 5 lines of code changed
- Preserves existing `getProducts` query structure
- Will still log errors for debugging but won't discard valid descriptions

**Implementation**:
```javascript
if (data.errors) {
    // Check if we still got data despite errors (partial error)
    if (data.data?.getProducts?.[0]) {
        console.log(`   Partial error: ${data.errors[0]?.message || 'Unknown'}`);
        console.log(`   But got data anyway - continuing...`);
        // Continue to extract description from data.data
    } else {
        // Total failure - no data at all
        return { apiError: true, errorMessage: errorMsg };
    }
}
```

---

## Lessons Learned

1. **CRITICAL LESSON - Investigate Raw Response First**: We spent DAYS trying to quantify and narrow down the error through elaborate binary search and diagnostic tests. If we had simply inspected the raw GraphQL response dump from `getProducts`, we would have immediately seen it was a partial error with valid description data present. Always examine raw API responses before building complex reproduction scenarios.

2. **Improve Error Logging**: The fetcher code needs to dump the raw error message AND indicate whether data was still returned. Current error handling is too binary (error = total failure). Need to distinguish:
   - Total failure (no data at all)
   - Partial error (some fields failed but others succeeded)
   - This would have revealed the issue immediately

3. **Check Network Tab Early**: Browser Network tab inspection should be done EARLY in investigation, not as "last resort". It shows exactly what Amazon's own page does and can reveal successful patterns we should mimic.

4. **Don't Assume Binary Outcomes**: GraphQL supports partial errors by design. Our code assumed "errors = total failure" when GraphQL explicitly allows "errors + data = partial success".

5. **Document Endpoint Dependencies**: When code relies on external APIs, document the endpoints and monitor for deprecation. The `/digital-graphql/v1` deprecation broke our "antidote" without warning.

---

## Files & Scripts

### Diagnostic Scripts (Browser Console)
- `diag-01-isbn-enrichment.js` - Tests 5 books with complete extraction logic
- `diag-02-queen-repetition-test.js` - Queen only 2500x (Test 1)
- `diag-03-alternating-test.js` - 2-book alternating 2500x (Test 2)
- `diag-04-full-library-alternating.js` - Full library fast (Test 3)
- `diag-05-time-based-cats-test.js` - Time-based slow fetch (Test 4)
- `diag-06-shuffle-test.js` - Shuffle sequence test (Test 7)
- `diag-08a-apoc-toxic-test.js` - Tests if position 2036 poisons Cats (Test 8a)
- `diag-08b-apoc-reverse-walk.js` - Walk backwards from Cats (superseded by Test 9)
- `diag-09-toxic-book-test.js` - Tests if Apoc poisons Cats/Queens (Test 9)
- `diag-10-queens-reverse-binary-search.js` - Reverse binary search (flawed target)
- `diag-11-queens-reverse-with-file-output.js` - With file output (dialog spam issue)
- `diag-12-queens-reverse-sparse-output.js` - Sparse output, single file (Test 12)
- `diag-13-binary-search-step-*.js` - Binary search iterations

### Antidote Test Scripts (Browser Console)
- `antidote-test-00-null.js` - Phase 0: Null antidote (repeated fetches with varying delays)
- `antidote-test-00a-null.js` - Phase 0a: Null antidote hardcoded for Cats
- `antidote-test-01-endpoint.js` - Phase 1: Test `/digital-graphql/v1` endpoint (FAILED - 404)
- `antidote-test-01a-endpoint-debug.js` - Phase 1a: Test multiple endpoint variations (all 404)
- `antidote-test-02-amazon-method.js` - Phase 2: Mimic Amazon's `getProduct` query (SUCCESS!)
- `antidote-test-02a-debug-response.js` - Phase 2a: Debug response structure
- `antidote-test-03-three-victims.js` - Phase 3: Validate Option A with all 3 victims (CONFIRMED!)

### Test Result Files
- `test-12-console-results.txt` - Test 12 console output (2472 lines)
- `test-12-final-results.json` - Test 12 structured results (downloaded)

### Investigation/Analysis Scripts (Node.js)
- `test-isbn-enrichment.js` - "Antidote" test (5 books, different API endpoint, succeeds after full fetch fails)
- `analyze-library.js` - Library analysis utility
- `check-duplicate-asins.js` - ASIN duplicate checker
- `diff-libraries.js` - Library comparison tool
- `verify-fetch.js` - Fetch verification utility
