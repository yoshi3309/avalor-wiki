# Responsive public imagery and mobile performance

The Archives build now generates smaller WebP variants for existing public raster uploads without changing or deleting original artwork.

## Workflow

- Source uploads live in assets/uploads and remain publicly accessible at the same URLs.
- Running python build.py generates WebP previews at widths up to 480, 960, and 1440 pixels under _site/assets/optimized/uploads. The build preserves aspect ratio and transparency.
- Generated previews live only in the build output, **not** the Git repository. They regenerate when the site is rebuilt, including new CMS uploads.
- Gallery collections, gallery cards, related illustrations, and article portraits use HTML picture elements with a WebP source set plus a source-preserving fallback image. The same mechanism covers inline CMS figures and ordinary Markdown article images.
- Opening a gallery image uses a larger WebP preview on supported browsers, while **View original full-resolution artwork** gives access to the untouched file. The official cartographic map deliberately uses the original in the large gallery viewer for detail and label fidelity.
- Intrinsic width and height reduce image layout shift; image tags below the fold have lazy loading and asynchronous decoding.
- SVG artwork remains a vector, GIF/animated assets are not converted, and the source bytes are never overwritten.
- The generator creates _site/media-report.json as a build report: image counts, original bytes, preview bytes, a **potential** preview savings estimate, and each variant path. The percentage is NOT a measured real-world Core Web Vitals result or total-page savings.
- Python Pillow is a bounded-major CI dependency, and changes to media_optimization.py trigger a GitHub Pages rebuild.

## Safety and maintenance

- Only files already under the explicitly public assets/uploads directory are examined; no DM folders, external network requests, or new canon are involved.
- Do not delete originals, rename URLs, add invented artworks, strip image alt text, or crop accepted visuals.
- Original format is retained as a fallback for browsers without WebP support.
- CI runs tests/check_media_performance.py, which checks variants exist, aspect ratios are preserved, alternative text remains in public HTML, and full-resolution links remain available.

## Remaining real-device verification

Manual checking is still recommended on iPhone Safari and Android Chrome with slow connections, high zoom, VoiceOver/TalkBack, and the map viewer at high zoom. A Lighthouse baseline and measured mobile Core Web Vitals would be useful before claiming specific page-load speed improvements.
