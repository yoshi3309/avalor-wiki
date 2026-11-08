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
        elif has_fragment and slugify(fragment) not in heading_ids(entries[resolved][1]):
            problems.append(f"{slug}: broken section wiki-link {target}")

for slug, (meta, body) in entries.items():
    related = str(meta.get("related") or "")
    for target in (s.strip() for s in related.split(",") if s.strip()):
        if target not in entries:
            problems.append(f"{slug}: missing related article '{target}'")

# User-approved correction supersedes older PDFs: Samuel is an aasimar.
samuel = entries.get("samuel-the-devoted")
if not samuel:
    problems.append("Samuel biography is missing")
else:
    meta, body = samuel
    facts = str(meta.get("facts") or "")
    if not re.search(r"aasimar", str(meta.get("summary") or "") + facts + body, re.I):
        problems.append("Samuel biography must identify him as aasimar")
    if re.search(r"monadic\s+deva", str(meta.get("summary") or "") + facts + body, re.I):
        problems.append("Samuel biography reintroduced obsolete Monadic Deva claim")

for slug, (meta, body) in entries.items():
    if slug == "samuel-the-devoted":
        continue
    for line_number, line in enumerate(body.splitlines(), 1):
        # Match explicit species assignments only, not a sentence that correctly
        # calls Astronoph a deva and then Samuel an aasimar.
        if re.search(r"\bSamuel\b\s*(?:,|is|was|:)?\s*(?:an?\s+)?(?:Monadic\s+)?Deva\b|\b(?:Monadic\s+)?Deva\s+Samuel\b", line, re.I):
            problems.append(f"{slug}:{line_number}: possibly misidentifies Samuel as deva")

if problems:
    print("PUBLIC CANON CHECK FAILED:")
    for problem in problems:
        print(" - " + problem)
    sys.exit(1)
print(f"Public canon checks passed: {len(entries)} article front matters, related slugs, entry numbers, wiki links, Samuel ancestry.")
