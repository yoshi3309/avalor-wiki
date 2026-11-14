# Avalor Canon Intake & Publication Playbook

**Purpose:** The public Archives of Avalor is the working, player-facing historical reference. The Keeper's Master Canon Bible, Living Chronicle and Compendium Volumes I–II are periodically updated from accumulated, approved additions rather than being rewritten each time a new person, place or story arrives.

**Effective:** 13 November 2026. This is an operational publishing process, not new setting lore. It does not revise the four current candidate PDFs or change existing creator-approved facts.

## The two levels of authority

1. **Keeper's explicit decisions govern the full setting.** A newer creator correction overrides earlier text, including a published page or dated sourcebook. An unresolved or suggested detail is not established by smooth prose.
2. **The published wiki governs what players can currently read as established history.** The wiki must reflect approved, releasable canon promptly. A publication delay does not invalidate the creator's decision, but unpublished information is not permission to disclose it.
3. **Private and public material are different records.** Material from an ongoing campaign, future adventures, unpublished mechanics, twists, or private character motives must never enter the public repository, including a branch, PR description, issue, images, filenames, test fixtures, Git history or source metadata. Redaction after a public commit does not make it secret.
4. **The four Keeper volumes are consolidation targets**, not prerequisites to publishing approved wiki changes. Sourcebook integration happens at the campaign or batch close.

The existing [public editorial override ledger](PUBLIC_CANON_OVERRIDES.md) remains authoritative for its approved historical decisions. New releases are indexed in [the lightweight public canon release log](CANON_PUBLIC_RELEASE_LOG.md), not duplicated into increasingly large narrative audit reports.

## Intake — casual by default

The Keeper may send raw notes, old backstories, session recaps, screenshots, character sheets, dialogue, maps, descriptions, or multiple characters/locations together. **No form or special format is required.** Preserve the original source material and identify its provenance.

For each substantive subject, identify only what is supported:

- Identity and aliases, chronology, place, species and pronouns when supplied
- Role, defining experiences, relationships, motivations and fate when supplied
- Previous connected wiki pages and any genuinely conflicting existing claim
- What is established fact, reported belief or testimony, interpretation, proposed connective writing, or deliberately open
- Whether a detail is approved for publication or belongs to the Keeper alone

Do not ask the Keeper to fill every optional field. Ask a concise question only when a contradiction or publication boundary actually blocks safe writing. Unanswered low-impact details remain omitted or open.

## Assign exactly the treatment each subject deserves

**Level I — Featured / Lavitz treatment.** Major protagonists, lasting antagonists, or places/events with a rich consequential history. A substantial standalone narrative with readable chapters, a supported opening and closing, optional illustrations, and *selective* chapter treatments (turning-point, remembrance, legacy). CMS permits up to three highlighted chapters, four callouts, and three in-article illustrations; these are maxima, not quotas. Editorial reflections are interpretations, not fabricated witnessed quotations. Imagery must be approved and correctly identify its subject.

**Level II — Standard standalone.** Important people, places, institutions or events that deserve a dedicated reference, but whose established material does not justify a showcase. Meaningful sections, clean contextual links, and accurate metadata; colored chapters and callouts only if genuinely useful.

**Level III — Brief entry in an existing collection.** Supporting heroes, adversaries, contacts and neutral figures belong under the appropriate Minor Heroes & Allies, Minor Villains & Adversaries, or Minor Characters heading. Minor places may belong in an established regional or smaller-settlements article; modest organizations and events may likewise fit their existing subject page. Give the entry a stable, linkable heading. Do not make a fresh article just because a person or location has a name.

**Level IV — Connected mention.** A name, event, family link, landmark or passing detail that deserves only a few lines inside an existing article. No redundant stub page.

Depth follows the **quantity and significance of approved story**, not a mechanical word count or character rank. Characters can be promoted from an inline mention to a brief entry or full biography when new source material warrants it. Preserve stable links and redirects if moving an existing entry. Keeper may override the recommended level.

## Repeatable batch workflow

