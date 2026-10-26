import unittest
from contest_scan import build,classify,relevant
class Contests(unittest.TestCase):
 def test_untrusted_discovery_stays_candidate(self):
  a=build([{'title':'Win a car worldwide','url':'https://example.org/contest'},{'title':'Win a car worldwide','url':'https://example.org/contest#duplicate'},{'title':'Win something','url':'javascript:alert(1)'}],'2026-10-25T09:00Z')
  self.assertEqual(len(a),1);self.assertEqual(a[0]['status'],'candidate');self.assertNotIn('eligible',a[0]);self.assertEqual(a[0]['category'],'Auto’s')
 def test_noise_is_not_a_contest(self):
  for title in ("WinRAR download free", "Windy: Wind map", "WIN Definition & Meaning", "Concours - Wikipedia", "Windows 11 Installation"):
   self.assertFalse(relevant(title,"https://example.org"))
 def test_house_matches(self):
  self.assertEqual(classify('Win een warmtepomp voor renovatie'),'Renovatie & verduurzaming')
if __name__=='__main__':unittest.main()

class DirectSources(unittest.TestCase):
 def test_direct_links_and_tracking(self):
  from contest_scan import ContestLinks
  p=ContestLinks({'url':'https://example.org/list','name':'Test'})
  p.feed('<a href="https://shop.example/win">Win 6 maanden gratis koffie</a><a href="https://glp8.net/ad">Win geld</a>')
  self.assertEqual(len(p.rows),1)
  self.assertEqual(classify(p.rows[0]['title']),'Lang gratis')
  self.assertEqual(p.rows[0]['discoveredVia'],'https://example.org/list')

class MitspielSourceTests(unittest.TestCase):
 def test_mitspiel_internal_detail_links_are_candidates_only(self):
  from contest_scan import ContestLinks
  p=ContestLinks({'url':'https://mitspiel.nl/winacties','name':'Mitspiel Nederland winacties'})
  p.feed('<a href="/winacties/win-anwb-reischeque-23905">Win: ANWB-reischeque van 5000 euro</a>'
         '<a href="/winacties">Alle winacties bekijken</a>'
         '<a href="/mitspiel-club">Registreer voor slimme alerts</a>')
  self.assertEqual(len(p.rows),1)
  self.assertEqual(p.rows[0]['url'],'https://mitspiel.nl/winacties/win-anwb-reischeque-23905')
  lead=build(p.rows,'2026-10-26T12:00:00Z')[0]
  self.assertEqual(lead['status'],'candidate')
  self.assertNotIn('eligible',lead)
  self.assertIn('nog niet bevestigd',lead['reason'].lower())
