const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,'../static/core/js/training.js'),'utf8');
const start = source.indexOf('    function bindGeometryKeyboard(');
const end = source.indexOf('    function bindFactorBuilderForm(',start);
assert.ok(start >= 0 && end > start);

function fixture(mode='place_points', values='100,100') {
    const handlers = {}, attributes = {};
    const point = {dataset:{geometryPoint:'A'},classList:{add(){},remove(){}},
        addEventListener(type, fn){handlers[type]=fn;}, setAttribute(k,v){attributes[k]=v;}};
    const question = {status:'unanswered', answerValues:{A:values},
        interactive:{mode, points:[{name:'A',x:80,y:80}], answers:{membership:'on'}, line:{a:0,b:1,c:-90}}};
    const context = vm.createContext({data:{questions:[question]},currentIndex:0,isSolved:q=>q.status==='correct',setTimeout(){}});
    vm.runInContext(source.slice(start,end),context);
    context.bindGeometryForm({querySelectorAll(selector){return selector === '[data-geometry-point]' ? [point] : [];},addEventListener(){}});
    function key(key,props={}) {const event={key,preventDefault(){this.defaultPrevented=true;},...props};handlers.keydown(event);return event;}
    return {question,attributes,key};
}

test('keyboard moves geometry point without re-rendering or navigating',()=>{
    const f=fixture();
    assert.equal(f.key('ArrowRight').defaultPrevented,true);
    assert.equal(f.question.answerValues.A,'101,100');
    f.key('ArrowUp',{shiftKey:true});
    assert.equal(f.question.answerValues.A,'101,90');
    assert.equal(f.attributes.transform,'translate(101 90)');
});
test('geometry movement stays inside canvas bounds and ignores modified shortcuts',()=>{
    const f=fixture('place_points','425,15');
    f.key('ArrowRight');f.key('ArrowUp');
    assert.equal(f.question.answerValues.A,'425,15');
    f.key('ArrowLeft',{ctrlKey:true});
    assert.equal(f.question.answerValues.A,'425,15');
    f.question.status='correct';f.key('ArrowLeft');
    assert.equal(f.question.answerValues.A,'425,15');
});
test('Enter and Space apply the same target/line snap as pointer release',()=>{
    const target=fixture();target.key('Enter');
    assert.equal(target.question.answerValues.A,'80,80');
    const line=fixture('point_on_line','100,100');line.key(' ');
    assert.equal(line.question.answerValues.A,'100,90');
});
test('keyboard activation of an SVG choice restores focus to its replacement',()=>{
    let activate,focused=false,clicks=0;
    const original={addEventListener(type,fn){activate=fn;},hasAttribute(){return true;},
        getAttribute(){return 'A';},dispatchEvent(){clicks++;}};
    const replacement={getAttribute(){return 'A';},focus(){focused=true;}};
    const context=vm.createContext({isSolved:()=>false,MouseEvent:class {},
        cardEl:{querySelectorAll(){return [replacement];}}});
    vm.runInContext(source.slice(start,source.indexOf('    function bindGeometryForm(',start)),context);
    context.bindGeometryKeyboard({querySelectorAll(){return [original];}},{});
    activate({key:'Enter',preventDefault(){}});
    assert.equal(clicks,1);assert.equal(focused,true);
});
test('changing geometry range keeps focus on the same control after canvas rerender',()=>{
    const handlers={};let focused=false,rendered=0;
    const input={dataset:{geometryRange:'line_angle'},value:'45',addEventListener(type,fn){handlers[type]=fn;}};
    const replacement={dataset:{geometryRange:'line_angle'},focus(){focused=true;}};
    const question={status:'unanswered',answerValues:{}};
    const context=vm.createContext({data:{questions:[question]},currentIndex:0,isSolved:()=>false,
        renderQuestion(){rendered++;},cardEl:{querySelectorAll(){return [replacement];}}});
    vm.runInContext(source.slice(start,end),context);
    context.bindGeometryForm({querySelectorAll(selector){return selector==='[data-geometry-range]'?[input]:[];},
        querySelector(){return {};},addEventListener(){}});
    handlers.input();handlers.change();
    assert.equal(question.answerValues.line_angle,'45');assert.equal(rendered,1);assert.equal(focused,true);
});
