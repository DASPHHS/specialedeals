#!/usr/bin/env python3
"""Discover dated sample sales from publicly listed events, separate from verified product deals.

No listing proves an individual size, price, stock or entry eligibility.
Previous published records remain visible when an index cannot be fetched,
with their last-seen date, until their event end date.
"""
import datetime as dt
import json
import pathlib
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "sample-events.json"
BASE = "https://www.stockverkopen.nl"
PAGES = [
    BASE + "/samplesales.html",
    BASE + "/kleding-sample-sales.html",
    BASE + "/permaand/deze-maand",
    BASE + "/perweek/deze-week",
]
MONTHS = {"januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5,
          "juni": 6, "juli": 7, "augustus": 8, "september": 9,
          "oktober": 10, "november": 11, "december": 12}
DATE = re.compile(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(20\d{2})\b", re.I)
MALE = ("heren", "mannen", "menswear", "unisex", "petrol", "kuyichi", "protest",
        "superdry", "vanguard", "circle of trust", "sportkleding", "outdoor",
        "sportswear", "nike", "adidas", "ralph lauren", "tommy hilfiger",
        "arc'teryx", "salomon", "hoka", "snickers", "tricorp", "state of art")
EXCLUDE = ("lingerie", "alleen dames", "uitsluitend dames", "uitsluitend voor vrouwen")


class Listings(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries = []
        self.current = None
        self.heading = False
        self.suppress = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.suppress += 1
        if tag == "h2":
            self.current = {"heading": [], "pieces": [], "url": ""}
            self.entries.append(self.current)
            self.heading = True
        if tag == "a" and self.current is not None and self.heading:
            href = dict(attrs).get("href", "")
            url = urllib.parse.urljoin(BASE, href)
            if re.match(r"https://(?:www\.)?stockverkopen\.nl/\d+/", url):
                self.current["url"] = url

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.suppress = max(0, self.suppress - 1)
        if tag == "h2":
            self.heading = False

    def handle_data(self, text):
        if self.current is not None and not self.suppress:
            self.current["pieces"].append(text)
            if self.heading:
                self.current["heading"].append(text)


def parse_listings(markup, today=None):
    today = today or dt.date.today()
    parser = Listings()
    parser.feed(markup)
    found = []
    for entry in parser.entries:
        title = " ".join(" ".join(entry["heading"]).split()).strip()
        url = entry["url"]
        body = " ".join(" ".join(entry["pieces"]).split())
        if not title or not url:
            continue
        dates = []
        for day, month, year in DATE.findall(body):
            try:
                dates.append(dt.date(int(year), MONTHS[month.casefold()], int(day)))
            except ValueError:
                continue
        if not dates:
            continue
        start, end = min(dates), max(dates)
        if end < today or start > today + dt.timedelta(days=180):
            continue
        text = (title + " " + body[:700]).casefold()
        if any(w in text for w in EXCLUDE) or not any(w in text for w in MALE):
            continue
        # Reject sales which explicitly stop below the watched EU47+ shoe size.
        if re.search(r"heren[^.]{0,65}(?:maat|maten)[^\d]{0,8}40\s*[-–]\s*46\b", text):
            continue
        if "klein aanbod herenschoenen" in text and "damesschoenen" in text:
            continue
        # Listing is a lead, not a confirmed discount or particular clothing size.
        lead = {"title": title[:160], "url": url, "startDate": start.isoformat(),
                "endDate": end.isoformat(), "city": "", "category": "Herenmode / sport",
                "brands": [], "sizes": "Maat en beschikbaarheid controleren",
                "note": "Gepubliceerd evenement; bekijk de organisator en voorwaarden.",
                "priority": 40, "source": "Stockverkopen.nl (agenda)",
                "verification": "Agenda gepubliceerd; prijs, maten en tickets nog controleren"}
        before = body[len(title):].split(str(start.day), 1)[0].strip()
        if 2 <= len(before) <= 55:
            lead["city"] = before.split()[-1]
        found.append(lead)
    return {event["url"]: event for event in found}


def run():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    try:
        prev = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        prev = {"events": []}
    previous = {e["url"]: e for e in prev.get("events", [])
                if isinstance(e, dict) and e.get("url") and e.get("endDate", "") >= today.isoformat()}
    combined = dict(previous)
    sources = []
    for url in PAGES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; KansenkompasEventRadar/1.0)"})
            with urllib.request.urlopen(req, timeout=16) as response:
                if response.status != 200:
                    raise ValueError("HTTP " + str(response.status))
                markup = response.read(1500000).decode("utf-8", "replace")
            found = parse_listings(markup, today)
            for key, lead in found.items():
                if key in combined:
                    # Keep richer editorial details already verified on the event listing.
                    combined[key]["lastSeenAt"] = now.isoformat()
                else:
                    lead["lastSeenAt"] = now.isoformat()
                    combined[key] = lead
            sources.append({"source": url, "status": "ok" if found else "empty",
                            "items": len(found)})
        except Exception as exc:
            sources.append({"source": url, "status": "error", "error": str(exc)[:140], "items": 0})
    events = sorted(combined.values(), key=lambda e: (-int(e.get("priority", 0)),
                    e.get("endDate", "9999"), e.get("title", "")))
    out = {"updatedAt": now.isoformat(), "sources": sources,
           "scanStatus": "ok" if any(s["status"] == "ok" for s in sources)
                         else "partial" if events else "no_results",
           "events": events,
           "note": "Evenementaankondigingen. Maten, producten, toegang en werkelijk voordeel zijn niet geverifieerd."}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sample_events": len(events), "source_status": sources}, ensure_ascii=False))


if __name__ == "__main__":
    run()
