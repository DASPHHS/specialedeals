#!/usr/bin/env python3
"""Conservative, transparent public listing discovery. No anti-bot circumvention."""
import datetime as dt
import hashlib
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

SOURCES=[
 ("AlleFolders aanbiedingen","deals","https://www.allefolders.nl/aanbiedingen"),
 ("Pepper","deals","https://nl.pepper.com/"),
 ("SuperSales","deals","https://www.supersales.nl/"),
 ("GratiZ prijsvragen","contests","https://www.gratiz.nl/prijsvragen"),
 ("Prijsvragen.nl","contests","https://www.prijsvragen.nl/"),
 ("Gratiswinactie","contests","https://gratiswinactie.nl/"),
 ("We Love Sample Sales","sales","https://www.welovesamplesales.nl/permaand/deze-maand"),
 ("Stockverkopen","sales","https://www.stockverkopen.nl/samplesales.html"),
 ("Your Sample Sale","sales","https://yoursamplesale.nl/evenementen/"),
 ("Eventbrite sample sales","sales","https://www.eventbrite.nl/d/netherlands/sample-sale/"),
 ("Chicmi","sales","https://www.chicmi.com/nl/sample-sales/"),
]
PREFERRED=("padel","hoka","salomon","nike","adidas","apple","dyson","rituals","outdoor","travel","vakantie","reis","racket","schoenen","sneakers","mode","heren","kleding","elektronica","design","koffie","festival","verzorging","sample sale","stock sale","warehouse","win","prijs","cash","geld","laptop","sale")
EXCLUDE=("baby","kinderwagen","kinderbed","schooltas","loterij","casino","gok","slot machine")
class Links(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.href=None;self.parts=[];self.depth=0
 def handle_starttag(self,tag,attrs):
  if tag=="a":self.href=dict(attrs).get("href");self.parts=[];self.depth=1
  elif self.href:self.depth+=1
 def handle_data(self,t):
  if self.href:self.parts.append(t)
 def handle_endtag(self,tag):
  if not self.href:return
  if tag=="a":
   title=" ".join(" ".join(self.parts).split())
   if title:self.links.append((title,self.href))
   self.href=None;self.parts=[];self.depth=0
  elif self.depth>1:self.depth-=1

def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; PersonalDealsRadar/1.0; public-listings-only)"})
 with urllib.request.urlopen(req,timeout=18) as resp:
  if resp.status!=200:raise ValueError("HTTP "+str(resp.status))
  return resp.read(1200000).decode("utf-8","replace")

def score(title,kind):
 t=title.casefold();n=45
 n+=min(28,sum(7 for w in PREFERRED if w in t))
 if any(w in t for w in EXCLUDE):n-=70
 if kind=="sales":n+=10
 if re.search(r"\b(gratis|free)\b",t):n+=4
 if re.search(r"\b(dames|women)\b",t):n-=3
 return n

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat();items={};stats=[]
 for name,kind,url in SOURCES:
  count=0
  try:
   p=Links();p.feed(fetch(url))
   for title,href in p.links:
    target=urljoin(url,html.unescape(href));h=urlsplit(target)
    if h.scheme!="https" or not h.hostname:continue
    if len(title)<12 or len(title)>175:continue
    if target.rstrip("/") == url.rstrip("/"):continue
    if any(w in title.casefold() for w in ("cookie","privacy","contact","facebook","instagram","inloggen","algemene voorwaarden","nieuwsbrief")):continue
    # Filter navigation: only real candidate links with signals in heading or path.
    t=(title+" "+h.path).casefold()
    hints={"deals":("aanbied","korting","sale","deal","product","actie","shop","outlet"),
           "contests":("win","prijsvraag","gratis","verloot","giveaway"),
           "sales":("sale","stock","verkoop","event","fashion","sample")}
    if not any(w in t for w in hints[kind]):continue
    rank=score(title,kind)
    if rank<30:continue
    key=hashlib.sha256((kind+"|"+target.split("?")[0]).encode()).hexdigest()[:20]
    items[key]={"id":key,"kind":kind,"title":title,"description":"Ontdekt op een openbare overzichtspagina. Prijs, datum, beschikbaarheid, afstand en voorwaarden nog bij de aanbieder controleren.","url":target,"source":name,"score":rank,"label":"Kandidaat • niet geverifieerd","discoveredAt":now}
    count+=1
   stats.append({"name":name,"status":"ok","count":count})
  except Exception as e:stats.append({"name":name,"status":"fout: "+str(e)[:100],"count":0})
 rows=sorted(items.values(),key=lambda x:-x["score"])
 with open("data.json","w",encoding="utf-8") as f:json.dump({"updatedAt":now,"items":rows[:300],"sources":stats,"notice":"Discovery only; no verified discount or ticket and no guarantee of completeness"},f,ensure_ascii=False,indent=2)
 print("Candidates:",len(rows),"Sources:",[(s["name"],s["status"],s["count"]) for s in stats])
if __name__=="__main__":main()
