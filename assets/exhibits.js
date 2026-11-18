(() => {
  'use strict';
  const search=document.getElementById('exhibits-search');
  const period=document.getElementById('exhibits-period');
  const count=document.getElementById('exhibits-count');
  const empty=document.getElementById('exhibits-empty');
  const cards=[...document.querySelectorAll('[data-exhibit-card]')];
  if(!search || !period || !count || !empty || !cards.length)return;
  function update() {
    const q=search.value.trim().toLocaleLowerCase(), group=period.value;
    let visible=0;
    for(const card of cards) {
      const show=(group==='all'||card.dataset.exhibitGroup===group)
        &&(!q||(card.dataset.exhibitText||'').toLocaleLowerCase().includes(q));
      card.hidden=!show;
      if(show)visible++;
    }
    count.textContent=visible+' OF '+cards.length+' EXHIBITS';
    empty.hidden=visible!==0;
  }
  search.addEventListener('input',update);
  period.addEventListener('change',update);
  update();
})();