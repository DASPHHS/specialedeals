# Kansenkompas — centrale eisen en voortgang

Bijgewerkt: 2026-10-28. Dit is de centrale publieke product-specificatie; geen privégegevens opnemen.

## Doel en afgifte
- Eén mooi, toegankelijk, mobile-first GitHub Pages-dashboard: https://dasphhs.github.io/specialedeals/
- Één ChatGPT-dagrapport dagelijks 08:00 Europe/Amsterdam, geen losse alert per categorie.
- Eén e-mail om 08:00 gewenst maar **NIET ingericht**: aparte veilige afzender, credentials en idempotente verzending nodig; ChatGPT-notificatie is geen gegarandeerde Gmail-verzending.
- Uurlijkse GitHub Actions-kandidatenscan is ingesteld. **Geen** volledige uurlijkse, onafhankelijke detailprijzen-scanner aanwezig; nooit suggereren van wel.

## Navigatie en UX
Start/Topkansen; Prijzen en wishlist; gecontroleerde winacties; sample-saleagenda; huisprojecten; broncontrole. Zoeken, filteren, mobiele kaarten, bronlink, betrouwbaarheidsstatus en controletijd. Ruwe leads niet op hoofdscherm; nul echte deals is acceptabel. Statuslabels: koopdeal, prijspeil, historisch/onbevestigd, verlopen, bronfout. Bewaren/verbergen alleen lokaal; deelnamehistorie nooit publiek.

## Strikte kwaliteitsregels
KOOPDEAL: >=10% aantoonbaar voordeel op exacte variant en NL all-in totaal tegenover onafhankelijk geverifieerde zelfde SKU/reële prijshistorie. Artikelvoorraad, verzendkosten, btw, invoer, garantie, conditie, betrouwbare winkel. **PRIJSPEIL**: laagste daadwerkelijk gecontroleerde huidige NL totaalprijs binnen vermelde set aanbieders, ook zonder korting. Historische notities nooit laagste actuele prijs noemen. Geen MSRP-rekenkorting of algemene categoriepagina's. Sorteer exact identieke uitvoering, maten/volumes/inhouden; abonnement en nieuw/refurbished apart. Toon actuele peildatum, prijs + verzendkosten, vergelijkingsbasis, directe productlink en € en % alleen indien onderbouwd.

## Productfocus
- Alleen Arc'teryx als algemeen outdoor-merk, heren L/XL, broeken W32/33/34; petten, handschoenen, tassen, Atom/Gamma/Beta/Alpha, softshell, hardshell etc. Breed internationaal retailerspectrum in de dagtaak.
- HOKA hardloopschoenen heren ongeveer EU47.
- Apple AirPods/Pro, MacBook Air/Pro, Watch Ultra; Dyson draadloos/handstofzuigers en vergelijkbare machines; padel, premium mode en huishoudelektronica.
- JANZEN Earth 46 verzorging inclusief douchefoam, Rituals Homme en Sport foam/deo, Giraffe Coffee Original Blend 350g/1kg (bonen/gemalen en abonnement afzonderlijk), YSL M7 alleen uitzonderlijk voordeel, YSL Y per concentratie en formaat.
- Black Friday/Cyber Monday alleen echte netto deal op wishlist/huisgezin; geen verhoogde schijnreferentie.

## Kansen
- Alleen officiële, gratis NL-toegankelijke winacties >=€250, vooral >=€1000; controleer deadline, uitsluitingen en officiële regels (ANWB, Columbus, merken). Geen pay-to-enter of leadgen-spam.
- Premium sample sales Nederland-breed, vereis echte locatie/datum/organisator/toegang. Geen dubbele merkpagina's of ongedateerde events.
- Huisprojecten: schilderwerk buiten en voortuin eerst; dan overkapping, schuur en isolatie/verduurzaming. Offertes en subsidies niet schatten.
- ING-voordelen controleren met echt rendement zonder privépunten publiek; reizen voor twee, incidentele AI-kansen, vaste-lastenoptimalisatie waar verifieerbaar.

## Technische acceptatiepunten
1. Detailprice crawler per exacte productvariant, met eenduidige product-ID, data herkomst, verificatie en shippingcalculatie, terughoudende foutafhandeling — **OPEN**.
2. UI toont onafhankelijke prijsvergelijking en gedocumenteerde discounts op gecontroleerde records — **GEDEELTELIJK**; momenteel veel indicatieve notities.
3. Bronmonitor en gedateerde geverifieerde winacties/sample-sales — **GEDEELTELIJK**.
4. Één in Gmail verzonden dagelijkse e-mail met deduplicatie en beveiligde secrets — **OPEN**.
5. End-to-end tests van JSON + UI op mobiel en desktop — **OPEN**.
6. Gedeelde ChatGPT-chat https://chatgpt.com/share/6ae20eb2-c284-83ed-98bf-475606cc2e3c — **NIET INGelezen**: link niet toegankelijk vanuit deze omgeving. Vereisten daarvan nog niet aantoonbaar gemerged.

De dagelijkse taak leest deze publieke configuratie en moet externe feiten zelf toetsen. GitHub Actions draait los van de ChatGPT-taak en is niet vanzelf een mailserver.
