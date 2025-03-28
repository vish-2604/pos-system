function updateProfilePic() {
    let input = document.getElementById("profile_pic");
    let file = input.files[0];

    if (file) {
        let reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById("profileImage").src = e.target.result;

            let modalElement = document.getElementById("editProfilePicModal");
            let modalInstance = bootstrap.Modal.getInstance(modalElement);

            if (modalInstance) {
                modalInstance.hide();
            }

            setTimeout(() => {
                document.querySelectorAll(".modal-backdrop").forEach(backdrop => backdrop.remove());
                document.body.classList.remove("modal-open"); 
                document.body.style.overflow = "auto"; 
            }, 300); 
        };

        reader.readAsDataURL(file);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            alert.style.animation = "fadeOut 0.5s forwards";
            setTimeout(() => alert.remove(), 500);
        });
    }, 3000);
  });