/* Archives of Avalor: offline, public-only search ranking. No remote services. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AvalorSearch = api;
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';
  const normalize = value => String(value || '').normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/&/g, ' and ').replace(/[’']/g, '')
    .replace(/[^a-z0-9]+/g, ' ').trim().replace(/\s+/g, ' ');
  const words = value => normalize(value).split(' ').filter(Boolean);
  const distance = (a, b, limit = 1) => {
    if (a === b) return 0;
    if (Math.abs(a.length - b.length) > limit) return limit + 1;
    const row = Array.from({length:b.length+1},(_,i)=>i);
    for (let i=1;i<=a.length;i++) {
      let last = row[0]; row[0] = i;
      let best = row[0];
      for (let j=1;j<=b.length;j++) {
        const previous=row[j];
        row[j]=Math.min(row[j]+1,row[j-1]+1,last+(a[i-1]===b[j-1]?0:1));
        last=previous; best=Math.min(best,row[j]);
      }
      if (best>limit) return limit+1;
    }
    return row[b.length];
  };
  const prepare = record => {
    const title = normalize(record.title);
    const aliases = (record.aliases || []).map(normalize);
    const subtitle = normalize(record.subtitle);
    const summary = normalize(record.summary);
    const body = normalize(record.body);
    const terms = [...new Set([title,...aliases,subtitle].flatMap(words))];
    return {...record,_title:title,_aliases:aliases,_subtitle:subtitle,_summary:summary,_body:body,_terms:terms};
  };
  const weigh = (term, item) => {
    if (item._title === term) return 145;
    if (item._aliases.includes(term)) return 135;
    if (item._title.startsWith(term)) return 86;
    if (item._aliases.some(a=>a.startsWith(term))) return 76;
    if (item._title.includes(term)) return 66;
    if (item._aliases.some(a=>a.includes(term))) return 61;
    if (item._subtitle.includes(term)) return 33;
    if (item._summary.includes(term)) return 19;
    if (item._body.includes(term)) return 4;
    if (term.length >= 4) {
      const fuzzy = item._terms.some(w => w.length >= 4 && Math.abs(w.length-term.length) <= 1 && distance(w,term,1) === 1);
      if (fuzzy) return 25;
    }
    return 0;
  };
  const search = (prepared, raw, category='all', limit=20) => {
    const query=normalize(raw);
    const terms=words(query);
    if (!terms.length) return prepared.filter(r=>(category==='all'||r.category===category) && r.featured).slice(0,limit);
    return prepared.filter(r=>category==='all'||r.category===category)
      .map(r=>{
        const strengths=terms.map(t=>weigh(t,r));
        if (strengths.some(n=>n===0)) return null;
        let score=strengths.reduce((a,b)=>a+b,0);
        if (r._title.includes(query)) score+=95;
        if (r._aliases.some(a=>a.includes(query))) score+=85;
        if (r.type==='section' && (r._title.includes(query) || r._aliases.some(a=>a.includes(query)))) score+=12;
        return {r,score};
      }).filter(Boolean).sort((a,b)=>b.score-a.score||a.r.title.localeCompare(b.r.title))
      .slice(0,limit).map(x=>x.r);
  };
  return {normalize, distance, prepare, search};
});
