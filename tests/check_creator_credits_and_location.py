"""Validate Phandalin relocation, editorial art briefs, and player creator credits."""
from pathlib import Path
import re
import yaml
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"content"/"articles"
SITE=ROOT/"_site"/"articles"
def read(slug):
    s=(ART/(slug+".md")).read_text(encoding="utf-8")
    m=re.match(r"\A---\s*\n(.*?)\n---\s*\n",s,re.S)
    assert m,slug
    return yaml.safe_load(m.group(1)),s
smaller,smaller_raw=read("lesser-settlements-of-avalor")
other,other_raw=read("other-locations-of-avalor")
_,notfred=read("notfred")
assert "## Phandalin" in smaller_raw
assert "## Phandalin" not in other_raw
assert "## Vey'thal" in other_raw and "## The Tide Gate" in other_raw
assert "lesser-settlements-of-avalor#phandalin" in notfred
aliases=yaml.safe_load((ROOT/"data"/"search-aliases.yml").read_text(encoding="utf-8"))["aliases"]
assert "Phandalin" in aliases["lesser-settlements-of-avalor"]
for slug in ("other-locations-of-avalor","escape-from-blackwater-bay","minor-characters"):
    meta,_=read(slug)
    assert len(meta["image_brief"])>350,slug
    # A prompt may coexist with its final, uploaded image; this is the
    # expected Pages CMS publishing workflow, not a contradiction.
    image = meta.get("image")
    if image:
        assert isinstance(image,str) and image.startswith("/assets/uploads/"),(slug,image)
        assert (ROOT/image.lstrip("/")).is_file(),(slug,image)
credits=yaml.safe_load((ROOT/"data"/"character-creators.yml").read_text(encoding="utf-8"))
assert credits["default"]=="Gilbert Ramirez"
expected={
    "svendyal-shadowwhisper":"Danny Davis","ferris-rumbuckle":"Danny Davis","ambrose-burntwood":"Danny Davis",
    "naeris-thorne":"John Payne Rios","mandu-durbar-marg":"John Payne Rios","heureux":"John Payne Rios",
    "mg-the-fixer":"Scott Singleton","notfred":"Joey Williams",
    "tellora-ebbenflow":"Eric Astacio","malikeah":"Eric Astacio","mera-ashenfall":"Eric Astacio","silas-dreadmore":"Eric Astacio",
    "amara":"Xiomara Ramirez"}
assert credits["exceptions"]==expected
excluded={"minor-characters","minor-heroes-and-allies","minor-villains-and-adversaries"}
count=0
for path in ART.glob("*.md"):
    meta,_=read(path.stem)
    if meta["category"]!="People & Legends" or not str(meta.get("entry","")).startswith("BIO.") or path.stem in excluded:
        continue
    html=(SITE/path.stem/"index.html").read_text(encoding="utf-8")
    credit=meta.get("character_creator") or expected.get(path.stem,"Gilbert Ramirez")
    assert "Character created by" in html and credit in html,(path.stem,credit)
    count+=1
assert count>=45,count
for slug in excluded:
    html=(SITE/slug/"index.html").read_text(encoding="utf-8")
    assert "Character created by" not in html,slug
print("Editorial cleanup validated:",count,"individual creator credits, 3 briefs, relocated Phandalin.")
