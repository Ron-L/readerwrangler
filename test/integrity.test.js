// Function tests for integrity.js's "books in no folder" rule. Run: node test/integrity.test.js
// tags: integrity, folders, tier 1
// covers: integrity.js
// 7.31.0 (TODO 20261115-1239 "A book left in no folder is caught the moment it happens…"; Ron, 2026-11-16): the rule
// behind the load-time check's "Homeless books" (Check 3) is ONE function, fileHomelessBooks, used by the load-time
// check AND by the check at every save (readerwrangler.js) — Law 22. The save-time check's screen test:
// test/ui/test_no_folder.py (NOFOLDER-).
'use strict';
const assert = require('assert');
const { test, done } = require('./harness');
const I = require('../integrity.js');

const book = (id, extra) => ({ id, asin: id, title: `Title ${id}`, author: `Author ${id}`, ...extra });
const BOOKS = [book('a'), book('b'), book('c'), book('d', { isDeleted: true })];
const FOLDERS = [
    { id: '__inbox__', name: 'Inbox', bookIds: ['x'] },
    { id: 'f1', name: 'One', bookIds: ['a'] },
];

console.log('integrity tests:');

test('HOMELESS-001', 'books in no folder (the Trash\'s excepted) go to the FRONT of the Inbox; other folders untouched', () => {
    const { folders, homeless } = I.fileHomelessBooks(BOOKS, FOLDERS);
    assert.deepStrictEqual(homeless.map(b => b.id), ['b', 'c'], 'b and c — not d, which is in the Trash');
    assert.deepStrictEqual(homeless[0], { id: 'b', title: 'Title b', author: 'Author b' }, 'each with its id, title and author');
    assert.deepStrictEqual(folders.find(f => f.id === '__inbox__').bookIds, ['b', 'c', 'x']);
    assert.strictEqual(folders.find(f => f.id === 'f1'), FOLDERS[1], 'a folder with nothing to change is the same folder');
    assert.deepStrictEqual(FOLDERS[0].bookIds, ['x'], 'the folders given are never changed');
});

test('HOMELESS-002', 'nothing in no folder: the SAME folder list back — nothing copied, nothing to save', () => {
    const all = [{ id: '__inbox__', name: 'Inbox', bookIds: ['b', 'c'] }, { id: 'f1', name: 'One', bookIds: ['a'] }];
    const { folders, homeless } = I.fileHomelessBooks(BOOKS, all);
    assert.deepStrictEqual(homeless, []);
    assert.strictEqual(folders, all);
});

test('HOMELESS-003', 'no Inbox: the books are still found (and reported) — the folders stay as they are', () => {
    const { folders, homeless } = I.fileHomelessBooks(BOOKS, [FOLDERS[1]]);
    assert.deepStrictEqual(homeless.map(b => b.id), ['b', 'c']);
    assert.deepStrictEqual(folders.map(f => f.id), ['f1']);
});

test('HOMELESS-004', 'the load-time check uses the same rule: its "with no folder — placed in Inbox" repair is this one', () => {
    const r = I.checkDataIntegrity(BOOKS, FOLDERS);
    const fix = r.autoFixed.find(f => f.type === 'homeless');
    assert.deepStrictEqual(fix.books, I.fileHomelessBooks(BOOKS, FOLDERS).homeless);
    assert.strictEqual(fix.description, '2 books with no folder — placed in Inbox');
    assert.deepStrictEqual(r.correctedFolders.find(f => f.id === '__inbox__').bookIds, ['b', 'c'],
        'at the front of the Inbox — "x" (no book at all) taken out first, by Check 1');
});

done();
