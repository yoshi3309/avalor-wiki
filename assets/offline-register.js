/* Register a small public offline shell; reading packs remain opt-in. */
(() => {
  'use strict';
  if (!('serviceWorker' in navigator) || !window.isSecureContext) return;
  const base = new URL(window.AVALOR_ROOT || './', window.location.href);
  if (base.origin !== window.location.origin) return;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(new URL('sw.js', base).href, {scope:base.pathname})
      .catch(() => { /* The Flight Library explains unsupported storage. */ });
  });
})();
