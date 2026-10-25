import datetime as dt
import unittest
from price_comparisons import find_gaps, build, identity

NOW = dt.datetime(2026, 10, 25, 20, 0, tzinfo=dt.timezone.utc)


def offer(store, price, gtin="4001638093989", stock="volgens winkel op voorraad",
          variant=True, hours=1, mpn=""):
    return {
        "title": "Weleda Skin Food 75 ml", "store": store,
        "price": price, "gtin": gtin, "mpn": mpn, "variantVerified": variant,
        "stockStatus": stock, "url": "https://example.com/" + store,
        "checkedAt": (NOW - dt.timedelta(hours=hours)).isoformat(),
        "shippingNote": "Verzending onbekend",
    }


class ComparablePrices(unittest.TestCase):
    def test_exact_gtin_compares_independent_shops(self):
        groups = find_gaps([offer("shop-a", 8.99), offer("shop-b", 10.49)], NOW)
        self.assertEqual(len(groups), 1)
        result = groups[0]
        self.assertEqual(result["articlePriceDifferenceEUR"], 1.50)
        self.assertEqual(result["articlePriceDifferencePct"], 14.3)
        self.assertEqual(result["bestStore"], "shop-a")
        self.assertFalse(result["purchaseSavingsVerified"])
        self.assertFalse(result["allInVerified"])

    def test_different_gtin_not_same_product_even_when_title_matches(self):
        self.assertEqual(find_gaps([offer("a", 8, "4001638093989"),
                                    offer("b", 10, "4001638501491")], NOW), [])

    def test_out_of_stock_low_price_does_not_create_fake_saving(self):
        self.assertEqual(find_gaps([offer("a", 4.00, stock="uitverkocht"),
                                    offer("b", 10.00)], NOW), [])

    def test_unverified_variant_or_stale_prices_are_excluded(self):
        self.assertEqual(find_gaps([offer("a", 4.00, variant=False),
                                    offer("b", 10.00)], NOW), [])
        self.assertEqual(find_gaps([offer("a", 4.00, hours=49),
                                    offer("b", 10.00)], NOW), [])

    def test_unconfirmed_gtin_does_not_infer_from_name(self):
        self.assertEqual(find_gaps([offer("a", 4.00, gtin=""),
                                    offer("b", 10.00, gtin="")], NOW), [])

    def test_one_store_repeated_not_independent_comparison(self):
        self.assertEqual(find_gaps([offer("a", 4.00), offer("a", 10.00)], NOW), [])

    def test_mpn_fallback_when_gtin_missing(self):
        self.assertEqual(identity(offer("a", 4, gtin="", mpn="SKU-X156")), "mpn:sku-x156")
        self.assertEqual(len(find_gaps([offer("a", 4, gtin="", mpn="SKU-X156"),
                                        offer("b", 6, gtin="", mpn="SKU-X156")], NOW)), 1)

    def test_never_mark_money_saved(self):
        data = build({"checkedAt": NOW.isoformat(),
                      "offers": [offer("a", 8.99), offer("b", 10.49)]}, now=NOW)
        self.assertEqual(data["verifiedAllInDeals"], 0)
        self.assertFalse(data["comparisons"][0]["purchaseSavingsVerified"])


if __name__ == "__main__":
    unittest.main()
