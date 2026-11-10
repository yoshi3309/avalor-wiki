"""Validate social previews for all public wiki pages and representative Discord embeds."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
BASE='https://yoshi3309.github.io/avalor-wiki/'

class Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta={}
        self.links={}
    def handle_starttag(self, tag, attrs):
        data=dict(attrs)
        if tag=='meta':
            key=data.get('property') or data.get('name')
            if key:self.meta[key]=data.get('content','')
        if tag=='link' and data.get('rel')=='canonical':
            self.links['canonical']=data.get('href','')

public_pages=[p for p in SITE.rglob('index.html') if 'assets' not in p.relative_to(SITE).parts]
assert len(public_pages)>=100, f'Expected published records and collection pages, found {len(public_pages)}'
seen=set()
for page in public_pages:
    html=page.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in html:
        continue
    parser=Head();parser.feed(html)
    tags=parser.meta
    for name in ('description','og:title','og:description','og:url','og:site_name','og:type',
                 'og:image','og:image:secure_url','og:image:width','og:image:height',
                 'og:image:type','og:image:alt','twitter:card','twitter:title',
                 'twitter:description','twitter:image'):
        assert tags.get(name), f'{page}: missing {name}'
    assert tags['og:site_name']=='The Archives of Avalor'
    assert tags['twitter:card']=='summary_large_image'
    assert tags['og:image:width']=='1200' and tags['og:image:height']=='630'
    assert tags['og:image:type']=='image/jpeg'
    assert tags['og:image']==tags['og:image:secure_url']==tags['twitter:image']
    assert parser.links['canonical']==tags['og:url']
    rel=page.relative_to(SITE)
    expected_url=BASE+str(rel.parent).replace('.','').strip('/') + ('/' if rel.parent!=Path('.') else '')
    assert tags['og:url']==expected_url,(page,tags['og:url'],expected_url)
    url=urlparse(tags['og:image'])
    assert url.scheme=='https' and url.netloc=='yoshi3309.github.io'
    assert url.path.startswith('/avalor-wiki/assets/social/'),tags['og:image']
    image=SITE/unquote(url.path[len('/avalor-wiki/'):])
    assert image.exists(), f'{page}: preview file not found {image}'
    if image not in seen:
        with Image.open(image) as preview:
            assert preview.format=='JPEG'
            assert preview.size==(1200,630)
        assert image.stat().st_size<1_500_000,(image,image.stat().st_size)
        seen.add(image)
assert len(seen)>=100, f'Not enough unique social previews: {len(seen)}'
for relative, title in [
    ('articles/lavitz-shawe/index.html','Lavitz'),
    ('articles/the-six/index.html','The Six'),
    ('articles/renada/index.html','Renada'),
    ('gallery/index.html','Illustration Gallery'),
    ('map/index.html',"Cartographer"),
    ('exhibits/founding-settlement/index.html','Settlement')]:
    doc=Head();doc.feed((SITE/relative).read_text(encoding='utf-8'))
    assert title.casefold() in doc.meta['og:title'].casefold(),relative
    assert 'sandbox:' not in doc.meta['og:image']
print('Discord social previews verified:',len(seen),'1200x630 cards and canonical Open Graph metadata.')
