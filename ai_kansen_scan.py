#!/usr/bin/env python3
"""Curated AI discovery from official source RSS and public Reddit RSS.
Results are DISCOVERIES only, never unsupported product claims.
"""
import datetime, html, json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
TARGET=ROOT/"ai-kansen.json"
USER_AGENT={"User-Agent":"DASPHHS-AIKansen/1.0 (public feed discovery; personal use)"}
FEEDS=[
("Reddit r/ChatGPT","https://www.reddit.com/r/ChatGPT/top/.rss?t=week","reddit"),
("Reddit r/automation","https://www.reddit.com/r/automation/top/.rss?t=week","reddit"),
("Reddit r/ADHD","https://www.reddit.com/r/ADHD/top/.rss?t=week","reddit"),
("Reddit r/teachers","https://www.reddit.com/r/Teachers/top/.rss?t=week","reddit"),
("OpenAI blog","https://openai.com/news/rss.xml","official"),
("n8n blog","https://blog.n8n.io/rss/","official"),
]
FOCUS={
"werk":("education","teaching","teacher","lesson","classroom","rubric","feedback","curriculum","docent","onderwijs","learning design","instructional"),
"praktisch":("automation","workflow","agent","shortcut","calendar","email","gmail","trello","n8n","productivity","reminder","free tool","open source","self-host"),
}
AI_WORDS=("ai","chatgpt","llm","claude","gemini","openai","agent","automation","automate","copilot","n8n","model")
STOP_WORDS=("meme","politics","nsfw","rant","hype","rumor","rumour","leak")
def clean(s):return re.sub(r"\\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",s or ""))).strip()
def relevant(title):
 t=title.casefold()
 if any(w in t for w in STOP_WORDS):return False
 if not any(re.search(r"(?<![a-z])"+re.escape(w)+r"(?![a-z])",t) for w in AI_WORDS):return False
 return any(w in t for words in FOCUS.values() for w in words)
def group(title,kind):
 if kind=="reddit":return "reddit"
 t=title.casefold()
 return "werk" if any(w in t for w in FOCUS["werk"]) else "praktisch"
def parse(raw,source,kind,now):
 root=ET.fromstring(raw);out=[]
 nodes=list(root.findall(".//item"))+list(root.findall(".//{http://www.w3.org/2005/Atom}entry"))
 for item in nodes:
  def value(tag):
   x=item.find(tag)
   return clean("".join(x.itertext())) if x is not None else ""
  title=value("title") or value("{http://www.w3.org/2005/Atom}title")
  url=value("link")
  if not url:
   x=item.find("{http://www.w3.org/2005/Atom}link")
   url=x.attrib.get("href","") if x is not None else ""
  if not title or not url.startswith("https://") or not relevant(title):continue
  group_name=group(title,kind)
  out.append({"title":title[:145],"why":"Relevant signaal voor jouw AI-, onderwijs- of automatiseringsinteresses; de bron bewijst nog niet dat de methode werkt.","action":"Lees het oorspronkelijke bericht en controleer of er een praktische demonstratie of officiële documentatie is.","url":url,"source":source,"date":now,"status":"Reddit-tip, niet onafhankelijk bevestigd" if kind=="reddit" else "Bronpublicatie, werking nog te controleren","group":group_name})
 return out
def main():
 old=json.loads(TARGET.read_text())
 today=datetime.datetime.now(datetime.timezone.utc)
 stamp=today.strftime("%Y-%m-%d")
 candidates=[];sources=[]
 for name,url,kind in FEEDS:
  try:
   req=urllib.request.Request(url,headers=USER_AGENT)
   with urllib.request.urlopen(req,timeout=12) as r: raw=r.read(900000).decode("utf-8","replace")
   items=parse(raw,name,kind,stamp)
   candidates+=items;sources.append({"name":name,"status":"ok","matches":len(items)})
  except Exception as exc:sources.append({"name":name,"status":"unavailable","detail":str(exc)[:100]})
 existing=old.get("items",[])
 seen={x["url"].split("?")[0]:x for x in existing}
 for x in candidates:
  key=x["url"].split("?")[0]
  if key not in seen:seen[key]=x
 # Keep editorially curated examples, and at most a few relevant new items from each type.
 stable=[x for x in existing if x.get("status")=="Officiële documentatie" or x.get("status")=="Officiële productinformatie"]
 fresh=[x for x in seen.values() if x not in stable and x.get("date","")>= (today-datetime.timedelta(days=14)).strftime("%Y-%m-%d")]
 fresh.sort(key=lambda x:x["date"],reverse=True)
 result=stable[:4]+fresh[:8]
 if not result:raise SystemExit("No verified/editorial content to publish")
 out={"updatedAt":today.isoformat(),"items":result,"sources":sources,"note":"Reddit discovery, not vetted advice; official launch claims require manual verification."}
 TARGET.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"entries":len(result),"sources":sources},ensure_ascii=False))
if __name__=="__main__":main()
