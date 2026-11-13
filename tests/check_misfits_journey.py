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
    "the-stalker",
    "hydra-temple-disaster",
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
assert "article-explore-deeper" in final_html
assert "Continue: The Queen Returns" in final_html

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
assert "Captain Funkin returned her body safely to Renada" in source("kel-maris"), (
    "Funkin returned Kel'Maris's body before his later death at the Hydra temple."
)
assert "Captain Funkin returned her body" in source("kel-maris")
assert "Captain Funkin" in source("the-stalker")
assert "Kel'Maris could not be among the survivors" in source("hydra-temple-disaster")
assert "Anna escaped" in source("hydra-temple-disaster")
assert "Kel'Maris" in source("the-stalker")
assert "Kel'Maris" in source("the-first-commission")
assert "Kel'Maris" in source("golgoroth-second-commission")
assert "Kel'Maris" in source("lavitz-shawe")
assert "Lion's Shadow" in source("king-gradvum-frozenroar")
assert "Zauks" in source("zauks")
assert "Amara" in source("zauks")
assert "cocoons" in source("zauks")
assert "Kel'Maris" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")
assert "KEL-001" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")
assert "Status: RESOLVED" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

assert "Master of Broken Wills" in source("jaaris")
assert "Jaaris had previously led the hostile fey who murdered Tristan and Kristofer" in source("cid-the-blood-king")
assert "Jaaris" in source("svendyal-shadowwhisper")
assert "Fo'Gurn chose to protect Lavitz" in source("jaaris")
assert "The earlier necromancer" in source("jaaris")

# Addendum 003 identities retained within two compact character indexes.
minor_heroes = source("minor-heroes-and-allies")
minor_villains = source("minor-villains-and-adversaries")
for slug, hub in (
    ("kurt-reyginald", "minor-heroes-and-allies"),
    ("captain-funkin", "minor-heroes-and-allies"),
    ("inspector-sihnion", "minor-heroes-and-allies"),
    ("ros-furband", "minor-villains-and-adversaries"),
    ("karina", "minor-villains-and-adversaries"),
    ("black-agnes-mudwallow", "minor-villains-and-adversaries"),
):
    assert not (ROOT / "content" / "articles" / f"{slug}.md").exists(), slug
    merges = yaml.safe_load((ROOT / "data" / "article-merges.yml").read_text(encoding="utf-8"))["retired"]
    assert merges[slug]["parent"] == hub
    assert merges[slug]["section"] == slug
    redirect = ROOT / "_site" / "articles" / slug / "index.html"
    assert redirect.is_file()
    assert f"articles/{hub}/#{slug}" in redirect.read_text(encoding="utf-8")
    destination = ROOT / "_site" / "articles" / hub / "index.html"
    assert f'id="{slug}"' in destination.read_text(encoding="utf-8")
for heading in ("Kurt Reyginald", "Captain Funkin", "Inspector Sihnion",
                "Quill", "Mira", "Nimbus", "Nadja Akayrn"):
    assert f"## {heading}" in minor_heroes
for heading in ("Karina", "Black Agnes Mudwallow", "Ros Furband"):
    assert f"## {heading}" in minor_villains
assert "ice-blue crystal" in minor_villains
assert "Tel'Lora" in minor_villains
assert "Misfits defeated and killed Black Agnes" in minor_villains
assert "Jinlin was defeated in a real confrontation" in source("minor-villains-and-adversaries")
assert "Captain Funkin" in minor_heroes
assert "Stalker" in minor_heroes
assert "Hydra temple" in minor_heroes
assert "Kel'Maris" in minor_heroes
assert "1946 to 1982 AF" in source("minor-characters")
# Deeper-reading links retain direct anchors to individuals inside the indexes.
journey_html = (ROOT / "_site" / "journeys" / "rise-of-the-misfits" / "index.html").read_text(encoding="utf-8")
assert "articles/minor-heroes-and-allies/#captain-funkin" in journey_html
assert "articles/minor-heroes-and-allies/#inspector-sihnion" in journey_html
assert "articles/minor-villains-and-adversaries/#karina" in journey_html
assert "articles/minor-villains-and-adversaries/#jinlin-vechon" in journey_html
assert "Noke" in source("noki-the-sheep")
assert "Den Mother" in source("noki-the-sheep")
assert "Amara" in source("zauks")
assert "cocoons" in source("zauks")
assert "Addendum 003" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

