const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vectors = require('../static/core/js/vector-workbench.js');
const examples = JSON.parse(fs.readFileSync(path.join(__dirname,'../docs/vectori_in_plan_interactive.examples.json'),'utf8')).examples;
const configOf=example=>Object.fromEntries(Object.entries(example).filter(([key])=>!['id','lesson','catalog','prompt','expected'].includes(key)));

test('all 12 approved modes render without needing a hidden answer key', () => {
    for(const example of examples) {
        const html=vectors.render({id:example.id,status:'unanswered',interactive:configOf(example)});
        assert.ok(html.includes('data-vector-workbench'),example.id);
        assert.ok(html.includes('data-vector-svg'),example.id);
        assert.ok(!html.includes('undefined'),example.id);
        assert.ok(!html.includes('NaN'),example.id);
        assert.ok(!html.includes('expected'),example.id);
        assert.ok(html.includes('role="status"'),example.id);
    }
});

test('screen coordinates preserve mathematical y-up and round trip under scaling', () => {
    const area={min:-10,max:10};
    assert.deepEqual(vectors.toScreen([0,0],area),[320,220]);
    assert.ok(vectors.toScreen([0,3],area)[1]<220);
    for(const point of [[3,2],[-6,-2],[4/3,-2/3],[0,0]]) {
        const restored=vectors.fromScreen(vectors.toScreen(point,area),area);
        point.forEach((value,i)=>assert.ok(Math.abs(value-restored[i])<1e-10));
    }
});

test('keyboard transport validates a displacement relative to its given origin', () => {
    const config=configOf(examples.find(e=>e.id==='V03'));
    const state=vectors.createState(config);
    assert.equal(vectors.moveByKey(config,state,'endpoint','ArrowRight'),true);
    assert.equal(vectors.moveByKey(config,state,'endpoint','ArrowUp',true),true);
    assert.deepEqual(state.endpoint,['1','2']);
    assert.deepEqual(vectors.answer(config,state),{endpoint:['1','2']});
    assert.equal(vectors.moveByKey(config,state,'endpoint','Home'),false);
});

test('position vector handle maps screen endpoint back to displacement', () => {
    const config=configOf(examples.find(e=>e.id==='V04'));
    const state=vectors.createState(config);
    vectors.move(config,state,'vector',[4,3]);
    assert.deepEqual(vectors.answer(config,state),{vector:['3','5']});
    assert.deepEqual(vectors.endpoint(config,state,'vector'),[4,3]);
});

test('head-to-tail answer requires both independently constructed values', () => {
    const config=configOf(examples.find(e=>e.id==='V07'));
    const state=vectors.createState(config);
    assert.notDeepEqual(state.tail,state.vector,'Initial handles must not overlap.');
    vectors.move(config,state,'tail',[3,1]);
    vectors.move(config,state,'vector',[2,3]);
    state.unexpected='never submitted';
    assert.deepEqual(vectors.answer(config,state),{tail:['3','1'],vector:['2','3']});
});

test('selection toggles candidates without sending internal UI properties', () => {
    const config=configOf(examples[0]),state=vectors.createState(config);
    vectors.toggleCandidate(state,'CD');vectors.toggleCandidate(state,'DC');vectors.toggleCandidate(state,'DC');
    assert.deepEqual(vectors.answer(config,state),{selected:['CD']});
});

test('fractional coefficients stay exact in submission and recombine in oblique basis', () => {
    const config=configOf(examples.find(e=>e.id==='V12'));
    const state={coefficients:['4/3','−2/3']};
    assert.deepEqual(vectors.answer(config,state),{coefficients:['4/3','-2/3']});
    const parts=vectors.decomposition(config,state);
    assert.deepEqual(parts.sum,[6,0]);
    assert.deepEqual(parts.first,[8,4]);
    assert.deepEqual(parts.second,[-2,-4]);
});

test('numeric syntax is canonicalized exactly and invalid/nonfinite inputs rejected', () => {
    for(const [raw,canonical] of [['0,5','1/2'],['1.5 / -0.5','-3'],['−2/3','-2/3'],['4/-6','-2/3'],['0','0'],['-0','0'],['.25','1/4']])
        assert.equal(vectors.canonicalNumber(raw),canonical);
    for(const raw of ['',true,null,NaN,Infinity,'NaN','1/0','1e2','0.00000001','x','1/'.repeat(50)])
        assert.equal(vectors.numeric(raw),null,String(raw));
});

