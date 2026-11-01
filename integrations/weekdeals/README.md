# Weekdeals NL → persoonlijke Google Sheet

**GitHub Actions staat ingesteld op dagelijks 05:30 UTC:** 06:30 uur in de winter en 07:30 uur in de zomer. Het script gebruikt de openbare Nederlandse PrijsProfeet-API. De API-test werkt zonder Google-inlog; schrijven naar je Google Sheet vereist nog aparte autorisatie.

De eerste fase ondersteunt supermarktacties. Action, Kruidvat, Etos, DA, Xenos, Zeeman, Wibra, HEMA, Praxis, GAMMA, HORNBACH, Intratuin, bol en andere webshops zijn al opgenomen in de broninventarisatie in de Google Sheet, maar hebben nog geen productimport. Picnic is een afzonderlijke, accountgebonden potentiële adapter.

## Eénmalige veilige autorisatie

1. Maak een Google Cloud-serviceaccount dat de Google Sheets API mag gebruiken en maak een JSON-sleutel.
2. Deel de bestaande Google Sheet als **Bewerker** met het adres in het veld client_email uit de JSON-sleutel.
3. Open **GitHub → DASPHHS/specialedeals → Settings → Secrets and variables → Actions → New repository secret**.
4. Voeg twee secrets toe: GOOGLE_SERVICE_ACCOUNT_JSON (de volledige JSON-sleutel) en GOOGLE_SHEET_ID (de ID tussen /d/ en /edit in de URL van je Sheet). Optioneel: PRIJSPROFEET_API_KEY (gratis API-sleutel voor hogere limieten).
5. Open **Actions → Weekdeals NL to Google Sheets → Run workflow** en controleer daarna je Sheet en de workflow-log.

**Zonder deze secrets wordt er geen Google Sheet bijgewerkt.** De dagelijkse workflow kan dan alleen de importer en de live bron-API testen. Deel een privésleutel nooit via chat, een issue, een commit of een openbare spreadsheet.

## Datastroom en controles

De importer leest ALLE pagina's van /api/v1/products/promotional/all, waarbij per pagina maximaal 100 deals worden opgehaald. Hij controleert totalen, ontbrekende product-ID's, nulresultaten, dubbele IDs en veranderingen tijdens paginering.

Hij bewaart in Google Sheets onder meer de actieprijs, eventuele van-prijs, actieperiode, EAN, bundelprijs, ledenprijs, online/winkel-only en bronlink. Onbekende lokale voorraad of geschatte einddatum wordt gemarkeerd en niet als bevestiging gepresenteerd. De oorspronkelijke 49 demonstratierecords worden bij een geslaagde volledige import vervangen; toekomstige deals van andere adapters blijven behouden.

Vóór publicatie worden de resultaten naar het tabblad **API import - staging** geschreven en gecontroleerd. De daadwerkelijke vervanging van het tabblad **Alle deals** gebeurt met één Google Sheets batchUpdate. Weekweergaven gebruiken overlap met de lopende kalenderweek. Expired API-ID's worden eenmalig bewaard in **Historie**.

De volledigheidscontrole geldt voor de gerapporteerde PrijsProfeet-dataset, niet voor de werkelijkheid van alle winkels. Aanbiedingen zijn indicatief en lokale winkelprijzen kunnen afwijken. De gratis API vereist bronvermelding: [Aanbiedingen via PrijsProfeet](https://www.prijsprofeet.nl).

## Code en tests

Importer: integrations/weekdeals/sync_deals.py

Tests: integrations/weekdeals/tests/test_sync.py

GitHub Actions: .github/workflows/weekdeals-google-sheets.yml

API-specificatie: https://github.com/PrijsProfeet/supermarkt-api/blob/main/openapi.json
