# Verlanglijst- en prijs-API-onderzoek — 1 november 2026

## Korte conclusie

De aangeleverde bronlijst bevat precies **23 niet-lege zoekprofielen**. Deze staan voortaan 1-op-1 in `wishlist.json.searchProfiles`; 20 zijn fysieke producten/productfamilies, 3 zijn contractvergelijkingen (*internet+tv*, *unlimited sim-only*, *gas+elektra*), terwijl **bijzondere sample sales** een evenementzoekprofiel is. Daardoor zijn het 19 productgerichte profielen, drie contractprofielen en één eventprofiel. De verschillen tussen afzonderlijke profielen en gegroepeerde scan-IDs (MacBook Air/Pro, HOKA Arahi/Kawana) zijn expliciet vastgelegd.

## Wat werkt al

- Verlanglijst-site: lokale wensen beheren, import/export, gefilterde kandidaten tonen.
- Centrale productcatalogus + onderzoeksroutes: gecontroleerd bijgewerkt, bestaande bronfilters.
- Bestaande productfeeds: PrijsProfeet en openbare winkelacties/nonfoodselectie; prijsreferenties zijn **niet** onafhankelijk geverifieerd.
- Nieuwe `integrations/merchant_feeds/adapter.py`: leest uitsluitend door de gebruiker/aanbieder rechtmatig beschikbaar gestelde CSV/JSON-bestanden en normaliseert product, GTIN, winkel/offer-ID, variant, prijs, valuta, bezorging, leverland, stockclaim en observatiedatum. Geen account, automatische download of extern API-toegang geconfigureerd. Het resultaat is **uitsluitend onderzoekskandidaat**, nooit een geverifieerde korting.

## Relevante open-source projecten

