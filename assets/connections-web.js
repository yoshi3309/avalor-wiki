(() => {
  'use strict';
  const root=document.querySelector('[data-cross-explorer]');
  const dataEl=document.getElementById('cross-data');
  if (!root || !dataEl)return;
  let data;
  try{data=JSON.parse(dataEl.textContent);}catch(_){return;}
  if(!Array.isArray(data.nodes)||!Array.isArray(data.edges))return;
  const byId=new Map(data.nodes.map(n=>[n.id,n]));
  const around=new Map(data.nodes.map(n=>[n.id,[]]));
  for(const edge of data.edges){
    if(!around.has(edge.from)||!around.has(edge.to))continue;
    around.get(edge.from).push({other:edge.to,edge});
    around.get(edge.to).push({other:edge.from,edge});
  }
  const site=window.AVALOR_ROOT||'../';
  const kinds={people:'Person',organizations:'Organization',places:'Place',events:'Historic event'};
  const nodes={
    search:document.getElementById('cross-search'),
    kind:document.getElementById('cross-kind'),
    results:document.getElementById('cross-results'),
    count:document.getElementById('cross-count'),
    orbit:document.getElementById('cross-orbit'),
    lines:document.getElementById('cross-lines'),
    more:document.getElementById('cross-more'),
    name:document.getElementById('cross-name'),
    summary:document.getElementById('cross-summary'),
    actions:document.getElementById('cross-actions'),
    edges:document.getElementById('cross-edges'),
    edgeCount:document.getElementById('cross-edge-count')
  };
  const linkFor=id=>site+'articles/'+encodeURIComponent(id)+'/';
  let selected=null;
  function listCandidates(){
    const query=nodes.search.value.trim().toLocaleLowerCase();
    return data.nodes.filter(n=>
      (nodes.kind.value==='all'||n.kind===nodes.kind.value)&&
      (!query||(n.label+' '+n.summary).toLocaleLowerCase().includes(query)))
      .sort((a,b)=>a.label.localeCompare(b.label));
  }
  function renderSearch(){
    nodes.results.replaceChildren();
    const items=listCandidates();
    nodes.count.textContent=items.length+' records';
    if(!items.length){const p=document.createElement('p');p.className='cross-empty';p.textContent='No matching public records. Try another name or category.';nodes.results.append(p);return;}
    for(const n of items){
      const b=document.createElement('button');b.type='button';b.className='cross-option'+(selected===n.id?' is-active':'');
      b.setAttribute('aria-pressed',String(selected===n.id));
      const title=document.createElement('strong');title.textContent=n.label;
      const sub=document.createElement('small');sub.textContent=(kinds[n.kind]||'Record')+' · '+(around.get(n.id)||[]).length+' links';
      b.append(title,sub);b.addEventListener('click',()=>focus(n.id));nodes.results.append(b);
    }
  }
  function orbitButton(n,x,y,central){
    const b=document.createElement('button');b.type='button';b.className='cross-node'+(central?' is-central':'');
    b.style.left=x+'%';b.style.top=y+'%';b.textContent=n.label;
    b.setAttribute('aria-label','Explore '+n.label);
    b.addEventListener('click',()=>focus(n.id));nodes.orbit.append(b);
  }
  function renderOrbit(n,links){
    nodes.orbit.replaceChildren();nodes.lines.replaceChildren();
    const nearest=links.slice(0,8);
    orbitButton(n,50,50,true);
    const rx=window.matchMedia('(max-width: 690px)').matches?31:37;
    const ry=window.matchMedia('(max-width: 690px)').matches?32:36;
    nearest.forEach((rel,i)=>{
      const other=byId.get(rel.other);
      const angle=i*2*Math.PI/nearest.length-Math.PI/2;
      const x=50+rx*Math.cos(angle),y=50+ry*Math.sin(angle);
      const line=document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1','500');line.setAttribute('y1','240');
      line.setAttribute('x2',String(10*x));line.setAttribute('y2',String(4.8*y));
      line.setAttribute('class','cross-line cross-line-'+rel.edge.type);
      nodes.lines.append(line);
      orbitButton(other,x,y,false);
    });
    nodes.more.textContent=links.length>8?(links.length-8)+' more documented connections are listed below.':'';
  }
  function renderFocused(){
    const n=byId.get(selected);if(!n)return;
    const connected=(around.get(n.id)||[]).slice().sort((a,b)=>byId.get(a.other).label.localeCompare(byId.get(b.other).label));
    nodes.name.textContent=n.label;nodes.summary.textContent=n.summary;
    nodes.edgeCount.textContent=String(connected.length);
    nodes.actions.replaceChildren();
    const record=document.createElement('a');record.href=linkFor(n.article);record.textContent='Read complete record ↗';nodes.actions.append(record);
    nodes.edges.replaceChildren();
    for(const rel of connected){
      const other=byId.get(rel.other);
      const row=document.createElement('div');row.className='cross-edge';
      const text=document.createElement('div');
      const select=document.createElement('button');select.type='button';select.textContent=other.label;select.addEventListener('click',()=>focus(other.id));
      const label=document.createElement('p');label.textContent=rel.edge.label;
      text.append(select,label);
      const source=document.createElement('a');source.href=linkFor(rel.edge.evidence);source.textContent='Evidence: '+rel.edge.source_title+' ↗';
      source.setAttribute('aria-label','Read source for '+rel.edge.label);
      row.append(text,source);nodes.edges.append(row);
    }
    renderOrbit(n,connected);
  }
  function focus(id,writeUrl=true){
    if(!byId.has(id))return;
    selected=id;
    if(writeUrl){
      const url=new URL(window.location.href);
      url.searchParams.set('focus',id);
      window.history.replaceState(null,'',url.pathname+url.search+url.hash);
    }
    renderFocused();renderSearch();
  }
  nodes.search.addEventListener('input',renderSearch);
  nodes.kind.addEventListener('change',renderSearch);
  window.addEventListener('resize',()=>{if(selected)renderOrbit(byId.get(selected),(around.get(selected)||[]).slice().sort((a,b)=>byId.get(a.other).label.localeCompare(byId.get(b.other).label)));},{passive:true});
  window.addEventListener('popstate',()=>{
    const id=new URLSearchParams(location.search).get('focus');
    focus(byId.has(id)?id:data.nodes[0].id,false);
  });
  const requested=new URLSearchParams(location.search).get('focus');
  focus(byId.has(requested)?requested:(byId.has('lavitz-shawe')?'lavitz-shawe':data.nodes[0].id),false);
})();