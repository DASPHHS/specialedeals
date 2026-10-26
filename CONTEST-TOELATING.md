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

## Centrale radar en privéregister, 26 oktober 2026

`contest_review.py` controleert alle bestaande officiële actie- en voorwaarden-URL's bij iedere scan. `contest-rechecks.json` bevat alleen openbare paginahashes, bereikbaarheid, controletijd en ontbrekende bewijsvelden. HTML-wijzigingen zijn een hercontrolesignaal, geen bewijs dat de voorwaarden zijn gewijzigd. Een succesvolle download verlengt nooit `verifiedAt` en bevestigt nooit gratis deelname, Nederlandse toelating, maximumdeelnames of een inzending. Ontdekresultaten blijven kandidaten zonder publicatielimiet. Trackingvarianten van dezelfde link worden samengevoegd; verschillende campagneparameters blijven behouden.

Leg inhoudelijk vast: `entryLimit` (aantal, persoon/huishouden, periode en bewijs-URL), `costs` (deelnamekosten, aankoop en bijkosten), expliciete `eligibleFromNetherlands`, plus controle van eventueel verbod op automatische deelname. Ontbrekend bewijs betekent niet toegestaan aannemen.

Eén privéregister gebruikt exact **bevestigd ingediend**, **hulp nodig**, **nog niet ingediend** en **ongeschikt**. Een gebruikersmelding van eerdere deelname blokkeert herinzending, maar telt zonder bewijs van de organisator niet als bevestigd ingediend. Een onduidelijke of afgebroken inzending blijft geblokkeerd totdat de ontvangst is uitgezocht. Deduplicatie geldt over alle bronnen en e-mailadressen heen, per organisatorcampagne, deelnemer/huishouden en toegestane periode. Nooit openbare issues, logs of Actions-artifacts gebruiken voor dit register.

De definitieve browserinzending voor een prijstrekking vereist gebruikersovername volgens de browserregels. CAPTCHA, login, e-mailverificatie, verplichte marketing of onbekende toestemming zijn concrete hulpvragen. Bij expliciet verbod op bots of automatische inzendingen uitsluitend handmatige deelname. De openbare winactiepagina bewaart geen nieuwe persoonlijke deelnamemarkeringen; het privéregister wordt apart bijgehouden en is geen live ingelogde GitHub Pages-app.
