"""Build checks for accessible reading preferences and keyboard-safe navigation."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
home=(SITE/'index.html').read_text(encoding='utf-8')
article=(SITE/'articles'/'lavitz-shawe'/'index.html').read_text(encoding='utf-8')
exhibit=(SITE/'exhibits'/'founding-settlement'/'index.html').read_text(encoding='utf-8')
reading_desk=(SITE/'reading-desk'/'index.html').read_text(encoding='utf-8')
js=(SITE/'assets'/'reading-comfort.js').read_text(encoding='utf-8')
css=(SITE/'assets'/'reading-comfort.css').read_text(encoding='utf-8')
app=(SITE/'assets'/'app.js').read_text(encoding='utf-8')
article_js=(SITE/'assets'/'article-reading.js').read_text(encoding='utf-8')
map_js=(SITE/'assets'/'map.js').read_text(encoding='utf-8')
for page in (home,article,exhibit,reading_desk):
    for token in ('assets/reading-comfort.css','assets/reading-comfort.js',
                  'id="reading-prefs-trigger"','id="reading-prefs-panel"',
                  'id="reading-prefs-contrast"','id="reading-prefs-motion"',
                  'id="reading-prefs-reset"','aria-controls="reading-prefs-panel"'):
        assert token in page, 'Missing reading preference control/asset: '+token
for size in ('comfortable','large','extra-large'):
    assert f'data-reader-size="{size}"' in home
for font in ('literary','clear'):
    assert f'data-reader-font="{font}"' in home
for attr in ('aria-expanded="false"','aria-pressed="false"','role="status"'):
    assert attr in home
assert 'aria-controls="sidebar"' in home and 'aria-expanded="false" id="menu-trigger"' in home
for token in ('avalor-reading-comfort-v1','localStorage.setItem','localStorage.getItem',
              "dataset.readingContrast","dataset.readingMotion","addEventListener('storage'",
              'panel.hidden=true','panel.hidden=false',"e.key==='Escape'"):
    assert token in js, 'Reading preference JS missing '+token
for token in ('--reader-text-size:15px','--reader-text-size:17px','--reader-text-size:19px',
              'html[data-reading-contrast="high"]','html[data-reading-motion="reduce"]',
              '@media(prefers-reduced-motion:reduce)','@media(max-width:710px)',
              '.article-body table{display:block','focus-visible','[hidden]{display:none'):
    assert token in css, 'Reading CSS missing '+token
assert 'sidebar.inert = !open' in app, 'Closed mobile sidebar remains tabbable'
assert "menuTrigger?.setAttribute('aria-expanded',String(open))" in app
assert 'sidebar.querySelectorAll' in app and 'e.shiftKey' in app
assert "heading.focus({preventScroll:true})" in article_js, 'Chapter jump does not move keyboard focus'
assert "document.documentElement.dataset.readingMotion==='reduce'" in map_js
print('Reading Comfort and Accessibility smoke tests passed.')
