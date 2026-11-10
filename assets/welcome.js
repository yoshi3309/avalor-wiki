(() => {
  'use strict';
  // Progressive enhancement: without JavaScript every route and its public
  // article links remain visible, reachable, and indexed.
  const cards = [...document.querySelectorAll('[data-welcome-choice]')];
  const panels = [...document.querySelectorAll('[data-welcome-panel]')];
  if (cards.length !== 4 || panels.length !== 4) return;
  const ids = new Set(panels.map(panel => panel.dataset.welcomePanel));
  const fallback = 'kingdom';
  const selectedFromHash = () => {
    const hash = window.location.hash.replace(/^#welcome-/, '');
    return ids.has(hash) ? hash : fallback;
  };
  function choose(id, moveFocus=false) {
    if (!ids.has(id)) id=fallback;
    for(const card of cards) {
      const active=card.dataset.welcomeChoice===id;
      card.classList.toggle('is-chosen', active);
      if(active) card.setAttribute('aria-current','true');
      else card.removeAttribute('aria-current');
    }
    for(const panel of panels) {
      panel.hidden=panel.dataset.welcomePanel!==id;
    }
    if (moveFocus) {
      const target=document.getElementById('welcome-panel-title-'+id);
      const section=document.getElementById('welcome-'+id);
      if(target && section) {
        target.setAttribute('tabindex','-1');
        window.requestAnimationFrame(()=>{
          target.focus({preventScroll:true});
          const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
            document.documentElement.dataset.readingMotion==='reduce';
          section.scrollIntoView({block:'start',behavior:reduce?'instant':'smooth'});
        });
      }
    }
  }
  for(const card of cards) {
    card.addEventListener('click',event=>{
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const id=card.dataset.welcomeChoice;
      if(!ids.has(id))return;
      const next='#welcome-'+id;
      choose(id, true);
      if(window.location.hash!==next) history.pushState(null,'',next);
    });
  }
  window.addEventListener('popstate',()=>choose(selectedFromHash(),true));
  window.addEventListener('hashchange',()=>choose(selectedFromHash(),true));
  choose(selectedFromHash(),false);
  // The browser may have tried navigating to an initially hidden section
  // before the script ran; reveal first and then align the linked heading.
  if(/^#welcome-(kingdom|heroes|history|world)$/.test(location.hash)) {
    window.requestAnimationFrame(()=>{
      document.getElementById('welcome-'+selectedFromHash())?.scrollIntoView({block:'start'});
    });
  }
})();