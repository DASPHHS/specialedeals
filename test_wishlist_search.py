import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from wishlist_search import build, search_one, selected_wishes, usable_result

NOW=datetime(2026,11,1,7,20,tzinfo=ZoneInfo("Europe/Amsterdam"))
WISH={"id":"apple-airpods-pro","name":"AirPods Pro","matchAny":["AirPods Pro"],"excludeTerms":["hoesje","cover","case only"]}
RSS=b"""<?xml version='1.0'?><rss><channel>
 <item><title>Apple AirPods Pro 3 - winkelactie</title><link>https://www.coolblue.nl/nl/product/12345/apple-airpods-pro-3.html?utm_source=bing</link></item>
 <item><title>Apple AirPods Pro 3 hoesje</title><link>https://www.coolblue.nl/product/2333</link></item>
 <item><title>Apple AirPods Pro 3 - webshop</title><link>https://www.suspicious.test/pro/3</link></item>
 <item><title>AirPods Pro review</title><link>https://www.bol.com/nl/nl/p/airpods/34</link></item>
 </channel></rss>"""

class SearchTests(unittest.TestCase):
 def test_domain_and_model_gate(self):
  self.assertTrue(usable_result("Apple AirPods Pro 3","https://www.coolblue.nl/nl/product/123",WISH))
  self.assertFalse(usable_result("Apple AirPods Pro 3 hoesje","https://www.coolblue.nl/nl/product/123",WISH))
  self.assertFalse(usable_result("Apple AirPods Pro 3","https://www.unknown.test/item",WISH))
  self.assertFalse(usable_result("Apple AirPods Pro 3 review","https://www.bol.com/nl/nl/p/34",WISH))

 def test_xml_parse_returns_only_direct_merchant_research_leads(self):
  results=search_one(WISH,fetch=lambda _:RSS)
  self.assertEqual(len(results),1)
  self.assertNotIn("?utm",results[0]["url"])
  self.assertNotIn("priceEUR",results[0])
  self.assertIn("niet gecontroleerd",results[0]["status"])

 def test_rotation_does_not_claim_every_item_checked(self):
  wishes=[{"id":str(i),"name":"HOKA Arahi", "matchAny":["HOKA Arahi"]} for i in range(23)]
  first=selected_wishes(wishes,NOW.replace(hour=6))
  second=selected_wishes(wishes,NOW)
  self.assertEqual(len(first),12)
  self.assertEqual(len(second),12)
  self.assertEqual(len({x["id"] for x in first+second}),23)

 def test_stale_leads_hidden_and_source_errors_recorded(self):
  items=[WISH,{"id":"hoka","name":"HOKA Arahi","matchAny":["HOKA Arahi"]}]
  previous={"results":[{"wishId":"apple-airpods-pro","searchedAt":(NOW-timedelta(days=3)).isoformat(),
                       "leads":[{"title":"Old listing","url":"https://coolblue.nl"}],
                       "status":"ok"}]}
  data=build(items,previous,NOW,lookup=lambda w: (_ for _ in ()).throw(OSError("429")),sleep=lambda _:None)
  self.assertEqual(len(data["errors"]),2)
  self.assertTrue(all(r["status"]=="source_error" for r in data["results"]))
  self.assertTrue(all(not r["leads"] for r in data["results"]))

if __name__=="__main__":unittest.main()
