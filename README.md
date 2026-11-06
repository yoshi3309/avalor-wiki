# The Archives of Avalor — Player-facing Wiki

A **free, customizable fantasy encyclopedia** built for GitHub Pages. This repository holds **only player-approved Scholar's Accounts**. It must never contain Keeper's Notes, campaign twists, secret maps, DM-only PDFs, or future campaign plans.

## What is ready now?

- Home page with original lion crest and illustrated skyline.
- 15 interconnected public articles in five categories.
- Search across public article text (Cmd/Ctrl + K).
- At-a-glance information boxes, table of contents, related pages, mobile navigation.
- A public Living Chronicle timeline.
- Browser editing through **Pages CMS** (`.pages.yml`).
- GitHub Actions publication workflow for free GitHub Pages hosting.
- Entire site is static. No subscription, database, login server, or paid CDN is needed.

## 1 — Preview it locally (optional)

The preview PNG files shared with this package show the design. For live navigation and search in a local browser, serve the site with Python:

```bash
python -m pip install -r requirements.txt
python build.py
cd _site
python -m http.server 8000
```

Then open http://localhost:8000 in a browser. To change text, edit any Markdown file under `content/articles`, then run `python build.py` again.

## 2 — Publish for free with GitHub Pages

1. Create a free GitHub account at https://github.com if needed.
2. Create a **PUBLIC** repository, e.g. `avalor-wiki`. A public repo is necessary for GitHub Pages with GitHub Free. **Do not add any restricted source files.**
3. Upload **the contents of this starter folder** (including hidden `.github/workflows` and `.pages.yml`) into the repository root. Do **not** upload the entire ZIP as one file.
4. On GitHub open **Settings → Pages**. Under **Build and deployment**, set **Source = GitHub Actions**.
5. Open **Actions → Publish the Archives of Avalor → Run workflow**, if it hasn't run automatically after the upload. The build generates `_site/` and publishes it.
6. GitHub supplies a URL like `https://YOUR-USERNAME.github.io/avalor-wiki/`. No domain purchase is required. Subsequent edits to Markdown trigger a rebuild automatically.

The site uses relative paths, so it works under any project-repository name or at the root of a domain—no base URL configuration required.

## 3 — Edit articles visually with Pages CMS (free)

1. Visit https://app.pagescms.org and sign in with GitHub.
2. Give Pages CMS access **only to the public Avalor repository**; never authorize or store Keeper files in it.
3. Pages CMS automatically reads `.pages.yml` from the repo root. Open **Public archive articles** to edit/create a page.
4. Edit the title, category, summary, fact box, related article filenames, and article body. Save. Your changes go to GitHub; the Actions workflow republishes the public site.

The editable `body` is normal Markdown; you can also write `[[The Aegis]]` or `[[The Misfits|Misfits]]` to create automatic cross-links to known article titles.

**Important:** The hosted CMS is third party, although its product currently advertises that it is free. Read its access permission screen before authorizing. No passwords or GitHub tokens belong in the project files.

## 4 — Add a new public article

In Pages CMS create an article and save. To add manually, duplicate a file in `content/articles`, rename it to a lowercase-hyphenated slug, and replace its frontmatter and Markdown. Example:

```markdown
---
title: The Great Citadel
subtitle: Seat of the Lion Throne
summary: A historical description suitable for players.
category: Kingdoms & Places
entry: LOC.004
era: Age of Ascendancy
facts: "Location: Renada\nInstitution: Royal government"
related: renada,kingdom-of-avalor
source: Approved Scholar's Account
featured: false
---

## The citadel

The citadel overlooks [[Renada]].
```

### Categories

- Kingdoms & Places
- People & Legends
- Organizations & Factions
- History & Chronicles
- Faith, Magic & Cosmology

## 5 — The non-negotiable security boundary

**PUBLIC REPOSITORY:** This package, the `content/articles` directory, the compiled `_site` and the publicly searchable index. Players can read all of this and inspect its source. Every fact is assumed public, even if it appears only in metadata or a hidden HTML element.

