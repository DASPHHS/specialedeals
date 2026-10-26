import unittest
from strategie_scan import article_candidates, plain


class StrategyScanTests(unittest.TestCase):
    def test_reddit_direct_topic_only(self):
        xml = """<rss><channel>
          <item><title>Internet verlengen: cashback of korting vergelijken</title>
           <link>https://www.reddit.com/r/zuinig/comments/1ro414d/reminder_om_je_internet_ook_te_verlengen/</link></item>
          <item><title>Internet verlengen met cashback</title>
           <link>https://example.org/reddit-r-zuinig</link></item>
          <item><title>AH bonus recepten boodschappenlijst</title>
           <link>https://www.reddit.com/r/zuinig/comments/1q6wadd/boodschappen/</link></item>
          <item><title>Coupon spam</title><link>https://reddit.com/r/zuinig</link></item>
        </channel></rss>"""
        found = article_candidates(xml)
        self.assertEqual(len(found), 1)
        self.assertFalse(found[0]["verified"])
        self.assertEqual(found[0]["status"], "community_onderzoekskandidaat")

    def test_reddit_atom_feed_discovers_only_relevant_posts(self):
        atom = """<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><title>Nieuwe cashback prijsvergelijking internet abonnement</title>
            <link href="https://www.reddit.com/r/zuinig/comments/1uv8ieq/welke_gewoonte_bespaart_geld/" rel="alternate"/>
          </entry>
          <entry><title>AH supermarkt recepten</title>
            <link href="https://www.reddit.com/r/zuinig/comments/1uv8def/ah_recept/" rel="alternate"/>
          </entry>
        </feed>"""
        found = article_candidates(atom)
        self.assertEqual(len(found),1)
        self.assertTrue(found[0]["url"].startswith("https://www.reddit.com/r/zuinig/comments/"))
        self.assertFalse(found[0]["verified"])

    def test_unparsed_or_empty_rss_is_not_false_success(self):
        self.assertEqual(article_candidates("<html>bad"), [])
        self.assertEqual(article_candidates("<rss><channel></channel></rss>"), [])

    def test_english_shipping_and_renewal_research_not_lost(self):
        xml = """<rss><channel>
          <item><title>Free shipping minimum: why adding items costs more</title><link>https://www.reddit.com/r/Frugal/comments/abc123/free_shipping_minimum/</link></item>
          <item><title>Broadband renewal versus switching provider</title><link>https://www.reddit.com/r/Netherlands/comments/abc124/broadband_renewal/</link></item>
        </channel></rss>"""
        rows=article_candidates(xml)
        self.assertEqual(len(rows),2)
        self.assertTrue(all(not r['verified'] for r in rows))

    def test_clean_html_removes_formatting(self):
        self.assertEqual(plain("<p>Korting&nbsp;voor klanten</p>"), "korting voor klanten")


if __name__ == "__main__":
    unittest.main()

