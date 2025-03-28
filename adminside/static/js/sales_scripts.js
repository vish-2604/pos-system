function toggleSearch() {
  const container = document.getElementById('searchContainer');
  const input = document.getElementById("searchInput");

  // Toggle only when screen width is greater than 415px
  if (window.innerWidth > 415) {
    container.classList.toggle('active');
    if (container.classList.contains("active")) {
      input.focus();
    }
  }
}

// No toggle effect below 415px
window.addEventListener("resize", function () {
  const container = document.getElementById('searchContainer');
  const input = document.getElementById("searchInput");

  if (window.innerWidth <= 415) {
    container.classList.add("active");
    input.style.width = "150px";
    input.style.opacity = "1";
    input.style.pointerEvents = "auto";
  } else {
    container.classList.remove("active");
    input.style.width = "0";
    input.style.opacity = "0";
    input.style.pointerEvents = "none";
  }
});



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
