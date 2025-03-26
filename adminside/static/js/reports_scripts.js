function filterReports() {
  let filterValue = document.getElementById("incomeDropdown").value;
  window.location.href = `?filter=${filterValue}`;  // Reload with query param
}

// Set the selected filter when the page loads
document.addEventListener("DOMContentLoaded", function() {
  let params = new URLSearchParams(window.location.search);
  let filterValue = params.get("filter") || "all";  // Default to "all"
  document.getElementById("incomeDropdown").value = filterValue;
});


  