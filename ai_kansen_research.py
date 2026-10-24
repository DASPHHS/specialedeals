#!/usr/bin/env python3
"""Research-only opportunity scan: broad Reddit and official sources.
No unverified Reddit/social results are added to the public curated ideas page.
"""
import datetime, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET, html
ROOT=pathlib.Path(__file__).resolve().parent
HEAD={"User-Agent":"DASPHHS-SlimmeKansenResearch/1.1 (research only)"}
FEEDS=[
("Reddit r/shortcuts","https://www.reddit.com/r/shortcuts/top/.rss?t=week"),
("Reddit r/homeautomation","https://www.reddit.com/r/homeautomation/top/.rss?t=week"),
("Reddit r/automation","https://www.reddit.com/r/automation/top/.rss?t=week"),
("Reddit r/productivity","https://www.reddit.com/r/productivity/top/.rss?t=week"),
("Reddit r/Frugal","https://www.reddit.com/r/Frugal/top/.rss?t=week"),
("Reddit r/BuyItForLife","https://www.reddit.com/r/BuyItForLife/top/.rss?t=week"),
("Reddit r/Teachers","https://www.reddit.com/r/Teachers/top/.rss?t=week"),
("Reddit r/selfhosted","https://www.reddit.com/r/selfhosted/top/.rss?t=week"),
("Reddit r/ChatGPT","https://www.reddit.com/r/ChatGPT/top/.rss?t=week"),
("Reddit r/personalfinance","https://www.reddit.com/r/personalfinance/top/.rss?t=week"),
("Reddit r/ADHD","https://www.reddit.com/r/ADHD/top/.rss?t=week"),
("OpenAI News","https://openai.com/news/rss.xml"),
("n8n blog","https://blog.n8n.io/rss/"),
]
TOPICS={
"Automatisering":("automate","automation","shortcut","nfc","workflow","home assistant","api","script","homekit","smartthings","agent","trigger"),
"Geld besparen":("saved","saving","cheaper","cashback","subscription","insurance","deal","budget","refund","price tracker"),
"Werk en planning":("calendar","email","teaching","student","school","lesson","reminder","tasks","trello","productivity","plan"),
"Nieuw en technologie":("released","launch","feature","update","new tool","apple intelligence","chatgpt","openai","model","ai"),
"Praktisch leven":("organize","organise","household","cleaning","meal prep","maintenance","habit","home","travel","fitness"),
}
ACTION=("i built","i made","how i","guide","tutorial","saved me","built a","new feature","released","automated","workflow","tool","setup","tips","works","hack","launched","i use","automation","shortcut","made this","open source")
EXCLUDE=("meme","political","drama","venting","giveaway","shitpost","my diagnosis","medical advice")
def clean(s):return re.sub(r"\\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",s or ""))).strip()
def parse(raw,name):
 root=ET.fromstring(raw);out=[]
 for e in list(root.findall(".//item"))+list(root.findall(".//{http://www.w3.org/2005/Atom}entry")):
  def val(tag):
   x=e.find(tag);return clean("".join(x.itertext())) if x is not None else ""
  title=val("title") or val("{http://www.w3.org/2005/Atom}title")
  url=val("link")
  if not url:
   z=e.find("{http://www.w3.org/2005/Atom}link")
   url=z.attrib.get("href","") if z is not None else ""
  if not url.startswith("https://") or not title:continue
  t=title.lower()
  if any(x in t for x in EXCLUDE):continue
  matches=[theme for theme,terms in TOPICS.items() if any(w in t for w in terms)]
  if not matches or not any(w in t for w in ACTION):continue
  out.append({"title":title[:160],"url":url,"source":name,"themes":matches,"status":"Ongecontroleerd onderzoekssignaal: geen publicatie of aanbeveling"})
 return out
def main():
 sources=[];candidates=[]
 for name,url in FEEDS:
  try:
   req=urllib.request.Request(url,headers=HEAD)
   with urllib.request.urlopen(req,timeout=12) as r:body=r.read(900000).decode("utf-8","replace")
   found=parse(body,name);candidates.extend(found)
   sources.append({"source":name,"status":"ok" if found else "empty","matches":len(found)})
  except Exception as exc:sources.append({"source":name,"status":"unavailable","error":str(exc)[:120]})
 seen=set();unique=[]
 for c in candidates:
  key=c["url"].split("?")[0].rstrip("/")
  if key not in seen:seen.add(key);unique.append(c)
 report={"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "items":unique[:150],"totalMatched":len(unique),"sources":sources,
 "note":"Research only; needs exact instructions, a real source, availability, costs and personal usefulness check prior to publication."}
 (ROOT/"ai-kansen-kandidaten.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"research_candidates":len(report["items"]),"sources":sources},ensure_ascii=False))
if __name__=="__main__":main()
