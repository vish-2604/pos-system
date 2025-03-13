function toggleSearch() {
  let searchContainer = document.querySelector(".search-container");
  let searchInput = document.querySelector(".search-input");

  searchContainer.classList.toggle("active");
  if (searchContainer.classList.contains("active")) {
    searchInput.focus();
  }
}

document.getElementById("searchInput").addEventListener("keyup", function () {
  let filter = this.value.toLowerCase();
  let rows = document.querySelectorAll("#customerBody tr");

  rows.forEach(function (row) {
    let fullName = row.cells[1].textContent.toLowerCase();
    let email = row.cells[2].textContent.toLowerCase();

    if (fullName.includes(filter) || email.includes(filter)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});

function openForm(isUpdate, customerData = {}) {
  document.getElementById("myForm").style.display = "block";
  document.getElementById("overlay").style.display = "block";
  document.getElementById("customerForm").reset();

  let submitBtn = document.querySelector(".form-buttons button[type='submit']");
  
  if (submitBtn) {
    if (isUpdate) {
      document.getElementById("customer_id").value = customerData.customer_id;
      document.getElementById("firstName").value = customerData.firstName;
      document.getElementById("lastName").value = customerData.lastName;
      document.getElementById("email").value = customerData.email;
      document.getElementById("phoneNo").value = customerData.phone;
      document.getElementById("gender").value = customerData.gender;
      submitBtn.textContent = "Update";
    } else {
      submitBtn.textContent = "Add";
    }
  } else {
    console.error("Submit button not found!");
  }
}


function closeForm() {
  document.getElementById("myForm").style.display = "none";
  document.getElementById("overlay").style.display = "none";
}

document.querySelector(".add-customer-button").addEventListener("click", () => openForm(false));
document.querySelector(".cancel").addEventListener("click", closeForm);

document.getElementById("customerForm").addEventListener("submit", validateForm);

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

function isValidEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
}

function validateForm(event) {
  event.preventDefault();
  clearErrors();

  let isValid = true;

  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phoneNo").value.trim();
  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const gender = document.getElementById("gender").value;

  if (email === "" || !isValidEmail(email)) {
    showError("email", "Enter a valid email address");
    isValid = false;
  }

  const phonePattern = /^[6789]\d{9}$/;
  if (phone === "" || !phonePattern.test(phone)) {
    showError("phoneNo", "Phone must start with 6,7,8,9 & be 10 digits");
    isValid = false;
  }

  if (firstName === "") {
    showError("firstName", "First name is required");
    isValid = false;
  }
  if (lastName === "") {
    showError("lastName", "Last name is required");
    isValid = false;
  }
  if (!gender) {
    showError("gender", "Select a gender");
    isValid = false;
  }

  if (isValid) {
    console.log("Submitting form...");
    document.getElementById("customerForm").submit(); // ✅ Submit the form
  }
}


document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("customerBody").addEventListener("click", function (event) {
    if (event.target.closest(".update-btn")) {
      let row = event.target.closest("tr");
      let customerData = {
        customer_id: row.children[0].textContent.trim(),
        firstName: row.children[1].textContent.split(" ")[0].trim(),
        lastName: row.children[1].textContent.split(" ")[1]?.trim() || "",
        email: row.children[2].textContent.trim(),
        phone: row.children[3].textContent.trim(),
        gender: row.children[4].textContent.trim()
      };
      openForm(true, customerData);
    }
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