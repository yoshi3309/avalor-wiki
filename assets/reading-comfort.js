(() => {
  'use strict';
  // Anonymous, per-browser reading preferences; no accounts or remote requests.
  // Executed in <head> to apply the stored typography before article paint.
  const KEY='avalor-reading-comfort-v1';
  const defaults={size:'comfortable',font:'literary',contrast:false,motion:false};
  const sizes=new Set(['comfortable','large','extra-large']);
  const fonts=new Set(['literary','clear']);
  let storageAvailable=true;
  function sanitize(value) {
    const v=(value && typeof value==='object' && !Array.isArray(value))?value:{};
    return {
      size:sizes.has(v.size)?v.size:defaults.size,
      font:fonts.has(v.font)?v.font:defaults.font,
      contrast:v.contrast===true,
      motion:v.motion===true
    };
  }
  function read() {
    try {return sanitize(JSON.parse(localStorage.getItem(KEY)||'null'));}
    catch (_) {storageAvailable=false;return {...defaults};}
  }
  let prefs=read();
  function apply() {
    const html=document.documentElement;
    html.dataset.readingSize=prefs.size;
    html.dataset.readingFont=prefs.font;
    html.dataset.readingContrast=prefs.contrast?'high':'standard';
    html.dataset.readingMotion=prefs.motion?'reduce':'system';
  }
  apply();
  function init() {
    const trigger=document.getElementById('reading-prefs-trigger');
    const panel=document.getElementById('reading-prefs-panel');
    const closeButton=document.getElementById('reading-prefs-close');
    const reset=document.getElementById('reading-prefs-reset');
    const contrast=document.getElementById('reading-prefs-contrast');
    const motion=document.getElementById('reading-prefs-motion');
    const status=document.getElementById('reading-prefs-status');
    const host=document.getElementById('reading-prefs');
    if (!trigger||!panel||!host||!contrast||!motion)return;
    const sizeButtons=[...panel.querySelectorAll('[data-reader-size]')];
    const fontButtons=[...panel.querySelectorAll('[data-reader-font]')];
    function sync() {
      sizeButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.readerSize===prefs.size)));
      fontButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.readerFont===prefs.font)));
      contrast.checked=prefs.contrast;
      motion.checked=prefs.motion;
    }
    function announce(message) {
      if (!status)return;
      status.textContent=message+(storageAvailable?'':' Browser storage is unavailable; settings may not persist when you leave this page.');
    }
    function save() {
      apply();
      try {localStorage.setItem(KEY,JSON.stringify(prefs));storageAvailable=true;}
      catch (_) {storageAvailable=false;}
      sync();
      announce('Reading preferences updated.');
    }
    function close(restore=false) {
      if (panel.hidden)return;
      panel.hidden=true;
      trigger.setAttribute('aria-expanded','false');
      if (restore)trigger.focus();
    }
    function open() {
      panel.hidden=false;
      trigger.setAttribute('aria-expanded','true');
      sizeButtons[0]?.focus();
    }
    trigger.addEventListener('click',()=>panel.hidden?open():close(true));
    closeButton?.addEventListener('click',()=>close(true));
    sizeButtons.forEach(b=>b.addEventListener('click',()=>{prefs.size=b.dataset.readerSize;save();}));
    fontButtons.forEach(b=>b.addEventListener('click',()=>{prefs.font=b.dataset.readerFont;save();}));
    contrast.addEventListener('change',()=>{prefs.contrast=contrast.checked;save();});
    motion.addEventListener('change',()=>{prefs.motion=motion.checked;save();});
    reset?.addEventListener('click',()=>{prefs={...defaults};save();announce('Default reading preferences restored.');});
    document.addEventListener('pointerdown',e=>{if(!panel.hidden&&!host.contains(e.target))close();});
    document.addEventListener('keydown',e=>{
      if(e.key==='Escape'&&!panel.hidden) {e.preventDefault();close(true);}
    });
    window.addEventListener('storage',e=>{
      if(e.key!==KEY)return;
      prefs=read();apply();sync();
      announce('Reading preferences updated in another tab.');
    });
    sync();
    if(!storageAvailable)announce('Reading preferences available for this page.');
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();