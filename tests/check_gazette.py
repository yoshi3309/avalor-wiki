"""Check Royal Gazette publication pages and every source-backed dispatch."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
issues=[yaml.safe_load(path.read_text(encoding='utf-8')) for path in (ROOT/'content/gazette').glob('*.yml')]
published=[issue for issue in issues if issue.get('published') is True]
assert published
home=(SITE/'gazette/index.html').read_text(encoding='utf-8')
assert 'The Royal' in home and 'Gazette' in home and 'assets/gazette.css' in home
assert 'href="../gazette/"' in (SITE/'archive/index.html').read_text(encoding='utf-8')
for issue in published:
    page=SITE/'gazette'/issue['id']/'index.html'
    assert page.exists(),page
    html=page.read_text(encoding='utf-8')
    assert 'EDITORIAL PUBLICATION' in html
    assert len(issue['dispatches'])>=2
    for i,item in enumerate(issue['dispatches'],1):
        assert f'id="dispatch-{i}"' in html
        assert f'href="../../articles/{item["article"]}/"' in html
        assert (ROOT/'content/articles'/f'{item["article"]}.md').exists()
    assert f'href="../{issue["id"]}/"' in home
assert 'href="./gazette/"' in (SITE/'index.html').read_text(encoding='utf-8')
print('Royal Gazette pages passed:',len(published),'edition(s).')
