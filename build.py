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
    {'date':'1 AF', 'era':'THE FOUNDING', 'title':'The kingdom is established', 'text':'Following the struggle against Lord Osmo and the victory at Heroes Hill, Rynhold Frozenroar unites the northern kingdoms beneath the lion banner.', 'article':'kingdom-of-avalor'},
    {'date':'38–106 AF','era':'THE EARLY CROWN','title':'A kingdom learns to endure','text':'Benedikt succeeds Rynhold. Queen Aldara later directs the Royal Survey of the Crossings, improving the roads and communications holding the realm together.','article':'house-frozenroar'},
    {'date':'107–178 AF','era':'THE ELVEN CONCORD','title':'Conflict and accommodation','text':'The reign of Dietmar brings conflict with elven communities of the Forest of the Fey. The resulting Concord is strengthened during Halton’s reign.','article':'house-frozenroar'},
    {'date':'298 AF','era':'THE ROYAL SUCCESSION','title':'The crown laid down','text':'Sylavor voluntarily abdicates, and Arelis assumes full sovereign authority despite her predecessor remaining alive.','article':'house-frozenroar'},
    {'date':'890–893 AF','era':'THE DIVIDED KINGDOM','title':'The War of the Two Lions','text':'Queen Elyra’s lawful crown is challenged by her twin brother Corven. The conflict ends with the accession of Torenna the Reconciler.','article':'house-frozenroar'},
    {'date':'1259–1402 AF','era':'AN AGE OF INJUSTICE AND REFORM','title':'The persecution and its reversal','text':'Arnaud’s reign brings grievous restrictions upon drow communities. Reina later curtails the persecution, and successive rulers extend reform.','article':'jaznaar'},
    {'date':'1983 AF','era':'THE PRESENT REIGN','title':'Gradvum takes the throne','text':'Gradvum Frozenroar begins his reign, later governing alongside Queen Melmiri during a period of consequential historical change.','article':'house-frozenroar'},
    {'date':'Recent decades','era':'THE BLOOD KING’S DEFEAT','title':'The Misfits uncover the truth','text':'The Misfits defeat Cid in the Shadowfell. Jaznaar’s innocence is publicly acknowledged and the old history corrected.','article':'the-misfits'},
    {'date':'Present age','era':'THE AGE OF ASCENDANCY','title':'A kingdom with a wider horizon','text':'Avalor grows in international prominence; Lavitz becomes Lord Marshal and Tel’Lora becomes High Wizard. The work of remembering and governing continues.','article':'age-of-ascendancy'},
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
ALIAS.update({'avalor':'kingdom-of-avalor','misfits':'the-misfits','tel-lora':'tellora-ebbenflow',"heavens-heart":'heavens-heart'})

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
    article['html']=rendered; article['headings']=headings
    return article
ALL=[make_html(a) for a in ALL]
BY_SLUG={a['slug']:a for a in ALL}
for cat in CATEGORIES:cat['count']=len([a for a in ALL if a['category']==cat['name']])
FEATURED=[a for a in ALL if a.get('featured')]
FEATURED.sort(key=lambda a:['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'].index(a['slug']) if a['slug'] in ['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'] else 50)
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
    render('list.html',f'collections/{cat["slug"]}/index.html',depth=2,page_type='category',title=cat['name'],crumbs=cat['name'],current_category=cat['name'],heading=cat['name'],overline='THE COLLECTIONS',intro=cat['description'],items=subset)
for a in ALL:
    category_slug=next(c['slug'] for c in CATEGORIES if c['name']==a['category'])
    related=[BY_SLUG[s] for s in a['related_slugs'] if s in BY_SLUG and s!=a['slug']][:4]
    render('article.html',f'articles/{a["slug"]}/index.html',depth=2,page_type='article',title=a['title'],description=a['summary'],crumbs=a['title'],article=a,related=related,category_slug=category_slug)
render('timeline.html','chronicle/index.html',depth=1,page_type='timeline',title='The Living Chronicle',crumbs='The Living Chronicle',events=EVENTS)
# All search data is intentionally player-facing and comes only from public article sources.
index=[{k:a.get(k,'') for k in ('slug','title','category','entry','summary','featured','body')} for a in ALL]
(PUBLIC/'search-index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf-8')
print(f'Built {len(ALL)} public articles, {len(CATEGORIES)} collections, a timeline and search index in {PUBLIC}')