# Discord & Social Link Previews — Public Archive

Every public page receives Open Graph metadata in server-rendered HTML and a landscape preview JPEG at 1200 × 630 pixels. This works for Discord and other link-unfurl bots that do not execute JavaScript.

## Metadata

The base template includes:
- A canonical absolute HTTPS page URL ending in a slash.
- Open Graph site name, type, title, description, URL, image, image type, image width/height, and image alt text.
- Twitter large-card metadata.
- A self-contained source-controlled public JPEG in _site/assets/social/ per page, not a remote image.

The default site base is https://yoshi3309.github.io/avalor-wiki/ and can be overridden by AVALOR_SITE_URL for future custom domains. Do not change the base without updating the real public deployment. Every image URL is absolute, including nested encyclopedia and exhibition pages.

## Image selection and canon

- Article pages use their approved header image where present, otherwise the first illustration linked by a published Gallery record, if one exists.
- A gallery collection page uses its published cover. The general gallery uses its first approved illustration.
- Maps and the homepage may use the official approved public map.
- Reading journeys use an approved image for their first published step, where available.
- Pages with no suitable image—including documentary exhibits that do not have photographs of genuine original documents—use a decorative heraldic composition.
- Social cards use existing public uploaded images only from assets/uploads, and the Archives' existing decorative lion crest. No Keeper notes, PDFs, private folders, or remote artwork are used. No claims are inferred from an image filename.

## Maintenance

- Running python build.py creates the social images along with the rest of the static site. The build script calls social_cards.card inside the general public render function so new CMS articles receive a preview automatically.
- Editing an article's title, summary, or approved artwork regenerates its preview on the next deploy. Discord may cache older previews. To refresh, use the published link with an innocuous version query parameter (e.g. ?v=2) when necessary or allow its cache to expire. The canonical metadata URL remains stable.
- The check_social_previews.py test confirms that generated JPEG paths exist, are 1200x630 pixels, and have valid absolute Open Graph/Twitter values.
- Run the GitHub Actions site build before announcing social previews as live.

## Scope and limits

This is a technical OG-image implementation, not an automated human review of each character composition. Crop, text fit, contrast, accessibility, and Discord's actual embed behavior should be checked with several live links (e.g. Lavitz, the Six, Renada, the map and historical exhibits). A static site cannot force Discord to immediately invalidate a cached preview.
