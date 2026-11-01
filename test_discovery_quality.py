"""Regression checks for noisy winactie searches and stale sample-sale listings."""
import datetime as dt
import unittest
from unittest.mock import patch
import discover_winacties as win
import scan


class DiscoveryQuality(unittest.TestCase):
 def test_concours_is_not_always_a_competition(self):
  bad=[
    ("Concours Parts and Accessories","https://concoursparts.com/","Restoration parts for cars"),
    ("Las Vegas Concours 2026 Schedule of Events","https://www.lasvegasconcours.com/events","Classic car parade"),
    ("CONCOURS - Définition et signification","https://mobile-dictionary.reverso.net/francais-definition/concours","Définition"),
    ("Las Vegas Car Shows | 2026 Las Vegas Concours at Wynn","https://www.lasvegasconcours.com","Car exhibition"),
    ("How to win a road race","https://example.com/racing","Win the race with a bike"),
    ("Win een Fiat Topolino","http://not-secure.test/win","Gratis auto"),
  ]
  for title,url,description in bad:
   with self.subTest(title=title):
    self.assertFalse(win.valid_candidate(title,url,description))

 def test_actual_prize_word_and_prize_topic_needed(self):
  self.assertTrue(win.valid_candidate("Win een elektrische fiets","https://aanbieder.example/win","Gratis deelname"))
  self.assertTrue(win.valid_candidate("Winactie Dyson stofzuiger 2026","https://aanbieder.example/winactie","Actie"))
  self.assertFalse(win.valid_candidate("Prijsvraag over de spelling","https://aanbieder.example/les","Geen hoofdprijs"))
  self.assertFalse(win.valid_candidate("Gewinnspiel Handy","https://anbieder.example","Alleen vragen, geen prijs"))

 def test_brand_archive_not_an_event(self):
  self.assertFalse(scan.is_real_sample_sale_event("Tommy Hilfiger","https://www.stockverkopen.nl/samplesales_per_merk/224/Tommy_Hilfiger"))
  self.assertFalse(scan.is_real_sample_sale_event("Sample Sales","https://www.stockverkopen.nl/samplesales.html"))
  self.assertTrue(scan.is_real_sample_sale_event("Circle of Trust Sample Sale Winter 2026","https://www.stockverkopen.nl/9246/circle-of-trust-sample-sale-winter-2026-nov-2026.html"))
  self.assertTrue(scan.is_real_sample_sale_event("Kuyichi Sample Sale","https://www.welovesamplesales.nl/samplesaleagenda/8298/kuyichi-sample-sale--2026"))
  self.assertFalse(scan.is_real_sample_sale_event("Wintersale 2025","https://www.stockverkopen.nl/9246/sample-sale-2025.html"))

 def test_curated_event_rechecks_actual_dates_and_is_never_verified_discount(self):
  import json
  from pathlib import Path
  event=json.loads(Path("sample-sales-to-watch.json").read_text())["items"][0]
  now="2026-11-01T13:00:00+00:00"
  html='<h1>Circle of Trust Sample Sale Winter 2026</h1><div>25 November 2026</div><div>27 November 2026</div>'
  offer=scan.read_curated_event(event,now,fetch_page=lambda _:html)
  self.assertEqual(offer["kind"],"sales")
  self.assertEqual(offer["startDate"],"2026-11-25")
  self.assertEqual(offer["endDate"],"2026-11-27")
  self.assertFalse(offer["organizerVerified"])
  self.assertFalse(offer["priceVerified"])
  self.assertIn("Ticket vereist",offer["conditions"])
  self.assertIsNone(scan.read_curated_event(event,now,fetch_page=lambda _:"Generic brand archive"))
  self.assertIsNone(scan.read_curated_event(event,"2026-11-28T13:00:00+00:00",fetch_page=lambda _:html))

 def test_stale_event_not_carried_forward(self):
  today=dt.date(2026,11,1)
  e={"title":"Kuyichi Sample Sale","url":"https://www.welovesamplesales.nl/samplesaleagenda/8298/kuyichi-sample-sale--2026",
     "lastSeenAt":"2026-10-28T10:00:00+00:00"}
  self.assertFalse(scan.valid_retained_sale(e,today))
  e["lastSeenAt"]="2026-10-31T10:00:00+00:00"
  self.assertTrue(scan.valid_retained_sale(e,today))
  e["url"]="https://www.stockverkopen.nl/samplesales_per_merk/224/Tommy_Hilfiger"
  self.assertFalse(scan.valid_retained_sale(e,today))


if __name__=="__main__":
 unittest.main()
