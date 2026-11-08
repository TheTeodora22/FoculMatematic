/* Progressive reveal: content is always readable, even without animation support. */
(function () {
    'use strict';
    const home = document.querySelector('.math-home');
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (!home || preference.matches || !('IntersectionObserver' in window) ||
        typeof home.animate !== 'function') return;
    const running = new Map();
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const section = entry.target;
            observer.unobserve(section);
            // Never move content underneath keyboard focus or on a reduced-motion request.
            if (preference.matches || section.contains(document.activeElement)) return;
            const animation = section.animate([
                {opacity: .35, transform: 'translateY(32px)'},
                {opacity: 1, transform: 'translateY(0)'}
            ], {duration: 850, easing: 'cubic-bezier(.22,1,.36,1)'});
            running.set(section, animation);
            animation.onfinish = animation.oncancel = () => running.delete(section);
        });
    }, {threshold: .08});
    home.querySelectorAll(':scope > section:not(.math-intro)').forEach(section => observer.observe(section));
    home.addEventListener('focusin', event => {
        running.forEach((animation, section) => {
            if (section.contains(event.target)) animation.cancel();
        });
    });
    preference.addEventListener('change', () => {
        if (!preference.matches) return;
        observer.disconnect();
        running.forEach(animation => animation.cancel());
    });
    window.addEventListener('pagehide', () => {
        observer.disconnect();
        running.forEach(animation => animation.cancel());
    }, {once: true});
})();
