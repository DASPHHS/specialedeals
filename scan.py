#!/usr/bin/env python3
"""Public-source discovery. Never present unverifiable candidates as actual price deals."""
import datetime as dt
import html
import hashlib
import json
import re
import urllib.request
from deal_verification import verified_offers
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

SOURCES=[
 ("We Love Sample Sales","sales","https://www.welovesamplesales.nl/permaand/deze-maand"),
 ("Stockverkopen","sales","https://www.stockverkopen.nl/samplesales.html"),
 ("Your Sample Sale","sales","https://yoursamplesale.nl/evenementen/"),
 ("Eventbrite","sales","https://www.eventbrite.nl/d/netherlands/sample-sale/"),
 ("Chicmi","sales","https://www.chicmi.com/nl/sample-sales/"),
 ("GratiZ","contests","https://www.gratiz.nl/prijsvragen"),
 ("Prijsvragen.nl","contests","https://www.prijsvragen.nl/"),
 ("Gratiswinactie","contests","https://gratiswinactie.nl/"),
 ("AlleFolders","deals","https://www.allefolders.nl/aanbiedingen"),
 ("Reclamefolder","deals","https://www.reclamefolder.nl/categorieen/"),
 ("Pepper","deals","https://nl.pepper.com/"),
 ("SuperSales","deals","https://www.supersales.nl/"),
 ("Amac Apple aanbiedingen","deals","https://www.amac.nl/sale/aanbiedingen"),
 ("Bever sale","deals","https://www.bever.nl/c/aanbiedingen.html"),
 ("Bergfreunde sale","deals","https://www.bergfreunde.nl/outlet/"),
 ("Bergzeit sale","deals","https://www.bergzeit.nl/outlet/"),
]
SIGNALS={"sales":("sample sale","stock sale","stockverkoop","stock sale","merkkleding","archive sale","outlet sale","warehouse sale","sample-sale","/sample","stock-sale","stockverkoop","sample sale"),
"contests":("win een","win de","win het","win 2","win 5","winactie","prijsvraag","giveaway","winnen","/winactie/"),
"deals":("aanbieding","korting","deal","outlet","sale","2+1","1+1","aanbiedingen","discount")}
LIKES=("padel","sport","schoenen","heren","menswear","premium","sneaker","hoka","apple","dyson","rituals","airpods","macbook","watch ultra","nike","adidas","tommy","ralph","kuyichi","vakantie","reizen","reis","cadeaubon","geld","shoptegoed","laptop","fashion","denim","super sale","ticket","elektronica","koffie")
NOISE=("baby","kinderspeelgoed","kinderwagen","loterij","gokken","casino","speelgoedfolder","/privacy","/cookies","/contact","/login","/tag/","/categorie/","/category/")
class Links(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.href=None;self.text=[];self.active=False
 def handle_starttag(self,tag,attrs):
  if tag=="a" and not self.active:
   self.href=dict(attrs).get("href","");self.text=[];self.active=True
 def handle_data(self,data):
  if self.active:self.text.append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.active:
   title=" ".join(" ".join(self.text).split())
   if title and self.href:self.links.append((title,self.href))
   self.active=False
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; DealsRadar/2.0; public-listings)","Accept-Language":"nl-NL,nl;q=0.9"})
 with urllib.request.urlopen(req,timeout=20) as response:
  if response.status!=200:raise ValueError("HTTP "+str(response.status))
  return response.read(2500000).decode("utf-8","replace")
def score(title,kind):
 t=title.casefold();value=45
 value+=sum(8 for word in LIKES if word in t)
 if kind=="sales":value+=25
 if any(w in t for w in ("arc\'teryx","arcteryx","hoka","janzen","dyson","airpods pro","airpods","macbook","watch ultra")):value+=20
 if kind=="contests":value+=22
 if "kinderen" in t or "kidswear" in t:value-=8
 if "dames" in t or "womenswear" in t:value+=2
 if "heren" in t or "menswear" in t:value+=8
 if any(n in t for n in NOISE):value-=70
 return min(100,max(0,value))

