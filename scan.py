#!/usr/bin/env python3
"""Public-source discovery. Never present unverifiable candidates as actual price deals."""
import datetime as dt
import html
import hashlib
import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

SOURCES=[
 ("We Love Sample Sales","sales","https://www.welovesamplesales.nl/permaand/deze-maand"),
 ("Stockverkopen","sales","https://www.stockverkopen.nl/samplesales.html"),
 ("Your Sample Sale","sales","https://yoursamplesale.nl/evenementen/"),
 ("Eventbrite","sales","https://www.eventbrite.nl/d/netherlands/sample-sale/"),
 ("Chicmi","sales","https://www.chicmi.com/nl/sample-sales/"),
 ("GratiZ","contests","https://www.gratiz.nl/prijsvragen"),
 ("Prijsvragen.nl","contests","https://www.prijsvragen.nl/"),
 ("Gratiswinactie","contests","https://gratiswinactie.nl/"),
 ("Prijzenzolder","contests","https://www.prijzenzolder.nl/wineenauto.html"),
 ("AlleFolders","deals","https://www.allefolders.nl/aanbiedingen"),
 ("Reclamefolder","deals","https://www.reclamefolder.nl/categorieen/"),
 ("Pepper","deals","https://nl.pepper.com/"),
 ("SuperSales","deals","https://www.supersales.nl/"),
]
SIGNALS={"sales":("sample sale","stock sale","stockverkoop","stock sale","merkkleding","archive sale","outlet sale","warehouse sale","sample-sale","/sample","stock-sale","stockverkoop","sample sale"),
"contests":("win een","win de","win het","win 2","win 5","winactie","prijsvraag","giveaway","winnen","/winactie/"),
"deals":("aanbieding","korting","deal","outlet","sale","2+1","1+1","aanbiedingen","discount")}
LIKES=("padel","sport","schoenen","heren","menswear","premium","outdoor","sneaker","salomon","hoka","apple","dyson","rituals","nike","adidas","tommy","ralph","kuyichi","vakantie","reizen","reis","cadeaubon","geld","shoptegoed","laptop","fashion","denim","super sale","ticket","elektronica","koffie")
NOISE=("baby","kinderspeelgoed","kinderwagen","loterij","gokken","casino","speelgoedfolder","/privacy","/cookies","/contact","/login","/tag/","/categorie/","/category/")
class Links(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.href=None;self.text=[];self.active=False
 def handle_starttag(self,tag,attrs):
  if tag=="a" and not self.active:
   self.href=dict(attrs).get("href","");self.text=[];self.active=True
 def handle_data(self,data):
  if self.active:self.text.append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.active:
   title=" ".join(" ".join(self.text).split())
   if title and self.href:self.links.append((title,self.href))
   self.active=False
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; DealsRadar/2.0; public-listings)","Accept-Language":"nl-NL,nl;q=0.9"})
 with urllib.request.urlopen(req,timeout=20) as response:
  if response.status!=200:raise ValueError("HTTP "+str(response.status))
  return response.read(2500000).decode("utf-8","replace")
def score(title,kind):
 t=title.casefold();value=45
 value+=sum(8 for word in LIKES if word in t)
 if kind=="sales":value+=8
 if "kinderen" in t or "kidswear" in t:value-=8
 if "dames" in t or "womenswear" in t:value+=2
 if "heren" in t or "menswear" in t:value+=8
 if any(n in t for n in NOISE):value-=70
 return min(100,max(0,value))
def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 today=dt.date.today().isoformat()
 try:
  with open("data.json",encoding="utf-8") as f:old=json.load(f)
 except (ValueError,OSError):old={"items":[]}
 # Retain previous recent discoveries only if they are younger than 7 days; do not imply new verification.
 items={x["id"]:x for x in old.get("items",[]) if x.get("id") and x.get("discoveredAt","")[:10]>=str(dt.date.today()-dt.timedelta(days=7))}
 statuses=[]
 for name,kind,base in SOURCES:
  try:
   p=Links();p.feed(fetch(base));count=0
   for title,href in p.links:
    if not 12<=len(title)<=160:continue
    url=urljoin(base,html.unescape(href));parts=urlsplit(url)
    if parts.scheme!="https" or not parts.hostname:continue
    if any(x in url.casefold() for x in ("/privacy","/cookie","/contact","/account","/login","facebook.com","instagram.com")):continue
    phrase=(title+" "+parts.path).casefold()
    if not any(s in phrase for s in SIGNALS[kind]):continue
    rank=score(title,kind)
    if rank<35:continue
    ident=hashlib.sha256((kind+" "+url.split("?")[0]).encode()).hexdigest()[:20]
    # A candidate cannot become a confirmed offer through discovery alone.
    if ident in items:items[ident]["lastSeenAt"]=now;count+=1;continue
    audience="women" if ("womenswear" in phrase or "dames" in phrase) and "heren" not in phrase and "menswear" not in phrase else "men" if ("heren" in phrase or "menswear" in phrase) and "dames" not in phrase else "all"
    items[ident]={"id":ident,"kind":kind,"title":title,"description":("Evenementvermelding. Controleer plaats, datum, maten, tickets en prijzen bij de organisator." if kind=="sales" else "Gevonden prijsvraag. Controleer gratis deelname, looptijd en Nederlandse toelating." if kind=="contests" else "Aanbiedingssignaal. Controleer artikel, echte prijs, voorraad en eventuele winkelafstand."),"source":name,"url":url,"status":"Te controleren","score":rank,"audience":audience,"discoveredAt":now,"lastSeenAt":now}
    count+=1
   statuses.append({"name":name,"status":"ok","count":count})
  except Exception as e:statuses.append({"name":name,"status":"error","count":0,"error":str(e)[:120]})
 # Conservative expiration until explicit date parsing is available.
 rows=sorted(items.values(),key=lambda x:(-x["score"],x["title"]))[:450]
 result={"updatedAt":now,"items":rows,"sources":statuses,"note":"Unverified public discovery only. Do not infer real availability, free entry or local distance."}
 with open("data.json","w",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"total":len(rows),"reachable":sum(s["status"]=="ok" for s in statuses),"status":statuses},ensure_ascii=False))
if __name__=="__main__":main()
