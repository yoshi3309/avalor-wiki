"""Public-only social preview cards for Discord, social media, and link unfurls.

All rendered images use confirmed public article/gallery assets or neutral
Archive branding. No hidden campaign data, new character art, or external fetches.
"""
from __future__ import annotations
import base64
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

SIZE = (1200, 630)
GOLD = (225, 188, 127)
CREAM = (244, 231, 203)
MUTED = (183, 199, 192)
PUBLIC_IMAGES = re.compile(r"assets/uploads/[a-zA-Z0-9_./-]+\.(?:png|jpg|jpeg|webp|gif)$", re.I)


def font(size: int, serif: bool = False, bold: bool = False):
    variants = (
        ['DejaVuSerif-Bold.ttf', 'DejaVuSerif.ttf'] if serif and bold else
        ['DejaVuSerif.ttf'] if serif else
        ['DejaVuSans-Bold.ttf', 'DejaVuSans.ttf'] if bold else
        ['DejaVuSans.ttf']
    )
    for name in variants:
        for location in (f'/usr/share/fonts/truetype/dejavu/{name}', name):
            try:
                return ImageFont.truetype(location, size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_lines(draw, text: str, f, max_width: int, max_lines: int):
    words = ' '.join(str(text).split()).split(' ')
    lines = []
    current = ''
    for word in words:
        attempt = (current + ' ' + word).strip()
        if draw.textlength(attempt, font=f) <= max_width:
            current = attempt
        else:
            if current:
                lines.append(current)
                current = word
            else:
                # Long technical terms can wrap safely without clipping.
                part = ''
                for ch in word:
                    if part and draw.textlength(part + ch, font=f) > max_width:
                        lines.append(part)
                        part = ch
                    else:
                        part += ch
                current = part
    if current:
        lines.append(current)
    if len(lines) <= max_lines:
        return lines
    result = lines[:max_lines]
    final = result[-1]
    while final and draw.textlength(final + '…', font=f) > max_width:
        final = final[:-1]
    result[-1] = final.rstrip(' .,') + '…'
    return result


def image_source(root: Path, raw: str | None):
    """Accept only actual source files within the already public uploads dir."""
    path = str(raw or '').strip().lstrip('/')
    while path.startswith('../'):
        path = path[3:]
    if not PUBLIC_IMAGES.fullmatch(path) or '..' in Path(path).parts:
        return None
    actual = root / path
    return actual if actual.is_file() else None


def lion_crest(root: Path):
    """The existing public SVG wraps the approved lion drawing as embedded PNG."""
    path = root / 'assets' / 'crest.svg'
    try:
        svg = path.read_text(encoding='utf-8')
        embedded = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', svg)
        if embedded:
            with Image.open(io.BytesIO(base64.b64decode(embedded.group(1)))) as icon:
                return icon.convert('RGBA')
    except (OSError, ValueError):
        pass
    return None


def card(root: Path, site: Path, key: str, title: str,
         description: str, category: str, artwork: str | None = None):
    """Render a single 1200x630 JPEG with legible title and approved imagery."""
    clean_key = key.strip('/')
    if not clean_key or any(not re.fullmatch(r'[a-z0-9-]+', part) for part in clean_key.split('/')):
        raise ValueError('Unsafe social card path: ' + key)
    dest = site / 'assets' / 'social' / (clean_key + '.jpg')
    dest.parent.mkdir(parents=True, exist_ok=True)

    canvas = Image.new('RGB', SIZE, (14, 29, 39))
    draw = ImageDraw.Draw(canvas)
    for y in range(SIZE[1]):
        blend = y / SIZE[1]
        draw.line((0, y, 1200, y), fill=(int(16 + blend * 4), int(31 + blend * 8), int(41 + blend * 8)))

    photo_file = image_source(root, artwork)
    with_photo = bool(photo_file)
    if photo_file:
        try:
            with Image.open(photo_file) as opened:
                picture = ImageOps.exif_transpose(opened)
                if getattr(opened, 'is_animated', False):
                    picture.seek(0)
                picture = picture.convert('RGB')
                picture = ImageOps.fit(picture, (505, 630), method=Image.Resampling.LANCZOS, centering=(.5, .40))
                canvas.paste(picture, (695, 0))
        except (OSError, ValueError):
            with_photo = False
    draw = ImageDraw.Draw(canvas, 'RGBA')
    if with_photo:
        # Maintain text contrast and blend the image into the archival panel.
        draw.rectangle((695, 0, 1200, 630), fill=(8, 19, 26, 58))
        for x in range(620, 950, 3):
            opacity = int(245 * (1 - (x-620)/330)**2)
            draw.rectangle((x, 0, x+3, 630), fill=(15, 30, 40, opacity))
        draw.line((1158, 30, 1158, 601), fill=(225, 188, 127, 145), width=2)
    else:
        # Neutral heraldic design without representing any specific event or character.
        for radius in (160, 225, 300, 385):
            draw.ellipse((1070-radius,315-radius,1070+radius,315+radius),
                         outline=(203, 164, 97, 33), width=2)
        draw.line((900, 60, 900, 580), fill=(210, 174, 112, 55), width=2)

    draw.rectangle((0, 0, 1199, 629), outline=(209, 166, 101, 165), width=3)
    draw.line((47, 51, 1151, 51), fill=(196, 158, 98, 100), width=2)
    draw.line((47, 578, 1151, 578), fill=(196, 158, 98, 125), width=2)

    crest = lion_crest(root)
    if crest:
        crest.thumbnail((70, 70), Image.Resampling.LANCZOS)
        canvas.paste(crest, (64, 75), crest)
    draw = ImageDraw.Draw(canvas)
    draw.text((145, 85), 'THE ARCHIVES OF AVALOR', font=font(24, bold=True), fill=CREAM)
    draw.text((145, 123), 'THE ROYAL COMMISSION  /  SCHOLAR’S EDITION',
              font=font(12, bold=True), fill=GOLD)

    max_text_width = 670 if with_photo else 950
    tag = ('PUBLIC ARCHIVE  /  ' + str(category).upper()).strip()
    tag_font = font(16, bold=True)
    if draw.textlength(tag, font=tag_font) > max_text_width:
        tag = 'PUBLIC ARCHIVE'
    draw.text((66, 189), tag, font=tag_font, fill=GOLD)
    draw.line((66, 224, 164, 224), fill=GOLD, width=3)

    title = ' '.join(str(title or 'Avalor').split())
    size = 69
    while size >= 38:
        face = font(size, serif=True, bold=True)
        title_lines = fit_lines(draw, title, face, max_text_width, 3)
        # Aim for up to three lines without pushing summary off the card.
        h = int(size * 1.12)
        fits = sum(len(x) for x in title_lines) >= min(len(title), 10)
        if fits and len(title_lines) * h <= 226:
            break
        size -= 2
    y = 249
    for line in title_lines:
        draw.text((65, y), line, font=face, fill=CREAM, stroke_width=0)
        y += int(size * 1.11)

    subtitle_font = font(19)
    subtitle_lines = fit_lines(draw, description or 'Discover the public records of Avalor.',
                               subtitle_font, max_text_width, 2)
    y = min(max(y+20, 444), 477)
    for line in subtitle_lines:
        draw.text((68, y), line, font=subtitle_font, fill=MUTED)
        y += 29

    draw.text((66, 595), 'EXPLORE THE ROYAL ARCHIVES', font=font(12, bold=True), fill=GOLD)
    draw.text((455, 595), 'AVALOR-WIKI', font=font(12, bold=True), fill=CREAM)
    # The shadowed image panel already uses approved public art; never add
    # character labels that aren't present in the page's own public metadata.
    canvas.save(dest, 'JPEG', quality=85, optimize=True, progressive=True, subsampling=0)
    return 'assets/social/' + clean_key + '.jpg'
