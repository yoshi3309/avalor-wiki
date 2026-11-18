"""Skrik and Corvin standalone biographies: established and newly approved continuity."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def article(s):
    return (ROOT/"content"/"articles"/(s+".md")).read_text(encoding="utf8")
skrik=article("skrik")
corvin=article("corvin-voss")
for article_text,entry in ((skrik,"BIO.071"),(corvin,"BIO.072")):
    assert "category: People & Legends" in article_text
    assert "entry: "+entry in article_text
    assert len(article_text.split())>1000
assert "Tide-Touched" in skrik and "Tidecaller" in skrik
assert "Tel'Lora" in skrik and "resonance" in skrik.lower() and "continued to study" in skrik
assert "sea dragon" in skrik and "not" in skrik
assert "Skrik" in article("clans-and-communities-of-avalor")
assert "33 years in 2020 AF" in corvin
assert "2008 AF" in corvin and "Ros Furband" in corvin and "Seb" in corvin
assert "have not been established" in corvin and "outlaws" in corvin
assert "Gladios" in corvin and "Naeris" in corvin and "volunteered first" in corvin
assert "black coin" in corvin.lower() and "Sven" in corvin
for forbidden in ("deity-fragment","divine fragment","Godkiller","Auren","The One Below","Dimir Operative"):
    assert forbidden not in skrik+"\n"+corvin, "Private or unapproved publication"
assert "Ros Furband" in article("minor-characters") and "2008 AF" in article("minor-characters")
assert "2008 AF" in article("minor-villains-and-adversaries")
nav=yaml.safe_load((ROOT/"data"/"people-navigation.yml").read_text(encoding="utf8"))
# Navigation schema is top-level groups, not an article index.
groups=nav.get("groups",[])
assert any({"skrik","corvin-voss"}.issubset(set(g.get("articles",[]))) for g in groups)
journeys=yaml.safe_load((ROOT/"data"/"reading-journeys.yml").read_text(encoding="utf8"))["journeys"]
route=next(j for j in journeys if j["id"]=="blackwater-escape")
deeper=[d["article"] for step in route["steps"] for d in step.get("deeper_reading",[])]
assert "skrik" in deeper and "corvin-voss" in deeper
assert all(len(step.get("deeper_reading",[]))<=5 for step in route["steps"])
print("Skrik and Corvin biographies, Ros-Seb precedent, public secrecy, and browse/navigation integrity verified.")
