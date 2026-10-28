# Speciale Deals

Publiek dashboard: https://dasphhs.github.io/specialedeals/

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
- Apple Watch Ultra: exact model/generatie en conditie bepalen.
- Dyson hand-/snoerloze stofzuiger, JANZEN Earth, HOKA heren rond EU47.
- Arc'teryx heren XL: **het enige outdoor-merk**. HOKA blijft een afzonderlijke hardloopschoenenwens, geen algemeen outdoormerk.
- Rituals, verzorging, premium mode, padel en verrassende andere hoogwaardige aanbiedingen blijven interessante ontdekkingscategorieën.

**Voorkeuren uit de GitHub-lijst staan centraal voor de scanner.** De invoervelden op de publieke site bewaren wijzigingen voorlopig alleen in deze browser. Exporteer ze en werk `wishlist.json` bij voor gebruik door de centrale scanner en de dagelijkse ChatGPT-taak. De website kan zonder authenticatie geen persoonlijke GitHub-inhoud wijzigen.

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
