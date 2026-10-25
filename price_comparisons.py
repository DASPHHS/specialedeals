#!/usr/bin/env python3
"""Find useful SAME-PRODUCT price gaps, without fabricating all-in savings.

An independently observed matching GTIN or reliable MPN is required.
A raw article-price difference is not a guaranteed deal because postage,
tax, eligibility, inventory and checkout may be unknown.
"""
import datetime as dt
import json
import pathlib
from decimal import Decimal, InvalidOperation

ROOT = pathlib.Path(__file__).resolve().parent
INPUT = ROOT / "merchant-observations.json"
OUTPUT = ROOT / "price-comparisons.json"


def cash(value):
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return d if d.is_finite() and d >= Decimal("0.50") else None


def identity(row):
    """GTIN gets precedence, only use MPN as fallback when GTIN absent."""
    gtin = str(row.get("gtin") or "").strip()
    if gtin.isdigit() and 8 <= len(gtin) <= 14:
        return "gtin:" + gtin
    mpn = str(row.get("exactModel") or row.get("mpn") or "").strip().casefold()
    if len(mpn) >= 5 and len(mpn) <= 40:
        return "mpn:" + mpn
    return None


def find_gaps(offers, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    families = {}
    for o in offers:
        if not o.get("variantVerified") or o.get("stockStatus") != "volgens winkel op voorraad":
            continue
        key, price = identity(o), cash(o.get("price"))
        if not key or price is None or not o.get("url") or not o.get("store"):
            continue
        try:
            checked = dt.datetime.fromisoformat(str(o["checkedAt"]).replace("Z", "+00:00"))
            if checked.tzinfo is None or not dt.timedelta() <= now - checked <= dt.timedelta(hours=48):
                continue
        except (ValueError, TypeError, KeyError):
            continue
        families.setdefault(key, []).append({**o, "_money": price})
    result = []
    for key, rows in families.items():
        by_store = {}
        for o in rows:
            store_key = o["store"].casefold()
            if store_key not in by_store or o["_money"] < by_store[store_key]["_money"]:
                by_store[store_key] = o
        stores = sorted(by_store.values(), key=lambda x: x["_money"])
        if len(stores) < 2:
            continue
        cheapest, highest = stores[0], stores[-1]
        if cheapest["_money"] >= highest["_money"]:
            continue
        gap = highest["_money"] - cheapest["_money"]
        percent = gap / highest["_money"] * 100
        result.append({
            "id": key, "product": cheapest["title"],
            "identity": key.split(":")[0].upper(), "identityCode": key.split(":", 1)[1],
            "storesCount": len(stores),
            "lowestObservedArticlePriceEUR": float(cheapest["_money"]),
            "highestObservedArticlePriceEUR": float(highest["_money"]),
            "articlePriceDifferenceEUR": float(gap),
            "articlePriceDifferencePct": float(round(percent, 1)),
            "bestStore": cheapest["store"],
            "referenceStore": highest["store"],
            "purchaseSavingsVerified": False, "allInVerified": False,
            "status": "prijsverschil_exclusief_verzendkosten",
            "shippingStatus": "Niet volledig gecontroleerd voor dezelfde winkelmand",
            "offers": [
                {"store": o["store"], "url": o["url"], "priceEUR": float(o["_money"]),
                 "shippingNote": o.get("shippingNote", ""),
                 "checkedAt": o["checkedAt"],
                 "merchantCountry": o.get("merchantCountry", "NL"),
                 "stockStatus": o["stockStatus"]}
                for o in stores
            ]
        })
    return sorted(result, key=lambda x: (-x["articlePriceDifferenceEUR"], -x["storesCount"], x["id"]))


def build(source=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    source = source if source is not None else json.loads(INPUT.read_text(encoding="utf-8"))
    gaps = find_gaps(source.get("offers", []), now=now)
    return {
        "updatedAt": now.isoformat(), "observationsCheckedAt": source.get("checkedAt"),
        "comparisons": gaps, "comparableGroups": len(gaps),
        "verifiedAllInDeals": 0,
        "note": "Verschillen in artikelprijzen van exact identieke GTIN/MPN waarnemingen, MET voorraadmelding. Verzendkosten en werkelijk bespaarde euro's zijn niet geverifieerd. Geen gegarandeerde korting of gerealiseerde besparing.",
    }


if __name__ == "__main__":
    output = build()
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sameProductPriceComparisons":len(output["comparisons"]),
                      "verifiedAllInDeals": 0}, ensure_ascii=False))
