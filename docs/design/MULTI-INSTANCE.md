# Multi-instance model: storage universes, writers, and guests

_Status: DECIDED 2026-08-30 (the folder-order-scramble forensics session). The guest guard +
field-preserving cache ship in 7.6.0-alpha.6; the read-only second tab (§4), the cross-browser
sequential-coherence check (§6, added 2026-09-22), and split view are designed-here, built-later.
This doc is the "Ron, Ron, Ron" reference for every future "two copies of RW touched the same
data" question._

---

## 1. The universe model

Browser storage (localStorage AND IndexedDB) is isolated **per browser × per profile × per site
address**. Every cell in that grid is a separate universe: localhost-in-Chrome,
readerwrangler.com-in-Chrome, localhost-in-Firefox, the installed PWA (which snapshots its install
address) — none can touch another. ALL same-universe residents share everything, instantly,
last-writer-wins, with no notification to other tabs.

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

## 4. Two desktops, same universe: the read-only second tab (designed, not built)

localStorage is last-writer-wins; a second desktop tab holds its ENTIRE organization in memory,
and one innocent edit writes the whole stale world over everything done since it loaded. Design
(ratified 2026-08-30):

- **Leader election via the Web Locks API**: first tab acquires the writer lock; later tabs open
  **read-only** (badge/border, mutation tools disabled; view changes allowed — presentation is
  per-tab app config, not data — but a viewer's view tweaks stay IN MEMORY, never written to the
  shared settings key). Lock releases automatically on tab close OR crash — no heartbeat, no
  dying-gasp problem (Ron's design, upgraded from his timestamp scheme).
- **Promotion is explicit and reloads first**: writer gone → viewer offers "Take over editing?" →
  **reload from stores, then acquire lock, then enable writes**. Never silent, never on stale
  state (a snapshot quietly becoming writer would commit the exact clobber this doc exists to
  prevent). A read-only tab is never auto-promoted.
- **Live by default, freezable anytime**: viewer follows the leader via a storage/BroadcastChannel
  listener; its banner carries a ❄ Freeze/Resume toggle ("Following live" ↔ "Frozen at 6:04 PM").
  Rejected: asking frozen-vs-live at open — the user can't know yet, and the reference moment
  usually isn't the open moment; a toggle pins the snapshot exactly when it becomes meaningful.
- **Cross-tab drag stays forbidden**: "move between two folders side-by-side" needs the drop tab
  to write — that's a second writer in disguise. The real answer is an in-app **dual-pane/split
  view** (own TODO item). A live viewer is for watching, not dropping.

## 5. Relay semantics for multiple desktops (for the record)

Credentials = channel ID (shared mailbox address) + passphrase (encryption key). Two desktops on
one channel **cannot corrupt each other's library sync** (7.0: self-committing letters,
deterministic merge, atomic generations — RELAY-FLOWS scenario 6b) and both receive every fetcher
letter. BUT organization never travels desktop→desktop (it rides only the one-way mobile
snapshot), so their organizations drift apart forever and the phone mirrors whichever pushed
last. Verdict: not dangerous, just incoherent — give a second real desktop (e.g. the Firefox
experiment) its **own channel** unless collecting the same fetcher data twice is the goal.

## 6. Sequential coherence across browsers: check-on-activation + soft lease (designed 2026-09-22, built-later)

**The footgun this closes.** A clever user restores Browser A's backup into Browser B to "keep them
in sync" — which copies the channel ID + passphrase, so now two desktops write the same channel.
§5 says this cannot *corrupt* the library sync (7.0 letters + merge), but the organization drifts
(each pushes its own monolithic device-state blob; the phone mirrors whichever pushed last), and
**the user is never told** — a silent mismatch between "I have sync" and what RW actually provides.
This section is the enforced, honest fix.

**Non-goal — live two-way concurrent sync (rejected on the ratio, 2026-09-22).** Medium value ÷
huge effort = a bad quotient. It needs two expensive things RW doesn't have: (a) **push** — the
relay is Cloudflare KV + a stateless worker (write keys, *poll* to read); real-time push means
Durable Objects holding a WebSocket per channel, i.e. the never-built "Phase 2" relay; and (b) a
**merge for organization** — folder hierarchy + order + pins + multi-placement are relational and
ordered, so concurrent moves/reorders are the textbook-hard CRDT cases, in the one domain where a
merge bug silently corrupts a user's whole organization. The monolithic last-writer-wins blob
exists precisely to dodge that merge. Not worth it.

