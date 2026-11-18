"""Stage 1 Blackwater foundations and Port Orange continuity."""
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
def article(slug):
    return (ROOT/"content"/"articles"/f"{slug}.md").read_text(encoding="utf-8")
blackwater=article("blackwater-bay")
ambrose=article("ambrose-burntwood")
port=article("port-orange")
for value in ["2020 AF","Black Diamond","Artifact's Rest","Pier Seven","the Teeth","merchant checkpoint"]:
    assert value.lower() in blackwater.lower(), f"Missing Blackwater foundation: {value}"
assert "approximately one day" in blackwater
assert "no formal party name" in blackwater.lower()
assert "Burntwood Tavern" not in blackwater.split("---", 2)[-1], "Wrong tavern in Blackwater Bay narrative"
assert "Blackwater Bay's Burntwood Tavern" not in ambrose
assert "Home: Port Orange" in ambrose
assert "Tavern in Port Orange" not in blackwater
assert "Lavitz came to the Burntwood Tavern in Port Orange" in ambrose
assert "## The Burntwood Tavern" in port
assert "Ambrose Burntwood" in port and "Aelianos Burntwood" in port
assert "Port Orange" in ambrose and "Blackwater Bay" in ambrose
assert "Pier Twelve" not in blackwater and "Dock Twelve" not in blackwater
assert "Sea Serpents" not in blackwater
assert "exact position" in blackwater.lower() and "not established" in blackwater.lower()
events=yaml.safe_load((ROOT/"data"/"living-chronicle.yml").read_text(encoding="utf-8"))["events"]
matches=[e for e in events if e.get("id")=="blackwater-bay-affair"]
assert len(matches)==1
event=matches[0]
assert event["date"]=="2020 AF" and event["date_kind"]=="exact"
assert event["article"]=="escape-from-blackwater-bay"
assert "approximately one day" in event["text"]
print("Blackwater Bay Stage 1: Port Orange tavern, harbor, recruitment, and 2020 AF chronology verified.")
