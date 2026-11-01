import unittest
from datetime import datetime
from da_adapter import extract,euro

def html_for(n=12):
    parts=[]
    for i in range(n):
        parts.append(
            '<a class="MuiButtonBase-root ProductListItem-root" href="/product/test-product-'+str(i)+'">'
            '<h2 class="ProductListItem-title">DA testproduct '+str(i)+'</h2>'
            '<div class="ProductListPrice-root"><div class="price"><div>9</div><span>.</span>'
            '<div class="decimal"><sup>99</sup></div></div></div>'
            '<div class="ProductListItem-discount">2 + 3 Gratis</div>'
            '</a>'
        )
    return "<html><body>"+''.join(parts)+"</body></html>"

class DaTests(unittest.TestCase):
    def test_money(self):
        self.assertEqual(euro("9 . 99"),9.99)
        self.assertEqual(euro("€12,50"),12.5)
        self.assertIsNone(euro("not a euro price"))

    def test_names_prices_and_no_fake_dates(self):
        records=extract(html_for(),datetime(2026,11,1))
        self.assertEqual(len(records),12)
        row=records[0]
        self.assertEqual(row["product"],"DA testproduct 0")
        self.assertEqual(row["prijs"],9.99)
        self.assertEqual(row["actievorm"],"2 + 3 Gratis")
        self.assertEqual(row["waargenomen_op"],"2026-11-01")
        self.assertNotIn("tot",row)
        self.assertTrue(row["einddatum_onbekend"])
        self.assertTrue(row["url"].startswith("https://www.da.nl/product/"))

    def test_incomplete_page_rejected(self):
        with self.assertRaises(ValueError):
            extract(html_for(2),datetime(2026,11,1))

    def test_unreadable_price_rejected(self):
        with self.assertRaises(ValueError):
            extract(html_for().replace('<div>9</div>','<div>ERR</div>'),datetime(2026,11,1))

if __name__=="__main__":
    unittest.main()
