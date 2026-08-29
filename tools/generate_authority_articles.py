#!/usr/bin/env python3
"""Generate the supporting authority cluster and refresh discovery surfaces."""

from authority_articles_data import ARTICLES
import generate_local_seo_articles as workflow


workflow.ARTICLES = ARTICLES
workflow.PUBLISHED_DATE = "2026-08-29"
workflow.DISPLAY_DATE = "29 أغسطس 2026"
workflow.STYLE_VERSION = "20260829-authority-cluster"
workflow.SEO_TITLES = {article["slug"]: article["seo_title"] for article in ARTICLES}


if __name__ == "__main__":
    workflow.main()
