"""Blackwater Bay Stage 2 faction, community, and supporting-cast integrity."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
def article(slug):
    return (ROOT / 'content' / 'articles' / (slug + '.md')).read_text(encoding='utf-8')

diamond = article('black-diamond')
esogoth = article('esogoth')
communities = article('clans-and-communities-of-avalor')
minor = article('minor-characters')
enemies = article('minor-villains-and-adversaries')
places = article('other-locations-of-avalor')
liberation = article('rotten-husk-liberation')
harbor = article('blackwater-bay')
assert '2020 AF' in diamond and 'Esogoth' in diamond
assert 'The Black Diamond' in esogoth and 'Pier Seven' in esogoth
assert 'not confirmed destroyed' in diamond
assert '## The Tide-Touched Kobolds' in communities
assert '## The Rotten Husk Clan' in communities
assert '\n### The Tidecaller and Grik' in communities  # nested under the Tide-Touched section
assert 'Tidecaller' in communities and 'Grik' in communities
assert '2000 AF' in communities and '2020 AF' in communities
assert '[[Freedom for the Rotten Husk]]' in communities
assert '## Gladios and Shadowthorn' in enemies
assert '## Mother Vey' in enemies and 'fate' in enemies.lower()
assert 'withdrew alive on Shadowthorn' in enemies
assert '## Stavros, the Pale Man' in minor
assert '## Seb Bramble' in minor
assert 'Katiri' in minor and 'custody' in minor.lower()
assert '## The Tide Gate' in places
assert 'onset of Blood Touch' in places
assert 'not evidence of actual travel to another time' in places.split('## The Tide Gate')[-1]
assert '[[The Rotten Husk Clan|Rotten Husk]]' in liberation  # legacy title resolves via redirect
assert 'Black Diamond' in harbor and 'Esogoth' in harbor
assert not (ROOT / 'content/articles/rotten-husk-clan.md').exists()
retired = yaml.safe_load((ROOT / 'data/article-merges.yml').read_text(encoding='utf-8'))['retired']
assert retired['rotten-husk-clan'] == {
    'title': 'The Rotten Husk Clan',
    'parent': 'clans-and-communities-of-avalor',
    'section': 'the-rotten-husk-clan'
}
nav = yaml.safe_load((ROOT / 'data/collection-navigation.yml').read_text(encoding='utf-8'))
groups = nav['organizations-factions']['groups']
found = {slug for g in groups for slug in (g.get('articles') or [])}
assert {'black-diamond','clans-and-communities-of-avalor'} <= found
assert 'rotten-husk-clan' not in found
assert (ROOT / 'content/articles/ringtree-clan.md').exists()
for source in (diamond, esogoth, communities, minor, enemies, places):
    assert 'Sea Serpents' not in source
    assert 'Strain 4' not in source
    assert 'Pier Twelve' not in source
print('Blackwater Bay Stage 2: faction, community preservation, minor cast and Gate continuity verified.')
