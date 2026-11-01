#!/usr/bin/env python3
"""Publish verified PrijsProfeet deal feed as self-contained static JSON for GitHub Pages."""
from __future__ import annotations
import json,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sync_deals import fetch_all,normalize_all

OUTPUT=Path(__file__).resolve().parents[2]/"weekdeals"/"deals.json"

def main():
    now=datetime.now(ZoneInfo("Europe/Amsterdam"))
    raw=fetch_all()
    mapped=normalize_all(raw,now.date().isoformat())
    deals=[]
    for r in mapped:
        d=dict(zip([
            "id","winkel","product","categorie","prijs","van_prijs","korting",
            "actievorm","verpakking","van_datum_serial","tot_datum_serial","bron","url",
            "check_datum_serial","kwaliteit","opmerking","ean","kanaal","ledenprijs",
            "loyaliteitsprogramma","bundelaantal","bundelprijs","product_id",
            "basisproduct_id","einddatum_geschat","alleen_online","alleen_winkel",
            "bron_bijgewerkt","eenheidsprijs","eenheid","promogroep"
        ],r))
        for key in ("van_datum_serial","tot_datum_serial","check_datum_serial"):
            d.pop(key,None)
        source=next((p for p in raw if "prijsprofeet:"+str(p.get("retailer"))+":"+str(p.get("product_id"))==d["id"]),None)
        if source is None: raise ValueError("Missing source match")
        d["van"]=source.get("valid_from") or ""
        d["tot"]=source.get("valid_until") or ""
        d["regio_status"]="Winkel in Bleiswijk bevestigd" if d["winkel"] in ("Albert Heijn","Jumbo","Lidl") else "Landelijke aanbieding; lokale vestiging/voorraad niet gecontroleerd"
        deals.append(d)
    if len(deals)<100:
        raise RuntimeError(f"Only {len(deals)} usable deals, refusing to replace prior publication")
    payload={"schema_version":1,"updated_at":now.isoformat(timespec="seconds"),
             "source":"PrijsProfeet","attribution":"Aanbiedingen via PrijsProfeet",
             "source_url":"https://www.prijsprofeet.nl",
             "scope":"Nederlandse supermarktacties; geen bewijs van beschikbaarheid per filiaal",
             "total_api":len(raw),"total_published":len(deals),
             "store_coverage":"Supermarkten via PrijsProfeet; overige retailers nog niet gekoppeld",
             "deals":deals}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUTPUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"),allow_nan=False),encoding="utf-8")
    tmp.replace(OUTPUT)
    print(f"Published {len(deals)} of {len(raw)} API deals to {OUTPUT}")

if __name__=="__main__":
    main()
