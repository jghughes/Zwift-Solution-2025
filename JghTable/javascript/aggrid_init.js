// URL of your JSON data on Azure Blob Storage
const DATA_URL = "https://customerzsun.blob.core.windows.net/preprocessed/rider_brute_dto_as_list.json";

// AG Grid column definitions with short headers, leftmost column pinned
const columnDefs = [
    { headerName: "ID", field: "zwift_id", pinned: 'left', sortable: true, resizable: true },
    { headerName: "Name", field: "name_racingapp", sortable: true, resizable: true },
    { headerName: "Country", field: "zwift_country_code3", sortable: true, resizable: true },
    { headerName: "Age", field: "zwift_age_years", sortable: true, resizable: true },
    { headerName: "Height (cm)", field: "zwift_height_cm", sortable: true, resizable: true },
    { headerName: "Weight (kg)", field: "zwift_weight_kg", sortable: true, resizable: true },
    { headerName: "Gender", field: "zwift_gender", sortable: true, resizable: true },
    { headerName: "Cat (Open)", field: "zwift_cat_open", sortable: true, resizable: true },
    { headerName: "Cat (Women)", field: "zwift_cat_women", sortable: true, resizable: true },
    { headerName: "Race Score", field: "zwift_racing_score", sortable: true, resizable: true },
    { headerName: "FTP (W)", field: "zwift_FTP_watts", sortable: true, resizable: true },
    { headerName: "zFTP (W)", field: "velo_zwiftpower_zFTP_watts", sortable: true, resizable: true },
    { headerName: "Cat (30d)", field: "velo_cat_num_30_days", sortable: true, resizable: true },
    { headerName: "Rating (30d)", field: "velo_rating_30_days", sortable: true, resizable: true },
    { headerName: "Cat Name (30d)", field: "velo_cat_name_30_days", sortable: true, resizable: true },
    { headerName: "Age Group", field: "velo_age_group", sortable: true, resizable: true },
    { headerName: "60min W", field: "jgh_60_min_watts", sortable: true, resizable: true },
    { headerName: "60min Curve A", field: "jgh_60_min_curve_coefficient", sortable: true, resizable: true },
    { headerName: "60min Curve B", field: "jgh_60_min_curve_exponent", sortable: true, resizable: true },
    { headerName: "TTT Pull A", field: "jgh_ttt_pull_curve_coefficient", sortable: true, resizable: true },
    { headerName: "TTT Pull B", field: "jgh_ttt_pull_curve_exponent", sortable: true, resizable: true },
    { headerName: "TTT R²", field: "jgh_ttt_pull_curve_fit_r_squared", sortable: true, resizable: true },
    { headerName: "Curves Fitted", field: "jgh_when_curves_fitted", sortable: true, resizable: true }
];

// AG Grid options
const gridOptions = {
    columnDefs: columnDefs,
    rowData: [], // Will be set after fetch
    defaultColDef: {
        sortable: true,
        resizable: true,
        filter: true
    },
    pagination: true,
    paginationPageSize: 25
};

// Fetch data and initialize AG Grid
function initializeGrid() {
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
            gridOptions.api.setRowData(data);
        })
        .catch(err => {
            let errorMsg = err.message;
            if (err.name === 'TypeError' && errorMsg.includes('Failed to fetch')) {
                errorMsg = 'Unable to fetch data. This may be due to a network issue. Please check your connection. If your connection is OK, this may be due to a CORS policy restriction. The site might not be configured to allow cross-origin requests.';
            } else if (errorMsg.includes('Unexpected token')) {
                errorMsg = 'Format error: Data file is not valid JSON.';
            }
            // Display error in the grid container
            const gridDiv = document.getElementById('myGrid');
            gridDiv.innerHTML = `<div style="color: red; padding: 16px;">${errorMsg}</div>`;
            console.error('Error loading data:', err);
        });
}

// Initialize AG Grid and filter after DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    const eGridDiv = document.getElementById('myGrid');
    new agGrid.Grid(eGridDiv, gridOptions);

    // Quick filter integration
    const filterInput = document.getElementById('filterInput');
    if (filterInput) {
        filterInput.addEventListener('input', function () {
            gridOptions.api.setQuickFilter(this.value);
        });
    }

    // Fetch and load data
    initializeGrid();
});