test('zero construction is shown as a labelled point without artificial direction', () => {
    const config=configOf(examples.find(e=>e.id==='V08'));
    const markup=vectors.scene(config,{vector:['0','0']},'zero');
    assert.ok(markup.includes('construcția ta = 0'));
    const zeroGroup=markup.match(/<g class="vw-vector vw-answer">(.*?)<\/g>/)[1];
    assert.ok(zeroGroup.includes('<circle'));
    assert.ok(!zeroGroup.includes('<line'));
});

test('solved refresh restores server-confirmed state and disables editing', () => {
    const question={id:'saved',status:'correct',interactive:configOf(examples.find(e=>e.id==='V12')),
        solvedValues:{coefficients:['4/3','-2/3']}};
    const markup=vectors.render(question);
    assert.deepEqual(question.vectorState,{coefficients:['4/3','-2/3']});
    assert.ok(markup.includes('value="4/3" disabled'));
    assert.ok(!markup.includes('type="submit"'));
});

function harness(config) {
    const listeners={},status={},error={},captured=[];
    const handle={dataset:{vectorHandle:'vector'},focus(){}};
    const svg={innerHTML:'',addEventListener(name,callback){listeners[name]=callback;},
        querySelector(){return handle;},querySelectorAll(){return [];},getBoundingClientRect(){return {width:640};},
        createSVGPoint(){return {x:0,y:0,matrixTransform(){return {x:this.x,y:this.y};}};},
        getScreenCTM(){return {inverse(){return {};}};},setPointerCapture(){},hasPointerCapture(){return true;},releasePointerCapture(){}};
    const fields=Object.entries(vectors.createState(config)).flatMap(([key,values])=>Array.isArray(values)&&key!=='selected'?values.map((value,index)=>({dataset:{vectorField:`${key}:${index}`},value,addEventListener(){}})):[]);
    let submitHandler;
    const form={ownerDocument:{activeElement:null},
        querySelector(selector){return selector==='[data-vector-svg]'?svg:selector==='[data-vector-status]'?status:error;},
        querySelectorAll(selector){return selector==='[data-vector-field]'?fields:[];},
        addEventListener(name,callback){if(name==='submit')submitHandler=callback;}};
    const question={id:1,status:'unanswered',interactive:config,vectorState:vectors.createState(config)};
    vectors.bind(form,question,async values=>captured.push(values));
    function key(key,extra={}) {const event={key,target:{closest(){return handle;}},preventDefault(){this.prevented=true;},stopPropagation(){this.stopped=true;},...extra};listeners.keydown(event);return event;}
    return {question,listeners,key,handle,fields,captured,status,error,submit:()=>submitHandler({preventDefault(){}})};
}

test('board arrow handling stops training navigation but preserves modified shortcuts', () => {
    const h=harness(configOf(examples.find(e=>e.id==='V08')));
    const moved=h.key('ArrowRight');
    assert.equal(moved.prevented,true);assert.equal(moved.stopped,true);
    assert.deepEqual(h.question.vectorState.vector,['1','0']);
    for(const modifier of ['ctrlKey','altKey','metaKey']) {
        const untouched=h.key('ArrowRight',{[modifier]:true});
        assert.ok(!untouched.prevented);
        assert.deepEqual(h.question.vectorState.vector,['1','0']);
    }
});

test('pointer placement snaps grid units, submits exact state, and Escape cancels drag', async () => {
    const h=harness(configOf(examples.find(e=>e.id==='V08')));
    const target={closest(){return h.handle;}};
    h.listeners.pointerdown({target,pointerId:1,preventDefault(){}});
    const [clientX,clientY]=vectors.toScreen([-6,-2],vectors.bounds(h.question.interactive));
    h.listeners.pointerup({pointerId:1,clientX,clientY});
    await h.submit();
    assert.deepEqual(h.captured,[{values:{vector:['-6','-2']}}]);
    h.listeners.pointerdown({target,pointerId:2,preventDefault(){}});
    h.listeners.pointermove({clientX:320,clientY:220});
    h.key('Escape');
    assert.deepEqual(h.question.vectorState.vector,['-6','-2']);
});

test('invalid typed vector does not render a misleading zero or submit', async () => {
    const h=harness(configOf(examples.find(e=>e.id==='V08')));
    h.question.vectorState.vector=['not-a-number','2'];
    assert.deepEqual(vectors.endpoint(h.question.interactive,h.question.vectorState,'vector'),[null,null]);
    await h.submit();
    assert.equal(h.captured.length,0);
    assert.ok(h.error.textContent.includes('valid'));
});

