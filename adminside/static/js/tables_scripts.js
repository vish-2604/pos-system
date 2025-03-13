document.addEventListener("DOMContentLoaded", function () {
  const openFormBtn = document.querySelector(".add-table-button");
  const overlay = document.getElementById("overlay");
  const formPopup = document.getElementById("myForm");

  if (openFormBtn) {
      openFormBtn.addEventListener("click", function () {
          formPopup.style.display = "block";
          overlay.style.display = "block";
      });
  }

  const closeFormBtn = document.querySelector(".btn-close");
  if (closeFormBtn) {
      closeFormBtn.addEventListener("click", function () {
          formPopup.style.display = "none";
          overlay.style.display = "none";
      });
  }
});

function setSeats(seatCount) {
  document.getElementById("seatInput").value = seatCount;  
  document.getElementById("tableForm").submit(); 
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