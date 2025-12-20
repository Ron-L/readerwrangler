---
name: readerwrangler-project
description: Project-specific context including architecture patterns, common pitfalls, file locations, and pending tasks for ReaderWrangler - a single-page React application for organizing ebook collections
---

# ReaderWrangler Project

## Project Context

**What it is:** Single-page React application for organizing ebook collections using drag-and-drop columns (like Trello). Users can load their ebook library from a JSON export (currently supports Amazon Kindle) and organize books into custom categories.


## Git Remote Workflow (Dev/Prod Pattern)

_Consider copying this pattern to other GitHub Pages projects_

**Remotes:**
- `dev` → readerwranglerdev repo (testing on GitHub Pages)
- `prod` → readerwrangler repo (production)
- No `origin` remote exists (prevents accidental pushes)

**Safety Design:**
- `git push` without specifying remote will **fail** (no default)
- Must explicitly choose: `git push dev main` or `git push prod main`

**Workflow Rules:**
- **Default push target: DEV** (`git push dev main`)
- **NEVER push to prod without explicit approval**
- "Proceed with push" = push to DEV only
- "Release to production" or "push to prod" = push to PROD
- After pushing to DEV, wait for GitHub Pages to deploy (~1-5 min), then test

**Approval Language:**
- "push" or "proceed with push" → `git push dev main`
- "release to production" or "push to prod" → `git push prod main`
- "release" alone → Clarify which target

**Push Rules by File Type:**
- **Navigator changes** (bookmarklet-nav-hub.js, URLs): Push to Dev first → test on GitHub Pages → then push to Prod
- **Other code changes**: After local testing, push to both Dev and Prod

**Testing Flow:**
1. Make changes locally
2. Commit
3. Test locally
4. `git push dev main` → test on ron-l.github.io/readerwranglerdev
5. When stable: `git push prod main` → live on readerwrangler.com
Note: Only changes to navigator and Data Status modals need testing on Dev before deployment to Prod
