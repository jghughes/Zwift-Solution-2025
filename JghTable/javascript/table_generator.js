// URL of your JSON data on Azure Blob Storage
const DATA_URL = "https://customerzsun.blob.core.windows.net/preprocessed/rider_brute_dto_as_list.json";

let allRiders = [];
let filteredRiders = [];
let currentPage = 1;
const pageSize = 25; // Adjust as needed

// Utility: Detect if value is numeric
function isNumeric(val) {
    return typeof val === 'number' || (!isNaN(val) && val !== '' && !isNaN(parseFloat(val)));
}

// Generate the table header and rows
function generateTable(data, tableId) {
    const table = document.getElementById(tableId);
    table.innerHTML = '';
    if (!data.length) return;

    // Header
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    const thead = document.createElement('thead');
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Rows
    const tbody = document.createElement('tbody');
    data.forEach(obj => {
        const row = document.createElement('tr');
        Object.values(obj).forEach(val => {
            const td = document.createElement('td');
            td.textContent = val;
            if (isNumeric(val)) td.classList.add('num');
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
}

// Get the data for the current page
function getPageData(data, page, pageSize) {
    const start = (page - 1) * pageSize;
    return data.slice(start, start + pageSize);
}

// Render pagination controls
function renderPagination(totalRows, pageSize, currentPage) {
    const totalPages = Math.ceil(totalRows / pageSize);
    const paginationDiv = document.getElementById('pagination');
    paginationDiv.innerHTML = '';

    if (totalPages <= 1) return;

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
        }
    };
    paginationDiv.appendChild(prevBtn);

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.disabled = i === currentPage;
        pageBtn.onclick = () => {
            currentPage = i;
            renderTable();
        };
        paginationDiv.appendChild(pageBtn);
    }

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
        }
    };
    paginationDiv.appendChild(nextBtn);
}

// Render the table and pagination
function renderTable() {
    const pageData = getPageData(filteredRiders, currentPage, pageSize);
    generateTable(pageData, 'riders-table');
    renderPagination(filteredRiders.length, pageSize, currentPage);
}

// Filter the table data
function filterTable(data, searchTerm) {
    if (!searchTerm) return data;
    return data.filter(row =>
        Object.values(row).some(val =>
            String(val).toLowerCase().includes(searchTerm.toLowerCase())
        )
    );
}

// Load data and initialize
fetch(DATA_URL)
    .then(response => response.json())
    .then(data => {
        allRiders = data;
        filteredRiders = allRiders;
        renderTable();
    })
    .catch(err => {
        document.getElementById('riders-table').innerHTML = '<tr><td colspan="100%">Failed to load data.</td></tr>';
        console.error('Error loading data:', err);
    });

// Filter input event
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('filterInput').addEventListener('input', function () {
        filteredRiders = filterTable(allRiders, this.value);
        currentPage = 1;
        renderTable();
    });
});
