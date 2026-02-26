// ============================================================================
// OLYMPICS APP CONFIGURATION
// ============================================================================

const DATA_URL = "https://customerzsun.blob.core.windows.net/wtrl-zrl-results-consolidated/18-6-club-leaderboard.json";

const FALLBACK_DATA = [
    { row: 1, route: "long", place: 99999, time: "00:00:00", "rider-name": "John Doe", "rider-flag": "USA", gender: "O", competition: "Open regular", league: "Cherry", division: "B1", "team-name": "Team A" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "Name", field: "rider-name", pinned: 'left', width: 150 },
    { headerName: "Flag", field: "rider-flag" },
    { headerName: "Place", field: "place", type: 'numericColumn' },
    { headerName: "Time", field: "time" },
    { headerName: "Points", field: "rider-totrp" },
    { headerName: "Route", field: "route" },
    { headerName: "Gender", field: "gender" },
    { headerName: "Competition", field: "competition", width: 150 },
    { headerName: "League", field: "league" },
    { headerName: "Div", field: "division" },
    { headerName: "Team", field: "team-name", width: 150 },
];

// ============================================================================
// INITIALIZE GRID USING SHARED FRAMEWORK
// ============================================================================
document.addEventListener('DOMContentLoaded', function () {
    const gridManager = new ZsunGridFramework.GridManager({
        appName: 'ZSUN Olympics',
        dataUrl: DATA_URL,
        fallbackData: FALLBACK_DATA,
        baseColumnDefs: BASE_COLUMN_DEFS,
        rowHeight: 25,
        headerHeight: 32,
        defaultColWidth: 80,
        sortable: true,
        resizable: true,
        filterable: true,
        minWidth: 40
    });

    gridManager.initialize();
});