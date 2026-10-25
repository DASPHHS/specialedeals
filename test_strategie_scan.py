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

    def test_unparsed_or_empty_rss_is_not_false_success(self):
        self.assertEqual(article_candidates("<html>bad"), [])
        self.assertEqual(article_candidates("<rss><channel></channel></rss>"), [])

    def test_clean_html_removes_formatting(self):
        self.assertEqual(plain("<p>Korting&nbsp;voor klanten</p>"), "korting voor klanten")


if __name__ == "__main__":
    unittest.main()