| Bron | Wat we overnemen als *ontwerppatroon* | Grenzen |
| --- | --- | --- |
| [Spryker MerchantProductOfferWishlistRestApi](https://github.com/spryker/merchant-product-offer-wishlist-rest-api) | Scheid een identiek product van het merchant-specifieke aanbod via `productOfferReference` en `merchantReference`. | Spryker PHP-commerce-extension, **proprietary** licentie, geen algemene prijszoek-API. Niet installeren op een statische GitHub Pages-site; code niet klakkeloos kopiëren. |
| [PriceBuddy](https://github.com/jez500/pricebuddy) / [REST API](https://pricebuddy.jez.me/api) | URL-per-aanbieding, prijsverloop, doelprijzen, voorraadstatus, eigen account/API. | Zelf hosten met Docker; niet automatisch een open webshopcatalogus. Rechten en store-/pagina-instellingen nodig. |
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | Monitor wijzigingen aan toegestane productpagina's, waarschuw bij prijs/voorraadwijziging. | Pagina-afhankelijk, geen betrouwbare landelijke prijsvergelijker of autorisatie voor anti-bot-omzeiling. |
| [KortingKlok](https://github.com/RashadAnsari/KortingKlok) | Snapshot-diffs, historische prijs, notificatie per gevolgde SKU. | GitHub-repository is gearchiveerd; specifieke scrapers zijn kwetsbaar voor winkelwijzigingen en gebruiksvoorwaarden. |
| [Arc'teryx Deals Platform](https://github.com/wantai-dev/001-arcteryx-deals-platform) | Productformaat met kleur, maat, model, regio en stockveld. | Het eigen DATA_UPDATE_REPORT zegt dat sommige maat- en voorraadgegevens defaults/simulaties waren. Niet als voorraadbewijs gebruiken. |
| [Black Friday Deals](https://github.com/mRs-/Black-Friday-Deals) | Handmatig gecureerde kortingsmeldingen als onderzoekslead. | Vaak digitale/wereldwijde promoties; geen echte prijsbenchmark. |

## Gerichte externe API's/feeds

1. **Awin publisher productfeeds** — [handleiding](https://help.awin.com/developers/docs/product-feed-publisher-guide-intro). Relevante kandidaten zijn namen, productlinks, prijs en mogelijk verzendkosten; afhankelijk van merchant en toegangsrechten. Vereist publisheraccount en eventueel programmatoelating.
2. **Daisycon publisher API en productfeeds** — [API](https://daisycon.com/en/developers/api/) / [feedtoegang](https://faq-publisher.daisycon.com/hc/nl/articles/204990231-Hoe-gebruik-ik-de-Daisycon-productfeeds). Productfeeds en promoties, eerst mediaprofiel aanmelden en goedkeuring per campagne. Kansrijk voor elektronica, geur, outdoor en mogelijk telecom/energie-leads.
3. **TradeTracker webservices/productfeeds** — [publisher-uitleg](https://tradetracker.com/nl/kenniscentrum/for-publishers/). Productfeeds en promoties onder passende campagne/gebruikrechten. Niet standaard JSON REST; gedocumenteerde webservices kunnen SOAP gebruiken.
4. **Keepa API** — [documentatie](https://keepa.com/api-docs/): Amazon-producthistorie, productzoekfunctie en tracking. Betaald API-plan en tokens, betreft vooral Amazon en is geen vervanging voor NL webshopprijzen.
5. **bol Partner/Retailer API** — [documentatie](https://api.bol.com/retailer/public/Retailer-API/): producten/offers voor gemachtigde bol-verkopers/partners. OAuth en seller/partner-rechten nodig, geen gratis publieke consumentenprijszoeker.
6. **Google Merchant API** — [documentatie](https://developers.google.com/merchant/api/guides/products/overview): beheer van eigen Merchant Center-productdata. Het is niet een openbare Google Shopping-multiwebshopfeed.
7. **Schema.org Product / Offer / OfferShippingDetails** — [Offer](https://schema.org/Offer) / [shipping](https://schema.org/OfferShippingDetails): gestandaardiseerde veldnamen voor SKU/GTIN, offers, seller, beschikbaarheid en leverkosten. Alleen gebruiken op publieke pagina's waar toegang en hergebruik toegestaan zijn; markup is op zichzelf geen onafhankelijk kortingbewijs.

## Prioritering

**P1 — licentie-geschikte Awin/Daisycon/TradeTracker-productfeeds** voor de gewenste kleinere Nederlandse/EU shops. Met minimale mapping: `source/provider`, `merchant`, `merchantReference`, `offerReference`, `EAN/GTIN`, `exact variant`, `observedAt`, `itemPriceEUR`, `shippingEUR`, `shippingCountryConfirmed`, `deliveredPriceNL_EUR` en bronlink.

**P2 — specifieke producten waarvan alleen een product-URL bekend is**: optionele, toegestane price-watch met verandering van werkelijk geobserveerde prijs over tijd, niet blind vertrouwen op adviesprijzen. Hiervoor kan PriceBuddy/changedetection als zelf-gehost apart component dienen. Geen directe installatie of credentialdeling uitgevoerd.

**P3 — Amazon**: betaalde Keepa API geschikt voor goede historiek, pas gebruiken bij geldig abonnement en sleutel in GitHub Actions Secrets, nooit in publieke JSON.

**P4 — contracten**: eigen contractvergelijkingen en toestemming/partner-API nodig; gebruik de bestaande persoonlijke energiegegevens alleen privé, publiceer nooit adres/postcode/contractnummer/jaarlijks verbruik zonder uitdrukkelijke toestemming.

## Beleid voor elke kandidaat

- Geen externe API-account of live store-feed wordt als 'verbonden' gerapporteerd zonder echt werkende authenticatie, toestemming én succesvolle test.
- SKU/GTIN + variant + maat worden strikt vergeleken. Accessoires, maten en kleuren niet verwarren met gevraagde uitvoering.
- Alleen **verifieerbare** NL all-in prijs als levering NL bevestigd is; bij onbekend land/verzending blijft `deliveredPriceNL_EUR=null`.
- Winkelkortingspercentage, affiliate-oldPrice of catalogusprijs is géén aangetoonde besparing. Zonder onafhankelijk actueel/historisch bewijs geen verified deal.
- Voor abonnementen geldt totale contractlooptijd-/jaarkostenvergelijking, niet 'x% korting op webshopadviesprijs'.
- Afhankelijkheden installeren onder hun eigen licentie; externe software niet opnemen door kopiëren zonder licentiereview.

## Nog nodig voor werkelijk bredere webshopdekking

Een toegestaan affiliate publisher-account en geautoriseerde feeds of toestemming/URL's van extra webshops, plus desgewenst een kleine private backend voor per-gebruiker gesynchroniseerde persoonlijke wensen en pushalerts. Tot die tijd kan de standaardadapter **bestaande bestanden converteren**, niet autonoom alle webshops bevragen.
