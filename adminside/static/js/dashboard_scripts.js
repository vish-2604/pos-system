document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.style.transition = "opacity 0.5s ease-out";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500); // Remove after fade-out
        });
    }, 3000);
});
