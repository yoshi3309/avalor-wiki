(() => {
 'use strict';
 // Appearance is independent of the Reading Comfort storage key.
 const KEY='avalor-appearance-v1';
 const root=document.documentElement;
 function read(){try{return localStorage.getItem(KEY)==='vellum'?'vellum':'night'}catch(_){return 'night'}}
 function apply(value){root.dataset.appearance=value;const b=document.getElementById('appearance-toggle');if(b){const next=value==='night'?'Vellum':'Night';b.setAttribute('aria-label','Switch to '+next+' appearance');b.setAttribute('aria-pressed',String(value==='vellum'));const label=b.querySelector('.appearance-toggle-label');if(label)label.textContent=value==='night'?'Night':'Vellum';const icon=b.querySelector('.appearance-toggle-icon');if(icon)icon.textContent=value==='night'?'☾':'☼'}}
 apply(read());
 function init(){const b=document.getElementById('appearance-toggle');if(!b)return;apply(read());b.addEventListener('click',()=>{const next=root.dataset.appearance==='night'?'vellum':'night';apply(next);try{localStorage.setItem(KEY,next)}catch(_){}});window.addEventListener('storage',e=>{if(e.key===KEY)apply(read())})}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();