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
