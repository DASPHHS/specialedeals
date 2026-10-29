#!/usr/bin/env python3
"""Append-only, unverified product-page price history. Not proof of delivered price."""
import datetime as dt
import json
import pathlib
import sqlite3
from decimal import Decimal, InvalidOperation

DB=pathlib.Path("price-history.sqlite3")
INPUT=pathlib.Path("price-probes.json")
OUTPUT=pathlib.Path("price-history-summary.json")

def record(db, probes, timestamp):
    db.execute("""CREATE TABLE IF NOT EXISTS observations (
      target_id TEXT NOT NULL, checked_at TEXT NOT NULL, seller TEXT NOT NULL,
      product_id TEXT NOT NULL, variant_key TEXT NOT NULL, url TEXT NOT NULL,
      item_price_eur TEXT NOT NULL,
      PRIMARY KEY(target_id,checked_at))""")
    count=0
    for item in probes:
        if item.get("status")!="product_price_candidate": continue
        try:
            value=Decimal(str(item["priceEUR"]))
            if not value.is_finite() or value<=0: continue
            keys=("targetId","seller","productId","variantKey","url")
            if any(not isinstance(item.get(k),str) or not item[k].strip() for k in keys): continue
            db.execute("INSERT OR IGNORE INTO observations VALUES (?,?,?,?,?,?,?)",
                (item["targetId"],timestamp,item["seller"],item["productId"],item["variantKey"],item["url"],str(value)))
            count+=1
        except (KeyError,TypeError,InvalidOperation): continue
    db.commit()
    return count

def summarize(db):
    rows=db.execute("""SELECT target_id, seller, product_id, variant_key,
         COUNT(*) AS samples, MIN(item_price_eur*1.0), MAX(checked_at)
         FROM observations GROUP BY target_id,seller,product_id,variant_key
         ORDER BY product_id,variant_key,seller""").fetchall()
    return {"notice":"Item-price observations only. Shipping and NL checkout unverified. Not live all-in comparisons or verified deals.",
            "sources":[{"targetId":a,"seller":b,"productId":c,"variantKey":d,"samples":e,
                        "lowestObservedItemPriceEUR":f"{f:.2f}","lastCheckedAt":g}
                       for a,b,c,d,e,f,g in rows]}

def main():
    data=json.loads(INPUT.read_text(encoding="utf-8"))
    stamp=data.get("updatedAt") or dt.datetime.now(dt.timezone.utc).isoformat()
    with sqlite3.connect(DB) as db:
        inserted=record(db,data.get("items",[]),stamp)
        result=summarize(db)
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Historical candidate observations:",inserted)

if __name__=="__main__": main()
