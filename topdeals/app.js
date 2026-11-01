"use strict";
(function(){
 const el=id=>document.getElementById(id),eur=n=>new Intl.NumberFormat("nl-NL",{style:"currency",currency:"EUR"}).format(n);
 const escape=s=>String(s??"").replace(/[&<>"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x]));
 const categories=["persoonlijk","supermarkt","tuin","bouwmarkt","drogisterij","elektronica","sport","huis","overig"];
 const validLink=url=>{try{const u=new URL(url);return u.protocol==="https:"&&!u.username&&!u.password?u.href:null}catch{return null}};
 const STORE="specialedeals-top10-saved-v1";
 let data=null,saved=[];
 try{const x=JSON.parse(localStorage.getItem(STORE)||"[]");if(Array.isArray(x))saved=x.map(String).slice(0,1000)}catch{}
 const params=new URLSearchParams(location.search);
 let active=params.get("categorie");
 if(!categories.includes(active))active=null;
 const status=(s,error=false)=>{el("status").textContent=s;el("status").dataset.error=String(error)};
 const dateNL=v=>{if(!v)return "onbekend";const t=new Date(v);return Number.isFinite(t.getTime())?t.toLocaleString("nl-NL",{timeZone:"Europe/Amsterdam",dateStyle:"short",timeStyle:"short"}):escape(v)};
 function toolbar(){
  el("categoryNav").innerHTML='<a href="./"'+(!active?' aria-current="page"':'')+'>Alle categorieën</a>'+
   categories.map(k=>{
     const c=data?.categories?.[k]||{},n=c.available??0;
     return '<a href="?categorie='+encodeURIComponent(k)+'"'+(k===active?' aria-current="page"':'')+'>'+
       escape(c.label||k)+' <small>'+n+'</small></a>';
   }).join("");
 }
 function offerCard(item,index){
   const href=validLink(item.url);
   const wish=item.wishMatches||[];
   const discount=item.advertisedDiscountPercent;
   const price=Number(item.priceEUR);
   const cost=Number.isFinite(price)?eur(price):"Prijs onbekend";
   const end=item.endDate?'· tot '+escape(item.endDate)+(item.dateEstimated?' (geschat)':''):'';
   const score=Number(item.rankScore);
   const evidence=(item.directProductPage?"Directe winkelpagina":"Bronoverzicht")+
       (item.individualDateUnknown?" · einddatum niet per artikel vastgesteld":"");
   const id=String(item.id||item.url),isSaved=saved.includes(id);
   return '<article class="top-card"><span class="top-rank">'+index+'</span><div class="top-card-body">'+
      '<div class="top-card-meta"><span class="top-shop">'+escape(item.shop)+'</span>'+
      (wish.length?'<span class="top-wish">♡ '+escape(wish.map(x=>x.name).slice(0,2).join(" / "))+'</span>':'')+'</div>'+
      '<h3>'+escape(item.title)+'</h3><div class="top-pricing"><span class="top-price">'+escape(cost)+'</span>'+
      (item.advertisedReferenceEUR?'<span class="top-crossed" title="Door winkel vermelde referentieprijs">'+eur(Number(item.advertisedReferenceEUR))+'</span>':'')+
      (discount!==null&&discount!==undefined?'<span class="top-claim">'+Number(discount).toLocaleString("nl-NL")+'% volgens winkelreferentie</span>':'')+
      '</div><p class="top-card-note">'+escape(item.quality||"Brongegevens; voorraad en bezorging niet gecontroleerd")+
      '. De getoonde prijs is geen bevestigde NL-totaalprijs.</p>'+
      '<div class="top-card-facts">'+(item.offerType?'<span>'+escape(item.offerType)+'</span>':'')+
      '<span>'+escape(evidence)+'</span>'+(end?'<span>'+end+'</span>':'')+
      (item.bundle?'<span>Bundel: geen prijs per stuk afgeleid</span>':'')+
      '</div><div class="top-card-bottom"><button class="top-save" type="button" data-id="'+escape(id)+'" aria-pressed="'+isSaved+'">'+
       (isSaved?'♥ Bewaard':'♡ Bewaar')+'</button>'+
       (href?'<a href="'+escape(href)+'" target="_blank" rel="noopener noreferrer">Controleer prijs bij bron ↗</a>':'')+
      '</div></div></article>';
 }
 function section(key){
   const c=data.categories[key],isPersonal=key==="persoonlijk";
   const search=el("search").value.trim().toLocaleLowerCase("nl-NL"),min=el("discount").value;
   const onlySaved=el("saved").value==="saved";
   let rows=(c.top10||[]).filter(x=>{
     if(search&&!([x.title,x.shop,x.source].join(" ").toLocaleLowerCase("nl-NL").includes(search)))return false;
     if(min!=="all"&&(!Number.isFinite(Number(x.advertisedDiscountPercent))||x.advertisedDiscountPercent===null||Number(x.advertisedDiscountPercent)<Number(min)))return false;
     if(onlySaved&&!saved.includes(String(x.id||x.url)))return false;
     return true;
   });
   const label=isPersonal?"Geen prijsgeldige verlanglijstmatches gevonden. Kijk ook op je verlanglijstpagina naar externe onderzoeksvondsten.":key==="bouwmarkt"?"De aangesloten feeds leverden geen kwalificerende bouwmarktproducten. Dat betekent niet dat winkels zoals GAMMA, Praxis en HORNBACH geen aanbiedingen hebben.":"Er zijn binnen deze bronnen en filters onvoldoende actuele, individueel geprijsde aanbiedingen. Een ontbrekend product wordt niet ingevuld met verouderde reclame.";
   return '<section class="top-list-section" id="groep-'+escape(key)+'"><div class="top-list-heading"><div>'+
     '<h2>'+escape(c.label)+'</h2><p>'+Number(c.available||0).toLocaleString("nl-NL")+' geschikte producten in bronselectie · '+rows.length+' in deze Top 10-weergave'+
     (isPersonal?" · niet op volledige markt gecontroleerd":"")+'</p></div>'+
     '<a href="../weekdeals/">Bekijk alle weekdeals ↗</a></div>'+
     (rows.length?'<div class="top-cards">'+rows.map((x,i)=>offerCard(x,i+1)).join("")+'</div>':
     '<div class="top-empty"><h3>Momenteel geen geschikte Top 10</h3>'+escape(label)+'</div>')+'</section>';
 }
 function sources(){
  el("sourceGrid").innerHTML=(data?.sourceHealth||[]).map(x=>{
    const s=x.sourceUpdatedAt?dateNL(x.sourceUpdatedAt):"geen datum";
    return '<div class="top-source"><strong>'+escape(x.source)+'</strong>'+
      '<span class="'+(x.usable?'top-good':'top-bad')+'">'+(x.usable?'Bronbestand recent genoeg':'Bronbestand te oud / niet beschikbaar')+'</span>'+
      '<small>Laatst bijgewerkt: '+s+' · '+escape(x.offersInSnapshot)+' records'+
      (x.ageHours!==null?' · '+escape(x.ageHours)+' uur oud':'')+'</small></div>';
  }).join("");
 }
 function render(){
  if(!data)return;
  toolbar();
  const chosen=active?[active]:categories;
  el("categorySections").innerHTML=chosen.map(section).join("");
  el("categorySections").querySelectorAll("button[data-id]").forEach(b=>b.addEventListener("click",()=>{
     const id=b.dataset.id;const set=new Set(saved);
     if(set.has(id))set.delete(id);else set.add(id);
     saved=[...set];try{localStorage.setItem(STORE,JSON.stringify(saved))}catch{}
     render();
  }));
  el("totalEligible").textContent=Number(data.eligibleCount||0).toLocaleString("nl-NL");
  el("wishlistCount").textContent=Number(data.wishlistMatchedCount||0).toLocaleString("nl-NL");
  el("verifiedCount").textContent=Number(data.verifiedDealCount||0).toLocaleString("nl-NL");
  el("sourceCount").textContent=(data.sourceHealth||[]).filter(x=>x.usable).length+"/"+(data.sourceHealth||[]).length;
  const when=data.generatedAt?dateNL(data.generatedAt):"onbekend";
  const feedDates=(data.sourceHealth||[]).map(x=>x.ageHours).filter(x=>typeof x==="number");
  const maxAge=feedDates.length?Math.max(...feedDates):null;
  const hours=Date.now()-new Date(data.generatedAt).getTime();
  status("Top 10 berekend: "+when+
    (Number.isFinite(hours)&&hours>2*3600000?" · Deze berekening is ouder dan 2 uur":"")+
    " · "+data.eligibleCount+" geschikte actuele actie-items · "+
    (maxAge!=null?"oudste beschikbare bronbestand "+maxAge+" uur":"geen gedateerde bron")+
    " · winkelprijzen niet onafhankelijk opnieuw gecontroleerd.");
  sources();
 }
 ["search","discount","saved"].forEach(id=>el(id).addEventListener(id==="search"?"input":"change",render));
 el("reset").addEventListener("click",()=>{
  el("search").value="";el("discount").value="all";el("saved").value="all";render();
 });
 fetch("./data.json?v="+Date.now(),{cache:"no-store"})
   .then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()})
   .then(j=>{if(!j.categories||!categories.every(k=>j.categories[k]?.top10 instanceof Array))throw Error("Onverwacht datamodel");
      data=j;render()})
   .catch(e=>{status("De Top 10 kon niet geladen worden: "+e.message,true);
     el("categorySections").innerHTML='<div class="top-empty">Geen actuele Top 10 beschikbaar. <a href="../weekdeals/">Bekijk de afzonderlijke Weekdeals</a>.</div>'});
})();