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
        self.elements = []
        self.rail_figures = []
        self._open_tags = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        self.classes.extend(classes)
        self.elements.append((tag, attrs))
        # Inspect the HTML structure semantically: CMS portrait selectors may add
        # classes/attributes to figures without changing the sidebar layout.
        if tag == "figure" and any(
            parent_tag == "aside" and "article-rail" in parent_classes
            for parent_tag, parent_classes in self._open_tags
        ):
            self.rail_figures.append(attrs)
        if tag == "img":
            self.images.append(attrs)
        if tag == "a":
            self.anchors.append(attrs)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img",
                       "input", "link", "meta", "param", "source", "track", "wbr"}:
            self._open_tags.append((tag, classes))

    def handle_endtag(self, tag):
        for i in range(len(self._open_tags) - 1, -1, -1):
            if self._open_tags[i][0] == tag:
                del self._open_tags[i:]
                break


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
assert any("enchanted-tavern-adventurers-gathering-w" in (img.get("src") or "")
           and img.get("src", "").endswith(".webp")
           and img.get("alt") for img in tags.images), "Optimized approved art or alt text missing"
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
assert any("the-six-beneath-golden-ruins-w" in (im.get("src") or "") and im.get("alt") for im in parsed.images)
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


# Location images use a full-width plate; portraits and optional portrait galleries
# belong in the sidebar. Never require an exact class string: Pages CMS can add
# valid alternate appearances and the template can expand its attributes.
for slug in ('renada', 'black-tower', 'heavens-heart', 'stanleyville'):
    page, parsed = audit(slug)
    landscapes = [
        i for i, (tag, attrs) in enumerate(parsed.elements)
        if tag == "figure" and
        {"article-illustration", "article-illustration--landscape"} <=
        set((attrs.get("class") or "").split())
    ]
    assert len(landscapes) == 1, f"{slug}: expected one landscape plate"
    split_index = next(
        (i for i, (tag, attrs) in enumerate(parsed.elements)
         if "article-split" in (attrs.get("class") or "").split()), None
    )
    assert split_index is not None and landscapes[0] < split_index, (
        f"{slug}: landscape plate must appear before article content"
    )
    assert not parsed.rail_figures, f"{slug}: unexpected sidebar figure"

lavitz_page, lavitz_tags = audit('lavitz-shawe')
assert 'article-illustration--landscape' not in lavitz_tags.classes
assert len(lavitz_tags.rail_figures) == 1, "Lavitz must have one portrait figure in the sidebar"
portrait = lavitz_tags.rail_figures[0]
assert "article-illustration" in (portrait.get("class") or "").split(), (
    "Lavitz sidebar portrait lacks its article-illustration class"
)
# If Lavitz has alternate CMS appearances, verify their selector is present
# instead of rejecting the extra class that makes the gallery work.
if "portrait_variants:" in (ROOT / "content/articles/lavitz-shawe.md").read_text(encoding="utf-8"):
    assert "character-portrait-gallery" in (portrait.get("class") or "").split()
    assert "data-portrait-gallery" in portrait
    assert "data-portrait-stage" in lavitz_page
# Article artwork is assigned through Pages CMS and may change between builds.
# A location with an assigned article image must have a landscape plate.
for slug in ('river-city', 'tinsel'):
    page, parsed = audit(slug)
    frontmatter = (ROOT / 'content' / 'articles' / f'{slug}.md').read_text(encoding='utf-8').split('---', 2)[1]
    import re
    assigned = bool(re.search(r'^image:\s*\S+', frontmatter, re.M))
    if assigned:
        assert 'article-illustration--landscape' in parsed.classes, f'{slug}: assigned location image lacks wide plate'
    else:
        assert 'article-illustration--landscape' not in parsed.classes, f'{slug}: unexpected image placeholder'
print('Geographic illustration layout passed: panoramic places and unchanged portrait treatment.')


