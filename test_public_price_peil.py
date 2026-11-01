import unittest
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from public_price_peil import build,record,classify

NOW=datetime(2026,11,1,15,30,tzinfo=ZoneInfo("Europe/Amsterdam"))
def row(name="accuboormachine"):
 return {"zoekterm":name,"url":"https://prijspuls.nl/vergelijk/"+name.replace(" ","-"),
         "laagste_eur":79.95,"gemiddelde_eur":99.95,"webshops":3,"aanbiedingen":9,
         "laagste_conditie":"nieuw","meetmoment":NOW.isoformat()}
class PublicPricePeilTests(unittest.TestCase):
 def test_classification_is_category_not_actual_product(self):
  self.assertEqual(classify("accuboormachine"),"bouwmarkt")
  self.assertEqual(classify("potgrond voor planten"),"tuin")
  self.assertEqual(classify("ssd 1tb"),"elektronica")
  self.assertEqual(classify("hardloopschoenen"),"sport")
  self.assertEqual(classify("parfum"),"drogisterij")
  self.assertEqual(classify("pizza oven"),"huis")
  self.assertEqual(classify("tv meubel"),"huis")
  self.assertEqual(classify("terrarium lamp"),"huis")
  self.assertEqual(classify("werkbroek"),"bouwmarkt")
 def test_verification_not_claimed(self):
  v=record(row(),NOW)
  self.assertEqual(v["lowestEUR"],79.95)
  self.assertEqual(v["spreadPercent"],20.0)
  self.assertFalse(v["verifiedDiscount"])
  self.assertFalse(v["verifiedProductMatch"])
  self.assertFalse(v["deliveredPriceVerified"])
  self.assertEqual(v["type"],"generic_market_price_level_not_a_deal")
 def test_only_current_trusted_refs(self):
  bad=[
    {"url":"https://malicious.example/vergelijk/accuboormachine"},
    {"url":"http://prijspuls.nl/vergelijk/accuboormachine"},
    {"laagste_eur":None},
    {"gemiddelde_eur":1},
    {"meetmoment":(NOW-timedelta(days=3)).isoformat()},
    {"webshops":0},
    {"zoekterm":"wijn bier"}
  ]
  for changed in bad:
   with self.subTest(changed=changed):
    self.assertIsNone(record({**row(),**changed},NOW))
 def test_build_requires_fresh_complete_source_and_groups(self):
  rows=[row("boormachine "+str(i)) for i in range(30)]+[row("SSD "+str(i)) for i in range(30)]
  doc={"bron":"prijspuls.nl","gegenereerd":NOW.isoformat(),"producten":rows}
  result=build(doc,NOW)
  self.assertEqual(result["usablePriceLevels"],60)
  self.assertEqual(result["groups"]["bouwmarkt"]["available"],30)
  self.assertEqual(result["groups"]["elektronica"]["available"],30)
  self.assertEqual(len(result["groups"]["bouwmarkt"]["top10"]),10)
  self.assertFalse(result["groups"]["bouwmarkt"]["top10"][0]["verifiedDiscount"])
  with self.assertRaises(ValueError):build({**doc,"bron":"unknown"},NOW)
  with self.assertRaises(ValueError):build({**doc,"gegenereerd":"2026-10-20T11:00:00+01:00"},NOW)
  with self.assertRaises(ValueError):build({**doc,"producten":rows[:2]},NOW)
if __name__=="__main__":unittest.main()
