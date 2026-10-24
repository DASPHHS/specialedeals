#!/usr/bin/env python3
"""Fail publication when dashboard syntax or critical data contracts break."""
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
PAGES={"index.html":('firstcards','observations','merchantUpdated','wishAdd','watchStatus','sourceRows','ingCompare','ingCompareResult','ingPoints'),
       "ai-kansen.html":('buildcards','buildcategory','othercards','researchPanel','researchCards')}
for file,ids in PAGES.items():
 html=(ROOT/file).read_text(encoding="utf-8")
 for identifier in ids:
  if ('id="'+identifier+'"') not in html:raise RuntimeError(file+": missing element "+identifier)
 blocks=re.findall(r"<script\b[^>]*>(.*?)</script>",html,flags=re.I|re.S)
 if not blocks:raise RuntimeError(file+": no JavaScript")
 for j,block in enumerate(blocks):
  # Node.js is installed on ubuntu-latest; do not execute browser code here.
  scratch=ROOT/("_sitecheck_"+str(j)+".js")
  scratch.write_text(block,encoding="utf-8")
  try:
   run=subprocess.run(["node","--check",str(scratch)],text=True,capture_output=True)
   if run.returncode:raise RuntimeError(file+": invalid JS "+run.stderr)
  finally:scratch.unlink(missing_ok=True)
for path,key in (("watchlist.json","items"),("shop-targets.json","targets"),("radar-config.json","brands"),
 ("bouwideeen.json","items"),("ai-kansen.json","items")):
 data=json.loads((ROOT/path).read_text(encoding="utf-8"))
 if not isinstance(data.get(key),list):raise RuntimeError(path+": "+key+" must be array")
data=json.loads((ROOT/"merchant-observations.json").read_text(encoding="utf-8"))
for entry in data.get("offers",[]):
 for k in ("title","store","price","url","checkedAt"):
  if k not in entry:raise RuntimeError("merchant observation missing "+k)
 if entry.get("marketComparisonVerified") is True and not entry.get("referencePrice"):
  raise RuntimeError("Proven market comparison has no reference price")

# Data contracts are stricter than mere HTML syntax. UI must never turn a merchant
# price observation into a guaranteed bargain or turn an out-of-stock item into a pick.
allowed_stock={"uitverkocht","volgens winkel op voorraad","tegenstrijdige voorraadinformatie",
 "onbekend","voorbestelling","nabestelling"}
seen_urls=set()
for entry in data.get("offers",[]):
 if entry.get("stockStatus") not in allowed_stock:raise RuntimeError("Unknown stock class")
 if not isinstance(entry.get("variantVerified"),bool):raise RuntimeError("Variant verification must be boolean")
 if entry.get("allInVerified") is True and entry.get("marketComparisonVerified") is not True:
  raise RuntimeError("All-in deal marked verified without market comparison")
 if entry.get("marketComparisonVerified") is True and not entry.get("otherTrackedShopPrices"):
  raise RuntimeError("Market comparison cannot be asserted without independent shop prices")
 if not (0.50<=float(entry["price"])<=5000):raise RuntimeError("Merchant price out of range")
 if entry["url"] in seen_urls:raise RuntimeError("Duplicate shop URL")
 seen_urls.add(entry["url"])
 if "ownHistoryLow90d" in entry and float(entry["ownHistoryLow90d"])>float(entry["price"]):
  raise RuntimeError("Impossible own-history low price")
 if "ownHistoryHigh90d" in entry and float(entry["ownHistoryHigh90d"])<float(entry["price"]):
  raise RuntimeError("Impossible own-history high price")
watch=json.loads((ROOT/"watchlist.json").read_text(encoding="utf-8"))
products=set()
for item in watch.get("items",[]):
 name=item.get("product","")
 if not isinstance(name,str) or not 3<=len(name)<=120:raise RuntimeError("Invalid public watch product")
 if not isinstance(item.get("maxPriceEUR"),(int,float)) or not .5<=item["maxPriceEUR"]<=10000:
  raise RuntimeError("Invalid watch maximum price")
 if name.casefold() in products:raise RuntimeError("Duplicate watch product")
 products.add(name.casefold())
live=json.loads((ROOT/"live-deals.json").read_text(encoding="utf-8"))
for key in ("deals","samples","promotions","sources"):
 if not isinstance(live.get(key),list):raise RuntimeError("Discovery feed missing "+key)
for row in live.get("deals",[]):
 if row.get("priceVerified") is True or row.get("allInVerified") is True:
  raise RuntimeError("Discovery lead falsely marked as verified")
index=(ROOT/"index.html").read_text(encoding="utf-8")
for phrase in ("stockInfo(d)","app.observations","Nog geen onafhankelijke marktprijsvergelijking","watchlist.json","ingCompare"):
 if phrase not in index:raise RuntimeError("Dashboard missing safety/alert behavior "+phrase)

print("Website and JSON quality checks passed.")
