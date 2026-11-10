"""Build a public-only, zero-cost static wiki for GitHub Pages.

IMPORTANT: only content/articles/*.md is read. Keeper notes/PDFs are deliberately
not part of this repository or deployment pipeline.
"""
from __future__ import annotations
import html
import json
import re
import shutil
import os
from datetime import date
from urllib.parse import urljoin
import unicodedata
from pathlib import Path
from functools import lru_cache
import yaml
import mistune
from public_references import public_sources
from media_optimization import generate_media
from social_cards import card as social_card
from site_quality import write_sitemap, audit_site
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
# Living Chronicle events and filters are maintained in data/living-chronicle.yml.
# This deliberately carries over the previously published event text unchanged.
CHRONICLE_SOURCE = yaml.safe_load((ROOT / 'data' / 'living-chronicle.yml').read_text(encoding='utf-8')) or {}
PERIODS = CHRONICLE_SOURCE.get('periods') or []
TOPICS = CHRONICLE_SOURCE.get('topics') or []
DATE_KINDS = CHRONICLE_SOURCE.get('date_kinds') or []
EVENTS = CHRONICLE_SOURCE.get('events') or []
for name, items in [('period', PERIODS), ('topic', TOPICS), ('date kind', DATE_KINDS)]:
    keys = [item.get('id') for item in items]
    if not keys or len(keys) != len(set(keys)):
        raise ValueError(f'Chronicle has empty or duplicate {name} filters')
    if any(not item.get('label' if name != 'period' else 'title') for item in items):
        raise ValueError(f'Chronicle {name} filter lacks its display title')
