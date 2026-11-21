"""Public Flight Library contract checks; no Keeper data or off-origin caches."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
assert (SITE / 'sw.js').is_file(), 'Missing generated service worker'
manifest = json.loads((SITE / 'offline-manifest.json').read_text(encoding='utf-8'))
assert manifest['schema'] == 1
packs = manifest['packs']
assert len(packs) >= 2
assert packs[0]['id'] == 'public-encyclopedia'
assert any(p['type'] == 'journey' for p in packs)
assert len({p['id'] for p in packs}) == len(packs)
assert len({p['revision'] for p in packs}) > 0
for pack in packs:
    assert re.fullmatch(r'[a-z0-9-]+', pack['id'])
    assert re.fullmatch(r'[0-9a-f]{16}', pack['revision'])
    assert pack['start'] in pack['paths']
    assert len(pack['paths']) == len(set(pack['paths']))
    assert pack['bytes'] > 0
    for path in pack['paths']:
        assert '..' not in path and not path.startswith('/') and '://' not in path
        file = SITE / path if path.endswith('.json') else SITE / path / 'index.html'
        assert file.is_file(), f'Missing pack page: {path}'
assert 'search-index.json' in packs[0]['paths']
assert all('search-index.json' not in p['paths'] for p in packs[1:])
assert (SITE / 'flight-library/index.html').is_file()
assert (SITE / 'offline/unavailable/index.html').is_file()
worker = (SITE / 'sw.js').read_text(encoding='utf-8')
assert '__AVALOR_' not in worker
assert 'self.registration.scope' in worker
assert 'cache.addAll' in worker
assert 'READY_URL' in worker
assert 'skipWaiting' in worker
assert 'cache.match(READY_URL)' in worker
page = (SITE / 'flight-library/index.html').read_text(encoding='utf-8')
assert 'data-flight-library' in page
assert 'offline.js' in page
assert 'offline-register.js' in page
assert 'Flight Library' in (SITE / 'index.html').read_text(encoding='utf-8')
print(f'Flight Library: {len(packs)} public reading packs, complete paths and scoped worker verified')
