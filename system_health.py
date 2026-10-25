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
            modules.append(assess(label, data, stamp, checks, good, hours, now))
        except (OSError, ValueError):
            modules.append(dict(name=label, state='mislukt', checkedAt=None, total=0, successful=0, unsuccessful=0, maxAgeHours=hours))
    return dict(updatedAt=now.isoformat(), modules=modules,
                capabilities=[
                    dict(name='Dagelijkse e-mail', state='niet geverifieerd', detail='De GitHub-scanner verstuurt geen e-mail. Een afzonderlijke taak vereist controle van uitvoering en bezorging.'),
                    dict(name='Hypotheekrente onder 3,6%', state='niet geverifieerd', detail='Geen bankrentefeed in deze scanner. Een private alerttaak is geen gecontroleerde rentevergelijking op deze site.'),
                    dict(name='Contractbesparingen', state='gedeeltelijk', detail='Lokale berekening beschikbaar. Geen automatische contract- of offertesynchronisatie.'),
                    dict(name='Winacties beoordelen', state='gedeeltelijk', detail='Automatische ontdekking; Nederlandse toelating, regels en deadlines vereisen inhoudelijke controle.'),
                ])


if __name__ == '__main__':
    (ROOT/'system-health.json').write_text(json.dumps(build(), ensure_ascii=False, indent=2)+'\n')
