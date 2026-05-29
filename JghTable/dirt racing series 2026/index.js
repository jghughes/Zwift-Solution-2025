// ============================================================================
// CONFIGURATION
// ============================================================================
const RACE_OPTIONS = [
    { label: "stage 1 - points - Peaky Pave", url: "https://customerzsun.blob.core.windows.net/dirt/12-s1-ZSUN.json" },
    { label: "stage 2 - TTR - ZG25 Queen", url: "https://customerzsun.blob.core.windows.net/dirt/12-s2-ZSUN.json" },
    { label: "stage 3 - points - Coast Crusher", url: "https://customerzsun.blob.core.windows.net/dirt/12-s3-ZSUN.json" },
    { label: "stage 4 - points - Temples and Towers", url: "https://customerzsun.blob.core.windows.net/dirt/12-s4-ZSUN.json" },
    { label: "stage 5 - points - Downtown Dolphins", url: "https://customerzsun.blob.core.windows.net/dirt/12-s5-ZSUN.json" },
    { label: "stage 6 - iTT - Harrowgate Circuit Reverse", url: "https://customerzsun.blob.core.windows.net/dirt/12-s6-ZSUN.json" },
    { label: "Series - totals", url: "https://customerzsun.blob.core.windows.net/dirt/12-series-ZSUN.json" },
];

const FALLBACK_DATA = [
    { finishingPlacePoints: 0, rider: "John Doe" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "Place (by Pts)", field: "finishingPlacePoints", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "Name", field: "rider", pinned: 'left', width: 150 },
    { headerName: "Team", field: "team", width: 150 },
    { headerName: "Zone", field: "timeZone" },
    { headerName: "KOM-pts", field: "pointsKom", type: 'numericColumn' },
    { headerName: "Sprint-pts", field: "pointsSprint", type: 'numericColumn' },
    { headerName: "Finish-pts", field: "pointsFinish", type: 'numericColumn' },
    { headerName: "Total-pts", field: "pointsTotal", type: 'numericColumn' },
    { headerName: "Time", field: "finishTimeHHMMSS" },
    { headerName: "Place (by Time)", field: "finishingPlaceTime", type: 'numericColumn', width: 60 },
    { headerName: "League", field: "league", width: 150 },
    { headerName: "ZwiftID", field: "zwiftId"},
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