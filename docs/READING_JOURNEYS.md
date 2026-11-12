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

## Event-led narrative and optional deeper reading

A journey's `steps` represent a **chronological core**. The Rise of the Misfits uses **History & Chronicles** event articles as its main chapters, not a character's biography as a substitute for an adventure. Biographies, organizations, locations and relic dossiers are optional **deeper reading** displayed within the chapter card and at the chapter article's reading-path panel.

Each step supports two new optional fields:

```yaml
      - article: some-historical-event
        label: The Event, not a character profile
        introduction: What happened and why it matters in this sequence.
        act: "ACT II · THE COST OF FRIENDSHIP"  # only when starting an act
        deeper_reading:
          - article: some-hero
            note: The same event through a companion's personal history.
          - article: some-relic
            note: The object's recorded history and limitations.
```

The compiler resolves every supplemental slug to a public article, requires a readable note, rejects self-links and duplicate supplemental links in one chapter, and limits extras to five. Supplemental articles do **not** alter chapter numbering or previous/next navigation. For journeys without extras, presentation remains unchanged.

In the Misfits route, four act dividers separate the early fellowship, growing losses, the interrupted rescue and the aftermath. A chapter's link leads to its historical account. The expandable deeper-reading area is clearly separate and never blocks the next chapter.

**Do not put restricted Keeper material in either main chapters or supplemental reading.**
