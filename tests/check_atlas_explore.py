"""Verify regional atlas controls and safe public pin-navigation enhancements."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
map_page=(ROOT/'_site/map/index.html').read_text(encoding='utf-8')
js=(ROOT/'_site/assets/map.js').read_text(encoding='utf-8')
for attr in ('atlas-area','atlas-focus-area','atlas-trail','atlas-trail-status','atlas-trail-previous','atlas-trail-next','atlas-share-place','atlas-share-status'):
    assert 'id="'+attr+'"' in map_page, 'Missing atlas control: '+attr
for marker in ("AREA_VIEWS","TRAILS","isPublic(loc)","mapUrlFor","showTrailStep","beginTrail"):
    assert marker in js, 'Missing atlas navigation function: '+marker
assert "fictional" not in map_page.lower()
assert "not verified travel itineraries" in map_page
assert "not political boundaries" in map_page
assert "const url=mapUrlFor(loc.id).href;" in js
assert "document.querySelectorAll('.atlas-pin').forEach" in js
assert 'id="atlas-edit-toggle"' in map_page
print('Atlas regional navigation smoke tests passed.')
