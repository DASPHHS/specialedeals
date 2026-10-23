#!/usr/bin/env python3
"""Speciale Deals: conservative daily feed collector, no fabricated prices."""
import json, re, urllib.request, urllib.parse, html, datetime, pathlib, xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parent
cfg=json.loads((ROOT/"radar-config.json").read_text())
headers={"User-Agent":"SpecialeDeals/1.0 (personal price discovery; contact via repository)"}
def fetch(url):
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=18) as r:
        if r.status!=200: raise ValueError("HTTP "+str(r.status))
        return r.read(2_000_000).decode("utf-8",errors="replace")
def strip(s): return re.sub(r"\s+"," ",html.unescape(re.sub("<[^>]+>"," ",s or ""))).strip()
def score(title):
    t=title.casefold(); points=0; matches=[]
    # Explicit women's products are outside the target profile.
    if any(re.search(r"(?<!\w)"+re.escape(term.casefold())+r"(?!\w)",t) for term in cfg.get("excludeGendered",[])):
        return -1000, []
    # Apparel and footwear must explicitly be for men or unisex.
    apparel=any(term in t for term in cfg.get("apparelTerms",[]))
    men=any(re.search(r"(?<!\w)"+re.escape(term.casefold())+r"(?!\w)",t) for term in cfg.get("menswearKeywords",[]))
    if apparel and not men:
        return -1000, []
    for brand in cfg["brands"]:
        if brand.casefold() in t: points+=32;matches.append(brand)
    for group,words in cfg["categories"].items():
        if any(w.casefold() in t for w in words):points+=12
    for term in cfg["exclude"]:
        if term.casefold() in t:points-=50
    if re.search(r"\b(47(?: 1/3)?|xl)\b",t):points+=8
    return points, matches
def extract_price(raw):
    """Return a feed-indicated euro price only if unambiguous, never 'verified'."""
    matches = re.findall(r"(?:€\s*|EUR\s+)(\d{1,5}(?:[.,]\d{2})?)(?!\d)", raw, flags=re.I)
    values = {float(value.replace(",", ".")) for value in matches}
    return next(iter(values)) if len(values) == 1 and 0.5 <= next(iter(values)) <= 10000 else None

def rss_items(text,source):
    root=ET.fromstring(text)
    out=[]
    for entry in list(root.findall(".//item"))+list(root.findall(".//{http://www.w3.org/2005/Atom}entry")):
        def value(tag):
            x=entry.find(tag)
            return ("".join(x.itertext()) if x is not None else "").strip()
        title=strip(value("title") or value("{http://www.w3.org/2005/Atom}title"))
        link=value("link")
        if not link:
            x=entry.find("{http://www.w3.org/2005/Atom}link")
            link=x.attrib.get("href","") if x is not None else ""
        description=value("description") or value("{http://www.w3.org/2005/Atom}summary")
        price=extract_price(title+" "+strip(description))
        if title and link.startswith("http"):out.append({"title":title,"url":link,"source":source,"price":price})
    return out
class IboodParser(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a" and a.get("href","").startswith(("/nl/","/offers/","https://www.ibood.com/")):
            self.current={"url":urllib.parse.urljoin("https://www.ibood.com",a["href"]),"parts":[]}
        if self.current and tag in ("h2","h3","span","p"):self.current["parts"].append(" ")
    def handle_data(self,data):
        if self.current:self.current["parts"].append(data)
    def handle_endtag(self,tag):
        if tag=="a" and self.current:
            title=strip(" ".join(self.current["parts"]))
            if 12<len(title)<220:self.links.append({"title":title,"url":self.current["url"],"source":"iBOOD"})
            self.current=None
def promotion_kind(title):
    t=title.casefold()
    if any(w in t for w in ("winactie","prijsvraag","win een","maak kans","giveaway","verloting")):
        return "winactie"
    if any(w in t for w in ("kortingscode","kortingscodes","actiecode","couponcode","voucher code","promocode","code:")):
        return "kortingscode"
    return "deal"

def main():
    results=[]; statuses=[]
    for src in cfg["sourceFeeds"]:
        try:
            raw=fetch(src["url"])
            if src["kind"]=="rss":items=rss_items(raw,src["name"])
            else:
                parser=IboodParser();parser.feed(raw);items=parser.links
            statuses.append({"source":src["name"],"status":"ok" if items else "empty","items":len(items)})
            results+=items
        except Exception as e:statuses.append({"source":src["name"],"status":"error","error":str(e)[:180]})
    # Extra discovery queries. Google News RSS is a discovery source, not proof of validity.
    searches=[
        ("Winacties sport en technologie","(winactie OR prijsvraag OR giveaway) (padel OR apple OR dyson OR salomon)"),
        ("Winacties wonen en reizen","(winactie OR prijsvraag OR maak kans) (wellness OR hotel OR keukenmachine OR rituals)"),
        ("Kortingscodes premium merken","(kortingscode OR actiecode OR promocode) (davines OR salomon OR arcteryx OR nike OR rituals)"),
    ]
    for name,query in searches:
        try:
            url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query+" when:7d","hl":"nl","gl":"NL","ceid":"NL:nl"})
            items=rss_items(fetch(url),name)
            statuses.append({"source":name,"status":"ok" if items else "empty","items":len(items)})
            results.extend(items)
        except Exception as e:
            statuses.append({"source":name,"status":"error","error":str(e)[:180]})
    seen=set();selected=[];promotions=[]
    for item in results:
        s,m=score(item["title"])\n        kind=promotion_kind(item["title"])\n        # Competition candidates may be useful even where a brand is not named.\n        if kind!="deal" and s<0: continue
        key=item["url"].split("?")[0].rstrip("/").casefold()
        minimum=cfg.get("discoveryMode",{}).get("minimumCategoryScore",cfg["minScore"])
        if (s>=minimum or (kind!="deal" and s>=0 and any(w in item["title"].casefold() for w in ("padel","wellness","hotel","keuken","rituals","apple","dyson","salomon")))) and key not in seen:
            seen.add(key)
            entry={**item,"score":s,"matched":m,"discovery":not bool(m),"priceVerified":False,"priceOrigin":"feed" if item.get("price") is not None else None}
            kind=promotion_kind(item["title"])
            if kind=="deal":selected.append(entry)
            else:
                entry.update({"kind":kind,"verified":False,"code":None,"deadline":None,"conditionsVerified":False})
                promotions.append(entry)
    selected.sort(key=lambda x:x["score"],reverse=True)
    promotions.sort(key=lambda x:x["score"],reverse=True)
    out={"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"deals":selected[:100],"promotions":promotions[:60],"sources":statuses,"note":"Feedvermeldingen zijn niet onafhankelijk geverifieerd; prijs, voorraad en geldigheid moeten op winkelwebsite worden gecontroleerd."}
    (ROOT/"live-deals.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"count":len(selected),"promotions":len(promotions),"sources":statuses},ensure_ascii=False))
if __name__=="__main__":main()
