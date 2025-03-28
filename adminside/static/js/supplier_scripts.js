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
    let rows = document.querySelectorAll("#supplierBody tr");

    rows.forEach(function (row) {
        let name = row.cells[1].textContent.toLowerCase();
        let company = row.cells[2].textContent.toLowerCase();

        if (name.includes(filter) || company.includes(filter)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
});

function openForm(isUpdate = false, supplierData = {}) {
    document.getElementById("myForm").style.display = "block";
    document.getElementById("overlay").style.display = "block";

    document.getElementById("supplierForm").reset();
    
    if (isUpdate) {
        document.getElementById("supplier_id").value = supplierData.supplier_id || "";
        document.getElementById("supplierName").value = supplierData.supplier_name || "";
        document.getElementById("companyName").value = supplierData.company_name || "";
        document.getElementById("supplierEmail").value = supplierData.supplier_email || "";
        document.getElementById("supplierAddress").value = supplierData.address || "";
        document.getElementById("supplierPhone").value = supplierData.supplier_phone || "";
        document.getElementById("submitBtn").textContent = "Update";
    } else {
        document.getElementById("submitBtn").textContent = "Add";
    }
}



function closeForm() {
    document.getElementById("myForm").style.display = "none";
    document.getElementById("overlay").style.display = "none";
}

document.querySelector(".add-fooditems-button").addEventListener("click", function () {
    openForm(false);
});

document.querySelector(".cancel").addEventListener("click", closeForm);

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("supplierForm").addEventListener("submit", validateForm);
});

function validateForm(event) {
    event.preventDefault();
    console.log("Validating form...");

    clearErrors();
    let isValid = true;

    const name = document.getElementById("supplierName").value.trim();
    const company = document.getElementById("companyName").value.trim();
    const email = document.getElementById("supplierEmail").value.trim();
    const address = document.getElementById("supplierAddress").value.trim();
    const phone = document.getElementById("supplierPhone").value.trim();

    if (name === "") {
        showError("supplierName", "Supplier name is required.");
        isValid = false;
    }

    if (company === "") {
        showError("companyName", "Company name is required.");
        isValid = false;
    }

    if (email === "" || !isValidEmail(email)) {
        showError("supplierEmail", "Enter a valid email address.");
        isValid = false;
    }

    if (address === "") {
        showError("supplierAddress", "Address is required.");
        isValid = false;
    }

    const phonePattern = /^[6789]\d{9}$/;
    if (phone === "" || !phonePattern.test(phone)) {
        showError("supplierPhone", "Phone must start with 6,7,8,9 & be 10 digits.");
        isValid = false;
    }

    if (isValid) {
        console.log("Form submitted! ✅");
        event.target.submit();
    }
}


function showError(inputId, message) {
    const inputElement = document.getElementById(inputId);
    const errorSpan = inputElement.nextElementSibling;
    
    if (errorSpan && errorSpan.classList.contains("error-message")) {
        errorSpan.textContent = message;
    } else {
        const newErrorSpan = document.createElement("span");
        newErrorSpan.classList.add("error-message");
        newErrorSpan.textContent = message;
        inputElement.parentNode.appendChild(newErrorSpan);
    }
}

function clearErrors() {
    document.querySelectorAll(".error-message").forEach(error => {
        error.textContent = "";
    });
}

function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}


document.querySelectorAll(".update-btn").forEach(button => {
    button.addEventListener("click", function () {
        let row = this.closest("tr");  
        let supplierData = {
            supplier_id: row.children[0].textContent.trim(),
            supplier_name: row.children[1].textContent.trim(),
            company_name: row.children[2].textContent.trim(),
            supplier_email: row.children[3].textContent.trim(),
            address: row.children[4].textContent.trim(),
            supplier_phone: row.children[5].textContent.trim(),
        };
        openForm(true, supplierData); 
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


function openDeleteModal(supplierId) {
  document.getElementById("delete_supplier_id").value = supplierId;
  document.getElementById("deleteModal").style.display = "block";
}

function closeDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
}
