const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/training.js'), 'utf8');

function load(name, next, context) {
    const start = source.indexOf(`    function ${name}(`);
    const end = source.indexOf(`    function ${next}(`, start);
    assert.ok(start >= 0 && end > start);
    vm.runInContext(source.slice(start, end), context);
}

test('percent slider has a visible associated label and percentage value', () => {
    const context = vm.createContext({isSolved:q => q.status === 'correct'});
    load('fractionPercentHtml', 'answerHtml', context);
    for (const status of ['unanswered', 'correct']) {
        const html = context.fractionPercentHtml({status,
            interactive:{mode:'slider', initial:25, answers:{percent:75}}});
        const id = html.match(/<input id="([^"]+)" type="range"/)[1];
        assert.ok(html.includes(`<label for="${id}">Procent ales</label>`));
        assert.ok(html.includes(`aria-valuetext="${status === 'correct' ? 75 : 25}%"`));
    }
});

test('moving slider updates both visual and accessible percentages', () => {
    let handler;
    const attrs = {};
    const slider = {value:'40', addEventListener(type, callback) {if(type === 'input') handler=callback;},
        setAttribute(key, value) {attrs[key]=value;}};
    const display = {};
    const question = {answerValues:{}};
    const context = vm.createContext({data:{questions:[question]}, currentIndex:0,
        isSolved:() => false});
    load('bindFractionPercentForm', 'bindParenthesesForm', context);
    context.bindFractionPercentForm({
        querySelectorAll(){return [];},
        addEventListener(){},
        querySelector(selector){return selector === '[data-percent-slider]' ? slider : display;},
    });
    for (const value of ['0','65','100']) {
        slider.value=value;
        handler();
        assert.equal(attrs['aria-valuetext'], `${value}%`);
        assert.equal(display.textContent, `${value}%`);
        assert.equal(question.answerValues.percent, value);
    }
});
