#!/usr/bin/env python3
"""Build the featured blog carousel and static, crawlable archive pagination."""

from __future__ import annotations

import html
import json
import math
import re
from datetime import date
from pathlib import Path

import generate_blog_expansion as shared
from blog_articles_data import ARTICLES as EXPANSION_ARTICLES
from generate_blog_expansion import OLD_ARTICLES
from local_seo_articles_data import ARTICLES as LOCAL_ARTICLES


ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
BASE_URL = "https://almoablat-adel.vercel.app"
PAGE_SIZE = 10
UPDATED = "2026-08-23"
STYLE_VERSION = "20260823-promo-assistant"

FEATURED_SLUGS = [
    "best-tiler-in-riyadh",
    "riyadh-tiler-complete-services",
    "floor-tiler-riyadh",
    "bathroom-tiler-riyadh",
    "best-tile-contractor-riyadh",
]

MONTHS = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "مايو",
    6: "يونيو",
    7: "يوليو",
    8: "أغسطس",
    9: "سبتمبر",
    10: "أكتوبر",
    11: "نوفمبر",
    12: "ديسمبر",
}


def plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def match(pattern: str, source: str, label: str) -> str:
    result = re.search(pattern, source, re.S | re.I)
    if not result:
        raise RuntimeError(f"Missing {label}")
    return result.group(1).strip()


def article_order() -> dict[str, int]:
    ordered = [
        *(article["slug"] for article in LOCAL_ARTICLES),
        *(article["slug"] for article in EXPANSION_ARTICLES),
        *(article["slug"] for article in OLD_ARTICLES),
    ]
    return {slug: index for index, slug in enumerate(ordered)}


def collect_articles() -> list[dict]:
    order = article_order()
    articles: list[dict] = []
    for page in BLOG.glob("*/index.html"):
        if page.parent.name == "page":
            continue
        source = page.read_text(encoding="utf-8")
        published = match(
            r'<meta property="article:published_time" content="([^"]+)"',
            source,
            f"published date in {page}",
        )
        published_date = date.fromisoformat(published)
        articles.append(
            {
                "slug": page.parent.name,
                "title": plain(match(r"<h1(?:\s[^>]*)?>(.*?)</h1>", source, f"H1 in {page}")),
                "description": html.unescape(
                    match(
                        r'<meta name="description" content="([^"]+)"',
                        source,
                        f"description in {page}",
                    )
                ),
                "image": match(r'<meta property="og:image" content="([^"]+)"', source, f"image in {page}"),
                "category": html.unescape(
                    match(
                        r'<meta property="article:section" content="([^"]+)"',
                        source,
                        f"section in {page}",
                    )
                ),
                "minutes": int(
                    match(
                        r'<div class="article-meta hero-meta">.*?<span>(\d+) دقائق قراءة</span>',
                        source,
                        f"reading time in {page}",
                    )
                ),
                "published": published,
                "published_date": published_date,
                "display_date": f"{published_date.day} {MONTHS[published_date.month]} {published_date.year}",
                "editorial_order": order.get(page.parent.name, 10_000),
            }
        )
    articles.sort(key=lambda item: (-item["published_date"].toordinal(), item["editorial_order"]))
    return articles


def arrow_icon(direction: str) -> str:
    path = "m15 18-6-6 6-6" if direction == "right" else "m9 18 6-6-6-6"
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'<path d="{path}"/></svg>'
    )


def render_card(article: dict, href_prefix: str, featured: bool = False) -> str:
    href = f'{href_prefix}{article["slug"]}/'
    badge = '<span class="featured-badge">مختار</span>' if featured else ""
    card_class = "article-card featured-article-card" if featured else "article-card archive-article-card"
    return f'''<article class="{card_class}" data-published="{article["published"]}">
<a class="card-media" href="{href}" aria-label="{shared.esc(article["title"])}">{badge}<img src="{article["image"]}" width="1200" height="800" loading="lazy" decoding="async" alt="{shared.esc(article["title"])}"><span class="media-fallback" aria-hidden="true"></span></a>
<div class="card-content"><div class="article-meta"><span>{shared.esc(article["category"])}</span><span><time datetime="{article["published"]}">{article["display_date"]}</time></span><span>{article["minutes"]} دقائق قراءة</span></div><h3><a href="{href}">{shared.esc(article["title"])}</a></h3><p>{shared.esc(article["description"])}</p><div class="blog-card-footer"><a class="text-link" href="{href}">قراءة المقال {arrow_icon("left")}</a></div></div>
</article>'''


def page_href(target: int, current: int) -> str:
    if current == 1:
        return "./" if target == 1 else f"./page/{target}/"
    return "../../" if target == 1 else f"../{target}/"


