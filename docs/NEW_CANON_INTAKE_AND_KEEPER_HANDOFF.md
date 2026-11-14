# Avalor — New Canon Intake, Wiki Publication & Keeper Handoff

**Adopted workflow proposal · 13 November 2026**  
**Purpose:** Make the player-facing Archives of Avalor the first publication destination for new campaign material, without requiring a world-wide audit or a rewrite of the four private reference books with every addition.

## Authority, publication and privacy

1. **Keeper rulings control truth.** The creator's latest explicit ruling supersedes conflicting older text. The public wiki is the working *player-facing* expression of approved, releasable canon; it is not the authority for unreleased Keeper material.
2. **The public GitHub repository is public in its entirety.** Markdown, branches, PR descriptions, commit history, tests, data, issue comments, and publication metadata are visible. Do **not** enter future campaign reveals, classified identities, confidential documents, undisclosed motivations, or private Keeper-only material in this repository, even on a draft branch.
3. **Private books are archival editions.** The Master Canon Bible, Living Chronicle, and Compendiums are updated in deliberate consolidated cycles, not after every new wiki article. Do not expose original Keeper PDFs in this public repository.
4. **Disclosure is separate from truth:** mark each claim as *approved and public*, *approved but private*, *proposed*, *contested in-world*, or *unresolved*. Only approved and public material goes into player-facing source files. A reveal from a finished campaign can be public when specifically authorized; never assume that every completed chapter releases every secret.

## Repeatable cycle (one character, location, event, or small batch)

### A — Intake (free-form, no mandatory template)

Accept story notes, older campaign PDFs, session transcripts, character sheets, art, recollections, and creator corrections as supplied. Do not force the creator to restate structured facts. Extract the named people, places, organizations, dates, relationships, events, source provenance, potential spoilers, and uncertainties. If the input is contradictory, retain versions until a decision is made.

Maintain a **private working intake record** outside this public repo for private facts; record in the public change description only safe, approved claims and affected public pages. Distinguish *creator-stated*, *source-attested*, *reasonably inferred*, and *proposed extrapolation*. An attractive interpretation is not automatically canon.

### B — Targeted dependency check (not a full audit)

Locate the subject's current page, redirects, collection index, and close cross-references. Check only relevant public records: overlapping character biographies, parent locations and organizations, chronology, related historical events, relationship data, Chronicle, maps, reading journeys, galleries and current creator overrides. Search broadly **only if** a change alters a world-scale rule, major date, genealogy, campaign chronology, institution, or important cross-campaign identity.

Produce a compact conflict note when appropriate: **Existing statement → New evidence or ruling → Affected public pages → Proposed correction → Unresolved question**. Do not quietly retcon a creator-established event or add made-up connective histories.

### C — Choose the smallest appropriate treatment

| Treatment | When | Typical structure |
|---|---|---|
| **Major feature** | Central PC, defining NPC, landmark, city or arc with consequential developed history | Dedicated substantial article; distinctive narrative chapters, contextual artwork when approved, useful fact box and related links, supported thematic highlights and clearly marked editorial reflections |
| **Supporting standalone** | Recurring figure, important settlement or institution with enough independent history to reward a dedicated page | Focused sections, a memorable opening and conclusion, key relationships and 1–2 grounded images only when helpful |
| **Minor collection entry** | Brief ally, adversary, neutral character, small place or supporting figure whose existing story warrants a few paragraphs | Usually 1–3 meaningful paragraphs in the correct existing collection, with stable `##` heading anchor |
| **Inline mention** | One-off encounter, incidental landmark, brief mention or passing connection | Sentence or short paragraph in the most relevant parent article |

**No word-count quotas.** Lavitz and Heyden are models for richly documented biographies, not minimum requirements for minor characters. Titles, power level and ancestry alone do not determine tier. Promote a previously minor entry when new approved history justifies it; maintain redirects and stable links.

For a new *location*, place it into the appropriate geographical hierarchy without inventing coordinates, borders, travel times or a map pin. An unlocated place may still receive an article or section.

### D — Draft in-world, then confirm canon

Use the Royal Commission's historical voice: compelling grounded storytelling, not modern editorial disclaimers about canon, missing author decisions, or incomplete PDFs. Separate witnessed events, later testimony, speculation and conflicting interpretations. Do not invent quoted eyewitness accounts or assign quotations to scholars without support.

