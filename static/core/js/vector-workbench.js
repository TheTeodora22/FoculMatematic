/* Vector construction uses mathematical coordinates, never pixel tolerances.
   Correct answers are computed only by the server. */
(function (root, factory) {
    const api = factory();
    if (typeof module === "object" && module.exports) module.exports = api;
    else root.fmVectorWorkbench = api;
})(typeof window === "object" ? window : globalThis, function () {
    "use strict";
    const WIDTH = 640, HEIGHT = 440, PAD = 36;
    const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
    const escape = text => String(text).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
    const add = (a,b) => [a[0]+b[0],a[1]+b[1]];
    function canonicalNumber(raw) {
        if (typeof raw === 'boolean' || raw === null || raw === undefined) return null;
        const value = String(raw).trim().replace(/−/g,'-').replace(',','.');
        if (!value || value.length > 32) return null;
        const pieces = value.split('/');
        if (pieces.length > 2 || pieces.some(v => !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(v.trim()))) return null;
        const decimal=part=>{const text=part.trim(),negative=text.startsWith('-'),digits=text.replace(/^[+-]/,'').split('.');return [BigInt((digits[0]||'0')+(digits[1]||''))*(negative?-1n:1n),10n**BigInt((digits[1]||'').length)];};
        const [an,ad]=decimal(pieces[0]),[bn,bd]=pieces.length===2?decimal(pieces[1]):[1n,1n];
        if(bn===0n) return null;
        let numerator=an*bd,denominator=ad*bn;
        if(denominator<0n){numerator=-numerator;denominator=-denominator;}
        const result=Number(numerator)/Number(denominator);
        if(!Number.isFinite(result)||Math.abs(result)>1000000) return null;
        let a=numerator<0n?-numerator:numerator,b=denominator;
        while(b!==0n){const next=a%b;a=b;b=next;}
        numerator/=a;denominator/=a;
        if(denominator>1000000n) return null;
        return denominator===1n?String(numerator):`${numerator}/${denominator}`;
    }
    function numeric(raw) {
        const exact=canonicalNumber(raw);
        if(exact===null) return null;
        const [a,b='1']=exact.split('/');
        return Number(a)/Number(b);
    }
    const vector = raw => Array.isArray(raw) && raw.length === 2 ? raw.map(numeric) : [null,null];
    const usable = raw => raw.every(value => value !== null && Number.isFinite(value));
    const short = value => Number.isInteger(value) ? String(value) : String(Number(value.toFixed(4)));
    const pair = raw => `(${raw.map(value => value === null ? '?' : short(value)).join('; ')})`;
    const resizeWatches=new Map();
    let removalWatch=null;
    function watchResize(form,svg,refresh) {
        resizeWatches.get(form)?.();
        const view=form.ownerDocument.defaultView;
        if(!view?.ResizeObserver) return ()=>{};
        let previousWidth=svg.getBoundingClientRect().width;
        let disposed=false;
        const watcher=new view.ResizeObserver(()=>{
            if(form.isConnected===false) {cleanup();return;}
            const width=svg.getBoundingClientRect().width;
            if(width>0&&Math.abs(width-previousWidth)>.5) {
                previousWidth=width;
                refresh();
            }
        });
        function cleanup() {
            if(disposed) return;
            disposed=true;
            watcher.disconnect();
            resizeWatches.delete(form);
            if(!resizeWatches.size&&removalWatch) {removalWatch.disconnect();removalWatch=null;}
        }
        resizeWatches.set(form,cleanup);
        if(!removalWatch&&view.MutationObserver) {
            removalWatch=new view.MutationObserver(()=>{
                for(const [element,dispose] of resizeWatches) if(element.isConnected===false) dispose();
            });
            removalWatch.observe(form.ownerDocument.documentElement,{childList:true,subtree:true});
        }
        watcher.observe(svg);
        return cleanup;
    }
    function bounds(config) {
        const points=[[0,0],...Object.values(config.points||{}),config.u,config.v,config.w].filter(Array.isArray).map(vector).filter(usable);
        if(config.mode==='scale_vector') points.push(vector(config.u).map(v=>v*numeric(config.scalar)));
        if(config.mode==='close_polygon') points.push(add(vector(config.u),vector(config.v)).map(v=>-v));
        if(config.mode==='head_to_tail') points.push([-5,-3],add([-5,-3],vector(config.v)),add(vector(config.u),vector(config.v)));
        if(config.mode==='translate_endpoint') points.push(add(vector(config.points[config.anchor]),vector(config.points[config.reference[1]]).map((v,i)=>v-vector(config.points[config.reference[0]])[i])));
        if(config.mode==='basis_decomposition') {
            // Reserve room for the construction, without displaying its answer.
            const u=vector(config.u),v=vector(config.v),w=vector(config.w),det=u[0]*v[1]-u[1]*v[0];
            if(det) points.push(u.map(x=>x*(w[0]*v[1]-w[1]*v[0])/det));
        }
        const xMin=Math.floor(Math.min(...points.map(p=>p[0])))-1,xMax=Math.ceil(Math.max(...points.map(p=>p[0])))+1;
        const yMin=Math.floor(Math.min(...points.map(p=>p[1])))-1,yMax=Math.ceil(Math.max(...points.map(p=>p[1])))+1;
        return {min:Math.min(xMin,yMin),max:Math.max(xMax,yMax),xMin,xMax,yMin,yMax};
    }
    const gridStep=area=>Math.max(1,10**Math.floor(Math.log10((area.max-area.min)/20)));
    function toScreen(point, area) {
        const xMin=area.xMin??area.min,xMax=area.xMax??area.max,yMin=area.yMin??area.min,yMax=area.yMax??area.max;
        const scale = Math.min((WIDTH-2*PAD)/(xMax-xMin),(HEIGHT-2*PAD)/(yMax-yMin));
        return [WIDTH/2+(point[0]-(xMin+xMax)/2)*scale,HEIGHT/2-(point[1]-(yMin+yMax)/2)*scale];
    }
    function fromScreen(point, area) {
        const xMin=area.xMin??area.min,xMax=area.xMax??area.max,yMin=area.yMin??area.min,yMax=area.yMax??area.max;
        const scale = Math.min((WIDTH-2*PAD)/(xMax-xMin),(HEIGHT-2*PAD)/(yMax-yMin));
        return [(point[0]-WIDTH/2)/scale+(xMin+xMax)/2,(HEIGHT/2-point[1])/scale+(yMin+yMax)/2];
    }
    function vectorKey(config) {
        if(config.mode==='translate_endpoint') return 'endpoint';
        if(config.mode==='midpoint') return 'midpoint';
        return 'vector';
    }
    function createState(config) {
        if(config.mode==='same_displacement') return {selected:[]};
        if(config.mode==='classify_vector') return {relation:''};
        if(config.mode==='basis_decomposition') return {coefficients:['0','0']};
        if(config.mode==='head_to_tail') return {tail:['-5','-3'],vector:['0','0']};
        return {[vectorKey(config)]:['0','0']};
    }
    function answer(config, state) {
        // Send only the documented answer shape, even if local state has UI fields.
        const keys = Object.keys(createState(config));
        return Object.fromEntries(keys.map(key=>[key,Array.isArray(state[key]) ? state[key].map(value=>key==='selected'?value:canonicalNumber(value)) : state[key]]));
    }
    function origin(config, key) {
        if(key==='endpoint') return vector(config.points[config.anchor]);
        if(config.mode==='position_from_origin') return vector(config.points[config.origin]);
        if(config.mode==='change_origin') return vector(config.points[config.new_origin]);
        return [0,0];
    }
    function endpoint(config, state, key) {
        const point = vector(state[key]);
        if(!usable(point)) return [null,null];
        return key==='vector' ? add(origin(config,key),point) : point;
    }
    function move(config, state, key, point, area=bounds(config)) {
        if(!own(state,key) || !Array.isArray(state[key])) return;
        const step=gridStep(area);
        let position = point.map((v,i)=>Math.max((i?area.yMin:area.xMin)??area.min,Math.min((i?area.yMax:area.xMax)??area.max,Math.round(v/step)*step)));
        if(key==='vector') {
            const start=origin(config,key);
            position=position.map((v,i)=>v-start[i]);
        }
        state[key]=position.map(String);
    }
    function moveByKey(config,state,key,keyboardKey,shift=false) {
        const offsets={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,1],ArrowDown:[0,-1]};
        if(!own(offsets,keyboardKey)) return false;
        const current=endpoint(config,state,key);
        if(!usable(current)) return false;
        const delta=offsets[keyboardKey].map(v=>v*(shift?2:1)*gridStep(bounds(config)));
        move(config,state,key,add(current,delta));
        return true;
    }
    function toggleCandidate(state,id) {
        const selected=new Set(state.selected);
        if(selected.has(id)) selected.delete(id); else selected.add(id);
        state.selected=[...selected];
    }
    function decomposition(config,state) {
        const coefficients=vector(state.coefficients),u=vector(config.u),v=vector(config.v);
        if(!usable(coefficients)||!usable(u)||!usable(v)) return null;
        return {first:u.map(x=>x*coefficients[0]),second:v.map(x=>x*coefficients[1]),
            sum:u.map((x,i)=>x*coefficients[0]+v[i]*coefficients[1])};
    }
    function scene(config,state,id,solved=false,fontSize=13) {
        const area=bounds(config),marker=`vector-arrow-${id}`;
        const xy=p=>toScreen(p,area);
        const occupied=[];
        for(const point of [...Object.values(config.points||{}).map(vector),...Object.keys(state).filter(k=>['vector','endpoint','midpoint','tail'].includes(k)).map(key=>endpoint(config,state,key))].filter(usable)) {
            const [x,y]=xy(point);occupied.push([x-10,y-10,x+10,y+10]);
        }
        function textLabel(text,candidates) {
            const width=String(text).length*fontSize*.58+4,height=fontSize+3;
            const options=candidates.map(([x,y,anchor='middle'])=>{
                const left=x-(anchor==='middle'?width/2:anchor==='end'?width:0),rect=[left,y-height,left+width,y+3];
                const overlap=occupied.reduce((sum,other)=>sum+Math.max(0,Math.min(rect[2],other[2])-Math.max(rect[0],other[0]))*Math.max(0,Math.min(rect[3],other[3])-Math.max(rect[1],other[1])),0);
                const outside=Math.max(0,4-rect[0])+Math.max(0,rect[2]-WIDTH+4)+Math.max(0,4-rect[1])+Math.max(0,rect[3]-HEIGHT+4);
                return {x,y,anchor,rect,score:overlap+outside*100};
            });
            options.sort((a,b)=>a.score-b.score);
            const best=options[0];occupied.push(best.rect);
            return `<text class="vw-label" x="${best.x}" y="${best.y}" text-anchor="${best.anchor}">${escape(text)}</text>`;
        }
        const pointLabel=(text,x,y)=>textLabel(text,[[x+14,y-12,'start'],[x+14,y+24,'start'],[x-14,y-12,'end'],[x-14,y+24,'end'],[x,y-24],[x,y+34],[x+28,y,'start'],[x-28,y,'end']]);
        const line=(a,b,label,style='given')=>{
            if(!usable(a)||!usable(b)) return '';
            const [x1,y1]=xy(a),[x2,y2]=xy(b);
            const zero=Math.hypot(b[0]-a[0],b[1]-a[1])<1e-10;
            if(zero) return `<g class="vw-vector vw-${style}"><circle cx="${x1}" cy="${y1}" r="5"/>${pointLabel(`${label} = 0`,x1,y1)}</g>`;
            const length=Math.hypot(x2-x1,y2-y1),nx=(y2-y1)/length,ny=-(x2-x1)/length,mx=(x1+x2)/2,my=(y1+y2)/2;
            const candidates=[18,-20,34,-36].map(distance=>[mx+nx*distance,my+ny*distance]);
            candidates.push([mx+nx*22+(x2-x1)*.16,my+ny*22+(y2-y1)*.16],[mx-nx*25-(x2-x1)*.16,my-ny*25-(y2-y1)*.16]);
            return `<g class="vw-vector vw-${style}"><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" marker-end="url(#${marker}-${style})"/>${textLabel(label,candidates)}</g>`;
        };
        const dot=(name,point)=>{const [x,y]=xy(point);return `<g class="vw-point"><circle cx="${x}" cy="${y}" r="2.5"/>${pointLabel(name,x,y)}</g>`;};
        const arrowScale=fontSize/13;
        let html=`<defs>${Object.entries({given:'#9cd7ef',candidate:'#e9ba68',selected:'#a0e1a8',target:'#d6b4fa',answer:'#ed8178'}).map(([style,color])=>`<marker id="${marker}-${style}" markerWidth="${10*arrowScale}" markerHeight="${8*arrowScale}" viewBox="0 0 10 8" preserveAspectRatio="none" refX="10" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L10,4 L0,8 Z" fill="${color}"/></marker>`).join('')}</defs>`;
        const tick=gridStep(area);
        const [left,top]=xy([area.xMin,area.yMax]),[right,bottom]=xy([area.xMax,area.yMin]),[zeroX,zeroY]=xy([0,0]);
        for(let i=Math.ceil(area.xMin/tick)*tick;i<=area.xMax;i+=tick) {
            const [x]=xy([i,0]);
            html+=`<path class="${i===0?'vw-axis':'vw-grid'}" d="M${x},${top}V${bottom}"/>`;
            if(i!==0) html+=`<text class="vw-tick" x="${x+2}" y="${zeroY+14}">${i}</text>`;
        }
        for(let i=Math.ceil(area.yMin/tick)*tick;i<=area.yMax;i+=tick) {
            const [,y]=xy([0,i]);
            html+=`<path class="${i===0?'vw-axis':'vw-grid'}" d="M${left},${y}H${right}"/>`;
            if(i!==0) html+=`<text class="vw-tick" x="${zeroX+4}" y="${y-2}">${i}</text>`;
        }
        html+=`<text class="vw-tick" x="${zeroX+5}" y="${zeroY+15}">O</text><text class="vw-tick" x="${right-12}" y="${zeroY-8}">x</text><text class="vw-tick" x="${zeroX+8}" y="${top+12}">y</text>`;
        const points=Object.fromEntries(Object.entries(config.points||{}).map(([name,p])=>[name,vector(p)]));
        for(const [name,point] of Object.entries(points)) html+=dot(name,point);
        if(config.reference) html+=line(points[config.reference[0]],points[config.reference[1]],config.reference.join(''));
        for(const candidate of config.candidates||[]) html+=line(points[candidate[0]],points[candidate[1]],candidate.join(''),state.selected?.includes(candidate.join(''))?'selected':'candidate');
        if(config.candidate) html+=line(points[config.candidate[0]],points[config.candidate[1]],config.candidate.join(''),'candidate');
        if(config.segment) html+=line(points[config.segment[0]],points[config.segment[1]],config.segment.join(''));
        if(config.u) html+=line([0,0],vector(config.u),'u');
        if(config.v && config.mode!=='head_to_tail') html+=line([0,0],vector(config.v),'v','candidate');
        if(config.mode==='head_to_tail') {
            // The transported vector keeps its given displacement; only its tail is selected.
            const tail=vector(state.tail);
            if(usable(tail)) html+=line(tail,add(tail,vector(config.v)),'v transportat','candidate');
        }
        if(config.w) html+=line([0,0],vector(config.w),'w (țintă)','target');
        if(config.mode==='basis_decomposition') {
            const parts=decomposition(config,state);
            if(parts) {
                if(parts.first.some(value=>Math.abs(value)>1e-10)) html+=line([0,0],parts.first,'a·u','candidate');
                if(parts.second.some(value=>Math.abs(value)>1e-10)) html+=line(parts.first,parts.sum,'b·v','candidate');
                html+=line([0,0],parts.sum,'construcția ta','answer');
            }
        }
        for(const key of Object.keys(state).filter(k=>['vector','endpoint','midpoint','tail'].includes(k))) {
            const point=endpoint(config,state,key);
            if(!usable(point)) continue;
            const label={vector:'Vârful vectorului construit',endpoint:'Punctul D',midpoint:'Punctul M',tail:'Originea vectorului v'}[key];
            if(key!=='midpoint' && key!=='tail') html+=line(origin(config,key),point,'construcția ta','answer');
            const [x,y]=xy(point);
            html+=`<g class="vw-handle" data-vector-handle="${key}" role="button" tabindex="${solved?-1:0}" aria-label="${escape(label)} ${escape(pair(point))}. Folosește săgețile pentru deplasare."${solved?' aria-disabled="true"':''}><circle class="vw-hit" cx="${x}" cy="${y}" r="24"/><circle class="vw-knob" cx="${x}" cy="${y}" r="8"/>${pointLabel(key==='tail'?'T':key==='midpoint'?'M':key==='endpoint'?'D':'R',x,y)}</g>`;
        }
        return html;
    }
    function render(question) {
        const config=question.interactive,solved=question.status==='correct';
        if(solved && question.solvedValues) question.vectorState=JSON.parse(JSON.stringify(question.solvedValues));
        question.vectorState ||= createState(config);
        const state=question.vectorState,id=String(question.id).replace(/[^a-zA-Z0-9_-]/g,'');
        const disabled=solved||question.saving?' disabled':'';
        let controls='';
        if(config.mode==='same_displacement') {
            controls=`<fieldset><legend>Segmentele echipolente</legend>${config.candidates.map(candidate=>{const name=candidate.join('');return `<label class="vw-option"><input type="checkbox" data-vector-candidate="${escape(name)}"${state.selected.includes(name)?' checked':''}${disabled}>${escape(name)}</label>`;}).join('')}</fieldset>`;
        } else if(config.mode==='classify_vector') {
            controls=`<fieldset><legend>Relația dintre vectori</legend>${[['equal','Egali'],['opposite','Opuși'],['collinear','Doar coliniari'],['noncollinear','Necoliniari']].map(([value,label])=>`<label class="vw-option"><input type="radio" name="vw-relation-${id}" value="${value}" data-vector-relation${state.relation===value?' checked':''}${disabled}>${label}</label>`).join('')}</fieldset>`;
        } else {
            controls=Object.entries(state).map(([key,values])=>{
                const title={coefficients:'Coeficienții descompunerii',tail:'Originea vectorului v transportat',vector:'Componentele vectorului construit',endpoint:'Coordonatele punctului D',midpoint:'Coordonatele mijlocului M'}[key];
                if(!title) return '';
                return `<fieldset><legend>${title}</legend><div class="vw-fields">${values.map((value,index)=>`<label>${key==='coefficients'?(index?'b':'a'):(index?'y':'x')}<input type="text" inputmode="text" autocomplete="off" maxlength="64" data-vector-field="${key}:${index}" value="${escape(value)}"${disabled}></label>`).join('')}</div>${key==='coefficients'?'':`<div class="vw-move" role="group" aria-label="Deplasare ${title.toLowerCase()}">${[['ArrowLeft','←','Stânga'],['ArrowUp','↑','Sus'],['ArrowDown','↓','Jos'],['ArrowRight','→','Dreapta']].map(([keyCode,symbol,label])=>`<button type="button" data-vector-move="${key}:${keyCode}" aria-label="${label}: ${escape(title.toLowerCase())}"${disabled}>${symbol}</button>`).join('')}</div>`}</fieldset>`;
            }).join('');
        }
        const summary=[];
        for(const [name,value] of Object.entries(config.points||{})) summary.push(`${name}${pair(vector(value))}`);
        for(const name of ['u','v','w']) if(config[name]) summary.push(`${name}=${pair(vector(config[name]))}`);
        if(config.scalar!==undefined) summary.push(`scalar=${config.scalar}`);
        const help=config.mode==='same_displacement'?'Compară deplasarea, lungimea și sensul săgeților. Bifează mai jos toate segmentele potrivite; poți folosi Tab și Spațiu.':
            config.mode==='classify_vector'?'Compară cele două săgeți și alege mai jos relația dintre ele. Poți folosi mouse-ul, atingerea sau tastatura.':
            config.mode==='basis_decomposition'?'Ajustează coeficienții a și b. Desenul arată suma construcției tale față de vectorul-țintă. Fracțiile se scriu exact, de exemplu 4/3.':
            'Mută punctele pe rețea prin tragere sau atingere. Din tastatură: Tab alege punctul, săgețile îl mută, Shift+săgeți mută două unități. Poți folosi și câmpurile sau butoanele de deplasare. Fracțiile se scriu ca 1/2.';
        return `<form class="training-vector-form vw-form" data-vector-workbench><p class="vw-help" id="vw-help-${id}">${help}</p><p class="vw-givens">Date: ${escape(summary.join('; '))}</p><div class="vw-board"><svg data-vector-svg viewBox="0 0 ${WIDTH} ${HEIGHT}" role="group" aria-label="Atelier de vectori în plan" aria-describedby="vw-help-${id}">${scene(config,state,id,solved)}</svg></div><div class="vw-controls">${controls}</div><p data-vector-status role="status" aria-live="polite" aria-atomic="true"></p><p data-vector-error role="alert"></p>${solved?'':`<button type="submit" class="btn btn-press"${disabled}>Verifică răspunsul</button>`}</form>`;
    }
    function bind(form,question,submit) {
        const readOnly=question.status==='correct'||question.saving;
        const config=question.interactive,state=question.vectorState;
        const svg=form.querySelector('[data-vector-svg]');
        const status=form.querySelector('[data-vector-status]'),error=form.querySelector('[data-vector-error]');
        const id=String(question.id).replace(/[^a-zA-Z0-9_-]/g,'');
        const announce=()=>{
            status.textContent=Object.entries(state).map(([key,value])=>`${{vector:'Vector',endpoint:'D',midpoint:'M',tail:'Origine v',coefficients:'Coeficienți',selected:'Selecție',relation:'Relație'}[key]}: ${Array.isArray(value)?value.join('; '):({equal:'egali',opposite:'opuși',collinear:'doar coliniari',noncollinear:'necoliniari'}[value]||value)}`).join('. ');
        };
        function refresh(focusKey=null,announceChange=true) {
            const focused=form.ownerDocument.activeElement;
            const retainedKey=focused?.closest?.('[data-vector-handle]')?.dataset.vectorHandle;
            const width=svg.getBoundingClientRect?.().width;
            const fontSize=width?Math.max(13,12*WIDTH/width):13;
            svg.innerHTML=scene(config,state,id,readOnly,fontSize);
            svg.style?.setProperty('--vw-label-size',`${fontSize}px`);
            if(width) svg.querySelectorAll('.vw-hit').forEach(hit=>hit.setAttribute('r',Math.max(24,22*WIDTH/width)));
            for(const input of form.querySelectorAll('[data-vector-field]')) {
                const [key,index]=input.dataset.vectorField.split(':');
                if(input!==form.ownerDocument.activeElement) input.value=state[key][Number(index)];
            }
            const restore=focusKey||retainedKey;
            if(restore) svg.querySelector(`[data-vector-handle="${restore}"]`)?.focus({preventScroll:true});
            if(announceChange) announce();
        }
        if(readOnly) {refresh(null,false);watchResize(form,svg,()=>refresh(null,false));return;}
        form.querySelectorAll('[data-vector-field]').forEach(input=>input.addEventListener('input',()=>{
            const [key,index]=input.dataset.vectorField.split(':');
            state[key][Number(index)]=input.value;
            error.textContent='';refresh(null,false);
        }));
        form.querySelectorAll('[data-vector-field]').forEach(input=>input.addEventListener('change',announce));
        form.querySelectorAll('[data-vector-candidate]').forEach(input=>input.addEventListener('change',()=>{
            toggleCandidate(state,input.dataset.vectorCandidate);refresh();
        }));
        form.querySelectorAll('[data-vector-relation]').forEach(input=>input.addEventListener('change',()=>{state.relation=input.value;announce();}));
        form.querySelectorAll('[data-vector-move]').forEach(button=>button.addEventListener('click',()=>{
            const [key,keyboardKey]=button.dataset.vectorMove.split(':');
            moveByKey(config,state,key,keyboardKey);refresh();
        }));
        svg.addEventListener('keydown',event=>{
            if(event.altKey||event.ctrlKey||event.metaKey) return;
            const handle=event.target.closest('[data-vector-handle]');
            if(!handle) return;
            if(event.key==='Enter'||event.key===' ') {event.preventDefault();event.stopPropagation();announce();return;}
            if(event.key==='Escape'&&drag) {
                event.preventDefault();event.stopPropagation();
                const key=drag;state[key]=dragOrigin;drag=null;refresh(key);return;
            }
            if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)) {
                event.preventDefault();event.stopPropagation();
                moveByKey(config,state,handle.dataset.vectorHandle,event.key,event.shiftKey);
                refresh(handle.dataset.vectorHandle);
            }
        });
        let drag=null,dragOrigin=null;
        const pointerPosition=event=>{
            const p=svg.createSVGPoint();p.x=event.clientX;p.y=event.clientY;
            const matrix=svg.getScreenCTM();
            if(!matrix) return null;
            const local=p.matrixTransform(matrix.inverse());
            return fromScreen([local.x,local.y],bounds(config));
        };
        svg.addEventListener('pointerdown',event=>{
            const handle=event.target.closest('[data-vector-handle]');
            if(!handle) return;
            event.preventDefault();drag=handle.dataset.vectorHandle;
            dragOrigin=[...state[drag]];
            handle.focus({preventScroll:true});
            svg.setPointerCapture(event.pointerId);
        });
        svg.addEventListener('pointermove',event=>{
            if(!drag) return;
            const point=pointerPosition(event);if(!point) return;
            move(config,state,drag,point);refresh(null,false);
        });
        svg.addEventListener('pointerup',event=>{
            if(!drag) return;
            const key=drag,point=pointerPosition(event);drag=null;
            if(point) move(config,state,key,point);
            if(svg.hasPointerCapture(event.pointerId)) svg.releasePointerCapture(event.pointerId);
            refresh(key);
        });
        svg.addEventListener('pointercancel',()=>{if(drag) state[drag]=dragOrigin;drag=null;refresh();});
        form.addEventListener('submit',async event=>{
            event.preventDefault();
            if(question.saving) return;
            const values=answer(config,state);
            const invalid=Object.entries(values).some(([key,value])=>{
                if(key==='selected') return !Array.isArray(value); // Empty selection is a valid attempted answer.
                if(key==='relation') return !value;
                return !usable(vector(value));
            });
            if(invalid) {error.textContent='Completează un răspuns valid. Folosește numere sau fracții, de exemplu 1/2.';return;}
            error.textContent='';
            await submit({values});
        });
        // Recompute touch hit areas for the actual responsive SVG width.
        refresh(null,false);
        watchResize(form,svg,()=>refresh(null,false));
    }
    return {render,bind,numeric,canonicalNumber,bounds,toScreen,fromScreen,createState,answer,origin,endpoint,move,moveByKey,toggleCandidate,decomposition,scene,watchResize};
});
