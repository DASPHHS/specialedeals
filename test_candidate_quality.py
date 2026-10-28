import unittest
from candidate_quality import candidate_quality

class CandidateQualityTests(unittest.TestCase):
 def check(self,title,source='Amac Apple aanbiedingen',matches=None):
  return candidate_quality({'title':title,'url':'https://www.amac.nl/product','source':source,'wishlistMatches':matches or []})[0]
 def test_full_price_apple_watch_rejected(self):self.assertFalse(self.check('Apple Watch Ultra 4',matches=['apple-watch-ultra']))
 def test_ordinary_apple_rejected(self):self.assertFalse(self.check('Apple MacBook Pro 16',matches=['apple-macbook']))
 def test_open_box_rejected(self):self.assertFalse(self.check('[Open Box] MacBook Air M5',matches=['apple-macbook']))
 def test_demo_rejected(self):self.assertFalse(self.check('[DEMO] MacBook Pro M4',matches=['apple-macbook']))
 def test_specific_pepper_deal_retained_as_lead(self):self.assertTrue(self.check('Lidl Dagdeal: PARKSIDE Hogedrukreiniger 110 bar',source='Pepper'))
 def test_price_claim_not_verified(self):self.assertTrue(self.check('50% korting op robotstofzuiger',source='Pepper'))

if __name__=='__main__':unittest.main()
