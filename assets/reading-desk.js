(() => {
  'use strict';
  const root = window.AVALOR_ROOT || './';
  const KEY = 'avalor-reading-desk-v1';
  const STORAGE_LIMIT = 750;
  let memory = {};
  let storageAvailable = true;
  const now = () => Date.now();
  const validSlug = s => typeof s === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s);
  const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const validHeading = s => typeof s==='string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s);
  const saved = () => {
    try {
      const result = JSON.parse(localStorage.getItem(KEY) || '{}');
      if (!result || typeof result!=='object' || Array.isArray(result)) return {};
      return Object.fromEntries(Object.entries(result).filter(([key, value]) => validSlug(key) && value && typeof value==='object' && !Array.isArray(value)));
    } catch (_) { storageAvailable=false; return memory; }
  };
  let entries = saved();
  function persist() {
    // Keep a bounded record of reading metadata, never article bodies or private notes.
    const records = Object.entries(entries).sort((a,b)=>(Number(b[1].visited)||0)-(Number(a[1].visited)||0)).slice(0,STORAGE_LIMIT);
    entries = Object.fromEntries(records);
    memory = entries;
    try {localStorage.setItem(KEY, JSON.stringify(entries));storageAvailable=true;}
    catch (_) {storageAvailable=false;}
  }
  const update = (slug, patch) => {
    if (!validSlug(slug)) return;
    entries[slug] = {...entries[slug], ...patch};
    persist();
    window.dispatchEvent(new CustomEvent('avalor-reading-updated',{detail:{slug}}));
  };
  const safeChapter = id => validHeading(id) ? id : '';
  const article = document.querySelector('[data-reading-slug]');
  if (article) {
    const slug = article.dataset.readingSlug;
    if (validSlug(slug)) {
      const bookmark = document.getElementById('reading-bookmark');
      const finished = document.getElementById('reading-finished');
      const resume = document.getElementById('reading-resume');
      const status = document.getElementById('reading-action-status');
      const headings = [...article.querySelectorAll('.article-body h2[id]')];
      const latest = entries[slug] || {};
      const mark = (text) => {if(status)status.textContent=text;};
      update(slug,{visited:now()});
      function syncButtons() {
        const item=entries[slug]||{};
        const isSaved=Boolean(item.bookmarked), isDone=Boolean(item.completed);
        bookmark.setAttribute('aria-pressed',String(isSaved));
        bookmark.textContent=isSaved?'★ Saved to Reading Desk':'☆ Save to Reading Desk';
        finished.setAttribute('aria-pressed',String(isDone));
        finished.textContent=isDone?'✓ Finished reading':'✓ Mark as read';
        if (resume) {
          const chapter=safeChapter(item.chapter);
          resume.hidden=!chapter;
          if (chapter) resume.href='#'+encodeURIComponent(chapter);
        }
      }
      bookmark?.addEventListener('click',()=>{
        const next=!entries[slug]?.bookmarked;
        update(slug,{bookmarked:next,visited:now()});
        syncButtons();mark(next?'Saved to your personal shelf.':'Removed from saved records.');
      });
      finished?.addEventListener('click',()=>{
        const next=!entries[slug]?.completed;
        update(slug,{completed:next,visited:now()});
        syncButtons();mark(next?'Marked as finished.':'Marked as not yet finished.');
      });
      let lastChapter=latest.chapter;
      let lastWritten=0;
      function capture() {
        if (!headings.length || document.visibilityState==='hidden')return;
        const y=Math.min(190,window.innerHeight*0.29);
        let active='';
        for (const heading of headings) {
          if (heading.getBoundingClientRect().top<=y+25)active=heading.id;
          else break;
        }
        if (!active || !validHeading(active) || active===lastChapter)return;
        lastChapter=active;
        update(slug,{chapter:active,visited:now()});
        lastWritten=now();
        syncButtons();
      }
      let ticking=false;
      window.addEventListener('scroll',()=>{
        if(ticking)return;
        ticking=true;
        requestAnimationFrame(()=>{ticking=false;capture();});
      },{passive:true});
      // Save a last-visited section on exit, even when the visitor only scrolls a little.
      window.addEventListener('pagehide',()=>{capture();});
      syncButtons();
      // Do not silently consider an article finished simply because it was scrolled.
      // Completion is always an intentional reader action.
    }
  }
  const desk = document.querySelector('[data-reading-desk]');
  if (!desk)return;
  const list = {
    continue:document.getElementById('reading-continue-list'),
    bookmarked:document.getElementById('reading-bookmarked-list'),
    completed:document.getElementById('reading-completed-list'),
    recent:document.getElementById('reading-recent-list')
  };
  const status=document.getElementById('reading-desk-status');
  const bySlug=new Map();
  let loaded=false;
  function normalizedItems() {
    return Object.entries(entries).map(([slug, state])=>({slug,state,record:bySlug.get(slug)}))
      .filter(v=>v.record).sort((a,b)=>(Number(b.state.visited)||0)-(Number(a.state.visited)||0));
  }
  function card(v, kind) {
    const item=v.record,state=v.state;
    const chapter=safeChapter(state.chapter);
    const entry=root+'articles/'+encodeURIComponent(v.slug)+'/'+(kind==='continue' && chapter ? '#'+encodeURIComponent(chapter):'');
    const note=kind==='continue' && chapter ? 'Resume at saved chapter' : kind==='completed'?'Finished record':kind==='bookmarked'?'Saved to your shelf':'Recently viewed';
    return '<article class="reading-desk-card"><div class="reading-desk-category">'+escapeHtml(item.category)+'</div><h3><a href="'+escapeHtml(entry)+'">'+escapeHtml(item.title)+'</a></h3><p>'+escapeHtml(item.summary)+'</p><div class="reading-desk-card-foot"><a href="'+escapeHtml(entry)+'">'+escapeHtml(note)+' ↗</a><button type="button" data-reading-action="'+(kind==='bookmarked'?'unsave':kind==='completed'?'unfinish':'bookmark')+'" data-reading-slug="'+escapeHtml(v.slug)+'">'+(kind==='bookmarked'?'Remove bookmark':kind==='completed'?'Mark unread':state.bookmarked?'★ Saved':'☆ Save')+'</button></div></article>';
  }
  function renderList(node,items,kind,empty) {
    node.innerHTML=items.length ? items.map(x=>card(x,kind)).join('') : '<p class="reading-desk-empty">'+escapeHtml(empty)+'</p>';
  }
  function render() {
    if (!loaded)return;
    const all=normalizedItems();
    const current=all.filter(v=>!v.state.completed && validHeading(v.state.chapter));
    const bookmarks=all.filter(v=>v.state.bookmarked);
    const completed=all.filter(v=>v.state.completed);
    document.getElementById('reading-bookmark-count').textContent=String(bookmarks.length);
    document.getElementById('reading-in-progress-count').textContent=String(current.length);
    document.getElementById('reading-completed-count').textContent=String(completed.length);
    renderList(list.continue,current.slice(0,12),'continue','No chapters saved yet. Open an article and read into a chapter to start.');
    renderList(list.bookmarked,bookmarks,'bookmarked','Your shelf is empty. Use “Save to Reading Desk” on an article.');
    renderList(list.completed,completed,'completed','No completed records yet. Mark an article as read when you finish it.');
    renderList(list.recent,all.slice(0,12),'recent','No recent articles. Start exploring the public Archives.');
    if (!storageAvailable) status.textContent='Browser storage is unavailable. Changes will last only until this page closes.';
  }
  desk.addEventListener('click',event=>{
    const button=event.target.closest('[data-reading-action]');
    if(!button)return;
    const slug=button.dataset.readingSlug;
    const action=button.dataset.readingAction;
    if(!validSlug(slug))return;
    if(action==='unsave')update(slug,{bookmarked:false});
    else if(action==='unfinish')update(slug,{completed:false});
    else if(action==='bookmark')update(slug,{bookmarked:!entries[slug]?.bookmarked});
    render();
  });
  window.addEventListener('storage',event=>{
    if(event.key===KEY){entries=saved();render();}
  });
  fetch(root+'reading-desk-index.json')
    .then(resp=>{if(!resp.ok)throw Error('Index unavailable');return resp.json();})
    .then(items=>{
      if(!Array.isArray(items))throw Error('Invalid index');
      for(const item of items)if(validSlug(item.slug))bySlug.set(item.slug,item);
      loaded=true;
      render();
    })
    .catch(()=>{status.textContent='Reading Desk index unavailable. Reload to try again.';});
})();
