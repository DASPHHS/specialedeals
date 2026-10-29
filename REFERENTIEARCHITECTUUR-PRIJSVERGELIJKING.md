# Referentiearchitectuur: DePrijsvergelijker en open-source prijsradars

Datum: 2026-10-29. Onderzoek, geen overname van auteursrechtelijk beschermde code.

## Geobserveerd bij DePrijsvergelijker
- https://www.deprijsvergelijker.com/pages/zo-vergelijken-wij beschrijft partnerproductfeeds, EAN-identiteit, nachtelijke metingen en prijswijzigingen sinds 3 oktober 2026.
- https://www.deprijsvergelijker.com/pages/vergelijken beschrijft de filter 'echt lager': minimaal 10% **en** €10 onder de laagste prijs bij dezelfde winkel in de voorafgaande 30 dagen; de historische periode is korter wanneer er nog geen 30 dagen zijn gemeten.
- De site waarschuwt dat feeds niet altijd de checkoutprijs zijn en dat niet alle Nederlandse winkels worden gemeten.
- Dit zijn referentieprincipes, niet bewijs dat de website ons datafeedtoegang geeft.

## Open-source referenties
- https://github.com/sonoyumi/price-tracker : SQLite history, schema.org JSON-LD/CSS parsing, rate-limited fetching, alert threshold tests.
- https://github.com/devoidx/price-tracker : multi-retailer product timelines, per-source schedules, failures and retries.
- https://github.com/Don-Monteverdi/price-scraper : EAN/GTIN first, comparator discovery, resumable job queue.
- https://github.com/PrabgunMokha/Price-Guard : product fingerprint and explicit product mismatch status.
- https://github.com/shopsavvy/sdk-go : commercial API alternative; license, NL coverage and cost must be evaluated before integration.
- https://www.reddit.com/r/selfhosted/comments/1e733vj/ : changedetection.io price thresholds and practical notification patterns.

## Proposed pipeline
1. **Canonical catalog**: product_id, gtin, sku, brand, model, volume, size, color, condition. Do not merge YSL M7 and Oud Absolu, Michael Kors EDP and EDT, HOKA sizes, Apple generations, padel pack sizes.
2. **Acquisition**: equal discovery priority for Pepper/mydealz, retailer pages/feeds, and price comparison sources. Prefer explicitly permitted feeds/APIs; use polite fetching and record 403/429.
3. **Raw observation**: retailer, exact URL, timestamp, item price, stock, raw product identifier, currency, NL shipping and other mandatory fees, extraction method, evidence provenance and confidence.
4. **Evidence gate**: identity, condition, NL shipping and stock must all pass before publishing 'gecontroleerde actuele totaalprijs'. Do not infer shipping=0.
5. **Historical store**: append immutable snapshots (SQLite for processing; public redacted JSON summary). Retain actual price history and errors. Avoid overwriting the only historical snapshot each run.
6. **Price comparison**: best total NL price *among observed retailers*, preferably >=4 distinct stores, count and timestamp shown.
7. **Discount test**: minimum 10% independent same-variant net discount; add 'historically genuinely lower' signal only when enough store history exists. Never use MSRP alone. Do not confuse historical discount and competing-store advantage.
8. **Site**: cards for verified current price, verified discount, official contests, verified menswear sales. Keep research leads separate. Show missing verification as one compact diagnostics section.
9. **Notifications**: single daily digest, de-duplication, no individual alerts, no auto-entry or purchase.
10. **Privacy**: no personal participation or account details in public GitHub; use private authenticated storage if multi-device sync is wanted.

## Implementation sequence and acceptance
P0: attach first exact product URLs and GTINs, prove price extraction on saved HTML fixtures; add 4 sources/product where available.
P1: authorized retailer feed adapter, historical SQLite snapshots, baseline from same-store measurements.
P2: evidence-backed delivery calculation, product mismatch handling, failed-source health report.
P3: side-by-side 4-store UI and source history chart; mobile-friendly filtering.
P4: household cost per wash/tablet/100 sheets, men's sale schedule, consolidated morning digest.

Do not merge until Python unit tests and workflow tests pass. The current `product-targets.json` remains empty until trustworthy product IDs and URLs have been verified. No live prices or discounts should be invented.
