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
EXCLUDED=(
 "win-rar.com","winrar.com","microsoft.com","merriam-webster.com",
 "dictionary.com","wikipedia.org","prijzenzolder.nl","gratiswinactie.nl",
 "prijsvragen.nl","gratiz.nl","loterij","casino","spelletjesweb",
 "reverso.net","wiktionary.org","wordreference.com","bab.la",
 "concoursparts.com","lasvegasconcours.com","dictionary.reverso.net",
)
PRIZE_TERMS=re.compile(
 r"\b(auto|fiat|car|fiets|bike|reis|vacation|holiday|vakantie|"
 r"keuken|kitchen|renovation|verbouwing|dyson|miele|apple|macbook|"
 r"iphone|laptop|scooter|e-bike|cadeaubon|tegoed|winactie)\b|€|\$|"
 r"\b\d[\d.,]*\s?(euro|euros)\b",re.I)
ACTIVE_VERBS=re.compile(
 r"\b(win\s+(?:een|de|het|an?|a|the|[€$]\s*\d)|"
 r"winactie|prijsvraag|verloot|verloting|giveaway|sweepstakes|"
 r"gagnez|gewinnspiel|wedstrijd\s*:\s*win)\b",re.I)
JUNK=re.compile(
 r"\b(lexicon|dictionary|definition|définition|signification|"
 r"parts and accessories|car show|schedule of events|festival|"
 r"ticket sales|dictionary|synonym|word meaning|how to win|de betekenis)\b",re.I)
CURRENT_YEAR=dt.datetime.now(dt.timezone.utc).year


def valid_candidate(title,link,description):
 """Return only plausible contest leads, not general pages or word meanings.

 The presence of 'concours' or 'win' as a substring is NOT a prize offer.
 Date/eligibility/value are unknown until the organizer is verified.
 """
 if not isinstance(title,str) or not isinstance(link,str):
  return False
 url=urllib.parse.urlsplit(link)
 if url.scheme!="https" or not url.hostname or url.username or url.password:
  return False
 host=url.hostname.lower()
 if any(x in host for x in EXCLUDED):
  return False
 if JUNK.search(title):
  return False
 if not ACTIVE_VERBS.search(title):
  return False
 if not PRIZE_TERMS.search(title+" "+description[:250]):
  return False
 if re.search(r"\b(20\d{2})\b",title):
  years=[int(y) for y in re.findall(r"\b(20\d{2})\b",title)]
  if max(years)<CURRENT_YEAR:
   return False
 return True


def search(q):
 url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"format":"rss"})
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 with urllib.request.urlopen(req,timeout=18) as response:
  root=ET.fromstring(response.read(800000))
 for entry in root.findall(".//item"):
  title=entry.findtext("title","").strip()
  link=entry.findtext("link","").strip()
  description=entry.findtext("description","").strip()
  if not valid_candidate(title,link,description):continue
  yield {"title":title[:180],"url":link,"snippet":description[:320],
         "origin":"Bing RSS zoekresultaat",
         "verificationStatus":"Onderzoekslead, niet geverifieerd: officiële prijswaarde, deadline, Nederlandse deelname en kosten controleren"}

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
