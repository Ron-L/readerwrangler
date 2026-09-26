// Unit tests for overlayRegistry.js — run: node test/overlayRegistry.test.js
// The overlay stack is the bug-prone heart of the dialog-dismissal system (ordering + cascade-close);
// RW has no browser test harness, so this Node gate locks its behavior. See DIALOG-DISMISSAL-AUDIT.md.
const assert = require('assert');
const reg = require('../overlayRegistry.js');

let passed = 0;
function test(name, fn) { reg._reset(); fn(); passed++; console.log('  ✓ ' + name); }

console.log('overlayRegistry tests:');

test('push/remove a single layer; topLayer + count track it', () => {
    assert.strictEqual(reg.topLayer(), null, 'empty stack has no top');
    assert.strictEqual(reg._count(), 0);
    const id = reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(reg._count(), 1);
    assert.strictEqual(reg.topLayer().id, id);
    reg.removeLayer(id);
    assert.strictEqual(reg._count(), 0);
    assert.strictEqual(reg.topLayer(), null);
});

test('hasModal is true only when a modal is on the stack', () => {
    assert.strictEqual(reg.hasModal(), false);
    const p = reg.pushLayer({ close: () => {}, kind: 'popover' });
    assert.strictEqual(reg.hasModal(), false, 'a popover alone is not a modal');
    const m = reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(reg.hasModal(), true);
    reg.removeLayer(m);
    assert.strictEqual(reg.hasModal(), false, 'removing the modal clears hasModal');
    reg.removeLayer(p);
});

test('topLayer is the most-recently pushed (LIFO ordering)', () => {
    reg.pushLayer({ close: () => {}, kind: 'modal' });
    const top = reg.pushLayer({ close: () => {}, kind: 'popover' });
    assert.strictEqual(reg.topLayer().id, top);
    assert.deepStrictEqual(reg._kinds(), ['modal', 'popover']);
});

test('removing a MIDDLE layer cascade-closes everything above it', () => {
    const closed = [];
    const a = reg.pushLayer({ close: () => closed.push('a'), kind: 'modal' });   // parent
    reg.pushLayer({ close: () => closed.push('b'), kind: 'popover' });           // child
    reg.pushLayer({ close: () => closed.push('c'), kind: 'popover' });           // grandchild
    reg.removeLayer(a);                                                          // close the parent
    assert.strictEqual(reg._count(), 0, 'the whole subtree is gone');
    // a's own close() is NOT invoked by removeLayer (its React unmount already ran / will run);
    // only the layers ABOVE it are closed by the cascade.
    assert.deepStrictEqual(closed, ['b', 'c'], 'only layers above the removed one are closed');
});

test('removing the TOP layer closes nothing else (no spurious cascade)', () => {
    const closed = [];
    reg.pushLayer({ close: () => closed.push('a'), kind: 'modal' });
    const b = reg.pushLayer({ close: () => closed.push('b'), kind: 'popover' });
    reg.removeLayer(b);
    assert.deepStrictEqual(closed, [], 'removing the top invokes no cascade closes');
    assert.strictEqual(reg._count(), 1);
});

test('removeLayer is idempotent (unknown / already-removed id is a no-op)', () => {
    const id = reg.pushLayer({ close: () => {}, kind: 'modal' });
    reg.removeLayer(id);
    reg.removeLayer(id);          // second remove must not throw
    reg.removeLayer(99999);       // never-existed id must not throw
    assert.strictEqual(reg._count(), 0);
});

test('closeTop calls the topmost close() and reports whether one existed', () => {
    let topClosed = false;
    reg.pushLayer({ close: () => {}, kind: 'modal' });
    reg.pushLayer({ close: () => { topClosed = true; }, kind: 'popover' });
    assert.strictEqual(reg.closeTop(), true);
    assert.strictEqual(topClosed, true, 'closeTop invoked the TOP layer close, not a lower one');
    reg._reset();
    assert.strictEqual(reg.closeTop(), false, 'closeTop on an empty stack returns false');
});

test('subscribers are notified on push and on remove', () => {
    let n = 0;
    const unsub = reg.subscribe(() => n++);
    const id = reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(n, 1, 'notified on push');
    reg.removeLayer(id);
    assert.strictEqual(n, 2, 'notified on remove');
    reg.removeLayer(id);           // no-op removal must NOT notify
    assert.strictEqual(n, 2, 'no notify on a no-op removal');
    unsub();
    reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(n, 2, 'unsubscribed callback is not called');
});

test('a throwing subscriber does not break the stack', () => {
    reg.subscribe(() => { throw new Error('boom'); });
    assert.doesNotThrow(() => reg.pushLayer({ close: () => {}, kind: 'modal' }));
    assert.strictEqual(reg._count(), 1);
});

console.log(`\n${passed} overlayRegistry tests passed.`);
