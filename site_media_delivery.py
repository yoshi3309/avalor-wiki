"""Publish optimized media while retaining full-resolution uploads in the CMS source.

Source files in assets/uploads remain untouched in GitHub, so editors can keep
using Pages CMS and all article frontmatter can retain stable source paths.
Only the _site output substitutes existing responsive WebPs for the large
originals. The high-detail official map is the sole permanent full-res exception.
"""
from __future__ import annotations

import json
from pathlib import Path

TEXT_OUTPUTS = {".html", ".css", ".js", ".json", ".xml", ".txt", ".svg"}
PRESERVED = {"assets/uploads/avalor-official-map.webp"}
REPORT_NAMES = {"media-report.json", "media-delivery-report.json", "quality-report.json"}


def publish_optimized_media(site: Path, catalog: dict) -> dict:
    replacements = {}
    for original, meta in catalog.items():
        if original in PRESERVED or meta.get("modal_original"):
            continue
        variants = meta.get("variants") or []
        if variants:
            replacements[original] = max(variants, key=lambda v: v["width"])["path"]

    # Transform rendered references only. Source Markdown, CMS config, and
    # originals remain unchanged for subsequent edits and future re-exports.
    # This includes embedded gallery JSON, article portrait data, inline links,
    # styles and generated home-page media URLs.
    changed_files = 0
    for output in site.rglob("*"):
        if not output.is_file() or output.suffix.lower() not in TEXT_OUTPUTS:
            continue
        if output.name in REPORT_NAMES:
            continue
        try:
            before = output.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        after = before
        for old, new in replacements.items():
            if old in after:
                after = after.replace(old, new)
        if after != before:
            output.write_text(after, encoding="utf-8")
            changed_files += 1

    bytes_excluded = 0
    originals_removed = 0
    for original in replacements:
        published_original = site / original
        if published_original.is_file():
            bytes_excluded += published_original.stat().st_size
            published_original.unlink()
            originals_removed += 1

    # Fail closed if any published page or script still points to an original
    # that has been omitted; site_quality also checks HTML local references.
    for output in site.rglob("*"):
        if not output.is_file() or output.suffix.lower() not in TEXT_OUTPUTS:
            continue
        if output.name in REPORT_NAMES:
            continue
        content = output.read_text(encoding="utf-8")
        for original in replacements:
            if original in content:
                raise ValueError(f"Unconverted media reference in {output}: {original}")

    remaining = {
        "count": sum(1 for p in (site / "assets" / "uploads").rglob("*") if p.is_file()),
        "bytes": sum(p.stat().st_size for p in (site / "assets" / "uploads").rglob("*") if p.is_file()),
    }
    site_bytes = sum(p.stat().st_size for p in site.rglob("*") if p.is_file())
    result = {
        "originals_replaced": originals_removed,
        "bytes_excluded": bytes_excluded,
        "rendered_files_updated": changed_files,
        "remaining_originals": remaining,
        "published_site_bytes": site_bytes,
    }
    (site / "media-delivery-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # The final package must not approach the Pages 1 GB ceiling unnoticed.
    if site_bytes > 900_000_000:
        raise ValueError(f"Published site is too large: {site_bytes:,} bytes")
    return result
