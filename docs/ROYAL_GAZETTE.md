# Royal Gazette — Phase 6.5

A dated circular of historical and editorial discoveries **in the existing Archives**, not a fictional newspaper. Issue dates are editorial publication dates, never in-world dates expressed in AF.

## Publication
- `/gazette/`: the latest editorial circular and a register of prior editions
- `/gazette/<issue-id>/`: one lead dispatch and two to eight source-linked notes
- The Chronicle sidebar group, the Archive Home, and the Welcome page link to the Gazette.

## Editing
Use Pages CMS → **Royal Gazette issues**, backed by `content/gazette/<id>.yml`. Each issue needs a stable id matching its filename, title, subtitle, quoted ISO date, intro, published flag, and two to eight dispatches. Each dispatch requires a kicker, title, summary, body and an existing article slug as source. Save with `published: false` for drafts; only published issues appear in the live site.

## Integrity
The builder validates IDs, issue dates and source article references. Publishing includes a standalone Gazette test, sitewide link audit, canonical sitemap and unique shareable social previews. Do not fabricate newly enacted decrees, events, dates, quotations or recovered documents to create a headline.