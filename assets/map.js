(() => {
  'use strict';
  const el = id => document.getElementById(id);
  const dataTag = el('atlas-data');
  if (!dataTag) return;
  const data = JSON.parse(dataTag.textContent);
  const WIDTH = 1448, HEIGHT = 1086;
  const viewport = el('atlas-viewport'), scene = el('atlas-scene');
  const mapImage = el('atlas-image'), fallback = el('atlas-fallback');
  const pinsEl = el('atlas-pins'), listEl = el('atlas-location-list'), detail = el('atlas-detail');
  const search = el('atlas-search'), count = el('atlas-count'), readout = el('atlas-zoom-readout');
  const editPanel = el('atlas-editor'), editToggle = el('atlas-edit-toggle');
  const editSelect = el('atlas-edit-location'), editOutput = el('atlas-edit-output');
  const copyButton = el('atlas-copy-position');
  const locations = data.locations.filter(v => v.published).map(v => ({...v}));
  let view = {zoom:1, scale:1, x:0, y:0};
  let state = {filter:'all', query:'', selected:null, editing:false, placing:null, position:null, pointer:null};
  const icons = {settlement:'⌂', region:'✦', water:'≈', historic:'⚔', institution:'♜'};
  const types = {settlement:'Settlement',region:'Region',water:'Waterway or sea',historic:'Historic site',institution:'Institution'};
  const escape = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clamp = (n,a,b) => Math.max(a,Math.min(b,n));
  const fit = () => Math.min(viewport.clientWidth/WIDTH,viewport.clientHeight/HEIGHT);
  const pxFor = (value,size) => Number(value)*size/100;
  const find = id => locations.find(v => v.id === id);
  const filtered = () => locations.filter(v => (state.filter === 'all' || v.type === state.filter) && (v.name+' '+v.description).toLowerCase().includes(state.query));
  function applyTransform() {
    const w = WIDTH*view.scale, h = HEIGHT*view.scale;
    view.x = w <= viewport.clientWidth ? (viewport.clientWidth-w)/2 : clamp(view.x,viewport.clientWidth-w,0);
    view.y = h <= viewport.clientHeight ? (viewport.clientHeight-h)/2 : clamp(view.y,viewport.clientHeight-h,0);
    scene.style.transform = `translate(${view.x}px,${view.y}px) scale(${view.scale})`;
    readout.textContent = Math.round(view.zoom*100)+'%';
  }
  function reset() {
    view.zoom = 1; view.scale = fit();
    view.x=(viewport.clientWidth-WIDTH*view.scale)/2;
    view.y=(viewport.clientHeight-HEIGHT*view.scale)/2;
    applyTransform();
  }
  function zoomAt(multiplier,centerX,centerY) {
    const next = clamp(view.zoom*multiplier,1,5);
    if (next===view.zoom) return;
    const localX=(centerX-view.x)/view.scale, localY=(centerY-view.y)/view.scale;
    view.zoom=next;view.scale=fit()*view.zoom;
    view.x=centerX-localX*view.scale;view.y=centerY-localY*view.scale;
    applyTransform();
  }
  function focus(loc) {
    if (!loc) return;
    if (view.zoom < 1.5) { view.zoom=1.5;view.scale=fit()*view.zoom; }
    view.x=viewport.clientWidth/2-pxFor(loc.x,WIDTH)*view.scale;
    view.y=viewport.clientHeight/2-pxFor(loc.y,HEIGHT)*view.scale;
    applyTransform();
  }
  function updateDetails() {
    const loc=find(state.selected);
    if (!loc){detail.innerHTML='<span class="atlas-detail-empty">Choose a place to reveal its record.</span>';return}
    const status=loc.provisional?'<div class="atlas-detail-status">◇ Approximate placement · awaiting your confirmation</div>':'';
    const href=loc.article ? `${data.root}articles/${encodeURIComponent(loc.article)}/` : null;
    const action=href ? `<a href="${href}">Open the related archive record ↗</a>` : '<span class="atlas-detail-no-link">A dedicated record has not yet been added.</span>';
    detail.innerHTML=`<div class="atlas-detail-tag">${escape(types[loc.type]||'Location')}</div><h3>${escape(loc.name)}</h3>${status}<p>${escape(loc.description)}</p>${action}`;
  }
  function select(id,shouldFocus=true) {
    if (!find(id)) return;
    state.selected=id;
    document.querySelectorAll('.atlas-pin').forEach(node=>node.classList.toggle('is-selected',node.dataset.id===id));
    renderList();updateDetails();
    if(shouldFocus)focus(find(id));
    const url=new URL(window.location.href);url.searchParams.set('place',id);
    history.replaceState(null,'',url.pathname+url.search+url.hash);
  }
  function renderPins() {
    pinsEl.replaceChildren();
    if (!data.image) return;
    filtered().forEach(loc=>{
      const btn=document.createElement('button');
      btn.type='button';btn.className='atlas-pin'+(loc.provisional?' is-provisional':'')+(loc.id===state.selected?' is-selected':'');
      btn.dataset.id=loc.id;btn.dataset.type=loc.type;
      btn.style.left=loc.x+'%';btn.style.top=loc.y+'%';
      btn.setAttribute('aria-label',loc.name+(loc.provisional?' (approximate location)':''));
      btn.innerHTML=`<span class="atlas-pin-symbol" aria-hidden="true">${icons[loc.type]||'✦'}</span><span class="atlas-pin-label">${escape(loc.name)}</span>`;
      btn.addEventListener('click',event=>{event.stopPropagation();select(loc.id)});
      pinsEl.append(btn);
    });
  }
  function renderList() {
    const choices=filtered();
    listEl.innerHTML=choices.length ? choices.map(loc=>`<button type="button" data-id="${escape(loc.id)}" class="${loc.id===state.selected?'is-selected':''}"><span>${escape(loc.name)}${loc.provisional?'<small>◇ Approximate location</small>':''}</span><span class="atlas-list-symbol" aria-hidden="true">${icons[loc.type]||'✦'}</span></button>`).join(''):'<p class="atlas-empty">No charted locations match this search.</p>';
    listEl.querySelectorAll('button[data-id]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.id)));
  }
  function refresh(){renderPins();renderList()}
  if (data.image) {
    mapImage.src=data.image;
    mapImage.hidden=false;
    mapImage.addEventListener('error',()=>{mapImage.hidden=true;pinsEl.replaceChildren();fallback.hidden=false});
    mapImage.addEventListener('load',()=>{fallback.hidden=true;renderPins()});
  } else fallback.hidden=false;
  count.textContent=locations.length;
  refresh();reset();
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(()=>{const prevZoom=view.zoom;reset();if(prevZoom>1){view.zoom=prevZoom;view.scale=fit()*prevZoom;applyTransform()}}).observe(viewport);
  el('atlas-zoom-in').addEventListener('click',()=>zoomAt(1.25,viewport.clientWidth/2,viewport.clientHeight/2));
  el('atlas-zoom-out').addEventListener('click',()=>zoomAt(1/1.25,viewport.clientWidth/2,viewport.clientHeight/2));
  el('atlas-reset').addEventListener('click',reset);
  viewport.addEventListener('wheel',event=>{
    if(!data.image) return;
    event.preventDefault();const rect=viewport.getBoundingClientRect();
    zoomAt(event.deltaY<0?1.17:1/1.17,event.clientX-rect.left,event.clientY-rect.top);
  },{passive:false});
  viewport.addEventListener('keydown',event=>{
    if(event.key==='+'||event.key==='='){event.preventDefault();zoomAt(1.25,viewport.clientWidth/2,viewport.clientHeight/2)}
    if(event.key==='-'){event.preventDefault();zoomAt(.8,viewport.clientWidth/2,viewport.clientHeight/2)}
    const step=36;
    if(event.key==='ArrowLeft'){view.x+=step;event.preventDefault()}
    else if(event.key==='ArrowRight'){view.x-=step;event.preventDefault()}
    else if(event.key==='ArrowUp'){view.y+=step;event.preventDefault()}
    else if(event.key==='ArrowDown'){view.y-=step;event.preventDefault()}
    else return;
    applyTransform();
  });
  viewport.addEventListener('pointerdown',e=>{
    if(!data.image || (e.target.closest('.atlas-pin') && !state.placing))return;
    if(e.button!==0)return;
    state.pointer={x:e.clientX,y:e.clientY,startX:view.x,startY:view.y,travel:0};
    viewport.setPointerCapture(e.pointerId);
  });
  viewport.addEventListener('pointermove',e=>{
    if(!state.pointer)return;
    const dx=e.clientX-state.pointer.x,dy=e.clientY-state.pointer.y;
    state.pointer.travel=Math.max(state.pointer.travel,Math.hypot(dx,dy));
    if(state.pointer.travel>5 && !state.placing){view.x=state.pointer.startX+dx;view.y=state.pointer.startY+dy;applyTransform()}
  });
  viewport.addEventListener('pointerup',e=>{
    if(!state.pointer)return;
    const wasClick=state.pointer.travel<7;state.pointer=null;
    if(wasClick&&state.editing&&state.placing){
      const rect=viewport.getBoundingClientRect();
      const x=clamp(((e.clientX-rect.left-view.x)/view.scale)/WIDTH*100,0,100);
      const y=clamp(((e.clientY-rect.top-view.y)/view.scale)/HEIGHT*100,0,100);
      const loc=find(state.placing);if(loc){loc.x=Number(x.toFixed(2));loc.y=Number(y.toFixed(2));state.position={id:loc.id,x:loc.x,y:loc.y};
      editOutput.textContent=`${loc.name} — X: ${loc.x}% · Y: ${loc.y}%. Copy these values to the matching row in Pages CMS.`;
      copyButton.disabled=false;renderPins();select(loc.id,false)}
    }
  });
  viewport.addEventListener('pointercancel',()=>{state.pointer=null});
  document.querySelectorAll('#atlas-filters button').forEach(button=>button.addEventListener('click',()=>{
    state.filter=button.dataset.filter;
    document.querySelectorAll('#atlas-filters button').forEach(b=>{const selected=b===button;b.classList.toggle('is-active',selected);b.setAttribute('aria-pressed',String(selected))});
    refresh();
  }));
  search.addEventListener('input',()=>{state.query=search.value.trim().toLowerCase();refresh()});
  editToggle.addEventListener('click',()=>{
    state.editing=!state.editing;
    editToggle.setAttribute('aria-pressed',String(state.editing));editPanel.hidden=!state.editing;
    viewport.classList.toggle('is-positioning',state.editing);
    if(state.editing){
      editSelect.innerHTML=locations.map(loc=>`<option value="${escape(loc.id)}">${escape(loc.name)}</option>`).join('');
      editSelect.value=state.selected||locations[0]?.id||'';
      state.placing=editSelect.value;
    }else{state.placing=null;state.position=null;copyButton.disabled=true}
  });
  editSelect.addEventListener('change',()=>{state.placing=editSelect.value;state.position=null;copyButton.disabled=true;editOutput.textContent='Now click the correct point on the map.'});
  copyButton.addEventListener('click',async()=>{
    if(!state.position)return;
    const loc=find(state.position.id);
    const text=`${loc.name}\nX: ${state.position.x}\nY: ${state.position.y}`;
    try {await navigator.clipboard.writeText(text);copyButton.textContent='Copied ✓';setTimeout(()=>copyButton.textContent='Copy coordinates',1700)}
    catch(e){editOutput.textContent=text+' — Clipboard unavailable; copy the coordinates above.'}
  });
  const params=new URLSearchParams(window.location.search);
  if(params.get('edit')==='1')editToggle.click();
  const requested=params.get('place');
  if(requested && find(requested))select(requested,true);
  else if(locations.length)select(locations.find(v=>v.id==='renada')?.id||locations[0].id,false);
})();