const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/ui-components.js'), 'utf8');

function element() {
    const classes = new Set(), attributes = {}, events = {};
    return {events, attributes, dataset: {}, classList: {
        add: name => classes.add(name), remove: name => classes.delete(name),
        contains: name => classes.has(name),
        toggle(name, on) {if (on) classes.add(name); else classes.delete(name);},
    }, addEventListener(type, handler) {events[type] = handler;},
    setAttribute(name, value) {attributes[name] = value;}, getAttribute(name) {return attributes[name] ?? null;},
    removeAttribute(name) {delete attributes[name];}, focus(options) {this.focused = true; this.focusOptions = options;}};
}
function setup() {
    const header = element(), toggle = element(), menu = element(), link = element(), item = element();
    item.querySelector = s => s === '.nav-dropdown-toggle' ? toggle : menu;
    item.contains = target => [item, toggle, menu, link].includes(target);
    menu.querySelector = () => link;
    const form = element(), submit = element(), status = {textContent: ''};
    const actions = [];
    form.append = action => {action.remove = () => {action.removed = true;}; actions.push(action);};
    form.dataset.busyLabel = 'Se salvează…';
    form.dataset.statusId = 'form-submit-status';
    const field = element(), control = element(), clientError = {id: 'field_error', hidden: true, textContent: ''};
    control.type = 'password'; control.willValidate = true; control.validity = {valid: true};
    control.validationMessage = 'Completează câmpul.';
    field.querySelector = s => s.includes('input') ? control : clientError;
    field.querySelectorAll = () => [clientError];
    form.querySelector = () => status;
    form.querySelectorAll = s => s === '.form-field' ? [field] : s === '[data-ui-submitter]' ? actions : [submit];
    const password = element(); password.dataset = {target: 'field', fieldLabel: 'Parolă'};
    const icon = {}; password.querySelector = () => icon;
    const dismiss = element(), message = element(), list = element(), main = element();
    dismiss.closest = () => message; message.parentElement = list;
    message.remove = () => {message.removed = true;};
    list.querySelector = () => null; list.remove = () => {list.removed = true;};
    const active = element(), hashLink = element();
    active.href = 'http://localhost/quizzes/'; hashLink.href = 'http://localhost/quizzes/#';
    const document = {documentElement: element(), events: {},
        createElement: element,
        querySelector: selector => selector === '#main-content' ? main : header,
        getElementById: id => id === 'form-submit-status' ? status : control,
        addEventListener(type, handler) {this.events[type] = handler;},
        querySelectorAll(selector) {return {
            '.nav__link .has-submenu': [item], 'form[data-ui-form]': [form],
            '.password-toggle[data-target]': [password],
            '[data-dismissible] .message-dismiss': [dismiss],
            '.site-header a[href]': [active, hashLink],
        }[selector] || [];},
    };
    const window = {events: {}, scrollY: 0, location: new URL('http://localhost/quizzes/'),
        addEventListener(type, handler) {this.events[type] = handler;}};
    vm.runInNewContext(source, {document, window, URL});
    return {header, toggle, menu, link, item, form, submit, status, control, field, clientError, password, icon, document, window, dismiss, message, list, main, active, actions};
}
test('compact header uses hysteresis and expands again near the top', () => {
    const s = setup(); s.window.scrollY = 100; s.window.events.scroll();
    assert.equal(s.header.classList.contains('is-compact'), true);
    s.window.scrollY = 50; s.window.events.scroll();
    assert.equal(s.header.classList.contains('is-compact'), true);
    s.window.scrollY = 0; s.window.events.scroll();
    assert.equal(s.header.classList.contains('is-compact'), false);
});
test('dropdown ArrowDown focuses its first link and Escape restores its trigger', () => {
    const s = setup(); assert.equal(s.menu.inert, true);
    s.toggle.events.keydown({key: 'ArrowDown', preventDefault() {}});
    assert.equal(s.menu.inert, false); assert.equal(s.link.focused, true);
    assert.equal(s.link.focusOptions.preventScroll, true);
    assert.equal(s.toggle.getAttribute('aria-expanded'), 'true');
    s.item.events.keydown({key: 'Escape', preventDefault() {}, stopPropagation() {}});
    assert.equal(s.menu.inert, true); assert.equal(s.toggle.focused, true);
    assert.equal(s.toggle.focusOptions.preventScroll, true);
});
test('dropdown toggles closed on a second click and dismisses on outside focus/click', () => {
    const s = setup(); s.toggle.events.click(); s.toggle.events.click();
    assert.equal(s.menu.inert, true);
    s.toggle.events.click(); s.item.events.focusout({relatedTarget: null});
    assert.equal(s.menu.inert, true);
    s.toggle.events.click(); s.document.events.click({target: {}});
    assert.equal(s.menu.inert, true);
});
test('keys inside an open desktop dropdown do not reach training shortcuts', () => {
    const s = setup(); s.toggle.events.click(); let stopped = false;
    s.item.events.keydown({key: 'ArrowRight', stopPropagation() {stopped = true;}});
    assert.equal(stopped, true); assert.equal(s.menu.inert, false);
});
test('form prevents duplicate submit and Back/Forward restores enabled controls', () => {
    const s = setup(); s.form.events.submit({defaultPrevented: false});
    assert.equal(s.submit.disabled, true); assert.equal(s.status.textContent, 'Se salvează…');
    let prevented = false;
    s.form.events.submit({defaultPrevented: false, preventDefault() {prevented = true;}});
    assert.equal(prevented, true);
    s.window.events.pageshow();
    assert.equal(s.submit.disabled, false); assert.equal(s.status.textContent, '');
    assert.equal(s.form.getAttribute('aria-busy'), null);
});
test('a submit cancelled by another handler does not disable the form', () => {
    const s = setup(); s.form.events.submit({defaultPrevented: true});
    assert.notEqual(s.submit.disabled, true); assert.equal(s.form.getAttribute('aria-busy'), null);
});
test('named submit action survives the loading state and is removed on Back/Forward', () => {
    const s = setup();
    s.form.events.submit({defaultPrevented: false, submitter: {name: 'action', value: 'new'}});
    assert.equal(s.actions.length, 1); assert.equal(s.actions[0].name, 'action');
    assert.equal(s.actions[0].value, 'new'); assert.equal(s.submit.disabled, true);
    s.window.events.pageshow(); assert.equal(s.actions[0].removed, true);
});
test('native validation is described inline and clears when the field is corrected', () => {
    const s = setup(); s.control.validity.valid = false; s.control.validity.valueMissing = true; s.control.events.blur();
    assert.equal(s.clientError.hidden, false); assert.equal(s.control.getAttribute('aria-invalid'), 'true');
    assert.equal(s.clientError.textContent, 'Completează acest câmp.');
    assert.match(s.control.getAttribute('aria-describedby'), /field_error/);
    s.control.validity.valid = true; s.control.events.input();
    assert.equal(s.clientError.hidden, true); assert.equal(s.control.getAttribute('aria-invalid'), 'false');
});
test('password visibility is reversible and exposes its pressed state', () => {
    const s = setup(); s.password.events.click();
    assert.equal(s.control.type, 'text'); assert.equal(s.password.getAttribute('aria-pressed'), 'true');
    s.password.events.click();
    assert.equal(s.control.type, 'password'); assert.equal(s.password.getAttribute('aria-pressed'), 'false');
});
test('closing the final notification restores a useful keyboard focus target', () => {
    const s = setup(); s.dismiss.events.click();
    assert.equal(s.message.removed, true); assert.equal(s.list.removed, true);
    assert.equal(s.main.focused, true);
});
test('navigation marks the current destination', () => {
    const s = setup(); assert.equal(s.active.getAttribute('aria-current'), 'page');
});
