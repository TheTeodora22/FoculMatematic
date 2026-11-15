/* Recovery is independent of the graph library and its initializer. */
(function () {
    let ready = false;
    document.documentElement.classList.add('fm-boards-loading');
    function showError() {
        if (ready) return;
        document.documentElement.classList.remove('fm-boards-loading');
        const panel = document.getElementById('boards-error');
        if (panel) panel.hidden = false;
        else document.addEventListener('DOMContentLoaded', showError, {once: true});
    }
    const timer = window.setTimeout(showError, 15000);
    window.fmMathBoardsBoot = {
        fail() { window.clearTimeout(timer); showError(); },
        ready() {
            ready = true;
            window.clearTimeout(timer);
            document.documentElement.classList.remove('fm-boards-loading');
            const panel = document.getElementById('boards-error');
            if (panel) panel.hidden = true;
        },
    };
    window.addEventListener('error', event => {
        if ((event.target?.tagName === 'SCRIPT' && event.target.hasAttribute('data-boards-script')) ||
            event.filename?.includes('/core/js/math-demo.js')) window.fmMathBoardsBoot.fail();
    }, true);
})();
