#!/usr/bin/env python3
"""Read exact public product prices, cautiously classify stock, and retain price history.

A merchant's structured data is an observation, not proof of checkout availability,
correct size, comparative lowest price or exact shipping price.
"""
import datetime, html, json, pathlib, re, urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
TARGETS=json.loads((ROOT/"shop-targets.json").read_text())["targets"]
HISTORY=ROOT/"price-history.json"

class ProductHTML(HTMLParser):
 def __init__(self):
  super().__init__();self.meta={};self.ld=[];self.collect=False;self.buffer=[];self.ignore=0;self.visible=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ("script","style"):self.ignore+=1
  if tag=="meta":
   key=(a.get("property") or a.get("name") or "").lower()
   if key:self.meta[key]=a.get("content","")
  if tag=="script" and a.get("type","").lower()=="application/ld+json":
   self.collect=True;self.buffer=[]
 def handle_data(self,data):
  if self.collect:self.buffer.append(data)
  elif self.ignore==0 and data.strip():self.visible.append(data.strip())
 def handle_endtag(self,tag):
  if tag=="script" and self.collect:
   raw="".join(self.buffer).strip();self.collect=False
   if raw:
    try:self.ld.append(json.loads(raw))
    except (ValueError,TypeError):pass
  if tag in ("script","style"):self.ignore=max(0,self.ignore-1)

def product_nodes(tree):
 if isinstance(tree,list):
  for x in tree:yield from product_nodes(x)
 elif isinstance(tree,dict):
  kind=tree.get("@type","")
  tags=kind if isinstance(kind,list) else [kind]
  if any(str(x).casefold()=="product" for x in tags):yield tree
  for val in tree.values():
   if isinstance(val,(dict,list)):yield from product_nodes(val)

def asprice(val):
 if val is None:return None
 try:
  price=float(str(val).replace("€","").replace(" ","").replace(",","."))
  return round(price,2) if 0.5<=price<=5000 else None
 except (ValueError,TypeError):return None
def normalize(s):
 s=html.unescape(str(s)).casefold()
 return re.sub(r"[^a-z0-9]+"," ",s).strip()
def matches(name,required):
 t=normalize(name)
 return all(normalize(word) in t for word in required)
def availability(value):
 v=str(value).casefold()
 if "outofstock" in v or "soldout" in v or "discontinued" in v:return "uitverkocht"
 if "instock" in v or "limitedavailability" in v:return "volgens winkel op voorraad"
 if "preorder" in v or "presale" in v:return "voorbestelling"
 if "backorder" in v:return "nabestelling"
 return "onbekend"

def classify_stock(structured,visible):
 stock=availability(structured)
 # Visible page contents can be stale or inconsistent with structured JSON-LD.
 # Never assert a verified stock count based on either source alone.
 page=re.sub(r"\s+"," ",visible).casefold()
 visible_in=bool(re.search(r"\bop voorraad\s*:\s*\d+|\bop voorraad\b",page))
 visible_out=bool(re.search(r"\buitverkocht\b|\bniet op voorraad\b",page))
 if stock=="uitverkocht" and visible_in and not visible_out:return "tegenstrijdige voorraadinformatie"
 if stock=="volgens winkel op voorraad" and visible_out and not visible_in:return "tegenstrijdige voorraadinformatie"
 return stock

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
    status=classify_stock(offers.get("availability")," ".join(parser.visible))
    return {"price":price,"titleOnPage":html.unescape(name),"currency":offers.get("priceCurrency","EUR"),
      "availability":str(offers.get("availability") or ""),"stockStatus":status,"method":"product_jsonld"}
 name=parser.meta.get("og:title","")
 price=asprice(parser.meta.get("product:price:amount"))
 if price is not None and matches(name,target["require"]):
  return {"price":price,"titleOnPage":html.unescape(name),"currency":parser.meta.get("product:price:currency","EUR"),
    "availability":"","stockStatus":"onbekend","method":"exact_title_product_meta"}
 return None

