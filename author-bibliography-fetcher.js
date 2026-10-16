// Author Bibliography Fetcher (Schema v2.1)
// Adds an author's Kindle books to your ReaderWrangler wishlist, in the language you choose.
//
// v2.1.0 (2026-10-16, Ron) - asks Amazon for the list itself instead of reading the page on screen:
//   - Works from ANY tab of an author page (Home — the address with the author's name — About, or All Books): it
//     loads the author's All Books page in the background and reads that page's built-in grid settings (`var config`).
//   - Asks Amazon's own All Books request (POST /juvec — the one the page makes when you set its filters) for
//     Kindle + the chosen language, PAGE_SIZE books at a time (Amazon sends book details for only the first 16 books
//     of a page, however big the page).
//   - Kindle only, said plainly. Amazon ignores the format filter without a language, and sends no book details for
//     non-Kindle editions — so "All languages" = one request per language the author has.
//   - Replaces the old page scrolling + card reading, whose Kindle check was computed but never applied (paperbacks,
//     hardcovers and audiobooks got in) and which never recorded a format.
//   Probed live on John Marrs + P. Djèlí Clark (2026-10-16). Request notes: .private/AMAZON-AUTHOR-PAGES.md
//
// Flow: author ID from the address → load the All Books settings → you pick a language (live count) → fetch every
// page → skip books already in your library → send the new ones as one run.
//
// Re-run: After pasting once, you can re-run with: importBibliography()

