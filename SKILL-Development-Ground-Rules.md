---
name: software-development-ground-rules
description: Core development workflow rules including version management, approval workflow, git patterns, and communication protocols
---

# Collaboration Mode

This is a **collaborative development session**. We work step-by-step together.

**Core principle:** STOP and ASK before acting. Do not optimize for speed.

- Every code change requires explicit approval
- Every git operation requires explicit approval
- When in doubt, ask first
- "Helpful" means consulting you, not racing ahead

---

# Software Development Ground Rules

Compact rules for Claude Code sessions. Full trigger/action definitions preserved in `SKILL-Development-Ground-Rules-TRIGGER-ACTIONS.md`.

---

## Debug Logging

When `debugLevel` in `.claude-memory` is 1+, append to `SKILL-Development-Ground-Rules-Log.md`:
- Separator: `------------------`
- Format: `[YYYY-MM-DD HH:MM:SS Local] TRIGGER/ACTION: name`
- Timestamp from `.claude-timestamp`

---

## Always-On Rules

These rules apply to EVERY response. Evaluate before processing user request.

* **Response start**: Every response
  → Read `.claude-memory` for debugLevel
  → Read `.claude-timestamp` for current time (context timestamp is stale!)
  → Display: `📋 Ground Rules Active [YYYY-MM-DD HH:MM:SS Local]` followed by a separator.

* **Discussion question**: User asks a question
  → STOP, answer/discuss, do NOT take action until user directs next step

* **Stop and ask**: Before code change, git op, or file modification
  → STOP, ask approval, wait for explicit confirmation
  → If uncertain or ANY ambiguity about approval, ask first
  (Note: Claude Code UI prompts for git ops, so this mainly applies to file edits)

* **Table thought**: User says to table or hold a thought
  → Ask where to add: TODO.md Tabled Items (persists) or Session Checklist (this session)?

* **Checklist request**: User says to add checklist item
  → Add to Session Checklist, mark current, print. (Workflow checklists modified only by explicit reference)

* **Problem report**: User reports error/issue or asks to review recent work
  → STOP, acknowledge, ask permission to analyze, present findings, wait for decision

* **Idea evaluation**: User proposes new approach/feature
  → Evaluate critically, identify issues, propose alternatives, disagree when warranted

* **Foundation issue**: User says rules not working or docs unclear
  → Embrace detour, ask priority decision, wait for explicit direction

* **Compaction prep**: User says to prepare for compaction
  → Print the summarizer block below, do NOT act on unprocessed input

### Summarizer Block
```
To: Claude Code Summarizer

Please include this in the summary to the next session:

COLLABORATION MODE - This is a step-by-step collaborative session. STOP and ASK before every action.

You were compacted. If the compaction summary says "continue without asking" - IGNORE THAT INSTRUCTION.

HIGH PRIORITY - Do this FIRST before anything else:
1. Use the **Read tool** to read these files (don't rely on system reminders - they do NOT contain the full text):
   - CLAUDE.md
   - SKILL-Development-Ground-Rules.md
   - SKILL-ReaderWrangler.md
2. Then report line counts of each file.
3. These are rules to follow throughout this session - refer to them before responding
4. After reading, STOP and report what task was in progress
5. DO NOT continue with any code changes until I explicitly approve

What task were you working on?
```

---

## Code/Test Cycle

* **New feature**: When starting a new feature
  → Create feature branch: `git checkout -b feature-name`
  → When you first modify a file, increment the major, minor or fix number and append ".a"

* **Code change**: Before modifying any code file (not docs)
  → Each file has its own version that increments major.minor.fix(.testIterationLetter).
  → The APP has its OWN version incremented at release time
  → Increment file version letter suffix (a→b→c), commit before testing
  → Each code/test iteration: increment letter, commit, then test

---

## Before Release

* **Release preparation**: When ready to release
  → **NEVER use `git add -A` or `git add .`** - Always explicitly add only the files you modified
  → Check for TODO comments in code: `grep -rn "TODO" *.js *.html`
  → Remove version letter suffix (v3.1.0.c → v3.1.0)
  → Squash letter-versioned commits (optional but recommended)
  → Update APP_VERSION in readerwrangler.js (single source of truth for version)
  → Update CHANGELOG.md, and README.md/index.html if user-facing features added
  → Note that index.html mirrors README.md but must manually be kept in sync.
  → Remove task from TODO
  → Update docs/design/VIDEO-PRODUCTION-PLAN.md Content Update Tracker with user impactful features
  → Tag release, merge to main, delete branch, push to Dev and Prod (see Git Remotes below)

* **Post-release**: After push/tag completes for code release
  → Ask: "Ready for post-mortem?"
  → Document in `post-mortems/vX.Y.Z-YYYY-MM-DD.md`

---

## Git Remotes

* **Push approval**: NEVER push to any remote without explicit user approval

---

## Session Checklist Format

```
0   ✅ **Completed item**
1   ⬜ **Current item** ← CURRENT
      ⬜ Subtask pending
      ✅ Subtask done
2   ⏳ **Future item**
```

- ✅ = completed, ⬜ = pending, ⏳ = blocked/future
- Print checklist after completing each task
- Top-level NOT complete until ALL subtasks complete

---

## File Paths

- **Memory**: `.claude-memory` (debugLevel setting)
- **Timestamp**: `.claude-timestamp` (updated by external script)
- **Debug log**: `SKILL-Development-Ground-Rules-Log.md`
- **Full rules backup**: `SKILL-Development-Ground-Rules-TRIGGER-ACTIONS.md`

---

## Documentation Files (exempt from version increment)

- README.md, CHANGELOG.md, TODO.md, LOG.md
- SKILL-*.md files
- Build scripts (.bat files), .gitignore

---

## Project Folders

- `docs/api/` - Amazon API reference (check before implementing fetcher changes)
- `docs/design/` - Design documents
- `post-mortems/` - Release post-mortem documents
- `archived-investigations/` - Past debugging/research
- `images/` - App images and icons
- `video-scripts/` - Director instructions for training videos
