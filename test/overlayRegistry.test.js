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

test('fence: a type-ahead list does NOT fence by default (its dialog already does); can opt in', () => {
    const l = reg.pushLayer({ close: () => {}, kind: 'list' });
    assert.strictEqual(reg.hasFence(), false, 'a list does not fence by default');
    reg.removeLayer(l);
    reg.pushLayer({ close: () => {}, kind: 'list', fence: true });
    assert.strictEqual(reg.hasFence(), true, 'explicit fence:true still honoured');
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

// --- outsideClickAction: the Popover outside-click policy, one case per earned rule ---
test('detached: a confirm opened from a menu SURVIVES the menu closing; normal children above still cascade', () => {
    // alpha.69 - Bake / New list: the menu item pushes a confirm above the still-open menu, then the menu unmounts.
    let confirmClosed = 0, childClosed = 0;
    const menu = reg.pushLayer({ close: () => {}, kind: 'menu' });
    reg.pushLayer({ close: () => { childClosed++; }, kind: 'popover' });          // the menu's own child
    const confirm = reg.pushLayer({ close: () => { confirmClosed++; }, kind: 'modal', detached: true });
    reg.removeLayer(menu);
    assert.strictEqual(confirmClosed, 0, 'the detached confirm is NOT closed');
    assert.strictEqual(childClosed, 1, 'the menu child still cascade-closes');
    assert.strictEqual(reg._count(), 1);
    assert.strictEqual(reg.topLayer().id, confirm, 'the confirm is still on the stack (and topmost — Esc reaches it)');
    assert.strictEqual(reg.hasFence(), true, 'and still fences library keys');
});
test('detached layers keep their order when a layer below them is removed', () => {
    const a = reg.pushLayer({ close: () => {}, kind: 'menu' });
    const d1 = reg.pushLayer({ close: () => {}, kind: 'modal', detached: true });
    const d2 = reg.pushLayer({ close: () => {}, kind: 'modal', detached: true });
    reg.removeLayer(a);
    assert.deepStrictEqual([reg._count(), reg.topLayer().id], [2, d2]);
    reg.removeLayer(d2);
    assert.strictEqual(reg.topLayer().id, d1);
});

const base = { insidePopup: false, onOwnTrigger: false, button: 0, kind: 'menu', isTopmost: true, imperativeUp: false, onPopupTrigger: false };
const act = (over) => reg.outsideClickAction({ ...base, ...over });

test('outside-click: a click inside the popup is ignored', () => {
    assert.strictEqual(act({ insidePopup: true }), 'ignore');
});
test('outside-click: LEFT-click on its own trigger is ignored (the toggle closes it); RIGHT-click there closes + passes through', () => {
    assert.strictEqual(act({ onOwnTrigger: true, button: 0 }), 'ignore');
    assert.strictEqual(act({ onOwnTrigger: true, button: 2 }), 'close', 'alpha.47: no second menu on top of a still-open dropdown');
});
test('outside-click: not the topmost overlay, or a confirm dialog is up → ignore (that overlay owns the click)', () => {
    assert.strictEqual(act({ isTopmost: false }), 'ignore');
    assert.strictEqual(act({ imperativeUp: true }), 'ignore', 'alpha.45: never eat a confirm dialog\'s OK');
});
test('outside-click: ANY other popup button closes and passes through (it opens in one click)', () => {
    assert.strictEqual(act({ onPopupTrigger: true }), 'close');
    assert.strictEqual(act({ onPopupTrigger: true, kind: 'popover' }), 'close', 'a panel too (e.g. More)');
    assert.strictEqual(act({ onPopupTrigger: true, isTopmost: false }), 'ignore', 'the topmost rule still wins');
    assert.strictEqual(act({ onPopupTrigger: true, onOwnTrigger: true }), 'ignore', 'its OWN button is still the toggle');
});
test('outside-click: an ordinary left-click (a book, empty space) is still swallowed — selections stay protected', () => {
    assert.strictEqual(act({}), 'close-swallow');
});
test('outside-click: right/middle-click anywhere closes and passes through', () => {
    assert.strictEqual(act({ button: 2 }), 'close');
    assert.strictEqual(act({ button: 1 }), 'close');
});
test('outside-click: a type-ahead list never swallows; a menu/popover left-click swallows', () => {
    assert.strictEqual(act({ kind: 'list' }), 'close');
    assert.strictEqual(act({ kind: 'menu' }), 'close-swallow');
    assert.strictEqual(act({ kind: 'popover' }), 'close-swallow');
});

console.log(`\n${passed} overlayRegistry tests passed.`);
