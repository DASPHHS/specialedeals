#!/usr/bin/env python3
"""DA.nl official offers listing: read server-rendered product cards.

Only the first rendered page (normally 24 products); not the 350 products
claimed by the website. DA does not show per-product promotion end dates here,
so all records are dated observations and must expire at midnight unless refetched.
"""
from __future__ import annotations
import hashlib,re
from urllib.parse import urljoin
from urllib.request import Request,urlopen

URL="https://www.da.nl/aanbiedingen"
def euro(value):
    if value is None:return None
    v=re.sub(r"\s+","",str(value)).replace("€","").replace(",",".")
    if not re.fullmatch(r"\d{1,4}(?:\.\d{1,2})?",v):return None
    n=float(v)
    return round(n,2) if 0<n<10000 else None

def extract(html,observed):
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(html,"html.parser")
    cards=soup.select("a.ProductListItem-root")
    if len(cards)<10:
        raise ValueError("DA offer cards missing; preserving previous snapshot")
    deals=[]
    for card in cards:
        title=card.select_one("h2.ProductListItem-title")
        p=card.select_one(".ProductListPrice-root .price")
        href=card.get("href") or ""
        if not title or not p or not href.startswith("/product/"):
            continue
        name=title.get_text(" ",strip=True)
        price=euro(p.get_text("",strip=True))
        if not name or price is None:continue
        # Do not conflate the standard item price with an effective bundle price.
        raw=card.get_text(" ",strip=True)
        m=re.search(r"\b\d+\s*\+\s*\d+\s*gratis\b|\b\d+\s*%\s*korting\b|\b\d+\s*voor\s*€?\s*\d+(?:[.,]\d{2})?\b",raw,re.I)
        promo=" ".join(m.group(0).split()) if m else ""
        if not promo and re.search(r"\bkorting\b",raw,re.I):
            promo="Korting (zie winkel voor voorwaarden)"
        old_node=card.find("s")
        old=euro(old_node.get_text("",strip=True)) if old_node else None
        if old is not None and old<=price:old=None
        full_url=urljoin("https://www.da.nl",href)
        key=hashlib.sha256(full_url.encode("utf-8")).hexdigest()[:16]
        item={"id":"da:"+key,"winkel":"DA","product":name,
              "categorie":"Drogisterij","prijs":price,
              "bron":"DA.nl","url":full_url,
              "waargenomen_op":observed.date().isoformat(),
              "einddatum_onbekend":True,"startdatum_onbekend":True,
              "kwaliteit":"Officiële aanbiedingenpagina; geldigheid niet vermeld",
              "prijstype":"Artikelprijs; bundelactie kan extra voordeel geven"}
        if old is not None:
            item["van_prijs"]=old
            item["korting"]=round((old-price)/old,6)
        if promo:item["actievorm"]=promo
        deals.append(item)
    if len(deals)<10:
        raise ValueError("DA had fewer than ten well-formed visible offer cards")
    return list({d["id"]:d for d in deals}.values())

def fetch(observed):
    with urlopen(Request(URL,headers={"User-Agent":"WeekdealsBleiswijk/1.0 personal daily price check",
                                      "Accept":"text/html"}),timeout=40) as response:
        if response.status!=200:raise RuntimeError("DA HTTP "+str(response.status))
        html=response.read(2500000).decode("utf-8","replace")
    return extract(html,observed)
