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
    ROW_HEIGHT: 25,
    HEADER_HEIGHT: 32,
    DEFAULT_COL_WIDTH: 80
};

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', sortable: true, resizable: true, type: 'numericColumn', width: 60 },
    { headerName: "name", field: "full_name", pinned: 'left', sortable: true, resizable: true, width: 150 },
    { headerName: "flag", field: "zwift_country_code3", sortable: true, resizable: true },
    { headerName: "zFTP", field: "zwift_zftp_wkg", sortable: true, resizable: true, type: 'numericColumn', valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "60min", field: "wkg_60min_curvefit", sortable: true, resizable: true, type: 'numericColumn', valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "zRS", field: "zwift_racing_score", sortable: true, resizable: true, type: 'numericColumn' },
    { headerName: "open", field: "cat_open", sortable: true, resizable: true },
    { headerName: "women", field: "cat_women", sortable: true, resizable: true },
    { headerName: "vELO", field: "velo_cat_label", sortable: true, resizable: true, width: 150 },
    { headerName: "zwiftID", field: "zwift_id", sortable: true, resizable: true },
    //{ headerName: "country", field: "zwift_country_code3", sortable: true, resizable: true },
    //{ headerName: "age", field: "age_years", sortable: true, resizable: true },
    //{ headerName: "height (cm)", field: "height_cm", sortable: true, resizable: true },
    //{ headerName: "weight (kg)", field: "weight_kg", sortable: true, resizable: true },
    //{ headerName: "gender", field: "gender_code", sortable: true, resizable: true },
    //{ headerName: "cat (open)", field: "cat_open", sortable: true, resizable: true },
    //{ headerName: "cat (women)", field: "cat_women", sortable: true, resizable: true },
    //{ headerName: "zRS", field: "zwift_racing_score", sortable: true, resizable: true },
    //{ headerName: "FTP (W)", field: "zwift_ftp_w", sortable: true, resizable: true },
    //{ headerName: "zFTP (W)", field: "zwift_zftp_w", sortable: true, resizable: true },
    //{ headerName: "zFTP (W/kg)", field: "zwift_zftp_wkg", sortable: true, resizable: true },
    //{ headerName: "zwift", field: "zwift_cat_label", sortable: true, resizable: true },
    //{ headerName: "velo rating (30d)", field: "velo_rating_30_days", sortable: true, resizable: true },
    //{ headerName: "velo # (30d)", field: "velo_cat_num_30_days", sortable: true, resizable: true },
    //{ headerName: "velo cat (30d)", field: "velo_cat_name_30_days", sortable: true, resizable: true },
    //{ headerName: "age group", field: "velo_age_group", sortable: true, resizable: true },
    //{ headerName: "w/kg 60min (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    //{ headerName: "60min W (curve)", field: "wkg_60min_curvefit", sortable: true, resizable: true },
    //{ headerName: "Wkg 5s", field: "wkg_05sec", sortable: true, resizable: true },
    //{ headerName: "W 5s", field: "w_05sec", sortable: true, resizable: true },
    //{ headerName: "Wkg 1min", field: "wkg_01min", sortable: true, resizable: true },
    //{ headerName: "W 1min", field: "w_01min", sortable: true, resizable: true },
    //{ headerName: "timestamp", field: "timestamp", sortable: true, resizable: true }
];

// ============================================================================
// STATE
// ============================================================================
let _currentData = [];
let _lastErrorMessage = null;
let gridOptions = null;

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
        if (!cloned.width) {
            cloned.width = CONFIG.DEFAULT_COL_WIDTH;
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
    const text = params.value == null ? '' : String(params.value);
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
    if (gridOptions?.api?.setRowData) {
        gridOptions.api.setRowData(_currentData);
        autoSizeColumns();
    } else {
        console.warn('AG Grid API not ready for setRowData');
    }
}

function autoSizeColumns() {
    if (!gridOptions?.columnApi?.autoSizeColumns) return;

    try {
        const allCols = gridOptions.columnApi.getAllColumns();
        if (!allCols || allCols.length === 0) return;

        const colIds = allCols.map(c => c.getColId());
        gridOptions.columnApi.autoSizeColumns(colIds, false);
    } catch (e) {
        console.warn('Column autosize failed', e);
    }
}

// ============================================================================
// ERROR HANDLING
// ============================================================================
function showGridError(message) {
    _lastErrorMessage = message;
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

    if (gridOptions) gridOptions.overlayNoRowsTemplate = template;
    if (gridOptions?.api?.showNoRowsOverlay) {
        gridOptions.api.showNoRowsOverlay();
        setTimeout(() => {
            const retry = document.getElementById('gridRetryBtn');
            if (retry && !retry.dataset.bound) {
                retry.dataset.bound = '1';
                retry.addEventListener('click', () => {
                    hideGridError();
                    initializeDataLoad();
                });
            }
        }, 0);
    }
}

function hideGridError() {
    if (gridOptions?.api?.hideOverlay) {
        try { gridOptions.api.hideOverlay(); }
        catch (e) { console.warn('hideOverlay failed', e); }
    }
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

    eGridDiv.innerHTML = '';
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
    if (gridOptions?.api?.showLoadingOverlay) {
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
            showGridError(errorMsg);
            console.error('Error loading data:', err);
        });
}

// ============================================================================
// DOM READY INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', function () {
    console.log('Initializing ZSUN Membership Grid...');

    initializeGrid();

    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        filterInput.addEventListener('input', function () {
            if (gridOptions?.api?.setQuickFilter) {
                gridOptions.api.setQuickFilter(this.value);
            }
        });
    }

    initializeDataLoad();
    console.log('Grid initialization complete');
});