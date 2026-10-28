"""Quality checks for catalog and per-product daily research plan."""
import json
import pathlib
import unittest
from urllib.parse import urlsplit

ROOT=pathlib.Path(__file__).resolve().parent

def load(name): return json.loads((ROOT/name).read_text(encoding="utf-8"))

class ResearchCatalogTests(unittest.TestCase):
    def test_source_registry_is_broad_and_deduplicated(self):
        sources=load("bronnenregister.json")["sources"]
        ids=[x["id"] for x in sources]
        self.assertGreaterEqual(len(ids),100)
        self.assertEqual(len(ids),len(set(ids)))
        for x in sources:
            parsed=urlsplit(x["url"])
            self.assertEqual(parsed.scheme,"https",x)
            self.assertTrue(parsed.hostname,x)
            self.assertTrue(x["groups"],x)
            self.assertEqual(x["priceEvidenceStatus"],"not_verified",x)
    def test_plan_covers_real_wishlist_and_household(self):
        plan=load("onderzoeksplan.json")
        source_ids={s["id"] for s in load("bronnenregister.json")["sources"]}
        target_ids={t["id"] for t in plan["targets"]}
        wanted={x["id"] for x in load("prijsradar-config.json")["items"]}
        household={"household-"+p["id"] for c in load("huishoudradar-config.json")["categories"] for p in c["products"]}
        self.assertTrue(wanted <= target_ids,sorted(wanted-target_ids))
        self.assertTrue(household <= target_ids,sorted(household-target_ids))
        self.assertIn("event-sales",target_ids)
        self.assertIn("event-contests",target_ids)
        for t in plan["targets"]:
            for field in ("retailerSourceIds","crosscheckSourceIds","discoverySourceIds"):
                self.assertTrue(set(t[field])<=source_ids,t["id"])
            self.assertGreater(len(t["retailerSourceIds"]),0,t["id"])
            self.assertGreater(len(t["crosscheckSourceIds"]),0,t["id"])
    def test_discovery_does_not_claim_a_discount(self):
        sources=load("bronnenregister.json")["sources"]
        for x in sources:
            self.assertIn("not_verified",x["priceEvidenceStatus"])
        self.assertIn("MSRP",load("onderzoeksplan.json")["targets"][0]["priceEvidence"])

if __name__=="__main__": unittest.main()
