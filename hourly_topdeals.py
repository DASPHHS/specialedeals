#!/usr/bin/env python3
"""Re-rank the current licensed/public Weekdeals snapshots every hour.

No source is represented as re-checked merely because this index is rebuilt.
Unknown shipping, EAN/variant and retailer-reference discounts are not verified
consumer savings. Product pages are not contacted by this indexer.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from datetime import datetime, date, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from wishlist_radar import matches as matches_wish, valid_url, price_value

ROOT=Path(__file__).resolve().parent
ZONE=ZoneInfo("Europe/Amsterdam")
OUT=ROOT/"topdeals"/"data.json"
ORDER=["persoonlijk","supermarkt","tuin","bouwmarkt","drogisterij","elektronica","sport","huis","overig"]
LABELS={
 "persoonlijk":"Mijn verlanglijst",
 "supermarkt":"Supermarkt & boodschappen",
 "tuin":"Tuin & buiten",
 "bouwmarkt":"Bouwmarkt & klussen",
 "drogisterij":"Drogisterij & verzorging",
 "elektronica":"Elektronica & gadgets",
 "sport":"Sport & outdoor",
 "huis":"Wonen & huishouden",
 "overig":"Overige buitenkansjes"
}
BUILD=re.compile(r"\b(verf|kwast|roller|schuurmachine|schroef|boor|accu|gereedschap|kitpistool|kitten|isolatie|bouwmarkt|hout|tegels?|bouwmateriaal|laminaat|verfroller|makita|dewalt|bosch professional|gamma|praxis|hornbach)\b",re.I)
GARDEN=re.compile(r"\b(tuin|tuinmeubel|tuinstoel|bloempot|potgrond|plant|planten|bloem|zaden|gazon|barbecue|bbq|grasmaaier|heggenschaar|tuinslang|terras|loungeset|hortensia|kerstboom)\b",re.I)
TECH=re.compile(r"\b(apple|airpods|macbook|imac|iphone|ipad|usb.?hub|usb4|thunderbolt|docking|ssd|laptop|oled|headphone|bluetooth|smartphone|dyson|elektronica|televisie|koptelefoon)\b",re.I)
SPORT=re.compile(r"\b(hoka|arc.?teryx|padel|hardloop|hardlopen|sportschoen|sportkleding|racket|sportartikel|fitness|tennis|outdoor|sneaker)\b",re.I)
CARE=re.compile(r"\b(rituals|janzen|douche|shampoo|deodorant|tandpasta|parfum|schoonheid|verzorging|gezondheid|cosmetica|crème|creme|vitamine|bodylotion|douglas|melatonine|lucovitaal)\b",re.I)
HOME=re.compile(r"\b(huishoud|wasmiddel|vaatwas|allesreiniger|stofzuiger|schoonmaak|opbergen|dekbed|kussen|servies|kaars|keukenrol|toiletpapier|woonaccessoire|wonen|inrichting)\b",re.I)
FOODCAT={"groceries","coffee & tea","sweets & snacks","meat & fish","bread & bakery",
         "biscuits & cakes","soft drinks & juices","vegetables & fruit","bakery",
         "dairy","frozen","snacks","drinks","supermarkt","eten & drinken","beverages"}
CARECAT={"health & beauty","drogisterij","personal care","beauty"}
NOISE=re.compile(r"\b(loterij|casino|loten|gok|seks|erotiek|vape|nicotine|alcohol|wijn|bier|whisky)\b",re.I)


def classify(row,source_id=None):
    """Use source/category first. Ambiguous words alone MUST NOT decide domain.

    'Bloem' in a fragrance isn't a garden flower, 'roller' is not a DIY roller,
    'apple' can be food or beer, and 'BBQ' in a pizza isn't a barbecue unit.
    """
    title=str(row.get("product") or "")
    cat=str(row.get("categorie") or "").lower().strip()
    store=str(row.get("winkel") or "").lower().strip()
    source=str(row.get("bron") or source_id or "")
    text=title.casefold()
    # Product groups with genuinely distinctive commercial terms.
    actual_build=re.search(
        r"\b(accuboormachine|accuschroefmachine|boormachine|klopboormachine|"
        r"schuurmachine|kettingzaag|decoupeerzaag|cirkelzaag|boorset|schroefset|"
        r"schroevendraaier|verfroller|verfbak|schilderstape|verfkwast|"
        r"muurverf|lakverf|kitpistool|tegelzaag|isolatieplaat|"
        r"bouwlaser|gereedschapskoffer|werkbank|elektrische zaag)\b",text)
    actual_garden=re.search(
        r"\b(potgrond|tuinaarde|tuinstoel|tuinset|tuinbank|tuinmeubel|"
        r"bloempot|plantenpot|tuinplant|kamerplant|tuinslang|"
        r"grasmaaier|robotmaaier|heggenschaar|bladblazer|"
        r"hogedrukreiniger|tuingereedschap|tuinverlichting|"
        r"terrashaard|vuurkorf|barbecue toestel|barbecue grill|bbq grill|"
        r"loungeset|tuinkussen|tuintafel|plantenbak)\b",text)
    actual_tech=re.search(
        r"\b(airpods|macbook|imac|iphone|ipad|apple watch|apple tv|"
        r"usb4|thunderbolt|usb.?hub|dockings?tation|monitor|"
        r"televisie|smartphone|koptelefoon|bluetooth speaker|"
        r"powerbank|laptop|gaming console|"
        r"oled scherm|draadloze oordopjes)\b",text)
    actual_sport=re.search(
        r"\b(hoka|arc.?teryx|padelballen|padelracket|tennisracket|"
        r"hardloopschoenen|sportschoenen|sportjack|outdoorjas|"
        r"voetbalschoenen|yogamat|fitnessapparaat|outdoor.?jas|"
        r"outdoor sweatjack)\b",text)
    actual_home=re.search(
        r"\b(wasmiddel|vaatwastabletten|wasverzachter|toiletpapier|"
        r"toiletblok|allesreiniger|afwasmiddel|keukenrol|"
        r"stofzuiger|schoonmaakmiddel|luchtverfrisser|"
        r"geurproducten|waspods|wasmiddelpods|wasmiddel capsules|"
        r"afwasblokjes|ariel.*pods|robij[n]? quickwash|boodschappentas|opbergbox)\b",text)
    if actual_build:return "bouwmarkt"
    if actual_garden:return "tuin"
    if actual_tech:return "elektronica"
    if actual_sport:return "sport"
    if actual_home:return "huis"
    if store=="intratuin" or any(s in cat for s in ("tuin & wonen","tuinartikelen","garden")):
        return "tuin"
    if any(s in cat for s in ("bouwmarkt","klus","gereedschap","diy")):
        return "bouwmarkt"
    if any(s in cat for s in ("elektronica","computer","multimedia")):
        return "elektronica"
    if any(s in cat for s in ("sportartikelen","hardlopen","outdoor")):
        return "sport"
    if any(s in cat for s in ("cleaning & laundry","household","huishoudelijk",
                               "schoonmaak","wasmiddelen","woningonderhoud")):
        return "huis"
    # Food always wins against false brand or scent keyword matches.
    if cat in FOODCAT or any(s in cat for s in (
        "groente","fruit","vlees","vis","brood","bakkerij","zuivel","melk",
        "diepvries","bier","wijn","dranken","snoep","chocolade","pizza",
        "broodbeleg","ijs &","chips","koek","koffie","thee",
        "aardappelen","rijst &","pasta","babyvoeding","voeding")):
        return "supermarkt"
    if cat in CARECAT or any(s in cat for s in ("verzorging","drogisterij",
        "gezondheid","beauty","health","cosmetica","personal care")):
        return "drogisterij"
    if source=="PrijsProfeet":
        # The PrijsProfeet feed is supermarket-based. Do not infer DIY/tech
        # from vaguely similar words when the category is unspecified.
        return "supermarkt"
    if store in ("kruidvat","etos","trekpleister","da"):
        if CARE.search(title):return "drogisterij"
        return "overig"
    if GARDEN.search(title) and ("outdoor" in cat or "garden" in cat):
        return "tuin"
    if HOME.search(title):return "huis"
    if CARE.search(title):return "drogisterij"
    return "overig"

def date10(value):
    v=str(value or "")[:10]
    try:return date.fromisoformat(v)
    except ValueError:return None


def when(value):
    try:
        stamp=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return stamp if stamp.tzinfo is not None else None
    except (ValueError,TypeError):return None


def source_health(source,now):
    stamp=when(source.get("updated_at") or source.get("updatedAt"))
    age=round((now-stamp.astimezone(now.tzinfo)).total_seconds()/3600,1) if stamp else None
    # A snapshot from >48 h ago cannot support a new consumer shortlist.
    ok=age is not None and 0<=age<=48
    return {"source":str(source.get("source") or "?"),"sourceUpdatedAt":stamp.isoformat() if stamp else None,
            "ageHours":age,"usable":ok,"offersInSnapshot":len(source.get("deals",[]))}


def asserted_discount(row):
    """Advertised store discount only, *never* independently verified saving."""
    if row.get("bundelaantal") or row.get("prijstype")=="bundeltotaal":
        return None
    p=price_value(row.get("prijs"))
    ref=price_value(row.get("van_prijs"))
    direct=row.get("korting")
    calculated=(ref-p)/ref if p is not None and ref is not None and ref>p else None
    if calculated is None:return None
    if isinstance(direct,(int,float)) and not isinstance(direct,bool):
        # Dissimilar references are ambiguous, not proof.
        if 0<float(direct)<=1 and abs(calculated-float(direct))<=0.04:
            return round(100*calculated,1)
        return None
    return round(100*calculated,1)


def eligible(row,now):
    """Only current, individually priced listings with traceable HTTPS URLs."""
    if not isinstance(row,dict) or not valid_url(row.get("url")):return False
    product=str(row.get("product") or "").strip()
    if not 5<=len(product)<=240 or NOISE.search(product):return False
    if price_value(row.get("prijs")) is None:return False
    today=now.date()
    start=date10(row.get("van"))
    end=date10(row.get("tot"))
    observed=date10(row.get("waargenomen_op"))
    if start and start>today:return False
    if end is not None:return end>=today
    # Unknown deadline: the source explicitly has to have been observed today.
    return observed==today


def normalize_name(value):
    s=unicodedata.normalize("NFKD",str(value or "").casefold())
    return " ".join(re.sub(r"[^a-z0-9]+"," ","".join(c for c in s if not unicodedata.combining(c))).split())


def wish_matches(row,wishes):
    title=str(row.get("product") or "")
    # Conservative: brand+model title is a research lead; exact size/ANC/stock not proved.
    return [{"id":w["id"],"name":w["name"]} for w in wishes if matches_wish(title,w)]


def quality(row):
    url=urlsplit(str(row.get("url") or ""))
    direct=("da.nl","intratuin.nl")
    host=(url.hostname or "").lower()
    is_direct=any(host==d or host.endswith("."+d) for d in direct) and "/product/" in url.path
    return ("Officiële productpagina; lokale voorraad/verzending niet gecontroleerd" if is_direct
            else "Bronoverzicht of externe productfeed; exacte productpagina/voorraad niet bevestigd"),is_direct


def pick(row,wishes,source_id):
    names=wish_matches(row,wishes)
    p=price_value(row.get("prijs"))
    discount=asserted_discount(row)
    note,direct=quality(row)
    group=classify(row,source_id)
    # Personal matches at top. Real source evidence quality matters more than high %
    # from a store MSRP. Always penalize uncheckable bundles.
    score=(135 if names else 0)+(20 if direct else 5)
    score+=min(25,discount*.35) if discount is not None else 0
    score+=10 if row.get("ean") else 0
    if row.get("einddatum_geschat") or row.get("einddatum_onbekend"):score-=5
    if row.get("ledenprijs") is not None:score-=4
    score+={"tuin":12,"bouwmarkt":15,"huis":10,"drogisterij":8,"supermarkt":5,
            "elektronica":14,"sport":14}.get(group,2)
    if p<=1.5:score-=3
    return {
        "id":str(row.get("id") or "")[:130], "title":str(row["product"])[:240],
        "shop":str(row.get("winkel") or "?")[:80], "category":group,
        "source":str(row.get("bron") or source_id)[:90],
        "url":str(row["url"]),
        "priceEUR":p,"unitPriceEUR":row.get("eenheidsprijs") if isinstance(row.get("eenheidsprijs"),(int,float)) else None,
        "unit":str(row.get("eenheid") or "")[:60] or None,
        "advertisedReferenceEUR":price_value(row.get("van_prijs")) if discount is not None else None,
        "advertisedDiscountPercent":discount,
        "offerType":str(row.get("actievorm") or "")[:100] or None,
        "startDate":str(row.get("van") or "")[:10] or None,
        "endDate":str(row.get("tot") or "")[:10] or None,
        "dateEstimated":row.get("einddatum_geschat") is True,
        "individualDateUnknown":str(row.get("einddatum_bron") or "").lower().startswith("paginabreed"),
        "observedAt":str(row.get("waargenomen_op") or "")[:10] or None,
        "wishMatches":names,
        "evidence":"Retailer promotion reference, not an independently verified discount",
        "verifiedDeal":False,"verifiedAllInPrice":False,"shippingEUR":None,
        "quality":note,"directProductPage":direct,
        "bundle":row.get("prijstype")=="bundeltotaal" or bool(row.get("bundelaantal")),
        "rankScore":round(score,2)
    }



def match_search_profile(offer, profile):
    """An umbrella wish can contain several distinct user requests.

    Do not claim a MacBook Pro offer matches MacBook Air, nor HOKA Kawana an
    Arahi. All resulting product hits STILL need SKU, size and shipping checks.
    """
    if profile.get("kind")!="product":
        return False
    ids=set(profile.get("wishlistIds") or [])
    if not ids.intersection(w["id"] for w in offer.get("wishMatches", [])):
        return False
    title=normalize_name(offer.get("title"))
    label=normalize_name(profile.get("name"))
    if label=="macbook air": return "macbook air" in title
    if label=="macbook pro": return "macbook pro" in title
    if label=="hoka arahi": return "hoka arahi" in title
    if label=="hoka kawana": return "hoka kawana" in title
    if label=="vergelijkbare stabiliteitsschoenen":
        return "hoka gaviota" in title or "stabiliteitsschoen" in title
    if label=="apple airpods anc alternatief":
        # Source title alone must actually mention ANC; standard AirPods
        # without that term cannot be promoted as the user's wanted model.
        return "anc" in title or "noise cancelling" in title or "ruisonderdrukking" in title
    return True


def profile_checks(profiles,pool,now):
    """One visible result for EVERY supplied user wish, including services.

    Service profiles and sample-sale research are not eligible price items.
    These statuses explicitly prevent hourly scans being misreported as
    actual service contract/API monitoring.
    """
    result=[]
    for profile in profiles:
        kind=profile.get("kind")
        candidates=[x for x in pool if match_search_profile(x,profile)] if kind=="product" else []
        candidates.sort(key=lambda x:(-x["rankScore"],x["priceEUR"]))
        if kind=="product":
            state="candidate" if candidates else "no_offer_in_feeds"
            method="Existing retailer/supermarket feed title-matching, not an exact SKU check"
            note=("Bronaanbod gevonden, maar variant, eventuele ANC/maat, voorraad en bezorgkosten controleren."
                  if candidates else "Geen passende actuele winkelprijs in aangesloten feeds; geen bewijs dat er elders geen aanbieding is.")
        elif kind=="service":
            state="not_connected"
            method="Separate contract feeds not connected"
            note="Geen vergelijkbare live contractprijzen of postcode-/verbruikscontrole aangesloten."
        else:
            state="separate_event_monitor"
            method="Official contest/sample-sale scanner is a separate feed"
            note="Bijzondere sample sales verschijnen via de afzonderlijke evenementenscanner, niet als webshop-productkorting."
        result.append({
          "position":int(profile.get("position") or len(result)+1),
          "name":str(profile.get("name") or "")[:120],
          "kind":kind,
          "state":state,
          "method":method,
          "note":note,
          "checkedAgainstFeedAt":now.isoformat() if kind=="product" else None,
          "trackedWishIds":list(profile.get("wishlistIds") or []) if kind=="product" else [],
          "candidateCount":len(candidates),
          "offers":candidates[:3],
        })
    return result


def generate(sources,wishlist,now):
    health=[source_health(s,now) for s in sources]
    wishes=wishlist.get("items",[])
    pool=[]
    duplicates=set()
    discarded={"expired_or_bad_price":0,"stale_source":0,"duplicates":0}
    for source,meta in zip(sources,health):
        if not meta["usable"]:
            discarded["stale_source"]+=len(source.get("deals",[]))
            continue
        for row in source.get("deals",[]):
            if not eligible(row,now):
                discarded["expired_or_bad_price"]+=1
                continue
            # Original per-store + same product + comparable price, not offers
            # from different merchants that have different shipping/stock.
            key=(normalize_name(row.get("winkel")),normalize_name(row.get("product")),
                 round(float(row["prijs"]),2))
            if key in duplicates:
                discarded["duplicates"]+=1
                continue
            duplicates.add(key)
            pool.append(pick(row,wishes,source.get("source")))
    pool.sort(key=lambda x:(-bool(x["wishMatches"]),-x["rankScore"],
                            -float(x.get("advertisedDiscountPercent") or 0),
                            x["priceEUR"],x["title"].casefold()))
    profiles=profile_checks(wishlist.get("searchProfiles",[]),pool,now)
    out={}
    for group in ORDER:
        selected=[x for x in pool if x["wishMatches"]] if group=="persoonlijk" else [x for x in pool if x["category"]==group]
        # Avoid one retailer filling all ten where there is choice.
        chosen=[]
        shop_counts={}
        for row in selected:
            if len(chosen)>=10:break
            if shop_counts.get(row["shop"],0)>=4 and len({x["shop"] for x in selected})>=3:
                continue
            chosen.append(row);shop_counts[row["shop"]]=shop_counts.get(row["shop"],0)+1
        if len(chosen)<10:
            ids={x["id"] for x in chosen}
            chosen.extend(x for x in selected if x["id"] not in ids and not ids.add(x["id"]) and len(chosen)<10)
        out[group]={"label":LABELS[group],"available":len(selected),"top10":chosen[:10]}
    return {
      "schemaVersion":1,"generatedAt":now.isoformat(),"timeZone":"Europe/Amsterdam",
      "sortPolicy":"Wishlist affinity, individual item price, source quality, advertised reference discount and source diversity. This is a ranked shortlist, NOT verified savings.",
      "coverage":"Only PrijsProfeet and selected FeedMyCart/DA/Intratuin sources; not all supermarkets, building-supply stores or webshops.",
      "discountPolicy":"Retailer-advertised reference only; actual 30-day or independent discount is NOT verified.",
      "siteReviewedNow":False,
      "liveRetailerPriceCheck":False,
      "verifiedDealCount":0,
      "profileCount":len(profiles),
      "profileChecks":profiles,
      "profileOfferCount":sum(p["candidateCount"] for p in profiles),
      "sourceHealth":health,"discarded":discarded,
      "eligibleCount":len(pool),"wishlistMatchedCount":sum(bool(x["wishMatches"]) for x in pool),
      "categories":out
    }


def main():
    now=datetime.now(ZONE)
    def read(path):
        return json.loads((ROOT/path).read_text(encoding="utf-8"))
    feeds=[read("weekdeals/deals.json"),read("weekdeals/nonfood.json")]
    wishlist=read("wishlist.json")
    data=generate(feeds,wishlist,now)
    if not any(x["usable"] for x in data["sourceHealth"]):
        raise SystemExit("All input sources stale or missing: refusing to publish misleading top-10")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"categoryCounts":{k:len(v["top10"]) for k,v in data["categories"].items()},
        "eligible":data["eligibleCount"],"wishesMatched":data["wishlistMatchedCount"],
        "health":data["sourceHealth"],"discarded":data["discarded"]},ensure_ascii=False))


if __name__=="__main__":
    main()
