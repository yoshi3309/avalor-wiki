/* The Archives of Avalor: small offline shell and explicitly selected reading packs.
   All caches are scoped to this public GitHub Pages site, never external sources. */
'use strict';
const SHELL_VERSION = '__AVALOR_SHELL_REVISION__';
const SHELL_FILES = __AVALOR_SHELL_FILES__;
const SHELL_PREFIX = 'avalor-flight-shell-v1-';
const PACK_PREFIX = 'avalor-flight-pack-v1-';
const SHELL_CACHE = SHELL_PREFIX + SHELL_VERSION;
const SCOPE = self.registration.scope;
const ROOT = new URL(SCOPE);
const READY_URL = new URL('offline/ready.json', SCOPE).href;
const FALLBACK_URL = new URL('offline/unavailable/', SCOPE).href;

const withinArchive = url => url.origin === ROOT.origin &&
  url.pathname.startsWith(ROOT.pathname);

async function offlineCopy(request) {
  const names = await caches.keys();
  const packs = names.filter(name => name.startsWith(PACK_PREFIX)).reverse();
  for (const name of packs) {
    const cache = await caches.open(name);
    if (!await cache.match(READY_URL)) continue; // unfinished downloads are never served
    const found = await cache.match(request, {ignoreSearch: true});
    if (found) return found;
  }
  const shell = await caches.open(SHELL_CACHE);
  return shell.match(request, {ignoreSearch: true});
}

function flaggedCopy(response) {
  const headers = new Headers(response.headers);
  headers.set('X-Avalor-Offline-Copy', '1');
  return response.clone().arrayBuffer().then(bytes =>
    new Response(bytes, {status:response.status,statusText:response.statusText,headers})
  );
}

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(SHELL_CACHE);
    await cache.addAll(SHELL_FILES.map(file => new URL(file, SCOPE).href));
    await self.skipWaiting();
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith(SHELL_PREFIX) && name !== SHELL_CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET' || !withinArchive(new URL(request.url))) return;
  event.respondWith((async () => {
    try {
      return await fetch(request); // always prefer current public pages while connected
    } catch (_) {
      const saved = await offlineCopy(request);
      if (saved) return flaggedCopy(saved);
      if (request.mode === 'navigate') {
        const fallback = await offlineCopy(FALLBACK_URL);
        if (fallback) return flaggedCopy(fallback);
        return new Response('<h1>Not saved for offline reading</h1><p>Reconnect and open the Flight Library to save this record.</p>',
          {status:503,headers:{'Content-Type':'text/html; charset=utf-8'}});
      }
      // Images are deliberately not part of text-first packs.
      if (request.destination === 'image') {
        return new Response('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="180" viewBox="0 0 480 180"><rect width="480" height="180" fill="#ddd1b8"/><text x="240" y="92" font-size="20" text-anchor="middle" fill="#443b2d">Illustration available online</text></svg>',
          {headers:{'Content-Type':'image/svg+xml; charset=utf-8'}});
      }
      return Response.error();
    }
  })());
});
