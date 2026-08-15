#!/usr/bin/env python3
"""Generate the August 2026 article expansion and refresh discovery surfaces."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

try:
    from .blog_articles_data import ARTICLES
except ImportError:  # Direct script execution from the tools directory.
    from blog_articles_data import ARTICLES


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://almoablat-adel.vercel.app"
PUBLISHED_DATE = "2026-08-15"
DISPLAY_DATE = "15 أغسطس 2026"
PHONE = "966567372527"
STYLE_VERSION = "20260815-blog-mobile"


OLD_ARTICLES = [
    {
        "slug": "choose-professional-tiler-riyadh",
        "title": "كيف تختار مبلطًا محترفًا في الرياض؟ دليل فحص العرض والتنفيذ",
        "description": "دليل عملي لاختيار مبلط في الرياض: أسئلة المعاينة، عناصر عرض السعر، علامات جودة التركيب، وطريقة الاستلام دون الاعتماد على الوعود العامة.",
        "category": "اختيار وتنفيذ",
        "image": "tile.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "tile-installation-cost-riyadh-2026",
        "title": "تكلفة تركيب البلاط في الرياض 2026: كيف تُحسب دون أرقام مضللة؟",
        "description": "شرح عملي لعوامل تكلفة تركيب البلاط في الرياض لعام 2026، ووحدات القياس، والأعمال الإضافية، وطريقة تجهيز طلب عرض سعر قابل للمقارنة.",
        "category": "تكلفة وتخطيط",
        "image": "ceramic.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "ceramic-vs-porcelain-vs-marble",
        "title": "السيراميك أم البورسلان أم الرخام؟ مقارنة عملية للمنازل في الرياض",
        "description": "مقارنة عملية بين السيراميك والبورسلان والرخام من حيث الاستخدام والامتصاص والصيانة والانزلاق والتركيب والتكلفة للمنازل في الرياض.",
        "category": "اختيار مواد",
        "image": "porcelain.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "tile-installation-steps",
        "title": "خطوات تركيب البلاط الصحيحة من تجهيز السطح حتى الاستلام",
        "description": "شرح مراحل تركيب البلاط: فحص القاعدة والتخطيط واللاصق والفواصل والميول والترويب والحماية، مع قائمة فحص عملية قبل الاستلام.",
        "category": "تنفيذ وجودة",
        "image": "tile.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "bathroom-waterproofing-before-tiles",
        "title": "عزل الحمامات قبل البلاط: المراحل والأخطاء واختبار التسرب",
        "description": "دليل عزل الحمامات قبل البلاط: تجهيز السطح والزوايا والمصارف وطبقات العزل والاختبار وطبقة الحماية وأسباب التسرب.",
        "category": "عزل ورطوبة",
        "image": "waterproofing.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "hollow-tiles-and-cracks-causes",
        "title": "أسباب تطبيل البلاط وتشققاته: التشخيص والإصلاح دون تخمين",
        "description": "تعرف على أسباب صوت الفراغ وتطبيل البلاط والتشققات، والفرق بين ضعف التثبيت وحركة القاعدة والرطوبة والتمدد قبل الإصلاح.",
        "category": "صيانة وتشخيص",
        "image": "repair.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "outdoor-yard-roof-tiles",
        "title": "بلاط الأحواش والأسطح في الرياض: الاختيار والميول وفواصل الحركة",
        "description": "دليل اختيار وتركيب بلاط الأحواش والأسطح بالرياض: مقاومة الانزلاق والحرارة والتصريف والميول والعزل وفواصل الحركة.",
        "category": "مساحات خارجية",
        "image": "stone.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "calculate-tile-quantity-waste",
        "title": "طريقة حساب كمية البلاط ونسبة الهدر للغرف والحمامات والدرج",
        "description": "طريقة عملية لحساب متر البلاط والوزرات والجدران والدرج وتحديد احتياط القص والكسر حسب شكل الغرفة والمقاس ونمط التركيب.",
        "category": "تكلفة وتخطيط",
        "image": "granite.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "tile-cleaning-polishing-guide",
        "title": "دليل تنظيف وتلميع البلاط والرخام دون إتلاف السطح أو الفواصل",
        "description": "إرشادات تنظيف السيراميك والبورسلان والرخام والحجر وإزالة غشاوة الترويب والبقع، ومتى يلزم الجلي أو التلميع المتخصص.",
        "category": "صيانة وتشخيص",
        "image": "polishing.jpg",
        "read_minutes": 6,
    },
    {
        "slug": "repair-old-tiles-without-full-replacement",
        "title": "ترميم البلاط القديم دون تغيير كامل: متى ينجح ومتى لا؟",
        "description": "خيارات إصلاح البلاط القديم موضعيًا: تبديل القطع وتجديد الفواصل ومعالجة الهبوط والتسرب ومعايير الإصلاح الجزئي أو الإزالة الكاملة.",
        "category": "صيانة وتشخيص",
        "image": "repair.jpg",
        "read_minutes": 6,
    },
]


BUSINESS_SCHEMA = {
    "@type": "HomeAndConstructionBusiness",
    "@id": f"{BASE_URL}/#business",
    "name": "المبلط عادل",
    "alternateName": "Adel Tiler Riyadh",
    "url": f"{BASE_URL}/",
    "logo": f"{BASE_URL}/assets/images/logo-mark.svg",
    "image": f"{BASE_URL}/assets/images/hero.png",
    "telephone": "+966567372527",
    "priceRange": "$$",
    "description": "خدمات تركيب البلاط والسيراميك والبورسلان والرخام والجرانيت والحجر الطبيعي والعزل والترميم في مدينة الرياض.",
    "areaServed": {"@type": "City", "name": "الرياض"},
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "الرياض",
        "addressRegion": "منطقة الرياض",
        "addressCountry": "SA",
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+966567372527",
        "contactType": "customer service",
        "areaServed": "SA",
        "availableLanguage": ["ar"],
        "url": f"https://wa.me/{PHONE}",
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def whatsapp_url(message: str) -> str:
    return f"https://wa.me/{PHONE}?text={quote(message)}"


def schema_script(graph: list[dict]) -> str:
    payload = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f'<script type="application/ld+json">{payload}</script>'


def website_schema() -> dict:
    return {
        "@type": "WebSite",
        "@id": f"{BASE_URL}/#website",
        "url": f"{BASE_URL}/",
        "name": "المبلط عادل",
        "inLanguage": "ar-SA",
        "publisher": {"@id": f"{BASE_URL}/#business"},
    }


def render_section(section: dict) -> str:
    parts = [f'<section id="{esc(section["id"])}"><h2>{esc(section["title"])}</h2>']
    parts.extend(f"<p>{paragraph}</p>" for paragraph in section.get("paragraphs", []))
    for subsection in section.get("subsections", []):
        parts.append(f'<h3 id="{esc(subsection["id"])}">{esc(subsection["title"])}</h3>')
        parts.extend(f"<p>{paragraph}</p>" for paragraph in subsection.get("paragraphs", []))
        if subsection.get("bullets"):
            items = "".join(f"<li>{esc(item)}</li>" for item in subsection["bullets"])
            parts.append(f'<ul class="article-list">{items}</ul>')
    if section.get("bullets"):
        items = "".join(f"<li>{esc(item)}</li>" for item in section["bullets"])
        parts.append(f'<ul class="article-list">{items}</ul>')
    if section.get("steps"):
        items = "".join(f"<li>{esc(item)}</li>" for item in section["steps"])
        parts.append(f'<ol class="article-list article-steps">{items}</ol>')
    parts.append("</section>")
    return "".join(parts)


def render_toc(article: dict) -> str:
    items: list[str] = []
    for section in article["sections"]:
        items.append(f'<li><a href="#{esc(section["id"])}">{esc(section["title"])}</a></li>')
        for subsection in section.get("subsections", []):
            items.append(
                f'<li class="toc-subitem"><a href="#{esc(subsection["id"])}">{esc(subsection["title"])}</a></li>'
            )
    items.append('<li><a href="#faq">الأسئلة الشائعة</a></li>')
    items.append(f'<li><a href="#conclusion">{esc(article["conclusion_title"])}</a></li>')
    return "".join(items)


def render_faq(article: dict) -> str:
    details = "".join(
        f'<details class="faq-item"><summary>{esc(question)}</summary><div><p>{esc(answer)}</p></div></details>'
        for question, answer in article["faqs"]
    )
    return (
        '<section id="faq"><h2>الأسئلة الشائعة عن الموضوع</h2>'
        '<p>إجابات مباشرة عن أكثر النقاط التي يحتاج العميل إلى حسمها قبل المعاينة والتنفيذ.</p>'
        f'<div class="faq-list article-faq">{details}</div></section>'
    )


def visible_word_count(article: dict) -> int:
    chunks = [article["title"], article["intro"], article["conclusion"]]
    for section in article["sections"]:
        chunks.append(section["title"])
        chunks.extend(section.get("paragraphs", []))
        chunks.extend(section.get("bullets", []))
        chunks.extend(section.get("steps", []))
        for subsection in section.get("subsections", []):
            chunks.append(subsection["title"])
            chunks.extend(subsection.get("paragraphs", []))
            chunks.extend(subsection.get("bullets", []))
    for question, answer in article["faqs"]:
        chunks.extend([question, answer])
    text = re.sub(r"<[^>]+>", " ", " ".join(chunks))
    return len(re.findall(r"\S+", text))


def article_head(article: dict, word_count: int) -> str:
    canonical = f'{BASE_URL}/blog/{article["slug"]}/'
    image_url = f'{BASE_URL}/assets/images/{article["image"]}'
    page_title = f'{article["title"]} | المبلط عادل'
    faq_schema = {
        "@type": "FAQPage",
        "@id": f'{canonical}#faq',
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in article["faqs"]
        ],
    }
    graph = [
        BUSINESS_SCHEMA,
        website_schema(),
        {
            "@type": "BlogPosting",
            "@id": f"{canonical}#article",
            "mainEntityOfPage": canonical,
            "url": canonical,
            "headline": article["title"],
            "description": article["description"],
            "image": [image_url],
            "datePublished": PUBLISHED_DATE,
            "dateModified": PUBLISHED_DATE,
            "inLanguage": "ar-SA",
            "wordCount": word_count,
            "articleSection": article["category"],
            "keywords": [article["keyword"], "معلم بلاط بالرياض", "المبلط عادل"],
            "author": {"@type": "Organization", "name": "فريق محتوى المبلط عادل", "url": f"{BASE_URL}/"},
            "publisher": {"@id": f"{BASE_URL}/#business"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "المدونة", "item": f"{BASE_URL}/blog/"},
                {"@type": "ListItem", "position": 3, "name": article["title"], "item": canonical},
            ],
        },
        faq_schema,
    ]
    return f'''<!doctype html>
<html lang="ar-SA" dir="rtl" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(article["description"])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="author" content="المبلط عادل">
<meta name="theme-color" content="#9a6a1f">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="../../assets/images/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="../../manifest.webmanifest">
<link rel="preload" as="image" href="{image_url}" fetchpriority="high">
<link rel="stylesheet" href="../../assets/css/style.css?v={STYLE_VERSION}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ar_SA">
<meta property="og:site_name" content="المبلط عادل">
<meta property="og:title" content="{esc(page_title)}">
<meta property="og:description" content="{esc(article["description"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:alt" content="{esc(article["title"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(page_title)}">
<meta name="twitter:description" content="{esc(article["description"])}">
<meta name="twitter:image" content="{image_url}">
<meta property="article:published_time" content="{PUBLISHED_DATE}">
<meta property="article:modified_time" content="{PUBLISHED_DATE}">
<meta property="article:section" content="{esc(article["category"])}">
{schema_script(graph)}
</head>'''


def article_markup(article: dict) -> str:
    contact_message = f'مرحبًا، قرأت مقال: {article["title"]} وأحتاج استشارة لمشروعي في الرياض'
    sections = []
    for index, section in enumerate(article["sections"]):
        sections.append(render_section(section))
        if index == 2:
            sections.append(
                '<aside class="inline-cta"><div><h2>هل لديك صور للموقع؟</h2>'
                '<p>أرسل صور المساحة ومقاس البلاط والحي لنراجع المتطلبات قبل المعاينة.</p></div>'
                f'<a class="button button-primary" href="{whatsapp_url(contact_message)}" target="_blank" rel="noopener">إرسال التفاصيل عبر واتساب</a></aside>'
            )
    sections.append(render_faq(article))
    sections.append(
        f'<section class="article-conclusion" id="conclusion"><h2>{esc(article["conclusion_title"])}</h2>'
        f'<p>{esc(article["conclusion"])}</p>'
        f'<a class="button button-primary" href="{whatsapp_url(contact_message)}" target="_blank" rel="noopener">تواصل الآن عبر واتساب</a></section>'
    )
    image_url = f'{BASE_URL}/assets/images/{article["image"]}'
    return f'''
<nav class="breadcrumbs container" aria-label="مسار التنقل"><a href="../../">الرئيسية</a><span aria-hidden="true">/</span><a href="../../blog/">المدونة</a><span aria-hidden="true">/</span><span aria-current="page">{esc(article["title"])}</span></nav>
<article class="article-page">
<header class="article-hero"><div class="container article-hero-grid"><div><div class="article-meta hero-meta"><span>{esc(article["category"])}</span><span>{article["read_minutes"]} دقائق قراءة</span><span>تحديث {DISPLAY_DATE}</span></div><h1>{esc(article["title"])}</h1><p>{esc(article["hero_summary"])}</p><div class="article-actions"><button class="button button-outline" type="button" data-share data-share-title="{esc(article["title"])}">مشاركة المقال</button><a class="button button-primary" href="{whatsapp_url(contact_message)}" target="_blank" rel="noopener">اسأل عبر واتساب</a></div></div><div class="hero-visual"><img src="{image_url}" width="1200" height="800" alt="{esc(article["title"])}" fetchpriority="high"><span class="media-fallback" aria-hidden="true"></span></div></div></header>
<div class="container article-layout">
<aside class="article-sidebar"><nav class="toc" aria-label="محتويات المقال"><h2>محتويات المقال</h2><ol>{render_toc(article)}</ol></nav><div class="sidebar-contact"><strong>تحتاج معاينة؟</strong><p>أرسل الحي وصور المساحة ونوع البلاط.</p><a href="{whatsapp_url(contact_message)}" target="_blank" rel="noopener">تواصل واتساب</a></div></aside>
<div class="article-prose"><p class="lead-paragraph">{esc(article["intro"])}</p>{''.join(sections)}</div>
</div>
</article>'''


def generate_articles() -> None:
    template = (ROOT / "blog/tile-installation-steps/index.html").read_text(encoding="utf-8")
    body_start = template.index("<body>")
    main_marker = '<main id="main-content">'
    body_prefix_end = template.index(main_marker, body_start) + len(main_marker)
    body_prefix = template[body_start:body_prefix_end]
    article_start = template.index('<article class="article-page">', body_prefix_end)
    article_end = template.index("</article>", article_start) + len("</article>")
    suffix = template[article_end:]
    # The source article has its own generic FAQ after </article>. New articles
    # already render a topic-specific FAQ inside <article>, so carrying this
    # section over would duplicate the visible questions and diverge from the
    # FAQPage schema.
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
        output = article_head(article, visible_word_count(article)) + body_prefix + article_markup(article) + suffix
        output = output.replace("دليل البلاط", "المدونة").replace(">الدليل<", ">المدونة<")
        output = output.replace("مشاركة الدليل", "مشاركة المقال").replace("اقرأ الدليل", "اقرأ المقال")
        destination.write_text(output, encoding="utf-8")


def render_card(article: dict, href_prefix: str) -> str:
    href = f'{href_prefix}{article["slug"]}/'
    image_url = f'{BASE_URL}/assets/images/{article["image"]}'
    return f'''<article class="article-card">
<a class="card-media" href="{href}" aria-label="{esc(article["title"])}"><img src="{image_url}" width="1200" height="800" loading="lazy" decoding="async" alt="{esc(article["title"])}"><span class="media-fallback" aria-hidden="true"></span></a>
<div class="card-content"><div class="article-meta"><span>{esc(article["category"])}</span><span>{article["read_minutes"]} دقائق قراءة</span></div><h3><a href="{href}">{esc(article["title"])}</a></h3><p>{esc(article["description"])}</p><a class="text-link" href="{href}">اقرأ المقال</a></div>
</article>'''


def blog_head(all_articles: list[dict]) -> str:
    title = "مدونة البلاط والسيراميك في الرياض | المبلط عادل"
    description = "مقالات احترافية عن تركيب البلاط والسيراميك والبورسلان والعزل والترميم في الرياض، مع خطوات تنفيذ وأسئلة شائعة وروابط مباشرة للخدمات."
    canonical = f"{BASE_URL}/blog/"
    graph = [
        BUSINESS_SCHEMA,
        website_schema(),
        {
            "@type": "Blog",
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{BASE_URL}/#website"},
            "about": {"@id": f"{BASE_URL}/#business"},
            "inLanguage": "ar-SA",
            "dateModified": PUBLISHED_DATE,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "المدونة", "item": canonical},
            ],
        },
        {
            "@type": "ItemList",
            "name": "مقالات مدونة المبلط عادل",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": article["title"],
                    "url": f'{BASE_URL}/blog/{article["slug"]}/',
                }
                for position, article in enumerate(all_articles, 1)
            ],
        },
    ]
    image_url = f"{BASE_URL}/assets/images/tile.jpg"
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
<link rel="icon" href="../assets/images/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="../manifest.webmanifest">
<link rel="stylesheet" href="../assets/css/style.css?v={STYLE_VERSION}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_SA">
<meta property="og:site_name" content="المبلط عادل">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:alt" content="{title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image_url}">
{schema_script(graph)}
</head>'''


def refresh_blog_index() -> None:
    all_articles = ARTICLES + OLD_ARTICLES
    path = ROOT / "blog/index.html"
    source = path.read_text(encoding="utf-8")
    body = source[source.index("<body>"):]

    hero_start = body.index('<nav class="breadcrumbs container"')
    content_start = body.index('<section class="section">', hero_start)
    hero = f'''<nav class="breadcrumbs container" aria-label="مسار التنقل"><a href="../">الرئيسية</a><span aria-hidden="true">/</span><span aria-current="page">المدونة</span></nav>
<section class="page-hero blog-hero"><div class="container page-hero-grid"><div><span class="eyebrow">مقالات متخصصة للسوق السعودي</span><h1>مدونة البلاط والسيراميك والتشطيبات</h1><p>محتوى عملي يساعدك على اختيار الخامة وفهم خطوات التنفيذ وفحص الأعمال قبل الاستلام، مع موضوعات محلية مرتبطة بخدمات البلاط والعزل والترميم في الرياض.</p><div class="hero-actions"><a class="button button-primary" href="{whatsapp_url('مرحبًا، قرأت أحد مقالات المدونة وأحتاج استشارة لمشروعي')}" target="_blank" rel="noopener">اطلب الخدمة عبر واتساب</a><a class="button button-secondary" href="tel:0567372527">اتصال مباشر</a></div></div><div class="hero-visual editorial-visual" aria-label="مزايا المدونة"><svg class="huge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v14H4zM8 9h8M8 13h8M8 17h5"/></svg><div><strong>SEO</strong><span>مواضيع بحث محلية</span></div><div><strong>FAQ</strong><span>إجابات مباشرة</span></div></div></div></section>
'''
    body = body[:hero_start] + hero + body[content_start:]

    cards_marker = '<div class="cards-grid article-grid blog-grid">'
    cards_start = body.index(cards_marker) + len(cards_marker)
    cards_end_marker = '</div></div></section>\n<section class="section section-dark">'
    cards_end = body.index(cards_end_marker, cards_start)
    cards = "".join(render_card(article, "./") for article in all_articles)
    body = body[:cards_start] + cards + body[cards_end:]
    path.write_text(blog_head(all_articles) + body, encoding="utf-8")


def refresh_homepage_articles() -> None:
    path = ROOT / "index.html"
    source = path.read_text(encoding="utf-8")
    section_start = source.index('<section class="section" aria-labelledby="blog-title">')
    cards_marker = '<div class="cards-grid article-grid">'
    cards_start = source.index(cards_marker, section_start) + len(cards_marker)
    next_section = source.index('<section class="section section-soft" aria-labelledby="faq-title">', cards_start)
    closing = source.rfind('</div>\n</div>\n</section>', cards_start, next_section)
    if closing == -1:
        raise RuntimeError("Homepage article grid closing marker not found")
    cards = "".join(render_card(article, "blog/") for article in ARTICLES[:3])
    source = source[:cards_start] + cards + source[closing:]
    path.write_text(source, encoding="utf-8")


def refresh_sitemap() -> None:
    entries: list[tuple[str, str, str]] = []
    for page in sorted(ROOT.rglob("*.html")):
        if page.name == "404.html":
            continue
        source = page.read_text(encoding="utf-8")
        match = re.search(r'<link rel="canonical" href="([^"]+)"', source)
        if not match:
            raise RuntimeError(f"Canonical not found in {page.relative_to(ROOT)}")
        url = match.group(1)
        if url == f"{BASE_URL}/":
            priority = "1.0"
        elif url in {f"{BASE_URL}/blog/", f"{BASE_URL}/services/"}:
            priority = "0.9"
        else:
            priority = "0.8"
        changefreq = "weekly" if "/blog/" in url else "monthly"
        entries.append((url, changefreq, priority))
    entries.sort(key=lambda item: (item[0] != f"{BASE_URL}/", item[0]))
    urls = "\n".join(
        "  <url>\n"
        f"    <loc>{url}</loc>\n"
        f"    <lastmod>{PUBLISHED_DATE}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>"
        for url, changefreq, priority in entries
    )
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
'''
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def main() -> None:
    if len(ARTICLES) != 10:
        raise RuntimeError(f"Expected 10 new articles, found {len(ARTICLES)}")
    slugs = [article["slug"] for article in ARTICLES]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("Duplicate article slugs")
    generate_articles()
    refresh_blog_index()
    refresh_homepage_articles()
    refresh_sitemap()
    print(f"Generated {len(ARTICLES)} new articles and refreshed blog discovery pages.")


if __name__ == "__main__":
    main()
