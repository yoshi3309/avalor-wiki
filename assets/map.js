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
  const areaSelect = el('atlas-area'), areaButton = el('atlas-focus-area');
  const trailSelect = el('atlas-trail'), trailStatus = el('atlas-trail-status');
  const trailPrevious = el('atlas-trail-previous'), trailNext = el('atlas-trail-next'), trailClear = el('atlas-trail-clear');
  const shareButton = el('atlas-share-place'), shareStatus = el('atlas-share-status');
  // All area anchors and trail stops are existing public map IDs, not invented coordinates.
  // The trails are thematic reading sequences; no journey, road, timing or borders is implied.
  const AREA_VIEWS = {
    capital:{anchor:'renada',zoom:2.4},
    mountains:{anchor:'spine-of-the-world',zoom:2.0},
    western:{anchor:'cove-city',zoom:2.1},
    eastern:{anchor:'briyans-autumn',zoom:2.0},
    southern:{anchor:'taveras',zoom:2.1}
  };
  const TRAILS = {
    founding:{label:'The Founding and Its Aftermath',stops:['lord-osmos-tower','heroes-hill','renada']},
    six:{label:'Echoes of the Six',stops:['heavens-heart','black-tower','wayword-sun']},
    river:{label:'Communities of the Rhys',stops:['renada','taveras','river-city']}
  };
  let activeTrail = null, trailIndex = -1;

  // The public atlas displays only approved, placed markers. The positioning
  // desk also shows player-safe drafts so the archivist can measure them.
  const locations = data.locations.map(v => ({...v, initiallyUnplaced:!v.placed}));
  // A local preview never becomes a public, approved pin until the actual
  // coordinates are saved in Pages CMS and a fresh site build is loaded.
  const isPublic = loc => Boolean(loc && loc.published && loc.placed && !loc.initiallyUnplaced);
  const accessible = () => locations.filter(v => state.editing || isPublic(v));
  const placementTray = el('atlas-placement-tray');
  const placementItems = el('atlas-placement-items');
  const placementCount = el('atlas-placement-count');
  const placementToggle = el('atlas-placement-toggle');
  const placementNote = el('atlas-placement-note');
  const awaitingPlacement = locations.filter(v => v.initiallyUnplaced);
  let view = {zoom:1, scale:1, x:0, y:0};
  let state = {filter:'all', query:'', selected:null, editing:false, placing:null, position:null, pointer:null};
  const icons = {settlement:'⌂', region:'✦', water:'≈', historic:'⚔', institution:'♜'};
  const types = {settlement:'Settlement',region:'Region',water:'Waterway or sea',historic:'Historic site',institution:'Institution'};
  const escape = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clamp = (n,a,b) => Math.max(a,Math.min(b,n));
  const fit = () => Math.min(viewport.clientWidth/WIDTH,viewport.clientHeight/HEIGHT);
  const pxFor = (value,size) => Number(value)*size/100;
  const find = id => locations.find(v => v.id === id);
  const filtered = () => accessible().filter(v => (state.filter === 'all' || v.type === state.filter) && (v.name+' '+v.description).toLowerCase().includes(state.query));
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
  function focus(loc, targetZoom=1.5) {
    if (!loc || !loc.placed) return;
    if (view.zoom < targetZoom) { view.zoom=targetZoom;view.scale=fit()*view.zoom; }
    view.x=viewport.clientWidth/2-pxFor(loc.x,WIDTH)*view.scale;
    view.y=viewport.clientHeight/2-pxFor(loc.y,HEIGHT)*view.scale;
    applyTransform();
  }
  function mapUrlFor(id) {
    const url=new URL(window.location.href);
    url.searchParams.delete('edit');
    if (id) url.searchParams.set('place',id);
    else url.searchParams.delete('place');
    return url;
  }
  function areaView(id) {
    const viewConfig=AREA_VIEWS[id];
    const loc=viewConfig ? find(viewConfig.anchor) : null;
    if (!isPublic(loc) || state.editing) return;
    // Reset search and filters so the selected area anchor is always visible.
    state.filter='all';state.query='';search.value='';
    document.querySelectorAll('#atlas-filters button').forEach(b=>{
      const active=b.dataset.filter==='all';
      b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',String(active));
    });
    clearTrail();
    view.zoom=viewConfig.zoom;
    view.scale=fit()*view.zoom;
    select(loc.id,false);
    focus(loc,viewConfig.zoom);
    refresh();
    viewport.scrollIntoView({block:'nearest',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  }
  function clearTrail() {
    activeTrail=null;trailIndex=-1;trailSelect.value='';
    trailStatus.textContent='Choose a trail to follow its recorded places.';
    trailPrevious.disabled=true;trailNext.disabled=true;trailClear.disabled=true;
    document.querySelectorAll('.atlas-pin.is-trail').forEach(b=>b.classList.remove('is-trail'));
  }
  function showTrailStep(i) {
    if(!activeTrail) return;
    const trail=TRAILS[activeTrail];
    if(!trail || !Number.isInteger(i) || i<0 || i>=trail.stops.length)return;
    const loc=find(trail.stops[i]);
    if(!isPublic(loc))return;
    trailIndex=i;
    state.filter='all';state.query='';search.value='';
    document.querySelectorAll('#atlas-filters button').forEach(b=>{
      const active=b.dataset.filter==='all';
      b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',String(active));
    });
    // Keep thematic stops highlighted without implying roads between them.
    refresh();
    select(loc.id,true);
    trailStatus.textContent=trail.label+' · '+(i+1)+' of '+trail.stops.length+': '+loc.name;
    trailPrevious.disabled=i===0;trailNext.disabled=i===trail.stops.length-1;trailClear.disabled=false;
    document.querySelectorAll('.atlas-pin').forEach(b=>b.classList.toggle('is-trail',trail.stops.includes(b.dataset.id)));
  }
  function beginTrail(id) {
    if(!TRAILS[id] || state.editing){clearTrail();return}
    const stops=TRAILS[id].stops;
    if(!stops.every(stop=>isPublic(find(stop)))) {
      clearTrail();
      trailStatus.textContent='Some trail locations are not yet available on the public map.';
      return;
    }
    activeTrail=id;trailSelect.value=id;
    areaSelect.value='';
    showTrailStep(0);
  }
  function updateDetails() {
    const loc=find(state.selected);
    if (!loc){detail.innerHTML='<span class="atlas-detail-empty">Choose a place to reveal its record.</span>';return}
    const status=!loc.placed ? '<div class="atlas-detail-status">✥ Not yet placed · select this location in the positioning desk</div>' : loc.provisional ? '<div class="atlas-detail-status">◇ Approximate placement · awaiting your confirmation</div>' : '';
    const href=loc.article ? `${data.root}articles/${encodeURIComponent(loc.article)}/${loc.article_anchor ? '#'+encodeURIComponent(loc.article_anchor) : ''}` : null;
    const action=href ? `<a href="${href}">Open the related archive record ↗</a>` : '<span class="atlas-detail-no-link">A dedicated record has not yet been added.</span>';
    const subplaces=(loc.subplaces||[]).map(p=>`<a class="atlas-subplace-link" href="${data.root}articles/${encodeURIComponent(p.slug)}/${p.anchor ? '#'+encodeURIComponent(p.anchor) : ''}">${escape(p.name)} ↗</a>`).join('');
    const nested=subplaces ? `<section class="atlas-subplaces"><strong>WITHIN THIS LOCATION</strong><div>${subplaces}</div></section>` : '';
    detail.innerHTML=`<div class="atlas-detail-tag">${escape(types[loc.type]||'Location')}</div><h3>${escape(loc.name)}</h3>${status}<p>${escape(loc.description)}</p>${action}${nested}`;
  }
  function select(id,shouldFocus=true) {
    if (!find(id) || (!state.editing && !isPublic(find(id)))) return;
    state.selected=id;
    if (state.editing && editSelect) {
      // A link or selection in the location list must also set the active
      // editing target. Otherwise a click can silently move a different pin.
      state.placing=id;
      editSelect.value=id;
      state.position=null;
      copyButton.disabled=true;
      editOutput.textContent='Positioning '+find(id).name+'. Click the correct point on the map. This is a preview only; copy X/Y to Pages CMS to save.';
    }
    document.querySelectorAll('.atlas-pin').forEach(node=>node.classList.toggle('is-selected',node.dataset.id===id));
    renderList();updateDetails();renderPlacementTray();
    if(shouldFocus && find(id).placed)focus(find(id));
    const url=new URL(window.location.href);url.searchParams.set('place',id);
    history.replaceState(null,'',url.pathname+url.search+url.hash);
  }
  function renderPins() {
    pinsEl.replaceChildren();
    if (!data.image) return;
    filtered().filter(loc => loc.placed).forEach(loc=>{
      const btn=document.createElement('button');
      btn.type='button';btn.className='atlas-pin'+(loc.provisional?' is-provisional':'')+(loc.initiallyUnplaced?' is-preview':'')+(loc.id===state.selected?' is-selected':'');
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
    listEl.innerHTML=choices.length ? choices.map(loc=>`<button type="button" data-id="${escape(loc.id)}" class="${loc.id===state.selected?'is-selected':''}"><span>${escape(loc.name)}${!loc.placed?'<small>✥ Needs placement · not public</small>':loc.provisional?'<small>◇ Approximate location</small>':''}</span><span class="atlas-list-symbol" aria-hidden="true">${icons[loc.type]||'✦'}</span></button>`).join(''):'<p class="atlas-empty">No charted locations match this search.</p>';
    listEl.querySelectorAll('button[data-id]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.id)));
  }
  function renderPlacementTray() {
    if (!placementTray || !awaitingPlacement.length) return;
    placementTray.hidden=false;
    placementCount.textContent=awaitingPlacement.length+' awaiting coordinates';
    placementItems.innerHTML=awaitingPlacement.map(loc=>{
      const active=state.selected===loc.id;
      const status=loc.placed ? '✓ Preview placed' : 'Place on map';
      return `<button type="button" data-place="${escape(loc.id)}" class="${active?'is-current':''}" aria-pressed="${active}"><span>${escape(loc.name)}</span><small>${status} ↗</small></button>`;
    }).join('');
    if (state.editing && state.placing) {
      const chosen=find(state.placing);
      placementNote.textContent=chosen
        ? 'Selected: '+chosen.name+'. Click the correct spot on the map. Preview positions are NOT automatically saved.'
        : 'Choose a landmark to place.';
    } else {
      placementNote.textContent='These locations have no approved map position yet. Select a name to place its pin.';
    }
  }
  function refresh(){renderPins();renderList();renderPlacementTray()}
  if (placementTray) {
    placementItems.addEventListener('click', event=>{
      const b=event.target.closest('button[data-place]');
      if (!b) return;
      const id=b.dataset.place;
      if (!state.editing)editToggle.click();
      select(id,false);
      placementTray.classList.add('is-collapsed');
      placementToggle.setAttribute('aria-expanded','false');
      placementToggle.textContent='Show list';
    });
    placementToggle.addEventListener('click',()=>{
      const collapsed=placementTray.classList.toggle('is-collapsed');
      placementToggle.setAttribute('aria-expanded',String(!collapsed));
      placementToggle.textContent=collapsed?'Show list':'Hide list';
    });
  }
  if (data.image) {
    mapImage.src=data.image;
    mapImage.hidden=false;
    mapImage.addEventListener('error',()=>{mapImage.hidden=true;pinsEl.replaceChildren();fallback.hidden=false});
    mapImage.addEventListener('load',()=>{fallback.hidden=true;renderPins()});
  } else fallback.hidden=false;
  count.textContent=locations.filter(isPublic).length;
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

  // Click once to position a selected draft; only an actual drag pans the map.
  // Avoid pointer-capture: it can prevent the browser from dispatching clicks
  // normally when mouse-down and mouse-up occur over different descendants.
  state.drag=null;state.ignoreClick=false;
  viewport.addEventListener('pointerdown',e=>{
    if(e.button!==0||e.target.closest('.atlas-placement-tray, .atlas-pin'))return;
    state.drag={x:e.clientX,y:e.clientY,panX:view.x,panY:view.y,dragged:false};
    state.ignoreClick=false;
  });
  viewport.addEventListener('pointermove',e=>{
    if(!state.drag)return;
    const dx=e.clientX-state.drag.x,dy=e.clientY-state.drag.y;
    if(Math.hypot(dx,dy)>7)state.drag.dragged=true;
    if(state.drag.dragged){state.ignoreClick=true;view.x=state.drag.panX+dx;view.y=state.drag.panY+dy;applyTransform();}
  });
  viewport.addEventListener('pointerup',()=>{state.drag=null});
  viewport.addEventListener('pointercancel',()=>{state.drag=null;state.ignoreClick=true});
  viewport.addEventListener('click',e=>{
    if(!state.editing||!state.placing||state.ignoreClick||e.target.closest('.atlas-placement-tray, .atlas-pin'))return;
    const loc=find(state.placing);
    if(!loc)return;
    const rect=scene.getBoundingClientRect();
    if(!rect.width||!rect.height)return;
    const x=(e.clientX-rect.left)/rect.width*100;
    const y=(e.clientY-rect.top)/rect.height*100;
    if(x<0||x>100||y<0||y>100){editOutput.textContent='Click within the illustrated map.';return}
    loc.x=Number(x.toFixed(2));loc.y=Number(y.toFixed(2));
    loc.placed=true;loc.provisional=true;
    select(loc.id,false);
    state.position={id:loc.id,x:loc.x,y:loc.y};
    renderPins();
    editOutput.textContent=loc.name+' — X: '+loc.x+'% · Y: '+loc.y+'%. PREVIEW PIN VISIBLE. Copy to Pages CMS, enable Show marker to players, untick Provisional, then Save.';
    copyButton.disabled=false;
    placementTray.classList.add('is-collapsed');
    placementToggle.setAttribute('aria-expanded','false');
    placementToggle.textContent='Show list';
  });
  document.querySelectorAll('#atlas-filters button').forEach(button=>button.addEventListener('click',()=>{
    state.filter=button.dataset.filter;
    document.querySelectorAll('#atlas-filters button').forEach(b=>{const selected=b===button;b.classList.toggle('is-active',selected);b.setAttribute('aria-pressed',String(selected))});
    refresh();
  }));
  search.addEventListener('input',()=>{state.query=search.value.trim().toLowerCase();refresh()});
  editToggle.addEventListener('click',()=>{
    state.editing=!state.editing;
    if(state.editing){clearTrail();areaSelect.value='';}
    editToggle.setAttribute('aria-pressed',String(state.editing));editPanel.hidden=!state.editing;
    viewport.classList.toggle('is-positioning',state.editing);
    if(state.editing){
      // The unplaced queue is first, so no fictitious coordinates are needed.
      const ordered=[...locations].sort((a,b)=>Number(a.placed)-Number(b.placed)||a.name.localeCompare(b.name));
      editSelect.innerHTML=ordered.map(loc=>`<option value="${escape(loc.id)}">${loc.placed?'':'✥ TO PLACE · '}${escape(loc.name)}</option>`).join('');
      editSelect.value=ordered.find(loc=>!loc.placed)?.id || state.selected || ordered[0]?.id || '';
      state.placing=editSelect.value;
      state.filter='all';state.query='';search.value='';
      document.querySelectorAll('#atlas-filters button').forEach(b=>{const active=b.dataset.filter==='all';b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',String(active))});
      if(state.placing)select(state.placing,false);
      editOutput.textContent='Select a place above and click its position on the map. This is only a preview until saved in Pages CMS.';
    }else{
      state.placing=null;state.position=null;copyButton.disabled=true;
      if(!isPublic(find(state.selected)))state.selected=locations.find(isPublic)?.id||null;
      if(state.selected)updateDetails();
      placementTray?.classList.remove('is-collapsed');
      if (placementToggle) {
        placementToggle.setAttribute('aria-expanded','true');
        placementToggle.textContent='Hide list';
      }
    }
    refresh();
  });
  editSelect.addEventListener('change',()=>{state.placing=editSelect.value;state.position=null;copyButton.disabled=true;select(state.placing,false);editOutput.textContent='Click the exact point on the map. Then copy X/Y into Pages CMS, enable Show marker to players, and save.'});
  copyButton.addEventListener('click',async()=>{
    if(!state.position)return;
    const loc=find(state.position.id);
    const text=`${loc.name}\nX: ${state.position.x}\nY: ${state.position.y}\nNext: Enter X/Y in Pages CMS, enable Show marker to players, untick Provisional, and Save.`;
    try {await navigator.clipboard.writeText(text);copyButton.textContent='Copied ✓';setTimeout(()=>copyButton.textContent='Copy coordinates',1700)}
    catch(e){editOutput.textContent=text+' — Clipboard unavailable; copy the coordinates above.'}
  });
  areaButton?.addEventListener('click',()=>areaView(areaSelect.value));
  areaSelect?.addEventListener('change',()=>{if(areaSelect.value)areaView(areaSelect.value)});
  trailSelect?.addEventListener('change',()=>beginTrail(trailSelect.value));
  trailPrevious?.addEventListener('click',()=>showTrailStep(trailIndex-1));
  trailNext?.addEventListener('click',()=>showTrailStep(trailIndex+1));
  trailClear?.addEventListener('click',clearTrail);
  shareButton?.addEventListener('click',async()=>{
    const loc=find(state.selected);
    if(!isPublic(loc)) {
      shareStatus.textContent='Choose a published map location first.';
      return;
    }
    const url=mapUrlFor(loc.id).href;
    try {
      if (!navigator.clipboard?.writeText) throw Error('Clipboard unavailable');
      await navigator.clipboard.writeText(url);
      shareStatus.textContent='Map link copied.';
    } catch (_) {
      shareStatus.textContent='Copy: '+url;
    }
  });
  const params=new URLSearchParams(window.location.search);
  if(params.get('edit')==='1')editToggle.click();
  const requested=params.get('place');
  if(requested && find(requested))select(requested,true);
  else if(!state.editing && locations.some(isPublic))select(locations.find(v=>v.id==='renada'&&isPublic(v))?.id||locations.find(isPublic).id,false);
})();