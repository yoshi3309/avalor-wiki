"""Smoke test sourced, curated public Connections Explorer."""
from pathlib import Path
import json,re
SITE=Path(__file__).resolve().parent.parent/'_site'
page=(SITE/'connections/index.html').read_text(encoding='utf-8')
m=re.search(r'<script type="application/json" id="cross-data">(.*?)</script>',page,re.S)
assert m,'Missing cross-archive public dataset'
data=json.loads(m.group(1))
nodes=data['nodes'];edges=data['edges']; ids={n['id'] for n in nodes}
assert len(nodes)>=60 and len(ids)==len(nodes)
assert len(edges)>=88
assert all(n['article']==n['id'] for n in nodes)
for required in ('heyden-of-the-goldenfoot','gomo','silver-of-moonlight','jinlin-vechon','king-gerran-frozenroar','kel-maris','cid-the-blood-king','jaaris','zauks'):
    assert required in ids, required
for a,b in (('heyden-of-the-goldenfoot','hunters-guild'),('heyden-of-the-goldenfoot','gomo'),('king-gerran-frozenroar','king-gradvum-frozenroar'),('jaaris','fo-gurn'),('jinlin-vechon','cid-the-blood-king')):
    assert any({e['from'],e['to']}=={a,b} for e in edges), (a,b)
assert all(n['kind'] in ('people','organizations','places','events') for n in nodes)
for e in edges:
    assert e['from'] in ids and e['to'] in ids and e['from']!=e['to']
    assert e['label'] and e['source_title']
    assert (SITE/'articles'/e['evidence']/'index.html').is_file(),e['evidence']
for item in nodes: assert (SITE/'articles'/item['article']/'index.html').is_file(),item['article']
for text in ('id="cross-search"','id="cross-kind"','id="cross-orbit"','id="cross-edges"','assets/connections-web.js'):
    assert text in page,text
six=(SITE/'connections/the-six/index.html').read_text(encoding='utf-8')
assert 'id="connection-web-return"' in six
lavitz=(SITE/'articles/lavitz-shawe/index.html').read_text(encoding='utf-8')
assert 'connections/?focus=lavitz-shawe' in lavitz
assert 'connection-web-article-prompt' in lavitz
print('Curated Connections Explorer validated: records, sources, interactive controls and diagram bridges.')
