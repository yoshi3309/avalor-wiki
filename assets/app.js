(() => {
  'use strict';
  const root = window.AVALOR_ROOT || './';
  const searchModal = document.getElementById('search-modal');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('sidebar-scrim');
  let records = null;
  let searchCategory = 'all';
  let selectedSearchIndex = -1;
  let previousFocus = null;
  const categoryButtons = [...document.querySelectorAll('[data-search-category]')];
  const searchStatus = document.getElementById('search-status');
  const searchDialog = searchModal?.querySelector('.search-dialog');
  const escape = str => String(str).replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
  const resultUrl = record => root + 'articles/' + encodeURIComponent(record.slug) + '/' + (record.fragment ? '#' + encodeURIComponent(record.fragment) : '');
  const resultMarkup = record => {
    const section = record.type === 'section';
    const label = section ? 'SECTION · ' + record.category : record.category + ' · ' + record.entry;
    const context = section ? record.subtitle : record.summary;
    return `<a class="search-result" href="${escape(resultUrl(record))}"><span>${escape(label)}</span><strong>${escape(record.title)}</strong><p>${escape(context)}</p></a>`;
  };
  const selectSearchResult = index => {
    const links = [...searchResults.querySelectorAll('a.search-result')];
    if (!links.length) { selectedSearchIndex = -1; return; }
    selectedSearchIndex = Math.max(0, Math.min(links.length - 1, index));
    links.forEach((link,i) => link.classList.toggle('is-keyboard-selected', i === selectedSearchIndex));
    links[selectedSearchIndex].scrollIntoView({block:'nearest'});
  };
  const displaySearch = () => {
    if (!records || !window.AvalorSearch) return;
    const query = searchInput.value.trim();
    const results = window.AvalorSearch.search(records, query, searchCategory, 20);
    selectedSearchIndex = -1;
    if (!query && searchCategory === 'all') {
      searchStatus.textContent = 'Featured public records';
    } else {
      searchStatus.textContent = results.length + (results.length === 1 ? ' matching record' : ' matching records') + (searchCategory === 'all' ? '' : ' in ' + searchCategory);
    }
    searchResults.innerHTML = results.length
      ? results.map(resultMarkup).join('')
      : '<p class="search-empty">No matching public records. Try another spelling, name, or collection.</p>';
  };
  const closeSearch = () => {
    if (!searchModal?.classList.contains('is-open')) return;
    searchModal.classList.remove('is-open');
    searchModal.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
    selectedSearchIndex = -1;
    if (previousFocus?.isConnected) previousFocus.focus();
  };
  const openSearch = async () => {
    if (!searchModal || !searchInput) return;
    if (!searchModal.classList.contains('is-open')) previousFocus = document.activeElement;
    searchModal.classList.add('is-open');
    searchModal.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    searchInput.focus();
    if (records) { displaySearch(); return; }
    try {
      const response = await fetch(root + 'search-index.json');
      if (!response.ok) throw Error('Could not retrieve search index');
      const items = await response.json();
      if (!Array.isArray(items) || !window.AvalorSearch) throw Error('Search data unavailable');
      records = items.map(window.AvalorSearch.prepare);
      displaySearch();
    } catch(err) {
      searchStatus.textContent = 'Search unavailable';
      searchResults.innerHTML = '<p class="search-empty">The public search index could not be loaded. Try reloading the page or browsing the collections.</p>';
    }
  };
  categoryButtons.forEach(button => button.addEventListener('click', () => {
    searchCategory = button.dataset.searchCategory;
    categoryButtons.forEach(other => {
      const active = other === button;
      other.classList.toggle('is-selected',active);
      other.setAttribute('aria-pressed',String(active));
    });
    displaySearch();
  }));
  document.querySelectorAll('.search-trigger').forEach(el => el.addEventListener('click',openSearch));
  document.querySelectorAll('[data-close-search]').forEach(el => el.addEventListener('click',closeSearch));
  searchInput?.addEventListener('input', displaySearch);
  searchResults?.addEventListener('mousemove', () => {
    searchResults.querySelectorAll('.is-keyboard-selected').forEach(el => el.classList.remove('is-keyboard-selected'));
    selectedSearchIndex = -1;
  });
  document.addEventListener('keydown',e=>{
    if ((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k') {e.preventDefault();openSearch();return;}
    if (e.key==='Escape') {closeSearch();closeMenu();return;}
    if (!searchModal?.classList.contains('is-open')) return;
    if (e.key==='ArrowDown' || e.key==='ArrowUp') {
      e.preventDefault();
      const count=searchResults.querySelectorAll('a.search-result').length;
      if (count) selectSearchResult((selectedSearchIndex<0 ? (e.key==='ArrowDown' ? 0 : count-1) : selectedSearchIndex+(e.key==='ArrowDown'?1:-1)+count)%count);
    } else if (e.key==='Enter' && selectedSearchIndex>=0 && document.activeElement===searchInput) {
      const result=searchResults.querySelectorAll('a.search-result')[selectedSearchIndex];
      if (result) {e.preventDefault();window.location.assign(result.href);}
    } else if (e.key==='Tab' && searchDialog) {
      const focusable=[...searchDialog.querySelectorAll('button:not([disabled]),input:not([disabled]),a[href]')].filter(el=>el.getClientRects().length);
      if (focusable.length) {
        const first=focusable[0],last=focusable[focusable.length-1];
        if (e.shiftKey && document.activeElement===first) {e.preventDefault();last.focus();}
        else if (!e.shiftKey && document.activeElement===last) {e.preventDefault();first.focus();}
      }
    }
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
  // People & Legends collection: progressive enhancement for its group directory.
  // Every biography remains an ordinary link and is visible without JavaScript.
  const peopleDirectory = document.getElementById('people-directory');
  if (peopleDirectory) {
    const cards = Array.from(document.querySelectorAll('#people-record-grid .people-record'));
    const groupButtons = Array.from(document.querySelectorAll('[data-people-group]'));
    const peopleSearch = document.getElementById('people-filter');
    const peopleCount = document.getElementById('people-visible-count');
    const peopleEmpty = document.getElementById('people-empty');
    const peopleReset = document.getElementById('people-reset');
    const peopleHeading = document.getElementById('people-directory-heading');
    const peopleDescription = document.getElementById('people-directory-description');
    let activeGroup = 'all';
    const updatePeople = () => {
      const terms = (peopleSearch.value || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let shown = 0;
      cards.forEach(card => {
        const groups = (card.dataset.groups || '').split(/\s+/);
        const matchGroup = activeGroup === 'all' || groups.includes(activeGroup);
        const searchable = card.dataset.search || '';
        const matchSearch = terms.every(term => searchable.includes(term));
        const visible = matchGroup && matchSearch;
        card.hidden = !visible;
        if (visible) shown += 1;
      });
      peopleCount.textContent = shown + ' of ' + cards.length + ' records';
      peopleEmpty.hidden = shown !== 0;
      peopleReset.hidden = activeGroup === 'all' && !terms.length;
    };
    groupButtons.forEach(button => button.addEventListener('click', () => {
      activeGroup = button.dataset.peopleGroup;
      groupButtons.forEach(other => {
        const selected = other === button;
        other.classList.toggle('is-selected', selected);
        other.setAttribute('aria-pressed', String(selected));
      });
      peopleHeading.textContent = activeGroup === 'all'
        ? 'All People A–Z'
        : button.querySelector('strong').textContent.trim();
      peopleDescription.textContent = activeGroup === 'all'
        ? 'Explore all public records in this collection.'
        : button.querySelector('.people-group-description').textContent.trim();
      updatePeople();
      peopleDirectory.scrollIntoView({ behavior: 'auto', block: 'start' });
    }));
    peopleSearch.addEventListener('input', updatePeople);
    peopleReset.addEventListener('click', () => {
      activeGroup = 'all';
      peopleSearch.value = '';
      peopleHeading.textContent = 'All People A–Z';
      peopleDescription.textContent = 'Explore all public records in this collection.';
      groupButtons.forEach(button => {
        const selected = button.dataset.peopleGroup === 'all';
        button.classList.toggle('is-selected', selected);
        button.setAttribute('aria-pressed', String(selected));
      });
      updatePeople();
      peopleSearch.focus();
    });
  }

})();