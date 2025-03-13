document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.classList.add("fade-out"); // Add a CSS class for animation
            setTimeout(() => alert.remove(), 500); // Remove after animation
        });
    }, 3000);
});
