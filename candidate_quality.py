"""Conservative discovery quality gates. Discovery is not price verification."""
import re
from urllib.parse import urlsplit

GENERIC_LISTING = re.compile(r"^(?:apple\s+)?(?:watch\s+ultra\s*\d+|airpods(?:\s+pro)?|macbook(?:\s+air|\s+pro)?|iphone\s*\d+)$", re.I)
CONDITION_MARKER = re.compile(r"\b(?:demo|open[ -]?box|refurbished|renewed|tweedehands|gebruikte)\b",re.I)
PROMOTION_MARKER = re.compile(r"(?:\b(?:korting|actieprijs|dagdeal|aanbieding|deal|uitverkoop|opruiming|sale)\b|\d{1,2}%\s*(?:korting|off)|(?:1\s*\+\s*1|2\s*\+\s*1)\s*gratis)",re.I)

def candidate_quality(item):
    """Return (eligible, reason) for a *research candidate*, never a verified deal."""
    title=str(item.get('title') or '').strip()
    url=str(item.get('url') or '')
    parsed=urlsplit(url)
    if not title or parsed.scheme!='https' or not parsed.hostname:
        return False,'Geen concrete HTTPS-productlink'
    if GENERIC_LISTING.fullmatch(title):
        return False,'Reguliere product-/categoriepagina, geen aanbieding'
    if CONDITION_MARKER.search(title):
        return False,'Demo, open-box of refurbished: aparte vergelijking vereist'
    if item.get('source','').casefold().startswith('amac') and not PROMOTION_MARKER.search(title):
        return False,'Amac productpagina zonder concreet actiebewijs'
    if not PROMOTION_MARKER.search(title) and not item.get('wishlistMatches'):
        return False,'Geen actie-indicatie of wishlistmatch'
    return True,'Onderzoekslead; prijs, voorraad en besparing nog niet geverifieerd'
