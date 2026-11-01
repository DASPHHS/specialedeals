#!/usr/bin/env python3
"""Read permitted Prijspuls public catalogue as generic market price levels.

This is *not* a live individual-SKU retailer feed, offer or verified discount.
Source explicitly permits using the figures with attribution + measurement time:
https://prijspuls.nl/pers . No claims about checkout/shipping or 500+ stores.
"""
from __future__ import annotations
import json,re,urllib.request
from datetime import datetime,timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

URL="https://prijspuls.nl/api/prijzen"
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"topdeals"/"prijspeil.json"
TZ=ZoneInfo("Europe/Amsterdam")
GROUPS=("supermarkt","tuin","bouwmarkt","drogisterij","elektronica","sport","huis","overig")
LABELS={"supermarkt":"Supermarkt & boodschappen","tuin":"Tuin & buiten",
        "bouwmarkt":"Bouwmarkt & klussen","drogisterij":"Drogisterij & verzorging",
        "elektronica":"Elektronica & gadgets","sport":"Sport & outdoor",
        "huis":"Wonen & huishouden","overig":"Overige categorieën"}
RULES={
 "bouwmarkt":r"\b(boormachine|schuurmachine|betonmolen|schroevendraaier|zaagmachine|bouwstofzuiger|verf|tegel|tegels|gereedschap|klopboor|hout|kitpistool|isolatie|dopsleutel|accuboormachine|drukspuit)\b",
 "tuin":r"\b(tuin|gras|grasmaaier|heggenschaar|bladblazer|planten|potgrond|bloembollen|barbecue|bbq|houtskool|hogedrukreiniger|snoeischaar|kettingzaag)\b",
 "elektronica":r"\b(ssd|videokaart|tv|televisie|oled|iphone|ipad|macbook|airpods|laptop|computer|smartphone|router|usb4|thunderbolt|speaker|grafische kaart|monitor|nas)\b",
 "sport":r"\b(hardloopschoenen|wandelschoenen|sneakers|kettlebell|hometrainer|halterbank|loopband|roeitrainer|fitness|sport|padel|schoenen|yogamat)\b",
 "drogisterij":r"\b(parfum|huidcr[eè]me|beauty|vitamines|vitamine|shampoo|tandpasta|huidverzorging|cosmetica|geur)\b",
 "huis":r"\b(matras|dekbed|kussen|stoel|bank|meubels|gordijn|handdoek|stofzuiger|wasmachine|wasdroger|vaatwasser|koelkast|airfryer|magnetron|verlichting|lamp)\b",
 "supermarkt":r"\b(koffie|boodschappen|thee|pindakaas|frisdrank|bier|groente|fruit|kaas|pizza|supermarkt)\b",
}
NOISE=re.compile(r"\b(wijn|bier|whisky|vodka|tabak|sigaret|vape|roulette|casino|gokken)\b",re.I)


def iso(value):
 try:
  t=datetime.fromisoformat(str(value).replace("Z","+00:00"))
  return t if t.tzinfo else None
 except (TypeError,ValueError):return None


def amount(value):
 if isinstance(value,bool) or not isinstance(value,(int,float)):return None
 return round(value,2) if 1<=value<=100000 else None


def classify(term):
 t=str(term or "").casefold()
 for group,pat in RULES.items():
  if re.search(pat,t):return group
 return "overig"


def record(raw,now):
 if not isinstance(raw,dict):return None
 term=str(raw.get("zoekterm") or "").strip()
 url=str(raw.get("url") or "").strip()
 host=urlsplit(url)
 if not term or len(term)>115 or NOISE.search(term):return None
 if host.scheme!="https" or host.hostname not in ("prijspuls.nl","www.prijspuls.nl") or not host.path.startswith("/vergelijk/"):
  return None
 low=amount(raw.get("laagste_eur"))
 avg=amount(raw.get("gemiddelde_eur"))
 measured=iso(raw.get("meetmoment") or raw.get("laagste_gemeten"))
 if low is None or avg is None or measured is None:return None
 age=now-measured.astimezone(now.tzinfo)
 if not timedelta(0)<=age<=timedelta(hours=48):return None
 if avg<low*.75:return None
 try:
  shops=int(raw.get("webshops") or 0)
  offers=int(raw.get("aanbiedingen") or 0)
 except (TypeError,ValueError):return None
 if shops<1 or offers<1:return None
 # Per-term comparison, not independently verified price drop.
 diff=round(max(0,(avg-low)/avg)*100,1) if avg>low else 0
 return {"term":term,"url":url,"group":classify(term),"lowestEUR":low,
   "averageEUR":avg,"shops":shops,"offers":offers,
   "measuredAt":measured.isoformat(),"spreadPercent":diff,
   "condition":str(raw.get("laagste_conditie") or "onbekend")[:60],
   "type":"generic_market_price_level_not_a_deal",
   "verifiedProductMatch":False,"verifiedDiscount":False,"deliveredPriceVerified":False}


def build(doc,now):
 if not isinstance(doc,dict) or doc.get("bron")!="prijspuls.nl" or not isinstance(doc.get("producten"),list):
  raise ValueError("Unexpected Prijspuls API response")
 if len(doc["producten"])<50:
  raise ValueError("Catalog much smaller than expected; refusing to publish")
 source_date=iso(doc.get("gegenereerd"))
 if not source_date or not timedelta(0)<=now-source_date.astimezone(now.tzinfo)<=timedelta(hours=48):
  raise ValueError("Prijspuls source too old")
 rows=[]
 seen=set()
 for entry in doc["producten"]:
  item=record(entry,now)
  if item and item["term"].casefold() not in seen:
   seen.add(item["term"].casefold());rows.append(item)
 if len(rows)<15:raise ValueError("No usable market comparisons")
 groups={}
 for group in GROUPS:
  pool=[r for r in rows if r["group"]==group]
  # Price spread vs market average is *not* a measured personal saving.
  pool.sort(key=lambda r:(-min(r["shops"],20),-r["spreadPercent"],r["term"]))
  groups[group]={"label":LABELS[group],"available":len(pool),"top10":pool[:10]}
 return {"schemaVersion":1,"generatedAt":now.isoformat(),
    "source":"prijspuls.nl","sourceUrl":"https://prijspuls.nl/",
    "licenseUrl":"https://prijspuls.nl/pers","sourceGeneratedAt":source_date.isoformat(),
    "catalogueCount":len(doc["producten"]),"usablePriceLevels":len(rows),
    "type":"generic_product_category_market_comparisons_not_retail_offers",
    "caveat":"Generic search-term market price levels, not exact wishlist models, discounts, checkout or shipping.",
    "groups":groups}


def main():
 now=datetime.now(TZ)
 req=urllib.request.Request(URL,headers={
   "Accept":"application/json",
   "User-Agent":"SpecialeDealsPricePeil/1.0 (+https://github.com/DASPHHS/specialedeals)"})
 with urllib.request.urlopen(req,timeout=20) as response:
  raw=response.read(1200000)
 doc=json.loads(raw)
 data=build(doc,now)
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Published Prijspuls generic comparison terms:",data["usablePriceLevels"],
       "category counts:",{k:v["available"] for k,v in data["groups"].items()})


if __name__=="__main__":main()
