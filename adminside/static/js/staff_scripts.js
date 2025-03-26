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
  let rows = document.querySelectorAll("#staffBody tr");

  rows.forEach(function (row) {
    let fullName = row.cells[1].textContent.toLowerCase();
    let userName = row.cells[2].textContent.toLowerCase();

    if (fullName.includes(filter) || userName.includes(filter)) {
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

document.querySelector(".add-staff-button").addEventListener("click", openForm);

document.querySelector(".cancel").addEventListener("click", closeForm);

document.getElementById("staffForm").addEventListener("submit", validateForm);

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

  const email = document.getElementById("staff_email").value.trim();
  const phone = document.getElementById("staff_phone").value.trim();
  const password = document.getElementById("staff_password").value.trim();
  const fullname = document.getElementById("staff_fullname").value.trim();
  const username = document.getElementById("staff_username").value.trim();
  const role = document.getElementById("staff_role").value;
  const branch = document.getElementById("branch").value;

  if (email === "" || !isValidEmail(email)) {
    showError("staff_email", "Enter a valid email address");
    isValid = false;
  }

  const phonePattern = /^[6789]\d{9}$/;
  if (phone === "" || !phonePattern.test(phone)) {
    showError("staff_phone", "Phone must start with 6,7,8,9 & be 10 digits");
    isValid = false;
  }

  const passwordPattern = /^(?=.*[A-Z])(?=.*[\W]).{6,}$/;
  if (password === "" || !passwordPattern.test(password)) {
    showError("staff_password", "Password must be 6+ chars, 1 uppercase, 1 special character");
    isValid = false;
  }
  if (fullname === "") {
    showError("staff_fullname", "Full name is required");
    isValid = false;
  }
  if (username === "") {
    showError("staff_username", "Username is required");
    isValid = false;
  }
  if (!role) {
    showError("staff_role", "Select a staff role");
    isValid = false;
  }
  if (!branch) {
    showError("branch", "Select a branch");
    isValid = false;
  }
  if (isValid) {
    document.getElementById("staffForm").submit();
  }
}


document.addEventListener("DOMContentLoaded", function () {
  window.openForm = function (isUpdate, staffData = {}) {
    document.getElementById("myForm").style.display = "block";
    document.getElementById("overlay").style.display = "block";

    document.getElementById("staffForm").reset();

    if (isUpdate) {
        document.getElementById("staff_id").value = staffData.staff_id;
        document.getElementById("staff_fullname").value = staffData.staff_fullname;
        document.getElementById("staff_username").value = staffData.username;
        document.getElementById("staff_email").value = staffData.staff_email;
        document.getElementById("staff_password").value = "******";
        document.getElementById("staff_phone").value = staffData.staff_phone;
        document.getElementById("date_joined").value = staffData.date_joined;
        document.getElementById("is_active").value = staffData.is_active ? "True" : "False";

        // Ensure the role is selected correctly
        let roleDropdown = document.getElementById("staff_role");
        if (staffData.staff_role) {
            roleDropdown.value = staffData.staff_role;
        } else {
            roleDropdown.selectedIndex = 0; // Default placeholder
        }

        let branchDropdown = document.getElementById("branch");

        if (staffData.branch) {
            let selectedBranch = staffData.branch.trim().toLowerCase();
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
    } else {
        document.getElementById("submitBtn").textContent = "Add";
    }
};



  window.closeForm = function () {
    document.getElementById("myForm").style.display = "none";
    document.getElementById("overlay").style.display = "none";
  };

  document.querySelectorAll(".update-btn").forEach(button => {
    button.addEventListener("click", function () {
      let row = this.closest("tr");
      let staffData = {
        staff_id: row.children[0].textContent.trim(),
        staff_fullname: row.children[2].textContent.trim(),
        username: row.children[3].textContent.trim(),
        staff_email: row.children[4].textContent.trim(),
        staff_role: row.children[6].textContent.trim(),
        staff_phone: row.children[7].textContent.trim(),
        branch: row.children[8].textContent.trim(),
        date_joined: row.children[9].textContent.trim(),
        is_active: row.children[10].textContent.trim() === "Active"
      };

      openForm(true, staffData);
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

function openDeleteModal(staffId) {
  document.getElementById("delete_staff_id").value = staffId;
  document.getElementById("deleteModal").style.display = "block";
}

function closeDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
}
