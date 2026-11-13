"""Check that Atlas Through Time uses only reviewed public geography."""
from pathlib import Path
import json,re,yaml
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
events=yaml.safe_load((ROOT/'data/living-chronicle.yml').read_text(encoding='utf-8'))['events']
map_src=yaml.safe_load((ROOT/'data/avalor-map.yml').read_text(encoding='utf-8'))
links=yaml.safe_load((ROOT/'data/atlas-history.yml').read_text(encoding='utf-8'))['links']
# Addendum 006 added four original-campaign death milestones to the earlier 18;
# Addendum 007 established their year as 2000 AF. No unsupported map pins were added.
assert len(events)==22, len(events)
assert all(e['id'] in {x['id'] for x in events} for e in
           ({'id':'stanleyville-deaths'}, {'id':'hydra-temple-deaths'},
            {'id':'jaznaar-final-rest'}, {'id':'zauks-end'}))
assert len(links)==6, len(links)
map_by_id={loc['id']:loc for loc in map_src['locations']}
events_by_id={e['id']:e for e in events}
assert len(events_by_id)==len(events)
assert len({x['event'] for x in links})==len(links)
for linked in links:
    assert linked['event'] in events_by_id
    assert linked['relation'] in ('event-site','associated-place','affected-region')
    assert len(linked['note'])>35
    loc=map_by_id[linked['place']]
    assert loc['published'] is True
    assert loc['provisional'] is False
    assert isinstance(loc['x'],(int,float)) and isinstance(loc['y'],(int,float))
    assert 0<=loc['x']<=100 and 0<=loc['y']<=100
map_page=(SITE/'map/index.html').read_text(encoding='utf-8')
chronicle=(SITE/'chronicle/index.html').read_text(encoding='utf-8')
for token in ('id="atlas-history"','id="atlas-history-period"','id="atlas-history-all"',
              'id="atlas-history-cards"','id="atlas-history-count"','id="atlas-history-detail"',
              'id="atlas-history-share"','id="atlas-history-data"',
              'assets/atlas-time.css','assets/atlas-time.js','atlas-history-drawer'):
    assert token in map_page, 'Atlas feature missing '+token
assert map_page.count('data-history-card')==len(events)
assert map_page.count('data-history-mapped="true"')==len(links)
assert map_page.count('data-history-mapped="false"')==len(events)-len(links)
raw=re.search(r'<script id="atlas-history-data" type="application/json">(.*?)</script>',map_page,re.S)
assert raw
embedded=json.loads(raw.group(1))
assert [e['id'] for e in embedded]==[e['id'] for e in events]
for actual,original in zip(embedded,events):
    for field in ('date','date_kind','period','text','title','article'):
        assert actual[field]==original[field],(actual['id'],field)
    assert actual['date_label'] and actual['date_note']
    assert (SITE/'articles'/actual['article']/'index.html').exists()
    if actual['atlas']:
        link=next(x for x in links if x['event']==actual['id'])
        assert actual['atlas']['pin']==link['place']
        assert actual['atlas']['relation']==link['relation']
        assert link['note'] in actual['atlas']['note']
        assert 'map/?event='+actual['id']+'#atlas-history-detail' in chronicle
    else:
        assert 'map/?event='+actual['id']+'#atlas-history-detail' not in chronicle
    assert 'id="event-'+actual['id']+'"' in chronicle
    assert 'data-history-id="'+actual['id']+'"' in map_page
assert 'History has a place' in chronicle
script=(SITE/'assets/atlas-time.js').read_text(encoding='utf-8')
map_js=(SITE/'assets/map.js').read_text(encoding='utf-8')
for token in ("avalor:history-pins","avalor:history-focus","history.pushState","history.replaceState",
              "navigator.clipboard?.writeText","sourceLink.href=","url.searchParams.set('event',id)"):
    assert token in script or token in map_js,token
assert 'historicalPins.has(loc.id)' in map_js
assert 'isPublic(loc)' in map_js
print('Atlas Through Time passed:',len(events),'events and',len(links),'source-qualified geographic connections.')
