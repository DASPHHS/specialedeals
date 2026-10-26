#!/usr/bin/env python3
"""Personal Speciale Deals *discovery* scanner.
Brings together targeted RSS and brand-specific Google News queries.
No feed mention is labeled an independently verified deal.
"""
import datetime, html, json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
CFG=json.loads((ROOT/"radar-config.json").read_text())
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; PersonalDealDiscovery/1.2; RSS reader)"}

def load_watches():
 try:
  data=json.loads((ROOT/"watchlist.json").read_text(encoding="utf-8"))
  return [str(x["product"]).strip() for x in data.get("items",[]) if isinstance(x,dict) and str(x.get("product","")).strip()][:100]
 except (OSError,ValueError,KeyError):
  return []
WATCHES=load_watches()
try:
 INTERNATIONAL=json.loads((ROOT/"international-stores.json").read_text(encoding="utf-8"))["retailers"]
except (OSError,ValueError,KeyError):
 INTERNATIONAL=[]
def normalized_tokens(value):
 stop={"maat","eu","us","heren","dames","euro","prijs","sale","korting","aanbieding","47","47⅓"}
 return [w for w in re.findall(r"[a-zà-ÿ0-9]+",value.casefold()) if w not in stop and len(w)>1]
def watch_match(title,watch):
 words=normalized_tokens(watch)
 titlewords=set(normalized_tokens(title))
 return len(words)>=2 and all(word in titlewords for word in words)

def fetch(url):
 req=urllib.request.Request(url,headers=HEADERS)
 with urllib.request.urlopen(req,timeout=18) as r:
  if r.status!=200:raise ValueError("HTTP "+str(r.status))
  return r.read(1500000).decode("utf-8","replace")
def strip(s): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",s or ""))).strip()
def cleanlink(url):
 url=strip(url)
 if not url.startswith("https://"):return ""
 return url
def score(title):
 t=title.casefold()
 if any(w in t for w in CFG["excludeTerms"]):return -1000,[]
 matched=[]
 for brand in CFG["brands"]:
  if brand.casefold() in t:matched.append(brand)
 for watch in WATCHES:
  if watch_match(title,watch):matched.append("watch:"+watch)
 if not matched:return -1000,[]
 # Ambiguous words: 'Apple' must be actual tech, not generic fruit.
 if "apple" in matched and not any(w in t for w in ("iphone","ipad","macbook","airpods","apple watch","imac","apple pencil","apple tv","apple silicon","apple store","apple computer")):matched.remove("apple")
 # 'Adidas/Nike' without an apparel/sports or sale context is not enough
 if matched and all(w in ("nike","adidas") for w in matched) and not any(w in t for w in ("schoen","sneaker","heren","sale","outlet","korting","padel","racket","sample","kleding","shirt","jas")):return -1000,[]
 if not matched:return -1000,[]
 if any(x in t for x in ("dames","women","womens","girls","meisjes")):return -1000,[]
 base=35+min(20,8*len(matched))
 if any(w in t for w in ("aanbieding","deal","korting","sale","outlet","uitverkoop","prijs","sample","discount")):base+=12
 if any(w in t for w in ("xl","47 1/3","47⅓","maat 47")):base+=9
 if any(w in t for w in ("sample sale","archive sale")):base+=8
 return base,matched
def category(title):
 t=title.casefold()
 for name,terms in CFG["groups"].items():
  if any(w in t for w in terms):return name
 return "Overig"
def extract_price(raw):
 vals=re.findall(r"(?:€\s*|EUR\s+)(\d{1,5}(?:[.,]\d{2})?)(?!\d)",raw,re.I)
 numbers={float(v.replace(",",".")) for v in vals}
 return next(iter(numbers)) if len(numbers)==1 and .5<=next(iter(numbers))<=10000 else None
def rss_items(raw,source,kind):
 root=ET.fromstring(raw);items=[]
 nodes=root.findall(".//item")+root.findall(".//{http://www.w3.org/2005/Atom}entry")
 for e in nodes:
  def val(key):
   x=e.find(key)
   return "".join(x.itertext()).strip() if x is not None else ""
  title=strip(val("title") or val("{http://www.w3.org/2005/Atom}title"))
  url=val("link");desc=strip(val("description") or val("{http://www.w3.org/2005/Atom}summary"))
  if not url:
   a=e.find("{http://www.w3.org/2005/Atom}link")
   if a is not None:url=a.attrib.get("href","")
  url=cleanlink(url)
  if not title or not url:continue
  date=strip(val("pubDate") or val("published") or val("{http://www.w3.org/2005/Atom}published"))
  items.append({"title":title[:230],"url":url,"source":source,"sourceType":kind,"published":date[:60],"price":extract_price(title+" "+desc) if kind=="community" else None})
 return items
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.active=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="a" and a.get("href","").startswith(("/nl/","/offers/","https://www.ibood.com/")):
   self.active={"url":urllib.parse.urljoin("https://www.ibood.com",a["href"]),"parts":[]}
 def handle_data(self,data):
  if self.active:self.active["parts"].append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.active:
   title=strip(" ".join(self.active["parts"]))
   if 8<len(title)<230:self.links.append({"title":title,"url":self.active["url"],"source":"iBOOD","sourceType":"retailer","price":None})
   self.active=None
