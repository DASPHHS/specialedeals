import unittest
from contest_scan import build,classify
class Contests(unittest.TestCase):
 def test_untrusted_discovery_stays_candidate(self):
  a=build([{'title':'Win a car worldwide','url':'https://example.org/contest'},{'title':'Win a car worldwide','url':'https://example.org/contest#duplicate'},{'title':'Win something','url':'javascript:alert(1)'}],'2026-10-25T09:00Z')
  self.assertEqual(len(a),1);self.assertEqual(a[0]['status'],'candidate');self.assertNotIn('eligible',a[0]);self.assertEqual(a[0]['category'],'Auto’s')
 def test_house_matches(self):
  self.assertEqual(classify('Win een warmtepomp voor renovatie'),'Renovatie & verduurzaming')
if __name__=='__main__':unittest.main()
