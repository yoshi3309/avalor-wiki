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
