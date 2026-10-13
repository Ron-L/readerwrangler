# Send to Production — REJECTED (2026-10-13)

**Status:** considered, partly built, **rejected** before any release (Ron, 2026-10-13). Nothing shipped; the branch held
no commits. This record exists so the idea — and the relay facts it uncovered — don't have to be re-discovered.

## The goal

Ron organizes his library on his local copy (contributor mode → the dev relay). To make readerwrangler.com match, he
saves a backup on localhost and restores it on readerwrangler.com. The idea: a **File → Send to Production…** command
(contributors only) that copies the local library + organization to the production relay in one deliberate step.

(It surfaced from a hazard: turning the contributor flag off in his regular localhost window reconnects that copy to
the production relay with his real credentials, and automatic saves would then write dev data to production. Flipping
the flag is not a sync — no control over *when*, *what*, or even *which direction*.)

## What was designed

1. **First idea — a temporary redirect (rejected by Ron).** Point the one shared relay connection at production for
   the duration of the send, and pause other relay activity meanwhile. Ron: it's a global flag with no lock — *"What if
   we add another caller later and forget to have Send to Prod pause it?"* Fail-open for every future caller. A
   per-call parameter was considered too: the send's public calls fan out into 20+ internal relay calls, and missing one
   would cause a **half-and-half write** (some pieces to production, some to dev).
2. **Second idea — a separate connection object (built, proven, then discarded with the feature).** `relay-client.js`
   wrapped in a factory, `createRelayClient(fixedServerUrl)`; `RWRelay` = the instance for the page's normal server
   (every existing caller unchanged); `RWRelay.forServer(url)` = a separate instance with its own credentials, key and
   caches, **pinned** to that server. Nothing shared changes state, so nothing needs pausing and no future caller can
   be redirected by accident. Verified: all 19 network calls in the file go through `workerUrl()`, and a Node probe
   with a fake browser showed the default instance → dev, the production instance → production, default again → dev.
   **If a second relay connection is ever genuinely needed, this is the design to use.**

## Why it was dropped

Preparing test steps, the *receiving* side was traced — and it doesn't behave the way the feature assumed
("readerwrangler.com picks it up with Import from Relay"):

- **The desktop app never applies organization from the relay.** It only *sends* device-state (folders, tags, Book
  Lists, Searches) for the phone to read; the desktop's only read is Relay Setup's connection test, which discards it.
- **Import from Relay merges; it doesn't replace.** It's built for "Amazon data comes in, your own edits win": user
  fields (tags, notes, ratings, price goals) keep the *local* value — and on readerwrangler.com "local" is the old
  production data.
- **A desktop that later saves automatically pushes its organization back**, overwriting whatever a send delivered.

Only **Restore** replaces everything (a time machine). So a working version needs a Restore-style step *on
readerwrangler.com* ("a full replacement arrived from your local copy — replace?"). Ron: *"If I have to open and run
the prod RW page, it is not saving me any work."* The only saving over today's routine would be skipping the file
picker — a lot of work for very little gain. And in practice Ron now uses the dev site on his phone and rarely visits
production at all, so syncing matters less.

## What remains

- **To make readerwrangler.com match dev:** Save Backup on localhost → Restore Backup on readerwrangler.com (unchanged).
- **To see dev data on the phone:** use the dev site — since 7.21.0, Relay Setup's phone-pairing code in contributor
  mode points there (it reads the dev relay). Caveat: the dev site runs untested changes first.

## Lesson

Trace the **receiving** side before proposing a feature that delivers something. "Readerwrangler.com picks it up"
pointed at a receiver that merges instead of replacing — the same class as PRINCIPLES' *"a design's 'reachable via Y'
must point at a Y that exists."*
