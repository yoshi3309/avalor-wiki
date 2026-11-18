(() => {
  'use strict';
  // All assertions and their chapter citations are generated from reviewed
  // public YAML and validated against existing biography headings at build time.
  const host=document.querySelector('[data-comparisons]');
  const raw=document.getElementById('dossier-data');
  if(!host||!raw)return;
  let model;
  try{model=JSON.parse(raw.textContent)}catch(_){return}
  if(!Array.isArray(model.profiles)||!Array.isArray(model.presets)||!Array.isArray(model.fields))return;
  const profiles=new Map(model.profiles.map(p=>[p.id,p]));
  const presets=new Map(model.presets.map(p=>[p.id,p]));
  const site=window.AVALOR_ROOT||'../';
  const first=document.getElementById('dossier-left');
  const second=document.getElementById('dossier-right');
  const leftPanel=document.getElementById('dossier-left-profile');
  const rightPanel=document.getElementById('dossier-right-profile');
  const rows=document.getElementById('dossier-rows');
  const status=document.getElementById('dossier-status');
  const swap=document.getElementById('dossier-swap');
  const copy=document.getElementById('dossier-copy');
  const recordURL=id=>site+'articles/'+encodeURIComponent(id)+'/';
  function el(tag,className,text){
    const node=document.createElement(tag);
    if(className)node.className=className;
    if(text!==undefined)node.textContent=text;
    return node;
  }
  const sourceURL=(p,category)=>recordURL(p.id)+'#'+encodeURIComponent(p.facts[category].chapter);
  function profilePanel(container,p,slot){
    container.replaceChildren();
    const imgWrap=el('div','dossier-person-art');
    if(p.image){
      const picture=document.createElement('picture');
      const variants=p.media?.variants||[];
      if(variants.length){
        const source=document.createElement('source');
        source.type='image/webp';
        source.srcset=variants.map(v=>site+v.path+' '+v.width+'w').join(', ');
        source.sizes='(max-width: 760px) 80vw, 400px';
        picture.append(source);
      }
      const img=document.createElement('img');
      img.src=site+p.image;
      img.alt=p.image_alt;
      img.loading='lazy';img.decoding='async';
      if(p.media){img.width=p.media.width;img.height=p.media.height;}
      picture.append(img);imgWrap.append(picture);
    } else {
      const placeholder=document.createElement('img');
      placeholder.src=site+'assets/crest.svg';
      placeholder.alt='';
      placeholder.className='dossier-person-crest';
      imgWrap.append(placeholder);
    }
    const body=el('div','dossier-person-body');
    body.append(el('span','dossier-person-slot',slot));
    const h=el('h3','dossier-person-name',p.name);body.append(h);
    body.append(el('p','dossier-person-subtitle',p.subtitle||'Public figure'));
    const era=el('p','dossier-person-era');
    era.append(el('span','', 'RECORDED ERA  '),document.createTextNode(p.era||'Not recorded'));
    body.append(era);
    body.append(el('p','dossier-person-summary',p.summary));
    const anchor=el('a','dossier-person-link','Read full biography ↗');
    anchor.href=recordURL(p.id);
    body.append(anchor);
    container.append(imgWrap,body);
  }
  function renderFacts(a,b){
    rows.replaceChildren();
    for(const field of model.fields){
      const section=el('section','dossier-comparison-row');
      section.append(el('h3','dossier-comparison-label',field.label));
      const pair=el('div','dossier-comparison-pair');
      for(const [p,slot] of [[a,'FIRST RECORD'],[b,'SECOND RECORD']]){
        const fact=p.facts[field.key];
        const cell=el('div','dossier-comparison-cell');
        cell.append(el('span','dossier-comparison-subject',slot+' · '+p.name));
        cell.append(el('p','dossier-comparison-statement',fact.text));
        const source=el('a','dossier-comparison-source','Read '+fact.source+' ↗');
        source.href=sourceURL(p,field.key);
        cell.append(source);
        pair.append(cell);
      }
      section.append(pair);rows.append(section);
    }
  }
  function render(){
    const a=profiles.get(first.value),b=profiles.get(second.value);
    if(!a||!b||a.id===b.id){
      status.textContent='Please choose two different published biographies.';
      return false;
    }
    profilePanel(leftPanel,a,'FIRST RECORD');
    profilePanel(rightPanel,b,'SECOND RECORD');
    renderFacts(a,b);
    const matched=model.presets.find(p=>p.left===a.id&&p.right===b.id);
    status.textContent=matched ?
      matched.title+': two source-linked biographies ready to examine.' :
      'Two source-linked public biographies ready to examine.';
    return true;
  }
  function comparableUrl(a,b){
    const matching=model.presets.find(p=>p.left===a&&p.right===b);
    if(matching)return new URL(site+'compare/pairs/'+encodeURIComponent(matching.id)+'/',location.href);
    const url=new URL(site+'compare/',location.href);
    url.searchParams.set('left',a);url.searchParams.set('right',b);
    return url;
  }
  function selectionFromUrl(){
    const params=new URLSearchParams(location.search);
    let a=params.get('left'),b=params.get('right');
    const parts=location.pathname.match(/\/compare\/pairs\/([a-z0-9-]+)\/?$/);
    const preset=parts?presets.get(parts[1]):null;
    if(!profiles.has(a))a=preset?.left||host.dataset.initialLeft||'lavitz-shawe';
    if(!profiles.has(b))b=preset?.right||host.dataset.initialRight||'lowkee';
    if(!profiles.has(a))a=model.profiles[0]?.id;
    if(!profiles.has(b)||b===a)b=[...profiles.keys()].find(k=>k!==a);
    return [a,b];
  }
  function syncFromAddress(){
    const [a,b]=selectionFromUrl();
    first.value=a;second.value=b;render();
  }
  function update(){
    if(!render())return;
    const url=comparableUrl(first.value,second.value);
    if(url.pathname+url.search!==location.pathname+location.search)history.pushState(null,'',url.pathname+url.search);
  }
  first.addEventListener('change',update);
  second.addEventListener('change',update);
  swap.addEventListener('click',()=>{
    [first.value,second.value]=[second.value,first.value];
    update();
  });
  copy.addEventListener('click',async()=>{
    if(!render())return;
    const url=comparableUrl(first.value,second.value).href;
    try{
      if(!navigator.clipboard?.writeText)throw Error('No clipboard');
      await navigator.clipboard.writeText(url);
      status.textContent='Comparison link copied. Share it in Discord.';
    }catch(_){
      status.textContent='Copy this link: '+url;
    }
  });
  window.addEventListener('popstate',syncFromAddress);
  syncFromAddress();
})();