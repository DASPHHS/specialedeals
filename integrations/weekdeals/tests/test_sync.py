import unittest
from sync_deals import fetch_all, normalize, normalize_all, serial, COLUMNS, validate_page

def product(id=1, **kw):
    p={"product_id":str(id),"retailer":"lidl","name":"Voorbeeld 500 g",
       "price":1.99,"original_price":2.99,"is_promotional":True,
       "promotion_status":"active","valid_from":"2026-11-01","valid_until":"2026-11-07",
       "savings_percentage":33.4}
    p.update(kw)
    return p

class SyncTests(unittest.TestCase):
    def test_pages(self):
        p=[product(x) for x in range(1,105)]
        def fetch(path,params):
            self.assertEqual(path,"/products/promotional/all")
            start=(params["page"]-1)*100
            return {"total":len(p),"products":p[start:start+100]}
        self.assertEqual(len(fetch_all(fetch)),104)

    def test_duplicates_rejected(self):
        def fetch(path,params):
            return {"total":2,"products":[product(1)]}
        with self.assertRaises(ValueError):
            fetch_all(fetch)

    def test_count_change_rejected(self):
        def fetch(path,params):
            if params["page"]==1:
                return {"total":101,"products":[product(i) for i in range(100)]}
            return {"total":102,"products":[product(100)]}
        with self.assertRaises(ValueError):
            fetch_all(fetch)

    def test_zero_rejected(self):
        with self.assertRaises(ValueError):
            fetch_all(lambda path,params:{"total":0,"products":[]})

    def test_invalid_shape_rejected(self):
        with self.assertRaises(ValueError):
            validate_page({"total":"100","products":[]},1)

    def test_normalization(self):
        r=normalize(product(),"2026-11-01")
        self.assertEqual(len(r),len(COLUMNS))
        self.assertEqual(r[9],serial("2026-11-01"))
        self.assertEqual(r[11],"PrijsProfeet")
        self.assertTrue(0.3<r[6]<0.4)

    def test_multibuy_not_invented(self):
        r=normalize(product(multi_buy_quantity=2,savings_percentage=None,original_price=None),"2026-11-01")
        self.assertEqual(r[6],"")
        self.assertEqual(r[20],2)

    def test_missing_end_date_stays_missing(self):
        r=normalize(product(valid_until=None),"2026-11-01")
        self.assertEqual(r[10],"")
        self.assertIn("Onbekende geldigheid",r[15])

    def test_no_shelf_deals(self):
        with self.assertRaises(ValueError):
            normalize_all([product(promotion_status="shelf")],"2026-11-01")

if __name__=="__main__":
    unittest.main()
