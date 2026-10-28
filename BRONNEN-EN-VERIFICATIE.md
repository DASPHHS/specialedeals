# Speciale Deals — bronstrategie en controleprotocol
**Onderzoek: 28 oktober 2026.** Dit document is geen claim dat 165 winkels automatisch worden uitgelezen. De actuele implementatie heeft een bronregister, onderzoeksmatrix, conservatieve prijsengine en regressietests; winkeladapters ontbreken nog voor de meeste retailers.

## Onderzoek: wat leren we van bestaande systemen?
1. **Tweakers Pricewatch** gebruikt winkelproductfeeds, ververst ze vaker per dag en houdt productprijsgrafieken bij. Rangschikking op totaalprijs, niet alleen artikelprijs. Bron: https://tweakers.net/info/faq/pricewatch/
2. **Kieskeurig** meldt dat winkel- en fabrikantfeeds fouten kunnen bevatten; prijs en verzendkosten kunnen uiteenlopen en refurbished is een andere categorie. Bron: https://www.kieskeurig.nl/hoe-wij-vergelijken
3. **changedetection.io** kan productprijzen, voorraad, JSON-LD/structured data, historische veranderingen en selectors volgen. Dit levert signalen maar **geen automatische onafhankelijke kortingstoets**. Bron: https://github.com/dgtlmoon/changedetection.io
4. **Checkjebon** ontsluit NL supermarktdata en vermeldt dat er bij ontbrekende prijswaarnemingen schattingen kunnen worden gebruikt. **Schattingen zijn geen actuele kassaprijs.** Bron: https://github.com/supermarkt/checkjebon
5. **PrijsProfeet API** maakt onderscheid tussen `active`, `upcoming`, `shelf` (normale prijs) en `historical`. Alleen `active` is een lopende promotie; `shelf` is juist een gewone prijs en `historical` kan verouderd zijn. EAN-dekking verschilt per keten. Bron: https://www.prijsprofeet.nl/api ; https://github.com/PrijsProfeet/supermarkt-api
6. **Supermarktscanner** gebruikt genormaliseerde eenheidsprijzen en prijshistorie voor boodschappen; laat actuele productprijs altijd nog bij winkel zelf toetsen. Bron: https://supermarktscanner.nl/beste-aanbiedingen
7. **Consumentenbond 2026** vond Hornbach en Bauhaus gemiddeld goedkoper dan andere onderzochte bouwmarkten, *maar het was een onderzoekssteekproef exclusief acties* en dus geen bewijs voor een concreet actueel product. Bron: https://www.consumentenbond.nl/verbouwen-en-klussen/prijspeiling-bouwmarkten
8. **Reddit r/thenetherlands** signaleert dat brede supermarktplaats- en eenheidsprijsvergelijking moeilijk is, prijzen geregeld verouderen en winkelreizen ook kosten meebrengen. Reddit is een ervaringsbron, geen prijsbewijs. https://www.reddit.com/r/thenetherlands/comments/13oorzq/ en https://www.reddit.com/r/thenetherlands/comments/1lcxjt7/
9. **ACM** vereist bij reclamekortingen in het algemeen een juiste van-prijs op basis van de laagste prijs van de verkoper in de 30 dagen vóór de actie (met wettelijke uitzonderingen). Een adviesprijs is nooit vanzelf bewijs van de geclaimde besparing. Bron: https://www.acm.nl/nl/verkoop-aan-consumenten/consumenten-informeren/prijzen-vermelden
10. **Nederlandse Douane**: bij niet-EU-aankopen moeten btw, invoerheffing, inklaring en internationale verzending expliciet worden betrokken; per 1 juli 2026 gelden gewijzigde regels voor zendingen van maximaal €150. Bron: https://www.douane.nl/onderwerpen/online-shoppen-en-pakketpost/shoppen-bij-een-buitenlandse-webwinkel/extra-kosten-bij-bestellen/

## Bronrollen en vertrouwen
- **A | Officiële winkel/verkoper:** enige directe bron voor de concrete orderprijs, actuele voorraad, actuele leveringskosten, kortingsvoorwaarden, afleveradres NL en geldigheid.
- **B | Onafhankelijke vergelijker/prijsgeschiedenis:** controle van dezelfde EAN/SKU, andere geobserveerde winkels en prijsontwikkeling. Let op feedvertraging, affiliate-selectie en verzendkosten.
- **C | Aggregator/communities/folders:** Pepper, mydealz, Dealabs, Voordeelmuis, Reclamefolder, Stockverkopen, Reddit. *Leads, geen geverifieerde prijzen.*
- **D | Productfabrikant/organisator:** exacte productidentiteit of officiële organisatorvoorwaarden; fabrieksadviesprijs niet als historische korting.

## Onderzoeksregister
- `bronnenregister.json` bevat **165** concrete URL-startpunten met regio, categorie en bronrol, niet allemaal gecontroleerd op live uitleesbaarheid.
- `onderzoeksplan.json` bevat **30** product-/wensroutes (14 bestaande prijsradarproducten, 13 huishoudcategorieën, sample sales, winacties en verwante categorieën). Per route worden afzonderlijk retail-, benchmark- en discoverybronnen voorgesteld.
- De dagelijkse ChatGPT-taak gebruikt dit als prioriteringsroute, maar moet live webbronnen **zelf** controleren. De GitHub-scanner gebruikt momenteel **niet automatisch alle 165 bronnen** en mag dat ook niet onbeperkt doen (robots, ToS, rate limits, veel bronruis). Sommige sites tonen geen voorraad of prijzen via openbare HTML.

