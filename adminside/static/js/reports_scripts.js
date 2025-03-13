function toggleSearch() {
    let searchContainer = document.querySelector(".search-container");
    let searchInput = document.querySelector(".search-input");
  
    searchContainer.classList.toggle("active");
    if (searchContainer.classList.contains("active")) {
      searchInput.focus();
    }
  }
  
  document.getElementById("searchInput").addEventListener("keyup", function () {
    let filter = this.value.trim().toLowerCase();
    let rows = document.querySelectorAll("#salesTableBody tr");  

    rows.forEach(function (row) {
        let itemname = row.cells[1]?.textContent.trim().toLowerCase(); 
        let category = row.cells[2]?.textContent.trim().toLowerCase(); 

        if (itemname.includes(filter) || category.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
});


  