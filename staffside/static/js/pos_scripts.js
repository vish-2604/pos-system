document.addEventListener("DOMContentLoaded", function () {
    // Handle category link clicks
    document.querySelectorAll(".category-link").forEach(link => {
        link.addEventListener("click", function () {
            window.location.href = this.href;
        });
    });

    // Auto-hide alerts after 3 seconds
    setTimeout(() => {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.style.animation = "fadeOut 0.5s forwards";
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);

    function showToast(message) {
        let toast = document.createElement("div");
        toast.className = "toast-message";
        toast.innerHTML = `${message} <div class="toast-progress"></div>`;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    let tableSelector = document.getElementById("table-selector");
    if (tableSelector) {
        tableSelector.addEventListener("change", function () {
            reloadWithTable(this);
        });
    }

    function reloadWithTable(select) {
        const selectedTable = select.value;
        const currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('table', selectedTable);
        window.location.href = currentUrl.href;
    }

    // Persist selected category
    document.querySelectorAll(".category-link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            let selectedCategory = this.getAttribute("href").split("=")[1];
            let currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set("category", selectedCategory);
            window.location.href = currentUrl.href;
        });
    });

    document.querySelectorAll(".size-btn").forEach(button => {
        button.addEventListener("click", function () {
            let selectedTable = document.getElementById("table-selector").value; // Fetch table inside event listener
            if (!selectedTable) {
                showToast("Please select a table first!");
                return;
            }
            let parentCard = this.closest(".product-item");
            let form = parentCard.querySelector("form");
            let sizeInput = form.querySelector(".selected-size");
            let basePriceElement = form.querySelector("input[name='price']");
            let basePrice = parseFloat(basePriceElement.dataset.basePrice);

            // Remove active class from all size buttons
            parentCard.querySelectorAll(".size-btn").forEach(btn => btn.classList.remove("active"));
            this.classList.add("active");

            // Set selected size value
            let selectedSize = this.dataset.size;
            sizeInput.value = selectedSize;

            // Update the price
            let updatedPrice = basePrice;
            if (selectedSize === "small") updatedPrice *= 0.8; // Decrease by 20%
            else if (selectedSize === "large") updatedPrice *= 1.2;

            basePriceElement.value = updatedPrice;
        });
    });

    document.querySelectorAll(".add-to-cart-button").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            let form = this.closest("form");
            let selectedSize = form.querySelector(".selected-size").value;
            let selectedTable = document.getElementById("table-selector").value;
            let itemId = form.querySelector("input[name='food_item']").value;
            let basePriceElement = form.querySelector("input[name='price']");
            let basePrice = parseFloat(basePriceElement.dataset.basePrice);

            if (!selectedTable) {
                showToast("Please select a table first!");
                return;
            }

            // Adjust price based on size
            let finalPrice = basePrice;
            if (selectedSize === "small") finalPrice *= 0.8;
            else if (selectedSize === "large") finalPrice *= 1.2;            
            basePriceElement.value = finalPrice;

            // Check if the exact size of the item already exists in the cart
            let existingCartItem = document.querySelector(`.cart-item[data-item-id="${itemId}"][data-size="${selectedSize}"]`);

            if (existingCartItem) {
                // Increase quantity instead of adding a duplicate entry
                let quantitySpan = existingCartItem.querySelector(".quantity-value");
                let quantityInput = existingCartItem.querySelector(".quantity-input");
                let newQuantity = parseInt(quantitySpan.innerText) + 1;

                quantitySpan.innerText = newQuantity;
                quantityInput.value = newQuantity;

                // Submit form to update quantity
                existingCartItem.querySelector("form").submit();
            } else {
                // If not already in cart, submit the form to add as a new item
                form.submit();
            }
        });
    });

    const cartContainer = document.getElementById("cart-container");
    const totalPriceElement = document.getElementById("cart-total-price");
    const totalItemsElement = document.getElementById("cart-items-count");

    if (cartContainer) {
        cartContainer.addEventListener("click", function (event) {
            let target = event.target;

            if (target.classList.contains("increase-quantity")) {
                updateCartItem(target, 1);
            }

            if (target.classList.contains("decrease-quantity")) {
                updateCartItem(target, -1);
            }

            if (target.classList.contains("remove-cart-item")) {
                removeCartItem(target);
            }
        });

        updateCartSummary();
    }

    function updateCartItem(target, change) {
        let cartItem = target.closest(".cart-item");
        let quantitySpan = cartItem.querySelector(".quantity-value");
        let quantityInput = cartItem.querySelector(".quantity-input");
        let itemId = cartItem.dataset.itemId;
        let size = cartItem.dataset.size;
    
        let currentQuantity = parseInt(quantitySpan.innerText);
        let newQuantity = currentQuantity + change;
    
        // Prevent quantity from going below 1
        if (newQuantity < 1) {
            return; // Stop further execution if the quantity is already 1
        }
    
        quantitySpan.innerText = newQuantity;
        quantityInput.value = newQuantity;
    
        updateCartSummary();
    
        let updateForm = cartItem.querySelector(".update-cart-form");
        if (updateForm) {
            updateForm.submit();
        }
    }
    
    
    function removeCartItem(target) {
        let cartItem = target.closest(".cart-item");
        cartItem.remove();
        updateCartSummary();

        let form = cartItem.querySelector(".remove-cart-form");
        if (form) {
            form.submit();
        }
    }

    function updateCartSummary() {
        let cartItems = document.querySelectorAll(".cart-item");
        let total = 0;
        let itemCount = 0;

        cartItems.forEach(cartItem => {
            let quantity = parseInt(cartItem.querySelector(".quantity-value").innerText);
            let price = parseFloat(cartItem.dataset.unitPrice);

            total += (quantity * price);
            itemCount += quantity;
        });

        if (totalPriceElement) totalPriceElement.innerText = `₹${total.toFixed(2)}`;
        if (totalItemsElement) totalItemsElement.innerText = `${itemCount}`;
    }

    function updateCartTotal() {
        let total = 0;
        let items = document.querySelectorAll(".cart-item");

        items.forEach(item => {
            let priceElement = item.querySelector(".price-value");
            let quantityElement = item.querySelector(".quantity-value");

            if (priceElement && quantityElement) {
                let price = parseFloat(priceElement.textContent.replace("₹", ""));
                let quantity = parseInt(quantityElement.textContent);

                if (!isNaN(price) && !isNaN(quantity)) {
                    total += price * quantity;
                }
            }
        });

        let totalElement = document.getElementById("cart-total-price");
        if (totalElement) {
            totalElement.textContent = `₹${total.toFixed(2)}`;
        }
    }

    updateCartTotal();
});


function reloadWithTable(selectElement) {
    let tableId = selectElement.value;
    let currentCategory = new URLSearchParams(window.location.search).get('category') || 'all';
    window.location.href = `?category=${currentCategory}&table_id=${tableId}`;
}

document.getElementById('search-input').addEventListener('input', function() {
    this.form.submit();  // Submit the form automatically as the user types
});