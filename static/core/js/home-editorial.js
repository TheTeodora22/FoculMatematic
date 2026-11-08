(function () {
    'use strict';
    const home = document.querySelector('.math-home');
    if (!home) return;
    const sections = Array.from(home.querySelectorAll(':scope > section'));
    if (sections.length !== 4) return;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const names = ['Introducere', 'Alege clasa', 'Cum înveți', 'Începe'];
    let active = 0, lockedUntil = 0, wheelSum = 0, wheelTime = 0;
    const nav = document.createElement('nav');
    nav.className = 'math-slide-nav';
    nav.setAttribute('aria-label', 'Secțiunile paginii');
    const buttons = sections.map((section, index) => {
        section.id = section.id || 'home-section-' + (index + 1);
        const button = document.createElement('button');
        button.type = 'button';
        button.setAttribute('aria-label', names[index] + ' — secțiunea ' + (index + 1) + ' din 4');
        button.setAttribute('aria-controls', section.id);
        button.addEventListener('click', () => go(index));
        nav.appendChild(button);
        return button;
    });
    const footer = document.querySelector('.footer');
    if (footer) sections[3].appendChild(footer);
    home.classList.add('snap-pages');
    home.appendChild(nav);
    function mark(index) {
        active = index;
        buttons.forEach((button, i) => {
            if (i === index) button.setAttribute('aria-current', 'step');
            else button.removeAttribute('aria-current');
        });
    }
    function go(index) {
        const next = Math.max(0, Math.min(sections.length - 1, index));
        if (next === active) return;
        const focused = sections[active].contains(document.activeElement);
        mark(next);
        lockedUntil = performance.now() + (reduced.matches ? 150 : 900);
        home.scrollTo({top: sections[next].offsetTop, behavior: reduced.matches ? 'instant' : 'smooth'});
        if (focused) {
            const heading = sections[next].querySelector('h1, h2');
            heading.setAttribute('tabindex', '-1');
            heading.focus({preventScroll: true});
        }
    }
    function canReadMore(direction) {
        const section = sections[active];
        return direction > 0 ? section.scrollTop + section.clientHeight < section.scrollHeight - 2 : section.scrollTop > 2;
    }
    home.addEventListener('wheel', event => {
        if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
        const direction = Math.sign(event.deltaY);
        if (canReadMore(direction)) return;
        event.preventDefault();
        const now = performance.now();
        if (now < lockedUntil) { wheelTime = now; wheelSum = 0; return; }
        if (now - wheelTime > 180 || Math.sign(wheelSum) !== direction) wheelSum = 0;
        wheelTime = now;
        wheelSum += event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? home.clientHeight : 1);
        if (Math.abs(wheelSum) < 45) return;
        wheelSum = 0;
        go(active + direction);
    }, {passive: false});
    let frame;
    home.addEventListener('scroll', () => {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(() => {
            mark(sections.reduce((best, section, i) => Math.abs(section.offsetTop - home.scrollTop) < Math.abs(sections[best].offsetTop - home.scrollTop) ? i : best, 0));
        });
    }, {passive: true});
    document.addEventListener('keydown', event => {
        if (event.defaultPrevented || event.ctrlKey || event.altKey || event.metaKey || event.target.closest('input, textarea, select, [contenteditable="true"], dialog, .site-header')) return;
        const forward = ['ArrowDown', 'PageDown'].includes(event.key);
        const back = ['ArrowUp', 'PageUp'].includes(event.key);
        if ((!forward && !back) || canReadMore(forward ? 1 : -1)) return;
        event.preventDefault();
        if (performance.now() >= lockedUntil) go(active + (forward ? 1 : -1));
    });
    home.addEventListener('click', event => {
        if (!event.target.closest('a[href="#home-classes"]')) return;
        event.preventDefault(); go(1);
    });
    const initial = sections.findIndex(section => '#' + section.id === window.location.hash);
    mark(initial >= 0 ? initial : 0);
    home.scrollTop = sections[active].offsetTop;
    window.addEventListener('resize', () => home.scrollTo({top: sections[active].offsetTop, behavior: 'instant'}));
})();
