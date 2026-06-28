const sidebar = document.querySelector(".sidebar");

function showSidebar() {
    if (sidebar) sidebar.style.display = "flex";
}

function closeSidebar() {
    if (sidebar) sidebar.style.display = "none";
}

window.addEventListener("resize", function () {
    const sb = document.querySelector(".sidebar");
    if (window.innerWidth > 1280 && sb && sb.style.display === "flex") {
        closeSidebar();
    }
});

/** Dezactivează butonul de submit la prima trimitere (evită dublu-click / POST dublu). */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form.fm-prevent-double-submit").forEach(function (form) {
        form.addEventListener("submit", function () {
            var btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                btn.disabled = true;
                btn.setAttribute("aria-busy", "true");
            }
        });
    });
});
