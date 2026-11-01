"""Tests for the 23 supplied search profiles and cautious external feed observations."""
import importlib.util
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("merchant_adapter", ROOT/"integrations"/"merchant_feeds"/"adapter.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SourceCatalogTests(unittest.TestCase):
    def test_all_23_uploaded_wishes_preserved(self):
        doc=json.loads((ROOT/"wishlist.json").read_text(encoding="utf-8"))
        profiles=doc["searchProfiles"]
        self.assertEqual(len(profiles),23)
        self.assertEqual([x["position"] for x in profiles],list(range(1,24)))
        self.assertEqual(len({x["name"] for x in profiles}),23)
        ids={x["id"] for x in doc["items"]}
        services={x["id"] for x in doc["serviceProfiles"]}
        plan=json.loads((ROOT/"onderzoeksplan.json").read_text())
        routes={p["id"] for p in plan["targets"]}|{i for t in plan["targets"] for i in t.get("wishlistIds",[])}
        for p in profiles:
            if p["kind"]=="product":
                self.assertTrue(set(p["wishlistIds"]) <= ids,p)
                self.assertTrue(set(p["wishlistIds"]) <= routes,p)
            elif p["kind"]=="service":
                self.assertIn(p["serviceId"],services)
            else:
                self.assertIn(p["researchTargetId"],routes)
        self.assertEqual(len([x for x in profiles if x["kind"]=="service"]),3)
        for x in doc["serviceProfiles"]:
            self.assertEqual(x["automationStatus"],"comparison_needed")
            self.assertTrue(x["comparisonUnit"])

    def test_normalizer_persists_offer_merchant_separation(self):
        row={"merchant":"Example Online","merchant_id":"M1","offer_id":"O39",
             "name":"Arc'teryx Gamma Pant M","product_url":"https://example.com/pant",
             "price":"119,95","shipping":"5,95","shipping_country":"NL",
             "currency":"EUR","ean":"1234567890123","stock_status":"in_stock",
             "observed_at":"2026-11-01T12:00:00+01:00"}
        a=mod.normalized(row,"licensed-sample")
        self.assertEqual(a["merchantReference"],"M1")
        self.assertEqual(a["offerReference"],"O39")
        self.assertEqual(a["deliveredPriceNL_EUR"],125.9)
        self.assertEqual(a["status"],"research_candidate_not_verified")
        self.assertFalse(a["verifiedDiscount"])
        self.assertIsNone(a["independentReferenceEUR"])

    def test_no_fabricated_shipping_or_discount(self):
        row={"merchant":"Store","name":"Dyson Airwrap",
             "url":"https://shop.example/dyson","price":"499.99",
             "shipping":"0","currency":"EUR"}
        a=mod.normalized(row,"approved")
        self.assertIsNone(a["deliveredPriceNL_EUR"])
        self.assertFalse(a["shippingCountryConfirmed"])
        self.assertIsNone(a["independentReferenceEUR"])
        self.assertIsNone(a["observedAt"])
        self.assertIsNone(mod.normalized({**row,"url":"http://shop.example"},"x"))

    def test_reject_unusable_catalog_rows(self):
        good={"merchant":"Store","name":"Dyson Airwrap","url":"https://shop.example/item",
              "price":"300","currency":"EUR"}
        variants=[
            {"url":"javascript:alert(1)"},{"url":"http://shop.example/item"},
            {"price":"NaN"},{"price":"-3"},{"price":"1.234,23"},
            {"price":"300","currency":"USD"},{"price":"10000000"},
            {"shipping":"-4"},{"merchant":""},{"name":"X"},
        ]
        for changed in variants:
            with self.subTest(changed=changed):
                self.assertIsNone(mod.normalized({**good,**changed},"x"))


if __name__=="__main__":
    unittest.main()
