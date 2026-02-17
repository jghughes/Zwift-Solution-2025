// URL of your JSON data on Azure Blob Storage
const DATA_URL = "https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json";

// Fallback sample data used when fetch fails
const FALLBACK_DATA = [
    { zwift_id: 999999, name_racingapp: "Joe Soap" }
];

// --- Excel-like sizing presets (canonical, simple) ---
const PRESETS = {
    normal: {
        colWidth: 120,      // initial column pixel width
        rowHeight: 24,      // initial row height (px)
        headerHeight: 28
    },
    dense: {
        colWidth: 90,
        rowHeight: 18,
        headerHeight: 20
    }
};

// Base column definitions (no width assigned here; generated per preset)
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

// State holders
let _currentData = [];
let _lastErrorMessage = null;
let _isDense = false;
let gridOptions = null;

// Helpers
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function generateColumnDefsForPreset(preset) {
    const w = preset.colWidth;
    return BASE_COLUMN_DEFS.map(cd => {
        const cloned = Object.assign({}, cd);
        // set an initial width that can be overridden by autosize
        cloned.width = w;
        return cloned;
    });
}

// Clipboard helpers
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

// Focusable copyable cell renderer (uses CSS flash)
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
        } catch (e) { /* ignore */ }
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

    span.title = 'Double-click to copy. Or focus and press Ctrl/C (Cmd/C on mac).';
    return span;
}

// Create grid options for a preset
function createGridOptions(preset) {
    return {
        columnDefs: generateColumnDefsForPreset(preset),
        rowData: [], // set after initialization
        rowHeight: preset.rowHeight,
        headerHeight: preset.headerHeight,
        defaultColDef: {
            sortable: true,
            resizable: true,
            filter: true,
            cellRenderer: copyableCellRenderer,
            minWidth: 40
        },
        enableRangeSelection: true,
        rowSelection: 'multiple',
        pagination: true,
        paginationPageSize: 25,
        overlayNoRowsTemplate: '', // set dynamically when needed
    };
}

// Safe set row data that preserves last loaded dataset
function safeSetRowData(data) {
    _currentData = Array.isArray(data) ? data : [];
    if (gridOptions && gridOptions.api && typeof gridOptions.api.setRowData === 'function') {
        gridOptions.api.setRowData(_currentData);
        // After setting data, auto-size and adjust
        setTimeout(() => {
            autoSizeAllColumns();
            adjustColumnSizing();
        }, 50);
    } else {
        console.warn('AG Grid API not ready for setRowData');
    }
}

// Autosize helper (keeps existing behaviour)
function autoSizeAllColumns(attempt = 0) {
    if (!gridOptions || !gridOptions.columnApi || typeof gridOptions.columnApi.autoSizeColumns !== 'function') {
        if (attempt < 8) {
            setTimeout(() => autoSizeAllColumns(attempt + 1), 120);
            return;
        }
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
                const totalColsWidth = allCols.reduce((s, c) => s + (c.getActualWidth ? c.getActualWidth() : 0), 0);
                const w = window.innerWidth || document.documentElement.clientWidth;
                if (w >= 900 && gridOptions.api && typeof gridOptions.api.sizeColumnsToFit === 'function' && totalColsWidth < gridWidth) {
                    gridOptions.api.sizeColumnsToFit();
                }
            } catch (e) { console.warn('post-autoSize check failed', e); }
        }, 50);
    } catch (e) {
        console.warn('autoSizeAllColumns failed', e);
    }
}

function adjustColumnSizing() {
    if (!gridOptions || !gridOptions.api) return;
    try {
        const w = window.innerWidth || document.documentElement.clientWidth;
        if (w >= 900 && typeof gridOptions.api.sizeColumnsToFit === 'function') {
            gridOptions.api.sizeColumnsToFit();
        }
    } catch (e) {
        console.warn('adjustColumnSizing error', e);
    }
}

// Update the density toggle button UI (text + ARIA)
function updateDensityToggleButton() {
    const btn = document.getElementById('toggleDensity');
    if (!btn) return;
    // Show the current state on the button ("Dense" or "Normal")
    btn.textContent = _isDense ? 'Dense' : 'Normal';
    btn.setAttribute('aria-pressed', _isDense ? 'true' : 'false');
    // Helpful title explaining the action
    btn.title = _isDense ? 'Currently dense spacing — click to switch to normal' : 'Currently normal spacing — click to switch to dense';
}

// Overlay, banner, logs functions remain similar but simplified for brevity
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
            initializeGrid(_isDense);
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
        try { gridOptions.api.showNoRowsOverlay(); setTimeout(bindOverlayControls, 0); return; } catch (e) { /* fallback */ }
    }
    createFallbackOverlay(template);
}

function bindOverlayControls() {
    const retry = document.getElementById('gridRetryBtn');
    const viewLogs = document.getElementById('gridViewLogsBtn');
    const help = document.getElementById('gridHelpLink');
    if (retry && !retry.dataset.bound) { retry.dataset.bound = '1'; retry.addEventListener('click', () => { hideGridError(); initializeGrid(_isDense); }); }
    if (viewLogs && !viewLogs.dataset.bound) { viewLogs.dataset.bound = '1'; viewLogs.addEventListener('click', (e) => { e.preventDefault(); showLogsOverlay(); }); }
    if (help && !help.dataset.bound) { help.dataset.bound = '1'; help.addEventListener('click', (e) => { e.preventDefault(); window.open('https://github.com/jghughes/Zwift-Solution-2025', '_blank'); }); }
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
                if (back && !back.dataset.bound) { back.dataset.bound = '1'; back.addEventListener('click', () => showGridError(_lastErrorMessage || 'Error')); }
                if (clear && !clear.dataset.bound) { clear.dataset.bound = '1'; clear.addEventListener('click', () => { _logBuffer.length = 0; const c = document.getElementById('gridLogsContent'); if (c) c.textContent = '(no logs yet)'; }); }
            }, 0);
            return;
        } catch (e) { /* fallback */ }
    }
    createFallbackOverlay(template);
}

