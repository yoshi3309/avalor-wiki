(() => {
  'use strict';
  const data = document.getElementById('gallery-data');
  const modal = document.getElementById('gallery-lightbox');
  if (!data || !modal) return;
  const entries = JSON.parse(data.textContent || '[]');
  if (!entries.length) return;
  const root = window.AVALOR_ROOT || '../';
  const dialog = modal.querySelector('.gallery-lightbox-dialog');
  const cards = [...document.querySelectorAll('.gallery-card[data-gallery-index]')];
  const image = document.getElementById('gallery-viewer-image');
  const heading = document.getElementById('gallery-viewer-title');
  const caption = document.getElementById('gallery-viewer-caption');
  const credit = document.getElementById('gallery-viewer-credit');
  const category = document.getElementById('gallery-viewer-category');
  const counter = document.getElementById('gallery-viewer-counter');
  const links = document.getElementById('gallery-viewer-links');
  const previous = document.getElementById('gallery-viewer-previous');
  const next = document.getElementById('gallery-viewer-next');
  const closeButton = modal.querySelector('.gallery-viewer-close');
  let active = -1;
  let returnFocus = null;

  function setUrl(id) {
    const url = new URL(window.location.href);
    if (id) url.searchParams.set('image', id);
    else url.searchParams.delete('image');
    window.history.replaceState(null, '', url.pathname + url.search + url.hash);
  }

  function display(index) {
    active = (index + entries.length) % entries.length;
    const entry = entries[active];
    image.src = root + entry.image;
    image.alt = entry.alt;
    heading.textContent = entry.title;
    caption.textContent = entry.caption;
    category.textContent = entry.collection_title + (entry.era ? ' · ' + entry.era : '');
    credit.textContent = entry.credit ? 'Artwork credit: ' + entry.credit : '';
    credit.hidden = !entry.credit;
    counter.textContent = String(active + 1).padStart(2, '0') + ' / ' + String(entries.length).padStart(2, '0');
    previous.disabled = entries.length < 2;
    next.disabled = entries.length < 2;
    links.replaceChildren();
    if (entry.related.length) {
      for (const record of entry.related) {
        const a = document.createElement('a');
        a.href = root + 'articles/' + record.slug + '/';
        a.textContent = record.title + ' ↗';
        links.append(a);
      }
    } else {
      const p = document.createElement('p');
      p.className = 'gallery-no-reference';
      p.textContent = 'No related archive record has been assigned.';
      links.append(p);
    }
    setUrl(entry.id);
  }

  function open(index) {
    if (index < 0 || index >= entries.length) return;
    if (modal.hidden) {
      returnFocus = document.activeElement;
      modal.hidden = false;
      modal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('gallery-viewer-open');
    }
    display(index);
    closeButton.focus();
  }

  function close() {
    if (modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('gallery-viewer-open');
    image.removeAttribute('src');
    setUrl('');
    active = -1;
    if (returnFocus && document.contains(returnFocus)) returnFocus.focus();
    else if (cards.length) cards[0].focus();
    returnFocus = null;
  }

  cards.forEach((card, index) => card.addEventListener('click', () => open(index)));
  modal.querySelectorAll('[data-gallery-close]').forEach(button => button.addEventListener('click', close));
  previous.addEventListener('click', () => { display(active - 1); });
  next.addEventListener('click', () => { display(active + 1); });
  document.addEventListener('keydown', event => {
    if (modal.hidden) return;
    if (event.key === 'Escape') { event.preventDefault(); close(); return; }
    if (event.key === 'ArrowLeft' && entries.length > 1) { event.preventDefault(); display(active - 1); return; }
    if (event.key === 'ArrowRight' && entries.length > 1) { event.preventDefault(); display(active + 1); return; }
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('button:not([disabled]),a[href]')];
    if (!focusable.length) { event.preventDefault(); dialog.focus(); return; }
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first.focus();
    }
  });
  const requested = new URLSearchParams(window.location.search).get('image');
  if (requested) {
    const index = entries.findIndex(item => item.id === requested);
    if (index !== -1) open(index);
  }
})();