valid_periods = {item['id'] for item in PERIODS}
valid_topics = {item['id'] for item in TOPICS}
valid_kinds = {item['id'] for item in DATE_KINDS}
event_ids = set()
for event in EVENTS:
    ident = str(event.get('id') or '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in event_ids:
        raise ValueError(f'Chronicle event has invalid or duplicate id: {ident}')
    event_ids.add(ident)
    if event.get('period') not in valid_periods or event.get('topic') not in valid_topics or event.get('date_kind') not in valid_kinds:
        raise ValueError(f'Chronicle event {ident}: unknown period/topic/date precision')
    if any(not event.get(field) for field in ('date','era','title','text','article')):
        raise ValueError(f'Chronicle event {ident}: missing required public details')
    event['date_note'] = next(kind['description'] for kind in DATE_KINDS if kind['id'] == event['date_kind'])
    event['date_label'] = next(kind['label'] for kind in DATE_KINDS if kind['id'] == event['date_kind'])
    event['period_title'] = next(period['title'] for period in PERIODS if period['id'] == event['period'])

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
for event in EVENTS:
    if event['article'] not in BY_SLUG:
        raise ValueError(f'Chronicle event {event["id"]}: unknown public article {event["article"]}')
if not ALL:raise RuntimeError('No public articles found')
ALIAS={}
for a in ALL:
    ALIAS[slugify(a['title'])] = a['slug']
    ALIAS[slugify(a['slug'])] = a['slug']
ALIAS.update({'avalor':'kingdom-of-avalor','misfits':'the-misfits','tel-lora':'tellora-ebbenflow',"heavens-heart":'heavens-heart','royal-commission-of-historical-inquiry':'royal-commission-historical-inquiry'})
# Retired entries remain accessible as anchors in authoritative parent articles.
# Their old slugs and titles keep resolving even after the source files are consolidated.
MERGES = (yaml.safe_load((ROOT/'data'/'article-merges.yml').read_text(encoding='utf-8')) or {}).get('retired', {})
for obsolete_slug, rule in MERGES.items():
    if obsolete_slug in BY_SLUG:
        raise ValueError(f'Retired article {obsolete_slug} still has a standalone source file')
    if rule['parent'] not in BY_SLUG:
        raise ValueError(f'Retired article {obsolete_slug} points to missing parent {rule["parent"]}')
    if not re.fullmatch(r'[a-z0-9-]+',str(rule['section'])):
        raise ValueError(f'Retired article {obsolete_slug} has invalid section')
    for alias_name in (obsolete_slug,rule['title']):
        name_key = slugify(alias_name)
        if name_key in ALIAS and ALIAS[name_key] != obsolete_slug:
            raise ValueError(f'Retired article {obsolete_slug} collides with alias {alias_name}')
        ALIAS[name_key] = obsolete_slug
MERGE_BY_DESTINATION={(r['parent'],r['section']):{'slug':old,'title':r['title']} for old,r in MERGES.items()}

@lru_cache

def markdown_renderer():
    return mistune.create_markdown(escape=True,plugins=['table','strikethrough'])

def resolve_wikilink_target(target):
    """Resolve an article or an article#heading link into its public URL parts."""
    article_name, divider, heading = str(target).partition('#')
    article_slug = ALIAS.get(slugify(article_name))
    if not article_slug:
        return None
    if article_slug in MERGES:
        retired = MERGES[article_slug]
        return (retired['parent'],retired['section'])
    anchor = slugify(heading) if divider else ''
    if divider and not anchor:
        return None
    return (article_slug, anchor)

def wikilink_sub(match, relative_root):
    target=match.group(1)
    if '|' in target: target, label = target.split('|',1)
    else: label=target
    resolved=resolve_wikilink_target(target)
    if resolved:
        target_slug, anchor = resolved
        suffix = f'#{anchor}' if anchor else ''
        return f'[{label}]({relative_root}articles/{target_slug}/{suffix})'
    return label

def render_fact_value(value):
    """Safely link fact values that name an article; allow explicit [[Article|label]].
    Facts are public editorial metadata, not Markdown or trusted HTML.
    """
    raw = str(value).strip()
    if '[[' not in raw:
        resolved = resolve_wikilink_target(raw)
        if resolved:
            slug, anchor = resolved
            suffix = f'#{anchor}' if anchor else ''
            return f'<a href="../../articles/{slug}/{suffix}">{html.escape(raw)}</a>'
        return html.escape(raw)
    parts = []
    position = 0
    for match in re.finditer(r'\[\[([^\]]+)\]\]', raw):
        parts.append(html.escape(raw[position:match.start()]))
        target, separator, label = match.group(1).partition('|')
        if not separator:
            label = target
        resolved = resolve_wikilink_target(target)
        if resolved:
            target_slug, anchor = resolved
            suffix = f'#{anchor}' if anchor else ''
            parts.append(f'<a href="../../articles/{target_slug}/{suffix}">{html.escape(label)}</a>')
        else:
            parts.append(html.escape(label))
        position = match.end()
    parts.append(html.escape(raw[position:]))
    return ''.join(parts)

# Article visual modules are public editorial presentation, not new lore.
# Their text, captions and image paths are escaped; raw HTML is never accepted.
def article_image_src(raw, article_slug):
    source = str(raw or '').strip()
    match = re.fullmatch(r'/?assets/uploads/([A-Za-z0-9._/-]+\.(?:png|jpg|jpeg|webp|gif))', source, re.I)
    if not match or '..' in match.group(1).split('/'):
        raise ValueError(f'{article_slug}: illustration must be an uploaded public image: {source}')
    filepath = ROOT / 'assets' / 'uploads' / match.group(1)
    if not filepath.is_file():
        raise ValueError(f'{article_slug}: illustration image missing: {source}')
    return '../../assets/uploads/' + match.group(1)


def insert_article_modules(rendered, article, headings):
    """Insert optional CMS-managed figures and callouts after a chosen paragraph.

    Placement is an existing section ID and optional 1-based paragraph number.
    Ordinary Markdown articles remain unchanged if no modules are provided.
    """
    existing = {h['id'] for h in headings}
    modules = []
    figures = article.get('illustrations') or []
    notes = article.get('callouts') or []
    highlights = article.get('highlight_sections') or []
    if not isinstance(figures, list) or len(figures) > 3:
        raise ValueError(f"{article['slug']}: illustrations must be a list of at most three")
    if not isinstance(notes, list) or len(notes) > 4:
        raise ValueError(f"{article['slug']}: callouts must be a list of at most four")
    if not isinstance(highlights, list) or len(highlights) > 3:
        raise ValueError(f"{article['slug']}: highlighted chapters must be a list of at most three")
    for figure in figures:
        if not isinstance(figure, dict):
            raise ValueError(f"{article['slug']}: invalid illustration")
        position = str(figure.get('after') or '').strip()
        layout = str(figure.get('layout') or 'wide')
        if layout not in {'wide', 'inset-left', 'inset-right'}:
            raise ValueError(f"{article['slug']}: invalid illustration layout {layout}")
        alt = str(figure.get('alt') or '').strip()
        caption = str(figure.get('caption') or '').strip()
        if not alt or not caption:
            raise ValueError(f"{article['slug']}: illustration needs alt text and a caption")
        url = article_image_src(figure.get('image'), article['slug'])
        fragment = (f'<figure class="archive-figure archive-figure--{layout}">'
                    f'<img loading="lazy" decoding="async" src="{html.escape(url, quote=True)}" '
                    f'alt="{html.escape(alt, quote=True)}">'
                    f'<figcaption>{html.escape(caption)}</figcaption></figure>')
        modules.append((position, figure.get('paragraph', 1), fragment))
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError(f"{article['slug']}: invalid callout")
        position = str(note.get('after') or '').strip()
        kind = str(note.get('type') or '')
        if kind not in {'quote', 'reflection', 'note', 'contested'}:
            raise ValueError(f"{article['slug']}: invalid callout type {kind}")
        words = str(note.get('text') or '').strip()
        if not words:
            raise ValueError(f"{article['slug']}: empty callout")
        name = {'quote': 'FROM THIS ACCOUNT', 'reflection': 'THE ARCHIVIST\'S REFLECTION',
                'note': "A SCHOLAR'S COMMENTARY", 'contested': 'A CONTESTED ACCOUNT'}[kind]
        if kind == 'quote' and words not in article['body']:
            raise ValueError(f"{article['slug']}: direct quotation must occur verbatim in the article")
        detail = html.escape(str(note.get('attribution') or '').strip())
        content = html.escape(words)
        if kind == 'quote':
            message = f'<blockquote><p>{content}</p></blockquote>'
        elif kind == 'reflection':
            message = f'<p class="archive-reflection-text">{content}</p>'
        else:
            message = f'<p>{content}</p>'
        if kind == 'note':
            scholar = str(note.get('scholar') or '').strip()
            scholar_names = {
                'lady-miren-dast': 'Lady Miren Dast',
                'brother-halden-korr': 'Brother Halden Korr',
                'professor-xiomara-thal': 'Professor Xiomara Thal'
            }
            if scholar not in scholar_names or scholar not in BY_SLUG:
                raise ValueError(f"{article['slug']}: scholarly note must name a known public Commission contributor")
            scholar_href = '../../articles/' + scholar + '/'
            credit = (f'<small>Commentary by <a href="{scholar_href}">'
                      f'{html.escape(scholar_names[scholar])}</a>'
                      + (f' · {detail}' if detail else '') + '</small>')
        else:
            credit = f'<small>{detail}</small>' if detail else ''
        fragment = (f'<aside class="archive-callout archive-callout--{kind}" '
                    f'aria-label="{html.escape(name, quote=True)}">'
                    f'<span class="archive-callout-label">{html.escape(name)}</span>'
                    f'{message}{credit}</aside>')
        modules.append((position, note.get('paragraph', 1), fragment))
    if not modules:
        return highlight_article_sections(rendered, article, headings)
    insertions = []
    for order, (position, paragraph, fragment) in enumerate(modules):
        section_id = slugify(position)
        if section_id not in existing:
            raise ValueError(f"{article['slug']}: visual module has unknown section {position}")
        try:
            paragraph = int(paragraph)
        except (ValueError, TypeError):
            raise ValueError(f"{article['slug']}: invalid visual module paragraph {paragraph}")
        if paragraph < 1:
            raise ValueError(f"{article['slug']}: paragraph number must start at 1")
        heading = re.search(r'<h2 id="' + re.escape(section_id) + r'">.*?</h2>', rendered, flags=re.S)
        if not heading:
            raise ValueError(f"{article['slug']}: section not rendered: {section_id}")
        next_heading = rendered.find('<h2 id=', heading.end())
        section_end = len(rendered) if next_heading == -1 else next_heading
        subsection = rendered[heading.end():section_end]
        paragraphs = list(re.finditer(r'<p(?:\s[^>]*)?>.*?</p>', subsection, flags=re.S))
        if paragraph > len(paragraphs):
            raise ValueError(f"{article['slug']}: visual module for {section_id} requests paragraph {paragraph}, only {len(paragraphs)} available")
        where = heading.end() + paragraphs[paragraph-1].end()
        insertions.append((where, order, fragment))
    for position, order, fragment in sorted(insertions, key=lambda item: (item[0], item[1]), reverse=True):
        rendered = rendered[:position] + '\n' + fragment + '\n' + rendered[position:]
    return highlight_article_sections(rendered, article, headings)


def highlight_article_sections(rendered, article, headings):
    """Tint a few consequential chapters while preserving every existing heading anchor."""
    items = article.get('highlight_sections') or []
    if not items:
        return rendered
    known = {h['id'] for h in headings}
    selected = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{article['slug']}: highlight entry must be an object")
        ident = slugify(str(item.get('section') or ''))
        tone = str(item.get('tone') or '')
        if ident not in known or ident in selected:
            raise ValueError(f"{article['slug']}: unknown or duplicate highlighted chapter {ident}")
        if tone not in {'turning-point', 'remembrance', 'legacy'}:
            raise ValueError(f"{article['slug']}: unsupported highlight tone {tone}")
        selected[ident] = tone
    matches = list(re.finditer(r'<h2 id="([^"]+)">.*?</h2>', rendered, re.S))
    for i in range(len(matches)-1, -1, -1):
        heading = matches[i]
        ident = heading.group(1)
        if ident not in selected:
            continue
        start = heading.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(rendered)
        tone = selected[ident]
        rendered = (rendered[:start] +
                    f'<section class="archive-highlight archive-highlight--{tone}" aria-labelledby="{ident}">' +
                    rendered[start:end].rstrip() +
                    '</section>\n' + rendered[end:])
    return rendered


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
    rendered=insert_article_modules(rendered, article, headings)
    # Convert Pages CMS media paths into relative paths that work on
    # project GitHub Pages sites such as /avalor-wiki/.
    image_raw=str(article.get('image') or '').strip()
    if image_raw.startswith('/assets/uploads/'):
        article['image_url']=rel+image_raw.lstrip('/')
    elif image_raw.startswith('assets/uploads/'):
        article['image_url']=rel+image_raw
    else:
        article['image_url']=None
    article['brief_entry'] = article['category'] == 'Kingdoms & Places' and len(re.findall(r"\b[\w'-]+\b", article['body'])) < 420
    for fact in article['facts_parsed']:
        if str(fact['value']).strip().casefold() == 'not established':
            fact['value'] = 'Unrecorded'
        fact['value_html'] = render_fact_value(fact['value'])
    article['html']=rendered; article['headings']=headings
    return article
ALL=[make_html(a) for a in ALL]
BY_SLUG={a['slug']:a for a in ALL}
for old, rule in MERGES.items():
    if rule['section'] not in {h['id'] for h in BY_SLUG[rule['parent']]['headings']}:
        raise ValueError(f'Retired record {old} points to missing section {rule["parent"]}#{rule["section"]}')
for cat in CATEGORIES:cat['count']=len([a for a in ALL if a['category']==cat['name']])
FEATURED=[a for a in ALL if a.get('featured')]
FEATURED.sort(key=lambda a:['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'].index(a['slug']) if a['slug'] in ['kingdom-of-avalor','renada','lavitz-shawe','the-misfits','the-aegis','house-frozenroar'] else 50)

# Guided journeys are public editorial reading routes assembled from existing articles.
# Do not load private Keeper notes or infer new history in route descriptions.
JOURNEYS_SOURCE = yaml.safe_load((ROOT / 'data' / 'reading-journeys.yml').read_text(encoding='utf-8')) or {}
JOURNEYS = []
JOURNEY_ARTICLE_STEPS = {}
JOURNEY_IDS = set()
for raw_journey in JOURNEYS_SOURCE.get('journeys', []):
    ident = str(raw_journey.get('id', '')).strip()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in JOURNEY_IDS:
        raise ValueError(f'Invalid or duplicate reading journey id: {ident}')
    JOURNEY_IDS.add(ident)
    steps = raw_journey.get('steps') or []
    if len(steps) < 3:
        raise ValueError(f'Journey {ident} must have at least three public records')
    mapped_steps = []
    seen = set()
    for number, raw_step in enumerate(steps, start=1):
        article_slug = str(raw_step.get('article') or '')
        if article_slug not in BY_SLUG or article_slug in seen:
            raise ValueError(f'Journey {ident}: missing or duplicated public article {article_slug}')
        if not raw_step.get('label') or not raw_step.get('introduction'):
            raise ValueError(f'Journey {ident}: step {number} is missing descriptive text')
        seen.add(article_slug)
        mapped_steps.append({
            'number': number, 'article': BY_SLUG[article_slug],
            'label': str(raw_step['label']), 'introduction': str(raw_step['introduction'])
        })
    if not all(raw_journey.get(key) for key in ('title', 'subtitle', 'overline', 'summary', 'editorial_note', 'era')):
        raise ValueError(f'Journey {ident} is missing required public presentation fields')
    journey = {key: raw_journey[key] for key in ('title', 'subtitle', 'overline', 'summary', 'editorial_note', 'era')}
    journey.update({'id': ident, 'steps': mapped_steps})
    JOURNEYS.append(journey)
    for i, step in enumerate(mapped_steps):
        JOURNEY_ARTICLE_STEPS.setdefault(step['article']['slug'], []).append({
            'journey_id': ident, 'journey_title': journey['title'], 'number': i+1,
            'total': len(mapped_steps),
            'previous': mapped_steps[i-1] if i else None,
            'next': mapped_steps[i+1] if i+1 < len(mapped_steps) else None
        })

# The Archivist's Welcome routes are curated player-facing navigation, never
# newly established facts or campaign secrets. Every reading step is a real
# public article, and every longer path is an existing public reading journey.
WELCOME_SOURCE = yaml.safe_load((ROOT / 'data' / 'welcome-routes.yml').read_text(encoding='utf-8')) or {}
WELCOME_ROUTES = []
WELCOME_EXPECTED_IDS = ('kingdom','heroes','history','world')
WELCOME_REQUIRED_TEXT = ('title','kicker','symbol','tagline','intro','welcome','destination_label')
for raw_route in WELCOME_SOURCE.get('routes', []):
    ident = str(raw_route.get('id') or '').strip()
    if ident not in WELCOME_EXPECTED_IDS or ident in {r['id'] for r in WELCOME_ROUTES}:
        raise ValueError(f'Welcome route ID is invalid or duplicated: {ident}')
    if any(not str(raw_route.get(key) or '').strip() for key in WELCOME_REQUIRED_TEXT):
        raise ValueError(f'Welcome route {ident} has missing display text')
    steps = raw_route.get('articles') or []
    if not isinstance(steps, list) or len(steps) != 3:
        raise ValueError(f'Welcome route {ident} must present exactly three public starting records')
    seen = set()
    mapped = []
    for number, step in enumerate(steps, 1):
        slug = str(step.get('article') or '')
        if slug not in BY_SLUG or slug in seen or not str(step.get('invitation') or '').strip():
            raise ValueError(f'Welcome route {ident}: invalid or repeated public article {slug}')
        seen.add(slug)
        mapped.append({'number':number,'article':BY_SLUG[slug],'invitation':str(step['invitation'])})
    dest = str(raw_route.get('destination') or '')
    if dest == 'atlas':
        dest_url = 'map/'
        dest_type = 'ATLAS'
    elif dest in JOURNEY_IDS:
        dest_url = 'journeys/' + dest + '/'
        dest_type = 'GUIDED READING JOURNEY'
    else:
        raise ValueError(f'Welcome route {ident}: destination must be a published journey or the Atlas')
    WELCOME_ROUTES.append({
        'id':ident, **{key:str(raw_route[key]) for key in WELCOME_REQUIRED_TEXT},
        'steps':mapped,'destination':dest_url,'destination_type':dest_type,
    })
if [r['id'] for r in WELCOME_ROUTES] != list(WELCOME_EXPECTED_IDS):
    raise ValueError('Welcome routes must contain the four established entry choices in order')

# The relationship atlas only depicts curated public connections. Never infer
# genealogy from consecutive reigns or invent links to make a diagram prettier.
RELATIONSHIPS_SOURCE = yaml.safe_load((ROOT / 'data' / 'relationship-maps.yml').read_text(encoding='utf-8')) or {}
RELATIONSHIP_MAPS = []
RELATIONSHIP_BY_ARTICLE = {}
RELATIONSHIP_IDS = set()
ALLOWED_EDGE_TYPES = {'fellowship', 'later', 'companion', 'prior-friendship', 'parent', 'consort', 'sibling'}
ALLOWED_NODE_KINDS = {'group', 'person', 'royal'}
for raw_graph in RELATIONSHIPS_SOURCE.get('maps', []):
    ident = str(raw_graph.get('id') or '').strip()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in RELATIONSHIP_IDS:
        raise ValueError(f'Invalid or duplicated relationship map id: {ident}')
    RELATIONSHIP_IDS.add(ident)
    required = ('title', 'subtitle', 'summary', 'note', 'related_article', 'icon')
    if not all(raw_graph.get(field) for field in required):
        raise ValueError(f'Incomplete relationship map description: {ident}')
    anchor = str(raw_graph['related_article'])
    if anchor not in BY_SLUG:
        raise ValueError(f'Relationship map {ident} missing public related article {anchor}')
    nodes = []
    node_index = {}
    for raw_node in raw_graph.get('nodes', []):
        node_id = str(raw_node.get('id') or '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', node_id) or node_id in node_index:
            raise ValueError(f'{ident}: invalid or duplicate node {node_id}')
        article = str(raw_node.get('article') or '')
        if article and article not in BY_SLUG:
            raise ValueError(f'{ident}: missing public article for {node_id}: {article}')
        x, y = float(raw_node.get('x', -1)), float(raw_node.get('y', -1))
        if not (6 <= x <= 94 and 6 <= y <= 94):
            raise ValueError(f'{ident}: node coordinates outside safe canvas: {node_id}')
        if raw_node.get('kind') not in ALLOWED_NODE_KINDS or not raw_node.get('label') or not raw_node.get('detail'):
            raise ValueError(f'{ident}: incomplete node {node_id}')
        node = {'id': node_id, 'x': x, 'y': y, 'kind': raw_node['kind'],
                'label': str(raw_node['label']), 'detail': str(raw_node['detail']), 'article': article,
                'symbol': str(raw_node.get('symbol') or '')}
        node_index[node_id] = node
        nodes.append(node)
    if len(nodes) < 2:
        raise ValueError(f'{ident}: too few relationship nodes')
    edges = []
    seen_edges = set()
    for raw_edge in raw_graph.get('edges', []):
        a, b = str(raw_edge.get('from') or ''), str(raw_edge.get('to') or '')
        kind = str(raw_edge.get('type') or '')
        pair = tuple(sorted((a,b)))
        if a not in node_index or b not in node_index or a == b:
            raise ValueError(f'{ident}: invalid relationship edge {a}/{b}')
        if pair in seen_edges or kind not in ALLOWED_EDGE_TYPES or not raw_edge.get('label'):
            raise ValueError(f'{ident}: duplicate or incomplete relationship edge {a}/{b}')
        seen_edges.add(pair)
        edges.append({'from': a, 'to': b, 'type': kind, 'label': str(raw_edge['label']),
                      'from_node': node_index[a], 'to_node': node_index[b]})
    if not edges:
        raise ValueError(f'{ident}: no relationships')
    legend_names = {'fellowship': 'Fellowship membership', 'later': 'Later arrival / traveling companion',
                    'parent': 'Documented parent–child', 'consort': 'Consorts / shared parentage',
                    'sibling': 'Documented siblings', 'companion': 'Honored companion',
                    'prior-friendship': 'Friends before the Misfits'}
    legend = [(kind, legend_names[kind]) for kind in legend_names if any(edge['type'] == kind for edge in edges)]
    graph = {'id': ident, **{key: raw_graph[key] for key in required},
             'nodes': nodes, 'edges': edges, 'legend': legend,
             'client_data': {'nodes': nodes,
                             'edges': [{key: edge[key] for key in ('from','to','type','label')} for edge in edges]}}
    RELATIONSHIP_MAPS.append(graph)
    for node in nodes:
        if node['article']:
            RELATIONSHIP_BY_ARTICLE.setdefault(node['article'], []).append(graph)
    RELATIONSHIP_BY_ARTICLE.setdefault(anchor, [])
    if graph not in RELATIONSHIP_BY_ARTICLE[anchor]:
        RELATIONSHIP_BY_ARTICLE[anchor].append(graph)

# A cross-archive connection index is separately curated rather than inferred
# from related-article lists (which indicate reading recommendations, not facts).
CONNECTION_WEB_SOURCE = yaml.safe_load((ROOT / 'data' / 'connections-explorer.yml').read_text(encoding='utf-8')) or {}
WEB_KINDS = {'people', 'organizations', 'places', 'events'}
WEB_EDGE_TYPES = {'fellowship', 'friendship', 'training', 'office', 'stewardship',
                  'heritage', 'location', 'record', 'history', 'kinship',
                  'founding', 'opposition', 'faith'}
CONNECTION_WEB_NODES = []
CONNECTION_WEB_BY_ARTICLE = {}
for raw_node in CONNECTION_WEB_SOURCE.get('nodes', []):
    slug = str(raw_node.get('article') or '')
    kind = raw_node.get('kind')
    if slug not in BY_SLUG or kind not in WEB_KINDS or slug in CONNECTION_WEB_BY_ARTICLE:
        raise ValueError('Connection Explorer has unknown, duplicated or mistyped public node: ' + slug)
    source_article = BY_SLUG[slug]
    item = {'id': slug, 'article': slug, 'label': source_article['title'],
            'kind': kind, 'summary': source_article['summary']}
    CONNECTION_WEB_NODES.append(item)
    CONNECTION_WEB_BY_ARTICLE[slug] = item
if len(CONNECTION_WEB_NODES) < 15:
    raise ValueError('Connection Explorer needs a meaningful range of public records')
CONNECTION_WEB_EDGES = []
connection_pairs = set()
for raw_edge in CONNECTION_WEB_SOURCE.get('edges', []):
    left, right = str(raw_edge.get('from') or ''), str(raw_edge.get('to') or '')
    evidence = str(raw_edge.get('evidence') or '')
    typ = str(raw_edge.get('type') or '')
    label = str(raw_edge.get('label') or '').strip()
    pair = tuple(sorted((left, right)))
    if (left not in CONNECTION_WEB_BY_ARTICLE or right not in CONNECTION_WEB_BY_ARTICLE or
            left == right or pair in connection_pairs or evidence not in BY_SLUG or
            typ not in WEB_EDGE_TYPES or not label):
        raise ValueError('Connection Explorer has an unsupported/duplicate relationship: ' + left + '/' + right)
    connection_pairs.add(pair)
    CONNECTION_WEB_EDGES.append({'from': left, 'to': right, 'label': label,
                                 'type': typ, 'evidence': evidence,
                                 'source_title': BY_SLUG[evidence]['title']})
if len(CONNECTION_WEB_EDGES) < 25:
    raise ValueError('Connection Explorer has too few curated relationships')
if any(not any(e['from']==n['id'] or e['to']==n['id'] for e in CONNECTION_WEB_EDGES) for n in CONNECTION_WEB_NODES):
    raise ValueError('Connection Explorer may not publish isolated nodes')
CONNECTION_WEB = {'nodes': CONNECTION_WEB_NODES, 'edges': CONNECTION_WEB_EDGES}
for graph in RELATIONSHIP_MAPS:
    graph['client_data']['web_articles'] = [node['article'] for node in graph['nodes']
                                           if node['article'] in CONNECTION_WEB_BY_ARTICLE]

# Only independently curated, public character dossiers enter side-by-side
# comparisons. Facts must name a chapter in that character's own published
# biography; a missing source section fails the build rather than guessing.
COMPARISON_SOURCE = yaml.safe_load((ROOT/'data'/'character-comparisons.yml').read_text(encoding='utf-8')) or {}
COMPARISON_FIELDS = ('role', 'affiliations', 'turning', 'legacy')
COMPARISON_LABELS = {'role':'Calling & public identity',
                     'affiliations':'Alliances & institutions',
                     'turning':'Defining decisions',
                     'legacy':'Legacy & significance'}
COMPARISON_PROFILES = []
COMPARISON_BY_SLUG = {}
for raw in COMPARISON_SOURCE.get('profiles', []):
    slug = str(raw.get('article') or '')
    if slug not in BY_SLUG or BY_SLUG[slug]['category'] != 'People & Legends' or slug in COMPARISON_BY_SLUG:
        raise ValueError('Comparison dossier references an unknown or duplicated public person: ' + slug)
    source = BY_SLUG[slug]
    known_chapters = {h['id'] for h in source['headings']}
    facts = {}
    for key in COMPARISON_FIELDS:
        record = raw.get(key)
        if not isinstance(record,dict):
            raise ValueError(f'Comparison dossier {slug}: missing {key}')
        statement = str(record.get('text') or '').strip()
        chapter = str(record.get('chapter') or '').strip()
        if not statement or chapter not in known_chapters:
            raise ValueError(f'Comparison dossier {slug}: unsupported {key} chapter {chapter}')
        facts[key] = {'text':statement,'chapter':chapter,
                      'source':'Chapter: '+next(h['text'] for h in source['headings'] if h['id']==chapter)}
    artwork = str(source.get('image') or '').lstrip('/')
    if artwork and (not re.fullmatch(r'assets/uploads/[A-Za-z0-9._/-]+\.(?:png|jpe?g|webp|gif)',artwork,re.I)
                    or '..' in artwork.split('/') or not (ROOT/artwork).is_file()):
        raise ValueError(f'Comparison dossier {slug}: invalid or missing public portrait')
    person = {'id':slug,'name':source['title'],'subtitle':str(source.get('subtitle') or ''),
              'summary':source['summary'],'era':str(source.get('era') or 'Era not recorded'),
              'image':artwork,'image_alt':str(source.get('image_alt') or ('Illustration accompanying the public record of '+source['title'])),
              'facts':facts}
    COMPARISON_PROFILES.append(person)
    COMPARISON_BY_SLUG[slug] = person
COMPARISON_PROFILES.sort(key=lambda p:p['name'].casefold())
if len(COMPARISON_PROFILES)<12:
    raise ValueError('Comparison Dossiers requires a substantial reviewed collection')

COMPARISON_PRESETS = []
COMPARISON_PRESET_IDS = set()
for raw in COMPARISON_SOURCE.get('presets', []):
    ident = str(raw.get('id') or '')
    left, right = str(raw.get('left') or ''), str(raw.get('right') or '')
    if (not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',ident) or
            ident in COMPARISON_PRESET_IDS or left not in COMPARISON_BY_SLUG or
            right not in COMPARISON_BY_SLUG or left == right or
            not str(raw.get('title') or '').strip() or not str(raw.get('description') or '').strip()):
        raise ValueError('Comparison Dossiers has invalid or duplicate suggested pairing: '+ident)
    COMPARISON_PRESET_IDS.add(ident)
    COMPARISON_PRESETS.append({
        'id': ident,'title':str(raw['title']),'description':str(raw['description']),
        'left':left,'right':right,
        'left_name':COMPARISON_BY_SLUG[left]['name'],'right_name':COMPARISON_BY_SLUG[right]['name']})
COMPARISON_DATA = {'profiles':COMPARISON_PROFILES,'presets':COMPARISON_PRESETS,
                   'fields':[{'key':key,'label':COMPARISON_LABELS[key]} for key in COMPARISON_FIELDS]}

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
    def map_reference(raw_ref):
        raw_ref = str(raw_ref or '').strip()
        if not raw_ref:
            return ('','', '')
        base, _, anchor = raw_ref.partition('#')
        if base in MERGES:
            r = MERGES[base]
            return (r['parent'],r['section'],r['title'])
        if base not in BY_SLUG:
            raise ValueError(f'{ident}: map article {raw_ref} does not exist')
        if anchor and anchor not in {h['id'] for h in BY_SLUG[base]['headings']}:
            raise ValueError(f'{ident}: map section {raw_ref} does not exist')
        match = MERGE_BY_DESTINATION.get((base,anchor)) if anchor else None
        return (base,anchor,match['title'] if match else BY_SLUG[base]['title'])
    article_slug, article_anchor, _ = map_reference(raw.get('article'))
    subplace_slugs = [s.strip() for s in str(raw.get('related_places') or '').split(',') if s.strip()]
    subplaces = []
    for source in subplace_slugs:
        slug, anchor, name = map_reference(source)
        if slug:
            subplaces.append({'slug':slug,'anchor':anchor,'name':name})
    MAP_LOCATIONS.append({
        'id':ident, 'name':str(raw.get('name') or ident),
        'type':kind,'x':x,'y':y,'placed':placed,
        'description':str(raw.get('description') or ''),
        'article':article_slug,'article_anchor':article_anchor,'subplaces':subplaces,
        'published':bool(raw.get('published',True)),
        'provisional':bool(raw.get('provisional',False)),
    })
raw_map_image = str(MAP.get('image') or '').strip().lstrip('/')
# No remote URLs, path traversal, or private source files allowed.
if raw_map_image and (not raw_map_image.startswith('assets/uploads/') or '..' in raw_map_image):
    raise ValueError('Map image must be a public file in assets/uploads/')
MAP_IMAGE = '../'+raw_map_image if raw_map_image else ''
MAP_DATA = {'image': MAP_IMAGE, 'root':'../','locations': MAP_LOCATIONS}
# Atlas Through Time: explicit provenance for each historic map spotlight.
# Events without source-supported locations remain visible in chronology but
# NEVER acquire invented coordinates, battlefields or ceremonial sites.
ATLAS_HISTORY_SOURCE = yaml.safe_load((ROOT/'data'/'atlas-history.yml').read_text(encoding='utf-8')) or {}
if not isinstance(ATLAS_HISTORY_SOURCE,dict) or not isinstance(ATLAS_HISTORY_SOURCE.get('links'),list):
    raise ValueError('Historical atlas links must be a YAML list')
ATLAS_HISTORY_RELATIONS = {
    'event-site':'Recorded site',
    'affected-region':'Affected region',
    'associated-place':'Associated place — not necessarily the event site',
}
ATLAS_HISTORY_LINKS = {}
mapped_by_id = {loc['id']:loc for loc in MAP_LOCATIONS}
event_by_id = {event['id']:event for event in EVENTS}
for item in ATLAS_HISTORY_SOURCE['links']:
    if not isinstance(item,dict):
        raise ValueError('Historical atlas link must be an object')
    event_id, place_id = str(item.get('event') or ''),str(item.get('place') or '')
    relation = str(item.get('relation') or '')
    note = str(item.get('note') or '').strip()
    loc = mapped_by_id.get(place_id)
    if event_id not in event_by_id or event_id in ATLAS_HISTORY_LINKS:
        raise ValueError(f'Historical atlas: unknown or duplicate event {event_id}')
    if not loc or not loc['published'] or not loc['placed'] or loc['provisional']:
        raise ValueError(f'Historical atlas: {event_id} requires an approved, non-provisional placed pin, got {place_id}')
    if relation not in ATLAS_HISTORY_RELATIONS or len(note)<35:
        raise ValueError(f'Historical atlas: {event_id} requires a clear type and public provenance note')
    ATLAS_HISTORY_LINKS[event_id] = {
        'pin':place_id,'place_name':loc['name'],'relation':relation,
        'relation_label':ATLAS_HISTORY_RELATIONS[relation],'note':note,
    }
ATLAS_HISTORY_EVENTS = []
for event in EVENTS:
    attachment = ATLAS_HISTORY_LINKS.get(event['id'])
    event['atlas_link'] = attachment
    ATLAS_HISTORY_EVENTS.append({
        'id':event['id'],'date':event['date'],'date_kind':event['date_kind'],
        'date_label':event['date_label'],'date_note':event['date_note'],
        'period':event['period'],'period_title':event['period_title'],
        'title':event['title'],'era':event['era'],'text':event['text'],
        'article':event['article'],'atlas':attachment,
    })
if len(ATLAS_HISTORY_EVENTS)!=len(EVENTS):
    raise ValueError('Atlas chronology must preserve every Chronicle record')

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


# The illustration gallery is deliberately curated: images uploaded for articles do
# not become gallery exhibits unless an editor publishes a gallery record.
# Editorial folios are modern public reconstructions, not authenticated originals.
EXHIBITS = []
EXHIBIT_IDS = set()
EXHIBITS_BY_ARTICLE = {}
EXHIBIT_PERIODS = {'Founding Age', 'Later Reigns', 'Age of Ascendancy'}
for path in sorted((ROOT/'content'/'exhibits').glob('*.yml')):
    record = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(record, dict):
        raise ValueError(f'{path}: expected YAML object')
    ident = str(record.get('id') or '').strip()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident != path.stem or ident in EXHIBIT_IDS:
        raise ValueError(f'{path}: invalid, duplicated or mismatched ID')
    EXHIBIT_IDS.add(ident)
    if not record.get('published', False): continue
    for field in ('title','subtitle','kind','period','period_group','symbol','summary',
                  'folio_title','folio_text','evidence','uncertainty','interpretation','source_article'):
        if not str(record.get(field) or '').strip():
            raise ValueError(f'{path}: published exhibit missing {field}')
    if record['period_group'] not in EXHIBIT_PERIODS:
        raise ValueError(f'{path}: unknown historical period group')
    src = str(record['source_article'])
    if src not in BY_SLUG:
        raise ValueError(f'{path}: unknown public source article {src}')
    paragraphs = str(record['folio_text']).splitlines()
    if len(paragraphs) < 2 or any(not line.strip() for line in paragraphs):
        raise ValueError(f'{path}: folio requires distinct, nonempty prose paragraphs')
    related = [slug.strip() for slug in str(record.get('related_articles') or '').split(',') if slug.strip()]
    if len(related) != len(set(related)) or any(slug not in BY_SLUG for slug in related):
        raise ValueError(f'{path}: duplicate or unknown related article')
    item = {
        'id': ident, 'title': str(record['title']), 'subtitle': str(record['subtitle']),
        'kind': str(record['kind']), 'period': str(record['period']),
        'period_group': str(record['period_group']), 'symbol': str(record['symbol']),
        'summary': str(record['summary']), 'folio_title': str(record['folio_title']),
        'folio_lines': paragraphs, 'evidence_lines': str(record['evidence']).splitlines(),
        'uncertainty_lines': str(record['uncertainty']).splitlines(),
        'interpretation': str(record['interpretation']),
        'source': {'slug':src, 'title':BY_SLUG[src]['title']},
        'related': [{'slug':slug,'title':BY_SLUG[slug]['title']} for slug in related],
        'featured': bool(record.get('featured', False)), 'reconstruction': True}
    EXHIBITS.append(item)
    for slug in set([src, *related]):
        EXHIBITS_BY_ARTICLE.setdefault(slug, []).append(item)
ORDER = {'founding-settlement':0,'elven-concord':1,'arnauds-edicts':2,
         'reinas-reforms':3,'jaznaars-vindication':4}
EXHIBITS.sort(key=lambda e:(ORDER.get(e['id'],100),e['title']))
for i,item in enumerate(EXHIBITS):
    item['number'] = f'{i+1:02d}'
    item['previous'] = EXHIBITS[i-1] if i else None
    item['next'] = EXHIBITS[i+1] if i+1 < len(EXHIBITS) else None

GALLERY_COLLECTIONS = [
    {'id':'characters', 'title':'Characters', 'description':'Portraits of the people whose lives shaped Avalor.'},
    {'id':'locations', 'title':'Locations', 'description':'Cities, landscapes, sanctuaries, and distant horizons.'},
    {'id':'historical-scenes', 'title':'Historical Scenes', 'description':'Moments from the kingdom’s remembered past.'},
    {'id':'artifacts-symbols', 'title':'Artifacts & Symbols', 'description':'Objects, insignia, and meaningful emblems.'},
    {'id':'maps-heraldry', 'title':'Maps & Heraldry', 'description':'The realm depicted in maps, banners, and arms.'},
]
GALLERY_COLLECTION_BY_ID = {wing['id']: wing for wing in GALLERY_COLLECTIONS}
GALLERY_ITEMS = []
GALLERY_BY_ARTICLE = {}
gallery_ids = set()
for gallery_file in sorted((ROOT / 'content' / 'gallery').glob('*.yml')):
    record = yaml.safe_load(gallery_file.read_text(encoding='utf-8'))
    if not isinstance(record, dict):
        raise ValueError(f'{gallery_file}: expected a YAML object')
    ident = str(record.get('id') or '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident != gallery_file.stem or ident in gallery_ids:
        raise ValueError(f'{gallery_file}: invalid, duplicate, or mismatched gallery ID')
    gallery_ids.add(ident)
    if not record.get('published', False):
        continue
    for field in ('title', 'collection', 'image', 'alt', 'caption'):
        if not str(record.get(field) or '').strip():
            raise ValueError(f'{gallery_file}: published exhibit lacks {field}')
    collection_id = str(record['collection'])
    if collection_id not in GALLERY_COLLECTION_BY_ID:
        raise ValueError(f'{gallery_file}: unknown gallery collection {collection_id}')
    raw_image = str(record['image']).strip().lstrip('/')
    # Gallery images are normally existing CMS uploads. Two vetted, source-controlled
    # archive SVGs are exceptions; never permit arbitrary SVG uploads or remote URLs.
    vetted_artwork = {'assets/crest.svg', 'assets/hero-scene.svg'}
    standard_upload = re.fullmatch(r'assets/uploads/[A-Za-z0-9._/-]+\.(?:png|jpe?g|webp|gif)', raw_image, re.I)
    if (not (standard_upload or raw_image in vetted_artwork)
            or '..' in Path(raw_image).parts or not (ROOT / raw_image).is_file()):
        raise ValueError(f'{gallery_file}: gallery image must be an existing public upload or approved archive illustration')
    related_slugs = [slug.strip() for slug in str(record.get('related_articles') or '').split(',') if slug.strip()]
    if len(related_slugs) != len(set(related_slugs)) or any(slug not in BY_SLUG for slug in related_slugs):
        raise ValueError(f'{gallery_file}: duplicate or unknown related article')
    item = {
        'id': ident,
        'title': str(record['title']),
        'collection': collection_id,
        'collection_title': GALLERY_COLLECTION_BY_ID[collection_id]['title'],
        'image': raw_image,
        'alt': str(record['alt']),
        'caption': str(record['caption']),
        'era': str(record.get('era') or ''),
        'credit': str(record.get('credit') or ''),
        'featured': bool(record.get('featured', False)),
        'related': [{'slug': slug, 'title': BY_SLUG[slug]['title']} for slug in related_slugs],
    }
    GALLERY_ITEMS.append(item)
    for slug in related_slugs:
        GALLERY_BY_ARTICLE.setdefault(slug, []).append(item)
# Automatically catalogue approved character portraits already assigned to
# published People & Legends articles. The curated galleries remain authoritative
# when they have an entry for that character; this only fills genuine gaps.
# Never infer artwork identity from a filename alone.
for article in ALL:
    if article['category'] != 'People & Legends':
        continue
    slug=article['slug']
    if any(item['related'] and item['related'][0]['slug'] == slug
           for item in GALLERY_ITEMS):
        continue
    raw_image=str(article.get('image') or '').strip().lstrip('/')
    # Image paths were validated by article_image_src; do not expose arbitrary
    # URLs, private material, or non-image assets as a portrait.
    if not re.fullmatch(r'assets/uploads/[A-Za-z0-9._/-]+\.(?:png|jpe?g|webp|gif)', raw_image, re.I):
        continue
    if not (ROOT / raw_image).is_file():
        continue
    ident='portrait-'+slug
    if ident in gallery_ids:
        continue
    gallery_ids.add(ident)
    item={
        'id':ident,
        'title':article['title'],
        'collection':'characters',
        'collection_title':GALLERY_COLLECTION_BY_ID['characters']['title'],
        'image':raw_image,
        'alt':str(article.get('image_alt') or 'Portrait associated with '+article['title']+'.'),
        'caption':str(article.get('image_caption') or article['summary']),
        'era':str(article.get('era') or ''),
        'credit':'',
        'featured':False,
        'related':[{'slug':slug,'title':article['title']}],
    }
    GALLERY_ITEMS.append(item)
    GALLERY_BY_ARTICLE.setdefault(slug,[]).append(item)

GALLERY_ITEMS.sort(key=lambda item: (not item['featured'], item['title'].casefold()))
for wing in GALLERY_COLLECTIONS:
    members = [item for item in GALLERY_ITEMS if item['collection'] == wing['id']]
    wing['count'] = len(members)
    wing['cover'] = members[0]['image'] if members else ''

# Dated editorial circulars; publication dates are not dates in Avalor's history.
GAZETTE_ISSUES=[]
for path in sorted((ROOT/'content/gazette').glob('*.yml')):
    issue=yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    if not isinstance(issue,dict) or issue.get('published') is not True:
        continue
    ident=issue.get('id')
    if not isinstance(ident,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',ident) or path.stem!=ident or any(x['id']==ident for x in GAZETTE_ISSUES):
        raise ValueError(f'{path}: invalid Gazette ID')
    if any(not isinstance(issue.get(k),str) or not issue[k].strip() for k in ('title','subtitle','intro','date')):
        raise ValueError(f'{ident}: missing Gazette details')
    try: day=date.fromisoformat(issue['date'])
    except ValueError: raise ValueError(f'{ident}: invalid publication date')
    notes=issue.get('dispatches')
    if not isinstance(notes,list) or not 2<=len(notes)<=8:
        raise ValueError(f'{ident}: two to eight dispatches required')
    prepared=[]
    for n,item in enumerate(notes,1):
        if not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not item[k].strip() for k in ('title','kicker','summary','body','article')):
            raise ValueError(f'{ident}: incomplete dispatch {n}')
        slug=item['article'].strip()
        if slug not in BY_SLUG: raise ValueError(f'{ident}: missing source record {slug}')
        prepared.append({**item,'article':BY_SLUG[slug],'number':n})
    GAZETTE_ISSUES.append({**issue,'date_display':day.strftime('%d %B %Y').lstrip('0'),'dispatches':prepared})
for n,issue in enumerate(sorted(GAZETTE_ISSUES,key=lambda x:(x['date'],x['id'])),1):
    issue['issue_number']=n
GAZETTE_ISSUES.sort(key=lambda x:(x['date'],x['id']),reverse=True)

ENV=Environment(loader=FileSystemLoader(ROOT/'templates'),autoescape=select_autoescape(['html','xml']))

# The canonical base must match the published GitHub Pages project URL; an
# eventual custom domain can override it in CI using AVALOR_SITE_URL.
SITE_URL = os.environ.get('AVALOR_SITE_URL', 'https://yoshi3309.github.io/avalor-wiki/').strip()
if not SITE_URL.startswith('https://') or ' ' in SITE_URL or '?' in SITE_URL or '#' in SITE_URL:
    raise ValueError('AVALOR_SITE_URL must be an absolute HTTPS site base URL')
SITE_URL = SITE_URL.rstrip('/') + '/'


def preview_subject(values):
    """Choose only artwork already assigned to public wiki records."""
    kind = values['page_type']
    title = str(values['title'])
    summary = str(values['description'])
    label = 'The Royal Archives'
    artwork = None
    if kind == 'article':
        a = values['article']
        label = a['category']
        artwork = a.get('image_url')
        if not artwork and GALLERY_BY_ARTICLE.get(a['slug']):
            artwork = GALLERY_BY_ARTICLE[a['slug']][0]['image']
    elif kind == 'gallery':
        wing = values.get('active_gallery_collection')
        label = 'Illustration Gallery'
        if wing:
            artwork = wing.get('cover')
        elif GALLERY_ITEMS:
            artwork = GALLERY_ITEMS[0]['image']
    elif kind == 'exhibits':
        label = 'Historical Documents'
        # A reconstructed folio has no approved photograph of the original.
        # Use neutral archive branding rather than suggesting a real original.
        if values.get('exhibit'):
            label = str(values['exhibit']['kind'])
    elif kind == 'map':
        label = 'Cartographer’s Table'
        artwork = MAP_IMAGE
    elif kind == 'home':
        label = 'A World of Kingdoms and Legends'
        artwork = 'assets/uploads/avalor-official-map.webp'
    elif kind == 'welcome':
        label = 'The Archivist’s Welcome'
    elif kind == 'journeys':
        label = 'Guided Reading'
        journey = values.get('journey')
        if journey and journey.get('steps'):
            first = journey['steps'][0]['article']
            artwork = first.get('image_url')
            if not artwork and GALLERY_BY_ARTICLE.get(first['slug']):
                artwork = GALLERY_BY_ARTICLE[first['slug']][0]['image']
    elif kind == 'compare':
        label = 'Character Comparison Dossiers'
        pair = values.get('comparison_pair')
        if pair:
            artwork = COMPARISON_BY_SLUG[pair['left']]['image'] or None
    elif kind == 'connections':
        label = 'People & Connections'
    elif kind == 'timeline':
        label = 'The Living Chronicle'
    elif kind == 'category':
        label = 'Public Collections'
        collection = values.get('current_category')
        for candidate in ALL:
            if candidate['category'] == collection and candidate.get('image_url'):
                artwork = candidate['image_url']
                break
    elif kind == 'gazette':
        label = 'The Royal Gazette'
        issue=values.get('gazette_issue')
        if issue:
            a=issue['dispatches'][0]['article']
            artwork=a.get('image_url') or (GALLERY_BY_ARTICLE.get(a['slug']) or [{}])[0].get('image')
    elif kind == 'reading-desk':
        label = 'Personal Reading Desk'
    elif kind == 'all':
        label = 'Encyclopedia'
    return (title, summary, label, artwork)


def render(template,path,depth=0,**kwargs):
    path_relative = str(path)
    page = PUBLIC / path_relative
    page.parent.mkdir(parents=True,exist_ok=True)
    rel='../'*depth or './'
    values={'root':rel,'categories':CATEGORIES,'total_count':len(ALL),'page_type':'home','current_category':None,'crumbs':'',
            'description':'Explore the people, places, and histories of the World of Avalor.','title':'The Royal Archives'}
    values.update(kwargs)
    title, summary, label, artwork = preview_subject(values)
    # The path is already a trusted, build-authored page path (never a URL from
    # uploaded content). Preserve canonical trailing slashes for Discord bots.
    canonical = urljoin(SITE_URL, path_relative.removesuffix('index.html'))
    key = path_relative.removesuffix('/index.html').removesuffix('.html')
    if key == 'index':
        key = 'home'
    preview = social_card(ROOT, PUBLIC, key, title, summary, label, artwork)
    values.update({
        'canonical_url': canonical,
        'social_title': title + ' | Archives of Avalor',
        'social_image': urljoin(SITE_URL, preview),
        'social_description': ' '.join(summary.split())[:220],
        'social_image_alt': 'Archive-style preview for ' + title,
        'social_type': 'article' if values['page_type'] in ('article','exhibits') and kwargs.get('exhibit') or values['page_type']=='article' else 'website'
    })
    page.write_text(ENV.get_template(template).render(**values),encoding='utf-8')

if PUBLIC.exists():shutil.rmtree(PUBLIC)
PUBLIC.mkdir()
shutil.copytree(ROOT/'assets',PUBLIC/'assets',dirs_exist_ok=True)
MEDIA_CATALOG = generate_media(ROOT, PUBLIC)
for dossier in COMPARISON_PROFILES:
    dossier['media'] = MEDIA_CATALOG.get(dossier['image'])
# The originals keep their existing stable URLs. Preview metadata is attached
# only after the optimized variants have been generated and verified.
for item in GALLERY_ITEMS:
    item['media'] = MEDIA_CATALOG.get(item['image'])
for wing in GALLERY_COLLECTIONS:
    wing['cover_media'] = MEDIA_CATALOG.get(wing['cover'])
for article in ALL:
    raw_image = str(article.get('image_url') or '').replace('../../','',1)
    article['image_media'] = MEDIA_CATALOG.get(raw_image)
    # Inline CMS figures and Markdown images are progressive-enhanced with
    # WebP <picture> sources, leaving their real original src/alt in place.
    def responsive_article_img(match):
        original_tag = match.group(0)
        src_match = re.search(r'\bsrc="([^"]+)"',original_tag)
        if not src_match:
            return original_tag
        src = html.unescape(src_match.group(1))
        if not src.startswith('../../assets/uploads/'):
            return original_tag
        media = MEDIA_CATALOG.get(src.replace('../../','',1))
        if not media or not media['variants']:
            return original_tag
        variants = media['variants']
        srcset = ', '.join('../../'+v['path']+' '+str(v['width'])+'w' for v in variants)
        img = original_tag
        if not re.search(r'\bwidth\s*=',img):
            img = img.replace('<img ','<img width="'+str(media['width'])+'" height="'+str(media['height'])+'" ',1)
        if not re.search(r'\bloading\s*=',img):
            img = img.replace('<img ','<img loading="lazy" ',1)
        if not re.search(r'\bdecoding\s*=',img):
            img = img.replace('<img ','<img decoding="async" ',1)
        return ('<picture class="archive-responsive-picture"><source type="image/webp" srcset="'
                +html.escape(srcset,quote=True)+'" sizes="(max-width: 710px) 90vw, 680px">'
                +img+'</picture>')
    article['html'] = re.sub(r'<img\b[^>]*>',responsive_article_img,article['html'])
(PUBLIC/'.nojekyll').write_text('')
render('welcome.html','index.html',page_type='welcome',title='Start Here',crumbs='Start Here',description='Choose your first path into Avalor: meet the kingdom, its heroes, its history, or the world itself.',welcome_routes=WELCOME_ROUTES)
render('home.html','archive/index.html',depth=1,page_type='home',title='Archive Home',crumbs='Archive Home',featured=FEATURED,journeys=JOURNEYS,relationship_maps=RELATIONSHIP_MAPS)
# Keep older shared /start/ links valid, including a selected doorway hash.
legacy_start = PUBLIC / 'start' / 'index.html'
legacy_start.parent.mkdir(parents=True, exist_ok=True)
legacy_start.write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<title>Start Here — Archives of Avalor</title>'
    '<meta name="robots" content="noindex">'
    f'<link rel="canonical" href="{SITE_URL}">'
    '<meta http-equiv="refresh" content="0; url=../">'
    '</head><body><p>Start Here has moved to the main entrance. '
    '<a href="../">Begin your visit</a>.</p>'
    '<script>location.replace("../" + location.search + location.hash);</script>'
    '</body></html>', encoding='utf-8')
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
        if related_slug in MERGES:
            rule=MERGES[related_slug]
            destination=rule['parent']
            key=(destination,rule['section'])
            if destination in BY_SLUG and key not in related_seen:
                # A retired record remains a navigable *section*, not a second article.
                related.append({
                    'slug':destination, 'fragment':rule['section'],
                    'title':rule['title'], 'entry':'SECTION',
                    'category':BY_SLUG[destination]['category']
                })
                related_seen.add(key)
        elif related_slug in BY_SLUG and related_slug != a['slug']:
            key=(related_slug,'')
            if key not in related_seen:
                related.append(BY_SLUG[related_slug])
                related_seen.add(key)
    render('article.html',f'articles/{a["slug"]}/index.html',depth=2,page_type='article',title=a['title'],description=a['summary'],crumbs=a['title'],article=a,related=related,category_slug=category_slug,map_location=MAP_LINKS.get(a['slug']),reading_paths=JOURNEY_ARTICLE_STEPS.get(a['slug'], []),relationship_maps=RELATIONSHIP_BY_ARTICLE.get(a['slug'], []),web_connection=a['slug'] in CONNECTION_WEB_BY_ARTICLE,gallery_items=GALLERY_BY_ARTICLE.get(a['slug'], []),historical_exhibits=EXHIBITS_BY_ARTICLE.get(a['slug'], []),comparison_available=a['slug'] in COMPARISON_BY_SLUG)
# Keep all bookmarks to consolidated entries working with immediate, crawler-safe redirects.
for old, rule in MERGES.items():
    target=f'../../articles/{rule["parent"]}/#{rule["section"]}'
    label=html.escape(str(rule['title']))
    location=html.escape(target,quote=True)
    destination=html.escape(rule['parent'].replace('-',' ').title())
    redirect_path=PUBLIC/'articles'/old/'index.html'
    redirect_path.parent.mkdir(parents=True,exist_ok=True)
    redirect_path.write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{label} — Archives of Avalor</title>'
        f'<meta http-equiv="refresh" content="0; url={location}">'
        f'<link rel="canonical" href="{location}">'
        '<meta name="robots" content="noindex"></head>'
        f'<body><p>{label} is now part of {destination}. '
        f'<a href="{location}">Open the section</a>.</p></body></html>',
        encoding='utf-8')
