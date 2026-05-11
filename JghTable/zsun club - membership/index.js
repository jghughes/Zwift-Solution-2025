// ============================================================================
// MEMBERSHIP APP CONFIGURATION
// ============================================================================

const DATA_URL = "https://customerzsun.blob.core.windows.net/zsun/rider_stats_dto_as_list.json";

const FALLBACK_DATA = [
    { row: 1, full_name: "Joe Soap" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 70 },
    { headerName: "name", field: "full_name", pinned: 'left', width: 150 },
    { headerName: "flag", field: "zwift_country_code3", width: 80 },
    { headerName: "zFTP", field: "zwift_zftp_wkg", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(1), width: 80 },
    { headerName: "60min", field: "wkg_60min_curvefit", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(1), width: 80 },
    { headerName: "zRS", field: "zwift_racing_score", type: 'numericColumn', width: 80 },
    { headerName: "open", field: "cat_open", cellStyle: { textAlign: 'center' }, width: 70 },
    { headerName: "women", field: "cat_women", cellStyle: { textAlign: 'center' }, width: 70 },
    { headerName: "km total", field: "total_distance_km", type: 'numericColumn', valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    { headerName: "exp pts", field: "total_experience_points", type: 'numericColumn', valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    { headerName: "level", field: "level", type: 'numericColumn', width: 80 },
    { headerName: "101+ level", field: "level_accelerated", type: 'numericColumn', width: 80 },
    { headerName: "ZRA rating", field: "velo_cat_label", width: 130 },
    { headerName: "zwiftID", field: "zwift_id" },
];
// ============================================================================
// INITIALIZE GRID USING SHARED FRAMEWORK
// ============================================================================
document.addEventListener('DOMContentLoaded', function () {
    const gridManager = new ZsunGridFramework.GridManager({
        appName: 'ZSUN Membership',
        dataUrl: DATA_URL,
        fallbackData: FALLBACK_DATA,
        baseColumnDefs: BASE_COLUMN_DEFS,
        rowHeight: 25,
        headerHeight: 32,
        defaultColWidth: 90,
        sortable: true,
        resizable: true,
        filterable: true,
        minWidth: 40
    });

    gridManager.initialize();
});