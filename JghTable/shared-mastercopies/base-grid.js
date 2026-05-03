// ============================================================================
// SHARED AG GRID FRAMEWORK FOR ZSUN APPS
// ============================================================================

window.ZsunGridFramework = (function () {
    'use strict';

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================
    function escapeHtml(str) {
        if (str == null) return '';
        str = String(str);
        return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function generateColumnDefs(baseColumnDefs, defaultWidth) {
        return baseColumnDefs.map(cd => {
            const cloned = Object.assign({}, cd);
            if (!cloned.width) {
                cloned.width = defaultWidth;
            }
            return cloned;
        });
    }

    // ============================================================================
    // CLIPBOARD FUNCTIONS
    // ============================================================================
    function copyTextToClipboard(text) {
        if (text == null) text = '';
        const str = String(text);
        if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
            navigator.clipboard.writeText(str).catch(() => fallbackCopyExecCommand(str));
            return;
        }
        fallbackCopyExecCommand(str);
    }

    function fallbackCopyExecCommand(text) {
        try {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        } catch (e) {
            console.warn('Clipboard copy failed', e);
        }
    }

    function copyableCellRenderer(params) {
        const span = document.createElement('span');
        span.className = 'copyable-cell';
        span.tabIndex = 0;
        const text = params.valueFormatted != null ? String(params.valueFormatted) : (params.value == null ? '' : String(params.value));
        span.textContent = text;

        span.addEventListener('keydown', (ev) => {
            if ((ev.ctrlKey || ev.metaKey) && (ev.key === 'c' || ev.key === 'C')) {
                ev.preventDefault();
                copyTextToClipboard(text);
            }
        });

        span.addEventListener('dblclick', () => {
            copyTextToClipboard(text);
        });

        span.title = 'Double-click to copy. Or focus and press Ctrl+C (Cmd+C on Mac).';
        return span;
    }

    // ============================================================================
    // GRID MANAGER CLASS
    // ============================================================================
    class GridManager {
        constructor(config) {
            this.config = config;
            this.gridOptions = null;
            this._currentData = [];
            this._lastErrorMessage = null;
        }

        createGridOptions() {
            return {
                columnDefs: generateColumnDefs(this.config.baseColumnDefs, this.config.defaultColWidth),
                rowData: [],
                rowHeight: this.config.rowHeight,
                headerHeight: this.config.headerHeight,
                defaultColDef: {
                    sortable: this.config.sortable,
                    resizable: this.config.resizable,
                    filter: this.config.filterable,
                    cellRenderer: copyableCellRenderer,
                    minWidth: this.config.minWidth
                },
                enableRangeSelection: true,
                rowSelection: 'multiple',
                overlayNoRowsTemplate: '',
            };
        }

        safeSetRowData(data) {
            this._currentData = Array.isArray(data) ? data : [];
            if (this.gridOptions?.api?.setRowData) {
                this.gridOptions.api.setRowData(this._currentData);
            } else {
                console.warn('AG Grid API not ready for setRowData');
            }
        }

        showGridError(message) {
            this._lastErrorMessage = message;
            const safe = escapeHtml(message);
            const template = `
                <div class="grid-overlay">
                    <strong>Error loading data</strong>
                    <div class="grid-error-message">${safe}</div>
                    <div class="grid-overlay-actions">
                        <button id="gridRetryBtn" class="btn">Retry</button>
                        <a id="gridHelpLink" href="https://github.com/jghughes/Zwift-Solution-2025" target="_blank">Help / Docs</a>
                    </div>
                </div>`;

            if (this.gridOptions) this.gridOptions.overlayNoRowsTemplate = template;
            if (this.gridOptions?.api?.showNoRowsOverlay) {
                this.gridOptions.api.showNoRowsOverlay();
                setTimeout(() => {
                    const retry = document.getElementById('gridRetryBtn');
                    if (retry && !retry.dataset.bound) {
                        retry.dataset.bound = '1';
                        retry.addEventListener('click', () => {
                            this.hideGridError();
                            this.loadData();
                        });
                    }
                }, 0);
            }
        }

        hideGridError() {
            if (this.gridOptions?.api?.hideOverlay) {
                try { this.gridOptions.api.hideOverlay(); }
                catch (e) { console.warn('hideOverlay failed', e); }
            }
        }

        initializeGrid() {
            const eGridDiv = document.getElementById('myGrid');
            if (!eGridDiv) {
                console.error('Grid container element not found');
                return;
            }

            eGridDiv.innerHTML = '';
            this.gridOptions = this.createGridOptions();

            try {
                new agGrid.Grid(eGridDiv, this.gridOptions);
                console.log('AG Grid initialized successfully');
            } catch (err) {
                this.showGridError(err.message || 'Error initializing AG Grid');
                console.error('Error initializing AG Grid:', err);
            }
        }

        loadData(url) {
            if (url) {
                this.config.dataUrl = url;
            }

            if (this.gridOptions?.api?.showLoadingOverlay) {
                try { this.gridOptions.api.showLoadingOverlay(); }
                catch (e) { console.warn('showLoadingOverlay failed', e); }
            }

            fetch(this.config.dataUrl)
                .then(response => {
                    if (!response.ok) {
                        let message = '';
                        switch (response.status) {
                            case 401:
                            case 403:
                                message = 'Authorization error: You do not have permission to access this data.';
                                break;
                            case 404:
                                message = 'File not found: The requested data file does not exist.';
                                break;
                            case 500:
                                message = 'Server error: There was a problem with the server.';
                                break;
                            default:
                                message = `HTTP error: ${response.status} ${response.statusText}`;
                        }
                        throw new Error(message);
                    }
                    return response.json();
                })
                .then(data => {
                    this.safeSetRowData(data);
                })
                .catch(err => {
                    let errorMsg = err.message || String(err);
                    if (err.name === 'TypeError' && errorMsg.includes('Failed to fetch')) {
                        errorMsg = 'Unable to fetch data. This may be due to a network issue or a CORS restriction.';
                    } else if (errorMsg.includes('Unexpected token')) {
                        errorMsg = 'Format error: Data file is not valid JSON.';
                    }
                    this.safeSetRowData(this.config.fallbackData);
                    this.showGridError(errorMsg);
                    console.error('Error loading data:', err);
                });
        }

        initialize() {
            console.log(`Initializing ${this.config.appName} Grid...`);
            this.initializeGrid();

            const filterInput = document.getElementById('filterInput');
            if (filterInput) {
                filterInput.addEventListener('input', () => {
                    if (this.gridOptions?.api?.setQuickFilter) {
                        this.gridOptions.api.setQuickFilter(filterInput.value);
                    }
                });
            }

            this.loadData();
            console.log('Grid initialization complete');
        }
    }

    // ============================================================================
    // PUBLIC API
    // ============================================================================
    return {
        GridManager: GridManager
    };
})();