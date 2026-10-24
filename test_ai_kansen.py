import unittest
import ai_kansen_scan as s
class RankingTests(unittest.TestCase):
 def test_relevant_ai_productivity(self):self.assertTrue(s.relevant("AI workflow that saves time on Gmail"))
 def test_irrelevant_hype(self):self.assertFalse(s.relevant("Fun AI meme"))
 def test_irrelevant_topic(self):self.assertFalse(s.relevant("A regular pizza recipe"))
 def test_parser_empty(self):self.assertEqual(s.parse("<rss><channel></channel></rss>","Example","reddit","2026-10-24"),[])
if __name__=="__main__":unittest.main()
