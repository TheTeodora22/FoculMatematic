const sidebar = document.querySelector(".sidebar");

function showSidebar() {
    if (!sidebar) return;
    sidebar.style.display = "flex";
    document.body.style.overflow = "hidden";
}

function collapseSubmenu(item) {
    const submenu = item.querySelector(".sidebar-submenu");
    item.classList.remove("open");
    if (submenu) submenu.style.maxHeight = "0";
    const toggle = item.querySelector(".submenu-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
}

function expandSubmenu(item) {
    const submenu = item.querySelector(".sidebar-submenu");
    item.classList.add("open");
    if (submenu) submenu.style.maxHeight = submenu.scrollHeight + "px";
    const toggle = item.querySelector(".submenu-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
}

function resetSidebarSubmenus() {
    document.querySelectorAll(".sidebar .has-submenu.open").forEach(function (item) {
        collapseSubmenu(item);
    });
}

function closeSidebar() {
    if (!sidebar) return;
    resetSidebarSubmenus();
    sidebar.style.display = "none";
    document.body.style.overflow = "";
}

window.addEventListener("resize", function () {
    if (window.innerWidth > 1400 && sidebar && sidebar.style.display === "flex") {
        closeSidebar();
    }
});

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSidebar();
});

document.querySelectorAll(".sidebar a[href]").forEach(function (link) {
    link.addEventListener("click", function () {
        if (link.getAttribute("href") !== "#") closeSidebar();
    });
});

document.querySelectorAll(".sidebar .submenu-toggle").forEach(function (toggle) {
    toggle.addEventListener("click", function (e) {
        e.preventDefault();
        const parent = toggle.closest(".has-submenu");
        if (!parent) return;

        const wasOpen = parent.classList.contains("open");

        document.querySelectorAll(".sidebar .has-submenu.open").forEach(function (item) {
            if (item !== parent) collapseSubmenu(item);
        });

        if (wasOpen) {
            collapseSubmenu(parent);
        } else {
            expandSubmenu(parent);
        }
    });
});
