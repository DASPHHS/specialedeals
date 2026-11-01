# Weekdeals Bleiswijk — automatische aanbiedingen zonder Google Cloud

**Website:** https://dasphhs.github.io/specialedeals/weekdeals/

Dit project draait volledig via GitHub Actions en GitHub Pages. Er zijn geen
eigen servers, serviceaccounts of geheime API-sleutels nodig voor de publieke bronnen.

## Wat werkt nu?

De API van PrijsProfeet levert een grote, gepagineerde selectie Nederlandse
supermarktacties. De dagelijkse GitHub-run controleert de volledigheid vóór
publicatie en schrijft `weekdeals/deals.json` naar GitHub Pages.

Daarnaast wordt `weekdeals/nonfood.json` dagelijks opnieuw opgebouwd met
zichtbare productaanbiedingen voor Kruidvat, Etos, Trekpleister, Action en Wibra
via de openbare productselectie van FeedMyCart. DA komt rechtstreeks van de officiële DA-aanbiedingenpagina en Intratuin van de eerste drie pagina's van zijn officiële aanbiedingenoverzicht.

**Geverifieerde stand 1 november 2026:** 219 niet-supermarktproducten en
-acties: Kruidvat 40, Etos 40, Trekpleister 40, DA 24, Action 17, Wibra 13, Intratuin 45.
Dit is **niet de volledige folderinhoud**. Onder de 40 Kruidvat-acties zijn
39 acties waarvoor de openbare bron wél de korting maar géén europrijs noemt.
Deze worden als `Prijs niet vermeld` weergegeven.

Het DA-overzicht geeft op de eerste HTML-pagina 24 producten. Een vermelde
artikelprijs bij `2+3 gratis` is **niet** de effectieve prijs van vijf stuks.
Het einde van zulke DA-acties wordt niet vermeld: die regels zijn slechts
geldig als gecontroleerde momentopname van vandaag. Niets wordt verzonnen.

## Codebestanden

| Bestand | Functie |
|---|---|
| `sync_deals.py` | PrijsProfeet ophalen, paginering, kwaliteitscontroles; optioneel Sheets-writer |
| `publish_json.py` | API-aanbiedingen compacter publiceren in GitHub Pages |
| `publish_nonfood_deals.py` | Productkaarten van vijf overige winkelketens controleren |
| `da_adapter.py` | Officiële DA-aanbiedingenpagina uitlezen (naam, prijs, actie, bronlink) |
| `intratuin_adapter.py` | Officiële Intratuin-productkaarten: prijs en van-prijs |
| `publish_folders.py` | Alleen foldermetadata (geen productprijzen), apart van de productimport |
| `tests/test_sync.py` | Supermarkt-API en foutcondities |
| `tests/test_nonfood.py` | Productkaarten, promoties zonder prijs, vervaldatums |
| `tests/test_da_adapter.py` | Officiële DA-productkaarten en onbekende einddatum |
| `tests/test_intratuin_adapter.py` | Verifieerbare actieprijzen, uitsluiten onduidelijke bundels |
| `tests/test_publish_json.py` | Eenheidsprijs, ledenprijs en Aldi-bundeltotaal |

### Dagelijkse jobs

- `.github/workflows/publish-weekdeals.yml` — supermarktproducten dagelijks om
  05:45 UTC (06:45 winter / 07:45 zomer).
- `.github/workflows/publish-nonfood-products.yml` — niet-supermarktproducten
  dagelijks om 06:10 UTC (07:10 winter / 08:10 zomer).
- `.github/workflows/publish-weekdeals-folders.yml` — losse foldermetadata,
  niet nodig om individuele productprijzen te kunnen bekijken.
- `.github/workflows/weekdeals-google-sheets.yml` — optioneel, **alleen handmatig**.
  Niet ingeschakeld voor automatische uitvoering: geen Google Cloud nodig.

## Dataveiligheid en eerlijkheid

De website controleert publicatiedatums, winkel, actieprijs en (wanneer bekend)
kortingspercentage. Producten zonder concrete prijs mogen alleen zichtbaar worden
als een échte actieomschrijving is gevonden. Bij een onbekende einddatum geeft
de site dat duidelijk aan en toont de productmomentopname alleen op de
controle-dag. Uit landelijke aanbiedingen volgt **geen** lokale voorraadgarantie
voor Bleiswijk of omgeving.

Publieke bronnen: [PrijsProfeet](https://www.prijsprofeet.nl),
[FeedMyCart](https://feedmycart.nl/en/countries/netherlands/),
[DA](https://www.da.nl/aanbiedingen) en [Intratuin](https://www.intratuin.nl/aanbiedingen). Voor Xenos, Zeeman, HEMA en bouwmarkten zijn nog geen voldoende betrouwbare productfeeds geactiveerd.

Opmerking over andere scrapers: een Playwright-script dat alleen een installatie-
instructie geeft is niet reproduceerbaar zonder het werkelijke `.py`-bestand.
Folderz gaf bij de GitHub-proef een lege HTTP 202-reactie, en Folderwijzer
blokkeerde productpagina's met HTTP 403. Die worden daarom niet als
werkende productimport aangemerkt.

## Zelf controleren of alles werkt

Open het tabblad **Actions** van de GitHub-repository, selecteer de
`Publish Nonfood Product Deals`- of `Publish Weekdeals Bleiswijk`-workflow,
en controleer of de laatste run **success** heeft. Open daarna de website en
selecteer `Drogisterij & andere winkels`. Filters en CSV-export werken zonder login.


## Verder onderzoek en prijscontrole — 1 november 2026

Checkjebon (https://github.com/supermarkt/checkjebon) levert een open
supermarktprijsdataset met verpakkingsmaten, ook een deel Picnic. Dit is
bruikbaar voor prijsvergelijking, maar **niet** automatisch bewijs dat iets
in de aanbieding is. De huidige website gebruikt deze dataset nog niet.
Vergelijking vereist eerst gelijke productidentiteit, inhoud en voorwaarden.

PrijsProfeet (https://github.com/PrijsProfeet/supermarkt-api) levert al
\`unit_price\`, \`unit\`, \`multi_buy_quantity\`, \`multi_buy_price\`,
\`loyalty_price\` en \`loyalty_program\`. Deze gegevens zijn nu toegevoegd aan
de compacte supermarktfeed en website. Bij Aldi kan het bronveld \`price\`
het bundeltotaal voorstellen; het wordt niet als enkele artikelprijs
gepresenteerd.

KortingKlok (https://github.com/RashadAnsari/KortingKlok) is een open-source
voorbeeld voor snapshots en prijsgeschiedenis, nog geen actieve bron.

De publieke FeedMyCart-index meldt duizenden NL-aanbiedingen, maar de
meeste categorie- en ketenpagina's tonen slechts de top 40. Extra
categoriepagina's leverden hoofdzakelijk dubbelen en zijn dus nog geen
volledige folder-export. Verder uitrollen vereist een expliciete, betrouwbare
en toegestane productfeed.

Intratuin (https://www.intratuin.nl/aanbiedingen) toont veel meer dan drie
pagina's aanbiedingen. De huidige adapter haalt bewust slechts drie pagina's
op en accepteert alleen aantoonbare actieprijs én normale prijs.
De einddatum is niet bekend; een import geldt als momentopname voor
de kalenderdag waarop is gecontroleerd.

GAMMA gaf bij de GitHub-test HTTP 429 en Praxis HTTP 403.
Dit is geen bewezen werkende productimport; blokkades worden niet omzeild.
