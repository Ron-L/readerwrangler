---
description: Mechanical class-of-sites comb — enumerate ALL instances by two independent pivots, then publish a file:line site-map table BEFORE editing.
argument-hint: <the class being changed, e.g. "dialog Esc dismissal" or "everything that moves book membership">
---

You are running the **class-of-sites comb** for: **$ARGUMENTS**

This is the RIGOROUS version, not an eyeball pass. Do every step. Cite `file:line` for every
claim. Do NOT edit any code until the site-map table is posted and the class definition is stated
as a falsifiable claim.

## Step 1 — Define the class precisely (one sentence)
State what the class actually IS — the *operation/state/surface*, not the artifact you happened to
notice. (e.g. NOT "drop handlers" but "every path that moves book membership"; NOT "dialogs I can
click to" but "every state that gates an overlay".) A wrong class definition is the #1 way this
fails, so write it down where it can be challenged.

## Step 2 — Pivot 1 (the primary signature)
Grep the most direct signature of the class and list every hit with `file:line`:
- callers of the function, OR
- renders of the component/overlay, OR
- writes to the state.
Do NOT stop here — a single positive-signature search is structurally blind to negative instances.

## Step 3 — Pivot 2 (an INDEPENDENT signature)
Grep a *different* signature that should identify the same class:
- the **guard condition / action type / state flag** (finds disabled & negative branches — the
  code that deliberately does nothing), OR
- **registry / dispatch membership** (what's in the OR-chain, the switch, the Esc chain), OR
- the **user-facing string**.
Two pivots rarely share a blind spot.

## Step 4 — Diff the pivots
Compare the Step 2 and Step 3 hit lists. **Where they disagree, the difference IS the suspected
missed instance.** List the diff explicitly. This converts "did I get them all?" from a feeling
into a diff.

## Step 5 — Surface walk (only for user-facing operations)
Walk RW's finite entry-surface inventory and ask, per surface, "does it expose this operation, and
does it now behave correctly — including its DISABLED states?":
keyboard shortcuts · book context menu · folder context menu · list/search context menus ·
menu bar · drag-and-drop · dialog buttons.
Surfaces don't hide; code does.

## Step 6 — Publish the site map (the artifact)
Post a table: `| instance | file:line | status (ok / needs-fix / n-a) | note |`, one row per member
of the class. Then state the class as a falsifiable claim: **"Class = N sites: A, B, C … — here is
each."** This is what Ron audits BEFORE the work — his catch lands here, not three mistakes later.

## Step 7 — Then chokepoint what was found
Note whether the N sites should collapse to ONE implementation (a shared function / registry /
component / FSM) with thin call sites. The comb FINDS; the chokepoint KEEPS it found. They compose
— neither substitutes for the other. If the fix is "add the same thing to N places," that is itself
the signal the structure is missing.

---
Reference: CLAUDE.md "Class-of-sites change" rule + `feedback_investigate_completely` (the three
rules: condition-grep · two independent pivots · surface walk). This command IS their mechanization
— running it is the difference between the comb and the impression of the comb.
