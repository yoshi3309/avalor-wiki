/* Explicit, versioned flight reading packs. No remote requests or user tracking. */
(() => {
  'use strict';
  const page = document.querySelector('[data-flight-library]');
  if (!page) return;

  const base = new URL(window.AVALOR_ROOT || '../', location.href);
  const prefix = 'avalor-flight-pack-v1-';
  const readyURL = new URL('offline/ready.json', base).href;
  const list = document.getElementById('flight-pack-list');
  const message = document.getElementById('flight-library-status');
  const summary = document.getElementById('flight-library-summary');
  const formatter = new Intl.NumberFormat(undefined, {maximumFractionDigits:1});
  const sizeText = bytes => bytes >= 1024 * 1024
    ? formatter.format(bytes / 1048576) + ' MB'
    : formatter.format(bytes / 1024) + ' KB';
  const hasSupport = 'serviceWorker' in navigator && 'caches' in window && window.isSecureContext;
  let busy = false;
  let catalogue = null;
  const packCacheName = pack => prefix + pack.id + '-' + pack.revision;
  const packURL = path => {
    if (!/^[a-z0-9][a-z0-9-]*\/(?:[a-z0-9-]+\/)*$/.test(path) && path !== 'search-index.json')
      throw new Error('Invalid published page path');
    const url = new URL(path, base);
    if (url.origin !== base.origin || !url.pathname.startsWith(base.pathname))
      throw new Error('Invalid offline destination');
    return url.href;
  };

  function status(text, isError=false) {
    message.textContent = text;
    message.classList.toggle('is-error', isError);
  }

  async function checkReady(name, pack) {
    const cache = await caches.open(name);
    const marker = await cache.match(readyURL);
    if (!marker) return false;
    try {
      const meta = await marker.json();
      if (meta.id !== pack.id || meta.revision !== name.slice((prefix + pack.id + '-').length)) return false;
      for (const path of pack.paths) if (!await cache.match(packURL(path))) return false;
      return true;
    } catch (_) {
      return false;
    }
  }

  async function stateOf(pack) {
    const names = await caches.keys();
    const current = packCacheName(pack);
    if (names.includes(current) && await checkReady(current, pack))
      return 'ready';
    const others = names.filter(name => name.startsWith(prefix + pack.id + '-') && name !== current);
    for (const name of others) if (await checkReady(name, pack))
      return 'outdated';
    return 'none';
  }

  const node = (tag, className, content) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content != null) el.textContent = content;
    return el;
  };

  async function render() {
    list.replaceChildren();
    const packs = catalogue.packs;
    const stored = await Promise.all(packs.map(stateOf));
    const readyCount = stored.filter(v => v === 'ready').length;
    const olderCount = stored.filter(v => v === 'outdated').length;
    summary.textContent = readyCount + ' current packs ready' +
      (olderCount ? ' · ' + olderCount + ' older pack' + (olderCount === 1 ? '' : 's') + ' saved' : '') +
      ' · Select a pack before going offline.';
    for (let i = 0; i < packs.length; i++) {
      const pack = packs[i], state = stored[i];
      const card = node('section', 'flight-pack');
      const top = node('div', 'flight-pack-heading');
      const heading = node('div');
      heading.append(node('div', 'kicker', pack.type === 'encyclopedia' ? 'THE COMPLETE PUBLIC COLLECTION' : 'A CURATED READING JOURNEY'));
      heading.append(node('h3', '', pack.title));
      top.append(heading);
      top.append(node('span', 'flight-pack-status ' + state, state === 'ready' ? 'Ready offline' : state === 'outdated' ? 'Update available' : 'Not downloaded'));
      card.append(top);
      card.append(node('p', 'flight-pack-description', pack.description));
      card.append(node('p', 'flight-pack-details', pack.paths.length + ' pages · approx. ' + sizeText(pack.bytes) + ' · text-first'));
      const actions = node('div', 'flight-pack-actions');
      const save = node('button', 'flight-action-primary', state === 'ready' ? 'Re-download' : state === 'outdated' ? 'Update offline copy' : 'Save for offline');
      save.type = 'button';
      save.disabled = busy || !navigator.onLine;
      save.addEventListener('click', () => void download(pack));
      actions.append(save);
      if (state !== 'none') {
        const open = node('a', 'flight-action-link', 'Open saved reading ↗︎');
        open.href = packURL(pack.start);
        actions.append(open);
        const remove = node('button', 'flight-action-remove', 'Remove download');
        remove.type = 'button';
        remove.disabled = busy;
        remove.addEventListener('click', () => void removePack(pack));
        actions.append(remove);
      }
      card.append(actions);
      list.append(card);
    }
  }

  async function removePack(pack) {
    if (busy) return;
    busy = true;
    try {
      const names = await caches.keys();
      await Promise.all(names.filter(name => name.startsWith(prefix + pack.id + '-')).map(name => caches.delete(name)));
      status('Removed offline pages for ' + pack.title + '. Bookmarks and reading progress were not changed.');
    } catch (error) {
      status('Could not remove this download: ' + error.message, true);
    } finally {
      busy = false;
      await render();
    }
  }

  async function download(pack) {
    if (busy || !navigator.onLine) {
      status('Connect to the internet before saving new reading material.', true);
      return;
    }
    busy = true;
    const name = packCacheName(pack);
    let completed = false;
    try {
      // Never replace an older ready pack until the entire new revision succeeds.
      await caches.delete(name);
      const cache = await caches.open(name);
      let index = 0, done = 0;
      status('Saving ' + pack.title + ': 0 of ' + pack.paths.length + ' pages.');
      await render();
      const worker = async () => {
        while (index < pack.paths.length) {
          const path = pack.paths[index++];
          const url = packURL(path);
          const response = await fetch(url, {cache:'reload', redirect:'error'});
          if (!response.ok || response.headers.get('X-Avalor-Offline-Copy') === '1')
            throw new Error('The connection was interrupted while saving ' + path);
          const type = response.headers.get('content-type') || '';
          if (!(type.includes('text/html') || (path === 'search-index.json' && type.includes('json'))))
            throw new Error('Unexpected content received for ' + path);
          if (new URL(response.url).origin !== base.origin)
            throw new Error('The source left the public Archives');
          await cache.put(url, response);
          done++;
          status('Saving ' + pack.title + ': ' + done + ' of ' + pack.paths.length + ' pages.');
        }
      };
      await Promise.all(Array.from({length:Math.min(3,pack.paths.length)},worker));
      for (const path of pack.paths) {
        if (!await cache.match(packURL(path))) throw new Error('A page failed verification: ' + path);
      }
      await cache.put(readyURL, new Response(JSON.stringify({id:pack.id, revision:pack.revision, count:pack.paths.length}), {headers:{'Content-Type':'application/json'}}));
      const names = await caches.keys();
      await Promise.all(names.filter(old => old.startsWith(prefix + pack.id + '-') && old !== name)
        .map(old => caches.delete(old)));
      completed = true;
      status(pack.title + ' is ready for airplane mode. Open a saved page before departure and test with Airplane Mode on.');
    } catch (error) {
      await caches.delete(name);
      status('Download incomplete; this pack is NOT ready. ' + error.message + '. Reconnect and try again.', true);
    } finally {
      busy = false;
      await render();
    }
  }

  async function initialize() {
    if (!hasSupport) {
      status('This browser does not support secure offline storage here. Try regular Safari or Chrome, outside private browsing.', true);
      return;
    }
    if (!navigator.onLine) status('Airplane mode is on. Previously saved packs may still be available.');
    try {
      const response = await fetch(new URL('offline-manifest.json', base), {cache:'no-store'});
      if (!response.ok) throw new Error('The offline catalogue is unavailable');
      catalogue = await response.json();
      if (catalogue.schema !== 1 || !Array.isArray(catalogue.packs))
        throw new Error('The offline catalogue format is unsupported');
      await navigator.serviceWorker.ready;
      await render();
      if (navigator.onLine) status('Choose a journey or the full encyclopedia to download. Only public articles are included.');
      window.addEventListener('online', () => {if (!busy) { status('Connection restored.'); void render();}});
      window.addEventListener('offline', () => {status('Airplane mode detected. Open any ready pack.'); void render();});
    } catch (error) {
      status('Unable to open the Flight Library: ' + error.message + '. Visit this page while connected first.', true);
    }
  }
  void initialize();
})();