For each subject, provide a short **editorial decision summary** to the creator: treatment tier, placement, confirmed facts, suggested connective prose, changed existing history, and **only consequential** OPEN questions. Seek approval for new facts, material retcons and disclosure decisions; do not require decisions about insignificant stylistic details. Approval of one batch does not grant blanket permission for all future material.

### E — Apply and verify a focused wiki patch

Once approved, update the subject's public article or existing collection and the directly dependent records, such as related slugs, article merges/redirects, search aliases, references, optional chronology/relationship data and curated navigation where genuinely relevant.

Before publishing:
- Verify the current creator-overrides ledger and relevant original evidence, including the newest superseding rulings.
- Check YAML/frontmatter, unique entry IDs, related links, internal body links, images and alt text, redirects and section anchors.
- Confirm the subject's date, identity, species, pronouns, affiliations and fate agree with **the affected** existing articles.
- Run the available build, link and feature tests, with targeted new regression checks for material canon corrections.
- Review changed text and PR metadata for spoilers. Do not put protected Keeper material in public comments, tests, titles or source citations.
- Publish through a tested GitHub branch/PR and verify the GitHub Pages deployment. A green test is necessary but does not itself prove historical accuracy; a merged PR is not the same as a completed deployment.

Do **not** create a new article, chronology event, map location, portrait, relationship edge or biography merely to fill a website feature. Avoid repeating full-corpus audits when only one neighborhood of lore changed.

### F — Capture a private Keeper handoff

After an approved wiki batch is published, preserve a durable **private** handoff entry outside this public repository:

- **Batch ID / approval date / campaign:** e.g. `AV-2026-011`.
- **Source(s):** original session, author notes, backstory, or submitted document, with distinguishable authority.
- **Status:** approved public / approved private / proposed / OPEN, at the level of individual claims.
- **Subjects & changes:** canonical names, dates, affiliations, relationships, key events and corrected prior claims.
- **Public delivery:** wiki article URLs, parent-section anchors, relevant PR/commit, publishing confirmation.
- **Keeper-only truths:** where stored in a private document; never quote or store these in the public repo.
- **Book propagation:** which of Bible, Chronicle, Compendium I, Compendium II must later change, and why.
- **Unresolved questions:** plainly labeled, with no inferred answer promoted to fact.

The private handoff entry is **not dependent on chat history or assistant memory**; keep a cumulative external file that can be supplied again if chats change. If a batch contains no Keeper-only details, a public-safe summary may additionally be maintained in repository documentation, but that does not replace the private compilation.

### G — Periodic archival edition, not continuous PDF churn

When a campaign finishes, a meaningful arc closes, or the creator requests it, combine the approved handoff records into **one cumulative, downloadable Keeper addendum PDF** organized by campaign, people, places, organizations, events and source-book destination. Cross-check that compilation against the then-current wiki and latest creator decisions.

Use it to update the four master volumes **in a separate editorial project** after the collected batch is settled. Preserve dated version information and decisions superseding older material; do not silently rewrite history in the reference editions. The public wiki need not wait for revised volumes to be published.

## When to escalate to a broad reconciliation

Do a broader audit only when the new lore changes a load-bearing fact such as:
- Founding/succession chronology, major genealogy, a named death/return, or the sequence of a whole campaign.
- Fundamental cosmology, planar rules, divinity or an identity connecting multiple campaigns.
- Major geography, nationhood, political hierarchy, or the structure of a widely referenced institution.
- Disclosure status of a secret affecting numerous public articles.

Otherwise, use **one subject + its direct dependents**, not every page in the encyclopedia.

## Batch completion checklist

- [ ] Keeper approved factual content and what can be public.
- [ ] Correct tier and placement; no unnecessary invented backstory.
- [ ] Existing relevant pages and redirects checked, without unrelated sweeping rewrites.
- [ ] In-world prose and accurately attributed source basis.
- [ ] Relevant link/build/canon tests pass.
- [ ] PR merged; Pages deployment successful.
- [ ] Private cumulative Keeper handoff entry stored externally for eventual PDF compilation.

**Working principle:** *Intake once, reconcile locally, publish the player story, retain the private truth, update the books in batches.*
