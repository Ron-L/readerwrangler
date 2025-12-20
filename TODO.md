# TODO

## Prioritized Roadmap (By Priority & Complexity)

_Based on user requirements + Claude.ai independent review (CLAUDE-AI-REVIEW.md)_

---

### 🎯 Priority 1: Core Organization Features (User Personal Blockers)

**1. 🔎 Advanced Filtering + Collections Integration UI** ✅ **COMPLETE v3.8.0** - MEDIUM/MEDIUM (8-12 hours)
   - **Advanced Filtering:**
     - ~~Filter by genre/category~~ ❌ (NOT AVAILABLE: Amazon API doesn't provide genre/category metadata)
     - Filter by rating ✅ (DONE v3.8.0.b)
     - Filter by acquisition date range ✅ (DONE v3.8.0.k, fixed v3.8.0.m)
     - Filter by read/unread status ✅ (already existed)
     - Filter by series ✅ (DONE v3.8.0.k)
     - Filter by wishlist status ✅ (DONE v3.8.0.b, fixed v3.8.0.n)
   - **Collections Integration UI:** See [docs/design/COLLECTIONS-UI.md](docs/design/COLLECTIONS-UI.md)
     - Visual indicators (badges/icons) for collections on book covers ✅ (DONE: tooltip already shows collection names)
     - Metadata display showing which collections each book belongs to (add to modal) ✅ (DONE v3.8.0.k)
     - Filtering by collection name ✅ (already existed)
     - Filtering by read status (READ/UNREAD/UNKNOWN) ✅ (already existed)
     - "Uncollected" pseudo-collection ⏳ (Deferred - low priority)
   - **Optional Enhancements:**
     - Badge system (active filter count) ✅ (DONE v3.8.0.b)
     - Collapsible filter panel ✅ (DONE v3.8.0.b)
     - Filter button pulse animation ✅ (DONE v3.8.0.e)
     - Filter state persistence ✅ (DONE v3.8.0.f)
     - Filter reset on library load ✅ (DONE v3.8.0.g)
     - Filter reset on Clear Library ✅ (DONE v3.8.0.h)
   - Problem: Hard to find specific subsets in 2,300+ book library, collections data fetched but not visible in UI
   - Impact: Improves discoverability for power users, leverages existing Amazon collections in organizer
   - Note: Combined from former #2 and #3 - both build same filtering infrastructure
   - **Released:** 2025-12-20

**2. 🔀 Column Sorting** - MEDIUM-HIGH/MEDIUM (4-6 hours)
   - Sort books within columns by: acquisitionDate, seriesPosition, rating, title, author
   - Permanent re-ordering (like Excel sort, persists to IndexedDB)
   - Multi-column selection: apply same sort to each column independently
   - Users can manually adjust positions after sorting (not locked)
   - Wishlist column sorts like all others (by title, author, rating, etc.)
   - Problem: After organizing books into columns, can't fine-tune order by meaningful criteria
   - Impact: Completes organization workflow - get books into columns, then order optimally within each

**3. 🎯 Wishlist Integration - Basic** - MEDIUM/MEDIUM (8-10 hours)
   - Bookmarklet on Amazon book page extracts basic metadata (ASIN, title, author, cover, rating)
   - Appends to existing `amazon-library.json` as new top-level `wishlist` array
   - User selects same library JSON file → app merges wishlist + owned books
   - Wishlist books displayed in special "Wishlist" column with visual distinction:
     - Gray-out effect on cover/title
     - "Wishlist" badge overlay
     - Click opens Amazon purchase page
   - Problem: Users browse Amazon, find interesting books, no easy way to track for later purchase
   - Impact: Bridges gap between browsing and buying, integrates with existing organization workflow
   - **Subtasks:**
     - Bookmarklet: Extract book metadata from Amazon product page DOM
     - Bookmarklet: Append to `amazon-library.json` under `wishlist` array (or create file if user doesn't have library yet)
     - App: Parse wishlist array on JSON load
     - App: Create "Wishlist" column (auto-created, can't be deleted while wishlist books exist)
     - App: Gray-out styling + badge for unowned books
     - App: Click handler → open Amazon purchase page in new tab

**4. 📖 Enhanced Series Management** - MEDIUM/MEDIUM (6-10 hours)
   - Expand current "Collect Series Books" button
   - Automatic series detection
   - Series reading order visualization
   - Missing book detection ("You have books 1, 2, and 4 of this series")
   - Problem: Series books scattered across library
   - Impact: Better management for series readers

**5. Book Copy Feature** #Optional - MEDIUM/MEDIUM (8-10 hours)
   - Allow same book to appear in multiple columns
   - See [docs/design/BOOK-COPY.md](docs/design/BOOK-COPY.md) for full spec
   - Array-based architecture, Ctrl+Drag UI, delete operation
   - Problem: Can't organize same book multiple ways
   - Impact: More flexible organization

**6. 🗂️ Nested Groups/Hierarchies** #Optional - LOW/HIGH (15-20 hours)
   - Multi-level organization: "Science Fiction" → "Space Opera" → "Culture Series"
   - Nested containers for related books (e.g., series/themes)
   - Significant UI rework required
   - Problem: Flat column structure limits deep organization, related books scattered
   - Impact: Better for very large libraries (1000+ books), better grouping for series/themes
   - Note: "Groups/series containers" is a specific implementation of this generic feature

---

### ✨ Priority 2: Nice-to-Have Features

**1. 📖 Reading Progress Visualization** - MEDIUM/HIGH (6-10 hours)
   - Show reading progress percentage/position for each book
   - Implementation guidance: [Amazon Organizer Reading Progress conversation](https://claude.ai/chat/6e6f23c8-b84e-4900-8c64-fecb6a6e0bd1)
   - Note: Collections data already merged (line 452 LOG.md), this adds progress visualization
   - Problem: Users can't see reading progress in organizer
   - Impact: Better tracking of currently-reading books

**2. 🏷️ Color-Coding/Tagging System** - MEDIUM/MEDIUM (8-10 hours)
   - Visual distinction beyond columns
   - Tag-based organization
   - Problem: Columns alone may not capture all organizational needs
   - Impact: More flexible organization

**3. 🤖 Smart Collections (Rule-Based)** #Optional - LOW/HIGH (12-16 hours)
   - "All unread books rated 4.5+"
   - Requires complex rule engine
   - Problem: Manual organization is tedious
   - Impact: Automation for power users

**4. 🎯 Wishlist Integration - Series Gap Detection** #Optional - MEDIUM/VERY HIGH (20-30 hours)
   - Automatic series detection for owned books (requires series metadata)
   - Identify missing books in series (e.g., own books 1, 2, 4 but not 3)
   - Fetch metadata for missing books via Amazon API or series page scraping
   - Auto-populate wishlist with series gaps
   - Series column UI: Show gaps visually (grayed placeholder covers?)
   - **Blockers**:
     - Requires Speed Up Enrichment (completed v3.7.1) to avoid API throttling
     - Amazon's inconsistent series tagging may limit effectiveness
   - Problem: Series readers often have incomplete sets, no easy way to identify gaps
   - Impact: Automatic discovery of missing series books, targeted purchasing
   - **Investigation tasks:**
     - Research Amazon API for series metadata (GraphQL? Product Advertising API?)
     - Test series detection accuracy across sample of 50+ series books
     - Determine if series page scraping is feasible fallback
     - Measure API rate limits for series metadata queries
   - **Subtasks:**
     - Series detection algorithm (pattern matching on titles, author clustering)
     - Series gap identification logic
     - Amazon API integration for missing book metadata
     - Wishlist auto-population workflow
     - Series column UI for gap visualization

**5. ✨ UX Quick Wins** - MEDIUM/LOW (1-3 hours each)
   - Tooltips for control buttons (Backup, Restore, Reset, Clear)
   - First-run Welcome dialog explaining what ReaderWrangler is
   - Column name filtering (search by column name)
   - Make status dialog draggable/movable (modal → draggable)

---

### 📖 Priority 3: Polish & Documentation (Before Public Launch)

**1. 📖 Quick Start Video & Written Guide** - HIGH/LOW (2-4 hours) - See [docs/design/VIDEO-PRODUCTION-PLAN.md](docs/design/VIDEO-PRODUCTION-PLAN.md)

**2. 📚 Comprehensive Documentation Hub** - HIGH/MEDIUM (8-12 hours)
   - Troubleshooting guide (What if scrape fails partway? How to recover?)
   - FAQ (Multiple Amazon accounts? Kindle Unlimited books? Mobile support?)
   - Keyboard shortcuts reference
   - Data management guide (backup, export, import, JSON format)
   - Technical details (How bookmarklet handles anti-scraping)
   - Problem: Users get stuck, have questions, can't find answers
   - Impact: Reduces support burden, improves user confidence

**3. 📱 Mobile Support Clarity** - HIGH/LOW (1 hour)
   - Document whether app works on mobile devices
   - Add to FAQ and main page
   - Problem: Major omission for users who browse libraries on phones/tablets
   - Impact: Sets correct expectations

**4. 📋 Changelog Visibility** - MEDIUM/LOW (30 minutes)
   - Link version display (e.g., "v3.6.0") to CHANGELOG.md
   - Problem: Users see version numbers but no context
   - Impact: Transparency about what changed

**5. Fill in Missing Sections in USER-GUIDE.md** - MEDIUM/LOW (2-3 hours)
   - Complete placeholder sections
   - Add screenshots/examples
   - Problem: Partial documentation confuses users
   - Impact: Complete feature documentation

**6. Enhanced Getting Started UX** #Architecture - See [docs/design/ENHANCED-GETTING-STARTED-UX.md](docs/design/ENHANCED-GETTING-STARTED-UX.md)
   - Status: Planned (post-rename enhancement)
   - Help menu links, enhanced empty library state

---

### 📊 Priority 4: Analytics & Export (MEDIUM Priority, LOW-MEDIUM Complexity)

**1. 📈 Reading Stats Dashboard** - MEDIUM/MEDIUM (8-12 hours)
   - Books acquired by month/year
   - ~~Genre distribution pie chart~~ ❌ (NOT AVAILABLE: Amazon API doesn't provide genre/category metadata)
   - Average rating of collection
   - "Time to read" estimates based on page counts
   - Problem: No insights into library composition
   - Impact: Interesting for users, helps rediscover forgotten books

**2. 💾 Enhanced Export Options** - MEDIUM/LOW (2-4 hours)
   - Export organization to CSV (already has JSON)
   - Print-friendly reading list
   - Privacy-respecting share feature
   - Problem: Limited backup/sharing options
   - Impact: Portability and sharing

---

### 🔧 Priority 5: Technical Improvements (MEDIUM-LOW Priority, MEDIUM-HIGH Complexity)

**1. Phase 3: UI Error Handling** #FetcherImprovements - MEDIUM/LOW (2-3 hours)
   - Warning banners for missing descriptions
   - "View Missing Descriptions" feature
   - Problem: Users unaware of missing enrichment data
   - Impact: Transparency about data quality

**2. Minor Fetcher Improvements** #FetcherImprovements - LOW/LOW (1-2 hours)
   - Timeout removal, messaging improvements, terminology consistency
   - Problem: Minor UX issues in fetcher scripts
   - Impact: Polish and consistency

**3. 🔄 Phase 3 Retry Logic + Recovery + Pause/Resume** - MEDIUM/HIGH (12-16 hours, optional)
   - See [docs/design/PHASE-3-RETRY-LOGIC.md](docs/design/PHASE-3-RETRY-LOGIC.md) for full spec
   - Retry logic for failed enrichments (~1.3% failure rate)
   - Pause/Resume capability with global flag + button UI
   - Recovery: Save extraction state to localStorage, resume from interruption
   - State persistence: Track progress, allow resumption after browser close/refresh
   - Problem: Random enrichment failures, long extractions without pause, lost progress on interruption
   - Impact: Data quality improvement (99.8%+ expected), better UX for long extractions, prevents data loss
   - Note: This consolidates former P2 "Extraction Error Recovery" feature

**4. 🔧 Fix Manifest/Status System Architecture** #Architecture #BROKEN - LOW/VERY HIGH (40-60 hours)
   - **CRITICAL CONTEXT - READ BEFORE ANY WORK**:
     - **Problem**: Fetcher runs on `amazon.com`, app runs on `readerwrangler.com` (or `localhost`) → **different domains**
     - **IndexedDB isolation**: Browser security prevents cross-domain IndexedDB access
     - **Current state**: Manifest system writes to amazon.com's IndexedDB, app reads from readerwrangler.com's IndexedDB → **always 0 manifests**
     - **Affected users**: EVERYONE (both local dev and production GitHub Pages)
     - **Why it was missed**: Localhost testing masked the issue when testing both fetcher and app on same domain
     - **Historical context**: Repeated same mistake twice (manifest file polling v3.6.0, IndexedDB manifests v3.6.1+)
   - **What the system was trying to solve**:
     - Track **Fetch state** (how fresh is the file on disk?) vs **Load state** (how fresh is data in app?)
     - Warn user: "You loaded 30-day-old data but have a 1-day-old file on disk - reload it!"
     - See [state-matrix.html](state-matrix.html) for full 25-state matrix explanation
   - **Why app can't re-read files**:
     - Browser security: file picker requires user action, can't poll files automatically
     - No persistent file handle after initial read
   - **Subtasks**:
     - Move `state-matrix.html` from project root to `docs/design/`
     - Update `STATUS-BAR-REDESIGN.md` to document cross-domain limitation
     - Evaluate solutions:
       - Option A: Embed complete manifest in JSON metadata (simple, loses "file on disk" detection)
       - Option B: Hybrid approach (IndexedDB + JSON fallback)
       - Option C: Accept limitation, simplify to Load-state only
     - Fetcher: Auto-cull old manifests in `ReaderWranglerManifests` DB (keep only latest per type)
     - Clean up dead code if manifest system is removed/simplified
   - **Manual cleanup needed**:
     - localhost: Delete `AmazonBookDB` (empty, unused)
     - localhost: Delete `ReaderWranglerManifests` (empty, cross-domain doesn't work)
     - amazon.com: Delete `ReaderWranglerManifests` (17 entries accumulating, never read)
   - Problem: Manifest tracking doesn't work, status bar shows misleading info, wasted engineering effort
   - Impact: Accurate status tracking OR accept simpler Load-state-only approach

---

### 🌐 Priority 6: Integrations & Advanced Features (LOW Priority, HIGH-VERY HIGH Complexity)

**1. 🔗 Third-Party Integrations** - LOW/HIGH (20-30 hours)
   - Goodreads sync (import ratings, mark as read)
   - StoryGraph integration
   - Export recommendations to Amazon wishlist
   - Problem: Complex API work, authentication, rate limits
   - Impact: Niche feature for users of these services

**2. ☁️ Multi-Device Sync** #Architecture - LOW/VERY HIGH (40-60 hours)
   - Cloud storage option (self-hosted or encrypted)
   - Sync organization across devices
   - Problem: Major architectural change, privacy implications
   - Impact: Convenience for multi-device users

**3. 🧠 Smart Recommendations** - LOW/HIGH (30-40 hours)
   - "You own these similar books you haven't read yet"
   - "Others who loved [this book] also read [these books] from your library"
   - Highlight forgotten purchases based on high ratings
   - Problem: Requires recommendation engine, ML/AI complexity
   - Impact: Book discovery from existing library

**4. Live reflow drag-and-drop animation** #Optional - LOW/MEDIUM (4-6 hours)
   - Smooth visual feedback during drag operations
   - Problem: Current drag-and-drop feels abrupt
   - Impact: Polish and visual appeal

**5. 2D matrix layout** #Optional - LOW/VERY HIGH (50-80 hours)
   - Major refactor to grid-based layout
   - Problem: Current column-only layout limiting
   - Impact: Alternative organization paradigm

**6. Multi-User Support** #Architecture - LOW/VERY HIGH (40-60 hours)
   - See [docs/design/MULTI-USER-DESIGN.md](docs/design/MULTI-USER-DESIGN.md) for full spec
   - Status: Future enhancement (single-user first, multi-user later)
   - Covers: AccountId identification, storage architecture, mismatch handling
   - Problem: Multiple Amazon accounts on same device
   - Impact: Household/family sharing
   - **Workaround Available**: See [USER-GUIDE.md FAQ](USER-GUIDE.md#faq) "Can I maintain separate organizational states?" for Backup/Restore method to swap between different organizational states (demo vs. actual collection, testing vs. production, etc.)

**7. Multi-Store Architecture** #Architecture - LOW/VERY HIGH (60-80 hours)
   - See [docs/design/MULTI-STORE-ARCHITECTURE.md](docs/design/MULTI-STORE-ARCHITECTURE.md) for full spec
   - Status: Future enhancement (Amazon first, other stores later)
   - Covers: File naming, bookmarklet detection, data structure, migration path
   - Problem: Only works with Amazon
   - Impact: Support for other ebook platforms
