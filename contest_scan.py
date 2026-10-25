#!/usr/bin/env python3
"""Public multilingual discovery. Never submits entries or promotes candidates to verified."""
import concurrent.futures, datetime, hashlib, json, pathlib, re, urllib.parse
from scan import fetch, rss_items
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent

class ContestLinks(HTMLParser):
 def __init__(self, source):
  super().__init__();self.source=source;self.href=None;self.parts=[];self.rows=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.parts=[]
 def handle_data(self,data):
  if self.href:self.parts.append(data)
 def handle_endtag(self,tag):
  if tag!='a' or not self.href:return
  title=' '.join(' '.join(self.parts).split());url=urllib.parse.urljoin(self.source['url'],self.href)
  host=urllib.parse.urlparse(url).hostname or ''
  # Tracking links are not official participation URLs.
  tracking=('glp8.net','secureomg.nl','tidd.ly','go2cloud.org','tjorven.nl','fr135.net')
  source_host=urllib.parse.urlparse(self.source['url']).hostname or ''
  path=urllib.parse.urlparse(url).path
  if 'prijsvragen.nl' in source_host and (host!=source_host or not path.startswith('/winactie/')):self.href=None;return
  if host==source_host and 'prijsvragen.nl' not in source_host:self.href=None;return
  if url.rstrip('/')==self.source['url'].rstrip('/'):self.href=None;return
  if len(title)>12 and (path.startswith('/winactie/') or re.search(r'\bwin\b|winactie|prijsvraag|giveaway|gewinnspiel',title,re.I)) and not any(host==h or host.endswith('.'+h) for h in tracking):
   self.rows.append({'title':title,'url':url,'discoveredVia':self.source['url'],'discoverySource':self.source['name']})
  self.href=None

def direct_lookup(source):
 try:
  parser=ContestLinks(source);parser.feed(fetch(source['url']))
  return parser.rows,{'source':source['name'],'url':source['url'],'method':'direct_html','status':'ok' if parser.rows else 'empty','items':len(parser.rows)}
 except Exception as e:return [],{'source':source['name'],'url':source['url'],'method':'direct_html','status':'error','error':str(e)[:150],'items':0}

def classify(title):
 t=title.casefold()
 if re.search(r'jaar lang|maanden.*gratis|gratis.*jaar|levenslang|year.*free',t):return 'Lang gratis'
 for name,words in [('Auto’s',['auto','car ','voiture','ev ','tesla']),('Renovatie & verduurzaming',['renovat','verbouw','warmtepomp','isolat','energie','solar','wärmepumpe']),('Tuin',['tuin','garden','garten','gereedschap']),('Apparatuur & gadgets',['keuken','kitchen','appliance','apparat','gadgets','dyson']),('Geld',['geld','cash','money','€']),('Reizen',['reis','travel','vakantie','voyage'])]:
  if any(w in t for w in words):return name
 return 'Overige prijzen'
def lookup(q):
 url='https://www.bing.com/search?'+urllib.parse.urlencode({'q':q['query'],'format':'rss'})
 try:
  rows=rss_items(fetch(url),'Meertalige openbare zoekscan','search')
  return rows,{'query':q['query'],'language':q['language'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ok' if rows else 'empty','items':len(rows)}
 except Exception as e:return [],{'query':q['query'],'status':'error','error':str(e)[:150],'items':0}
def relevant(title, url):
 t=title.casefold()
 host=urllib.parse.urlparse(url).hostname or ''
 if any(host==x or host.endswith('.'+x) for x in ('wikipedia.org','wiktionary.org','merriam-webster.com','dictionary.com','collinsdictionary.com','thefreedictionary.com')):return False
 if any(x in t for x in ('winrar','windows','download','win map','wind map','concours owners','car shows')):return False
 # A word boundary prevents Windows/Windy/WinRAR from matching “win”.
 return bool(re.search(r'\b(?:winactie|winacties|prijsvraag|prijsvragen|giveaway|gewinnspiel|sweepstakes?|competition)\b|\bwin\s+(?:een|a|an|je|de|het|your|the)\b|\bconcours\b.*\b(?:gagnez|gagner|gratuit|voyage|voiture|cadeau)\b',t))

def build(rows,now):
 out={}
 for row in rows:
  title=row.get('title','');url=row.get('url','')
  if not url.startswith('https://') or not (relevant(title,url) or row.get('discoveredVia')):continue
  key=hashlib.sha256(url.split('#')[0].encode()).hexdigest()[:20]
  out[key]={'id':key,'title':title,'sourceUrl':url,'category':classify(title),'checkedAt':now,'status':'candidate','reason':'Alleen zoekresultaat gevonden. Gratis deelname, deadline, officiële regels, Nederlandse toelating en eventuele kosten nog controleren.'}
  out[key].update({k:row[k] for k in ('discoveredVia','discoverySource') if k in row})
  if row.get('discoveredVia'):out[key]['reason']='Gevonden op een direct uitgelezen prijsvragenoverzicht. Einddatum, kosten en Nederlandse toelating nog niet bevestigd.'
 return list(out.values())
def main():
 queries=json.loads((ROOT/'contest-searches.json').read_text())['queries'];rows=[];sources=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for found,status in pool.map(lookup,queries):rows.extend(found);sources.append(status)
 direct=json.loads((ROOT/'contest-sources.json').read_text())['sources']
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for found,status in pool.map(direct_lookup,direct):rows.extend(found);sources.append(status)
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();target=ROOT/'contest-candidates.json'
 old=json.loads(target.read_text()) if target.exists() else {'candidates':[]}
 # Source failures never wipe previously collected candidates.
 candidates={r['id']:r for r in old.get('candidates',[]) if not r.get('reason','').startswith('Alleen zoekresultaat') or relevant(r.get('title',''),r.get('sourceUrl',''))}
 for row in build(rows,now):candidates[row['id']]=row
 target.write_text(json.dumps({'updatedAt':now,'candidates':list(candidates.values()),'sources':sources,'complete':not any(s['status']=='error' for s in sources),'note':'Discovery only. No automatic participation. No universal coverage claim.'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'queries':len(queries),'candidates':len(candidates),'failed':sum(s['status']=='error' for s in sources)}))
if __name__=='__main__':main()
