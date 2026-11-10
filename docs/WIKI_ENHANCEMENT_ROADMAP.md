# Archives of Avalor — Wiki Enhancement Roadmap

Last updated: 2026-11-10. This is the canonical **project checklist for website improvements**, not a lore document. Keep it current when new work is completed or new ideas are parked. Only public-facing material belongs in the repository.

## Main quest: six planned enhancements

| # | Upgrade | Status | Notes |
|---|---|---|---|
| 1 | Guided journeys through the archives | COMPLETE | Reusable public reading journeys. The Fall of the Six, The Rise of the Misfits, and The Frozenroar Dynasty. `data/reading-journeys.yml`; `/journeys/`. |
| 2 | Interactive relationships | COMPLETE | Interactive, canon-checked explorer for The Six, The Misfits, and House Frozenroar. `data/relationship-maps.yml`; `/connections/`. |
| 3 | Living Chronicle 2.0 | COMPLETE | Five eras, subject and date-confidence filters, keyword search, royal register and guided-journey navigation. `data/living-chronicle.yml`; `/chronicle/`. |
| 4 | Smarter archive search | COMPLETE | Ranked alias-aware search, typo tolerance, collection filters, keyboard navigation and merged-section results. `assets/search.js`, `data/search-aliases.yml`. |
| 5 | Article reading improvements | COMPLETE | Gold reading progress, active TOC, mobile chapter navigation, CMS-managed inline artwork and gold/blue/oxblood callouts. Lavitz showcase. `docs/ARTICLE_READING_DESIGN.md`. |
| 6 | Illustration gallery | COMPLETE | Five populated wings with 29 curated existing public artworks, captions, reference links, lightbox, and shareable exhibit URLs. `content/gallery/`; `/gallery/`. |

## Active Phase 5 improvements

- **Interactive Atlas regional exploration (2026-11-09):** Five curated area views based exclusively on existing approved map pins; three narrative trails using already-published locations; shareable selected-location links. These are navigation aids, not newly asserted borders, roads, measured distances or canonical itineraries. Historical border overlays remain deferred until geographic source maps are approved.

- **Personal Reading Desk (2026-11-09):** Browser-local bookmarks, saved chapter positions, recently opened accounts and explicit completed-reading markers, with a personal shelf at `/reading-desk/`. No accounts, uploads, analytics, or cross-device synchronization.

- **Cross-Archive Connections Explorer (2026-11-09):** 40 curated public nodes and 56 sourced relationships spanning people, organizations, places and events, with search, subject filters, focus links, evidence links and bridges to the original three maps. Data is deliberately curated, never inferred from cross-references. `data/connections-explorer.yml`; `/connections/`.

- **Historical Documents & Archive Exhibits (2026-11-09):** Five canon-grounded, clearly labeled editorial reconstructions, rendered as archival folios with accessible text, evidence, uncertainties, and links to source articles. No invented quotations, original decrees, signatures, seals, or undocumented political details. Public exhibit pages: `/exhibits/`.

- **Reading Comfort & Accessibility (2026-11-09):** Shared Aa reading controls with browser-local font sizing (standard/large/extra large), classic/clear typeface, higher-contrast mode and site motion reduction. Improved paper/exhibit legibility, focus indicators, chapter jump focus, and keyboard-safe mobile navigation; includes automated build checks. Further manual screen-reader and multi-device testing remain worthwhile. `assets/reading-comfort.js`, `assets/reading-comfort.css`.

- **Responsive artwork & mobile media optimization (2026-11-09):** Automatic Pillow/WebP variants (480/960/1440px) generated for approved public raster uploads during GitHub Pages builds, using source-preserving picture tags for gallery cards, collection covers, article figures and portraits. Full-resolution originals remain accessible, especially the atlas map. Intrinsic image dimensions, lazy loading, and a public build-time media report are included. `media_optimization.py`, `tests/check_media_performance.py`.

