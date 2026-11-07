"""Lightweight public-archive integrity checks. No Keeper files are loaded."""
from pathlib import Path
import re
import sys
import unicodedata
import yaml

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
    meta = yaml.safe_load(match.group(1))
    if not isinstance(meta, dict) or not meta.get("title"):
        problems.append(f"{path.name}: missing title")
        continue
    entries[path.stem] = (meta, match.group(2))
    aliases[slugify(str(meta["title"]))] = path.stem
    aliases[slugify(path.stem)] = path.stem

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
        if re.search(r"\bSamuel\b.{0,115}\b(?:Monadic\s+)?Deva\b|\b(?:Monadic\s+)?Deva\b.{0,115}\bSamuel\b", line, re.I):
            problems.append(f"{slug}:{line_number}: possibly misidentifies Samuel as deva")

if problems:
    print("PUBLIC CANON CHECK FAILED:")
    for problem in problems:
        print(" - " + problem)
    sys.exit(1)
print(f"Public canon checks passed: {len(entries)} article front matters, related slugs, Samuel ancestry.")
