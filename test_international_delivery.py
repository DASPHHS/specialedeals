import unittest
from international_delivery import estimate_delivery_to_nl, eligible_to_present_as_verified_deal, load_stores


class InternationalDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stores = load_stores()

    def test_all_retailers_publish_nl_delivery_evidence(self):
        self.assertGreaterEqual(len(self.stores), 3)
        for shop in self.stores.values():
            self.assertEqual(shop["shippingToNL"], "confirmed_store_level")
            self.assertTrue(shop["shippingPolicyUrl"].startswith("https://"))
            self.assertFalse(shop["productDeliveryVerified"])

    def test_bike24_basket_based_tariffs_are_estimates(self):
        shop = self.stores["bike24"]
        low = estimate_delivery_to_nl(shop, 49.95)
        self.assertEqual(low["shippingEstimateEUR"], 5.99)
        self.assertEqual(low["estimatedTotalEUR"], 55.94)
        self.assertFalse(low["allInVerified"])
        self.assertEqual(low["status"], "published_tariff_estimate")
        high = estimate_delivery_to_nl(shop, 100)
        self.assertEqual(high["shippingEstimateEUR"], 2.99)
        self.assertEqual(high["estimatedTotalEUR"], 102.99)

    def test_variable_tariff_is_never_guessed(self):
        quote = estimate_delivery_to_nl(self.stores["runnerinn"], 75)
        self.assertIsNone(quote["estimatedTotalEUR"])
        self.assertEqual(quote["status"], "requires_checkout")
        self.assertFalse(quote["allInVerified"])

    def test_observed_basket_still_needs_independent_comparison(self):
        q = estimate_delivery_to_nl(self.stores["bike24"], 64, checkout_shipping_eur=5.99)
        self.assertFalse(eligible_to_present_as_verified_deal(q))
        self.assertFalse(eligible_to_present_as_verified_deal(
            q, item_delivery_confirmed=True, price_and_variant_verified=True,
            full_checkout_total_verified=True, customs_and_vat_accounted=True))
        self.assertTrue(eligible_to_present_as_verified_deal(
            q, item_delivery_confirmed=True, price_and_variant_verified=True,
            full_checkout_total_verified=True, customs_and_vat_accounted=True,
            independent_market_comparison_verified=True))

    def test_invalid_prices_and_currency(self):
        self.assertEqual(estimate_delivery_to_nl(self.stores["bike24"], "n/a")["status"], "invalid_price")
        foreign = {**self.stores["bike24"], "currency": "GBP"}
        self.assertEqual(estimate_delivery_to_nl(foreign, 50)["status"], "exchange_rate_required")
        self.assertEqual(estimate_delivery_to_nl(self.stores["bike24"], 15,
            checkout_shipping_eur="-1")["status"], "invalid_checkout_shipping")

if __name__ == "__main__":
    unittest.main()
