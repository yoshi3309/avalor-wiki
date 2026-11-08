"""Lightweight public-archive integrity checks. No Keeper files are loaded."""
from pathlib import Path
import re
import sys
import unicodedata
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from public_references import public_sources, INTERNAL_SOURCE

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"

def slugify(value):
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")

files = sorted(ARTICLES.glob("*.md"))
if not files:
    sys.exit("No wiki articles found")

entries = {}
aliases = {}
problems = []
for path in files:
    raw = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", raw, re.S)
    if not match:
        problems.append(f"{path.name}: no YAML front matter")
        continue
    # Pages CMS rejects a multi-line quoted YAML scalar even if PyYAML accepts
    # the folded representation. Require quoted values to close on their line
    # or use a YAML block scalar (| or >) for multi-line facts.
    for lineno, line in enumerate(match.group(1).splitlines(), 2):
        key_value = line.split(":", 1)
        value = key_value[1].lstrip() if len(key_value) == 2 else ""
        if value.startswith(("'", '"')) and not value.rstrip().endswith(value[0]):
            problems.append(f"{path.name}:{lineno}: quoted frontmatter value spans lines; use YAML block scalar")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        problems.append(f"{path.name}: invalid YAML frontmatter: {e}")
        continue
    if not isinstance(meta, dict) or not meta.get("title"):
        problems.append(f"{path.name}: missing title")
        continue
    public_note = public_sources(meta.get("source"))
    if INTERNAL_SOURCE.search(public_note):
        problems.append(f"{path.name}: internal editorial source exposed to public")
    if not public_note:
        problems.append(f"{path.name}: public source display empty")
    entries[path.stem] = (meta, match.group(2))
    aliases[slugify(str(meta["title"]))] = path.stem
    aliases[slugify(path.stem)] = path.stem

# Catalogue identifiers must be unique and every wiki-link must resolve
# through the exact alias rules used by build.py.
aliases.update({"avalor": "kingdom-of-avalor", "misfits": "the-misfits",
                "tel-lora": "tellora-ebbenflow", "heavens-heart": "heavens-heart",
                "royal-commission-of-historical-inquiry": "royal-commission-historical-inquiry"})
def heading_ids(body):
    """Build the same h2 fragment IDs as build.py for section links."""
    ids = set()
    used = set()
    for heading in re.findall(r"^##\s+(.+)$", body, flags=re.M):
        plain = re.sub(r"<[^>]*>", "", heading)
        plain = re.sub(r"[*_`]", "", plain)
        tag = slugify(plain) or "heading"
        anchor = tag
        n = 2
        while anchor in used:
            anchor = f"{tag}-{n}"
            n += 1
        used.add(anchor)
        ids.add(anchor)
    return ids

MERGES = (yaml.safe_load((ROOT/'data'/'article-merges.yml').read_text(encoding='utf-8')) or {}).get('retired',{})
for old, rule in MERGES.items():
    if old in entries:
        problems.append(f"{old}: retired source still exists")
    parent = rule['parent']
    if parent not in entries:
        problems.append(f"{old}: missing merged parent {parent}")
    elif rule['section'] not in heading_ids(entries[parent][1]):
        problems.append(f"{old}: missing merged section {parent}#{rule['section']}")
    for text_alias in (old, rule['title']):
        key = slugify(text_alias)
        if key in aliases and aliases[key] != old:
            problems.append(f"{old}: redirect alias conflicts with existing title {text_alias}")
        aliases[key] = old

ids = {}
for slug, (meta, body) in entries.items():
    archive_id = str(meta.get("entry") or "").strip()
    if not archive_id:
        problems.append(f"{slug}: missing entry number")
    elif archive_id in ids:
        problems.append(f"{slug}: duplicate entry number {archive_id} (also {ids[archive_id]})")
    else:
        ids[archive_id] = slug
    for match in re.finditer(r"\[\[([^\]]+)\]\]", body):
        target = match.group(1).split("|", 1)[0]
        target_title, has_fragment, fragment = target.partition("#")
        resolved = aliases.get(slugify(target_title))
        if not resolved:
            problems.append(f"{slug}: broken wiki-link {target}")
        elif resolved in MERGES:
            if not MERGES[resolved]['parent'] in entries:
                problems.append(f"{slug}: retired link {target} has missing parent")
        elif has_fragment and slugify(fragment) not in heading_ids(entries[resolved][1]):
            problems.append(f"{slug}: broken section wiki-link {target}")

for slug, (meta, body) in entries.items():
    related = str(meta.get("related") or "")
    for target in (s.strip() for s in related.split(",") if s.strip()):
        if target not in entries and target not in MERGES:
            problems.append(f"{slug}: missing related article '{target}'")

# Latest creator correction (November 2026): Samuel is a Monadic Deva.
# Never confuse him with the distinct aasimar Cal'el or the female deva Astronoph.
samuel = entries.get("samuel-the-devoted")
if not samuel:
    problems.append("Samuel biography is missing")
else:
    meta, body = samuel
    facts = str(meta.get("facts") or "")
    identity = str(meta.get("summary") or "") + facts + body
    if not re.search(r"monadic\s+deva", identity, re.I):
        problems.append("Samuel biography must identify him as a Monadic Deva")
    if re.search(r"\bSamuel\b\s*(?:,|is|was|:)?\s*(?:an?\s+)?aasimar\b|\baasimar\s+Samuel\b", identity, re.I):
        problems.append("Samuel biography incorrectly identifies him as aasimar")

