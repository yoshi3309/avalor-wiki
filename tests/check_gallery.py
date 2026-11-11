"""Smoke tests for all curated illustration gallery wings and cross-links."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
index = (SITE / 'gallery/index.html').read_text(encoding='utf-8')
assert 'Illustration Gallery' in index and 'gallery-wing' in index
assert 'id="gallery-lightbox"' in index and 'assets/gallery.js' in index
assert 'gallery-share-link' in index, 'Exhibit sharing control missing'
assert 'Copy exhibit link' in index, 'Accessible share label missing'

expected = {
    'characters': 35,
    'locations': 5,
    'historical-scenes': 2,
    'artifacts-symbols': 1,
    'maps-heraldry': 1,
}
seen=set()
for collection, minimum in expected.items():
    p=SITE / 'gallery' / collection / 'index.html'
    assert p.is_file(), 'Missing collection: ' + collection
    html=p.read_text(encoding='utf-8')
    match=re.search(r'<script id="gallery-data" type="application/json">(.*?)</script>',html,re.S)
    assert match, 'Missing gallery JSON: ' + collection
    items=json.loads(match.group(1))
    assert len(items)>=minimum, f'{collection} needs at least {minimum} exhibits, found {len(items)}'
    for item in items:
        assert item['id'] not in seen, 'Duplicate gallery exhibit: ' + item['id']
        seen.add(item['id'])
        assert item['alt'] and item['caption'] and item['related'], item['id']
        assert 'keeper' not in item['id'].lower(), 'Restricted reference in gallery ID'
        assert (SITE / item['image'].lstrip('/')).exists(), 'Gallery image not found: '+item['image']
        for rec in item['related']:
            assert (SITE / 'articles'/rec['slug']/'index.html').exists(), rec['slug']
assert len(seen)>=40, 'Gallery is missing public character portraits'
for article, exhibit in [('lavitz-shawe','lavitz-shawe'),('heureux','heureux'),('the-six','the-six-fellowship'),('kingdom-of-avalor','avalor-royal-map'),('jaznaar','portrait-jaznaar'),('samuel-the-devoted','portrait-samuel-the-devoted'),('katiri-tenderfoot','portrait-katiri-tenderfoot'),('renada','renada'),('black-tower','the-black-tower'),('heavens-heart','heavens-heart'),('stanleyville','stanleyville')]:
    page=(SITE/'articles'/article/'index.html').read_text(encoding='utf-8')
    assert 'gallery-related' in page and ('image='+exhibit) in page, (article,exhibit)
print('Illustration Gallery passed: five populated collections, vetted images, per-article exhibit links, and share control.')

# Curated location exhibits are the primary reference for published landscapes.
# The builder also admits later place-image assignments without duplicate entries.
for exhibit in ('renada','the-black-tower','heavens-heart','stanleyville'):
    location=(SITE/'gallery/locations/index.html').read_text(encoding='utf-8')
    assert '"id": "'+exhibit+'"' in location or '"id":"'+exhibit+'"' in location, exhibit
