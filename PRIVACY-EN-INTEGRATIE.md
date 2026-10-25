# Kansenkompas: privégegevens, contracten en één meldhistorie

Status: architectuurafspraak, **geen claim dat de beveiligde synchronisatie al werkt**.

## Gescheiden verantwoordelijkheden

- **Openbaar op GitHub Pages:** geverifieerde publieke deals, officiële winactievoorwaarden, sample-saleagenda, generieke productcategorieën, openbare merk- en maatfilters, prijswaarnemingen zonder klantidentificatie, bronfouten zonder credentials.
- **Alleen in een eigenaar-geautoriseerde privéomgeving:** namen/adressen, telefoons, geboortedatum, exacte contract-/polisgegevens, rekeningafschriften, betaling, klantnummers, Gmail-berichten, kalenderinhoud, inzend-/deelnamestatus, privé-notities, persoonlijke AI-actiegeschiedenis.
- **Alleen op het apparaat:** tijdelijke presentatie-instellingen, niet-gevoelige UI-favorieten. Dit is geen betrouwbare centrale opslag voor contracten of deelnamehistorie.

## Minimale privécontractstructuur

`contractId, type, provider, product, startDate, endDate, monthlyCost, annualUsage, renewalPrice, contractTerms, sourceRef, verifiedAt, nextReviewAt, ownerConfirmed, actionStatus`.

De velden mogen per contract verschillen. Een energierekening wordt op jaarlijkse levering, teruglevering, variabele/vastrecht-kosten en reële verbruiksgegevens vergeleken; nooit uitsluitend het voorschot.

Bekende aanbieders in eerdere gesprekken zijn **zoekaanwijzingen**, geen bewezen actuele looptijd of prijs. Controleer overeenkomst en wijzigingsdatum in de oorspronkelijke Gmail-bijlage/documenten of via geautoriseerde gebruikersinformatie voordat een bedrag of vervaldatum ingevuld wordt.

## Veilige synchronisatie

1. De eigenaar authenticeert bij de bestaande private Kansenkompas-dienst, of bij een ander werkelijk afgeschermd gegevenssysteem.
2. Inlezen van Gmail, Agenda en contracten gebeurt alleen op de geautoriseerde server/connector met minimale rechten; tokens blijven buiten HTML/JS, GitHub en issue-teksten.
3. De private dienst bewaart versleutelde gegevens, herkomst, verificatietijd, eigenaarbevestiging en wijzigingslog.
4. Een publiek GitHub Pages-dashboard mag **nooit** via een statisch meegeleverde API-sleutel privégegevens ophalen. Een privépaneel vereist server-side sessie/authenticatie of een expliciete overgang naar een apart beveiligd dashboard.
5. Publieke bestanden bevatten hoogstens anonieme totalen, zonder herleidbare contractstatus of persoonlijke deelnamegegevens. Geldbedragen en exacte einddatums niet automatisch publiceren.
6. Verwijderbaar, exporteerbaar en controleerbaar; geen automatische inschrijving, aanschaf, contractwijziging of financiële transactie zonder passende specifieke autorisatie.

## Centrale meldregistratie

De privé meldhistorie bevat `eventType, eventKey, productOrContestId, meaningfulChangeHash, channel, sentAt, deliveryEvidence, expiresAt`. Gebruik dezelfde idempotency-sleutel voor dagmail, uitzonderlijke alert, winactielijst en contractherinnering. Alleen nieuwe substantiële feiten rechtvaardigen een tweede melding.

## Buitenlandse winkelprijzen

- Bewijs NL-levering van de winkel en van het **specifieke product** afzonderlijk.
- Exacte maat, variant, prijs, btw, vracht, douane en eventuele inklaringskosten worden vastgelegd vóór een *bewezen koopdeal*.
- Een gepubliceerde standaardverzendstaffel is een indicatie, niet automatisch de checkoutprijs.
- Bij niet-EU verzending: alleen koopadvies als invoerrechten en alle belastingen bekend en verrekend zijn. Geen ongefundeerde 'tax free'-aanname.
- Retourkosten, retourrechten en garantie worden naast het netto prijsverschil zichtbaar gemaakt.
- `international-stores.json` bevat **uitsluitend** openbaar winkel- en verzendbeleid, geen adres of andere privégegevens.
