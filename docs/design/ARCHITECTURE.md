# ReaderWrangler Architecture

## Tech Stack

- **Frontend:** React 18 (via CDN), Tailwind CSS (via CDN), Babel (via CDN)
- **Storage:** IndexedDB for book data, localStorage for UI state/settings
- **File Format:** Single HTML file (no build process)

## Data Flow

- User loads library → Parse JSON → Store in IndexedDB
- UI state (columns, book positions) → localStorage
- Collections data fetched from `amazon-collections.json` with cache-busting

## Version Management

Each code file has its own version constant for tracking changes during code/test cycles:
- **ORGANIZER_VERSION** in readerwrangler.js - Main organizer application
- **FETCHER_VERSION** in fetcher files - Data fetching utilities

Version letter suffix (a→b→c) increments with each code/test iteration, removed before release.

Project/release version is maintained in README.md badge (single source of truth for releases).

## Status Icons (Critical Pattern)

- Pre-load ALL 5 icons in DOM simultaneously
- Toggle visibility with CSS `display: none/inline-block`
- **NEVER change `src` attribute** (causes 30-60s browser lag)
- See CHANGELOG Technical Notes for failed approaches

### Icon Display Lag (Lessons Learned)
- Changing `src` attribute causes 30-60s lag
- Using `key` prop causes blank icon during mount/unmount
- Cache-busting on image src doesn't help
- Solution: Pre-load all icons, toggle CSS display property

## Cache-Busting

**Collections file:** `amazon-collections.json?t=${Date.now()}` in readerwrangler.js:828
- Prevents browser from caching collections data

**Dev mode scripts:** `?v=' + Date.now()` in bookmarklet-nav-hub.js:160
- Used for fetcher script loading in development environment

## Terminology

- Use "load" not "sync" (user loads files, not syncing with service)
- "Library loaded" not "Last synced"
- "Load Updated Library" not "Sync Now"

## Three-Environment Testing

**Environments:**
| Environment | URL | Bookmarklet | Use Case |
|-------------|-----|-------------|----------|
| LOCAL | localhost:8000 | ⚠️ LOCAL (orange) | Rapid iteration, instant feedback |
| DEV | ron-l.github.io/readerwranglerdev | 🔧 DEV (blue) | Test GitHub Pages deployment |
| PROD | readerwrangler.com | 📚 ReaderWrangler (purple) | Production users |

**Bookmarklet Behavior:**
- LOCAL bookmarklet → loads from localhost:8000
- DEV bookmarklet → loads from readerwranglerdev repo
- PROD bookmarklet → loads from readerwrangler.com (or github.io fallback)

**Why three bookmarklets?**
Bookmarklets run on Amazon.com, not our servers. They can't detect if you're a developer. Solution: Install all three from localhost installer, then choose which environment to test.

**Testing workflow:**
1. Start local server: `python -m http.server 8000`
2. Visit localhost:8000/install-bookmarklet.html (shows all 3)
3. Drag bookmarklets to toolbar
4. On Amazon, click appropriate bookmarklet to test that environment
