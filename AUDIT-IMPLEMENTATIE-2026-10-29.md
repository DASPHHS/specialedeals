# Kansenkompas: technische audit en implementatieplan (29 oktober 2026)

## Geconstateerde blokkade
De scanner haalt vooral categorie-/overzichtspagina's op en publiceert onderzoeksleads. De strenge prijsengine leest `price-observations.json`, maar dit bestand heeft momenteel `items: []`. Er zijn dus geen live, per variant gecontroleerde prijzen om te publiceren. De GitHub Actions-job draait wel, maar de detectie is geen verificatie. De statische GitHub Pages-site kan niet zelf betrouwbaar webwinkels crawlen en kan browser-lokale verlanglijstwijzigingen niet automatisch naar GitHub synchroniseren.

## Gewenste architectuur
1. **Discovery**: evenveel onderzoeksbudget voor Pepper/mydealz/community, directe retailers en onafhankelijke vergelijkers. Nieuws-/categoriepagina's leveren uitsluitend leads. Een blokkade (403/429) wordt als bronfout opgeslagen, niet omzeild.
2. **Canonical product matching**: per EAN/GTIN, exacte SKU, generatie, maat, kleur, flesinhoud en conditie. Verwijder samples/accessoires als mismatch. Herenoutdoor uitsluitend Arc'teryx; HOKA sportschoenen apart. Bij sample sales uitsluitend bewezen relevant mannenaanbod; onbekend wordt niet als herenaanbod gepubliceerd.
3. **Per-retailer adapters**: relevante concrete product-URL's ophalen; bij voorkeur schema.org Product/Offer JSON-LD en toegestane winkel-API/productfeeds. Handmatige uitzonderingscontrole bij complexe of geblokkeerde sites.
4. **Delivery verification**: valideer btw, actuele NL-bezorgkosten, invoer, voorraad en verkoper. Sla observatie met timestamp, bron-URL en methodiek op. Een onzekere shipping cost blijft onvolledig, nooit €0 aannemen.
5. **Price engine**: gebruik `price_engine.py` op echte `price-observations.json` met circa 4 aanbieders als onderzoeksdoel. Toon alleen laagste prijs **onder daadwerkelijk gecontroleerde verkopers**. Kortingsstatus is een aparte toets via `deal_verification.py`; MSRP of Pepper-claim is onvoldoende.
6. **Opslag/historie**: bewaar bronmetingen historisch, met retentie en foutcodes. Vergelijk gedocumenteerde recente daadwerkelijk verkoopbare prijzen en controleer of referentie exact dezelfde variant is. Geen oneindige Git-commits per scan: overweeg kleine database zodra volume groeit.
7. **Dashboard**: scheid harde deals, reguliere geverifieerde prijzen, grote winacties en herensample sales; verberg oude prijsnotities standaard. Toon prijsdatum, aantal onderzochte winkels, levertarief en concrete verificatie-uitval. Geen 'live' zonder recente waarneming.
8. **Privégegevens**: persoonlijke status en browserfeedback niet naar openbare repo publiceren. GitHub Pages is statisch; automatische multi-device sync vergt afgeschermde backend/authenticatie.
9. **Planning**: test dagelijks 08:00 via aparte ChatGPT-taak; GitHub Actions scan is geen ChatGPT-bezorging of e-mail.
10. **Acceptatiecriteria**: regressietests voor verkeerde variant, onzekere NL-verzending, >36 uur oud, onafhankelijke referentie, 10%-drempel, damesgerichte sample sales, ontbrekende inventaris, Pepper-categoriepagina's, duplicaten en privacy.

## Vergeleken implementaties
- Pepper: community sourcing, actuele prijsvergelijking, prijshistorie, betrouwbare verkoper en verzend-/retourvoorwaarden; zie https://help.business.pepper.com/help/what-do-our-editorial-team-check-for .
- changedetection.io: webpagina-/prijsveranderingen, selectorgebaseerde tracking, drempelregels en historie; zie https://github.com/dgtlmoon/changedetection.io . Reddit wijst op captcha's, wrong-element selection en waarschuwingsoverlast: https://www.reddit.com/r/selfhosted/comments/1e733vj/ .
- sonoyumi/price-tracker: JSON-LD/CSS selectors en SQLite-historie; https://github.com/sonoyumi/price-tracker .
- devoidx/price-tracker: multi-store prijsontwikkeling, actuele lage prijs per bron, foutweergave en notificatiedrempels; https://github.com/devoidx/price-tracker .

## Eerste configuratieveranderingen in deze branch
- Michael Kors Pour Homme **Eau de Parfum** toegevoegd aan zowel centrale wishlist als prijsradar.
- YSL originele M7 nu gericht op actuele prijsvergelijking, Oud Absolu apart.
- 1:1:1 onderzoeksspreiding (community/retailers/vergelijkers) en 1:1 eindrapportbalans (echte deals versus actuele prijsvergelijkingen).
- Uitsluiting damesgerichte sample sales en voorkeur voor bewezen herenaanbod expliciet in configuratie.

**Nog niet gereed:** echte retaileradapters, automatische bronmetingen en dashboardpublicatie van nieuwe live prijzen. Geen onterechte claim dat de volledige radar al werkt.
