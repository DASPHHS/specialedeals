import unittest
import scan
class ScannerTests(unittest.TestCase):
    def test_single_euro_price(self):
        self.assertEqual(scan.extract_price("Prijs: € 129,95"), 129.95)
        self.assertEqual(scan.extract_price("EUR 85.00"), 85)
    def test_ambiguous_price(self):
        self.assertIsNone(scan.extract_price("Van € 150,00 voor € 99,00"))
    def test_no_price(self):
        self.assertIsNone(scan.extract_price("Alleen vandaag korting"))
    def test_gender_filter(self):
        score, _ = scan.score("Salomon damesschoenen")
        self.assertLess(score, 0)
    def test_men_lifestyle(self):
        score, _ = scan.score("Adidas Metalbone Carbon padelracket")
        self.assertGreater(score, 0)
if __name__ == "__main__":
    unittest.main()
