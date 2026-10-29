import json
import unittest
from price_probe import probe

PAGE='<script type="application/ld+json">'+json.dumps({"@type":"Product","name":"Sample Product 100 ml","sku":"SKU-100","offers":{"@type":"Offer","price":"25.50","priceCurrency":"EUR","availability":"https://schema.org/InStock"}})+'</script>'
class ProbeTests(unittest.TestCase):
 def test_matching_identity_is_only_candidate(self):
  t={"id":"a","url":"https://shop.example/p","seller":"Shop","productId":"p","variantKey":"100ml","sku":"SKU-100","expectedName":"Sample Product"}
  x=probe(t,lambda _:PAGE)
  self.assertEqual(x["status"],"product_price_candidate")
  self.assertFalse(x["shippingVerified"])
  self.assertIsNone(x["shipsToNL"])
 def test_wrong_sku_not_accepted(self):
  self.assertEqual(probe({"id":"a","url":"https://shop.example/p","sku":"OTHER"},lambda _:PAGE)["status"],"identity_not_matched")
 def test_without_identity_rejected(self):
  self.assertEqual(probe({"id":"a","url":"https://shop.example/p"},lambda _:PAGE)["status"],"identity_not_configured")
 def test_source_error(self):
  def fail(_): raise TimeoutError()
  self.assertEqual(probe({"id":"a","url":"https://shop.example/p","sku":"SKU-100"},fail)["status"],"source_error")
if __name__=="__main__":unittest.main()