# Public reading-desk catalogue contains metadata only; browser preferences never reach the build.
(PUBLIC/'reading-desk-index.json').write_text(json.dumps([
    {'slug':a['slug'],'title':a['title'],'summary':a['summary'],'category':a['category']}
    for a in ALL
],ensure_ascii=False,separators=(',',':')),encoding='utf-8')
render('reading-desk.html','reading-desk/index.html',depth=1,page_type='reading-desk',title='My Reading Desk',crumbs='My Reading Desk')
render('exhibits.html','exhibits/index.html',depth=1,page_type='exhibits',title='Historical Documents & Exhibits',crumbs='Historical Exhibits',exhibits=EXHIBITS)
for exhibit in EXHIBITS:
    render('exhibit.html',f'exhibits/{exhibit["id"]}/index.html',depth=2,page_type='exhibits',title=exhibit['title'],description=exhibit['summary'],crumbs=exhibit['title'],exhibit=exhibit)
render('compare.html','compare/index.html',depth=1,page_type='compare',title='Character Comparison Dossiers',description='Examine documented lives side by side: public identity, institutions, turning points, and legacies, with sources for every claim.',crumbs='Character Comparisons',comparison_data=COMPARISON_DATA,comparison_pair=None)
for pair in COMPARISON_PRESETS:
    render('compare.html',f'compare/pairs/{pair["id"]}/index.html',depth=3,page_type='compare',title=pair['title']+' · Character Dossiers',description=pair['description'],crumbs=pair['title'],comparison_data=COMPARISON_DATA,comparison_pair=pair)
