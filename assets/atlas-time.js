(() => {
  'use strict';
  const src=document.getElementById('atlas-history-data');
  const host=document.getElementById('atlas-history');
  if(!src||!host)return;
  let events;
  try{events=JSON.parse(src.textContent)}catch(_){return}
  if(!Array.isArray(events)||!events.length)return;
  const byId=new Map(events.map(e=>[e.id,e]));
  const cards=[...host.querySelectorAll('[data-history-card]')];
  const period=host.querySelector('#atlas-history-period');
  const showAll=host.querySelector('#atlas-history-all');
  const count=host.querySelector('#atlas-history-count');
  const heading=host.querySelector('#atlas-history-detail-title');
  const era=host.querySelector('#atlas-history-detail-era');
  const text=host.querySelector('#atlas-history-detail-text');
  const note=host.querySelector('#atlas-history-detail-note');
  const read=host.querySelector('#atlas-history-read');
  const sourceLink=host.querySelector('#atlas-history-source');
  const share=host.querySelector('#atlas-history-share');
  const detail=host.querySelector('#atlas-history-detail');
  const root=window.AVALOR_ROOT||'../';
  if(!period||!showAll||!count||!heading||!era||!text||!note||!read||!sourceLink||!share||!detail)return;
  let selected=null;
  const displayCount=()=>cards.filter(c=>!c.hidden).length;
  function spotlight(ids){
    // The interactive map accepts only published, placed, non-provisional pins.
    document.dispatchEvent(new CustomEvent('avalor:history-pins',{detail:{ids}}));
  }
  function deselect(){
    selected=null;
    cards.forEach(card=>{
      card.classList.remove('is-history-selected');
      card.querySelector('[data-history-select]')?.setAttribute('aria-current','false');
    });
    spotlight([]);
    era.textContent="THE SCHOLAR'S GEOGRAPHIC RECORD";
    heading.textContent='Choose a moment in history';
    text.textContent='Select an account to read its history and, where possible, illuminate a place on the chart above.';
    note.textContent='The chart marks sites, regions, and places associated with the accounts. The boundaries of earlier ages remain a subject of study.';
    read.href=root+'chronicle/';
    sourceLink.hidden=true;
    share.disabled=true;
  }
  function applyFilters(){
    const all=showAll.checked,chosenPeriod=period.value;
    for(const card of cards){
      const matchesPeriod=chosenPeriod==='all'||card.dataset.historyPeriod===chosenPeriod;
      const matchesPlace=all||card.dataset.historyMapped==='true';
      card.hidden=!(matchesPeriod&&matchesPlace);
    }
    const countNow=displayCount();
    count.textContent=countNow+' of '+events.length+' Chronicle entries shown'
      +(!all?' · events with charted locations':' · including events with unrecorded locations');
    if(selected && host.querySelector('[data-history-id="'+selected+'"]')?.hidden){
      deselect();
      const url=new URL(location.href);
      url.searchParams.delete('event');
      history.replaceState(null,'',url.pathname+url.search+url.hash);
    }
  }
  function select(id,fromAddress=false){
    const record=byId.get(id);
    if(!record)return false;
    const drawer=host.closest('details');
    if(drawer) drawer.open=true;
    if(period.value!=='all' && period.value!==record.period) period.value=record.period;
    if(!record.atlas && !showAll.checked) showAll.checked=true;
    selected=id;
    applyFilters();
    cards.forEach(card=>{
      const active=card.dataset.historyId===id;
      card.classList.toggle('is-history-selected',active);
      card.querySelector('[data-history-select]')?.setAttribute('aria-current',String(active));
    });
    heading.textContent=record.title;
    era.textContent=record.era+' · '+record.date;
    text.textContent=record.text;
    read.href=root+'chronicle/#event-'+encodeURIComponent(id);
    sourceLink.href=root+'articles/'+encodeURIComponent(record.article)+'/';
    sourceLink.hidden=false;
    share.disabled=false;
    if(record.atlas){
      note.textContent=record.atlas.relation_label+' — '+record.atlas.place_name+'. '+record.atlas.note
        +' Date: '+record.date_label+'. '+record.date_note;
      spotlight([record.atlas.pin]);
      document.dispatchEvent(new CustomEvent('avalor:history-focus',{detail:{id:record.atlas.pin}}));
    }else{
      note.textContent='LOCATION UNRECORDED — No surviving chart identifies a site, region, or landmark for this event. '+record.date_label+': '+record.date_note;
      spotlight([]);
    }
    if(!fromAddress){
      const url=new URL(location.href);
      url.searchParams.delete('edit');
      url.searchParams.delete('place');
      url.searchParams.set('event',id);
      url.hash='atlas-history-detail';
      // A focus event may select an approved place in the map; explicitly keep
      // the historical event query so a shared link reproduces the selected record.
      history.pushState(null,'',url.pathname+url.search+url.hash);
      detail.focus({preventScroll:true});
      detail.scrollIntoView({block:'nearest',behavior:'instant'});
    }
    return true;
  }
  function fromURL(){
    const id=new URLSearchParams(location.search).get('event');
    if(id && byId.has(id)){
      select(id,true);
      return;
    }
    deselect();
    applyFilters();
  }
  host.addEventListener('click',event=>{
    const link=event.target.closest('[data-history-select]');
    if(!link||event.defaultPrevented||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    event.preventDefault();
    select(link.dataset.historySelect);
  });
  period.addEventListener('change',applyFilters);
  showAll.addEventListener('change',applyFilters);
  share.addEventListener('click',async()=>{
    if(!selected)return;
    const url=new URL(location.href);
    url.searchParams.delete('edit');
    url.searchParams.delete('place');
    url.searchParams.set('event',selected);
    url.hash='atlas-history-detail';
    try{
      if(!navigator.clipboard?.writeText) throw Error('No clipboard');
      await navigator.clipboard.writeText(url.href);
      count.textContent='Historical Atlas link copied — ready for Discord.';
    }catch(_){
      count.textContent='Copy this link: '+url.href;
    }
  });
  window.addEventListener('popstate',fromURL);
  fromURL();
})();