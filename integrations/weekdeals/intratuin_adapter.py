#!/usr/bin/env python3
"""Read a small sample of official Intratuin product specials, without scraping blockers.

Only prices explicitly rendered in BOTH "special-price" and "old-price"
are published. No claim of full catalogue coverage or local inventory.
"""
from __future__ import annotations

import hashlib
import re
import time
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import Request,urlopen

from bs4 import BeautifulSoup

ROOT="https://www.intratuin.nl/aanbiedingen"
PAGES=3

def euro(s):
    if not s:return None
    t=str(s).strip().replace("€","").replace("\u00a0","").replace(" ","")
    if t.endswith(".-"):t=t[:-2]
    if not re.fullmatch(r"\d{1,5}(?:[.,]\d{1,2})?",t):
        return None
    # Prices over 1000 appear as 1299.- or 1299,99, not with thousands dots
    v=float(t.replace(",","."))
    return round(v,2) if 0<v<100000 else None

def extract(html,observed):
    soup=BeautifulSoup(html,"html.parser")
    cards=soup.select("li.product-item")
    if len(cards)<10:
        raise ValueError("Intratuin special-offer listing has no usable grid")
    records={}
    for card in cards:
        link=card.select_one("a.product-item-link")
        special=card.select_one(".special-price .price")
        regular=card.select_one(".old-price .price")
        if not (link and special and regular):
            continue
        name=link.get_text(" ",strip=True)
        href=link.get("href") or ""
        parsed=urlparse(href)
        if parsed.scheme!="https" or parsed.hostname not in ("www.intratuin.nl","intratuin.nl"):
            continue
        price=euro(special.get_text(" ",strip=True))
        old=euro(regular.get_text(" ",strip=True))
        if not name or len(name)<4 or price is None or old is None or not price<old:
            continue
        key=hashlib.sha256(href.split("?")[0].encode()).hexdigest()[:16]
        records[key]={
            "id":"intratuin:"+key,
            "winkel":"Intratuin","product":name,
            "categorie":"Tuin & wonen",
            "prijs":price,"van_prijs":old,
            "korting":round((old-price)/old,6),
            "bron":"Intratuin.nl","url":href.split("?")[0],
            "waargenomen_op":observed.date().isoformat(),
            "startdatum_onbekend":True,
            "einddatum_onbekend":True,
            "kwaliteit":"Officiële aanbiedingspagina; winkelvoorraad en einddatum niet bevestigd",
            "prijstype":"Speciale actieprijs volgens Intratuin.nl"
        }
    return list(records.values())

def fetch(observed,pages=PAGES):
    if not 1<=pages<=5:
        raise ValueError("Bound pages to 1..5; limit server traffic")
    rows={}
    for page in range(1,pages+1):
        if page>1:time.sleep(1.6)
        url=ROOT+(f"?p={page}" if page>1 else "")
        with urlopen(Request(url,headers={
            "User-Agent":"WeekdealsBleiswijk/1.0 (personal daily offers; limited pages)",
            "Accept":"text/html"}),timeout=40) as resp:
            if resp.status!=200:raise RuntimeError(f"Intratuin HTTP {resp.status}")
            html=resp.read(3500000).decode("utf-8","replace")
        records=extract(html,observed)
        if page==1 and len(records)<8:
            raise ValueError("Intratuin first page lacks eight price-verified discounts")
        for row in records:
            rows[row["id"]]=row
    if len(rows)<10:
        raise ValueError("Intratuin complete sample has fewer than ten verified offers")
    return list(rows.values())
