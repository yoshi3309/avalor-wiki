(() => {
  'use strict';
  const root = window.AVALOR_ROOT || './';
  const searchModal = document.getElementById('search-modal');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('sidebar-scrim');
  let records = null;
  const escape = str => String(str).replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
  const openSearch = async () => {
    searchModal.classList.add('is-open');
    searchModal.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    searchInput.focus();
    if (!records) {
      try {
        const response = await fetch(root + 'search-index.json');
        if (!response.ok) throw new Error('Could not retrieve index');
        records = await response.json();
      } catch(err) {
        searchResults.innerHTML = '<p class="search-empty">Search requires a web server. Run the local preview command in the README, or view the deployed website.</p>';
        return;
      }
    }
    displaySearch(searchInput.value);
  };
  const closeSearch = () => {
    searchModal.classList.remove('is-open');
    searchModal.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
  };
  const displaySearch = (raw) => {
    if (!records) return;
    const q = raw.trim().toLocaleLowerCase();
    if (!q) {
      const featured = records.filter(r => r.featured).slice(0, 5);
      searchResults.innerHTML = featured.map(r => resultMarkup(r)).join('');
      return;
    }
    const terms = q.split(/\s+/);
    const found = records.map(r => {
      const title = r.title.toLocaleLowerCase(), summary = r.summary.toLocaleLowerCase(), body = r.body.toLocaleLowerCase();
      const score = terms.every(t => (title + ' ' + summary + ' ' + body).includes(t))
        ? terms.reduce((n,t)=>n+(title.includes(t)?12:0)+(summary.includes(t)?4:0)+(body.includes(t)?1:0),0) : -1;
      return {r, score};
    }).filter(x=>x.score>=0).sort((a,b)=>b.score-a.score).slice(0,15).map(x=>x.r);
    searchResults.innerHTML = found.length ? found.map(resultMarkup).join('') : '<p class="search-empty">No matching public records. Try a different name or place.</p>';
  };
  const resultMarkup = r => `<a class="search-result" href="${root}articles/${encodeURIComponent(r.slug)}/"><span>${escape(r.category)} · ${escape(r.entry)}</span><strong>${escape(r.title)}</strong><p>${escape(r.summary)}</p></a>`;
  document.querySelectorAll('.search-trigger').forEach(el => el.addEventListener('click',openSearch));
  document.querySelectorAll('[data-close-search]').forEach(el => el.addEventListener('click',closeSearch));
  searchInput?.addEventListener('input',e=>displaySearch(e.target.value));
  document.addEventListener('keydown',e=>{
    if ((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}
    if(e.key==='Escape'){closeSearch(); closeMenu()}
  });
  const closeMenu = () => { sidebar.classList.remove('show');scrim.classList.remove('show'); };
  document.getElementById('menu-trigger')?.addEventListener('click',()=>{sidebar.classList.add('show');scrim.classList.add('show')});
  scrim?.addEventListener('click',closeMenu);
  document.querySelectorAll('.side-nav a').forEach(a=>a.addEventListener('click',closeMenu));
  const filter = document.getElementById('catalog-filter');
  filter?.addEventListener('input',()=>{
    const q=filter.value.toLocaleLowerCase().trim();let count=0;
    document.querySelectorAll('#catalog-list .catalog-item').forEach(el=>{const visible=el.dataset.filter.includes(q);el.hidden=!visible;if(visible)count++});
    document.getElementById('catalog-empty').hidden = count>0;
  });
})();