async function importBibliography() {
    'use strict';

    const FETCHER_VERSION = 'v2.1.0';
    const SCHEMA_VERSION = '2.1';
    const PAGE_SIZE = 16;      // Amazon sends book details for only the first 16 books of a page (probed 2026-10-16)
    const MAX_PAGES = 60;      // safety stop: 960 books per language
    const ALL_LANGUAGES = '';  // the chooser's "All languages" value

    // Use top-level document/window to handle iframe context
    const doc = top.document;
    const win = top.window;

    console.log('========================================');
    console.log(`Author Bibliography Fetcher ${FETCHER_VERSION}`);
    console.log('========================================\n');

    // ============================================================================
    // Helper Functions
    // ============================================================================

    function getTodayDate() {
        return new Date().toISOString().split('T')[0];
    }

    const escapeHtml = (s) => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

    // Amazon's language names run words together ("ChineseSimplified").
    const languageLabel = (name) => String(name).replace(/([a-z])([A-Z])/g, '$1 $2');
    const languageText = (language) => language === ALL_LANGUAGES ? 'in all languages' : `in ${languageLabel(language)}`;
    const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;

    // ============================================================================
    // Progress UI (toast-style overlay)
    // ============================================================================
    const progressUI = (() => {
        let overlay = null;

        const closeButtonHtml = (id = '') => `
                <button ${id ? `id="${id}"` : ''} style="
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: none;
                    border: none;
                    font-size: 20px;
                    color: #999;
                    cursor: pointer;
                    padding: 4px 8px;
                    line-height: 1;
                " onmouseover="this.style.color='#333'" onmouseout="this.style.color='#999'" ${id ? '' : 'onclick="this.parentElement.remove()"'}>✕</button>`;

        const progressHtml = () => `
                ${closeButtonHtml()}
                <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;">
                    📚 Bibliography Importer ${FETCHER_VERSION}
                </div>
                <div id="progressPhase" style="font-size: 14px; color: #667eea; margin-bottom: 8px; font-weight: 500;">
                    Starting...
                </div>
                <div id="progressDetail" style="font-size: 13px; color: #666; margin-bottom: 10px;">
                    Initializing
                </div>
                <div id="progressBarContainer" style="
                    background: #e0e0e0;
                    border-radius: 4px;
                    height: 8px;
                    overflow: hidden;
                    display: none;
                ">
                    <div id="progressBar" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        height: 100%;
                        width: 0%;
                        transition: width 0.3s ease;
                    "></div>
                </div>
            `;

        function create() {
            overlay = doc.createElement('div');
            overlay.id = 'bibliography-fetcher-progress';
            overlay.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                padding: 20px;
                padding-top: 35px;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                min-width: 320px;
                max-width: 420px;
            `;
            overlay.innerHTML = progressHtml();
            doc.body.appendChild(overlay);
        }

        // v2.1.0 - back to the progress view after the chooser replaced it
        function showProgress() {
            if (!overlay) create();
            overlay.innerHTML = progressHtml();
        }

        function updatePhase(phase, detail = '') {
            if (!overlay) create();
            const phaseElement = overlay.querySelector('#progressPhase');
            const detailElement = overlay.querySelector('#progressDetail');
            if (phaseElement) phaseElement.textContent = phase;
            if (detailElement) detailElement.textContent = detail;
        }

        function showProgressBar() {
            if (!overlay) create();
            const container = overlay.querySelector('#progressBarContainer');
            if (container) container.style.display = 'block';
        }

        function updateProgress(current, total) {
            if (!overlay) return;
            const bar = overlay.querySelector('#progressBar');
            if (bar) {
                const percent = Math.round((current / total) * 100);
                bar.style.width = `${percent}%`;
            }
        }

        function remove() {
            if (overlay && overlay.parentElement) {
                overlay.style.transition = 'opacity 0.3s';
                overlay.style.opacity = '0';
                setTimeout(() => overlay.remove(), 300);
            }
        }

        // v2.1.0 (Ron) - the one question before anything is fetched: which language. Kindle only, said plainly. The
        // count updates as you change the language (countFor → Promise<number>; a slower answer for an earlier choice
        // is ignored). Resolves with the chosen language (ALL_LANGUAGES for all) or null on Cancel / ✕.
        function showChooser({ authorName, languages, defaultLanguage, countFor }) {
            return new Promise((resolve) => {
                if (!overlay) create();
                const options = languages
                    .map(l => `<option value="${escapeHtml(l)}"${l === defaultLanguage ? ' selected' : ''}>${escapeHtml(languageLabel(l))}</option>`)
                    .join('') + `<option value="${ALL_LANGUAGES}">All languages</option>`;
                overlay.innerHTML = `
                    ${closeButtonHtml('rwChooserClose')}
                    <div style="font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;">
                        📚 Bibliography Importer ${FETCHER_VERSION}
                    </div>
                    <div style="font-size: 15px; color: #333; margin-bottom: 4px;">
                        Add <strong>${escapeHtml(authorName)}</strong>'s books to your wishlist
                    </div>
                    <div style="font-size: 13px; color: #666; margin-bottom: 12px;">Kindle books only.</div>
                    <label style="font-size: 14px; color: #333; display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                        Language:
                        <select id="rwChooserLang" style="font-size: 14px; padding: 4px 6px; border: 1px solid #ccc; border-radius: 4px;">${options}</select>
                    </label>
                    <div id="rwChooserCount" style="font-size: 13px; color: #667eea; margin-bottom: 14px; min-height: 18px;">Counting…</div>
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button id="rwChooserCancel" style="
                            background: transparent; color: #666; border: 1px solid #ccc; padding: 8px 16px;
                            border-radius: 8px; font-size: 14px; cursor: pointer;">Cancel</button>
                        <button id="rwChooserAdd" style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;
                            padding: 8px 18px; border-radius: 8px; font-size: 14px; font-weight: bold;">Add to wishlist</button>
                    </div>
                `;
                const select = overlay.querySelector('#rwChooserLang');
                const countEl = overlay.querySelector('#rwChooserCount');
                const addBtn = overlay.querySelector('#rwChooserAdd');
                let ticket = 0;
                const setAddEnabled = (on) => {
                    addBtn.disabled = !on;
                    addBtn.style.opacity = on ? '1' : '0.5';
                    addBtn.style.cursor = on ? 'pointer' : 'default';
                };
                const recount = async () => {
                    const mine = ++ticket;
                    setAddEnabled(false);
                    countEl.style.color = '#667eea';
                    countEl.textContent = 'Counting…';
                    try {
                        const n = await countFor(select.value);
                        if (mine !== ticket) return;
                        countEl.textContent = n
                            ? `${plural(n, 'Kindle book')} ${languageText(select.value)} — any already in your library are skipped.`
                            : `No Kindle books ${languageText(select.value)}.`;
                        setAddEnabled(n > 0);
                    } catch (e) {
                        if (mine !== ticket) return;
                        countEl.style.color = '#c62828';
                        countEl.textContent = e.message;
                    }
                };
                const finish = (value) => { ticket++; resolve(value); };
                select.onchange = recount;
                overlay.querySelector('#rwChooserCancel').onclick = () => { finish(null); remove(); };
                overlay.querySelector('#rwChooserClose').onclick = () => { finish(null); remove(); };
                addBtn.onclick = () => { if (!addBtn.disabled) finish(select.value); };
                recount();
            });
        }

        function showComplete(message, autoCloseMs = 15000) {
            if (!overlay) create();
            overlay.innerHTML = `
                ${closeButtonHtml()}
                <div style="font-size: 18px; font-weight: bold; color: #2e7d32; margin-bottom: 10px;">
                    ✅ Bibliography Import Complete!
                </div>
                <div style="font-size: 14px; color: #666; margin-bottom: 15px;">
                    ${message}
                </div>
                <button style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                " onclick="this.parentElement.remove()">
                    Close
                </button>
            `;
            setTimeout(remove, autoCloseMs);
        }

        function showError(message) {
            if (!overlay) create();
            overlay.innerHTML = `
                ${closeButtonHtml()}
                <div style="font-size: 18px; font-weight: bold; color: #c62828; margin-bottom: 10px;">
                    ❌ Error
                </div>
                <div style="font-size: 14px; color: #666; margin-bottom: 15px;">
                    ${message}
                </div>
                <div style="font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px;">
                    Check console for details
                </div>
                <button style="
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                    margin-top: 10px;
                " onclick="this.parentElement.remove()">
                    Close
                </button>
            `;
        }

        function getOverlay() {
            if (!overlay) create();
            return overlay;
        }

        function showRetryUpload(errorMessage) {
            return new Promise((resolve) => {
                if (!overlay) create();
                overlay.innerHTML = `
                    <div style="font-size: 18px; font-weight: bold; color: #d32f2f; margin-bottom: 10px;">
                        ❌ Upload Failed
                    </div>
                    <div style="font-size: 14px; color: #666; margin-bottom: 15px;">
                        ${errorMessage}
                    </div>
                    <button id="retryBtn" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; border: none; padding: 12px 20px;
                        border-radius: 8px; font-size: 16px; font-weight: bold;
                        cursor: pointer; width: 100%; transition: transform 0.1s;
                    ">
                        🔄 Retry Upload
                    </button>
                    <button id="cancelBtn" title="Discard data" style="
                        background: transparent; color: #999;
                        border: 1px solid #ccc; padding: 6px 16px;
                        border-radius: 4px; font-size: 12px;
                        cursor: pointer; margin-top: 15px;
                    ">
                        Cancel
                    </button>
                `;
                const retryBtn = overlay.querySelector('#retryBtn');
                retryBtn.onmouseover = () => retryBtn.style.transform = 'scale(1.02)';
                retryBtn.onmouseout = () => retryBtn.style.transform = 'scale(1)';
                retryBtn.onclick = () => resolve('retry');
                overlay.querySelector('#cancelBtn').onclick = () => resolve('cancel');
            });
        }

        return { create, showProgress, updatePhase, showProgressBar, updateProgress, remove, showChooser, showComplete, showError, getOverlay, showRetryUpload };
    })();

    // Initialize progress UI
    progressUI.create();

    // ============================================================================
    // Amazon: the author's All Books settings + its book-list request
    // ============================================================================

    // Both author-page addresses carry the ID: /stores/John-Marrs/author/B00F1CRG9U and /stores/author/B00F1CRG9U/allbooks
    function getAuthorId() {
        const match = win.location.pathname.match(/\/author\/([A-Z0-9]{10})/i);
        return match ? match[1].toUpperCase() : null;
    }

    // Parse the JSON object starting at text[start] ('{'), matching braces outside strings.
    function readObjectAt(text, start) {
        let depth = 0, inString = false, escaped = false;
        for (let i = start; i < text.length; i++) {
            const c = text[i];
            if (inString) {
                if (escaped) escaped = false;
                else if (c === '\\') escaped = true;
                else if (c === '"') inString = false;
                continue;
            }
            if (c === '"') inString = true;
            else if (c === '{') depth++;
            else if (c === '}' && --depth === 0) return JSON.parse(text.slice(start, i + 1));
        }
        throw new Error('settings object never closed');
    }

    // The All Books page's built-in grid settings: one `var config = {...}` holding requestContext (the request's keys),
    // pageContext and content (authorSearch, languageFilter, ...). Loaded in the background, so the tab you're on and
    // anything you set on screen don't matter.
    async function loadGridSettings(authorId) {
        const res = await win.fetch(`${win.location.origin}/stores/author/${authorId}/allbooks`, { credentials: 'include' });
        if (!res.ok) throw new Error(`Amazon didn't send this author's book list (error ${res.status}). Try again in a minute.`);
        const html = await res.text();
        const mark = html.indexOf('AuthorAllBooksProductGrid');
        const at = mark === -1 ? -1 : html.lastIndexOf('var config', mark);
        let grid = null;
        try {
            grid = at === -1 ? null : readObjectAt(html, html.indexOf('{', at));
        } catch (e) {
            console.warn('   Could not parse the All Books settings:', e.message);
        }
        if (!grid?.requestContext || !grid?.pageContext || !grid?.content) {
            throw new Error("Couldn't read this author's book list — Amazon may have changed its author pages. Please let us know.");
        }
        return grid;
    }

    // One page of Kindle books in one language — the same request the All Books page makes when you set its filters.
    // One retry: an occasional request fails for no visible reason (seen once while probing).
    async function askAmazon(grid, language, page) {
        const { products, ASINList, ...gridSearch } = grid.content;
        const body = {
            requestContext: grid.requestContext,
            pageContext: grid.pageContext,
            widgetType: grid.widgetType,
            sectionType: grid.sectionType,
            ...gridSearch,
            authorSearch: { ...gridSearch.authorSearch, pageSize: PAGE_SIZE, page },
            authorFilters: { format: ['kindle'], language: [language] },
            content: { includeOutOfStock: true },
            includeOutOfStock: true,
            endpoint: 'ajax-data'
        };
        for (let attempt = 1; ; attempt++) {
            try {
                const res = await win.fetch(`${win.location.origin}/juvec`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'content-type': 'application/json; charset=UTF-8', accept: 'application/json, text/plain, */*' },
                    body: JSON.stringify(body)
                });
                if (!res.ok) throw new Error(`status ${res.status}`);
                const data = await res.json();
                if (data.isSuccess === false) throw new Error('Amazon reported no success');
                return { total: data.totalResultCount || 0, asins: data.ASINList || [], products: data.products || [] };
            } catch (e) {
                console.warn(`   Amazon request failed (${language}, page ${page}, try ${attempt}): ${e.message}`);
                if (attempt >= 2) throw new Error("Amazon didn't answer. Try again in a minute.");
                await new Promise(r => setTimeout(r, 1500));
            }
        }
    }

    const languagesFor = (language, languages) => language === ALL_LANGUAGES ? languages : [language];

    // How many Kindle books — page 1 of each language carries the total.
    async function countBooks(grid, language, languages) {
        let total = 0;
        for (const lang of languagesFor(language, languages)) total += (await askAmazon(grid, lang, 1)).total;
        return total;
    }

    // Amazon's product → a wishlist book. Only the listed book itself, and only if it's a Kindle edition: the answer
    // also carries each book's other editions (hardcover, paperback, audiobook...).
    function toBook(product, authorName) {
        if (!product?.asin || product.bindingInformation?.binding?.symbol !== 'kindle_edition') return null;
        const title = product.title?.displayString || '';
        if (!title) return null;

        const authors = (product.byLine?.contributors || [])
            .filter(c => c.roles?.some(r => r.type === 'author'))
            .map(c => c.name)
            .filter(Boolean)
            .join(', ') || authorName;

        const images = product.productImages?.images || [];
        const coverUrl = images[0]?.hiRes?.url || images[0]?.lowRes?.url || null;
        const rating = product.customerReviewsSummary?.rating?.value || null;
        const reviewCount = product.customerReviewsSummary?.count?.value || null;

        let currentPrice = null;
        for (const option of product.buyingOptions || []) {
            if (option.type === 'KINDLE_ALC' || option.type === 'NEW') {
                const priceValue = option.price?.priceToPay?.moneyValueOrRange?.value;
                if (priceValue?.amount !== undefined) {
                    currentPrice = priceValue.amount; // a number, not a string
                    break;
                }
            }
        }

        const series = product.bookSeriesInfo?.seriesTitle || null;
        const seriesPosition = product.bookSeriesInfo?.position || null;

        return {
            asin: product.asin.toUpperCase(),
            onWishlist: true,
            ownershipType: 'wishlist',
            addedToWishlist: getTodayDate(),
            title,
            authors,
            binding: 'Kindle Edition', // FORMAT-POLICY spelling
            coverUrl,
            rating,
            reviewCount,
            ...(series && { series }),
            ...(seriesPosition && { seriesPosition }),
            ...(currentPrice && { currentPrice, priceAsOf: getTodayDate() })
        };
    }

    // Every Kindle book in the chosen language(s), page by page. `unreadable` = listed but not a Kindle edition with
    // details (expected 0 — reported, never silently dropped).
    async function collectBooks(grid, language, languages, authorName, onProgress) {
        const books = new Map();
        let unreadable = 0;
        for (const lang of languagesFor(language, languages)) {
            for (let page = 1; page <= MAX_PAGES; page++) {
                const { total, asins, products } = await askAmazon(grid, lang, page);
                const byAsin = new Map(products.map(p => [p.asin, p]));
                for (const asin of asins) {
                    const book = toBook(byAsin.get(asin), authorName);
                    if (book) books.set(book.asin, book);
                    else unreadable++;
                }
                onProgress(books.size, lang);
                if (asins.length < PAGE_SIZE || page * PAGE_SIZE >= total) break;
            }
        }
        return { books: [...books.values()], unreadable };
    }

    // The language you use Amazon in (its request's "en-US"), if this author has books in it; else English, else the first.
    function pickDefaultLanguage(languages, amazonLanguage) {
        let name = null;
        try {
            name = new Intl.DisplayNames(['en'], { type: 'language' }).of(String(amazonLanguage || 'en').split('-')[0]);
        } catch (e) { /* older browser: fall through */ }
        return languages.find(l => l === name) || (languages.includes('English') ? 'English' : languages[0]);
    }

    // ============================================================================
    // Relay I/O — shared implementations live in relay-client.js (one copy for all
    // wishlist-style fetchers; UI stays here via callbacks)
    // ============================================================================

    const loadKnownBooks = () =>
        win.RWRelay.loadKnownBooks((phase, detail) => progressUI.updatePhase(phase, detail));

    const sendWishlistRun = (newBooks) =>
        win.RWRelay.sendWishlistRun(newBooks,
            { schemaVersion: SCHEMA_VERSION, source: 'author-bibliography-fetcher',
              fetcherVersion: FETCHER_VERSION, cancelMessage: 'Cancelled — the books were not saved.' },
            (phase, detail) => progressUI.updatePhase(phase, detail),
            (errMsg) => progressUI.showRetryUpload(errMsg));

    const ageCapCheck = (known) => win.RWRelay.ageCapCheck(known);

    // ============================================================================
    // Main Flow
    // ============================================================================

    try {
        // Step 1: the author, from the address
        progressUI.updatePhase('Finding the author', 'Reading the page address...');
        console.log('[1] Finding the author...');
        const authorId = getAuthorId();
        if (!authorId) {
            throw new Error("This isn't an Amazon author page. Click an author's name on a book page, then click the bookmarklet again.");
        }

        // Step 2: the All Books settings (loaded in the background)
        progressUI.updatePhase('Finding the author', "Loading the author's book list from Amazon...");
        const grid = await loadGridSettings(authorId);
        const authorName = grid.pageContext.brandName || 'this author';
        const languages = grid.content.languageFilter?.length ? grid.content.languageFilter : ['English'];
        console.log(`   Author: "${authorName}" (${authorId}) | languages: ${languages.join(', ')}\n`);

        // Step 3: you choose the language
        const language = await progressUI.showChooser({
            authorName,
            languages,
            defaultLanguage: pickDefaultLanguage(languages, grid.requestContext.language),
            countFor: (lang) => countBooks(grid, lang, languages)
        });
        if (language === null) {
            console.log('   Cancelled — nothing was added.\n');
            return;
        }
        const inLanguage = languageText(language);

        // Step 4: every page
        progressUI.showProgress();
        progressUI.updatePhase('Fetching books', `Asking Amazon for ${authorName}'s Kindle books ${inLanguage}...`);
        console.log(`[2] Fetching Kindle books ${inLanguage}...`);
        const { books, unreadable } = await collectBooks(grid, language, languages, authorName,
            (n, lang) => progressUI.updatePhase('Fetching books', `${plural(n, 'Kindle book')} so far (${languageLabel(lang)})...`));
        console.log(`   ✅ ${books.length} Kindle books${unreadable ? ` (${unreadable} listed without details — skipped)` : ''}\n`);

        if (books.length === 0) {
            progressUI.showComplete(`No Kindle books found for <strong>${escapeHtml(authorName)}</strong> ${inLanguage}.`, 15000);
            return;
        }

        // Step 5: read known books (canonical + pending) for duplicate detection
        console.log('[3] Checking your library...');
        const known = await loadKnownBooks();

        // Step 6: dedup against known + pending
        progressUI.updatePhase('Adding to Wishlist', `Processing ${books.length} books...`);
        progressUI.showProgressBar();
        console.log(`[4] Adding ${books.length} books...`);

        let addedCount = 0;
        let duplicateCount = 0;
        const newBooks = [];

        for (let i = 0; i < books.length; i++) {
            const book = books[i];
            progressUI.updateProgress(i + 1, books.length);

            if (known.byAsin.has(book.asin)) {
                duplicateCount++;
                continue;
            }

            known.byAsin.set(book.asin, book);
            newBooks.push(book);
            addedCount++;
        }

        console.log(`   ✅ ${addedCount} new books`);
        if (duplicateCount > 0) {
            console.log(`   ℹ️  Skipped ${duplicateCount} duplicates (already in library)\n`);
        }

        // Step 7: send new books as one atomic run (never rewrites the library)
        if (newBooks.length > 0) {
            console.log('[5] Sending to your library...');
            await sendWishlistRun(newBooks);
            ageCapCheck(known);
        }

        // Step 8: summary
        const missingPrice = newBooks.filter(b => !b.currentPrice).length;
        console.log('========================================');
        console.log('✅ BIBLIOGRAPHY IMPORT COMPLETE!');
        console.log('========================================');
        console.log(`   Author: "${authorName}"`);
        console.log(`   Added: ${addedCount} Kindle books ${inLanguage}`);
        console.log(`   Skipped (already in library): ${duplicateCount} books`);
        if (missingPrice > 0) {
            console.log(`   ℹ️  ${missingPrice} books missing price - run Library Fetcher to complete`);
        }
        console.log(`   Library incl. these + pending: ${known.byAsin.size} books`);
        console.log('========================================\n');

        let summaryMessage = `<strong>${escapeHtml(authorName)}</strong><br>`;
        summaryMessage += addedCount > 0
            ? `Added ${plural(addedCount, 'Kindle book')} ${inLanguage} to your wishlist<br>`
            : `All ${plural(books.length, 'Kindle book')} ${inLanguage} are already in your library — nothing new to add.<br>`;
        if (addedCount > 0 && duplicateCount > 0) {
            summaryMessage += `<span style="color: #888; font-size: 12px;">Skipped: ${duplicateCount} already in your library</span><br>`;
        }
        if (unreadable > 0) {
            summaryMessage += `<span style="color: #888; font-size: 12px;">Skipped: ${unreadable} listed by Amazon without book details</span><br>`;
        }
        if (missingPrice > 0) {
            summaryMessage += `<br><span style="color: #1976d2; font-size: 11px;">`;
            summaryMessage += `ℹ️ ${missingPrice} books missing price - run Library Fetcher to complete</span>`;
        }

        progressUI.showComplete(summaryMessage, 20000);

        // Analytics
        new Image().src = 'https://readerwrangler.goatcounter.com/count?p=/event/bibliography-import-completed';

    } catch (error) {
        console.error('\n========================================');
        console.error('❌ ERROR');
        console.error('========================================');
        console.error(error.message);
        console.error(error.stack);
        console.error('========================================\n');

        progressUI.showError(escapeHtml(error.message));
    }
}

// Auto-run on first paste
importBibliography();
