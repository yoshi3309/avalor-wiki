"""Validate the event-driven Rise of the Misfits and optional deeper reading.

Runs after python build.py. Does not load private Keeper materials.
"""
from pathlib import Path
from html.parser import HTMLParser
import re
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
    article_text = article_path.read_text(encoding="utf-8")
    front = article_text.split("---", 2)[1]
    narrative = article_text.split("---", 2)[2].rstrip()
    last_line = narrative.splitlines()[-1].strip()
    assert not re.match(r"^#{1,6}\s+\S", last_line), (
        f"Unfinished trailing section heading in {s['article']}: {last_line}"
    )
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
assert "Follow the main chapters in order" not in other.read_text(encoding="utf-8")
assert "Read each chapter in sequence" in other.read_text(encoding="utf-8")


# Twenty-year retrospective truths are intentionally public; absence is a regression.
def source(slug):
    return (ROOT / "content" / "articles" / (slug + ".md")).read_text(encoding="utf-8")
assert "Erevan Ilesere in disguise" in source("anna-lowkees-keeper")
assert "Vandria Gilmadrith" in source("misfits-return-to-renada")
assert "Sven gave no answer" in source("misfits-return-to-renada")
assert "temporary spiritual connection" in source("emerald-of-armanti")
assert "bar Cid" in source("emerald-of-armanti")
assert "subsequently raised his body" in source("fo-gurn")
assert "before Jaaris died" in source("fo-gurn")
assert "rest one final time" in source("fo-gurn")
assert "Blood Sickness" in source("independent-factions-of-the-misfits-era")
assert "unwanted vampirism" in source("independent-factions-of-the-misfits-era")
assert "hands" in source("shadowfell-confrontation")
assert "unknown" in source("shadowfell-confrontation")
# Completed-campaign truths stay public and Fo'Gurn's short original-campaign absence
# must not be mistaken for the separate twenty-year interval after his final rest.
assert "contested in the public record" not in source("the-misfits")
assert "not fully established for public readers" not in source("the-misfits")
assert "believed dead for years" not in source("the-misfits")
assert "## The years of mourning" not in source("fo-gurn")
assert "what the five faced together" not in source("zauks-false-lives")
assert "Jaaris later raised" in source("the-misfits")
for slug in ("shadowfell-confrontation", "emerald-of-armanti"):
    article = source(slug)
    assert "Auren's later retrieval" not in article
    assert "later Godkiller" not in article
# Stage B narrative pass: preserve chronology, public revelations, and limits of testimony.
assert "ice-blue crystal" in source("jaznaar-refuge-revelation")
assert "Karina" in source("jaznaar-refuge-revelation")
assert "temple of Bane" in source("hydra-temple-disaster")
assert "mortal vessel for divine power" in source("hydra-temple-disaster")
assert "after the Tournament of Champions" in source("hydra-temple-disaster")
assert "assumed identities" in source("tournament-of-champions")
assert "cocoons" in source("zauks-false-lives")
assert "Amara killed the mind flayer" in source("zauks-false-lives")
assert "Erevan Ilesere" not in source("search-for-lowkees-keeper"), (
    "Anna's identity should be revealed in the Renada homecoming, not at the first meeting."
)
assert "Erevan Ilesere" in source("misfits-return-to-renada")
assert "Sven gave no answer" in source("misfits-return-to-renada")
for slug in (
    "moonville-manor-incident",
    "search-for-lowkees-keeper",
    "hydra-temple-disaster",
    "jaznaar-refuge-revelation",
    "tournament-of-champions",
    "zauks-false-lives",
    "misfits-return-to-renada",
):
    body = source(slug).split("---", 2)[2]
    assert len(body.split()) >= 500, f"Stage B main account unexpectedly abbreviated: {slug}"

# New lore approved 12 November 2026: Kel'Maris and the standalone Zauks account.
assert "Kel'Maris" in source("kel-maris")
assert "Kurt Reyginald" in source("kel-maris")
assert "Kel Scythe" in source("kel-maris")
assert "Stanleyville" in source("kel-maris")
assert "Captain Funkin was able to safely bring back" not in source("kel-maris"), (
    "The conflicting claim about who recovered her body must remain in the pending addendum."
)
assert "Kel'Maris" in source("the-stalker")
assert "Kel'Maris" in source("the-first-commission")
assert "Kel'Maris" in source("golgoroth-second-commission")
assert "Kel'Maris" in source("lavitz-shawe")
assert "The Lion's Shadow" in source("king-gradvum-frozenroar")
assert "Zauks" in source("zauks")
assert "Amara" in source("zauks")
assert "cocoons" in source("zauks")
assert "Kel'Maris" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")
assert "OPEN KEL-001" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

print("Twenty-year retrospective revelations are public; future/open mysteries remain protected.")

print(f"Misfits event reading journey passed: {len(steps)} historical chapters, {extra_count} deeper records.")
