document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.classList.add("fade-out"); 
            setTimeout(() => alert.remove(), 500); 
        });
    }, 3000);
});
