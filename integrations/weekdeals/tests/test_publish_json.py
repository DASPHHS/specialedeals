import unittest
from publish_json import compact_offer
from sync_deals import normalize

def source(**kw):
    d={"retailer":"jumbo","product_id":"123","name":"Voorbeeldpak melk",
       "price":2.00,"original_price":2.50,
       "valid_from":"2026-11-01","valid_until":"2026-11-07",
       "unit_price":2.0,"unit":"L","quantity":"1 liter"}
    d.update(kw)
    return d

def convert(p):
    r=normalize(p,"2026-11-01")
    return compact_offer(r,p)

class PublicationContract(unittest.TestCase):
    def test_unit_price_from_source_only(self):
        d=convert(source())
        self.assertEqual(d["eenheidsprijs"],2)
        self.assertEqual(d["eenheid"],"L")
        self.assertEqual(d["prijs"],2)
        self.assertNotIn("bundelprijs",d)

    def test_bundle_price_and_loyalty_kept_separate(self):
        d=convert(source(multi_buy_quantity=2,multi_buy_price=3.0,
                         loyalty_price=1.4,loyalty_program="Jumbo Extra's"))
        self.assertEqual(d["prijs"],2)
        self.assertEqual(d["bundelprijs"],3)
        self.assertEqual(d["bundelaantal"],2)
        self.assertEqual(d["ledenprijs"],1.4)
        self.assertEqual(d["loyaliteitsprogramma"],"Jumbo Extra's")

    def test_aldi_bundle_total_not_compared_to_regular_item_price(self):
        d=convert(source(retailer="aldi",price=3.0,original_price=2.0,
                         multi_buy_quantity=2,multi_buy_price=3.0))
        self.assertEqual(d["prijstype"],"bundeltotaal")
        self.assertEqual(d["prijs"],3)
        self.assertNotIn("van_prijs",d)
        self.assertNotIn("korting",d)

    def test_estimated_validity_marked(self):
        d=convert(source(valid_until_estimated=True))
        self.assertTrue(d["einddatum_geschat"])

    def test_no_guessed_unit_price(self):
        d=convert(source(unit_price=None,unit=None))
        self.assertNotIn("eenheidsprijs",d)
        self.assertNotIn("eenheid",d)

if __name__=="__main__":
    unittest.main()
