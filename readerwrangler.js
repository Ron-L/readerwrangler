        // ReaderWrangler JS v3.14.0.a - Dividers as Drop Targets
        // ARCHITECTURE: See docs/design/ARCHITECTURE.md for Version Management, Status Icons, Cache-Busting patterns
        const { useState, useEffect, useRef } = React;
        const ORGANIZER_VERSION = "v3.13.0";
        document.title = `ReaderWrangler ${ORGANIZER_VERSION}`;
        const STORAGE_KEY = "readerwrangler-state";
        const CACHE_KEY = "readerwrangler-enriched-cache";
        const SETTINGS_KEY = "readerwrangler-settings";
        const STATUS_KEY = "readerwrangler-status"; // v3.7.0.n - persist library/collections status
        const FILTERS_KEY = "readerwrangler-filters"; // v3.8.0.f - persist filter state
        const DB_NAME = "ReaderWranglerDB";
        const DB_VERSION = 1;
        const BOOKS_STORE = "books";
        // MANIFEST_CHECK_INTERVAL removed in v3.6.1 - replaced with IndexedDB manifests
        
        // IndexedDB Helper Functions
        const openDB = () => {
            return new Promise((resolve, reject) => {
                const request = indexedDB.open(DB_NAME, DB_VERSION);
                
                request.onerror = () => reject(request.error);
                request.onsuccess = () => resolve(request.result);
                
                request.onupgradeneeded = (event) => {
                    const db = event.target.result;
                    if (!db.objectStoreNames.contains(BOOKS_STORE)) {
                        db.createObjectStore(BOOKS_STORE, { keyPath: 'id' });
                    }
                };
            });
        };
        
        const saveBooksToIndexedDB = async (books) => {
            try {
                console.log(`🔄 Saving ${books.length} books to IndexedDB...`);

                // Deduplicate by ASIN (keep last occurrence)
                const seenAsins = new Set();
                const duplicates = [];
                const uniqueBooks = [];

                for (let i = books.length - 1; i >= 0; i--) {
                    const book = books[i];
                    if (seenAsins.has(book.asin)) {
                        duplicates.push(book.asin);
                    } else {
                        seenAsins.add(book.asin);
                        uniqueBooks.unshift(book);
                    }
                }

                if (duplicates.length > 0) {
                    console.warn(`⚠️  Found ${duplicates.length} duplicate ASINs, keeping unique books only`);
                    console.warn(`   Sample duplicates:`, duplicates.slice(0, 5));
                }

                const db = await openDB();

                // First transaction: Clear existing books
                await new Promise((resolve, reject) => {
                    const clearTxn = db.transaction([BOOKS_STORE], 'readwrite');
                    const clearStore = clearTxn.objectStore(BOOKS_STORE);
                    clearStore.clear();
                    clearTxn.oncomplete = () => {
                        console.log('✅ Cleared existing IndexedDB books');
                        resolve();
                    };
                    clearTxn.onerror = () => reject(clearTxn.error || new Error('Failed to clear IndexedDB'));
                });

                // Second transaction: Add all unique books
                return new Promise((resolve, reject) => {
                    const addTxn = db.transaction([BOOKS_STORE], 'readwrite');
                    const addStore = addTxn.objectStore(BOOKS_STORE);

                    // Add all unique books
                    for (const book of uniqueBooks) {
                        addStore.add(book);
                    }

                    addTxn.oncomplete = () => {
                        console.log('✅ Saved', uniqueBooks.length, 'unique books to IndexedDB');
                        resolve();
                    };
                    addTxn.onerror = () => {
                        const error = addTxn.error || new Error('IndexedDB transaction failed with no error details');
                        console.error('❌ IndexedDB save failed:', error);
                        reject(error);
                    };
                });
            } catch (error) {
                console.error('❌ IndexedDB save exception:', error);
                throw error || new Error('IndexedDB save failed');
            }
        };
        
        const loadBooksFromIndexedDB = async () => {
            const db = await openDB();
            const transaction = db.transaction([BOOKS_STORE], 'readonly');
            const store = transaction.objectStore(BOOKS_STORE);
            const request = store.getAll();
            
            return new Promise((resolve, reject) => {
                request.onsuccess = () => {
                    console.log('✅ Loaded', request.result.length, 'books from IndexedDB');
                    resolve(request.result);
                };
                request.onerror = () => reject(request.error);
            });
        };
        
        const clearIndexedDB = async () => {
            const db = await openDB();
            const transaction = db.transaction([BOOKS_STORE], 'readwrite');
            const store = transaction.objectStore(BOOKS_STORE);
            await store.clear();
            console.log('✅ Cleared IndexedDB');
        };


        // Calculate freshness status from fetchDate
        const calculateFreshness = (fetchDate) => {
            if (!fetchDate) return 'unknown';

            const now = new Date();
            const fetchTime = new Date(fetchDate);
            const daysSinceFetch = (now - fetchTime) / (1000 * 60 * 60 * 24);

            if (daysSinceFetch < 7) return 'fresh';
            if (daysSinceFetch <= 30) return 'stale';
            return 'obsolete';
        };

        // Format relative time for display
        const formatRelativeTime = (dateString) => {
            if (!dateString) return 'Unknown';

            const now = new Date();
            const date = new Date(dateString);
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays}d ago`;
            if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
            return `${diffDays}d ago`;
        };

        function ReaderWrangler() {
            const [books, setBooks] = useState([]);
            const [columns, setColumns] = useState([{ id: 'unorganized', name: 'Unorganized', books: [] }]);
            const [searchTerm, setSearchTerm] = useState('');
            const [draggedBook, setDraggedBook] = useState(null);
            const [draggedFromColumn, setDraggedFromColumn] = useState(null);
            const [draggedColumn, setDraggedColumn] = useState(null);
            const [columnDropTarget, setColumnDropTarget] = useState(null);
            const [modalBook, setModalBook] = useState(null);
            const [modalColumnId, setModalColumnId] = useState(null);
            const [dragStartPos, setDragStartPos] = useState({ x: 0, y: 0 });
            const [dragCurrentPos, setDragCurrentPos] = useState({ x: 0, y: 0 });
            const [isDragging, setIsDragging] = useState(false);
            const [isDraggingColumn, setIsDraggingColumn] = useState(false);
            const [dropTarget, setDropTarget] = useState(null);
            const [dataSource, setDataSource] = useState('none');
            const [blankImageBooks, setBlankImageBooks] = useState(new Set());
            const [editingColumn, setEditingColumn] = useState(null);
            const [editingName, setEditingName] = useState('');
            const [sortMenuOpen, setSortMenuOpen] = useState(null);
            const [columnMenuOpen, setColumnMenuOpen] = useState(null); // v3.11.0 - Unified column dropdown menu
            const [editingDivider, setEditingDivider] = useState(null); // v3.11.0 - {columnId, dividerId}
            const [editingDividerLabel, setEditingDividerLabel] = useState(''); // v3.11.0
            const [insertDividerOpen, setInsertDividerOpen] = useState(null); // v3.11.0 - columnId for Insert Divider modal
            const [newDividerLabel, setNewDividerLabel] = useState(''); // v3.11.0
            const [hoveringDivider, setHoveringDivider] = useState(null); // v3.11.0 - {columnId, dividerId}
            const [helpOpen, setHelpOpen] = useState(false);
            const [settingsOpen, setSettingsOpen] = useState(false);
            const [deleteDialogOpen, setDeleteDialogOpen] = useState(null);
            const [deleteDestination, setDeleteDestination] = useState('');
            const [showAllReviews, setShowAllReviews] = useState(false);
            const [collectSeriesOpen, setCollectSeriesOpen] = useState(false);
            const [seriesBooks, setSeriesBooks] = useState({ current: [], other: [] });
            const [syncStatus, setSyncStatusInternal] = useState('loading'); // 'loading', 'fresh', 'stale', 'none', 'unknown'
            const [lastSyncTime, setLastSyncTime] = useState(null);
            // manifestData state removed in v3.7.0.m - replaced by libraryStatus/collectionsStatus
            const [statusModalOpen, setStatusModalOpen] = useState(false);
            const [resetConfirmOpen, setResetConfirmOpen] = useState(false);
            const [collectionsData, setCollectionsData] = useState(null); // Map of ASIN -> {readStatus, collections[]}
            const [collectionFilter, setCollectionFilter] = useState(''); // Filter by collection name or special values
            const [selectedBooks, setSelectedBooks] = useState(new Set()); // Multi-select state
            const [lastClickedBook, setLastClickedBook] = useState(null); // For shift+click range selection
            const [selectedDivider, setSelectedDivider] = useState(null); // v3.13.0 - Selected divider {columnId, dividerId}
            const [activeColumnId, setActiveColumnId] = useState(null); // Track which column has focus for Ctrl+A
            const [contextMenu, setContextMenu] = useState(null); // {x, y, bookId, columnId}
            const [readStatusFilter, setReadStatusFilter] = useState(''); // Filter by READ/UNREAD/UNKNOWN
            const [ratingFilter, setRatingFilter] = useState(''); // Filter by minimum rating (NEW v3.8.0)
            const [wishlistFilter, setWishlistFilter] = useState(''); // Filter by wishlist status: '' | 'owned' | 'wishlist' (NEW v3.8.0)
            const [seriesFilter, setSeriesFilter] = useState(''); // Filter by series name or "NOT_IN_SERIES" (NEW v3.8.0.k)
            const [dateFrom, setDateFrom] = useState(''); // Filter by acquisition date from (YYYY-MM-DD) (NEW v3.8.0.k)
            const [dateTo, setDateTo] = useState(''); // Filter by acquisition date to (YYYY-MM-DD) (NEW v3.8.0.k)
            const [filterPanelOpen, setFilterPanelOpen] = useState(false); // Collapsible filter panel state (NEW v3.8.0)
            const [, forceUpdate] = useState({});

            // v3.11.0.d - Ref for column menu click-outside detection
            const columnMenuRef = useRef(null);

            // v3.12.0 - Auto-scroll during drag
            const [autoScrollInterval, setAutoScrollInterval] = useState(null);

            // Status bar state (v3.9.0 - Load-state-only, 4 states)
            const [libraryStatus, setLibraryStatus] = useState({
                loadStatus: 'empty',     // empty, fresh, stale, obsolete
                loadDate: null           // ISO date string from loaded JSON metadata.fetchDate
            });
            const [collectionsStatus, setCollectionsStatus] = useState({
                loadStatus: 'empty',
                loadDate: null
            });

            // Wrapper for setSyncStatus
            const setSyncStatus = (newStatus) => {
                setSyncStatusInternal(newStatus);
            };
            const [settings, setSettings] = useState({
                cacheExpirationDays: 30
            });
            const dragThreshold = 50;

            // Load saved filters from localStorage on mount (v3.8.0.f, updated v3.8.0.k)
            React.useEffect(() => {
                try {
                    const savedFilters = localStorage.getItem(FILTERS_KEY);
                    if (savedFilters) {
                        const filters = JSON.parse(savedFilters);
                        if (filters.searchTerm !== undefined) setSearchTerm(filters.searchTerm);
                        if (filters.readStatusFilter !== undefined) setReadStatusFilter(filters.readStatusFilter);
                        if (filters.collectionFilter !== undefined) setCollectionFilter(filters.collectionFilter);
                        if (filters.ratingFilter !== undefined) setRatingFilter(filters.ratingFilter);
                        if (filters.wishlistFilter !== undefined) setWishlistFilter(filters.wishlistFilter);
                        if (filters.seriesFilter !== undefined) setSeriesFilter(filters.seriesFilter);
                        if (filters.dateFrom !== undefined) setDateFrom(filters.dateFrom);
                        if (filters.dateTo !== undefined) setDateTo(filters.dateTo);
                    }
                } catch (e) {
                    console.error('Failed to load filters from localStorage:', e);
                }
            }, []); // Empty dependency array = run once on mount

            // Save filters to localStorage whenever they change (v3.8.0.f, updated v3.8.0.k)
            React.useEffect(() => {
                try {
                    const filters = {
                        searchTerm,
                        readStatusFilter,
                        collectionFilter,
                        ratingFilter,
                        wishlistFilter,
                        seriesFilter,
                        dateFrom,
                        dateTo
                    };
                    localStorage.setItem(FILTERS_KEY, JSON.stringify(filters));
                } catch (e) {
                    console.error('Failed to save filters to localStorage:', e);
                }
            }, [searchTerm, readStatusFilter, collectionFilter, ratingFilter, wishlistFilter, seriesFilter, dateFrom, dateTo]);

            const formatAcquisitionDate = (timestamp) => {
                if (!timestamp) return '';
                const ts = typeof timestamp === 'string' ? parseInt(timestamp) : timestamp;
                const date = new Date(ts > 9999999999 ? ts : ts * 1000);
                if (isNaN(date.getTime())) return timestamp;
                return date.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                });
            };

            const getRelativeTime = (timestamp) => {
                if (!timestamp) return '';
                const now = Date.now();
                const diff = now - timestamp;
                const minutes = Math.floor(diff / 60000);
                const hours = Math.floor(diff / 3600000);
                const days = Math.floor(diff / 86400000);
                
                if (minutes < 1) return 'just now';
                if (minutes < 60) return `${minutes}m ago`;
                if (hours < 24) return `${hours}h ago`;
                return `${days}d ago`;
            };

            // checkManifest function removed in v3.6.1 - replaced with IndexedDB manifests
            // Status is now computed from libraryStatus and collectionsStatus state

            // Initial load from IndexedDB
            useEffect(() => {
                const loadData = async () => {
                    try {
                        // Load settings
                        const savedSettings = localStorage.getItem(SETTINGS_KEY);
                        if (savedSettings) {
                            setSettings(JSON.parse(savedSettings));
                        }

                        // Restore libraryStatus and collectionsStatus from localStorage (v3.7.0.n)
                        const savedStatus = localStorage.getItem(STATUS_KEY);
                        if (savedStatus) {
                            const statusData = JSON.parse(savedStatus);
                            if (statusData.libraryStatus) {
                                setLibraryStatus(statusData.libraryStatus);
                                console.log('📦 Restored libraryStatus from localStorage:', statusData.libraryStatus.loadStatus);
                            }
                            if (statusData.collectionsStatus) {
                                setCollectionsStatus(statusData.collectionsStatus);
                                console.log('📦 Restored collectionsStatus from localStorage:', statusData.collectionsStatus.loadStatus);
                            }
                        }

                        // Load books from IndexedDB
                        let loadedBooks = await loadBooksFromIndexedDB();

                        // Merge collections data into loaded books
                        if (loadedBooks.length > 0) {
                            loadedBooks = await mergeCollectionsIntoBooks(loadedBooks);
                            setBooks(loadedBooks);
                            // Update IndexedDB with merged data
                            await saveBooksToIndexedDB(loadedBooks);
                        }

                        let effectiveLastSync = null;

                        if (loadedBooks.length > 0) {
                            
                            // Load organization from localStorage
                            const saved = localStorage.getItem(STORAGE_KEY);
                            if (saved) {
                                const state = JSON.parse(saved);
                                if (state.organization?.columns) {
                                    const restoredColumns = state.organization.columns.map(col => ({
                                        id: col.id,
                                        name: col.name,
                                        books: col.bookIds || col.books
                                    }));
                                    setColumns(restoredColumns);
                                    setBlankImageBooks(new Set(state.organization.blankImageBooks || []));
                                    setDataSource(state.organization.dataSource || 'enriched');
                                    effectiveLastSync = state.lastSyncTime || Date.now();
                                    setLastSyncTime(effectiveLastSync);
                                    console.log('✅ Restored organization from localStorage');
                                } else {
                                    // No organization saved, put all books in first column
                                    setColumns([{ id: 'unorganized', name: 'Unorganized', books: loadedBooks.map(b => b.id) }]);
                                    setDataSource('enriched');
                                    effectiveLastSync = Date.now();
                                    setLastSyncTime(effectiveLastSync);
                                }
                            } else {
                                // No saved state, put all books in first column
                                setColumns([{ id: 'unorganized', name: 'Unorganized', books: loadedBooks.map(b => b.id) }]);
                                setDataSource('enriched');
                                effectiveLastSync = Date.now();
                                setLastSyncTime(effectiveLastSync);
                            }
                        }


                        // Loading complete - set syncStatus to indicate we're done loading
                        // Actual status display now comes from libraryStatus/collectionsStatus
                        setSyncStatus('none');
                    } catch (error) {
                        console.error('Failed to load data:', error);
                        setSyncStatus('none');
                    }
                };
                
                loadData();
            }, []);

            // Auto-save organization
            useEffect(() => {
                if (books.length > 0 && columns.length > 0) {
                    try {
                        const state = {
                            organization: {
                                columns: columns.map(col => ({
                                    id: col.id,
                                    name: col.name,
                                    bookIds: col.books
                                })),
                                dataSource,
                                blankImageBooks: Array.from(blankImageBooks)
                            },
                            lastSyncTime: lastSyncTime || Date.now(),
                            savedAt: Date.now()
                        };
                        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
                    } catch (e) {
                        console.warn('Could not auto-save organization:', e);
                    }
                }
            }, [columns, blankImageBooks, dataSource, lastSyncTime]);

            useEffect(() => {
                localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
            }, [settings]);

            // Save libraryStatus and collectionsStatus to localStorage (v3.7.0.n)
            useEffect(() => {
                const statusData = { libraryStatus, collectionsStatus };
                localStorage.setItem(STATUS_KEY, JSON.stringify(statusData));
            }, [libraryStatus, collectionsStatus]);

            // Expose books to window for debugging
            useEffect(() => {
                window.books = books;
            }, [books]);

            // ESC key to clear selection, Ctrl+A to select all in active column
            useEffect(() => {
                const handleKeyDown = (e) => {
                    if (e.key === 'Escape') {
                        clearSelection();
                        setContextMenu(null);
                    }

                    // Ctrl+A: Select all books in active column
                    if ((e.ctrlKey || e.metaKey) && e.key === 'a' && activeColumnId) {
                        e.preventDefault(); // Prevent browser's select-all
                        const column = columns.find(col => col.id === activeColumnId);
                        if (column) {
                            const visibleBooks = filteredBooks(column.books);
                            setSelectedBooks(new Set(visibleBooks.map(book => book.id)));
                        }
                    }
                };

                window.addEventListener('keydown', handleKeyDown);
                return () => window.removeEventListener('keydown', handleKeyDown);
            }, [activeColumnId, columns, filteredBooks]);

            // Initialize activeColumnId to first column when columns are loaded
            useEffect(() => {
                if (columns.length > 0 && !activeColumnId) {
                    setActiveColumnId(columns[0].id);
                }
            }, [columns, activeColumnId]);

            // Close context menu on click
            useEffect(() => {
                const handleClick = () => setContextMenu(null);
                if (contextMenu) {
                    window.addEventListener('click', handleClick);
                    return () => window.removeEventListener('click', handleClick);
                }
            }, [contextMenu]);

            // v3.11.0.d - Close column menu and sort submenu on ESC key
            useEffect(() => {
                const handleEsc = (e) => {
                    if (e.key === 'Escape') {
                        if (sortMenuOpen !== null) {
                            setSortMenuOpen(null);
                        } else if (columnMenuOpen !== null) {
                            setColumnMenuOpen(null);
                        }
                    }
                };
                window.addEventListener('keydown', handleEsc);
                return () => window.removeEventListener('keydown', handleEsc);
            }, [columnMenuOpen, sortMenuOpen]);

            // v3.11.0.d - Close column menu on click outside
            useEffect(() => {
                const handleClickOutside = (e) => {
                    if (columnMenuOpen !== null && columnMenuRef.current && !columnMenuRef.current.contains(e.target)) {
                        setColumnMenuOpen(null);
                        setSortMenuOpen(null);
                    }
                };
                if (columnMenuOpen !== null) {
                    document.addEventListener('mousedown', handleClickOutside);
                    return () => document.removeEventListener('mousedown', handleClickOutside);
                }
            }, [columnMenuOpen]);

            const saveSettings = (newSettings) => {
                setSettings(newSettings);
                setSettingsOpen(false);
            };

            const syncNow = async () => {
                // Close the dialog immediately when file picker opens
                setStatusModalOpen(false);

                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        try {
                            const text = await file.text();
                            const parsedData = JSON.parse(text);
                            const syncTime = Date.now();
                            setLastSyncTime(syncTime);

                            // Show loading status while waiting
                            setSyncStatus('loading');

                            let timeoutId;
                            let callbackFired = false;

                            // Setup timeout (60 seconds for large libraries)
                            timeoutId = setTimeout(() => {
                                if (!callbackFired) {
                                    console.error('⚠️ Status check timed out after 60 seconds');
                                    setSyncStatus('unknown');
                                    alert('Library loaded but status check timed out. Please refresh the page.');
                                }
                            }, 60000);

                            // Load data with callback
                            await loadEnrichedData(text, () => {
                                callbackFired = true;
                                clearTimeout(timeoutId);
                                // checkManifest removed in v3.6.1 - status updated in loadEnrichedData
                            });

                        } catch (error) {
                            console.error('Failed to sync:', error);
                            setSyncStatus('none'); // Clear loading spinner (v3.9.0.l)
                            if (error && error.message) {
                                console.error('Error details:', error.message, error.stack);
                                alert(`Failed to load library file: ${error.message}`);
                            } else {
                                console.error('Error details: Unknown error (null or no message)');
                                alert('Failed to load library file: Unknown error');
                            }
                        }
                    }
                };
                input.click();
            };

            const loadCollectionsNow = async () => {
                // Close the dialog immediately when file picker opens
                setStatusModalOpen(false);

                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        try {
                            const text = await file.text();
                            const parsedData = JSON.parse(text);
                            const syncTime = Date.now();
                            setLastSyncTime(syncTime);

                            // Show loading status while waiting
                            setSyncStatus('loading');

                            let timeoutId;
                            let callbackFired = false;

                            // Setup timeout (60 seconds)
                            timeoutId = setTimeout(() => {
                                if (!callbackFired) {
                                    console.error('⚠️ Status check timed out after 60 seconds');
                                    setSyncStatus('unknown');
                                    alert('Collections loaded but status check timed out. Please refresh the page.');
                                }
                            }, 60000);

                            // Load collections data with callback
                            await loadCollectionsFromFile(text, (collectionsCount) => {
                                callbackFired = true;
                                clearTimeout(timeoutId);
                                setSyncStatus('none');
                            });

                        } catch (error) {
                            console.error('Failed to load collections:', error);
                            setSyncStatus('none'); // Clear loading spinner (v3.9.0.l)
                            if (error && error.message) {
                                console.error('Error details:', error.message, error.stack);
                                alert(`Failed to load collections file: ${error.message}`);
                            } else {
                                console.error('Error details: Unknown error (null or no message)');
                                alert('Failed to load collections file: Unknown error');
                            }
                        }
                    }
                };
                input.click();
            };

            const openCollectSeriesDialog = () => {
                if (!modalBook || !modalBook.series || !modalColumnId) return;
                
                const currentColumn = columns.find(c => c.id === modalColumnId);
                if (!currentColumn) return;
                
                const allSeriesBooks = books.filter(b => 
                    b.series && b.series === modalBook.series && b.id !== modalBook.id
                );
                
                const inCurrentColumn = allSeriesBooks.filter(b => 
                    currentColumn.books.includes(b.id)
                );
                
                const inOtherColumns = allSeriesBooks.filter(b => 
                    !currentColumn.books.includes(b.id)
                ).map(b => {
                    const col = columns.find(c => c.books.includes(b.id));
                    return { ...b, columnName: col?.name || 'Unknown' };
                });
                
                const sortByPosition = (a, b) => {
                    const posA = parseInt(a.seriesPosition) || 999;
                    const posB = parseInt(b.seriesPosition) || 999;
                    return posA - posB;
                };
                
                inCurrentColumn.sort(sortByPosition);
                inOtherColumns.sort(sortByPosition);
                
                setSeriesBooks({
                    current: inCurrentColumn,
                    other: inOtherColumns
                });
                
                setCollectSeriesOpen(true);
            };

            const collectSeriesBooks = (includeAllColumns) => {
                if (!modalBook || !modalColumnId) return;
                
                const targetColumn = columns.find(c => c.id === modalColumnId);
                if (!targetColumn) return;
                
                const booksToCollect = includeAllColumns 
                    ? [...seriesBooks.current, ...seriesBooks.other]
                    : seriesBooks.current;
                
                if (booksToCollect.length === 0) {
                    setCollectSeriesOpen(false);
                    return;
                }
                
                const allBooksInSeries = [modalBook, ...booksToCollect].sort((a, b) => {
                    const posA = parseInt(a.seriesPosition) || 999;
                    const posB = parseInt(b.seriesPosition) || 999;
                    return posA - posB;
                });
                
                const currentBookIndexInTarget = targetColumn.books.indexOf(modalBook.id);
                
                const newColumns = columns.map(col => {
                    if (col.id === modalColumnId) {
                        let newBooks = col.books.filter(id => 
                            !allBooksInSeries.find(b => b.id === id)
                        );
                        
                        const insertIndex = Math.min(currentBookIndexInTarget, newBooks.length);
                        newBooks.splice(insertIndex, 0, ...allBooksInSeries.map(b => b.id));
                        
                        return { ...col, books: newBooks };
                    } else if (includeAllColumns) {
                        return {
                            ...col,
                            books: col.books.filter(id => 
                                !allBooksInSeries.find(b => b.id === id)
                            )
                        };
                    }
                    return col;
                });
                
                setColumns(newColumns);
                setCollectSeriesOpen(false);
            };

            const renderStars = (rating) => {
                const fullStars = Math.floor(rating);
                const hasHalfStar = rating % 1 >= 0.5;
                const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
                
                return (
                    <span className="text-yellow-500 text-2xl">
                        {'★'.repeat(fullStars)}
                        {hasHalfStar && '½'}
                        {'☆'.repeat(emptyStars)}
                    </span>
                );
            };

            const exportBackup = async () => {
                try {
                    const allBooks = await loadBooksFromIndexedDB();
                    const state = {
                        books: allBooks,
                        columns,
                        dataSource,
                        blankImageBooks: Array.from(blankImageBooks),
                        lastSyncTime: lastSyncTime || Date.now(),
                        backupDate: new Date().toISOString(),
                        version: ORGANIZER_VERSION
                    };
                    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `readerwrangler-backup-${new Date().toISOString().split('T')[0]}.json`;
                    a.click();
                    URL.revokeObjectURL(url);
                    console.log('✅ Backup created');
                } catch (error) {
                    console.error('Failed to create backup:', error);
                    alert('Failed to create backup');
                }
            };

            const importRestore = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                try {
                    const text = await file.text();
                    const state = JSON.parse(text);
                    
                    if (state.books && state.columns) {
                        // Save books to IndexedDB
                        await saveBooksToIndexedDB(state.books);
                        setBooks(state.books);
                        
                        // Restore organization
                        setColumns(state.columns);
                        setDataSource(state.dataSource || 'enriched');
                        setBlankImageBooks(new Set(state.blankImageBooks || []));
                        setLastSyncTime(state.lastSyncTime || Date.now());
                        
                        console.log('✅ Restored from backup');
                        alert('✅ Successfully restored from backup!');
                    } else {
                        alert('Invalid backup file');
                    }
                } catch (e) {
                    console.error('Failed to restore:', e);
                    alert('Failed to restore from backup');
                }
            };

            const clearLibrary = () => {
                setResetConfirmOpen(true);
            };

            const confirmReset = async () => {
                setResetConfirmOpen(false);
                try {
                    await clearIndexedDB();
                    localStorage.removeItem(STORAGE_KEY);
                    localStorage.removeItem(CACHE_KEY);
                    localStorage.removeItem(STATUS_KEY); // v3.7.0.n - clear saved status
                    localStorage.removeItem(FILTERS_KEY); // v3.8.0.h - clear saved filters

                    // Reset all filters (v3.8.0.h, updated v3.8.0.k)
                    setSearchTerm('');
                    setReadStatusFilter('');
                    setCollectionFilter('');
                    setRatingFilter('');
                    setWishlistFilter('');
                    setSeriesFilter('');
                    setDateFrom('');
                    setDateTo('');

                    setBooks([]);
                    setColumns([{ id: 'unorganized', name: 'Unorganized', books: [] }]);
                    setDataSource('none');
                    setBlankImageBooks(new Set());
                    setLastSyncTime(null);
                    setSyncStatus('none');
                    // Reset v3.9.0 status bar state (Load-state-only)
                    setLibraryStatus({
                        loadStatus: 'empty',
                        loadDate: null
                    });
                    setCollectionsStatus({
                        loadStatus: 'empty',
                        loadDate: null
                    });
                    console.log('✅ Cleared library - app reset to initial state');
                } catch (error) {
                    console.error('Failed to clear library:', error);
                    alert('Failed to clear library data');
                }
            };

            const handleFileUpload = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const text = await file.text();
                
                if (file.name.endsWith('.json')) {
                    await loadEnrichedData(text);
                } else if (file.name.endsWith('.csv')) {
                    loadBooksFromCSV(text);
                }
            };

            const loadBooksFromCSV = (csvContent) => {
                const lines = csvContent.split('\n');
                const parsedBooks = [];
                
                const startLine = lines[0].includes('ASIN') ? 1 : 0;
                
                for (let i = startLine; i < lines.length && parsedBooks.length < 100; i++) {
                    const line = lines[i].trim();
                    if (!line) continue;
                    
                    const parts = line.split(',');
                    let asin = parts[0]?.trim().replace(/[="']/g, '');
                    
                    if (asin && asin.length < 10 && /^[0-9]+$/.test(asin)) {
                        asin = asin.padStart(10, '0');
                    }
                    
                    if (asin && asin.length === 10) {
                        parsedBooks.push({
                            id: asin,  // Use ASIN as stable ID instead of sequential number
                            asin: asin,
                            title: parts[6] || 'Unknown',
                            author: parts[13] || 'Unknown',
                            acquired: parts[2] || '',
                            series: parts[12] || '',
                            coverUrl: `https://images-na.ssl-images-amazon.com/images/P/${asin}.01.LZZZZZZZ.jpg`,
                            hasEnrichedData: false
                        });
                    }
                }
                
                setBooks(parsedBooks);
                setColumns([{ id: 'unorganized', name: 'Unorganized', books: parsedBooks.map(b => b.id) }]);
                setDataSource('csv');
            };

            const loadCollectionsData = async () => {
                try {
                    // ARCHITECTURE: Cache-Busting - See docs/design/ARCHITECTURE.md (Cache-Busting section)
                    // Try to fetch collections data from same directory with cache-busting
                    const response = await fetch(`amazon-collections.json?t=${Date.now()}`);
                    if (!response.ok) {
                        console.log('No collections data file found (this is optional)');
                        return null;
                    }

                    const collectionsJson = await response.json();

                    // Validate schema version (1.0)
                    if (collectionsJson.schemaVersion !== '1.0') {
                        console.warn('Collections data schema version mismatch, skipping');
                        return null;
                    }

                    // Create a Map indexed by ASIN for O(1) lookup
                    const collectionsMap = new Map();

                    collectionsJson.books.forEach(book => {
                        collectionsMap.set(book.asin, {
                            readStatus: book.readStatus,
                            collections: book.collections || []
                        });
                    });

                    console.log(`✅ Loaded collections data for ${collectionsMap.size} books`);
                    console.log(`   - ${collectionsJson.booksWithCollections} books have collections`);
                    console.log(`   - Fetcher version: ${collectionsJson.fetcherVersion}`);

                    // Update collections status (v3.9.0 - Load-state-only)
                    const loadStatus = collectionsJson.fetchDate ? calculateFreshness(collectionsJson.fetchDate) : 'unknown';

                    setCollectionsStatus({
                        loadStatus,
                        loadDate: collectionsJson.fetchDate || null
                    });

                    setCollectionsData(collectionsMap);
                    return collectionsMap;
                } catch (error) {
                    console.log('Could not load collections data (this is optional):', error.message);
                    return null;
                }
            };

            const loadCollectionsFromFile = async (content, onComplete = null) => {
                const collectionsJson = JSON.parse(content);

                // Check if user selected library file instead of collections file (v3.9.0.k)
                if (collectionsJson.type === 'library') {
                    console.error('❌ Wrong file type selected');
                    console.error('   You selected a Library file');
                    console.error('   Please select your Collections file instead');
                    throw new Error('You selected a Library file. Please select your Collections file instead.');
                }

                // Validate schema version (1.0)
                if (collectionsJson.schemaVersion !== '1.0') {
                    console.error('❌ Invalid collections JSON format');
                    console.error('   Expected schema v1.0');
                    console.error('   Received schema:', collectionsJson.schemaVersion);
                    throw new Error('Invalid collections JSON format - please re-fetch your collections using the latest fetcher');
                }

                // Create a Map indexed by ASIN for O(1) lookup
                const collectionsMap = new Map();

                collectionsJson.books.forEach(book => {
                    collectionsMap.set(book.asin, {
                        readStatus: book.readStatus,
                        collections: book.collections || []
                    });
                });

                console.log(`✅ Loaded collections data for ${collectionsMap.size} books`);
                console.log(`   - ${collectionsJson.booksWithCollections} books have collections`);
                console.log(`   - Fetcher version: ${collectionsJson.fetcherVersion}`);
                console.log(`   - Fetched: ${new Date(collectionsJson.fetchDate).toLocaleString()}`);

                // Update collections status (v3.9.0 - Load-state-only)
                const loadStatus = collectionsJson.fetchDate ? calculateFreshness(collectionsJson.fetchDate) : 'unknown';

                setCollectionsStatus({
                    loadStatus,
                    loadDate: collectionsJson.fetchDate || null
                });

                setCollectionsData(collectionsMap);

                // Merge collections into existing books and re-save to IndexedDB (v3.9.0.j)
                // Pass collectionsMap directly instead of relying on state (state update is async)
                const mergedBooks = books.map(book => {
                    const bookCollections = collectionsMap.get(book.asin) || { readStatus: 'UNKNOWN', collections: [] };
                    return {
                        ...book,
                        readStatus: bookCollections.readStatus,
                        collections: bookCollections.collections
                    };
                });
                await saveBooksToIndexedDB(mergedBooks);
                setBooks(mergedBooks);

                // Log merge results
                const booksWithCollections = mergedBooks.filter(b => b.collections && b.collections.length > 0).length;
                const readBooks = mergedBooks.filter(b => b.readStatus === 'READ').length;
                const unreadBooks = mergedBooks.filter(b => b.readStatus === 'UNREAD').length;
                console.log(`📚 Collections data merged:`);
                console.log(`   - ${booksWithCollections} books have collections`);
                console.log(`   - ${readBooks} READ, ${unreadBooks} UNREAD, ${mergedBooks.length - readBooks - unreadBooks} UNKNOWN`);

                // Trigger callback if provided
                if (onComplete) {
                    onComplete(collectionsMap.size);
                }

                return collectionsMap;
            };

            const mergeCollectionsIntoBooks = async (booksToMerge) => {
                // Only use collections data if user has loaded it via File Picker (v3.9.0)
                const collections = collectionsData;
                if (!collections) {
                    console.log('No collections data available to merge');
                    return booksToMerge;
                }

                // Merge collections into each book
                const mergedBooks = booksToMerge.map(book => {
                    const bookCollections = collections.get(book.asin) || { readStatus: 'UNKNOWN', collections: [] };
                    return {
                        ...book,
                        readStatus: bookCollections.readStatus,
                        collections: bookCollections.collections
                    };
                });

                // Log results
                const booksWithCollections = mergedBooks.filter(b => b.collections.length > 0).length;
                const readBooks = mergedBooks.filter(b => b.readStatus === 'READ').length;
                const unreadBooks = mergedBooks.filter(b => b.readStatus === 'UNREAD').length;
                console.log(`📚 Collections data merged:`);
                console.log(`   - ${booksWithCollections} books have collections`);
                console.log(`   - ${readBooks} READ, ${unreadBooks} UNREAD, ${mergedBooks.length - readBooks - unreadBooks} UNKNOWN`);

                // Show sample book with collections for verification
                const sampleBook = mergedBooks.find(b => b.collections.length > 0);
                if (sampleBook) {
                    console.log(`\n📖 Sample book with collections:`);
                    console.log(`   Title: ${sampleBook.title}`);
                    console.log(`   ASIN: ${sampleBook.asin}`);
                    console.log(`   Read Status: ${sampleBook.readStatus}`);
                    console.log(`   Collections: ${sampleBook.collections.map(c => c.name).join(', ')}`);
                }

                return mergedBooks;
            };

            const loadEnrichedData = async (content, onComplete = null) => {
                const parsedData = JSON.parse(content);

                // Check if user selected collections file instead of library file (v3.9.0.k)
                if (parsedData.type === 'collections') {
                    console.error('❌ Wrong file type selected');
                    console.error('   You selected a Collections file');
                    console.error('   Please select your Library file instead');
                    throw new Error('You selected a Collections file. Please select your Library file instead.');
                }

                // Schema v3.0.0 - object with metadata and books array
                if (!parsedData.metadata || !parsedData.books) {
                    console.error('❌ Invalid library JSON format');
                    console.error('   Expected schema v3.0.0: {metadata, books}');
                    console.error('   Received:', Object.keys(parsedData));
                    throw new Error('Invalid library JSON format - please re-fetch your library using the latest fetcher');
                }

                const data = parsedData.books;
                const metadata = parsedData.metadata;

                console.log(`📋 Loaded schema ${metadata.schemaVersion}`);
                console.log(`   Total books: ${metadata.totalBooks}`);
                console.log(`   Books without descriptions: ${metadata.booksWithoutDescriptions}`);
                console.log(`   Fetched: ${new Date(metadata.fetchDate).toLocaleString()}`);
                console.log(`   Fetcher version: ${metadata.fetcherVersion}`);

                // Update library status from loaded JSON metadata (v3.9.0 - Load-state-only)
                const loadStatus = metadata.fetchDate ? calculateFreshness(metadata.fetchDate) : 'unknown';

                setLibraryStatus({
                    loadStatus,
                    loadDate: metadata.fetchDate || null
                });

                // Collections must be loaded via File Picker (v3.9.0 - Load-State-Only)
                // Auto-fetch removed to ensure user controls which files are loaded
                const collections = collectionsData || null;

                const extractDescription = (descData) => {
                    if (!descData?.sections?.[0]?.content) return '';
                    
                    const content = descData.sections[0].content;
                    
                    if (content.text) return content.text;
                    
                    if (content.fragments) {
                        const texts = [];
                        content.fragments.forEach(frag => {
                            if (frag.text) {
                                texts.push(frag.text);
                            } else if (frag.semanticContent?.content?.text) {
                                texts.push(frag.semanticContent.content.text);
                            } else if (frag.semanticContent?.content?.fragments) {
                                frag.semanticContent.content.fragments.forEach(subfrag => {
                                    if (subfrag.text) texts.push(subfrag.text);
                                    if (subfrag.semanticContent?.content?.text) {
                                        texts.push(subfrag.semanticContent.content.text);
                                    }
                                });
                            }
                        });
                        return texts.join(' ').trim();
                    }
                    
                    return '';
                };
                
                const processedBooks = data.map((item) => {
                    const isNewFormat = !item.amazonData;

                    // Get collections data for this book (if available)
                    const bookCollections = collections?.get(item.asin) || { readStatus: 'UNKNOWN', collections: [] };

                    if (isNewFormat) {
                        return {
                            id: item.asin,  // Use ASIN as stable ID instead of sequential number
                            asin: item.asin,
                            title: item.title || 'Unknown',
                            author: item.authors || 'Unknown',
                            acquired: item.acquisitionDate || '',
                            series: item.series || '',
                            seriesPosition: item.seriesPosition || '',
                            seriesTotal: '',
                            rating: item.rating || 0,
                            ratingCount: item.reviewCount || '',
                            description: item.description || '',
                            topReviews: item.topReviews || [],
                            binding: item.binding || 'Kindle eBook',
                            coverUrl: item.coverUrl,
                            hasEnrichedData: true,
                            store: "Amazon",
                            isWishlist: item.isWishlist || 0,  // NEW v3.8.0.n - wishlist flag
                            // Collections data
                            readStatus: bookCollections.readStatus,
                            collections: bookCollections.collections
                        };
                    } else {
                        const amazonData = item.amazonData?.data?.getProduct;
                        const imageData = amazonData?.images?.images?.[0]?.hiRes;
                        
                        let asin = item.asin;
                        if (asin && asin.length < 10 && /^[0-9]+$/.test(asin)) {
                            asin = asin.padStart(10, '0');
                        }
                        
                        let coverUrl = `https://images-na.ssl-images-amazon.com/images/P/${asin}.01.LZZZZZZZ.jpg`;
                        if (imageData?.physicalId) {
                            coverUrl = `https://images-na.ssl-images-amazon.com/images/I/${imageData.physicalId}.${imageData.extension}`;
                        }
                        
                        return {
                            id: asin,  // Use ASIN as stable ID instead of sequential number
                            asin: asin,
                            title: amazonData?.title?.displayString || item.title || 'Unknown',
                            author: amazonData?.byLine?.contributors?.[0]?.contributor?.author?.profile?.displayName || item.author || 'Unknown',
                            acquired: amazonData?.pastPurchase?.purchaseHistory?.lastOrderDate || item.acquired || '',
                            series: amazonData?.bookSeries?.singleBookView?.series?.title || '',
                            seriesPosition: amazonData?.bookSeries?.singleBookView?.series?.position || '',
                            seriesTotal: amazonData?.bookSeries?.singleBookView?.series?.numberOfBooks || '',
                            rating: amazonData?.customerReviewsSummary?.rating?.value || 0,
                            ratingCount: amazonData?.customerReviewsSummary?.count?.displayString || '',
                            description: extractDescription(amazonData?.description),
                            topReviews: amazonData?.customerReviewsTop?.reviews || [],
                            binding: amazonData?.bindingInformation?.binding?.displayString || 'Kindle eBook',
                            coverUrl: coverUrl,
                            hasEnrichedData: true,
                            store: "Amazon",
                            // Collections data
                            readStatus: bookCollections.readStatus,
                            collections: bookCollections.collections
                        };
                    }
                });

                // Sort books by acquisition date (newest first) to maintain original order
                try {
                    processedBooks.sort((a, b) => {
                        // Handle missing dates - put them at the end
                        if (!a.acquired && !b.acquired) return 0;
                        if (!a.acquired) return 1;
                        if (!b.acquired) return -1;

                        // Parse dates safely
                        const dateA = new Date(a.acquired);
                        const dateB = new Date(b.acquired);

                        // Handle invalid dates
                        const isValidA = !isNaN(dateA.getTime());
                        const isValidB = !isNaN(dateB.getTime());

                        if (!isValidA && !isValidB) return 0;
                        if (!isValidA) return 1;
                        if (!isValidB) return -1;

                        // Compare dates (descending - newest first)
                        return dateB - dateA;
                    });
                    console.log('✅ Books sorted by acquisition date (newest first)');
                } catch (error) {
                    console.error('❌ Sort failed:', error);
                    console.error('Error details:', error.message, error.stack);
                    // Continue without sorting if sort fails
                }

                // Log collections merge results
                if (collections) {
                    const booksWithCollections = processedBooks.filter(b => b.collections.length > 0).length;
                    const readBooks = processedBooks.filter(b => b.readStatus === 'READ').length;
                    const unreadBooks = processedBooks.filter(b => b.readStatus === 'UNREAD').length;
                    console.log(`📚 Collections data merged:`);
                    console.log(`   - ${booksWithCollections} books have collections`);
                    console.log(`   - ${readBooks} READ, ${unreadBooks} UNREAD, ${processedBooks.length - readBooks - unreadBooks} UNKNOWN`);

                    // Show sample book with collections for verification
                    const sampleBook = processedBooks.find(b => b.collections.length > 0);
                    if (sampleBook) {
                        console.log(`\n📖 Sample book with collections:`);
                        console.log(`   Title: ${sampleBook.title}`);
                        console.log(`   ASIN: ${sampleBook.asin}`);
                        console.log(`   Read Status: ${sampleBook.readStatus}`);
                        console.log(`   Collections: ${sampleBook.collections.map(c => c.name).join(', ')}`);
                    }
                }

                // Save to IndexedDB
                await saveBooksToIndexedDB(processedBooks);
                setBooks(processedBooks);

                // Reset all filters when loading new library (v3.8.0.g, updated v3.8.0.k)
                setSearchTerm('');
                setReadStatusFilter('');
                setCollectionFilter('');
                setRatingFilter('');
                setWishlistFilter('');
                setSeriesFilter('');
                setDateFrom('');
                setDateTo('');
                localStorage.setItem(FILTERS_KEY, JSON.stringify({
                    searchTerm: '',
                    readStatusFilter: '',
                    collectionFilter: '',
                    ratingFilter: '',
                    wishlistFilter: '',
                    seriesFilter: '',
                    dateFrom: '',
                    dateTo: ''
                }));
                console.log('🔍 Filters cleared for new library');

                // Check if we have saved organization to restore
                try {
                    const saved = localStorage.getItem(STORAGE_KEY);
                    if (saved) {
                        const state = JSON.parse(saved);
                        if (state.organization?.columns) {
                            const restoredColumns = state.organization.columns.map(col => ({
                                id: col.id,
                                name: col.name,
                                books: col.bookIds || col.books
                            }));
                            setColumns(restoredColumns);
                            setBlankImageBooks(new Set(state.organization.blankImageBooks || []));
                            console.log('✅ Restored saved organization');
                            setDataSource('enriched');
                            setLastSyncTime(Date.now());
                            setSyncStatus('fresh');
                            if (onComplete) setTimeout(() => onComplete(metadata.totalBooks), 0);
                            return;
                        }
                    }
                } catch (e) {
                    console.log('Note: Could not restore organization, starting fresh');
                }
                
                // No saved organization, start fresh
                setColumns([{ id: 'unorganized', name: 'Unorganized', books: processedBooks.map(b => b.id) }]);
                setDataSource('enriched');
                setLastSyncTime(Date.now());
                setSyncStatus('fresh');
                if (onComplete) setTimeout(() => onComplete(metadata.totalBooks), 0);
            };

            const addColumn = () => {
                const newId = `col-${Date.now()}`;
                setColumns([...columns, { id: newId, name: 'New Column', books: [] }]);
                // Set this column to edit mode immediately
                setTimeout(() => setEditingColumn(newId), 0);
            };

            const startEditingColumn = (columnId, currentName) => {
                setEditingColumn(columnId);
                setEditingName(currentName);
            };

            const finishEditingColumn = (columnId) => {
                if (editingName.trim()) {
                    setColumns(columns.map(col => 
                        col.id === columnId ? { ...col, name: editingName.trim() } : col
                    ));
                }
                setEditingColumn(null);
                setEditingName('');
            };

            const sortColumn = (columnId, sortType) => {
                setColumns(columns.map(col => {
                    if (col.id !== columnId) return col;
                    
                    const sortedBookIds = [...col.books].sort((aId, bId) => {
                        const a = books.find(b => b.id === aId);
                        const b = books.find(b => b.id === bId);
                        if (!a || !b) return 0;
                        
                        switch(sortType) {
                            case 'title-asc':
                                return a.title.localeCompare(b.title);
                            case 'title-desc':
                                return b.title.localeCompare(a.title);
                            case 'author-asc':
                                return a.author.localeCompare(b.author);
                            case 'author-desc':
                                return b.author.localeCompare(a.author);
                            case 'rating-desc':
                                return (b.rating || 0) - (a.rating || 0);
                            case 'rating-asc':
                                return (a.rating || 0) - (b.rating || 0);
                            case 'acquired-desc':
                                return (b.acquired || '').localeCompare(a.acquired || '');
                            case 'acquired-asc':
                                return (a.acquired || '').localeCompare(b.acquired || '');
                            case 'series-pos-asc':
                                // v3.11.0.e - Books without series go to end, books with series but no position go last in their series
                                const aHasSeriesAsc = a.series;
                                const bHasSeriesAsc = b.series;

                                if (!aHasSeriesAsc && !bHasSeriesAsc) return 0; // Both have no series, keep original order
                                if (!aHasSeriesAsc) return 1; // a has no series, goes after b
                                if (!bHasSeriesAsc) return -1; // b has no series, goes after a

                                // Primary sort: group by series name (alphabetical)
                                const seriesCompareAsc = a.series.localeCompare(b.series);
                                if (seriesCompareAsc !== 0) return seriesCompareAsc;

                                // Secondary sort: position within same series (books without position go last)
                                return (parseInt(a.seriesPosition) || 999) - (parseInt(b.seriesPosition) || 999);
                            case 'series-pos-desc':
                                // v3.11.0.e - Books without series go to end, books with series but no position go last in their series
                                const aHasSeriesDesc = a.series;
                                const bHasSeriesDesc = b.series;

                                if (!aHasSeriesDesc && !bHasSeriesDesc) return 0; // Both have no series, keep original order
                                if (!aHasSeriesDesc) return 1; // a has no series, goes after b
                                if (!bHasSeriesDesc) return -1; // b has no series, goes after a

                                // Primary sort: group by series name (alphabetical)
                                const seriesCompareDesc = a.series.localeCompare(b.series);
                                if (seriesCompareDesc !== 0) return seriesCompareDesc;

                                // Secondary sort: position within same series (REVERSED, books without position go last)
                                return (parseInt(b.seriesPosition) || 999) - (parseInt(a.seriesPosition) || 999);
                            default:
                                return 0;
                        }
                    });
                    
                    return { ...col, books: sortedBookIds };
                }));
                setSortMenuOpen(null);
                setColumnMenuOpen(null); // v3.11.0 - Also close parent menu
            };

            const checkIfBlankImage = (img, bookId) => {
                if (img.naturalWidth === 1 && img.naturalHeight === 1) {
                    setBlankImageBooks(prev => new Set([...prev, bookId]));
                }
            };

            const openDeleteDialog = (columnId) => {
                const col = columns.find(c => c.id === columnId);
                
                if (col && col.books.length === 0) {
                    setColumns(columns.filter(c => c.id !== columnId));
                    return;
                }
                
                const otherColumns = columns.filter(c => c.id !== columnId);
                if (otherColumns.length > 0) {
                    setDeleteDialogOpen(columnId);
                    setDeleteDestination(otherColumns[0].id);
                }
            };

            const confirmDeleteColumn = () => {
                const columnToDelete = columns.find(c => c.id === deleteDialogOpen);
                const destinationColumn = columns.find(c => c.id === deleteDestination);

                if (!columnToDelete || !destinationColumn) return;

                setColumns(columns.filter(c => c.id !== deleteDialogOpen).map(c =>
                    c.id === deleteDestination ? { ...c, books: [...c.books, ...columnToDelete.books] } : c
                ));

                setDeleteDialogOpen(null);
                setDeleteDestination('');
            };

            // v3.11.0 - Divider Functions
            const insertDivider = (columnId) => {
                if (!newDividerLabel.trim()) return;

                const dividerId = `divider-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                const divider = {
                    type: 'divider',
                    id: dividerId,
                    label: newDividerLabel.trim()
                };

                setColumns(columns.map(col => {
                    if (col.id !== columnId) return col;

                    // Find insertion position: before first selected book, or at top if no selection
                    let insertIndex = 0; // Default to top
                    if (selectedBooks.size > 0) {
                        // Find first selected book in this column
                        const firstSelectedIndex = col.books.findIndex(item =>
                            typeof item === 'string' && selectedBooks.has(item)
                        );
                        if (firstSelectedIndex !== -1) {
                            insertIndex = firstSelectedIndex;
                        }
                    }

                    const newBooks = [...col.books];
                    newBooks.splice(insertIndex, 0, divider);
                    return { ...col, books: newBooks };
                }));

                setInsertDividerOpen(null);
                setNewDividerLabel('');
                setColumnMenuOpen(null);
            };

            const startEditingDivider = (columnId, dividerId, currentLabel) => {
                setEditingDivider({ columnId, dividerId });
                setEditingDividerLabel(currentLabel);
            };

            const finishEditingDivider = () => {
                if (!editingDivider) return;

                const { columnId, dividerId } = editingDivider;
                const newLabel = editingDividerLabel.trim();

                if (!newLabel) {
                    setEditingDivider(null);
                    setEditingDividerLabel('');
                    return;
                }

                setColumns(columns.map(col =>
                    col.id === columnId
                        ? {
                            ...col,
                            books: col.books.map(item =>
                                (typeof item === 'object' && item.type === 'divider' && item.id === dividerId)
                                    ? { ...item, label: newLabel }
                                    : item
                            )
                        }
                        : col
                ));

                setEditingDivider(null);
                setEditingDividerLabel('');
            };

            const deleteDivider = (columnId, dividerId) => {
                setColumns(columns.map(col =>
                    col.id === columnId
                        ? {
                            ...col,
                            books: col.books.filter(item =>
                                !(typeof item === 'object' && item.type === 'divider' && item.id === dividerId)
                            )
                        }
                        : col
                ));
            };

            const autoDivideBySeries = (columnId) => {
                const column = columns.find(c => c.id === columnId);
                if (!column) return;

                // Get actual book objects (not dividers)
                const bookItems = column.books.filter(item => typeof item === 'string');
                const bookObjects = bookItems.map(id => books.find(b => b.id === id)).filter(Boolean);

                if (bookObjects.length === 0) return;

                // Group books by series (books without series stay at end)
                const seriesGroups = {};
                const noSeriesBooks = [];

                bookObjects.forEach(book => {
                    if (book.series) {
                        if (!seriesGroups[book.series]) {
                            seriesGroups[book.series] = [];
                        }
                        seriesGroups[book.series].push(book.id);
                    } else {
                        noSeriesBooks.push(book.id);
                    }
                });

                // Sort series names alphabetically
                const sortedSeriesNames = Object.keys(seriesGroups).sort((a, b) => a.localeCompare(b));

                // v3.11.0.f - Sort books within each series by position
                sortedSeriesNames.forEach(seriesName => {
                    const bookIds = seriesGroups[seriesName];
                    const seriesBookObjects = bookIds.map(id => books.find(b => b.id === id)).filter(Boolean);

                    // Sort by seriesPosition (books without position go last)
                    seriesBookObjects.sort((a, b) => {
                        return (parseInt(a.seriesPosition) || 999) - (parseInt(b.seriesPosition) || 999);
                    });

                    // Update the group with sorted IDs
                    seriesGroups[seriesName] = seriesBookObjects.map(book => book.id);
                });

                // Build new books array with dividers
                const newBooks = [];
                sortedSeriesNames.forEach(seriesName => {
                    const dividerId = `divider-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                    newBooks.push({
                        type: 'divider',
                        id: dividerId,
                        label: seriesName
                    });
                    newBooks.push(...seriesGroups[seriesName]);
                });

                // v3.11.0.e - Add "Miscellaneous" divider for books without series
                if (noSeriesBooks.length > 0) {
                    const dividerId = `divider-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                    newBooks.push({
                        type: 'divider',
                        id: dividerId,
                        label: 'Miscellaneous'
                    });
                    newBooks.push(...noSeriesBooks);
                }

                setColumns(columns.map(col =>
                    col.id === columnId ? { ...col, books: newBooks } : col
                ));

                setColumnMenuOpen(null);
            };

            const autoDivideByRating = (columnId) => {
                const column = columns.find(c => c.id === columnId);
                if (!column) return;

                // Get actual book objects (not dividers)
                const bookItems = column.books.filter(item => typeof item === 'string');
                const bookObjects = bookItems.map(id => books.find(b => b.id === id)).filter(Boolean);

                if (bookObjects.length === 0) return;

                // Group books by rating tier
                const ratingTiers = {
                    '5 Stars': [],
                    '4 Stars': [],
                    '3 Stars': [],
                    '2 Stars': [],
                    '1 Star': [],
                    'No Rating': []
                };

                bookObjects.forEach(book => {
                    if (!book.rating || book.rating === 0) {
                        ratingTiers['No Rating'].push(book.id);
                    } else if (book.rating >= 4.5) {
                        ratingTiers['5 Stars'].push(book.id);
                    } else if (book.rating >= 3.5) {
                        ratingTiers['4 Stars'].push(book.id);
                    } else if (book.rating >= 2.5) {
                        ratingTiers['3 Stars'].push(book.id);
                    } else if (book.rating >= 1.5) {
                        ratingTiers['2 Stars'].push(book.id);
                    } else {
                        ratingTiers['1 Star'].push(book.id);
                    }
                });

                // Build new books array with dividers (only for non-empty tiers)
                const tierOrder = ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star', 'No Rating'];
                const newBooks = [];

                tierOrder.forEach(tier => {
                    if (ratingTiers[tier].length > 0) {
                        const dividerId = `divider-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                        newBooks.push({
                            type: 'divider',
                            id: dividerId,
                            label: tier
                        });
                        newBooks.push(...ratingTiers[tier]);
                    }
                });

                setColumns(columns.map(col =>
                    col.id === columnId ? { ...col, books: newBooks } : col
                ));

                setColumnMenuOpen(null);
            };

            const openBookModal = (book, columnId) => {
                try {
                    const cache = localStorage.getItem(CACHE_KEY);
                    if (cache) {
                        const cacheData = JSON.parse(cache);
                        if (cacheData[book.asin]) {
                            const cached = cacheData[book.asin];
                            book = {
                                ...book,
                                description: cached.description || book.description,
                                rating: cached.rating || book.rating,
                                ratingCount: cached.ratingCount || book.ratingCount,
                                topReviews: cached.topReviews || book.topReviews
                            };
                        }
                    }
                } catch (e) {
                    console.error('Cache read error:', e);
                }
                
                setModalBook(book);
                setModalColumnId(columnId);
                setShowAllReviews(false);
            };

            const closeBookModal = () => {
                setModalBook(null);
                setModalColumnId(null);
            };

            // Multi-select helper functions
            const toggleBookSelection = (bookId) => {
                setSelectedBooks(prev => {
                    const newSet = new Set(prev);
                    if (newSet.has(bookId)) {
                        newSet.delete(bookId);
                    } else {
                        newSet.add(bookId);
                    }
                    return newSet;
                });
            };

            const selectBookRange = (startBookId, endBookId, columnId) => {
                // Only select within the same column
                const column = columns.find(col => col.id === columnId);
                if (!column) return;

                const visibleBooks = filteredBooks(column.books);
                const startIdx = visibleBooks.findIndex(b => b.id === startBookId);
                const endIdx = visibleBooks.findIndex(b => b.id === endBookId);

                if (startIdx === -1 || endIdx === -1) return;

                const [min, max] = [Math.min(startIdx, endIdx), Math.max(startIdx, endIdx)];
                const rangeBooks = visibleBooks.slice(min, max + 1);
                const rangeIds = rangeBooks.map(book => book.id);

                setSelectedBooks(new Set(rangeIds));
            };

            const clearSelection = () => {
                setSelectedBooks(new Set());
                setLastClickedBook(null);
                setSelectedDivider(null); // v3.13.0 - Clear divider selection too
            };

            // v3.13.0 - Select divider and all books in its group
            const selectDividerGroup = (columnId, dividerId) => {
                const column = columns.find(col => col.id === columnId);
                if (!column) return;

                // Find divider index
                const dividerIndex = column.books.findIndex(item =>
                    typeof item === 'object' && item.type === 'divider' && item.id === dividerId
                );
                if (dividerIndex === -1) return;

                // Find all books from this divider until next divider (or end of column)
                const booksInGroup = [];
                for (let i = dividerIndex + 1; i < column.books.length; i++) {
                    const item = column.books[i];
                    // Stop at next divider
                    if (typeof item === 'object' && item.type === 'divider') break;
                    // Add book ID to group
                    if (typeof item === 'string') booksInGroup.push(item);
                }

                // Select the books in this group
                setSelectedBooks(new Set(booksInGroup));
                setSelectedDivider({ columnId, dividerId });
                setActiveColumnId(columnId);
            };

            const navigateBook = (direction) => {
                if (!modalBook || !modalColumnId) return;
                
                const column = columns.find(c => c.id === modalColumnId);
                if (!column) return;
                
                const visibleBooks = filteredBooks(column.books);
                const currentIndex = visibleBooks.findIndex(b => b.id === modalBook.id);
                if (currentIndex === -1) return;
                
                let newIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
                
                if (newIndex < 0 || newIndex >= visibleBooks.length) return;
                
                const newBook = visibleBooks[newIndex];
                
                if (newBook) {
                    setModalBook(newBook);
                }
            };

            const getBookPosition = () => {
                if (!modalBook || !modalColumnId) return { current: 0, total: 0 };
                
                const column = columns.find(c => c.id === modalColumnId);
                if (!column) return { current: 0, total: 0 };
                
                const visibleBooks = filteredBooks(column.books);
                const currentIndex = visibleBooks.findIndex(b => b.id === modalBook.id);
                
                if (currentIndex === -1) return { current: 0, total: 0 };
                
                return {
                    current: currentIndex + 1,
                    total: visibleBooks.length,
                    hasPrev: currentIndex > 0,
                    hasNext: currentIndex < visibleBooks.length - 1
                };
            };

            const handleColumnDragStart = (e, columnId) => {
                e.stopPropagation();
                setDragStartPos({ x: e.clientX, y: e.clientY });
                setDragCurrentPos({ x: e.clientX, y: e.clientY });
                setDraggedColumn(columnId);
                setIsDraggingColumn(false);
            };

            const calculateColumnDropPosition = (e) => {
                const columnsContainer = document.querySelector('.columns-container');
                if (!columnsContainer) return null;

                const columnElements = Array.from(columnsContainer.querySelectorAll('[data-column-id]'));
                const mouseX = e.clientX;

                for (let i = 0; i < columnElements.length; i++) {
                    const rect = columnElements[i].getBoundingClientRect();
                    const midpoint = rect.left + rect.width / 2;
                    
                    if (mouseX < midpoint) {
                        return i;
                    }
                }

                return columnElements.length;
            };

            const handleMouseDown = (e, book, columnId) => {
                // Don't start drag if using modifier keys for selection
                if (e.ctrlKey || e.metaKey || e.shiftKey) {
                    return;
                }

                e.preventDefault();

                // If clicking a book that's not in the selection, clear selection first
                if (selectedBooks.size > 0 && !selectedBooks.has(book.id)) {
                    clearSelection();
                }

                setDragStartPos({ x: e.clientX, y: e.clientY });
                setDragCurrentPos({ x: e.clientX, y: e.clientY });
                setDraggedBook(book);
                setDraggedFromColumn(columnId);
                setIsDragging(false);
                setDropTarget(null);
            };

            // v3.11.0 - Handle divider dragging
            const handleDividerMouseDown = (e, divider, columnId) => {
                e.preventDefault();
                e.stopPropagation();

                setDragStartPos({ x: e.clientX, y: e.clientY });
                setDragCurrentPos({ x: e.clientX, y: e.clientY });
                setDraggedBook(divider); // Reuse draggedBook state for dividers
                setDraggedFromColumn(columnId);
                setIsDragging(false);
                setDropTarget(null);
            };

            const calculateDropPosition = (e, columnId) => {
                const column = columns.find(c => c.id === columnId);
                if (!column) return null;

                const columnElement = document.querySelector(`[data-column-id="${columnId}"] .book-grid`);
                if (!columnElement) return null;

                // v3.14.0 - Include both books and dividers as drop targets
                const bookElements = Array.from(columnElement.querySelectorAll('.book-item'));
                const dividerElements = Array.from(columnElement.querySelectorAll('.divider-item'));
                const allElements = [...bookElements, ...dividerElements];

                if (allElements.length === 0) {
                    return { columnId, index: 0 };
                }

                const mouseX = e.clientX;
                const mouseY = e.clientY;
                let closestIndex = 0;
                let closestDistance = Infinity;
                let closestElement = null;

                allElements.forEach((el, idx) => {
                    const rect = el.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;

                    const distance = Math.sqrt(
                        Math.pow(mouseX - centerX, 2) +
                        Math.pow(mouseY - centerY, 2)
                    );

                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestIndex = idx;
                        closestElement = el;
                    }
                });

                const closestRect = closestElement.getBoundingClientRect();
                const closestCenterX = closestRect.left + closestRect.width / 2;
                const closestCenterY = closestRect.top + closestRect.height / 2;

                // v3.14.0 - Check if closest element is a divider or book
                const closestDividerId = closestElement.dataset.dividerId;
                const closestBookId = closestElement.dataset.bookId;

                let actualIndexInColumn;
                if (closestDividerId) {
                    // Divider: find index in column.books array
                    actualIndexInColumn = column.books.findIndex(item =>
                        typeof item === 'object' && item.type === 'divider' && item.id === closestDividerId
                    );
                } else {
                    // Book: find index in column.books array
                    actualIndexInColumn = column.books.indexOf(closestBookId);
                }

                if (actualIndexInColumn === -1) {
                    return { columnId, index: column.books.length };
                }

                // v3.14.0 - For dividers, use top/bottom half instead of quadrant logic
                if (closestDividerId) {
                    const isBelowDivider = mouseY > closestCenterY;
                    const insertIndex = isBelowDivider ? actualIndexInColumn + 1 : actualIndexInColumn;
                    return { columnId, index: insertIndex };
                }

                // For books, use original quadrant logic
                const isRightOfBook = mouseX > closestCenterX;
                const isBelowBook = mouseY > closestCenterY;

                const insertAfter = isRightOfBook || (!isRightOfBook && isBelowBook);
                const insertIndex = insertAfter ? actualIndexInColumn + 1 : actualIndexInColumn;

                return { columnId, index: insertIndex };
            };

            const handleMouseMove = (e) => {
                if (draggedColumn) {
                    setDragCurrentPos({ x: e.clientX, y: e.clientY });

                    const deltaX = e.clientX - dragStartPos.x;
                    const deltaY = e.clientY - dragStartPos.y;
                    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                    if (distance > dragThreshold) {
                        if (!isDraggingColumn) {
                            setIsDraggingColumn(true);
                        }
                        const dropPos = calculateColumnDropPosition(e);
                        setColumnDropTarget(dropPos);
                    }
                    return;
                }

                if (!draggedBook) return;

                setDragCurrentPos({ x: e.clientX, y: e.clientY });

                const deltaX = e.clientX - dragStartPos.x;
                const deltaY = e.clientY - dragStartPos.y;
                const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                if (distance > dragThreshold) {
                    if (!isDragging) {
                        setIsDragging(true);
                    }

                    const target = e.target.closest('[data-column-id]');
                    if (target) {
                        const columnId = target.dataset.columnId;
                        const dropPos = calculateDropPosition(e, columnId);
                        setDropTarget(dropPos);

                        // v3.12.0.c - Auto-scroll when dragging near column edges
                        // Use dragged book position (center of ghost) instead of cursor position
                        // Scroll speed proportional to proximity (closer = faster)
                        const columnElement = target.querySelector('.overflow-y-auto');
                        if (columnElement) {
                            const rect = columnElement.getBoundingClientRect();
                            const edgeThreshold = 100; // pixels from top/bottom to trigger scroll
                            const minScrollSpeed = 2; // pixels per interval at threshold edge
                            const maxScrollSpeed = 20; // pixels per interval at column edge
                            const scrollInterval = 50; // milliseconds

                            // Calculate dragged book's center position (ghost is at dragCurrentPos.y - 75, with height ~150px)
                            const draggedBookCenterY = dragCurrentPos.y;

                            const distanceFromTop = draggedBookCenterY - rect.top;
                            const distanceFromBottom = rect.bottom - draggedBookCenterY;

                            // Clear existing auto-scroll interval
                            if (autoScrollInterval) {
                                clearInterval(autoScrollInterval);
                                setAutoScrollInterval(null);
                            }

                            // Start scrolling up if book center near top edge
                            if (distanceFromTop < edgeThreshold && distanceFromTop > 0) {
                                // Calculate proportional speed: closer to edge = faster
                                // distanceFromTop: 0px (at edge) → 100px (threshold edge)
                                // speed: maxScrollSpeed (at edge) → minScrollSpeed (threshold edge)
                                const proximity = 1 - (distanceFromTop / edgeThreshold); // 1.0 at edge, 0.0 at threshold
                                const scrollSpeed = minScrollSpeed + (proximity * (maxScrollSpeed - minScrollSpeed));

                                const interval = setInterval(() => {
                                    columnElement.scrollTop = Math.max(0, columnElement.scrollTop - scrollSpeed);
                                }, scrollInterval);
                                setAutoScrollInterval(interval);
                            }
                            // Start scrolling down if book center near bottom edge
                            else if (distanceFromBottom < edgeThreshold && distanceFromBottom > 0) {
                                // Calculate proportional speed: closer to edge = faster
                                const proximity = 1 - (distanceFromBottom / edgeThreshold);
                                const scrollSpeed = minScrollSpeed + (proximity * (maxScrollSpeed - minScrollSpeed));

                                const interval = setInterval(() => {
                                    columnElement.scrollTop = Math.min(
                                        columnElement.scrollHeight - columnElement.clientHeight,
                                        columnElement.scrollTop + scrollSpeed
                                    );
                                }, scrollInterval);
                                setAutoScrollInterval(interval);
                            }
                        }
                    } else {
                        setDropTarget(null);
                        // Clear auto-scroll if mouse leaves column
                        if (autoScrollInterval) {
                            clearInterval(autoScrollInterval);
                            setAutoScrollInterval(null);
                        }
                    }
                }
            };

            const handleMouseUp = (e) => {
                // v3.12.0 - Clear auto-scroll interval when drag ends
                if (autoScrollInterval) {
                    clearInterval(autoScrollInterval);
                    setAutoScrollInterval(null);
                }

                if (isDraggingColumn && draggedColumn && columnDropTarget !== null) {
                    const currentIndex = columns.findIndex(c => c.id === draggedColumn);
                    if (currentIndex !== -1 && currentIndex !== columnDropTarget) {
                        const newColumns = [...columns];
                        const [movedColumn] = newColumns.splice(currentIndex, 1);
                        const adjustedIndex = currentIndex < columnDropTarget ? columnDropTarget - 1 : columnDropTarget;
                        newColumns.splice(adjustedIndex, 0, movedColumn);
                        setColumns(newColumns);
                    }

                    setDraggedColumn(null);
                    setIsDraggingColumn(false);
                    setColumnDropTarget(null);
                    return;
                }

                if (!isDragging || !draggedBook || !dropTarget) {
                    setDraggedBook(null);
                    setDraggedFromColumn(null);
                    setIsDragging(false);
                    setDropTarget(null);
                    setDraggedColumn(null);
                    setIsDraggingColumn(false);
                    setColumnDropTarget(null);
                    return;
                }

                const sourceColumn = columns.find(c => c.id === draggedFromColumn);
                const targetColumn = columns.find(c => c.id === dropTarget.columnId);

                if (!sourceColumn || !targetColumn) {
                    console.error('Invalid source or target column');
                    setDraggedBook(null);
                    setDraggedFromColumn(null);
                    setIsDragging(false);
                    setDropTarget(null);
                    clearSelection();
                    return;
                }

                // v3.13.0 - Handle dividers (can move with their book group if selected)
                const isDivider = typeof draggedBook === 'object' && draggedBook.type === 'divider';

                // Determine which items to move
                let itemsToMove;
                if (isDivider) {
                    // v3.13.0 - If divider is selected, move divider + all books in its group
                    if (selectedDivider && selectedDivider.dividerId === draggedBook.id) {
                        // Build array: [divider, ...bookIds]
                        itemsToMove = [draggedBook, ...Array.from(selectedBooks)];
                    } else {
                        // Divider not selected: move alone
                        itemsToMove = [draggedBook];
                    }
                } else {
                    // Regular book: move selection or just this book
                    itemsToMove = (selectedBooks.size > 0 && selectedBooks.has(draggedBook.id)
                        ? Array.from(selectedBooks) // Move all selected books
                        : [draggedBook.id]); // Move just the dragged book
                }

                if (draggedFromColumn === dropTarget.columnId) {
                    // Same column: reorder
                    setColumns(columns.map(col => {
                        if (col.id === draggedFromColumn) {
                            const newBooks = [...col.books];

                            // v3.13.0 - Filter items to move (handle divider objects and book IDs)
                            const itemsToMoveFiltered = itemsToMove.filter(item => {
                                if (typeof item === 'object' && item.type === 'divider') {
                                    // Divider: check if exists in column
                                    return newBooks.some(b => typeof b === 'object' && b.type === 'divider' && b.id === item.id);
                                } else {
                                    // Book ID: check if exists in column
                                    return newBooks.includes(item);
                                }
                            });

                            // Remove all items to move
                            itemsToMoveFiltered.forEach(item => {
                                if (typeof item === 'object' && item.type === 'divider') {
                                    const idx = newBooks.findIndex(b => typeof b === 'object' && b.type === 'divider' && b.id === item.id);
                                    if (idx !== -1) newBooks.splice(idx, 1);
                                } else {
                                    const idx = newBooks.indexOf(item);
                                    if (idx !== -1) newBooks.splice(idx, 1);
                                }
                            });

                            // Calculate adjusted insert index
                            let adjustedIndex = dropTarget.index;
                            itemsToMoveFiltered.forEach(item => {
                                let originalIndex;
                                if (typeof item === 'object' && item.type === 'divider') {
                                    originalIndex = col.books.findIndex(b => typeof b === 'object' && b.type === 'divider' && b.id === item.id);
                                } else {
                                    originalIndex = col.books.indexOf(item);
                                }
                                if (originalIndex !== -1 && originalIndex < dropTarget.index) {
                                    adjustedIndex--;
                                }
                            });

                            // Insert all items at the target position
                            newBooks.splice(adjustedIndex, 0, ...itemsToMoveFiltered);

                            return { ...col, books: newBooks };
                        }
                        return col;
                    }));
                } else {
                    // Cross-column: move items (dividers can only move within same column)
                    if (isDivider) {
                        console.log('Dividers cannot be moved between columns');
                        setDraggedBook(null);
                        setDraggedFromColumn(null);
                        setIsDragging(false);
                        setDropTarget(null);
                        return;
                    }

                    setColumns(columns.map(col => {
                        if (col.id === draggedFromColumn) {
                            // Remove books from source column
                            return { ...col, books: col.books.filter(id => !itemsToMove.includes(id)) };
                        }
                        if (col.id === dropTarget.columnId) {
                            // Add books to target column
                            const newBooks = [...col.books];
                            const insertIndex = Math.min(dropTarget.index, newBooks.length);
                            newBooks.splice(insertIndex, 0, ...itemsToMove);
                            return { ...col, books: newBooks };
                        }
                        return col;
                    }));
                }

                setDraggedBook(null);
                setDraggedFromColumn(null);
                setIsDragging(false);
                setDropTarget(null);
                clearSelection();
            };

            const getAllCollectionNames = () => {
                const collectionNames = new Set();
                books.forEach(book => {
                    if (book.collections && book.collections.length > 0) {
                        book.collections.forEach(c => collectionNames.add(c.name));
                    }
                });
                return Array.from(collectionNames).sort();
            };

            const getAllSeriesNames = () => {
                const seriesNames = new Set();
                books.forEach(book => {
                    if (book.series && book.series.trim() !== '') {
                        seriesNames.add(book.series);
                    }
                });
                return Array.from(seriesNames).sort();
            };

            const filteredBooks = (bookIds) => {
                return bookIds.map(item => {
                    // v3.11.0 - Handle dividers (pass through as-is)
                    if (typeof item === 'object' && item.type === 'divider') {
                        return item;
                    }
                    // Regular book ID - look up book object
                    return books.find(b => b.id === item);
                }).filter(book => {
                    // v3.11.0 - Dividers always pass through filters
                    if (typeof book === 'object' && book.type === 'divider') return true;

                    if (!book) return false;

                    // Text search filter
                    const matchesSearch = !searchTerm ||
                        book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        book.author.toLowerCase().includes(searchTerm.toLowerCase());

                    // Read status filter
                    const matchesReadStatus = !readStatusFilter || book.readStatus === readStatusFilter;

                    // Collection filter
                    let matchesCollection = true;
                    if (collectionFilter) {
                        if (collectionFilter === 'UNCOLLECTED') {
                            matchesCollection = !book.collections || book.collections.length === 0;
                        } else {
                            matchesCollection = book.collections &&
                                book.collections.some(c => c.name === collectionFilter);
                        }
                    }

                    // Rating filter (NEW v3.8.0)
                    const matchesRating = !ratingFilter || (book.rating >= parseFloat(ratingFilter));

                    // Wishlist filter (NEW v3.8.0)
                    const matchesWishlist = !wishlistFilter ||
                        (wishlistFilter === 'wishlist' && book.isWishlist) ||
                        (wishlistFilter === 'owned' && !book.isWishlist);

                    // Series filter (NEW v3.8.0.k)
                    let matchesSeries = true;
                    if (seriesFilter) {
                        if (seriesFilter === 'NOT_IN_SERIES') {
                            matchesSeries = !book.series || book.series.trim() === '';
                        } else {
                            matchesSeries = book.series && book.series === seriesFilter;
                        }
                    }

                    // Date range filter (NEW v3.8.0.k, fixed v3.8.0.l for epoch milliseconds and field name)
                    let matchesDateRange = true;
                    if (dateFrom || dateTo) {
                        if (book.acquired) {
                            // Convert epoch milliseconds to YYYY-MM-DD
                            const bookDate = new Date(parseInt(book.acquired)).toISOString().split('T')[0];
                            const fromDate = dateFrom || '0000-01-01'; // Default to earliest date if From is empty
                            const toDate = dateTo || new Date().toISOString().split('T')[0]; // Default to today if To is empty

                            if (bookDate < fromDate || bookDate > toDate) {
                                matchesDateRange = false;
                            }
                        } else {
                            matchesDateRange = false; // Exclude books without acquisition dates when filter is active
                        }
                    }

                    return matchesSearch && matchesReadStatus && matchesCollection && matchesRating && matchesWishlist && matchesSeries && matchesDateRange;
                });
            };

            // Calculate combined urgency from Library and Collections status
            // Urgency is based ONLY on Load status (what's in the app right now)
            const getUrgencyInfo = () => {
                const libLoad = libraryStatus.loadStatus;
                const colLoad = collectionsStatus.loadStatus;

                // Priority: empty/obsolete > stale > unknown > fresh
                const urgencyOrder = { empty: 4, obsolete: 3, stale: 2, unknown: 1, fresh: 0 };
                const worstStatus = urgencyOrder[libLoad] >= urgencyOrder[colLoad] ? libLoad : colLoad;

                const urgencyMap = {
                    empty: { icon: '🛑', text: 'Must act', color: 'text-red-600', tooltip: 'Please click to see required action(s)' },
                    obsolete: { icon: '🛑', text: 'Obsolete', color: 'text-red-600', tooltip: 'Please click to see required action(s)' },
                    stale: { icon: '⚠️', text: 'Stale', color: 'text-orange-600', tooltip: 'Please click to see suggested action(s)' },
                    unknown: { icon: '❓', text: 'Unknown', color: 'text-gray-500', tooltip: 'Please click to see available info' },
                    fresh: { icon: '✅', text: 'Fresh', color: 'text-green-700', tooltip: 'No actions required' }
                };

                return urgencyMap[worstStatus] || urgencyMap.unknown;
            };

            const renderStatusIndicator = () => {
                const urgency = getUrgencyInfo();
                const isLoading = syncStatus === 'loading';

                if (isLoading) {
                    return (
                        <span className="text-sm text-gray-500">
                            <span className="inline-block animate-spin mr-1">⏳</span>
                            Loading...
                        </span>
                    );
                }

                return (
                    <span
                        className={`text-sm ${urgency.color} status-indicator`}
                        onClick={() => setStatusModalOpen(true)}
                        title={urgency.tooltip}
                    >
                        <span className="mr-1">{urgency.icon}</span>
                        Data Status: {urgency.text}
                    </span>
                );
            };

            return (
                <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 to-indigo-100 text-gray-900" 
                     onMouseMove={handleMouseMove} 
                     onMouseUp={handleMouseUp}>
                    <div className="bg-white border-b border-gray-300 p-4 shadow-sm">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-3">
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900">
                                        <a href="index.html" style={{ color: 'inherit', textDecoration: 'none' }}>
                                            ReaderWrangler
                                        </a>
                                        {books.length > 0 && <span className="text-lg text-gray-500 ml-2">({books.length} books)</span>}
                                    </h1>
                                    <p className="text-sm text-gray-600 mt-1">
                                        {dataSource === 'enriched' ? '✨ With ratings & reviews' :
                                         dataSource === 'csv' ? '📄 Basic CSV data' :
                                         '📂 No library loaded'} • {renderStatusIndicator()}
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-2 items-center">
                                <button onClick={exportBackup} 
                                        className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium"
                                        disabled={books.length === 0}>
                                    💾 Backup
                                </button>
                                <label className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg cursor-pointer text-sm font-medium">
                                    📥 Restore
                                    <input type="file" accept=".json" onChange={importRestore} className="hidden" />
                                </label>
                                <button onClick={clearLibrary}
                                        className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium"
                                        title="Click for details about what will be reset">
                                    🗑️ Reset App
                                </button>
                                <button 
                                    onClick={() => setSettingsOpen(!settingsOpen)}
                                    className="text-gray-600 hover:text-gray-700 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full bg-gray-200 hover:bg-gray-300"
                                    title="Settings">
                                    ⚙️
                                </button>
                                <button 
                                    onClick={() => setHelpOpen(!helpOpen)}
                                    className="text-blue-600 hover:text-blue-700 text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200"
                                    title="Help & Instructions">
                                    ?
                                </button>
                            </div>
                        </div>

                        {/* Filter Panel (NEW v3.8.0, updated v3.8.0.k) */}
                        <div className="flex gap-4 items-center mb-4">
                            <button
                                onClick={() => setFilterPanelOpen(!filterPanelOpen)}
                                className={`px-4 py-2 border rounded-lg flex items-center gap-2 ${
                                    (searchTerm || readStatusFilter || collectionFilter || ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo)
                                    ? `border-blue-500 text-blue-600 font-semibold ${!filterPanelOpen ? 'filter-button-active' : ''}`
                                    : 'border-gray-300 text-gray-700'
                                }`}
                                title="Toggle filter panel">
                                🔍 Filters {(searchTerm || readStatusFilter || collectionFilter || ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo) &&
                                    `(${[searchTerm, readStatusFilter, collectionFilter, ratingFilter, wishlistFilter, seriesFilter, dateFrom, dateTo].filter(Boolean).length})`}
                                {filterPanelOpen ? ' ▼' : ' ▶'}
                            </button>
                            <button onClick={addColumn}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2">
                                ➕ Add Column
                            </button>
                        </div>

                        {/* Collapsible Filter Panel (v3.8.0.k - moved above Active Filters banner) */}
                        {filterPanelOpen && (
                            <div className="bg-white border border-gray-300 rounded-lg p-4 mb-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {/* Search */}
                                    <div className="relative">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">🔍 Search</label>
                                        <span className="absolute left-3 top-9 text-gray-400">🔍</span>
                                        <input type="text"
                                               placeholder="Title or author..."
                                               value={searchTerm}
                                               onChange={(e) => setSearchTerm(e.target.value)}
                                               className="w-full pl-10 pr-10 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" />
                                        {searchTerm && (
                                            <button
                                                onClick={() => setSearchTerm('')}
                                                className="absolute right-3 top-9 text-gray-400 hover:text-gray-600 text-xl"
                                                title="Clear search">
                                                ×
                                            </button>
                                        )}
                                    </div>

                                    {/* Read Status */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">📖 Read Status</label>
                                        <select
                                            value={readStatusFilter}
                                            onChange={(e) => setReadStatusFilter(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                                            <option value="">All Status</option>
                                            <option value="READ">✓ Read</option>
                                            <option value="UNREAD">○ Unread</option>
                                            <option value="UNKNOWN">? Unknown</option>
                                        </select>
                                    </div>

                                    {/* Collection */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">🗂️ Collection</label>
                                        <select
                                            value={collectionFilter}
                                            onChange={(e) => setCollectionFilter(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                                            <option value="">All Collections</option>
                                            <option value="UNCOLLECTED">📚 Uncollected</option>
                                            {getAllCollectionNames().map(name => (
                                                <option key={name} value={name}>{name}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {/* Rating */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">⭐ Rating</label>
                                        <select
                                            value={ratingFilter}
                                            onChange={(e) => setRatingFilter(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                                            <option value="">All Ratings</option>
                                            <option value="5">5★</option>
                                            <option value="4">4+★</option>
                                            <option value="3">3+★</option>
                                            <option value="2">2+★</option>
                                            <option value="1">1+★</option>
                                        </select>
                                    </div>

                                    {/* Wishlist */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">❤️ Wishlist</label>
                                        <select
                                            value={wishlistFilter}
                                            onChange={(e) => setWishlistFilter(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                                            <option value="">All Books</option>
                                            <option value="owned">Owned Books Only</option>
                                            <option value="wishlist">Wishlist Books Only</option>
                                        </select>
                                    </div>

                                    {/* Series (NEW v3.8.0.k) */}
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">📚 Series</label>
                                        <select
                                            value={seriesFilter}
                                            onChange={(e) => setSeriesFilter(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                                            <option value="">All Series</option>
                                            <option value="NOT_IN_SERIES">📖 Not in Series</option>
                                            {getAllSeriesNames().map(name => (
                                                <option key={name} value={name}>{name}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {/* Acquisition Date Range (NEW v3.8.0.k) - Full width row */}
                                <div className="mt-4 flex items-end gap-4">
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">📅 Acquisition Date - From</label>
                                        <input
                                            type="date"
                                            value={dateFrom}
                                            onChange={(e) => setDateFrom(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">📅 Acquisition Date - To</label>
                                        <input
                                            type="date"
                                            value={dateTo}
                                            onChange={(e) => setDateTo(e.target.value)}
                                            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                        />
                                    </div>
                                    {(dateFrom || dateTo) && (
                                        <button
                                            onClick={() => {
                                                setDateFrom('');
                                                setDateTo('');
                                            }}
                                            className="px-3 py-2 text-blue-600 hover:text-blue-800 font-semibold text-sm whitespace-nowrap"
                                            title="Clear date range">
                                            📅 Clear
                                        </button>
                                    )}
                                </div>

                                {/* Result Counter */}
                                <div className="mt-4 flex justify-between items-center text-sm text-gray-600">
                                    <span>
                                        Showing: {columns.reduce((sum, col) => sum + filteredBooks(col.books).length, 0)} of {books.length} books
                                    </span>
                                    <button
                                        onClick={() => {
                                            setSearchTerm('');
                                            setReadStatusFilter('');
                                            setCollectionFilter('');
                                            setRatingFilter('');
                                            setWishlistFilter('');
                                            setSeriesFilter('');
                                            setDateFrom('');
                                            setDateTo('');
                                        }}
                                        className="text-blue-600 hover:text-blue-800 font-semibold">
                                        Clear All Filters
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Active Filters Banner (v3.8.0.k - moved below Filter Panel) */}
                        {(searchTerm || readStatusFilter || collectionFilter || ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo) && (
                            <div className="bg-blue-100 border border-blue-300 rounded-lg px-4 py-2 mb-4 flex items-center justify-between">
                                <div className="flex items-center gap-2 flex-wrap text-sm">
                                    <span className="font-semibold">🔍 Active:</span>
                                    {searchTerm && <span>Search: "{searchTerm}"</span>}
                                    {searchTerm && (readStatusFilter || collectionFilter || ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo) && <span>|</span>}
                                    {readStatusFilter && <span>Read: {readStatusFilter}</span>}
                                    {readStatusFilter && (collectionFilter || ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo) && <span>|</span>}
                                    {collectionFilter && <span>Collection: {collectionFilter === 'UNCOLLECTED' ? 'Uncollected' : collectionFilter}</span>}
                                    {collectionFilter && (ratingFilter || wishlistFilter || seriesFilter || dateFrom || dateTo) && <span>|</span>}
                                    {ratingFilter && <span>Rating: {ratingFilter}+★</span>}
                                    {ratingFilter && (wishlistFilter || seriesFilter || dateFrom || dateTo) && <span>|</span>}
                                    {wishlistFilter && <span>Wishlist: {wishlistFilter === 'owned' ? 'Owned Only' : 'Wishlist Only'}</span>}
                                    {wishlistFilter && (seriesFilter || dateFrom || dateTo) && <span>|</span>}
                                    {seriesFilter && <span>Series: {seriesFilter === 'NOT_IN_SERIES' ? 'Not in Series' : seriesFilter}</span>}
                                    {seriesFilter && (dateFrom || dateTo) && <span>|</span>}
                                    {(dateFrom || dateTo) && <span>Date: {dateFrom || '...'} to {dateTo || '...'}</span>}
                                </div>
                                <button
                                    onClick={() => {
                                        setSearchTerm('');
                                        setReadStatusFilter('');
                                        setCollectionFilter('');
                                        setRatingFilter('');
                                        setWishlistFilter('');
                                        setSeriesFilter('');
                                        setDateFrom('');
                                        setDateTo('');
                                    }}
                                    className="text-blue-600 hover:text-blue-800 font-semibold text-sm whitespace-nowrap">
                                    Clear All ×
                                </button>
                            </div>
                        )}
                    </div>

                    {statusModalOpen && (() => {
                        // ARCHITECTURE: Status Icons pattern - See docs/design/ARCHITECTURE.md (Status Icons section)
                        const urgency = getUrgencyInfo();
                        const statusIcon = (status) => {
                            const icons = { fresh: '✅', stale: '⚠️', obsolete: '🛑', empty: '🗄️', unknown: '❓' };
                            return icons[status] || '❓';
                        };
                        const statusLabel = (status, date) => {
                            if (status === 'empty') return 'Missing';
                            if (status === 'unknown') return 'Unknown';
                            const label = status.charAt(0).toUpperCase() + status.slice(1);
                            if (date) {
                                const d = new Date(date);
                                const days = Math.floor((Date.now() - d.getTime()) / (1000 * 60 * 60 * 24));
                                if (days < 1) return `${label} (today)`;
                                if (days === 1) return `${label} (1d ago)`;
                                return `${label} (${days}d ago)`;
                            }
                            return label;
                        };
                        const needsLibraryAction = ['empty', 'stale', 'obsolete', 'unknown'].includes(libraryStatus.loadStatus);
                        const needsCollectionsAction = ['empty', 'stale', 'obsolete'].includes(collectionsStatus.loadStatus);

                        return (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setStatusModalOpen(false)}>
                            <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
                                {/* Header with darker background */}
                                <div className="flex justify-between items-start p-4 bg-gray-200 rounded-t-lg border-b border-gray-300">
                                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                        <span>{urgency.icon}</span>
                                        {urgency.text === 'Fresh' ? 'All Good!' :
                                         urgency.text === 'Must act' ? 'Action Required' :
                                         urgency.text === 'Stale' ? 'Update Recommended' :
                                         urgency.text === 'Obsolete' ? 'Action Required' : 'Status Info'}
                                    </h2>
                                    <button onClick={() => setStatusModalOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl leading-none">×</button>
                                </div>

                                {/* Main content area */}
                                <div className="p-6">
                                {/* Contextual guidance based on state - ACTION FIRST */}
                                {/* State 2: Fresh Both (v3.9.0.o) */}
                                {libraryStatus.loadStatus === 'fresh' && collectionsStatus.loadStatus === 'fresh' && (
                                    <div className="space-y-3">
                                        {/* Status lines with inline Reload buttons */}
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📚 <strong>Library:</strong> Loaded {statusLabel(libraryStatus.loadStatus, libraryStatus.loadDate)} ✅
                                                </p>
                                                <button
                                                    onClick={syncNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs whitespace-nowrap">
                                                    Reload Anyway
                                                </button>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📁 <strong>Collections:</strong> Loaded {statusLabel(collectionsStatus.loadStatus, collectionsStatus.loadDate)} ✅
                                                </p>
                                                <button
                                                    onClick={loadCollectionsNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs whitespace-nowrap">
                                                    Reload Anyway
                                                </button>
                                            </div>
                                        </div>

                                        {/* Two-column instructions for dual destinations */}
                                        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                            <p className="mb-2"><strong>If you've made Amazon purchases or collection changes since loading:</strong></p>
                                            <div className="grid grid-cols-2 gap-4 text-xs">
                                                <div>
                                                    <p className="font-semibold mb-1">📚 Library</p>
                                                    <ol className="list-decimal ml-4 space-y-1">
                                                        <li>Go to <a href="https://www.amazon.com/yourbooks" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Library</a></li>
                                                        <li>Click bookmarklet</li>
                                                        <li>Choose "Fetch Library"</li>
                                                        <li>Return & click Reload button above</li>
                                                    </ol>
                                                </div>
                                                <div>
                                                    <p className="font-semibold mb-1">📁 Collections</p>
                                                    <ol className="list-decimal ml-4 space-y-1">
                                                        <li>Go to <a href="https://www.amazon.com/hz/mycd/myx" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Collections</a></li>
                                                        <li>Click bookmarklet</li>
                                                        <li>Choose "Fetch Collections"</li>
                                                        <li>Return & click Reload button above</li>
                                                    </ol>
                                                </div>
                                            </div>
                                            <p className="mt-2 text-center">Otherwise, continue organizing!</p>
                                        </div>
                                    </div>
                                )}

                                {libraryStatus.loadStatus === 'empty' && collectionsStatus.loadStatus === 'empty' && (
                                    <div className="space-y-3">
                                        {/* Status lines with inline Load buttons (v3.9.0.o - right-aligned UX pattern) */}
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📚 <strong>Library:</strong> Not loaded 🛑
                                                </p>
                                                <button
                                                    onClick={syncNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs">
                                                    Load Library
                                                </button>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📁 <strong>Collections:</strong> Not loaded 🛑
                                                </p>
                                                <button
                                                    onClick={loadCollectionsNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs">
                                                    Load Collections
                                                </button>
                                            </div>
                                        </div>

                                        {/* Help text for users with files */}
                                        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                            <p className="text-center">Load your library to get started!</p>
                                        </div>

                                        {/* Fetch instructions for users without files */}
                                        <div className="border border-blue-200 rounded overflow-hidden text-sm text-gray-700">
                                            <div className="bg-blue-100 px-3 py-2 border-b border-blue-200">
                                                <p className="font-medium">Don't have files yet? Fetch them from Amazon:</p>
                                            </div>
                                            <div className="bg-blue-50 p-3">
                                                <div className="grid grid-cols-2 gap-4">
                                                    {/* Library fetch instructions */}
                                                    <div>
                                                        <p className="font-medium mb-2">📚 Library</p>
                                                        <ol className="list-decimal ml-4 space-y-1 text-xs">
                                                            <li>Go to <a href="https://www.amazon.com/yourbooks" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Library</a></li>
                                                            <li>Click bookmarklet</li>
                                                            <li>Choose "Fetch Library"</li>
                                                            <li>Return & click Load button above</li>
                                                        </ol>
                                                    </div>
                                                    {/* Collections fetch instructions */}
                                                    <div>
                                                        <p className="font-medium mb-2">📁 Collections</p>
                                                        <ol className="list-decimal ml-4 space-y-1 text-xs">
                                                            <li>Go to <a href="https://www.amazon.com/hz/mycd/myx" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Collections</a></li>
                                                            <li>Click bookmarklet</li>
                                                            <li>Choose "Fetch Collections"</li>
                                                            <li>Return & click Load button above</li>
                                                        </ol>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {(libraryStatus.loadStatus === 'stale' || libraryStatus.loadStatus === 'obsolete') && (
                                    <div className="space-y-3">
                                        <p className="text-sm text-gray-700">
                                            {libraryStatus.loadStatus === 'stale' ?
                                                <>⚠️ <strong>Library data loaded {statusLabel(libraryStatus.loadStatus, libraryStatus.loadDate)}</strong></> :
                                                <>🛑 <strong>Library data loaded {statusLabel(libraryStatus.loadStatus, libraryStatus.loadDate)}</strong></>
                                            }
                                        </p>
                                        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                            <p><strong>If you've made Amazon purchases/changes, re-fetch and reload:</strong></p>
                                            <ol className="list-decimal ml-4 mt-2 space-y-1 text-xs">
                                                <li>Go to <a href="https://www.amazon.com/yourbooks" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Library</a></li>
                                                <li>Click the ReaderWrangler bookmarklet → "Fetch Library"</li>
                                                <li>Return here and click "Reload Library" below</li>
                                            </ol>
                                        </div>
                                        <button
                                            onClick={syncNow}
                                            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                                            Reload Library
                                        </button>
                                    </div>
                                )}

                                {libraryStatus.loadStatus === 'unknown' && libraryStatus.loadStatus !== 'empty' && (
                                    <div className="space-y-3">
                                        <p className="text-sm text-gray-700">
                                            ❓ <strong>Status unknown</strong>
                                        </p>
                                        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-gray-700">
                                            <p>Your library file doesn't have date tracking metadata.</p>
                                            <p className="mt-1">Re-fetch to enable full status tracking.</p>
                                        </div>
                                        <button
                                            onClick={syncNow}
                                            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                                            Load Library
                                        </button>
                                    </div>
                                )}

                                {/* State 3: Library Fresh, Collections needs action (v3.9.0.o) */}
                                {libraryStatus.loadStatus === 'fresh' && collectionsStatus.loadStatus !== 'fresh' && (
                                    <div className="space-y-3">
                                        {/* Status lines with inline buttons */}
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📚 <strong>Library:</strong> Loaded {statusLabel(libraryStatus.loadStatus, libraryStatus.loadDate)} ✅
                                                </p>
                                                <button
                                                    onClick={syncNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs whitespace-nowrap">
                                                    Reload Anyway
                                                </button>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📁 <strong>Collections:</strong> {collectionsStatus.loadStatus === 'empty' || collectionsStatus.loadStatus === 'unknown' ?
                                                        <>Not loaded 🛑</> :
                                                        <>Loaded {statusLabel(collectionsStatus.loadStatus, collectionsStatus.loadDate)} {statusIcon(collectionsStatus.loadStatus)}</>
                                                    }
                                                </p>
                                                <button
                                                    onClick={loadCollectionsNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs">
                                                    Load Collections
                                                </button>
                                            </div>
                                        </div>

                                        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                            <p>Your library is up to date! Collections are optional for organizing books by Amazon's categories.</p>
                                        </div>

                                        {/* Single-column fetch instructions (~60% width, centered) */}
                                        <div className="flex justify-center">
                                            <div className="w-3/5 border border-blue-200 rounded overflow-hidden text-sm text-gray-700">
                                                <div className="bg-blue-100 px-3 py-2 border-b border-blue-200">
                                                    <p className="font-medium">Don't have your Collections file yet? Fetch it from Amazon:</p>
                                                </div>
                                                <div className="bg-blue-50 p-3">
                                                    <p className="font-medium mb-2">📁 Collections</p>
                                                    <ol className="list-decimal ml-4 space-y-1 text-xs">
                                                        <li>Go to <a href="https://www.amazon.com/hz/mycd/myx" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Collections</a></li>
                                                        <li>Click bookmarklet</li>
                                                        <li>Choose "Fetch Collections"</li>
                                                        <li>Return & click Load button above</li>
                                                    </ol>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* State 4: Collections Fresh, Library needs action - symmetric to State 3 (v3.9.0.o) */}
                                {collectionsStatus.loadStatus === 'fresh' && libraryStatus.loadStatus !== 'fresh' && (
                                    <div className="space-y-3">
                                        {/* Status lines with inline buttons */}
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📚 <strong>Library:</strong> {libraryStatus.loadStatus === 'empty' || libraryStatus.loadStatus === 'unknown' ?
                                                        <>Not loaded 🛑</> :
                                                        <>Loaded {statusLabel(libraryStatus.loadStatus, libraryStatus.loadDate)} {statusIcon(libraryStatus.loadStatus)}</>
                                                    }
                                                </p>
                                                <button
                                                    onClick={syncNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs">
                                                    Load Library
                                                </button>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <p className="text-sm text-gray-700">
                                                    📁 <strong>Collections:</strong> Loaded {statusLabel(collectionsStatus.loadStatus, collectionsStatus.loadDate)} ✅
                                                </p>
                                                <button
                                                    onClick={loadCollectionsNow}
                                                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs whitespace-nowrap">
                                                    Reload Anyway
                                                </button>
                                            </div>
                                        </div>

                                        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                            <p>Load your library to see your books!</p>
                                        </div>

                                        {/* Single-column fetch instructions (~60% width, centered) */}
                                        <div className="flex justify-center">
                                            <div className="w-3/5 border border-blue-200 rounded overflow-hidden text-sm text-gray-700">
                                                <div className="bg-blue-100 px-3 py-2 border-b border-blue-200">
                                                    <p className="font-medium">Don't have your Library file yet? Fetch it from Amazon:</p>
                                                </div>
                                                <div className="bg-blue-50 p-3">
                                                    <p className="font-medium mb-2">📚 Library</p>
                                                    <ol className="list-decimal ml-4 space-y-1 text-xs">
                                                        <li>Go to <a href="https://www.amazon.com/yourbooks" target="_blank" rel="noopener" className="text-blue-600 underline">Amazon Library</a></li>
                                                        <li>Click bookmarklet</li>
                                                        <li>Choose "Fetch Library"</li>
                                                        <li>Return & click Load button above</li>
                                                    </ol>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                                </div>
                            </div>
                        </div>
                        );
                    })()}

                    {resetConfirmOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setResetConfirmOpen(false)}>
                            <div className="bg-white rounded-lg shadow-2xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
                                <div className="flex justify-between items-start p-4 bg-gray-200 rounded-t-lg border-b border-gray-300">
                                    <h2 className="text-xl font-bold text-gray-900">Reset App Confirmation</h2>
                                    <button onClick={() => setResetConfirmOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl font-bold">×</button>
                                </div>
                                <div className="p-6 space-y-4">
                                    <p className="text-gray-800 font-semibold">This will completely reset the app to its initial unused state.</p>
                                    <div className="text-gray-700">
                                        <p className="font-semibold mb-2">This will:</p>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li>Unload library and collections</li>
                                            <li>Remove all columns and organization</li>
                                            <li>Reset all filters</li>
                                        </ul>
                                    </div>
                                    <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                        <p className="mb-2">Your library/collections files on disk will NOT be deleted. You can reload them anytime.</p>
                                    </div>
                                    <div className="bg-yellow-50 border border-yellow-300 rounded p-3 text-sm">
                                        <p className="font-semibold text-gray-800">💡 Tip: Use the Backup button first to save your organization before resetting.</p>
                                    </div>
                                    <div className="flex gap-3 justify-end pt-2">
                                        <button
                                            onClick={() => setResetConfirmOpen(false)}
                                            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg font-medium">
                                            Cancel
                                        </button>
                                        <button
                                            onClick={confirmReset}
                                            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium">
                                            Reset App
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {insertDividerOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setInsertDividerOpen(null)}>
                            <div className="bg-white rounded-lg shadow-2xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
                                <div className="flex justify-between items-start p-4 bg-gray-200 rounded-t-lg border-b border-gray-300">
                                    <h2 className="text-xl font-bold text-gray-900">Insert Divider</h2>
                                    <button onClick={() => setInsertDividerOpen(null)} className="text-gray-500 hover:text-gray-700 text-2xl font-bold">×</button>
                                </div>
                                <div className="p-6 space-y-4">
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-2">Divider Label</label>
                                        <input
                                            type="text"
                                            value={newDividerLabel}
                                            onChange={(e) => setNewDividerLabel(e.target.value)}
                                            onKeyPress={(e) => { if (e.key === 'Enter') insertDivider(insertDividerOpen); }}
                                            placeholder="e.g., Jerry Mitchell, Read Books, 5 Stars"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            autoFocus
                                        />
                                    </div>
                                    <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-gray-700">
                                        <p>The divider will appear at the bottom of the column. You can drag it to any position.</p>
                                    </div>
                                    <div className="flex gap-3 justify-end pt-2">
                                        <button
                                            onClick={() => setInsertDividerOpen(null)}
                                            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg font-medium">
                                            Cancel
                                        </button>
                                        <button
                                            onClick={() => insertDivider(insertDividerOpen)}
                                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                                            disabled={!newDividerLabel.trim()}>
                                            Insert
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {settingsOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setSettingsOpen(false)}>
                            <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
                                <div className="flex justify-between items-start mb-4">
                                    <h2 className="text-xl font-bold text-gray-900">Settings</h2>
                                    <button onClick={() => setSettingsOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
                                </div>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                                            Cache Expiration for Ratings/Reviews (days)
                                        </label>
                                        <p className="text-xs text-gray-600 mb-2">
                                            Descriptions are cached forever. Ratings and reviews expire after this many days to stay fresh.
                                        </p>
                                        <input 
                                            type="number"
                                            min="1"
                                            max="365"
                                            value={settings.cacheExpirationDays}
                                            onChange={(e) => setSettings({...settings, cacheExpirationDays: parseInt(e.target.value) || 30})}
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                        <p className="text-xs text-gray-500 mt-1">
                                            Current: {settings.cacheExpirationDays} days
                                        </p>
                                    </div>
                                </div>
                                <div className="flex gap-2 justify-end mt-6">
                                    <button 
                                        onClick={() => setSettingsOpen(false)}
                                        className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg">
                                        Cancel
                                    </button>
                                    <button 
                                        onClick={() => saveSettings(settings)}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                                        Save
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {helpOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setHelpOpen(false)}>
                            <div className="bg-white rounded-lg shadow-2xl p-6 max-w-2xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                                <div className="flex justify-between items-start mb-4">
                                    <h2 className="text-xl font-bold text-gray-900">How to Use</h2>
                                    <button onClick={() => setHelpOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
                                </div>
                                <div className="space-y-4 text-sm text-gray-700">
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">📚 Getting Your Books</h3>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li><strong>Install Bookmarklet:</strong> Visit the installer page (see README) and drag the bookmarklet to your toolbar</li>
                                            <li><strong>Run Fetcher:</strong> Go to your online library page and click the bookmarklet</li>
                                            <li><strong>Auto-saves:</strong> Fetcher creates library JSON in your Downloads</li>
                                            <li><strong>First Load:</strong> Click status indicator to load library</li>
                                            <li><strong>Updates:</strong> Run fetcher again, then sync when you see Stale indicator</li>
                                        </ul>
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">Status Indicator</h3>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li><strong>Fresh:</strong> Your library is up to date</li>
                                            <li><strong>Stale:</strong> New books available - click to load updated library</li>
                                            <li><strong>Click here to load library:</strong> Click to load your first library</li>
                                        </ul>
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">📚 Organizing Books</h3>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li><strong>View Details:</strong> Click a book cover to see full details</li>
                                            <li><strong>Move/Reorder:</strong> Drag a book to move it to another column or reorder within same column</li>
                                            <li><strong>Navigate:</strong> Use ← → arrows in book details to browse prev/next books</li>
                                            <li><strong>Collect Series:</strong> Click "📚 Collect Series Books" in book details</li>
                                        </ul>
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">📋 Managing Columns</h3>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li><strong>Create:</strong> Type name in field and click ➕ (or press Enter)</li>
                                            <li><strong>Rename:</strong> Double-click any column name to edit</li>
                                            <li><strong>Reorder:</strong> Drag any column header left/right</li>
                                            <li><strong>Sort:</strong> Click ⬆ button to sort books</li>
                                            <li><strong>Delete:</strong> Click ⌫ and choose where to move the books</li>
                                        </ul>
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 mb-1">💾 Data Management</h3>
                                        <ul className="list-disc list-inside space-y-1 ml-2">
                                            <li><strong>Auto-saves:</strong> Everything persists automatically in your browser</li>
                                            <li><strong>Backup:</strong> Download complete backup for safekeeping</li>
                                            <li><strong>Restore:</strong> Restore from a backup file</li>
                                            <li><strong>Reset App:</strong> Complete app reset to initial state (files on disk not affected)</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {deleteDialogOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                            <div className="bg-white rounded-lg shadow-2xl p-6 max-w-md" onClick={(e) => e.stopPropagation()}>
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Delete Column</h2>
                                <p className="text-sm text-gray-700 mb-4">
                                    Where should the {columns.find(c => c.id === deleteDialogOpen)?.books.length || 0} books from 
                                    "<strong>{columns.find(c => c.id === deleteDialogOpen)?.name}</strong>" be moved?
                                </p>
                                <select 
                                    value={deleteDestination}
                                    onChange={(e) => setDeleteDestination(e.target.value)}
                                    className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    {columns.filter(c => c.id !== deleteDialogOpen).map(col => (
                                        <option key={col.id} value={col.id}>{col.name}</option>
                                    ))}
                                </select>
                                <div className="flex gap-2 justify-end">
                                    <button 
                                        onClick={() => { setDeleteDialogOpen(null); setDeleteDestination(''); }}
                                        className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg">
                                        Cancel
                                    </button>
                                    <button 
                                        onClick={confirmDeleteColumn}
                                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg">
                                        Delete Column
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {collectSeriesOpen && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]" onClick={() => setCollectSeriesOpen(false)}>
                            <div className="bg-white rounded-lg shadow-2xl p-6 max-w-2xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                                <h2 className="text-xl font-bold text-gray-900 mb-4">Collect Series Books</h2>
                                
                                {modalBook && (
                                    <p className="text-sm text-gray-700 mb-4">
                                        Collecting books from: <strong style={{ color: '#621e31' }}>{modalBook.series}</strong>
                                    </p>
                                )}
                                
                                {seriesBooks.current.length > 0 && (
                                    <div className="mb-4">
                                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                                            Found in this column ({seriesBooks.current.length}):
                                        </h3>
                                        <ul className="space-y-1 ml-4">
                                            {seriesBooks.current.map(book => (
                                                <li key={book.id} className="text-sm text-gray-700">
                                                    • {book.seriesPosition ? `Book ${book.seriesPosition}: ` : ''}{book.title}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                
                                {seriesBooks.other.length > 0 && (
                                    <div className="mb-6">
                                        <h3 className="text-sm font-semibold text-gray-900 mb-2">
                                            Found in other columns ({seriesBooks.other.length}):
                                        </h3>
                                        <ul className="space-y-1 ml-4">
                                            {seriesBooks.other.map(book => (
                                                <li key={book.id} className="text-sm text-gray-700">
                                                    • {book.seriesPosition ? `Book ${book.seriesPosition}: ` : ''}{book.title} 
                                                    <span className="text-gray-500 ml-2">({book.columnName})</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                
                                {seriesBooks.current.length === 0 && seriesBooks.other.length === 0 && (
                                    <p className="text-sm text-gray-600 mb-6 italic">
                                        No other books from this series found in your library.
                                    </p>
                                )}
                                
                                <div className="flex gap-2 justify-end">
                                    <button 
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setCollectSeriesOpen(false);
                                        }}
                                        className="px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-lg">
                                        Cancel
                                    </button>
                                    {seriesBooks.current.length > 0 && (
                                        <button 
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                collectSeriesBooks(false);
                                            }}
                                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
                                            This Column Only
                                        </button>
                                    )}
                                    {seriesBooks.other.length > 0 && (
                                        <button 
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                collectSeriesBooks(true);
                                            }}
                                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg">
                                            All Columns
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {modalBook && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={closeBookModal}>
                            <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                                <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <button 
                                            onClick={() => navigateBook('prev')}
                                            disabled={!getBookPosition().hasPrev}
                                            className="p-2 hover:bg-gray-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                                            title="Previous book">
                                            ← 
                                        </button>
                                        <span className="text-sm text-gray-600">
                                            Book {getBookPosition().current} of {getBookPosition().total}
                                        </span>
                                        <button 
                                            onClick={() => navigateBook('next')}
                                            disabled={!getBookPosition().hasNext}
                                            className="p-2 hover:bg-gray-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                                            title="Next book">
                                            →
                                        </button>
                                    </div>
                                    <button onClick={closeBookModal} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
                                </div>
                                
                                <div className="p-6">
                                    <div className="flex gap-6 mb-6">
                                        {blankImageBooks.has(modalBook.id) ? (
                                            <div className="w-48 h-72 rounded shadow-lg overflow-hidden flex flex-col flex-shrink-0" 
                                                 style={{ backgroundColor: '#d4c5a9' }}>
                                                <div className="flex-1 flex items-center justify-center px-4">
                                                    <div className="text-center">
                                                        <div className="text-sm font-serif font-bold text-gray-800 leading-tight mb-3">
                                                            {modalBook.title}
                                                        </div>
                                                        <div className="text-xs text-gray-600 mt-3">KINDLE EDITION</div>
                                                    </div>
                                                </div>
                                            </div>
                                        ) : (
                                            <img src={modalBook.coverUrl} 
                                                 alt={modalBook.title}
                                                 className="w-48 h-72 object-cover rounded shadow-lg flex-shrink-0"
                                                 onError={(e) => e.target.src = 'https://via.placeholder.com/192x288/4f46e5/fff?text=No+Cover'} />
                                        )}
                                        <div className="flex-1">
                                            <h2 className="text-3xl font-bold text-gray-900 mb-3">{modalBook.title}</h2>
                                            <p className="text-xl text-gray-700 mb-4">by {modalBook.author}</p>
                                            
                                            {modalBook.rating > 0 && (
                                                <div className="flex items-center gap-3 mb-4">
                                                    {renderStars(modalBook.rating)}
                                                    <span className="text-xl font-bold text-gray-700">{modalBook.rating.toFixed(1)}</span>
                                                    {modalBook.ratingCount && (
                                                        <span className="text-sm text-gray-500">({modalBook.ratingCount} ratings)</span>
                                                    )}
                                                </div>
                                            )}
                                            
                                            {modalBook.series && (
                                                <div className="mb-3">
                                                    <p className="text-lg mb-2" style={{ color: '#621e31' }}>
                                                        {(modalBook.seriesPosition && modalBook.seriesTotal)
                                                            ? `Book ${modalBook.seriesPosition} of ${modalBook.seriesTotal}: ${modalBook.series}`
                                                            : modalBook.seriesPosition 
                                                                ? `Book ${modalBook.seriesPosition}: ${modalBook.series}`
                                                                : modalBook.series
                                                        }
                                                    </p>
                                                    <button
                                                        onClick={openCollectSeriesDialog}
                                                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium flex items-center gap-2">
                                                        📚 Collect Series Books
                                                    </button>
                                                </div>
                                            )}
                                            
                                            <div className="space-y-2 text-sm">
                                                {modalBook.binding && (
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-gray-700">Format:</span>
                                                        <span className="text-gray-600">{modalBook.binding}</span>
                                                    </div>
                                                )}
                                                {modalBook.acquired && (
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-gray-700">Acquired:</span>
                                                        <span className="text-gray-600">{formatAcquisitionDate(modalBook.acquired)}</span>
                                                    </div>
                                                )}
                                                {modalBook.asin && (
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-gray-700">ASIN:</span>
                                                        <span className="text-gray-600 font-mono text-xs">{modalBook.asin}</span>
                                                    </div>
                                                )}
                                                {/* Collections metadata (NEW v3.8.0.k) */}
                                                {modalBook.collections && modalBook.collections.length > 0 ? (
                                                    <div className="flex items-start gap-2">
                                                        <span className="font-semibold text-gray-700">Collections:</span>
                                                        <span className="text-gray-600 flex-1">
                                                            {modalBook.collections.map(c => c.name).join(', ')}
                                                        </span>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-gray-700">Collections:</span>
                                                        <span className="text-gray-400 italic">No collections</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {!modalBook.description && (
                                        <div className="mb-6 pb-6 border-b border-gray-200">
                                            <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
                                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                                <p className="text-sm text-gray-700">
                                                    ⚠️ <strong>Description not available</strong>
                                                </p>
                                                <p className="text-xs text-gray-600 mt-2">
                                                    This book may not have a description in Amazon's database, or the description wasn't captured during the library fetch.
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                    
                                    {modalBook.description && (
                                        <div className="mb-6 pb-6 border-b border-gray-200">
                                            <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
                                            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                                {modalBook.description}
                                            </p>
                                        </div>
                                    )}
                                    
                                    {modalBook.topReviews && modalBook.topReviews.length > 0 && (
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-3">Top Reviews</h3>
                                            <div className="space-y-4">
                                                {modalBook.topReviews.slice(0, showAllReviews ? modalBook.topReviews.length : 3).map((review, idx) => {
                                                    const stars = review.stars || 0;
                                                    const title = review.title || '';
                                                    const text = review.text || review.contentAbstract?.textAbstract || '';
                                                    const reviewer = review.reviewer || review.contributor?.publicProfile?.publicProfile?.publicName?.displayString || '';
                                                    
                                                    return (
                                                        <div key={idx} className="bg-gray-50 rounded-lg p-4">
                                                            <div className="flex items-center gap-3 mb-2">
                                                                <span className="text-yellow-500 text-lg">{'★'.repeat(stars)}</span>
                                                                {title && (
                                                                    <span className="font-semibold text-gray-900">{title}</span>
                                                                )}
                                                            </div>
                                                            {reviewer && (
                                                                <p className="text-sm text-gray-600 mb-2">
                                                                    by {reviewer}
                                                                </p>
                                                            )}
                                                            {text && (
                                                                <p className="text-sm text-gray-700 leading-relaxed">
                                                                    {text}
                                                                </p>
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                            {!showAllReviews && modalBook.topReviews.length > 3 && (
                                                <button 
                                                    onClick={() => setShowAllReviews(true)}
                                                    className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
                                                    Show More Reviews ({modalBook.topReviews.length - 3} more)
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="flex-1 overflow-x-auto overflow-y-hidden" onClick={(e) => {
                        // Clear selection if clicking on empty space (not on books or columns)
                        if (e.target === e.currentTarget || e.target.classList.contains('columns-container')) {
                            clearSelection();
                        }
                    }}>
                        <div className="flex h-full p-4 gap-4 columns-container" style={{ minWidth: 'fit-content' }} onClick={(e) => {
                            // Clear selection if clicking between columns
                            if (e.target === e.currentTarget) {
                                clearSelection();
                            }
                        }}>
                            {columns.map((column, colIndex) => (
                                <div key={column.id}
                                     data-column-id={column.id}
                                     onClick={() => setActiveColumnId(column.id)}
                                     className={`flex-shrink-0 w-96 bg-white rounded-lg flex flex-col relative ${isDragging && dropTarget?.columnId === column.id ? 'drop-target' : ''} ${draggedColumn === column.id && isDraggingColumn ? 'column-dragging' : ''}`}
                                     style={activeColumnId === column.id ? {
                                         boxShadow: 'inset 0 2px 4px rgba(64, 64, 64, 0.4), inset 0 -2px 4px rgba(64, 64, 64, 0.4), inset 2px 0 4px rgba(64, 64, 64, 0.4), inset -2px 0 4px rgba(64, 64, 64, 0.4), 0 1px 3px rgba(0, 0, 0, 0.12)',
                                         border: '2px solid rgb(96, 96, 96)'
                                     } : { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)' }}>
                                    {isDraggingColumn && columnDropTarget === colIndex && draggedColumn !== column.id && (
                                        <div className="column-drop-indicator" style={{ left: '-8px' }} />
                                    )}
                                    <div className="p-4 border-b border-gray-200 flex items-center justify-between"
                                         onMouseDown={(e) => handleColumnDragStart(e, column.id)}
                                         style={{ cursor: 'grab' }}>
                                        <div className="flex items-center gap-2 flex-1">
                                            <span className="text-gray-400">⋮⋮</span>
                                            {editingColumn === column.id ? (
                                                <input
                                                    type="text"
                                                    value={editingName}
                                                    onChange={(e) => setEditingName(e.target.value)}
                                                    onBlur={() => finishEditingColumn(column.id)}
                                                    onKeyPress={(e) => e.key === 'Enter' && finishEditingColumn(column.id)}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Escape') {
                                                            setEditingColumn(null);
                                                            setEditingName('');
                                                        }
                                                    }}
                                                    className="text-lg font-semibold text-gray-900 border-2 border-blue-500 rounded px-2 py-1"
                                                    autoFocus
                                                />
                                            ) : (
                                                <div className="flex items-center gap-1 editable-title-container">
                                                    <h2
                                                        className="text-lg font-semibold text-gray-900 editable-title"
                                                        onDoubleClick={() => startEditingColumn(column.id, column.name)}
                                                        title="Double-click to rename"
                                                    >
                                                        {column.name}
                                                    </h2>
                                                    <span className="pencil-icon text-gray-400 text-sm">✏️</span>
                                                </div>
                                            )}
                                            <span className="text-sm text-gray-500">({filteredBooks(column.books).length})</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <div className="relative" ref={columnMenuOpen === column.id ? columnMenuRef : null}>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); setColumnMenuOpen(columnMenuOpen === column.id ? null : column.id); }}
                                                    className="p-1 hover:bg-gray-100 rounded text-lg"
                                                    title="Column options">
                                                    ⋮
                                                </button>
                                                {columnMenuOpen === column.id && (
                                                    <div className="absolute right-0 top-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 w-56"
                                                         onClick={(e) => e.stopPropagation()}>
                                                        <div className="p-2">
                                                            {/* Sort submenu */}
                                                            <div className="relative">
                                                                <button
                                                                    onClick={(e) => { e.stopPropagation(); setSortMenuOpen(sortMenuOpen === column.id ? null : column.id); }}
                                                                    className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm flex items-center justify-between">
                                                                    Sort Column
                                                                    <span>▸</span>
                                                                </button>
                                                                {sortMenuOpen === column.id && (
                                                                    <div className="absolute left-full top-0 ml-1 bg-white border border-gray-300 rounded-lg shadow-lg w-48 z-50">
                                                                        <div className="p-2">
                                                                            <button onClick={() => sortColumn(column.id, 'title-asc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Title (A→Z)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'title-desc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Title (Z→A)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'author-asc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Author (A→Z)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'author-desc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Author (Z→A)</button>
                                                                            {dataSource === 'enriched' && (
                                                                                <>
                                                                                    <button onClick={() => sortColumn(column.id, 'rating-desc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Rating (High→Low)</button>
                                                                                    <button onClick={() => sortColumn(column.id, 'rating-asc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Rating (Low→High)</button>
                                                                                </>
                                                                            )}
                                                                            <button onClick={() => sortColumn(column.id, 'acquired-desc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Date (Newest)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'acquired-asc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Date (Oldest)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'series-pos-asc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Series (1→99)</button>
                                                                            <button onClick={() => sortColumn(column.id, 'series-pos-desc')} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Series (99→1)</button>
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </div>

                                                            <div className="border-t border-gray-200 my-1"></div>

                                                            {/* Auto-divide options */}
                                                            <button onClick={() => autoDivideBySeries(column.id)} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Auto-Divide by Series</button>
                                                            {dataSource === 'enriched' && (
                                                                <button onClick={() => autoDivideByRating(column.id)} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Auto-Divide by Rating</button>
                                                            )}

                                                            <div className="border-t border-gray-200 my-1"></div>

                                                            {/* Insert Divider */}
                                                            <button onClick={() => { setInsertDividerOpen(column.id); setNewDividerLabel(''); }} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Insert Divider</button>

                                                            <div className="border-t border-gray-200 my-1"></div>

                                                            {/* Rename and Delete */}
                                                            <button onClick={() => { startEditingColumn(column.id, column.name); setColumnMenuOpen(null); }} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm">Rename Column</button>
                                                            {columns.length > 1 && (
                                                                <button onClick={() => { openDeleteDialog(column.id); setColumnMenuOpen(null); }} className="w-full text-left px-2 py-1 hover:bg-gray-100 rounded text-sm text-red-600">Delete Column</button>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex-1 overflow-y-auto p-4">
                                        <div className="grid grid-cols-3 gap-3 relative book-grid">
                                            {filteredBooks(column.books).map((item) => {
                                                // v3.11.0 - Handle dividers
                                                if (typeof item === 'object' && item.type === 'divider') {
                                                    const isHovering = hoveringDivider && hoveringDivider.columnId === column.id && hoveringDivider.dividerId === item.id;
                                                    const isEditing = editingDivider && editingDivider.columnId === column.id && editingDivider.dividerId === item.id;
                                                    const isSelected = selectedDivider && selectedDivider.columnId === column.id && selectedDivider.dividerId === item.id; // v3.13.0

                                                    // v3.14.0 - Find actual index for drop indicator
                                                    const actualIndex = column.books.findIndex(b =>
                                                        typeof b === 'object' && b.type === 'divider' && b.id === item.id
                                                    );

                                                    return (
                                                        <div key={item.id} className="col-span-3 relative">
                                                            {/* v3.14.0 - Drop indicator for dividers */}
                                                            {isDragging && dropTarget?.columnId === column.id && dropTarget?.index === actualIndex && (
                                                                <div className="drop-indicator" style={{ top: '-6px' }} />
                                                            )}
                                                            <div className={`flex items-center gap-2 py-2 px-3 my-1 rounded cursor-pointer divider-item ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
                                                                 data-divider-id={item.id}
                                                                 style={{ backgroundColor: isSelected ? '#dbeafe' : '#f3f4f6' }}
                                                                 onClick={(e) => {
                                                                     if (!isEditing) {
                                                                         e.stopPropagation();
                                                                         selectDividerGroup(column.id, item.id);
                                                                     }
                                                                 }}
                                                                 onMouseEnter={() => setHoveringDivider({ columnId: column.id, dividerId: item.id })}
                                                                 onMouseLeave={() => setHoveringDivider(null)}>
                                                                {isHovering && (
                                                                <span
                                                                    className="text-gray-400 cursor-grab text-lg"
                                                                    onMouseDown={(e) => handleDividerMouseDown(e, item, column.id)}
                                                                    style={{ cursor: 'grab' }}>
                                                                    ⋮
                                                                </span>
                                                            )}
                                                            <div className="flex-1 text-center">
                                                                {isEditing ? (
                                                                    <input
                                                                        type="text"
                                                                        value={editingDividerLabel}
                                                                        onChange={(e) => setEditingDividerLabel(e.target.value)}
                                                                        onBlur={finishEditingDivider}
                                                                        onKeyPress={(e) => {
                                                                            if (e.key === 'Enter') finishEditingDivider();
                                                                        }}
                                                                        onKeyDown={(e) => {
                                                                            if (e.key === 'Escape') {
                                                                                setEditingDivider(null);
                                                                                setEditingDividerLabel('');
                                                                            }
                                                                        }}
                                                                        className="text-sm font-semibold text-gray-700 border-2 border-blue-500 rounded px-2 py-1 text-center"
                                                                        autoFocus
                                                                        onClick={(e) => e.stopPropagation()}
                                                                    />
                                                                ) : (
                                                                    <span
                                                                        className="text-sm font-semibold text-gray-700 cursor-pointer select-none"
                                                                        onDoubleClick={() => startEditingDivider(column.id, item.id, item.label)}
                                                                        title="Double-click to rename">
                                                                        ═══ {item.label} ═══
                                                                    </span>
                                                                )}
                                                            </div>
                                                            {isHovering && (
                                                                <button
                                                                    onClick={() => deleteDivider(column.id, item.id)}
                                                                    className="text-gray-400 hover:text-red-600 font-bold text-lg"
                                                                    title="Delete divider">
                                                                    ✕
                                                                </button>
                                                            )}
                                                            </div>
                                                        </div>
                                                    );
                                                }

                                                // Regular book rendering
                                                const book = item;
                                                const actualIndex = column.books.findIndex(b =>
                                                    (typeof b === 'object' && b.type === 'divider' && b.id === item.id) ||
                                                    (typeof b === 'string' && b === book.id)
                                                );
                                                return (
                                                    <div key={book.id} className="relative book-item" data-book-id={book.id}>
                                                        {isDragging && dropTarget?.columnId === column.id && dropTarget?.index === actualIndex &&
                                                         draggedBook?.id !== book.id && !selectedBooks.has(book.id) && (
                                                            <div className="drop-indicator" style={{ top: '-6px' }} />
                                                        )}
                                                        <div className={`book-clickable ${selectedBooks.has(book.id) ? 'selected' : ''} ${draggedBook?.id === book.id && isDragging ? 'dragging' : ''}`}
                                                             onMouseDown={(e) => handleMouseDown(e, book, column.id)}
                                                             onClick={(e) => {
                                                                 e.stopPropagation();

                                                                 if (isDragging) return;

                                                                 // Always set active column when clicking a book
                                                                 setActiveColumnId(column.id);

                                                                 if (e.ctrlKey || e.metaKey) {
                                                                     // Ctrl+Click: Toggle selection
                                                                     toggleBookSelection(book.id);
                                                                     setLastClickedBook({ id: book.id, columnId: column.id });
                                                                 } else if (e.shiftKey) {
                                                                     // Shift+Click: Range selection
                                                                     if (lastClickedBook && lastClickedBook.columnId === column.id) {
                                                                         // Range from last clicked book to this book (same column)
                                                                         selectBookRange(lastClickedBook.id, book.id, column.id);
                                                                     } else {
                                                                         // No anchor point or different column: treat as single click
                                                                         clearSelection();
                                                                         toggleBookSelection(book.id);
                                                                         setLastClickedBook({ id: book.id, columnId: column.id });
                                                                     }
                                                                 } else {
                                                                     // Single click: Select this book (replace selection)
                                                                     clearSelection();
                                                                     toggleBookSelection(book.id);
                                                                     setLastClickedBook({ id: book.id, columnId: column.id });
                                                                 }
                                                             }}
                                                             onDoubleClick={(e) => {
                                                                 e.stopPropagation();
                                                                 // Double-click: Open modal
                                                                 openBookModal(book, column.id);
                                                             }}
                                                             onContextMenu={(e) => {
                                                                 e.preventDefault();
                                                                 // Right-click: If book not in selection, select it first
                                                                 if (!selectedBooks.has(book.id)) {
                                                                     clearSelection();
                                                                     toggleBookSelection(book.id);
                                                                 }
                                                                 // Show context menu
                                                                 setContextMenu({
                                                                     x: e.clientX,
                                                                     y: e.clientY,
                                                                     bookId: book.id,
                                                                     columnId: column.id
                                                                 });
                                                             }}
                                                             title={book.collections && book.collections.length > 0
                                                                ? `Collections:\n${book.collections.map(c => c.name).join('\n')}`
                                                                : '📭 No collections'}>
                                                            <div className="relative">
                                                                {blankImageBooks.has(book.id) ? (
                                                                    <div className="w-full aspect-[2/3] rounded shadow-lg overflow-hidden flex flex-col" 
                                                                         style={{ backgroundColor: '#d4c5a9' }}>
                                                                        <div className="flex-1 flex items-center justify-center px-4">
                                                                            <div className="text-center">
                                                                                <div className="text-xs font-serif font-bold text-gray-800 leading-tight mb-2">
                                                                                    {book.title.length > 40 ? book.title.substring(0, 40) + '...' : book.title}
                                                                                </div>
                                                                                <div className="text-xs text-gray-600 mt-2">KINDLE EDITION</div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                ) : (
                                                                    <img src={book.coverUrl} 
                                                                         alt={book.title} 
                                                                         className="w-full rounded shadow-lg"
                                                                         onLoad={(e) => checkIfBlankImage(e.target, book.id)}
                                                                         onError={(e) => e.target.src = 'https://via.placeholder.com/128x192/4f46e5/fff?text=No+Cover'} />
                                                                )}
                                                                {/* Top-right: Rating badge */}
                                                                {book.rating > 0 && (
                                                                    <div className="absolute top-1 right-1 bg-black bg-opacity-75 rounded px-1.5 py-0.5 text-xs font-bold text-yellow-400">
                                                                        ★ {book.rating.toFixed(1)}
                                                                    </div>
                                                                )}
                                                                {/* Bottom-right: Read status checkmark */}
                                                                {book.readStatus === 'READ' && (
                                                                    <div className="absolute bottom-1 right-1 bg-green-600 rounded-full w-6 h-6 flex items-center justify-center" title="Read">
                                                                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                                                                        </svg>
                                                                    </div>
                                                                )}
                                                                {/* Top-left: Selection, Wishlist, or Collections badge (priority order) */}
                                                                {selectedBooks.has(book.id) ? (
                                                                    <div className="absolute top-1 left-1 bg-blue-600 rounded-full w-6 h-6 flex items-center justify-center z-10">
                                                                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                                                                        </svg>
                                                                    </div>
                                                                ) : book.isWishlist ? (
                                                                    <div className="absolute top-1 left-1 bg-red-500 bg-opacity-80 rounded px-1.5 py-0.5 text-xs font-bold text-white">
                                                                        ❤+
                                                                    </div>
                                                                ) : book.collections && book.collections.length > 0 && (
                                                                    <div className="absolute top-1 left-1 bg-gray-700 bg-opacity-75 rounded px-1.5 py-0.5 text-xs font-bold text-white">
                                                                        📁 {book.collections.length}
                                                                    </div>
                                                                )}
                                                            </div>
                                                            <div className="mt-2 text-xs">
                                                                <div className="font-medium text-gray-800 leading-tight line-clamp-2" title={book.title}>
                                                                    {book.title}
                                                                </div>
                                                                <div className="text-gray-600 mt-1 leading-tight line-clamp-1" title={book.author}>
                                                                    {book.author}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                            {isDragging && dropTarget?.columnId === column.id && dropTarget?.index >= column.books.length && (
                                                <div className="drop-indicator" style={{ bottom: '-6px' }} />
                                            )}
                                        </div>
                                    </div>
                                    {isDraggingColumn && columnDropTarget === colIndex + 1 && draggedColumn !== column.id && (
                                        <div className="column-drop-indicator" style={{ right: '-8px' }} />
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {selectedBooks.size > 0 && (
                        <div className="fixed bottom-20 right-4 bg-blue-600 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 z-50">
                            <span className="font-medium">{selectedBooks.size} book{selectedBooks.size !== 1 ? 's' : ''} selected</span>
                            <button
                                onClick={clearSelection}
                                className="hover:bg-blue-700 px-3 py-1 rounded bg-blue-500 transition-colors">
                                Clear
                            </button>
                        </div>
                    )}

                    {contextMenu && (
                        <div className="fixed bg-white border border-gray-300 rounded-lg shadow-xl z-[60] py-1 min-w-[180px]"
                             style={{
                                 left: `${contextMenu.x}px`,
                                 top: `${contextMenu.y}px`
                             }}
                             onClick={(e) => e.stopPropagation()}>
                            <div className="px-2 py-1 text-xs font-semibold text-gray-500 border-b border-gray-200">
                                {selectedBooks.size} book{selectedBooks.size !== 1 ? 's' : ''} selected
                            </div>
                            {columns.filter(col => col.id !== contextMenu.columnId).map(col => (
                                <button
                                    key={col.id}
                                    className="w-full text-left px-4 py-2 hover:bg-blue-50 text-sm text-gray-700 flex items-center gap-2"
                                    onClick={() => {
                                        // Move selected books to this column
                                        const booksToMove = Array.from(selectedBooks);
                                        setColumns(columns.map(column => {
                                            if (column.id === contextMenu.columnId) {
                                                // Remove from source column
                                                return { ...column, books: column.books.filter(id => !booksToMove.includes(id)) };
                                            }
                                            if (column.id === col.id) {
                                                // Add to target column at the end
                                                return { ...column, books: [...column.books, ...booksToMove] };
                                            }
                                            return column;
                                        }));
                                        clearSelection();
                                        setContextMenu(null);
                                    }}>
                                    📁 Move to "{col.name}"
                                </button>
                            ))}
                        </div>
                    )}

                    <div className="fixed bottom-2 right-2 text-xs text-gray-400">
                        v{ORGANIZER_VERSION}
                    </div>

                    {isDragging && draggedBook && (
                        <div className="drag-ghost"
                             style={{
                                 left: dragCurrentPos.x - 50,
                                 top: dragCurrentPos.y - 75,
                                 width: '100px'
                             }}>
                            {/* Show stacked effect if dragging multiple books */}
                            {selectedBooks.size > 1 && selectedBooks.has(draggedBook.id) && (
                                <>
                                    <div className="absolute" style={{ left: '8px', top: '8px', opacity: 0.4 }}>
                                        <div className="w-full aspect-[2/3] rounded shadow-2xl border-2 border-blue-500 bg-blue-100" style={{ width: '100px' }}></div>
                                    </div>
                                    <div className="absolute" style={{ left: '4px', top: '4px', opacity: 0.6 }}>
                                        <div className="w-full aspect-[2/3] rounded shadow-2xl border-2 border-blue-500 bg-blue-200" style={{ width: '100px' }}></div>
                                    </div>
                                </>
                            )}
                            {/* Main dragged book */}
                            <div className="relative">
                                {blankImageBooks.has(draggedBook.id) ? (
                                    <div className="w-full aspect-[2/3] rounded shadow-2xl border-2 border-blue-500"
                                         style={{ backgroundColor: '#d4c5a9' }}>
                                        <div className="flex items-center justify-center h-full px-1">
                                            <div className="text-xs font-serif font-bold text-gray-800 text-center leading-tight">
                                                {draggedBook.title.length > 20 ? draggedBook.title.substring(0, 20) + '...' : draggedBook.title}
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <img src={draggedBook.coverUrl}
                                         alt={draggedBook.title}
                                         className="w-full rounded shadow-2xl border-2 border-blue-500" />
                                )}
                                {/* Count badge for multiple books */}
                                {selectedBooks.size > 1 && selectedBooks.has(draggedBook.id) && (
                                    <div className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold border-2 border-white">
                                        {selectedBooks.size}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        ReactDOM.render(<ReaderWrangler />, document.getElementById('root'));
