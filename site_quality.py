"""Build-time public sitemap and local integrity audit for Archives of Avalor.

The audit checks only generated, public HTML and files. It makes no network
requests and never reads private setting material. Off-site links are reported
as out of scope rather than assumed valid.
"""
from __future__ import annotations

import json
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree as ET

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', SITEMAP_NS)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicates: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.missing_alt: int = 0
        self.noindex: bool = False
        self.canonical: str | None = None
        self.headings: int = 0

    def handle_starttag(self, tag: str, attrs):
        attrs = dict(attrs)
        ident = attrs.get('id')
        if ident:
            if ident in self.ids:
                self.duplicates.append(ident)
            self.ids.add(ident)
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            self.noindex |= 'noindex' in attrs.get('content', '').lower()
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')
        if tag == 'h1':
            self.headings += 1
        if tag == 'a' and attrs.get('href'):
            self.links.append(('link', attrs['href']))
        if tag in ('img', 'script') and attrs.get('src'):
            self.links.append((tag, attrs['src']))
        if tag == 'img' and 'alt' not in attrs:
            self.missing_alt += 1
        if tag == 'link':
            rel = attrs.get('rel', '').lower().split()
            if any(item in rel for item in ('stylesheet', 'icon', 'preload', 'manifest')) and attrs.get('href'):
                self.links.append(('resource', attrs['href']))
        if tag in ('img', 'source') and attrs.get('srcset'):
            for candidate in attrs['srcset'].split(','):
                url = candidate.strip().split(' ', 1)[0]
                if url:
                    self.links.append(('resource', url))


def public_pages(site: Path) -> list[Path]:
    return sorted(site.rglob('index.html'))


def parsed(path: Path) -> Page:
    document = Page()
    document.feed(path.read_text(encoding='utf-8'))
    return document


def page_url(site: Path, path: Path, base: str) -> str:
    relative = path.relative_to(site)
    if relative.name != 'index.html':
        raise ValueError(f'Not a public HTML index: {relative}')
    segment = relative.parent.as_posix()
    return base.rstrip('/')+'/' + (segment.strip('/') + '/' if segment != '.' else '')


def write_sitemap(site: Path, base: str) -> dict:
    """List only canonical, indexable HTML pages; never merged redirects."""
    site = Path(site)
    base = base.rstrip('/')+'/'
    indexable: list[str] = []
    redirects = 0
    for page in public_pages(site):
        parsed_page = parsed(page)
        if parsed_page.noindex:
            redirects += 1
            continue
        canonical = page_url(site, page, base)
        if parsed_page.canonical != canonical:
            raise ValueError(f'{page}: expected canonical {canonical}, got {parsed_page.canonical}')
        indexable.append(canonical)
    root = ET.Element(f'{{{SITEMAP_NS}}}urlset')
    for url in indexable:
        e = ET.SubElement(root, f'{{{SITEMAP_NS}}}url')
        ET.SubElement(e, f'{{{SITEMAP_NS}}}loc').text = url
    ET.ElementTree(root).write(site/'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (site/'robots.txt').write_text(
        f'User-agent: *\nAllow: /\n\nSitemap: {urljoin(base,"sitemap.xml")}\n',
        encoding='utf-8',
    )
    return {'indexable_pages':len(indexable),'redirects_excluded':redirects}


def audit_site(site: Path, base: str) -> dict:
    """Validate generated local links, chapter fragments, basic HTML semantics."""
    site=Path(site).resolve()
    base=base.rstrip('/')+'/'
    host=urlparse(base).netloc
    prefix=urlparse(base).path
    if not prefix.endswith('/'):
        raise ValueError('Site URL needs a trailing slash')
    errors: list[str] = []
    scanned = 0
    internal_links = 0
    external_links = 0
    image_elements = 0
    missing_alt = 0
    duplicate_ids = 0

    @lru_cache(maxsize=512)
    def inspect(file: Path) -> Page:
        return parsed(file)

    for page in public_pages(site):
        doc=inspect(page)
        scanned += 1
        origin=page_url(site,page,base)
        image_elements += sum(1 for kind, _ in doc.links if kind=='img')
        missing_alt += doc.missing_alt
        if doc.duplicates:
            duplicate_ids += len(doc.duplicates)
            errors.append(f'{page.relative_to(site)}: repeated HTML ID(s): {", ".join(doc.duplicates[:6])}')
        if doc.missing_alt:
            errors.append(f'{page.relative_to(site)}: {doc.missing_alt} image(s) lack alt attributes')
        if not doc.noindex and doc.headings != 1:
            errors.append(f'{page.relative_to(site)}: expected one page h1, found {doc.headings}')

        for kind, raw in doc.links:
            raw=raw.strip()
            if not raw or raw == '#':
                continue
            if raw.startswith(('data:', 'blob:', 'mailto:', 'tel:')):
                continue
            if raw.lower().startswith('javascript:'):
                errors.append(f'{page.relative_to(site)}: unsafe javascript: URL in {kind}')
                continue
            resolved=urlparse(urljoin(origin,raw))
            if resolved.scheme not in ('http','https'):
                continue
            if resolved.netloc != host or not resolved.path.startswith(prefix):
                external_links += 1
                continue
            internal_links += 1
            relative=unquote(resolved.path[len(prefix):])
            target=(site/relative).resolve()
            if not target.is_relative_to(site):
                errors.append(f'{page.relative_to(site)}: link escapes public root: {raw}')
                continue
            if resolved.path.endswith('/') or target.is_dir():
                target = target / 'index.html'
            elif not target.suffix:
                target = target / 'index.html'
            if not target.is_file():
                errors.append(f'{page.relative_to(site)}: broken {kind}: {raw}')
                continue
            if kind == 'link' and resolved.fragment and target.suffix.lower()=='.html':
                fragment=unquote(resolved.fragment)
                if fragment not in inspect(target).ids:
                    errors.append(f'{page.relative_to(site)}: missing destination chapter #{fragment}: {raw}')

    report = {
        'pages_checked':scanned,
        'local_references_checked':internal_links,
        'external_references_not_checked':external_links,
        'image_elements':image_elements,
        'missing_image_alt':missing_alt,
        'duplicate_ids':duplicate_ids,
        'issue_count':len(errors),
        'issues':errors[:150],
    }
    (site/'quality-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
