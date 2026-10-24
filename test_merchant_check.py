import unittest
from merchant_check import find_observation,asprice,classify_stock,availability,same_observed_product
TARGET={"require":["metalbone","carbon"]}
class MerchantTests(unittest.TestCase):
 def test_competitor_identity(self):
  self.assertTrue(same_observed_product({"gtin":"1234567890123"},{"gtin":"1234567890123"}))
  self.assertTrue(same_observed_product({"mpn":"AR2AA2U22"},{"mpn":"AR2AA2U22"}))
  self.assertFalse(same_observed_product({"gtin":"1234567890123"},{"gtin":"1234567890124"}))
  self.assertFalse(same_observed_product({"title":"Adidas Metalbone Carbon"},{"title":"Adidas Metalbone Carbon"}))
 def test_product_gtin(self):
  h='<script type="application/ld+json">{"@type":"Product","name":"Adidas Metalbone Carbon 26","gtin13":"8436548240123","offers":{"price":125,"priceCurrency":"EUR"}}</script>'
  self.assertEqual(find_observation(h,TARGET)["gtin"],"8436548240123")
 def test_no_gtin_fallback(self):
  h='<meta property="og:title" content="Adidas Metalbone Carbon 26"><meta property="product:price:amount" content="125.00">'
  self.assertEqual(find_observation(h,TARGET)["gtin"],"")
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
 def test_structured_outofstock(self):
  self.assertEqual(availability("https://schema.org/OutOfStock"),"uitverkocht")
 def test_stock_conflict(self):
  self.assertEqual(classify_stock("https://schema.org/OutOfStock","Op voorraad: 6 Items"),"tegenstrijdige voorraadinformatie")
 def test_in_stock(self):
  self.assertEqual(classify_stock("https://schema.org/InStock","Op voorraad: 2 Items"),"volgens winkel op voorraad")
 def test_html_conflict(self):
  h='<script type="application/ld+json">{"@type":"Product","name":"Adidas Metalbone Carbon 26","offers":{"price":125,"availability":"https://schema.org/OutOfStock"}}</script><p>Op voorraad: 6 Items</p>'
  self.assertEqual(find_observation(h,TARGET)["stockStatus"],"tegenstrijdige voorraadinformatie")
if __name__=="__main__":unittest.main()
