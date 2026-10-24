#!/usr/bin/env python3
"""Fail publication when dashboard syntax or critical data contracts break."""
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent
PAGES={"index.html":('firstcards','observations','merchantUpdated','wishAdd','watchStatus','sourceRows'),
       "ai-kansen.html":('buildcards','buildcategory','othercards','researchPanel','researchCards')}
for file,ids in PAGES.items():
 html=(ROOT/file).read_text(encoding="utf-8")
 for identifier in ids:
  if ('id="'+identifier+'"') not in html:raise RuntimeError(file+": missing element "+identifier)
 blocks=re.findall(r"<script\b[^>]*>(.*?)</script>",html,flags=re.I|re.S)
 if not blocks:raise RuntimeError(file+": no JavaScript")
 for j,block in enumerate(blocks):
  # Node.js is installed on ubuntu-latest; do not execute browser code here.
  scratch=ROOT/("_sitecheck_"+str(j)+".js")
  scratch.write_text(block,encoding="utf-8")
  try:
   run=subprocess.run(["node","--check",str(scratch)],text=True,capture_output=True)
   if run.returncode:raise RuntimeError(file+": invalid JS "+run.stderr)
  finally:scratch.unlink(missing_ok=True)
for path,key in (("watchlist.json","items"),("shop-targets.json","targets"),("radar-config.json","brands"),
 ("bouwideeen.json","items"),("ai-kansen.json","items")):
 data=json.loads((ROOT/path).read_text(encoding="utf-8"))
 if not isinstance(data.get(key),list):raise RuntimeError(path+": "+key+" must be array")
data=json.loads((ROOT/"merchant-observations.json").read_text(encoding="utf-8"))
for entry in data.get("offers",[]):
 for k in ("title","store","price","url","checkedAt"):
  if k not in entry:raise RuntimeError("merchant observation missing "+k)
 if entry.get("marketComparisonVerified") is True and not entry.get("referencePrice"):
  raise RuntimeError("Proven market comparison has no reference price")
print("Website and JSON quality checks passed.")
