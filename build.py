"""Build a public-only, zero-cost static wiki for GitHub Pages.

IMPORTANT: only content/articles/*.md is read. Keeper notes/PDFs are deliberately
not part of this repository or deployment pipeline.
"""
from __future__ import annotations
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path
from functools import lru_cache
import yaml
import mistune
from public_references import public_sources
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / '_site'
CONTENT = ROOT / 'content' / 'articles'
CATEGORIES = [
    {'name':'Kingdoms & Places','slug':'kingdoms-places','icon':'♜','description':'Kingdoms, cities, ancient roads, and the places between.'},
    {'name':'People & Legends','slug':'people-legends','icon':'♕','description':'Heroes, rulers, and the names remembered across the ages.'},
    {'name':'Organizations & Factions','slug':'organizations-factions','icon':'⚜','description':'Orders, councils, royal houses, and their obligations.'},
    {'name':'History & Chronicles','slug':'history-chronicles','icon':'◷','description':'Wars, discoveries, and the turning of the ages.'},
    {'name':'Faith, Magic & Cosmology','slug':'faith-magic-cosmology','icon':'✧','description':'Divinity, traditions, and the questions beyond the known.'},
]
EVENTS = [
    {'date':"Before 1 AF",'era':"THE FOUNDING WARS",'title':"The northern crowns unite against Osmo",'text':"Rynhold of Kroubia helps assemble an alliance against the mortal conqueror. Bradgem Glav dies defeating Osmo at Heroes Hill; the exact battle year is not established.",'article':"founding-wars"},
    {'date':"1 AF",'era':"THE FOUNDING",'title':"The kingdom is established",'text':"After the struggle against Lord Osmo and the victory at Heroes Hill, Rynhold unites allied northern realms by political agreement. The battle's precise year is not separately settled.",'article':"unification-of-avalor"},
    {'date':"c. 10 AF",'era':"THE FOUNDING",'title':"The Black Tower catastrophe",'text':"Aldus's experiments bring calamity in the early kingdom. The date is approximate, not an independently confirmed anniversary.",'article':"sundering-of-the-six"},
    {'date':"38–106 AF",'era':"THE EARLY CROWN",'title':"The first successors",'text':"Benedikt preserves the union; Queen Aldara later directs the Royal Survey of the Crossings. Their reigns are 38–71 and 72–106 AF respectively.",'article':"house-frozenroar"},
    {'date':"107–155 AF",'era':"THE ELVEN CONCORD",'title':"Rights of the old forest",'text':"Under Dietmar, conflict with elven communities leads to the Elven Concord, preserving ancestral rights alongside recognition of the crown.",'article':"forest-of-the-fey"},
    {'date':"156–178 AF",'era':"THE ELVEN CONCORD",'title':"Halton and Dathyra",'text':"Halton's marriage to Dathyra Blueshadow strengthens the Concord; they become the parents of Sylavor.",'article':"house-frozenroar"},
    {'date':"298 AF",'era':"ROYAL SUCCESSION",'title':"Sylavor abdicates",'text':"Sylavor steps down voluntarily. Arelis assumes independent sovereign authority despite the former monarch remaining alive.",'article':"house-frozenroar"},
    {'date':"857 AF",'era':"THE DIVIDED KINGDOM",'title':"Elyra takes the crown",'text':"The firstborn of the twins Elyra and Corven becomes queen under the established rules of succession.",'article':"house-frozenroar"},
    {'date':"890–893 AF",'era':"THE DIVIDED KINGDOM",'title':"War of the Two Lions",'text':"Corven challenges his elder twin sister Elyra's lawful rule. Elyra dies of illness in 893 AF; the war ends amid a transition.",'article':"house-frozenroar"},
    {'date':"894 AF",'era':"RECONCILIATION",'title':"Torenna's accession",'text':"Elyra's daughter Torenna begins her formal reign and establishes the Concord of the Two Lions. This is not the older Elven Concord.",'article':"house-frozenroar"},
    {'date':"1259–1315 AF",'era':"THE EDICTS",'title':"Arnaud's persecution",'text':"Royal decrees discriminate against drow communities. Jeyse and Cal’el resist the seizure of families sheltered at Heaven's Heart.",'article':"arnauds-edicts"},
    {'date':"1316–1402 AF",'era':"REFORM",'title':"Reina's reversal",'text':"Queen Reina curtails the restrictions and seeks to restore equal treatment, though prejudice and its consequences endure.",'article':"reinas-reforms"},
    {'date':"1462–1511 AF",'era':"WAR ACROSS THE SEA",'title':"The cost of Wolfram's reign",'text':"A prolonged overseas war during Wolfram's reign strains the kingdom. The date range identifies his reign, not necessarily every military campaign.",'article':"house-frozenroar"},
    {'date':"1511 AF",'era':"THE SECOND ABDICATION",'title':"Wolfram relinquishes the crown",'text':"Wolfram voluntarily abdicates through a negotiated settlement to prevent further political division.",'article':"house-frozenroar"},
    {'date':"1512 AF",'era':"RESTORATION",'title':"Ysoria accedes",'text':"Queen Ysoria assumes the crown and works to restore trust and oversee the kingdom's foreign commitments.",'article':"house-frozenroar"},
    {'date':"1983 AF",'era':"THE PRESENT REIGN",'title':"Gradvum takes the throne",'text':"Gradvum begins his reign; Queen Melmiri later oversees much of the kingdom's daily administration.",'article':"king-gradvum-frozenroar"},
    {'date':"Around 2000 AF",'era':"THE BLOOD KING’S DEFEAT",'title':"The Misfits uncover the truth",'text':"The Misfits defeat Cid in the Shadowfell. Jaznaar's innocence is publicly proclaimed. The year is approximate.",'article':"jaznaars-vindication"},
    {'date':"About twenty years later",'era':"THE AGE OF ASCENDANCY",'title':"A kingdom with a wider horizon",'text':"Avalor gains international prominence; Lavitz is Lord Marshal and Tel’Lora is High Wizard. The date remains approximate.",'article':"age-of-ascendancy"},
]