def is_navigation(title,url,kind):
 t=title.casefold().strip()
 p=urlsplit(url).path.casefold().rstrip("/")
 generic=("sample sales","sample sale","stockverkopen","alle aanbiedingen","actuele aanbiedingen","winacties","prijsvragen","womenswear sample sales","menswear sample sales","schoenen sample sales","dames- en herenmode sample sales","alle winacties")
 if t in generic:return True
 if any(z in t for z in (" sample sales per ","sample sales deze ","inloggen","meer aanbiedingen","alle folders","nieuwste folders","contact opnemen","bekijk alle","onze nieuwsbrief","volg ons","prijsvragen en antwoorden","van vandaag","per provincie","per maand","per week")):return True
 if re.search(r"/(categorie|category|categories|merken|brand|brands|tags|tag|permaand|perweek|samplesales-per-provincie|show_verkoop_provincie|zoek|search|aanbiedingen)$",p):return True
 if kind=="sales" and re.search(r"^(heren|dames|womenswear|menswear|kleding|schoenen|accessoires|kidswear|lingerie)\s+(sample sales|stockverkopen)$",t):return True
 if kind=="contests" and not re.search(r"\bwin\b|winactie|geef weg|prijsvraag|verloot|gratis",t):return True
 return False


# Conservative prefilter: only potentially substantial prizes. Unknown value is
# excluded from the daily shortlist rather than portrayed as a major win.
BIG_PRIZES=("vakantie","droomreis","reis naar","weekend weg","hotelovernachting","hotelverblijf","cruise","vliegtickets","elektrische fiets","e-bike","bakfiets","auto winnen","win een auto","win een elektrische auto","scooter","macbook","ipad","iphone","laptop","playstation","televisie","tv winnen","dyson","robotstofzuiger","jaar lang","jaarlang","verbouwing","keuken winnen","hypotheek","geldprijs","geldbedrag","cashprijs","€ 500","€500","€ 1.000","€1000","€ 2.000","€2000","€ 5.000","€5000","cadeaubon van € 250","cadeaubon van €250","tegoed van € 250","tegoed van €250")

# Leads for major prizes; discovery is NOT official verification.
HIGH_VALUE_PRIZE_TERMS=(
 "complete keuken","nieuwe keuken","gratis keuken","keukenrenovatie",
 "wasmachine","wasdroger","droger","vaatwasser","koelkast","vriezer","witgoed",
 "carwrap","car wrap","auto wrappen","carwrapping","wrapbeurt",
 "boormachine","zaagmachine","accuboormachine","gereedschapset","gereedschapsset",
 "makita","dewalt","bosch professional","miele","steelstofzuiger","stofzuiger",
 "hogedrukreiniger","robotmaaier","tuinmachine","koffiemachine","espressomachine",
 "smartphone","robotstofzuiger","apple watch","samsung galaxy","a-merk"
)
TRIVIAL=("win een boek","win boeken","win een cd","win een dvd","win een mok","win een pen","win stickers","win een sleutelhanger","win een proefpakket","win een sample","win een goodiebag","win kaartjes","win tickets","win een ticket","win een bioscoopkaart","win een puzzel","win een tijdschrift","win een t-shirt","win een beautybox","win een pakket","enquête","survey","leadgeneratie","postcode loterij","vriendenloterij","staatsloterij","kansspel")
def worthwhile_contest(title,url):
 t=title.casefold()
 if any(x in t for x in TRIVIAL):return False
 # An explicit euro prize may qualify only when at least EUR 250.
 eurovalues=[]
 for amount in re.findall(r"€\s*(\d[\d.,]*)",t):
  cleaned=amount.rstrip(".,")
  if "," in cleaned:
   cleaned=cleaned.split(",")[0]
  try:eurovalues.append(int(cleaned.replace(".","")))
  except ValueError:pass
 if eurovalues:
  return max(eurovalues)>=250
 return any(key in t for key in BIG_PRIZES+HIGH_VALUE_PRIZE_TERMS)


CATEGORIES={
 "Huis & tuin":("keuken","wasmachine","vaatwasser","koelkast","stofzuiger","machine","tuin","woning","huis","meubel","interieur","keuken","verbouw","badkamer","gereedschap","robotmaaier","terras","bankstel"),
 "Auto's & mobiliteit":("carwrap","auto wrappen","carwrapping","auto","tesla","volvo","bmw","elektrische fiets","e-bike","fiets","bakfiets","scooter","mobiliteit"),
 "Vakanties & reizen":("vakantie","reis","hotel","cruise","vliegticket","weekend weg","overnachting","reisvoucher","reischeque"),
 "Uitjes & belevenissen":("concert","festival","dagje uit","pretpark","diner","restaurant","wellness","spa","belevenis","tickets"),
 "Geld & tegoed":("geld","cash","euro","shoptegoed","winkeltegoed","waardebon","cadeaubon","tegoed","hypotheek"),
 "Elektronica":("iphone","ipad","macbook","apple","dyson","laptop","playstation","televisie","tv","smartphone","koptelefoon","tablet"),
 "Gratis spullen & producten":("gratis","pakket","product","schoenen","kleding","parfum","verzorging","sport","racket")
}
def classify(title,kind):
 t=title.casefold()
 if kind=="sales":return "Sample sales"
 if kind=="deals":
  if any(w in t for w in CATEGORIES["Huis & tuin"]):return "Huis & tuin"
  if any(w in t for w in ("airpods","macbook","watch ultra")):return "Apple & elektronica"
  if any(w in t for w in CATEGORIES["Elektronica"]):return "Elektronica"
  if any(w in t for w in ("terrasoverkapping","overkapping","veranda","tuinrenovatie","isolatie","warmtepomp","schuur renoveren","schilderwerk")):return "Huisprojecten & verduurzaming"
  if any(w in t for w in ("rituals","janzen","parfum","verzorging","shampoo","beauty","skincare")):return "Verzorging & beauty"
  if any(w in t for w in ("schoen","kleding","shirt","jas","nike","adidas","mode")):return "Mode & schoenen"
  return "Overige deals"
 for category, words in CATEGORIES.items():
  if any(w in t for w in words):return category
 return "Overige waardevolle prijzen"


