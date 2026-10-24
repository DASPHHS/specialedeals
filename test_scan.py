import unittest
import scan
class ScannerTests(unittest.TestCase):
 def test_price(self):self.assertEqual(scan.extract_price("€ 129,95"),129.95)
 def test_ambiguous(self):self.assertIsNone(scan.extract_price("€ 100,00 naar € 80,00"))
 def test_branded(self):self.assertGreater(scan.score("Weleda Skin Food aanbieding")[0],0)
 def test_irrelevant(self):self.assertLess(scan.score("Ninja airfryer sale")[0],0)
 def test_womens(self):self.assertLess(scan.score("Salomon dames schoenen sale")[0],0)
 def test_apple_fruit(self):self.assertLess(scan.score("Apple pie recipe discount")[0],0)
 def test_metalbone(self):self.assertGreater(scan.score("Adidas Metalbone Carbon 2026 padelracket aanbieding")[0],0)
 def test_sample_aliases(self):
  self.assertTrue(scan.is_sample("Ralph Lauren magazijnverkoop in Rotterdam"))
  self.assertTrue(scan.is_sample("Nike warehouse sale Amsterdam"))
  self.assertFalse(scan.is_sample("Kuyichi jeans normaal"))
 def test_broad_brand_filter(self):
  self.assertLess(scan.score("willekeurige matrassen aanbieding")[0],0)
 def test_kind(self):self.assertEqual(scan.promotion_kind("Winactie maak kans op Davines"),"winactie")
 def test_rss(self):
  rss='<rss><channel><item><title>Weleda Skin Food sale</title><link>https://example.com/w</link></item></channel></rss>'
  self.assertEqual(len(scan.rss_items(rss,"test","news")),1)
if __name__=="__main__":unittest.main()
