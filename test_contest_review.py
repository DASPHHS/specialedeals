import datetime as dt
import unittest
from contest_review import review

class OfficialRechecks(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,26,14,tzinfo=dt.timezone.utc)
  self.c={'id':'example','sourceUrl':'https://example.org/action','termsUrl':'https://example.org/terms','deadline':'2026-11-01'}
 def test_reachable_is_never_verified(self):
  r=review(self.c,{},self.now,lambda u:'terms')
  self.assertTrue(r['reviewRequired']);self.assertIn('entry_limit_not_documented',r['reasons'])
  self.assertNotIn('submitted',r);self.assertNotIn('eligible',r)
 def test_changed_and_failed_pages_require_review(self):
  old=review(self.c,{},self.now,lambda u:'old')
  r=review(self.c,old,self.now,lambda u:'new')
  self.assertIn('page_changed',r['reasons'])
  def fail(u):raise ValueError('secret must never be logged')
  r=review(self.c,old,self.now,fail)
  self.assertIn('official_page_unavailable',r['reasons']);self.assertNotIn('secret',str(r))
 def test_expired_in_dutch_timezone(self):
  self.c['deadline']='2026-10-25'
  self.assertIn('expired',review(self.c,{},self.now,lambda u:'ok')['reasons'])
