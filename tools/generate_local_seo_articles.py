#!/usr/bin/env python3
"""Generate the local-intent article cluster and refresh discovery surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path

import generate_blog_expansion as base
from local_seo_articles_data import ARTICLES


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_DATE = "2026-08-23"
DISPLAY_DATE = "23 أغسطس 2026"
STYLE_VERSION = "20260823-promo-assistant"
SEO_TITLES = {
    "best-tiler-in-riyadh": "أفضل مبلط في الرياض: اختيار وتنفيذ | المبلط عادل",
    "riyadh-tiler-complete-services": "مبلط الرياض للفلل والشقق | المبلط عادل",
    "floor-tiling-specialist-riyadh": "معلم تبليط أرضيات بالرياض | المبلط عادل",
    "best-tile-contractor-riyadh": "أفضل مقاول بلاط بالرياض | المبلط عادل",
    "north-riyadh-tiler": "مبلط شمال الرياض | المبلط عادل",
    "floor-tiler-riyadh": "مبلط أرضيات بالرياض | المبلط عادل",
    "bathroom-tiler-riyadh": "مبلط حمامات بالرياض | المبلط عادل",
    "villa-tiler-riyadh": "مبلط فلل بالرياض | المبلط عادل",
    "porcelain-tiler-riyadh": "معلم بورسلان بالرياض | المبلط عادل",
    "tile-renovation-tiler-riyadh": "مبلط ترميمات بالرياض | المبلط عادل",
}


def configure_renderer() -> None:
    for article in ARTICLES:
        article["seo_title"] = SEO_TITLES[article["slug"]]
    base.ARTICLES = ARTICLES
    base.PUBLISHED_DATE = PUBLISHED_DATE
    base.DISPLAY_DATE = DISPLAY_DATE
    base.STYLE_VERSION = STYLE_VERSION


def generate_articles() -> None:
    template = (ROOT / "blog/large-format-porcelain-installation-riyadh/index.html").read_text(
        encoding="utf-8"
    )
    body_start = template.index("<body>")
    main_marker = '<main id="main-content">'
    body_prefix_end = template.index(main_marker, body_start) + len(main_marker)
    body_prefix = template[body_start:body_prefix_end]
    article_start = template.index('<article class="article-page">', body_prefix_end)
    article_end = template.index("</article>", article_start) + len("</article>")
    suffix = template[article_end:]
    suffix = re.sub(
        r'\n?<section class="section section-soft" aria-labelledby="faq-title">.*?</section>\n?',
        "\n",
        suffix,
        count=1,
        flags=re.S,
    )

    for article in ARTICLES:
        destination = ROOT / "blog" / article["slug"] / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        output = (
            base.article_head(article, base.visible_word_count(article))
            + body_prefix
            + base.article_markup(article)
            + suffix
        )
        output = output.replace("دليل البلاط", "المدونة").replace(">الدليل<", ">المدونة<")
        output = output.replace("مشاركة الدليل", "مشاركة المقال").replace("اقرأ الدليل", "اقرأ المقال")
        destination.write_text(output, encoding="utf-8")


def update_blog_schema(source: str) -> str:
    pattern = r'<script type="application/ld\+json">(.*?)</script>'
    match = re.search(pattern, source, re.S)
    if not match:
        raise RuntimeError("Blog JSON-LD block not found")
    payload = json.loads(match.group(1))
    graph = payload.get("@graph", [])
    item_list = next((item for item in graph if item.get("@type") == "ItemList"), None)
    blog = next((item for item in graph if item.get("@type") == "Blog"), None)
    if item_list is None or blog is None:
        raise RuntimeError("Blog or ItemList schema missing")
    new_urls = {f'{base.BASE_URL}/blog/{article["slug"]}/' for article in ARTICLES}
    existing = [
        item for item in item_list.get("itemListElement", []) if item.get("url") not in new_urls
    ]
    fresh = [
        {
            "@type": "ListItem",
            "position": position,
            "name": article["title"],
            "url": f'{base.BASE_URL}/blog/{article["slug"]}/',
        }
        for position, article in enumerate(ARTICLES, 1)
    ]
    combined = fresh + existing
    for position, item in enumerate(combined, 1):
        item["position"] = position
    item_list["itemListElement"] = combined
    blog["dateModified"] = PUBLISHED_DATE
    replacement = '<script type="application/ld+json">' + json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    ) + "</script>"
    return source[: match.start()] + replacement + source[match.end() :]


def refresh_blog_index() -> None:
    path = ROOT / "blog/index.html"
    source = update_blog_schema(path.read_text(encoding="utf-8"))
    grid_marker = '<div class="cards-grid article-grid blog-grid">'
    start = source.index(grid_marker) + len(grid_marker)
    end_marker = '</div></div></section>\n<section class="section section-dark">'
    end = source.index(end_marker, start)
    current_cards = source[start:end]
    for article in ARTICLES:
        slug = re.escape(article["slug"])
        current_cards = re.sub(
            rf'<article class="article-card">(?:(?!</article>).)*href="\./{slug}/"(?:(?!</article>).)*</article>',
            "",
            current_cards,
            flags=re.S,
        )
    new_cards = "".join(base.render_card(article, "./") for article in ARTICLES)
    source = source[:start] + new_cards + current_cards + source[end:]
    path.write_text(source, encoding="utf-8")


def refresh_homepage() -> None:
    base.refresh_homepage_articles()


def refresh_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    new_urls = [f'{base.BASE_URL}/blog/{article["slug"]}/' for article in ARTICLES]
    for url in new_urls:
        source = re.sub(
            rf'\s*<url>\s*<loc>{re.escape(url)}</loc>.*?</url>',
            "",
            source,
            flags=re.S,
        )
    blocks = "\n".join(
        "  <url>\n"
        f"    <loc>{url}</loc>\n"
        f"    <lastmod>{PUBLISHED_DATE}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>0.8</priority>\n"
        "  </url>"
        for url in new_urls
    )
    source = source.replace("</urlset>", blocks + "\n</urlset>")
    for changed_url in (f"{base.BASE_URL}/", f"{base.BASE_URL}/blog/"):
        source = re.sub(
            rf'(<loc>{re.escape(changed_url)}</loc>\s*<lastmod>)[^<]+',
            rf"\g<1>{PUBLISHED_DATE}",
            source,
        )
    path.write_text(source, encoding="utf-8")


def validate_inputs() -> None:
    if len(ARTICLES) != 10:
        raise RuntimeError(f"Expected 10 articles, found {len(ARTICLES)}")
    slugs = [article["slug"] for article in ARTICLES]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("Duplicate local SEO article slugs")
    titles = [article["title"] for article in ARTICLES]
    if len(titles) != len(set(titles)):
        raise RuntimeError("Duplicate local SEO article titles")
    for article in ARTICLES:
        words = base.visible_word_count(article)
        if words < 430:
            raise RuntimeError(f'{article["slug"]}: only {words} visible words')
        if len(article["faqs"]) < 4:
            raise RuntimeError(f'{article["slug"]}: insufficient FAQ coverage')


def main() -> None:
    validate_inputs()
    configure_renderer()
    generate_articles()
    from build_blog_archive import build as build_blog_archive

    build_blog_archive()
    refresh_homepage()
    refresh_sitemap()
    print("Generated 10 SEO articles and refreshed blog, homepage, and sitemap.")


if __name__ == "__main__":
    main()
