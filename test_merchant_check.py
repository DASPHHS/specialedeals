import unittest
from merchant_check import find_observation,asprice
TARGET={"require":["metalbone","carbon"]}
class MerchantTests(unittest.TestCase):
 def test_jsonld(self):
  h='<script type="application/ld+json">{"@type":"Product","name":"Adidas Metalbone Carbon 26","offers":{"price":"125.00","priceCurrency":"EUR","availability":"https://schema.org/InStock"}}</script>'
  self.assertEqual(find_observation(h,TARGET)["price"],125.)
 def test_graph(self):
  h='<script type="application/ld+json">{"@graph":[{"@type":"Organization","name":"X"},{"@type":"Product","name":"Metalbone Carbon","offers":{"price":125}}]}</script>'
  self.assertEqual(find_observation(h,TARGET)["price"],125)
 def test_wrong_variant(self):
  h='<script type="application/ld+json">{"@type":"Product","name":"Adidas Metalbone HRD+","offers":{"price":200}}</script>'
  self.assertIsNone(find_observation(h,TARGET))
 def test_meta(self):
  h='<meta property="og:title" content="Adidas Metalbone Carbon 26"><meta property="product:price:amount" content="125.00">'
  self.assertEqual(find_observation(h,TARGET)["price"],125)
 def test_range(self):self.assertIsNone(asprice("99,99-199,99"))
 def test_empty(self):self.assertIsNone(find_observation("<div>€125</div>",TARGET))
if __name__=="__main__":unittest.main()
