#!/usr/bin/env python3
"""Gratis PrijsProfeet-scan. Geen niet-gecontroleerde deals publiceren."""
import json, sys, urllib.request, urllib.parse, datetime, pathlib, hashlib, re
BASE="https://www.prijsprofeet.nl/api/v1/search"
LEGACY_TERMS=["kip","kwark","skyr","eieren","zalm","tonijn","spinazie","groente","banaan","noten","wraps","melk","olijfolie","wasmiddel","vaatwastabletten","rituals","janzen","earth 46","doucheschuim","deodorant","deo","shower foam","geurstokjes","handzeep","bodylotion","douchegel","huisparfum","luchtverfrisser","sandelhout","cederhout","knijpkwark","knijpzak","proteinekwark","proteïnekwark"]
RETAILERS={"albert_heijn":"Albert Heijn","jumbo":"Jumbo","lidl":"Lidl","aldi":"Aldi","dirk":"Dirk","plus":"PLUS","hoogvliet":"Hoogvliet","vomar":"Vomar"}
PREMIUM={"rituals","janzen","earth 46","doucheschuim","deodorant","deo","shower foam","geurstokjes","handzeep","bodylotion","douchegel","huisparfum","luchtverfrisser","sandelhout","cederhout"}
FOOD={"kip","kwark","skyr","eieren","zalm","tonijn","spinazie","groente","banaan","noten","wraps","melk","olijfolie","knijpkwark","knijpzak","proteinekwark","proteïnekwark"}
TERMS=[t for t in LEGACY_TERMS if t not in FOOD]
TODAY=datetime.datetime.now(datetime.timezone.utc).date()
def get(term):
    rows=[];page=1
    while True:
        params=urllib.parse.urlencode({"q":term,"page_size":50,"page":page})
        req=urllib.request.Request(BASE+"?"+params,headers={"User-Agent":"Kansenkompas/2.0","Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=25) as response:data=json.load(response)
        batch=data.get("results")
        if not isinstance(batch,list):raise ValueError("Missing results")
        rows.extend(batch)
        total=data.get("total_pages") or data.get("pagination",{}).get("total_pages")
        if (total and page>=int(total)) or not batch or (not total and len(batch)<50):break
        if page>=500:raise ValueError("Pagination safety guard; incomplete query")
        page+=1
    return {"results":rows}
def comparable_unit(title, price):
    name=title.lower().replace(",", ".")
    for pat,unit,divisor in [(r"(\d+)\s*(?:wasbeurten|wasbeurt|wasjes|sc)\b", "wasbeurt", 1),(r"(\d+(?:\.\d+)?)\s*kg\b", "kg", 1),(r"(\d+(?:\.\d+)?)\s*g\b", "kg", 1000),(r"(\d+(?:\.\d+)?)\s*ml\b", "liter", 1000),(r"(\d+(?:\.\d+)?)\s*(?:liter|ltr)\b", "liter", 1)]:
        m=re.search(pat,name)
        if m:
            qty=float(m.group(1))/divisor
            if qty: return {"unit":unit,"price_per_unit":round(price/qty,3)}
    return None

def compare_exact(items):
    indexed={}
    for d in items:
        if len(d.get("ean",""))>=8: indexed.setdefault(d["ean"],[]).append(d)
    for d in items:
        alt=sorted([x for x in indexed.get(d.get("ean"),[]) if x["store"]!=d["store"]],key=lambda x:x["price"])
        d["other_stores"]=[{"store":x["store"],"price":x["price"],"url":x["url"]} for x in alt[:5]]
        d["exact_cheapest"]=None if not alt else d["price"]<=alt[0]["price"]
        d["cheaper_elsewhere_percent"]=round((d["price"]-alt[0]["price"])/d["price"]*100,1) if alt and alt[0]["price"]<d["price"] else 0 if alt else None
    for d in items:
        name=d["title"].lower()
        category=None
        if "wasmiddel" in name:
            category="capsules" if "capsul" in name else "poeder" if "poeder" in name else "vloeibaar" if "vloeibaar" in name else None
        d["alternative_type"]=category
        if category and d.get("unit") and d["unit"].get("unit")=="wasbeurt":
            alternatives=[]
            for other in items:
                oname=other["title"].lower()
                otype="capsules" if "capsul" in oname else "poeder" if "poeder" in oname else "vloeibaar" if "vloeibaar" in oname else None
                if other["id"]!=d["id"] and otype==category and other.get("unit") and other["unit"].get("unit")=="wasbeurt":
                    alternatives.append(other)
            alternatives.sort(key=lambda x:x["unit"]["price_per_unit"])
            d["alternatives"]=[{"title":x["title"],"store":x["store"],"price_per_unit":x["unit"]["price_per_unit"],"url":x["url"]} for x in alternatives[:3]]
        else:d["alternatives"]=[]
    return items

def scan():
    warnings=[]; out={}; successful=0
    for term in TERMS:
        try:
            data=get(term)
            if not isinstance(data.get("results"),list): raise ValueError("Geen results-lijst")
            successful+=1
            for p in data["results"]:
                if p.get("promotion_status")!="active":continue
                retailer=str(p.get("retailer") or "").lower()
                if retailer not in RETAILERS:continue
                end=str(p.get("valid_until") or "")[:10]
                if not end:continue
                try:
                    if datetime.date.fromisoformat(end)<TODAY:continue
                except ValueError:continue
                name=str(p.get("name") or "").strip()
                price=p.get("price")
                if not name or not isinstance(price,(int,float)) or price<=0:continue
                code=str(p.get("id") or p.get("ean") or hashlib.sha256((name+retailer+end).encode()).hexdigest()[:16])
                key=retailer+":"+code
                old=p.get("original_price")
                saving=p.get("savings_percentage")
                if not isinstance(saving,(int,float)):saving=None
                source=p.get("url") or p.get("product_url")
                if not isinstance(source,str) or not source.startswith("https://"):
                    source="https://www.prijsprofeet.nl/api/v1/search?"+urllib.parse.urlencode({"q":name[:55]})
                out[key]={"ean":str(p.get("ean") or ""), "unit":comparable_unit(name,price), "id":key,"title":name,"store":RETAILERS[retailer],"category":"food" if term in FOOD else "premium" if term in PREMIUM else "home","price":round(price,2),"original_price":round(old,2) if isinstance(old,(int,float)) and old>price else None,"discount_percent":round(saving,1) if saving is not None else None,"valid_until":end,"url":source,"verified":True,"note":"Aanbieding uit PrijsProfeet, controleer beschikbaarheid en afrekenprijs bij de winkel.","source":"PrijsProfeet"}
        except Exception as exc: warnings.append(term+": "+str(exc)[:180])
    if not successful:
        raise RuntimeError("Geen enkele API-aanroep gelukt: bestaand deals.json blijft ongewijzigd. "+str(warnings[:3]))
    arr=compare_exact(list(out.values()))
    arr=sorted(arr,key=lambda p:(p["exact_cheapest"] is True,p["discount_percent"] or 0),reverse=True)
    result={"last_updated":datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),"deals":arr,"warnings":warnings+["Vergelijkingen met Action, Zeeman en huismerken ontbreken zolang hun actuele prijsdata niet aangesloten is. EAN-vergelijking dekt uitsluitend exact dezelfde producten. Deze API dekt alleen aangesloten supermarktproducten. Rituals/Janzen buiten supermarkten, Action, Kruidvat en dupes zijn nog niet volledig aangesloten. Geen historische prijscontrole beschikbaar op gratis API."],"sources":{"PrijsProfeet":"OK","failed_queries":len(warnings)}}
    (pathlib.Path(__file__).resolve().parent.parent/"household.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{len(arr)} actieve deals, {successful} API-queries geslaagd, {len(warnings)} waarschuwingen")
if __name__=="__main__":scan()

