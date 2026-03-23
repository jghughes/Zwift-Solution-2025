// ============================================================================
// ZRL 2026 ROUND 3 APP CONFIGURATION
// ============================================================================

const RACE_OPTIONS = [
    { label: "Stage 1 - points", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage1-leaderboard-club.json" },
    { label: "Stage 2 - TTR", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage2-leaderboard-club.json" },
    { label: "Stage 3 - points", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage3-leaderboard-club.json" },
    { label: "Stage 4 - points", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage4-leaderboard-club.json" },
    { label: "Stage 5 - iTT", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage5-leaderboard-club.json" },
    { label: "Stage 6 - points", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-stage6-leaderboard-club.json" },
    { label: "Yellow jersey", url: "https://customerzsun.blob.core.windows.net/dirt-results-consolidated/2026-yellow-jersey-club.json" },
];

const FALLBACK_DATA = [
    { row: 1, rider: "John Doe" }
];

const BASE_COLUMN_DEFS = [
    { headerName: "row", field: "row", pinned: 'left', type: 'numericColumn', width: 60 },
    { headerName: "Name", field: "rider", pinned: 'left', width: 150 },
    { headerName: "Zone", field: "time-zone" },
    { headerName: "Place", field: "place", type: 'numericColumn' },
    { headerName: "KOM-pts", field: "points-kom" },
    { headerName: "Sprint-pts", field: "points-sprint" },
    { headerName: "Fin-pts", field: "points-finish" },
    { headerName: "Total-pts", field: "points-total" },
    { headerName: "Time", field: "time" },
    { headerName: "League", field: "league", width: 150 },
    { headerName: "Team", field: "team", width: 150 },
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