**The insight that makes it cheap:** the user is one person at one machine at a time. The real need
is **sequential** coherence — "whichever browser I sit down at next continues from my latest" — not
live concurrency. You only need the truth *at the transition* (idle→in-use), so a check-on-activation
replaces a live feed, and no push is required.

The design:

1. **One "am I the editor?" concept, two enforcement layers.** Same-browser tabs → the §4 Web Locks
   lease (hard, auto-releasing on close/crash). Cross-browser → a **soft relay lease** record (holder
   instance id + heartbeat/timestamp). Soft = advisory, not a mutex (KV is eventually-consistent and
   rate-limited; two claims in the same instant could both think they won) — acceptable because this
   guards a *single-user footgun*, not adversarial contention. Not security, just a guard.
   **The lease is the safety net, and it is NOT focus-driven** — two physical computers can both stay
   focused, neither ever blurs, so a focus trigger would never re-fire. Instead:
   - **Write-gated on the lease (the floor):** every mutation checks "do I currently hold the lease?"
     *at commit time* and refuses + flips to read-only if not. This prevents the clobber no matter how
     many browsers stay focused — B cannot write over A while A holds the pen.
   - **A light periodic lease poll while active** (~15–30 s): so a browser's read-only/editor UI stays
     honest without a focus event — B, sitting focused, sees A holds the lease; if A goes idle and its
     lease expires, B can offer takeover. Bounded (only while the tab is active), one tiny KV read — not
     the Tier-2 push infra creeping back in.

2. **Org-freshness check — lazy, on activation.** This is separate from the lease (point 1) and has a
   different cadence: you only need to see the latest *organization* when you sit down at a browser. On
   idle→in-use (`visibilitychange` / window focus), fetch the relay device-state and compare its
   **serialized-state stamp** (`organization.savedAt` — the §3 guard's stamp, the timestamp OF THE STATE
   SERIALIZED, never wall-clock) to the last stamp this browser adopted or pushed (stored locally). Relay
   stamp newer → this browser is **behind**. For *this* check, one read on activation (no poll loop) is
   enough — you don't care about staleness while you're away from the machine. (The lease, by contrast,
   *is* refreshed periodically while active — point 1 — precisely because focus can't cover two focused
   computers.)

3. **Prompt only when there's a decision** (Law 16, inverted — don't surface a control with nothing
   to choose). In sync, or *ahead* (this browser was the last editor), with the lease free → silently
   become the editor, no nag. Prompt only when **behind**, or the lease is held by a live instance.

4. **Intent-shaped choice, not two raw toggles.** "Sync?" and "take the lease?" are one intent to the
   user. When a behind browser activates:
   > *"Another browser has been organizing your library — this one is showing an older view."*
   > **Catch up & edit here** (adopt latest + take the lease — the "I've moved to this machine" case)
   > · **Just view** (adopt latest, stay read-only) · **Leave as-is**

5. **Adopt = the real work.** "Catch up" reconstitutes *this* browser's folders/lists/order/tags from
   the relay blob. The phone already rebuilds a *view* from a device-state blob, but the desktop has
   never applied one to its own **editable** state (today `getDeviceState` on the desktop is only a
   connection test — readerwrangler.js:1246). Reuse §4's discipline: **reload-from-state, then acquire
   the lease, then enable writes — never promote on stale state.** The monolithic blob is authoritative
   and single-writer (the lease guarantees one writer), so **nothing needs merging.**

6. **The one honest cost.** If someone genuinely edits two browsers in overlapping sessions, the
   second is read-only until an explicit handoff, and taking over reloads — discarding that viewer's
   in-memory tweaks. §4 already accepts this as correct (a snapshot silently becoming writer commits
   the exact clobber this doc exists to prevent). That is the single-writer contract, stated plainly.

**New surfaces this needs:** a small per-channel **lease record** on the relay (holder + heartbeat),
and a real desktop **device-state adopt path** (distinct from today's connection-test read). The
"catch up / view / leave" prompt is a new modal → `anyDialogOpen` + `handleModalEsc` + ✕ + backdrop
(or the `<Dialog>` primitive once it lands).

## 7. Loose ends tracked elsewhere

- **F1 consolidation** (folders → blob-only + load reorder) — TODO, unchanged by today: the
  double-store made diagnosis harder even though it wasn't the thief.
- **Mobile's IndexedDB books write**: now gated by the guest guard, but the field-shape mapping
  (`mapBackupBook` vs desktop book records) still deserves an audit — TODO.
- **`rw_folders`** (41 KB): orphan localStorage key no code reads or writes. Archaeology; inspect
  before deleting.
