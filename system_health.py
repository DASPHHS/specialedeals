"""Publish evidence-based module health; fresh files alone never imply source success."""
import datetime as dt
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent


def assess(label, data, timestamp, checks, good, max_hours, now):
    stamp = data.get(timestamp)
    try:
        age = (now - dt.datetime.fromisoformat(stamp.replace('Z', '+00:00'))).total_seconds()/3600
    except (ValueError, TypeError, AttributeError):
        age = None
    rows = data.get(checks, [])
    ok = sum(row.get('status') in good for row in rows)
    errors = len(rows) - ok
    state = 'onbekend' if not rows else 'werkt' if ok and not errors else 'gedeeltelijk' if ok else 'mislukt'
    if age is None or age > max_hours or age < -1:
        state = 'verouderd'
    return dict(name=label, state=state, checkedAt=stamp, maxAgeHours=max_hours,
                successful=ok, unsuccessful=errors, total=len(rows))


def build(root=ROOT, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    modules = []
    for label, file, stamp, checks, good, hours in [
        ('Deals ontdekken', 'live-deals.json', 'updatedAt', 'sources', {'ok', 'empty'}, 8),
        ('Productprijzen controleren', 'merchant-observations.json', 'checkedAt', 'checks', {'observed'}, 8),
        ('Winacties ontdekken', 'contest-candidates.json', 'updatedAt', 'sources', {'ok', 'empty'}, 8),
        ('AI en innovaties onderzoeken', 'ai-kansen-kandidaten.json', 'updatedAt', 'sources', {'ok', 'empty'}, 30),
    ]:
        try:
            data = json.loads((root/file).read_text())
            quality = assess(label, data, stamp, checks, good, hours, now)
            if label == 'Deals ontdekken':
                found = int(data.get('coverage', {}).get('personalMatches', 0))
                # Feed hits are not usable, independently confirmed personal bargains.
                # The separately checked merchant data is needed before "werkt".
                try:
                    merchants = json.loads((root/'merchant-observations.json').read_text(encoding='utf-8'))
                    verified = sum(
                        o.get('allInVerified') is True
                        and o.get('marketComparisonVerified') is True
                        and o.get('variantVerified') is True
                        and o.get('stockStatus') == 'volgens winkel op voorraad'
                        for o in merchants.get('offers', [])
                    )
                except (OSError, ValueError, TypeError):
                    verified = 0
                queries = [q for q in data.get('sources', [])
                           if str(q.get('source', '')).startswith(
                             ('Merkscan', 'Samplezoekopdracht', 'Winkelzoekopdracht',
                              'Internationale zoekopdracht'))]
                contributing = sum(int(q.get('items',0)) > 0 for q in queries)
                quality['personalMatches'] = found
                quality['verifiedProductDeals'] = verified
                quality['contributingQueries'] = contributing
                quality['totalTargetedQueries'] = len(queries)
                quality['detail'] = (
                    str(found) + ' onbevestigde persoonlijke feedvondsten; '
                    + str(verified) + ' onafhankelijk gecontroleerde koopdeals. '
                    + str(contributing) + '/' + str(len(queries)) +
                    ' gerichte zoekopdrachten met relevante resultaten. '
                    'Een geslaagde bronopvraag is geen bewezen koopkans.'
                )
                if verified == 0 and quality['state'] == 'werkt':
                    quality['state'] = 'gedeeltelijk'
            modules.append(quality)
        except (OSError, ValueError):
            modules.append(dict(name=label, state='mislukt', checkedAt=None, total=0, successful=0, unsuccessful=0, maxAgeHours=hours))
    try:
        tactics=json.loads((root/'strategie-scan.json').read_text(encoding='utf-8'))
        verified_sources=sum(x.get('status')=='terms_found' for x in tactics.get('officialSources',[]))
        total_sources=len(tactics.get('officialSources',[]))
        reddit_leads=len(tactics.get('redditCandidates',[]))
        strategy_status='gedeeltelijk' if verified_sources>0 else 'mislukt'
        strategy_detail=(f"{verified_sources}/{total_sources} officiële bronpagina's met verwachte voorwaarden; "
                         f"{reddit_leads} onbevestigde Reddit-onderzoekskandidaten. "
                         "Strategieën zijn bruikbaar als controlelijst, maar niet automatisch uitgevoerd.")
    except (OSError,ValueError,TypeError):
        strategy_status='niet geverifieerd'
        strategy_detail='Bespaarstrategiescan ontbreekt of is ongeldig.'
    return dict(updatedAt=now.isoformat(), modules=modules,
                capabilities=[
                    dict(name='Bespaarstrategieën Meervoordeel, drogist en Reddit', state=strategy_status, detail=strategy_detail),
                    dict(name='Dagelijkse e-mail', state='niet geverifieerd', detail='De GitHub-scanner verstuurt geen e-mail. Een afzonderlijke taak vereist controle van uitvoering en bezorging.'),
                    dict(name='Hypotheekrente onder 3,6%', state='niet geverifieerd', detail='Geen bankrentefeed in deze scanner. Een private alerttaak is geen gecontroleerde rentevergelijking op deze site.'),
                    dict(name='Contractbesparingen', state='gedeeltelijk', detail='Lokale berekening beschikbaar. Geen automatische contract- of offertesynchronisatie.'),
                    dict(name='Winacties beoordelen', state='gedeeltelijk', detail='Relevantie en deadlines worden gerangschikt; alleen officiële regels en bevestigde NL-toelating zijn deelnameklaar. Geen verzonnen winkansen.'),
                    dict(name='Internationale deals naar NL', state='gedeeltelijk', detail='Geselecteerde Europese shops en gepubliceerde NL-verzendvoorwaarden geregistreerd; exacte maat, afrekenprijs en onafhankelijke marktvergelijking zijn niet overal bevestigd.'),
                ])


if __name__ == '__main__':
    (ROOT/'system-health.json').write_text(json.dumps(build(), ensure_ascii=False, indent=2)+'\n')
