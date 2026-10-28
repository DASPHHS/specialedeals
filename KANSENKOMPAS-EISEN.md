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
6. Gedeelde ChatGPT-chat: tekst door gebruiker aangeleverd en aanvullende voorkeuren verwerkt in taak en dit document; technische claims afzonderlijk te verifiëren.

De dagelijkse taak leest deze publieke configuratie en moet externe feiten zelf toetsen. GitHub Actions draait los van de ChatGPT-taak en is niet vanzelf een mailserver.

## Aanvulling: Pepper, huishoudradar en categorieprofiel (28-10-2026)
- Pepper en vergelijkbare dealsites dienen als ontdekking, niet als onafhankelijk bewijs. Toon bij echte koopdeals absoluut EUR-voordeel en percentage tegenover dezelfde actuele all-in SKU-prijs of echte prijshistorie. Rangschik op persoonlijk nut en netto besparing; ook uitzonderlijke deals buiten bekende merken.
- Nieuw `huishoudradar-config.json`: levensmiddelen, koffie, shampoo, wasmiddelpods, vaatwastabletten, schoonmaakmiddelen, toiletpapier, verf, gereedschap, tuin, discount- en huishoudartikelen. Bronnetwerk: supermarkten, drogisterijen, Action, Zeeman, Xenos, HEMA, Wibra en bouwmarkten.
- Maak onderscheid tussen structureel beste koop en tijdelijke aanbieding. Normaliseer naar EUR per wasbeurt/tablet/100 ml/liter/kg/stuk/m², en controleer vergelijkbare kwaliteit, verpakking, dosering, voorwaarden en beschikbaarheid. Geen winkel als goedkoopste aanwijzen zonder recente onafhankelijke gegevens.
- Favorietenfilters zijn toegevoegd in het GitHub Pages-verlanglijstscherm. Live unit-price crawler, prijs- en historieopslag en een automatische aanbevelingsmotor zijn **nog open**.
- De door gebruiker geplakte gedeelde-chattekst is nu gelezen. Toegevoegd: categoriefilters voor winacties (huis/tuin, auto's, reizen, uitjes, geld, elektronica, gratis spullen), premium/designer sample sales, geen Prijzenzolder-spam of herensokken, ANWB-kaliber grote hoofdprijzen. De eerdere beweringen in die tekst over wat al technisch werkt zijn niet als bewijs overgenomen.


## Bronnenonderzoek en dagtaak (28 oktober 2026)
- De dagelijkse ChatGPT-automatisering **Kansenkompas | Dagoverzicht**, dagelijks 08:00 Europe/Amsterdam, moet zelfstandig meerdere officiële webshops + onafhankelijke vergelijking + prijshistorie doorzoeken, niet slechts `data.json` samenvatten. Het bronnenregister heeft **165 onderzoeksstartpunten** en `onderzoeksplan.json` **30 concrete onderzoeksroutes**. Dit zijn **geen** 165 actieve of onafhankelijk gecontroleerde retaileradapters.
- Onderzoek prioriteitsproducten exact op variant, maat, conditie, EAN, complete bezorgkosten NL en checkdatum; per hoofdproduct streef naar 2-4 verschillende shops en minstens 1 onafhankelijke crosscheck. Zoek ook EU (DE/BE/FR/ES/IT etc.) maar zonder bekende NL-verzending en invoerkosten nooit all-in goedkoopste claimen.
- Scheid: (1) officiële huidige prijs zonder kortingsclaim, (2) aantoonbare tijdelijke korting >=10% op een eerlijke gedocumenteerde referentie, (3) prijsvoordeel tussen twee winkels zonder promotieclaim, (4) onverified discovery.
- Per dagelijkse output: echte deals met €/% en bronnen; laagste gecontroleerde SKU-prijs ook zonder deal; huishoudprijzen per effectief gebruik/kwaliteit; bouwmarkt; meerdere officiële grote winacties; geverifieerde toekomstige sample sales; bronbereik en afgekeurde/ontoegankelijke bronnen. Geen opvulling.
- Benut `bronnenregister.json`, `onderzoeksplan.json` en `BRONNEN-EN-VERIFICATIE.md`. Checkjebon-prijsschattingen en PrijsProfeet `historical`, `upcoming` of `shelf` zijn geen actuele promoties. Geverifieerde prijshistorie nodig voor korting; reguliere Apple Watch Ultra-voorraad/nieuwprijs is geen aanbieding.
- De ChatGPT-taak schrijft niet automatisch naar GitHub en Gmail-delivery is niet ingesteld. Uurlijkse GitHub-scanner blijft beperkter dan de dagelijkse onderzoeksopdracht totdat winkeladapters worden gebouwd.
