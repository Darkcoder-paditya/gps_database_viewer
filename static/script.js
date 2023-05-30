function sortDataByTemperature() {
    
    var table = document.getElementById("data-table");
    var rows = Array.from(table.getElementsByTagName("tr"));

    rows.sort(function(a, b) {
        var aValue = parseFloat(a.cells[2].innerText);
        var bValue = parseFloat(b.cells[2].innerText);

        if (isNaN(aValue) || isNaN(bValue)) {
            return 0;
        }

        return aValue - bValue;
    });

    var tbody = table.querySelector("tbody");
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

function sortDataByLatitude() {
    var table = document.getElementById("data-table");
    var rows = Array.from(table.getElementsByTagName("tr"));

    rows.sort(function(a, b) {
        var aValue = parseFloat(a.cells[3].innerText);
        var bValue = parseFloat(b.cells[3].innerText);

        if (isNaN(aValue) || isNaN(bValue)) {
            return 0;
        }

        return aValue - bValue;
    });

    var tbody = table.querySelector("tbody");
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

function sortDataByLongitude() {
    var table = document.getElementById("data-table");
    var rows = Array.from(table.getElementsByTagName("tr"));

    rows.sort(function(a, b) {
        var aValue = parseFloat(a.cells[4].innerText);
        var bValue = parseFloat(b.cells[4].innerText);

        if (isNaN(aValue) || isNaN(bValue)) {
            return 0;
        }

        return aValue - bValue;
    });

    var tbody = table.querySelector("tbody");
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

function sortDataBySerialNumber() {
    var table = document.getElementById("data-table");
    var rows = Array.from(table.getElementsByTagName("tr"));

    rows.sort(function(a, b) {
        var aValue = parseInt(a.cells[0].innerText);
        var bValue = parseInt(b.cells[0].innerText);

        if (isNaN(aValue) || isNaN(bValue)) {
            return 0;
        }

        return aValue - bValue;
    });

    var tbody = table.querySelector("tbody");
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}
function deleteData() {
    if (confirm("Are you sure you want to delete all data?")) {
        // Send an AJAX request to the server to delete all data
        fetch("/delete", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ database: "gps_data", collection: "gps_messages" })
        })
        .then(response => {
            if (response.ok) {
                alert("All data deleted successfully!");
                location.reload(); // Refresh the page to reflect the changes
            } else {
                throw new Error("Failed to delete data. Please try again.");
            }
        })
        .catch(error => {
            alert(error.message);
        });
    }
}
// setInterval(function() {
//     location.reload();
// }, 5000);
// var autoRefreshInterval;
// var autoRefreshEnabled = false;

// function toggleAutoRefresh() {
//     autoRefreshEnabled = !autoRefreshEnabled;
//     if (autoRefreshEnabled) {
//         var interval = parseInt(document.getElementById("interval-input").value) || 0;
//         if (interval > 0) {
//             autoRefreshInterval = setInterval(function () {
//                 location.reload();
//             }, interval * 1000);
//         }
//     } else {
//         clearInterval(autoRefreshInterval);
//     }
// }