# Glossary — the words ReaderWrangler shows users

_The single list of user-facing terms (Ron, 2026-11-04: "show me our legend / terms / glossary"). **Decided** terms
come from their decision records; **proposed** ones are under discussion and change status here when decided. Words
users never see (IndexedDB, JSON, localStorage, tombstone, Relay, "Sync now"…) are listed at the end._

_**Read this before writing any words a person sees** — a message, a button, a help line, a page, the CHANGELOG (Ron,
2026-11-12: CLAUDE.md points here; every agent brief that touches words names this file). A new term, or a change, is
proposed here first and decided by Ron. (Until 2026-11-12 this header said the User Guide's glossary is built from this
list — no page had a glossary; a page built from this file is TODO "A glossary page on the site, built from
GLOSSARY.md".)_

## On screen today — until the Cloud Sync rename ships

Until the rename ships (TODO "Cloud Sync: rename Relay…"), the app still shows **Relay, Credentials, Channel ID,
Passphrase, Import from Relay, Download Library / Download Collections** — mirror those exact words on the surfaces
that show them (don't invent "Cloud Storage"); they become the Cloud Sync words below when the rename ships. **Plain
"cloud" is fine in ordinary prose** ("syncs through the cloud") — the 2026-08-28 vocabulary rule (7.0.1–7.4.0
post-mortem).

## Cloud Sync (decided 2026-10-23 — docs/design/CLOUD-SYNC-NAMING.md; building it: TODO "Cloud Sync: rename Relay…")

| Term | Meaning | Status |
| --- | --- | --- |
| **Cloud Sync** | The service that carries your library and organization between your computer, your phone and the bookmarklet, encrypted end to end. Replaces "Relay". | Decided |
| **Cloud Sync Setup** | The window where you set it up (was Relay Setup). | Decided |
| **Cloud Sync Key** | The one secret that opens your cloud library: `RW1-` + 13 groups of 5 characters. Replaces Credentials / Channel ID / Passphrase. Whoever has it can read **and change** your cloud copy. | Decided |
| **Support code** | The last 6 characters of the key's ID, shown beside the key — safe to quote to support. | Decided |
| **Save Key** | Save the key you typed (was "Save Credentials"). | Decided |
| **Make a new key** | Replace your key and lock out the old one ("change the locks"); your books and folders stay as they are. | Decided |
| **Import** (from Cloud Sync) | The click that brings new data in — never "Sync now". | Decided |
| **Send Library / Send Collections to ReaderWrangler** | The bookmarklet's buttons on Amazon's page. | Decided |
| **the sync server** | The server, on the security and site pages (was "relay server"). | Decided |
| **your cloud library** | What your Cloud Sync Key opens, held by Cloud Sync — **always encrypted**, readable only with your key in your ReaderWrangler or your bookmarklets. Two purposes: **(1) the relay** between your Amazon fetches and the app (and the phone); **(2) a backup** of your books and organization — *books today; your organization once the app can take it back (TODO "Keep your tabs and browsers in step…"); until then, Save Backup is your backup.* A **new key means a new cloud library** — no problem: your next fetch and your next change fill it (set up the bookmarklet and phone again — the old key is built into them); "Make a new key" deletes the old one right away, and a cloud library nobody uses for a year is deleted (planned). Inside it: two copies — the Fetched Copy and the Complete Copy (see "Our working names"). | Decided 2026-11-04 (Ron); **renamed 2026-11-23** (Ron) from "your cloud copy" — "copy" now means only one of its two parts |

## Backups

| Term | Meaning | Status |
| --- | --- | --- |
| **Save Backup / Restore Backup** | A file of your whole library and organization — never "Import/Export". Restore **replaces** what this browser has. | Decided (CLAUDE.md) |
| **key password** | An optional password that **locks the Cloud Sync Key inside your backups**, so sharing a backup file doesn't share access to your cloud library. Forgetting it loses nothing but the key (restore everything else; enter the key or make a new one). | Decided 2026-11-04 (not "backup password" — reads as "protects the backup" or "a spare password"); menu **File → Key Password…** |
| **lock** (the key) | What the key password does — chosen over "scramble" (sounds undoable by anyone) and "encrypt" (that's what Cloud Sync does). | Decided 2026-11-04 |
| **Save as Spreadsheet** | Your books as a spreadsheet file (CSV) — no key, no organization. | Decided (7.10) |

## In the app

| Term | Meaning | Status |
| --- | --- | --- |
| **All Books** | A **view** of every book, not a folder ("shortcut" / "Linked Copies" retired). | Decided (User Guide review, 2026-10-23) |
| **Folders · Book Lists · Searches** | Where you organize: folders hold books; Book Lists are hand-picked lists; Searches are saved filters. | Decided (6.12) |
| **Inbox · Trash** | Landmarks: new books arrive in the Inbox; deleted books wait in the Trash. | Decided |
| **Tags** | Your own labels in ReaderWrangler. | Decided |
| **Amazon tags** | Amazon's genre tags for a book ("Magical Realism", "Spine-Chilling Horror") — always prefixed "Amazon" so they're never confused with your tags. | Decided 2026-11-03 |
| **Collections** | Your Kindle collections, brought in from Amazon (edited on your Kindle / Amazon, not in the app). | Decided |
| **Data Status** | The File-menu indicator of how fresh your library data is — not a sync status. | Decided |
| **Toast** | The small floating message near the status bar (not a window). | Decided (CLAUDE.md) |
| **View on Amazon** | Opens the book's Amazon page. | The app's label (checked 2026-11-02) |
| **Read in Kindle** | Opens the book to read (Kindle app on Android; Cloud Reader elsewhere). | Decided 2026-11-02 (not built) |
| **bookmarklet** | The button you drag to your bookmarks bar that fetches from Amazon's pages. Kept — no plainer word. | Decided |
| **update your library from Amazon** | Running the bookmarklet on Amazon's page to bring your books in — the act, in messages ("…the next time you update your library from Amazon"). Replaces "run the fetcher": the TOOL is **the bookmarklet**, the ACT is this — "fetcher" is retired (Ron, 2026-11-12, review queue Q-033/Q-034). First used in 7.28.1's owned-book boxes; the rest of the app, the help pages and the User Guide still say "the fetcher" until the Cloud Sync rename's sweep, which the anti-glossary then enforces. | Decided 2026-11-12 (Ron) |

## Our working names — for docs, code and our talk (internal)

_Muddled names lead to muddled thinking (Ron, 2026-11-22, during outside review 3). Mostly not shown to people — they
see "your cloud library". Named by **what the thing holds or is**, not who writes it or what device shows it, so the names
stay true if the writers change (the phone may edit one day)._

| Term | Meaning | Replaces (retired when the rename migrates — TODO "Our working names in the code and docs…") | Status |
| --- | --- | --- | --- |
| **Fetched Copy** | The copy of your **books** in your cloud library, as fetched from Amazon — fed by the bookmarklet's uploads, read by Import. Holds no organization. **After a Restore Backup, it starts from the backup's books, your edits included** (Ron, 2026-11-23). | "the canonical", "canonical library", "generations" (of the library), "the cloud's library copy" | Decided 2026-11-22 (Ron) |
| **Complete Copy** | The copy of **everything** in your cloud library — books, organization and your own fields — written by the app, read by the compact view (and, once "Keep your tabs and browsers in step" is built, by any browser that's behind). | "device-state", "dstate", "the phone's copy", "the mobile payload" | Decided 2026-11-22 (Ron) |
| **version** | One saved state of a copy. Each copy keeps its newest versions (today two; one between saves once the pointer keeper is built — MULTI-INSTANCE.md §4). The three levels never share a word: **cloud library** → its two **copies** → their **versions**. | "generation" (the code's word), "copy" when it meant a saved state | Decided 2026-11-23 (Ron) |
| **compact view** | ReaderWrangler on a small screen (a window under 768 pixels wide — a phone, or a narrow computer window): `mobile.js`. | "the phone page", "mobile app", "mobile viewer", "the phone" (when it means the view, not the device) | Decided 2026-11-22 (Ron) |
| **full view** | ReaderWrangler on a wider screen — everything: `readerwrangler.js`. | "the desktop app", "desktop" (when it means the view) | Decided 2026-11-22 (Ron) |

## Words users never see

Relay · Credentials · Channel ID · Passphrase (until the rename ships, they're still on screen) · "Sync now" ·
"Import/Export" for backups · IndexedDB · JSON · localStorage · tombstone · mailbox · storage bucket · "your cloud copy"
(now "your cloud library", 2026-11-23).
