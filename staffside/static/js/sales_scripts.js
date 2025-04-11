function filterTable() {
    let searchInput = document.getElementById("searchInput").value.trim().toLowerCase();
    let tableRows = document.querySelectorAll("tbody tr");

    tableRows.forEach(row => {
        let orderId = row.cells[0].textContent.replace("#", "").trim().toLowerCase(); // Remove #

        if (searchInput === "" || orderId.includes(searchInput)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// 🔹 Make Search Work Automatically (When Typing)
document.getElementById("searchInput").addEventListener("input", filterTable);
