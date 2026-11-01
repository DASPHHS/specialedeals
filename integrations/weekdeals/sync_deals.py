#!/usr/bin/env python3
"""Dagelijkse Nederlandse supermarktdeals -> privé Google Sheet.

Alleen de API van PrijsProfeet is actief. Non-food bronnen vereisen eigen adapters.
Geen persoonsgegevens, inloggegevens of Google Sheet-ID's in deze repository.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API="https://www.prijsprofeet.nl/api/v1"
API_HOME="https://www.prijsprofeet.nl"
PAGE_SIZE=100
COLUMNS=["Deal-ID","Winkel","Product","Categorie","Prijs (€)","Van-prijs (€)","Korting",
         "Actievorm","Verpakking","Van datum","Tot datum","Bron","Bron-URL",
         "Gecontroleerd op","Kwaliteit","Opmerking","EAN","Verkoopkanaal",
         "Ledenprijs","Loyaliteitsprogramma","Bundelaantal","Bundelprijs",
         "Product-ID","Basisproduct-ID","Einddatum geschat","Alleen online",
         "Alleen winkel","Bron bijgewerkt op","Eenheidsprijs","Eenheid","Promogroep-ID"]
N=len(COLUMNS)
NAMES={"albert_heijn":"Albert Heijn","jumbo":"Jumbo","lidl":"Lidl","aldi":"Aldi",
       "plus":"PLUS","dirk":"Dirk","hoogvliet":"Hoogvliet","dekamarkt":"DekaMarkt",
       "vomar":"Vomar","ekoplaza":"Ekoplaza","spar":"SPAR","poiesz":"Poiesz",
       "nettorama":"Nettorama","boons_markt":"Boon's Markt","gewoon_coop":"Coop",
       "mcd":"MCD","amazing_oriental":"Amazing Oriental"}
BLEISWIJK_CONFIRMED={"albert_heijn","jumbo","lidl"}
LOG=logging.getLogger("weekdeals")

def as_num(x):
    if isinstance(x, bool) or x is None:
        return ""
    if isinstance(x, (float,int)) and math.isfinite(x):
        return x
    return ""

def serial(s):
    try:
        return (date.fromisoformat(str(s)[:10])-date(1899,12,30)).days
    except (ValueError,TypeError):
        return ""

def tri(x):
    return "Ja" if x is True else ("Nee" if x is False else "Onbekend")

def get_json(endpoint,params=None,delay=2.2):
    url=API+endpoint+("?" + urlencode(params) if params else "")
    hdr={"Accept":"application/json",
         "User-Agent":"WeekdealsNL/1.0 (+https://github.com/DASPHHS/specialedeals)"}
    if os.getenv("PRIJSPROFEET_API_KEY"):
        hdr["X-API-Key"]=os.environ["PRIJSPROFEET_API_KEY"]
    for attempt in range(6):
        try:
            with urlopen(Request(url,headers=hdr),timeout=50) as r:
                payload=json.load(r)
            if not isinstance(payload,dict):
                raise ValueError("Expected JSON object")
            time.sleep(delay)
            return payload
        except HTTPError as err:
            if err.code not in (429,500,502,503,504):
                raise
            raw=err.headers.get("Retry-After")
            try:
                pause=min(float(raw),180) if raw else min(2**attempt*3,90)
            except (TypeError,ValueError):
                pause=min(2**attempt*3,90)
            LOG.warning("API HTTP %d; retry in %.0fs",err.code,pause)
        except (URLError,TimeoutError) as err:
            LOG.warning("API network error: %s",err)
            pause=min(2**attempt*3,90)
        time.sleep(pause+random.random())
    raise RuntimeError("API unavailable after six attempts")

def validate_page(payload, page):
    if (not isinstance(payload.get("total"),int) or payload["total"]<0
            or not isinstance(payload.get("products"),list)):
        raise ValueError(f"Page {page}: invalid total/products")
    return payload["total"],payload["products"]

def fetch_all(fetch=get_json):
    seen=set()
    data=[]
    expected=None
    for page in range(1,1001):
        payload=fetch("/products/promotional/all",{"page":page,"page_size":PAGE_SIZE})
        total,batch=validate_page(payload,page)
        if expected is None:
            if total==0:
                raise ValueError("Zero results: refusing to replace existing data")
            expected=total
        if total!=expected:
            raise ValueError(f"Pagination changed during fetch ({expected} -> {total})")
        if not batch and len(data)<expected:
            raise ValueError(f"Early empty page {page} at {len(data)}/{expected}")
        for item in batch:
            if not isinstance(item,dict) or not item.get("product_id") or not item.get("retailer"):
                raise ValueError(f"Page {page}: product ID/retailer missing")
            key=(str(item["retailer"]),str(item["product_id"]))
            if key in seen:
                raise ValueError(f"Duplicate product ID {key}")
            seen.add(key)
            data.append(item)
        LOG.info("page %d: %d/%d",page,len(data),expected)
        if len(data)>=expected:
            break
    if len(data)!=expected:
        raise ValueError(f"Expected {expected} deals, got {len(data)}")
    return data

def normalize(product,today):
    if product.get("is_promotional") is False or product.get("promotion_status") in ("shelf","historical"):
        return None
    if not product.get("name"):
        return None
    price=as_num(product.get("price"))
    if price=="" or price<0:
        return None
    retailer=str(product["retailer"])
    start=serial(product.get("valid_from"))
    end=serial(product.get("valid_until"))
    original=as_num(product.get("original_price"))
    multibuy=product.get("multi_buy_quantity")
    pct=as_num(product.get("savings_percentage"))
    if multibuy and pct!="":
        discount=pct/100 if 0<=pct<=100 else ""
    elif multibuy:
        discount=""
    elif original!="" and original>0 and price<=original:
        discount=(original-price)/original
    elif pct!="" and 0<=pct<=100:
        discount=pct/100
    else:
        discount=""
    flags=[]
    if start=="" or end=="":
        flags.append("Onbekende geldigheid")
    if product.get("valid_until_estimated"):
        flags.append("Einddatum geschat")
    if retailer not in BLEISWIJK_CONFIRMED:
        flags.append("Lokale vestiging niet bevestigd")
    if product.get("online_only") is True:
        channel="Alleen online"
    elif product.get("in_store_only") is True:
        channel="Alleen winkel"
    else:
        channel="Online/winkel onbekend"
    return [
        "prijsprofeet:"+retailer+":"+str(product["product_id"]),
        NAMES.get(retailer,retailer),str(product["name"]),
        product.get("unified_category") or "",price,original,discount,
        product.get("promotion_type") or "",product.get("quantity") or "",
        start,end,"PrijsProfeet",product.get("product_url") or API_HOME,
        serial(today),"API / geschat" if product.get("valid_until_estimated") else "API / bronwaarde",
        "; ".join(flags),product.get("ean") or "",channel,
        as_num(product.get("loyalty_price")),product.get("loyalty_program") or "",
        as_num(multibuy),as_num(product.get("multi_buy_price")),
        str(product["product_id"]),product.get("base_product_id") or "",
        tri(product.get("valid_until_estimated")),tri(product.get("online_only")),
        tri(product.get("in_store_only")),str(product.get("extracted_at") or "")[:19],
        as_num(product.get("unit_price")),product.get("unit") or "",
        product.get("promo_group_id") or ""
    ]

def normalize_all(items,today):
    rows=[r for p in items if (r:=normalize(p,today)) is not None]
    if not rows:
        raise ValueError("Normalization produced no usable deals")
    return rows

def worksheet(book,title,rows,cols=N):
    import gspread
    try:
        w=book.worksheet(title)
    except gspread.WorksheetNotFound:
        w=book.add_worksheet(title=title,rows=max(rows,100),cols=max(cols,10))
    if w.row_count<rows or w.col_count<cols:
        w.resize(rows=max(w.row_count,rows),cols=max(w.col_count,cols))
    return w

def pad(row):
    return list(row[:N])+[""]*max(N-len(row),0)

def write_blocks(w,all_rows):
    for offset in range(0,len(all_rows),500):
        block=all_rows[offset:offset+500]
        w.update(range_name=f"A{offset+1}:AE{offset+len(block)}",
                 values=block,value_input_option="USER_ENTERED")

def apply(book,raw):
    import gspread
    sheet_id=os.environ.get("GOOGLE_SHEET_ID")
    service_json=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sheet_id or not service_json:
        raise RuntimeError("GitHub Actions secrets GOOGLE_SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON required")
    client=gspread.service_account_from_dict(json.loads(service_json))
    book=client.open_by_key(sheet_id)
    today=datetime.now(ZoneInfo("Europe/Amsterdam")).date().isoformat()
    rows=normalize_all(raw,today)
    live=worksheet(book,"Alle deals",len(rows)+1)
    old=live.get("A1:AE",value_render_option="UNFORMATTED_VALUE")
    old_data=old[1:] if old else []
    # Keep future adapters' verified records, drop old provisional demo rows.
    others=[pad(r) for r in old_data if r and not str(r[0]).startswith(("start-","prijsprofeet:"))
            and (len(r)<12 or str(r[11])!="PrijsProfeet")]
    records=rows+others
    if len(records)+1>100000:
        raise ValueError("Too many records for this Sheets design: use a database first")
    staging=worksheet(book,"API import - staging",len(records)+1)
    staging.clear()
    write_blocks(staging,[COLUMNS]+records)
    if staging.acell(f"A{len(records)+1}").value!=str(records[-1][0]):
        raise RuntimeError("Staging verification failed")
    # Archive discontinued PrijsProfeet entries, but never provisional demo rows.
    previous=[pad(r) for r in old_data if r and str(r[0]).startswith("prijsprofeet:")]
    current_ids={str(r[0]) for r in rows}
    expired=[r for r in previous if str(r[0]) not in current_ids]
    if expired:
        hist=worksheet(book,"Historie",max(len(expired)+10,100))
        if hist.acell("A1").value!="Deal-ID":
            hist.update(range_name="A1:AE1",values=[COLUMNS],value_input_option="RAW")
        existing=set(hist.col_values(1)[1:])
        new=[r for r in expired if str(r[0]) not in existing]
        for pos in range(0,len(new),500):
            hist.append_rows(new[pos:pos+500],value_input_option="USER_ENTERED")
    # All-or-nothing Sheets batchUpdate for clear+copy. Other tabs unchanged.
    size=max(live.row_count,len(records)+1)
    live.resize(rows=size,cols=max(live.col_count,N))
    book.batch_update({"requests":[
        {"repeatCell":{"range":{"sheetId":live.id,"startRowIndex":0,"endRowIndex":size,
                                "startColumnIndex":0,"endColumnIndex":N},
                       "cell":{},"fields":"userEnteredValue"}},
        {"copyPaste":{"source":{"sheetId":staging.id,"startRowIndex":0,"endRowIndex":len(records)+1,
                                "startColumnIndex":0,"endColumnIndex":N},
                      "destination":{"sheetId":live.id,"startRowIndex":0,
                                     "endRowIndex":len(records)+1,"startColumnIndex":0,
                                     "endColumnIndex":N},
                      "pasteType":"PASTE_NORMAL","pasteOrientation":"NORMAL"}},
        {"setBasicFilter":{"filter":{"range":{"sheetId":live.id,"startRowIndex":0,
                                              "endRowIndex":len(records)+1,
                                              "startColumnIndex":0,"endColumnIndex":N}}}},
        {"updateSheetProperties":{"properties":{"sheetId":live.id,
                                                "gridProperties":{"frozenRowCount":1}},
                                  "fields":"gridProperties.frozenRowCount"}}
    ]})
    # Week views are based on overlapping validity periods, not promotion start only.
    for name,days in (("Deze week",0),("Volgende week",7)):
        w=worksheet(book,name,len(records)+1)
        w.update(range_name="A1:AE1",values=[COLUMNS],value_input_option="RAW")
        start=f"TODAY()-WEEKDAY(TODAY();2)+{1+days}"
        end=f"TODAY()-WEEKDAY(TODAY();2)+{7+days}"
        formula=(f"=IFERROR(FILTER('Alle deals'!A2:AE;'Alle deals'!J2:J<={end};"
                 f"'Alle deals'!K2:K>={start};'Alle deals'!J2:J<>\"\";"
                 f"'Alle deals'!K2:K<>\"\");\"\")")
        w.update(range_name="A2",values=[[formula]],value_input_option="USER_ENTERED")
    overview=book.worksheet("Overzicht")
    overview.update(range_name="A1:B3",values=[
        ["WEEKDEALS NL | ACTUELE API-SYNC",""],
        ["Peildatum",serial(today)],
        ["Status",f"API volledig: {len(rows)} supermarktacties; {len(others)} overige records bewaard; non-food nog niet geautomatiseerd"]
    ],value_input_option="USER_ENTERED")
    overview.update(range_name="A12:B12",values=[
        ["Bronvermelding","Aanbiedingen via PrijsProfeet — https://www.prijsprofeet.nl"]
    ],value_input_option="RAW")
    report=worksheet(book,"Importlog",100,8)
    report.append_row([serial(today),"PrijsProfeet","Volledige API-synchronisatie",
                       len(rows),0,"Ja","API volledig; niet alle NL winkels",
                       f"{len(raw)} ontvangen, {len(rows)} ingelezen, {len(expired)} verlopen"],
                      value_input_option="USER_ENTERED")
    print(f"OK: {len(rows)} supermarktdeals naar Google Sheets, {len(others)} overige records behouden")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check-api",action="store_true",help="Test eerste API-pagina zonder Sheets-toegang")
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    if args.check_api:
        count,items=validate_page(get_json("/products/promotional/all",{"page":1,"page_size":5}),1)
        if count<=0 or not items:
            raise RuntimeError("API check returned empty data")
        print(f"API OK: first page {len(items)} products, reported total={count}")
        return
    items=fetch_all()
    apply(None,items)

if __name__=="__main__":
    main()
