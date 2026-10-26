#!/usr/bin/env python3
"""Technical rechecks of official public pages. Never verify eligibility or submit.
No private data, cookies, confirmations or participation history are accepted.
"""
import concurrent.futures
import datetime as dt
import hashlib
import json
from zoneinfo import ZoneInfo
from scan import fetch, strip, ROOT


def review(contest, previous, now, loader=fetch):
    result = {'id': contest['id'], 'checkedAt': now.isoformat(),
              'verificationLevel': 'technical_recheck_only', 'pages': []}
    for url in dict.fromkeys([contest.get('sourceUrl'), contest.get('termsUrl')]):
        if not url or not url.startswith('https://'):
            result['pages'].append({'url': url, 'status': 'missing'})
            continue
        try:
            body = loader(url)
            digest = hashlib.sha256(body.encode()).hexdigest()
            prior = next((p for p in previous.get('pages', []) if p.get('url') == url), {})
            result['pages'].append({'url': url, 'status': 'reachable', 'contentHash': digest,
                'changed': prior.get('contentHash') != digest if prior.get('contentHash') else None})
        except Exception:
            # Never publish exception text (redirect URLs may contain access tokens).
            result['pages'].append({'url': url, 'status': 'unavailable'})
    reasons = []
    end = contest.get('deadlineAt')
    try:
        expired = dt.datetime.fromisoformat(end.replace('Z', '+00:00')) <= now if end else contest['deadline'] < now.astimezone(ZoneInfo('Europe/Amsterdam')).date().isoformat()
        if expired: reasons.append('expired')
    except (KeyError, ValueError, TypeError): reasons.append('deadline_unknown')
    if any(p['status'] != 'reachable' for p in result['pages']): reasons.append('official_page_unavailable')
    if any(p.get('changed') is True for p in result['pages']): reasons.append('page_changed')
    if not isinstance(contest.get('entryLimit'), dict): reasons.append('entry_limit_not_documented')
    if contest.get('eligibleFromNetherlands') is not True: reasons.append('explicit_nl_evidence_missing')
    if not isinstance(contest.get('costs'), dict): reasons.append('cost_evidence_missing')
    # Human interpretation is ALWAYS needed, even when HTTP and hashes match.
    result.update(reviewRequired=True, reasons=reasons, note='Bereikbaarheid en wijzigingsdetectie bewijzen geen actuele voorwaarden, toelating of deelname.')
    return result


def main():
    target = ROOT / 'contest-rechecks.json'
    old = json.loads(target.read_text()) if target.exists() else {}
    previous = {r['id']: r for r in old.get('reviews', [])}
    contests = json.loads((ROOT / 'contests.json').read_text())['contests']
    now = dt.datetime.now(dt.timezone.utc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        reviews = list(pool.map(lambda c: review(c, previous.get(c['id'], {}), now), contests))
    output = {'updatedAt': now.isoformat(), 'verificationLevel': 'technical_recheck_only',
              'reviews': reviews, 'complete': all(all(p['status'] == 'reachable' for p in r['pages']) for r in reviews)}
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actionsChecked': len(reviews), 'unavailablePages': sum(p['status'] != 'reachable' for r in reviews for p in r['pages']), 'submissions': 0}))

if __name__ == '__main__': main()
