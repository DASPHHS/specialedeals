#!/usr/bin/env python3
"""Static, compact personal supermarket-deals feed for GitHub Pages."""
from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).resolve().parent))
from sync_deals import fetch_all,normalize_all

OUTPUT=Path(__file__).resolve().parents[2]/"weekdeals"/"deals.json"

def compact_offer(r,p):
    """Project a verified source offer into the compact browser schema.

    Never treat bundle totals as normal single-item prices. In particular the
    PrijsProfeet API documents Aldi price as the *bundle total*.
    """
    d={"id":r[0],"winkel":r[1],"product":r[2],"categorie":r[3],
       "prijs":r[4],"van":p.get("valid_from") or "",
       "tot":p.get("valid_until") or "","url":r[12]}
    fields={"van_prijs":r[5],"korting":r[6],"actievorm":r[7],
            "verpakking":r[8],"ledenprijs":r[18],
            "loyaliteitsprogramma":r[19],
            "kanaal":r[17],"bundelaantal":r[20],
            "bundelprijs":r[21],
            "eenheidsprijs":r[28],"eenheid":r[29]}
    d.update({k:v for k,v in fields.items() if v not in ("",None)})
    if r[1]=="Aldi" and isinstance(r[20],(int,float)) and r[20]>=2:
        d["prijstype"]="bundeltotaal"
        # Do not show a single-item strikethrough against Aldi's bundle total.
        d.pop("van_prijs",None)
        d.pop("korting",None)
    if p.get("valid_until_estimated") is True:
        d["einddatum_geschat"]=True
    return d

def main():
    now=datetime.now(ZoneInfo("Europe/Amsterdam"))
    raw=fetch_all()
    mapped=normalize_all(raw,now.date().isoformat())
    by_id={"prijsprofeet:"+str(p.get("retailer"))+":"+str(p.get("product_id")):p for p in raw}
    deals=[]
    for r in mapped:
        p=by_id.get(r[0])
        if p is None: raise ValueError("Product source missing: "+str(r[0]))
        d=compact_offer(r,p)
        deals.append(d)
    if len(deals)<100:
        raise RuntimeError(f"Only {len(deals)} products; keeping previous publication")
    payload={"schema_version":2,"updated_at":now.isoformat(timespec="seconds"),
             "source":"PrijsProfeet","attribution":"Aanbiedingen via PrijsProfeet",
             "source_url":"https://www.prijsprofeet.nl",
             "scope":"Alleen landelijke supermarktacties, niet per filiaal bevestigd",
             "total_api":len(raw),"total_published":len(deals),
             "deals":deals}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUTPUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"),
                              allow_nan=False),encoding="utf-8")
    tmp.replace(OUTPUT)
    print(f"Published {len(deals)} of {len(raw)} product offers: {OUTPUT.stat().st_size} bytes")

if __name__=="__main__":
    main()
