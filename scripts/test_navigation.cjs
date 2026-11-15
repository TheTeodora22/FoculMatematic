// Exercise the actual drawer handlers without a browser or database.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/FMJava.js'), 'utf8');

function setup(reducedMotion = true, exitDuration = '0.22s', animationName = 'sidebar-slide-out') {
    function element() {
        const listeners = {}, attributes = {}, classes = new Set();
        return {listeners, attributes, style: {}, inert: true, scrollHeight: 400,
            addEventListener(type, handler) { listeners[type] = handler; },
            setAttribute(name, value) { attributes[name] = value; },
            removeAttribute(name) { delete attributes[name]; },
            getAttribute(name) { return attributes[name]; },
            classList: {add(name) {classes.add(name);}, remove(name) {classes.delete(name);}, contains(name) {return classes.has(name);}},
            focus() { this.focused = true; }};
    }
    const opener = element(), closer = element(), submenu = element(), toggle = element();
    const item = element();
    item.querySelector = selector => selector === '.sidebar-submenu' ? submenu : toggle;
    toggle.closest = () => item;
    const link = element(); link.attributes.href = '/quizzes/';
    const dialog = element(); dialog.open = false;
    dialog.showModal = () => {dialog.open = true;};
    dialog.close = () => {dialog.open = false; dialog.listeners.close();};
    dialog.getBoundingClientRect = () => ({left: 100, right: 400, top: 0, bottom: 800});
    const window = {innerWidth: 390, listeners: {}, matchMedia() {return {matches: reducedMotion};}, addEventListener(type, handler) {this.listeners[type] = handler;}};
    const document = {
        body: {style: {overflow: 'auto'}},
        querySelector(selector) {return {'.sidebar': element(), '.sidebar-dialog': dialog, '.sidebar-open': opener, '.sidebar-close': closer}[selector];},
        querySelectorAll(selector) {
            if (selector === '.sidebar .has-submenu.open') return item.classList.contains('open') ? [item] : [];
            if (selector === '.sidebar a[href]') return [link];
            if (selector === '.sidebar .submenu-toggle') return [toggle];
            return [];
        },
    };
    let pendingTimer, timerDelay;
    vm.runInNewContext(source, {window, document,
        getComputedStyle() {return {animationDuration: exitDuration, animationName};},
        setTimeout(callback, delay) {pendingTimer = callback; timerDelay = delay; return 1;},
        clearTimeout() {pendingTimer = undefined;},
    });
    return {document, window, opener, closer, dialog, toggle, submenu, item, link,
        timerDelay() {return timerDelay;},
        finishTimer() {pendingTimer?.();}};
}

test('animated dismissal keeps the page inert until the panel finishes and can reopen', () => {
    const s = setup(false); s.opener.listeners.click(); s.closer.listeners.click();
    assert.equal(s.dialog.open, true);
    assert.equal(s.dialog.classList.contains('is-closing'), true);
    assert.equal(s.document.body.style.overflow, 'hidden');
    s.dialog.listeners.animationend({target: s.dialog, animationName: 'sidebar-slide-out'});
    assert.equal(s.dialog.open, false);
    assert.equal(s.document.body.style.overflow, 'auto');
    assert.equal(s.opener.focused, true);
    s.opener.listeners.click();
    assert.equal(s.dialog.open, true);
    assert.equal(s.dialog.classList.contains('is-closing'), false);
});

test('exit fallback follows the computed CSS duration instead of a fixed timeout', () => {
    const s = setup(false, '0.4s'); s.opener.listeners.click(); s.closer.listeners.click();
    assert.equal(s.timerDelay(), 464);
    s.finishTimer();
    assert.equal(s.dialog.open, false);
});

test('cancelled exit animation restores focus and scrolling without waiting for fallback', () => {
    const s = setup(false); s.opener.listeners.click(); s.closer.listeners.click();
    s.dialog.listeners.animationcancel({target: s.dialog, animationName: 'sidebar-slide-out'});
    assert.equal(s.dialog.open, false);
    assert.equal(s.document.body.style.overflow, 'auto');
    assert.equal(s.opener.focused, true);
});

test('disabled or zero-duration CSS animation closes immediately', () => {
    for (const [duration, name] of [['0s', 'sidebar-slide-out'], ['0.22s', 'none']]) {
        const s = setup(false, duration, name); s.opener.listeners.click(); s.closer.listeners.click();
        assert.equal(s.dialog.open, false);
        assert.equal(s.timerDelay(), undefined);
        assert.equal(s.document.body.style.overflow, 'auto');
    }
});

test('Escape uses animated dismissal with a fallback if animationend is missing', () => {
    const s = setup(false); s.opener.listeners.click(); let prevented = false;
    s.dialog.listeners.cancel({preventDefault() {prevented = true;}});
    assert.equal(prevented, true);
    assert.equal(s.dialog.open, true);
    s.closer.listeners.click();
    s.finishTimer();
    assert.equal(s.dialog.open, false);
    assert.equal(s.opener.attributes['aria-expanded'], 'false');
});

test('opening and closing preserves overflow and restores the trigger state/focus', () => {
    const s = setup(); s.opener.listeners.click();
    assert.equal(s.dialog.open, true);
    assert.equal(s.opener.attributes['aria-expanded'], 'true');
    assert.equal(s.document.body.style.overflow, 'hidden');
    s.closer.listeners.click();
    assert.equal(s.dialog.open, false);
    assert.equal(s.document.body.style.overflow, 'auto');
    assert.equal(s.opener.attributes['aria-expanded'], 'false');
    assert.equal(s.opener.focused, true);
});
test('native close, including Escape, resets expanded groups and makes links inert', () => {
    const s = setup(); s.opener.listeners.click();
    s.toggle.listeners.click({preventDefault() {}});
    assert.equal(s.submenu.inert, false);
    assert.equal(s.toggle.attributes['aria-expanded'], 'true');
    assert.equal(s.submenu.style.maxHeight, '400px');
    s.dialog.close();
    assert.equal(s.submenu.inert, true);
    assert.equal(s.submenu.attributes['aria-hidden'], 'true');
    assert.equal(s.toggle.attributes['aria-expanded'], 'false');
});
test('following a link closes the drawer and restores scrolling', () => {
    const s = setup(); s.opener.listeners.click(); s.link.listeners.click();
    assert.equal(s.dialog.open, false);
    assert.equal(s.document.body.style.overflow, 'auto');
});
test('desktop resize closes the drawer without focusing the hidden mobile trigger', () => {
    const s = setup(); s.opener.listeners.click();
    s.window.innerWidth = 1366; s.window.listeners.resize();
    assert.equal(s.dialog.open, false);
    assert.notEqual(s.opener.focused, true);
});
test('only a click outside the panel bounds dismisses its backdrop', () => {
    const s = setup(); s.opener.listeners.click();
    s.dialog.listeners.click({target: s.dialog, clientX: 200, clientY: 100});
    assert.equal(s.dialog.open, true);
    s.dialog.listeners.click({target: s.dialog, clientX: 50, clientY: 100});
    assert.equal(s.dialog.open, false);
});
test('drawer keys do not reach training shortcuts or cancel native dialog behavior', () => {
    const s = setup(); let stopped = false;
    s.dialog.listeners.keydown({stopPropagation() {stopped = true;}});
    assert.equal(stopped, true);
});
