#!/usr/bin/env python3
"""Monitor official saving-offer terms and discover Reddit tactics as unverified leads.

Public record never stores user data, credentials or presumed eligibility.
Reddit/community tips require independent testing before appearing as advice.
"""
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
OUTPUT = ROOT / "strategie-scan.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Kansenkompas-SavingsResearch/1.0)"}
OFFICIAL = [
    ("MeerVoordeel Ziggo", "https://meervoordeel.nl/ziggo/korting-of-cadeau",
     ("ziggo", "korting", "cadeau")),
    ("MeerVoordeel voorwaarden", "https://meervoordeel.nl/ziggo",
     ("ziggo", "cadeau", "klant")),
    ("MeerVoordeel hollandsnieuwe", "https://meervoordeel.nl/hollandsnieuwe",
     ("hollandsnieuwe", "10.000")),
    ("De Online Drogist prijzen", "https://www.deonlinedrogist.nl/recommended-prices-and-offers",
     ("adviesprij", "aanbieding")),
    ("De Online Drogist verzending", "https://www.deonlinedrogist.nl/shipping-and-delivery",
     ("25", "3,95")),
    ("De Online Drogist spaarprogramma", "https://www.deonlinedrogist.nl/blog/spaarprogramma/",
     ("spaarpunten", "beloning")),
]
REDDIT_QUERIES = [
    "site:reddit.com/r/zuinig internet verlengen overstappen korting 2026",
    "site:reddit.com/r/zuinig drogist verzorging kortingscode spaarpunten",
    "site:reddit.com/r/zuinig aanbieding prijsverleden cashback Black Friday",
    "site:reddit.com/r/Netherlands coupon stacking online discount Netherlands",
]
REDDIT_FEEDS = [
    "https://www.reddit.com/r/zuinig/new/.rss?limit=50",
    "https://www.reddit.com/r/frugal/new/.rss?limit=50",
]
INTERESTING = ("korting", "bespaar", "cashback", "verlengen", "overstap",
               "prijs", "black friday", "sale", "kortingscode", "deal",
               "retour", "garantie", "loyalty", "refurbished")
OUT_SCOPE = ("boodschappenlijst", "recepten", "maaltijden", "recept",
             "jumbo", "supermarkt", "ah bonus", "lidl")


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=13) as response:
        if response.status != 200:
            raise ValueError("HTTP " + str(response.status))
        return response.read(950000).decode("utf-8", "replace")


def plain(markup):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip().casefold()


def article_candidates(xml_text):
    """Only real reddit.com topic URLs, not subreddit fronts or search adverts."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    found = []
    nodes = [(x, False) for x in root.findall(".//item")]
    nodes += [(x, True) for x in root.findall(".//{http://www.w3.org/2005/Atom}entry")]
    for item, atom in nodes:
        title_value = item.findtext("{http://www.w3.org/2005/Atom}title") if atom else item.findtext("title")
        title = re.sub(r"\s+", " ", title_value or "").strip()
        if atom:
            links = item.findall("{http://www.w3.org/2005/Atom}link")
            link = next((x.attrib.get("href","") for x in links
                         if x.attrib.get("rel","alternate")=="alternate"), "")
        else:
            link = item.findtext("link") or ""
        link = link.split("#")[0].split("?")[0]
        parsed = urllib.parse.urlparse(link)
        domain = parsed.hostname or ""
        if domain not in ("reddit.com", "www.reddit.com", "old.reddit.com"):
            continue
        if not re.fullmatch(r"/r/[\w]+/comments/[a-z0-9]+/[^/]+/?", parsed.path, re.I):
            continue
        lower = title.casefold()
        if len(title) < 12 or not any(word in lower for word in INTERESTING):
            continue
        if any(word in lower for word in OUT_SCOPE):
            continue
        identity = hashlib.sha256(parsed.path.lower().encode()).hexdigest()[:16]
        found.append({"id": identity, "title": title[:190], "url": link,
                      "status": "community_onderzoekskandidaat", "verified": False})
    return found


def run():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {"redditCandidates": []}
    preserved = {r["id"]: r for r in previous.get("redditCandidates", [])
                 if isinstance(r, dict) and r.get("id") and r.get("url")}
    checks = []
    for name, url, key_terms in OFFICIAL:
        try:
            content = plain(fetch(url))
            matched = all(term.casefold() in content for term in key_terms)
            checks.append({"name": name, "url": url,
                           "status": "terms_found" if matched else "content_changed_review_needed",
                           "checkedAt": now,
                           "note": "Site bereikbaar, voorwaarden/productacties zijn niet handmatig herbevestigd."})
        except Exception as exc:
            checks.append({"name": name, "url": url, "status": "error",
                           "error": str(exc)[:140], "checkedAt": now})
    queries = []
    for q in REDDIT_QUERIES:
        url = "https://www.bing.com/search?" + urllib.parse.urlencode(
            {"q": q, "format": "rss", "setlang": "nl-NL"})
        try:
            items = article_candidates(fetch(url))
            for item in items:
                item["lastSeenAt"] = now
                preserved[item["id"]] = item
            queries.append({"query": q, "status": "ok" if items else "empty",
                            "items": len(items)})
        except Exception as exc:
            queries.append({"query": q, "status": "error", "items": 0,
                            "error": str(exc)[:140]})
    reddit_feeds = []
    for url in REDDIT_FEEDS:
        try:
            items = article_candidates(fetch(url))
            for item in items:
                item["lastSeenAt"] = now
                preserved[item["id"]] = item
            reddit_feeds.append({"url":url,"status":"ok" if items else "empty",
                                 "items":len(items)})
        except Exception as exc:
            # Public Reddit endpoints may require OAuth or return HTTP 429.
            # Do not bypass restrictions or label a blocked feed as working.
            reddit_feeds.append({"url":url,"status":"error","items":0,
                                 "error":str(exc)[:140]})
    # Community leads have no independent eligibility or savings evidence.
    ideas = list(preserved.values())[:120]
    output = {"updatedAt": now, "officialSources": checks, "redditQueries": queries,
              "redditCandidates": ideas, "redditFeeds": reddit_feeds,
              "reviewedStrategyCount": len(json.loads((ROOT/"bespaarstrategien.json").read_text(encoding="utf-8")).get("items", [])),
              "note": "Automatisch ontdekte Reddit posts zijn alleen onderzoekskandidaten. Officiële bronbereikbaarheid en tekstmatch bewijzen geen actuele persoonlijke besparing."}
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"officialTermsFound":sum(x["status"]=="terms_found" for x in checks),
                      "officialChecks":len(checks),
                      "redditCandidates":len(ideas),
                      "redditQueryErrors":sum(x["status"]=="error" for x in queries),
                      "redditFeedErrors":sum(x["status"]=="error" for x in reddit_feeds)}, ensure_ascii=False))


if __name__ == "__main__":
    run()
