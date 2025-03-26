document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");

  searchInput.addEventListener("keyup", function () {
      let filter = searchInput.value.toLowerCase();
      let tableRows = document.querySelectorAll("tbody tr");

      tableRows.forEach(row => {
          let orderId = row.cells[0].textContent.toLowerCase(); // Order ID column
          let date = row.cells[4].textContent.toLowerCase(); // Date column

          if (orderId.includes(filter) || date.includes(filter)) {
              row.style.display = "";
          } else {
              row.style.display = "none";
          }
      });
  });
});

