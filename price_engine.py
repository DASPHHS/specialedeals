#!/usr/bin/env python3
"""Evidence-first price engine. No generic pages, no inferred delivery, no fake discounts."""
import datetime as dt
import json
import re
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from urllib.parse import urlsplit

MAX_AGE_HOURS = 36

def money(value):
    if isinstance(value, bool) or value is None: raise ValueError("missing price")
    raw = str(value).strip().replace("€","").replace(" ","")
    if not raw: raise ValueError("missing price")
    if "," in raw and "." in raw:
        raw = raw.replace(".","").replace(",",".") if raw.rfind(",") > raw.rfind(".") else raw.replace(",","")
    elif "," in raw: raw = raw.replace(",",".")
    elif raw.count(".") > 1: raw = raw.replace(".","")
    value = Decimal(raw)
    if not value.is_finite() or value <= 0: raise ValueError("invalid price")
    return value.quantize(Decimal("0.01"))

def product_type(value):
    if isinstance(value,list): return any(product_type(v) for v in value)
    return isinstance(value,str) and value.rsplit("/",1)[-1].casefold() == "product"

def offer_type(value):
    if isinstance(value,list): return any(offer_type(v) for v in value)
    return isinstance(value,str) and value.rsplit("/",1)[-1].casefold() in ("offer","aggregateoffer")

class StructuredData(HTMLParser):
    def __init__(self): super().__init__(); self.inside=False; self.scripts=[]; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=="script" and dict(attrs).get("type","").lower()=="application/ld+json":
            self.inside=True; self.parts=[]
    def handle_data(self,data):
        if self.inside: self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=="script" and self.inside:
            self.scripts.append("".join(self.parts)); self.inside=False

def walk_products(obj):
    if isinstance(obj,list):
        for item in obj: yield from walk_products(item)
    elif isinstance(obj,dict):
        if product_type(obj.get("@type")): yield obj
        for key in ("@graph","mainEntity","itemListElement"):
            if key in obj: yield from walk_products(obj[key])

def extract_product_offers(html,expected_name=None):
    """Only unambiguous single-product JSON-LD offers; never a page-wide price regex."""
    parser=StructuredData(); parser.feed(html)
    products=[]
    for script in parser.scripts:
        try: products.extend(walk_products(json.loads(script)))
        except (ValueError,TypeError): continue
    if expected_name:
        products=[p for p in products if expected_name.casefold() in str(p.get("name","")).casefold()]
    if len(products)!=1: return [],"ambiguous_or_missing_product"
    product=products[0]; offers=product.get("offers")
    if isinstance(offers,dict): offers=[offers]
    if not isinstance(offers,list): return [],"missing_offers"
    results=[]
    for offer in offers:
        if not isinstance(offer,dict) or not offer_type(offer.get("@type")): continue
        if isinstance(offer.get("offers"),list): continue # AggregateOffer is not a specific seller's price
        if str(offer.get("priceCurrency","")).upper()!="EUR": continue
        if not offer.get("price") or not offer.get("availability"): continue
        if not str(offer["availability"]).lower().endswith("instock"): continue
        try: price=money(offer["price"])
        except (ValueError,InvalidOperation): continue
        results.append({"name":product.get("name"),"sku":product.get("sku"),"gtin":product.get("gtin13") or product.get("gtin"),"priceEUR":str(price),"currency":"EUR","availability":"InStock","seller":offer.get("seller"),"source":"json-ld"})
    return results, "parsed" if results else "no_usable_offer"

def assess(observation, now=None):
    """Validate an observation. Merely parsed HTML never implies verified NL delivery."""
    now=now or dt.datetime.now(dt.timezone.utc)
    required=("productId","variantKey","seller","url","priceEUR","shippingEUR","checkedAt","currency","inStock","shipsToNL","variantMatched","sellerTrusted","shippingVerified","condition")
    missing=[k for k in required if k not in observation]
    if missing: return None,"missing:"+",".join(missing)
    u=urlsplit(observation["url"])
    if u.scheme!="https" or not u.hostname: return None,"invalid_url"
    if observation["currency"]!="EUR": return None,"currency_not_eur"
    if any(observation.get(k) is not True for k in ("inStock","shipsToNL","variantMatched","sellerTrusted","shippingVerified")): return None,"verification_incomplete"
    try:
        price=money(observation["priceEUR"]); shipping=Decimal(str(observation["shippingEUR"]))
        if not shipping.is_finite() or shipping<0: return None,"invalid_shipping"
        stamp=dt.datetime.fromisoformat(observation["checkedAt"].replace("Z","+00:00"))
        if stamp.tzinfo is None or not dt.timedelta(0)<=now-stamp<=dt.timedelta(hours=MAX_AGE_HOURS): return None,"stale"
    except (ValueError,TypeError,InvalidOperation,OverflowError): return None,"invalid_observation"
    return dict(observation,totalPriceEUR=str((price+shipping).quantize(Decimal("0.01")))),"verified_current"

def rank(observations,now=None):
    """Lowest *among checked retailers*, never a universal lowest price."""
    groups={}; rejected=[]
    for o in observations:
        record,reason=assess(o,now)
        if record is None: rejected.append({"productId":o.get("productId"),"seller":o.get("seller"),"reason":reason});continue
        key=(record["productId"],record["variantKey"],record["condition"])
        groups.setdefault(key,[]).append(record)
    results=[]
    for (product,variant,condition),rows in sorted(groups.items()):
        # Never conflate several listings from one seller with independent competitors.
        sellers={}
        for row in rows:
            name=row["seller"].casefold()
            if name not in sellers or Decimal(row["totalPriceEUR"])<Decimal(sellers[name]["totalPriceEUR"]): sellers[name]=row
        ordered=sorted(sellers.values(),key=lambda x:Decimal(x["totalPriceEUR"]))
        best=ordered[0]
        results.append({"productId":product,"variantKey":variant,"condition":condition,"lowestChecked":best,"checkedSellerCount":len(ordered),"comparisonStatus":"verified_current_price_within_checked_sellers","discountStatus":"not_established_without_valid_independent_reference"})
    return {"updatedAt":(now or dt.datetime.now(dt.timezone.utc)).isoformat(),"items":results,"rejected":rejected,"notice":"No deal inferred from prices alone. Lowest only among checked sellers."}

def main():
    import pathlib
    path=pathlib.Path("price-observations.json")
    data=json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"items":[]}
    result=rank(data.get("items",[]))
    pathlib.Path("verified-pricepeil.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Price engine: {len(result['items'])} checked products, {len(result['rejected'])} rejected observations")

if __name__=="__main__": main()
