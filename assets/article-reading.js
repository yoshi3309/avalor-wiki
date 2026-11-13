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
  // Move keyboard/screen-reader focus to the requested section after jumping.
  // Plain anchors remain fully usable when scripting is unavailable.
  for (const link of [...desktop,...mobile]) link.addEventListener('click',()=>{
    const raw = link.getAttribute('href') || '';
    const heading = raw.startsWith('#') ? document.getElementById(decodeURIComponent(raw.slice(1))) : null;
    if (heading && body.contains(heading)) {
      if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex','-1');
      requestAnimationFrame(()=>heading.focus({preventScroll:true}));
    }
    const details = link.closest('.article-mobile-toc');
    if (details) details.open = false;
  });
  // Copy chapter URLs or publication citations without fabricating quotations.
  // The # links remain functional without this script.
  const canonical = document.querySelector('link[rel="canonical"]')?.href || window.location.href.split('#')[0];
  const articleTitle = article.dataset.readingTitle || document.title.split(' · ')[0];
  const shareButtons = [...body.querySelectorAll('button[data-chapter-share]')];
  if (shareButtons.length) article.classList.add('chapter-sharing-ready');
  async function copyChapter(button) {
    const heading = button.closest('h2[id]');
    if (!heading || !body.contains(heading)) return;
    const kind = button.dataset.chapterShare;
    if (kind !== 'link' && kind !== 'citation') return;
    const url = new URL(canonical, window.location.href);
    url.hash = button.dataset.chapterId || heading.id;
    const payload = kind === 'citation'
      ? articleTitle + ' — ' + (button.dataset.chapterTitle || '') + ' | The Archives of Avalor | ' + url.href
      : url.href;
    for (const node of body.querySelectorAll('.chapter-share-feedback')) node.textContent = '';
    const feedback = heading.querySelector('.chapter-share-feedback');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(payload);
      if (feedback) feedback.textContent = kind === 'citation' ? 'Chapter citation copied.' : 'Chapter link copied.';
    } catch (_) {
      window.prompt('Select and copy this ' + (kind === 'citation' ? 'chapter citation' : 'chapter link') + ':', payload);
      if (feedback) feedback.textContent = 'Copy from the open dialog.';
    }
  }
  body.addEventListener('click', event => {
    const button = event.target.closest('button[data-chapter-share]');
    if (button && body.contains(button)) void copyChapter(button);
  });
  update();
})();