render('connections.html','connections/index.html',depth=1,page_type='connections',title='People & Connections',crumbs='People & Connections',relationship_maps=RELATIONSHIP_MAPS,connection_web=CONNECTION_WEB)
for graph in RELATIONSHIP_MAPS:
    render('connection.html',f'connections/{graph["id"]}/index.html',depth=2,page_type='connections',title=graph['title'] + ' · Connections',description=graph['summary'],crumbs=graph['title'],graph=graph)
render('journeys.html','journeys/index.html',depth=1,page_type='journeys',title='Reading Journeys',crumbs='Reading Journeys',journeys=JOURNEYS)
for journey in JOURNEYS:
    render('journey.html',f'journeys/{journey["id"]}/index.html',depth=2,page_type='journeys',title=journey['title'],description=journey['summary'],crumbs=journey['title'],journey=journey)
render('timeline.html','chronicle/index.html',depth=1,page_type='timeline',title='The Living Chronicle',crumbs='The Living Chronicle',events=EVENTS,periods=PERIODS,topics=TOPICS,date_kinds=DATE_KINDS,journeys=JOURNEYS)
render('gazette.html','gazette/index.html',depth=1,page_type='gazette',title='The Royal Gazette',crumbs='The Royal Gazette',description='Dated scholarly dispatches from the Royal Archives.',gazette_issues=GAZETTE_ISSUES)
for issue in GAZETTE_ISSUES:
    render('gazette-issue.html',f'gazette/{issue["id"]}/index.html',depth=2,page_type='gazette',title=issue['title']+' · The Royal Gazette',description=issue['intro'],crumbs=issue['title'],gazette_issue=issue)

