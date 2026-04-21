// ============================================================================
// APP CONFIGURATION
// ============================================================================

const RACE_OPTIONS = [
    { label: "race 1", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r1-ZSUN.json" },
    { label: "race 2", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r2-ZSUN.json" },
    { label: "race 3", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r3-ZSUN.json" },
    { label: "race 4", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r4-ZSUN.json" },
    { label: "race 5", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r5-ZSUN.json" },
    { label: "race 6", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-r6-ZSUN.json" },
    { label: "series - time", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-yellow-jersey-ZSUN.json" },
    { label: "series - points", url: "https://customerzsun.blob.core.windows.net/wtrl-zrl/sr19-green-jersey-ZSUN.json" },
];

const FALLBACK_DATA = [
    { row: 1, route: "long", place: 99999, time: "00:00:00", "rider-name": "John Doe", "rider-flag": "USA", gender: "O", competition: "Open regular", league: "Cherry", division: "B1", "team-name": "Team A" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "Name", field: "rider-name", pinned: 'left', width: 150 },
    { headerName: "Flag", field: "rider-flag" },
    { headerName: "Place", field: "place", type: 'numericColumn' },
    { headerName: "Time", field: "time" },
    { headerName: "FAL", field: "rider-falrp" },
    { headerName: "FTS", field: "rider-ftsrp" },
    { headerName: "FIN", field: "rider-finrp" },
    { headerName: "BONUS", field: "rider-pbprp" },
    { headerName: "TOTAL", field: "rider-totrp" },
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
    // Populate the race selector dropdown
    const raceSelector = document.getElementById('raceSelector');
    RACE_OPTIONS.forEach((option, index) => {
        const opt = document.createElement('option');
        opt.value = option.url;
        opt.textContent = option.label;
        raceSelector.appendChild(opt);
    });
    // Default to first race
    raceSelector.value = RACE_OPTIONS[0].url;

    const gridManager = new ZsunGridFramework.GridManager({
        appName: 'ZRL 2026 Round 3',
        dataUrl: raceSelector.value,
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

    // Reload grid data when a different race is selected
    raceSelector.addEventListener('change', function () {
        gridManager.loadData(raceSelector.value);
    });
});