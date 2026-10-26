# Bronnen en ontwikkelstatus

Bijgewerkt: 25 oktober 2026. Dit document beschrijft implementatie en ontbrekende dekking; het is geen verklaring dat alles werkt.

## Acceptatie en afbakening

Eén dashboard voor persoonlijke premiumdeals, Nederlandse/internationale winacties, sample sales, contractbesparingen, AI en innovaties. Herenmaten en persoonlijke merken uit README zijn leidend. Boodschappenmaatje, AH/Jumbo/Lidl en recepten worden niet gewijzigd. Geen willekeurige aantallimiet op gepubliceerde deals. De winactiefilter verwijdert zoekruis zoals Windows, WinRAR en woordenboekpagina’s; 45 bestaande ruisrecords zijn verwijderd.

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
| Daisycon | REST/JSON publisher-API, productfeeds en promoties | Voorstel: elke 4 uur | Partnerdata binnen toegestane campagnes | Account, OAuth en campagnerechten ontbreken; niet aangesloten |
| Reddit | Officiële OAuth Data API voor structurele toegang | Dagelijks | Onderzoekssignalen | Huidige openbare uitlezing geeft deels 429; geen betrouwbare volledige dekking |
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

- https://daisycon.com/en/developers/api/
- https://faq-publisher.daisycon.com/hc/en-us/articles/24827817954193-Daisycon-API
- https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- https://schema.org/Offer
- https://schema.org/OfferShippingDetails
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

## Directe winactiebronnen

`contest-sources.json` registreert vier directe HTML-overzichten: GratiZ, Prijsvragen.nl auto, Prijsvragen.nl reizen en Winacties.nl reizen. `contest_scan.py` leest deze naast de bestaande meertalige zoekopdrachten. Iedere kandidaat bewaart vindplaats en bronnaam. Bekende trackinglinks worden uitgesloten. De bronstatus meldt uitleesfouten en lege resultaten. Dit zijn HTML-adapters, geen geclaimde publieke API's. De bron garandeert geen actuele deadline of NL-toelating: inhoudelijke controle blijft vereist voordat een kandidaat in 'Gecontroleerd en open' terechtkomt. De standaardweergave toont alle gevonden acties met zichtbare status. Filters omvatten langdurig gratis producten, cadeaubonnen, hotels/wellness en sport/fietsen.


## Verificatie en prioriteiten per 26 oktober 2026

**Technisch getest**

- `scan.yml` en `ai-kansen.yml`: daadwerkelijke GitHub Actions-runs opnieuw succesvol; `site_check.py`, Node- en Python-regressietests doorlopen.
- GitHub-publicatiecontrole: bij gelijktijdige wijzigingen kan de push mislukken. Beide publicerende scanworkflows gebruiken nu maximaal vijf veilige fetch/rebase/push-herpogingen. De eigenaar-issue voor alerts is via dezelfde concurrency-groep geserialiseerd.
- Homepage heeft nu eerst een deadlinegerichte actielijst van recent gedocumenteerde Nederlandse/toegankelijke gratis winacties en aangekondigde sample sales. Verbergen is een lokale voorkeur, geen claim van inschrijving. Dubbele kaartenlijsten staan ingeklapt.
- Contractvergelijking: 12/24-maandskosten en cashback/cadeau/geschatte doorverkoop na kosten; nooit een gegarandeerde financiële opbrengst.
- Privé-bespaarteller: alleen door gebruiker bevestigde, daadwerkelijk betaalde eindprijzen in browseropslag op dat apparaat, met export/wissen. Een totaal op de homepage is alleen zelfrapportage. Geen veilige synchronisatie tussen apparaten.
- Reddit: naast zoekmachine-RSS worden publieke officiële r/zuinig en r/frugal Atom-feeds op relevante onderwerpen onderzocht; nieuwe posts blijven alleen onderzoekskandidaten. r/frugal geeft op de eerste run HTTP 429, dat wordt als beperking gemeld.
- De businesslogica telt nu alleen inhoudelijk relevante merk-/producthits voor de 59 gerichte zoekopdrachten. Een Bing-pagina met tien Ajax-resultaten is niet tien gevonden deals. Bij afwezigheid van onafhankelijke totale prijsbewijzen wordt Deals **gedeeltelijk** en niet *werkt*.

**Werkelijke resultaten / onbevestigd**

- Laatste gecontroleerde productzoektocht rond 26 oktober: circa 151–215 ruwe vermeldingen, ongeveer 1–2 persoonlijke feedvondsten, **nul** onafhankelijke, volledig controleerbare koopdeals. Er is één exact EAN-prijsverschil van €1,50 bij Weleda Skin Food 75 ml gevonden, exclusief niet-gevalideerde vracht.
- Zes recente aangekondigde sample sales in de agenda. Exacte herenmaat, aanwezigheid, tickets en korting moeten per evenement worden gecontroleerd.
- Achttien redactioneel geregistreerde winacties en veel meer onbevestigde kandidaatvondsten. Geen garantie op deelname of winst. Een al ingezonden actie wordt niet automatisch als ingediend geregistreerd vanuit GitHub Pages.
- Drie nieuwe Reddit-posts gevonden over refurbished Miele, kortingscodesites en Meervoordeel overstappen. Dit zijn nog **onbevestigde** ideeën, geen automatisch toepasbare persoonlijke aanbiedingen.
- E-mail: één Gmail-verzonden `Speciale Deals | Dagoverzicht` op 25 oktober aangetroffen. Elke dag daadwerkelijk versturen, ontvangen en dedupliceren is nog niet end-to-end bewezen.