# Addendum 008: short neutral/villain collections and the first new hunter.
for slug, parent in (
    ("jinlin-vechon", "minor-villains-and-adversaries"),
    ("king-gerran-frozenroar", "minor-characters"),
):
    assert not (ROOT / "content" / "articles" / (slug + ".md")).exists(), slug
    merges = yaml.safe_load((ROOT / "data" / "article-merges.yml").read_text(encoding="utf-8"))["retired"]
    assert merges[slug]["parent"] == parent
    assert merges[slug]["section"] == slug
    redirect = ROOT / "_site" / "articles" / slug / "index.html"
    assert redirect.is_file()
    assert f"articles/{parent}/#{slug}" in redirect.read_text(encoding="utf-8")
    target = ROOT / "_site" / "articles" / parent / "index.html"
    assert f'id="{slug}"' in target.read_text(encoding="utf-8")
assert "## Jinlin Vechon" in source("minor-villains-and-adversaries")
assert "## King Gerran Frozenroar" in source("minor-characters")
assert "## Gomo" in source("minor-characters")
assert "## Silver of Moonlight" in source("minor-characters")
assert "title: Lowkee Nicklebane" in source("lowkee")
assert "title: Faelynn Naïlo" in source("faelynn")
heyden=source("heyden-of-the-goldenfoot")
assert "title: Heyden of the Goldenfoot" in heyden
for detail in ("Allosaurus", "Great Elk", "Gomo", "Silver of Moonlight",
               "Shadow", "Jeothor", "Verbos", "Seals", "Revenant Double-Bladed Scimitar",
               "Hunters Guild coin"):
    assert detail in heyden, detail
journey_08 = (ROOT / "_site" / "journeys" / "rise-of-the-misfits" / "index.html").read_text(encoding="utf-8")
assert "articles/minor-villains-and-adversaries/#jinlin-vechon" in journey_08
assert "Addendum 008" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

# Addendum 005: keep retrospective truths aligned across reference articles.
assert "Fo'Gurn chose to protect Lavitz" in source("death-souls-and-the-afterlife")
assert "his final rest" in source("death-souls-and-the-afterlife")
assert "roughly twenty years afterward" in source("death-souls-and-the-afterlife")
assert "## Two interventions in the Misfits' campaign" in source("samuel-the-devoted")
assert "At the ruined temple near Stanleyville" in source("samuel-the-devoted")
assert "Later, during the final struggle in the Shadowfell" in source("samuel-the-devoted")
assert "## The years not yet written" in source("age-of-ascendancy")
assert "Royal Commission of Historical Inquiry" in source("age-of-ascendancy")
assert "Black Diamond" not in source("age-of-ascendancy")
assert "Kel'Maris" in source("the-aegis")
assert "## The farewell to the Lion's Shadow" in source("great-cathedral")
assert "three days" in source("great-cathedral")
assert "ashes were scattered" in source("geography-of-avalor")
assert "## Ilyanamel" in source("lesser-settlements-of-avalor")
assert "exact location" in source("lesser-settlements-of-avalor")
assert "Status:" in (ROOT / "docs" / "CHARACTER_FATE_AND_DEATH_DATE_REVIEW_2026-11.md").read_text(encoding="utf-8")
assert "Addendum 005" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

# Addendum 006: approximate original-campaign death chronology and Keeper's gap ruling.
chronicle = yaml.safe_load((ROOT / "data" / "living-chronicle.yml").read_text(encoding="utf-8"))
events = chronicle["events"]
event_by_id = {event["id"]: event for event in events}
ordered_death_ids = [
    "stanleyville-deaths",
    "hydra-temple-deaths",
    "jaznaar-final-rest",
    "zauks-end",
    "misfits-victory",
]
event_ids = [event["id"] for event in events]
assert [event_ids.index(i) for i in ordered_death_ids] == sorted(event_ids.index(i) for i in ordered_death_ids)
for event_id in ordered_death_ids:
    event = event_by_id[event_id]
    assert event["date_kind"] == "exact", event_id
    assert event["date"] == "2000 AF", event_id
assert "Jinlin" in event_by_id["zauks-end"]["text"]
assert "Jaaris" in event_by_id["misfits-victory"]["text"]
assert "ultimate death is unconfirmed" in event_by_id["misfits-victory"]["text"]
for slug in (
    "kel-maris", "jack-of-stanleyville", "fo-gurn", "jaaris",
    "zauks", "jaznaar", "the-stalker", "shadowfell-confrontation",
):
    assert "2000 AF" in source(slug), slug
assert "2000 AF" in source("minor-heroes-and-allies")
assert "2000 AF" in source("minor-villains-and-adversaries")
assert "His ultimate death has not been confirmed" in source("minor-villains-and-adversaries"), "Defeat is not a death date."
register = (ROOT / "docs" / "CHARACTER_FATE_AND_DEATH_DATE_REVIEW_2026-11.md").read_text(encoding="utf-8")
assert "no established named cast member died during the twenty-year interval" in register.lower()
assert "Tristan and Kristofer" in register
assert "precise year" in register or "exact year" in register
assert "Addendum 006" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