# Quality gate: discovery is not verification. Do not publish aggregator-only
# competition leads as suitable personal recommendations.
DEAL_JUNK=("sokken","wollen sok","wol sok","onderbroek","boxershort","veters","schoenlepel","sleutelhanger","theedoek","washand","katoenen tas","baby","kinder","speelgoed","telefoonhoes","screenprotector","sticker","mok","pennen","t-shirt","basic shirt")
PREMIUM_MATCH=("terrasoverkapping","veranda","overkapping","tuinaanleg","tuinrenovatie","isolatie","warmtepomp","schuur","schilderwerk","hogedrukreiniger","janzen earth","janzen","rituals","janzen","marie-stella-maris","davines","weleda","dyson","apple","ipad","iphone","macbook","airpods","watch ultra","hoka","arc'teryx","ralph lauren","tommy hilfiger","nike","adidas","padelracket","padel racket","lego technic","koffiemachine","espresso","robotstofzuiger","gereedschapsset","tuinmeubel")
PREMIUM_SALE_BRANDS=("arc'teryx","arcteryx","nike","adidas","ralph lauren","tommy hilfiger","scotch & soda","scotch and soda","kuyichi","circle of trust","vanguard","state of art","cast iron","pme legend","g-star","g star","boss","hugo boss","new balance","asics","lacoste","calvin klein","polo","dyson","rituals","janzen","marie-stella-maris","my jewellery","love stories","sandro","maje","ba&sh","denham","daily paper")
DEAL_SIGNALS=("70%","60%","50%","40%","35%","30%","€ 100","€100","€ 150","€150","€ 200","€200","€ 250","€250","halve prijs","2 halen 1 betalen","1+1 gratis")

# Enig gewenst outdoor-merk is Arc'teryx. HOKA is uitsluitend een
# apart, expliciet gewenst hardloopschoenenproduct op de verlanglijst.
OUTDOOR_EXCLUDED_BRANDS=(
 "salomon","patagonia","norrøna","norrona","mammut","rab","fjällräven",
 "fjallraven","the north face","jack wolfskin","columbia","vaude",
 "haglofs","haglöfs","ortovox","helly hansen","peak performance",
 "black diamond","protest","bergans","marmot","montane","cotopaxi",
 "mountain equipment","berghaus","regatta","lowe alpine",
)
OUTDOOR_SOURCE_NAMES=("Bever sale","Bergfreunde sale","Bergzeit sale")
OUTDOOR_GENERIC_TERMS=(
 "outdoor","outdoorschoen","wandel","hiking","trekking","hardshell",
 "softshell","bergwandelen","bergklimmen","bergkleding","klimjas",
 "fleecejack","gore-tex","gore tex","wandelrugzak",
)
def arcteryx_mentioned(title):
 t=title.casefold().replace("’","'")
 return "arc'teryx" in t or "arcteryx" in t

def unwanted_outdoor(title,source=""):
 t=title.casefold().replace("’","'")
 if any(re.search(r"(?<!\w)"+re.escape(brand)+r"(?!\w)",t)
        for brand in OUTDOOR_EXCLUDED_BRANDS):
  return True
 if arcteryx_mentioned(title):return False
 if source in OUTDOOR_SOURCE_NAMES:return True
 if any(word in t for word in OUTDOOR_GENERIC_TERMS):return True
 return False


