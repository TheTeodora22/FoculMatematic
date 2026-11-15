const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
test('general pages avoid exercise CSS and mathematical engine; asset budgets remain small',()=>{
    const base=read('templates/base.html');
    assert.doesNotMatch(base,/katex\.min|training-exercises\.css/);
    assert.ok(fs.statSync(path.join(root,'static/core/css/fm-app.css')).size<50000);
    assert.ok(fs.statSync(path.join(root,'static/core/img/5-cell.webm')).size<200000);
    assert.doesNotMatch(read('static/core/css/fm-app.css'),/@import/);
    assert.ok(base.indexOf('block exercise_styles')<base.indexOf('frontend-polish.css'));
    for(const file of ['math_demo','quizzes/quiz_take','quizzes/quiz_result','quizzes/generated_quiz','quizzes/generated_quiz_result','quizzes/training']) {
        assert.match(read('templates/'+file+'.html'),/includes\/math_assets\.html/);
    }
});
function video(reduced, reject=false) {
    let src=null,plays=0,pauses=0;
    const events={},button={dataset:{},addEventListener:(k,fn)=>events[k]=fn},status={};
    const media={tagName:'VIDEO',dataset:{animatedSrc:'animation.webm'},getAttribute:()=>src,
        set src(v){src=v;},play(){plays++;return reject?Promise.reject(Error('blocked')):Promise.resolve();},pause(){pauses++;}};
    vm.runInNewContext(read('static/core/js/accessibility.js'),{
        document:{querySelector:s=>s.includes('toggle')?button:s.includes('media')?media:null,getElementById:()=>status},
        window:{matchMedia:()=>({matches:reduced,addEventListener(){}})}});
    return {events,button,status,get src(){return src;},get plays(){return plays;},get pauses(){return pauses;}};
}
test('reduced motion does not request the animation; explicit play and pause retain control',()=>{
    const f=video(true);assert.equal(f.src,null);assert.equal(f.plays,0);
    f.events.click();assert.equal(f.src,'animation.webm');assert.equal(f.plays,1);
    f.events.click();assert.equal(f.button.dataset.paused,'true');assert.equal(f.pauses,2);
});
test('autoplay rejection recovers without an unhandled rejection or a false running state',async()=>{
    const f=video(false,true);await Promise.resolve();
    assert.equal(f.button.dataset.paused,'true');assert.match(f.status.textContent,/nu a pornit/);
});
test('a stale rejected play cannot override a later user pause',async()=>{
    const f=video(false,true);f.events.click();await Promise.resolve();
    assert.equal(f.status.textContent,'Animație oprită.');
});
test('math observer ignores unrelated UI updates and batches only affected formula roots',()=>{
    let callback,frame,scans=0,frames=0,observes=0;
    const math={isConnected:true,closest:()=>math,nodeType:1};
    const container={querySelectorAll(){scans++;return [math];}};
    class Observer {constructor(fn){callback=fn;}observe(){observes++;}disconnect(){}}
    vm.runInNewContext(read('static/core/js/math-rendering.js'),{window:{},document:{readyState:'complete',querySelector:()=>container},
        MutationObserver:Observer,requestAnimationFrame(fn){frame=fn;frames++;}});
    const unrelated={nodeType:1,closest:()=>null,querySelectorAll:()=>[]};
    callback([{type:'childList',target:unrelated,addedNodes:[unrelated]}]);assert.equal(frames,0);
    callback([{type:'characterData',target:{nodeType:3,parentElement:math}}]);
    callback([{type:'childList',target:math,addedNodes:[]}]);assert.equal(frames,1);
    frame();assert.equal(scans,1);assert.equal(observes,2);
    math.isConnected=false;callback([{type:'childList',target:math,addedNodes:[]}]);frame();assert.equal(scans,1);
});
