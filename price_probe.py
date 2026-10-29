#!/usr/bin/env python3
"""Conservative product-page probe. Discovery is NOT checkout verification."""
import datetime as dt
import json
import pathlib
import urllib.request
from urllib.parse import urlsplit
from decimal import Decimal
from price_engine import extract_product_offers

INPUT=pathlib.Path("product-targets.json")
OUTPUT=pathlib.Path("price-probes.json")

def probe(target, fetcher=None):
    url=target.get("url","")
    parts=urlsplit(url)
    if parts.scheme!="https" or not parts.hostname:
        return {"targetId":target.get("id"),"status":"invalid_url"}
    fetcher=fetcher or fetch
    try:
        if target.get("adapter")=="shopify":
            return probe_shopify(target,fetcher)
        html=fetcher(url)
        offers,reason=extract_product_offers(html,target.get("expectedName"))
        expected_sku=target.get("sku")
        expected_gtin=target.get("gtin")
        if not expected_sku and not expected_gtin:
            return {"targetId":target.get("id"),"status":"identity_not_configured"}
        matched=[o for o in offers if (expected_sku and str(o.get("sku"))==str(expected_sku)) or
                 (expected_gtin and str(o.get("gtin"))==str(expected_gtin))]
        if len(matched)!=1:
            return {"targetId":target.get("id"),"status":"identity_not_matched","parserStatus":reason}
        o=matched[0]
        return {"targetId":target.get("id"),"status":"product_price_candidate",
                "seller":target.get("seller"),"url":url,"productId":target.get("productId"),
                "variantKey":target.get("variantKey"),"sku":o.get("sku"),"gtin":o.get("gtin"),
                "priceEUR":o["priceEUR"],"inStock":True,
                "shippingVerified":False,"shipsToNL":None,
                "note":"No verified shipping, checkout, seller trust, warranty or exact variant beyond SKU/GTIN; NOT a verified price."}
    except Exception as exc:
        return {"targetId":target.get("id"),"status":"source_error","errorType":type(exc).__name__}

def probe_shopify(target, fetcher):
    """Shopify public product JSON: variant-specific item price, never checkout verified."""
    url=target["url"]
    try:
        data=json.loads(fetcher(url.rstrip("/")+".js"))
        expected=str(target.get("variantTitle","")).casefold().strip()
        if not expected: return {"targetId":target.get("id"),"status":"identity_not_configured"}
        matches=[v for v in data.get("variants",[]) if str(v.get("public_title") or v.get("title") or "").casefold().strip()==expected]
        if len(matches)!=1: return {"targetId":target.get("id"),"status":"identity_not_matched"}
        v=matches[0]
        if v.get("available") is not True: return {"targetId":target.get("id"),"status":"out_of_stock"}
        price=Decimal(str(v["price"]))/100
        if not price.is_finite() or price<=0: return {"targetId":target.get("id"),"status":"invalid_price"}
        return {"targetId":target["id"],"status":"product_price_candidate","seller":target["seller"],
                "url":url,"productId":target["productId"],"variantKey":target["variantKey"],
                "sku":v.get("sku"),"shopifyVariantId":str(v["id"]),"priceEUR":str(price.quantize(Decimal("0.01"))),
                "inStock":True,"shippingVerified":False,"shipsToNL":None,
                "note":"Exact Shopify variant title; shipping, checkout, seller trust and NL total NOT verified."}
    except Exception as exc:
        return {"targetId":target.get("id"),"status":"source_error","errorType":type(exc).__name__}

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"SpecialeDeals/1.0 (+public research; no bot bypass)","Accept-Language":"nl-NL,nl;q=0.9"})
    with urllib.request.urlopen(req,timeout=15) as response:
        if response.status!=200: raise ValueError("non-200")
        return response.read(1500000).decode("utf-8","replace")

def main():
    targets=json.loads(INPUT.read_text(encoding="utf-8")).get("targets",[])
    result={"updatedAt":dt.datetime.now(dt.timezone.utc).isoformat(),
            "notice":"Product-page leads only; never counted as verified live NL delivered prices.",
            "items":[probe(t) for t in targets[:40]]}
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Price probes:",len(result["items"]),"targets")

if __name__=="__main__": main()
