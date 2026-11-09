"""Build-level smoke tests for optional article visual modules.

Run after: python build.py
These checks inspect generated PUBLIC HTML; no Keeper source is loaded.
"""
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "_site" / "articles"


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = []
        self.anchors = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        self.classes.extend(classes)
        if tag == "img":
            self.images.append(attrs)
        if tag == "a":
            self.anchors.append(attrs)


def audit(slug):
    page = ARTICLES / slug / "index.html"
    assert page.is_file(), f"Missing built article: {page}"
    html = page.read_text(encoding="utf-8")
    parsed = Audit()
    parsed.feed(html)
    return html, parsed


lavitz, tags = audit("lavitz-shawe")
assert "article-reading-track" in tags.classes, "Reading progress absent"
assert "article-mobile-toc" in tags.classes, "Mobile chapter navigation absent"
assert "archive-figure" in tags.classes, "Lavitz demonstration illustration absent"
assert "archive-callout--reflection" in tags.classes, "Lavitz editorial reflections absent"
assert "archive-callout--note" in tags.classes, "Lavitz historical commentary absent"
assert "archive-highlight--turning-point" in tags.classes, "Lavitz pivotal-chapter emphasis absent"
assert "archive-highlight--remembrance" in tags.classes, "Lavitz remembrance emphasis absent"
assert "archive-highlight--legacy" in tags.classes, "Lavitz leadership emphasis absent"
assert "THE ARCHIVIST" in lavitz, "Editorial reflections need distinct attribution"
assert "brother-halden-korr" in lavitz, "Halden's scholarly perspective absent"
assert "professor-xiomara-thal" in lavitz, "Xiomara's scholarly perspective absent"
assert "The broader" not in lavitz or "Standing Army" not in lavitz, "Extraneous army summary remains in Lavitz account"
assert any("enchanted-tavern-adventurers-gathering.png" in (img.get("src") or "")
           and img.get("alt") for img in tags.images), "Approved art or alt text missing"
assert "assets/article-reading.js" in lavitz
assert "assets/article-reading.css" in lavitz
assert any(a.get("href") == "#varis-and-thia" for a in tags.anchors), "Mobile TOC anchor missing"

other, tags = audit("heavens-heart")
assert "article-reading-track" in tags.classes, "Reading progress must work on every article"
assert "archive-figure" not in tags.classes, "Unconfigured article acquired an illustration"
print("Article Reading 2.0 smoke tests passed (Lavitz showcase + unchanged article).")

# These four major histories now use the illuminated Lavitz reading treatment.
for slug, required in (
    ("tellora-ebbenflow", ("archive-callout--reflection", "archive-callout--note", "archive-highlight--legacy")),
    ("svendyal-shadowwhisper", ("archive-callout--reflection", "archive-callout--note", "archive-highlight--turning-point")),
    ("the-misfits", ("archive-callout--reflection", "archive-callout--note", "archive-highlight--remembrance")),
    ("aldus-greystone-iii", ("archive-figure", "archive-callout--note", "archive-highlight--turning-point")),
):
    page, parsed = audit(slug)
    for cls in required:
        assert cls in parsed.classes, f"{slug} missing {cls}"
    assert "article-reading-track" in parsed.classes and "article-mobile-toc" in parsed.classes
page, parsed = audit("aldus-greystone-iii")
assert any("the-six-beneath-golden-ruins.png" in (im.get("src") or "") and im.get("alt") for im in parsed.images)
map_html = (ROOT / "_site/connections/the-misfits/index.html").read_text(encoding="utf-8")
assert "👻" not in map_html and "✧" in map_html and "☠" in map_html
print("Expanded character-reading treatments and Connections emblems passed.")


# Sven's creator-confirmed family and divine history now forms the biography's foundation.
sven, parsed = audit("svendyal-shadowwhisper")
for phrase in ("Tristan", "Kristofer", "Vandria Gilmadrith", "Erevan Ilesere",
               "Gwathrenflos", "Shadowwhisperer", "justice", "silver ring"):
    assert phrase in sven, "Sven biography missing: " + phrase
assert "archive-callout--reflection" in parsed.classes
assert "archive-highlight--turning-point" in parsed.classes
print("Sven's family and divine history passed.")


# Phase 2 cultural histories and cross-links.
for slug, required in (
    ("peoples-of-avalor", ("Books of Names", "Concord Walk", "Kelsalor", "Northern Desert Tribes")),
    ("ringtree-clan", ("Yesteryear Tome", "Her", "Heureux", "Cid")),
    ("forest-of-the-fey", ("Concord Walk", "Ringtree Clan")),
    ("the-faiths-of-families-and-peoples", ("Ringtree Clan", "Books of Names")),
    ("kingdom-of-avalor", ("Many histories beneath the lion banner", "everyday belonging")),
):
    page, parsed = audit(slug)
    for phrase in required:
        assert phrase in page, f"{slug} missing cultural material: {phrase}"
    assert "article-reading-track" in parsed.classes, f"{slug} missing reading controls"
for slug in ("peoples-of-avalor", "ringtree-clan", "forest-of-the-fey"):
    page, parsed = audit(slug)
    assert "archive-highlight--" in page, f"{slug} missing narrative highlight"
print("Phase 2 cultural articles and cross-links passed.")


# Phase 3: ancient histories remain scholarly uncertainties, not DM revelations.
for slug, required in (
    ("aethrion", ("Scribe's Question", "Blank Folio", "Halden", "Thal")),
    ("the-beyond", ("Unfinished Gloss", "Unplaced Index", "Halden", "Thal")),
):
    page, parsed = audit(slug)
    for phrase in required:
        assert phrase in page, f"{slug} missing public canon: {phrase}"
    assert "archive-callout--note" in parsed.classes
    assert "archive-highlight--" in page
    assert "article-mobile-toc" in parsed.classes
faith, _ = audit("faiths-and-gods-of-avalor")
assert "The Keeper of the First Dawn in folklore" in faith
print("Phase 3 public scholar histories and restrained Keeper folklore passed.")
