## Confirmed consolidation — November 8, 2026

The creator approved these umbrella articles, to keep the wiki focused and allow meaningful sections rather than thin standalones:

- **The Avalorian Forces** (`avalorian-forces`): military hub with separate sections for **The Avalorian Standing Army**, **Lion's Bane**, and **Dina Hyanda**. Their individual command, responsibilities, founding traditions, and coordination remain distinct. Previous article slugs redirect to the relevant section.
- **The Guilds of Avalor** (`guilds-of-avalor`): shared guild article, particularly the **Thieves Guild** in Olivruch and the **Clerics Guild** in Stannisport; both may be developed further when the creator provides more lore. Keep the independently substantial Hunters Guild and Bard Guild articles.
- **Independent Factions of the Misfits Era** (`independent-factions-of-the-misfits-era`): separate historical sections for **the Cult of Gol'Goroth** and **the Wrath of Innocent**, including its founder **Jinlin Vechon**. Both suffered defeats during Misfits adventures, but their present-day survival or activity **is not confirmed**. Do not conflate them or assume Cid led the cult.
- **Rotten Husk Clan** remains an independent article, since it is a people/community rather than just a defeated adversary.

Implemented with source-file retirement, automatic legacy URL redirects, direct section cross-links and revised Organizations & Factions navigation. The architecture has **three new hubs replacing five standalone pages**, a net decrease of two. The article redirect data is in `data/article-merges.yml`.

---
# Avalor Royal Archives — Editorial Architecture Audit
**Status:** Second pass completed · 2026-11-07 · **96 public standalone records** at this review  
**Scope:** Public, established Avalorian material only. No expansion beyond Avalor or publication of Keeper-only information.

## Editorial test
A subject earns its own article if it independently matters to the setting, has a distinct history or institution, appears in multiple important stories, has substantial approved canon, or is intended for later campaign development. Page length alone is not decisive. Avoid repeating what a better parent biography, city, or campaign history already says.

## Second-round recommendations (NOT YET APPROVED — do not merge)
| Candidate source | Preferred destination | Reason | Caution |
| --- | --- | --- | --- |
| `fo-gurn-and-the-hydra` | `fo-gurn#the-hydra-and-the-decision-to-remain` (add exact heading upon migration) or another Fo'Gurn section | Event is already covered extensively in Fo'Gurn, Lavitz, and the Misfits; current stand-alone retells those same facts | Preserve the years of mourning, Jaaris distinction and Zauks's memory-copy; keep a redirect |
| `cult-of-golgoroth` | `the-first-commission#the-second-commission` | Public article currently contains chiefly the second commission and Heureux's arrival, without independently established doctrine, leadership, or fate | **Hold if the cult is still important in active campaigns or will gain future canon**; retain name and cross-links |
| `jaznaars-refuge` | `jaznaar#the-refuge-beyond-ordinary-knowledge` (verified current heading) | No confirmed map location; entire account is closely tied to Jaznaar and Tel'Lora's encounter, told in both biographies | Keep the route uncharted and avoid revealing access details; redirect old URL |
| `rotten-husk` | `the-misfits#the-liberation-of-the-rotten-husk` (new section) | Short account of an encounter already covered in the Misfits and Heureux | **Conditional**: the Rotten Husk is a named community, not merely a monster encounter; preserve standalone if the tribe will receive independent history |
| `jinlin-vechon-wrath-of-innocent` | `the-misfits`, as a dedicated section, only if its wider role is complete | Currently a single encounter with an adversary whose faction has no fully published structure | **Conditional**: named antagonist plus founded faction may justify its own article; ask about future importance before retiring |
| `sanctuary-at-heavens-heart` | `arnauds-edicts` or `cathedral-paladins` under a specific sanctuary section | Considerable overlap with Arnaud's edicts and the order's established First Teaching | **Borderline; lean retain** because this is a distinct important historical confrontation, not a passing detail |

## Independently significant: retain
### People and character development
- All six of the Founding Six, the Misfits including **Fo'Gurn** and **Jack**, the royal house's important figures, established recurring adversaries, and other named people who carry independent stories.
- **Noki** remains a separate character article by express creator direction: a larger role in the ongoing Hunters campaign.
- Keep the five Aegis councilors and all four appointed sheriffs **for now**. Their current articles are office-heavy, but they are named political actors with the potential to gain character histories. Consider richer **personality, motivations, relationships, tensions** only when approved by the creator.
- **Cid the Blood King** deserves his own entry despite being the same person as Aldus: the persona and historical era differ significantly. Add clear mutual references, rather than duplicate the same entire backstory.

