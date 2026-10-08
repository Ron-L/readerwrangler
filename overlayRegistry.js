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

let _layers = [];              // [{ id, close, kind, nodeRef, fence, detached }] — [0] outermost, [n-1] topmost
let _seq = 0;                  // monotonic id source
const _subs = new Set();       // subscribers notified on any change (React syncs hasModal() from this)

const _notify = () => { _subs.forEach(fn => { try { fn(); } catch (e) { /* a subscriber must not break the stack */ } }); };

// Register an overlay; returns its id. kind: 'modal' | 'popover' | 'menu'. Optional nodeRef is a React
// ref to the overlay's DOM node — used to scope select-all (Ctrl+A) to the overlay's own content.
// fence (v7.18.0-alpha.40): does this layer raise the KEYSTROKE fence (library shortcuts — cut/copy/
// paste/delete/select-all/undo — must not reach the page beneath)? Default: a modal AND a menu fence
// (v7.18.0-alpha.44, Ron: an open right-click menu must not let Ctrl+A/Delete hit the library behind
// it); a plain popover doesn't unless it opts in (toast history does — a Ctrl+X in it once cut a
// selected book). Kept separate from `kind` because "dims like a dialog" and "blocks library keys"
// are different facts.
// detached (alpha.69): an INDEPENDENT overlay — never cascade-closed when a layer beneath it is removed (see removeLayer).
const pushLayer = ({ close, kind, nodeRef, fence, detached }) => {
    const id = ++_seq;
    // alpha.54: a 'list' (type-ahead suggestions under a field) doesn't fence by default either — it lives inside a
    // dialog that already does.
    _layers.push({ id, close, kind, nodeRef, fence: fence === undefined ? (kind === 'modal' || kind === 'menu') : !!fence, detached: !!detached });
    _notify();
    return id;
};

// Remove a layer AND everything above it, closing those above (cascade). Idempotent: removing an
// id that's already gone is a no-op (so React unmount-after-cascade doesn't double-fire or throw).
// v7.18.0-alpha.69 - EXCEPT layers marked `detached`: an independent overlay that merely happens to sit above (the
// imperative confirm-style dialogs). A menu item that opens a confirm pushes the confirm ABOVE the still-open menu in the
// same click; the menu's React unmount then removed "it and everything above" — closing the confirm before it was ever
// seen (Ron: "Bake Order" / "New Book List" never appeared, alpha.68). A detached layer is nobody's child, so it survives.
const removeLayer = (id) => {
    const i = _layers.findIndex(l => l.id === id);
    if (i < 0) return;                          // already gone — no-op, no notify
    const above = _layers.slice(i + 1);
    const closing = above.filter(l => !l.detached);
    _layers = _layers.slice(0, i).concat(above.filter(l => l.detached)); // drop id + its (non-detached) children
    for (const l of closing) {
        if (l.close) { try { l.close(); } catch (e) { /* keep tearing down */ } }
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

// Is ANY open layer fencing library keystrokes? (A modal by default; a popover only if it opted in.)
// This — not hasModal — is what the app's keystroke/undo fence consults.
const hasFence = () => _layers.some(l => l.fence);

// Is the layer `id` the topmost MODAL — i.e. no modal-kind layer sits above it? (Popovers/menus above
// do NOT count.) v7.18.0-alpha.38: only the topmost modal paints its dimming scrim, so stacked dialogs
// don't compound their backdrops to near-black; a popover over a dialog leaves the dialog's dimming.
const isTopmostModal = (id) => {
    const i = _layers.findIndex(l => l.id === id);
    if (i < 0) return false;
    for (let j = i + 1; j < _layers.length; j++) { if (_layers[j].kind === 'modal') return false; }
    return true;
};

// v7.18.0-alpha.58 - THE outside-click policy for a <Popover>, as one pure, tested decision (it used to be branches
// inside the React mousedown handler). Given what the mousedown hit, return:
//   'ignore'         — do nothing (the click belongs to someone else)
//   'close'          — close the popover and let the click go THROUGH to what was clicked
//   'close-swallow'  — close the popover and EAT the click (it only dismisses)
// Rules, in order (each one earned in 7.18.0):
//   1. inside the popup itself                                → ignore
//   2. LEFT-click on its own trigger button (the toggle owns it) → ignore                         (alpha.40/47)
//   3. another overlay is above it, or a confirm-style dialog is up → ignore (that overlay owns it) (alpha.45)
//   4. ANY other popup's trigger button (data-popover-trigger) → close, pass through: it opens in one click.
//      (alpha.58 limited this to "siblings" in the same named group; alpha.61 broadened it — Ron: a click on a popup
//      button is unmistakable intent and protects nothing by being eaten; group bookkeeping was easy to miss, e.g.
//      "💾 … Save ▾" sits in a different row from the filter buttons yet reads as part of the same filter area.)
//   5. right/middle-click anywhere                             → close, pass through               (alpha.41/47)
//   6. a type-ahead 'list'                                     → close, pass through (click into the next field) (alpha.54)
//   7. any other left-click                                    → close-swallow (protects your selection)        (alpha.41)
const outsideClickAction = ({ insidePopup, onOwnTrigger, button, kind, isTopmost, imperativeUp, onPopupTrigger }) => {
    if (insidePopup) return 'ignore';
    if (onOwnTrigger && button === 0) return 'ignore';
    if (!isTopmost || imperativeUp) return 'ignore';
    if (onPopupTrigger) return 'close';
    if (button !== 0) return 'close';
    if (kind === 'list') return 'close';
    return 'close-swallow';
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
    window.overlayRegistry = { pushLayer, removeLayer, topLayer, closeTop, hasModal, hasFence, isTopmostModal, subscribe, outsideClickAction };
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        pushLayer, removeLayer, topLayer, closeTop, hasModal, hasFence, isTopmostModal, subscribe, outsideClickAction,
        _reset, _count, _kinds,
    };
}
