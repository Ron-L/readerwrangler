# Multi-instance model: storage universes, writers, and guests

_Status: DECIDED 2026-08-30 (the folder-order-scramble forensics session). The guest guard +
field-preserving cache ship in 7.6.0-alpha.6; keeping tabs and browsers in step (§4 — rewritten 2026-11-02 as ONE
mechanism for both, replacing the read-only second tab and the cross-browser lease of §6) and split view are
designed-here, built-later (TODO "Keep your tabs and browsers in step…").
This doc is the "Ron, Ron, Ron" reference for every future "two copies of RW touched the same
data" question._

---

## 1. The universe model

Browser storage (localStorage AND IndexedDB) is isolated **per browser × per profile × per site
address**. Every cell in that grid is a separate universe: localhost-in-Chrome,
readerwrangler.com-in-Chrome, localhost-in-Firefox, the installed PWA (which snapshots its install
address) — none can touch another. ALL same-universe residents share everything, instantly,
last-writer-wins. (Corrected 2026-11-02: a localStorage write DOES notify the other tabs — the browser fires a
`storage` event there; an IndexedDB write doesn't. Today nothing listens.)

Residents of one universe and what they write:

| Resident | Writes | Notes |
|---|---|---|
| Desktop app | FOLDERS_KEY, org blob (STORAGE_KEY), EXPLORER_KEY, IndexedDB books, device-state → relay | The owner |
| Mobile app | The SAME folder/org keys + IndexedDB books (its offline cache) | **Reads the relay, never writes it.** Renders FROM its cache, not from the payload |
| Relay | nothing local | Post office, not a resident |

Mobile shares desktop's keys deliberately: on a phone it's the only resident, the cache makes
boot instant + offline work, and the Desktop Mode switch finds a library waiting.

## 2. The 2026-08-30 post-mortem (three-layer bug, all layers confirmed live)

1. **Fragile base**: Ron's root folder order existed only as IMPLICIT ARRAY ORDER — no `sortIndex`
   on any root folder (backups carried order as array position). Any array rewrite scrambled the
   display to raw creation order ("Jim Butcher first").
2. **The thief**: mobile's `restoreOrganization` cached the relay payload through an **allow-list
   field map that stripped `sortIndex`** (same bug class as restore bug #3), and wrote it over the
   desktop keys **stamped `savedAt: Date.now()`** — relay-lagged, field-stripped data masquerading
   as fresh local truth. Every mobile load on localhost re-scrambled (explains the 2026-08-15
   ghost, the "fresh code" correlation — new alpha → test mobile — and the bake dying in 20 min).
3. **Exonerated**: localStorage quota (217 KB total), the integrity checker (spreads preserve
   fields), the wire (the push serializes folders with a deny-list spread — sortIndex travels).

**Vaccine** (applied live): one Move-to-Top gesture renumbers ALL roots via the canonical reorder —
order becomes explicit `sortIndex`, array rewrites stop mattering. **Any scramble after alpha.6
means something actively rewrote explicit indices — run the forensic snippet immediately.**

## 3. The guest guard (7.6.0-alpha.6)

**Rule: a resident may only overwrite the shared cache with data NEWER than the cache.**

- The desktop push **source-stamps** `organization.savedAt` with the org blob's own `savedAt` —
  the timestamp OF THE STATE SERIALIZED, not the send time. (A wall-clock send stamp would be
  newer than the blob it was built from and the guard would misfire — hole found by Ron.)
- Mobile caches the payload (org keys AND IndexedDB books — both writes gated together) only when
  `payload.organization.savedAt > localBlob.savedAt`, and **re-stamps its cache write with the
  payload's source stamp**, never `Date.now()` — one clock lineage (the desktop's), monotone
  comparisons forever. (Second hole found in self-check: a wall-clock mobile stamp would exceed
  every later payload stamp and freeze the phone's cache.)
- Mobile's field map becomes a deny-list spread (`{ ...f, bookIds: filtered }`): `sortIndex`,
  `isInbox`, `description`, future `pinned` survive automatically.

Consequences by universe:
- **Phone** (mobile-only resident): cache carries the last payload's stamp; every newer push wins;
  behavior unchanged.
- **Dev machine** (desktop + mobile emulation share localhost): desktop blob is stamped at local
  edit time, always ≥ any payload's source stamp → mobile **never writes** → and since mobile
  renders from cache, dev-mobile displays the (fresher) local data. Both properties desirable.
- **Transition**: unstamped payloads (pushed pre-alpha.6) are treated as stamp 0 → never overwrite
  an existing blob; a truly EMPTY universe (new phone pairing, nothing to protect) accepts even an
  unstamped payload so first-pairing against an old payload still works.

**Rejected: separate cache keys for mobile.** Would isolate equally well but breaks phone Desktop
Mode (desktop code would find no library) — the guard achieves the same protection with no
feature loss. Held in reserve if the guard ever leaks.

## 4. Tabs and browsers in step: one mechanism (designed 2026-11-02, not built)

_Replaces the 2026-08-30 read-only second tab (Web Locks leader election, "Take over editing?") and the 2026-09-22
cross-browser check-on-activation + soft lease (§6). Both are in git history. Decided in the TODO review (Ron +
Claude), re-read through Law 18 — a stopping prompt or a locked tab is still a block._

**The problem is one problem in two places.** A copy working from an old state overwrites a newer one:
- **Two tabs, same universe:** localStorage is last-writer-wins; a second tab holds its ENTIRE organization in
  memory, and one innocent edit writes the whole stale world over everything done since it loaded. Stale *in memory*.
- **Two browsers/computers, one channel** (e.g. a backup restored into a second browser — it carries the
  credentials): each pushes its own monolithic device-state blob; the organizations drift apart, the phone mirrors
  whichever pushed last, and **the user is never told**. Stale *in its own storage*.

**The insight (kept from §6):** one person sits at one machine at a time. The need is **sequential** coherence —
"whichever tab or browser I use next continues from my latest" — not live concurrency.

**The four states are the same everywhere:** in sync · behind · ahead · both changed (since the last version both
saw). Model them as one state machine, not flags.

**The mechanism — compare before you overwrite:**
1. Every saved copy of the organization carries a version stamp — the blob's own `savedAt` (the timestamp OF THE
   STATE SERIALIZED, §3's lineage, never wall-clock at send).
2. Every write says "I'm replacing the version I last saw" and is refused if that has changed. Two places:
   - **this browser's storage** — compare the stored `savedAt` with the one this tab last loaded or wrote, before
     each organization write;
   - **the cloud copy** — an optional "expect" generation on the device-state pointer flip (`handlePutPointer`); the
     worker answers 409 if the pointer has moved. KV takes up to ~a minute to agree everywhere, so this is a guard
     for one person moving between machines, not a lock (the same honesty the lease had).
3. **The responses (the same everywhere):**
   - **behind, with no changes of its own** → catch up silently; toast *"Caught up with changes from your other tab /
     browser"* + **Undo**;
   - **ahead or in sync** → nothing;
   - **both changed** → a banner, not a modal (you keep working): **Use the other one's** / **Keep this one's**; this
     copy sends nothing to the cloud until you choose.

**What differs by place — only how a copy hears, and how it catches up:**

| | Hears | Catches up by |
|---|---|---|
| Tab | At once, free: the `storage` event (the app saves the organization on every change) | Reloading from storage |
| Browser | On return (`visibilitychange` / focus: one read of the device-state pointer — the phone's freshness check, `getDeviceStatePointerGen`) or when the cloud refuses a send | Taking the cloud copy — which writes its storage, which brings its other tabs along |

The layers stack: a browser catching up from the cloud IS a storage write, so its tabs follow by the tab rule.

**Why the gatekeepers went:**
- **The read-only second tab** blocked editing where you are (even "Edit here instead" was a click to get permission).
  With compare-before-overwrite every tab can stay a writer, because a stale one is refused and catches up instead
  of clobbering. Between tabs "both changed" is close to impossible — saves and notices are both instant.
- **The soft lease** needed a per-channel record kept fresh by heartbeat: a KV write every 15–30 s per active user
  (~120/hour, against ~1,000 writes/day on the free plan — the 7.x write diet undone). Compare-at-send needs no
  record and no extra writes, and it also covers two computers that both stay focused (the case the lease's poll was
  for): the second one's send is refused.

**Kept:**
- **❄ Freeze** (Ron, 2026-08-30): a tab can be frozen as a reference snapshot ("Frozen at 6:04 PM"); it stops catching
  up, and a frozen tab doesn't edit or send. Resume = catch up. (Asking frozen-vs-live at open stays rejected — the
  reference moment usually isn't the open moment.)
- **Never write from stale state** — catch-up reloads first, then enables writes.

**Duplicate sends:** a tab sends to the cloud only when the stored version differs from the last one sent (recorded in
the shared storage), so two in-step tabs don't both push as you leave them.

**Taking the cloud copy is the real work:** the phone rebuilds a *view* from a device-state blob, but the desktop has
never applied one to its own editable state — today it reads it only in the Relay Setup connection test
(readerwrangler.js ~1845). The monolithic blob is authoritative, so nothing needs merging.

**Still to decide when building:**
1. **Undo after catching up** — the tab's older undo steps refer to the pre-catch-up state; undoing one must not bring
   old state back. Lean: catching up starts a fresh undo history, the catch-up itself its one step. Check
   UNDO-MODEL.md first.
2. **Mid-gesture** — a tab mid-drag or with the book details window open catches up when that ends.
3. **Books live in IndexedDB** (written whole, apart from the organization) — the compare must cover them too, or
   one stamp covers both.
4. **Cross-tab drag** — no longer a second writer in disguise (both tabs are current); allow it or not? Decided in TODO
   "Two-pane split view" (2026-11-03): two windows side by side first, including whether a drag between them can
   finish a move; the in-app split view only if that falls short.

**Non-goal — live two-way concurrent sync** (rejected on the ratio, 2026-09-22): it needs (a) **push** — the relay is
KV + a stateless worker, so real-time means Durable Objects holding a WebSocket per channel — and (b) a **merge for
organization**: hierarchy + order + pins + multi-placement are the textbook-hard CRDT cases, in the one domain where a
merge bug silently corrupts a user's whole organization. The monolithic last-writer-wins blob exists to dodge that.

**Test (browser driver):** two real tabs — edit in A; B catches up with the toast; Undo; nothing lost; one send. Then
two throwaway browsers on one test channel — edit in A, return to B → caught up; edit both → banner, and no
overwrite either way.

## 5. Relay semantics for multiple desktops (for the record)

Credentials = channel ID (shared mailbox address) + passphrase (encryption key). Two desktops on
one channel **cannot corrupt each other's library sync** (7.0: self-committing letters,
deterministic merge, atomic generations — RELAY-FLOWS scenario 6b) and both receive every fetcher
letter. BUT organization never travels desktop→desktop (it rides only the one-way mobile
snapshot), so their organizations drift apart forever and the phone mirrors whichever pushed
last. Verdict: not dangerous, just incoherent — give a second real desktop (e.g. the Firefox
experiment) its **own channel** unless collecting the same fetcher data twice is the goal.

## 6. Sequential coherence across browsers (2026-09-22) — folded into §4 on 2026-11-02

This section designed the cross-browser half separately: a check on returning to a browser (kept — §4's "hears on
return"), a **soft relay lease** with a 15–30 s poll and a write gate on holding it, and a three-choice prompt
(*Catch up & edit here / Just view / Leave as-is*). The 2026-11-02 review replaced the lease with compare-at-send (no
record, no heartbeat writes, covers two focused computers too) and the prompt with a silent catch-up + Undo (Law 18),
and saw that tabs and browsers are one problem — so the whole design now lives in §4. Its insight (sequential, not
live, coherence) and its non-goal (live two-way sync) moved there. The original text is in git history.

## 7. Loose ends tracked elsewhere

- **F1 consolidation** (folders → blob-only + load reorder) — TODO, unchanged by today: the
  double-store made diagnosis harder even though it wasn't the thief.
- **Mobile's IndexedDB books write**: now gated by the guest guard, but the field-shape mapping
  (`mapBackupBook` vs desktop book records) still deserves an audit — TODO.
- **`rw_folders`** (41 KB): orphan localStorage key no code reads or writes. Archaeology; inspect
  before deleting.