- **Discord & social previews (2026-11-09):** Open Graph and Twitter large-card metadata with canonical absolute URLs, source-grounded descriptions, and generated 1200 × 630 JPEG artwork for every public page. Approved public article/gallery art is preferred; pages without suitable assets receive an archival heraldic card. Preserves originals, embeds image metadata for Discord bots, tests paths and dimensions, and allows a future HTTPS base URL through AVALOR_SITE_URL. See docs/DISCORD_SOCIAL_PREVIEWS.md.

## Phase 6 — User-selected implementation order

These priorities reflect the author's chosen order on November 9, 2026. This table's priority numbers are the new execution sequence, not the original numbered suggestions.

| Priority | Feature | Status | Focus |
|---|---|---|---|
| 1 | The Archivist's Welcome | COMPLETE | Optional first-visit page at /start/. Four public starting paths (kingdom, heroes, history, world), three verified public records each, reading-journey/atlas handoffs, homepage invitation. No forced onboarding. |
| 2 | Character Comparison Dossiers | COMPLETE | Source-cited dossiers for 17 reviewed public figures, four matched categories, responsive portraits, shareable selections, and seven curated pair pages with unique Discord previews. No invented rankings, abilities, or relationships. |
| 3 | Atlas Through Time | COMPLETE | Source-aware geographical layer joining all 18 Chronicle events to current Atlas navigation. Six reviewed public pin associations distinguish sites, affected regions and associated places; twelve uncharted events remain visible. Era filters, contextual spotlight, date-precision notices, and Chronicle/Discord links. No invented historic borders, routes or dates. |
| 4 | Archive Quality & Maintenance | COMPLETE | Canonical XML sitemap with retired redirects excluded, robots sitemap pointer, generated-page link/anchor/resource and image-alt audits, refreshed 112-article maintainer guide, safe mobile/keyboard improvements, and CI publication gates. Manual device and assistive-technology checks remain recommended. |
| 5 | The Royal Gazette | NEXT | Dated editorial publication and update highlights; no invented in-world breaking news. |
| 6 | Chapter Sharing to Discord | PLANNED | Copy chapter URLs and source-grounded citations; reuse existing anchors and social previews. |

The first-time welcome is an invitation, not a gate. Returning readers can keep using the full site directly. Data lives in data/welcome-routes.yml and links only to published articles, existing reading journeys, or the atlas.

## Completed side quests

- **Misfits relationship map refinement (2026-11-08):** The five main adventurers have solid links. Fo'Gurn and Jack are honored companions with distinct dashed links and memorial/ghost symbols; Lavitz and Fo'Gurn's earlier friendship has its own blue dashed line. The presentation does not erase Fo'Gurn's historical membership.

- **Article editorial quality refinement (2026-11-08):** Revised Lavitz after visual review: original editorial reflections rather than duplicated quotation, two clearly attributed Commission scholar perspectives, three selectively tinted chapters, and a tighter Lord Marshal section centered on Lavitz rather than military inventory. Established an ongoing editorial rule: prioritize relevant biography and narrative substance; trim repetitive or tangential material throughout the archive before adding decorative callouts.

## Supporting technical work (as useful, not a seventh major phase)

- Media delivery follow-up: assess field performance on phones (real-device Web Vitals) and consider caching policies after deployment
- Further assistive-technology and keyboard usability audits (manual cross-browser/screen-reader verification)
- Social preview follow-up: check Discord's cached embeds and consider per-article editorial artwork overrides after live testing
- Sitemap generation and more maintainable timeline data
- README / editor documentation updates

## Current focus and guardrails

- **Current main quest:** Phase 6 priorities are locked in the table above. The Archivist's Welcome, Character Comparison Dossiers and Atlas Through Time and Archive Quality & Maintenance are complete; The Royal Gazette is next. The original six website enhancements remain complete.
- Future lore development, content audits, or other ideas can be handled as side quests without losing this list.
- Add a new idea here rather than silently changing the order of the main quest.
- No Keeper notes, future campaign secrets, unapproved family genealogy, or speculative personal ties may appear in public relationship data.
- Relationships should cite or closely reflect established public articles; a reign-to-reign succession is **not** automatically parentage.
- Each feature should work on mobile and provide accessible navigation.