# Wishlist title matches are unverified leads, not validated product variants.
def wishlist_hits(title, wishlist_items):
 t=title.casefold().replace("’","'")
 hits=[]
 for item in wishlist_items:
  patterns=item.get("matchAny") or item.get("keywords") or []
  if not any(str(k).casefold().replace("’","'") in t for k in patterns):continue
  if any(str(k).casefold().replace("’","'") in t for k in item.get("excludeTerms",[])):continue
  if item.get("id")=="dyson-handstofzuiger" and "dyson" not in t and "stofzuiger" not in t:continue
  hits.append(item["id"])
 return hits

APPLE_ACCESSORY_TERMS=(
 "airpods hoes","airpods case","airpods cover","airpods oplaadcase",
 "airpods bescherm","airpods accessoire","macbook hoes","macbook case",
 "macbook cover","macbook lader","macbook sleeve","watch ultra band",
 "watch ultra strap","watch ultra hoes","watch ultra cover",
 "apple watch ultra band","apple watch ultra strap",
)
def generic_apple_accessory(title):
 t=title.casefold()
 if any(x in t for x in APPLE_ACCESSORY_TERMS):return True
 # Avoid navigation, accessories and comparison pages masquerading as products.
 if re.match(r"^(?:apple\s+)?(?:alle\s+)?airpods[\s-]*(?:modellen|vergelijken|accessoires|accessory|accessories)\b",t):return True
 if re.search(r"^(?:alle\s+)?(?:macbooks?|apple\s+watch(?:\s+ultra)?)\s+(?:vergelijken|modellen|accessoires)\b",t):return True
 return False

def high_quality_candidate(title,kind,source=""):
 if unwanted_outdoor(title,source):return False
 if generic_apple_accessory(title):return False
 t=title.casefold()
 if kind=="sales":
  return any(brand in t for brand in PREMIUM_SALE_BRANDS)
 if kind=="deals":
  if re.fullmatch(r"(?:arc[\u0027\u2019]?teryx|arcteryx)\s*(?:\(\d+\))?",t):return False
  if any(w in t for w in DEAL_JUNK):return False
  # No undifferentiated ordinary folder products in curated results.
  return any(w in t for w in PREMIUM_MATCH) or any(w in t for w in DEAL_SIGNALS)
 if kind=="contests":
  # Aggregator result is only a lead. Real organizer vetting is not implemented.
  # Do not disguise it as a recommendation on the public site.
  return False
 return True

def official_contests(now):
 """Explicitly curated organizer records. Never infer verification from aggregator text."""
 with open("verified-winacties.json",encoding="utf-8") as f:entries=json.load(f)["contests"]
 today=dt.datetime.now(dt.timezone.utc).date().isoformat()
 return [{**v,"id":"official-"+v["id"],"kind":"contests","source":v["organizer"],"audience":"all","score":95,"discoveredAt":now,"lastSeenAt":now,"status":"Voorwaarden gecontroleerd"} for v in entries if v.get("startDate","")<=today<=v.get("endDate","") and v.get("officialTermsUrl")]


def duplicate_key(item):
 # Merge identical visible offers even when tracking parameters or path variants differ.
 name=re.sub(r"[^a-z0-9]+"," ",item.get("title","").casefold()).strip()
 origin=re.sub(r"[^a-z0-9]+"," ",item.get("source","").casefold()).strip()
 return (item.get("kind",""),origin,name)

def unique_offers(rows):
 seen=set();out=[]
 for item in rows:
  key=duplicate_key(item)
  if key in seen:continue
  seen.add(key);out.append(item)
 return out

