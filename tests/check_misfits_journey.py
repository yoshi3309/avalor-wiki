"""Validate the event-driven Rise of the Misfits and optional deeper reading.

Runs after python build.py. Does not load private Keeper materials.
"""
from pathlib import Path
from html.parser import HTMLParser
import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE = yaml.safe_load((ROOT / "data" / "reading-journeys.yml").read_text(encoding="utf-8"))
journeys = {j["id"]: j for j in SOURCE["journeys"]}
route = journeys["rise-of-the-misfits"]
steps = route["steps"]

expected = [
    "moonville-manor-incident",
    "the-first-commission",
    "golgoroth-second-commission",
    "noki-sheep-incident",
    "search-for-lowkees-keeper",
    "hydra-temple-disaster",
    "the-stalker",
    "rotten-husk-liberation",
    "jaznaar-refuge-revelation",
    "tournament-of-champions",
    "ros-furband-jinlin-ordeal",
    "zauks-false-lives",
    "shadowfell-confrontation",
    "misfits-return-to-renada",
    "jaznaars-vindication",
]
actual = [s["article"] for s in steps]
assert actual == expected, f"Misfits event order changed: {actual}"
assert len(steps) == 15
assert sum(bool(s.get("act")) for s in steps) == 4
assert len(set(actual)) == len(actual)

extra_count = 0
for s in steps:
    article_path = ROOT / "content" / "articles" / (s["article"] + ".md")
    assert article_path.is_file(), f"Missing historical account {article_path}"
    front = article_path.read_text(encoding="utf-8").split("---", 2)[1]
    assert "category: History & Chronicles" in front, (
        f"Main chapter must be a historical event, not a biography: {s['article']}"
    )
    extra = s.get("deeper_reading", [])
    assert extra, f"No optional deeper reading for {s['article']}"
    assert 1 <= len(extra) <= 5
    assert s["article"] not in [e["article"] for e in extra]
    for e in extra:
        assert (ROOT / "content" / "articles" / (e["article"] + ".md")).is_file()
        assert e["note"].strip()
        extra_count += 1
assert extra_count >= 30

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = []
        self.links = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        self.classes.extend((attrs.get("class") or "").split())
        if tag == "a":
            self.links.append(attrs.get("href", ""))

page = ROOT / "_site" / "journeys" / "rise-of-the-misfits" / "index.html"
assert page.is_file()
html = page.read_text(encoding="utf-8")
scan = Scan()
scan.feed(html)
assert scan.classes.count("journey-chapter") == 15
assert scan.classes.count("journey-deeper-reading") == 15
assert scan.classes.count("journey-act-kicker") == 4
assert scan.tags.count("details") >= 15
assert "Shadowfell Confrontation" in html
assert 'CHAPTER 13' in html
assert 'Cid the Blood King' in html  # supplemental reading, not the main chapter
assert 'The Last Battle in the Shadowfell' in html
for slug in actual:
    assert any("/articles/" + slug + "/" in u for u in scan.links), (
        f"Journey does not link to main event article: {slug}"
    )
assert any("/articles/cid-the-blood-king/" in u for u in scan.links), (
    "The Blood King's biography should be available as deeper reading."
)

finale = ROOT / "_site" / "articles" / "shadowfell-confrontation" / "index.html"
assert finale.is_file()
final_html = finale.read_text(encoding="utf-8")
assert "journey-article-deeper" in final_html
assert "Next: The Queen Returns" in final_html

# Other journeys still build with their original event/biography choices and without
# automatically acquiring supplemental blocks or act headers.
other = ROOT / "_site" / "journeys" / "frozenroar-dynasty" / "index.html"
assert other.is_file()
assert 'class="journey-deeper-reading"' not in other.read_text(encoding="utf-8")

print(f"Misfits event reading journey passed: {len(steps)} historical chapters, {extra_count} deeper records.")
