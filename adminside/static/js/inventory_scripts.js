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
  let rows = document.querySelectorAll("#foodTableBody tr");
  
  rows.forEach(function (row) {
    let itemname = row.cells[2].textContent.trim().toLowerCase();
    let category = row.cells[3].textContent.trim().toLowerCase();
    
    if (itemname.includes(filter) || category.includes(filter)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});


function openForm() {
  document.getElementById("itemName").value = "";  
  document.getElementById("itemCategory").value = "";
  document.getElementById("itemQuantity").value = "";
  
  document.getElementById("myForm").style.display = "block";
  document.getElementById("overlay").style.display = "block"; 
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
  document.getElementById("overlay").style.display = "none";
}

function validateForm(event) {
  event.preventDefault();
  let isValid = true;

  let name = document.getElementById("itemName").value.trim();
  let category = document.getElementById("itemCategory").value;
  let description = document.getElementById("itemDescription").value.trim();
  let quantity = document.getElementById("itemQuantity").value.trim();
  let sellingPrice = document.getElementById("itemSelling").value.trim();
  let costPrice = document.getElementById("itemCost").value.trim();
  let mfgDate = document.getElementById("itemMFG").value;
  let expiryDate = document.getElementById("itemExpiry").value;

  function showError(inputId, message) {
    let input = document.getElementById(inputId);
    let errorDiv = document.createElement("div");
    errorDiv.className = "error-message";
    errorDiv.style.color = "red";
    errorDiv.style.fontSize = "12px";
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
  }

  document.querySelectorAll(".error-message").forEach((el) => el.remove());

  if (name === "") {
    showError("itemName", "Name is required");
    isValid = false;
  }
  if (!category) {
    showError("itemCategory", "Select a category");
    isValid = false;
  }
  if (description === "") {
    showError("itemDescription", "Description is required");
    isValid = false;
  }
  if (quantity === "" || quantity <= 0) {
    showError("itemQuantity", "Enter a valid quantity");
    isValid = false;
  }
  if (sellingPrice === "" || sellingPrice <= 0) {
    showError("itemSelling", "Enter a valid selling price");
    isValid = false;
  }
  if (costPrice === "" || costPrice <= 0) {
    showError("itemCost", "Enter a valid cost price");
    isValid = false;
  }
  if (!mfgDate) {
    showError("itemMFG", "Select a manufacturing date");
    isValid = false;
  }
  if (!expiryDate) {
    showError("itemExpiry", "Select an expiry date");
    isValid = false;
  }
  if (new Date(mfgDate) > new Date(expiryDate)) {
    showError("itemExpiry", "Expiry date must be after manufacturing date");
    isValid = false;
  }

  if (isValid) {
    document.getElementById("foodItemForm").submit();
  }
}

document.getElementById("foodItemForm").addEventListener("submit", validateForm);

document.addEventListener("DOMContentLoaded", function () {
  const overlay = document.getElementById("overlay");
  const formPopup = document.getElementById("myForm");
  const form = document.getElementById("foodItemForm");
  const submitBtn = document.getElementById("submitbtn");
  const inventoryIdInput = document.getElementById("inventory_id");
  let isUpdate = false;

  window.openForm = function (inventoryData = null) {
      overlay.style.display = "block";
      formPopup.style.display = "block";
      
      if (inventoryData) {
          isUpdate = true;
          submitBtn.textContent = "Update";
          inventoryIdInput.value = inventoryData.id || "";
          document.getElementById("itemName").value = inventoryData.name || "";
          document.getElementById("itemDescription").value = inventoryData.description || "";
          document.getElementById("itemQuantity").value = inventoryData.stock || "";
          document.getElementById("itemCost").value = inventoryData.cost || "";
          document.getElementById("itemSelling").value = inventoryData.price || "";
          document.getElementById("itemMFG").value = inventoryData.mfg_date || "";
          document.getElementById("itemExpiry").value = inventoryData.exp_date || "";
          document.getElementById("itemCategory").value = inventoryData.category_id || "";
          document.getElementById("itemActive").value = inventoryData.active ? "true" : "false";
      } else {
          isUpdate = false;
          submitBtn.textContent = "Add";
          form.reset();
      }
  };

  window.closeForm = function () {
      overlay.style.display = "none";
      formPopup.style.display = "none";
      form.reset();
  };

  window.toggleSearch = function () {
      let searchValue = document.getElementById("searchInput").value.toLowerCase();
      let tableRows = document.querySelectorAll(".fooditem-detail-table tbody tr");

      tableRows.forEach(row => {
          let itemName = row.cells[2]?.textContent.toLowerCase();
          row.style.display = itemName.includes(searchValue) ? "" : "none";
      });
  };

  document.getElementById("searchInput").addEventListener("keyup", toggleSearch);

  document.querySelectorAll(".update-btn").forEach(button => {
      button.addEventListener("click", function () {
          const row = this.closest("tr");
          const inventoryData = {
              id: row.cells[0].textContent.trim(),
              name: row.cells[2].textContent.trim(),
              category_id: row.cells[3].getAttribute("data-category-id"),
              description: row.cells[4].textContent.trim(),
              stock: row.cells[6].textContent.trim(),
              price: row.cells[8].textContent.trim(),
              cost: row.cells[9].textContent.trim(),
              mfg_date: row.cells[10].textContent.trim(),
              exp_date: row.cells[11].textContent.trim(),
              active: row.cells[12].textContent.includes("Active")
          };
          openForm(inventoryData);
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