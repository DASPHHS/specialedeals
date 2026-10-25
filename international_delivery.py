#!/usr/bin/env python3
"""Calculate NL-bound indicative landed prices for foreign merchants.

Policy tariff estimates are not checkout proof. In particular, never infer that
a merchant shipping to NL means every item or brand can be shipped to NL.
"""
import json
import pathlib
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

ROOT = pathlib.Path(__file__).resolve().parent
STORES = ROOT / "international-stores.json"


def amount(value):
    if isinstance(value, bool):
        return None
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not x.is_finite() or x < 0:
        return None
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_stores():
    data = json.loads(STORES.read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["retailers"]}


def estimate_delivery_to_nl(store, price_eur, checkout_shipping_eur=None):
    """Return a tariff-informed estimate, never a 'verified deal'.

    Costs for return shipping are decision context, not automatically
    added to purchase cost. Checkout, product size and exact taxes still
    require verification.
    """
    price = amount(price_eur)
    if price is None or price < Decimal("0.50"):
        return {"status": "invalid_price", "allInVerified": False}
    if store.get("currency") != "EUR":
        return {"status": "exchange_rate_required", "allInVerified": False}
    if store.get("shippingToNL") != "confirmed_store_level":
        return {"status": "destination_unconfirmed", "allInVerified": False}
    policy = store.get("shipping", {})
    shipping = None
    status = "requires_checkout"
    evidence = "No exact NL checkout/shipping amount available."
    if checkout_shipping_eur is not None:
        shipping = amount(checkout_shipping_eur)
        if shipping is None:
            return {"status": "invalid_checkout_shipping", "allInVerified": False}
        status = "basket_shipping_observed"
        evidence = "Shipping entered from basket; product and tax verification still required."
    elif policy.get("mode") == "threshold_estimate":
        cutoff = amount(policy.get("thresholdEUR"))
        below = amount(policy.get("belowEUR"))
        above = amount(policy.get("atOrAboveEUR"))
        if None not in (cutoff, below, above):
            shipping = below if price < cutoff else above
            status = "published_tariff_estimate"
            evidence = "Published standard parcel tariff; basket and oversize exceptions may change it."
    estimate = float(price + shipping) if shipping is not None else None
    return {
        "status": status, "articlePriceEUR": float(price),
        "shippingEstimateEUR": float(shipping) if shipping is not None else None,
        "estimatedTotalEUR": estimate, "allInVerified": False,
        "nlDelivery": "store_level_only_not_item_approved",
        "customs": store.get("taxes", {}).get("customs", "must_verify"),
        "evidence": evidence,
    }


def eligible_to_present_as_verified_deal(quote, *, item_delivery_confirmed=False,
                                         price_and_variant_verified=False,
                                         full_checkout_total_verified=False,
                                         independent_market_comparison_verified=False,
                                         customs_and_vat_accounted=False):
    """Evidence gate; external flags must reflect real checks, never inference."""
    return all((quote.get("status") == "basket_shipping_observed",
                item_delivery_confirmed, price_and_variant_verified,
                full_checkout_total_verified,
                independent_market_comparison_verified,
                customs_and_vat_accounted))


if __name__ == "__main__":
    print(json.dumps({"registeredForeignStores": len(load_stores()),
                      "destination": "NL", "status": "policy_and_calculator_only"}))
