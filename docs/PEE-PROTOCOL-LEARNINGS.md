# Protocol Execution Engine (PEE) - Learnings and Approaches

**Date**: 2025-12-13
**Context**: Attempts to make Claude reliably execute ground rules as a "Protocol Execution Engine"

---

## The Core Problem

When Claude reads a large file (like SKILL-Development-Ground-Rules.md at ~700 lines), the content gets **summarized into context** rather than retained verbatim. This creates a fundamental issue:

1. **"Read the file"** → File content enters context as a summary
2. **Subsequent references** → Claude refers to the summary, not the original text
3. **Details get lost** → Specific trigger conditions, action steps, edge cases are approximated
4. **Protocol drift** → Claude executes "the gist" rather than the literal rules

### Evidence of This Behavior

- Rules say "do X before Y" → Claude does Y then X (order lost in summary)
- Rules list 5 specific checks → Claude does 3 (some checks dropped)
- Rules have exception clauses → Claude applies rule universally (nuance lost)
- Post-compaction → Rules file is "too large to include" in context restoration

### Why This Happens

Claude's context window has limits. When content exceeds what can be held verbatim, the system:
1. Summarizes to fit available space
2. Prioritizes recent/relevant content
3. Compresses older/reference content more aggressively

A 700-line rules file becomes a ~100-line summary, then a ~20-line summary as the conversation grows.

---

## Attempted Solutions and Results

### Attempt 1: "Read Before Respond" Instruction

**Approach**: CLAUDE.md says "read .claude-timestamp at start of EVERY response"

**Result**: Partially works. Small files (~1 line) are read and processed correctly. But the instruction to read the *rules* file at start of each response would be too slow and would itself get summarized.

### Attempt 2: Debug Logging to Prove Execution

**Approach**: Write to SKILL-Development-Ground-Rules-Log.md to prove triggers/actions fired

**Result**: Works for visibility but doesn't fix the underlying summary problem. Log shows what Claude *claims* to have done, not whether rules were followed literally.

### Attempt 3: PEE Protocol Cue ("PEE:" prefix)

**Approach**: User prefixes message with "PEE:" to trigger explicit re-read of rules

**Result**: Mixed. Forces a fresh read, but large file still gets summarized. Helps with compaction recovery but doesn't solve ongoing drift.

### Attempt 4: Role Identity Emphasis

**Approach**: Strong language in ROLE IDENTITY section: "You are a Protocol Execution Engine", "Execute, don't approximate"

**Result**: Improves intent but can't override context mechanics. Claude *wants* to execute literally but still references summaries.

---

## Three Proposed Options

### Option A: Grep-Based Chunked Ingestion

**Concept**: Structure rules file with grep-friendly headers. Claude greps for specific sections, getting small chunks that fit in context verbatim.

**Workflow**:
1. Grep for TOC section "TRIGGERS Events That Activate Protocols"
2. Scan TOC for potentially relevant triggers
3. Grep for specific trigger definition (e.g., "##### READY-TO-RELEASE-TRIGGER")
4. Get small chunk (~10-30 lines) of just that trigger
5. Grep for each action referenced in the trigger
6. Build understanding from multiple small, verbatim chunks

**Pros**:
- Each chunk is small enough to not be summarized
- Gets literal text of relevant rules only
- Scales to large rule files

**Cons**:
- Many grep calls = significant latency (each tool call takes measurable time)
- Requires knowing what to grep for (chicken-and-egg)
- Complex orchestration logic itself might be forgotten
- Still relies on Claude remembering to do the greps

**Verdict**: Technically sound but operationally slow and fragile.

### Option B: Pre-Made Checklists Per Workflow

**Concept**: Extract key workflows into small, standalone checklist files. Claude only needs to remember which checklist applies.

**Structure**:
```
SKILL-Development-Ground-Rules.md (master reference, rarely read in full)
├── RULES-CHECKLIST-BEGIN-FEATURE.md (~20 lines)
├── RULES-CHECKLIST-RELEASE-FEATURE.md (~30 lines)
├── RULES-CHECKLIST-CODE-CHANGE.md (~15 lines)
└── etc.
```

**Workflow**:
1. User says "let's release this feature"
2. Claude reads small RULES-CHECKLIST-RELEASE-FEATURE.md (verbatim, not summarized)
3. Claude copies checklist to Session Checklist
4. Work through checklist step by step

