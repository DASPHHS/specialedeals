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
    for brand in cfg["brands"]:
        if brand.casefold() in t: points+=32;matches.append(brand)
    for group,words in cfg["categories"].items():
        if any(w.casefold() in t for w in words):points+=12
    for term in cfg["exclude"]:
        if term.casefold() in t:points-=50
    if re.search(r"\b(47(?: 1/3)?|xl)\b",t):points+=8
    return points, matches
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
        if title and link.startswith("http"):out.append({"title":title,"url":link,"source":source})
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
    seen=set();selected=[]
    for item in results:
        s,m=score(item["title"])
        key=(item["title"].casefold(),item["url"])
        if s>=cfg["minScore"] and key not in seen:
            seen.add(key);selected.append({**item,"score":s,"matched":m,"price":None,"priceVerified":False})
    selected.sort(key=lambda x:x["score"],reverse=True)
    out={"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"deals":selected[:100],"sources":statuses,"note":"Feedvermeldingen zijn niet onafhankelijk geverifieerd; prijs, voorraad en geldigheid moeten op winkelwebsite worden gecontroleerd."}
    (ROOT/"live-deals.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"count":len(selected),"sources":statuses},ensure_ascii=False))
if __name__=="__main__":main()
