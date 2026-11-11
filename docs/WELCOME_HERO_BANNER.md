# Welcome Banner (main Start Here landing page)

The hero is a purely illustrative image behind the heading `Welcome to Avalor`. The heading, crest, four doorways, and navigation are part of the page itself and are **not** baked into the artwork.

## Updating in Pages CMS

1. Open https://app.pagescms.org/ and select `yoshi3309/avalor-wiki` on `main`.
2. In the content menu, open **Welcome page hero banner**.
3. Under **Hero illustration**, select an existing uploaded image or upload a new public JPEG, PNG, or WebP.
4. Choose **Where to center the illustration**. Default **right center** leaves readable space for the text on the left. Use **center center** for a balanced panorama or **left center** only if you deliberately place the visual subject on the left.
5. Save once. The resulting commit triggers the GitHub Pages publishing pipeline; check the success status before refreshing the website. The home page is https://yoshi3309.github.io/avalor-wiki/.
6. If the upload interface reports an error, first inspect whether the image already appears in Media or the repository commit history before retrying. Do not upload a duplicate until you know the first request failed. A failed *fetch* is a UI/network symptom, not proof that GitHub discarded the write.

Recommended art: 16:9 or wider landscape, 1920×1080, JPG or WebP under 3 MB, with a strong focal subject on the right and dark/quiet negative space on the left. Do not include the welcome title, logo, or navigation text inside the image. The page overlays these independently.

### Technical details
- Editor data: `data/welcome-hero.yml`
- Public image media: `assets/uploads/`
- Builder validates file extension, path, existence and crop choice in `build.py`
- HTML: `templates/welcome.html`
- Responsive crop, darkness and legibility: `assets/welcome.css`
- Fallback: source-controlled `assets/hero-scene.svg` when no image is selected

The banner is separate from the Archive Home hero and separate from the social-share card. A selected image will also inform the main Start Here share preview, but the generated card adds its own editorial layout.
