"""Validate the optional, public-canon Archivist's Welcome and entry paths."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
routes=yaml.safe_load((ROOT/'data/welcome-routes.yml').read_text(encoding='utf-8'))['routes']
assert [r['id'] for r in routes]==['kingdom','heroes','history','world']
page=(SITE/'start/index.html').read_text(encoding='utf-8')
home=(SITE/'index.html').read_text(encoding='utf-8')
assert 'assets/welcome.js' in page and 'assets/welcome.css' in page
assert 'ARCHIVIST' in page
assert 'What brings you to Avalor, traveler?' in page
assert 'href="./start/"' in home
assert 'New here? Begin your visit' in home and 'Meet the Archivist' in home
assert 'href="../start/"' in page
assert 'Keeper material' in page
assert 'data-welcome-panel' in page and 'data-welcome-choice' in page
assert 'aria-controls="welcome-' in page
assert 'data-welcome-panel="kingdom"' in page and 'data-welcome-panel="world"' in page
journeys=yaml.safe_load((ROOT/'data/reading-journeys.yml').read_text(encoding='utf-8'))
ids={r['id'] for r in journeys['journeys']}
seen=set()
for route in routes:
    name=route['id']
    assert name not in seen
    seen.add(name)
    for token in ('title','kicker','tagline','intro','welcome','destination_label'):
        assert route[token] and str(route[token]).strip()
    assert 'href="#welcome-'+name+'"' in page, name
    assert 'id="welcome-'+name+'"' in page, name
    assert 'data-welcome-choice="'+name+'"' in page
    assert page.count('data-welcome-panel="'+name+'"')==1
    steps=route['articles']
    assert len(steps)==3
    slugs=[step['article'] for step in steps]
    assert len(set(slugs))==3
    for step in steps:
        slug=step['article']
        assert step['invitation']
        assert (ROOT/'content/articles'/f'{slug}.md').is_file(), (name,slug)
        assert f'href="../articles/{slug}/"' in page, slug
    dest=route['destination']
    if dest=='atlas':
        assert 'href="../map/"' in page
    else:
        assert dest in ids,(name,dest)
        assert f'href="../journeys/{dest}/"' in page
assert (SITE/'assets/welcome.js').is_file()
assert (SITE/'assets/welcome.css').is_file()
script=(SITE/'assets/welcome.js').read_text(encoding='utf-8')
for token in ("window.addEventListener('popstate'","window.addEventListener('hashchange'","panel.hidden=",
              "target.focus({preventScroll:true})","prefers-reduced-motion","dataset.readingMotion"):
    assert token in script, 'Welcome keyboard/history navigation missing '+token
assert '<meta property="og:image"' in page
assert '<link rel="canonical" href="https://yoshi3309.github.io/avalor-wiki/start/">' in page
print('Archivist Welcome passed: four curated public paths and homepage navigation.')
