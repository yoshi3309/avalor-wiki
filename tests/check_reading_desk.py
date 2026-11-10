"""Check the account-free, public-metadata-only Personal Reading Desk."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
index=json.loads((SITE/'reading-desk-index.json').read_text(encoding='utf-8'))
assert len(index)>=100
assert len({item['slug'] for item in index})==len(index)
assert all(set(item)=={'slug','title','summary','category'} for item in index)
page=(SITE/'reading-desk/index.html').read_text(encoding='utf-8')
article=(SITE/'articles/lavitz-shawe/index.html').read_text(encoding='utf-8')
home=(SITE/'index.html').read_text(encoding='utf-8')
script=(SITE/'assets/reading-desk.js').read_text(encoding='utf-8')
assert 'id="reading-continue-list"' in page and 'id="reading-bookmarked-list"' in page
assert 'id="reading-completed-list"' in page and 'id="reading-recent-list"' in page
assert 'only in this browser on this device' in page
for attr in ('data-reading-slug="lavitz-shawe"','id="reading-bookmark"'):
    assert attr in article, attr
assert 'reading-desk/' in home and 'assets/reading-desk.js' in home
assert 'id="reading-finished"' not in article and 'class="reading-desk-entry"' not in article
assert 'aria-label="My Reading Desk"' in article
assert "localStorage.setItem(KEY" in script and "data-reading-action" in script
assert 'fetch(root+\'reading-desk-index.json\')' in script
assert 'completed:next' in script and 'chapter:active' in script
print('Personal Reading Desk build checks passed.')