test('all approved construction endpoints fit the mathematical board', () => {
    for(const example of examples) {
        const config=configOf(example),area=vectors.bounds(config),expected=example.expected;
        const points=[];
        if(expected.endpoint) points.push(expected.endpoint);
        if(expected.midpoint) points.push(expected.midpoint);
        if(expected.vector) {
            const start=vectors.origin(config,'vector');
            points.push(expected.vector.map((value,index)=>vectors.numeric(value)+start[index]));
        }
        if(expected.coefficients) points.push(config.u.map(value=>vectors.numeric(value)*vectors.numeric(expected.coefficients[0])));
        for(const point of points) {
            const [x,y]=vectors.toScreen(point,area);
            assert.ok(x>=15&&x<=625&&y>=15&&y<=425,`${example.id}: construction endpoint is clipped`);
        }
    }
});

test('arrowheads stay small and directional; opposite segment labels are separated', () => {
    const config=configOf(examples[0]),markup=vectors.scene(config,vectors.createState(config),'labels');
    assert.ok(markup.includes('markerUnits="userSpaceOnUse"'));
    assert.ok(!markup.includes('context-stroke'));
    for(const match of markup.matchAll(/markerWidth="([\d.]+)" markerHeight="([\d.]+)"/g)) {
        assert.ok(Number(match[1])<=12&&Number(match[2])<=10);
    }
    const position=name=>markup.match(new RegExp(`<text class="vw-label" x="([^"]+)" y="([^"]+)"[^>]*>${name}</text>`)).slice(1);
    assert.notDeepEqual(position('CD'),position('DC'));
});

test('initial basis view shows one zero construction instead of three overlapping zero annotations', () => {
    const config=configOf(examples.find(e=>e.id==='V12'));
    const markup=vectors.scene(config,vectors.createState(config),'initial');
    assert.ok(markup.includes('construcția ta = 0'));
    assert.ok(!markup.includes('a·u = 0'));
    assert.ok(!markup.includes('b·v = 0'));
});

test('responsive board redraws only on width change and disconnects when question is replaced', () => {
    let resizeCallback,removalCallback,width=390,disconnected=0,mutationDisconnected=0,refreshes=0;
    class ResizeObserver {
        constructor(callback) {resizeCallback=callback;}
        observe() {}
        disconnect() {disconnected++;}
    }
    class MutationObserver {
        constructor(callback) {removalCallback=callback;}
        observe() {}
        disconnect() {mutationDisconnected++;}
    }
    const form={isConnected:true,ownerDocument:{defaultView:{ResizeObserver,MutationObserver},documentElement:{}}};
    const svg={getBoundingClientRect:()=>({width})};
    const dispose=vectors.watchResize(form,svg,()=>refreshes++);
    resizeCallback();
    assert.equal(refreshes,0,'Initial notification should not redraw identical width.');
    width=872;resizeCallback();
    assert.equal(refreshes,1,'Mobile-to-desktop resize must recompute labels and marker scale.');
    resizeCallback();
    assert.equal(refreshes,1,'Unchanged width should not cause a redraw loop.');
    width=0;resizeCallback();
    assert.equal(refreshes,1,'Hidden board should not redraw at zero width.');
    form.isConnected=false;removalCallback();
    assert.equal(disconnected,1);
    assert.equal(mutationDisconnected,1);
    dispose(); // disposal is harmless if invoked more than once
    assert.equal(disconnected,1);
});

test('solved board rescales actual labels and markers after rotation without altering its answer', () => {
    let width=390,resizeCallback;
    const properties={};
    const svg={innerHTML:'',style:{setProperty:(key,value)=>properties[key]=value},
        getBoundingClientRect:()=>({width}),querySelectorAll:()=>[]};
    class ResizeObserver {constructor(callback){resizeCallback=callback;} observe(){} disconnect(){}}
    const form={isConnected:true,ownerDocument:{activeElement:null,defaultView:{ResizeObserver}},
        querySelector:selector=>selector==='[data-vector-svg]'?svg:{},querySelectorAll:()=>[]};
    const config=configOf(examples.find(e=>e.id==='V12'));
    const question={id:'resize-solved',status:'correct',interactive:config,solvedValues:{coefficients:['4/3','-2/3']}};
    vectors.render(question);
    vectors.bind(form,question,()=>{throw new Error('Resize must never submit an answer.');});
    const mobileFont=parseFloat(properties['--vw-label-size']);
    width=872;resizeCallback();
    const desktopFont=parseFloat(properties['--vw-label-size']);
    assert.ok(mobileFont>desktopFont);
    assert.equal(desktopFont,13);
    assert.ok(svg.innerHTML.includes('markerWidth="10" markerHeight="8"'));
    assert.deepEqual(question.vectorState,{coefficients:['4/3','-2/3']});
    form.isConnected=false;resizeCallback();
});
