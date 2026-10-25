import datetime as dt
import unittest
from unittest import mock
import sample_events_scan as scan


class SampleEventsTests(unittest.TestCase):
    def test_extract_relevant_active_mens_sale(self):
        html = ('<h2><a href="/9244/van-dal-mannenmode-outlet-nov-2026.html">'
                'Van Dal mannenmode Outlet</a></h2><p>Breda 17 November 2026 --- '
                '21 November 2026</p><p>Herenmaten M tot 4XL</p>')
        found = scan.parse_listings(html, today=dt.date(2026, 10, 25))
        self.assertEqual(len(found), 1)
        result = next(iter(found.values()))
        self.assertEqual(result["startDate"], "2026-11-17")
        self.assertEqual(result["endDate"], "2026-11-21")
        self.assertIn("stockverkopen.nl/9244/", result["url"])
        self.assertNotIn("verified", result)

    def test_expired_sale_excluded(self):
        html = ('<h2><a href="/1234/old.html">Petrol menswear sample sale</a></h2>'
                '<p>Tilburg 12 Oktober 2026 --- 20 Oktober 2026</p>')
        self.assertEqual(scan.parse_listings(html, dt.date(2026, 10, 25)), {})

    def test_women_only_excluded(self):
        html = ('<h2><a href="/9000/women.html">Lingerie sample sale</a></h2>'
                '<p>Haarlem 30 Oktober 2026 --- 31 Oktober 2026</p>')
        self.assertEqual(scan.parse_listings(html, dt.date(2026, 10, 25)), {})

    def test_no_invented_size_or_discount(self):
        html = ('<h2><a href="/9001/kuyichi.html">Kuyichi Sample Sale</a></h2>'
                '<p>Vleuten 29 Oktober 2026 --- 31 Oktober 2026</p>')
        event = next(iter(scan.parse_listings(html, dt.date(2026, 10, 25)).values()))
        self.assertIn("controleren", event["sizes"])
        self.assertIn("controleren", event["verification"])


if __name__ == "__main__":
    unittest.main()
