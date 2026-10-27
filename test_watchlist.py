import json
import unittest
import scan


class WishlistAndProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("wishlist.json",encoding="utf-8") as stream:
            cls.wishlist=json.load(stream)["items"]
        with open("radar-profiel.json",encoding="utf-8") as stream:
            cls.profile=json.load(stream)

    def hits(self,title):
        return set(scan.wishlist_hits(title,self.wishlist))

    def test_wishlist_covers_apple_models(self):
        for item in ("apple-airpods","apple-airpods-pro","apple-macbook","apple-watch-ultra"):
            self.assertIn(item,{p["id"] for p in self.wishlist})

    def test_separate_airpods_vs_pro(self):
        self.assertEqual(self.hits("Apple AirPods 4 aanbieding"),{"apple-airpods"})
        self.assertEqual(self.hits("Apple AirPods Pro 3 noise cancelling korting"),{"apple-airpods-pro"})
        self.assertEqual(self.hits("Apple AirPods Max sale"),set())

    def test_macbook_and_watch_ultra(self):
        self.assertIn("apple-macbook",self.hits("Apple MacBook Air M5 16GB 512GB korting"))
        self.assertIn("apple-watch-ultra",self.hits("Apple Watch Ultra 3 aanbieding"))
        self.assertNotIn("apple-watch-ultra",self.hits("Apple Watch Ultra bandje"))

    def test_accessories_are_not_deals(self):
        for title in ("Apple Watch Ultra bandje -50%","AirPods case 40% korting","MacBook hoes sale"):
            self.assertFalse(scan.high_quality_candidate(title,"deals","Amac Apple aanbiedingen"))
        self.assertTrue(scan.high_quality_candidate("Apple AirPods Pro 3 korting","deals","Amac Apple aanbiedingen"))

    def test_important_preferences_remain(self):
        self.assertEqual(self.profile["coverage"]["physicalShopRadiusKm"],20)
        self.assertEqual(self.profile["contests"]["minimumPrizeValueEUR"],250)
        self.assertEqual(self.profile["wishlist"]["outdoorOnly"],["Arc'teryx"])
        self.assertEqual(self.profile["homeProjects"]["priority"],["buitenschilderwerk","voortuin"])
        self.assertEqual(self.profile["sampleSales"]["coverage"],"heel Nederland")

    def test_no_unverified_high_value_contests(self):
        self.assertFalse(scan.high_quality_candidate("Win een dure Fiat","contests","Prijsvragen.nl"))


if __name__=="__main__":
    unittest.main()