## Prijsclassificatie (moet altijd expliciet zijn)
1. **Onbevestigde lead:** merk/SKU, titellink en tip gevonden; geen gecontroleerde actuele NL-totaalprijs. Geen kortingspercentage overnemen.
2. **Prijspeil (geen deal):** exacte SKU, nieuw/condition, actuele NL totaalprijs, voorraad, winkel en checktijd geverifieerd. “Laagste bij 4 gecontroleerde winkels” alleen indien werkelijk 4 zijn gecontroleerd.
3. **Prijsvoordeel t.o.v. andere winkel:** actueel product A is €X goedkoper dan exact product A bij winkel B; expliciet andere winkel als referentie. *Niet* automatisch een tijdelijke aanbieding/korting.
4. **Echte promotie ≥10%:** actuele prijsverlaging van de verkoper én voldoende gedocumenteerde, eerlijke, herleidbare referentie met prijshistorie/30-dagenreferentie waar van toepassing. Onafhankelijke actuele winkelvergelijking om te toetsen of het ondanks de promotie een goede koop is.
5. **Vaste beste koop:** herhaald recent geverifieerd goedkoopste prijs per **effectief gebruik** bij voldoende kwaliteit, met meerdere vergelijkbare aanbieders. Een Action-prijs zonder betrouwbaar vergelijkingsmateriaal geeft geen universele beste koop.

## Productmatching en falsificatie
- Voor exact product: EAN/GTIN indien betrouwbaar, merk, model, generatie, variant, kleur, maat, hoeveelheid, conditie, abonnement, BTW en accessoires.
- Apple Watch Ultra: gewone Amac-productpagina of catalogusprijs = **nieuwprijs**, geen deal. MacBook refurbished/demo/open-box apart; AirPods verschillende generaties/cases apart.
- Arc'teryx alleen als outdoor merk; maten L/XL en broeken W32-34 werkelijk op voorraad; schoenen HOKA circa EU47.
- JANZEN Earth 46 200ml niet verwarren met navulling, gel of geur; Rituals Homme/Sport/Sakura onderscheiden. Voor YSL Y concentratie en ml; M7 en M7 Oud Absolu apart.
- Koffie Original Blend 350g vs 1000g, bonen vs gemalen en abonnement gescheiden. Een aanbieding in 1kg wordt niet doorgerekend als korting op 350g.
- Waspods: €/voorgeschreven wasbeurt; vaatwastablet: €/tablet; shampoo: €/100 ml; toiletpapier: €/100 vellen; schoonmaakconcentraat: €/werkende oplossing; verf: €/m² dekking met geschikt product. Huismerken mogen winnen wanneer kwaliteit voldoende.
- Buitenlandse shops: shop-country != delivery-country; controleer NL-levering en checkout, BTW, retourgarantie, en niet-EU-invoer. Bij onbekende kosten: prijs niet all-in bevestigd.

## Concreet uitvoerbare dagroutine 08:00 Europe/Amsterdam
1. Lees `wishlist.json`, `prijsradar-config.json`, `huishoudradar-config.json`, `bronnenregister.json`, `onderzoeksplan.json`, de bestaande geverifieerde en kandidaatbestanden.
2. Kies gericht ca. 8-12 van de **meest relevante productvarianten** voor diepgaand onderzoek; roteer de rest over de week en neem extra spectaculaire onverwachte kansen mee. Geen claim dat alle 165 sites dagelijks worden nagekeken.
3. Per hoofdproduct probeer 2-4 verschillende betrouwbare verkopers plus 1 onafhankelijke prijs-/historiebron. Leg concrete productlink en controle-moment vast. Vergelijk dezelfde SKU, conditie en verzendkosten. Bij moeilijke buitenlandse aanbieders: markeer onzeker in plaats van goedkoop te claimen.
4. Onderzoek 3-8 concrete prijsverhoudingen voor vaste aankopen: Action/Xenos/Zeeman/Kruidvat/Etos versus Lidl/Aldi/Dirk/AH/Jumbo; prijs per effectief gebruik, kwaliteit. Bouwmarkten voor schilderwerk/tuin/klus plus prijsgarantie alleen wanneer de winkelvoorwaarden op die SKU passen.
5. Zoek via Stockverkopen, We Love Sample Sales, Your Sample Sale en organisator/boekingsticket naar echte komende sample sales met merk, data, locatie, toegangsprijs/tickets, beschikbare maten en retourvoorwaarden. **Geen sample-sale-nul claim op basis van alleen de onvolledige scraper.**
6. Zoek bij officiële merken/retailers naar waardevolle gratis winacties, met NL-inwonerschap, vervaldatum en T&C. Geen claims over deelnamekans.
7. Formatteer één ochtendbriefing: (A) echte promoties, (B) laagste geverifieerde reguliere prijzen, (C) huishoud/bouwmarkt eenheidsprijzen, (D) officiële winacties, (E) sample sales, (F) 0-3 onbevestigde leads, (G) bronbereik en beperkingen. Korte tabellen, concrete euro- en percentages alleen met berekeningsgrondslag en directe URL.
8. Geen Gmail-verzending claimen en niet suggereren dat de ChatGPT-taak het GitHub-dashboard bijwerkt. De bestaande GitHub-scan is een **onafhankelijke** stroom.

## Bekende beperkingen
Geen brede, automatisch geautoriseerde retailerfeeds geïntegreerd in de repository; geen live totaalprijzen voor alle 165 bronnen; geen garantie dat webshops scraping toestaan. Bronnenregister en ochtendtaak betekenen geen voltooid prijsplatform. Dagelijkse webbeschikbaarheid kan beperkt zijn; wees concreet over welke winkels die run daadwerkelijk zijn gecontroleerd. 
