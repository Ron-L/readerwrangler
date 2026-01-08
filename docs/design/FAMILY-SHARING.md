# Family Sharing Feature Design

**Status:** Research Complete, Ready for Implementation
**Priority:** Low (nice-to-have)
**Estimated Effort:** 2-4 hours
**Date:** 2026-01-08

## Overview

Amazon Family Library allows household members to share purchased Kindle books. This feature adds the ability to:
1. Fetch which books the user has shared with family members
2. Display sharing info in the book detail modal
3. Optionally filter/badge shared books

## API Discovery

### API 1: GetKFTChildrenData (Household Members)

**Endpoint:** `https://www.amazon.com/hz/mycd/ajax`
**Method:** POST
**Content-Type:** `application/x-www-form-urlencoded`
**Auth:** `window.csrfToken` (same as collections fetcher)

**Request Body:**
```javascript
{
    clientId: 'MYCD_WebService',
    csrfToken: window.csrfToken,
    data: JSON.stringify({
        param: {
            GetKFTChildrenData: {}
        }
    })
}
```

**Response:**
```json
{
    "GetKFTChildrenData": {
        "householdId": "HH3469F44SUGP8O",
        "hasHouseholdId": true,
        "success": true,
        "isHouseholdEnabled": true,
        "householdMembers": [
            {
                "avatarUri": "https://images-na.ssl-images-amazon.com/...",
                "customerId": "A1FUA26SXTWGE9",
                "firstName": "Dana Lewis",
                "role": "ADULT"
            }
        ],
        "householdAgreements": [...]
    }
}
```

**Notes:**
- Call once per session (cacheable)
- Returns empty `householdMembers` array if user not in Family Library

### API 2: GetHouseholdDetails (Book Sharing Info)

**Endpoint:** `https://www.amazon.com/hz/mycd/digital-console/ajax`
**Method:** POST
**Content-Type:** `application/x-www-form-urlencoded`
**Auth:** `window.csrfToken` (same as collections fetcher)

**Request Body:**
```javascript
{
    activity: 'GetHouseholdDetails',
    activityInput: JSON.stringify({
        asins: ['B087DZX3PP', 'B08...', ...],  // Array of ASINs
        categoryList: ['KindleEBook'],
        getChildWhitelistedAsins: true,
        getHouseholdMemberDetails: true,
        surfaceType: 'LargeDesktop'
    }),
    clientId: 'MYCD_WebService',
    csrfToken: window.csrfToken
}
```

**Response:**
```json
{
    "success": true,
    "GetHouseholdDetails": {
        "householdId": "HH3469F44SUGP8O",
        "householdEnabled": true,
        "whitelistData": {
            "A1FUA26SXTWGE9": ["B087DZX3PP", "B08..."]
        },
        "success": true,
        "primeSharedAsinMap": {},
        "householdMemberData": {
            "A1FUA26SXTWGE9": {
                "role": "ADULT",
                "name": "Dana Lewis"
            }
        }
    }
}
```

**Key Fields:**
- `whitelistData`: Map of `customerId` → array of ASINs shared with that person
- `householdMemberData`: Map of `customerId` → name and role

## Batch Size Testing Results

| Batch Size | Response Time | Result |
|------------|---------------|--------|
| 10 | 141ms | ✅ Success |
| 25 | 162ms | ✅ Success |
| 50 | 225ms | ✅ Success |
| 100 | 226ms | ✅ Success |
| 200 | 198ms | ✅ Success |
| 500 | 198ms | ✅ Success |
| 1000 | 226ms | ✅ Success |

**Conclusion:** No practical batch size limit. Response time is nearly constant (~200ms) regardless of batch size. Amazon deduplicates server-side.

**Recommendation:** Fetch entire library in a single API call.

## Implementation Plan

### Phase 1: Data Collection (Collections Fetcher)

Add to `amazon-collections-fetcher.js`:

1. **Fetch household members** (1 API call)
   - Call `GetKFTChildrenData`
   - Store in memory for display
   - Skip remaining steps if no household members

2. **Fetch sharing info** (1 API call for entire library)
   - Call `GetHouseholdDetails` with all ASINs
   - Map response to book objects

3. **Store in JSON export:**
```javascript
{
    // Existing book fields...
    "sharedWith": ["Dana Lewis"]  // Array of names (empty if not shared)
}
```

4. **Store household metadata:**
```javascript
{
    "metadata": {
        // Existing fields...
        "household": {
            "id": "HH3469F44SUGP8O",
            "members": [
                { "id": "A1FUA26SXTWGE9", "name": "Dana Lewis", "role": "ADULT" }
            ]
        }
    }
}
```

### Phase 2: Display (Organizer)

1. **Book Detail Modal:**
   - Add "Shared with: Dana Lewis" line below ownership type
   - Only show if `sharedWith` array is non-empty

2. **Optional Future Enhancements:**
   - Filter by "Shared" status
   - Badge on book covers for shared books
   - Bulk share/unshare actions (requires additional API research)

