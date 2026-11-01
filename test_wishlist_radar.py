import json
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from wishlist_radar import contains, fresh_offer, matches, produce, verified_deal, variation_note

NOW = datetime(2026, 11, 1, 13, 0, tzinfo=ZoneInfo("Europe/Amsterdam"))
WISH = {
    "items": [
        {"id": "apple-airpods-pro", "name": "AirPods Pro", "matchAny": ["AirPods Pro"],
         "excludeTerms": ["hoesje", "case only"]},
        {"id": "apple-airpods", "name": "AirPods ANC", "matchAny": ["AirPods"],
         "excludeTerms": ["AirPods Pro", "case"]},
        {"id": "hoka-schoenen", "name": "HOKA heren 47⅓", "matchAny": ["HOKA Arahi"]},
    ]
}
def entry(title, **kw):
    return {
        "id": title, "product": title, "winkel": "Voorbeeldwinkel", "bron": "Prijsfeed",
        "url": "https://winkel.example/item", "prijs": 99.95,
        "tot": "2026-11-04", "waargenomen_op": "2026-11-01", **kw
    }


class RadarTests(unittest.TestCase):
    def test_exact_phrase_and_exclusion(self):
        self.assertTrue(contains("Apple AirPods Pro 3", "AirPods Pro"))
        self.assertFalse(contains("AirPods Products", "AirPods Pro"))
        self.assertFalse(matches("AirPods Pro siliconen hoesje", WISH["items"][0]))
        self.assertTrue(matches("AirPods Pro 3", WISH["items"][0]))
        self.assertFalse(matches("AirPods Pro 3", WISH["items"][1]))
        self.assertTrue(matches("HOKA Arahi 7 heren", WISH["items"][2]))

    def test_size_not_fabricated(self):
        self.assertIn("niet bevestigd", variation_note("HOKA Arahi 7 heren", WISH["items"][2]))
        self.assertIn("niet bevestigd", variation_note("AirPods 4", WISH["items"][1]))
        self.assertIn("controleren", variation_note("HOKA Arahi EU 47 1/3", WISH["items"][2]))

    def test_expired_or_unknown_end_excluded(self):
        now = NOW.date()
        self.assertFalse(fresh_offer(entry("HOKA Arahi", tot="2026-10-31"), now))
        self.assertFalse(fresh_offer(entry("HOKA Arahi", tot="", waargenomen_op="2026-10-31"), now))
        self.assertTrue(fresh_offer(entry("HOKA Arahi", tot="", waargenomen_op="2026-11-01"), now))
        self.assertFalse(fresh_offer(entry("HOKA Arahi", van="2026-11-08"), now))

    def test_store_reference_is_not_verified(self):
        r = produce(WISH, [
            {"deals": [entry("AirPods Pro 3", korting=.7, van_prijs=329),
                       entry("HOKA Arahi 7 heren")]}], {"deals": []}, NOW)
        self.assertEqual(r["candidateCount"], 2)
        self.assertEqual(r["verifiedDealCount"], 0)
        p = r["items"][0]["candidates"][0]
        self.assertFalse(p["verifiedDiscount"])
        self.assertEqual(p["storeDiscountPercent"], 70.0)
        self.assertEqual(p["status"], "Onbevestigde winkelactie")

    def test_verified_requires_real_complete_price_and_freshness(self):
        verified = {
            "title": "AirPods Pro 3", "url": "https://shop.example/item",
            "source": "Shop", "sku": "pro3", "priceVerified": True,
            "totalPriceEUR": 179, "referencePriceEUR": 220,
            "discountPercent": 18.6, "verifiedAt": NOW.isoformat()
        }
        self.assertIsNotNone(verified_deal(verified, WISH["items"][0], NOW))
        for changed in (
            {"priceVerified": False}, {"referencePriceEUR": 180},
            {"totalPriceEUR": None}, {"sku": None},
            {"verifiedAt": (NOW-timedelta(hours=40)).isoformat()},
            {"url": "http://unsafe.example/"}, {"title": "AirPods Pro hoesje"},
        ):
            self.assertIsNone(verified_deal({**verified, **changed}, WISH["items"][0], NOW))

    def test_dedupe_and_summary(self):
        r = produce(WISH, [{"updated_at": NOW.isoformat(),
            "deals": [entry("AirPods Pro 3"),entry("AirPods Pro 3")]}],
            {"deals": []}, NOW)
        self.assertEqual(r["wishCount"], 3)
        self.assertEqual(r["candidateCount"], 1)
        self.assertEqual(r["shopsSeen"], 1)


if __name__ == "__main__":
    unittest.main()
