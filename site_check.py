#!/usr/bin/env python3
"""Fail publication when dashboard syntax or critical data contracts break."""
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
PAGES={"index.html":('firstcards','observations','merchantUpdated','wishAdd','watchStatus','sourceRows','ingCompare','ingCompareResult','ingPoints'),
       "ai-kansen.html":('buildcards','buildcategory','othercards','researchPanel','researchCards'),
       "besparen.html":('contracts','strategyCards','strategyCount','strategyCategory','contractDealResult','benefitType','compareCurrent')}
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

# Every generated public dataset must be structurally valid and timestamped.
for file in ("merchant-observations.json","live-deals.json","watchlist.json"):
 doc=json.loads((ROOT/file).read_text(encoding="utf-8"))
 timestamp=doc.get("checkedAt") or doc.get("updatedAt")
 if not isinstance(timestamp,str) or not timestamp:raise RuntimeError(file+": missing scan/update timestamp")
# Explicitly reject a false positive when product variants are not verified.
for entry in data.get("offers",[]):
 if entry.get("variantVerified") is False and entry.get("allInVerified") is True:
  raise RuntimeError("Unverified variant cannot be an all-in verified deal")
 if entry.get("stockStatus") in ("uitverkocht","tegenstrijdige voorraadinformatie") and entry.get("allInVerified") is True:
  raise RuntimeError("Unavailable or contradictory stock cannot be a verified deal")
# All outgoing links in public HTML must avoid javascript: navigation.
for filename in ("index.html","ai-kansen.html","winacties.html"):
 markup=(ROOT/filename).read_text(encoding="utf-8")
 if re.search(r'href\s*=\s*["\']\s*javascript:',markup,re.I):
  raise RuntimeError(filename+": unsafe javascript link")

# Prevent reintroducing grocery dashboards into this personal opportunities project.
if 'householdCards' in index or "fetch('./household.json" in index:
 raise RuntimeError("Grocery/household feed must not be rendered in Kansenkompas")
if '<details class="panel" id="rawPrices">' not in index:
 raise RuntimeError("Unverified shop observations should not dominate homepage")
ai=(ROOT/"ai-kansen.html").read_text(encoding="utf-8")
if 'active="nu"' not in ai or 'openTab("nu")' not in ai:
 raise RuntimeError("AI page must start with currently applicable options")
# Price observations are evidence, not deals; enforce separation.
if 'source==="retailer"?app.observations' not in index:
 raise RuntimeError("Retailer observations must only appear in the explicit price-source filter")
if 'highlighted.forEach(x=>first.append(card(x,"store")))' in index:
 raise RuntimeError("Unverified shop prices must not be shown as personal top picks")
if 'zonder resultaten' not in index:
 raise RuntimeError("Source overview must disclose zero-result searches")
# Sample-sale and contest cards must show real dated opportunities rather than blank panels.
events=json.loads((ROOT/"sample-events.json").read_text(encoding="utf-8"))
if not isinstance(events.get("events"),list):raise RuntimeError("Sample events list missing")
for e in events["events"]:
 for field in ("title","startDate","endDate","url","verification"):
  if not isinstance(e.get(field),str) or not e[field]:
   raise RuntimeError("Sample event missing "+field)
 if e["endDate"]<e["startDate"]:raise RuntimeError("Sample event end before start")
 if not e["url"].startswith("https://"):raise RuntimeError("Invalid sample-event URL")
for phrase in ('id="featuredEvents"','id="featuredContests"','id="samplecount"','id="contestcount"',
               'sample-events.json','contests.json','function renderSamples','function renderContests'):
 if phrase not in index:raise RuntimeError("Homepage missing a meaningful opportunity module "+phrase)
# NL-shipping foreign retailers are documented, but item-level NL delivery
# and complete checkout prices may not be asserted from shop-level policies.
intl=json.loads((ROOT/"international-stores.json").read_text(encoding="utf-8"))
if intl.get("destinationCountry")!="NL" or not isinstance(intl.get("retailers"),list):
 raise RuntimeError("International shops require an NL destination registry")
for shop in intl["retailers"]:
 for k in ("id","name","country","baseUrl","shippingPolicyUrl","shippingToNL"):
  if not isinstance(shop.get(k),str) or not shop[k]:
   raise RuntimeError("Foreign retailer missing "+k)
 if shop["shippingToNL"]!="confirmed_store_level":
  raise RuntimeError("International shop lacks explicit Netherlands delivery")
 if shop.get("productDeliveryVerified") is not False:
  raise RuntimeError("Unverified foreign item delivery must not be asserted")
 if not shop["baseUrl"].startswith("https://") or not shop["shippingPolicyUrl"].startswith("https://"):
  raise RuntimeError("International retailer URL must be secure")
