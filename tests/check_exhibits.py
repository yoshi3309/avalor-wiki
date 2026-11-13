"""Validate public historical exhibits and documentary integrity."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'_site'
items=[yaml.safe_load(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'content'/'exhibits').glob('*.yml'))]
published=[e for e in items if e.get('published')]
assert len(published)==5, f'Expected five initial exhibits, got {len(published)}'
assert len({e['id'] for e in published})==5
index=(SITE/'exhibits/index.html').read_text(encoding='utf-8')
for token in ('id="exhibits-search"','id="exhibits-period"','id="exhibits-catalogue"','assets/exhibits.js','editorial reconstructions'):
    assert token in index,token
for record in published:
    page=(SITE/'exhibits'/record['id']/'index.html').read_text(encoding='utf-8')
    for token in ('NOT AN ORIGINAL DOCUMENT','reconstructed account','What the record establishes','What remains unverified','Curatorial interpretation','id="transcription"'):
        assert token in page, f'{record["id"]}: missing {token}'
    assert record['folio_title'] in page
    assert (SITE/'articles'/record['source_article']/'index.html').exists()
    for slug in str(record.get('related_articles','')).split(','):
        if slug.strip(): assert (SITE/'articles'/slug.strip()/'index.html').exists(),slug
    article=(SITE/'articles'/record['source_article']/'index.html').read_text(encoding='utf-8')
    assert 'exhibits/'+record['id']+'/' in article
    assert 'article-explore-exhibits' in article
assert 'exhibits/' in (SITE/'index.html').read_text(encoding='utf-8')
print('Documentary Cabinet passed: five reconstructed folios, source links, labels and article navigation.')
