"""Phase 0 appearance checks. Run after the public site build."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
pages = [
    SITE / "index.html",
    SITE / "start" / "index.html",
    SITE / "articles" / "lavitz-shawe" / "index.html",
    SITE / "map" / "index.html",
]
js = (SITE / "assets" / "appearance.js").read_text(encoding="utf-8")
css = (SITE / "assets" / "appearance.css").read_text(encoding="utf-8")
for page in pages:
    html = page.read_text(encoding="utf-8")
    for token in ("assets/appearance.css", "assets/appearance.js",
                  'id="appearance-toggle"', 'aria-pressed="false"',
                  "assets/reading-comfort.css", "assets/reading-comfort.js"):
        assert token in html, f"{page}: missing {token}"
    assert html.index("assets/appearance.js") < html.index("</head>")
    assert html.index("assets/appearance.css") > html.index("assets/reading-comfort.css")
    assert html.count('id="appearance-toggle"') == 1
for token in ("avalor-appearance-v1", "localStorage.setItem", "localStorage.getItem",
              "dataset.appearance", "addEventListener('storage'",
              "aria-pressed", "Vellum appearance"):
    assert token in js, f"Missing theme switch behavior: {token}"
for token in ('data-appearance="vellum"', 'data-reading-contrast="high"',
              ".welcome-step-body", ".page-home .archive-wing",
              ".reading-prefs-panel", "@media(max-width:710px)"):
    assert token in css, f"Missing Vellum coverage: {token}"
assert "avalor-reading-comfort-v1" not in js, "Appearance must not overwrite reader preferences"
start = pages[1].read_text(encoding="utf-8")
for route in ("kingdom", "heroes", "history", "world"):
    assert f'data-welcome-choice="{route}"' in start
    assert f'data-welcome-panel="{route}"' in start
print("Vellum & Night Phase 0 static site checks passed.")
