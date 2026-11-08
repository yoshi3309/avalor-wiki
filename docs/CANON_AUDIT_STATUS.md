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
| Samuel | **Monadic Deva**, confirmed by creator's World Anvil biography in November 2026, superseding prior aasimar correction | Samuel's biography, three cross-references and validator |
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
- **Beldir**: author-provided World Anvil backstory now **confirms his admiral's rank** after defeating Pirate Lord Por Rostin, and his leg prosthesis.

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

## Aegis identities and public references — editorial review

**Reviewed against:** the Aegis roster in the Master Canon Bible, Volume I, section VII; the public body of Compendium II, entry II.001, section VI; and its internal concordance section VII. The Aegis members' **names and current offices are confirmed**:

| Member | Established office | Portrait suggests (not independently verified) |
|---|---|---|
| Belgram of Mountain Hall Clan | Third Hand, coordinating council offices | Dwarven king; clan affiliation does not prove royal status or exact ancestry |
| Myxi Twinefoot | Golden Hand, finance | No unverified ancestry or rank added |
| Katiri Tenderfoot | Silver Hand, official intelligence | Orc warrior; identity/physical appearance not established by Aegis text |
| Rastrin Diltir | Warden of Order, internal order | Tortle magistrate; appearance and the precise judicial rank are not established |
| Beldir Willowrun | Sentinel of the Seas, maritime counsel | Admiral; council office does not automatically confer naval rank |
| Samuel | The Devoted, Tyr and Helm representative | **Monadic Deva**, per latest author-provided World Anvil text |
| Lavitz Shawe | Lord Marshal, commander of Lion's Bane | **Drow**, present Oath of Devotion |
| Tel'Lora Ebbenflow | High Wizard, eighth seat | **Male half-elf wizard** |

**Action:** retain the creator's chosen portraits and current public biographical descriptions; **do not** infer species, royal status, or military command from image filenames. Belgram, Katiri, Rastrin, and Beldir remain open for author confirmation. This is a deliberate unresolved canon choice, not a failing validation check.

### Public-facing source attribution fix

- Added `public_references.py` so the built website displays suitable *Living Chronicle* and *Compendium* references without rendering private editorial labels such as `Master Canon Bible` and `canon ledger`.
- Original `source:` metadata stays in the repository and Pages CMS for editorial provenance. This is **not** replaced by invented in-world evidence.
- Articles with no attributable public reference receive the transparent message `Public historical attribution under review.`
- The publishing test checks rendered source strings for internal labels and that the displayed attribution is nonempty.
- Added an alias for the Royal Commission article so three existing linked references resolve to its proper page.

**Limits:** These changes clean the *display* of source notes and confirm council roles. They do **not** independently establish every assertion in every article, nor do they establish the actual species/ranks of the four disputed portraits. Full line-by-line claim/source verification remains open.

## Frozenroar dynastic chronology and pedigree — verified register pass

**Primary public source:** *The Living Chronicle*, Chapter V, Appendix: **The Frozenroar Royal Register**, **A Partial Pedigree of House Frozenroar**, and **A Chronology of the Lion**. Cross-checked against the public historical record in Compendium Volume II, Entry II.001, Section IV, and the Master Canon Bible's continuity notes. The Chronicle's appendices are the source for the precise reign-year list.

### Verified succession facts

- The later public histories identify **34 sovereigns** from **Rynhold (1–37 AF)** through **Gradvum (1983 AF–present)**, with consecutive reign entries. The older Master Canon Bible's note that an earlier account called Gradvum the *seventh* Frozenroar king is a **superseded unresolved source discrepancy**, not authority to discard 27 named rulers.
- The earliest verified familial links in the published partial pedigree: **Benedikt → Aldara** (father to daughter); **Aldara → Dietmar** (mother to son). **Rynhold and Benedikt's parentage is not established**.
- **Dietmar → Halton** is established as succession by his acknowledged heir, **not confirmed parentage**. **Halton and Dathyra Blueshadow** were the parents of **Sylavor**.
- **Sylavor → Arelis** and **Wolfram → Ysoria** are successions following abdication, with parentage/precise kinship **unrecorded**.
- **Elyra and Corven** were twins, **Elyra born first**. **Torenna** was Elyra's daughter. Corven was **spared** after renouncing his claim, rather than executed.
- **Crown Prince Alaric** was the elder brother of **Orrec**, and died before accession; Alaric is **not** an additional reigning sovereign.
- Present royal children confirmed: **Theodric** (eldest son and heir), **Leontes** (younger son), and **Vivienne** (daughter).

### Chronology checked and reflected in public site

