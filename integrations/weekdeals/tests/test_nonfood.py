import json
import unittest
from datetime import datetime
from publish_nonfood_deals import parse,money,DealParser

def html_for(items):
    ld={"@context":"https://schema.org","@type":"ItemList",
        "itemListElement":[{"@type":"ListItem","position":i+1,
              "item":{"@type":"Product","name":it[0],
                      "offers":{"@type":"AggregateOffer","lowPrice":str(it[1]),
                                "priceCurrency":"EUR","priceValidUntil":it[3]}}}
             for i,it in enumerate(items)]}
    section=''.join(
        '<li class="deal"><span class="deal__name">'+name+
        '</span><span class="deal__tags">'+promo+
        '</span><span class="deal__price"><s>€'+str(old)+
        '</s> <b>€'+str(price)+'</b></span></li>'
        for name,price,old,end,promo in items
    )
    return ('<html><head><script type="application/ld+json">'+json.dumps(ld)+
            '</script></head><body><h2>Health &amp; Beauty</h2><ul class="deals">'+
            section+'</ul></body></html>')

class NonFoodTests(unittest.TestCase):
    def test_money(self):
        self.assertEqual(money("€ 9,99"),9.99)
        self.assertEqual(money("€1.259,00"),1259)
        self.assertIsNone(money("Geen prijs"))

    def test_parse(self):
        src=html_for([("Dove crème 200 ml",3.99,5.49,"2026-11-03","1+1"),
                      ("Oral-B tandenborstel",29.99,59.99,"2026-11-04","50%")])
        r=parse(src,"etos",datetime(2026,11,1))
        self.assertEqual(len(r),2)
        self.assertEqual(r[0]["winkel"],"Etos")
        self.assertEqual(r[0]["prijs"],3.99)
        self.assertEqual(r[0]["van_prijs"],5.49)
        self.assertEqual(r[0]["categorie"],"Health & Beauty")
        self.assertEqual(r[0]["actievorm"],"1+1")
        self.assertTrue(r[0]["startdatum_onbekend"])

    def test_expired_excluded(self):
        src=html_for([("Dove crème 200 ml",3.99,5.49,"2026-10-30","50%")])
        self.assertEqual(parse(src,"etos",datetime(2026,11,1)),[])

    def test_price_mismatch_rejected(self):
        src=html_for([("Dove crème 200 ml",3.99,5.49,"2026-11-03","")])
        src=src.replace('<b>€3.99</b>','<b>€5.49</b>')
        self.assertEqual(parse(src,"etos",datetime(2026,11,1)),[])

    def test_invalid_html_rejected(self):
        with self.assertRaises(ValueError):
            parse("<html>geen productdata</html>","action",datetime(2026,11,1))

if __name__=="__main__":
    unittest.main()