1. **Receive and triage.** Group related notes into a numbered editorial intake batch. Separate established, inferred/proposed, disputed/open, and Keeper-only details. Present proposed substantive inventions for approval instead of turning them into fact.
2. **Choose release boundary.** Finished original-campaign revelations already authorized by the Keeper may be public; ongoing or future-campaign secrets remain private until expressly cleared. If release permission is ambiguous, hold the sensitive detail, not necessarily the whole batch.
3. **Assign a level to each subject.** Draft the page, index entry or connected mention in the established Royal Commission voice. Keep a person-centered biography, not repeated institutional exposition. Do not invent dates, maps, personal motivations, family links or dialogue.
4. **Targeted collision check only.** Compare the new material with its directly related existing articles, established public canon overrides and connected timeline/map/index data. Do not reopen the entire 132-plus-article archive or the four PDFs for every intake.
5. **Update only necessary connections.** Update directly affected related links, index headings, search aliases, redirects, reading journeys, timelines, relationship diagrams, map annotations and galleries **only when supported and relevant**. Never create guessed coordinates or relationships just to make features look complete.
6. **Preview, validate and publish.** Use a small topical PR; review its text for factual drift, unwanted spoilers and fabricated provenance. Run the repository's automated canon/link/build checks, fix any regressions, and merge after publication clearance. Verify GitHub Pages deployment; a successful commit is not proof of a live deployment.
7. **Log and close.** Add one concise row per released batch to the public release log with batch ID, subjects, treatment levels, affected public paths and PR/commit URL. Give the Keeper a short summary of what was published, what was deliberately left untouched and what remains open. Do not trigger another full audit.

Technical checks do not certify narrative truth. Protect existing titles and URLs; metadata, imagery, archive entry numbers, names, dates, faiths and gender/pronouns should all be checked where applicable.

## Lightweight change record

Use an editorial identifier such as **INT-2026-11-13-01**. This is a **real-world editorial ID**, never a date in Avalor. Each intake batch tracks:

- **Public release:** established new facts or approved corrections, relevant subjects, chosen levels, affected article slugs/anchors, related feature edits, and release PR/commit.
- **Superseded:** exactly which old claims have been replaced and why, if applicable.
- **Open:** meaningful missing or disputed items; no guessed answer.
- **Keeper-only:** recorded *outside the public GitHub repository* for later private consolidation.

The public [release log](CANON_PUBLIC_RELEASE_LOG.md) contains only safe-to-publish changes. A Keeper-only queue is not maintained in this public repository.

## Campaign-close Keeper addendum (PDF)

At the Keeper's request, normally **after a campaign or substantial intake batch is complete**, compile a private **Campaign Canon Addendum**. It must be substantive enough to update the Master Bible and Compendiums without reconstructing previous chat discussions. The PDF contains:

1. **Release manifest:** batch IDs, published wiki articles/anchors, PRs, and the exact narrative treatments applied.
2. **Approved setting additions:** organized people, locations, events, factions, artifacts, chronological anchors and important relationships, with original-source provenance where available.
3. **Corrections and supersessions:** old version, new approved fact, implications for nearby stories, and any retcons explicitly authorized by the Keeper.
4. **Keeper-only material:** disclosed privately but not in the wiki; clear spoiler/release status.
5. **Open questions:** what is not settled, without manufactured explanations.
6. **Volume integration map:** what belongs in the Master Canon Bible, Living Chronicle, Compendium I and Compendium II; note that some details belong in one volume but not others.

The PDF is **private Keeper material**. Supply it as a downloadable attachment or maintain it in a user-controlled private location; do not commit it to this public repository. Use one rolling addendum for the active campaign, then revise the master volumes **once the Keeper chooses to close the intake cycle**. A new campaign can start a new addendum.

## How to invoke this in conversation

The Keeper can simply say **"New canon:"** and paste material; even that prefix is optional in an established Avalor wiki conversation. For other outcomes:

- **"Keeper only"** — process privately, do not stage any information in public GitHub.
- **"This replaces the old account"** — treat as a superseding correction and check only direct collisions.
- **"Publish these"** — take approved player-safe material through PR validation and deployment.
- **"Close this campaign's canon"** — generate the private addendum PDF and volume integration map.

**Default operating rule:** Recommend the level, use the smallest canon-safe change set, publish clearly authorized player-visible material, and retain private or unresolved details without blocking unrelated additions. Do not request a new full master-book reconciliation every time the Keeper supplies lore.
