#!/usr/bin/env python3
"""Apply only repository-owner GitHub issues to public watchlist.json.

Event body format:
SPECIALDEALS-WATCH-V1
actie=toevoegen
product=HOKA Arahi 8 EU47 1/3
maxprijs=100
"""
import datetime,json,os,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parent
OWNER="DASPHHS"
TARGET=ROOT/"watchlist.json"
def normal(s):return " ".join(str(s).casefold().split())
def parse(body):
 lines=[line.strip() for line in (body or "").splitlines() if line.strip()]
 if not lines or lines[0]!="SPECIALDEALS-WATCH-V1":raise ValueError("Verzoek is niet van het juiste type.")
 opts={}
 for line in lines[1:]:
  if "=" not in line:continue
  k,v=line.split("=",1)
  if k not in ("actie","product","maxprijs"):continue
  opts[k]=v.strip()
 action=opts.get("actie")
 if action not in ("toevoegen","verwijderen"):raise ValueError("Onbekende actie.")
 name=opts.get("product","")
 if not (3<=len(name)<=120) or any(ord(c)<32 for c in name) or "<" in name or ">" in name:raise ValueError("Ongeldige productnaam.")
 raw=opts.get("maxprijs","").replace(",",".")
 if action=="toevoegen":
  if not re.fullmatch(r"\d{1,5}(?:\.\d{1,2})?",raw):raise ValueError("Maxprijs ontbreekt of is ongeldig.")
  maximum=round(float(raw),2)
  if not (.5<=maximum<=10000):raise ValueError("Maximum ligt buiten bereik.")
 else: maximum=None
 return action,name,maximum
def apply(data,event):
 issue=event.get("issue") or {}
 if (issue.get("user") or {}).get("login","").casefold()!=OWNER.casefold():raise PermissionError("Alleen repository-eigenaar mag watchlist wijzigen.")
 action,name,maximum=parse(issue.get("body",""))
 items=list(data.get("items") or [])
 key=normal(name)
 if action=="verwijderen":
  items=[item for item in items if normal(item["product"])!=key]
 else:
  items=[item for item in items if normal(item["product"])!=key]
  if len(items)>=100:raise ValueError("Maximaal 100 alertproducten.")
  items.append({"product":name,"maxPriceEUR":maximum,"createdAt":datetime.datetime.now(datetime.timezone.utc).isoformat()})
 items.sort(key=lambda item:normal(item["product"]))
 return {**data,"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"items":items}
def main():
 with open(os.environ["GITHUB_EVENT_PATH"],encoding="utf-8") as f:event=json.load(f)
 data=json.loads(TARGET.read_text(encoding="utf-8"))
 result=apply(data,event)
 TARGET.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Watchlist updated, items:",len(result["items"]))
if __name__=="__main__":main()
