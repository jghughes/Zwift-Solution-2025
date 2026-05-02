// ============================================================================
// MEMBERSHIP APP CONFIGURATION
// ============================================================================

const DATA_URL = "https://customerzsun.blob.core.windows.net/zsun/rider_stats_dto_as_list.json";

const FALLBACK_DATA = [
    { row: 1, full_name: "Joe Soap" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "name", field: "full_name", pinned: 'left', width: 150 },
    { headerName: "flag", field: "zwift_country_code3" },
    { headerName: "zFTP", field: "zwift_zftp_wkg", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "60min", field: "wkg_60min_curvefit", type: 'numericColumn', valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "zRS", field: "zwift_racing_score", type: 'numericColumn' },
    { headerName: "open", field: "cat_open" },
    { headerName: "women", field: "cat_women" },
    { headerName: "vELO", field: "velo_cat_label", width: 150 },
    { headerName: "level", field: "achievement_level" },
    { headerName: "zwiftID", field: "zwift_id" },
    //{ headerName: "country", field: "zwift_country_code3" },
    //{ headerName: "age", field: "age_years" },
    //{ headerName: "height (cm)", field: "height_cm" },
    //{ headerName: "weight (kg)", field: "weight_kg" },
    //{ headerName: "gender", field: "gender_code" },
    //{ headerName: "cat (open)", field: "cat_open" },
    //{ headerName: "cat (women)", field: "cat_women" },
    //{ headerName: "zRS", field: "zwift_racing_score" },
    //{ headerName: "FTP (W)", field: "zwift_ftp_w" },
    //{ headerName: "zFTP (W)", field: "zwift_zftp_w" },
    //{ headerName: "zFTP (W/kg)", field: "zwift_zftp_wkg" },
    //{ headerName: "zwift", field: "zwift_cat_label" },
    //{ headerName: "velo rating (30d)", field: "velo_rating_30_days" },
    //{ headerName: "velo # (30d)", field: "velo_cat_num_30_days" },
    //{ headerName: "velo cat (30d)", field: "velo_cat_name_30_days" },
    //{ headerName: "age group", field: "velo_age_group" },
    //{ headerName: "w/kg 60min (curve)", field: "wkg_60min_curvefit" },
    //{ headerName: "60min W (curve)", field: "wkg_60min_curvefit" },
    //{ headerName: "Wkg 5s", field: "wkg_05sec" },
    //{ headerName: "W 5s", field: "w_05sec" },
    //{ headerName: "Wkg 1min", field: "wkg_01min" },
    //{ headerName: "W 1min", field: "w_01min" },
    //{ headerName: "timestamp", field: "timestamp" }
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