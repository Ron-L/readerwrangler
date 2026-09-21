# PRINCIPLES — the distilled laws of this project

_Every principle below was paid for. Sources: all 107 release post-mortems (2025-11-11 → 2026-09-04),
distilled 2026-09-04 so the archive never needs re-reading. The archive remains the depth; this is the law._

**The meta-principle that governs this file** (proven by the archive itself): *documenting a lesson does not
prevent its recurrence — only a mechanism does.* Version confusion was documented five times in the v3 era
and recurred ~11 more times anyway; one PM even records the lesson being read and **inverted** (a
"Mistakes Made" entry internalized as the correct pattern). So every Law below names its **enforcement**:
the rule, checklist item, memory file, or code pattern that makes it mechanical. A principle without an
enforcement is a wish.

**The newest and most literal mechanism (2026-09-17): the pre-build gate.** A `PreToolUse` hook
(`.claude/hooks/gate-check.py`) denies the *first* edit of `readerwrangler.js`/`mobile.js` each turn and
presents an 11-point checklist; a `Stop`/`SessionStart` hook re-arms it per turn. It exists because of a
sharper form of the meta-principle, paid for the same week it was written: **invoking a rule's name is not
running it.** A "new dialog checklist" added to CLAUDE.md was skipped the same session it was authored, and a
class-of-sites "comb" was performed *by eye* (missing a 5th broken overlay) while its name was invoked — the
mechanical two-pivot grep found what the impression missed. A written rule gets *performed*; a gate *fires*
whether it's remembered or not. The 11 points (source of truth: `gate-check.py`): (1) extending a spaghetti
section → restructure; (2) adding state → represent *legal* states (FSM / cooperating FSMs / reducer), not
loose flags [Law 17]; (3) reinventing a React/DOM wheel?; (4) can the relationship live in a *structure*
(containment) not a hand-synced list?; (5) call the existing closer/accessor, don't hand-roll a partial;
(6) less code, not cleverer?; (7) class of sites → run `/sitemap` (two pivots, publish the table before
claiming coverage) [Law 5]; (8) grounded in the code, not a hazy memory? [Law 2]; (9) delivering less than
asked → name + FILE the gap; (10) build-grade or explore-quality?; (11) did Ron approve *this* change? [Law
1]. It is a trial (`.claude/settings.local.json`); the design of the *structural* version that would retire
it — a self-registering `<Dialog>`/`<Popover>` layer registry — is in **DIALOG-DISMISSAL-AUDIT.md** (deferred
to its own branch).

**Era note (Ron, 2026-09-04)**: some recurrence counts below are partly artifacts of earlier AI model
generations, not process gaps — early models fought the versioning rules, couldn't reliably evaluate the
old trigger-based rule system (abandoned for that reason), and drifted from instructions in ways current
models (Fable 5 era) simply don't. The enforcement mechanisms remain valuable — but "execution failures
against adequate rules" largely healed with better models, which was outside our control and happily
happened. Read the pre-2026-08 war stories with that lens; keep the mechanisms anyway.

---

## THE LAWS

### 1. STOP and ASK — discussion is not approval; wait for the answer
The single most-repeated collaboration failure (10+ recurrences, including "You went off the reservation"
and three violations in one release). Questions asked without waiting are monologue. After any confusion or
correction: state the conclusion, then WAIT — the 10-second pause prevents the 10-minute fix.
Two amendments (Ron, 2026-09-04): **if in doubt of the user's intention, ask and clarify** — a wrong guess
executed is worse than a question; and **honest pushback is always welcome** — a standing invitation, not a
risk. The record backs both: every pushback that shipped (title-tiebreak veto, backwards-controls catch,
auto-mode-switch rejection) improved the product.
**Enforcement**: CLAUDE.md Collaboration Mode; `feedback_wait_for_answer` memory; "discussion mode" protocol
with explicit enter/exit.

