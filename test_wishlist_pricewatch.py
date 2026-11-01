import unittest
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from wishlist_pricewatch import euro,on_tweakers,valid_model,parse_results,build,choose,QUERIES

NOW=datetime(2026,11,1,15,15,tzinfo=ZoneInfo("Europe/Amsterdam"))
AIR={"id":"apple-airpods-pro","matchAny":["AirPods Pro"],"excludeTerms":["hoesje","cover"]}
ANC={"id":"apple-airpods","matchAny":["AirPods"],"excludeTerms":["AirPods Pro","hoesje","cover"]}
MAC={"id":"apple-macbook","matchAny":["MacBook"]}
PAYLOAD={"articles":[
 {"name":"Apple AirPods Pro 3 USB-C","link":"/pricewatch/2244211/apple-airpods-pro-3-usb-c.html"},
 {"name":"AirPods Pro hoesje","link":"/pricewatch/2244212/hoesje.html"},
 {"name":"Product from another site","link":"https://evil.example/pricewatch/2244213/foobar"},
],"entities":[
 {"type":"product","name":"Apple AirPods Pro 3 USB-C","link":"/pricewatch/2244211/apple-airpods-pro-3-usb-c.html","minPrice":"<span>€ 239,95</span>"},
 {"type":"product","name":"Apple AirPods Pro 2 USB-C","link":"/pricewatch/2231444/airpods-pro-2.html","minPrice":"€ 219,00"},
 {"type":"shop","name":"Apple AirPods Pro case","link":"/pricewatch/2244218/airpods-pro-case.html"},
]}

class PricewatchTests(unittest.TestCase):
 def test_prices(self):
  self.assertEqual(euro("<b>€ 1.299,00</b>"),1299)
  self.assertEqual(euro("€ 799.95"),799.95)
  self.assertEqual(euro("€ 1.299"),1299)
  self.assertIsNone(euro("$999"))
  self.assertIsNone(euro("€0"))
  self.assertIsNone(euro("€9999999"))
 def test_url(self):
  self.assertEqual(on_tweakers("/pricewatch/2244211/foo.html")[1],"2244211")
  self.assertIsNone(on_tweakers("https://fake.tweakers.net.evil.example/pricewatch/2244211/"))
  self.assertIsNone(on_tweakers("https://tweakers.net/blog/2244211/"))
  self.assertIsNone(on_tweakers("javascript:alert(1)"))
 def test_exact_model_and_accessories(self):
  self.assertFalse(valid_model("Apple AirPods Pro case",AIR))
  self.assertFalse(valid_model("Apple AirPods 4 without noise cancelling",ANC))
  self.assertTrue(valid_model("Apple AirPods 4 ANC",ANC))
  self.assertFalse(valid_model("Apple AirPods 4",ANC))
 def test_products_and_price_indications(self):
  items=parse_results(PAYLOAD,AIR,NOW)
  self.assertEqual(len(items),2)
  self.assertEqual(items[0]["indicativePriceEUR"],239.95)
  self.assertEqual(items[1]["indicativePriceEUR"],219)
  self.assertFalse(items[0]["verifiedDiscount"])
  self.assertFalse(items[0]["stockVerified"])
  self.assertFalse(items[0]["shippingVerified"])
 def test_rotation_and_source_failures(self):
  w=[{"id":id,"matchAny":["AirPods Pro"]} for id in QUERIES]
  self.assertEqual(len(choose(w,NOW)),5)
  state=build(w,{},NOW,lookup=lambda w,n: (_ for _ in ()).throw(OSError("HTTP 403")))
  self.assertEqual(state["searchedThisRun"],5)
  self.assertEqual(state["errorCount"],5)
  self.assertFalse(any(x["offers"] for x in state["results"]))
 def test_stale_observations_are_hidden(self):
  w=[AIR]
  before={"results":[{"wishId":"apple-airpods-pro","searchedAt":(NOW-timedelta(days=2)).isoformat(),
                      "status":"ok","offers":[{"title":"AirPods Pro", "indicativePriceEUR":140}]}]}
  data=build(w,before,NOW,lookup=lambda w,n:[],sleep=lambda _:None)
  self.assertEqual(data["comparisonCount"],0)
 def test_bad_data_and_unknown_schema(self):
  with self.assertRaises(ValueError):
   parse_results({"articles":{}},AIR,NOW)

if __name__=="__main__":unittest.main()
