# Bronnen en ontwikkelstatus

Bijgewerkt: 25 oktober 2026. Dit document beschrijft implementatie en ontbrekende dekking; het is geen verklaring dat alles werkt.

## Acceptatie en afbakening

Eén dashboard voor persoonlijke premiumdeals, Nederlandse/internationale winacties, sample sales, contractbesparingen, AI en innovaties. Herenmaten en persoonlijke merken uit README zijn leidend. Boodschappenmaatje, AH/Jumbo/Lidl en recepten worden niet gewijzigd. Geen willekeurige aantallimiet op gepubliceerde deals. De winactiefilter verwijdert zoekruis zoals Windows, WinRAR en woordenboekpagina’s; 52 bestaande ruisrecords zijn verwijderd.

## Bronstrategie

| Onderdeel | Methode | Ritme | Betrouwbaar voor | Nog nodig |
|---|---|---|---|---|
| Dealontdekking | Bestaande Pepper RSS, Google News/Bing RSS | Elke 4 uur op minuut 17 UTC | Nieuwe vindplaatsen | Officiële productcontrole; nieuws is geen prijsfeed |
| Exacte producten | Bestaande JSON-LD/meta-parser op shop-targets.json | Elke 4 uur | Winkelprijs met controletijd en voorraadsignaal | Verzendprijs, passende variant, onafhankelijke vergelijking |
| Prijshistorie | Waargenomen prijzen per winkel | Iedere productscan | Eigen historische prijs | Geen marktbrede laagsteprijsgarantie |
| Winacties | Meertalige discovery en redactionele contests.json | Elke 4 uur | Kandidaten en controleerbare regels | Officiële voorwaarden, NL-toelating, deadline inhoudelijk herbeoordelen |
| Sample sales | Gerichte merkzoekopdrachten | Elke 4 uur | Aankondigingen | Datum, locatie, toegang en maten verifiëren; geen login-scraping |
| AI/gezondheid | Bestaande officiële/Reddit-onderzoekssignalen | Dagelijks | Ontdekking | Primaire publicatie, beschikbaarheid en bewijsniveau beoordelen |
| Awin productfeeds | Publisher Product API / downloadfeed | Voorstel: elke 4 uur | Productidentiteit, prijs, variantvelden indien geleverd | Account, partnership en feedrechten ontbreken; niet aangesloten |
| ING/Veepee/BestSecret | Geautoriseerde accounttoegang | Niet aangesloten | Geen automatische claim | Geen publieke bruikbare feed geverifieerd |
| Hypotheek | Nog geen aangesloten rente-adapter | Niet geverifieerd | Geen huidige rentemeting | Officiële tarieven per aanbieder, NHG/LTV, rentevast, voorwaarden en timestamp |
| E-mail | Afzonderlijke private taak | Niet geverifieerd in repo | Geen bezorgbewijs | Uitvoerings- en bezorgcontrole, deduplicatie en meldhistorie |

Awin ondersteunt productfeeds en een Publisher Product API voor Enhanced Feeds binnen toegankelijke partnerships. Een advertentie-upload-API is geen publieke prijszoek-API. Geen API of scrapingmethode wordt aangesloten uitsluitend omdat een leverancier bestaat.

GitHub-planningen kunnen vertragen of vervallen. Daarom wordt actualiteit opnieuw berekend bij het openen van de site, onafhankelijk van de laatste geschreven status. Geen gegarandeerde uitvoering op de minuut.

## Technische bronvoorwaarden

- Gebruik officiële API/feed waar toegang daadwerkelijk bestaat; daarna gestructureerde productdata op exacte openbare URL's.
- HTTP 403/429, login en CAPTCHA blijven zichtbare beperkingen. Niet omzeilen of als succes tellen.
- Alleen exact GTIN/MPN vergelijken; gelijke productnamen bewijzen geen gelijke variant.
- Verzendkosten onbekend betekent geen bewezen totaalprijs. Cashback/codes/punten alleen bij aantoonbare toepasbaarheid.
- Een succesvolle HTTP-respons zonder bruikbare productvelden is geen succesvolle prijscontrole.
- Iedere publicatie controleert syntaxis, datacontracten en voorraad-/variantregels.

## Ontwikkeloverzicht

| Functie | Implementatiestatus | Acceptatie |
|---|---|---|
| Eén navigatie en dashboard | Gebouwd | 40 tests en DOM-navigatiecontrole geslaagd; livecontrole bij publicatie |
| Bestaande detailmodules in dashboard | Gebouwd | Zelfde oorsprong, behoud bestaande lokale opslag, lazy loading |
| Deals/filters/productwaarnemingen | Gedeeltelijk | Winkelwaarneming is geen koopadvies |
| Bronstatus inclusief ouderdom en deeluitval | Gebouwd en unit-getest | Nooit vers bestand met mislukte bronnen als werkt labelen |
| Automatische discovery | Bestaand, iedere 4 uur ingepland | Werkelijke runstatus in Actions leidend |
| Dagmail / snelle meldingen | Niet geverifieerd | Niet als werkend presenteren |
| Hypotheek <3,6% | Niet geverifieerd | Alle rentevaste periodes, met financieringsvoorwaarden |
| Contracten | Lokale rekenhulp | Geen privésynchronisatie of verzonnen contractvelden |
| Automatisch deelnemen | Niet gebouwd | Nooit voltooid zonder bevestiging |
| Feedpartners | Onderzocht, niet aangesloten | Pas actief na echte toegang en proefscan |

## Primaire documentatie geraadpleegd

- https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://help.awin.com/developers/docs/introduction-1
- https://success.awin.com/articles/en_US/Knowledge/Product-Data-Feed-FAQ

## Volgende concrete acceptatiepunten

1. Verzending en identieke varianten voor prioritair gevolgde producten verifiëren.
2. Officiële sample-saleagenda's en winvoorwaarden structureel uitlezen en hercontroleren.
3. Private contractgegevens en meldketen aansluiten zonder publicatie van persoonsgegevens.
4. Rente-adapter met bewezen officiële bron en vergelijkbare financieringsscenario's.
5. Accountfeeds uitsluitend aansluiten wanneer credentials en rechten beschikbaar zijn.

Publicatiebotsing vastgesteld in run 40193373320: beide scanners lazen de event-commit, waarna system-health.json conflicteerde. Beide workflows halen nu expliciet de actuele main-branch op binnen dezelfde concurrency-groep. Handmatig onderzochte kandidaten blijven behouden bij de ruisfilter.
