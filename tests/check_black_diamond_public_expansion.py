"""Validate public-facing expansion of Esogoth and Black Diamond without Keeper revelations."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
def article(slug):
    return (ROOT / "content" / "articles" / (slug + ".md")).read_text(encoding="utf-8")

diamond = article("black-diamond")
esogoth = article("esogoth")
for s, archive_id, category in (
    (diamond, "ORG.020", "Organizations & Factions"),
    (esogoth, "BIO.070", "People & Legends"),
):
    assert "entry: " + archive_id in s
    assert "category: " + category in s
    assert "[[Escape from Blackwater Bay]]" in s or "Escape from Blackwater Bay" in s

for phrase in (
    "The three pillars of power", "Commerce: wealth and access",
    "Criminal influence: enforcement and protection",
    "Occult research: the forbidden pursuit",
    "The price of forbidden research", "A city begins to resist",
    "Corvin Voss", "Stavros", "Gladios",
):
    assert phrase in diamond, phrase

for phrase in (
    "The man who made rivals cooperate", "Pier Seven", "The cost of a failed recovery",
    "Corvin Voss", "Naeris Thorne", "Gladios",
):
    assert phrase in esogoth, phrase

# Sensitive Keeper revelations may not be committed to the public repository.
# Guard both articles, preserving genuine historical knowledge about Cid elsewhere.
for forbidden in (
    "Cid the Blood King", "restoring Cid", "restore Cid", "bringing Cid back",
    "replace Cid", "next Blood King", "Auren",
    "a conscious artifact", "artifact recognized", "artifact rejected",
    "Esogoth's intended betrayal", "Esogoth was an acolyte",
):
    assert forbidden.lower() not in (diamond + "\n" + esogoth).lower(), forbidden

assert "not conclusively broken everywhere" in diamond
assert "not definitively ended" in esogoth
assert "INT-2026-11-16-01" in (ROOT / "docs" / "CANON_PUBLIC_RELEASE_LOG.md").read_text(encoding="utf-8")
print("Esogoth and Black Diamond: public narrative, continuity, and disclosure boundary passed.")
