#!/usr/bin/env python3
"""Import public folder metadata, NEVER invent non-food product prices.

Folderwijzer API: https://folderwijzer.nl/folder-api/
Its public JSON includes folder-level data for non-alcohol categories, not item prices.
"""
from __future__ import annotations
import json
import re
from datetime import date,datetime
from pathlib import Path
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

URL="https://folderwijzer.nl/api/v1/folders.json"
OUT=Path(__file__).resolve().parents[2]/"weekdeals"/"folders.json"
FOCUS={"kruidvat":"Drogisterij","trekpleister":"Drogisterij","xenos":"Wonen & huishoudelijk"}
NAMES={"kruidvat":"Kruidvat","trekpleister":"Trekpleister","xenos":"Xenos"}

def choose(v,*keys):
    if not isinstance(v,dict): return None
    for k in keys:
        if v.get(k) is not None: return v[k]
    return None

def iso(x):
    if x is None:return ""
    s=str(x)[:10]
    try:
        date.fromisoformat(s)
        return s
    except ValueError:return ""

def token(s):
    return re.sub(r"[^a-z0-9]+","-",str(s or "").lower()).strip("-")

def retailer(info,parent):
    v=choose(info,"retailer","store","chain","winkel","brand")
    if v is None: v=choose(parent,"retailer","store","chain","winkel","brand")
    if isinstance(v,dict):
        name=choose(v,"slug","name","id","retailerSlug")
    else:name=v
    if not name:
        name=choose(info,"retailerSlug","retailer_slug","storeSlug") or choose(parent,"slug","name","id")
    val=token(name)
    for k in FOCUS:
        if val==k or val.endswith("-"+k) or val.startswith(k+"-"):
            return k
    return ""

def candidates(data):
    """Recursive parser supports index as array, nested retailer-index, or dictionary."""
    found=[]
    def walk(node,parent):
        if isinstance(node,list):
            for child in node:walk(child,parent)
        elif isinstance(node,dict):
            start=iso(choose(node,"validFrom","valid_from","startDate","start_date"))
            end=iso(choose(node,"validUntil","valid_until","endDate","end_date"))
            link=choose(node,"url","folderUrl","folder_url","deeplink")
            k=retailer(node,parent or {})
            if start and end and isinstance(link,str) and link.startswith("https://") and k:
                if end>=date.today().isoformat(): # current and forthcoming folders
                    rawcount=choose(node,"offerCount","offer_count","totalOffers")
                    try:count=int(rawcount) if rawcount is not None else None
                    except (TypeError,ValueError):count=None
                    found.append({"id":k+":"+start+":"+end,"winkel":NAMES[k],
                                  "categorie":FOCUS[k],"van":start,"tot":end,
                                  "url":link,"aanbiedingen_aantal":count,
                                  "type":"folderlink","bron":"Folderwijzer"})
            for key,val in node.items():
                if isinstance(val,(dict,list)):
                    walk(val,node if any(x in node for x in ("slug","retailer","name","retailerSlug")) else parent)
    walk(data,{})
    dedup={}
    for f in found:
        if f["url"].startswith("https://folderwijzer.nl/") or f["url"].startswith("https://www.folderwijzer.nl/"):
            dedup[(f["id"],f["url"])]=f
    return sorted(dedup.values(),key=lambda x:(x["winkel"],x["van"],x["url"]))

def main():
    request=Request(URL,headers={"User-Agent":"WeekdealsBleiswijk/1.0 (personal public folder viewer)",
                                  "Accept":"application/json"})
    with urlopen(request,timeout=40) as r:
        data=json.load(r)
    print("Folderwijzer index schema:",
          "root_type=",type(data).__name__,
          "root_keys=",list(data.keys())[:18] if isinstance(data,dict) else "array",
          "root_len=",len(data))
    folders=candidates(data)
    if not folders:
        sample=str(data)[:900]
        raise RuntimeError("No valid Kruidvat/Trekpleister/Xenos folder records; index shape: "+sample)
    payload={"schema_version":1,
             "updated_at":datetime.now(ZoneInfo("Europe/Amsterdam")).isoformat(timespec="seconds"),
             "source":"Folderwijzer","attribution":"Folders via Folderwijzer",
             "source_url":"https://folderwijzer.nl/","description":"Folderniveau: geen productprijzen",
             "folders":folders}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    tmp.replace(OUT)
    print("Published",len(folders),"non-food folders:",sorted(set(x["winkel"] for x in folders)))

if __name__=="__main__":
    main()
