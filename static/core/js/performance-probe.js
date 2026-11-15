/* Opt-in local diagnostics (?frontend_perf=1). No network reporting or storage. */
(() => {
    const metrics = {lcpMs: null, cls: 0, maxInteractionMs: null, longTasks: 0, shifts: []};
    let sessionStart = 0, lastShift = 0, sessionValue = 0, timer;
    function publish() {
        clearTimeout(timer);
        timer = setTimeout(() => {
            let output = document.getElementById('frontend-performance');
            if (!output) {
                output = document.createElement('script');
                output.type = 'application/json'; output.id = 'frontend-performance';
                document.head.append(output);
            }
            const nav = performance.getEntriesByType('navigation')[0];
            output.textContent = JSON.stringify({...metrics,
                dclMs: nav?.domContentLoadedEventEnd, loadMs: nav?.loadEventEnd,
                paints: performance.getEntriesByType('paint').map(e => ({name:e.name,ms:e.startTime})),
                resources: performance.getEntriesByType('resource').map(e => ({
                    name: new URL(e.name).pathname, bytes:e.decodedBodySize,
                    transfer:e.transferSize, duration:e.duration
                }))});
        }, 100);
    }
    function observe(type, callback, extra = {}) {
        if (!window.PerformanceObserver || !PerformanceObserver.supportedEntryTypes.includes(type)) return;
        new PerformanceObserver(list => {list.getEntries().forEach(callback); publish();})
            .observe({type, buffered:true, ...extra});
    }
    observe('largest-contentful-paint', e => {metrics.lcpMs = e.startTime;});
    observe('layout-shift', e => {
        if (e.hadRecentInput) return;
        if (metrics.shifts.length < 20) metrics.shifts.push({ms:e.startTime,value:e.value,
            sources:(e.sources||[]).map(s=>({node:s.node?.id||s.node?.className,
                from:{x:s.previousRect.x,y:s.previousRect.y,width:s.previousRect.width,height:s.previousRect.height},
                to:{x:s.currentRect.x,y:s.currentRect.y,width:s.currentRect.width,height:s.currentRect.height}}))});
        if (!sessionStart || e.startTime-lastShift > 1000 || e.startTime-sessionStart > 5000) {
            sessionStart=e.startTime; sessionValue=0;
        }
        lastShift=e.startTime; sessionValue+=e.value;
        metrics.cls=Math.max(metrics.cls,sessionValue);
    });
    // Maximum observed event duration is diagnostic, not the field INP percentile.
    observe('event', e => {if(e.interactionId)metrics.maxInteractionMs=Math.max(metrics.maxInteractionMs||0,e.duration);}, {durationThreshold:16});
    observe('longtask', () => {metrics.longTasks++;});
    window.addEventListener('load', publish, {once:true});
})();
