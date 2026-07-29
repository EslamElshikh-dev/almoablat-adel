#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def fail(path: Path, message: str) -> None:
    ERRORS.append(f"{path.relative_to(ROOT)}: {message}")


def warn(path: Path, message: str) -> None:
    WARNINGS.append(f"{path.relative_to(ROOT)}: {message}")


def extract(pattern: str, text: str, flags: int = 0) -> list[str]:
    return re.findall(pattern, text, flags)


html_files = sorted(ROOT.rglob('*.html'))
titles: dict[str, Path] = {}
canonicals: dict[str, Path] = {}

for path in html_files:
    text = path.read_text(encoding='utf-8')
    is_404 = path.name == '404.html'
    if '<html lang="ar-SA" dir="rtl"' not in text:
        fail(path, 'lang/dir غير مضبوطين')
    h1s = extract(r'<h1(?:\s[^>]*)?>(.*?)</h1>', text, re.I | re.S)
    if len(h1s) != 1:
        fail(path, f'عدد H1 = {len(h1s)} بدل 1')
    title_match = extract(r'<title>(.*?)</title>', text, re.I | re.S)
    if len(title_match) != 1:
        fail(path, 'عنوان الصفحة مفقود أو مكرر')
    else:
        title = re.sub(r'<[^>]+>', '', title_match[0]).strip()
        if title in titles:
            fail(path, f'عنوان مكرر مع {titles[title].relative_to(ROOT)}')
        titles[title] = path
    descriptions = extract(r'<meta\s+name="description"\s+content="([^"]+)"', text, re.I)
    if len(descriptions) != 1:
        fail(path, 'Meta description مفقود أو مكرر')
    elif len(descriptions[0]) < 70:
        warn(path, 'Meta description قصير')
    canonical_match = extract(r'<link\s+rel="canonical"\s+href="([^"]+)"', text, re.I)
    if len(canonical_match) != 1:
        fail(path, 'Canonical مفقود أو مكرر')
    else:
        canonical = canonical_match[0]
        if canonical in canonicals:
            fail(path, f'Canonical مكرر مع {canonicals[canonical].relative_to(ROOT)}')
        canonicals[canonical] = path
    for block in extract(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.I | re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            fail(path, f'JSON-LD غير صالح: {exc}')
    for img in extract(r'<img\s+[^>]*>', text, re.I):
        if not re.search(r'\salt="[^"]*"', img, re.I):
            fail(path, 'صورة بدون alt')
    for href in extract(r'<a\s+[^>]*href="([^"]+)"', text, re.I):
        if href.startswith(('#', 'http://', 'https://', 'tel:', 'mailto:', 'javascript:')):
            continue
        clean = unquote(href.split('#', 1)[0].split('?', 1)[0])
        if not clean:
            continue
        target = (path.parent / clean).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            fail(path, f'رابط يخرج من مجلد الموقع: {href}')
            continue
        if target.is_dir():
            target = target / 'index.html'
        elif target.suffix == '':
            target = target / 'index.html'
        if not target.exists():
            fail(path, f'رابط داخلي غير موجود: {href}')
    if not is_404 and 'index,follow' not in text:
        fail(path, 'صفحة قابلة للفهرسة بدون index,follow')

js_path = ROOT / 'assets/js/app.js'
if not js_path.exists():
    ERRORS.append('assets/js/app.js: الملف مفقود')
else:
    js = js_path.read_text(encoding='utf-8')
    if '```' in js:
        ERRORS.append('assets/js/app.js: يحتوي علامات Markdown')
    if '[data-whatsapp-form]' not in js:
        ERRORS.append('assets/js/app.js: ربط نموذج واتساب مفقود')

sitemap_path = ROOT / 'sitemap.xml'
if not sitemap_path.exists():
    ERRORS.append('sitemap.xml: الملف مفقود')
else:
    sitemap = sitemap_path.read_text(encoding='utf-8')
    locs = extract(r'<loc>(.*?)</loc>', sitemap)
    indexable_html = [p for p in html_files if p.name != '404.html']
    if len(locs) != len(indexable_html):
        ERRORS.append(f'sitemap.xml: عدد الروابط {len(locs)} لا يساوي الصفحات القابلة للفهرسة {len(indexable_html)}')

for required in ['robots.txt', 'manifest.webmanifest', 'vercel.json', 'assets/css/style.css', 'assets/images/logo-mark.svg']:
    if not (ROOT / required).exists():
        ERRORS.append(f'{required}: ملف مطلوب مفقود')

print(f'HTML pages: {len(html_files)}')
print(f'Unique titles: {len(titles)}')
print(f'Unique canonicals: {len(canonicals)}')
if WARNINGS:
    print('\nWarnings:')
    for item in WARNINGS:
        print(f'- {item}')
if ERRORS:
    print('\nErrors:')
    for item in ERRORS:
        print(f'- {item}')
    sys.exit(1)
print('\nPASS: site structure, metadata, JSON-LD, links, images and sitemap validated.')
