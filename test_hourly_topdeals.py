import unittest
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from hourly_topdeals import (generate,classify,eligible,asserted_discount,
                             source_health,wish_matches,ORDER)

NOW=datetime(2026,11,1,13,40,tzinfo=ZoneInfo("Europe/Amsterdam"))
def offer(name="HOKA Arahi 7 heren 47 1/3",**overrides):
    x={"id":"a","winkel":"Bever","product":name,"categorie":"Sport",
       "prijs":95.0,"van_prijs":125.0,"korting":.24,
       "tot":"2026-11-03","waargenomen_op":"2026-11-01",
       "bron":"PrijsProfeet","url":"https://winkel.example/item"}
    x.update(overrides)
    return x

def snapshot(rows):
    return {"source":"PrijsProfeet","updated_at":NOW.isoformat(),"deals":rows}

WISH={"items":[{"id":"hoka-schoenen","name":"HOKA 47⅓","matchAny":["HOKA Arahi"],
                "excludeTerms":["dames","women","kids"]},
               {"id":"apple-airpods-pro","name":"AirPods Pro","matchAny":["AirPods Pro"],
                "excludeTerms":["hoesje","cover"]}]}

class Top10Tests(unittest.TestCase):
 def test_categories(self):
    self.assertEqual(classify(offer("Kettingzaag Makita 18V",categorie="Tuin & wonen")),"bouwmarkt")
    self.assertEqual(classify(offer("Potgrond en planten",categorie="Tuin & wonen")),"tuin")
    self.assertEqual(classify(offer("Shampoo 250ml",categorie="Drogisterij")),"drogisterij")
    self.assertEqual(classify(offer("USB4 Thunderbolt hub",categorie="Overig")),"elektronica")
    self.assertEqual(classify(offer("Arc'teryx outdoor jas",categorie="Outdoor")),"sport")
    self.assertEqual(classify(offer("Koffiebonen 1kg",categorie="Coffee & Tea")),"supermarkt")
    # Real production examples that previously appeared in wrong Top 10s.
    self.assertEqual(classify(offer("Happy Earth 100% Natural Deodorant Roller",categorie="Health & Beauty",winkel="Etos")),"drogisterij")
    self.assertEqual(classify(offer("Dr. Oetker Big Americans pizza bbq chicken",categorie="Frozen",winkel="DekaMarkt")),"supermarkt")
    self.assertEqual(classify(offer("Le Petit Marseillais Douchegel Bio Tiare Bloem",categorie="Health & Beauty",winkel="Poiesz")),"drogisterij")
    self.assertEqual(classify(offer("True Dates Sour apple",categorie="Sweets & Snacks",winkel="Albert Heijn")),"supermarkt")
    self.assertEqual(classify(offer("Beyond Meat Plant-based burger",categorie="Vleesvervangers",winkel="Albert Heijn")),"supermarkt")
    self.assertEqual(classify(offer("Alle Apple Bandit, Desperados of Texels speciaalbier",categorie="Beer",winkel="Boon's Markt")),"supermarkt")
    self.assertEqual(classify(offer("Ariel The big one original pods",categorie="Wasmiddelen",winkel="Hoogvliet")),"huis")
    self.assertEqual(classify(offer("Côte d'Or Tablet puur amandel karamel",categorie="Chocolade",bron=None),"PrijsProfeet"),"supermarkt")
    self.assertEqual(classify(offer("Milka Chocolade biscuit tablet lu",categorie="Overig",bron=None),"PrijsProfeet"),"supermarkt")
    self.assertEqual(classify(offer("Hoogvliet Goudse 48+ kaasstuk jong",categorie="Kaas",bron=None),"PrijsProfeet"),"supermarkt")
    self.assertEqual(classify(offer("Robijn Quickwash optimum white",categorie="Overig",bron=None),"PrijsProfeet"),"huis")
    self.assertEqual(classify(offer("Ariel Pods",categorie="Overig",bron=None),"PrijsProfeet"),"huis")
    self.assertEqual(classify(offer("Emma Aanpasbaar matras 90 x 200 cm",categorie="Overig",bron=None),"PrijsProfeet"),"huis")
    self.assertEqual(classify(offer("Happy Earth 100% Natuurlijke Nourishing Bodycrème",categorie="Overig",bron=None),"FeedMyCart"),"drogisterij")
    self.assertEqual(classify(offer("Max Factor Facefinity Compact Refill",categorie="Overig",bron=None),"FeedMyCart"),"drogisterij")
    self.assertEqual(classify(offer("Max Factor Mascara",categorie="Overig",bron=None),"FeedMyCart"),"drogisterij")
    self.assertEqual(classify(offer("Robijn Vloeibaar wsmiddel pinksensation",categorie="Overig",bron=None),"PrijsProfeet"),"huis")

 def test_deal_gates(self):
    self.assertTrue(eligible(offer(),NOW))
    self.assertFalse(eligible(offer(tot="2026-10-31"),NOW))
    self.assertFalse(eligible(offer(van="2026-11-03"),NOW))
    self.assertFalse(eligible(offer(prijs=None),NOW))
    self.assertFalse(eligible(offer(url="http://shop.example"),NOW))
    self.assertFalse(eligible(offer(product="Win de loterij"),NOW))
    self.assertTrue(eligible(offer(tot=None),NOW))
    self.assertFalse(eligible(offer(tot=None,waargenomen_op="2026-10-31"),NOW))
 def test_discount_is_advertised_only(self):
    self.assertEqual(asserted_discount(offer()),24.0)
    self.assertIsNone(asserted_discount(offer(bundelaantal=2)))
    self.assertIsNone(asserted_discount(offer(van_prijs=None,korting=.7)))
    self.assertIsNone(asserted_discount(offer(korting=.7)))
    self.assertIsNone(asserted_discount(offer(prijstype="bundeltotaal")))
 def test_source_freshness(self):
    self.assertTrue(source_health(snapshot([offer()]),NOW)["usable"])
    stale=snapshot([offer()])
    stale["updated_at"]=(NOW-timedelta(hours=49)).isoformat()
    self.assertFalse(source_health(stale,NOW)["usable"])
    self.assertFalse(source_health({"source":"missing","deals":[offer()]},NOW)["usable"])
 def test_affinity_sku_uncertainty_and_separate_merchants(self):
    offers=[offer(),offer(id="b",winkel="Andere winkel",url="https://ander.example/aanbieding"),
            offer(id="c",product="AirPods Pro hoesje",prijs=7),
            offer(id="d",product="HOKA Arahi 7 dames 47 1/3",prijs=84)]
    out=generate([snapshot(offers)],WISH,NOW)
    self.assertEqual(out["wishlistMatchedCount"],2)
    self.assertEqual(len(out["categories"]["persoonlijk"]["top10"]),2)
    for x in out["categories"]["persoonlijk"]["top10"]:
        self.assertFalse(x["verifiedDeal"])
        self.assertFalse(x["verifiedAllInPrice"])
        self.assertIsNone(x["shippingEUR"])
        self.assertEqual(x["advertisedDiscountPercent"],24.0)
    self.assertEqual(out["verifiedDealCount"],0)
 def test_top10_each_category_and_stale_source_filtered(self):
    rows=[offer(id=str(i),product=f"Potgrond groen {i} liter",prijs=2+i,
                van_prijs=4+i,korting=(2/(4+i)),url=f"https://intratuin.nl/product/{i}",
                winkel="Intratuin",bron="Intratuin.nl") for i in range(16)]
    old={"source":"old","updated_at":(NOW-timedelta(days=4)).isoformat(),
         "deals":[offer(id="old",product="HOKA Arahi 7 heren 47 1/3")]}
    out=generate([snapshot(rows),old],WISH,NOW)
    self.assertEqual(len(out["categories"]["tuin"]["top10"]),10)
    self.assertEqual(out["discarded"]["stale_source"],1)
    self.assertEqual(out["wishlistMatchedCount"],0)
    self.assertEqual(set(out["categories"]),set(ORDER))
    self.assertEqual(len(out["categories"]["bouwmarkt"]["top10"]),0)
    self.assertEqual(out["eligibleCount"],16)
 def test_each_explicit_user_profile_checked_separately(self):
    profiles=[
      {"position":1,"kind":"product","name":"MacBook Air","wishlistIds":["apple-macbook"]},
      {"position":2,"kind":"product","name":"MacBook Pro","wishlistIds":["apple-macbook"]},
      {"position":3,"kind":"product","name":"HOKA Arahi","wishlistIds":["hoka-schoenen"]},
      {"position":4,"kind":"product","name":"HOKA Kawana","wishlistIds":["hoka-schoenen"]},
      {"position":5,"kind":"service","name":"Gas en elektra","serviceId":"gas-elektra"},
      {"position":6,"kind":"event","name":"Bijzondere sample sales","researchTargetId":"event-sales"}
    ]
    wishes={"items":[
      {"id":"apple-macbook","name":"MacBook","matchAny":["MacBook Air","MacBook Pro"]},
      {"id":"hoka-schoenen","name":"HOKA","matchAny":["HOKA Arahi","HOKA Kawana"]}
    ],"searchProfiles":profiles}
    out=generate([snapshot([
      offer(id="mb",product="Apple MacBook Air M4 16GB",categorie="Elektronica",prijs=1000),
      offer(id="ar",product="HOKA Arahi 8 heren maat 47",categorie="Sport",prijs=100)
    ])],wishes,NOW)
    self.assertEqual(out["profileCount"],6)
    got={x["name"]:x for x in out["profileChecks"]}
    self.assertEqual(got["MacBook Air"]["candidateCount"],1)
    self.assertEqual(got["MacBook Pro"]["candidateCount"],0)
    self.assertEqual(got["HOKA Arahi"]["candidateCount"],1)
    self.assertEqual(got["HOKA Kawana"]["candidateCount"],0)
    self.assertEqual(got["Gas en elektra"]["state"],"not_connected")
    self.assertIsNone(got["Gas en elektra"]["checkedAgainstFeedAt"])
    self.assertEqual(got["Bijzondere sample sales"]["state"],"separate_event_monitor")
    self.assertTrue(all(not x["verifiedDeal"] for x in got["MacBook Air"]["offers"]))

 def test_production_list_covers_all_original_23_profiles(self):
    import json
    from pathlib import Path
    wishlist=json.loads(Path("wishlist.json").read_text())
    profiles=wishlist["searchProfiles"]
    self.assertEqual(len(profiles),23) # 22 supplied items + separately requested sample sales
    self.assertEqual(len([x for x in profiles if x["kind"]=="service"]),3)
    self.assertEqual(len([x for x in profiles if x["kind"]=="event"]),1)
    self.assertEqual(len({x["position"] for x in profiles}),23)

 def test_no_priced_reference_for_free_shipping_guesses(self):
    row=offer(prijs=34.99,van_prijs=50,korting=.3002,
              bron="FeedMyCart",url="https://feedmycart.nl/en/countries/netherlands/")
    out=generate([snapshot([row])],WISH,NOW)
    x=out["categories"]["sport"]["top10"][0]
    self.assertIsNone(x["shippingEUR"])
    self.assertFalse(x["directProductPage"])
    self.assertNotIn("geverifieerd",x["evidence"].lower())

if __name__=="__main__":
    unittest.main()
