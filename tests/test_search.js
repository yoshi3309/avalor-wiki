/* Node's built-in test runner. No network or dependencies. */
'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const search = require('../assets/search.js');
const entries = [
  {type:'article',slug:'faelynn',title:'Faelynn',subtitle:'Ranger of the founding age',category:'People & Legends',summary:'Founder of the Hunters Guild',aliases:['Night Mistress','Faelynn Naïlo'],body:'A wood elf ranger',featured:false},
  {type:'article',slug:'house-frozenroar',title:'House Frozenroar',subtitle:'Royal House',category:'Organizations & Factions',summary:'The royal succession',aliases:['Frozenroar Dynasty'],body:'Thirty-four sovereigns',featured:true},
  {type:'article',slug:'hunters-guild',title:'The Hunters Guild',subtitle:'Wayword Sun',category:'Organizations & Factions',summary:'Founded by Faelynn',aliases:[],body:'Dangerous wilderness',featured:false},
  {type:'article',slug:'the-misfits',title:'The Misfits',subtitle:'Champions',category:'People & Legends',summary:'Adventuring fellowship',aliases:[],body:'Moonville Manor and the Ripped Beard',featured:true},
  {type:'section',slug:'avalorian-forces',fragment:'lion-s-bane',title:"Lion's Bane",subtitle:'Section within the Avalorian Forces',category:'Organizations & Factions',summary:'Open this section in The Avalorian Forces.',aliases:['lions bane'],body:'',featured:false}
].map(search.prepare);
test('normalizes apostrophes, accents and whitespace',()=>{
  assert.equal(search.normalize("  Fo’Gurn  "),'fogurn');
  assert.equal(search.normalize('Faelynn Naïlo'),'faelynn nailo');
});
test('finds established nickname as the top result',()=>{
  assert.equal(search.search(entries,'Night Mistress')[0].slug,'faelynn');
});
test('tolerates a one-character misspelling in a proper name',()=>{
  assert.equal(search.search(entries,'Frozenroar')[0].slug,'house-frozenroar');
  assert.equal(search.search(entries,'Froznroar')[0].slug,'house-frozenroar');
});
test('finds retired subarticles as anchor targets',()=>{
  const result=search.search(entries,"Lion's Bane")[0];
  assert.equal(result.type,'section');
  assert.equal(result.fragment,'lion-s-bane');
});
test('filters to the requested archive collection',()=>{
  const out=search.search(entries,'guild','Organizations & Factions');
  assert(out.length>0);
  assert(out.every(x=>x.category==='Organizations & Factions'));
});
test('unmatched searches return nothing',()=>{
  assert.deepEqual(search.search(entries,'somethingthatdoesnotexist'),[]);
});
test('empty search recommends featured public records only',()=>{
  const out=search.search(entries,'');
  assert(out.length>0);
  assert(out.every(x=>x.featured));
});
test('exact titles rank over incidental full-body mentions',()=>{
  assert.equal(search.search(entries,'misfits')[0].slug,'the-misfits');
});
