// URL of your JSON data on Azure Blob Storage
const DATA_URL = "https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json";

// Fallback sample data used when fetch fails
const FALLBACK_DATA = [
    { zwift_id: 999999, name_racingapp: "Joe Soap"}
];

// AG Grid column definitions with short headers, leftmost column pinned
const columnDefs = [
    { headerName: "Name", field: "full_name", pinned: 'left', sortable: true, resizable: true },
    //{ headerName: "zFTP (W/kg)", field: "zwift_zftp_wkg", sortable: true, resizable: true },
    //{ headerName: "W/kg 60min (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    { headerName: "Zwift", field: "zwift_cat_label", sortable: true, resizable: true },
    { headerName: "ZwiftRacingApp", field: "velo_cat_label", sortable: true, resizable: true },
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
    //{ headerName: "Velo Rating (30d)", field: "velo_rating_30_days", sortable: true, resizable: true },
    //{ headerName: "Velo # (30d)", field: "velo_cat_num_30_days", sortable: true, resizable: true },
    //{ headerName: "Velo Cat (30d)", field: "velo_cat_name_30_days", sortable: true, resizable: true },
    //{ headerName: "Age Group", field: "velo_age_group", sortable: true, resizable: true },
//    { headerName: "W/kg 60min (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
//    { headerName: "60min W (curve)", field: "w_60min_curvefit", sortable: true, resizable: true },
//    { headerName: "Wkg 5s", field: "wkg_05sec", sortable: true, resizable: true },
//    { headerName: "W 5s", field: "w_05sec", sortable: true, resizable: true },
//    { headerName: "Wkg 1min", field: "wkg_01min", sortable: true, resizable: true },
//    { headerName: "W 1min", field: "w_01min", sortable: true, resizable: true },
//    { headerName: "Timestamp", field: "timestamp", sortable: true, resizable: true }
];
// Clipboard + copyable cell renderer helpers

function copyTextToClipboard(text) {
    if (text == null) text = '';
    const str = String(text);
    // Modern async clipboard API (works on secure contexts)
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        navigator.clipboard.writeText(str).catch(() => {
            // fallback to execCommand if navigator.clipboard fails
            fallbackCopyExecCommand(str);
        });
        return;
    }
    // Fallback
    fallbackCopyExecCommand(str);
}

function fallbackCopyExecCommand(text) {
    try {
        const ta = document.createElement('textarea');
        ta.value = text;
        // Prevent page jump
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(ta);
        if (!ok) console.warn('execCommand copy returned false');
    } catch (e) {
        console.warn('fallbackCopyExecCommand failed', e);
    }
}

// Focusable cell renderer that supports Ctrl/C (Cmd/C) copy and double-click copy.
// Returns a DOM element (span).
function copyableCellRenderer(params) {
    const span = document.createElement('span');
    span.className = 'copyable-cell';
    span.tabIndex = 0; // focusable
    const text = params.value == null ? '' : String(params.value);
    span.textContent = text;

    // keyboard copy when element is focused (Ctrl/Cmd + C)
    span.addEventListener('keydown', (ev) => {
        // Do not interfere with other keys; handle both 'c' and 'C'
        if ((ev.ctrlKey || ev.metaKey) && (ev.key === 'c' || ev.key === 'C')) {
            ev.preventDefault();
            copyTextToClipboard(text);
            // Optional: brief visual feedback (flash)
            span.style.transition = 'background-color 150ms';
            const orig = span.style.backgroundColor;
            span.style.backgroundColor = '#e8f0fe';
            setTimeout(() => { span.style.backgroundColor = orig; }, 180);
        }
    });

    // double-click to copy
    span.addEventListener('dblclick', () => {
        copyTextToClipboard(text);
        span.style.transition = 'background-color 150ms';
        const orig = span.style.backgroundColor;
        span.style.backgroundColor = '#e8f0fe';
        setTimeout(() => { span.style.backgroundColor = orig; }, 180);
    });

    // tooltip helps users discover the behaviour
    span.title = 'Double-click to copy. Or focus and press Ctrl/C (Cmd/C on mac).';

    return span;
}

// AG Grid options
const gridOptions = {
    columnDefs: columnDefs,
    rowData: [], // Will be set after fetch
    defaultColDef: {
        sortable: true,
        resizable: true,
        filter: true,
        // Use the focusable, copyable renderer by default; explicit column renderers override this
        cellRenderer: copyableCellRenderer
    },
    // Enable range selection so users can select cells/ranges and press Ctrl/C to copy ranges
    enableRangeSelection: true,
    // Allow row selection (useful for other actions and copySelectedRows)
    rowSelection: 'multiple',
    pagination: true,
    paginationPageSize: 25
};

