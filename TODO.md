# TODO

## Prioritized Roadmap (By Priority & Complexity)

_Based on user requirements + Claude.ai independent review (CLAUDE-AI-REVIEW.md)_

---

### 🎯 Priority 1: Core Organization Features (User Personal Blockers)

**1. 🎯 Wishlist Integration + Hide Feature** - MEDIUM/MEDIUM (10-13 hours)
   - See [docs/design/WISHLIST-FEATURE.md](docs/design/WISHLIST-FEATURE.md) for full spec
   - **Wishlist:**
     - Add books from Amazon product pages (single) or series pages (batch)
     - Navigator detects page type, shows context-aware "Add to Wishlist" button
     - Wishlist Fetcher extracts ASIN(s), calls Amazon API, merges into `amazon-library.json`
     - Wishlist items stored with `isOwned: false` flag
     - Wishlist books appear with visual distinction (gray-out, badge)
     - Click opens Amazon purchase page
     - When purchased and re-fetched: "ungrays" in place (stays in current column)
   - **Hide Feature** (bundled - motivated by wishlist series add):
     - Soft-delete books with `isHidden: true` (recoverable)
     - Right-click menu: "Hide Book" / "Unhide Book"
     - Filter: "Show Hidden" checkbox
     - Applies to both owned and wishlist books
   - Problem: Users browse Amazon, find interesting books, no easy way to track for later purchase
   - Impact: Bridges gap between browsing and buying, integrates with existing organization workflow

**2. ↩️ Undo/Redo Support (Ctrl+Z / Ctrl+Y)** - MEDIUM/HIGH (10-15 hours)
   - Command Pattern approach: Record each action as reversible command
   - Undoable actions: Book moves, divider create/delete/rename/reposition, column create/delete/rename/reorder
   - Maintain history stack (configurable depth, e.g., 50 actions)
   - Redo support via second stack
   - Key risk: Must integrate carefully with useRef-based drag performance optimization
   - Problem: No way to recover from accidental moves/deletes; expected UX capability
   - Impact: Standard user expectation, especially important for drag-and-drop interfaces

**3. 📖 Enhanced Series Management** - MEDIUM/MEDIUM (6-10 hours)
   - Expand current "Collect Series Books" button
   - Automatic series detection
   - Series reading order visualization
   - Missing book detection ("You have books 1, 2, and 4 of this series")
   - Problem: Series books scattered across library
   - Impact: Better management for series readers

**4. Book Copy Feature** #Optional - MEDIUM/MEDIUM (8-10 hours)
   - Allow same book to appear in multiple columns
   - See [docs/design/BOOK-COPY.md](docs/design/BOOK-COPY.md) for full spec
   - Array-based architecture, Ctrl+Drag UI, delete operation
   - Problem: Can't organize same book multiple ways
   - Impact: More flexible organization

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
   - **Drag Divider by Title Area** - Click-drag on divider title text (not just ⋮ handle) to reposition. Must not conflict with double-click to rename.
   - **More Auto-Divide Helpers** - Auto-Divide by Author, by Acquisition Date (Year groups), by Page Count (Short/Medium/Long). All use same divider infrastructure.

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

**4. (MOVED TO PRIORITY 1 #0)** Simplify to Load-State-Only Status System - See Priority 1 for details

**5. 🔧 Refactor readerwrangler.js into Modules** - LOW/MEDIUM (4-6 hours)
   - Current state: 3,862-line monolithic file with 50+ state variables, 80+ functions
   - **Recommended: Minimal Split (4 modules)**

   | Module | ~Lines | Contents |
   |--------|--------|----------|
   | `storage.js` | 150 | IndexedDB, localStorage operations |
   | `dataProcessing.js` | 400 | Import, merge, filter logic |
   | `dragDrop.js` | 500 | Drag handlers, binary search optimization |
   | `uiHelpers.js` | 200 | Formatters, display helpers, constants |
   | `readerwrangler.js` | 1,500 | State, hooks, orchestration, JSX |

   - **Key risks to preserve:**
     - Drag performance uses refs to avoid re-renders - must preserve
     - `loadLibrary()` handles multiple JSON formats - complex parsing
     - 8 filters must stay coordinated
     - State sync between books array and column.books IDs
   - **Alternative: Thorough split (12 files)** with components + custom hooks - cleaner but 2-3 days work
   - Problem: Large monolithic file hard to navigate and maintain
   - Impact: Better code organization, easier future maintenance, testability
   - **Implementation order:**
     1. Extract `uiHelpers.js` (no dependencies)
     2. Extract `storage.js` (only localStorage/IndexedDB)
     3. Extract `dataProcessing.js` (uses above)
     4. Extract `dragDrop.js` (uses uiHelpers)
     5. Update main component imports

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
