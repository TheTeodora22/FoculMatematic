/* Executes actual training handlers in a minimal DOM harness, with deferred I/O.
   Run: node --test scripts/test_training_p0.cjs
   No browser or live database is touched. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/training.js'), 'utf8');
const start = source.indexOf('    function bindForm() {');
const end = source.indexOf('    function keepOnlyDigits(', start);
assert.ok(start >= 0 && end > start, 'Training handler harness must match the application entry points.');

function setup() {
    let submit, resolve, reject;
    const saved = new Promise((yes, no) => { resolve = yes; reject = no; });
    const painted = new Map();
    const renders = [];
    const errors = [];
    const form = {
        addEventListener(type, handler) { if (type === 'submit') submit = handler; },
        querySelector() { return {value: '7'}; },
    };
    const context = {
        data: {questions: [
            {id:1, status:'unanswered', correctOptionId:7},
            {id:2, status:'unanswered', correctOptionId:8},
        ]},
        currentIndex:0,
        cardEl: {querySelector(selector) { return selector === '.training-options-form' ? form : null; }},
        hideSaveError() {},
        showSaveError(message) { errors.push(message); },
        isSolved: q => q.status === 'correct',
        updateGridCell(index, status) { painted.set(index, status); },
        renderQuestion() {
            const question=context.data.questions[context.currentIndex];
            renders.push({index:context.currentIndex, status:question.status});
            if(question.saveError)context.showSaveError(question.saveError);
        },
        persistAnswer() { return saved; },
    };
    vm.createContext(context);
    vm.runInContext(source.slice(start, end), context);
    context.bindForm();
    assert.equal(typeof submit, 'function');
    return {context, painted, renders, errors, resolve, reject,
        submit: () => submit({preventDefault(){}})};
}

test('P0-17: rejected save leaves grid question retryable and unsolved', async () => {
    const h = setup();
    const pending = h.submit();
    h.reject(new Error('Offline fixture'));
    await pending;
    assert.deepEqual(h.errors, ['Offline fixture']);
    assert.notEqual(h.context.data.questions[0].status, 'correct', 'Unconfirmed progress is displayed as solved.');
    assert.notEqual(h.painted.get(0), 'correct');
});

test('P0-17: delayed grid response cannot repaint a different current question', async () => {
    const h = setup();
    const pending = h.submit();
    h.context.currentIndex = 1; // User navigates while the request is in flight.
    h.resolve({status:'correct', is_correct:true});
    await pending;
    assert.equal(h.context.data.questions[1].status, 'unanswered');
    assert.equal(h.renders.filter(r => r.index === 1).length, 0,
        'An old save triggered rendering of the newly selected question.');
});

test('P0-17: delayed interactive result updates the original grid cell only', async () => {
    const h = setup();
    const pending = h.context.submitInteractiveAnswer(h.context.data.questions[0], {value:42});
    h.context.currentIndex = 1;
    h.resolve({status:'correct', is_correct:true});
    await pending;
    assert.notEqual(h.painted.get(1), 'correct', 'The next question receives the previous answer status.');
    assert.equal(h.painted.get(0), 'correct');
});

test('control: successful save confirms the original answer', async () => {
    const h = setup();
    const pending = h.submit();
    h.resolve({status:'correct', is_correct:true, explanation:'fixture'});
    await pending;
    assert.equal(h.context.data.questions[0].status, 'correct');
    assert.equal(h.context.data.questions[0].explanation, 'fixture');
    assert.deepEqual(h.errors, []);
});

test('control: failed interactive save reports error without marking progress', async () => {
    const h = setup();
    const pending = h.context.submitInteractiveAnswer(h.context.data.questions[0], {value:42});
    h.reject(new Error('Offline fixture'));
    await pending;
    assert.equal(h.context.data.questions[0].status, 'unanswered');
    assert.equal(h.painted.size, 0);
    assert.deepEqual(h.errors, ['Offline fixture']);
});

test('unconfirmed answer remains unsolved and repeated submit sends only one request', async () => {
    const h=setup();let requests=0;
    const original=h.context.persistAnswer;
    h.context.persistAnswer=()=>{requests++;return original();};
    const pending=h.submit();
    assert.equal(h.context.data.questions[0].saving,true);
    assert.equal(h.context.data.questions[0].status,'unanswered');
    await h.submit();assert.equal(requests,1);
    h.resolve({status:'correct',is_correct:true});await pending;
    assert.equal(h.context.data.questions[0].saving,false);
});

test('after a rejected save the same selected answer can be retried successfully', async () => {
    const h=setup();const pending=h.submit();h.reject(new Error('Offline fixture'));await pending;
    assert.equal(h.context.data.questions[0].selectedOptionId,7);
    h.context.persistAnswer=async()=>({status:'correct',is_correct:true});
    await h.submit();
    assert.equal(h.context.data.questions[0].status,'correct');
    assert.equal(h.context.data.questions[0].saveError,'');
});

test('a previous question save error is stored without replacing the current question', async () => {
    const h=setup();const pending=h.submit();h.context.currentIndex=1;
    h.reject(new Error('Offline fixture'));await pending;
    assert.equal(h.context.data.questions[0].saveError,'Offline fixture');
    assert.equal(h.context.data.questions[1].status,'unanswered');
    assert.deepEqual(h.errors,[]);
    h.context.currentIndex=0;h.context.renderQuestion();
    assert.deepEqual(h.errors,['Offline fixture']);
});

test('malformed or contradictory server responses never mark the question solved', async () => {
    for(const response of [null,{}, {status:'correct',is_correct:false}]){
        const h=setup();const pending=h.submit();h.resolve(response);await pending;
        assert.equal(h.context.data.questions[0].status,'unanswered');
        assert.ok(h.context.data.questions[0].saveError.includes('confirmat'));
    }
});

test('rendering a pending answer disables controls and restores errors when returning',()=>{
    const controls=[{}],tabControls=[{setAttribute(k,v){this[k]=v;}}],errors=[];
    let pendingStatus;
    const question={text:'fixture',type:'multiple_choice',status:'unanswered',saving:true,saveError:'fixture offline'};
    const card={querySelectorAll(selector){return selector==='[tabindex]'?tabControls:controls;}};
    const context=vm.createContext({data:{questions:[question]},currentIndex:0,cardEl:card,
        escapeHtml:String,bindForm(){},feedbackHtml(){return '';},explanationHtml(){return '';},
        answerHtml(){return '';},updateSaveStatus(q){pendingStatus=q.saving;},updateProgress(){},updateArrows(){},updateGridCurrent(){},showSaveError:m=>errors.push(m)});
    const renderStart=source.indexOf('    function renderQuestion(');
    const renderEnd=source.indexOf('    function updateProgress(',renderStart);
    vm.runInContext(source.slice(renderStart,renderEnd),context);
    context.renderQuestion(null,false);
    assert.equal(controls[0].disabled,true);
    assert.equal(tabControls[0].tabindex,'-1');
    assert.equal(pendingStatus,true);
    assert.ok(!card.innerHTML.includes('Se salvează răspunsul'), 'Status belongs in the reserved live region, outside the rebuilt card.');
    assert.deepEqual(errors,['fixture offline']);
});
