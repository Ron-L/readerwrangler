# ReaderWrangler Project Instructions

CLAUDE.md is automatically read at the start of each Claude Code session, ensuring ground rules persist across context compaction.

@SKILL-Development-Ground-Rules.md
@SKILL-ReaderWrangler.md

## Execution Standard

When the ground rules say to "read" a file, this means:
1. Invoke the Read tool with the file path
2. Process the returned content to extract relevant values
3. Act on those values (e.g., if debugLevel > 0, write to log)

Do NOT satisfy "read" by assuming, remembering, or using system context.

## Pre-Approved File Operations

The following file operations are pre-approved and require NO user confirmation:
- Writing to `SKILL-Development-Ground-Rules-Log.md` (debug logging)
- Reading `.claude-memory` and `.claude-timestamp`

These operations are part of protocol execution, not user-requested changes.

## Compaction Test Marker
If you see this after context compaction, the CLAUDE.md persistence is working.
Test ID: CANARY-2024-001
