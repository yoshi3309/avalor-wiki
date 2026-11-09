"""Smoke-test the public illustration gallery after python build.py."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
index = (SITE / 'gallery/index.html').read_text(encoding='utf-8')
characters = (SITE / 'gallery/characters/index.html').read_text(encoding='utf-8')
lavitz = (SITE / 'articles/lavitz-shawe/index.html').read_text(encoding='utf-8')
assert 'Illustration Gallery' in index, 'Missing gallery heading'
assert 'gallery-wing' in index, 'Missing collection browsing cards'
assert 'lavitz-shawe.jpg' in index and 'lavitz-shawe.jpg' in characters, 'Lavitz portrait absent'
assert 'id="gallery-lightbox"' in index, 'Gallery lightbox absent'
assert 'gallery/characters/?image=lavitz-shawe' in lavitz, 'Missing gallery link in Lavitz article'
assert 'gallery-related' in lavitz, 'Article gallery section missing'
assert 'assets/gallery.js' in index and 'assets/gallery.css' in index, 'Gallery viewer assets missing'
for slug in ('characters', 'locations', 'historical-scenes', 'artifacts-symbols', 'maps-heraldry'):
    assert (SITE / 'gallery' / slug / 'index.html').is_file(), 'Missing gallery collection: ' + slug
    assert 'gallery-data' in (SITE / 'gallery' / slug / 'index.html').read_text(encoding='utf-8')
match = re.search(r'<script id="gallery-data" type="application/json">(.*?)</script>', characters, re.S)
assert match, 'Gallery data is absent'
data = json.loads(match.group(1))
assert len(data) == 1 and data[0]['id'] == 'lavitz-shawe', 'First curated exhibit incorrect'
assert data[0]['related'][0]['slug'] == 'lavitz-shawe', 'Related article resolution incorrect'
assert all('keeper' not in key.lower() for entry in data for key in entry), 'Private data field exposed'
print('Illustration Gallery smoke tests passed (curation, viewer, five collections, article links).')
