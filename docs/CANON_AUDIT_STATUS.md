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
