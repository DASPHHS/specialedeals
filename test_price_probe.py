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
 def test_shopify_variant_selection(self):
  data={"variants":[{"id":1,"title":"350 gram koffiebonen","price":1295,"available":True},{"id":2,"title":"1000 gram koffiebonen","price":3500,"available":True}]}
  target={"id":"coffee","adapter":"shopify","url":"https://shop.example/products/coffee","seller":"Coffee Shop","productId":"coffee","variantKey":"1000g","variantTitle":"1000 gram koffiebonen"}
  x=probe(target,lambda _:json.dumps(data))
  self.assertEqual(x["status"],"product_price_candidate")
  self.assertEqual(x["priceEUR"],"35.00")
  self.assertFalse(x["shippingVerified"])
 def test_shopify_missing_variant_rejected(self):
  target={"id":"coffee","adapter":"shopify","url":"https://shop.example/products/coffee","variantTitle":"500 gram"}
  self.assertEqual(probe(target,lambda _:json.dumps({"variants":[]}))["status"],"identity_not_matched")
 def test_source_error(self):
  def fail(_): raise TimeoutError()
  self.assertEqual(probe({"id":"a","url":"https://shop.example/p","sku":"SKU-100"},fail)["status"],"source_error")
if __name__=="__main__":unittest.main()
