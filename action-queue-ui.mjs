import {selectActionable} from "./action-queue.mjs";
const $ = id => document.getElementById(id);
const target = $("urgentActions");
const count = $("urgentCount");
const storageKey = "kansenkompas_actions_completed_device_v1";
const nowIsoNL = () => new Intl.DateTimeFormat("sv-SE", {timeZone:"Europe/Amsterdam"}).format(new Date());
const fmt = day => new Date(day + "T12:00:00").toLocaleDateString("nl-NL", {day:"numeric",month:"short"});
const mk = (tag,cls,text) => {const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e};
let actions = [];
let done = {};
try {done=JSON.parse(localStorage.getItem(storageKey)||"{}")||{};}catch{done={}}

function render(){
  target.replaceChildren();
  const active=actions.filter(x=>!done[x.id]);
  count.textContent=String(active.length);
  for(const a of active.slice(0,5)){
    const card=mk("article","card action-item");
    card.append(mk("small","event-meta",a.kind==="contest"?"Winactie · voor jou":"Sample sale · aangekondigd"));
    card.append(mk("h3",null,a.title));
    card.append(mk("p","event-date",(a.remaining===0?"Laatste dag":a.remaining===1?"Nog 1 dag":"Sluit "+fmt(a.deadline))+(a.location?" · "+a.location:"")));
    if(a.detail)card.append(mk("p",null,a.detail));
    card.append(mk("p","small",a.status));
    const row=mk("div","action-buttons");
    const link=mk("a",null,a.action);link.href=a.url;link.target="_blank";link.rel="noopener noreferrer";
    row.append(link);
    const finish=mk("button","secondary","Verberg op dit apparaat");
    finish.type="button";
    finish.addEventListener("click",()=>{
      // Only local dismissal: does NOT assert successful competition entry.
      done[a.id] = Date.now();
      try {localStorage.setItem(storageKey,JSON.stringify(done));}catch{}
      render();
    });
    row.append(finish);card.append(row);target.append(card);
  }
  if(!active.length)target.append(mk("p","muted","Geen nieuwe geprioriteerde acties op basis van recent gecontroleerde gegevens."));
  $("resetActions").hidden=Object.keys(done).length===0;
}
$("resetActions").addEventListener("click",()=>{
 done={};try{localStorage.removeItem(storageKey)}catch{}
 render();
});
Promise.allSettled(["contests.json","sample-events.json"].map(file=>fetch("./"+file+"?"+Date.now(),{cache:"no-store"}).then(r=>{
 if(!r.ok)throw Error("HTTP "+r.status);
 return r.json();
}))).then(([c,e])=>{
 if(c.status!=="fulfilled"||e.status!=="fulfilled"){
   target.replaceChildren(mk("p","muted","Een bron is niet bereikbaar. Deze actielijst is nog niet compleet."));
   count.textContent="–";return;
 }
 const now = new Date();
 actions=selectActionable(c.value.contests||[],e.value.events||[],nowIsoNL(),now,20);
 // Forget old dismissal keys after 90 days; no personal details stored.
 for(const [id,time] of Object.entries(done))
   if(!Number.isFinite(time)||now.getTime()-time>90*86400000)delete done[id];
 render();
});
