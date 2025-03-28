document.addEventListener("DOMContentLoaded", function () {
    function loadContent(url, clickedLink = null) {
        fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                document.getElementById("content-area").innerHTML = html;
                window.history.pushState({ path: url }, "", url);

            })
            .catch(error => console.error("Error loading content:", error));
    }

    document.querySelectorAll(".sidebar a").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            let url = this.getAttribute("href");
            loadContent(url);
        });
    });

    window.onpopstate = function (event) {
        if (event.state && event.state.path) {
            loadContent(event.state.path);
        }
    };

    updateActiveLink();

    if (window.location.pathname !== "/") {
        loadContent(window.location.pathname);
    }
});

function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    sidebar.style.width = sidebar.style.width === "250px" ? "70px" : "250px";
}


