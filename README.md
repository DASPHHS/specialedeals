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