// Simple in-memory client-side log buffer for "View logs"
const _logBuffer = [];
(function captureConsole() {
    const orig = {
        log: console.log,
        warn: console.warn,
        error: console.error
    };
    function push(level, args) {
        const ts = new Date().toISOString();
        _logBuffer.push({
            ts, level, message: args.map(a => {
                try { return typeof a === 'string' ? a : JSON.stringify(a); } catch (e) { return String(a); }
            }).join(' ')
        });
        // keep buffer bounded
        if (_logBuffer.length > 200) _logBuffer.shift();
    }
    console.log = function () { push('log', Array.from(arguments)); orig.log.apply(console, arguments); };
    console.warn = function () { push('warn', Array.from(arguments)); orig.warn.apply(console, arguments); };
    console.error = function () { push('error', Array.from(arguments)); orig.error.apply(console, arguments); };
})();

// Helpers
function escapeHtml(str) {
    if (str == null) return '';
    str = String(str);
    return str.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

let _lastErrorMessage = null;

// Responsive column sizing helpers
function debounce(fn, wait) {
    let t;
    return function () {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, arguments), wait);
    };
}

// Auto-size all columns to content, then if total column width < grid width and screen is wide,
// call sizeColumnsToFit to stretch columns to fill the grid.
// Retries a few times if APIs are not yet attached.
function autoSizeAllColumns(attempt = 0) {
    if (!gridOptions.columnApi || typeof gridOptions.columnApi.autoSizeColumns !== 'function') {
        if (attempt < 10) {
            setTimeout(() => autoSizeAllColumns(attempt + 1), 100);
            return;
        }
        console.warn('columnApi not available for autoSizeAllColumns');
        return;
    }

    try {
        const allCols = gridOptions.columnApi.getAllColumns();
        if (!allCols || allCols.length === 0) return;

        const colIds = allCols.map(c => c.getColId());
        // auto-size to content (this measures cells and header)
        gridOptions.columnApi.autoSizeColumns(colIds, false);

        // small delay to allow widths to be updated in DOM
        setTimeout(() => {
            try {
                const gridDiv = document.getElementById('myGrid');
                const gridWidth = gridDiv ? gridDiv.clientWidth : (window.innerWidth || document.documentElement.clientWidth);
                const totalColsWidth = allCols.reduce((s, c) => s + (c.getActualWidth ? c.getActualWidth() : 0), 0);

                // If on wide screen and total content width is less than available grid width,
                // stretch columns to fit to avoid empty space
                const w = window.innerWidth || document.documentElement.clientWidth;
                if (w >= 900 && gridOptions.api && typeof gridOptions.api.sizeColumnsToFit === 'function' && totalColsWidth < gridWidth) {
                    gridOptions.api.sizeColumnsToFit();
                }
            } catch (e) {
                console.warn('post-autoSize sizing check failed', e);
            }
        }, 50);
    } catch (e) {
        console.warn('autoSizeAllColumns failed', e);
    }
}

function adjustColumnSizing() {
    if (!gridOptions.api) return;
    try {
        const w = window.innerWidth || document.documentElement.clientWidth;
        // On wide screens make columns fit the grid width (after possible autosize)
        if (w >= 900) {
            if (typeof gridOptions.api.sizeColumnsToFit === 'function') {
                gridOptions.api.sizeColumnsToFit();
            }
        } else {
            // On smaller screens we prefer content autosize (already applied) and allow horizontal scroll.
            // Do nothing here to avoid forcing fit and causing cramped columns.
        }
    } catch (e) {
        console.warn('adjustColumnSizing error', e);
    }
}

// Re-run sizing on window resize (debounced)
window.addEventListener('resize', debounce(adjustColumnSizing, 150));

