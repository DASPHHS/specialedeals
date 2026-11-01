"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
function read(p){return fs.readFileSync(path.join(root,p),"utf8");}
function inlineScripts(html){
  return [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(x=>x[1]).filter(x=>x.trim());
}
const main=read("index.html"),week=read("weekdeals/index.html"),wishlist=read("verlanglijst/index.html"),css=read("ui/speciale.css");
for(const [name,html] of [["homepage",main],["weekdeals",week]]){
  const scripts=inlineScripts(html);
  assert(scripts.length>0,name+" has no inline JavaScript");
  for(let i=0;i<scripts.length;i++)new vm.Script(scripts[i],{filename:name+"-"+i+".js"});
  assert(html.includes("ui/speciale.css"),name+" missing shared stylesheet");
}
assert(main.includes("function currentSampleLead("),"Sample event publication gate missing");
assert(!main.includes('x.organizerVerified===true'),"Sample events must not be silently hidden without auto verification");
assert(read("verlanglijst/index.html").includes('value="research"'),"Missing researched-product filter");
assert(read("verlanglijst/app.js").includes("function researchRow("),"Research result rendering missing");
assert(main.includes('id="lens"'),"Missing opportunity selector");
assert(main.includes('value="opportunities"'),"Missing opportunities");
assert(main.includes('value="discount"'),"Missing evidence-aware discount sort");
assert(main.includes('value="saving"'),"Missing euro savings sort");
assert(main.includes('value="deadline"'),"Missing urgency sort");
assert(main.includes('id="resetFilters"'),"Missing reset button");
assert(main.includes('class="mobile-dock"'),"Missing mobile nav");
assert(main.includes('src="./ui/deal-filters.js"'),"Missing evidence helper");
assert(week.includes('id="offerType"'),"Missing Weekdeals filter");
assert(week.includes('id="rank"'),"Missing Weekdeals ranking");
assert(week.includes('value="loyalty"'),"Missing loyalty filter");
assert(week.includes('id="weekFound"'),"Missing Weekdeals stats");
assert(css.includes("prefers-reduced-motion"),"Respect reduced motion");
assert(css.includes(":focus-visible"),"Keyboard focus styles");
assert(css.includes("@media(max-width:700px)"),"Mobile layout");
assert(main.includes('href="./verlanglijst/"'),"Homepage wishlist nav missing");
assert(wishlist.includes('id="wishGrid"'),"Wishlist grid missing");
assert(wishlist.includes('id="wishForm"'),"Wishlist editor missing");
assert(wishlist.includes('id="wishStatus"'),"Wishlist filtering missing");
assert(wishlist.includes('id="downloadList"')&&wishlist.includes('id="importList"'),"Wishlist backup tools missing");
assert(wishlist.includes('src="./app.js"'),"Wishlist JS not linked");
assert(wishlist.includes('href="./style.css"'),"Wishlist style not linked");
assert(read("verlanglijst/style.css").includes("prefers-reduced-motion"),"Wishlist motion settings missing");
new vm.Script(read("verlanglijst/app.js"),{filename:"verlanglijst/app.js"});
const top=read("topdeals/index.html");
assert(main.includes('href="./topdeals/"'),"Homepage Top10 link missing");
assert(week.includes('href="../topdeals/"'),"Weekdeals Top10 link missing");
assert(wishlist.includes('href="../topdeals/?categorie=persoonlijk"'),"Wishlist Top10 link missing");
assert(top.includes('id="categoryNav"')&&top.includes('id="categorySections"'),"Top10 category page missing controls");
assert(top.includes('id="marketSection"')&&top.includes('id="marketGrid"'),"Public source market comparison section missing");
assert(read("topdeals/app.js").includes('prijspeil.json'),"Missing sourced independent market price feed");
assert(top.includes('src="./app.js"')&&top.includes('href="./style.css"'),"Top10 source assets not linked");
assert(read("topdeals/style.css").includes("prefers-reduced-motion"),"Top10 motion setting missing");
new vm.Script(read("topdeals/app.js"),{filename:"topdeals/app.js"});
console.log("Site HTML, scripts, wishlist and Top10 navigation smoke tests passed");
