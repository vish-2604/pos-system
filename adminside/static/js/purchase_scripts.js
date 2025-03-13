document.addEventListener("DOMContentLoaded", function () {
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
    let rows = document.querySelectorAll("#purchaseBody tr");

    rows.forEach(function (row) {
      let foodItem = row.cells[1].textContent.toLowerCase();
      row.style.display = foodItem.includes(filter) ? "" : "none";
    });
  });

  function openForm(isUpdate = false, purchaseData = {}) {
    let formPopup = document.getElementById("myForm");
    let overlay = document.getElementById("overlay");
    let purchaseForm = document.getElementById("purchaseForm");

    if (!formPopup || !overlay || !purchaseForm) return;

    formPopup.style.display = "block";
    overlay.style.display = "block";
    purchaseForm.reset();
    clearValidationMessages(); // Clear old validation messages

    let purchaseIdField = document.getElementById("purchase_id");
    let foodItemField = document.getElementById("foodItem");
    let quantityField = document.getElementById("quantity");
    let costField = document.getElementById("cost");
    let supplierField = document.getElementById("Supplier");
    let purchaseDateField = document.getElementById("purchaseDate");
    let statusField = document.getElementById("status");

    if (isUpdate) {
      purchaseIdField.value = purchaseData.purchase_id || "";
      foodItemField.value = purchaseData.food_item || "";
      quantityField.value = purchaseData.quantity || "";
      costField.value = purchaseData.cost_price || "";
      supplierField.value = purchaseData.supplier_id || "";
      purchaseDateField.value = purchaseData.purchased_date || "";
      statusField.value = purchaseData.payment_status || "";

      let branchDropdown = document.getElementById("branch");

      if (purchaseData.branch) {
          let selectedBranch = purchaseData.branch.trim().toLowerCase();
          let matchFound = false;
      
          Array.from(branchDropdown.options).forEach(option => {
              if (option.value.trim().toLowerCase() === selectedBranch) {
                  branchDropdown.value = option.value;
                  matchFound = true;
              }
          });
      
          if (!matchFound) {
              branchDropdown.selectedIndex = 0; 
          }
      } else {
          branchDropdown.selectedIndex = 0;
      }
      document.getElementById("submitBtn").textContent = "Update";
    }
    else {
      document.getElementById("submitBtn").textContent = "Add";
    }
  }

  function closeForm() {
    document.getElementById("myForm").style.display = "none";
    document.getElementById("overlay").style.display = "none";
  }

  function validateForm(event) {
    event.preventDefault(); // Prevent form submission
    let isValid = true;

    let foodItemField = document.getElementById("foodItem");
    let quantityField = document.getElementById("quantity");
    let costField = document.getElementById("cost");
    let supplierField = document.getElementById("Supplier");
    let purchaseDateField = document.getElementById("purchaseDate");
    let statusField = document.getElementById("status");
    let branch = document.getElementById("branch").value;


    clearValidationMessages(); // Clear previous messages

    if (!foodItemField.value.trim()) {
      showError(foodItemField, "Food Item is required.");
      isValid = false;
    }
    if (!quantityField.value.trim() || parseInt(quantityField.value) <= 0) {
      showError(quantityField, "Quantity must be a positive number.");
      isValid = false;
    }
    if (!costField.value.trim() || parseFloat(costField.value) <= 0) {
      showError(costField, "Cost Price must be greater than 0.");
      isValid = false;
    }
    if (!supplierField.value.trim()) {
      showError(supplierField, "Please select a supplier.");
      isValid = false;
    }

    if (!branch) {
      showError("branch", "Select a branch");
      isValid = false;
    }

    if (!purchaseDateField.value.trim()) {
      showError(purchaseDateField, "Purchase date is required.");
      isValid = false;
    }
    if (!statusField.value.trim()) {
      showError(statusField, "Payment status is required.");
      isValid = false;
    }

    if (isValid) {
      document.getElementById("purchaseForm").submit();
    }
  }

  function showError(inputElement, message) {
    let errorSpan = document.createElement("span");
    errorSpan.classList.add("error-message");
    errorSpan.style.color = "red";
    errorSpan.textContent = message;
    inputElement.parentNode.appendChild(errorSpan);
  }

  function clearValidationMessages() {
    document.querySelectorAll(".error-message").forEach((el) => el.remove());
  }

  document.querySelectorAll(".update-btn").forEach(button => {
    button.addEventListener("click", function () {
      let row = this.closest("tr");
      if (!row) return;

      let purchaseData = {
        purchase_id: row.children[0]?.textContent.trim() || "",
        food_item: row.children[1]?.textContent.trim() || "",
        quantity: row.children[2]?.textContent.trim() || "",
        cost_price: row.children[3]?.textContent.trim() || "",
        supplier_id: row.children[4]?.getAttribute("data-supplier-id") || "", // Ensure supplier ID is set correctly
        branch: row.children[8].textContent.trim(),
        purchased_date: row.children[6]?.textContent.trim() || "",
        payment_status: row.children[7]?.textContent.trim() || "",
      };

      openForm(true, purchaseData);
    });
  });

  document.querySelector(".add-fooditems-button").addEventListener("click", () => openForm(false));
  document.querySelector(".cancel").addEventListener("click", closeForm);
  document.getElementById("purchaseForm").addEventListener("submit", validateForm);
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