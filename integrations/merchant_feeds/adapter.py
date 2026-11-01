#!/usr/bin/env python3
"""Normalize *authorized* retailer/affiliate feeds into price observations.

No scraping, no API credentials, no feed download and no discount verification.
Unlike Spryker, this is an independent cross-merchant observation adapter.
Only inputs explicitly supplied by the feed licensee are read (CSV or JSON).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlsplit

FIELDS = {
    "merchant": ("merchant", "shop", "winkel", "advertiser_name"),
    "merchantReference": ("merchant_reference", "merchant_id", "advertiser_id"),
    "offerReference": ("offer_reference", "offer_id", "product_id", "id"),
    "name": ("name", "product_name", "title"),
    "url": ("url", "product_url", "deeplink", "deep_link"),
    "ean": ("ean", "gtin", "gtin13", "barcode"),
    "sku": ("sku", "merchant_sku", "product_sku"),
    "price": ("price", "price_eur", "current_price", "sale_price"),
    "shipping": ("shipping", "shipping_eur", "delivery_cost"),
    "currency": ("currency", "price_currency"),
    "condition": ("condition", "item_condition"),
    "availability": ("availability", "stock_status", "in_stock"),
    "observedAt": ("observed_at", "last_updated", "updated_at"),
    "variant": ("variant", "variant_key", "size", "model"),
}
REJECT_UNSAFE = {"javascript", "data", "file", "http"}


def field(row: dict, name: str):
    for key in FIELDS[name]:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return value
    return None


def money(value):
    if isinstance(value, bool) or value is None:
        return None
    raw = str(value).strip().replace("€", "").replace(" ", "")
    # Accept standard decimal dot or EU-style comma, not mixed thousands separators.
    if "," in raw and "." in raw:
        return None
    try:
        n = Decimal(raw.replace(",", "."))
    except InvalidOperation:
        return None
    if not n.is_finite() or n < 0 or n >= 100000 or n.as_tuple().exponent < -2:
        return None
    return float(n)


def safe_url(value):
    try:
        s = str(value or "").strip()
        u = urlsplit(s)
        if u.scheme.lower() != "https" or not u.hostname or u.username or u.password:
            return None
        if len(s) > 2000 or u.hostname in {"localhost", "127.0.0.1"}:
            return None
        return s
    except ValueError:
        return None


def normalized(row: dict, provider: str) -> dict | None:
    """Return a clearly labelled candidate, *never* a verified discount."""
    if not isinstance(row, dict):
        return None
    url = safe_url(field(row, "url"))
    price = money(field(row, "price"))
    merchant = str(field(row, "merchant") or "").strip()
    title = str(field(row, "name") or "").strip()
    currency = str(field(row, "currency") or "EUR").strip().upper()
    if not url or not merchant or len(title) < 4 or price is None or price == 0 or currency != "EUR":
        return None
    shipping_raw = field(row, "shipping")
    shipping = money(shipping_raw) if shipping_raw is not None else None
    if shipping_raw is not None and shipping is None:
        return None
    ean = re.sub(r"\D", "", str(field(row, "ean") or ""))
    if ean and len(ean) not in (8, 12, 13, 14):
        ean = ""
    sku = str(field(row, "sku") or "")[:100].strip() or None
    variant = str(field(row, "variant") or "")[:120].strip() or None
    observed = str(field(row, "observedAt") or "")[:40]
    # Missing timestamps must not be filled with the execution time; stale
    # input remains stale and is never promoted into live offers.
    if observed:
        try:
            parsed = datetime.fromisoformat(observed.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                observed = ""
        except ValueError:
            observed = ""
    return {
        "provider": str(provider)[:70], "merchant": merchant[:100],
        "merchantReference": str(field(row,"merchantReference") or "")[:120] or None,
        "offerReference": str(field(row,"offerReference") or "")[:120] or None,
        "name": title[:250], "url": url, "ean": ean or None,
        "sku": sku, "variant": variant, "condition": str(field(row,"condition") or "unknown")[:50],
        "availability": str(field(row,"availability") or "unknown")[:60],
        "currency": "EUR", "itemPriceEUR": price,
        "shippingEUR": shipping,
        "deliveredPriceNL_EUR": round(price + shipping, 2) if shipping is not None else None,
        "observedAt": observed or None,
        "status": "research_candidate_not_verified",
        "verifiedDiscount": False, "independentReferenceEUR": None,
        "notes": "A supplier/feed price is an observation, not proven stock, all-in NL delivery eligibility, or a verified discount.",
    }


def load_rows(path: Path):
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            yield from csv.DictReader(f)
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("items", data.get("products", []))
        if not isinstance(data, list):
            raise ValueError("JSON must be an array or an object with items/products array")
        yield from data
    else:
        raise ValueError("Only explicit .csv or .json files are accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", type=Path, help="Locally supplied licensed merchant feed, CSV or JSON")
    parser.add_argument("--provider", required=True, help="Trusted feed account/provider ID")
    parser.add_argument("--output", type=Path, required=True, help="Candidate JSON output (not a live deal feed)")
    args = parser.parse_args()
    if not args.input_file.is_file():
        parser.error("Feed file does not exist")
    products = [x for row in load_rows(args.input_file) if (x := normalized(row, args.provider))]
    result = {"schemaVersion": 1, "provider": args.provider, "scope": "authorized_input_only",
              "verifiedDeals": 0, "candidates": products}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Normalized {len(products)} safe candidates; zero independently verified discounts")


if __name__ == "__main__":
    main()
