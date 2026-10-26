# Toelating winacties

Gebruikersvoorkeur: uitsluitend legitieme acties in het publieke deelnameoverzicht. Aantallen zijn ondergeschikt aan betrouwbaarheid.

Een aggregator, HTTPS, bekende merknaam, gelezen voorwaarden of werkende URL bewijst op zichzelf geen legitimiteit. Discovery mag nooit automatisch een record naar contests.json promoveren.

Controleer vóór toelating: identiteit van organisator en relatie met officieel domein; specifieke actievoorwaarden en looptijd; daadwerkelijke Nederlandse toelating; prijs en wijze van toekenning; aankoop-, betaal-, nieuwsbrief- en marketingvoorwaarden; eventuele bijkosten en gebruik van persoonsgegevens. Ontbrekende informatie blijft onbekend. Geen voorafgaande betaling om een gewonnen prijs te ontvangen, geen verborgen loterijabonnement, geen nagebootste merkpagina of generieke leadformulieractie als aanbevolen kans.

Leg bevindingen met officiële bronlinks, datum en concrete evidence vast. Bij tegenstrijdigheden of onduidelijke organisator: reviewRequired=true; buiten het overzicht houden tot hercontrole. Redactionele controle verloopt na zeven dagen. Oude informatie niet als vers markeren zonder hercontrole.

Het dashboard toont uitsluitend open of toekomstige redactionele records met verplichte bewijsvelden. contest-candidates.json blijft onderzoeksinput; niet standaard of via een alles-filter mengen met deelnameadvies. Dit is een toelatingsfilter, geen nieuwe onafhankelijke audit van alle bestaande records.

## Bronnen en persoonlijke deelname
Mitspiel Nederland (https://mitspiel.nl/winacties) is een extra onafhankelijke aggregatie- en **ontdekkingsbron**, geen bevestiging van de Nederlandse deelnamerechten of officiële aanbiederstatus van elke actie. De scanner leest Mitspiel-detailpagina-URL's uitsluitend als onderzoeksresultaten. De officiële actiepagina en voorwaarden moeten separaat worden geverifieerd voordat een kandidaat in contests.json kan verschijnen. Hetzelfde geldt voor internationale Mitspiel-sites: lokale vermeldingen geven geen automatisch recht op deelname vanuit Nederland.

De winactiespagina kan per geverifieerde actie een **lokale gebruikersmarkering** bewaren nadat de gebruiker expliciet aangeeft een organisatorbevestiging te hebben ontvangen. Dat is niet hetzelfde als automatisch invullen, door de scanner geverifieerde inzending of gewonnen prijs. Browseropslag is apparaatgebonden en wordt niet naar GitHub verzonden. Bewaar geen persoonsgegevens of unieke bevestigingscodes in publieke JSON-bestanden.

### Automatisch deelnemen: nog niet geïmplementeerd
Voor echte indiening is een bevoegde interactieve browserworkflow nodig die per officiële website toestemming, formulier, indienknop en daadwerkelijke bevestiging controleert. Omzeil geen CAPTCHA's of registratie-/deelnamelimieten; verstuur niet meerdere inzendingen vanuit alternatieve e-mailadressen wanneer één inzending per persoon/huishouden is toegestaan. Zonder door de organisator bevestigde deelname is de status nooit 'ingediend'.