// Non-destructive status banner shown above the document container with Retry
function showStatusBanner(message) {
    const container = document.querySelector('.document-container') || document.body;
    const existing = document.getElementById('gridStatusBanner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'gridStatusBanner';
    banner.style.background = '#fff4e5';
    banner.style.color = '#333';
    banner.style.padding = '10px 12px';
    banner.style.margin = '12px 0';
    banner.style.borderRadius = '6px';
    banner.style.display = 'flex';
    banner.style.alignItems = 'center';
    banner.style.boxShadow = '0 1px 4px rgba(0,0,0,0.04)';
    banner.innerHTML = `<div style="flex:1;white-space:pre-wrap;">${escapeHtml(message)}</div>
                        <button id="gridBannerRetry" style="margin-left:12px;background:#1976d2;color:#fff;border:none;padding:6px 10px;border-radius:4px;cursor:pointer;">Retry</button>`;
    if (container.firstElementChild) {
        container.insertBefore(banner, container.firstElementChild);
    } else {
        container.appendChild(banner);
    }

    const retry = document.getElementById('gridBannerRetry');
    if (retry && !retry.dataset.bound) {
        retry.dataset.bound = '1';
        retry.addEventListener('click', () => {
            const b = document.getElementById('gridStatusBanner');
            if (b) b.remove();
            initializeGrid();
        });
    }
}

// Show a rich error overlay (uses AG Grid overlay when available; falls back to DOM node)
function showGridError(message) {
    _lastErrorMessage = message;
    const safeMessage = escapeHtml(message);
    const template = `
        <div style="padding:16px;color:#b00020;background:#fff3f2;border-radius:6px;font-family:Segoe UI,Arial,sans-serif;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:15px">Error loading data</strong>
            </div>
            <div style="margin-top:8px;white-space:pre-wrap;color:#5a0010;">${safeMessage}</div>
            <div style="margin-top:12px;display:flex;gap:8px;">
                <button id="gridRetryBtn" style="background:#1976d2;color:#fff;border:none;padding:8px 10px;border-radius:4px;cursor:pointer;">Retry</button>
                <button id="gridViewLogsBtn" style="background:#eee;color:#222;border:none;padding:8px 10px;border-radius:4px;cursor:pointer;">View logs</button>
                <a id="gridHelpLink" href="#" style="margin-left:auto;color:#1976d2;text-decoration:underline;font-size:13px;">Help / Docs</a>
            </div>
        </div>
    `;
    gridOptions.overlayNoRowsTemplate = template;

    if (gridOptions.api && typeof gridOptions.api.showNoRowsOverlay === 'function') {
        try {
            gridOptions.api.showNoRowsOverlay();
            // bind buttons after overlay is rendered into DOM
            setTimeout(bindOverlayControls, 0);
            return;
        } catch (e) {
            console.warn('showNoRowsOverlay failed, falling back to DOM overlay.', e);
        }
    }

    // fallback DOM overlay (non-destructive)
    createFallbackOverlay(template);
}

function bindOverlayControls() {
    const retry = document.getElementById('gridRetryBtn');
    const viewLogs = document.getElementById('gridViewLogsBtn');
    const help = document.getElementById('gridHelpLink');

    if (retry && !retry.dataset.bound) {
        retry.dataset.bound = '1';
        retry.addEventListener('click', function (e) {
            hideGridError();
            initializeGrid();
        });
    }

    if (viewLogs && !viewLogs.dataset.bound) {
        viewLogs.dataset.bound = '1';
        viewLogs.addEventListener('click', function (e) {
            e.preventDefault();
            showLogsOverlay();
        });
    }

    if (help && !help.dataset.bound) {
        help.dataset.bound = '1';
        help.addEventListener('click', function (e) {
            e.preventDefault();
            // Replace with real docs URL if available
            window.open('https://github.com/jghughes/Zwift-Solution-2025', '_blank');
        });
    }
}

function createFallbackOverlay(html) {
    const gridDiv = document.getElementById('myGrid');
    if (!gridDiv) return;
    // remove existing fallback overlay if any
    const existing = document.getElementById('gridErrorOverlayCustom');
    if (existing) existing.parentNode.removeChild(existing);

    const container = document.createElement('div');
    container.id = 'gridErrorOverlayCustom';
    container.style.position = 'absolute';
    container.style.top = '8px';
    container.style.left = '8px';
    container.style.right = '8px';
    container.style.pointerEvents = 'auto';
    container.style.zIndex = '10';
    container.innerHTML = html;
    gridDiv.style.position = gridDiv.style.position || 'relative';
    gridDiv.appendChild(container);

    // bind fallback controls
    setTimeout(bindOverlayControls, 0);
}

function showLogsOverlay() {
    const logsHtml = _logBuffer.map(l => `${l.ts} [${l.level}] ${escapeHtml(l.message)}`).join('\n');
    const template = `
        <div style="padding:12px;background:#fff;border-radius:6px;max-height:300px;overflow:auto;font-family:monospace;font-size:12px;">
            <div style="display:flex;gap:8px;align-items:center;">
                <strong>Client logs</strong>
                <button id="gridBackBtn" style="margin-left:auto;background:#1976d2;color:#fff;border:none;padding:6px 8px;border-radius:4px;cursor:pointer;">Back</button>
                <button id="gridClearLogsBtn" style="background:#eee;color:#222;border:none;padding:6px 8px;border-radius:4px;cursor:pointer;">Clear</button>
            </div>
            <pre id="gridLogsContent" style="white-space:pre-wrap;margin-top:8px;">${escapeHtml(logsHtml || '(no logs yet)')}</pre>
        </div>
    `;
    gridOptions.overlayNoRowsTemplate = template;
    if (gridOptions.api && typeof gridOptions.api.showNoRowsOverlay === 'function') {
        try {
            gridOptions.api.showNoRowsOverlay();
            setTimeout(() => {
                const back = document.getElementById('gridBackBtn');
                const clear = document.getElementById('gridClearLogsBtn');
                if (back && !back.dataset.bound) {
                    back.dataset.bound = '1';
                    back.addEventListener('click', function () { showGridError(_lastErrorMessage || 'Error'); });
                }
                if (clear && !clear.dataset.bound) {
                    clear.dataset.bound = '1';
                    clear.addEventListener('click', function () {
                        _logBuffer.length = 0;
                        const content = document.getElementById('gridLogsContent');
                        if (content) content.textContent = '(no logs yet)';
                    });
                }
            }, 0);
            return;
        } catch (e) {
            console.warn('showNoRowsOverlay failed for logs overlay, falling back.', e);
        }
    }
    createFallbackOverlay(template);
}

function hideGridError() {
    // hide AG Grid overlay if available
    if (gridOptions.api) {
        if (typeof gridOptions.api.hideOverlay === 'function') {
            try { gridOptions.api.hideOverlay(); } catch (e) { console.warn('hideOverlay failed', e); }
        } else {
            // older API: hideNoRowsOverlay/hideLoadingOverlay
            try { if (gridOptions.api.hideNoRowsOverlay) gridOptions.api.hideNoRowsOverlay(); } catch (e) { /* ignore */ }
        }
    }
    // remove fallback overlay if present
    const existing = document.getElementById('gridErrorOverlayCustom');
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
}

// Safe helpers that guard against gridOptions.api being unavailable
function safeSetRowData(data, attempt = 0) {
    if (gridOptions.api && typeof gridOptions.api.setRowData === 'function') {
        gridOptions.api.setRowData(data);
        hideGridError();
        // After setting data, auto-size columns (safe for <1000 rows)
        setTimeout(() => {
            autoSizeAllColumns();
            // Then run adjust sizing so wide screens fill the width
            adjustColumnSizing();
        }, 50);
        return;
    }

    // Retry a few times in case API is not yet attached
    if (attempt < 10) {
        setTimeout(() => safeSetRowData(data, attempt + 1), 100);
        return;
    }

    // Final fallback: log and show unobtrusive message
    console.error('AG Grid API not available to set row data after multiple attempts.');
    showGridError('Unable to populate grid: internal API unavailable.');
}

function safeSetQuickFilter(value) {
    if (gridOptions.api && typeof gridOptions.api.setQuickFilter === 'function') {
        gridOptions.api.setQuickFilter(value);
    } else {
        console.warn('Quick filter ignored: AG Grid API not ready.');
    }
}

// Fetch data and initialize AG Grid
function initializeGrid() {

    // show loading overlay when starting
    if (gridOptions.api && typeof gridOptions.api.showLoadingOverlay === 'function') {
        try { gridOptions.api.showLoadingOverlay(); } catch (e) { console.warn('showLoadingOverlay failed', e); }
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
            // hide loading + set data
            safeSetRowData(data);
        })
        .catch(err => {
            let errorMsg = err.message;
            if (err.name === 'TypeError' && errorMsg.includes('Failed to fetch')) {
                errorMsg = 'Unable to fetch data. This may be due to a network issue or a CORS restriction.';
            } else if (errorMsg.includes('Unexpected token')) {
                errorMsg = 'Format error: Data file is not valid JSON.';
            }

            // Populate the grid with fallback sample data so the UI remains usable
            safeSetRowData(FALLBACK_DATA);

            // Non-destructive status banner advising the user
            showStatusBanner(`Failed to load remote data: ${errorMsg}\nShowing sample data. Click Retry to attempt again.`);

            // Also show the richer overlay to provide Retry / View logs options
            showGridError(errorMsg);

            console.error('Error loading data:', err);
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const eGridDiv = document.getElementById('myGrid');
    try {
        new agGrid.Grid(eGridDiv, gridOptions);
    } catch (err) {
        // Display error in the grid container using overlay UI
        showGridError(err.message || 'Error initializing AG Grid');
        console.error('Error initializing AG Grid:', err);
        return; // Prevent further execution if grid failed to initialize
    }

    // Quick filter integration
    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        filterInput.addEventListener('input', function () {
            safeSetQuickFilter(this.value);
        });
    }

    // Fetch and load data
    initializeGrid();
});