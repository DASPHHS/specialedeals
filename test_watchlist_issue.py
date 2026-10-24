import unittest
from watchlist_issue import parse,apply
def event(user,body):return {"issue":{"user":{"login":user},"body":body}}
class WatchTests(unittest.TestCase):
 def test_add(self):
  out=apply({"items":[]},event("DASPHHS","SPECIALDEALS-WATCH-V1\nactie=toevoegen\nproduct=HOKA Arahi 47\nmaxprijs=100"))
  self.assertEqual(out["items"][0]["maxPriceEUR"],100)
 def test_update_same(self):
  prior={"items":[{"product":"HOKA Arahi 47","maxPriceEUR":100}]}
  out=apply(prior,event("DASPHHS","SPECIALDEALS-WATCH-V1\nactie=toevoegen\nproduct=hoka arahi 47\nmaxprijs=90"))
  self.assertEqual(len(out["items"]),1)
  self.assertEqual(out["items"][0]["maxPriceEUR"],90)
 def test_remove(self):
  prior={"items":[{"product":"HOKA Arahi 47","maxPriceEUR":100}]}
  out=apply(prior,event("DASPHHS","SPECIALDEALS-WATCH-V1\nactie=verwijderen\nproduct=HOKA Arahi 47"))
  self.assertFalse(out["items"])
 def test_owner_only(self):
  with self.assertRaises(PermissionError):apply({"items":[]},event("stranger","SPECIALDEALS-WATCH-V1\nactie=toevoegen\nproduct=secret\nmaxprijs=100"))
 def test_invalid_price(self):
  with self.assertRaises(ValueError):parse("SPECIALDEALS-WATCH-V1\nactie=toevoegen\nproduct=HOKA\nmaxprijs=abc")
 def test_not_a_watch(self):
  with self.assertRaises(ValueError):parse("Here is a post\nproduct=HOKA")
if __name__=="__main__":unittest.main()