**Nog open en daarom niet als 'werkt' markeren**

1. Breed actuele, aantoonbaar betere all-in prijzen per exacte maat/SKU inclusief buitenlandse verzending.
2. Betrouwbare gestandaardiseerde bronfeeds, niet uitsluitend RSS-hitlijsten; branche-API's vereisen geautoriseerde toegang.
3. E-mail en iPhone-notificaties volledig verifiëren, inclusief ontvangen bericht, anti-dubbel en gebruikersinstellingen.
4. Privécontracten automatisch en veilig synchroniseren, eigen offerte vergelijken, hypotheekrente onder 3,6% controleren via betrouwbare banktarieven.
5. Apparaatoverstijgende privébesparingen en deelnamehistorie, alsook werkelijk uitvoerbare AI-integraties via passende autorisatie.
6. Browsertests op echte iPhones en andere mobiele apparaten, niet uitsluitend code- en JSON-regressietests.

**Afbakening blijft absoluut:** geen wijzigingen, synchronisatie, migratie of aanroepen naar de afzonderlijke hernoemde supermarkt- en receptenrepository.



## Dagelijkse kwaliteitscontrole 26 oktober, Reddit en daadwerkelijke kosten

- Baseline scanner 40288333231 en Pages 40288490379 geslaagd. Nog slechts één onbevestigde feedmatch, nul bewezen persoonlijke all-in koopdeals; 0/59 gerichte productqueries met bruikbare uitkomst. Geen brede 'werkt'-claim.
- Engelstalige bespaartactieken vielen door Nederlandse trefwoorden weg; parser uitgebreid met shipping/coupon/price/broadband/renewal en r/Netherlands. Regressietest verifieert dat deze leads kandidaat blijven. Automatische officiële tekstherkenning krijgt contentHash en expliciet humanReviewed=false.
- Doorverkoopcalculator corrigeert verlies: €10 opbrengst minus €25 verkoopkosten is -€15, niet €0. Python- en Node-regressies geslaagd.
- Nieuwe strategieën: alleen benodigde artikelen bundelen voor verzenddrempel; FNV-code op aanbiedingen ongeschikt; retentie en overstap vergelijken op gelijke looptijd blijft onderzoekskandidaat tot echte offertes beschikbaar zijn. Meervoordeel-claimroute verschilt per cadeau/provider; geen twee keer €100 cashback/kaart tellen.
- De Online Drogist gecontroleerd: Skin Food 75 ml €8,99, standaard verzending onder €25 €3,95. Eén tube €12,94 tegenover drie tubes €26,97; meer tubes is niet automatisch minder totale uitgave. Dit is geen checkouttest of marktlaagste claim. Punten pas na echte verzilvering tellen. Davines-prijs niet herbevestigd.
- Lloyds officiële tarief-PDF geldig vanaf 23 oktober gelezen; laagste gevonden tarief 3,70%, geen <3,60%-treffer in deze bankcontrole. Geen volledig marktoordeel; Rabobank tarieftabel niet uit gelezen publieke tekst verkregen.
- Geautoriseerde privé-Site-read geslaagd; geen privévelden naar publieke repo gekopieerd. Vier publieke dashboardroutes en BIKE24-verzendpagina op bereikbaarheid gecontroleerd, geen volledige mobiele UI-test.
- Gedetailleerde dagstatus: quality-review.json. Inhoud beschikbaar voor het bestaande centrale dagoverzicht; geen tweede gewone dealmail verzonden. Definitieve nieuwe Actions/Pages-verificatie vastleggen in Issue #5.
- Hernoemde boodschappen-/receptenrepository niet benaderd of gewijzigd.

## Winactieradar, 26 oktober 2026

- Gebouwd en lokaal getest: officiële URL-hercontrole voor alle bestaande acties, inhoudshashes, zichtbare bronuitval, trackingdeduplicatie en geen nieuwe persoonlijke deelnameopslag op GitHub Pages.
- Inhoudelijk herlezen: Wibra Topolino, ANWB droomvakantie en Méribel; maximum één deelname vastgelegd. Wanderlust verbiedt automatische inzendingen expliciet.
- Gedeeltelijk: discovery via bestaande NL/EN/DE/FR-zoekopdrachten en aggregatorpagina's. Geen universele dekkingsgarantie. Nieuwe Columbus-bron en twee elektronicaleads toegevoegd; deze leads blijven ongeverifieerd.
- Nog te verifiëren: dagelijkse inhoudelijke herbeoordeling van iedere nieuwe kandidaat. Technische URL-check is geen inhoudelijke toets.
- Geen automatische formulierinzending gebouwd. Definitieve prijstrekkinginzending blijft gebruikershandeling. Bevestigingen en vier deelnamestatussen uitsluitend in een geautoriseerd privéregister.
