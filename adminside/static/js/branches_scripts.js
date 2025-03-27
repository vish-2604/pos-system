// Toggle search input on small devices
function toggleSearch() {
  let searchContainer = document.querySelector(".search-container");
  let searchInput = document.querySelector(".search-input");

  searchContainer.classList.toggle("active");
  if (searchContainer.classList.contains("active")) {
    searchInput.focus();
  }
}

// Search function
document.getElementById("searchInput").addEventListener("keyup", function () {
  let filter = this.value.toLowerCase();
  let rows = document.querySelectorAll("#storeTableBody tr");

  rows.forEach(function (row) {
    let store = row.cells[1].textContent.toLowerCase();
    let manager = row.cells[2].textContent.toLowerCase();

    if (store.includes(filter) || manager.includes(filter)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});

function openForm() {
  document.getElementById("myForm").style.display = "block";
  document.getElementById("overlay").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
  document.getElementById("overlay").style.display = "none";
}

document.querySelector(".add-fooditems-button").addEventListener("click", openForm);

document.querySelector(".cancel").addEventListener("click", closeForm);

function clearErrors() {
  document.querySelectorAll(".error-message").forEach((element) => element.remove());
}

function showError(inputId, message) {
  const inputElement = document.getElementById(inputId);
  const inputGroup = inputElement.closest(".input-group");

  if (!inputGroup) return;

  let existingError = inputGroup.querySelector(".error-message");
  if (existingError) {
    existingError.textContent = message;
    return;
  }
  const errorElement = document.createElement("div");
  errorElement.className = "error-message";
  errorElement.style.color = "red";
  errorElement.style.fontSize = "12px";
  errorElement.textContent = message;

  inputGroup.appendChild(errorElement);
}

function clearErrors() {
  document.querySelectorAll(".error-message").forEach((el) => el.remove());
}

function validateForm(event) {
  event.preventDefault();
  clearErrors();

  let isValid = true;

  const location = document.getElementById("location").value.trim();
  const storeArea = document.getElementById("storeArea").value.trim();
  const phone = document.getElementById("PhoneNo").value.trim();
  const isActive = document.getElementById("is_active").value;
  const managerID = document.getElementById("managerID").value.trim(); // Capture manager ID

  if (location === "") {
    showError("location", "Location is required");
    isValid = false;
  }

  if (storeArea === "") {
    showError("storeArea", "Store area is required");
    isValid = false;
  }

  const phonePattern = /^[6789]\d{9}$/;
  if (phone === "" || !phonePattern.test(phone)) {
    showError("PhoneNo", "Phone must start with 6,7,8,9 & be 10 digits");
    isValid = false;
  }

  if (!isActive) {
    showError("is_active", "Status is required");
    isValid = false;
  }

  if (isValid) {
    document.getElementById("storeForm").submit(); // Submit the form
  }
}

document.getElementById("storeForm").addEventListener("submit", validateForm);


document.addEventListener("DOMContentLoaded", function () {
  window.openForm = function (isUpdate, branchData = {}) {
    document.getElementById("myForm").style.display = "block";
    document.getElementById("overlay").style.display = "block";
    document.getElementById("storeForm").reset();
    console.log(document.getElementById("managerID").value)
  
    if (isUpdate) {
      document.getElementById("branch_id").value = branchData.id || ""; 
      document.getElementById("location").value = branchData.location || "";
      document.getElementById("storeArea").value = branchData.area || "";
    
      document.getElementById("managerID").value = branchData.manager_id || "";
      
      document.getElementById("PhoneNo").value = branchData.phone_no || "";
      document.getElementById("is_active").value = branchData.is_active ? "True" : "False";
      document.getElementById("submitBtn").textContent = "Update";
    }
    else {
      document.getElementById("submitBtn").textContent = "Add";
      document.getElementById("branch_id").value = "";
    }
  };
  

  window.closeForm = function () {
    document.getElementById("myForm").style.display = "none";
    document.getElementById("overlay").style.display = "none";
  };

  document.querySelectorAll(".update-btn").forEach(button => {
    button.addEventListener("click", function () {
      let row = this.closest("tr");

      let branchData = {
        id: row.children[0].textContent.trim(),  // Fetch Branch ID
        location: row.children[1].textContent.trim(),
        area: row.children[2].textContent.trim(),
        manager_id: row.children[3].textContent.trim() !== "No Manager" ? row.children[3].getAttribute("data-manager-id") : "", // Fetch manager's ID from data attribute
        phone_no: row.children[4].textContent.trim(),
        is_active: row.children[5].textContent.includes("Active")
      };

      openForm(true, branchData);
    });
  });
});

document.addEventListener("DOMContentLoaded", function() {
  setTimeout(() => {
      let alerts = document.querySelectorAll(".alert");
      alerts.forEach(alert => {
          alert.style.animation = "fadeOut 0.5s forwards";
          setTimeout(() => alert.remove(), 500);
      });
  }, 3000);
});

function openDeleteModal(branchId) {
  document.getElementById("delete_branch_id").value = branchId;
  document.getElementById("deleteModal").style.display = "flex";
}

function closeDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
}

