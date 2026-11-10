# The Archives of Avalor

The **player-facing Scholar's Edition of the World of Avalor** — a static, illustrated fantasy encyclopedia published on GitHub Pages. It is not a DM repository or a transcription of secret campaign material.

**Live site / Start Here:** https://yoshi3309.github.io/avalor-wiki/

**Archive Home:** https://yoshi3309.github.io/avalor-wiki/archive/

**Content editor:** https://app.pagescms.org/ (repository: yoshi3309/avalor-wiki)

**Current roadmap:** [Wiki Enhancement Roadmap](docs/WIKI_ENHANCEMENT_ROADMAP.md)

## What's inside?

As of November 10, 2026, the repository holds **112 public encyclopedia articles** across five collections, **29 curated illustration exhibits**, and **five editorial historical exhibits**. These counts change as editors publish new material.

| Explore | URL | Purpose |
|---|---|---|
| Archivist's Welcome | / | Four introductory pathways; the default landing page |
| Archive Home | /archive/ | Color-coded deeper exploration hub |
| Encyclopedia | /articles/ | Discover and search public records |
| Living Chronicle | /chronicle/ | 18 historically qualified entries |
| Interactive Atlas | /map/ | Approved public map pins, regions, and landmarks |
| Atlas Through Time | /map/#atlas-history | Six documented geographic links to Chronicle events |
| Connections Explorer | /connections/ | Curated, source-backed relationships |
| Character Comparison Dossiers | /compare/ | 17 reviewed people, with cited facts and shareable comparisons |
| Reading Journeys | /journeys/ | Curated reading sequences |
| Illustration Gallery | /gallery/ | Public character artwork and landscape exhibits |
| Historical Exhibits | /exhibits/ | Five explicitly modern editorial reconstructions |
| My Reading Desk | /reading-desk/ | Browser-local bookmarks and progress |

Additional features include responsive WebP artwork, original full-resolution files, Discord preview cards for published pages, the search command (Cmd/Ctrl + K), chapter navigation, and reading comfort settings for font size, typeface, contrast, and motion.

## Edit public material through Pages CMS

Sign in to [Pages CMS](https://app.pagescms.org/), open **yoshi3309/avalor-wiki**, and choose an editorial collection. Saving creates a GitHub commit and triggers publishing checks.

- **Articles:** Source Markdown is under content/articles/. Use unique lowercase-hyphenated filenames. Supply a public title, category, summary, provenance, and body. Markdown links and public wiki links support named articles and chapter headings.
- **Illustrations:** Upload only approved public JPG, PNG, or WebP files to assets/uploads through Pages CMS. Provide meaningful alternative text. WebP previews are regenerated automatically; originals are preserved.
- **Atlas:** data/avalor-map.yml is editable under Map settings & locations. Open /map/?edit=1 to preview positions, then copy both X and Y into Pages CMS and save. Clicking the map alone does NOT publish coordinates. Never invent a marker position for convenience.
- **Gallery:** Records under content/gallery/ include title, collection, caption, image, and related sources. Renaming an artwork does not automatically change its gallery collection; update that field separately.
- **Historical exhibits:** Records under content/exhibits/ are labeled editorial reconstructions. Do not claim their wording, parchment, or modern archive crest are genuine recovered manuscripts.
- **Historical and comparison datasets:** Source-controlled YAML under data/ requires valid public article IDs and, where applicable, verified chapter anchors.

Detailed feature guides: [Archivist's Welcome](docs/ARCHIVISTS_WELCOME.md), [Character Comparisons](docs/CHARACTER_COMPARISONS.md), [Atlas Through Time](docs/ATLAS_THROUGH_TIME.md), [Responsive Media](docs/RESPONSIVE_MEDIA.md), and [Discord Previews](docs/DISCORD_SOCIAL_PREVIEWS.md).

## Preview locally

Requires Python 3.12. Install the requirements from requirements.txt, build with Python, then serve _site with any static HTTP server. Example commands:

    python -m pip install -r requirements.txt
    python build.py
    python tests/check_site_quality.py
    python -m http.server 8000 --directory _site

Then visit http://localhost:8000/. No paid hosting or local database is required. The build writes _site/sitemap.xml, _site/quality-report.json, and _site/media-report.json.

To reproduce the complete publishing checks, follow [.github/workflows/publish.yml](.github/workflows/publish.yml). The workflow validates public canon, internal links and chapter anchors, generated HTML, image alternative text, previews, historical references, and accessibility smoke checks.

## Search engine and quality safeguards

Each build creates a canonical sitemap at /sitemap.xml and a robots.txt sitemap pointer. Retired articles remain accessible through redirects but are excluded from the sitemap.

The build's quality report checks actual generated pages and references: local links, destination chapters, resources, duplicate IDs, missing image alt attributes and top-level headings. The publishing test fails if unresolved issues remain. Off-site links are not fetched and require separate human verification.

The site audit is **not** a formal WCAG certification, an automated screen-reader test, or a guarantee of live mobile speed. Manually test iPhone Safari, Android Chrome, keyboard navigation, high browser zoom and assistive technology after major visual changes.

## GitHub Pages and domain notes

This repository publishes to https://yoshi3309.github.io/avalor-wiki/ through GitHub Actions.

The builder uses that actual HTTPS base for canonical links, sitemap entries, and absolute Discord preview image URLs. If the site moves to a custom domain, configure AVALOR_SITE_URL to match the **real deployed HTTPS address**, and test the deployment and crawler metadata. Do not merely change URLs in documentation.

Discord can cache older link previews. Curated paired comparisons have independent preview cards; arbitrary selector combinations use the general comparison-page image.

## Non-negotiable canon and privacy boundary

**Everything committed to this public repository can be viewed by players.** That includes all source Markdown and YAML, images, datasets, generated HTML, and search metadata. Hiding an entry in the interface does not keep it secret in GitHub.

Keep Master Canon Bibles, Keeper volumes, private encounters, undisclosed lore, secret maps, unreleased character art, and future campaign plans in a **separate private repository or local folder**. Never publish DM-only information in public-source metadata.

Do not invent missing genealogies, personal relationships, ancient political borders, exact historical event locations, fake document provenance, character abilities, dates, or map coordinates just to populate an interactive feature.

## Operating cost

The public site is static and does not need a database, paid CDN, account system or purchased domain. GitHub Pages is publicly accessible and does not provide private player-only access through a public repository. Pages CMS is a third-party service; review its current access permissions and pricing before granting repository access.
