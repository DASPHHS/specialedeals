import unittest
from datetime import datetime
from intratuin_adapter import extract,euro

def card(i,old="69.99",new="49.99",bundle=False):
    name="Intratuin testplant "+str(i)
    prices=(f'<span class="price">{new}</span>' if bundle else
            f'<div class="special-price"><span class="price">{new}</span></div>'
            f'<div class="old-price"><span class="price">{old}</span></div>')
    return (f'<li class="item product product-item">'
            f'<a class="product-item-link" href="https://www.intratuin.nl/test-{i}.html">{name}</a>'
            f'{prices}</li>')

class IntratuinTests(unittest.TestCase):
    def test_euro_price_parser(self):
        self.assertEqual(euro("149.-"),149)
        self.assertEqual(euro("€49.99"),49.99)
        self.assertEqual(euro("1.99"),1.99)
        self.assertIsNone(euro("met klantenkaart"))

    def test_verified_sale(self):
        rows=extract("<ul>"+''.join(card(i) for i in range(14))+"</ul>",datetime(2026,11,1))
        self.assertEqual(len(rows),14)
        self.assertEqual(rows[0]["prijs"],49.99)
        self.assertEqual(rows[0]["van_prijs"],69.99)
        self.assertEqual(rows[0]["winkel"],"Intratuin")
        self.assertTrue(rows[0]["einddatum_onbekend"])
        self.assertNotIn("tot",rows[0])

    def test_unverified_bundle_cards_excluded(self):
        html="<ul>"+''.join(card(i,bundle=(i%2==0)) for i in range(14))+"</ul>"
        rows=extract(html,datetime(2026,11,1))
        self.assertEqual(len(rows),7)

    def test_invalid_discount_excluded(self):
        html="<ul>"+''.join(card(i,new="79.99") for i in range(14))+"</ul>"
        self.assertEqual(extract(html,datetime(2026,11,1)),[])

    def test_missing_grid_is_error(self):
        with self.assertRaises(ValueError):
            extract("<html>No price records</html>",datetime(2026,11,1))

if __name__=="__main__":
    unittest.main()