function hideGridError() {
    if (gridOptions && gridOptions.api) {
        if (typeof gridOptions.api.hideOverlay === 'function') {
            try { gridOptions.api.hideOverlay(); } catch (e) { /* ignore */ }
        } else {
            try { if (gridOptions.api.hideNoRowsOverlay) gridOptions.api.hideNoRowsOverlay(); } catch (e) { /* ignore */ }
        }
    }
    const existing = document.getElementById('gridErrorOverlayCustom');
    if (existing && existing.parentNode) existing.parentNode.removeChild(existing);
}

// preserve console logs
const _logBuffer = [];
(function captureConsole() {
    const orig = { log: console.log, warn: console.warn, error: console.error };
    function push(level, args) {
        const ts = new Date().toISOString();
        _logBuffer.push({ ts, level, message: args.map(a => { try { return typeof a === 'string' ? a : JSON.stringify(a); } catch (e) { return String(a); } }).join(' ') });
        if (_logBuffer.length > 200) _logBuffer.shift();
    }
    console.log = function () { push('log', Array.from(arguments)); orig.log.apply(console, arguments); };
    console.warn = function () { push('warn', Array.from(arguments)); orig.warn.apply(console, arguments); };
    console.error = function () { push('error', Array.from(arguments)); orig.error.apply(console, arguments); };
})();

// escape helper
function escapeHtml(str) {
    if (str == null) return '';
    str = String(str);
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// Initialize or re-initialize the grid with the selected preset
function initializeGrid(useDense) {
    _isDense = !!useDense;
    const preset = _isDense ? PRESETS.dense : PRESETS.normal;
    const eGridDiv = document.getElementById('myGrid');

    // preserve column state and sorting if possible
    let prevColState = null;
    let prevSortModel = null;
    if (gridOptions && gridOptions.api && gridOptions.columnApi) {
        try {
            prevColState = gridOptions.columnApi.getColumnState();
            prevSortModel = gridOptions.api.getSortModel();
            // preserve scroll position? (left as-is)
            gridOptions.api.destroy();
        } catch (e) {
            console.warn('Error preserving grid state', e);
        }
    }

    // update host class for dense visual styles
    if (eGridDiv) {
        if (_isDense) eGridDiv.classList.add('dense'); else eGridDiv.classList.remove('dense');
    }

    // Update button text immediately
    updateDensityToggleButton();

    // create new options and instantiate
    gridOptions = createGridOptions(preset);
    try {
        new agGrid.Grid(eGridDiv, gridOptions);
    } catch (err) {
        showGridError(err.message || 'Error initializing AG Grid');
        console.error('Error initializing AG Grid:', err);
        return;
    }

    // restore column state and sort model if available (apply after grid is ready)
    setTimeout(() => {
        try {
            if (prevColState && gridOptions.columnApi && typeof gridOptions.columnApi.applyColumnState === 'function') {
                gridOptions.columnApi.applyColumnState({ state: prevColState, applyOrder: true });
            }
            if (prevSortModel && gridOptions.api && typeof gridOptions.api.setSortModel === 'function') {
                gridOptions.api.setSortModel(prevSortModel);
            }
            // if data already loaded, repopulate
            if (_currentData && _currentData.length > 0) {
                safeSetRowData(_currentData);
            }
            // Update button text again after re-init/restore
            updateDensityToggleButton();
        } catch (e) {
            console.warn('Restore state failed', e);
        }
    }, 50);
}

// Toggle density handler
function toggleDensity() {
    initializeGrid(!_isDense);
}

// Fetch and load data (unchanged behaviour)
function initializeDataLoad() {
    if (gridOptions && gridOptions.api && typeof gridOptions.api.showLoadingOverlay === 'function') {
        try { gridOptions.api.showLoadingOverlay(); } catch (e) { /* ignore */ }
    }
    fetch(DATA_URL)
        .then(response => {
            if (!response.ok) {
                let message = '';
                switch (response.status) {
                    case 401:
                    case 403: message = 'Authorization error: You do not have permission to access this data.'; break;
                    case 404: message = 'File not found: The requested data file does not exist.'; break;
                    case 500: message = 'Server error: There was a problem with the server.'; break;
                    default: message = `HTTP error: ${response.status} ${response.statusText}`;
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

// DOM ready: create grid, wire up filter and toggle
document.addEventListener('DOMContentLoaded', function () {
    // initialize with normal preset
    initializeGrid(false);

    // wire filter
    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        filterInput.addEventListener('input', function () {
            if (gridOptions && gridOptions.api && typeof gridOptions.api.setQuickFilter === 'function') {
                gridOptions.api.setQuickFilter(this.value);
            }
        });
    }

    // density toggle button
    const toggleBtn = document.getElementById('toggleDensity');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            toggleDensity();
        });
        // ensure button reflects initial state
        updateDensityToggleButton();
    }

    // load data
    initializeDataLoad();
});