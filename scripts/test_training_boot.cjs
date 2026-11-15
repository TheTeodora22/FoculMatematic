const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname,'../static/core/js');
const boot = fs.readFileSync(path.join(root,'training-boot.js'),'utf8');

function fixture() {
    const timers=new Map(), listeners={};let reloads=0;
    function element() {
        const classes=new Set();
        return {classes,hidden:true,style:{},attrs:{},children:[],
            classList:{add:c=>classes.add(c),remove:c=>classes.delete(c)},
            setAttribute(k,v){this.attrs[k]=v;},replaceChildren(){this.children=[];},
            append(...items){this.children.push(...items);},addEventListener(type,fn){this[type]=fn;}};
    }
    const page=element(),loader=element();page.classes.add('training-page--loading');
    const window={setTimeout(fn){timers.set(1,fn);return 1;},clearTimeout(id){timers.delete(id);},
        addEventListener(type,fn){listeners[type]=fn;},location:{reload(){reloads++;}}};
    const document={documentElement:element(),querySelector:()=>page,
        getElementById:id=>id==='training-loader'?loader:null,createElement:element};
    const context=vm.createContext({window,document});vm.runInContext(boot,context);
    return {context,window,document,page,loader,listeners,timers,get reloads(){return reloads;}};
}
test('missing training script produces a visible recoverable error',()=>{
    const f=fixture();
    f.listeners.error({target:{tagName:'SCRIPT',hasAttribute:key=>key==='data-training-script'}});
    assert.equal(f.page.classes.has('training-page--loading'),false);
    assert.equal(f.loader.hidden,false);assert.equal(f.loader.attrs.role,'alert');
    assert.equal(f.loader.children[1].textContent,'Reîncarcă pagina');
    f.loader.children[1].click();assert.equal(f.reloads,1);
});
test('hung script times out and exposes the server-rendered page',()=>{
    const f=fixture();f.timers.get(1)();
    assert.equal(f.page.classes.has('training-page--loading'),false);
    assert.equal(f.loader.children.length,2);
});
test('training runtime error is handled while unrelated script failures are ignored',()=>{
    const f=fixture();f.listeners.error({filename:'/static/other.js'});
    assert.equal(f.loader.children.length,0);
    f.listeners.error({filename:'/static/core/js/training.js?v=1'});
    assert.equal(f.loader.children.length,2);
});
test('successful initialization cancels timeout and ignores subsequent fallback attempts',()=>{
    const f=fixture();f.window.fmTrainingBoot.ready();
    assert.equal(f.timers.size,0);f.window.fmTrainingBoot.fail();
    assert.equal(f.loader.children.length,0);
});
test('malformed payload reports the parse failure rather than a temporal-dead-zone exception',()=>{
    const f=fixture();const original=f.document.getElementById;
    f.document.getElementById=id=>id==='training-data'?{textContent:'invalid-json'}:original(id);
    assert.doesNotThrow(()=>vm.runInContext(fs.readFileSync(path.join(root,'training.js'),'utf8'),f.context));
    assert.equal(f.loader.children[0].textContent,'Nu am putut citi datele antrenării.');
});
