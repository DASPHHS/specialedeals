#!/usr/bin/env python3
"""Product-specific external *research links* for the central wishlist.

This module uses public Bing RSS search (not price scraping, feed access or a
live seller API). Results are NOT current shop offers, prices or verified deals.
It records coverage, errors and timestamps instead of claiming all stores.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from wishlist_radar import matches, norm, valid_url

ROOT=Path(__file__).resolve().parent
LOCAL=ZoneInfo("Europe/Amsterdam")
DOMAIN_ALLOWLIST=(
 "bol.com","coolblue.nl","mediamarkt.nl","amac.nl","apple.com",
 "amazon.nl","amazon.de","alternate.nl","megekko.nl","azerty.nl",
 "proshop.nl","galaxus.nl","debijenkorf.nl","dyson.nl","hoka.com",
 "all4running.nl","hardloopshop.nl","runnersworld.nl","bever.nl",
 "bergfreunde.nl","bergfreunde.de","bergzeit.nl","bergzeit.de",
 "arcteryx.com","outlet.arcteryx.com","snowleader.nl","trekkinn.com",
 "zalando.nl","otrium.nl","rituals.com","janzen.com","douglas.nl",
 "iciparisxl.nl","notino.nl","plein.nl","deloox.nl","kaars.nl",
 "lampeberger.nl","maison-berger.com","nl.pepper.com"
)
BLOCK_PATH=("/search","/zoeken","/blog","/forum","/contact","/login","/account","/category",
            "/privacy","/vacatures","/nieuws","/reviews","/merken","/brands")
BLOCK_TITLE=("review","reviews","vergelijk alle","beste", "handleiding","uitleg","nieuws",
             "review:","recept","reparatie","onderdelen","onderdeel","vacatures")
RESEARCH_HORIZON_HOURS=48
PER_WISH_LIMIT=3


def trusted_host(url):
    if not valid_url(url):
        return False
    u=urllib.parse.urlsplit(url)
    host=(u.hostname or "").lower()
    return any(host==d or host.endswith("."+d) for d in DOMAIN_ALLOWLIST)


def usable_result(title,url,wish):
    if not title or not trusted_host(url) or len(title)<7:
        return False
    low=norm(title)
    if any(re.search(r"\b"+re.escape(norm(term))+r"\b",low) for term in BLOCK_TITLE):
        return False
    path=urllib.parse.urlsplit(url).path.lower()
    if any(s in path for s in BLOCK_PATH):
        return False
    return matches(title,wish)


def terms(wish):
    """An exact product family with manufacturer, never model number alone."""
    patterns=wish.get("matchAny") or wish.get("keywords") or []
    good=[str(p).strip() for p in patterns if len(norm(p))>=7 and len(norm(p).split())>=2]
    if not good:
        good=[str(wish.get("name","")).split(" / ")[0]]
    # Prefer specificity; leave brand in the expression.
    return max(good,key=lambda x:len(norm(x).split()))[:80]


def search_one(wish, fetch=None):
    if fetch is None:
        def fetch(url):
            request=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (compatible; SpecialsWishlistRadar/1.0)",
                "Accept":"application/rss+xml,application/xml;q=0.9"
            })
            with urllib.request.urlopen(request,timeout=16) as resp:
                return resp.read(800000)
    phrase=terms(wish)
    query='"'+phrase.replace('"','')+'" aanbieding Nederland webshop'
    url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":query,"format":"rss"})
    root=ET.fromstring(fetch(url))
    found=[]
    seen=set()
    for r in root.findall(".//item"):
        title=(r.findtext("title") or "").strip()
        link=(r.findtext("link") or "").strip()
        if not usable_result(title,link,wish):
            continue
        parsed=urllib.parse.urlsplit(link)
        clean=urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,parsed.path,"",""))
        if clean in seen:
            continue
        seen.add(clean)
        found.append({"title":title[:180],"url":clean,"domain":parsed.hostname,
            "status":"Externe zoekvondst — prijs, maat, voorraad en actualiteit niet gecontroleerd"})
        if len(found)>=PER_WISH_LIMIT:
            break
    return found


def selected_wishes(wishes,now):
    # Deterministic day+time rotation (the action runs twice each morning).
    items=[w for w in wishes if w.get("id") and w.get("matchAny")]
    if not items:return []
    slot=now.date().toordinal()*2+(1 if now.hour>=7 else 0)
    count=min(12,len(items))
    start=(slot*count)%len(items)
    return (items+items)[start:start+count]


def build(wishes,prev,now,lookup=search_one,sleep=lambda _:None):
    previous={x["wishId"]:x for x in (prev.get("results") or [])
              if isinstance(x,dict) and x.get("wishId")}
    by_id={w["id"]:w for w in wishes if w.get("id")}
    chosen=selected_wishes(wishes,now)
    errors=[]
    for i,wish in enumerate(chosen):
        try:
            found=lookup(wish)
            previous[wish["id"]]={"wishId":wish["id"],"searchedAt":now.isoformat(),
                "query":terms(wish),"leads":found[:PER_WISH_LIMIT],
                "status":"ok","searchSource":"Bing RSS webzoekresultaten"}
        except (OSError,ValueError,ET.ParseError) as err:
            errors.append({"wishId":wish["id"],"reason":str(err)[:100]})
            previous[wish["id"]]={"wishId":wish["id"],"searchedAt":now.isoformat(),
                "query":terms(wish),"leads":[],"status":"source_error"}
        if i<len(chosen)-1:sleep(1.6)
    output=[]
    for id,w in by_id.items():
        row=previous.get(id)
        if not row:
            output.append({"wishId":id,"status":"not_scanned","leads":[],"searchedAt":None})
            continue
        at=row.get("searchedAt")
        try:
            parsed=datetime.fromisoformat(at)
            fresh=parsed.tzinfo is not None and timedelta(0)<=now-parsed.astimezone(now.tzinfo)<=timedelta(hours=RESEARCH_HORIZON_HOURS)
        except (TypeError,ValueError):
            fresh=False
        if not fresh:
            row={**row,"leads":[],"status":"stale"}
        output.append(row)
    return {"schemaVersion":1,"updatedAt":now.isoformat(),
      "scope":"Selective Bing RSS research, not an ecommerce API or live price verification",
      "searchedThisRun":len(chosen),"errors":errors,
      "results":output,
      "disclaimer":"A search hit is not proof of in-stock products, discounted price, shipment to NL or current listing."}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--online",action="store_true")
    args=parser.parse_args()
    now=datetime.now(LOCAL)
    wishes=json.loads((ROOT/"wishlist.json").read_text(encoding="utf-8")).get("items",[])
    path=ROOT/"verlanglijst/zoekvondsten.json"
    try:prev=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):prev={}
    if args.online:
        data=build(wishes,prev,now,lookup=search_one,sleep=time.sleep)
    else:
        data=build(wishes,prev,now,lookup=lambda w: [],sleep=lambda _:None)
    if not args.online:
        print("Offline validation only: no new research file generated")
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Product research: {data['searchedThisRun']} wishes, "
          f"{sum(len(x['leads']) for x in data['results'])} valid unverified source leads, "
          f"{len(data['errors'])} errors")


if __name__=="__main__":main()