def render_pagination(current: int, total: int) -> str:
    parts = ['<nav class="blog-pagination" aria-label="صفحات المقالات">']
    if current > 1:
        parts.append(
            f'<a class="pagination-direction" href="{page_href(current - 1, current)}" rel="prev">'
            f'{arrow_icon("right")}<span>الأحدث</span></a>'
        )
    else:
        parts.append('<span class="pagination-direction is-disabled" aria-hidden="true">'
                     f'{arrow_icon("right")}<span>الأحدث</span></span>')
    parts.append('<div class="pagination-numbers" aria-label="أرقام الصفحات">')
    for number in range(1, total + 1):
        if number == current:
            parts.append(f'<span class="pagination-number is-current" aria-current="page">{number}</span>')
        else:
            parts.append(
                f'<a class="pagination-number" href="{page_href(number, current)}" '
                f'aria-label="الانتقال إلى الصفحة {number}">{number}</a>'
            )
    parts.append("</div>")
    if current < total:
        parts.append(
            f'<a class="pagination-direction" href="{page_href(current + 1, current)}" rel="next">'
            f'<span>الأقدم</span>{arrow_icon("left")}</a>'
        )
    else:
        parts.append('<span class="pagination-direction is-disabled" aria-hidden="true">'
                     f'<span>الأقدم</span>{arrow_icon("left")}</span>')
    parts.append("</nav>")
    return "".join(parts)


def render_featured(articles: list[dict]) -> str:
    cards = "".join(render_card(article, "./", featured=True) for article in articles)
    dots = "".join(
        f'<button type="button" data-featured-dot="{index}" aria-label="عرض المقال المختار {index + 1}"'
        f'{" aria-current=\"true\"" if index == 0 else ""}></button>'
        for index in range(len(articles))
    )
    return f'''<section class="section featured-articles-section" aria-labelledby="featured-title">
<div class="container"><div class="featured-heading"><div><span class="eyebrow">مختارات تساعدك على القرار</span><h2 id="featured-title">أفضل 5 مقالات في المدونة</h2><p>أدلة أساسية تجمع أكثر الأسئلة أهمية قبل اختيار المبلط أو بدء تركيب الأرضيات والحمامات في الرياض.</p></div><div class="featured-controls" aria-label="التحكم في المقالات المختارة"><button type="button" data-featured-prev aria-label="المقال السابق">{arrow_icon("right")}</button><button type="button" data-featured-next aria-label="المقال التالي">{arrow_icon("left")}</button></div></div>
<div class="featured-carousel" data-featured-carousel><div class="featured-articles-track" data-featured-track tabindex="0" aria-label="المقالات المختارة">{cards}</div><div class="featured-carousel-footer"><div class="featured-dots" aria-label="اختيار مقال مميز">{dots}</div><span class="sr-only" data-featured-status aria-live="polite">المقال 1 من {len(articles)}</span><span class="carousel-hint">يتحرك تلقائيًا ويمكنك السحب للتصفح</span></div></div></div>
</section>'''


def render_hero(page_number: int, article_count: int) -> str:
    if page_number == 1:
        eyebrow = "مقالات متخصصة للسوق السعودي"
        heading = "مدونة البلاط والسيراميك والتشطيبات"
        summary = "محتوى عملي يساعدك على اختيار الخامة وفهم خطوات التنفيذ وفحص الأعمال قبل الاستلام، مع موضوعات محلية مرتبطة بخدمات البلاط والعزل والترميم في الرياض."
    else:
        eyebrow = "أرشيف المقالات مرتب زمنيًا"
        ordinal = "الثانية" if page_number == 2 else "الثالثة" if page_number == 3 else str(page_number)
        heading = f"مقالات البلاط والتشطيبات – الصفحة {ordinal}"
        summary = "تابع أدلة التركيب والعزل والترميم مرتبة من الأحدث إلى الأقدم، وانتقل بين الصفحات دون إخفاء أي مقال من المدونة."
    return f'''<section class="page-hero blog-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{eyebrow}</span><h1>{heading}</h1><p>{summary}</p><div class="hero-actions"><a class="button button-primary" href="https://wa.me/966567372527?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D9%82%D8%B1%D8%A3%D8%AA%20%D8%A3%D8%AD%D8%AF%20%D9%85%D9%82%D8%A7%D9%84%D8%A7%D8%AA%20%D8%A7%D9%84%D9%85%D8%AF%D9%88%D9%86%D8%A9%20%D9%88%D8%A3%D8%AD%D8%AA%D8%A7%D8%AC%20%D8%A7%D8%B3%D8%AA%D8%B4%D8%A7%D8%B1%D8%A9%20%D9%84%D9%85%D8%B4%D8%B1%D9%88%D8%B9%D9%8A" target="_blank" rel="noopener">اطلب الخدمة عبر واتساب</a><a class="button button-secondary" href="tel:0567372527">اتصال مباشر</a></div></div><div class="hero-visual editorial-visual" aria-label="مزايا المدونة"><svg class="huge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v14H4zM8 9h8M8 13h8M8 17h5"/></svg><div><strong>{article_count}</strong><span>مقالًا كاملًا</span></div><div><strong>SEO</strong><span>بحث محلي منظم</span></div></div></div></section>'''