def update_history(entries,now):
 try:before=json.loads(HISTORY.read_text()).get("products",{})
 except (ValueError,OSError):before={}
 fresh=datetime.datetime.fromisoformat(now)
 cutoff=fresh-datetime.timedelta(days=90)
 current={key:[record for record in series if record.get("at") and datetime.datetime.fromisoformat(record["at"])>=cutoff]
          for key,series in before.items() if isinstance(series,list)}
 for entry in entries:
  key=entry["store"]+"|"+entry["url"]
  series=current.setdefault(key,[])
  point={"at":now,"price":entry["price"],"stock":entry["stockStatus"]}
  if not series or series[-1]["price"]!=point["price"] or series[-1]["stock"]!=point["stock"] or series[-1]["at"][:10]!=now[:10]:
   series.append(point)
  entry["priceHistoryCount"]=len(series)
  prices=[p["price"] for p in series]
  entry["ownHistoryLow90d"]=min(prices)
  entry["ownHistoryHigh90d"]=max(prices)
 HISTORY.write_text(json.dumps({"updatedAt":now,"products":current,"note":"Historical OBSERVED prices from monitored merchant; not a comparison of multiple merchants."},ensure_ascii=False,indent=2)+"\n")

def main():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 entries=[];checks=[]
 for target in TARGETS:
  outcome={"store":target["store"],"url":target["url"],"checkedAt":now}
  try:
   req=urllib.request.Request(target["url"],headers={"User-Agent":"Mozilla/5.0 (compatible; PersonalDealsObserver/1.1)"})
   with urllib.request.urlopen(req,timeout=13) as res:body=res.read(1500000).decode("utf-8","replace")
   result=find_observation(body,target)
   if result is None:outcome.update(status="not_extracted",note="Geen betrouwbaar exact productprijsveld")
   elif str(result["currency"]).upper()!="EUR":outcome.update(status="currency_mismatch")
   else:
    outcome.update(status="observed",method=result["method"],stockStatus=result["stockStatus"])
    entries.append({"title":target["title"],"store":target["store"],"url":target["url"],"category":target["category"],
      "price":result["price"],"checkedAt":now,"titleOnPage":result["titleOnPage"],
      "availabilityText":result["availability"],"stockStatus":result["stockStatus"],
      "shippingNote":target["shippingNote"],"referencePrice":None,"allInVerified":False,
      "marketComparisonVerified":False,"variantVerified":not bool(target.get("variantNote")),
      "variantNote":target.get("variantNote",""),"comparisonGroup":target.get("comparisonGroup"),
      "exactModel":target.get("exactModel"),"status":"Winkelprijs waargenomen; geen bewezen marktdeal"})
  except Exception as exc:outcome.update(status="unavailable",error=str(exc)[:150])
  checks.append(outcome)
 # Compare matching exact models only, where merchant product prices are observed.
 # This is not a comparison of shipping and not a verified 'best all-in' deal.
 groups={}
 for entry in entries:
  g=entry.get("comparisonGroup")
  if g and entry["variantVerified"] and entry["stockStatus"]=="volgens winkel op voorraad":
   groups.setdefault(g,[]).append(entry)
 for g,items in groups.items():
  if len(items)<2:continue
  lowest=min(x["price"] for x in items)
  for entry in items:
   entry["otherTrackedShopPrices"]=[{"store":other["store"],"price":other["price"],"url":other["url"]} for other in items if other["url"]!=entry["url"]]
   entry["lowestTrackedProductPrice"]=lowest
   entry["lowestOfTrackedStores"]=entry["price"]==lowest
 update_history(entries,now)
 payload={"checkedAt":now,"offers":entries,"checks":checks,
   "note":"Productprijzen rechtstreeks uit winkeldata. Bij tegenstrijdige voorraad, varianten of onbekende verzending GEEN bevestigde koopalert."}
 (ROOT/"merchant-observations.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"observed":len(entries),"checks":len(checks),"stockStatusCounts":{status:sum(e["stockStatus"]==status for e in entries) for status in sorted({x["stockStatus"] for x in entries})},
 "errors":[{"store":c["store"],"status":c["status"]} for c in checks if c["status"]!="observed"]},ensure_ascii=False))
if __name__=="__main__":main()
