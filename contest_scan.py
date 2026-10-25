#!/usr/bin/env python3
"""Public multilingual discovery. Never submits entries or promotes candidates to verified."""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.parse
from scan import fetch, rss_items
ROOT=pathlib.Path(__file__).resolve().parent

def classify(title):
 t=title.casefold()
 for name,words in [('Auto’s',['auto','car ','voiture','ev ','tesla']),('Renovatie & verduurzaming',['renovat','verbouw','warmtepomp','isolat','energie','solar','wärmepumpe']),('Tuin',['tuin','garden','garten','gereedschap']),('Apparatuur & gadgets',['keuken','kitchen','appliance','apparat','gadgets','dyson']),('Geld',['geld','cash','money','€']),('Reizen',['reis','travel','vakantie','voyage'])]:
  if any(w in t for w in words):return name
 return 'Overige prijzen'
def lookup(q):
 url='https://www.bing.com/search?'+urllib.parse.urlencode({'q':q['query'],'format':'rss'})
 try:
  rows=rss_items(fetch(url),'Meertalige openbare zoekscan','search')
  return rows,{'query':q['query'],'language':q['language'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ok' if rows else 'empty','items':len(rows)}
 except Exception as e:return [],{'query':q['query'],'status':'error','error':str(e)[:150],'items':0}
def build(rows,now):
 out={}
 for row in rows:
  title=row.get('title','');url=row.get('url','')
  if not url.startswith('https://') or not any(x in title.casefold() for x in ['win','giveaway','gewinn','concours','sweepstake','competition','prijsvraag']):continue
  key=hashlib.sha256(url.split('#')[0].encode()).hexdigest()[:20]
  out[key]={'id':key,'title':title,'sourceUrl':url,'category':classify(title),'checkedAt':now,'status':'candidate','reason':'Alleen zoekresultaat gevonden. Gratis deelname, deadline, officiële regels, Nederlandse toelating en eventuele kosten nog controleren.'}
 return list(out.values())
def main():
 queries=json.loads((ROOT/'contest-searches.json').read_text())['queries'];rows=[];sources=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for found,status in pool.map(lookup,queries):rows.extend(found);sources.append(status)
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();target=ROOT/'contest-candidates.json'
 old=json.loads(target.read_text()) if target.exists() else {'candidates':[]}
 # Source failures never wipe previously collected candidates.
 candidates={r['id']:r for r in old.get('candidates',[])}
 for row in build(rows,now):candidates[row['id']]=row
 target.write_text(json.dumps({'updatedAt':now,'candidates':list(candidates.values()),'sources':sources,'complete':not any(s['status']=='error' for s in sources),'note':'Discovery only. No automatic participation. No universal coverage claim.'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'queries':len(queries),'candidates':len(candidates),'failed':sum(s['status']=='error' for s in sources)}))
if __name__=='__main__':main()
