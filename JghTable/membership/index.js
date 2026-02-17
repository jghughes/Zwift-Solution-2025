// ============================================================================
// GUARD AGAINST DUPLICATE SCRIPT LOADS
// ============================================================================
if (window.__MEMBERSHIP_GRID_INITIALIZED) {
    console.error('Grid script loaded multiple times!');
    throw new Error('Duplicate script load detected');
}
window.__MEMBERSHIP_GRID_INITIALIZED = true;

// ============================================================================
// CONFIGURATION
// ============================================================================
const DATA_URL = "https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json";

const FALLBACK_DATA = [
    { zwift_id: 999999, name_racingapp: "Joe Soap" }
];

const CONFIG = {
    DESKTOP_MIN_WIDTH: 900,
    AUTOSIZE_DELAY_MS: 50,
    MAX_AUTOSIZE_ATTEMPTS: 8,
    MAX_LOG_ENTRIES: 200,
    // Excel-like defaults (11pt Calibri ? 15px)
    ROW_HEIGHT: 25,
    HEADER_HEIGHT: 32,
    DEFAULT_COL_WIDTH: 60
};

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', sortable: true, resizable: true },
    { headerName: "Name", field: "full_name", pinned: 'left', sortable: true, resizable: true },
    { headerName: "Flag", field: "zwift_country_code3", sortable: true, resizable: true },
    { headerName: "zFTP", field: "zwift_zftp_wkg", sortable: true, resizable: true },
    { headerName: "60min", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    { headerName: "zRS", field: "zwift_racing_score", sortable: true, resizable: true },
    { headerName: "Open", field: "cat_open", sortable: true, resizable: true },
    { headerName: "Women", field: "cat_women", sortable: true, resizable: true },
    { headerName: "vELO", field: "velo_cat_label", sortable: true, resizable: true },
    { headerName: "ZwiftID", field: "zwift_id", sortable: true, resizable: true },
    //{ headerName: "Country", field: "zwift_country_code3", sortable: true, resizable: true },
    //{ headerName: "Age", field: "age_years", sortable: true, resizable: true },
    //{ headerName: "Height (cm)", field: "height_cm", sortable: true, resizable: true },
    //{ headerName: "Weight (kg)", field: "weight_kg", sortable: true, resizable: true },
    //{ headerName: "Gender", field: "gender_code", sortable: true, resizable: true },
    //{ headerName: "Cat (Open)", field: "cat_open", sortable: true, resizable: true },
    //{ headerName: "Cat (Women)", field: "cat_women", sortable: true, resizable: true },
    //{ headerName: "ZRS", field: "zwift_racing_score", sortable: true, resizable: true },
    //{ headerName: "FTP (W)", field: "zwift_ftp_w", sortable: true, resizable: true },
    //{ headerName: "zFTP (W)", field: "zwift_zftp_w", sortable: true, resizable: true },
    //{ headerName: "zFTP (W/kg)", field: "zwift_zftp_wkg", sortable: true, resizable: true },
    //{ headerName: "Zwift", field: "zwift_cat_label", sortable: true, resizable: true },
    //{ headerName: "Velo Rating (30d)", field: "velo_rating_30_days", sortable: true, resizable: true },
    //{ headerName: "Velo # (30d)", field: "velo_cat_num_30_days", sortable: true, resizable: true },
    //{ headerName: "Velo Cat (30d)", field: "velo_cat_name_30_days", sortable: true, resizable: true },
    //{ headerName: "Age Group", field: "velo_age_group", sortable: true, resizable: true },
    //{ headerName: "W/kg 60min (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    //{ headerName: "60min W (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    //{ headerName: "Wkg 5s", field: "wkg_05sec", sortable: true, resizable: true },
    //{ headerName: "W 5s", field: "w_05sec", sortable: true, resizable: true },
    //{ headerName: "Wkg 1min", field: "wkg_01min", sortable: true, resizable: true },
    //{ headerName: "W 1min", field: "w_01min", sortable: true, resizable: true },
    //{ headerName: "Timestamp", field: "timestamp", sortable: true, resizable: true }
];
// ============================================================================
// STATE
// ============================================================================
let _currentData = [];
let _lastErrorMessage = null;
let gridOptions = null;

