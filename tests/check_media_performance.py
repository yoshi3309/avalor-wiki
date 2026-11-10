"""Build-time checks for responsive, original-preserving public artwork."""
from __future__ import annotations
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
REPORT=SITE/'media-report.json'
assert REPORT.is_file(),'Missing media optimization build report'
report=json.loads(REPORT.read_text(encoding='utf-8'))
items=report['items']
assert report['image_count']>=35, 'Approved public uploads unexpectedly omitted'
assert report['source_total_bytes']>50_000_000, 'Media source inventory unexpectedly small'
assert report['preview_total_bytes']<report['source_total_bytes'], 'Generated previews are larger than original image sources'
for original, meta in items.items():
    assert original.startswith('assets/uploads/'), original
    src=ROOT/original
    assert src.exists(), 'Missing source '+original
    assert (SITE/original).exists(), 'Original absent from public site: '+original
    assert meta['width']>0 and meta['height']>0
    assert meta['variants'], 'No responsive preview generated for '+original
    seen=set()
    for v in meta['variants']:
        assert v['path'].startswith('assets/optimized/uploads/')
        assert (SITE/v['path']).is_file(),'Missing responsive variant: '+v['path']
        assert 0<v['width']<=meta['width']
        assert v['width'] not in seen and v['height']>0
        assert abs((v['width']/v['height'])-(meta['width']/meta['height']))<0.02
        assert v['bytes']>0
        seen.add(v['width'])

class Pictures(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources=[]
        self.images=[]
        self.links=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='source' and attrs.get('type')=='image/webp': self.sources.append(attrs)
        if tag=='img': self.images.append(attrs)
        if tag=='a': self.links.append(attrs)

def inspect(relative):
    page=SITE/relative
    assert page.is_file(),relative
    parsed=Pictures()
    parsed.feed(page.read_text(encoding='utf-8'))
    return parsed

gallery=inspect('gallery/index.html')
assert len(gallery.sources)>=10, 'Gallery previews not responsive'
assert any('/optimized/uploads/' in a.get('srcset','') for a in gallery.sources)
assert any('loading' in im and im['loading']=='lazy' and im.get('alt') for im in gallery.images), 'Gallery thumbnails need alt and lazy loading'
assert any(a.get('id')=='gallery-original-link' for a in gallery.links), 'Gallery missing original art link'
assert (SITE/'assets/gallery.js').is_file()
assert 'entry.media' in (SITE/'assets/gallery.js').read_text(encoding='utf-8')

article=inspect('articles/lavitz-shawe/index.html')
assert any('/optimized/uploads/' in a.get('srcset','') for a in article.sources), 'Article did not use optimized WebP'
assert any(im.get('src','').endswith('lavitz-shawe.jpg') for im in article.images), 'Original Lavitz portrait changed'
assert any(im.get('alt') for im in article.images if 'assets/uploads/' in im.get('src',''))

map_meta=items['assets/uploads/avalor-official-map.webp']
assert map_meta['modal_original'], 'High-detail map must preserve original lightbox'
print('Responsive media passed:',report['image_count'],'uploads; potential preview byte savings', report['potential_preview_savings_pct'],'percent.')