# Phase 2: flagship sites use existing article visual components without lore invention.
for slug, expected in (
    ("renada", ("archive-figure", "archive-callout--reflection", "archive-callout--note",
                "archive-highlight--turning-point", "archive-highlight--remembrance", "archive-highlight--legacy")),
    ("the-aegis", ("archive-callout--reflection", "archive-callout--note", "archive-highlight--legacy")),
    ("house-frozenroar", ("archive-figure", "archive-callout--reflection", "archive-callout--contested",
                          "archive-highlight--turning-point", "archive-highlight--legacy")),
    ("lowkee", ("archive-callout--reflection", "archive-highlight--legacy")),
    ("kel-maris", ("archive-callout--reflection", "archive-highlight--remembrance")),
):
    page, parsed = audit(slug)
    for cls in expected:
        assert cls in parsed.classes, f"{slug} missing restoration class {cls}"
    assert "article-mobile-toc" in parsed.classes, f"{slug} missing mobile navigation"
aegis, _ = audit("the-aegis")
assert "Sacred counsel, justice, and protection of the vulnerable" in aegis
royal, _ = audit("house-frozenroar")
assert "Rynhold Frozenroar" in royal and "Gradvum Frozenroar" in royal
assert "creator approval in November" not in royal
renada, _ = audit("renada")
assert 'the-city-made-by-the-river' not in renada
print("Restoration of five major entries verified.")


# Phase 3: one coherent article exploration region, with all pathways retained.
for slug in ('lavitz-shawe', 'renada', 'the-misfits', 'house-frozenroar', 'the-aegis'):
    html, parsed = audit(slug)
    assert html.count('class="article-explore"') == 1, f'{slug}: exploration region missing or duplicated'
    assert html.count('id="article-explore-title"') == 1, f'{slug}: exploration heading missing or duplicated'
    assert 'Continue exploring' in html
    assert 'comparison-article-prompt' not in html, f'{slug}: duplicate comparison panel remains'
    assert 'connection-web-article-prompt' not in html, f'{slug}: duplicate connections panel remains'
    assert 'journey-article-prompt' not in html, f'{slug}: duplicate journey panel remains'
    assert 'assets/article-explore.css' in html
lavitz, _ = audit('lavitz-shawe')
assert 'article-explore-action--connections' in lavitz, "Lavitz connections explorer lost"
assert 'article-explore-action--compare' in lavitz, "Lavitz comparison lost"
assert 'gallery-related-card' in lavitz, "Lavitz gallery links lost"
assert 'article-explore-related' in lavitz, "Lavitz related records lost"
finale, _ = audit('shadowfell-confrontation')
assert 'article-explore-journey' in finale, "Misfits finale guided reading lost"
assert 'article-explore-deeper' in finale, "Misfits finale optional deeper reading lost"
royal, _ = audit('house-frozenroar')
assert 'creator approval' not in royal.lower()
assert 'The **Royal Register**' not in royal # Markdown should have rendered to HTML
assert '34 sovereigns' in royal
print('Phase 3 article discovery verified: one region, preserved routes, compact disclosure and in-world royal history.')

# Phase 4: all chapter tools bind to stable in-world headings.
import re as _share_re
for slug in ('lavitz-shawe','house-frozenroar','the-misfits','the-beyond','renada'):
    page, parsed = audit(slug)
    source = (ROOT / 'content' / 'articles' / (slug + '.md')).read_text(encoding='utf-8')
    chapter_count = len(_share_re.findall(r'^## +', source, flags=_share_re.M))
    ids = _share_re.findall(r'data-chapter-share="link" data-chapter-id="([a-z0-9-]+)"', page)
    assert ids and len(ids) == chapter_count, f'{slug}: chapter/link count mismatch'
    assert page.count('class="chapter-share-controls"') == chapter_count, slug
    assert page.count('data-chapter-share="link"') == len(ids), slug
    assert page.count('data-chapter-share="citation"') == len(ids), slug
    assert page.count('class="chapter-share-feedback"') == len(ids), slug
    for anchor in ids:
        assert f'class="chapter-permalink" href="#{anchor}"' in page, (slug, anchor)
        assert f'data-chapter-id="{anchor}"' in page, (slug, anchor)
print('Chapter sharing output verified: static permalinks, in-world labels, and copy actions.')