def promotion_kind(title):
 t=title.casefold()
 if any(w in t for w in ("winactie","maak kans","giveaway","prijsvraag")):return "winactie"
 if any(w in t for w in ("kortingscode","promocode","actiecode","couponcode")):return "kortingscode"
 return "deal"
def is_sample(title):
 t=title.casefold()
 return any(w in t for w in ("sample sale","sample-sale","archive sale","stock sale","warehouse sale","sampleverkoop","stockverkoop","magazijnverkoop"))
def search_quality(item):
 if item.get("sourceType")!="search":return True
 url=item.get("url","")
 host=(urllib.parse.urlparse(url).hostname or "").lower()
 allowed=CFG.get("allowedDiscoveryDomains",[])
 if not any(host==d or host.endswith("."+d) for d in allowed):return False
 t=(item.get("title","")+" "+urllib.parse.urlparse(url).path).casefold()
 # Do not publish brand homepages, Wikipedia, US retailers or generic catalogs
 return any(term in t for term in ("aanbieding","korting","sale","outlet","actie","deal","sample","discount","weekend-aanbieding","prijs","%","clearance","special"))

def relevant_hits(rows):
 """Count genuinely relevant usable discovery leads, not successful HTTP/Bing responses."""
 return sum(1 for item in rows
            if search_quality(item) and score(item.get("title",""))[0] >= CFG["minScore"])

def discovery():
 raw_items=[];statuses=[]
 for source in CFG["sourceFeeds"]:
  try:
   content=fetch(source["url"])
   if source["kind"]=="rss":rows=rss_items(content,source["name"],source.get("type","feed"))
   else:
    p=Links();p.feed(content);rows=p.links
   statuses.append({"source":source["name"],"status":"ok" if rows else "empty","items":len(rows)})
   raw_items.extend(rows)
  except Exception as e:statuses.append({"source":source["name"],"status":"error","error":str(e)[:120],"items":0})
 for i,q in enumerate(CFG["priorityQueries"]+["\""+w+"\" aanbieding korting" for w in WATCHES[:12]]):
  try:
   query=q+" when:7d"
   url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query,"hl":"nl","gl":"NL","ceid":"NL:nl"})
   rows=rss_items(fetch(url),"Gerichte merkzoekopdracht","news")
   hit_count=relevant_hits(rows)
   statuses.append({"source":"Merkscan "+str(i+1),"status":"ok" if hit_count else "empty","items":hit_count,"retrieved":len(rows)})
   raw_items.extend(rows)
  except Exception as e:statuses.append({"source":"Merkscan "+str(i+1),"status":"error","error":str(e)[:120],"items":0})
 # Officially announced future premium-brand sales can be published weeks ahead.
 # Discovery is not confirmation of dates, admission, prices, or user sizes.
 for i,q in enumerate(CFG.get("sampleSearchQueries",[])):
  try:
   url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:60d","hl":"nl","gl":"NL","ceid":"NL:nl"})
   rows=rss_items(fetch(url),"Gerichte sample-sale-zoekopdracht","news")
   hit_count=relevant_hits(rows)
   statuses.append({"source":"Samplezoekopdracht "+str(i+1),"status":"ok" if hit_count else "empty","items":hit_count,"retrieved":len(rows)})
   raw_items.extend(rows)
  except Exception as exc:
   statuses.append({"source":"Samplezoekopdracht "+str(i+1),"status":"error","error":str(exc)[:120],"items":0})
 # Secondary broad RSS discovery, explicitly kept as unverified search leads.
 # This adds retailer and outlet coverage where the news RSS has no product offers.
 for i,q in enumerate(CFG.get("broadSearchQueries",[])):
  try:
   url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"format":"rss","setlang":"nl-NL","cc":"nl"})
   rows=rss_items(fetch(url),"Gerichte winkelscan","search")
   hit_count=relevant_hits(rows)
   statuses.append({"source":"Winkelzoekopdracht "+str(i+1),"status":"ok" if hit_count else "empty","items":hit_count,"retrieved":len(rows)})
   raw_items.extend(rows)
  except Exception as e:
   statuses.append({"source":"Winkelzoekopdracht "+str(i+1),"status":"error","error":str(e)[:120],"items":0})
 # Search foreign EU merchants that officially publish NL delivery. Each hit stays
 # a research lead, with no assumption about shipping for the chosen item.
 for i,q in enumerate(CFG.get("internationalQueries",[])):
  try:
   url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"format":"rss","setlang":"en-US","cc":"nl"})
   rows=rss_items(fetch(url),"Internationale winkelscan","search")
   hit_count=relevant_hits(rows)
   statuses.append({"source":"Internationale zoekopdracht "+str(i+1),"status":"ok" if hit_count else "empty","items":hit_count,"retrieved":len(rows)})
   raw_items.extend(rows)
  except Exception as exc:
   statuses.append({"source":"Internationale zoekopdracht "+str(i+1),"status":"error","error":str(exc)[:120],"items":0})
 return raw_items,statuses