## Data Model Changes

### Book Object
```typescript
interface Book {
    // Existing fields...
    sharedWith?: string[];  // Names of household members book is shared with
}
```

### Metadata Object
```typescript
interface Metadata {
    // Existing fields...
    household?: {
        id: string;
        members: Array<{
            id: string;
            name: string;
            role: 'ADULT' | 'CHILD';
        }>;
    };
}
```

## Edge Cases

1. **No Family Library:** `householdMembers` will be empty - skip sharing fetch
2. **Book shared with multiple people:** `sharedWith` array has multiple names
3. **Household member removed:** Their shared books may still show in `whitelistData`
4. **User is the recipient:** This API shows books *you* shared out, not books shared *to* you

## Test Script

See `test-sharing-api.js` in project root for standalone API testing.

## Files to Modify

| File | Changes |
|------|---------|
| `amazon-collections-fetcher.js` | Add sharing API calls |
| `readerwrangler.js` | Display `sharedWith` in modal |
| `docs/design/FAMILY-SHARING.md` | This document |
| `TODO.md` | Add implementation task |

## Open Questions

1. Should we show sharing info as a badge on book covers? (Probably not - too noisy)
2. Should we add a "Shared" filter? (Nice-to-have, low priority)
3. Can we programmatically share/unshare books? (Requires more API research)

---

## Appendix: Raw API Captures

Captured from Chrome DevTools Network tab on 2026-01-08.

**Page URL:** `https://www.amazon.com/hz/mycd/digital-console/contentlist/booksAll/dateDsc/`

### GetKFTChildrenData (Household Members)

**Request:**
```javascript
fetch("https://www.amazon.com/hz/mycd/ajax", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "body": "clientId=MYCD_WebService&csrfToken={CSRF_TOKEN}&data=%7B%22param%22%3A%7B%22GetKFTChildrenData%22%3A%7B%7D%7D%7D",
  "method": "POST",
  "credentials": "include"
});
```

**Response:**
```json
{
    "GetKFTChildrenData": {
        "householdId": "HH3469F44SUGP8O",
        "hasHouseholdId": true,
        "success": true,
        "isHouseholdEnabled": true,
        "householdMembers": [
            {
                "avatarUri": "https://images-na.ssl-images-amazon.com/images/G/01/gifts/kids-birthday/generic-avatar_85x85._V388026645_.png",
                "customerId": "A1FUA26SXTWGE9",
                "firstName": "Dana Lewis",
                "role": "ADULT"
            }
        ],
        "householdAgreements": [
            {
                "secondsSinceUpdated": "233857950",
                "agreementName": "WALLET"
            },
            {
                "secondsSinceUpdated": "233857950",
                "agreementName": "WARM_SEAT"
            },
            {
                "secondsSinceUpdated": "233857950",
                "agreementName": "CONTENT"
            },
            {
                "secondsSinceUpdated": "233857848",
                "agreementName": "DEEP_PI_CHECK"
            }
        ]
    }
}
```

### GetHouseholdDetails (Book Sharing Info)

**Request:**
```javascript
fetch("https://www.amazon.com/hz/mycd/digital-console/ajax", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "body": "activity=GetHouseholdDetails&activityInput=%7B%22asins%22%3A%5B%22B087DZX3PP%22%5D%2C%22categoryList%22%3A%5B%22KindleEBook%22%5D%2C%22getChildWhitelistedAsins%22%3Atrue%2C%22getHouseholdMemberDetails%22%3Atrue%2C%22surfaceType%22%3A%22LargeDesktop%22%7D&clientId=MYCD_WebService&csrfToken={CSRF_TOKEN}",
  "method": "POST",
  "credentials": "include"
});
```

**Decoded activityInput:**
```json
{
    "asins": ["B087DZX3PP"],
    "categoryList": ["KindleEBook"],
    "getChildWhitelistedAsins": true,
    "getHouseholdMemberDetails": true,
    "surfaceType": "LargeDesktop"
}
```

**Response:**
```json
{
    "success": true,
    "GetHouseholdDetails": {
        "householdId": "HH3469F44SUGP8O",
        "householdEnabled": true,
        "whitelistData": {
            "A1FUA26SXTWGE9": [
                "B087DZX3PP"
            ]
        },
        "success": true,
        "primeSharedAsinMap": {},
        "householdMemberData": {
            "A1FUA26SXTWGE9": {
                "role": "ADULT",
                "name": "Dana Lewis"
            }
        },
        "householdAgreements": null
    }
}
```

**Notes:**
- Cookie header omitted for security (contains session tokens)
- `csrfToken` available at `window.csrfToken` on the MYCD page
- Test ASIN `B087DZX3PP` = "A Contemporary Asshat at the Court of Henry VIII"

### Test Script (for reference)

Used to verify API batch limits. Run in browser console on MYCD page.

