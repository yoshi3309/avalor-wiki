"""Generate responsive public artwork from already-approved CMS uploads.

The build never mutates originals, crops subjects, or adds artwork. Public assets
remain available at their existing paths for full-resolution inspection.
"""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError

WIDTHS = (480, 960, 1440)
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}


def generate_media(root: Path, site: Path) -> dict:
    assets = root / 'assets' / 'uploads'
    out = site / 'assets' / 'optimized' / 'uploads'
    catalog: dict[str, dict] = {}
    input_bytes = 0
    preview_bytes = 0
    for source in sorted(assets.rglob('*')):
        if not source.is_file() or source.suffix.lower() not in EXTENSIONS:
            continue
        relative = source.relative_to(assets)
        public_path = 'assets/uploads/' + relative.as_posix()
        try:
            with Image.open(source) as opened:
                if getattr(opened, 'is_animated', False):
                    continue
                photo = ImageOps.exif_transpose(opened)
                # Preserve source transparency, avoiding halos around character art.
                if photo.mode in ('RGBA', 'LA') or 'transparency' in photo.info:
                    photo = photo.convert('RGBA')
                else:
                    photo = photo.convert('RGB')
                orig_width, orig_height = photo.size
                if not orig_width or not orig_height:
                    raise ValueError(f'Image has invalid dimensions: {public_path}')
                variants = []
                for preferred in WIDTHS:
                    actual_width = min(preferred, orig_width)
                    if any(variant['width'] == actual_width for variant in variants):
                        continue
                    target = photo.copy()
                    target.thumbnail((actual_width, orig_height), Image.Resampling.LANCZOS)
                    destination = out / relative.parent / f'{source.stem}-w{target.width}.webp'
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    target.save(destination, 'WEBP', quality=81, method=4, exact=True)
                    variant_path = 'assets/optimized/uploads/' + (relative.parent / destination.name).as_posix()
                    variants.append({
                        'path': variant_path, 'width': target.width,
                        'height': target.height, 'bytes': destination.stat().st_size,
                    })
                variants.sort(key=lambda item: item['width'])
                original_size = source.stat().st_size
                catalog[public_path] = {
                    'width': orig_width, 'height': orig_height,
                    'original_bytes': original_size,
                    'variants': variants,
                    # Maps are normally viewed for labels and precision:
                    # use the existing original in the large viewer.
                    'modal_original': source.name == 'avalor-official-map.webp',
                }
                input_bytes += original_size
                if variants:
                    preview_bytes += variants[0]['bytes']
        except (UnidentifiedImageError, OSError, ValueError) as err:
            raise ValueError(f'Cannot prepare public image {public_path}: {err}') from err
    stats = {
        'image_count': len(catalog),
        'source_total_bytes': input_bytes,
        'preview_total_bytes': preview_bytes,
        'potential_preview_savings_pct':
            round(100*(1-preview_bytes/input_bytes),1) if input_bytes else 0,
        'items': catalog,
    }
    (site / 'media-report.json').write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return catalog
