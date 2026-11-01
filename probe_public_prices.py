#!/usr/bin/env python3
"""Diagnostic only: metadata and short sample JSON from documented public APIs.

No credentials, no write actions, and no personal data.
"""
import json
import urllib.request
import urllib.error

urls=[
"https://prijspuls.nl/api/prijs?q=Dyson%20Airwrap",
"https://prijspuls.nl/api/prijzen",
"https://www.koopwizer.com/api/v1/products/search?q=Giraffe%20Original%20Blend&limit=2",
"https://www.koopwizer.com/api/v1/deals?limit=2",
]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"SpecialeDealsIntegrationCheck/1.0","Accept":"application/json"})
  with urllib.request.urlopen(req,timeout=16) as r:
   content_type=r.headers.get("content-type")
   raw=r.read(180000)
   try:
    doc=json.loads(raw)
    if url=="https://prijspuls.nl/api/prijzen":
     from public_price_peil import build,TZ
     from datetime import datetime
     try:
      market=build(doc,datetime.now(TZ))
      print("Prijspuls adapter dry run:",market["usablePriceLevels"],
            {k:v["available"] for k,v in market["groups"].items()})
     except (ValueError,TypeError) as exc:
      print("Prijspuls adapter source validation failed:",str(exc))
      raise
    if isinstance(doc,dict):
     example={k:(str(v)[:500] if not isinstance(v,(dict,list)) else
          {"type":type(v).__name__,"length":len(v),"first":str(v[:1] if isinstance(v,list) else list(v.items())[:4])[:1800]})
          for k,v in list(doc.items())[:16]}
     print(json.dumps({"url":url,"status":r.status,"type":content_type,"shape":"object","example":example},ensure_ascii=False)[:6500])
    else:print(json.dumps({"url":url,"status":r.status,"type":content_type,"shape":type(doc).__name__,"head":str(doc[:2])[:2600]},ensure_ascii=False))
   except (ValueError,TypeError):
    print(json.dumps({"url":url,"status":r.status,"type":content_type,"shape":"not_json","head":raw[:80].decode("utf-8","replace")}))
 except (OSError,ValueError) as e:print(json.dumps({"url":url,"error":str(e)[:200]}))
