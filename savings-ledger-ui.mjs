import {normalizeEntry,addSavings,totalSaved} from "./savings-ledger.mjs";

const storageKey="kansenkompas_privatesavings_device_v1";
const $=id=>document.getElementById(id);
const eur=n=>new Intl.NumberFormat("nl-NL",{style:"currency",currency:"EUR"}).format(n);
const now=()=>new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Amsterdam"}).format(new Date());
const mk=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
const dateField=$("ledgerDate");
dateField.value=now();
dateField.max=now();
let entries=[];
try{
 const rows=JSON.parse(localStorage.getItem(storageKey)||"[]");
 if(Array.isArray(rows))entries=rows.filter(x=>normalizeEntry({...x,confirmed:true},now()));
}catch{}
function persist(){
 try{localStorage.setItem(storageKey,JSON.stringify(entries));return true}
 catch{return false}
}
function render(){
 const root=$("ledgerEntries");root.replaceChildren();
 $("ledgerTotal").textContent=eur(totalSaved(entries));
 $("ledgerCount").textContent=entries.length+" geregistreerde besparingen";
 for(const x of [...entries].reverse().slice(0,40)){
  const row=mk("div","ledger-row");
  const main=mk("div");
  main.append(mk("strong",null,x.description));
  main.append(mk("p","muted",x.category+" · "+x.date+" · Gewoon "+eur(x.usualPrice)+" → betaald "+eur(x.paidPrice)));
  row.append(main);
  row.append(mk("strong","good",eur(x.savedEUR)));
  const del=mk("button","secondary","Verwijder");
  del.type="button";
  del.addEventListener("click",()=>{
   entries=entries.filter(v=>v.id!==x.id);
   persist();render();
  });
  row.append(del);root.append(row);
 }
 if(!entries.length)root.append(mk("p","muted","Nog geen door jou geregistreerde besparingen. Alleen werkelijk afgeronde aankopen of betaalde facturen meetellen."));
}
$("ledgerAdd").addEventListener("click",()=>{
 const raw={date:$("ledgerDate").value,
  description:$("ledgerDescription").value,
  category:$("ledgerCategory").value,
  usualPrice:$("ledgerUsual").value,
  paidPrice:$("ledgerPaid").value,
  confirmed:$("ledgerConfirmed").checked,
  id:"save-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,10)};
 const result=addSavings(entries,raw,now());
 const status=$("ledgerStatus");
 if(!result.added){
  status.textContent=result.reason==="duplicate"?"Deze besparing is al geregistreerd.":"Controleer de datum, bedragen, categorie en vink aan dat de aankoop of rekening daadwerkelijk betaald is.";
  return;
 }
 entries=result.entries;
 if(!persist()){status.textContent="Opslaan in de browser is mislukt; controleer je browserinstellingen.";return}
 status.textContent="Op dit apparaat geregistreerd. Dit is jouw eigen bevestiging, geen onafhankelijk geverifieerd transactiebedrag.";
 $("ledgerDescription").value="";
 $("ledgerConfirmed").checked=false;
 render();
});
$("ledgerExport").addEventListener("click",()=>{
 const clean=entries.map(x=>({...x})); // Explicit user action; nothing auto-sent.
 const blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),records:clean},null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob);
 const link=document.createElement("a");
 link.href=url;link.download="kansenkompas-prive-besparingen.json";link.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
 $("ledgerStatus").textContent="Exportbestand aangemaakt. Bewaar het privé; het kan aankoopgegevens bevatten.";
});
$("ledgerClear").addEventListener("click",()=>{
 if(!confirm("Alle door jou lokaal bijgehouden besparingen op dit apparaat wissen?"))return;
 entries=[];persist();render();
 $("ledgerStatus").textContent="Lokale registratie gewist.";
});
render();
