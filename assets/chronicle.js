(() => {
  'use strict';
  const chronicle = document.querySelector('.chronicle-v2');
  if (!chronicle) return;
  const buttons = [...chronicle.querySelectorAll('[data-period]')];
  const events = [...chronicle.querySelectorAll('[data-chronicle-event]')];
  const groups = [...chronicle.querySelectorAll('[data-chronicle-section]')];
  const topic = chronicle.querySelector('#chronicle-topic');
  const precision = chronicle.querySelector('#chronicle-precision');
  const search = chronicle.querySelector('#chronicle-search');
  const counter = chronicle.querySelector('#chronicle-count');
  const empty = chronicle.querySelector('#chronicle-empty');
  const reset = chronicle.querySelector('#chronicle-reset');
  let period = 'all';
  const update = () => {
    const needle = search.value.toLocaleLowerCase().trim();
    const terms = needle.split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const event of events) {
      const match = (period === 'all' || event.dataset.period === period)
        && (topic.value === 'all' || event.dataset.topic === topic.value)
        && (precision.value === 'all' || event.dataset.precision === precision.value)
        && terms.every(term => event.dataset.search.includes(term));
      event.hidden = !match;
      if (match) visible++;
    }
    for (const section of groups) {
      section.hidden = !section.querySelector('[data-chronicle-event]:not([hidden])');
    }
    buttons.forEach(button => {
      const active = button.dataset.period === period;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    counter.textContent = visible + (visible === 1 ? ' event' : ' events') + ' in the public record';
    empty.hidden = visible !== 0;
  };
  buttons.forEach(button => button.addEventListener('click', () => {
    period = button.dataset.period;
    update();
  }));
  [topic, precision, search].forEach(control => control.addEventListener(control === search ? 'input' : 'change', update));
  reset.addEventListener('click', () => {
    period = 'all'; topic.value = 'all'; precision.value = 'all'; search.value = '';
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
    update();
  });
  chronicle.querySelectorAll('[data-chronicle-jump]').forEach(link => link.addEventListener('click', () => {
    period = link.dataset.chronicleJump;
    topic.value = 'all'; precision.value = 'all'; search.value = '';
    update();
  }));
  const hash = decodeURIComponent(location.hash.slice(1));
  const anchor = hash && document.getElementById(hash);
  if (anchor) {
    const section = anchor.closest('[data-chronicle-section]');
    if (section) {
      period = section.dataset.chronicleSection;
      update();
      requestAnimationFrame(() => anchor.scrollIntoView({block:'start'}));
    } else update();
  } else update();
})();
