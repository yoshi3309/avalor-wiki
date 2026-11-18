"""Blackwater Bay Stage 3: public narrative, continuity, navigation and aftermath."""
from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
def source(slug):
    return (ROOT/"content"/"articles"/f"{slug}.md").read_text(encoding="utf-8")

mission=source("escape-from-blackwater-bay")
assert "category: History & Chronicles" in mission
assert "entry: HIS.036" in mission
assert "2020 AF" in mission and "twenty-four hours" in mission
assert "not a newly founded order" in mission
assert all(name in mission for name in (
    "Silas Dreadmore","Naeris Thorne","MG the Fixer","Notfred","Ambrose Burntwood",
    "Corvin Voss","Skrik","Stavros","Jack of Stanleyville"))
assert "Pier Seven" in mission and "the Teeth" in mission
assert all(term in mission for term in ("Blood Touch","The living Anchor","Naeris volunteered","Corvin volunteered"))
assert "survived" in mission and "physical scars" in mission
assert "artifact" in mission.lower() and "discovered missing" in mission.lower()
assert "Gladios" in mission and "escaped on Shadowthorn" in mission
assert "Port Orange" in mission and "Burntwood Tavern" in mission
assert "some sailors had died" in mission.lower()
assert "later" in mission.lower() and "seven" in mission.lower()
assert all(name in mission for name in ("### Silas","### Naeris","### MG","### Notfred","### Ambrose","### Corvin","### Skrik"))
for banned in ("Strain 4","Pier Twelve","Dock Twelve","Sea Serpents","literal time travel",
               "Fo’Gurn","Fo'Gurn","Auren","gods were being killed"):
    assert banned not in mission, f"Keeper-only or superseded phrasing: {banned}"
assert "[[Escape from Blackwater Bay]]" in source("blackwater-bay")
for slug in ("silas-dreadmore","naeris-thorne","mg-the-fixer","notfred","ambrose-burntwood",
             "lavitz-shawe","age-of-ascendancy","black-diamond"):
    assert "escape-from-blackwater-bay" in source(slug), slug
nav=yaml.safe_load((ROOT/"data/collection-navigation.yml").read_text(encoding="utf-8"))
chronicle_groups=nav["history-chronicles"]["groups"]
assert any("escape-from-blackwater-bay" in (g.get("articles") or []) for g in chronicle_groups)
events=yaml.safe_load((ROOT/"data/living-chronicle.yml").read_text(encoding="utf-8"))["events"]
blackwater=[e for e in events if e.get("id")=="blackwater-bay-affair"]
assert len(blackwater)==1
assert blackwater[0]["article"]=="escape-from-blackwater-bay"
assert blackwater[0]["date"]=="2020 AF"
journeys=yaml.safe_load((ROOT/"data/reading-journeys.yml").read_text(encoding="utf-8"))["journeys"]
route=[j for j in journeys if j["id"]=="blackwater-escape"]
assert len(route)==1
steps=route[0]["steps"]
assert [s["article"] for s in steps]==[
    "age-of-ascendancy","lavitz-shawe","blackwater-bay","black-diamond",
    "escape-from-blackwater-bay","notfred","naeris-thorne","ambrose-burntwood"]
assert len(steps[4]["deeper_reading"])==5
for item in steps:
    assert (ROOT/"content"/"articles"/(item["article"]+".md")).is_file()
assert "INT-2026-11-14-07" in (ROOT/"docs/CANON_PUBLIC_RELEASE_LOG.md").read_text(encoding="utf-8")
print("Blackwater Stage 3: coherent public chronicle, existing artwork intact, journey and biographies connected.")