```javascript
// Test script for Family Sharing API
// Run this in browser console on: https://www.amazon.com/hz/mycd/digital-console/contentlist/booksAll/dateDsc/

async function testSharingAPI() {
    console.log('========================================');
    console.log('Family Sharing API Test');
    console.log('========================================\n');

    // Verify we're on the right page
    if (!window.location.href.includes('amazon.com/hz/mycd/digital-console')) {
        console.error('❌ Wrong page! Run this on: https://www.amazon.com/hz/mycd/digital-console/contentlist/booksAll/dateDsc/');
        return;
    }

    // Get CSRF token
    const csrfToken = window.csrfToken;
    if (!csrfToken) {
        console.error('❌ CSRF token not found. Make sure page is fully loaded.');
        return;
    }
    console.log(`✅ CSRF token found: ${csrfToken.substring(0, 20)}...\n`);

    // ===========================================
    // TEST 1: GetKFTChildrenData (Family Members)
    // ===========================================
    console.log('[Test 1] GetKFTChildrenData - Fetching family members...');

    try {
        const familyBody = new URLSearchParams({
            clientId: 'MYCD_WebService',
            csrfToken: csrfToken,
            data: JSON.stringify({
                param: {
                    GetKFTChildrenData: {}
                }
            })
        });

        const familyResponse = await fetch('https://www.amazon.com/hz/mycd/ajax', {
            method: 'POST',
            headers: {
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/x-www-form-urlencoded'
            },
            credentials: 'include',
            body: familyBody
        });

        if (!familyResponse.ok) {
            console.error(`❌ HTTP error: ${familyResponse.status}`);
            return;
        }

        const familyData = await familyResponse.json();
        console.log('✅ Family members response:');
        console.log(JSON.stringify(familyData, null, 2));

        if (familyData.GetKFTChildrenData?.householdMembers) {
            const members = familyData.GetKFTChildrenData.householdMembers;
            console.log(`\n📋 Found ${members.length} household member(s):`);
            members.forEach(m => console.log(`   - ${m.firstName} (${m.role}) - ID: ${m.customerId}`));
        } else {
            console.log('\n⚠️ No household members found (you may not be in a Family Library)');
        }
    } catch (error) {
        console.error(`❌ Family members fetch failed: ${error.message}`);
        return;
    }

    // ===========================================
    // TEST 2: GetHouseholdDetails (Book Sharing)
    // ===========================================
    console.log('\n[Test 2] GetHouseholdDetails - Testing batch sizes...');

    // Try to extract ASINs from page
    let testAsins = [];
    const pageContent = document.body.innerHTML;
    const asinMatches = pageContent.match(/B[0-9A-Z]{9}/g);
    if (asinMatches) {
        testAsins = [...new Set(asinMatches)].slice(0, 100);
        console.log(`✅ Found ${testAsins.length} ASINs on page to test with`);
    }

    if (testAsins.length === 0) {
        console.log('⚠️ No ASINs found on page. Using single test ASIN.');
        testAsins = ['B087DZX3PP'];
    }

    // Test with increasing batch sizes (duplicate ASINs to create larger batches)
    const batchSizes = [100, 200, 500, 1000];

    for (const batchSize of batchSizes) {
        let batchAsins = [];
        while (batchAsins.length < batchSize) {
            batchAsins = batchAsins.concat(testAsins);
        }
        batchAsins = batchAsins.slice(0, batchSize);

        console.log(`\n📦 Testing batch size: ${batchSize} ASINs...`);

        try {
            const startTime = Date.now();

            const sharingBody = new URLSearchParams({
                activity: 'GetHouseholdDetails',
                activityInput: JSON.stringify({
                    asins: batchAsins,
                    categoryList: ['KindleEBook'],
                    getChildWhitelistedAsins: true,
                    getHouseholdMemberDetails: true,
                    surfaceType: 'LargeDesktop'
                }),
                clientId: 'MYCD_WebService',
                csrfToken: csrfToken
            });

            const sharingResponse = await fetch('https://www.amazon.com/hz/mycd/digital-console/ajax', {
                method: 'POST',
                headers: {
                    'accept': 'application/json, text/plain, */*',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                credentials: 'include',
                body: sharingBody
            });

            const elapsed = Date.now() - startTime;

            if (!sharingResponse.ok) {
                console.error(`   ❌ HTTP error: ${sharingResponse.status} (${elapsed}ms)`);
                break;
            }

            const sharingData = await sharingResponse.json();

            if (sharingData.success === false) {
                console.error(`   ❌ API error (${elapsed}ms)`);
                break;
            }

            const whitelistData = sharingData.GetHouseholdDetails?.whitelistData || {};
            let sharedCount = 0;
            for (const customerId in whitelistData) {
                sharedCount += whitelistData[customerId].length;
            }

            console.log(`   ✅ Success (${elapsed}ms) - ${sharedCount} book-share relationships found`);

        } catch (error) {
            console.error(`   ❌ Fetch failed: ${error.message}`);
            break;
        }

        await new Promise(r => setTimeout(r, 500));
    }

    console.log('\n========================================');
    console.log('Test complete!');
    console.log('========================================');
}

testSharingAPI();
```
