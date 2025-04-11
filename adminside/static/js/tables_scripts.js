document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".table-card").forEach((table) => {
    table.addEventListener("click", function () {
      openTableModal(this);
    });
  });
});

function openTableModal(element) {
  let tableId = element.getAttribute("data-table-number");
  let currentStatus = element.getAttribute("data-status");

  if (currentStatus === "occupied") {
    return;
  }

  tableId = tableId.replace(/\D/g, "");

  document.getElementById("table_id").value = tableId; 
  document.getElementById("status").value = currentStatus; 

  let toggle = document.getElementById("reservedToggle");
  toggle.checked = (currentStatus.toLowerCase() === "reserved");

  var tableModal = new bootstrap.Modal(document.getElementById("tableModal"));
  tableModal.show();
}

document.getElementById("reservedToggle").addEventListener("change", function () {
  document.getElementById("status").value = this.checked ? "on" : "off";
});

document.addEventListener("DOMContentLoaded", function () {
  const openFormBtn = document.querySelector(".add-table-button");
  const overlay = document.getElementById("overlay");
  const formPopup = document.getElementById("myForm");
  const branchDropdown = document.getElementById("branchDropdown"); // Branch dropdown
  const branchInput = document.getElementById("branchInput"); // Hidden input for branch ID
  const seatInput = document.getElementById("seatInput"); // Hidden input for seat count

  if (openFormBtn) {
      openFormBtn.addEventListener("click", function () {
          let selectedBranch = branchDropdown.value; // Get selected branch ID
          if (!selectedBranch) {
              showAlert("Please select a branch first!", "error");
              return;
          }
          branchInput.value = selectedBranch; // Set branch ID in hidden input
          formPopup.style.display = "block";
          overlay.style.display = "block";
      });
  }

  const closeFormBtn = document.querySelector(".btn-close");
  if (closeFormBtn) {
      closeFormBtn.addEventListener("click", function () {
          formPopup.style.display = "none";
          overlay.style.display = "none";
      });
  }

  // Function to set seats and submit the form
  function setSeats(seatCount) {
      let selectedBranch = branchDropdown.value; // Ensure branch is selected
      if (!selectedBranch) {
          showAlert("Please select a branch first!", "error");
          return;
      }

      seatInput.value = seatCount; // Set seats value
      branchInput.value = selectedBranch; // Ensure branch ID is set

      console.log("Submitting Form - Branch ID:", selectedBranch, "Seats:", seatCount);

      document.getElementById("tableForm").submit(); // Submit form
  }

  // Attach `setSeats` to buttons
  document.querySelectorAll(".add-table-card").forEach(button => {
      button.addEventListener("click", function (event) {
          event.preventDefault(); // Prevent direct form submission
          let seatCount = this.getAttribute("onclick").match(/\d+/)[0]; // Extract seat number
          setSeats(seatCount);
      });
  });

  function showAlert(message, type = "info") {
    // Remove existing alerts if any
    document.querySelectorAll(".alert-box").forEach(el => el.remove());

    // Create alert box
    let alertBox = document.createElement("div");
    alertBox.className = `alert-box ${type}`;
    alertBox.innerHTML = `<p>${message}</p>`;

    // Create progress bar inside alert box
    let progressBar = document.createElement("div");
    progressBar.className = "progress-bar";

    // Append progress bar inside alert box
    alertBox.appendChild(progressBar);

    // Append alert box to body
    document.body.appendChild(alertBox);

    // Remove notification after 3 seconds
    setTimeout(() => {
        alertBox.style.opacity = "0";
        setTimeout(() => {
            alertBox.remove();
        }, 500);
    }, 3000);
}

});


document.addEventListener("DOMContentLoaded", function () {
  let urlParams = new URLSearchParams(window.location.search);
  let status = urlParams.get("status");
  let branch = urlParams.get("branch_id");

  if (status) {
      document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(tab => tab.classList.remove("show", "active"));

      if (status === "vacant") {
          document.querySelector('[href="#vacant"]').classList.add("active");
          document.getElementById("vacant").classList.add("show", "active");
      } else if (status === "occupied") {
          document.querySelector('[href="#occupied"]').classList.add("active");
          document.getElementById("occupied").classList.add("show", "active");
      } else if (status === "disabled") {
          document.querySelector('[href="#reserved"]').classList.add("active");
          document.getElementById("reserved").classList.add("show", "active");
      } else {
          document.querySelector('[href="#allTables"]').classList.add("active");
          document.getElementById("allTables").classList.add("show", "active");
      }
  }
});

function filterByStatus(status) {
  let urlParams = new URLSearchParams(window.location.search);
  let branch = urlParams.get("branch_id");

  urlParams.set("status", status);
  if (branch) {
      urlParams.set("branch_id", branch); // Keep branch in URL
  }

  window.location.search = urlParams.toString(); // Reload with correct parameters
}