**Pros**:
- Small files stay verbatim in context
- Checklist format matches how Claude already works well
- User can see and correct checklist before execution
- Reduces cognitive load - just follow the list

**Cons**:
- Requires maintaining multiple files in sync with master rules
- Duplication between checklist files and master
- Still need Claude to recognize which checklist to load

**Verdict**: Promising. Works with Claude's strengths (checklists, small chunks).

### Option C: Dynamic Checklist Generation (Hybrid)

**Concept**: User prompts Claude to read specific sections and generate a checklist on-the-fly.

**Observed Example**:
```
User: "we should release to both Dev and Prod. Please see SKILL-Development-Ground-Rules.md
and review the Feature Development Lifecycle triggers and generate a Session Checklist
from the Actions of those Triggers that apply"

Claude generates:
0   ⬜ **Commit collections fetcher changes** ← CURRENT
1   ⬜ **PREPARE-RELEASE-ACTION**
      ⬜ Update to release versions (remove letters)
2   ⬜ **RELEASE-FINALIZATION-TRIGGER actions**
      ⬜ UPDATE-CHANGELOG-ACTION
      ⬜ REVIEW-CODE-TODOS-ACTION
      ...
```

**Workflow**:
1. User explicitly asks Claude to read relevant section
2. Claude reads and generates checklist *before* doing work
3. User reviews/corrects checklist
4. Claude executes approved checklist

**Pros**:
- No extra files to maintain
- User involvement catches errors early
- Checklist becomes the working document
- Generates fresh each time (no stale checklists)

**Cons**:
- Requires user to know which section to ask about
- Initial read still subject to summarization
- User must validate generated checklist

**Verdict**: Currently the best balance. Proved effective in 2025-12-13 session.

---

## Key Insights

### 1. Checklists Work With Claude's Architecture

Claude handles checklists well because:
- Sequential structure matches generation patterns
- Visual markers (✅ ⬜) create clear state
- "← CURRENT" provides focus
- Small, concrete steps reduce ambiguity

### 2. User Validation is Essential

The workflow that worked best:
1. Claude generates checklist from rules
2. User reviews and corrects ("aren't 1.1 and 1.2 reversed?")
3. Claude acknowledges and proceeds

This catches errors like:
- Wrong order (squash before vs after removing suffix)
- Missing steps (forgot to mark TODO.md complete)
- Wrong assumptions (thought files weren't committed)

### 3. Small Context > Large Context

Better: Read 30 lines of checklist, execute verbatim
Worse: Read 700 lines of rules, execute from summary

The goal isn't to get all rules into context. It's to get *relevant* rules into context in a form that won't be summarized.

### 4. Explicit Prompts Beat Implicit Triggers

What doesn't work:
- "When X happens, do Y" (trigger might not fire, or fires from summary)

What works:
- "Please read section X and generate a checklist" (explicit user instruction)

---

## Recommendations

### Short Term: Use Option C

For now, the most reliable approach is:

1. **User prompts explicitly**: "Read the Release triggers and generate a Session Checklist"
2. **Claude generates checklist**: Based on fresh read of specific section
3. **User validates**: Corrects any errors before execution
4. **Work the checklist**: Both parties track progress

### Medium Term: Consider Option B

If certain workflows are repeated frequently:
1. Create small checklist files for common scenarios
2. Less work for user to prompt
3. Less chance of generation errors
4. Trade-off: maintenance of multiple files

### Long Term: Tool/MCP Integration

The ideal solution would be:
- Rules stored in a structured format (YAML/JSON)
- MCP tool that retrieves relevant rules on demand
- Claude calls tool to get specific rules, not whole file
- No summarization because tool returns focused content

---

## Glossary

- **PEE**: Protocol Execution Engine - the concept of Claude executing rules literally
- **Context summarization**: When large content is compressed to fit context window
- **Session Checklist**: Running task list for current work session
- **Rules Checklist**: Pre-defined checklist extracted from ground rules for specific workflow
- **Compaction**: Context limit reached, conversation summarized to continue

---

## Related Files

- [SKILL-Development-Ground-Rules.md](../SKILL-Development-Ground-Rules.md) - Master rules file
- [COMPACTION-RECOVERY-PROMPT.md](../COMPACTION-RECOVERY-PROMPT.md) - Recovery instructions after compaction
- [post-mortems/v3.7.2-2025-12-13.md](../post-mortems/v3.7.2-2025-12-13.md) - Session where Option C was tested
