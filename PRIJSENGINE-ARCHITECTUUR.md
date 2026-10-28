# Kansenkompas — betrouwbaar prijs- en dealsysteem v2

Datum 2026-10-28. Dit is een architectuurplan, niet de claim dat alles al geïmplementeerd is.

## Onderzochte patronen
- changedetection.io: schema.org/JSON-LD-prijs en voorraad, historiek, browser-rendering bij JavaScript-sites. https://github.com/dgtlmoon/changedetection.io
- sonoyumi/price-tracker: expliciete prijsparsing, SQLite-historie, per-site beleefde retries, eerste observatie niet als prijsdaling. https://github.com/sonoyumi/price-tracker
- andrewschultzw/price-tracker: meerdere aanbieders per SKU, drempels voor historische diepte, tests en staleness. https://github.com/andrewschultzw/price-tracker
- Reddit r/selfhosted: per retailer/postcode genormaliseerde rijen, productmatching los van extractie, communitybronnen zijn geen prijsbewijs. https://www.reddit.com/r/selfhosted/comments/1t8s6r6/price_comparing_app/

## Datastroom (bouwvolgorde)
1. **Discovery:** Pepper, folder, fabrikant, winkel, winactie, sample sale. Sla titel, URL, bron, timestamp en type op. **Nooit** automatisch een deal noemen. Weiger generieke product-/categoriepagina's, open-box en demo in de nieuwe-prijs feed.
2. **Productidentiteit:** canonical product key: EAN/GTIN waar bevestigd, anders merk + exact model + generatie + capaciteit/maat/kleur + conditie. Match alleen binnen dezelfde conditie. Nieuw/refurbished/open-box en abonnement apart. Generieke 'Apple Watch Ultra' is geen prijsvergelijkbaar product.
3. **Extractie:** voorkeur voor officiële API/merchant feeds, dan JSON-LD schema.org Product/Offer, dan expliciete winkeladapter/selector. Browser-rendering alleen waar toegestaan en nodig. Geen captcha omzeilen. Leg raw snapshot/parseversie vast en markeer ambiguïteit. Een pagina met meerdere prijzen moet exact de juiste offer en variant aanwijzen.
4. **Verificatie:** prijs in EUR, BTW, leveringskosten NL, verplichte kosten, in-stock, betrouwbare verkoper, productvariant, productconditie, controle-tijd. Weiger claim bij ontbrekende bezorgkosten of onduidelijke winkelvoorwaarden. Voor fysieke winkel: echte vestiging binnen 20 km Bleiswijk en bevestigde vestigingsprijs.
5. **Historie:** bewaar elke controle per winkel/SKU (niet alleen wijzigingen). 30/90 dagen referenties pas na voldoende waarnemingen; eerste waarneming is **geen** prijsdaling. Controleer referentie op promotionele uitschieters. Geen geclaimde MSRP-besparing.
6. **Vergelijking:** laagste actuele geverifieerde all-in prijs onder N gecontroleerde aanbieders (N expliciet tonen); koopdeal alleen bij >=10% onder onafhankelijke actuele prijs of betrouwbare historische transactiebasis. Besparing EUR = referentie - huidige totaalprijs, besparing % = 100 * verschil / referentie. Vergelijkbaarheid, referentiedatum, prijsverificatie en evidence-links vereist.
7. **Huishoudens:** twee rankings: identieke SKU en functioneel vergelijkbaar bij voldoende kwaliteit. Eenheidsprijzen per wasbeurt/tablet/100 ml/l/kg/m², werkelijke dosering, verpakkingsgrootte en eventuele bezorgkosten. Geen universeel beste winkel zonder consistente recente steekproef.
8. **Publicatie:** aparte bestanden `price-observations.json`, `verified-pricepeil.json`, `verified-deals.json`, `research-candidates.json` met JSON Schema. Publiceer alleen data na CI-validatie, tests en deduplicatie. Afgekeurde leads apart en niet als besparing in de UI.
9. **Dagrapport:** 08:00 Europe/Amsterdam, top besparingen in EUR en %, laagste reguliere prijs apart, 3 grote winacties, echte sample sales, huishoudens/bouwmarkt. Nooit 'nul resultaten' maskeren met nepdeals. Stuur alleen notificaties na verificatie.

## Implementatiestatus
- **Gereed:** expliciete kandidaatkwaliteitsfilter voor reguliere Apple Watch/Amac-productpagina's en demo/open-box; regressietests toegevoegd aan scan-workflow. UI filtert zulke items ook defensief.
- **Nog open:** echte retail adapters, schema.org-extractie, prijs-/voorraadhistorie, onafhankelijk vergelijkingsbewijs, shipping-calculator, kwaliteitsscore, geautomatiseerde actuele EUR-besparing, volledige sample-saleverificatie, emailaflevering.
- **Veiligheidsregel:** bron bereikbaar of '70% korting' in de titel is nooit bewijs van een deal. Geen actuele prijs = geen besparingsbedrag.