// ============================================================================
// CONSOLE LOG CAPTURE (runs immediately)
// ============================================================================
const _logBuffer = [];
(function captureConsole() {
    const orig = { log: console.log, warn: console.warn, error: console.error };
    function push(level, args) {
        const ts = new Date().toISOString();
        _logBuffer.push({
            ts,
            level,
            message: args.map(a => {
                try { return typeof a === 'string' ? a : JSON.stringify(a); }
                catch (e) { return String(a); }
            }).join(' ')
        });
        if (_logBuffer.length > CONFIG.MAX_LOG_ENTRIES) _logBuffer.shift();
    }
    console.log = function () { push('log', Array.from(arguments)); orig.log.apply(console, arguments); };
    console.warn = function () { push('warn', Array.from(arguments)); orig.warn.apply(console, arguments); };
    console.error = function () { push('error', Array.from(arguments)); orig.error.apply(console, arguments); };
})();

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

function generateColumnDefs() {
    return BASE_COLUMN_DEFS.map(cd => {
        const cloned = Object.assign({}, cd);
        cloned.width = CONFIG.DEFAULT_COL_WIDTH;
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
        console.warn('fallbackCopyExecCommand failed', e);
    }
}

function copyableCellRenderer(params) {
    const span = document.createElement('span');
    span.className = 'copyable-cell';
    span.tabIndex = 0;
    const text = params.value == null ? '' : String(params.value);
    span.textContent = text;

    function flash() {
        try {
            span.classList.add('copy-flash');
            setTimeout(() => span.classList.remove('copy-flash'), 180);
        } catch (e) {
            console.warn('Flash animation failed', e);
        }
    }

    span.addEventListener('keydown', (ev) => {
        if ((ev.ctrlKey || ev.metaKey) && (ev.key === 'c' || ev.key === 'C')) {
            ev.preventDefault();
            copyTextToClipboard(text);
            flash();
        }
    });

    span.addEventListener('dblclick', () => {
        copyTextToClipboard(text);
        flash();
    });

    span.title = 'Double-click to copy. Or focus and press Ctrl+C (Cmd+C on Mac).';
    return span;
}

// ============================================================================
// GRID CONFIGURATION
// ============================================================================
function createGridOptions() {
    return {
        columnDefs: generateColumnDefs(),
        rowData: [],
        rowHeight: CONFIG.ROW_HEIGHT,
        headerHeight: CONFIG.HEADER_HEIGHT,
        defaultColDef: {
            sortable: true,
            resizable: true,
            filter: true,
            cellRenderer: copyableCellRenderer,
            minWidth: 40
        },
        enableRangeSelection: true,
        rowSelection: 'multiple',
        overlayNoRowsTemplate: '',
    };
}

// ============================================================================
// DATA MANAGEMENT
// ============================================================================
function safeSetRowData(data) {
    _currentData = Array.isArray(data) ? data : [];
    if (gridOptions && gridOptions.api && typeof gridOptions.api.setRowData === 'function') {
        gridOptions.api.setRowData(_currentData);
        // Columns will use their default width from CONFIG.DEFAULT_COL_WIDTH
    } else {
        console.warn('AG Grid API not ready for setRowData');
    }
}

// ============================================================================
// COLUMN SIZING
// ============================================================================
function autoSizeAllColumns(attempt = 0) {
    if (!gridOptions || !gridOptions.columnApi || typeof gridOptions.columnApi.autoSizeColumns !== 'function') {
        if (attempt < CONFIG.MAX_AUTOSIZE_ATTEMPTS) {
            setTimeout(() => autoSizeAllColumns(attempt + 1), 120);
            return;
        }
        console.warn('Column API not available after max attempts');
        return;
    }
    try {
        const allCols = gridOptions.columnApi.getAllColumns();
        if (!allCols || allCols.length === 0) return;

        const colIds = allCols.map(c => c.getColId());
        gridOptions.columnApi.autoSizeColumns(colIds, false);

        setTimeout(() => {
            try {
                const gridDiv = document.getElementById('myGrid');
                const gridWidth = gridDiv ? gridDiv.clientWidth : window.innerWidth;
                const totalColsWidth = allCols.reduce((s, c) =>
                    s + (c.getActualWidth ? c.getActualWidth() : 0), 0);
                const w = window.innerWidth || document.documentElement.clientWidth;

                if (w >= CONFIG.DESKTOP_MIN_WIDTH &&
                    gridOptions.api &&
                    typeof gridOptions.api.sizeColumnsToFit === 'function' &&
                    totalColsWidth < gridWidth) {
                    gridOptions.api.sizeColumnsToFit();
                }
            } catch (e) {
                console.warn('post-autoSize check failed', e);
            }
        }, CONFIG.AUTOSIZE_DELAY_MS);
    } catch (e) {
        console.warn('autoSizeAllColumns failed', e);
    }
}

function adjustColumnSizing() {
    if (!gridOptions || !gridOptions.api) return;
    try {
        const w = window.innerWidth || document.documentElement.clientWidth;
        if (w >= CONFIG.DESKTOP_MIN_WIDTH && typeof gridOptions.api.sizeColumnsToFit === 'function') {
            gridOptions.api.sizeColumnsToFit();
        }
    } catch (e) {
        console.warn('adjustColumnSizing error', e);
    }
}

// ============================================================================
// ERROR/STATUS OVERLAYS
// ============================================================================
function showStatusBanner(message) {
    const container = document.querySelector('.document-container') || document.body;
    const existing = document.getElementById('gridStatusBanner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'gridStatusBanner';
    banner.className = 'grid-status-banner';
    banner.innerHTML = `<div class="message">${escapeHtml(message)}</div>
                        <button id="gridBannerRetry" class="btn">Retry</button>`;
    if (container.firstElementChild) container.insertBefore(banner, container.firstElementChild);
    else container.appendChild(banner);

    const retry = document.getElementById('gridBannerRetry');
    if (retry && !retry.dataset.bound) {
        retry.dataset.bound = '1';
        retry.addEventListener('click', () => {
            const b = document.getElementById('gridStatusBanner');
            if (b) b.remove();
            initializeDataLoad();
        });
    }
}

function showGridError(message) {
    _lastErrorMessage = message;
    const safe = escapeHtml(message);
    const template = `
        <div class="grid-error-overlay">
            <div class="grid-overlay-header"><strong class="grid-overlay-title">Error loading data</strong></div>
            <div class="grid-error-message">${safe}</div>
            <div class="actions">
                <button id="gridRetryBtn" class="btn">Retry</button>
                <button id="gridViewLogsBtn" class="btn secondary">View logs</button>
                <a id="gridHelpLink" class="help-link" href="#">Help / Docs</a>
            </div>
        </div>`;
    if (gridOptions) gridOptions.overlayNoRowsTemplate = template;
    if (gridOptions && gridOptions.api && typeof gridOptions.api.showNoRowsOverlay === 'function') {
        try {
            gridOptions.api.showNoRowsOverlay();
            setTimeout(bindOverlayControls, 0);
            return;
        } catch (e) {
            console.warn('showNoRowsOverlay failed', e);
        }
    }
    createFallbackOverlay(template);
}

function bindOverlayControls() {
    const retry = document.getElementById('gridRetryBtn');
    const viewLogs = document.getElementById('gridViewLogsBtn');
    const help = document.getElementById('gridHelpLink');

    if (retry && !retry.dataset.bound) {
        retry.dataset.bound = '1';
        retry.addEventListener('click', () => {
            hideGridError();
            initializeDataLoad();
        });
    }
    if (viewLogs && !viewLogs.dataset.bound) {
        viewLogs.dataset.bound = '1';
        viewLogs.addEventListener('click', (e) => {
            e.preventDefault();
            showLogsOverlay();
        });
    }
    if (help && !help.dataset.bound) {
        help.dataset.bound = '1';
        help.addEventListener('click', (e) => {
            e.preventDefault();
            window.open('https://github.com/jghughes/Zwift-Solution-2025', '_blank');
        });
    }
}

function createFallbackOverlay(html) {
    const gridDiv = document.getElementById('myGrid');
    if (!gridDiv) return;
    const existing = document.getElementById('gridErrorOverlayCustom');
    if (existing) existing.parentNode.removeChild(existing);

    const container = document.createElement('div');
    container.id = 'gridErrorOverlayCustom';
    container.className = 'grid-fallback-overlay';
    container.innerHTML = html;
    gridDiv.style.position = gridDiv.style.position || 'relative';
    gridDiv.appendChild(container);
    setTimeout(bindOverlayControls, 0);
}

function showLogsOverlay() {
    const logsHtml = _logBuffer.map(l => `${l.ts} [${l.level}] ${escapeHtml(l.message)}`).join('\n');
    const template = `
        <div class="grid-logs-overlay">
            <div class="grid-logs-controls">
                <strong>Client logs</strong>
                <div class="grid-logs-actions">
                    <button id="gridBackBtn" class="btn">Back</button>
                    <button id="gridClearLogsBtn" class="btn secondary">Clear</button>
                </div>
            </div>
            <pre id="gridLogsContent" class="grid-logs-pre">${escapeHtml(logsHtml || '(no logs yet)')}</pre>
        </div>`;
    if (gridOptions) gridOptions.overlayNoRowsTemplate = template;
    if (gridOptions && gridOptions.api && typeof gridOptions.api.showNoRowsOverlay === 'function') {
        try {
            gridOptions.api.showNoRowsOverlay();
            setTimeout(() => {
                const back = document.getElementById('gridBackBtn');
                const clear = document.getElementById('gridClearLogsBtn');
                if (back && !back.dataset.bound) {
                    back.dataset.bound = '1';
                    back.addEventListener('click', () => showGridError(_lastErrorMessage || 'Error'));
                }
                if (clear && !clear.dataset.bound) {
                    clear.dataset.bound = '1';
                    clear.addEventListener('click', () => {
                        _logBuffer.length = 0;
                        const c = document.getElementById('gridLogsContent');
                        if (c) c.textContent = '(no logs yet)';
                    });
                }
            }, 0);
            return;
        } catch (e) {
            console.warn('showNoRowsOverlay failed for logs', e);
        }
    }
    createFallbackOverlay(template);
}

function hideGridError() {
    if (gridOptions && gridOptions.api) {
        if (typeof gridOptions.api.hideOverlay === 'function') {
            try { gridOptions.api.hideOverlay(); }
            catch (e) { console.warn('hideOverlay failed', e); }
        } else {
            try {
                if (gridOptions.api.hideNoRowsOverlay) gridOptions.api.hideNoRowsOverlay();
            } catch (e) {
                console.warn('hideNoRowsOverlay failed', e);
            }
        }
    }
    const existing = document.getElementById('gridErrorOverlayCustom');
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
}

// ============================================================================
// GRID INITIALIZATION
// ============================================================================
function initializeGrid() {
    const eGridDiv = document.getElementById('myGrid');
    if (!eGridDiv) {
        console.error('Grid container element not found');
        return;
    }

    // Clear any existing content
    eGridDiv.innerHTML = '';

    // Create grid options and instantiate
    gridOptions = createGridOptions();
    try {
        new agGrid.Grid(eGridDiv, gridOptions);
        console.log('AG Grid initialized successfully');
    } catch (err) {
        showGridError(err.message || 'Error initializing AG Grid');
        console.error('Error initializing AG Grid:', err);
    }
}

// ============================================================================
// DATA LOADING
// ============================================================================
function initializeDataLoad() {
    if (gridOptions && gridOptions.api && typeof gridOptions.api.showLoadingOverlay === 'function') {
        try { gridOptions.api.showLoadingOverlay(); }
        catch (e) { console.warn('showLoadingOverlay failed', e); }
    }

    fetch(DATA_URL)
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
            safeSetRowData(data);
        })
        .catch(err => {
            let errorMsg = err.message || String(err);
            if (err.name === 'TypeError' && errorMsg.includes('Failed to fetch')) {
                errorMsg = 'Unable to fetch data. This may be due to a network issue or a CORS restriction.';
            } else if (errorMsg.includes('Unexpected token')) {
                errorMsg = 'Format error: Data file is not valid JSON.';
            }
            safeSetRowData(FALLBACK_DATA);
            showStatusBanner(`Failed to load remote data: ${errorMsg}\nShowing sample data. Click Retry to attempt again.`);
            showGridError(errorMsg);
            console.error('Error loading data:', err);
        });
}

// ============================================================================
// DOM READY INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', function () {
    console.log('Initializing ZSUN Membership Grid...');

    // Initialize grid
    initializeGrid();

    // Wire up filter input
    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        filterInput.addEventListener('input', function () {
            if (gridOptions && gridOptions.api && typeof gridOptions.api.setQuickFilter === 'function') {
                gridOptions.api.setQuickFilter(this.value);
            }
        });
    }

    // Load data
    initializeDataLoad();

    console.log('Grid initialization complete');
});