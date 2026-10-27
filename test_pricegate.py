import datetime as dt
import unittest
from deal_verification import verified_offers

NOW=dt.datetime(2026,10,28,8,tzinfo=dt.timezone.utc)

def deal(**changes):
    record=dict(id="apple-watch-ultra-4",title="Apple Watch Ultra 4",
        source="Amac",url="https://www.amac.nl/apple-watch-ultra-4",
        sku="WATCH-ULTRA-4-49MM",comparisonSku="WATCH-ULTRA-4-49MM",
        totalPriceEUR=899,comparisonTotalPriceEUR=999,
        comparisonUrl="https://www.example.com/price-check",
        comparisonType="competing_retailer",condition="new",comparisonCondition="new",
        inStock=True,shipsToNL=True,verified=True,identicalVariantChecked=True,
        includesAllDeliveryCosts=True,sellerTrusted=True,verifiedAt="2026-10-28T07:00:00+00:00")
    record.update(changes)
    return record

class StrictDealRules(unittest.TestCase):
    def test_ten_percent_passes(self):
        rows=verified_offers([deal(totalPriceEUR=899,comparisonTotalPriceEUR=1000)],now=NOW)
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["priceVerified"])
        self.assertGreaterEqual(rows[0]["discountPercent"],10)
    def test_same_price_is_not_sale(self):
        self.assertEqual(verified_offers([deal(totalPriceEUR=899,comparisonTotalPriceEUR=899)],now=NOW),[])
    def test_sub_ten_percent_is_rejected(self):
        self.assertEqual(verified_offers([deal(totalPriceEUR=899,comparisonTotalPriceEUR=980)],now=NOW),[])
    def test_advertised_discount_without_evidence_is_rejected(self):
        self.assertEqual(verified_offers([deal(comparisonUrl="")],now=NOW),[])
        self.assertEqual(verified_offers([deal(verified=False)],now=NOW),[])
    def test_wrong_variant_refurbished_and_out_of_stock(self):
        self.assertEqual(verified_offers([deal(comparisonSku="OTHER")],now=NOW),[])
        self.assertEqual(verified_offers([deal(comparisonCondition="refurbished")],now=NOW),[])
        self.assertEqual(verified_offers([deal(inStock=False)],now=NOW),[])
    def test_stale_and_shipping_cost_uncertainty(self):
        self.assertEqual(verified_offers([deal(verifiedAt="2026-10-26T06:00:00+00:00")],now=NOW),[])
        self.assertEqual(verified_offers([deal(includesAllDeliveryCosts=False)],now=NOW),[])
    def test_empty_deals(self):
        self.assertEqual(verified_offers([],now=NOW),[])

if __name__=="__main__":unittest.main()
