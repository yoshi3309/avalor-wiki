# Character Comparison Dossiers — Phase 6.2

An interactive, canon-conscious side-by-side reading tool at /compare/ within the Archives of Avalor. Curated pair pages live at /compare/pairs/<id>/ and have individually shareable social preview cards.

## Scope and provenance

- Seventeen reviewed public People & Legends biographies are in the first collection, with seven curated pairings.
- The reviewed statements live in data/character-comparisons.yml. Each profile supplies four fields: public identity and calling, institutions and affiliations, defining decisions, and historical legacy.
- Each field specifies text (a brief editorial synopsis) and chapter (the exact h2 slug in that same public biography).
- The site build validates every person belongs to People & Legends and every cited chapter actually exists. Missing or mistyped chapters fail the build.
- Historical era, article name, subtitle, summary, and art are inherited from published biography metadata.
- No ability scores, character levels, unconfirmed genealogies, invented relations, speculative motivations, or fabricated comparative ratings are shown. Comparing two people does not suggest they met.
- Existing responsive previews are reused; images must be already approved public portrait assets.

## User experience

Readers choose any two supported biographies, swap positions, read four parallel rows, and open the full underlying biographies. Each claim has a direct link to the supporting public article chapter. Smaller screens reflow for legibility.

Selections update the URL for sharing. Featured combinations have individual pages /compare/pairs/<id>/ with distinct Discord/Open Graph previews. Other combinations use /compare/?left=<slug>&right=<slug>. Discord shows the general Comparison Dossiers card for ad-hoc query combinations; the page loads the correct selected figures client-side.

The tool requires no login or private information. Without JavaScript, preset cards and individual source biographies remain available through normal HTML links.

## Editorial updates

Edit data/character-comparisons.yml to add a new reviewed public person or curated pairing. Every new character requires four concise statements backed by exact headings in its existing published biography. Every new pair needs a unique permanent ID and two supported biographies. Keep both sides different. Run the GitHub publishing tests. Do not fill gaps with unsupported lore.

## Quality assurance

GitHub Actions runs node --check assets/comparisons.js and python tests/check_comparisons.py. The checks cover reviewed profiles and existing article chapters, seven pair routes and canonical social metadata, cross-links from articles and Connections, and the generated files. Manual mobile and assistive technology checks are recommended before making formal compliance claims.
