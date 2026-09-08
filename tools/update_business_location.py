#!/usr/bin/env python3
"""Synchronize the business location across every JSON-LD block."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_URL = "https://maps.app.goo.gl/Jxbv6G8HS91jD3zo8"
ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "حي المصيف، 2914 المحبي، 6959",
    "addressLocality": "الرياض",
    "addressRegion": "منطقة الرياض",
    "postalCode": "12465",
    "addressCountry": "SA",
}
GEO = {
    "@type": "GeoCoordinates",
    "latitude": 24.762114449181418,
    "longitude": 46.679954222287,
}
SCHEMA_PATTERN = re.compile(
    r'(<script\s+type="application/ld\+json">)(.*?)(</script>)',
    flags=re.IGNORECASE | re.DOTALL,
)


def update_entities(value: object) -> int:
    updated = 0
    if isinstance(value, dict):
        entity_type = value.get("@type")
        types = entity_type if isinstance(entity_type, list) else [entity_type]
        if "HomeAndConstructionBusiness" in types:
            value["address"] = ADDRESS.copy()
            value["geo"] = GEO.copy()
            value["hasMap"] = MAP_URL
            updated += 1
        for child in value.values():
            updated += update_entities(child)
    elif isinstance(value, list):
        for child in value:
            updated += update_entities(child)
    return updated


def update_page(path: Path) -> tuple[bool, int]:
    source = path.read_text(encoding="utf-8")
    entity_count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal entity_count
        payload = json.loads(match.group(2))
        entity_count += update_entities(payload)
        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return f"{match.group(1)}{serialized}{match.group(3)}"

    updated = SCHEMA_PATTERN.sub(replace, source)
    if entity_count == 0:
        raise RuntimeError(f"No business entity found in {path.relative_to(ROOT)}")
    if updated != source:
        path.write_text(updated, encoding="utf-8")
        return True, entity_count
    return False, entity_count


def main() -> None:
    pages = sorted(ROOT.rglob("*.html"))
    changed_pages = 0
    entity_count = 0
    for page in pages:
        changed, updated_entities = update_page(page)
        changed_pages += int(changed)
        entity_count += updated_entities
    print(
        f"Updated {entity_count} business entities across "
        f"{changed_pages} of {len(pages)} HTML pages."
    )


if __name__ == "__main__":
    main()