def slugify(value):
    value=unicodedata.normalize('NFKD',value.lower())
    value=''.join(ch for ch in value if not unicodedata.combining(ch))
    value=re.sub(r"[^a-z0-9]+",'-',value).strip('-')
    return value

def read_source(path):
    content = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\s*\n(.*?)\n---\s*\n(.*)\Z',content,re.S)
    if not match: raise ValueError(f'{path}: missing YAML frontmatter')
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata,dict): raise ValueError(f'{path}: invalid YAML')
    for key in ('title','summary','category'):
        if not metadata.get(key):raise ValueError(f'{path}: missing {key}')
    if metadata['category'] not in [c['name'] for c in CATEGORIES]:raise ValueError(f'{path}: unknown category')
    metadata.update({'slug':path.stem,'body':match.group(2).strip()})
    metadata['public_source'] = public_sources(metadata.get('source'))
    facts = str(metadata.get('facts') or '').splitlines()
    metadata['facts_parsed'] = [{'label':l.strip(),'value':v.strip()} for fact in facts if ':' in fact for l,v in [fact.split(':',1)]]
    metadata['related_slugs'] = [s.strip() for s in str(metadata.get('related') or '').split(',') if s.strip()]
    return metadata

ALL = sorted([read_source(p) for p in CONTENT.glob('*.md')],key=lambda a:a['title'].lower())
BY_SLUG={a['slug']:a for a in ALL}
if not ALL:raise RuntimeError('No public articles found')
ALIAS={}
for a in ALL:
    ALIAS[slugify(a['title'])] = a['slug']
    ALIAS[slugify(a['slug'])] = a['slug']
ALIAS.update({'avalor':'kingdom-of-avalor','misfits':'the-misfits','tel-lora':'tellora-ebbenflow',"heavens-heart":'heavens-heart','royal-commission-of-historical-inquiry':'royal-commission-historical-inquiry'})

@lru_cache

def markdown_renderer():
    return mistune.create_markdown(escape=True,plugins=['table','strikethrough'])

def wikilink_sub(match, relative_root):
    target=match.group(1)
    if '|' in target: target, label = target.split('|',1)
    else: label=target
    slug=ALIAS.get(slugify(target))
    if slug:return f'[{label}]({relative_root}articles/{slug}/)'
    return label

def render_fact_value(value):
    """Safely link fact values that name an article; allow explicit [[Article|label]].
    Facts are public editorial metadata, not Markdown or trusted HTML.
    """
    raw = str(value).strip()
    if '[[' not in raw:
        slug = ALIAS.get(slugify(raw))
        if slug in BY_SLUG:
            return f'<a href="../../articles/{slug}/">{html.escape(raw)}</a>'
        return html.escape(raw)
    parts = []
    position = 0
    for match in re.finditer(r'\[\[([^\]]+)\]\]', raw):
        parts.append(html.escape(raw[position:match.start()]))
        target, separator, label = match.group(1).partition('|')
        if not separator:
            label = target
        slug = ALIAS.get(slugify(target))
        if slug in BY_SLUG:
            parts.append(f'<a href="../../articles/{slug}/">{html.escape(label)}</a>')
        else:
            parts.append(html.escape(label))
        position = match.end()
    parts.append(html.escape(raw[position:]))
    return ''.join(parts)