def render_listing(articles: list[dict], current: int, total: int, href_prefix: str) -> str:
    cards = "".join(render_card(article, href_prefix) for article in articles)
    start = 1 + (current - 1) * PAGE_SIZE
    end = start + len(articles) - 1
    title = "أحدث المقالات" if current == 1 else f"أرشيف المقالات – الصفحة {current}"
    return f'''<section class="section blog-listing-section" aria-labelledby="latest-articles-title"><div class="container"><div class="blog-archive-heading"><div><span class="eyebrow">من الأحدث إلى الأقدم</span><h2 id="latest-articles-title">{title}</h2><p>بطاقات كاملة وواضحة لكل مقال؛ اختر الموضوع الأقرب لمشروعك وانتقل بين صفحات الأرشيف بسهولة.</p></div><span class="archive-range" aria-label="المقالات المعروضة">عرض {start}–{end}</span></div><div class="cards-grid article-grid blog-grid">{cards}</div>{render_pagination(current, total)}</div></section>'''


def schema_graph(page_number: int, page_articles: list[dict], featured: list[dict]) -> list[dict]:
    canonical = f"{BASE_URL}/blog/" if page_number == 1 else f"{BASE_URL}/blog/page/{page_number}/"
    title = (
        "مدونة البلاط والسيراميك في الرياض | المبلط عادل"
        if page_number == 1
        else f"مقالات البلاط في الرياض – الصفحة {page_number} | المبلط عادل"
    )
    page_type = "Blog" if page_number == 1 else "CollectionPage"
    page_entity = {
        "@type": page_type,
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": title,
        "description": "أرشيف مقالات المبلط عادل عن تركيب البلاط والسيراميك والبورسلان والعزل والترميم في الرياض، مرتب من الأحدث إلى الأقدم.",
        "isPartOf": {"@id": f"{BASE_URL}/#website"},
        "about": {"@id": f"{BASE_URL}/#business"},
        "inLanguage": "ar-SA",
        "dateModified": UPDATED,
    }
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{BASE_URL}/"},
        {"@type": "ListItem", "position": 2, "name": "المدونة", "item": f"{BASE_URL}/blog/"},
    ]
    if page_number > 1:
        breadcrumb_items.append(
            {"@type": "ListItem", "position": 3, "name": f"الصفحة {page_number}", "item": canonical}
        )
    graph = [
        shared.BUSINESS_SCHEMA,
        shared.website_schema(),
        page_entity,
        {"@type": "BreadcrumbList", "itemListElement": breadcrumb_items},
        {
            "@type": "ItemList",
            "@id": f"{canonical}#articles",
            "name": "أحدث مقالات المبلط عادل" if page_number == 1 else f"مقالات المدونة – الصفحة {page_number}",
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "numberOfItems": len(page_articles),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": article["title"],
                    "url": f'{BASE_URL}/blog/{article["slug"]}/',
                }
                for position, article in enumerate(page_articles, 1)
            ],
        },
    ]
    if page_number == 1:
        graph.append(
            {
                "@type": "ItemList",
                "@id": f"{canonical}#featured",
                "name": "أفضل 5 مقالات مختارة",
                "numberOfItems": len(featured),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "name": article["title"],
                        "url": f'{BASE_URL}/blog/{article["slug"]}/',
                    }
                    for position, article in enumerate(featured, 1)
                ],
            }
        )
    return graph


