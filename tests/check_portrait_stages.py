"""Validate optional character stage selectors and compact People & Legends navigation."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parent.parent
config = yaml.safe_load((ROOT / "data/people-navigation.yml").read_text(encoding="utf-8"))
groups = {g["id"]: g for g in config["groups"]}
for removed in ("minor-neutral", "minor-heroes", "minor-villains"):
    assert removed not in groups, f"Redundant single-article story card: {removed}"
minor_slugs = {"minor-characters", "minor-heroes-and-allies", "minor-villains-and-adversaries"}
assert not any(minor_slugs.intersection(g.get("articles") or []) for g in groups.values())
for slug in minor_slugs:
    assert (ROOT / "content" / "articles" / (slug + ".md")).is_file()

builder = (ROOT / "build.py").read_text(encoding="utf-8")
template = (ROOT / "templates" / "article.html").read_text(encoding="utf-8")
base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
cms = yaml.safe_load((ROOT / ".pages.yml").read_text(encoding="utf-8"))
articles = next(c for c in cms["content"] if c["name"] == "articles")
field_names = {field["name"] for field in articles["fields"]}
assert {"image", "portrait_label", "portrait_variants"} <= field_names
variants = next(field for field in articles["fields"] if field["name"] == "portrait_variants")
assert {"label", "image", "alt", "caption"} <= {f["name"] for f in variants["fields"]}
assert "portrait_stages" in builder and "article_image_src(variant.get('image')" in builder
assert "alternate portraits require a People & Legends main portrait" in builder
assert "duplicate portrait image" in builder
assert "data-portrait-gallery" in template and "data-stage-srcset" in template
assert "aria-current" in template and "data-portrait-caption" in template
assert "portrait-stages.js" in base
script = (ROOT / "assets" / "portrait-stages.js").read_text(encoding="utf-8")
assert "preventDefault()" in script and "setAttribute('src'" in script and "aria-current" in script

# Confirm optimized portrait data only references approved local public uploads.
assert re.search(r"if not match or '\.\.' in match\.group\(1\)\.split", builder)
print("Portrait stages / compact People & Legends browse: configuration and progressive enhancement verified.")
