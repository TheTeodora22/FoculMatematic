const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/core/js/responsive.js'), 'utf8');
function region(width=240, content=640, attrs={}) {
    return {clientWidth: width, scrollWidth: content, isConnected: true, dataset: {}, scrollLeft: 0,
        attrs: {...attrs}, events: {}, content: {},
        getAttribute(name) {return this.attrs[name] ?? null;}, setAttribute(name,value) {this.attrs[name]=value;},
        removeAttribute(name) {delete this.attrs[name];}, addEventListener(type,fn) {this.events[type]=fn;},
        before(hint) {this.hint=hint; this.hints=(this.hints||0)+1;}, querySelector() {return this.content;}};
}
function setup(initial=region()) {
    let nodes=[initial], resize, mutation;
    const observed=new Set(), events={}, location={pathname:'/question/1/'};
    class ResizeObserver {
        constructor(fn) {resize=fn;} observe(el) {observed.add(el);} unobserve(el) {observed.delete(el);}
    }
    class MutationObserver {constructor(fn) {mutation=fn;} observe() {}}
    const document={querySelectorAll:()=>nodes, getElementById:()=>({}), createElement:()=>({})};
    const window={location,addEventListener(type,fn) {events[type]=fn;}};
    vm.runInNewContext(source,{window,document,ResizeObserver,MutationObserver});
    return {initial,events,observed,location,resize:()=>resize(),
        replace(next) {initial.isConnected=false;nodes=[next];mutation();}};
}
test('actual overflow becomes keyboard reachable with a visible explanation',()=>{
    const f=setup(), e=f.initial;
    assert.equal(e.attrs.tabindex,'0');assert.equal(e.attrs.role,'region');
    assert.equal(e.dataset.horizontalScroll,'true');assert.equal(e.hint.hidden,false);
    assert.ok(f.observed.has(e));assert.ok(f.observed.has(e.content));
});
test('wide layouts remove generated focus stops while preserving existing semantics',()=>{
    const e=region(240,640,{'aria-label':'Datele lecției'}),f=setup(e);
    e.clientWidth=700;f.resize();
    assert.equal(e.attrs.tabindex,undefined);assert.equal(e.attrs.role,undefined);
    assert.equal(e.attrs['aria-label'],'Datele lecției');assert.equal(e.hint.hidden,true);
    f.resize();assert.equal(e.hints,1);
});
test('horizontal arrows keep native scrolling and never reach exercise navigation',()=>{
    const f=setup();let stopped=false,prevented=false;
    f.initial.events.keydown({key:'ArrowRight',stopPropagation(){stopped=true;},preventDefault(){prevented=true;}});
    assert.equal(stopped,true);assert.equal(prevented,false);
    stopped=false;f.initial.events.keydown({key:'ArrowRight',ctrlKey:true,stopPropagation(){stopped=true;}});
    assert.equal(stopped,false);
});
test('question redraw restores horizontal position and disconnects the old region',()=>{
    const f=setup();f.initial.scrollLeft=180;f.initial.events.scroll();
    const next=region();f.replace(next);
    assert.equal(next.scrollLeft,180);assert.equal(f.observed.has(f.initial),false);
    assert.equal(f.observed.has(f.initial.content),false);
    next.scrollLeft=220;f.resize();assert.equal(next.scrollLeft,220,'Resize must not force an old scroll position.');
});
test('a different question starts with its own horizontal position',()=>{
    const f=setup();f.initial.scrollLeft=180;f.initial.events.scroll();
    f.location.pathname='/question/2/';const next=region();f.replace(next);
    assert.equal(next.scrollLeft,0);
});
test('keyboard focus reveals a table control hidden behind its sticky row heading',()=>{
    const e=region();e.classList={contains:name=>name==='criteria-table-wrap'};
    const header={getBoundingClientRect:()=>({right:160})};
    e.querySelector=selector=>selector==='th'?header:e.content;
    setup(e);e.scrollLeft=40;
    const control={matches:()=>true,getBoundingClientRect:()=>({left:140})};
    e.events.focusin({target:{closest:()=>control}});
    assert.equal(e.scrollLeft,12);
    e.scrollLeft=40;control.matches=()=>false;
    e.events.focusin({target:{closest:()=>control}});
    assert.equal(e.scrollLeft,40,'Pointer focus must not move the control away from the click.');
});
test('statistics graph retains its mathematical coordinates inside the responsive region',()=>{
    const training=fs.readFileSync(path.join(__dirname,'../static/core/js/training.js'),'utf8');
    const start=training.indexOf('    function statisticsChartSvg('),end=training.indexOf('    function statisticsChartHtml(',start);
    const context=vm.createContext({isSolved:()=>false,escapeHtml:String});
    vm.runInContext(training.slice(start,end),context);
    const html=context.statisticsChartSvg({interactive:{values:[10,20],mode:"read_bar", labels:['A','B'],max_value:20,step:5},answerValues:{}});
    assert.match(html,/class="statistics-chart-scroll"/);assert.match(html,/viewBox="0 0 620 300"/);
    assert.match(html,/x="101.5" y="136" width="176" height="118"/);
    assert.match(html,/data-stat-choice="0"/);
});
test('question navigation has visible numbers when hover tooltips are unavailable',()=>{
    const training=fs.readFileSync(path.join(__dirname,'../static/core/js/training.js'),'utf8');
    const start=training.indexOf('    function buildGrid('),end=training.indexOf('    function feedbackHtml(',start);
    const grid={};const context=vm.createContext({gridEl:grid,data:{questions:Array.from({length:315},()=>({status:'unanswered'}))},currentIndex:314,trainingUrl:i=>'/question/'+i});
    vm.runInContext(training.slice(start,end),context);context.buildGrid();
    assert.equal((grid.innerHTML.match(/>\d+<\/a>/g)||[]).length,315);
    assert.match(grid.innerHTML,/aria-label="Întrebarea 315"/);
    assert.match(grid.innerHTML,/aria-current="true">315<\/a>/);
});
