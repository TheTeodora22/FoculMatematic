/* Enhance actual overflow, without changing exercise values or SVG coordinates. */
(function () {
    'use strict';
    const selector = '.criteria-table-wrap, .statistics-chart-scroll, .statistics-table-wrap, .decimal-place-table-wrap, .percent-table-wrap, .profile-activity-wrap, .analytics-table-wrap';
    const regions = new Map();
    const positions = new Map();
    const observer = typeof ResizeObserver === 'function' ? new ResizeObserver(updateAll) : null;

    function restoreAttribute(element, name, original) {
        if (original === null) element.removeAttribute(name);
        else element.setAttribute(name, original);
    }
    function update(element, info) {
        const overflowing = element.clientWidth > 0 && element.scrollWidth > element.clientWidth + 2;
        element.dataset.horizontalScroll = String(overflowing);
        if (overflowing) {
            element.setAttribute('tabindex', info.tabindex ?? '0');
            element.setAttribute('role', info.role ?? 'region');
            element.setAttribute('aria-label', info.label ?? element.dataset.scrollLabel ?? 'Conținut derulabil orizontal');
            info.hint.hidden = false;
            if (!info.restored) {
                const position = positions.get(info.key);
                if (position !== undefined) element.scrollLeft = position;
                info.restored = true;
            }
        } else {
            restoreAttribute(element, 'tabindex', info.tabindex);
            restoreAttribute(element, 'role', info.role);
            restoreAttribute(element, 'aria-label', info.label);
            info.hint.hidden = true;
            if (element.clientWidth > 0) info.restored = true;
        }
    }
    function updateAll() { regions.forEach((info, element) => update(element, info)); }
    function refresh() {
        for (const [element] of regions) {
            if (!element.isConnected) {
                observer?.unobserve(element);
                const content = element.querySelector('table');
                if (content) observer?.unobserve(content);
                regions.delete(element);
            }
        }
        document.querySelectorAll(selector).forEach((element, index) => {
            if (regions.has(element)) return;
            const hint = document.createElement('p');
            hint.className = 'horizontal-scroll-hint';
            hint.textContent = 'Derulează orizontal. Din tastatură: ← / →.';
            hint.hidden = true;
            element.before(hint);
            const info = {
                key: window.location.pathname + ':' + index,
                tabindex: element.getAttribute('tabindex'), role: element.getAttribute('role'),
                label: element.getAttribute('aria-label'), hint,
            };
            regions.set(element, info);
            element.addEventListener('scroll', () => {
                if (element.isConnected) positions.set(info.key, element.scrollLeft);
            }, {passive: true});
            element.addEventListener('keydown', event => {
                if (element.dataset.horizontalScroll === 'true' && ['ArrowLeft', 'ArrowRight'].includes(event.key) &&
                    !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey) event.stopPropagation();
            });
            element.addEventListener('focusin', event => {
                if (!element.classList?.contains('criteria-table-wrap') || element.scrollLeft <= 0) return;
                const control = event.target.closest?.('button, input, select, textarea');
                const header = element.querySelector('th');
                if (!control || !header || !control.matches(':focus-visible')) return;
                const covered = header.getBoundingClientRect().right + 8 - control.getBoundingClientRect().left;
                if (covered > 0) {
                    element.scrollLeft = Math.max(0, element.scrollLeft - covered);
                    positions.set(info.key, element.scrollLeft);
                }
            });
            observer?.observe(element);
            const content = element.querySelector('table');
            if (content) observer?.observe(content);
        });
        updateAll();
    }
    refresh();
    window.addEventListener('resize', updateAll, {passive: true});
    const training = document.getElementById('training-question');
    // Only direct question replacements; graph dragging and KaTeX internals do
    // not trigger a full-document scan.
    if (training && typeof MutationObserver === 'function') {
        new MutationObserver(refresh).observe(training, {childList: true});
    }
})();
