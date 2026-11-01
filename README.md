# Speciale Deals

## Uurlijkse Top 10 koopjes per categorie

Nieuwe [Top 10 startpagina](https://dasphhs.github.io/specialedeals/topdeals/) met eigen deelbare categorieroutes:
`?categorie=persoonlijk`, `?categorie=tuin`, `?categorie=bouwmarkt`, `?categorie=supermarkt`, `?categorie=drogisterij`, `?categorie=elektronica`, `?categorie=sport`, `?categorie=huis` en `?categorie=overig`. Deze worden zowel vanuit de homepage, Weekdeals als de centrale verlanglijst gelinkt.

**Per uur:** GitHub Actions `.github/workflows/hourly-topdeals.yml` draait op `7 * * * *` (UTC; ieder uur) en publiceert een opnieuw gerangschikt `topdeals/data.json`. De UI toont precieze berekeningstijd, de laatst bijgewerkte **bronmomenten** en welke feeds ouder dan 48 uur zijn. De uurlijkse rangschikking gebruikt de nieuwste lokale bron-snapshots, **niet** een nieuwe live webshopscan per uur. De PrijsProfeet- en nonfoodbronnen blijven onder de bestaande afzonderlijke workflows binnenkomen. Verlopen aanbiedingen worden geweerd, onbekende einddatum alleen bij bronobservatie vandaag.

**Alleen aantoonbare informatie:** elk topaanbod heeft een geprijsd product en traceerbare HTTPS-link; retailer-advertentiekorting wordt als **winkelreferentie** gelabeld, niet onafhankelijk bewezen voordeel. Verzendkosten, exacte voorraad en lokale filialen zijn onbekend. Bundeltotalen worden niet als individuele prijs of berekend kortingspercentage gebruikt. Vergelijkbare winkelreferenties kunnen inconsistent zijn en worden dan verborgen; alle prijzen blijven onderzoekskandidaten. Meerdere winkeldeals per product kunnen apart worden vermeld als de verkoper verschilt. Zware uitsluitingsfilters verwijderen gevaarlijk/restricted aanbod, maar niet iedere producttitel is inhoudelijk geverifieerd.

**Personalisatie:** de `persoonlijk`-categorie geeft voorrang aan tekstmatches met `wishlist.json` en bewaart voorkeuren in de browser. Een match zonder exact SKU, ANC, maat of NL-totaalprijs is geen bevestigde koopdeal. Een categorie zoals bouwmarkt kan terecht 0 tonen zolang er geen bruikbare productfeed voor aangesloten bouwmarkten is. Een zoekresultaat of folderlink wordt niet automatisch tot echte korting gepromoveerd.

**Tests:** `python -m unittest -v test_hourly_topdeals.py`, `python hourly_topdeals.py`, `node ui/site-smoke.test.js`. Voor echte onafhankelijke korting vereist het project nog geautoriseerde merk-/winkeldata, SKU- en prijsvergelijking plus bevestiging van afrekenkosten. Geen user-specific alert e-mails worden automatisch verzonden door de openbare site.

Publiek dashboard: https://dasphhs.github.io/specialedeals/


## 23 aangeleverde wensen, inclusief contractvergelijkingen

De oorspronkelijke lijst met 23 ingevulde zoekprofielen staat nu volledig en in dezelfde volgorde in `wishlist.json.searchProfiles`. Gedeelde zoekgroepen (MacBook Air/Pro, HOKA Arahi/Kawana) verwijzen naar de juiste centrale productwens zonder een dubbel aanbod als afzonderlijke bewezen korting te tellen. Nieuw als afzonderlijke productwens: Dyson Airwrap, Arc'teryx Gamma broek, vergelijkbare Arc'teryx werkbroek, wit Arc'teryx logo T-shirt en betaalbare alternatieven voor luxe huisparfums.

Internet/TV, unlimited sim-only en gas/elektra staan apart in `wishlist.json.serviceProfiles`: dat zijn contractvergelijkingen zonder automatische webshopkorting. De verlanglijstpagina toont deze profielen afzonderlijk en vermeldt dat er nog geen rechtstreekse live contractfeed gekoppeld is. Sample sales vallen onder het bestaande `event-sales`-onderzoek.

Het uitgewerkte [GitHub- en API-onderzoek](integrations/merchant_feeds/RESEARCH.md) onderscheidt Spryker-product-aanbodverwijzingen (architectuur, géén openbare prijs-API), PriceBuddy/changedetection (eigen monitoring), Awin/Daisycon/TradeTracker (licentie-afhankelijke echte merchant productfeeds), Keepa (Amazon-prijshistorie) en bol/Google Merchant APIs (alleen met passende partner-/merchanttoegang). De standaard[feedadapter](integrations/merchant_feeds/adapter.py) normaliseert uitsluitend aangeleverde, toegestane CSV/JSON-productfeeds en promoveert nooit winkelkortingsclaims naar geverifieerde deals.

## Mijn verlanglijst — automatische productradar

De nieuwe [verlanglijstpagina](https://dasphhs.github.io/specialedeals/verlanglijst/) laat iedere centrale wens als eigen kaart zien, met **geverifieerde koopdeals** gescheiden van nog te controleren winkelacties. De pagina ondersteunt zoeken, statusfilters, sorteren, een richtprijs, eigen aanvullingen, varianten, link naar een product, import en export van JSON.

**Automatische index:** wishlist_radar.py leest de centrale wishlist.json en de reeds bestaande weekdeals/deals.json (PrijsProfeet), weekdeals/nonfood.json (FeedMyCart, DA.nl, Intratuin.nl) en verified-deals.json. De GitHub Action publish-wishlist-radar.yml maakt tweemaal per ochtend een compacte verlanglijst/signalen.json en publiceert die op GitHub Pages. De browser hoeft dus niet iedere keer de volledige supermarktfeed te downloaden.

**Bewijsstatus:** een productmatch is een *onbevestigde winkelactie*. Geadverteerde van-prijzen zijn geen onafhankelijk bewijs. Alleen recente controle van exacte SKU/model/variant, echte referentie, complete NL-totaalprijs en minimaal 10% daling mag koopdeal heten. Onbekende maten, ANC, conditie en voorraad worden expliciet niet bevestigd.

**Eigen wijzigingen:** nieuwe wensen en aangepaste richtprijzen worden lokaal in deze browser opgeslagen; de website heeft geen gebruikersauthenticatie of schrijftoegang naar de openbare centrale GitHub-lijst. Exporteer je gegevens als backup en neem nieuwe wensen op in de centrale [wishlist.json](https://github.com/DASPHHS/specialedeals/edit/main/wishlist.json) om ze ook automatisch in de centrale scanner en 08.00-ChatGPT-alert op te nemen. Er is **geen** automatische synchronisatie tussen apparaten en **geen** pushmelding.

**Webshopdekking:** geen enkele scraper kan legaal en betrouwbaar zonder API of toestemming alle webshops dekken. Deze versie verwerkt bestaande aangesloten bronfeeds en biedt per wens een handmatige bredere Google Shopping-zoeklink. Nieuwe winkelbronnen moeten als afzonderlijke betrouwbare adapter worden toegevoegd; er is geen anti-bot bypass. Geen winkelreferentiekorting wordt verward met onafhankelijk vastgesteld voordeel.

**GitHub-onderzoek:** inspiratie: [KortingKlok](https://github.com/RashadAnsari/KortingKlok) (prijs-snapshots en notificaties), [PriceBuddy](https://github.com/jez500/pricebuddy) (individuele URLs en prijsdoelen), [Arc'teryx Deals Platform](https://github.com/wantai-dev/001-arcteryx-deals-platform) (varianten en beschikbare maten). Het Arc'teryx DATA_UPDATE_REPORT.md waarschuwt dat sommige maat- en voorraadvelden fictieve defaults zijn: deze worden **niet** als feiten overgenomen. [Black Friday Deals](https://github.com/mRs-/Black-Friday-Deals) en promo-codes-topic zijn hoogstens ontdekkingsbronnen, geen winkelprijsbewijs.

Tests: python -m unittest -v test_wishlist_radar.py en node ui/site-smoke.test.js.

## Nieuwe gebruikersinterface (november 2026)

De website heeft een gezamenlijke visuele stijl voor [Speciale Deals](https://dasphhs.github.io/specialedeals/) en [Weekdeals](https://dasphhs.github.io/specialedeals/weekdeals/). De mobiele weergave heeft directe navigatie naar Ontdekken, Verlanglijst, Huisprojecten en Weekdeals.

**Ontdekken:** snelle filters voor *Buitenkansjes*, *Hoogste bewezen korting*, *Grootste besparing in euro's*, *Sluit binnenkort*, *Nieuw deze week*, *Mijn verlanglijst* en *Bewaard*. Met **Wis filters** terug naar het standaardoverzicht. Kansen kun je met **Bewaar** lokaal markeren; ze worden uitsluitend in deze browser opgeslagen. Buitenkansjes zijn geverifieerde koopdeals van minimaal 20% korting of minimaal €75 aantoonbaar voordeel, officieel gecontroleerde winacties met prijswaarde vanaf €1.000, of relevante door de organisator bevestigde sample sales. Onbevestigde kortingsclaims uit research-kandidaten blijven hiervan gescheiden. Nul resultaten is een correcte uitkomst als er geen bewijs is.

**Weekdeals:** extra filters voor concreet vermelde prijs, getoonde winkelkorting vanaf 30%, ledenprijs of bundelaanbieding; sortering op getoonde korting of artikelprijs, plus kaart- en CSV-overzicht. **Let op:** een door een winkel vermelde actie- of van-prijs bewijst nog geen echte prijsdaling ten opzichte van onafhankelijke historie. Weekdeals mag daarom geen geverifieerde prijsbesparing suggereren. Voor lokale prijzen en voorraad blijft een aparte controle nodig.

**Verlanglijst:** een knop **Herstel ontbrekende wensen** voegt nieuwe centrale wensen toe aan een oudere lokaal opgeslagen lijst, zonder eigen toevoegingen te overschrijven. Om gewijzigde voorkeuren naar de scanner te sturen, moet de centrale `wishlist.json` nog steeds in GitHub worden bijgewerkt.

Technisch: `ui/speciale.css`, `ui/deal-filters.js` en `ui/site-smoke.test.js`; CI via `.github/workflows/test-website-ui.yml`. De front-end houdt zich aan bestaande privacy- en prijsverificatieregels.

## Één centrale voorkeurenset

De configuratie is gescheiden van de scanners en van de website. De automatische GitHub-scan leest:

- `radar-profiel.json`: **alle globale afspraken** over gezin, regio, kwaliteitsnormen, premiummerken, uitsluitingen, grote winacties, sample sales, gewenste categorieën, huisprojecten en dagoverzicht.
- `wishlist.json`: **concrete producten**, productvarianten en eventuele maximumprijzen.
- `huisprojecten.json`: schilderwerk en voortuin voorop, daarna overkapping, schuur, isolatie en verduurzaming.
- `winactie-profiel.json`: grote hoofdprijzen, vanaf een aangetoonde waarde van €250; betrouwbaar en gratis.
- `verified-winacties.json`: bewust geselecteerde officiële acties met vastgelegde controles.
- `winactie-kandidaten.json`: **onbevestigde zoekvondsten**, nooit automatisch een betrouwbare hoofdprijs.

### Verlanglijst

- Apple AirPods **standaard** en Apple AirPods **Pro** apart.
- Apple MacBook: Air versus Pro, chip, RAM, SSD, scherm en toetsenbord moeten overeenkomen.
- Apple iMac: exacte chip, RAM, SSD, scherm en toetsenbordconfiguratie.
- AirPods-voorkeur: ANC vereist voor koopadvies; liever AirPods Pro.
- Lampe Berger / Maison Berger luxe huisgeuren, met goedkopere alternatieven afzonderlijk beoordeeld.
- Innovatieve USB4/Thunderbolt 4/5-hubs en hoogwaardige gadgets; geen gewone goedkope adapters.
- HOKA Arahi/Kawana of relevante stabiliteitsalternatieven rond herenmaat EU 47 1/3.
- Apple Watch Ultra: exact model/generatie en conditie bepalen.
- Dyson hand-/snoerloze stofzuiger, JANZEN Earth, HOKA heren rond EU47.
- Arc'teryx heren XL: **het enige outdoor-merk**. HOKA blijft een afzonderlijke hardloopschoenenwens, geen algemeen outdoormerk.
- Rituals, verzorging, premium mode, padel en verrassende andere hoogwaardige aanbiedingen blijven interessante ontdekkingscategorieën.

**Voorkeuren uit de GitHub-lijst staan centraal voor de scanner.** De invoervelden op de publieke site bewaren wijzigingen voorlopig alleen in deze browser. Exporteer ze en werk `wishlist.json` bij voor gebruik door de centrale scanner en de dagelijkse ChatGPT-taak. De website kan zonder authenticatie geen persoonlijke GitHub-inhoud wijzigen.

### Weekdeals + verlanglijst

De [Weekdeals-pagina](https://dasphhs.github.io/specialedeals/weekdeals/) toont een
aparte knop **Mijn verlanglijst**. De browser koppelt de openbare
supermarkt- en non-foodaanbiedingen aan de centrale `wishlist.json` met
variant- en accessoire-uitsluitingen. Dit zijn alleen **mogelijke matches**,
niet de geverifieerde koopdeals van de hoofdsite. Het verandert de bestaande
brondekking niet; de aanbieding en de exacte uitvoering blijven te controleren.

### Prijzen en koopadvies

**Harde minimumregel vanaf 28 oktober 2026: minimaal 10% aantoonbare, echte korting.** De actuele totale kassaprijs moet minstens 10% lager zijn dan een recent gecontroleerde prijs van exact hetzelfde product bij een onafhankelijke retailer of een gedocumenteerde echte transactieprijs uit de prijshistorie. Een adviesprijs (MSRP), producttitel met 'sale', losse Apple Watch Ultra-pagina, kortingsclaim of onduidelijke bron telt niet. Controle blijft 36 uur geldig.

- `deal-kandidaten.json`: ontdekte producten, NIET zichtbaar als koopdeal op de website.
- `verified-deals.json`: alleen door extra brononderzoek verifieerbare aanbiedingen met SKU/variant, winkel, concrete totaalprijs, onafhankelijke vergelijking, verzendkosten, voorraad, verificatiedatum en minimaal 10% korting.
- `deal_verification.py`: harde controle op prijs, exact model, verschil, onafhankelijke vergelijking, geldigheid en leverbaarheid. Onvolledige aanbiedingen worden geweigerd.
- De publieke site controleert de 10%-drempel opnieuw, ook wanneer oude data nog in de browser zit. Daardoor kan het koopdealoverzicht terecht leeg zijn.

**ING Punten:** `radar-profiel.json` bevat ook een beleid voor officiële ING-kortingscodes of Puntenwinkel-voordelen. Alleen kortingscodes met minstens 10% effectieve korting en een netto lagere prijs dan de marktprijs zijn interessant. De puntenkosten, eventuele bijbetaling, vervaldatum en voorwaarden moeten bevestigd zijn. Het persoonlijke puntensaldo wordt NIET in deze publieke GitHub-repository opgeslagen.

Een zoekresultaat is **geen** gecontroleerde deal. De scanner slaat alleen kandidaatvondsten op en kan niet garanderen dat iets de laagste prijs is. Een echte prijsvergelijking vereist het identieke artikel (EAN/SKU, model/generatie, uitvoering, conditie en maat), actuele voorraad, prijs plus btw, bezorging naar Nederland, eventuele invoerkosten, retourvoorwaarden, garantie en onafhankelijke concurrentprijzen of historie. Onduidelijke kortingpercentages zijn geen koopadvies.

In `data.json` staan de leesbare kandidaten, bronfouten, resultaten die aan verlanglijstitems gekoppeld zijn, en de laatste scan. Producten en Apple-accessoires/categoriepagina's worden zo goed mogelijk gescheiden; ook hier is validatie bij de bron nodig.

### Coverage en betrouwbaarheid

- Normale fysieke winkelacties: **maximaal 20 km vanaf Bleiswijk**, alleen als de vestigingslocatie is vastgesteld.
- Online deals: Nederland en betrouwbare buitenlandse winkels die aan Nederlandse klanten leveren.
- Premium sample sales: **heel Nederland**; alleen Arc'teryx wanneer het outdoor betreft.
- Winacties: **alleen** officieel gecontroleerde Nederlandse of internationale acties waarvoor deelname door Nederlandse inwoners expliciet mag en prijsbezorging/verzilvering in Nederland mogelijk is. Algemene zoekkandidaten blijven gescheiden.
- Geen herensokken, kleine weggevers, ruis, twijfelachtige verkopers, spam, prijzendumps of dubbele kaarten.

De scanner probeert publieke overzichten van onder meer Pepper, AlleFolders, SuperSales, Amac, Bever, Bergfreunde en Bergzeit, plus sample-sale-agenda's. Sommige sites blokkeren geautomatiseerde verzoeken; de bronstatus maakt dat inzichtelijk. Geen omzeiling van login of anti-botmaatregelen.

### Planning en dagelijkse taak

GitHub Actions draait meerdere scans per dag en op relevante configuratiewijzigingen. De bestaande **ChatGPT-taak om 08.00 uur (Europe/Amsterdam)** leest dezelfde centrale bestanden en moet daarnaast officiële deelnamevoorwaarden, bruikbare koopvergelijkingen en belangrijke uitzonderingen apart controleren. Deze taak is een ChatGPT-overzicht, **geen gegarandeerd verzonden Gmail-bericht**. Het ChatGPT-schema wordt buiten deze repository beheerd en is geen onderdeel van de GitHub Actions-workflow.

### Tests

`python -m unittest -v test_outdoor.py test_watchlist.py`

De workflow voert deze tests uit vóór elke scan. Ze controleren uitsluiting van andere outdoormerken, afzonderlijke Apple-modellen, geen accessoirefouten en behoud van primaire profielregels.

Deze repository is publiek. Sla hier geen adres op huisnummerniveau, wachtwoorden, privégesprekken of deelnamegeschiedenis op.