### 2. NEVER ASSUME — verify it or ask; a belief you haven't checked is not a fact (Ron: "the biggest rule")
The most-recurrent technical failure (12+ PMs): asserting from a hazy model instead of reading. A hazy
mental model — or a fragment of a compaction summary — is the *signal* to re-read, not license to guess.
Page-vs-API claims require a captured request. Sub-agent output is intermediate, not settled. The
costliest case: an entire durability argument built on confusing RW-Wishlist with the Amazon wishlist —
corrected twice before "go read the code." **The tell that catches an assumption in flight — the words
_just / only / redundant / cosmetic / should be / safe to / probably / I'm sure / I think_** — each marks
a belief about to be acted on unchecked; stop and verify before the next keystroke (7.15.0: "*just*
cosmetic" dropped a CSS class a live handler matched on — the assuming, not the class, made the mistake).
**Ron's standing trade (2026-09-21): OVER-confirm — spend the tokens and the time; that cost is always
smaller than a mistake built on incomplete memory or an assumption. He would rather wait.**
**Enforcement**: `feedback_verify_dont_assume` + `feedback_wait_for_answer` memory; the pre-build gate's
item 8; the NEVER-ASSUME rule atop `../CLAUDE.md` (loaded every turn); cheap read-only probes as the
default first move.

### 3. Instrument → prove the theory → fix → prove the fix (Ron's doctrine)
Fix-then-test just *moves* the problem; testing only the old symptom lets it go. Prove where the time/bug
actually is before touching code, and let the same instrumentation certify the fix. Twin failure mode:
**confidence before evidence** — never present a theory as a verdict; present it with the probe that would
falsify it. (v5.5.4 spent ~10 alphas optimizing React renders; the diagnostic showed 2 renders in a
44-second drag — it was browser paint.)
**Enforcement**: `feedback_debugging` Rule 1b; two-rounds-of-theory stop rule.

### 4. After 3 iterations, question the abstraction
Proposed 2025-11-11; ignored through 26 alphas (v3.14.0 drag-drop) and 9 alphas (v6.11.2 — where one
question, "why aren't these just items?", replaced all nine). If each fix adds a special case instead of
removing one, the design is wrong: stop, list the edge cases, ask "are these actually different things?",
propose Plan Mode. 15 minutes of design beats 3 hours of patches, every measured time.
**Enforcement**: `feedback_debugging` Rule 2.

### 5. Enumerate ALL instances of a class — including copies, setters, and siblings
Fixing only the reported instance is the default failure ("Claude doesn't naturally do this" — v3, 2025;
still true in v7 until made mechanical). The class includes: sibling fetchers (the same user-gesture bug
fixed in 5 files across 4 releases), all registrations of a listener (a second keydown handler hid for 16
alphas), every modal close path, every render path, `foo` AND `setFoo`, and **inline duplicates of a
structure you extend** (the alpha.13 crash lived in a copy of `enterEditMode`). **And the remote
consumers of an element's markup**: when you change a DOM element's class / attributes / structure,
grep for what *else* keys on it — `.closest('.x')`, `querySelector`, class/attr hooks — because a
markup change can silently break a handler elsewhere in the file. 7.15.0: a menu refactor moved
`position:fixed` from the `fixed` CSS **class** to an inline style and dropped the class; the
close-on-outside handler matched `e.target.closest('.fixed')`, so every menu item's click died on
mousedown — **no console error, 6 alphas to find.** A class/attribute an element wears may be
load-bearing for code that never appears in the diff.
**Enforcement**: `feedback_investigate_completely` memory; grep-the-class before declaring done —
for a markup change, grep the class/attr name across the file for remote matchers *before* editing.

### 6. Commit before every test; one concern per alpha; build markers on every surface
What keeps 25-alpha runs bisectable and revertible, and what makes "which build am I running?" answerable
(invisible changes + no build marker = guaranteed mystery). Alphas are tested locally or on dev — never
against prod (APP_VERSION doesn't bump during alphas, so prod serves stale JS no matter how hard you reload).
**Enforcement**: CLAUDE.md versioning workflow; `feedback_alpha_testing` memory.

### 7. Version discipline: file version ≠ app version; bump the number, then suffix
The most-repeated single mistake in project history (documented 5×, recurred ~11× more before becoming
mechanical). Feature = minor, fix = patch; bump first, then `-alpha.N`; drop the suffix at release without
re-incrementing; every runtime change gets a bump ("we HOPE it acts the same but can never be sure");
cache-busters (`storage.js?v=`, CSS) update in the same commit as the file (one sat at 5.0.0 while the app
shipped 5.4.7 — a full investigation chased code the browser never loaded).
**Enforcement**: CLAUDE.md versioning table + release checklist.

### 8. Real data, real scale, real hands — one minute of real use beats a day of review
Single-item testing validates the implementation; multi-item real data validates the design (five series
sorts looked perfect until Larry Bond). Ron's first minute with a feature has caught something in nearly
every release; ship rough for feel-testing rather than polishing a private model. Corollaries: test where
the *behavior* lives (touch tooltips on a phone, Ctrl+Drag on Windows, ask-where-to-save on AND off), and
know the **dev-machine blind spots** — paths whose correct local behavior is "never runs" are untested by
construction; say so before shipping.
**Enforcement**: the alpha cadence itself; test instructions with precise expected values — magnitude AND
shape (`feedback_debugging` Rule 4).

### 9. Guarded persistence — every irreplaceable datum gets a load-gated writer
An unguarded save-effect stamps defaults over saved data on mount; a restore gated on the wrong condition
falls back to a stale second store. This class ate 24 Book Lists (cold-boot race), scrambled folder order
for weeks (field-stripping cache write), and hid behind an audit note that said "it's a trap… OK for now"
— **a trap rated OK-for-now is a latent incident.** The cures: single guarded source of truth, writers
gated on load-complete, guest guards on read-mostly instances, atomic generational commits for multi-key
writes, and loud (never silent) save failures.
**Enforcement**: F1 consolidation shipped; the pattern is now the codebase's standing shape.

### 10. Any field that enters export travels everywhere — "app-side-only" data isn't
Backups carry it, restores push it to the relay, imports bring it home again. A migration that clears a
value **must** pair with an inbound filter while any source of truth still carries it, or the value
resurrects on every import (the 'Kindle eBook' token did exactly this, silently zeroing a backfill).
A **user's deliberate clear is the same shape as a migration's clear**: a cleared field is `null`, and
`incoming ?? local` reads `null` as "absent — use incoming", so the stale value comes back. Fields the
user owns and the fetcher never sets must be **local-wins**, not `??` (7.14.4: cleared goals/ratings/tags/
notes resurrected on import for exactly this reason). Declare each field's ownership in **one registry**
(`bookMerge.js` `BOOK_FIELD_OWNERSHIP`) and drive the merge from it — a field can't be missed and its
behavior lives in one place.
**Corollary — a merge must never invent a field name.** The same file preserved a phantom `note` (real
field `userNote`) and once a phantom `hidden` (`isHidden`): the wrong name is silently created, the real
one silently dropped, and JS never complains. The mechanism is a test invariant: **the merge output may
not contain a key absent from both inputs** (that is exactly what a phantom target name looks like),
paired with a per-user-field clear-survives round-trip. Both would have caught both phantoms on sight.
The maximal cure is field-name **constants** used at every site so a typo is a reference error (filed).
**Enforcement**: FORMAT-POLICY.md; the migration+filter pair as the standard shape; `bookMerge.js` +
`test/bookMerge.test.js` (the ownership registry + the no-invented-keys / clear-survives gate tests).

### 11. Design-doc-first for anything architectural — then check yourself against it
The single most consistent predictor of smooth execution across all eras (11+ PMs; the four cleanest
releases in the archive were plan-mode-with-line-numbers). Writing the doc *before* code exposed real holes
in already-agreed designs, twice. For risky designs: epistemic tags (`[verified in code]` / `[assumption]`)
plus an adversarial cold review — 7.0.0's review found two correctness-critical flaws on paper. Record
**rejected** options with reasons (re-litigation cost thereafter: zero — see MULTI-INSTANCE, FORMAT-POLICY).
**Enforcement**: the design-doc culture in docs/design/; never-relitigate docs for settled facts.

### 12. Mechanical honesty — every display, ritual, and receipt needs a mechanism that can actually know
"Saved" must mean saved (picker before toast), "newer" must mean a different generation (not a timestamp
race), a commit message must describe what's in the commit (one claimed 8 edits and contained none), and
timestamps come from the tool, never extrapolation — a fabricated header drifted 4½ hours and corrupted an
analysis. When a compliance ritual gets easy to fake, that's the moment it's about to matter.
**Enforcement**: `feedback_mechanical_honesty` memory; the heredoc ban (three-for-three earned a ban, not a
caution); receipts-and-honesty as a feature genre.

### 13. Post-compaction (or post-gap) state is fragments plus assumptions — re-read, never remember
The "Runaway Robot" law: after compaction, rules must be re-read with the Read tool (a claimed reading was
once caught with a line-count quiz), permissions do not carry over, and design details do not survive
summarization (a dialog was once built entirely wrong from a summary — "You did not get the plan": ask for
the design again instead).
**Enforcement**: CLAUDE.md compaction protocol; persistent files (CLAUDE.md, design docs, memory) as the
only state that survives.

### 14. Look backward before inventing forward; investigate before estimating
"What did we do before?" precedes "what should we do next?" — the archive's oldest law. `git show` is a
design tool; the feature estimated at 4-6 hours took 15 minutes because 5 of its 8 capabilities already
existed. Simplicity wins; don't over-engineer rare operations; "leave it as-is" is a valid design decision.
**Enforcement**: habit + this file. (The unfixed cousin: optimistic scope framing — "minor" keeps becoming
"major." Budget accordingly.)

### 15. Chase every alarming number until it has a name
Deferred mysteries return as unreproducible field issues at ten times the price (Ron's doctrine). The
13-orphans day is the proof: three convincing wrong answers survived until every number was named —
wishlist, sample-pair, husk, echo, token — "and once everything had a name, there was nothing left to
fear." Beware the **numerology trap**: unrelated sets of similar size masquerade as each other; name all of
them in one table. Never bare "not worth chasing" — chase it or log it with the evidence for a scheduled chase.
**Enforcement**: `feedback_debugging` Rule 1c; telemetry tripwires instead of speculation (the
`newOwnershipType` instrument paid off twice with zero user friction).

### 16. Perceivable at the point of effect — absence, position, and silence are not communication channels
(2026-09-07→09, the invisible-control purge — ten instances in one cycle, see the v7.8.0-7.9.0 PM's table.)
A control styled as a display, a keystroke consumed silently, a stored rule firing invisibly, meaning encoded
in a caption's ABSENCE, a capped list wearing a scrollbar, primary nav that hides until scrolled — each one
survived until the sole user (who BUILT several of them) failed to perceive them within minutes of real use.
State changes must be visible where they happen; every offered action must visibly act or visibly explain;
hidden standing rules need a surface where they can be seen and revoked, or they don't ship (the alias
rejection, the Reset-flag rejection).
**Enforcement**: the design question at review time — "does the control announce itself where the need
arises, and does its effect show where the eye already is?" Ron's field test catches these today; at launch
that instrument is gone and only this question remains.

### 17. Represent legal states, not loose flags — make illegal states unrepresentable (Ron's doctrine)
N independent booleans for one feature permit 2ⁿ combinations, including the nonsensical ones — the
Auto-Organize orphan was exactly an illegal combo a flag allowed ("preview closed, child popup still open").
Two failure modes compound: a *new* flag must be threaded into every existing decision point or it **fails
open** (the one branch you forget is a silent bug), whereas an FSM's states are **enumerable**, so a new
state is a thing you're forced to consider. Related-but-*independent* dimensions aren't an excuse for flags:
model them as one FSM over the reachable combinations (`None, A, AB, B`) or as **cooperating / orthogonal
FSMs** that coordinate by event — both make illegal states unrepresentable without a 2ⁿ transition table. The
tell that the structure is missing: a close/reset function that hand-clears 3+ related states (and the day
one path clears a subset, you have an orphan). Pairs with the containment law — push the relationship into a
structure so the procedure shrinks to nothing.
**Enforcement**: pre-build gate checklist item 2; the overlay-registry design (DIALOG-DISMISSAL-AUDIT.md) as
the worked example; `project_714_release` memory.

---

## SECOND TIER — by theme (the best of the rest)

**Debugging**
- Log the raw response before theorizing; GraphQL returns data AND errors together — only fail when there's
  truly no data. Scary vendor errors are often benign.
- Trust an unexpected test result over the mental model, immediately ("no console output" once broke the
  wrong model — the refactored handlers were dead fallbacks; `feedback_verify_live_handler`).
- Compare working vs non-working sibling paths; trace data across every transformation boundary (field-name
  mismatches fail silently — `acquisitionDate` vs `acquired` once blanked a whole filter).
- Some "bugs" are expectations (cockpit error); verify intended behavior before declaring a defect.

**Architecture**
- Extract logic into a pure, node-tested engine before wiring UI — but remember engine tests validate LOGIC,
  not INTEGRATION (8/8 green while undo was broken).
- References not copies for multi-membership; signals in the data (`userEdited`) beat out-of-band params;
  single source of truth for config (parallel label maps rot); sentinels beat booleans for "unset vs cleared."
- Every `{entityId: value}` map needs a paired cleanup on entity delete.
- React: never read a ref inside a state updater (the deferred-updater trap — cost two releases); hooks
  above conditionals (Babel can't catch #310); refs + direct DOM for 60fps work; global key handlers need
  escape hatches (input focus, modal open) — and there may be TWO of them.

**Release engineering**
- Divergence pre-flight (`git log branch..main`) before drafting merge steps — prod accumulates hotfixes;
  `--ff-only` fails loudly; **never force-push**.
- Small independent branches; a git worktree when a second branch must not disturb the serving tree.
- `git add` specific files only (the `-A` rule was earned three times); `git status` before the release commit.
- Big-bang refactors leak features for weeks (v5.0.0: 175 alphas, then 8 hotfixes in 48 hours) — the
  **feature-parity checklist** it needed was recommended four times and never built; build one next time.

**UX & copy**
- UX-hat analysis before implementing — consistently better outcomes across ~10 PMs; the user's workflow
  beats the assistant's consistency instinct; the user is often the better designer (3-state toggle, HTML
  tables, sliding windows all theirs).
- Convert symptom-lists into invariants with the user; invariant specs implement in one pass.
- Symbols make promises the clicks must keep; visual feedback IS the feature; error copy states the
  constraint, the why, and the alternative; behavior over category ("you can't move books out of here — use
  folders"); name the actor; positive framing; an ellipsis promises a dialog.
- Handle gracefully, don't forbid (flexible tool = escape hatches, not guards). Match platform mental
  models (Trash, File Explorer). Labels on environments — indistinguishable instances invite
  cross-environment mistakes.

**Platform facts worth their scars** (details live in the referenced docs)
- Amazon API: `getProducts` max 30 ASINs; only the plural endpoint works; partial errors are normal; the
  full library-API map (records vs titles, NOT-hash filters, pagination exonerated, 2801=2801) lives in
  **FORMAT-POLICY.md**; author-string parsing is a settled NO.
- Cloudflare KV: per-value atomicity only; ~60s list lag; ~1 write/sec/key; quotas are account-wide;
  permanent keys compound (the 678 MB lesson) — sweep orphans.
- Browser: drag events lie about modifier keys on Windows; `title` doesn't render on touch; `aria-label`
  overrides visible text; user gestures expire during long async work (`showSaveFilePicker` first);
  localStorage beats useState defaults; IndexedDB is domain-isolated; null in persisted state becomes
  `"nullpx"`. Status icons (v3.5 PNG era): swapping an `<img>` `src` to change an icon caused a
  30-60s load lag, and a React `key` prop blanked it during mount — the fix was pre-load ALL icon
  variants and toggle CSS `display`, never touch `src` (salvaged 2026-09-18 from the retired
  `readerwrangler-project` skill; verify whether it still bites the current SVG icons before relying
  on it).

---

## THE GRAVEYARD — good ideas the archive proposed and nobody adopted (until now)

| Proposal | Proposed | Fate |
|---|---|---|
| PATTERNS.md / pattern library | v3.3.2 (2025-11-11) | **This file**, ten months later |
| Complexity budget (>3 iterations → review) | v3.3.2 (2025-11-11) | `feedback_debugging` Rule 2 (2026-08-30) |
| Feature-parity checklist for big refactors | v5.0.x (4 recommendations) | Still unbuilt — required for the next big-bang |
| Field-mapping reference doc | v3.8.0 (2025-12-20) | Superseded 2026-09-04: the test gate's import-mapping snapshot suite IS the field map, enforced |
| Automated test suite | v4.16.0, v5.0.0 | Deliberately deferred → **pre-launch test gate** (data paths only; PRELAUNCH-TEST-GATE.md) |
| Domain-boundary checklist (cross-component comms) | v3.8.0 (2025-12-20) | Superseded: Law 2 + the platform-facts section + MULTI-INSTANCE.md's universe model |
| Release-criteria checkpoint before dropping the suffix | v3.8.0 (2025-12-20) | Superseded: the CLAUDE.md release checklist + the CHANGELOG-past-Ron ("word") ritual |
| Trigger-based rule system | v3.x era | Abandoned — early models couldn't evaluate triggers reliably; replaced by CLAUDE.md behaviors + memory rules, which current models follow |
| Pre-build structural checklist / gate | implicit across many PMs | **Built 2026-09-17** — a `PreToolUse` hook fires an 11-point checklist on the first app edit each turn (the meta-principle made literal); `/sitemap` command mechanizes the class-of-sites comb |
| Overlay dismissal redesign (`<Dialog>`/`<Popover>` layer registry) | 2026-09-16 | **Designed** (DIALOG-DISMISSAL-AUDIT.md), deferred to its own branch; the audit found the defect is a *class* (~40 overlays, 3 Esc regimes); stopgap shipped 7.14.2, the class-fix awaits the primitive |

The pattern in the graveyard is the meta-principle again: proposals became real only when they became
mechanisms (a file that loads, a rule that fires, a checklist line). When adding to this document, add the
enforcement or expect the graveyard.

---

*Maintenance: when a post-mortem earns a new principle, add it here with its enforcement, same day. The
release checklist's "post-mortem → memory" step is where this file gets its updates.*
