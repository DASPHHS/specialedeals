#!/usr/bin/env python3
"""Minimal exact-product shop observer using public Product JSON-LD/meta data.
No price-history, discount validation or fake live-stock inference.
"""
import datetime,json,pathlib,re,urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
TARGETS=json.loads((ROOT/"shop-targets.json").read_text())["targets"]
class ProductHTML(HTMLParser):
 def __init__(self):
  super().__init__();self.meta={};self.ld=[];self.collect=False;self.buffer=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta":
   key=(a.get("property") or a.get("name") or "").lower()
   if key:self.meta[key]=a.get("content","")
  if tag=="script" and a.get("type","").lower()=="application/ld+json":
   self.collect=True;self.buffer=[]
 def handle_data(self,data):
  if self.collect:self.buffer.append(data)
 def handle_endtag(self,tag):
  if tag=="script" and self.collect:
   raw="".join(self.buffer).strip();self.collect=False
   if raw:
    try:self.ld.append(json.loads(raw))
    except (ValueError,TypeError):pass
def product_nodes(tree):
 if isinstance(tree,list):
  for x in tree:yield from product_nodes(x)
 elif isinstance(tree,dict):
  kind=tree.get("@type","")
  if isinstance(kind,list):is_product=any(str(t).lower()=="product" for t in kind)
  else:is_product=str(kind).lower()=="product"
  if is_product:yield tree
  for v in tree.values():
   if isinstance(v,(dict,list)):yield from product_nodes(v)
def asprice(value):
 if value is None:return None
 try:
  v=float(str(value).replace("€","").replace(" ","").replace(",","."))
  return round(v,2) if 0.5<=v<=5000 else None
 except (ValueError,TypeError):return None
def normalize(s):return re.sub(r"[^a-z0-9]+"," ",str(s).casefold()).strip()
def matches(name,required):
 t=normalize(name)
 return all(normalize(w) in t for w in required)
def find_observation(body,target):
 parser=ProductHTML();parser.feed(body)
 for obj in parser.ld:
  for product in product_nodes(obj):
   name=str(product.get("name") or "")
   if not matches(name,target["require"]):continue
   offers=product.get("offers") or {}
   if isinstance(offers,list):offers=next((o for o in offers if isinstance(o,dict) and asprice(o.get("price")) is not None),{})
   if not isinstance(offers,dict):continue
   price=asprice(offers.get("price"))
   if price is None:
    spec=offers.get("priceSpecification") or {}
    if isinstance(spec,dict):price=asprice(spec.get("price"))
   if price is not None:
    return {"price":price,"titleOnPage":name,"currency":offers.get("priceCurrency","EUR"),"availability":str(offers.get("availability") or "niet gepubliceerd"),"method":"product_jsonld"}
 # Only use merchant price meta when exact open graph item title matches expected variant.
 name=parser.meta.get("og:title","")
 price=asprice(parser.meta.get("product:price:amount"))
 if price is not None and matches(name,target["require"]):
  return {"price":price,"titleOnPage":name,"currency":parser.meta.get("product:price:currency","EUR"),"availability":"niet uit productdata bevestigd","method":"exact_title_product_meta"}
 return None
def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 entries=[];checks=[]
 for target in TARGETS:
  outcome={"store":target["store"],"url":target["url"],"checkedAt":now}
  try:
   req=urllib.request.Request(target["url"],headers={"User-Agent":"Mozilla/5.0 (compatible; PersonalDealsObserver/1.0)"})
   with urllib.request.urlopen(req,timeout=13) as res:
    body=res.read(1100000).decode("utf-8","replace")
   result=find_observation(body,target)
   if result is None:
    outcome.update(status="not_extracted",note="Geen betrouwbaar exact productprijsveld")
   elif str(result["currency"]).upper()!="EUR":
    outcome.update(status="currency_mismatch")
   else:
    outcome.update(status="observed",method=result["method"])
    entries.append({"title":target["title"],"store":target["store"],"url":target["url"],"category":target["category"],"price":result["price"],
       "checkedAt":now,"titleOnPage":result["titleOnPage"],"availabilityText":result["availability"],"shippingNote":target["shippingNote"],
       "referencePrice":None,"allInVerified":False,"marketComparisonVerified":False,"status":"Geobserveerde winkelprijs: onafhankelijke vergelijking ontbreekt"})
  except Exception as exc:
   outcome.update(status="unavailable",error=str(exc)[:150])
  checks.append(outcome)
 payload={"checkedAt":now,"offers":entries,"checks":checks,"note":"Exact merchant structured product prices, not independently compared market prices or guaranteed shipping total. Items with unavailable data omitted."}
 (ROOT/"merchant-observations.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"observed":len(entries),"checked":len(checks),"status":[{"shop":x["store"],"status":x["status"]} for x in checks]},ensure_ascii=False))
if __name__=="__main__":main()