- Avalor founded **1 AF**. The battle at Heroes Hill occurred in the founding era; its exact independent date is **open**.
- The Black Tower catastrophe is **approximately 10 AF**, not a precisely authenticated year.
- Elven Concord during **Dietmar (107–155 AF)**; strengthened by Halton's later marriage. This **Elven Concord** is not Torenna's later **Concord of the Two Lions**.
- Sylavor abdicated **298 AF**; Arelis began reign **299 AF**.
- Elyra reigned **857–893 AF**. War of the Two Lions lasted **890–893 AF**. Elyra died of illness in **893 AF**, not assassination; Torenna formally reigned from **894 AF**. The succession transition should not be misdated to the start of the war.
- Arnaud reigned **1259–1315 AF**. Reina **1316–1402 AF** reversed additional discriminatory laws against drow communities, but did not eliminate prejudice. Sanctuary at Heaven's Heart did **not** become a general war between the crown and the paladins.
- Wolfram reigned **1462–1511 AF** and voluntarily abdicated **1511 AF** under negotiated pressure; Ysoria acceded **1512 AF**. The reign span must not be mistaken for verified precise dates of the *War Across the Sea* campaigns.
- Gradvum acceded **1983 AF**. Original Misfits defeat of Cid **around 2000 AF** remains approximate. Roughly twenty years followed; do not convert provisional dates to fixed anniversaries.

### Publications updated

- **House Frozenroar**: all 34 ruler names and reigns, verified partial pedigree and source-supported historical account.
- **King Gradvum** and **Queen Melmiri**: names of the three children and Theodric's position as heir.
- **Forest of the Fey**: clarified that the register identifies Halton as Dietmar's heir but does not independently verify their parentage.
- **The Living Chronicle** timeline (site chronology): 17 events with clearer chronology and dates, retaining approximations.

**Still open:** Complete kinship between many successive sovereigns; the precise founding-era date of Heroes Hill; exact Black Tower disaster year; origins and participants in the provisional War of the Narrow Straits; dates of individual War Across the Sea campaigns. No new claims were invented to settle these.


## The Founding Wars, Black Tower, and drow-rights history — new public records

Ten player-safe Scholar's Accounts added after reviewing the public *Living Chronicle* (Chapters II, IV, V and VII), the Master Canon Bible's distinction between established and unresolved history, and the public historical sections of Volume II:

- **Founding Wars** (`HIS.016`) — Osmo was a mortal conqueror; a coalition fought multiple campaigns, not only Heroes Hill; exact campaign years are open.
- **Bradgem Glav** (`BIO.032`) — killed Osmo at Heroes Hill and died from mortal wounds; the rearing-horse memorial is established, its intended symbolism is not.
- **Unification of Avalor** (`HIS.017`) — founded in **1 AF** through negotiated union; Renada was already a settlement; the exact date of the battle is not assumed to be 1 AF.
- **Blood Sickness** (`HIS.018`) — arcane corruption arising from Aldus's experiments, **not** an established contagious plague with known symptoms or transmission.
- **Sundering of the Six** (`HIS.019`) — Black Tower ritual interrupted roughly a decade after the founding; no confirmed single killing blow; Aldus's mortal death did not end Cid.
- **Betrayer's Legend** (`HIS.020`) — Cid's agents spread the paired false accounts of Aldus the savior and Jaznaar the betrayer; the original founders knew Jaznaar was innocent.
- **Arnaud's Edicts** (`HIS.021`) — royal discrimination during **1259–1315 AF** had serious consequences for drow families and cannot be explained away by fear of magic.
- **Sanctuary at Heaven's Heart** (`HIS.022`) — Jeyse (deva) and Cal'el (aasimar) defended threatened families; resolved through negotiation, **not a general war**.
- **Reina's Reforms** (`HIS.023`) — curtailment of discriminatory laws **1316–1402 AF**, centuries **before** Jaznaar's public historical vindication.
- **Jaznaar's Vindication** (`HIS.024`) — Gradvum's proclamation after the Misfits defeated Cid; historical correction did not undo the harm caused by the false legend.

All were connected to existing records and to the Chronicle timeline, with an additional founding-wars timeline entry. No new atlas pins were created.

**Editorial limits:** the exact Heroes Hill battle year, the precise Black Tower anniversary, the full mechanism of the Blood Sickness, the exhaustive history of Cid's propaganda agents, and a complete list of Arnaud-era victims remain unresolved. Public accounts do not present Keeper-only future developments as established history.

**Publishing status:** GitHub article and cross-link deployments passed; timeline deployment should be verified in the GitHub Actions log.

## November 2026 — Character background and prose corrections

Creator's original World Anvil biographies supersede earlier speculative descriptions of Beldir, Katiri, Myxi and Samuel. Samuel is now confirmed as a **Monadic Deva** and founder of **the Bloodless**. Lady Miren is a female dwarf, Professor Xiomara a female drow, and Brother Halden a human male. Cassian's backstory was rewritten in a more natural narrative style, without treating the absence of named foreign geography as a plot point. All changes use public material supplied by the creator.