# Addendum 007: unbroken lineage, approval of campaign calendar and mixed royal endings.
assert event_by_id["ascendancy"]["date"] == "2020 AF"
assert event_by_id["ascendancy"]["date_kind"] == "exact"
assert "1997 AF" in source("svendyal-shadowwhisper")
assert "1997 AF" in source("jaaris")
assert "2000 AF" in source("the-misfits")
royal = source("house-frozenroar")
assert "All belong to the Frozenroar bloodline" in royal
assert "| 34 | Gradvum Frozenroar | 1983–present |" in royal
assert "killed defending coastal shipping against pirates" in royal
assert "Sered" in royal and "frontier skirmish" in royal
assert "Brannic" in royal and "wilderness expedition" in royal
assert "298 AF; died peacefully, 312 AF" in royal
assert "1511 AF; died, 1528 AF" in royal
assert "1982 AF" in source("minor-characters")
assert "father of Benedikt" in source("rynhold-frozenroar") or "Son Benedikt" in source("rynhold-frozenroar")
fate_register = (ROOT / "docs" / "CHARACTER_FATE_AND_DEATH_DATE_REVIEW_2026-11.md").read_text(encoding="utf-8")
assert "**2000 AF** is now the **confirmed calendar year**" in fate_register
assert "1997 AF" in fate_register
assert "2020 AF" in fate_register
assert "Addendum 007" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

# Editorial cross-feature review (November 13, 2026).
for person in ("gomo", "silver-of-moonlight"):
    merges = yaml.safe_load((ROOT / "data" / "article-merges.yml").read_text(encoding="utf-8"))["retired"]
    assert merges[person]["parent"] == "minor-characters", person
    redirect = (ROOT / "_site" / "articles" / person / "index.html").read_text(encoding="utf-8")
    assert "articles/minor-characters/#" + person in redirect
traveler_places = source("distant-lands-of-the-hunter")
for heading in ("## The Kingdom of Labos","## Chult","## Weyland Forest",
                "## Valiant and the Woodland Elves","## The Wood of the Fey"):
    assert heading in traveler_places, heading
heyden_dossier = source("heyden-of-the-goldenfoot")
assert "## The prince who learned to stay" in heyden_dossier
assert "highlight_sections:" in heyden_dossier
assert "callouts:" in heyden_dossier
assert "not a confirmed portrait of Heyden" in heyden_dossier
assert "The Hunters Guild" in source("hunters-guild")
assert "changes of dynasty" not in source("kingdom-of-avalor")
assert "unbroken Frozenroar royal bloodline" in source("kingdom-of-avalor")
assert "The **Cartographer's Table** now marks" in source("geography-of-avalor")
assert "creator-approved lore" not in source("age-of-ascendancy")
for illustrated in ("faelynn","jaaris","cid-the-blood-king","amara","fo-gurn","jaznaar","rynhold-frozenroar"):
    assert "callouts:" in source(illustrated), illustrated
    assert "highlight_sections:" in source(illustrated), illustrated
atlas_data = (ROOT / "data" / "avalor-map.yml").read_text(encoding="utf-8").lower()
for unknown_position in ("weyland forest", "chult", "valiant"):
    assert unknown_position not in atlas_data, unknown_position
assert "Addendum 009" in (ROOT / "docs" / "PENDING_MASTER_CANON_ADDENDA.md").read_text(encoding="utf-8")

print("Twenty-year retrospective revelations are public; future/open mysteries remain protected.")

print(f"Misfits event reading journey passed: {len(steps)} historical chapters, {extra_count} deeper records.")

# Phase 6: source-led chronology and historical voice.
cid = source("cid-the-blood-king")
misfits = source("the-misfits")
shadowfell = source("shadowfell-confrontation")
assert cid.index("## The suffering at Stanleyville") < cid.index("## Prisoners at the ruined temple")
assert "Captain Funkin brought her body home to Renada" in cid
assert "Captain Funkin" in cid and "Inspector Sihnion" in cid
assert "Cid was removed from the battle, not confirmed dead" in cid
assert "Jinlin Vechon" in cid and "real defeat" in cid
assert "broke Jaaris's hold before the necromancer died" in cid
assert "Lowkee" in cid and "Erevan Ilesere" in cid
assert "The Emerald's seal and Cid's removal were distinct events" in cid
assert misfits.index("## III. Stanleyville and the Stalker") < misfits.index("## IV. The hydra and the missing companion")
assert "player-character" not in misfits.lower()
assert "the sealing of the Emerald and the removal of Cid were distinct events" in misfits
assert "broke Jaaris's control while the necromancer was still alive" in misfits
assert "The Misfits defeated Jinlin in a real battle" in shadowfell
assert "He chose to protect Lavitz" in shadowfell and "before** Jaaris was killed" in shadowfell
print("Phase 6 canon reconciliation passed.")
