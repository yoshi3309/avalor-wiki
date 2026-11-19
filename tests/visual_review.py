"""Capture actual built Avalor pages in Night and Vellum with headless Chromium.

This is a non-deploying visual review. Screenshots are CI artifacts and assertions
cover navigation, appearance, persistence and obvious layout regressions.
"""
from __future__ import annotations

import functools
import http.server
import json
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
OUT = ROOT / "visual-review"
OUT.mkdir(exist_ok=True)
PAGES = {
    "home": "/",
    "start": "/start/",
    "lavitz": "/articles/lavitz-shawe/",
    "renada": "/articles/renada/",
    "short-record": "/articles/heavens-heart/",
    "all-records": "/articles/",
    "people-collection": "/collections/people-legends/",
    "places-collection": "/collections/kingdoms-places/",
    "faith-collection": "/collections/faith-magic-cosmology/",
    "chronicle": "/chronicle/",
    "journeys": "/journeys/",
    "founding-journey": "/journeys/fall-of-the-six/",
    "atlas": "/map/",
    "gallery": "/gallery/",
    "exhibits": "/exhibits/",
}
SIZES = {"desktop": (1440, 900), "mobile": (390, 844)}
ISSUES = []


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check(condition, message):
    if not condition:
        ISSUES.append(message)


