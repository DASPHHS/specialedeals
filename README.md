# Speciale Deals — persoonlijke premiumradar

**Dashboard:** https://dasphhs.github.io/specialedeals/  
**Slimme Kansen:** https://dasphhs.github.io/specialedeals/ai-kansen.html  
**Koopkracht:** een ANDER project (https://github.com/DASPHHS/koopkracht) dat hier niet wordt gewijzigd.

## Wat daadwerkelijk geautomatiseerd is

- [x] `scan.py`: Pepper en gerichte RSS-/webzoekopdrachten, gefilterd op jouw exacte merken/producten. Resultaten in `live-deals.json` zijn **kandidaten**, géén geverifieerde koopdeals.
- [x] `merchant_check.py`: haalt bij openbaar uitleesbare **exacte productpagina's** de gestructureerde winkelprijs op, met controletijd, waarschuwing bij onbevestigde uitvoeringen en voorraadsignaal. Kijk in `merchant-observations.json`. Ontbrekende producten worden niet verzonnen.
- [x] `price-history.json`: bewaart circa 90 dagen waargenomen prijzen bij dezelfde winkels. Een lage eigen historische prijs is géén bewijs van marktlaagste prijs.
- [x] GitHub Actions `.github/workflows/scan.yml`: viermaal per dag plus na relevante broncode-/watchlistwijzigingen. Open Actions voor de werkelijke status.
- [x] Dashboard: persoonlijke shortlist, alle bronnen, aparte sample-sale-vondsten, ING Punten (zonder verzonnen ranglijst), winkelprijzen en eigen alertinstellingen.
- [x] `watchlist.json`: centrale, openbare alertlijst met per product een maximale prijs. De **bevestiging van de GitHub-issue door de repository-eigenaar** zorgt voor synchronisatie via `alert-config.yml`. Dit is geen rechtstreeks onzichtbare save door GitHub Pages.
- [x] Uurlijkse en dagelijkse ChatGPT-taken kunnen `watchlist.json` en de scanresultaten lezen. Een e-mail wordt via een **aparte Gmail-actie** verstuurd, niet door GitHub Pages. Gmail-verzenden is via een eenmalige test gecontroleerd.
- [x] Slimme Kansen: 73 afzonderlijke, persoonlijke bouwideeën met zoek/filter en favorieten die alleen lokaal op het apparaat blijven.
- [ ] ING Punten achter login: automatisch actuele vouchers en puntenprijzen uitlezen — niet mogelijk zonder betrouwbare geautoriseerde toegang.
- [ ] Toonaangevende webshops die geen API/productdata toelaten: automatische livevoorraad en prijzen. Een HTTP 403 is een echte beperking, geen successtatus.
- [ ] Automatische onafhankelijke checkout-/bezorgprijsvergelijking voor álle aanbiedingen.
- [ ] Website rechtstreeks persoonlijke ChatGPT-automations laten aan-/uitzetten zonder GitHub-bevestiging. Dit vereist een authenticatieserver/appkoppeling.
- [ ] Alle nieuwe Reddit/AI-berichten inhoudelijk onafhankelijk beoordelen: geautomatiseerde `ai-kansen-kandidaten.json` bevat uitsluitend researchsignalen, geen bewezen nieuws.

## Nieuwe alert vanuit iPhone
1. Open Speciale Deals > Mijn alerts.
2. Vul een product plus maximale totaalprijs in.
3. Tik **Alert instellen via GitHub**.
4. Log zonodig in op GitHub en bevestig de vooringevulde issue met **Submit new issue**.
5. De workflow accepteert **alleen issues aangemaakt door eigenaar DASPHHS** met geldig formaat, schrijft `watchlist.json` bij en sluit de issue.
6. De eerstvolgende geplande scan en de bestaande ChatGPT-dealtaak kunnen de nieuwe voorkeur raadplegen.

**Let op: repository en watchlist zijn openbaar.** Gebruik geen privé-, medische, financiële of geheime informatie in de productnaam of een issue.

## Verificatie en interpretatie

| Status | Betekenis |
|---|---|
| Feedkandidaat | Bericht ontdekt, eindprijs/voorraad niet gecontroleerd |
| Winkelprijs waargenomen | Uit gestructureerde productpagina gehaald, met timestamp |
| Voorraadsignaal uitverkocht of tegenstrijdig | Niet in koopaanbevelingen |
| Juiste variant niet bevestigd | Geen koopadvies, ook niet bij lage prijs |
| Echte buitenkans | Pas na controle actuele maat/variant, voorraad, verzendkosten en onafhankelijke marktprijzen |

Een winkel kan op zijn pagina 'op voorraad' schrijven terwijl de gestructureerde gegevens 'OutOfStock' melden. Zulke tegenstrijdigheden geven **geen** bevestigde koopbare deal. Producten kunnen tussen scans wijzigen. Doe geen aankoop zonder laatste controle.

## Beheer

- `radar-config.json`: vaste voorkeuren, zoekopdrachten en overzicht van betrouwbare controle-/ontdekbronnen.
- `shop-targets.json`: exact bewaakte productpagina's. Een URL is pas 'actief gecontroleerd' bij een succesvolle observatie in de JSON-uitvoer.
- `alert-profiel.json`: rubric voor ChatGPT-alerts.
- `watchlist.json`: daadwerkelijk aan de alerttaak gekoppelde extra producten en prijsgrenzen.
- `.github/workflows/alert-config.yml`: beveiligde issueverwerking; vereist dat Issues in de GitHub-repository ingeschakeld zijn en Actions schrijfrechten hebben.
- `ai_kansen_research.py`: verzamelt nieuws-/Reddit-kandidaten, gelabeld als onbevestigd. Geen automatische medische aanbevelingen.

**GitHub Pages:** Settings > Pages > Deploy from branch `main`, folder `/ (root)`. GitHub Actions: Settings > Actions > General > Workflow permissions: **Read and write permissions** als commits door de bot anders geweigerd worden.

Er worden geen API-sleutels, wachtwoorden of persoonsgegevens in de publieke repository opgeslagen.

## Samenvoeging Kansenkompas / Kansenradar — 25 oktober 2026

Het gezamenlijke dashboard staat in deze repository. `winacties.html` leest de gecontroleerde openbare acties uit `contests.json` en kandidaten apart uit `contest-candidates.json`, met zoekopdracht, categorie en actuele fase (open/binnenkort/hercontrole/afgelopen). Geen limiet van veertien. Een record is één actie, niet iedere deelprijs afzonderlijk.

`contest_scan.py` zoekt via 23 Nederlandstalige, Engelse, Duitse en Franse RSS-zoekopdrachten naar auto/EV, cash, renovatie, verduurzaming, tuin, keukenapparatuur en reizen. Alle resultaten blijven kandidaten: alleen een redactionele controle van officiële regels kan gratis deelname en Nederlandse toelating bevestigen. Geen automatische inzendingen door GitHub, geen garantie op volledige dekking. Bronfouten worden geregistreerd en wissen bestaande kandidaten niet.

De niet-voedingsscanner uit Kansenradar is gemigreerd naar `scripts/household_scan.py`, met paginering. Het gezamenlijke tabblad Huishouden & verzorging leest `household.json`. Exacte EAN alleen uit echte EAN-data; een product-ID is geen EAN. Een procentueel verschil gebruikt de getoonde actieprijs als noemer. Ontbrekende Action/Zeeman-prijzen blijven een dekkingsgat.

De oude Kansenradar-startpagina verwijst naar hier. Gitgeschiedenis en een `legacy-index.html` blijven behouden. De oude dagelijkse scanner krijgt geen eigen planning meer; deze repository verzorgt de gezamenlijke scan. Koopkracht blijft ongewijzigd apart.

De eigenaar-private Sites-versie blijft de opslag voor voorraad, profiel en deelnamestatus. Alleen openbare actiegegevens worden in deze repo opgenomen. Geen contacten, e-mailadressen, bewijs- of deelnamehistorie exporteren. De dagelijkse ChatGPT-taak kan geverifieerde openbare records bijwerken; GitHub Actions verzorgt discovery viermaal per dag. De hypotheekgrens wordt door de bestaande private dagelijkse taak bewaakt, niet door een verzonnen bankfeed in GitHub Pages.


## Integrale wensen uit eerdere gesprekken (scope en acceptatiecriteria)

**Harde projectgrens:** `DASPHHS/koopkracht` en alle AH/Jumbo/Lidl-recepten en supermarktacties blijven een volledig afzonderlijk project; deze repository mag daar niets in wijzigen.

- **Persoonlijke productradar:** Arc'teryx heren XL, Salomon EU47/47⅓, HOKA EU47⅓ (Arahi/Kawana/Gaviota), Adidas Metalbone Carbon/HRD+, padelballen, Weleda Skin Food, Giraffe Original Blend, Davines, Rituals, Janzen Earth, Marie-Stella-Maris, Apple, Dyson, Ralph Lauren, Tommy Hilfiger, Nike, Adidas, premium outdoor/sneakers, herenmode, verzorging en luxe woonproducten. Relevante nieuwe merken mogen worden ontdekt. Geen algemene Pepper-stortvloed.
- **Bewijs boven aantallen:** alleen passende variant, maat, werkelijke voorraad, actuele prijs incl. verzendkosten en onafhankelijke referentie vergelijken; bij voorkeur >=25% echte besparing. Toon ruwe feedvondsten apart als ongecontroleerd. Bewaar prijshistorie, dedupliceer en meld mislukte bronnen.
- **Sample sales:** online én fysiek, uitzonderlijk relevante herenmode, schoenen, outdoor, verzorging, design en elektronica; Randstad/Bleiswijk als basis, heel Nederland bij uitzonderlijke kans. Altijd data, locatie/link, toegang/tickets, bekende maten, prijsstatus en reden; toekomstig event als 'sale-alert', nooit automatisch als bewezen productdeal.
- **Winacties:** veel meer relevante Nederlandse en internationale acties waarvoor een inwoner van Nederland aantoonbaar mag deelnemen, incl. reizen, auto's, technologie, wellness; controleer einddatum, deelnameregels, privacyvoorwaarden en werkende deelname-link. Geen onbevestigde claims over automatisch invullen of deelname.
- **Financieel voordeel:** hypotheekrente-alert onder 3,6%, energie, internet/tv, mobiel, zorg- en andere verzekeringen, subsidies/duurzaamheidsleningen, cashback, kortingscodes, Black Friday-prijsbaseline, sample-sale-agenda, contractvervaldata en objectieve bespaarvergelijkingen. Neem Tesla-laden en andere relevante mobiliteitskosten mee waar betrouwbare tarieven beschikbaar zijn.
- **ING Punten:** puntenwaarde, bijbetaling, verzending, geldigheid, alternatieve winkelprijs en persoonlijke relevantie; 51.000 punten is slechts lokaal ingevoerde indicatie, geen banksynchronisatie.
- **Reizen/wellness:** bijzondere arrangementen, bosrijke wellness/hotels voor twee rond €100 per nacht waar haalbaar; verifieer werkelijke totaalprijs en voorwaarden.
- **Slimme Kansen:** géén limiet van tien ideeën; praktische, verrassende, direct toepasbare automatiseringen voor iPhone/iOS, Mac, Gmail, Outlook, Google Agenda, Trello, SmartThings, WoonVeilig, huishouden, onderhoud, werk als docent, sport, financiën en dagelijks leven. Beschrijf per idee concrete trigger, actie, benodigde apps/rechten, kosten, privacy, eerste stap, beschikbaarheid en geschatte winst. Ontdek nieuwe mogelijkheden via officiële release-notes en Reddit, maar scheid onderzoekssignalen van bewezen functies.
- **Gezondheid en persoonlijke verbetering:** bredere wetenschappelijk onderbouwde innovaties in tandheelkunde, haar, huid, uiterlijk, welzijn en relevante medicijnen/behandelingen; vermeld bewijsniveau, regulatoire beschikbaarheid, veiligheidsrisico's, nazorg en realistische kosten. FUE/DHI NL/Turkije nooit op korting alleen selecteren; controle arts, kwalificaties, complicatieopvang en reis-/nazorgkosten.
- **Alerts en UX:** overzichtelijk mobiel dashboard, instelbare product- en drempelalerts, e-mailoverzichten, vroegtijdige uitzonderlijke sale-alerts, duidelijke categorieën, topaanbevelingen, bronlinks, statussen en geen dubbele Gmail-berichten. Uurlijkse monitoring mag alleen nieuwe, verifieerbare kansen versturen; geen aankoop/boeking. Meld fouten expliciet. Geen schijnzekerheid over externe accounts of werkende automatisering.

**Status:** dit is een functionele specificatie, geen claim dat alle functies al gebouwd of geverifieerd zijn. Houd in het dashboard zichtbaar wat werkt, gedeeltelijk werkt of nog onderzoek vereist.
