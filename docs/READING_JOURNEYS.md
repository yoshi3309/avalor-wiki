# Guided Reading Journeys — Public Archive

The guided-journey system is a *navigation layer*, not a new source of historical canon. It only links public `content/articles/*.md` records and provides short scholar-approved contextual introductions.

- Public index: `/journeys/`
- First reading path: `/journeys/fall-of-the-six/`
- Data: `data/reading-journeys.yml`
- Page templates: `templates/journeys.html`, `templates/journey.html`
- Styles: `assets/journeys.css`

## Adding another journey

Add a unique `id` and a new journey entry under `journeys:` in `data/reading-journeys.yml`. Provide a title, subtitle, overline, summary, editorial note, era, and an ordered `steps:` list. Each step must supply an existing public `article` slug, a short `label`, and `introduction`. Build validation rejects invalid IDs, missing articles, duplicate steps, and paths of fewer than three records.

Every new journey automatically appears in the public index. Each linked article gains a reading-path panel with previous/next links; article content itself is not modified. Readers may enter the journey from any chapter. Existing article URLs and the search index remain unchanged.

**Public safety:** Never store Keeper-only facts, undiscovered future campaign developments, private maps, or restricted notes in reading-journey data. The GitHub repository and generated pages are public.
