// THROWAWAY (2026-11-26, outside review 2 item 13): can a bookmarklet run code it fetched as text on Amazon's page?
// Ron's live test only. Delete after the test — it must not reach production.
window.__rwHelloRuns = (window.__rwHelloRuns || 0) + 1;
console.log('RW hello: ran (' + window.__rwHelloRuns + ')');
