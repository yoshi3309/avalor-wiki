# Archives of Avalor — Wiki Enhancement Roadmap

Last updated: 2026-11-09. This is the canonical **project checklist for website improvements**, not a lore document. Keep it current when new work is completed or new ideas are parked. Only public-facing material belongs in the repository.

## Main quest: six planned enhancements

| # | Upgrade | Status | Notes |
|---|---|---|---|
| 1 | Guided journeys through the archives | COMPLETE | Reusable public reading journeys. The Fall of the Six, The Rise of the Misfits, and The Frozenroar Dynasty. `data/reading-journeys.yml`; `/journeys/`. |
| 2 | Interactive relationships | COMPLETE | Interactive, canon-checked explorer for The Six, The Misfits, and House Frozenroar. `data/relationship-maps.yml`; `/connections/`. |
| 3 | Living Chronicle 2.0 | COMPLETE | Five eras, subject and date-confidence filters, keyword search, royal register and guided-journey navigation. `data/living-chronicle.yml`; `/chronicle/`. |
| 4 | Smarter archive search | COMPLETE | Ranked alias-aware search, typo tolerance, collection filters, keyboard navigation and merged-section results. `assets/search.js`, `data/search-aliases.yml`. |
| 5 | Article reading improvements | COMPLETE | Gold reading progress, active TOC, mobile chapter navigation, CMS-managed inline artwork and gold/blue/oxblood callouts. Lavitz showcase. `docs/ARTICLE_READING_DESIGN.md`. |
| 6 | Illustration gallery | COMPLETE | Five populated wings with 29 curated existing public artworks, captions, reference links, lightbox, and shareable exhibit URLs. `content/gallery/`; `/gallery/`. |

## Completed side quests

- **Misfits relationship map refinement (2026-11-08):** The five main adventurers have solid links. Fo'Gurn and Jack are honored companions with distinct dashed links and memorial/ghost symbols; Lavitz and Fo'Gurn's earlier friendship has its own blue dashed line. The presentation does not erase Fo'Gurn's historical membership.

- **Article editorial quality refinement (2026-11-08):** Revised Lavitz after visual review: original editorial reflections rather than duplicated quotation, two clearly attributed Commission scholar perspectives, three selectively tinted chapters, and a tighter Lord Marshal section centered on Lavitz rather than military inventory. Established an ongoing editorial rule: prioritize relevant biography and narrative substance; trim repetitive or tangential material throughout the archive before adding decorative callouts.

## Supporting technical work (as useful, not a seventh major phase)

- Image performance / media optimization, especially on phones
- Accessibility and keyboard usability audits
- Social preview and page metadata
- Sitemap generation and more maintainable timeline data
- README / editor documentation updates

## Current focus and guardrails

- **Current main quest:** All six initial website enhancements complete. Future features are scoped separately as selected, without automatically expanding lore.
- Future lore development, content audits, or other ideas can be handled as side quests without losing this list.
- Add a new idea here rather than silently changing the order of the main quest.
- No Keeper notes, future campaign secrets, unapproved family genealogy, or speculative personal ties may appear in public relationship data.
- Relationships should cite or closely reflect established public articles; a reign-to-reign succession is **not** automatically parentage.
- Each feature should work on mobile and provide accessible navigation.
