"""Validate the optional, public-canon Archivist's Welcome and entry paths."""
from pathlib import Path
import json
import yaml
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
routes=yaml.safe_load((ROOT/'data/welcome-routes.yml').read_text(encoding='utf-8'))['routes']
assert [r['id'] for r in routes]==['kingdom','heroes','history','world']
page=(SITE/'start/index.html').read_text(encoding='utf-8')
home=(SITE/'index.html').read_text(encoding='utf-8')
legacy_archive=(SITE/'archive/index.html').read_text(encoding='utf-8')
assert 'assets/welcome.js' in page and 'assets/welcome.css' in page
assert 'class="welcome-hero-art"' in page
# The banner is editor-controlled: a real upload replaces the optional fallback.
hero = yaml.safe_load((ROOT/'data/welcome-hero.yml').read_text(encoding='utf-8')) or {}
expected_image = str(hero.get('image') or '/assets/hero-scene.svg').lstrip('/')
expected_focus = str(hero.get('focus') or 'right center')
# The CMS refers to the original, while GitHub Pages serves a high-quality
# WebP derivative without duplicating the heavy image in the public site.
if expected_image.startswith('assets/uploads/') and expected_image != 'assets/uploads/avalor-official-map.webp':
    media=json.loads((SITE/'media-report.json').read_text(encoding='utf-8'))['items'][expected_image]
    expected_published_image=max(media['variants'], key=lambda v:v['width'])['path']
else:
    expected_published_image=expected_image
assert f'src="../{expected_published_image}"' in page, 'Configured Welcome hero image missing from published HTML'
assert f'object-position:{expected_focus}' in page, 'Welcome hero crop setting not reflected'
assert (SITE/expected_published_image).is_file(), 'Welcome hero image missing from built site'
assert 'ARCHIVIST' in page
assert 'What brings you to Avalor, traveler?' in page
assert 'href="./start/"' in home and 'New to Avalor? Start Here' in home
assert 'assets/archive-home.css' in home
assert 'id="archive-collections"' in home and 'id="archive-chronicle"' in home
assert 'href="../"' in page
assert 'name="robots" content="noindex"' in legacy_archive
assert 'location.hash' in legacy_archive
assert 'Keeper material' not in page
assert 'The Royal Commission welcomes all' in page
assert 'data-welcome-panel' in page and 'data-welcome-choice' in page
# Symbols are vector artwork: iOS must not convert swords or diagonal arrows into emoji.
assert page.count('class="welcome-swords-icon"') == 3, "Crossed swords must be vector in the doorway, card label and reading panel"
assert page.count('class="welcome-link-arrow"') == 25, "All Start Here diagonal arrows must be vector"
assert "⚔" not in page and "↗" not in page, "Emoji-prone font glyph leaked into Start Here HTML"
assert "stroke=\"currentColor\"" in page, "Vectors must inherit Night/Vellum ink color"
assert 'assets/icons/crossed-swords.svg' not in page, "Swords must not depend on an unbundled icon"
assert 'aria-controls="welcome-' in page
assert 'data-welcome-panel="kingdom"' in page and 'data-welcome-panel="world"' in page
# Inline SVG icons prevent iOS from substituting colorful emoji for swords/arrows.
assert page.count('class="welcome-swords-icon"') == 3, 'Heroes doorway/panel must use consistent vector swords'
assert page.count('class="welcome-link-arrow"') == 25, 'All four doorways, twelve reading links, four onward paths, and five footer links need vector arrows'
assert '↗' not in page, 'Unicode northeast arrow can render as emoji on iOS'
assert '<svg class="welcome-swords-icon"' in page and 'stroke="currentColor"' in page

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
