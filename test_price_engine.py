import datetime as dt
import unittest
from price_engine import money,extract_product_offers,assess,rank

NOW=dt.datetime(2026,10,28,12,tzinfo=dt.timezone.utc)
def obs(**kwargs):
    d=dict(productId="watch",variantKey="ultra-3-49mm-new",condition="new",seller="Shop A",url="https://shop.example/watch",priceEUR="799",shippingEUR="0",checkedAt="2026-10-28T11:00:00Z",currency="EUR",inStock=True,shipsToNL=True,variantMatched=True,sellerTrusted=True,shippingVerified=True)
    d.update(kwargs);return d
class PriceEngineTests(unittest.TestCase):
 def test_price_locales(self):
    self.assertEqual(str(money("1.299,95")),"1299.95")
    self.assertEqual(str(money("1,299.95")),"1299.95")
 def test_missing_shipping_rejected(self):
    x=obs();x.pop("shippingEUR");self.assertIsNone(assess(x,NOW)[0])
 def test_unverified_rejected(self):self.assertIsNone(assess(obs(shippingVerified=False),NOW)[0])
 def test_stale_rejected(self):self.assertIsNone(assess(obs(checkedAt="2026-10-26T11:00:00Z"),NOW)[0])
 def test_same_variant_and_condition(self):
    r=rank([obs(),obs(seller="Shop B",priceEUR="790",shippingEUR="15"),obs(variantKey="ultra-4-49mm-new",priceEUR="900"),obs(condition="refurbished",priceEUR="600")],NOW)
    self.assertEqual(len(r["items"]),3)
    self.assertEqual(r["items"][1]["lowestChecked"]["seller"],"Shop A")
    self.assertEqual(r["items"][1]["checkedSellerCount"],2)
    self.assertEqual(r["items"][1]["discountStatus"],"not_established_without_valid_independent_reference")
 def test_jsonld_extraction(self):
    page='<script type="application/ld+json">{"@type":"Product","name":"Watch Ultra 3","sku":"U3","offers":{"@type":"Offer","price":"799.95","priceCurrency":"EUR","availability":"https://schema.org/InStock"}}</script>'
    x,state=extract_product_offers(page,"Watch Ultra 3")
    self.assertEqual(state,"parsed");self.assertEqual(x[0]["priceEUR"],"799.95")
 def test_ambiguous_product_rejected(self):
    page='<script type="application/ld+json">[{"@type":"Product","name":"Watch A"},{"@type":"Product","name":"Watch B"}]</script>'
    self.assertEqual(extract_product_offers(page)[1],"ambiguous_or_missing_product")
 def test_listing_without_offers_is_not_a_price(self):
    self.assertEqual(extract_product_offers('<h1>Apple Watch Ultra 4</h1>')[0],[])
if __name__=="__main__":unittest.main()
