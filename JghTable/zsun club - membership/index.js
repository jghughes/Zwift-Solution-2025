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
    { headerName: "height (cm)", field: "height_cm", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "weight (kg)", field: "weight_kg", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "zFTP (W/kg)", field: "zwift_zftp_wkg", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(2), },
    { headerName: "60min (W/kg)", field: "wkg_60min_curvefit", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "ZRS", field: "zwift_racing_score", type: 'numericColumn', width: 80 },
    { headerName: "open cat", field: "cat_open", cellStyle: { textAlign: 'center' }, width: 70 },
    { headerName: "women cat", field: "cat_women", cellStyle: { textAlign: 'center' }, width: 70 },
    { headerName: "ZR.app rating", field: "velo_cat_label", width: 130 },
    { headerName: "zwiftID", field: "zwift_id" },

    { headerName: "frontal area (m²)", field: "frontal_area_m2", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "segment length (km)", field: "single_segment_distance_km", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "predicted power (W)", field: "single_segment_watts", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "predicted power (W/kg)", field: "single_segment_wgk", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "predicted time (sec)", field: "single_segment_duration_sec", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "predicted time (HhMmSs)", field: "single_segment_duration_hh_mm_ss", width: 80 },
    { headerName: "route", field: "route_description", type: 'numericColumn', width: 150},
    { headerName: "route lead_in (km)", field: "route_lead_in_length_km", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "route length (km)", field: "route_length_km", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(1) },
    { headerName: "predicted power (W)", field: "route_power_output_watts", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "predicted power (W/kg)", field: "route_power_output_wkg", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(2) },
    { headerName: "predicted time (sec)", field: "route_fastest_achievable_time_sec", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toFixed(0) },
    { headerName: "predicted time (HhMmSs)", field: "route_fastest_achievable_time_hh_mm_ss", width: 80 },



    // { headerName: "km total", field: "total_distance_km", type: 'numericColumn', valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    // { headerName: "exp points", field: "total_experience_points", type: 'numericColumn', valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    // { headerName: "level", field: "level", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    // { headerName: "rider score", field: "target_experience_points", type: 'numericColumn', width: 90, valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
    // { headerName: "level 101+", field: "projected_accelerated_level", type: 'numericColumn', width: 80, valueFormatter: params => params.value?.toLocaleString('en-GB', { maximumFractionDigits: 0 }) },
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