function filterReports() {
  let filterValue = document.getElementById("incomeDropdown").value;
  window.location.href = `?filter=${filterValue}`;  
}

document.addEventListener("DOMContentLoaded", function() {
  let params = new URLSearchParams(window.location.search);
  let filterValue = params.get("filter") || "all";  
  document.getElementById("incomeDropdown").value = filterValue;
});


  