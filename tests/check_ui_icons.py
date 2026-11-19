"""Guard public UI icons against colorful iOS emoji substitutions.

This checks presentation glyphs in templates and UI data/scripts only.
Narrative Markdown and Keeper material are intentionally out of scope.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UI_FILES = (
    *sorted((ROOT / "templates").glob("*.html")),
    ROOT / "assets/map.js",
    ROOT / "assets/gallery.js",
    ROOT / "assets/reading-desk.js",
    ROOT / "data/collection-navigation.yml",
    ROOT / "data/relationship-maps.yml",
    ROOT / "data/people-navigation.yml",
)
assert UI_FILES, "No public UI sources found"
arrow_count = 0
swords_count = 0
for path in UI_FILES:
    source = path.read_text(encoding="utf-8")
    bare_arrow = source.count("\u2197") - source.count("\u2197\ufe0e")
    bare_swords = source.count("\u2694") - source.count("\u2694\ufe0e")
    assert bare_arrow == 0, f"{path.relative_to(ROOT)} has {bare_arrow} emoji-prone arrows"
    assert bare_swords == 0, f"{path.relative_to(ROOT)} has {bare_swords} emoji-prone swords"
    arrow_count += source.count("\u2197\ufe0e")
    swords_count += source.count("\u2694\ufe0e")
assert arrow_count >= 70, f"Expected site-wide monochrome arrows, found {arrow_count}"
assert swords_count >= 4, f"Expected site-wide monochrome swords, found {swords_count}"
welcome = (ROOT / "templates/welcome.html").read_text(encoding="utf-8")
assert 'welcome-swords-icon' in welcome and 'welcome-link-arrow' in welcome, "Keep Start Here vectors intact"
assert "\u231b\ufe0e" in (ROOT / "data/welcome-routes.yml").read_text(encoding="utf-8"), "Keep the text-style hourglass"
print(f"Phase 10 icon presentation passed: {arrow_count} arrows, {swords_count} swords.")
