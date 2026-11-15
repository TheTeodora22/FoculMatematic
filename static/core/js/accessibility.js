/* User-controlled decorative motion; no animation is required to use the page. */
(function () {
    const button = document.querySelector('[data-motion-toggle]');
    const image = document.querySelector('[data-motion-media]') || document.querySelector('.hero-artwork img[data-animated-src]');
    if (!button || !image) return;
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const staticSource = image.getAttribute('src');
    const status = document.getElementById('hero-motion-status');
    let paused = preference.matches;
    const video = image.tagName === 'VIDEO';
    let revision = 0;
    function apply(announce) {
        const current = ++revision;
        if (video) {
            if (paused) image.pause();
            else {
                if (!image.getAttribute('src')) image.src = image.dataset.animatedSrc;
                image.play().catch(() => {
                    if (current !== revision) return;
                    paused = true; apply(false);
                    if (status) status.textContent = 'Animația nu a pornit. O poți porni din buton.';
                });
            }
        } else image.src = paused ? staticSource : image.dataset.animatedSrc;
        button.textContent = paused ? 'Pornește animația' : 'Oprește animația';
        button.dataset.paused = String(paused);
        if (announce && status) status.textContent = paused ? 'Animație oprită.' : 'Animație pornită.';
    }
    button.hidden = false;
    const trigger = document.querySelector('[data-motion-trigger]');
    const menu = document.querySelector('[data-motion-menu]');
    function closeMenu(restoreFocus = false) {
        if (!menu || menu.hidden) return;
        menu.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
        if (restoreFocus) trigger.focus({preventScroll:true});
    }
    if (trigger && menu) {
        function openMenu(x, y) {
            menu.hidden = false;
            menu.style.left = Math.max(8, Math.min(x, window.innerWidth-menu.offsetWidth-8))+'px';
            menu.style.top = Math.max(8, Math.min(y, window.innerHeight-menu.offsetHeight-8))+'px';
            trigger.setAttribute('aria-expanded', 'true');
            button.focus({preventScroll:true});
        }
        trigger.addEventListener('contextmenu', event => {
            event.preventDefault();
            const bounds = trigger.getBoundingClientRect();
            openMenu(event.clientX || bounds.left+16, event.clientY || bounds.top+16);
        });
        trigger.addEventListener('keydown', event => {
            if (event.key === 'ContextMenu' || (event.shiftKey && event.key === 'F10')) {
                event.preventDefault();
                const bounds = trigger.getBoundingClientRect();
                openMenu(bounds.left+16, bounds.top+16);
            }
        });
        menu.addEventListener('keydown', event => {
            if (event.key === 'Escape') {event.preventDefault(); closeMenu(true);}
            else if (event.key === 'Tab') closeMenu(true);
            else if (['ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) {
                event.preventDefault(); button.focus({preventScroll:true});
            }
        });
        document.addEventListener('pointerdown', event => {if (!menu.contains(event.target)) closeMenu();});
        menu.addEventListener('focusout', event => {if (!menu.contains(event.relatedTarget)) closeMenu();});
        window.addEventListener('resize', () => closeMenu());
        window.addEventListener('scroll', () => closeMenu(), {passive:true});
    }
    button.addEventListener('click', () => {paused = !paused; apply(true); closeMenu(true);});
    preference.addEventListener('change', () => {
        if (preference.matches) {paused = true; apply(true);}
    });
    apply(false);
})();
