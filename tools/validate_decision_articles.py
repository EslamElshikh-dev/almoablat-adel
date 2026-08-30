#!/usr/bin/env python3
"""Fail when the decision-stage batch drifts back toward duplicate content."""

from __future__ import annotations

import html
import itertools
import json
import re
from pathlib import Path

from decision_articles_data import ARTICLES


ROOT = Path(__file__).resolve().parents[1]
MAX_FIVE_WORD_SIMILARITY = 0.20
MIN_VISIBLE_WORDS = 430


def article_source(slug: str) -> str:
    page = ROOT / "blog" / slug / "index.html"
    return page.read_text(encoding="utf-8")


def visible_article_text(slug: str) -> str:
    page = ROOT / "blog" / slug / "index.html"
    source = article_source(slug)
    match = re.search(
        r'<div class="article-prose">(.*?)</div>\s*</div>\s*</article>',
        source,
        re.S,
    )
    if not match:
        raise RuntimeError(f"Missing article-prose in {page}")
    without_markup = re.sub(r"<[^>]+>", " ", match.group(1))
    return re.sub(r"\s+", " ", html.unescape(without_markup)).strip()


def five_word_shingles(text: str) -> set[str]:
    words = text.split()
    return {
        " ".join(words[index:index + 5])
        for index in range(max(0, len(words) - 4))
    }


def main() -> None:
    failures: list[str] = []
    texts: dict[str, str] = {}
    section_titles: set[str] = set()
    faq_questions: set[str] = set()

    for article in ARTICLES:
        slug = article["slug"]
        source = article_source(slug)
        text = visible_article_text(slug)
        texts[slug] = text
        word_count = len(text.split())
        if word_count < MIN_VISIBLE_WORDS:
            failures.append(f"{slug}: only {word_count} visible words")
        if len(article["faqs"]) < 4:
            failures.append(f"{slug}: fewer than four FAQs")

        schema_nodes: list[dict] = []
        for block in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            source,
            re.S,
        ):
            payload = json.loads(block)
            schema_nodes.extend(payload.get("@graph", []))
        schema_types = {node.get("@type") for node in schema_nodes}
        for required_type in ("BlogPosting", "FAQPage", "BreadcrumbList"):
            if required_type not in schema_types:
                failures.append(f"{slug}: missing {required_type} schema")
        faq_schema = next(
            (node for node in schema_nodes if node.get("@type") == "FAQPage"),
            None,
        )
        if faq_schema and len(faq_schema.get("mainEntity", [])) != len(article["faqs"]):
            failures.append(f"{slug}: FAQ schema does not match visible FAQ count")

        for section in article["sections"]:
            title = section["title"].strip()
            if title in section_titles:
                failures.append(f"Repeated section title: {title}")
            section_titles.add(title)

        for question, _answer in article["faqs"]:
            question = question.strip()
            if question in faq_questions:
                failures.append(f"Repeated FAQ question: {question}")
            faq_questions.add(question)

    comparisons: list[tuple[float, str, str]] = []
    for left, right in itertools.combinations(texts, 2):
        left_shingles = five_word_shingles(texts[left])
        right_shingles = five_word_shingles(texts[right])
        denominator = min(len(left_shingles), len(right_shingles))
        similarity = (
            len(left_shingles & right_shingles) / denominator
            if denominator
            else 0.0
        )
        comparisons.append((similarity, left, right))
        if similarity >= MAX_FIVE_WORD_SIMILARITY:
            failures.append(
                f"{left} vs {right}: {similarity:.2%} five-word similarity"
            )

    average = sum(item[0] for item in comparisons) / len(comparisons)
    maximum, left, right = max(comparisons)
    print(f"Decision articles: {len(ARTICLES)}")
    print(f"Pairwise five-word similarity: average {average:.2%}, max {maximum:.2%}")
    print(f"Closest pair: {left} vs {right}")

    if failures:
        raise SystemExit("\n".join(failures))

    print("Decision article uniqueness validation passed.")


if __name__ == "__main__":
    main()
