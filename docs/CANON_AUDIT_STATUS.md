# Avalor Public Archives — Canon Audit Status

**Status:** In progress — technical pass complete; narrative/source-by-source review ongoing.

## Technical integrity — pass

- The public wiki has **91 archive articles** at the start of this review.
- The full archive has passed the GitHub Actions `tests/check_public_canon.py` validation for parseable YAML and related-article references after the CMS formatting repair.
- The **Faiths and Gods** editor error was caused by a multiline quoted `facts` field. That record and **22 additional articles** were normalized to YAML block scalars (`facts: |-`).
- The workflow now validates YAML frontmatter and rejects unclosed multiline quotation styles before publishing.
- A successful GitHub build certifies technical integrity only, **not** historical accuracy.

## Confirmed corrections already implemented

| Topic | Canon status | Applied |
|---|---|---|
| Samuel | **Aasimar**, not Monadic Deva; user correction overrides older PDFs | Samuel's biography plus three cross-references |
| Samuel's divine representation | **Tyr and Helm**; the **Cathedral** honors Tyr, Helm, and Torm | Samuel's biography |
| Lavitz | Current **Oath of Devotion**; formerly Oath of Vengeance | Lavitz's biography |
| Astronoph | **Female deva**, High Priest of the Great Cathedral | Preserved |
| Jeyse | **Deva** | Preserved |
| Cal'el | **Aasimar** | Preserved |
| Jaznaar | Drow spellcaster; wizard-vs.-sorcerer class remains **OPEN** | Preserved |

## Public-record distinctions checked

- Fo'Gurn was an original Misfit and a close friend of Lavitz; the **five publicly celebrated companions** were Lavitz, Tel'Lora, Sven, Heureux, and Amara.
- Tel'Lora is a **male half-elf** and current High Wizard.
- Aldus Greystone III became Cid the Blood King; his history must not be split into separate unrelated lives.
- The Great Cathedral and Great Citadel belong **within Renada** and should not have competing world-map pins.
- Karhold's claim to independence remains a political dispute, not settled crown administration.
- The current Aegis is an eight-seat council; the four sheriffs are appointed royal officers, not hereditary rulers.

## Visual canon review — open

The CMS contains character portraits whose filenames/appearance may imply more than the **written** public source establishes. These images are **not** being modified until the creator confirms intended canon.

- **Belgram**: image titled as a *dwarven king*; established public records confirm the *Third Hand* and Mountain Hall Clan but do not establish royalty or ancestry.
- **Rastrin**: image titled as a *tortle magistrate*; written canon establishes the *Warden of Order* but not ancestry.
- **Beldir**: image titled as an *admiral*; source confirms *Sentinel of the Seas* but does not independently establish a naval rank.

## Remaining narrative audit

**Not yet certified:** complete line-by-line comparison of all 91 articles against the public Living Chronicle, Master Canon Bible, and relevant approved portions of other volumes. Continue in this order:

1. People & Legends: full identity/kinship/age/title/appearance audit; do not infer anatomy or office from illustration filenames.
2. Organizations & Factions: leadership, jurisdictions, patron faiths, and guard/military distinction.
3. Kingdoms & Places: nested locations, geographical claims, and atlas consistency.
4. History & Chronicles: dynasty, dates, multiple necromancers, and the timeline of the Six/Misfits.
5. Faith, Magic & Cosmology: patron gods, rituals, the limits of religious testimony.
6. Verify that no Keeper-only plot developments appear in public material.

## Rules for future writing

- **User's latest explicit canon corrections supersede outdated PDF statements**.
- Treat the Living Chronicle as a public historical account, with its own stated epistemic limits.
- Never infer unsupported species, ranks, relationships, or geographical positions.
- Separate historical fact from in-world rumor and from author-created narrative connective prose.
- Flag truly unresolved claims as **OPEN**, without silently choosing a version.

## Source-backed audit pass — 6 November 2026

**Method:** Compared the live wiki's ninety-one article front matters and core historical claims against the public *Living Chronicle* and the approved, public portions of the canon compendia. Restricted notes were used only to detect conflicts and protect boundaries, not as player-visible narrative. This is an editorial pass, **not** an attestation that every sentence is now independently verified.

### Confirmed corrections committed

- **Tel'Lora Ebbenflow** — the article now identifies him explicitly as a **male half-elf wizard**, in agreement with the Living Chronicle and the canon reference.
- **Amara** — the at-a-glance record now states **female**; her established role as druid and descendant of Petris is unchanged.
- **Age of Ascendancy** — retained as the name used by the public Living Chronicle, while avoiding a claim that a formal royal act established it as an official calendar division. The older reference Bible marked the name as WORKING; the later public text uses the term.
- **The Misfits' First Commission** — archive number was duplicated with the Age of Ascendancy at HIS.005; reassigned the commission's identifier to **HIS.015**, without changing the event's chronology.
- **Historical prose** — replaced three out-of-world uses of the word *canon* with in-world documentary language in Malikeah, Heureux's Bard Academy, and Jinlin Vechon's account.

### Additional continuous checks

- GitHub publishing validation now checks **unique archive identifiers** and **resolvable article-body wiki-links** as well as YAML and related slugs. This is separate from substantive canon checking.
- Preliminary manual inspection of the article headings, facts, and key narrative passages did not reveal additional source-confirmed contradictions requiring immediate factual rewrite. This is **not** a claim that all narrative paragraphs have been certified.
- Distinctions preserved: the first necromancer was not Jaaris; Fo'Gurn was part of the original party, Jack traveled onward with the company, and Sven's public reputation does not justify publishing his private actions.
- Names of the royal Aegis officers and four appointed sheriffs match the public political records; none of their unverified species, rank, or personal details has been inferred from uploaded portraits.
- No obvious mentions of the restricted campaign plot names were identified in the public article titles and content searches. This is a targeted check rather than a proof against every indirect spoiler.

### Open editorial questions

1. **Art and appearance:** the filenames for Belgram's portrait imply a dwarven **king**, Rastrin's a **tortle magistrate**, Katiri's an **orc warrior**, and Beldir's an **admiral**. The currently approved texts confirm their offices but not all these additional species or ranks. Preserve images pending creator verification.
2. **Public-facing references:** some `source:` fields still cite the *Master Canon Bible* or an editorial *canon ledger*. They do not expose private plot details in the cited field, but they break the in-world archival voice and imply a public source where one may not exist. Preserve existing provenance pending a decision on separate private/editorial and public citation displays; do not fabricate a replacement source.
3. **The First Commission numbering:** `HIS.015` resolves the duplicate without renumbering established historical articles. The exact archive-wide numbering convention remains open for a future systematic catalogue design.
4. **Jaznaar's character class:** explicitly **OPEN** between wizard and sorcerer, even though some historical accounts describe him generically as a spellcaster.
5. **Historic calendar:** do not silently identify nearly two thousand years of later history with a precise birthday or fix unresolved chronology by invention.
6. **Full sentence-level corroboration:** a second pass is still required for complete line-by-line attribution, especially where the public articles cite the editorial canon Bible as their only recorded source.

### Publishing status

The above corrections were committed to the `main` branch while Pages CMS artwork edits were also arriving. Deployment runs may remain queued; a commit is not evidence of successful publication until its build and deployment finish.
