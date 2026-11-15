const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
function setup() {
    const events={},attrs={};let focused;
    const button={dataset:{},focus(){focused='button';},addEventListener:(k,fn)=>events['button:'+k]=fn};
    const trigger={setAttribute:(k,v)=>attrs[k]=v,focus(){focused='trigger';},getBoundingClientRect:()=>({left:100,top:100}),addEventListener:(k,fn)=>events['trigger:'+k]=fn};
    const menu={hidden:true,style:{},offsetWidth:180,offsetHeight:54,contains:e=>e===button,addEventListener:(k,fn)=>events['menu:'+k]=fn};
    const image={dataset:{animatedSrc:'animated.gif'},getAttribute:()=> 'static.png'};
    const controls={'[data-motion-toggle]':button,'[data-motion-trigger]':trigger,'[data-motion-menu]':menu,'[data-motion-media]':image};
    vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/core/js/accessibility.js'),'utf8'),{
        document:{querySelector:s=>controls[s]||null,getElementById:()=>({}),addEventListener:(k,fn)=>events['document:'+k]=fn},
        window:{innerWidth:320,innerHeight:740,matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener:(k,fn)=>events['window:'+k]=fn}});
    return {events,attrs,menu,button,image,get focus(){return focused;}};
}
test('context action starts hidden, right click opens a viewport-clamped menu, activation closes it',()=>{
    const f=setup();assert.equal(f.menu.hidden,true);
    let prevented=false;f.events['trigger:contextmenu']({clientX:310,clientY:735,preventDefault(){prevented=true;}});
    assert.equal(prevented,true);assert.equal(f.menu.hidden,false);assert.equal(f.menu.style.left,'132px');assert.equal(f.menu.style.top,'678px');
    assert.equal(f.focus,'button');assert.equal(f.attrs['aria-expanded'],'true');
    f.events['button:click']();assert.equal(f.image.src,'static.png');assert.equal(f.menu.hidden,true);assert.equal(f.focus,'trigger');
});
test('Shift+F10 opens the menu and Escape restores focus without changing motion',()=>{
    const f=setup();f.events['trigger:keydown']({key:'F10',shiftKey:true,preventDefault(){}});
    assert.equal(f.menu.hidden,false);assert.equal(f.focus,'button');
    f.events['menu:keydown']({key:'Escape',preventDefault(){}});
    assert.equal(f.menu.hidden,true);assert.equal(f.focus,'trigger');assert.equal(f.image.src,'animated.gif');
});
test('outside click and scrolling dismiss without stealing focus',()=>{
    const f=setup();const open=()=>f.events['trigger:contextmenu']({clientX:100,clientY:100,preventDefault(){}});
    open();f.events['document:pointerdown']({target:{}});assert.equal(f.menu.hidden,true);assert.equal(f.focus,'button');
    open();f.events['window:scroll']();assert.equal(f.menu.hidden,true);assert.equal(f.attrs['aria-expanded'],'false');
});
