const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
function motion(reduced=false) {
    const events={},status={},button={dataset:{},addEventListener:(type,fn)=>events[type]=fn};
    const image={dataset:{animatedSrc:'animated.gif'},getAttribute:()=> 'static.png'};
    const preference={matches:reduced,addEventListener:(type,fn)=>events.preference=fn};
    vm.runInNewContext(fs.readFileSync(path.join(root,'static/core/js/accessibility.js'),'utf8'),{
        document:{querySelector:selector=>selector.includes('toggle')?button:selector.includes('media')||selector.includes('img')?image:null,getElementById:()=>status},
        window:{matchMedia:()=>preference}});
    return {button,image,status,events,preference};
}
test('decorative animation can pause and resume, with an announced state',()=>{
    const f=motion();assert.equal(f.image.src,'animated.gif');assert.equal(f.button.hidden,false);
    f.events.click();assert.equal(f.image.src,'static.png');assert.equal(f.button.dataset.paused,'true');
    assert.equal(f.status.textContent,'Animație oprită.');
    f.events.click();assert.equal(f.image.src,'animated.gif');assert.equal(f.button.dataset.paused,'false');
});
test('reduced motion begins static and a live preference change stops animation',()=>{
    const f=motion(true);assert.equal(f.image.src,'static.png');
    f.events.click();assert.equal(f.image.src,'animated.gif');
    f.events.preference();assert.equal(f.image.src,'static.png');
    f.preference.matches=false;f.events.preference();assert.equal(f.image.src,'static.png');
});
const training=fs.readFileSync(path.join(root,'static/core/js/training.js'),'utf8');
function extract(from,to) {return training.slice(training.indexOf('    function '+from+'('),training.indexOf('    function '+to+'('));}
test('chart controls are exposed as a group, selected state is explicit, solved charts are images',()=>{
    let solved=false;
    const c=vm.createContext({isSolved:()=>solved,escapeHtml:String});
    vm.runInContext(extract('statisticsChartSvg','statisticsChartHtml'),c);
    const q={interactive:{mode:'read_bar',values:[2,3],labels:['A','B'],max_value:5,step:1},answerValues:{selected:'1'}};
    let html=c.statisticsChartSvg(q);
    assert.match(html,/role="group"/);assert.match(html,/aria-pressed="true" data-stat-choice="1"/);
    solved=true;html=c.statisticsChartSvg(q);assert.match(html,/role="img"/);assert.doesNotMatch(html,/role="button"/);
    solved=false;q.interactive.mode='build_bar';html=c.statisticsChartSvg(q);
    assert.doesNotMatch(html,/tabindex="0"/);assert.doesNotMatch(c.statisticsChartSvg(q,false,false),/statistics-chart-scroll/);
});
test('keyboard chart selection keeps the same focused control and updates pressed state',()=>{
    const marks=[0,1].map(i=>({dataset:{statChoice:String(i)},attrs:{},events:{},classList:{toggle(){}},
        setAttribute(k,v){this.attrs[k]=v;},addEventListener(k,v){this.events[k]=v;}}));
    const q={interactive:{answers:{selected:1}},answerValues:{}};
    const form={querySelectorAll:s=>s==='[data-stat-choice]'?marks:[],addEventListener(){}};
    const c=vm.createContext({data:{questions:[q]},currentIndex:0,isSolved:()=>false});
    vm.runInContext(extract('bindStatisticsForm','bindAlgebraForm'),c);c.bindStatisticsForm(form);
    let prevented=false;marks[1].events.keydown({key:' ',preventDefault(){prevented=true;}});
    assert.equal(prevented,true);assert.equal(q.answerValues.selected,'1');
    assert.equal(marks[1].attrs['aria-pressed'],'true');assert.equal(marks[0].attrs['aria-pressed'],'false');
});
test('slider updates only the drawing, preserving the input and its event listener',()=>{
    const valueLabel={},events={},replaced=[];
    const input={dataset:{statRange:'value:0'},value:'2',closest:()=>({querySelector:()=>valueLabel}),addEventListener:(k,fn)=>events[k]=fn};
    const q={interactive:{mode:'build_bar',answers:{'value:0':3}},answerValues:{}};
    const form={querySelectorAll:s=>s==='[data-stat-range]'?[input]:[],querySelector:()=>({replaceWith:node=>replaced.push(node)}),addEventListener(){}};
    const c=vm.createContext({data:{questions:[q]},currentIndex:0,isSolved:()=>false,
        document:{createElement:()=>({firstElementChild:'svg'})},statisticsChartSvg:()=>'<svg></svg>'});
    vm.runInContext(extract('bindStatisticsForm','bindAlgebraForm'),c);c.bindStatisticsForm(form);
    events.input();input.value='3';events.input();
    assert.equal(q.answerValues['value:0'],'3');assert.equal(valueLabel.textContent,'3');assert.equal(replaced.length,2);
});
for (const scenario of ['same question','different question','disabled control','user moved focus']) {
    test('question repaint focus: '+scenario,()=>{
        const doc={body:{}};
        const original={tagName:'BUTTON',attributes:[{name:'data-bit-index',value:'0'}]};
        doc.activeElement=original;
        const focused=[];
        const replacement={tagName:'BUTTON',disabled:scenario==='disabled control',getAttribute:k=>k==='data-bit-index'?'0':null,focus:()=>focused.push('control')};
        const heading={focus:()=>focused.push('heading')};
        const card={_renderedQuestionIndex:scenario==='different question'?1:0,contains:e=>e===original,
            set innerHTML(value){doc.activeElement=doc.body;},querySelectorAll:()=>[replacement],querySelector:()=>heading};
        const context={document:doc,cardEl:card,data:{questions:[{text:'Test'}]},currentIndex:0,escapeHtml:String,
            feedbackHtml:()=>'',explanationHtml:()=>'',answerHtml:()=>'',
            bindForm:()=>{if(scenario==='user moved focus')doc.activeElement={isConnected:true};},
            updateSaveStatus(){},updateProgress(){},updateArrows(){},updateGridCurrent(){}};
        vm.runInNewContext(extract('renderQuestion','updateProgress')+';renderQuestion(null,false);',context);
        assert.deepEqual(focused,scenario==='same question'?['control']:scenario==='disabled control'?['heading']:[]);
    });
}
