function searchTable() {
  let input = document.getElementById("searchInput").value.toLowerCase();
  let table = document.getElementById("salesTable");
  let rows = table.getElementsByTagName("tr");

  for (let i = 1; i < rows.length; i++) {  // Start from 1 to skip table headers
      let orderIDCell = rows[i].getElementsByTagName("td")[1]; // Order ID column

      if (orderIDCell) {
          let orderIDText = orderIDCell.textContent || orderIDCell.innerText;
          rows[i].style.display = orderIDText.toLowerCase().includes(input) ? "" : "none";
      }
  }
}
