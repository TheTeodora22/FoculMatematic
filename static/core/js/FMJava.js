const sidebar = document.querySelector(".sidebar");
const sidebarDialog = document.querySelector(".sidebar-dialog");
const sidebarOpener = document.querySelector(".sidebar-open");
let previousBodyOverflow = "";
let sidebarCloseTimer = null;

function showSidebar() {
    if (!sidebar || !sidebarDialog || sidebarDialog.open) return;
    previousBodyOverflow = document.body.style.overflow;
    sidebarDialog.showModal();
    if (sidebarOpener) sidebarOpener.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
}

function collapseSubmenu(item) {
    const submenu = item.querySelector(".sidebar-submenu");
    item.classList.remove("open");
    if (submenu) {
        submenu.style.maxHeight = "0";
        submenu.inert = true;
        submenu.setAttribute("aria-hidden", "true");
    }
    const toggle = item.querySelector(".submenu-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
}

function expandSubmenu(item) {
    const submenu = item.querySelector(".sidebar-submenu");
    item.classList.add("open");
    if (submenu) {
        submenu.inert = false;
        submenu.removeAttribute("aria-hidden");
        submenu.style.maxHeight = submenu.scrollHeight + "px";
    }
    const toggle = item.querySelector(".submenu-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
}

function resetSidebarSubmenus() {
    document.querySelectorAll(".sidebar .has-submenu.open").forEach(function (item) {
        collapseSubmenu(item);
    });
}

function closeSidebar() {
    if (!sidebarDialog || !sidebarDialog.open) return;
    if (sidebarDialog.classList.contains("is-closing")) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        sidebarDialog.close();
        return;
    }
    sidebarDialog.classList.add("is-closing");
    const exitStyle = getComputedStyle(sidebarDialog);
    // Computed animation durations are expressed in seconds by the browser.
    const exitDuration = parseFloat(exitStyle.animationDuration) * 1000;
    if (exitStyle.animationName === "none" || !Number.isFinite(exitDuration) || exitDuration <= 0) {
        sidebarDialog.close();
        return;
    }
    // Keep the dialog modal until its exit animation finishes.
    sidebarCloseTimer = setTimeout(function () {
        if (sidebarDialog.open) sidebarDialog.close();
    }, exitDuration + 64);
}

function finishClosingSidebar() {
    clearTimeout(sidebarCloseTimer);
    sidebarCloseTimer = null;
    sidebarDialog.classList.remove("is-closing");
    resetSidebarSubmenus();
    document.body.style.overflow = previousBodyOverflow;
    if (sidebarOpener) {
        sidebarOpener.setAttribute("aria-expanded", "false");
        if (window.innerWidth <= 1280) sidebarOpener.focus({preventScroll: true});
    }
}

if (sidebarOpener) sidebarOpener.addEventListener("click", showSidebar);
const sidebarCloser = document.querySelector(".sidebar-close");
if (sidebarCloser) sidebarCloser.addEventListener("click", closeSidebar);
if (sidebarDialog) {
    sidebarDialog.addEventListener("close", finishClosingSidebar);
    sidebarDialog.addEventListener("cancel", function (event) {
        event.preventDefault();
        closeSidebar();
    });
    function finishSidebarExit(event) {
        if (event.target === sidebarDialog && event.animationName === "sidebar-slide-out" &&
            sidebarDialog.classList.contains("is-closing") && sidebarDialog.open) {
            sidebarDialog.close();
        }
    }
    sidebarDialog.addEventListener("animationend", finishSidebarExit);
    sidebarDialog.addEventListener("animationcancel", finishSidebarExit);
    sidebarDialog.addEventListener("keydown", function (event) {
        // Keep training's document-level shortcuts behind the modal drawer.
        // Tab stays native; the cancel handler animates Escape dismissal.
        event.stopPropagation();
    });
    sidebarDialog.addEventListener("click", function (event) {
        if (event.target !== sidebarDialog) return;
        const bounds = sidebarDialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) closeSidebar();
    });
}

window.addEventListener("resize", function () {
    if (window.innerWidth > 1280 && sidebarDialog && sidebarDialog.open) {
        closeSidebar();
    }
});

// The native dialog handles focus containment and the inert background.

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