def main():
    handler = functools.partial(QuietHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            for size, (width, height) in SIZES.items():
                context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
                for theme in ("night", "vellum"):
                    for name, url in PAGES.items():
                        page = context.new_page()
                        page.goto(origin + url, wait_until="load")
                        page.evaluate("(value) => localStorage.setItem('avalor-appearance-v1',value)", theme)
                        page.reload(wait_until="load")
                        page.locator("#appearance-toggle").wait_for()
                        current = page.evaluate("document.documentElement.dataset.appearance")
                        check(current == theme, f"{size}/{name}: wanted {theme}, got {current}")
                        check(page.locator("#appearance-toggle").get_attribute("aria-pressed") == str(theme == "vellum").lower(),
                              f"{size}/{name}/{theme}: toggle aria-pressed wrong")
                        check(page.locator("main#main-content").count() == 1, f"{size}/{name}: missing main")
                        metrics = page.evaluate("""() => ({
                          viewport: document.documentElement.clientWidth,
                          scroll: document.documentElement.scrollWidth,
                          body: document.body.scrollWidth
                        })""")
                        check(metrics["scroll"] <= metrics["viewport"] + 3,
                              f"{size}/{name}/{theme}: horizontal overflow {metrics}")
                        if name in ("lavitz", "renada", "short-record"):
                            check(page.locator(".document-paper .article-body").count() == 1,
                                  f"{size}/{name}/{theme}: article body missing")
                            check(page.locator("#reading-bookmark").count() == 1,
                                  f"{size}/{name}/{theme}: reading bookmark missing")
                            measure = page.locator(".article-body").evaluate("(el) => getComputedStyle(el).maxWidth")
                            check(measure in ("none", "100%") or measure.endswith(("px", "ch", "rem")),
                                  f"{size}/{name}/{theme}: invalid reading measure {measure}")
                        if name == "all-records":
                            check(page.locator("#catalog-filter").count() == 1, f"{size}/{theme}: record filter missing")
                            check(page.locator(".catalog-item").count() > 20, f"{size}/{theme}: catalogue entries missing")
                            page.locator("#catalog-filter").fill("zz-nonexistent-record-xyz")
                            check(page.locator(".catalog-item:visible").count() == 0, f"{size}/{theme}: catalogue filter did not narrow results")
                            page.locator("#catalog-filter").fill("")
                        if name.endswith("-collection"):
                            check(page.locator(".people-record").count() > 0, f"{size}/{name}/{theme}: collection empty")
                            check(page.locator(".people-record").first.get_attribute("href"), f"{size}/{name}/{theme}: record link missing")
                            if page.locator("#people-filter").count():
                                page.locator("#people-filter").fill("zz-nonexistent-record-xyz")
                                check(page.locator(".people-record:visible").count() == 0, f"{size}/{name}/{theme}: collection filter did not narrow results")
                                page.locator("#people-filter").fill("")
                        if name == "chronicle":
                            check(page.locator("[data-chronicle-event]").count() > 0,
                                  f"{size}/{theme}: Chronicle missing events")
                            check(page.locator("#chronicle-search").count() == 1,
                                  f"{size}/{theme}: Chronicle search absent")
                            page.locator("#chronicle-search").fill("zz-nonexistent-event-xyz")
                            check(page.locator("[data-chronicle-event]:visible").count() == 0,
                                  f"{size}/{theme}: Chronicle search did not hide unmatched events")
                            page.locator("#chronicle-search").fill("")
                        if name == "journeys":
                            check(page.locator(".journeys-card").count() > 0,
                                  f"{size}/{theme}: journey directory empty")
                        if name == "founding-journey":
                            check(page.locator(".journey-chapter").count() > 0,
                                  f"{size}/{theme}: journey chapters absent")
                            check(page.locator(".journey-primary-link").get_attribute("href"),
                                  f"{size}/{theme}: primary chapter link absent")
                        if name == "atlas":
                            check(page.locator("#atlas-viewport").count() == 1,
                                  f"{size}/{theme}: atlas viewport missing")
                            check(page.locator("#atlas-image").count() == 1,
                                  f"{size}/{theme}: map art missing")
                            check(page.locator("#atlas-zoom-in").count() == 1,
                                  f"{size}/{theme}: zoom control missing")
                            check(page.locator("#atlas-search").count() == 1,
                                  f"{size}/{theme}: atlas location search missing")
                        if name == "gallery":
                            check(page.locator(".gallery-card").count() > 0,
                                  f"{size}/{theme}: gallery artwork absent")
                            page.locator(".gallery-card").first.click()
                            check(page.locator("#gallery-lightbox").is_visible(),
                                  f"{size}/{theme}: gallery viewer failed to open")
                            check(page.locator("#gallery-viewer-image").get_attribute("src"),
                                  f"{size}/{theme}: gallery viewer artwork absent")
                            page.locator(".gallery-viewer-close").click()
                            check(not page.locator("#gallery-lightbox").is_visible(),
                                  f"{size}/{theme}: gallery viewer failed to close")
                        if name == "exhibits":
                            check(page.locator("[data-exhibit-card]").count() > 0,
                                  f"{size}/{theme}: exhibit catalogue empty")
                            page.locator("#exhibits-search").fill("zz-no-exhibit-xyz")
                            check(page.locator("[data-exhibit-card]:visible").count() == 0,
                                  f"{size}/{theme}: exhibit filter did not hide unmatched records")
                            page.locator("#exhibits-search").fill("")
                        if name == "start":
                            choices = page.locator("[data-welcome-choice]")
                            check(choices.count() == 4, f"{size}/{theme}: expected 4 start paths")
                            choices.nth(1).click()
                            check(page.locator('[data-welcome-panel="heroes"]').is_visible(),
                                  f"{size}/{theme}: heroes panel did not open")
                        page.screenshot(path=str(OUT / f"{size}-{name}-{theme}.png"), full_page=True, animations="disabled")
                        page.close()
                # Check both controls keep independent persisted state.
                page = context.new_page()
                page.goto(origin + "/start/")
                page.locator("#appearance-toggle").click()
                next_theme = page.evaluate("document.documentElement.dataset.appearance")
                page.locator("#reading-prefs-trigger").click()
                page.locator('[data-reader-size="large"]').click()
                page.reload()
                check(page.evaluate("document.documentElement.dataset.appearance") == next_theme,
                      f"{size}: theme did not persist")
                check(page.evaluate("document.documentElement.dataset.readingSize") == "large",
                      f"{size}: reading size did not persist")
                page.close()
                context.close()
            browser.close()
    finally:
        server.shutdown()
    report = {"screenshots": len(list(OUT.glob("*.png"))), "issues": ISSUES, "pages": PAGES, "viewports": SIZES}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    assert not ISSUES, "Visual browser checks identified regressions"


if __name__ == "__main__":
    main()
