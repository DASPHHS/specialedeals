# Speciale Deals — nieuwe start (27 oktober 2026)
Publieke website: https://dasphhs.github.io/specialedeals/

## Definitieve voorkeuren
- Primair voor man van 36, met ook relevante vondsten voor zijn vrouw van 33; geen kinderen.
- Fysieke gewone winkeldeals: maximaal 20 km vanaf Bleiswijk (harde locatiecontrole vereist).
- **Sample sales: heel Nederland**, alleen relevante uitschieters; niet begrensd tot 20 km.
- Online deals: wereldwijd mits feitelijk beschikbaar voor Nederlandse consumenten.
- Winacties: Nederlandse deelname en gratis voorwaarden altijd eerst bij de officiële organisator vaststellen.

## Huidige implementatie en eerlijke beperkingen
Deze eerste schone versie heeft vier tabs: Vandaag, Deals, Winacties en Sample sales. GitHub Actions verzamelt openbare **kandidaten** via 11 bronpagina's en registreert fouten per bron. Er is **nog geen betrouwbare productprijscontrole, exacte 20 km-winkellocatiefilter, verificatie van officiële wedstrijdregels, datumparser voor evenementen of bevestigde beschikbaarheid**. Dat soort kandidaten wordt expliciet als ongeverifieerd getoond; het systeem mag dus nooit claimen dat een aanbieding geverifieerd is. Het is géén volwaardige automatische dealsvergelijker.

Bronnen die de scanner niet toegankelijk kan uitlezen krijgen een zichtbare foutstatus. De scan gebruikt geen omzeiling van blokkades, geen accountgegevens en geen ongedocumenteerde bron-API. GitHub Pages wordt gepubliceerd vanaf main/root. Actions kan alleen commits doen als workflow-schrijfrechten ingeschakeld zijn.

De aparte ChatGPT-ochtendtaak 08.00 kan geverifieerde selectie maken en hoeft niet te vertrouwen op deze kandidaten. Geschiedenis van de oude repository blijft via eerdere Git-commits herstelbaar. Alle oude actieve workflowbestanden zijn uit de huidige tree verwijderd.

## Ontwikkelvolgorde
1. Strikte geografische winkelvalidatie: vast adres, vestiging en afstand, maximaal 20 km.
2. Betere, individuele bronadapters voor AlleFolders, SuperSales, Pepper en wedstrijdsites.
3. Nationale sample-sale-calendars met begin/einddatum, ticketprijs, kledingmaat, merk en duplicate detection.
4. Dealerprijs en prijshistorie met identieke SKU, bezorgkosten en voorraad.
5. Validatietests en melding wanneer scans falen; dagelijkse korte highlights na controles.

Gebruik geen klantgegevens in deze publieke repository.