for phrase in ('international-stores.json','id="internationalShops"','id="region"','function renderInternational'):
 if phrase not in index:raise RuntimeError("Dashboard missing foreign retailer integration "+phrase)
for row in data.get("offers",[]):
 if row.get("merchantCountry") and row.get("destinationCountry")=="NL" and row.get("allInVerified"):
  raise RuntimeError("Unverified foreign checkout must not be marked all-in")
if not (ROOT/"PRIVACY-EN-INTEGRATIE.md").exists():
 raise RuntimeError("Private data handling specification missing")
# Cross-shop article price comparisons are evidence-only, never realized savings.
comparisons=json.loads((ROOT/"price-comparisons.json").read_text(encoding="utf-8"))
if not isinstance(comparisons.get("comparisons"),list):raise RuntimeError("Comparison feed missing")
for entry in comparisons["comparisons"]:
 if entry.get("allInVerified") is not False or entry.get("purchaseSavingsVerified") is not False:
  raise RuntimeError("Unverified article price gap cannot be guaranteed saving")
 if len({x.get("store") for x in entry.get("offers",[])})<2:
  raise RuntimeError("Cross-shop comparison must involve independent stores")
 if entry.get("articlePriceDifferenceEUR",0)<=0:
  raise RuntimeError("Comparison must have a positive documented article price gap")
if 'id="comparablePrices"' not in index or 'price-comparisons.json' not in index or 'renderPriceComparisons' not in index:
 raise RuntimeError("Homepage missing comparable product prices")
# Audited money-saving strategies are not the same as a confirmed customer discount.
strategies=json.loads((ROOT/"bespaarstrategien.json").read_text(encoding="utf-8"))
if not isinstance(strategies.get("items"),list):raise RuntimeError("Savings strategies missing")
if len(strategies["items"])<7:raise RuntimeError("Strategies incomplete")
ids=set()
for st in strategies["items"]:
 if st.get("id") in ids:raise RuntimeError("Duplicate money-saving strategy")
 ids.add(st["id"])
 if not isinstance(st.get("actions"),list) or not st["actions"]:
  raise RuntimeError("Strategy missing concrete actions")
 if not str(st.get("url","")).startswith("https://"):
  raise RuntimeError("Strategy missing secure direct source URL")
 if st.get("sourceType") not in ("officiele_aanbieder","reddit_ervaringen"):
  raise RuntimeError("Strategy missing source evidence category")
html=(ROOT/"besparen.html").read_text(encoding="utf-8")
for phrase in ("bespaar-strategie-ui.mjs","bespaar-calculator.mjs" if False else "contractDealCompare",
               'id="strategyCards"','id="compareCurrent"','id="benefitType"'):
 if phrase not in html:raise RuntimeError("Savings calculator UI incomplete "+phrase)
workflow=(ROOT/".github/workflows/scan.yml").read_text(encoding="utf-8")
if "python strategie_scan.py" not in workflow or "node test_bespaar_calculator.mjs" not in workflow:
 raise RuntimeError("Recurring strategy research and tests not configured")
if "python scripts/household_scan.py" in workflow:
 raise RuntimeError("Grocery scanner must not be called from Kansenkompas")
# Homepage actions are proven editorial deadlines, never guesses from raw feeds.
for phrase in ('id="urgentActions"','id="urgentCount"','id="resetActions"','action-queue-ui.mjs'):
 if phrase not in index:raise RuntimeError("Personal action queue missing "+phrase)
# Paid savings remain solely local; public backend must never auto-assert receipt.
savings_page=(ROOT/"besparen.html").read_text(encoding="utf-8")
for phrase in ('id="ledger"','id="ledgerTotal"','id="ledgerConfirmed"',
               'id="ledgerAdd"','id="ledgerExport"','savings-ledger-ui.mjs',
               'id="resaleFeesWrap"','value="resale"'):
 if phrase not in savings_page:raise RuntimeError("Confirmed savings/gift resale UI missing "+phrase)
workflow=(ROOT/".github/workflows/scan.yml").read_text(encoding="utf-8")
for test in ('node test_action_queue.mjs','node test_savings_ledger.mjs','node test_bespaar_calculator.mjs'):
 if test not in workflow:raise RuntimeError("Savings/action test not scheduled: "+test)
print("Website and JSON quality checks passed.")