### Places
- Independent cities, settlements, ports and trade centers such as Stanleyville, Cove City, Tinsel, Stems Port, Siesta Ford, Karhold, Land's End, and Wayward Sun retain independent geographic significance even if current information is limited.
- Great Citadel, Great Cathedral, Great Library, Shamman’s Tower, Black Tower, Great Fork Tower, Lord Osmo's Tower, Heroes Hill and Heaven's Heart are distinct geographic/institutional subjects.
- The Forest of the Fey, Denzians Forest, Dead Marshes, Great Desert, Spine of the World remain regional articles.
- Renada neighborhoods, Black Stair, Moonville Manor and Ripped Beard already consolidated in the approved first pass.

### Institutions, beliefs and histories
- Retain House Frozenroar (complete Royal Register), Aegis, Cathedral Paladins, Hunters Guild, standing army, Lion's Bane, Dina Hyanda, Royal Commission and Four Sheriffdoms. These organizations have distinct mandates.
- Retain **Bard Guild** and **Heureux's Bard Academy** as separate institutions; their formal relationship is not established.
- Retain **The Threefold Devotion**, **The Sacred Balance**, **Lathander and the Dawn**, **The Faiths of Families and Peoples**, and the faith overview: their focus is distinct even if some material recurs.
- Retain Founding Wars, Unification, Sundering, Blood Sickness, Betrayer's Legend, Jaznaar's Vindication, Arnaud's Edicts and Reina's Reforms as historically distinctive accounts. Do not collapse them merely because some people recur.
- **The Tournament of Champions** remains a major independently significant turning point.
- The **Age of Ascendancy** is a period overview, not only a duplicate of the Misfits' epilogue, although it would benefit from later expansion.

## Expand rather than merge
- **Cid the Blood King** (currently very brief relative to his historical importance): expand the public record with already attested identity, public appearances, manipulation of the founding narrative, and defeat; do not reveal the new campaign's Godkiller/revival secrets.
- **Stanleyville** (currently short): expand its distinctive metalworking history, founding tradition and civic life within confirmed canon; retain a standalone location article.
- **The Aegis**: richer hub for its eight offices and council, preserving officeholder biographies.
- **The kingdom's present government**: develop relationships and duties where already established, not as invented political intrigue.
- **Heaven's Heart**: enrich the settlement's distinct relationship to the Cathedral Paladins, Great Library, and nearby Black Tower without conflating their geography.

## Navigation and technical findings
- After merging Renada's neighborhoods, the 'Within Renada' collection group contained only the Great Cathedral and Great Citadel, already repeated in 'Towers & Landmarks'. The redundant group has been removed while the individual institutions remain accessible.
- Related-record cards initially collapsed retired subarticles to their parents' top-level URLs. Updated rendering preserves section **name and fragment** for remaining `related` metadata that references retired slugs.
- Existing retired article URLs continue redirecting through `data/article-merges.yml` and the build; no retired slug should be reused for a different entity.
- Cross-link navigation to specific sections is supported and verified by the public-canon checker. The full editorial audit should continue to identify mentions that *ought* to be linked, which mechanical link validation alone cannot detect.
- Consider later a compact top-of-article **“In this city”** table of contents for Renada, since it now contains many named sections. This is a UI enhancement rather than a reason to split the city again.
- The published map should preserve standalone major locations. No new locations or positions were invented by this review.

## Safe consolidation protocol
For each creator-approved merge, migrate *all* documented facts to an appropriate parent section; revise wikilinks, metadata, navigation and map references; retain the prior URL as a redirect to the specific section; preserve search; and verify GitHub Actions. **Never merge merely to chase a lower article count.**

## Decisions awaiting the creator
1. Should Fo'Gurn's hydra event and Jaznaar's refuge become sections of the characters' biographies?
2. Is the cult of Gol'Goroth an ongoing/future-campaign concern, or can it become part of the first/second-commission history?
3. Will the Rotten Husk, Jinlin Vechon or Wrath of Innocent be expanded later? If yes, their standalone entries remain.
4. Should the Heaven's Heart sanctuary confrontation stay a distinct event article (editorial recommendation: yes)?