def make_html(article):
    rel='../../'
    md = re.sub(r'\[\[([^\]]+)\]\]',lambda m:wikilink_sub(m,rel),article['body'])
    md = re.sub(r'\]\(/assets/uploads/', f']({rel}assets/uploads/',md)
    rendered=markdown_renderer()(md)
    headings=[]
    used=set()
    def heading_id(m):
        raw=re.sub('<[^>]*>','',m.group(1)); raw=html.unescape(raw)
        tag=slugify(raw) or 'heading'; anchor=tag; n=2
        while anchor in used: anchor=f'{tag}-{n}';n+=1
        used.add(anchor);headings.append({'id':anchor,'text':raw})
        return f'<h2 id="{anchor}">{m.group(1)}</h2>'
    rendered=re.sub(r'<h2>(.*?)</h2>',heading_id,rendered,flags=re.S)
    # Convert Pages CMS media paths into relative paths that work on
    # project GitHub Pages sites such as /avalor-wiki/.
    image_raw=str(article.get('image') or '').strip()
    if image_raw.startswith('/assets/uploads/'):
        article['image_url']=rel+image_raw.lstrip('/')
    elif image_raw.startswith('assets/uploads/'):
        article['image_url']=rel+image_raw
    else:
        article['image_url']=None
    for fact in article['facts_parsed']:
        fact['value_html'] = render_fact_value(fact['value'])
    article['html']=rendered; article['headings']=headings
    return article
ALL=[make_html(a) for a in ALL]
BY_SLUG={a['slug']:a for a in ALL}
for cat in CATEGORIES:cat['count']=len([a for a in ALL if a['category']==cat['name']])
FEATURED=[a for a in ALL if a.get('featured')]
FEATURED.sort(key=lambda a:['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'].index(a['slug']) if a['slug'] in ['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'] else 50)

