const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('assets/article-reading.js', 'utf8');
function setup(clipboard=true, reject=false) {
  const copies=[],prompts=[], feedback={textContent:''};
  const heading={id:'the-first-teaching',querySelector:q=>q==='.chapter-share-feedback'?feedback:null,getBoundingClientRect:()=>({top:0}),hasAttribute:()=>true};
  const button={dataset:{chapterId:'the-first-teaching',chapterTitle:'The first teaching',chapterShare:'link'},closest:q=>q==='h2[id]'?heading:null};
  let click;
  const body={getBoundingClientRect:()=>({top:0,height:1000}),contains:x=>x===heading||x===button,querySelectorAll:q=>q==='h2[id]'?[heading]:q==='button[data-chapter-share]'?[button]:q==='.chapter-share-feedback'?[feedback]:[],addEventListener:(event,fn)=>{if(event==='click')click=fn;}};
  const article={dataset:{readingTitle:'Lowkee Nicklebane'},querySelector:q=>q==='.article-body'?body:null,querySelectorAll:()=>[],classList:{add:()=>{}}};
  const document={title:'Lowkee Nicklebane · The Archives of Avalor',querySelector:q=>q==='[data-article-reading]'?article:q==='.article-reading-track'?{querySelector:()=>({style:{}}),setAttribute:()=>{}}:q==='link[rel="canonical"]'?{href:'https://yoshi3309.github.io/avalor-wiki/articles/lowkee/'}:null};
  const window={location:{href:'https://yoshi3309.github.io/avalor-wiki/articles/lowkee/'},innerHeight:800,addEventListener:()=>{},prompt:(...args)=>prompts.push(args)};
  const navigator=clipboard?{clipboard:{writeText:async s=>{if(reject)throw Error('No');copies.push(s)}}}:{};
  vm.runInNewContext(script,{document,window,navigator,URL,requestAnimationFrame:fn=>fn()});
  return {button,copies,prompts,feedback,click:()=>click({target:{closest:()=>button}})};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
test('copies canonical article chapter URL',async()=>{const a=setup();a.click();await tick();assert.deepEqual(a.copies,['https://yoshi3309.github.io/avalor-wiki/articles/lowkee/#the-first-teaching']);assert.equal(a.feedback.textContent,'Chapter link copied.');});
test('copies cited article and section without false quotes',async()=>{const a=setup();a.button.dataset.chapterShare='citation';a.click();await tick();assert.equal(a.copies[0],'Lowkee Nicklebane — The first teaching | The Archives of Avalor | https://yoshi3309.github.io/avalor-wiki/articles/lowkee/#the-first-teaching');assert.equal(a.feedback.textContent,'Chapter citation copied.');});
test('clipboard rejection offers manual copy',async()=>{const a=setup(true,true);a.click();await tick();assert.equal(a.copies.length,0);assert.equal(a.prompts.length,1);assert.equal(a.feedback.textContent,'Copy from the open dialog.');});
test('clipboard unavailable offers manual copy',async()=>{const a=setup(false);a.click();await tick();assert.equal(a.prompts.length,1);});
