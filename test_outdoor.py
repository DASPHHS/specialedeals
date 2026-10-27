import unittest
import scan


class OutdoorPreferencesTests(unittest.TestCase):
    def test_only_arcteryx_from_outdoor_retailer(self):
        self.assertTrue(scan.high_quality_candidate(
            "Arc'teryx Beta Jacket XL 35% korting", "deals", "Bever sale"
        ))
        self.assertFalse(scan.high_quality_candidate(
            "Outdoorschoenen", "deals", "Bergfreunde sale"
        ))
        self.assertFalse(scan.high_quality_candidate(
            "Salomon XT6 50% korting", "deals", "Bever sale"
        ))

    def test_block_other_outdoor_brands_across_sources(self):
        for brand in ("Salomon", "Patagonia", "Mammut", "Norrøna",
                      "Fjällräven", "Rab", "The North Face", "Jack Wolfskin"):
            with self.subTest(brand=brand):
                self.assertFalse(scan.high_quality_candidate(
                    brand + " jacket sale 50%", "deals", "Pepper"
                ))
                self.assertFalse(scan.high_quality_candidate(
                    brand + " Sample Sale", "sales", "Stockverkopen"
                ))

    def test_independent_wishlist_categories_stay_available(self):
        self.assertTrue(scan.high_quality_candidate(
            "HOKA Clifton hardloopschoenen 40% korting", "deals", "Pepper"
        ))
        self.assertTrue(scan.high_quality_candidate(
            "JANZEN Earth huisgeur 40% korting", "deals", "Pepper"
        ))
        self.assertTrue(scan.high_quality_candidate(
            "Ralph Lauren Sample Sale", "sales", "Stockverkopen"
        ))


if __name__ == "__main__":
    unittest.main()