render('map.html','map/index.html',depth=1,page_type='map',title='The Cartographer\'s Table',crumbs='Interactive map',map=MAP,map_data=MAP_DATA,atlas_history_events=ATLAS_HISTORY_EVENTS,atlas_history_periods=PERIODS,atlas_history_count=len(ATLAS_HISTORY_LINKS))
render('gallery.html','gallery/index.html',depth=1,page_type='gallery',title='Illustration Gallery',crumbs='Illustration Gallery',gallery_items=GALLERY_ITEMS,gallery_collections=GALLERY_COLLECTIONS,active_gallery_collection=None,gallery_data=GALLERY_ITEMS)
for wing in GALLERY_COLLECTIONS:
    member_items = [item for item in GALLERY_ITEMS if item['collection'] == wing['id']]
    render('gallery.html',f'gallery/{wing["id"]}/index.html',depth=2,page_type='gallery',title=wing['title'] + ' · Illustration Gallery',crumbs=wing['title'],description=wing['description'],gallery_items=member_items,gallery_collections=GALLERY_COLLECTIONS,active_gallery_collection=wing,gallery_data=member_items)
# All search data is intentionally public-facing. Aliases refer only to published
# articles; consolidated records link directly to their actual parent sections.
SEARCH_ALIASES = (yaml.safe_load((ROOT / 'data' / 'search-aliases.yml').read_text(encoding='utf-8')) or {}).get('aliases', {})
if not isinstance(SEARCH_ALIASES, dict):
    raise ValueError('Search aliases must be a slug-to-list mapping')
