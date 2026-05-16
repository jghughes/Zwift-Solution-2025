// ============================================================================
// MEMBERSHIP APP CONFIGURATION
// ============================================================================

const DATA_URL = "https://customerzsun.blob.core.windows.net/zsun/rider_compute_dto_as_list.json";

const FALLBACK_DATA = [
    { row: 1, name_racingapp: "Joe Soap" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "name", field: "name_racingapp", pinned: 'left', width: 150 },
    { headerName: "flag", field: "zwift_country_code3" },
    { headerName: "zFTP W", field: "velo_zwiftpower_zFTP_watts", type: 'numericColumn' },
    { headerName: "FTP W (curve)", field: "jgh_60_min_watts", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "0% kph (60min)", field: "jgh_60_min_kph_0pc_gradient", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "2% kph (60min)", field: "jgh_60_min_kph_2pc_gradient", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "4% kph (60min)", field: "jgh_60_min_kph_4pc_gradient", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "zRS", field: "zwift_racing_score", type: 'numericColumn' },
    { headerName: "vELO rating", field: "velo_rating_30_days", type: 'numericColumn' },
    { headerName: "vELO cat", field: "velo_cat_name_30_days" },
    { headerName: "vELO cat", field: "velo_cat_num_30_days", type: 'numericColumn' },
    { headerName: "age", field: "velo_age_group" },
    { headerName: "height (cm)", field: "zwift_height_cm", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "weight (kg)", field: "zwift_weight_kg", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "gender", field: "zwift_gender" },
    { headerName: "open", field: "zwift_cat_open" },
    { headerName: "women", field: "zwift_cat_women" },
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