function toggleSearch() {
  const container = document.getElementById('searchContainer');
  container.classList.toggle('active');
}

  // Your existing search function remains the same
  function searchTable() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let table = document.getElementById("salesTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
      let orderIDCell = rows[i].getElementsByTagName("td")[1];
      if (orderIDCell) {
        let orderIDText = orderIDCell.textContent || orderIDCell.innerText;
        rows[i].style.display = orderIDText.toLowerCase().includes(input) ? "" : "none";
      }
    }
  }
