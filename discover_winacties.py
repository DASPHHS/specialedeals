#!/usr/bin/env python3
"""Find possible high-value giveaways, separately from manually verified contests."""
import datetime as dt
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

QUERIES=[
 "win auto 2026 gratis actievoorwaarden site:.nl",
 "win fiat keuken auto vakantie gratis winactie 2026",
 "win keuken renovatie overkapping 2026 officiële actie",
 "win reis vakantie 5000 euro 2026 winactie",
 "win dyson miele wasmachine 2026 winkel actievoorwaarden",
 "win elektrische fiets 2026 gratis",
 "wibra anwb hema kruidvat gamma praxis winactie hoofdprijs 2026",
 "international giveaway 2026 open to Netherlands residents official terms prize",
 "EU sweepstakes 2026 Netherlands eligible win car trip electronics",
 "Gewinnspiel Niederlande Teilnahme erlaubt 2026 Auto Reise",
 "concours ouvert aux résidents des Pays-Bas voyage 2026 règlement",
 "Belgium winactie Nederland inwoners deelname 2026 hoofdprijs",
 "UK Europe giveaway Netherlands eligible official rules 2026",
]
EXCLUDED=("win-rar.com","winrar.com","microsoft.com","merriam-webster.com","dictionary.com","wikipedia.org","prijzenzolder.nl","gratiswinactie.nl","prijsvragen.nl","gratiz.nl","loterij","casino","spelletjesweb")
def search(q):
 url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"format":"rss"})
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 with urllib.request.urlopen(req,timeout=18) as response:
  root=ET.fromstring(response.read(800000))
 for entry in root.findall(".//item"):
  title=entry.findtext("title","").strip()
  link=entry.findtext("link","").strip()
  if not link.startswith("https://") or any(x in link.lower() for x in EXCLUDED):continue
  if not re.search(r"\b(win (?:een|de|het|an?|a|the)|giveaway|sweepstakes|gewinnspiel|concours|gagnez|verloting|verloot|prijsvraag|winactie|wedstrijd)\b",title,re.I):continue
  if not re.search(r"auto|fiat|car\b|fiets|bike|reis|vacation|holiday|vakantie|keuken|kitchen|renovation|verbouwing|dyson|miele|apple|macbook|iphone|€|eur|\$|[0-9][.,]?[0-9]*\s?(euro|euros)",title+" "+entry.findtext("description",""),re.I):continue
  yield {"title":title[:180],"url":link,"snippet":entry.findtext("description","")[:320],"verificationStatus":"Niet bevestigd: Nederlandse deelname, prijswaarde, deadline en internationale levering expliciet bij organisator controleren"}

def main():
 results={}
 errors=[]
 for query in QUERIES:
  try:
   for item in search(query):
    results[item["url"].split("?")[0]]=item
  except Exception as err:errors.append({"query":query,"error":str(err)[:120]})
 out={"updatedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"status":"Alleen zoekkandidaten. Niet aanbevelen zonder officieel bewijs van NL-toelating, kosteloosheid, concrete waarde en levering","items":list(results.values())[:100],"errors":errors}
 with open("winactie-kandidaten.json","w",encoding="utf-8") as fp:json.dump(out,fp,ensure_ascii=False,indent=2)
 print("Candidates:",len(out["items"]),"Source failures:",len(errors))
if __name__=="__main__":main()