# The cartographer's table is public-facing. This file contains no hidden
# locations; the original Keeper documents are never read by this build.
MAP_CONFIG = ROOT / 'data' / 'avalor-map.yml'
MAP = yaml.safe_load(MAP_CONFIG.read_text(encoding='utf-8')) or {}
if not isinstance(MAP, dict): raise ValueError('Map configuration must be a YAML mapping')
MAP_ALLOWED_TYPES = {'settlement','region','water','historic','institution'}
MAP_LOCATIONS = []
MAP_IDS = set()
for raw in MAP.get('locations', []):
    if not isinstance(raw, dict): raise ValueError('Each map location must be an object')
    ident = str(raw.get('id','')).strip()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', ident) or ident in MAP_IDS:
        raise ValueError(f'Invalid or duplicate map location id: {ident}')
    MAP_IDS.add(ident)
    kind = str(raw.get('type') or 'region')
    if kind not in MAP_ALLOWED_TYPES: raise ValueError(f'{ident}: unknown marker type')
    # Blank coordinates are permitted for draft landmarks. This avoids
    # inventing canonical positions just to make markers editable.
    def coordinate(value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return float(value)
    x, y = coordinate(raw.get('x')), coordinate(raw.get('y'))
    if (x is None) != (y is None):
        raise ValueError(f'{ident}: enter both X and Y, or leave both empty')
    placed = x is not None and y is not None
    if placed and not (0 <= x <= 100 and 0 <= y <= 100):
        raise ValueError(f'{ident}: coordinates out of bounds')
    article_slug = str(raw.get('article') or '').strip()
    if article_slug and article_slug not in BY_SLUG:
        raise ValueError(f'{ident}: article filename {article_slug} does not exist')
    subplace_slugs = [s.strip() for s in str(raw.get('related_places') or '').split(',') if s.strip()]
    for subslug in subplace_slugs:
        if subslug not in BY_SLUG:
            raise ValueError(f'{ident}: nested article {subslug} does not exist')
    subplaces = [{'slug': s, 'name': BY_SLUG[s]['title']} for s in subplace_slugs]
    MAP_LOCATIONS.append({
        'id':ident, 'name':str(raw.get('name') or ident),
        'type':kind,'x':x,'y':y,'placed':placed,
        'description':str(raw.get('description') or ''),
        'article':article_slug,'subplaces':subplaces,
        'published':bool(raw.get('published',True)),
        'provisional':bool(raw.get('provisional',False)),
    })
raw_map_image = str(MAP.get('image') or '').strip().lstrip('/')
# No remote URLs, path traversal, or private source files allowed.
if raw_map_image and (not raw_map_image.startswith('assets/uploads/') or '..' in raw_map_image):
    raise ValueError('Map image must be a public file in assets/uploads/')
MAP_IMAGE = '../'+raw_map_image if raw_map_image else ''
MAP_DATA = {'image': MAP_IMAGE, 'root':'../','locations': MAP_LOCATIONS}
MAP_LINKS = {}
for loc in MAP_LOCATIONS:
    if loc['published'] and loc['placed']:
        if loc['article']:
            MAP_LINKS.setdefault(loc['article'],loc['id'])
        for subplace in loc['subplaces']:
            MAP_LINKS.setdefault(subplace['slug'],loc['id'])

# Collection navigation is a public editorial index, separate from character canon.
# A person may belong to more than one browsing group. Unlisted people receive a
# catch-all entry without requiring a code change when Pages CMS adds a biography.
PEOPLE_NAV_CONFIG = yaml.safe_load((ROOT / 'data' / 'people-navigation.yml').read_text(encoding='utf-8'))
PEOPLE_ITEMS = [a for a in ALL if a['category'] == 'People & Legends']
PEOPLE_BY_SLUG = {a['slug']: a for a in PEOPLE_ITEMS}
PEOPLE_GROUPS = []
PEOPLE_ASSIGNED = set()
PEOPLE_GROUP_IDS = set()
for raw_group in PEOPLE_NAV_CONFIG['groups']:
    group_id = str(raw_group['id'])
    if group_id in PEOPLE_GROUP_IDS or not re.fullmatch(r'[a-z0-9-]+', group_id):
        raise ValueError(f'Duplicate or invalid people navigation group: {group_id}')
    PEOPLE_GROUP_IDS.add(group_id)
    slugs = raw_group.get('articles', [])
    invalid = [slug for slug in slugs if slug not in PEOPLE_BY_SLUG]
    if invalid:
        raise ValueError(f'People group {group_id} names missing/non-person entries: {invalid}')
    PEOPLE_ASSIGNED.update(slugs)
    PEOPLE_GROUPS.append({
        'id': group_id, 'title': raw_group['title'],
        'eyebrow': raw_group['eyebrow'], 'icon': raw_group['icon'],
        'description': raw_group['description'], 'slugs': list(slugs)
    })
# Future people automatically appear in "Other Figures" and the full directory.
if 'other-figures' not in PEOPLE_GROUP_IDS:
    raise ValueError('People navigation requires an other-figures catch-all group')
for group in PEOPLE_GROUPS:
    if group['id'] == 'other-figures':
        group['slugs'] += sorted(set(PEOPLE_BY_SLUG) - PEOPLE_ASSIGNED)
    group['count'] = len(group['slugs'])
for a in PEOPLE_ITEMS:
    a['browse_groups'] = [group['id'] for group in PEOPLE_GROUPS if a['slug'] in group['slugs']]
PEOPLE_FEATURED = PEOPLE_BY_SLUG.get(str(PEOPLE_NAV_CONFIG.get('featured', ''))) or PEOPLE_ITEMS[0]

# Public-only collection navigation uses the same grouping principle as People & Legends.
# These groups organize the existing records; they do not invent new lore or alter articles.
COLLECTION_NAV = yaml.safe_load((ROOT / 'data' / 'collection-navigation.yml').read_text(encoding='utf-8'))
COLLECTION_PAGES = {}
for cat in CATEGORIES:
    if cat['name'] == 'People & Legends':
        continue
    config = COLLECTION_NAV.get(cat['slug'])
    if not isinstance(config, dict):
        raise ValueError(f"Missing browse configuration for collection {cat['slug']}")
    articles = [a for a in ALL if a['category'] == cat['name']]
    by_slug = {a['slug']: a for a in articles}
    featured_slug = str(config.get('featured') or '')
    if featured_slug not in by_slug:
        raise ValueError(f"Collection {cat['slug']} featured article is not in this collection: {featured_slug}")
    seen_ids = set()
    assigned = set()
    groups = []
    for raw in config.get('groups', []):
        group_id = str(raw['id'])
        if group_id in seen_ids or not re.fullmatch(r'[a-z0-9-]+', group_id):
            raise ValueError(f"Invalid or duplicate group '{group_id}' for {cat['slug']}")
        seen_ids.add(group_id)
        slugs = raw.get('articles', [])
        if len(slugs) != len(set(slugs)):
            raise ValueError(f"Duplicate article in {cat['slug']} group {group_id}")
        invalid = [slug for slug in slugs if slug not in by_slug]
        if invalid:
            raise ValueError(f"Nonexistent or cross-collection record(s) in {cat['slug']} group {group_id}: {invalid}")
        assigned.update(slugs)
        groups.append({
            'id': group_id, 'title': raw['title'], 'eyebrow': raw['eyebrow'],
            'description': raw['description'], 'icon': raw['icon'], 'slugs': list(slugs)
        })
    catchall = str(config.get('catchall') or '')
    if catchall:
        if catchall not in seen_ids:
            raise ValueError(f"Missing catch-all group '{catchall}' in {cat['slug']}")
        for group in groups:
            if group['id'] == catchall:
                group['slugs'] += sorted(set(by_slug) - assigned)
    # Don't display an empty Other Places / Other Chronicles card until it has records.
    groups = [group for group in groups if group['slugs']]
    for group in groups:
        group['count'] = len(group['slugs'])
    for article in articles:
        article['browse_groups'] = [group['id'] for group in groups if article['slug'] in group['slugs']]
    if groups and any(not a['browse_groups'] for a in articles):
        raise ValueError(f"Uncategorized article in collection {cat['slug']}")
    COLLECTION_PAGES[cat['slug']] = {'config': config, 'groups': groups, 'featured': by_slug[featured_slug]}

ENV=Environment(loader=FileSystemLoader(ROOT/'templates'),autoescape=select_autoescape(['html','xml']))

def render(template,path,depth=0,**kwargs):
    path=PUBLIC/path
    path.parent.mkdir(parents=True,exist_ok=True)
    rel='../'*depth or './'
    values={'root':rel,'categories':CATEGORIES,'total_count':len(ALL),'page_type':'home','current_category':None,'crumbs':'','description':'Explore the people, places, and histories of the World of Avalor.','title':'The Royal Archives'}
    values.update(kwargs)
    path.write_text(ENV.get_template(template).render(**values),encoding='utf-8')

if PUBLIC.exists():shutil.rmtree(PUBLIC)
PUBLIC.mkdir()
shutil.copytree(ROOT/'assets',PUBLIC/'assets',dirs_exist_ok=True)
(PUBLIC/'.nojekyll').write_text('')
render('home.html','index.html',page_type='home',title='Home',featured=FEATURED)
render('list.html','articles/index.html',depth=1,page_type='all',title='All records',crumbs='All records',heading='All records',overline='CATALOGUE · A–Z',intro='An alphabetical index of publicly accessible records, maintained by the Royal Commission of Historical Inquiry.',items=ALL)
for cat in CATEGORIES:
    subset=[a for a in ALL if a['category']==cat['name']]
    if cat['name'] == 'People & Legends':
        render('people.html',f'collections/{cat["slug"]}/index.html',depth=2,page_type='category',title=cat['name'],crumbs=cat['name'],current_category=cat['name'],heading=cat['name'],overline='THE COLLECTIONS',intro=cat['description'],items=subset,people_groups=PEOPLE_GROUPS,people_featured=PEOPLE_FEATURED)
    else:
        page = COLLECTION_PAGES[cat['slug']]
        render('collection.html',f'collections/{cat["slug"]}/index.html',depth=2,page_type='category',title=cat['name'],crumbs=cat['name'],current_category=cat['name'],heading=cat['name'],overline='THE COLLECTIONS',intro=cat['description'],items=subset,collection_slug=cat['slug'],nav_config=page['config'],groups=page['groups'],collection_featured=page['featured'])
for a in ALL:
    category_slug=next(c['slug'] for c in CATEGORIES if c['name']==a['category'])
    related=[]
    related_seen=set()
    for related_slug in a['related_slugs']:
        if related_slug in BY_SLUG and related_slug != a['slug'] and related_slug not in related_seen:
            related.append(BY_SLUG[related_slug])
            related_seen.add(related_slug)
    render('article.html',f'articles/{a["slug"]}/index.html',depth=2,page_type='article',title=a['title'],description=a['summary'],crumbs=a['title'],article=a,related=related,category_slug=category_slug,map_location=MAP_LINKS.get(a['slug']))
render('timeline.html','chronicle/index.html',depth=1,page_type='timeline',title='The Living Chronicle',crumbs='The Living Chronicle',events=EVENTS)
render('map.html','map/index.html',depth=1,page_type='map',title='The Cartographer\'s Table',crumbs='Interactive map',map=MAP,map_data=MAP_DATA)
# All search data is intentionally player-facing and comes only from public article sources.
index=[{k:a.get(k,'') for k in ('slug','title','category','entry','summary','featured','body')} for a in ALL]
(PUBLIC/'search-index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf-8')
print(f'Built {len(ALL)} public articles, {len(CATEGORIES)} collections, a timeline and search index in {PUBLIC}')