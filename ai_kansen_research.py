#!/usr/bin/env python3
"""Find Reddit/official *research candidates* without publishing vague claims as tips.

AI Kansen only displays editorially checked ai-kansen.json; discoveries go to
ai-kansen-kandidaten.json for manual review. No auto-promotion.
"""
import datetime, json, pathlib, urllib.request
import ai_kansen_scan as old
ROOT=pathlib.Path(__file__).resolve().parent
FEEDS=old.FEEDS
def main():
 today=datetime.datetime.now(datetime.timezone.utc)
 results=[];sources=[]
 for name,url,kind in FEEDS:
  try:
   req=urllib.request.Request(url,headers=old.USER_AGENT)
   with urllib.request.urlopen(req,timeout=12) as r: raw=r.read(900000).decode("utf-8","replace")
   rows=old.parse(raw,name,kind,today.strftime("%Y-%m-%d"))
   # Require a technology AND concrete action claim in the headline; candidates only
   action_words=("how to","guide","tutorial","built","created","step by step","released","launch","automated","workflow","script","extension","shortcut","api")
   rows=[row for row in rows if any(w in row["title"].lower() for w in action_words)]
   results.extend(rows);sources.append({"name":name,"status":"ok","candidates":len(rows)})
  except Exception as e:sources.append({"name":name,"status":"unavailable","detail":str(e)[:100]})
 unique={x["url"].split("?")[0]:x for x in results}
 out={"updatedAt":today.isoformat(),"reviewRequired":True,"items":list(unique.values())[:25],"sources":sources,
 "warning":"These are unverified research leads; not published on AI Kansen."}
 (ROOT/"ai-kansen-kandidaten.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"research_candidates":len(out["items"]),"sources":sources},ensure_ascii=False))
if __name__=="__main__":main()
