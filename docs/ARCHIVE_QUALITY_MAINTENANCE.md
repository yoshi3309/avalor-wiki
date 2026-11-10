# Phase 6.4 — Archive Quality and Maintenance

This phase adds a practical maintenance gate to the published Scholar's Edition without changing any established lore.

## Generated public artifacts

- /sitemap.xml lists only canonical, indexable generated HTML pages; no retired article redirects, source files, private content, or media downloads.
- /robots.txt references the real HTTPS sitemap endpoint.
- /quality-report.json is a build report containing counts of generated pages, local links and references scanned, missing image alt attributes, duplicate IDs, and actionable issues.
- /media-report.json continues to describe responsive image variants and potential preview savings; it does not claim field performance.

All public data remains public even when a CMS flag hides a UI entry. The audit must never ingest Keeper materials.

## Integrity checks

The build inspects generated HTML, not just Markdown source. It validates:

- local page links, stylesheet/script/asset URLs, image and srcset paths;
- existing target chapter fragment IDs on published pages;
- one main H1 on each indexable page, unique HTML IDs, and alt attributes for all image elements;
- canonical sitemap URLs and omission of retired redirect pages;
- keyboard skip-link target, mobile reading comfort assets, and basic navigation structure.

Links to external domains, JavaScript-created URLs, and browser behavior cannot be fully verified by a static file scan. They remain human-review items. The test checks actual generated site contents and fails the publishing workflow for unresolved internal defects.

## Maintenance workflow

1. Edit approved public content or code through Pages CMS/GitHub.
2. Run the publishing workflow. The builder generates the static site, sitemap and quality report.
3. If the quality gate fails, inspect the exact paths in the output, correct the source article/template/asset, then rerun. Do not silently ignore or whitelist real broken paths.
4. For major interface changes, separately review responsive widths, keyboard navigation, high browser zoom, reduced motion, VoiceOver/NVDA or TalkBack, and actual Discord previews.

## Mobile and accessibility refinements

- The main-content skip target is programmatically focusable.
- Sidebar and skip-link targets meet a comfortable minimum height; the skip link remains clearly visible when focused.
- Mobile content, prose, code and tables retain safe overflow behavior.
- Forced-colors systems receive visible keyboard outlines.
- Existing reduced-motion and user reading-preference controls remain unchanged.

These are safeguards and automated smoke checks, **not** formal proof of WCAG compliance or real-device performance.

## URLs and canonical policy

The build currently uses https://yoshi3309.github.io/avalor-wiki/ . A future move requires an actual HTTPS deployment plus a matching AVALOR_SITE_URL override. Do not index redirect pages or construct multiple competing canonical locations. Sitemap and Open Graph URLs must agree.
