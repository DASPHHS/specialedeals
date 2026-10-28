# Kansenkompas 2.0 — product- en UI-roadmap

Status: voorstel, niet geïmplementeerd. Datum: 2026-10-28.

## Productdoel
Eén mobielvriendelijk persoonlijk beslisdashboard en één geconsolideerd ochtendoverzicht. Scheid onafhankelijk geverifieerde koopdeals, officieel geverifieerde gratis winacties, sample sales en ongeverifieerde onderzoeksleads. Geen aparte sample-sale-mails.

## P0: nuttig vanaf de start
1. Startscherm 'Vandaag': urgente deadlines, beste bewezen deals, voor jou relevante winacties, sample sales en huisprojecten; geen opvulling wanneer nul geverifieerde deals.
2. Uniforme kaarten met bronlink, verificatiestatus, controle-tijdstip, deadline, exacte voorwaarden, leverbaarheid, besparing/waarde en actieknop.
3. Dealvergelijker: identieke SKU/maat/conditie, all-in NL prijs, onafhankelijke referentie en >=10% netto voordeel; mislukte checks zichtbaar.
4. Winacties: officiële voorwaarden, NL-geschiktheid, gratis deelname, prijs >= EUR250, deadline, belastingen/bijkosten. 'Al meegedaan' alleen in private opslag.
5. Sample-sale-agenda met merk, locatie, datum, toegangskosten, relevantie; geen productkorting suggereren zonder bewijs.
6. Deduplicatie via SKU, contest-ID en event-ID; één dagoverzicht en bronstatus.

## P1: interactie en personalisatie
7. Feedback: bewaren, niet relevant, reeds gekocht, al meegedaan, verbergen; private opslag met authenticatie, nooit in publieke GitHub.
8. Persoonlijke score: prioriteit voor Apple, Arc'teryx XL, HOKA circa EU47, premium verzorging, reis voor twee en huisprojecten; scheid score van verificatiebewijs.
9. Watchlist met exacte varianten, doelprijzen en meldingsvoorkeuren.
10. Historie en audit trail: waarom gepromoveerd, gewijzigd, verlopen of afgewezen; broncontroles en fouten.
11. Optionele integratie van hypotheek/vaste lasten, AI-kansen en privéregister, alleen met private gegevensopslag.

## P2: UX en operatie
12. Mobiel-eerst, toegankelijkheid, snelle zoekfunctie, filters op urgentie/categorie/status, kalender- en kaartweergave.
13. Bronkwaliteit-dashboard met laatste succesvolle controle en expliciete 429/403/foutstatus.
14. Testplan: geen dubbelmeldingen, geen valse kortingsclaims, geen privégegevens in publiek JSON, geen onjuiste winactie-deelnameclaims.
15. E-mailarchitectuur: één gecontroleerde verzender als afzonderlijke Gmail-bezorging gewenst is; inventariseer en schakel eventuele andere mailers pas uit na inspectie.

## Inspiratie
- Reddit r/selfhosted: dashboards met aangepaste widgets en heldere categorieën: https://www.reddit.com/r/selfhosted/comments/1qj359n/my_homepage_dashboard/
- Reddit r/selfhosted: compacte categorie-indeling en notificatiewidgets: https://www.reddit.com/r/selfhosted/comments/1qw1w75/homepage_dashboard_with_couple_of_customapi/
- Reddit r/startpages: nextDash, inbox, slimme collecties en zoekfuncties: https://www.reddit.com/r/startpages/comments/1wz1lbu/nextdash_a_selfhosted_keyboarddriven_start_page/

## Privacy en uitvoerbaarheid
GitHub Pages is statisch. Een privéregister met synchronisatie tussen apparaten vereist afzonderlijke toegangscontrole en backend. Publiceer geen e-mailadres, puntensaldo, deelnamehistorie of privéregister in openbare repository. Deze roadmap verandert nog geen live UI of mailworkflow.