def render_head(page_number: int, total_pages: int, page_articles: list[dict], featured: list[dict]) -> str:
    canonical = f"{BASE_URL}/blog/" if page_number == 1 else f"{BASE_URL}/blog/page/{page_number}/"
    title = (
        "مدونة البلاط والسيراميك في الرياض | المبلط عادل"
        if page_number == 1
        else f"مقالات البلاط في الرياض – الصفحة {page_number} | المبلط عادل"
    )
    description = (
        "مدونة المبلط عادل: أفضل 5 أدلة مختارة، ثم أحدث مقالات تركيب البلاط والسيراميك والبورسلان والعزل والترميم في الرياض مرتبة زمنيًا."
        if page_number == 1
        else f"الصفحة {page_number} من أرشيف مقالات المبلط عادل في الرياض: أدلة كاملة عن البلاط والسيراميك والبورسلان والعزل والترميم مرتبة من الأحدث للأقدم."
    )
    asset_prefix = "../" if page_number == 1 else "../../../"
    relations = []
    if page_number > 1:
        prev_url = f"{BASE_URL}/blog/" if page_number == 2 else f"{BASE_URL}/blog/page/{page_number - 1}/"
        relations.append(f'<link rel="prev" href="{prev_url}">')
    if page_number < total_pages:
        relations.append(f'<link rel="next" href="{BASE_URL}/blog/page/{page_number + 1}/">')
    schema = json.dumps(
        {"@context": "https://schema.org", "@graph": schema_graph(page_number, page_articles, featured)},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f'''<!doctype html>
<html lang="ar-SA" dir="rtl" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="author" content="المبلط عادل">
<meta name="theme-color" content="#9a6a1f">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{canonical}">
{''.join(relations)}
<link rel="icon" href="{asset_prefix}assets/images/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{asset_prefix}manifest.webmanifest">
<link rel="stylesheet" href="{asset_prefix}assets/css/style.css?v={STYLE_VERSION}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_SA">
<meta property="og:site_name" content="المبلط عادل">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}/assets/images/tile.jpg">
<meta property="og:image:alt" content="{title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{BASE_URL}/assets/images/tile.jpg">
<script type="application/ld+json">{schema}</script>
</head>'''


def adjust_shared_paths(fragment: str, page_number: int) -> str:
    if page_number == 1:
        return fragment
    return fragment.replace('href="../', 'href="../../../').replace('src="../', 'src="../../../')


def breadcrumbs(page_number: int) -> str:
    if page_number == 1:
        return '<nav class="breadcrumbs container" aria-label="مسار التنقل"><a href="../">الرئيسية</a><span aria-hidden="true">/</span><span aria-current="page">المدونة</span></nav>'
    return f'<nav class="breadcrumbs container" aria-label="مسار التنقل"><a href="../../../">الرئيسية</a><span aria-hidden="true">/</span><a href="../../">المدونة</a><span aria-hidden="true">/</span><span aria-current="page">الصفحة {page_number}</span></nav>'


def refresh_sitemap(total_pages: int) -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    source = re.sub(
        r'\s*<url>\s*<loc>https://almoablat-adel\.vercel\.app/blog/page/\d+/</loc>.*?</url>',
        "",
        source,
        flags=re.S,
    )
    blocks = "\n".join(
        "  <url>\n"
        f"    <loc>{BASE_URL}/blog/page/{page_number}/</loc>\n"
        f"    <lastmod>{UPDATED}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>0.7</priority>\n"
        "  </url>"
        for page_number in range(2, total_pages + 1)
    )
    source = re.sub(
        rf'(<loc>{re.escape(BASE_URL)}/blog/</loc>\s*<lastmod>)[^<]+',
        rf"\g<1>{UPDATED}",
        source,
    )
    source = source.replace("</urlset>", blocks + "\n</urlset>")
    path.write_text(source, encoding="utf-8")


def build() -> None:
    source_path = BLOG / "index.html"
    source = source_path.read_text(encoding="utf-8")
    body_start = source.index("<body>")
    content_start = source.index('<nav class="breadcrumbs container"', body_start)
    suffix_start = source.index('<section class="section section-dark">', content_start)
    body_prefix = source[body_start:content_start]
    suffix = source[suffix_start:]

    articles = collect_articles()
    if len(articles) < 15:
        raise RuntimeError("At least 15 articles are required for the featured/archive layout")
    article_map = {article["slug"]: article for article in articles}
    missing = [slug for slug in FEATURED_SLUGS if slug not in article_map]
    if missing:
        raise RuntimeError(f"Featured articles missing: {', '.join(missing)}")
    featured = [article_map[slug] for slug in FEATURED_SLUGS]
    remaining = [article for article in articles if article["slug"] not in FEATURED_SLUGS]
    total_pages = math.ceil(len(remaining) / PAGE_SIZE)

    for page_number in range(1, total_pages + 1):
        page_articles = remaining[(page_number - 1) * PAGE_SIZE : page_number * PAGE_SIZE]
        href_prefix = "./" if page_number == 1 else "../../"
        page_body = (
            adjust_shared_paths(body_prefix, page_number)
            + breadcrumbs(page_number)
            + render_hero(page_number, len(articles))
            + (render_featured(featured) if page_number == 1 else "")
            + render_listing(page_articles, page_number, total_pages, href_prefix)
            + adjust_shared_paths(suffix, page_number)
        )
        output = render_head(page_number, total_pages, page_articles, featured) + page_body
        output = re.sub(r'app\.js\?v=[^"]+', f'app.js?v={STYLE_VERSION}', output)
        destination = source_path if page_number == 1 else BLOG / "page" / str(page_number) / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")

    refresh_sitemap(total_pages)
    print(
        f"Built featured carousel with {len(featured)} articles and {total_pages} archive pages "
        f"for {len(remaining)} additional articles."
    )


if __name__ == "__main__":
    build()
