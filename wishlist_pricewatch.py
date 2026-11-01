#!/usr/bin/env python3
"""Low-volume, read-only Tweakers Pricewatch discovery for specific wishlist items.

The suggest endpoint is public but undocumented: integration may cease working.
A search result is a PRICE INDICATION, never an audited retailer checkout or
verified discount. Never bypass login/consent or anti-bot protection.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timedelta
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

from wishlist_radar import matches, norm, valid_url

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"verlanglijst"/"prijsvergelijkers.json"
ZONE=ZoneInfo("Europe/Amsterdam")
BASE="https://tweakers.net"
# Product-family-specific comparisons only; excludes services, perfumery and
# generic outdoor apparel that Tweakers does not routinely cover.
QUERIES={
 "apple-airpods-pro":"Apple AirPods Pro",
 "apple-airpods":"Apple AirPods 4 ANC",
 "apple-macbook":"Apple MacBook Air",
 "apple-imac":"Apple iMac",
 "apple-watch-ultra":"Apple Watch Ultra",
 "usb-hubs-premium":"Thunderbolt 4 dock",
 "hightech-gadgets":"e-ink tablet",
 "dyson-handstofzuiger":"Dyson V12",
 "dyson-airwrap":"Dyson Airwrap",
}
MAX_REQUESTS=5
FRESH_HOURS=8
MAX_RESULTS=4


def euro(value):
    """Only parse explicit euro quotes; not discounts or unknown currencies."""
    if isinstance(value,(float,int)) and not isinstance(value,bool):
        return round(float(value),2) if 1<=float(value)<100000 else None
    raw=unescape(re.sub(r"<[^>]*>"," ",str(value or "")))
    match=re.search(r"€\s*([\d.,\s]+)",raw)
    if not match:return None
    raw=match.group(1).replace("\xa0","").replace(" ","").strip(".,")
    try:
        if "," in raw and "." in raw:
            price=float(raw.replace(".","").replace(",","."))
        elif "," in raw:
            price=float(raw.replace(",","."))
        elif raw.count(".")==1 and len(raw.split(".")[-1])==3:
            price=float(raw.replace(".",""))
        else:
            price=float(raw)
        return round(price,2) if 1<=price<100000 else None
    except ValueError:return None


def on_tweakers(url):
    if not isinstance(url,str):return None
    full=urllib.parse.urljoin(BASE,url)
    if not valid_url(full):return None
    u=urllib.parse.urlsplit(full)
    if u.hostname not in ("tweakers.net","www.tweakers.net"):return None
    m=re.match(r"^/pricewatch/(\d{4,12})(?:/|$)",u.path)
    if not m:return None
    return urllib.parse.urlunsplit(("https",u.hostname,u.path,"","")),m.group(1)


def valid_model(title,wish):
    if not matches(title,wish):return False
    text=norm(title)
    if wish["id"] in ("apple-airpods","apple-airpods-pro"):
        if re.search(r"\b(hoesje|cover|accessoire|beschermhoes)\b|\bairpods(?: pro)? case\b",text):
            return False
    wid=wish["id"]
    if wid=="apple-airpods":
        if re.search(r"\b(zonder|without|geen|no)\s+(?:actieve?\s+)?(?:noise\s+)?(?:cancell?ing|ruisonderdrukking|anc)\b",text):return False
        return bool(re.search(r"\banc\b|noise cancellation|noise cancelling|ruisonderdrukking",text))
    if wid=="dyson-handstofzuiger":
        return bool(re.search(r"\b(v8|v10|v11|v12|v15|gen5|digital slim|omni glide)\b",text))
    if wid=="apple-macbook":return "macbook" in text
    if wid=="apple-imac":return "imac" in text
    if wid=="dyson-airwrap":return "airwrap" in text and not any(x in text for x in ("accessoire","opzetstuk","opbergcase"))
    return True


def parse_results(payload,wish,now):
    if not isinstance(payload,dict):raise ValueError("Pricewatch response is not a JSON object")
    if not isinstance(payload.get("articles",[]),list) or not isinstance(payload.get("entities",[]),list):
        raise ValueError("Unexpected Pricewatch JSON structure")
    results=[];seen=set()
    for bucket in ("entities","articles"):
        for item in payload.get(bucket,[])[:25]:
            if not isinstance(item,dict):continue
            if bucket=="entities" and item.get("type")!="product":continue
            link=on_tweakers(item.get("link"))
            name=str(item.get("name") or "").strip()
            if not link or link[1] in seen or not valid_model(name,wish):continue
            seen.add(link[1])
            quote=euro(item.get("minPrice")) if bucket=="entities" else None
            results.append({
              "title":name[:180],"url":link[0],"domain":"tweakers.net",
              "provider":"Tweakers Pricewatch","productId":link[1],
              "indicativePriceEUR":quote,
              "observedAt":now.isoformat(),"priceKind":"Pricewatch minimum price indication; shipping, seller, variant and stock not checked",
              "stockVerified":False,"shippingVerified":False,"verifiedDiscount":False,
              "status":"Product gevonden in Pricewatch; vergelijk winkelprijzen en exacte configuratie"
            })
            if len(results)>=MAX_RESULTS:return results
    return results


def search(wish,now,fetch=None):
    query=QUERIES[wish["id"]]
    url=BASE+"/ajax/zoeken/pricewatch/?"+urllib.parse.urlencode({"keyword":query})
    if fetch is None:
        def fetch(location):
            request=urllib.request.Request(location,headers={
                "User-Agent":"SpecialeDealsPriceResearch/1.0 (+https://github.com/DASPHHS/specialedeals)",
                "Accept":"application/json"})
            with urllib.request.urlopen(request,timeout=16) as response:
                if int(response.headers.get("content-length") or 0)>400000:
                    raise ValueError("Search response too big")
                return response.read(400001)
    raw=fetch(url)
    if isinstance(raw,bytes) and len(raw)>400000:raise ValueError("Response exceeds size limit")
    data=json.loads(raw) if isinstance(raw,(bytes,str)) else raw
    return parse_results(data,wish,now)


def choose(wishes,now):
    eligible=[w for w in wishes if w.get("id") in QUERIES]
    if not eligible:return []
    # Rotate deterministically, covering nine targets within two hours.
    idx=(now.date().toordinal()*24+now.hour)*MAX_REQUESTS%len(eligible)
    return (eligible+eligible)[idx:idx+min(MAX_REQUESTS,len(eligible))]


def build(wishes,previous,now,lookup=search,sleep=lambda _:None):
    old={r["wishId"]:r for r in previous.get("results",[])
         if isinstance(r,dict) and r.get("wishId") in QUERIES}
    selected=choose(wishes,now);errors=[]
    for i,w in enumerate(selected):
        wid=w["id"]
        try:
            found=lookup(w,now)
            old[wid]={"wishId":wid,"query":QUERIES[wid],"searchedAt":now.isoformat(),
                 "status":"ok","offers":found[:MAX_RESULTS]}
        except (OSError,ValueError,KeyError,urllib.error.HTTPError) as e:
            old[wid]={"wishId":wid,"query":QUERIES[wid],"searchedAt":now.isoformat(),
                 "status":"source_error","offers":[]}
            errors.append({"wishId":wid,"reason":str(e)[:120]})
        if i<len(selected)-1:sleep(1.3)
    output=[]
    for wid in QUERIES:
        row=old.get(wid)
        if row is None:
            output.append({"wishId":wid,"searchedAt":None,"status":"not_scanned","offers":[]})
            continue
        try:
            at=datetime.fromisoformat(str(row.get("searchedAt") or ""))
            fresh=at.tzinfo and timedelta(0)<=now-at.astimezone(now.tzinfo)<=timedelta(hours=FRESH_HOURS)
        except ValueError:fresh=False
        if not fresh:row={**row,"status":"stale","offers":[]}
        output.append(row)
    return {"schemaVersion":1,"updatedAt":now.isoformat(),
            "provider":"Tweakers Pricewatch (undocumented public suggest endpoint)",
            "scope":"Search suggestions; no direct retailer price/stock or checkout validation",
            "searchedThisRun":len(selected),"errorCount":len(errors),"errors":errors,
            "results":output,"comparisonCount":sum(len(r["offers"]) for r in output),
            "policy":"All prices are Pricewatch indications; no verified discount or delivered NL total."}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--online",action="store_true")
    args=parser.parse_args()
    now=datetime.now(ZONE)
    wishlist=json.loads((ROOT/"wishlist.json").read_text(encoding="utf-8"))
    try:previous=json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError,ValueError):previous={}
    data=build(wishlist["items"],previous,now,lookup=search if args.online else lambda w,n:[])
    if not args.online:
        print("Offline sanity run completed; no file changed")
        return
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Pricewatch research:",len(choose(wishlist["items"],now)),"queries,",
          data["comparisonCount"],"current suggestions,",data["errorCount"],"errors")
    for r in data["results"]:
        if r["searchedAt"]==now.isoformat():
            print(r["wishId"],r["status"],len(r["offers"]))


if __name__=="__main__":
    main()
