"""Check indexability, sitemap output, navigation, media references and HTML integrity."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
BASE='https://yoshi3309.github.io/avalor-wiki/'
report=json.loads((SITE/'quality-report.json').read_text(encoding='utf-8'))
assert report['pages_checked']>=140, report
assert report['local_references_checked']>1000, report
assert report['missing_image_alt']==0, report
assert report['duplicate_ids']==0, report
assert report['issue_count']==0, '\n'.join(report['issues'][:100])

root=ET.parse(SITE/'sitemap.xml').getroot()
ns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls=[el.text for el in root.findall('./sm:url/sm:loc',ns)]
assert len(urls)>130, len(urls)
assert len(urls)==len(set(urls)), 'Sitemap includes duplicate canonical URLs'
assert all(url.startswith(BASE) for url in urls)
assert all(url.endswith('/') for url in urls)
assert BASE in urls
assert BASE+'map/' in urls
assert BASE+'chronicle/' in urls
assert BASE+'start/' in urls
assert BASE+'compare/' in urls
assert BASE+'gallery/' in urls
assert BASE+'exhibits/' in urls
assert BASE+'articles/lavitz-shawe/' in urls
assert all('/assets/' not in url for url in urls), 'Sitemap contains resources'
assert all('/index.html' not in url for url in urls)
assert all('/articles/rynhold-park/' not in url for url in urls), 'Retired redirect indexed'

robots=(SITE/'robots.txt').read_text(encoding='utf-8')
assert 'Sitemap: '+BASE+'sitemap.xml' in robots
assert 'User-agent: *' in robots
home=(SITE/'index.html').read_text(encoding='utf-8')
assert 'id="main-content" class="site-main" tabindex="-1"' in home
assert 'href="#main-content"' in home
assert 'assets/maintenance.css' in home

print('Site quality passed:',len(urls),'canonical sitemap pages;',
      report['pages_checked'],'HTML pages;',
      report['local_references_checked'],'checked local references; zero broken links or missing alt.')
