/* Progressive enhancement for optional, public character appearances.
 * Without JavaScript each thumbnail remains a link to its full image. */
(() => {
  'use strict';
  for (const gallery of document.querySelectorAll('[data-portrait-gallery]')) {
    const picture = gallery.querySelector('picture');
    const portrait = picture?.querySelector('img');
    const source = picture?.querySelector('source');
    const caption = gallery.querySelector('[data-portrait-caption]');
    const choices = [...gallery.querySelectorAll('[data-portrait-stage]')];
    if (!portrait || !caption || choices.length < 2) continue;
    for (const choice of choices) {
      choice.addEventListener('click', (event) => {
        const src = choice.dataset.stageSrc;
        if (!src) return;
        event.preventDefault();
        // Keep responsive WebP sources in step with the selected original.
        if (source) {
          if (choice.dataset.stageSrcset) {
            source.setAttribute('srcset', choice.dataset.stageSrcset);
          } else {
            source.removeAttribute('srcset');
          }
        }
        portrait.setAttribute('src', src);
        portrait.setAttribute('alt', choice.dataset.stageAlt || '');
        if (choice.dataset.stageWidth && choice.dataset.stageHeight) {
          portrait.setAttribute('width', choice.dataset.stageWidth);
          portrait.setAttribute('height', choice.dataset.stageHeight);
        } else {
          portrait.removeAttribute('width');
          portrait.removeAttribute('height');
        }
        caption.textContent = choice.dataset.stageCaption || '';
        for (const item of choices) {
          const selected = item === choice;
          item.classList.toggle('is-selected', selected);
          if (selected) item.setAttribute('aria-current', 'true');
          else item.removeAttribute('aria-current');
        }
      });
    }
  }
})();
