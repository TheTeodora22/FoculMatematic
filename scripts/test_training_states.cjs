const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/training.js'), 'utf8');
function snippet(start, end) {return source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start)));}
function persistence(fetch) {
    const timers = new Map();
    const context = vm.createContext({fetch, AbortController, data: {submitUrl: '/test'},
        FormData: class {constructor() {this.values = new Map();} append(k,v) {this.values.set(k,v);}},
        getCsrfToken: () => 'fixture',
        window: {setTimeout(fn, delay) {timers.set(1, {fn, delay}); return 1;}, clearTimeout(id) {timers.delete(id);}},
    });
    vm.runInContext(snippet('    async function persistAnswer(', '    function bindForm('), context);
    return {context, timers, submit: () => context.persistAnswer({id: 1, type: 'multiple_choice'}, {optionId: 7})};
}
test('successful persistence preserves request fields and clears its timeout', async () => {
    let request;
    const h = persistence(async (_url, options) => {request = options; return {ok: true, json: async () => ({status: 'correct', is_correct: true})};});
    const result = await h.submit();
    assert.equal(result.is_correct, true); assert.equal(request.body.values.get('option_id'), '7');
    assert.equal(request.credentials, 'same-origin'); assert.equal(h.timers.size, 0);
});
test('a hung request aborts after the deadline and reports a retryable error', async () => {
    const h = persistence((_url, {signal}) => new Promise((_resolve, reject) => {
        signal.addEventListener('abort', () => reject(Object.assign(new Error(), {name: 'AbortError'})));
    }));
    const pending = h.submit();
    assert.equal(h.timers.get(1).delay, 20000); h.timers.get(1).fn();
    await assert.rejects(pending, /durează prea mult/); assert.equal(h.timers.size, 0);
});
test('network and malformed response errors are understandable and clear their timers', async () => {
    for (const [fetch, message] of [
        [async () => {throw new TypeError('Failed to fetch');}, /confirma salvarea/],
        [async () => ({ok: true, json: async () => {throw new SyntaxError('HTML');}}), /Serverul nu a confirmat/],
        [async () => ({ok: false, json: async () => ({error: 'Eroare server fixture'})}), /Eroare server fixture/],
    ]) {
        const h = persistence(fetch); await assert.rejects(h.submit(), message); assert.equal(h.timers.size, 0);
    }
});
test('a chosen option remains selected after saving or a failed save', () => {
    const context = vm.createContext({isSolved: q => q.status === 'correct', escapeHtml: String, trainingUrl: () => '/', currentIndex: 0});
    const start = source.indexOf('    function optionsHtml(');
    vm.runInContext(source.slice(start, source.indexOf('\n    function ', start + 1)), context);
    const html = context.optionsHtml({status: 'unanswered', options: [{id: 7, text: 'A'}, {id: 8, text: 'B'}]}, 7, false);
    assert.match(html, /value="7" checked/); assert.doesNotMatch(html, /value="8" checked/);
});
test('retry submits the current form and refuses stale or already saving questions', () => {
    let click, submits = 0;
    const context = vm.createContext({saveErrorEl: {querySelector: () => ({addEventListener(_type, fn) {click = fn;}})},
        escapeHtml: String, window: {location: {pathname: '/fixture'}}, currentIndex: 0,
        data: {questions: [{saving: false}, {saving: false}]}, cardEl: {querySelector: () => ({requestSubmit() {submits++;}})},
    });
    vm.runInContext(snippet('    function showSaveError(', '    function hideSaveError('), context);
    context.showSaveError('Fixture'); click(); assert.equal(submits, 1);
    context.data.questions[0].saving = true; click(); assert.equal(submits, 1);
    context.currentIndex = 1; click(); assert.equal(submits, 1);
});
test('reserved live status distinguishes pending, failed, and confirmed results', () => {
    const status = {};
    const context = vm.createContext({saveStatusEl: status});
    vm.runInContext(snippet('    function updateSaveStatus(', '    function showSaveError('), context);
    context.updateSaveStatus({saving: true}); assert.match(status.textContent, /Se salvează/);
    context.updateSaveStatus({saveError: 'offline'}); assert.match(status.textContent, /nu a fost confirmată/);
    context.updateSaveStatus({status: 'correct'}); assert.match(status.textContent, /salvat. Corect/);
    context.updateSaveStatus({status: 'unanswered'}); assert.equal(status.textContent, '');
});
