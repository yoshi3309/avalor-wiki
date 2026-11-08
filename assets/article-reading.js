(() => {
  'use strict';
  const article = document.querySelector('[data-article-reading]');
  const body = article?.querySelector('.article-body');
  const track = document.querySelector('.article-reading-track');
  if (!article || !body || !track) return;
  const fill = track.querySelector('.article-reading-fill');
  const headings = [...body.querySelectorAll('h2[id]')];
  const desktop = [...article.querySelectorAll('.toc-panel a[href^="#"]')];
  const mobile = [...article.querySelectorAll('.article-mobile-toc a[href^="#"]')];
  let ticking = false;
  const update = () => {
    ticking = false;
    const rect = body.getBoundingClientRect();
    const viewport = window.innerHeight || 800;
    // Start when the opening of the account reaches the reading zone;
    // finish once the end of the account passes that same zone.
    const zone = Math.min(180, viewport * 0.28);
    const total = Math.max(rect.height, 1);
    const percentage = Math.max(0, Math.min(100, Math.round(100 * (zone - rect.top) / total)));
    fill.style.width = percentage + '%';
    track.setAttribute('aria-valuenow', String(percentage));
    let active = headings[0]?.id || '';
    for (const h of headings) {
      if (h.getBoundingClientRect().top <= zone + 35) active = h.id;
      else break;
    }
    for (const link of [...desktop, ...mobile]) {
      const current = link.getAttribute('href') === '#' + active;
      link.classList.toggle('is-current', current);
      if (current) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  };
  const schedule = () => {
    if (!ticking) {ticking = true; requestAnimationFrame(update);}
  };
  window.addEventListener('scroll', schedule, {passive:true});
  window.addEventListener('resize', schedule, {passive:true});
  article.querySelectorAll('.article-mobile-toc a').forEach(a => a.addEventListener('click', () => {
    const details = a.closest('details');
    if (details) details.open = false;
  }));
  update();
})();