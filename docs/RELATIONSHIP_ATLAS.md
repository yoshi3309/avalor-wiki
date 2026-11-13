# Interactive Relationship Atlas — Public Archive

The relationship atlas is a **public navigation and discovery feature**. It does not infer or establish new canon.

- Directory: `/connections/`
- Cross-archive focus link: `/connections/?focus=lavitz-shawe`
- Curated public evidence data: `data/connections-explorer.yml`
- Cross-archive UI: `assets/connections-web.js` and the shared connections stylesheet
- The Six: `/connections/the-six/`
- The Misfits: `/connections/the-misfits/`
- House Frozenroar: `/connections/house-frozenroar/`
- Public data: `data/relationship-maps.yml`
- Shared templates: `templates/connections.html` and `templates/connection.html`
- Interaction: `assets/connections.js` and `assets/connections.css`

## Editing

Each `maps` entry defines a page with unique `id`, title, subtitle, summary, editorial note, icon, and an existing public `related_article` slug. Each node has `id`, `label`, `detail`, `kind` (`group`, `person`, or `royal`), and fixed percent coordinates `x`/`y`. `article` is optional and must match a public `content/articles` slug if present.

Each edge identifies `from` and `to` node IDs, a labeled relationship, and one of `fellowship`, `later`, `companion`, `prior-friendship`, `parent`, `consort`, `sibling`. Build validation rejects missing or duplicated node IDs, invalid public slugs, unsupported types, self-links, repeated links, and out-of-range coordinates. This keeps the feature small, easy to maintain, and separate from wiki article bodies.

When a map includes an article as a node or its `related_article`, the article automatically shows an "Explore the connections" entry point.

## Canon and interaction rules

- Never equate consecutive reigns with a parent-child relationship.
- Do not guess kinships between royal branches merely because they share a surname.
- The separate kinship clusters in the Frozenroar map are **separate documented kinships**; their layout does not represent missing generations.
- The Six's center means fellowship, not family or identical moral judgments.
- The Misfits relationship map now distinguishes the five core player-character adventurers (Lavitz, Tel'Lora, Sven, Amara, and Heureux) from honored in-world traveling companions Fo'Gurn and Jack. This distinction is a diagram design choice, not a denial of Fo'Gurn's historical membership in the company.
- Fo'Gurn's memorial symbol acknowledges his death during the campaign; Jack's ghost symbol acknowledges his spectral nature and the party's adoption of him.
- A separate blue dashed link marks Lavitz and Fo'Gurn's documented friendship before the Misfits formed. Solid lines mark the five central adventurers; warm dashed lines mark honored companions.
- No player-facing data may contain Keeper-only or future campaign secrets.
- All nodes use native keyboard-focusable buttons, with a details panel and a secondary figure directory; no third-party graph library is needed.
- Keep the public record navigable without JavaScript using the provided static source links.

## Cross-archive explorer (9 November 2026)

The searchable explorer draws only from a curated list of public article nodes and explicit relationships with evidence articles. It never guesses relations from article cross-links, common surnames, succession, or shared campaign appearances. Its diagram shows up to eight immediate neighbors; the adjacent list shows all documented connections. Each relationship identifies its own public source. Existing fellowship and dynasty diagrams remain unchanged and link to the broader explorer.

## Enhancement roadmap

See `docs/WIKI_ENHANCEMENT_ROADMAP.md` for the six-part running checklist. The six initial enhancement milestones are complete; later phases are planned independently.

## Connections Explorer review (13 November 2026)

The **Connections Explorer** is distinct from the visual family/fellowship Relationship Atlas. Its curated evidence-backed graph has been expanded to **60 nodes and 88 relationships**, adding Heyden, Gomo, Silver, Gerran, Jinlin, Kel'Maris and the Misfits-era adversaries. Retired biographies (Jinlin and Gerran) and the newly registered short character entries (Gomo and Silver) retain stable direct section links. Connections describe **documented relationships only**: e.g. King Gerran is Gradvum's father, but Jinlin's ancient opposition to Cid does not prove Jinlin's death. A separate source article is attached to each relation.
