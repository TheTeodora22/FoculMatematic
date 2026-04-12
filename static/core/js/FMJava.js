const sidebar = document.querySelector(".sidebar");

function showSidebar() {
    if (sidebar) sidebar.style.display = "flex";
}

function closeSidebar() {
    if (sidebar) sidebar.style.display = "none";
}

window.addEventListener("resize", function () {
    const sb = document.querySelector(".sidebar");
    if (window.innerWidth > 640 && sb && sb.style.display === "flex") {
        closeSidebar();
    }
});

(function () {
    const mqTablet = window.matchMedia("(min-width: 641px) and (max-width: 1024px)");
    const nav = document.querySelector(".nav__link");
    if (!nav) return;

    function closeNavDropdowns() {
        nav.querySelectorAll("li.nav-dropdown-open").forEach(function (li) {
            li.classList.remove("nav-dropdown-open");
            const btn = li.querySelector(".navDDToggle");
            if (btn) btn.setAttribute("aria-expanded", "false");
        });
    }

    function onDocClick(e) {
        if (!mqTablet.matches) return;
        if (!nav.contains(e.target)) closeNavDropdowns();
    }

    nav.querySelectorAll(".has-dropdown .navDDToggle").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            if (!mqTablet.matches) return;
            e.preventDefault();
            e.stopPropagation();
            const li = btn.closest("li.has-dropdown");
            const open = li.classList.contains("nav-dropdown-open");
            closeNavDropdowns();
            if (!open) {
                li.classList.add("nav-dropdown-open");
                btn.setAttribute("aria-expanded", "true");
            }
        });
    });

    nav.querySelectorAll(".has-dropdown .submenu a").forEach(function (a) {
        a.addEventListener("click", function () {
            if (mqTablet.matches) closeNavDropdowns();
        });
    });

    document.addEventListener("click", onDocClick);
    mqTablet.addEventListener("change", closeNavDropdowns);
})();
