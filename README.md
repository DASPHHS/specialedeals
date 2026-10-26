# Speciale Deals — persoonlijke premiumradar

**Dashboard:** https://dasphhs.github.io/specialedeals/  
**Slimme Kansen:** https://dasphhs.github.io/specialedeals/ai-kansen.html  
**Hernoemde boodschappen- en receptenrepository:** volledig afzonderlijk en strikt buiten scope; vanuit dit project nooit benaderen of wijzigen.

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

Historisch is een huishoudscanner overgenomen uit Kansenradar. Deze is inmiddels uit de geplande workflow en webweergave verwijderd. Algemene huishoud-/supermarktacties en recepten vallen buiten de huidige scope.

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

## Dashboardverbetering 25 oktober 2026

Eén hoofdnavigatie met ingebouwde detailmodules en deeplinks. `system_health.py` en `system-health-ui.js` tonen bronuitval, ontbrekende modules en veroudering apart. Automatische discovery elke vier uur, zonder publicatielimiet voor deals. Totale ontdekuitval bewaart vorige vondsten met hun oude bewijsstatus. Ontwikkelstatus en bronkeuzes: [BRONNEN-EN-ONTWIKKELSTATUS.md](BRONNEN-EN-ONTWIKKELSTATUS.md). Dagmail en hypotheekfeed zijn niet door de repo geverifieerd.


## Internationale productdeals met Nederlandse bezorging (25 oktober 2026)

- `international-stores.json` registreert uitsluitend buitenlandse winkels waarvoor een **officiële Nederlandse verzendmogelijkheid** is vastgesteld, met bronlinks, regio en verzendbeleid. Op dit moment onder andere Bergfreunde (DE), BIKE24 (DE) en de Runnerinn/Smashinn-kanalen van Tradeinn (ES).
- `radar-config.json` bevat aparte internationale zoekopdrachten; `scan.py` verwerkt deze als **onbevestigde ontdekresultaten** en telt nul-resultaatbronnen eerlijk mee.
- Twee concrete internationale Arc'teryx-productpagina's zijn toegevoegd aan de productobservatie, met XL-uitvoering en buitenlandse afrekenkosten expliciet **niet bevestigd**.
- `international_delivery.py` berekent hoogstens een standaardtariefindicatie richting Nederland. Alleen werkelijk gecontroleerde variant, NL-afleverbaarheid, onafhankelijke marktvergelijking, btw/douane en checkout-totaal mogen een koopklare deal vormen. Retour- en garantievoorwaarden blijven zichtbaar als beslisinformatie.
- Het onderdeel Deals bevat een afzonderlijke weergave van buitenlandse winkels en een landfilter. Buitenlandse winkelvermeldingen zijn niet automatisch een geverifieerd koopje.
- De winactiepagina gebruikt `contest-ranking.mjs`: persoonlijke relevantie, prijswaarde, naderende einddatum, optionele nieuwsbrieven, benodigde inspanning en uitsluitend onderbouwde winkansgegevens. Onbevestigde Nederlandse deelname verschijnt niet als deelnameklaar.
- `system_health.py` markeert 0 persoonlijke dealmatches als **gedeeltelijk**, zelfs als alle bronverzoeken technisch geslaagd zijn.
- `PRIVACY-EN-INTEGRATIE.md` legt vast welke contract-, deelname- en e-mailgegevens nooit in het openbare project mogen belanden. De daadwerkelijke private sync is nog **niet gerealiseerd**.

Status na codewijziging: alle bovenstaande onderdelen zijn gebouwd, maar echte end-to-end internationale checkoutvergelijkingen en volautomatische persoonlijke contractinvulling zijn **nog te ontwikkelen**. Alleen succesvolle Actions- en Pages-runs bewijzen de technische publicatie, niet dat er al bewezen buitenlandse koopdeals zijn.

## Gerichte bespaarstrategieën en Nederlandse community-inzichten (25 oktober 2026)

- **Bronnen en onderzoeksresultaat:** `bespaarstrategien.json` bevat negen concreet uitvoerbare methoden voor contracten, premiumproducten en verzorging, met officiële pagina's of Reddit-ervaringen, actiepunten en toepassingsvoorwaarden.
- **Meervoordeel.nl:** geen reguliere webshop met goedkope producten; het platform biedt telecomabonnementen met cadeaus/cashback/promotie. Nieuwe-klantenvoorwaarden, 12/24-maandstotaalprijzen, extra bijbetaling en tijdige cadeauclaim worden gecontroleerd.
- **De Online Drogist:** officieel verzendbeleid, kortingspercentages ten opzichte van leveranciersadviesprijzen, minimumaantallen bij 1+1, spaarprogramma en beperking bij combineren van kortingscodes worden onderscheiden.
- **Reddit-onderzoek:** `strategie_scan.py` zoekt tijdens geplande scans herhaalbare tactieken en controleert zes officiële informatiepagina's; nieuwe posts zijn alleen onderzoekskandidaten. De geautomatiseerde Bing/RSS-zoekopdrachten kunnen leeg of geblokkeerd zijn en zijn geen garantie op dekking.
- **Berekening:** `bespaar-calculator.mjs` vergelijkt bestaande maandlasten over 12/24 maanden met een nieuwe actie, inclusief welkomstkorting, installatiekosten en exclusief gekozen cashback óf persoonlijke bruikbare cadeauwaarde. Geen statistische voorspelling of gerealiseerde besparing.
- **Mobiele UI:** de bespaarpagina toont standaard de drie meest waardevolle tactieken en op aanvraag de rest, met voorwaarden en primaire links. `bespaar-strategie-ui.mjs` slaat deze calculatorinvoer niet op een openbare GitHub-pagina op.
- **Automatisch en testbaar:** GitHub Actions controleert bereikbaarheid/termmatches, voert nieuwe Python- en JavaScript-tests uit en publiceert `strategie-scan.json`. `system_health.py` rapporteert deze bronnen als gedeeltelijke functionaliteit, gescheiden van werkelijk behaalde kostenverlaging.
- **Scope:** voor de hernoemde boodschappen-/receptenrepository wordt geen code gelezen of gewijzigd. Het incidenteel meetrekken van de oude huishoudscanner in Speciale Deals is uit de geplande workflow verwijderd.

**Nog niet gerealiseerd:** automatisch toepassen van kortingscodes, privécontracten inladen, echte gepersonaliseerde provider-offertes vergelijken en automatische claim-/contractacties. Deze worden nooit als voltooid gemarkeerd zonder concrete integratietest.


## Kwaliteitscontrole 26 oktober 2026

- Reddit-detectie uitgebreid voor Engelstalige shipping/coupon/price/broadband/renewal-termen en r/Netherlands. Kandidaten blijven ongeverifieerd. Een 429 wordt niet omzeild.
- Automatische trefwoordcontrole bewaart nu contentHash, verificationLevel=keyword_match_only en humanReviewed=false; geen handmatige herbevestiging suggereren.
- Cadeau-doorverkoopcalculator toont ook een nettoverlies wanneer verkoopkosten hoger zijn dan de opbrengst.
- Bespaarstrategieën bijgewerkt met NL-verzenddrempel, specifieke Meervoordeel-claimroutes en afwijzing van FNV-stapeling op actieproducten. Persoonlijke geschiktheid en checkout blijven afzonderlijke controles.
