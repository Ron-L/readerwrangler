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

test('closeTop forwards its reason to the top layer close()', () => {
    let seen = 'none';
    reg.pushLayer({ close: (reason) => { seen = reason; }, kind: 'modal' });
    reg.closeTop('esc');
    assert.strictEqual(seen, 'esc', 'reason is passed through to the layer close');
    reg._reset();
    let seen2 = 'none';
    reg.pushLayer({ close: (reason) => { seen2 = reason; }, kind: 'modal' });
    reg.closeTop();
    assert.strictEqual(seen2, undefined, 'no reason → undefined (backward compatible)');
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

test('pushLayer carries an optional nodeRef through to the layer record', () => {
    const nodeRef = { current: 'PANEL_NODE' };
    reg.pushLayer({ close: () => {}, kind: 'modal', nodeRef });
    assert.strictEqual(reg.topLayer().nodeRef, nodeRef, 'topLayer exposes the nodeRef for scoped Ctrl+A select-all (and the planned focus-trap pass)');
    const plain = reg.pushLayer({ close: () => {}, kind: 'popover' });
    assert.strictEqual(reg.topLayer().nodeRef, undefined, 'nodeRef is optional');
});

test('a throwing subscriber does not break the stack', () => {
    reg.subscribe(() => { throw new Error('boom'); });
    assert.doesNotThrow(() => reg.pushLayer({ close: () => {}, kind: 'modal' }));
    assert.strictEqual(reg._count(), 1);
});

test('isTopmostModal: top modal true; a modal above unseats it; popovers above do NOT', () => {
    const m1 = reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(reg.isTopmostModal(m1), true, 'lone modal is the topmost modal');
    reg.pushLayer({ close: () => {}, kind: 'popover' });
    assert.strictEqual(reg.isTopmostModal(m1), true, 'a popover above does NOT unseat the top modal');
    const m2 = reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(reg.isTopmostModal(m1), false, 'a modal above unseats it');
    assert.strictEqual(reg.isTopmostModal(m2), true, 'the upper modal is now topmost');
    assert.strictEqual(reg.isTopmostModal(99999), false, 'unknown id is not topmost');
});

test('fence: modals and menus fence by default; a popover does not unless it opts in', () => {
    assert.strictEqual(reg.hasFence(), false, 'empty stack fences nothing');
    const pop = reg.pushLayer({ close: () => {}, kind: 'popover' });
    assert.strictEqual(reg.hasFence(), false, 'a plain popover does NOT fence');
    const hist = reg.pushLayer({ close: () => {}, kind: 'popover', fence: true });
    assert.strictEqual(reg.hasFence(), true, 'an opted-in popover fences (toast history)');
    assert.strictEqual(reg.hasModal(), false, 'opting a popover into the fence does NOT make it a modal (no dimming effects)');
    reg.removeLayer(hist);
    assert.strictEqual(reg.hasFence(), false, 'fence lifts when the fencing popover closes');
    reg.removeLayer(pop);
    const menu = reg.pushLayer({ close: () => {}, kind: 'menu' });
    assert.strictEqual(reg.hasFence(), true, 'a menu fences by default (alpha.44 — right-click menus block library keys)');
    reg.removeLayer(menu);
    reg.pushLayer({ close: () => {}, kind: 'modal' });
    assert.strictEqual(reg.hasFence(), true, 'a modal fences by default');
});

test('fence: a menu can opt OUT explicitly (fence:false)', () => {
    reg.pushLayer({ close: () => {}, kind: 'menu', fence: false });
    assert.strictEqual(reg.hasFence(), false);
});

test('fence: a modal can opt OUT explicitly (fence:false)', () => {
    reg.pushLayer({ close: () => {}, kind: 'modal', fence: false });
    assert.strictEqual(reg.hasFence(), false);
    assert.strictEqual(reg.hasModal(), true, 'still a modal for dimming purposes');
});

test('fence: a fencing popover above a modal does not unseat the modal as topmost (dimming unchanged)', () => {
    const m = reg.pushLayer({ close: () => {}, kind: 'modal' });
    reg.pushLayer({ close: () => {}, kind: 'popover', fence: true });
    assert.strictEqual(reg.isTopmostModal(m), true);
});

console.log(`\n${passed} overlayRegistry tests passed.`);
