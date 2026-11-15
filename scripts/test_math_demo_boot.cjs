const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/math-demo-boot.js'), 'utf8');
function setup() {
    const classes = new Set(), timers = new Map(), events = {};
    const panel = {hidden: true};
    const document = {documentElement: {classList: {add: c => classes.add(c), remove: c => classes.delete(c)}},
        getElementById: () => panel, addEventListener() {}};
    const window = {setTimeout(fn) {timers.set(1, fn); return 1;}, clearTimeout(id) {timers.delete(id);},
        addEventListener(type, handler) {events[type] = handler;}};
    vm.runInNewContext(source, {document, window});
    return {classes, timers, events, panel, boot: window.fmMathBoardsBoot};
}
test('failed graph script shows a recoverable error and stops loading', () => {
    const f = setup(); f.events.error({target: {tagName: 'SCRIPT', hasAttribute: () => true}});
    assert.equal(f.panel.hidden, false); assert.equal(f.classes.has('fm-boards-loading'), false);
    assert.equal(f.timers.size, 0);
});
test('hung graph loading times out, while late successful initialization can recover', () => {
    const f = setup(); f.timers.get(1)(); assert.equal(f.panel.hidden, false);
    f.boot.ready(); assert.equal(f.panel.hidden, true); assert.equal(f.timers.size, 0);
});
test('successful initialization ignores a late fallback', () => {
    const f = setup(); f.boot.ready(); f.boot.fail();
    assert.equal(f.panel.hidden, true); assert.equal(f.classes.has('fm-boards-loading'), false);
});
test('unrelated script errors do not disable the graphs', () => {
    const f = setup(); f.events.error({filename: '/other.js'});
    assert.equal(f.panel.hidden, true); assert.equal(f.classes.has('fm-boards-loading'), true);
});