for slug, (meta, body) in entries.items():
    if slug == "samuel-the-devoted":
        continue
    for line_number, line in enumerate(body.splitlines(), 1):
        if re.search(r"\bSamuel\b\s*(?:,|is|was|:)?\s*(?:an?\s+)?aasimar\b|\baasimar\s+Samuel\b", line, re.I):
            problems.append(f"{slug}:{line_number}: obsolete aasimar identification for Samuel")

# Curated journeys must only reference existing, public archive articles.
routes = yaml.safe_load((ROOT / "data" / "reading-journeys.yml").read_text(encoding="utf-8")) or {}
journey_ids = set()
for journey in routes.get("journeys", []):
    journey_id = str(journey.get("id") or "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", journey_id) or journey_id in journey_ids:
        problems.append(f"Invalid or duplicate reading journey id: {journey_id}")
    journey_ids.add(journey_id)
    if any(not journey.get(k) for k in ("title", "subtitle", "overline", "summary", "editorial_note", "era")):
        problems.append(f"{journey_id}: incomplete journey metadata")
    steps = journey.get("steps") or []
    if len(steps) < 3:
        problems.append(f"{journey_id}: fewer than three records")
    used = set()
    for step in steps:
        slug = str(step.get("article") or "")
        if slug not in entries or slug in used:
            problems.append(f"{journey_id}: missing or repeated public article {slug}")
        used.add(slug)
        if not step.get("label") or not step.get("introduction"):
            problems.append(f"{journey_id}: incomplete step for {slug}")


# The relationship atlas is an editorial index of public records. Reject missing
# articles, broken links, and duplicated or invented-looking structural references.
atlas = yaml.safe_load((ROOT / "data" / "relationship-maps.yml").read_text(encoding="utf-8")) or {}
relationship_ids = set()
allowed_kinds = {"group", "person", "royal"}
allowed_types = {"fellowship", "later", "companion", "prior-friendship", "parent", "consort", "sibling"}
for relationship in atlas.get("maps", []):
    ident = str(relationship.get("id") or "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident) or ident in relationship_ids:
        problems.append(f"Relationship map has invalid or duplicate id {ident}")
    relationship_ids.add(ident)
    if relationship.get("related_article") not in entries:
        problems.append(f"{ident}: missing main source article")
    if any(not relationship.get(k) for k in ("title", "subtitle", "summary", "note", "icon")):
        problems.append(f"{ident}: incomplete map metadata")
    node_ids = set()
    for node in relationship.get("nodes", []):
        node_id = str(node.get("id") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", node_id) or node_id in node_ids:
            problems.append(f"{ident}: invalid or duplicate node id {node_id}")
        node_ids.add(node_id)
        if node.get("article") and node["article"] not in entries:
            problems.append(f"{ident}: node {node_id} links to nonpublic article")
        if node.get("kind") not in allowed_kinds or not node.get("label") or not node.get("detail"):
            problems.append(f"{ident}: missing data for {node_id}")
        if not 6 <= float(node.get("x", -1)) <= 94 or not 6 <= float(node.get("y", -1)) <= 94:
            problems.append(f"{ident}: node coordinates invalid for {node_id}")
    seen_links = set()
    for edge in relationship.get("edges", []):
        a, b = edge.get("from"), edge.get("to")
        pair = tuple(sorted([str(a), str(b)]))
        if a not in node_ids or b not in node_ids or a == b or pair in seen_links:
            problems.append(f"{ident}: missing, repeated or invalid edge {a}/{b}")
        seen_links.add(pair)
        if edge.get("type") not in allowed_types or not edge.get("label"):
            problems.append(f"{ident}: incomplete relationship for {a}/{b}")



# The chronology uses stable public record slugs and preserves confidence labels.
chronicle = yaml.safe_load((ROOT / "data" / "living-chronicle.yml").read_text(encoding="utf-8")) or {}
period_ids = {p["id"] for p in chronicle.get("periods", [])}
topic_ids = {p["id"] for p in chronicle.get("topics", [])}
kind_ids = {p["id"] for p in chronicle.get("date_kinds", [])}
event_ids = set()
if not period_ids or not topic_ids or not kind_ids:
    problems.append("Living Chronicle: missing filters or date classifications")
for event in chronicle.get("events", []):
    event_id = str(event.get("id") or "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", event_id) or event_id in event_ids:
        problems.append(f"Living Chronicle: invalid or repeated event id {event_id}")
    event_ids.add(event_id)
    if event.get("article") not in entries:
        problems.append(f"Living Chronicle: event {event_id} has missing public article")
    if event.get("period") not in period_ids or event.get("topic") not in topic_ids or event.get("date_kind") not in kind_ids:
        problems.append(f"Living Chronicle: event {event_id} has unknown classification")
    if any(not event.get(k) for k in ("date", "era", "title", "text")):
        problems.append(f"Living Chronicle: incomplete public entry {event_id}")
if len(event_ids) != 18:
    problems.append(f"Living Chronicle: expected all 18 previously published events, found {len(event_ids)}")


if problems:
    print("PUBLIC CANON CHECK FAILED:")
    for problem in problems:
        print(" - " + problem)
    sys.exit(1)
print(f"Public canon checks passed: {len(entries)} article front matters, related slugs, entry numbers, wiki links, Samuel's Monadic Deva nature.")