def main():
 raw,statuses=discovery();deals=[];promos=[];samples=[];seen=set()
 rejected={"irrelevant":0,"source_quality":0,"duplicate":0};diagnostic_samples=[];source_quality_examples=[]
 for item in raw:
  title=item["title"];relevance,matches=score(title)
  if not search_quality(item):
   rejected["source_quality"]+=1
   if len(source_quality_examples)<10:source_quality_examples.append({"title":title[:130],"url":item.get("url","")[:220],"source":item.get("source","")})
   if len(diagnostic_samples)<8:diagnostic_samples.append({"why":"source_quality","title":title[:120],"url":item.get("url","")[:200],"source":item.get("source","")})
   continue
  if relevance<CFG["minScore"]:
   rejected["irrelevant"]+=1
   if len(diagnostic_samples)<12:diagnostic_samples.append({"why":"irrelevant","title":title[:120],"url":item.get("url","")[:200],"source":item.get("source","")})
   continue
  # Distinct titles, not repeated Google News syndications.
  key=re.sub(r"[^a-z0-9]","",title.casefold())[:100]
  if key in seen:rejected["duplicate"]+=1;continue
  seen.add(key)
  item.update({"score":relevance,"matched":matches,"category":category(title),"discovery":True,"priceVerified":False,"allInVerified":False,"stockVerified":False,"variantVerified":False,"referencePriceVerified":False,"status":"Kandidaat: controle vereist","referencePrice":None,"checkedAt":None})
  k=promotion_kind(title)
  if is_sample(title):item["kind"]="sample_sale";samples.append(item)
  elif k!="deal":item["kind"]=k;item["verified"]=False;promos.append(item)
  else:deals.append(item)
 for group in (deals,samples,promos):group.sort(key=lambda d:(d["score"],d["sourceType"]!="news"),reverse=True)
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 result={"updatedAt":now,"diagnostics":{**rejected,"examples":diagnostic_samples,"sourceQualityExamples":source_quality_examples},"deals":deals,"samples":samples,"promotions":promos,"sources":statuses,"retailers":CFG["specialistRetailers"]+[{"name":r["name"],"url":r["dealLandingUrl"],"category":"Internationaal · "+r["category"],"shippingPolicyUrl":r["shippingPolicyUrl"],"shippingToNL":r["shippingToNL"],"country":r["country"]} for r in INTERNATIONAL],"coverage":{"searchQueries":len(CFG["priorityQueries"])+len(CFG.get("broadSearchQueries",[]))+len(CFG.get("sampleSearchQueries",[]))+len(CFG.get("internationalQueries",[]))+min(12,len(WATCHES)),"internationalQueries":len(CFG.get("internationalQueries",[])),"internationalShops":len(INTERNATIONAL),"sourcesConfigured":len(CFG["sourceFeeds"]),"scannedItems":len(raw),"personalMatches":len(deals)+len(samples)+len(promos)},"note":"Discovery only. Every price/size/stock/discount must be checked at the merchant before buying."}
 if statuses and all(x["status"]=="error" for x in statuses):
  try:
   previous=json.loads((ROOT/"live-deals.json").read_text())
   for key in ("deals","samples","promotions"):
    result[key]=previous.get(key,[])
   result["lastSuccessfulDiscoveryAt"]=previous.get("lastSuccessfulDiscoveryAt",previous.get("updatedAt"))
   result["note"]="Alle ontdekbronnen mislukt. Vorige vondsten behouden; niet opnieuw geverifieerd."
  except (OSError,ValueError):pass
 else:result["lastSuccessfulDiscoveryAt"]=now
 (ROOT/"live-deals.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"deals":len(deals),"samples":len(samples),"promotions":len(promos),"coverage":result["coverage"],"failed":sum(s["status"]=="error" for s in statuses)}))
if __name__=="__main__":main()
