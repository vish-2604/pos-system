document.addEventListener("DOMContentLoaded", function () {
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
        let rows = document.querySelectorAll("#categoriesTableBody tr");
        rows.forEach(function (row) {
            let categoryName = row.cells[1].textContent.trim().toLowerCase();
            if (categoryName.includes(filter)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    function openForm(isUpdate = false, categoryData = {}) {
        document.getElementById("myForm").style.display = "block";
        document.getElementById("overlay").style.display = "block";
        document.getElementById("foodItemForm").reset();

        if (isUpdate) {
            document.getElementById("category_id").value = categoryData.category_id;
            document.getElementById("itemName").value = categoryData.category_name;
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

    document.querySelectorAll(".update-btn").forEach(button => {
        button.addEventListener("click", function () {
            let row = this.closest("tr");
            let categoryData = {
                category_id: row.children[0].textContent.trim(),
                category_name: row.children[1].textContent.trim()
            };
            openForm(true, categoryData);
        });
    });

    document.getElementById("foodItemForm").addEventListener("submit", function () {
        setTimeout(closeForm, 100);
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