**PRIVATE DM ARCHIVE:** Keep the Master Canon Bible, the Keeper's Editions of Volumes I and II, restricted annotations, character plans, encounter notes, and future campaign material in a **separate private repository or your own local folder**. Create the private repo independently on GitHub, choose **Private**, and do not turn on GitHub Pages for it. No private notes or PDFs are included in this starter package.

**Publication rule:** Only export and publish a scholar-approved text after reviewing it. The script reads `content/articles/*.md` exclusively, never a Keeper PDF; and the search index is built solely from those same public articles. A private folder inside a public repository is *not private*.

## Editorial boundary / historical scope

This starter's articles follow the **Age of Ascendancy**, after the Misfits defeated Cid and at the established Age of Ascendancy historical boundary. Sources consulted for player-approved facts: *The Living Chronicle (Historical Sources Edition)* and the public Scholar's Account portions of *Compendium Volume II (Keeper's Edition)*. The Keeper sections were consulted for continuity and **were not copied**. Entries are concise editorial adaptations, **not full transcriptions** of the source books; review public-facing wording before inviting players.

## Cost

**$0 required** for a public repository, GitHub Pages hosting, the site's code, and the optional Pages CMS editing interface under their currently published free offerings. A custom domain is optional and not included. If you need to restrict website viewers to specific players, GitHub Pages' public hosting does **not** provide password-protected access on the free tier.
## 6 — Add images yourself (no coding)

In [Pages CMS](https://app.pagescms.org), open `yoshi3309/avalor-wiki` and select **Public archive articles**. Open a public article:

- **Main image / character portrait**: choose or upload a JPG, PNG, or WebP. It appears in the illustrated panel alongside the article's facts. Add a useful **Image description** and optional **Image caption or artist credit**.
- **The Scholar's Account**: use the rich-text editor's image tool to insert extra artwork between paragraphs, such as maps, ruins, or tavern illustrations. The editor stores uploaded images in `assets/uploads` automatically.
- Click **Save**. The GitHub Actions workflow rebuilds the website. You never need to edit the code to add art.

**Important:** Every image in the public repository is visible to players. Do not upload secret location maps, villain concept art, or unpublished campaign reveals here. Keep the Keeper archive separate.


## Interactive Atlas of Avalor (The Cartographer's Table)

Open the atlas at `/map/`. It supports zoom/pan, searchable and filtered markers, summaries, hyperlinks to articles, and provisional-location markers. The atlas has no paid map service or external map data provider.

### One-time map artwork upload

The original map was supplied in chat, not through GitHub, so the code does not automatically contain that image. To attach the **exact original artwork**:

1. Visit https://app.pagescms.org and open your `yoshi3309/avalor-wiki` repository.
2. Choose **Map settings & locations** (new section).
3. Find **Map illustration**. Upload the new Avalor PNG (the one with the White Sea, Forest of the Fey, and Great Desert), then Save.
4. The Pages CMS media manager commits it into `assets/uploads/`; GitHub Actions rebuilds the atlas. Your original file is preserved, not redrawn.

### Verify the provisional town locations

1. Open `/map/?edit=1` and press **Position pins** if it isn't already active.
2. Pick Renada, Heaven's Heart, Heroes Hill, Stanleyville, or Shamman’s Tower in **Place to position**.
3. Click the exact location on your illustrated map. The positioning desk shows X and Y coordinates (percentages).
4. Open **Map settings & locations** in Pages CMS, expand that place's entry, and enter its new X/Y. Untick **Mark position as provisional** when you're satisfied; Save.
5. Revisit the atlas. The pin moves and its provisional marker disappears.

The 12 labeled regional/water markers are anchored approximately to their printed labels. You can also move these. Add locations by creating another record in the CMS list; give each an unused lowercase-hyphen key, name, type, coordinates, and optional article filename (without `.md`). For unverified content, set **Show marker to players** to off.

### DM safety

This atlas is **fully public**, including each point's name, description, and image in the underlying GitHub files. Never put Keeper secrets, hidden passages, undiscovered plot locations, private campaign maps, or future encounters in Map settings. A secret or unrevealed location belongs only in the separate private DM archive. Provisional means **uncertain placement**, not hidden or confidential.
