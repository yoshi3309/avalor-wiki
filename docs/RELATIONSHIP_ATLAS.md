# Interactive Relationship Atlas — Public Archive

The relationship atlas is a **public navigation and discovery feature**. It does not infer or establish new canon.

- Directory: `/connections/`
- The Six: `/connections/the-six/`
- The Misfits: `/connections/the-misfits/`
- House Frozenroar: `/connections/house-frozenroar/`
- Public data: `data/relationship-maps.yml`
- Shared templates: `templates/connections.html` and `templates/connection.html`
- Interaction: `assets/connections.js` and `assets/connections.css`

## Editing

Each `maps` entry defines a page with unique `id`, title, subtitle, summary, editorial note, icon, and an existing public `related_article` slug. Each node has `id`, `label`, `detail`, `kind` (`group`, `person`, or `royal`), and fixed percent coordinates `x`/`y`. `article` is optional and must match a public `content/articles` slug if present.

Each edge identifies `from` and `to` node IDs, a labeled relationship, and one of `fellowship`, `later`, `parent`, `consort`, `sibling`. Build validation rejects missing or duplicated node IDs, invalid public slugs, unsupported types, self-links, repeated links, and out-of-range coordinates. This keeps the feature small, easy to maintain, and separate from wiki article bodies.

When a map includes an article as a node or its `related_article`, the article automatically shows an "Explore the connections" entry point.

## Canon and interaction rules

- Never equate consecutive reigns with a parent-child relationship.
- Do not guess kinships between royal branches merely because they share a surname.
- The three clusters in the Frozenroar map are **separate documented kinships**; their layout does not represent missing generations.
- The Six's center means fellowship, not family or identical moral judgments.
- The Misfits map distinguishes founding membership, later membership, and a traveling companion.
- No player-facing data may contain Keeper-only or future campaign secrets.
- All nodes use native keyboard-focusable buttons, with a details panel and a secondary figure directory; no third-party graph library is needed.
- Keep the public record navigable without JavaScript using the provided static source links.

## Enhancement roadmap

See `docs/WIKI_ENHANCEMENT_ROADMAP.md` for the six-part running checklist. The next core milestone is Living Chronicle 2.0.
