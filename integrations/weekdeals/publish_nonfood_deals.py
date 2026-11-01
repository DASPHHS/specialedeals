#!/usr/bin/env python3
"""One daily, polite, product-level extract of FeedMyCart's public NL chain pages.

Only the publicly displayed selection (max ~40 per chain), not complete folders.
Extracts facts: product, displayed price, old price, promotion and end date.
Never guesses unshown prices or original promotion start dates.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

BASE="https://feedmycart.nl/en/countries/netherlands/{}/"
CHAINS={"kruidvat":"Kruidvat","etos":"Etos","trekpleister":"Trekpleister",
        "action":"Action","wibra":"Wibra"}
OUT=Path(__file__).resolve().parents[2]/"weekdeals"/"nonfood.json"
LOG=logging.getLogger(__name__)

class DealParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.current=None
        self.items=[]
        self.category=""
        self.heading=None
        self.scripts=[]
        self.script=None

    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        classes=a.get("class","").split()
        self.stack.append((tag,classes))
        if tag=="script" and a.get("type","").lower()=="application/ld+json":
            self.script=[]
        if tag=="h2" and self.current is None:
            self.heading=[]
        if tag=="li" and "deal" in classes:
            self.current={"name":"","promotion":"","old":"","new":"",
                          "category":self.category}

    def handle_data(self,data):
        if self.script is not None:
            self.script.append(data)
        if self.heading is not None:
            self.heading.append(data)
        if self.current is None:
            return
        classes={c for _,cs in self.stack for c in cs}
        if "deal__name" in classes:
            self.current["name"]+=data
        elif "deal__tags" in classes:
            self.current["promotion"]+=data
        elif "deal__price" in classes:
            if any(tag=="s" for tag,_ in self.stack):
                self.current["old"]+=data
            elif any(tag=="b" for tag,_ in self.stack):
                self.current["new"]+=data

    def handle_endtag(self,tag):
        if tag=="script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script=None
        if tag=="h2" and self.heading is not None:
            self.category=" ".join("".join(self.heading).split())
            self.heading=None
        if tag=="li" and self.current is not None and self.stack and self.stack[-1][0]=="li":
            self.items.append(self.current)
            self.current=None
        if self.stack:
            for i in range(len(self.stack)-1,-1,-1):
                if self.stack[i][0]==tag:
                    del self.stack[i:]
                    break

def money(raw):
    if raw is None:return None
    s=re.sub(r"[^0-9,.]","",str(raw))
    if not s:return None
    if "," in s and "." in s:
        s=s.replace(".","").replace(",",".")
    elif "," in s:s=s.replace(",",".")
    try:n=float(s)
    except ValueError:return None
    if not 0<n<10000:return None
    return round(n,2)

def jsonld_products(scripts):
    rows=[]
    def walk(node):
        if isinstance(node,list):
            for e in node:walk(e)
        elif isinstance(node,dict):
            if isinstance(node.get("itemListElement"),list):
                for entry in node["itemListElement"]:
                    if not isinstance(entry,dict):continue
                    obj=entry.get("item",entry)
                    if isinstance(obj,dict) and str(obj.get("@type","")).lower()=="product":
                        rows.append(obj)
            for k,v in node.items():
                if k!="itemListElement" and isinstance(v,(dict,list)):
                    walk(v)
    for raw in scripts:
        try:walk(json.loads(raw))
        except (TypeError,ValueError,json.JSONDecodeError):
            pass
    return rows

def parse(html,chain,observed):
    parser=DealParser()
    parser.feed(html)
    ld=jsonld_products(parser.scripts)
    if not ld or not parser.items:
        raise ValueError(f"{chain}: no JSON-LD products or visible deal cards")
    visible={}
    for item in parser.items:
        name=" ".join(item["name"].split())
        if name:visible.setdefault(name.casefold(),item)
    data=[]
    rejected=0
    for item in ld:
        name=" ".join(str(item.get("name") or "").split())
        card=visible.get(name.casefold())
        offer=item.get("offers") or {}
        if not isinstance(offer,dict) or not card or len(name)<3:
            rejected+=1
            continue
        end=str(offer.get("priceValidUntil") or "")[:10]
        try:
            if datetime.strptime(end,"%Y-%m-%d").date()<observed.date():continue
        except ValueError:
            rejected+=1
            continue
        price=money(offer.get("lowPrice"))
        shown=money(card["new"])
        if price is None or shown is None or abs(price-shown)>0.011:
            rejected+=1
            continue
        old=money(card["old"])
        if old is not None and old<=price:old=None
        promo=" ".join(card["promotion"].split())
        key=hashlib.sha256(f"{chain}|{name.casefold()}|{price}|{end}".encode()).hexdigest()[:16]
        entry={"id":f"feedmycart:{chain}:{key}",
               "winkel":CHAINS[chain],"product":name,
               "categorie":card["category"] or "Overig",
               "prijs":price,"tot":end,
               "waargenomen_op":observed.date().isoformat(),
               "startdatum_onbekend":True,
               "bron":"FeedMyCart",
               "url":BASE.format(chain),
               "kwaliteit":"Openbare selectie; lokale voorraad niet bevestigd"}
        if old is not None:
            entry["van_prijs"]=old
            entry["korting"]=round((old-price)/old,6)
        if promo:entry["actievorm"]=promo[:160]
        data.append(entry)
    # Public chain pages also contain visible offer cards absent from JSON-LD.
    # Read only facts visibly printed on the card; the page-wide date is not
    # claimed to be an individually verified promotion end date.
    page_end=None
    month_match=re.search(
        r"Valid through\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(\d{1,2})\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)",
        html,re.I)
    if month_match:
        try:
            guessed=datetime.strptime(
                month_match.group(1)+" "+month_match.group(2)+" "+str(observed.year),"%d %B %Y").date()
            if guessed<observed.date() and (observed.date()-guessed).days>180:
                guessed=guessed.replace(year=observed.year+1)
            if observed.date()<=guessed and (guessed-observed.date()).days<=45:
                page_end=guessed.isoformat()
        except ValueError:
            pass
    ld_names={str(obj.get("name") or "").strip().casefold() for obj in ld}
    for normalized,card in visible.items():
        if normalized in ld_names:
            continue  # Never downgrade a JSON-LD price contradiction to unvalidated HTML.
        if not page_end:
            continue
        name=" ".join(card["name"].split())
        price=money(card["new"])
        promo=" ".join(card["promotion"].split())
        if len(name)<3 or (price is None and not promo):
            continue
        old=money(card["old"])
        if price is not None and old is not None and old<=price:
            old=None
        key=hashlib.sha256(
            f"{chain}|{name.casefold()}|{price}|{page_end}|html".encode()).hexdigest()[:16]
        extra={"id":f"feedmycart:{chain}:{key}","winkel":CHAINS[chain],
               "product":name,"categorie":card["category"] or "Overig",
               "tot":page_end,"waargenomen_op":observed.date().isoformat(),
               "startdatum_onbekend":True,"einddatum_bron":"Paginabreed; niet per artikel",
               "bron":"FeedMyCart","url":BASE.format(chain),
               "kwaliteit":"Openbare productkaart; einddatum op paginaniveau, voorraad niet bevestigd"}
        if price is not None:extra["prijs"]=price
        if price is not None and old is not None:
            extra["van_prijs"]=old
            extra["korting"]=round((old-price)/old,6)
        if promo:extra["actievorm"]=promo[:160]
        data.append(extra)
    unique={x["id"]:x for x in data}
    LOG.info("%s: %d visible, %d JSON-LD, %d valid, %d skipped",
             chain,len(parser.items),len(ld),len(unique),rejected)
    return list(unique.values())

def fetch(chain):
    url=BASE.format(chain)
    req=Request(url,headers={
        "Accept":"text/html",
        "User-Agent":"WeekdealsBleiswijk/1.0 (public offer selection; daily only)"
    })
    with urlopen(req,timeout=35) as r:
        html=r.read(400000).decode("utf-8","replace")
        if r.status!=200 or not html:
            raise RuntimeError(f"{chain}: HTTP {r.status} or blank HTML")
    return html

def main():
    logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
    now=datetime.now(ZoneInfo("Europe/Amsterdam"))
    all_rows=[]
    failures={}
    counts={}
    for i,chain in enumerate(CHAINS):
        if i:time.sleep(2)
        try:
            rows=parse(fetch(chain),chain,now)
            if not rows:
                raise RuntimeError("No valid non-expired offers in public selection")
            counts[CHAINS[chain]]=len(rows)
            all_rows+=rows
        except Exception as err:
            LOG.warning("Source %s unavailable: %s",chain,err)
            failures[CHAINS[chain]]=str(err)[:150]
    if len(all_rows)<15 or len(counts)<2:
        raise RuntimeError("Insufficient coverage; keep previous JSON untouched")
    output={"schema_version":1,
            "updated_at":now.isoformat(timespec="seconds"),
            "source":"FeedMyCart",
            "source_url":"https://feedmycart.nl/en/countries/netherlands/",
            "scope":"Public top-selection of nonfood chains, not complete flyers or local stock",
            "complete_folders":False,
            "counts":counts,"failures":failures,"deals":all_rows}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(output,ensure_ascii=False,separators=(",",":"),
                              allow_nan=False),encoding="utf-8")
    tmp.replace(OUT)
    print(f"SUCCESS {len(all_rows)} nonfood product deals in {len(counts)} chains:",
          counts,"failures:",failures)

if __name__=="__main__":
    main()
