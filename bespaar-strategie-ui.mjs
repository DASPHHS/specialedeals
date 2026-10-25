import {compareContract} from "./bespaar-calculator.mjs";

const $ = id => document.getElementById(id);
const eur = n => new Intl.NumberFormat("nl-NL",{style:"currency",currency:"EUR"}).format(n);
const safeLink = link => typeof link === "string" && /^https:\/\/[^/]+/.test(link);
const mk=(tag,cl,text)=>{const n=document.createElement(tag);if(cl)n.className=cl;if(text!==undefined)n.textContent=text;return n};
let strategies=[],expanded=false;

function strategyCard(x){
 const el=mk("article","strategy-card");
 el.append(mk("small","muted",x.category+" · "+x.effort+" · "+(x.sourceType==="reddit_ervaringen"?"Reddit-methode, uitkomst niet gegarandeerd":"voorwaarden gevonden")));
 el.append(mk("h3",null,x.title));
 el.append(mk("p",null,x.why));
 const details=mk("details");
 details.append(mk("summary",null,"Wat moet ik concreet doen?"));
 const list=mk("ol");
 for(const task of x.actions||[])list.append(mk("li",null,task));
 details.append(list);
 if(x.conditions)details.append(mk("p","muted","Let op: "+x.conditions));
 el.append(details);
 if(safeLink(x.url)){const link=mk("a",null,"Bekijk actie of onderbouwing");link.href=x.url;link.target="_blank";link.rel="noopener noreferrer";el.append(link)}
 return el;
}
function renderStrategies(){
 const category=$("strategyCategory").value;
 const rows=strategies.filter(x=>!category||x.category===category)
   .sort((a,b)=>(b.priority||0)-(a.priority||0));
 const root=$("strategyCards");root.replaceChildren();
 for(const item of (expanded?rows:rows.slice(0,3)))root.append(strategyCard(item));
 $("strategyCount").textContent=rows.length+" onderzochte strategieën; "+Math.min(expanded?rows.length:3,rows.length)+" getoond";
 $("moreStrategies").hidden=rows.length<=3;
 $("moreStrategies").textContent=expanded?"Toon alleen de belangrijkste":"Bekijk alle "+rows.length+" strategieën";
 if(!rows.length)root.append(mk("p","muted","Geen strategieën in deze categorie."));
}
$("strategyCategory").addEventListener("change",()=>{expanded=false;renderStrategies()});
$("moreStrategies").addEventListener("click",()=>{expanded=!expanded;renderStrategies()});
fetch("./bespaarstrategien.json?"+Date.now(),{cache:"no-store"})
 .then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()})
 .then(d=>{
  strategies=(d.items||[]).filter(x=>x.id&&x.title&&x.url&&Array.isArray(x.actions));
  renderStrategies();
 })
 .catch(()=>{$("strategyCards").textContent="Strategieën tijdelijk niet bereikbaar. Controleer de laatste publicatiestatus.";});

function readAmount(id,required=true){
 const value=$(id).value.trim().replace(",",".");
 if(!value && !required)return 0;
 return value && Number.isFinite(Number(value)) ? Number(value) : NaN;
}
function renderCalculator(){
 const type=$("benefitType").value;
 $("benefitLabel").textContent=type==="gift"?"Cadeauwaarde die je zelf écht zou betalen (€)":"Bedrag cashback of kortingstegoed (€)";
 $("giftCopayWrap").hidden=type!=="gift";
 $("benefitAmountWrap").hidden=type==="none";
}
$("benefitType").addEventListener("change",renderCalculator);
renderCalculator();

$("contractDealCompare").addEventListener("click",()=>{
 const type=$("benefitType").value;
 const raw={
  months:Number($("compareDuration").value),
  promoMonths:Number($("comparePromoMonths").value),
  currentMonthly:readAmount("compareCurrent"),
  introMonthly:readAmount("comparePromo"),
  normalMonthly:readAmount("compareStandard"),
  activationEUR:readAmount("compareOneOff",false),
  benefitType:type,
  benefitEUR:type==="none"?0:readAmount("compareBenefit"),
  giftCopayEUR:type==="gift"?readAmount("compareGiftCopay",false):0
 };
 const q=compareContract(raw);
 const root=$("contractDealResult");root.replaceChildren();
 if(q.status!=="estimate_only"){
  root.append(mk("p","bad","Vul alle verplichte prijzen correct in. Het aantal actiemaanden mag niet langer zijn dan de contractduur."));
  return;
 }
 root.append(mk("p",null,"Huidig contract over "+q.months+" maanden: "+eur(q.baselineCostEUR)));
 root.append(mk("p",null,"Nieuwe maandlasten en aansluitkosten: "+eur(q.chargesEUR)));
 root.append(mk("p",null,"Voorlopige contante kosten van het nieuwe aanbod: "+eur(q.cashCostEUR)));
 if(type==="gift")root.append(mk("p",null,"Zelf ingeschatte bruikbare cadeauwaarde: "+eur(q.userGiftValueEUR)+" (geen geldontvangst)."));
 const figure=mk("strong","potentialResult",
  "Mogelijk economisch verschil: "+(q.possibleEconomicDifferenceEUR>=0?"+":"")+eur(q.possibleEconomicDifferenceEUR));
 root.append(figure);
 root.append(mk("p","muted","Scenario, niet gerealiseerde besparing. Controleer daadwerkelijke looptijd, tijdelijke korting, contractvoorwaarden, recht op cashback/cadeau, claimdeadline, installatiekosten en de exacte diensten. Een cadeau krijgt uitsluitend de waarde die je anders zelf echt zou uitgeven."));
});
