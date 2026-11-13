"""Verify curated source-grounded character comparisons and shareable pair pages."""
from pathlib import Path
import json,re,yaml,html as html_utils
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
source=yaml.safe_load((ROOT/'data/character-comparisons.yml').read_text(encoding='utf-8'))
page=(SITE/'compare/index.html').read_text(encoding='utf-8')
m=re.search(r'<script id="dossier-data" type="application/json">(.*?)</script>',page,re.S)
assert m,'Comparison dataset missing from public page'
data=json.loads(m.group(1))
profiles=data['profiles'];presets=data['presets']
assert len(profiles)==21,len(profiles)
assert len(presets)==10,len(presets)
ids={p['id'] for p in profiles}
assert len(ids)==21
expected=('role','affiliations','turning','legacy')
assert [row['key'] for row in data['fields']]==list(expected)
assert len(source['profiles'])==len(profiles)
for record in profiles:
    slug=record['id']
    article_path=ROOT/'content/articles'/f'{slug}.md'
    built=SITE/'articles'/slug/'index.html'
    assert article_path.is_file(),slug
    assert built.is_file(),slug
    html=built.read_text(encoding='utf-8')
    for key in expected:
        fact=record['facts'][key]
        assert fact['text'] and fact['source'].startswith('Chapter: ')
        assert f'id="{fact["chapter"]}"' in html,(slug,key,fact['chapter'])
    if record['image']:
        assert record['image'].startswith('assets/uploads/'),slug
        assert (SITE/record['image']).exists(),slug
        assert record['image_alt'],slug
        assert record['media'] and record['media']['variants'],slug
    assert 'Compare '+record['name'] in html_utils.unescape(html),slug
assert 'assets/comparisons.js' in page and 'assets/comparisons.css' in page
for needle in ('id="dossier-left"','id="dossier-right"','id="dossier-swap"',
               'id="dossier-copy"','id="dossier-rows"','id="dossier-portraits"'):
    assert needle in page,needle
assert 'not a contest of strength' in page
assert 'data-initial-left=""' in page and 'data-initial-right=""' in page
for preset in presets:
    assert preset['left'] in ids and preset['right'] in ids and preset['left']!=preset['right']
    assert 'href="../compare/pairs/'+preset['id']+'/"' in page,preset['id']
    pair_path=SITE/'compare/pairs'/preset['id']/'index.html'
    assert pair_path.is_file(),preset['id']
    pair=pair_path.read_text(encoding='utf-8')
    assert 'data-initial-left="'+preset['left']+'"' in pair,preset['id']
    assert 'data-initial-right="'+preset['right']+'"' in pair,preset['id']
    assert '<meta property="og:url" content="https://yoshi3309.github.io/avalor-wiki/compare/pairs/'+preset['id']+'/">' in pair
    assert preset['title'] in pair
connections=(SITE/'connections/index.html').read_text(encoding='utf-8')
assert 'href="../compare/"' in connections
assert 'Character Comparison Dossiers' in connections
home=(SITE/'index.html').read_text(encoding='utf-8')
assert 'href="./compare/"' in home
script=(SITE/'assets/comparisons.js').read_text(encoding='utf-8')
for phrase in ("new URL(site+'compare/'","navigator.clipboard?.writeText","window.addEventListener('popstate'",
               "recordURL(p.id)+'#'","p.facts[field.key]","sourceURL(p,field.key)","srcset"):
    assert phrase in script,phrase
print('Character comparisons verified: 21 cited profiles, 10 curated pair previews, deep source links and site navigation.')