for slug, aliases in SEARCH_ALIASES.items():
    if slug not in BY_SLUG or not isinstance(aliases, list) or not all(isinstance(a, str) and a.strip() for a in aliases):
        raise ValueError(f'Invalid public search aliases for {slug}')
index = []
for a in ALL:
    # Keep existing full-public-text search, while providing weighted titles,
    # subtitles and alternative names for much more precise results.
    index.append({
        'type': 'article', 'slug': a['slug'], 'fragment': '',
        'title': a['title'], 'subtitle': a.get('subtitle') or '',
        'category': a['category'], 'entry': a.get('entry') or '',
        'summary': a['summary'], 'featured': bool(a.get('featured')),
        'aliases': SEARCH_ALIASES.get(a['slug'], []),
        'body': a['body']
    })
for old_slug, rule in MERGES.items():
    parent = BY_SLUG[rule['parent']]
    section = next((h for h in parent['headings'] if h['id'] == rule['section']), None)
    if not section:
        raise ValueError(f'Retired search target missing section: {old_slug}')
    # Use a summary from the public parent article, never deleted or private text.
    index.append({
        'type': 'section', 'slug': parent['slug'], 'fragment': rule['section'],
        'title': str(rule['title']), 'subtitle': 'Section within ' + parent['title'],
        'category': parent['category'], 'entry': 'SECTION',
        'summary': 'Open this section in ' + parent['title'] + '.',
        'featured': False, 'aliases': [old_slug.replace('-', ' '), section['text']],
        'body': ''
    })
(PUBLIC/'search-index.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
SITEMAP_RESULT = write_sitemap(PUBLIC, SITE_URL)
QUALITY_RESULT = audit_site(PUBLIC, SITE_URL)
print(f'Archive index: {SITEMAP_RESULT["indexable_pages"]} canonical pages; '
      f'{SITEMAP_RESULT["redirects_excluded"]} retired redirects excluded. '
      f'Checked {QUALITY_RESULT["local_references_checked"]} local references; '
      f'{QUALITY_RESULT["issue_count"]} issues.')
print(f'Built {len(ALL)} public articles, {len(CATEGORIES)} collections, {len(GALLERY_ITEMS)} curated illustrations, a timeline and search index in {PUBLIC}')