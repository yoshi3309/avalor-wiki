# Article Reading 2.0 — the Archives of Avalor

**Purpose:** Give long player-facing histories more visual rhythm while preserving the parchment manuscript aesthetic and existing sources. Nothing here changes canon or requires a new article.

## Shared changes

- A restrained gold reading progress line runs along the top of every article.
- The desktop section table of contents highlights the currently read chapter.
- On phones, the formerly hidden table of contents has an accessible **In this record** dropdown.
- Articles can include optional editorial pull quotes, historical notes and contested-record callouts in three distinct muted colors.
- In-body illustrations display with a printed archival frame, caption, optional credit in the caption, alt text, and mobile-responsive wide / inset-left / inset-right layouts.
- All visual modules are optional. Existing articles without them retain their existing text and structure.

## How to add in-body artwork with Pages CMS

1. Open a public article under **Public archive articles** in Pages CMS.
2. Under **In-article illustrations**, add a row and choose/upload an approved public image.
3. Add a concise, accurate image description and an archival caption or artist credit. Use JPEG or WebP under 3 MB when possible.
4. Choose the existing chapter heading ID in **Insert after chapter heading**. You can find an ID by opening the published article and clicking its heading in the table of contents (e.g. `adventures-on-roads-without-a-single-destiny`).
5. Use **After paragraph number** to place the image after paragraph 1, 2, etc. in that section.
6. Choose `wide`, `inset-left`, or `inset-right`. On narrow screens, inset art automatically becomes a full-width figure.

**Recommended editorial restraint:** one or two illustrations per substantial article, at most three supported by the engine. The existing main portrait or location artwork remains separate in the article sidebar.

## How to add a callout

Under **Archival callouts and pull quotes** add a row:

- `reflection` — antique gold; a newly written **editorial synthesis** that adds meaning instead of repeating the preceding sentence. Label it as a reflection, never as a historical quotation.
- `quote` — antique gold; reserve for a **meaningful, already-authenticated excerpt**, not a sentence simply repeated from the surrounding paragraph. The build requires exact occurrence in the published article, but editors must also judge whether extracting it adds value. Never invent historical dialogue.
- `note` — subdued blue; a constructive interpretive note **assigned to a known Commission scholar** (Lady Miren Dast, Brother Halden Korr, or Professor Xiomara Thal). Write in the scholar's established perspective and make it add a new angle. It is newly authored commentary, not a purported verbatim transcript.
- `contested` — subdued oxblood; conflicting testimony or corrected traditional accounts, not arbitrary dramatic emphasis.

**Highlighted chapters:** Under `highlight_sections`, specify an existing heading ID and one of `turning-point`, `remembrance`, or `legacy`. The builder tints only these chapters, keeping all text and links intact. Use at most three per article, and only when a whole chapter warrants visual distinction.

**Editorial rule:** **Emphasis must earn its place.** If the note restates what the prose already explained, rewrite or omit it. Remove tangential institutional detail from a biography rather than trying to improve it with more decorative elements.

Choose the section heading ID and 1-based paragraph number in which it should appear. Optional attribution may identify the actual historical record or explicitly verified speaker. Use at most one or two callouts per substantial article; the renderer permits up to four.

## Lavitz Shawe — revised editorial demonstration

Following visual review, the initial highlighted sentence was removed because it merely repeated the immediately preceding line.

The revised Lavitz article now includes:
- Two **original editorial reflections** about the Shawe family's experience of prejudice and Lavitz's decision to lower his knife; these are explicitly labeled reflections rather than historical speech.
- Two constructive Commission scholarly interpretations: Brother Halden Korr reflects on the ethical meaning of Devotion after Vengeance; Professor Xiomara Thal considers why one drow's appointment cannot by itself repair longstanding injustice.
- Three subtly tinted turning-point chapters: **The night he set the knife down** (antique gold), **Fo'Gurn and the cost of survival** (muted green-gray), and **Lord Marshal of Avalor** (slate blue).
- The existing approved Misfits illustration, framed within Lavitz's adventures, with alt text and archival caption.
- An editorially tightened **Lord Marshal** chapter that keeps his relationships, personal burdens, and transition to command instead of listing military units, training sites, and unrelated royal forces.

This is an example of **visual rhythm supported by meaningful prose**, not a fixed quota of callouts for every article. The other entries should be reviewed individually and trimmed where necessary.

## Implementation / guardrails

- Config: `.pages.yml` adds `illustrations` and `callouts` fields on articles; no raw HTML in public article bodies is necessary.
- Renderer: `build.py` validates heading IDs, paragraph positions, visual styles, image paths and actual public uploaded image existence; output text is escaped.
- Styles: `assets/article-reading.css`
- Interaction: `assets/article-reading.js`
- Build-level smoke check: `tests/check_article_reading.py` runs after the standard site build and asserts both the Lavitz example and an article with no visual modules.
- Workflow: `.github/workflows/publish.yml` checks JS syntax and built HTML before publication.
- Restriction: do not upload or embed Keeper-only materials or future plot details to the public repository.

## Testing locally

```sh
python tests/check_public_canon.py
python build.py
python tests/check_article_reading.py
node --check assets/article-reading.js
```

After GitHub Pages deploys, visually verify the Lavitz biography on both mobile and desktop. The code-level smoke test cannot replace a real visual review, especially for different image proportions.
