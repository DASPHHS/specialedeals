import sqlite3
import unittest
from price_history import record,summarize
class PriceHistoryTests(unittest.TestCase):
 def test_append_and_dedupe(self):
  with sqlite3.connect(":memory:") as db:
   x={"status":"product_price_candidate","targetId":"a","seller":"Store","productId":"coffee","variantKey":"350g","url":"https://example.com/p","priceEUR":"12.95"}
   self.assertEqual(record(db,[x],"2026-10-29T10:00:00Z"),1)
   record(db,[x],"2026-10-29T10:00:00Z")
   self.assertEqual(summarize(db)["sources"][0]["samples"],1)
   x["priceEUR"]="11.95"
   record(db,[x],"2026-10-30T10:00:00Z")
   self.assertEqual(summarize(db)["sources"][0]["lowestObservedItemPriceEUR"],"11.95")
 def test_reject_noncandidate_and_bad_prices(self):
  with sqlite3.connect(":memory:") as db:
   a={"status":"verified","targetId":"a","seller":"Shop","productId":"p","variantKey":"v","url":"https://example.com","priceEUR":"1"}
   b=dict(a,status="product_price_candidate",priceEUR="NaN")
   self.assertEqual(record(db,[a,b],"2026-10-29T10:00:00Z"),0)
   self.assertEqual(summarize(db)["sources"],[])
if __name__=="__main__":unittest.main()