def main():
 with open("winactie-profiel.json",encoding="utf-8") as f:contest_profile=json.load(f)
 with open("wishlist.json",encoding="utf-8") as f:wishlist=json.load(f)
 wishlist_items=wishlist.get("items",[])
 with open("radar-profiel.json",encoding="utf-8") as f:radar_profile=json.load(f)
 minimum=contest_profile["minimumPrizeValueEUR"]
 with open("verified-deals.json",encoding="utf-8") as f:verified_deal_records=json.load(f)
 deal_candidates={}
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 today=dt.date.today().isoformat()
 try:
  with open("data.json",encoding="utf-8") as f:old=json.load(f)
 except (ValueError,OSError):old={"items":[]}
 # Retain previous recent discoveries only if they are younger than 7 days; do not imply new verification.
 items={x["id"]:x for x in old.get("items",[]) if x.get("kind")=="sales" and x.get("id") and x.get("discoveredAt","")[:10]>=str(dt.date.today()-dt.timedelta(days=7)) and not is_navigation(x.get("title",""),x.get("url",""),x.get("kind","")) and high_quality_candidate(x.get("title",""),x.get("kind",""),x.get("source","")) and (x.get("kind")!="contests" or worthwhile_contest(x.get("title",""),x.get("url","")))}
 statuses=[]
 for name,kind,base in SOURCES:
  try:
   p=Links();p.feed(fetch(base));count=0
   for title,href in p.links:
    if not 12<=len(title)<=160:continue
    url=urljoin(base,html.unescape(href));parts=urlsplit(url)
    if parts.scheme!="https" or not parts.hostname:continue
    if any(x in url.casefold() for x in ("/privacy","/cookie","/contact","/account","/login","facebook.com","instagram.com")):continue
    if is_navigation(title,url,kind):continue
    if not high_quality_candidate(title,kind,name):continue
    matched_wishes=wishlist_hits(title,wishlist_items)
    if kind=="contests" and not worthwhile_contest(title,url):continue
    phrase=(title+" "+parts.path).casefold()
    if not any(signal in phrase for signal in SIGNALS[kind]) and not (kind=="deals" and matched_wishes and name=="Amac Apple aanbiedingen"):continue
    rank=score(title,kind)
    if matched_wishes:rank=min(100,rank+30)
    if rank<35:continue
    ident=hashlib.sha256((kind+" "+url.split("?")[0]).encode()).hexdigest()[:20]
    # Unverified product links remain discovery data, never storefront deals.
    if kind=="deals":
     deal_candidates[ident]={"id":ident,"title":title,"url":url,"source":name,"wishlistMatches":matched_wishes,"detectedAt":now,"status":"Niet geverifieerd: actuele prijs en vergelijking ontbreken"}
     count+=1
     continue
    if ident in items:items[ident]["lastSeenAt"]=now;items[ident]["category"]=classify(title,kind);items[ident]["wishlistMatches"]=matched_wishes;count+=1;continue
    audience="women" if ("womenswear" in phrase or "dames" in phrase) and "heren" not in phrase and "menswear" not in phrase else "men" if ("heren" in phrase or "menswear" in phrase) and "dames" not in phrase else "all"
    items[ident]={"id":ident,"kind":kind,"title":title,"description":("Evenementvermelding. Controleer plaats, datum, maten, tickets en prijzen bij de organisator." if kind=="sales" else "Gevonden prijsvraag. Controleer gratis deelname, looptijd en Nederlandse toelating." if kind=="contests" else "Aanbiedingssignaal. Controleer artikel, echte prijs, voorraad en eventuele winkelafstand."),"source":name,"url":url,"category":classify(title,kind),"wishlistMatches":matched_wishes,"priceVerified":False,"status":"Waarde en voorwaarden controleren" if kind=="contests" else "Te controleren","score":rank,"audience":audience,"discoveredAt":now,"lastSeenAt":now}
    count+=1
   statuses.append({"name":name,"status":"ok","count":count})
  except Exception as e:statuses.append({"name":name,"status":"error","count":0,"error":str(e)[:120]})
 # Conservative expiration until explicit date parsing is available.
 for record in items.values():
  record["category"]=classify(record.get("title",""),record.get("kind",""))
  record["wishlistMatches"]=wishlist_hits(record.get("title",""),wishlist_items)
  if record.get("kind")=="deals":record["priceVerified"]=False
 approved=verified_offers(verified_deal_records.get("deals",[]),minimum=radar_profile.get("deals",{}).get("minimumRealDiscountPercent",10))
 rows=unique_offers(approved+official_contests(now)+sorted(items.values(),key=lambda x:(-x["score"],x["title"])))[:450]
 with open("deal-kandidaten.json","w",encoding="utf-8") as f:
  json.dump({"updatedAt":now,"items":list(deal_candidates.values())[:300],"notice":"Discovery only, not a confirmed deal, no automatic advertised discount proof"},f,ensure_ascii=False,indent=2)
 result={"updatedAt":now,"items":rows,"sources":statuses,"wishlistLastRead":wishlist.get("updatedAt"),"radarProfileLastRead":radar_profile.get("updatedAt"),"minDealDiscountPercent":radar_profile.get("deals",{}).get("minimumRealDiscountPercent",10),"dealCandidates":len(deal_candidates),"wishlistProducts":[{"id":x["id"],"name":x["name"],"category":x.get("category",""),"maxPriceEUR":x.get("maxPriceEUR")} for x in wishlist_items],"contestProfile":{"minimumPrizeValueEUR":minimum,"newsletterPolicy":contest_profile["newsletterPolicy"],"preferredPrizeCategories":contest_profile["preferredPrizeCategories"]},"note":"Only manually checked organizer records appear among winacties; source timestamps show scan time, not automatic re-verification of terms."}
 with open("data.json","w",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"total":len(rows),"reachable":sum(s["status"]=="ok" for s in statuses),"status":statuses},ensure_ascii=False))
if __name__=="__main__":main()
