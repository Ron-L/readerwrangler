// integrity.js - Data integrity checks for ReaderWrangler
// v6.3.0 - Initial implementation
// Depends on: nothing (pure functions + localStorage)

const INTEGRITY_KEY = 'readerwrangler-integrity';

// Run all integrity checks against current books + folders.
// Pure function — no side effects, no state access.
// Returns:
//   correctedFolders: updated folder array with auto-fixable issues applied
//   autoFixed:        array of { type, description, books: [{id, title}] }
//   needsReview:      array of { type, description, ... }
//   checkedAt:        timestamp (ms)
const checkDataIntegrity = (books, folders) => {
    const autoFixed = [];
    const needsReview = [];

    // Deep-copy folder array so we can mutate safely
    let correctedFolders = folders.map(f => ({ ...f, bookIds: [...(f.bookIds || [])] }));

    // Build map of active (non-deleted) books
    const activeBookMap = new Map(
        books.filter(b => !b.isDeleted).map(b => [b.id, b])
    );

    // ── Check 1: Ghost folder references ─────────────────────────────────────
    // bookIds in folders that point to non-existent or deleted books
    let ghostTotal = 0;
    correctedFolders = correctedFolders.map(folder => {
        const valid = folder.bookIds.filter(id => activeBookMap.has(id));
        const removed = folder.bookIds.length - valid.length;
        if (removed > 0) {
            ghostTotal += removed;
            return { ...folder, bookIds: valid };
        }
        return folder;
    });
    if (ghostTotal > 0) {
        autoFixed.push({
            type: 'ghost-ref',
            description: `${ghostTotal} missing book reference${ghostTotal !== 1 ? 's' : ''} removed from folders`,
            books: []
        });
    }

    // ── Check 2: Duplicate bookId refs within a single folder ─────────────────
    let dupeRefTotal = 0;
    correctedFolders = correctedFolders.map(folder => {
        const seen = new Set();
        const deduped = folder.bookIds.filter(id => {
            if (seen.has(id)) { dupeRefTotal++; return false; }
            seen.add(id);
            return true;
        });
        return deduped.length !== folder.bookIds.length ? { ...folder, bookIds: deduped } : folder;
    });
    if (dupeRefTotal > 0) {
        autoFixed.push({
            type: 'duplicate-ref',
            description: `${dupeRefTotal} duplicate folder reference${dupeRefTotal !== 1 ? 's' : ''} removed`,
            books: []
        });
    }

    // ── Check 3: Homeless books ───────────────────────────────────────────────
    // Non-deleted books with no folder membership (design invariant: always in ≥1 folder)
    // 7.31.0 - the rule is fileHomelessBooks (below), shared with the check at every save (readerwrangler.js)
    const filed = fileHomelessBooks(books, correctedFolders);
    if (filed.homeless.length > 0) {
        correctedFolders = filed.folders;
        autoFixed.push({
            type: 'homeless',
            description: `${filed.homeless.length} book${filed.homeless.length !== 1 ? 's' : ''} with no folder — placed in Inbox`,
            books: filed.homeless
        });
    }

    // ── Check 4: Corrupted book objects (missing required fields) ─────────────
    // Cannot auto-fix — surface for review
    const corrupted = books.filter(b => !b.id || !b.asin || !b.title);
    if (corrupted.length > 0) {
        needsReview.push({
            type: 'corrupted',
            description: `${corrupted.length} book record${corrupted.length !== 1 ? 's' : ''} with missing required fields`,
            books: corrupted.map(b => ({ id: b.id || '(none)', title: b.title || '(no title)' }))
        });
    }

    // Note: duplicate ASINs (same book, multiple objects) are already detected and
    // surfaced by the existing Duplicates section in Data Status. Not duplicated here.

    return { correctedFolders, autoFixed, needsReview, checkedAt: Date.now() };
};

// 7.31.0 (TODO 20261115-1239 "A book left in no folder is caught the moment it happens…"; Ron, 2026-11-16) - THE rule for
// books in no folder: every book not in the Trash that no folder holds goes to the FRONT of the Inbox. One function, used
// by the load-time check above (Check 3) and by the check at every save (readerwrangler.js — Law 22). One pass over the
// folders and one over the books. Returns { folders, homeless: [{ id, title, author }] }; with none in no folder, the SAME
// folder list (nothing copied, nothing to save). The folders given are never changed. Without an Inbox, the books are
// still reported and the folders stay as they are. Tests: test/integrity.test.js (HOMELESS-).
const fileHomelessBooks = (books, folders) => {
    const filed = new Set();
    for (const f of folders) for (const id of (f.bookIds || [])) filed.add(id);
    const active = new Map(books.filter(b => !b.isDeleted).map(b => [b.id, b]));   // one entry per id, as Check 1 sees them
    const homeless = [...active.values()].filter(b => !filed.has(b.id))
        .map(b => ({ id: b.id, title: b.title, author: b.author || '' }));
    if (homeless.length === 0) return { folders, homeless };
    const ids = homeless.map(b => b.id);
    return {
        folders: folders.map(f => (f.id === '__inbox__' ? { ...f, bookIds: [...ids, ...(f.bookIds || [])] } : f)),
        homeless
    };
};

// Persist integrity results to localStorage (replaces previous results entirely)
const saveIntegrityResults = ({ autoFixed, needsReview, checkedAt }) => {
    try {
        localStorage.setItem(INTEGRITY_KEY, JSON.stringify({ autoFixed, needsReview, checkedAt }));
    } catch (e) {
        rwLog.log('warning', 'INTEG-07', 'Could not save the integrity check\'s results (storage full?)', { error: String(e) });
    }
};

// Load persisted integrity results. Returns null if none saved or they can't be used.
// Caller should NOT clear previous results on check failure (per design).
// 7.29.1 - through the one reader (uiHelpers.js readSaved). The two lists are checked too: the Data Status window reads
// their .length while it draws, so results without them would break the screen the moment it opened.
const loadIntegrityResults = () => {
    const saved = readSaved(INTEGRITY_KEY, null, 'object');
    return saved && Array.isArray(saved.autoFixed) && Array.isArray(saved.needsReview) ? saved : null;
};

// Node only (the function tests, test/integrity.test.js) — in the page these are plain script names
if (typeof module !== 'undefined' && module.exports) module.exports = { checkDataIntegrity, fileHomelessBooks };
