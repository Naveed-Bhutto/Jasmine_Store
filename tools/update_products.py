#!/usr/bin/env python3
"""
update_products.py — Jasmine Store product injector
=====================================================
Reads products.json and rewrites the PRODUCTS array inside index.html
(between the PRODUCTS_START / PRODUCTS_END markers).

This lets you (or an AI / GitHub Action) manage products in a simple
JSON file without ever touching the website code.

Usage:
    python3 tools/update_products.py                 # uses ./products.json → ./index.html
    python3 tools/update_products.py --json my.json --html index.html

Validation performed on every product:
    • required fields present (id, title, description, price,
      originalPrice, platform, rating, affiliateLink)
    • price < originalPrice (so the discount ribbon is always positive)
    • rating between 0 and 5
    • affiliateLink starts with https://
    • no EXAMPLE placeholder links (warning only)
"""

import argparse
import json
import re
import sys
from pathlib import Path

START = "/* PRODUCTS_START"
END   = "/* PRODUCTS_END"

REQUIRED = ["id", "title", "description", "price", "originalPrice",
            "platform", "category", "rating", "affiliateLink"]

VALID_PLATFORMS = {"AliExpress", "Daraz", "Amazon"}


def validate(products: list) -> list:
    """Return a list of error strings (empty list = all good)."""
    errors, warnings, seen_ids = [], [], set()

    for i, p in enumerate(products):
        label = f"product #{i + 1} ({p.get('title', 'untitled')!r})"

        for field in REQUIRED:
            if field not in p:
                errors.append(f"{label}: missing required field '{field}'")

        if "id" in p:
            if p["id"] in seen_ids:
                errors.append(f"{label}: duplicate id {p['id']}")
            seen_ids.add(p["id"])

        if "price" in p and "originalPrice" in p and p["price"] >= p["originalPrice"]:
            errors.append(f"{label}: price must be LOWER than originalPrice")

        if "rating" in p and not (0 <= p["rating"] <= 5):
            errors.append(f"{label}: rating must be between 0 and 5")

        link = p.get("affiliateLink", "")
        if link and not link.startswith("https://"):
            errors.append(f"{label}: affiliateLink must start with https://")
        if "EXAMPLE" in link:
            warnings.append(f"{label}: affiliateLink still contains an EXAMPLE placeholder")

        if p.get("platform") not in VALID_PLATFORMS:
            warnings.append(f"{label}: platform {p.get('platform')!r} is not one of {VALID_PLATFORMS}")

    for w in warnings:
        print(f"  ⚠️  {w}")
    return errors


def to_js(products: list) -> str:
    """Serialize the product list as a pretty JavaScript array literal."""
    return json.dumps(products, indent=4, ensure_ascii=False)


def inject(html: str, js_array: str) -> str:
    """Replace everything between the PRODUCTS markers with the new array."""
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"[^*]*\*/",
        re.DOTALL,
    )
    replacement = (
        f"{START} — do not remove this marker (used by tools/update_products.py) */\n"
        f"  const PRODUCTS = {js_array};\n"
        f"  {END} — do not remove this marker */"
    )
    new_html, count = pattern.subn(replacement, html, count=1)
    if count != 1:
        sys.exit("❌ Could not find PRODUCTS_START/PRODUCTS_END markers in the HTML file.")
    return new_html


def main() -> None:
    ap = argparse.ArgumentParser(description="Inject products.json into index.html")
    ap.add_argument("--json", default="products.json", help="path to products JSON file")
    ap.add_argument("--html", default="index.html", help="path to the website HTML file")
    args = ap.parse_args()

    json_path, html_path = Path(args.json), Path(args.html)
    if not json_path.exists():
        sys.exit(f"❌ {json_path} not found")
    if not html_path.exists():
        sys.exit(f"❌ {html_path} not found")

    products = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(products, list) or not products:
        sys.exit("❌ products.json must contain a non-empty JSON array")

    print(f"📦 Loaded {len(products)} products from {json_path}")

    errors = validate(products)
    if errors:
        print("\n❌ Validation failed:")
        for e in errors:
            print(f"   • {e}")
        sys.exit(1)

    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(inject(html, to_js(products)), encoding="utf-8")
    print(f"✅ Injected {len(products)} products into {html_path}")


if __name__ == "__main__":
    main()
