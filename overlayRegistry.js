// overlayRegistry.js — the ONE ordered stack of open overlays (dialogs, popovers, menus).
// v7.18.0. Loaded as a classic script BEFORE readerwrangler.js (browser); required by
// test/overlayRegistry.test.js (Node). Pure logic — no React, no DOM, no window listener — so the
// trickiest part of the overlay system (stack ordering + cascade-close) is unit-tested in isolation.
//
// WHY THIS FILE EXISTS
//   RW's overlay layer had three unrelated Esc mechanisms + a hand-maintained keystroke fence
//   (`anyDialogOpen` OR-chain). A new overlay was correct only if a human remembered a 4-point
//   checklist — which failed twice in one release cycle (docs/design/DIALOG-DISMISSAL-AUDIT.md).
//   The fix: overlays self-register here on mount and deregister on unmount, so the fence,
//   Esc-ordering, and cascade-close become STRUCTURAL — an overlay can't be born non-compliant.
//   This module is the "minimal stack for Esc-ordering" every mature overlay lib converged on
//   (Radix DismissableLayer, React-Aria overlay stack). The React parts — useOverlayLayer / <Dialog>
//   / <Popover> — live in readerwrangler.js; the single keydown listener is installed there (via a
//   useEffect) so its lifecycle is React-managed and THIS module stays pure/testable.
//
// The model: `_layers` is ordered [outermost … topmost]. close() is the overlay's own closer
// (its React onClose). Closing a layer also closes everything ABOVE it (stack order = the implicit
// parent→child hierarchy — "containment is a stack"), a belt-and-suspenders partner to React
// unmounting nested children automatically.

let _layers = [];              // [{ id, close, kind }] — [0] outermost, [n-1] topmost
let _seq = 0;                  // monotonic id source
const _subs = new Set();       // subscribers notified on any change (React syncs hasModal() from this)

const _notify = () => { _subs.forEach(fn => { try { fn(); } catch (e) { /* a subscriber must not break the stack */ } }); };

// Register an overlay; returns its id. kind: 'modal' | 'popover' | 'menu'. Optional nodeRef is a React
// ref to the overlay's DOM node — used to scope select-all (Ctrl+A) to the overlay's own content.
const pushLayer = ({ close, kind, nodeRef }) => {
    const id = ++_seq;
    _layers.push({ id, close, kind, nodeRef });
    _notify();
    return id;
};

// Remove a layer AND everything above it, closing those above (cascade). Idempotent: removing an
// id that's already gone is a no-op (so React unmount-after-cascade doesn't double-fire or throw).
const removeLayer = (id) => {
    const i = _layers.findIndex(l => l.id === id);
    if (i < 0) return;                          // already gone — no-op, no notify
    const removed = _layers.splice(i);          // remove id and everything above it, synchronously
    for (const l of removed) {
        if (l.id !== id && l.close) { try { l.close(); } catch (e) { /* keep tearing down */ } }
    }
    _notify();
};

const topLayer = () => _layers[_layers.length - 1] || null;

// Close the topmost layer (what the Esc listener calls). The close() drives a React state change →
// unmount → the effect cleanup calls removeLayer(id); we do NOT splice here (React owns removal).
// reason ('esc' | 'backdrop' | 'button' | undefined) is forwarded to the layer's close() so a
// dialog can behave differently per source (e.g. Esc backs out an in-dialog sub-view; backdrop closes).
const closeTop = (reason) => {
    const t = topLayer();
    if (t && t.close) { try { t.close(reason); } catch (e) { /* no-op */ } }
    return !!t;                                 // true if there was something to close
};

const hasModal = () => _layers.some(l => l.kind === 'modal');

// Is the layer `id` the topmost MODAL — i.e. no modal-kind layer sits above it? (Popovers/menus above
// do NOT count.) v7.18.0-alpha.38: only the topmost modal paints its dimming scrim, so stacked dialogs
// don't compound their backdrops to near-black; a popover over a dialog leaves the dialog's dimming.
const isTopmostModal = (id) => {
    const i = _layers.findIndex(l => l.id === id);
    if (i < 0) return false;
    for (let j = i + 1; j < _layers.length; j++) { if (_layers[j].kind === 'modal') return false; }
    return true;
};

// Subscribe to stack changes; returns an unsubscribe fn.
const subscribe = (fn) => { _subs.add(fn); return () => _subs.delete(fn); };

// --- test-only helpers (harmless in the browser) ---
const _reset = () => { _layers = []; _seq = 0; _subs.clear(); };
const _count = () => _layers.length;
const _kinds = () => _layers.map(l => l.kind);

// Browser: expose ONE namespaced global — readerwrangler.js calls `overlayRegistry.X`. Unlike the
// bare-const shared modules (uiHelpers/bookFields expose `packBook` etc. directly), the overlay API is
// namespaced so generic names (pushLayer/topLayer/hasModal/…) don't pollute the global scope.
if (typeof window !== 'undefined') {
    window.overlayRegistry = { pushLayer, removeLayer, topLayer, closeTop, hasModal, isTopmostModal, subscribe };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        pushLayer, removeLayer, topLayer, closeTop, hasModal, isTopmostModal, subscribe,
        _reset, _count, _kinds,
    };
}
