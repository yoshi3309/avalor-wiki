import re

INTERNAL_SOURCE = re.compile(r"master canon bible|keeper.?s?\s+(?:notes|edition)|canon ledger", re.I)

def public_sources(raw):
    """Keep public archival references; never display internal source metadata."""
    accepted = []
    for part in str(raw or "").split(";"):
        part = part.strip().strip('"').strip("'").strip()
        if re.search(r"master canon bible|keeper.?s?\s+(?:notes|edition)", part, re.I):
            continue
        part = re.sub(r"\s*(?:and\s+)?(?:(?:political|Volume II)\s+)?canon ledger.*$", "", part, flags=re.I).strip(" ,;-")
        if re.search(r"Compendium\s+(?:I|II)\b|Living Chronicle|Royal Register", part, re.I):
            accepted.append(part)
    return "; ".join(accepted) if accepted else "Public historical attribution under review."
