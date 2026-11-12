// logkit-settings.js — ReaderWrangler's settings for its logging module (logkit/logger.js, "Logging as its own module",
// 7.28.0). Loaded just BEFORE logkit/logger.js on every page that logs; it decides everything about RW that the module
// must not know. The module itself stays general (logkit/README.md).
//
// Wrapped in a function like the module: only window.LOGKIT_SETTINGS (and Node's exports, for the tests and the commit
// check) leave this file.
(function () {
'use strict';

// The areas (LOGGING.md §2). JavaScript has no enums; a frozen object is the standard stand-in. UI must be here: the
// module's own codes are UI-02…05. tools/message_codes.py reads this list (never a copy).
const LOG_AREAS = Object.freeze({
    BOOT: 'BOOT', SYNC: 'SYNC', IMPORT: 'IMPORT', BACKUP: 'BACKUP', STORE: 'STORE', INTEG: 'INTEG', FIELD: 'FIELD',
    MOVE: 'MOVE', UNDO: 'UNDO', COVER: 'COVER', PREF: 'PREF', PHONE: 'PHONE', UI: 'UI',
    // 2026-11-09 (Ron) - for the toasts none of the 13 fit: folders, Book Lists, Searches and tags as things (ORG); a
    // book's details (EDIT); Auto-Organize (AUTO); copying titles, authors, links, the email text (SHARE)
    ORG: 'ORG', EDIT: 'EDIT', AUTO: 'AUTO', SHARE: 'SHARE'
});

// THE short form of a Channel ID — first 8 … last 4, as Relay Setup shows it — used by the log's cleaner AND Relay Setup
// (rwLog.shortChannelId), so the two can never show one channel two ways, and two keys that share their first 8 still
// read differently (Ron, 2026-11-09: telling old credentials from new matters most when they've just changed).
function shortChannelId(id) {
    const s = id == null ? '' : String(id);
    return s.length > 12 ? `${s.slice(0, 8)}...${s.slice(-4)}` : s;
}

const settings = Object.freeze({
    product: 'ReaderWrangler',
    globalName: 'rwLog',  /* page-global: rwLog */        // the page's logger: window.rwLog (the comment tells the name check)
    elementIdPrefix: 'rw-log',                            // the banner and box: #rw-log-banner, #rw-log-critical
    areas: LOG_AREAS,
    pageLoadArea: 'BOOT',
    storageKey: 'readerwrangler-log',
    oldLevelKey: 'readerwrangler-log-level',              // the OLD remembered ?log= level (before 2026-11-09) — read once, then removed
    // The two switches (LOGGING.md §5 step 5.1 — Ron, 2026-11-09): remembered in this browser as 'on'; absent = off.
    switchKeys: Object.freeze({ errorBanner: 'readerwrangler-log-banner', logDetail: 'readerwrangler-log-detail' }),
    // What the cleaner takes out of everything kept or shown: Channel IDs → their short form; the Cloud Sync passphrase.
    idPattern: /\b([0-9a-f]{8})-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi,
    shortId: shortChannelId,
    secretLabel: '[passphrase]',                          // what the hidden passphrase shows as (the kit's own word: "[hidden]")
    secrets: () => {
        try {
            const r = JSON.parse(window.localStorage.getItem('readerwrangler-relay') || 'null');
            return r && r.passphrase ? [r.passphrase] : [];
        } catch (e) { return []; }
    },
    build: () => (typeof APP_VERSION !== 'undefined' ? APP_VERSION : undefined),   // eslint-disable-line no-undef
    // The critical box (wording: Ron, 2026-11-07). Neither alert blocks: "save a backup now" needs the menu reachable.
    critical: Object.freeze({
        title: 'ReaderWrangler hit a problem that may affect your library.',
        advice: 'To be safe, save a backup now: File → Save Backup. If ReaderWrangler stops responding, reload the page. '
            + 'If this keeps happening, press Copy details and send it to us through Feedback at the bottom of the window.',
    }),
    extraApi: Object.freeze({ shortChannelId }),          // rwLog.shortChannelId (Relay Setup, the phone)
});

if (typeof window !== 'undefined') window.LOGKIT_SETTINGS = settings;
if (typeof module !== 'undefined' && module.exports) module.exports = { settings, LOG_AREAS, shortChannelId };
})();
