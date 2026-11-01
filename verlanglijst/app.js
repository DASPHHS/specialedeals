"use strict";
/* Personal wishlist client. A candidate is never a verified deal. */
(function(){
 const el=id=>document.getElementById(id);
 const KEY="specialedeals-wishlist-radar-v2",LEGACY="specialedeals-wishlist-v1";
 const eur=x=>new Intl.NumberFormat("nl-NL",{style:"currency",currency:"EUR"}).format(x);
 const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 const trim=x=>String(x??"").trim();
 const urlSafe=x=>{try{const u=new URL(String(x));return u.protocol==="https:"&&!u.username&&!u.password?u.href:null}catch{return null}};
 const category=w=>{const n=String(w.name||"").toLowerCase();
  if(w.category&&w.category!=="Overig")return w.category;
  if(/hoka|padel|tennis/.test(n))return "Sport";
  if(/arc.?teryx|jacket|outdoor/.test(n))return "Mode & outdoor";
  if(/apple|airpods|macbook|imac|watch ultra/.test(n))return "Apple & elektronica";
  if(/geur|parfum|rituals|janzen|berger/.test(n))return "Verzorging & huisgeur";
  if(/usb|thunderbolt|gadgets|e-ink/.test(n))return "Tech & gadgets";
  return "Overig";
 };
 let central=[],signals=null,editing=null,expanded=new Set(),loaded=false;
 let state={local:[],overrides:{}};
 try{const x=JSON.parse(localStorage.getItem(KEY)||"null");
  if(x&&typeof x==="object"){if(Array.isArray(x.local))state.local=x.local;
   if(x.overrides&&typeof x.overrides==="object"&&!Array.isArray(x.overrides))state.overrides=x.overrides}
 }catch{}
 const persist=()=>{try{localStorage.setItem(KEY,JSON.stringify(state));return true}catch{return false}};
 function allWishes(){
  const listed=central.map(w=>{const o=state.overrides[w.id]||{};return {
   id:String(w.id),name:String(w.name),category:category(w),notes:trim(o.notes??w.notes),
   targetPriceEUR:o.targetPriceEUR??w.maxPriceEUR??null,url:o.url??null,local:false
  }});
  const names=new Set(listed.map(x=>x.name.toLowerCase().trim()));
  return listed.concat(state.local.filter(w=>w&&typeof w.name==="string"&&trim(w.name)&&!names.has(trim(w.name).toLowerCase()))
    .map(w=>({id:String(w.id),name:trim(w.name),category:category(w),notes:trim(w.notes),
     targetPriceEUR:w.targetPriceEUR,url:w.url,local:true})));
 }
 const getHits=id=>{const s=signals?.items?.find(w=>w.id===id);
  return {verified:s?.verifiedDeals||[],candidates:s?.candidates||[],vcount:s?.verifiedCount||0,ccount:s?.candidateCount||0};
 };
 function status(text,error=false){el("pageStatus").textContent=text;el("pageStatus").dataset.error=String(error)}
 function migrate(){
  if(localStorage.getItem(KEY)!==null)return;
  try{const old=JSON.parse(localStorage.getItem(LEGACY)||"[]");if(!Array.isArray(old))return;
   const names=new Set(central.map(w=>String(w.name).toLowerCase()));
   for(const w of old){const name=trim(w?.name);
    if(!name||names.has(name.toLowerCase()))continue;
    state.local.push({id:"local-migrated-"+state.local.length,name:name.slice(0,150),
     category:category(w),targetPriceEUR:w.maxPriceEUR??null,notes:"",url:null});
    names.add(name.toLowerCase());
   }persist();
  }catch{}
 }
 function price(x,verified){
  const value=verified?x.totalPriceEUR:x.priceEUR;
  return value!=null&&Number.isFinite(Number(value))?eur(Number(value))+(verified?" incl. verzending*":" winkelprijs*"):"Prijs niet vermeld";
 }
 function offerRow(x,verified){
  const link=urlSafe(x.url),label=verified?"BEWEZEN KOOPDEAL":"WINKELACTIE · NOG CONTROLEREN";
  const discount=verified?x.discountPercent+"% echte korting":
      x.storeDiscountPercent!=null?x.storeDiscountPercent+"% volgens winkelreferentie":"Kortingsclaim niet onafhankelijk geverifieerd";
  return '<article class="wish-offer"><div class="wish-offer-head"><div><div class="wish-offer-label'+(verified?' good':'')+'">'+label+'</div>'+
   '<h4>'+esc(x.title)+'</h4></div><div class="wish-offer-price">'+esc(price(x,verified))+'</div></div>'+
   '<p>'+esc(x.shop||x.source||"Bron")+' · '+esc(discount)+(x.endDate?' · gepubliceerd t/m '+esc(x.endDate):'')+'</p>'+
   (verified?'<p>Referentie: '+esc(eur(x.referencePriceEUR))+' · aangetoonde besparing '+esc(eur(x.savingsEUR))+'.</p>':'')+
   '<p>'+esc(verified?'Laatst geverifieerd: '+x.verifiedAt+' · variant '+x.variant:
    (x.variantNote||"Exacte uitvoering en bezorgkosten controleren")+
      (x.linkType==="bronoverzicht"?". Bronlink is geen directe productpagina":""))+'</p>'+
   (link?'<a href="'+esc(link)+'" target="_blank" rel="noopener noreferrer">Bekijk '+(verified?'geverifieerde deal':'bron')+' ↗</a>':'')+'</article>';
 }
 function wishCard(w){
  const h=getHits(w.id),count=h.verified.length+h.candidates.length,open=expanded.has(w.id);
  const target=Number(w.targetPriceEUR)>0?Number(w.targetPriceEUR):null;
  const within=target&&h.verified.some(x=>Number(x.totalPriceEUR)<=target);
  const label=h.vcount?'<span class="wish-badge verified">✓ '+h.vcount+' bewezen koopdeal(s)</span>':
    h.ccount?'<span class="wish-badge candidate">◷ '+h.ccount+' mogelijke winkelactie(s)</span>':
    '<span class="wish-badge">Nog geen actuele match</span>';
  const actions=(count?'<button class="wish-mini" type="button" data-action="expand" data-id="'+esc(w.id)+'" aria-expanded="'+open+'">'+(open?'Verberg hits':'Bekijk '+count+' hits')+'</button>':'')+
   '<button class="wish-mini light" type="button" data-action="edit" data-id="'+esc(w.id)+'">Bewerk</button>'+
   (w.local?'<button class="wish-mini light" type="button" data-action="remove" data-id="'+esc(w.id)+'" aria-label="Verwijder deze wens">×</button>':'');
  const search="https://www.google.com/search?tbm=shop&q="+encodeURIComponent(w.name);
  const offers=h.verified.map(x=>offerRow(x,true)).join("")+h.candidates.map(x=>offerRow(x,false)).join("");
  return '<article class="wish-card'+(h.vcount?' with-deal':'')+'">'+
   '<div class="wish-card-top"><div><span class="wish-card-category">'+esc(w.category)+'</span><h3>'+esc(w.name)+'</h3></div>'+
   '<span class="wish-card-icon" aria-hidden="true">'+(h.vcount?'✳':h.ccount?'⌕':'♡')+'</span></div>'+
   '<div class="wish-card-status">'+label+(w.local?'<span class="wish-badge local">Alleen op dit apparaat</span>':'')+
   (within?'<span class="wish-badge verified">Binnen richtprijs*</span>':'')+'</div>'+
   '<p class="wish-card-notes">'+esc(w.notes||'Voeg een specifieke maat, variant of uitvoering toe om gerichter te vergelijken.')+'</p>'+
   '<div class="wish-card-metrics"><div><strong>'+count+'</strong><small>Resultaten zichtbaar</small></div>'+
   '<div><strong>'+(target?esc(eur(target)):'—')+'</strong><small>Jouw richtprijs</small></div>'+
   '<div><strong>'+(w.local?'Lokaal':'Centraal')+'</strong><small>'+(w.local?'Nog niet in scanner':'Gevolgd door scanner')+'</small></div></div>'+
   '<div class="wish-card-cta"><div class="wish-card-actions">'+actions+'</div><a href="'+esc(search)+'" target="_blank" rel="noopener noreferrer">Zoek breder ↗</a></div>'+
   (w.url&&urlSafe(w.url)?'<a href="'+esc(urlSafe(w.url))+'" class="wish-more-note" target="_blank" rel="noopener noreferrer">Jouw productlink ↗</a>':'')+
   (w.local?'<div class="wish-more-note">Nieuwe lokale wensen worden nog niet automatisch via de centrale bronnen doorzocht. Voeg ze aan GitHub toe voor dagelijkse tracking.</div>':'')+
   (count?'<div class="wish-offers" '+(open?'':'hidden')+'>'+offers+
     (h.ccount>h.candidates.length?'<p class="wish-more-note">'+(h.ccount-h.candidates.length)+' extra onderzoekshits niet getoond.</p>':'')+'</div>':'')+
   '</article>';
 }
 function render(){
  const q=trim(el("wishSearch").value).toLocaleLowerCase("nl-NL"),f=el("wishStatus").value,sort=el("wishSort").value;
  const wishes=allWishes();
  let selected=wishes.filter(w=>{
   const h=getHits(w.id);
   if(q&&!([w.name,w.category,w.notes].join(" ").toLocaleLowerCase("nl-NL").includes(q)))return false;
   if(f==="verified"&&!h.vcount)return false;
   if(f==="candidate"&&!h.ccount)return false;
   if(f==="missing"&&(h.vcount||h.ccount))return false;
   if(f==="local"&&!w.local)return false;return true;
  });
  selected.sort((a,b)=>{
   const x=getHits(a.id),y=getHits(b.id);
   if(sort==="name")return a.name.localeCompare(b.name,"nl");
   if(sort==="target")return (Number(a.targetPriceEUR)||Infinity)-(Number(b.targetPriceEUR)||Infinity)||a.name.localeCompare(b.name,"nl");
   if(sort==="count")return y.ccount+y.vcount-x.ccount-x.vcount||a.name.localeCompare(b.name,"nl");
   return y.vcount-x.vcount||y.ccount-x.ccount||a.name.localeCompare(b.name,"nl");
  });
  el("wishGrid").innerHTML=selected.map(wishCard).join("");
  el("emptyState").hidden=selected.length>0;
  el("statWishes").textContent=wishes.length.toLocaleString("nl-NL");
  el("statVerified").textContent=(signals?.verifiedDealCount??0).toLocaleString("nl-NL");
  el("statCandidates").textContent=(signals?.candidateCount??0).toLocaleString("nl-NL");
  el("statStores").textContent=signals?.shopsSeen!=null?signals.shopsSeen.toLocaleString("nl-NL"):"—";
  el("heroMatchCount").textContent=(signals?.candidateCount??0).toLocaleString("nl-NL");
 }
 function edit(w){
  editing=w||null;el("editor").hidden=false;el("wishForm").reset();
  el("editId").value=w?.id||"";el("editorTitle").textContent=w?"Wens aanpassen":"Product toevoegen";
  el("productName").value=w?.name||"";el("productName").readOnly=!!w&&!w.local;
  el("productCategory").value=w?.category||"Overig";el("productCategory").disabled=!!w&&!w.local;
  el("productTarget").value=w?.targetPriceEUR||"";
  el("productNotes").value=w?.notes||"";
  el("productURL").value=w?.url||"";
  el("formStatus").textContent=w&&!w.local?
    "Centrale naam blijft ongewijzigd. Richtprijs en notities worden alleen lokaal aangepast.":
    "De centrale scanner volgt pas wensen uit GitHub. Deze invoer wordt lokaal bewaard.";
  el("editor").scrollIntoView({behavior:"smooth",block:"start"});el("productName").focus();
 }
 function close(){el("editor").hidden=true;editing=null;}
 function save(e){
  e.preventDefault();const name=trim(el("productName").value).slice(0,150);
  if(!name)return;
  const target=el("productTarget").value?Number(el("productTarget").value):null;
  if(target!==null&&(!Number.isFinite(target)||target<=0||target>100000)){
   el("formStatus").textContent="Vul een geldige richtprijs in.";return;
  }
  const u=trim(el("productURL").value);
  if(u&&!urlSafe(u)){el("formStatus").textContent="Gebruik alleen een https-productlink.";return;}
  const data={name,category:trim(el("productCategory").value),targetPriceEUR:target,
   notes:trim(el("productNotes").value).slice(0,250),url:u||null};
  if(editing&&!editing.local)state.overrides[editing.id]={targetPriceEUR:target,notes:data.notes,url:data.url};
  else if(editing){const old=state.local.find(x=>x.id===editing.id);if(old)Object.assign(old,data);}
  else state.local.push({id:"local-"+Date.now()+"-"+Math.random().toString(36).slice(2,8),...data});
  const saved=persist();close();render();status(saved?"Wens lokaal opgeslagen. Centrale tracking vereist een update van GitHub.":
   "Wens weergegeven, maar browseropslag is uitgeschakeld. Exporteer je lijst.",!saved);
 }
 function download(){
  const body={schemaVersion:2,exportedAt:new Date().toISOString(),source:"Speciale Deals lokaal",
    items:allWishes().map(x=>({id:x.id,name:x.name,category:x.category,notes:x.notes,
      maxPriceEUR:x.targetPriceEUR,productURL:x.url,source:x.local?"local":"central"}))};
  const blob=new Blob([JSON.stringify(body,null,2)],{type:"application/json"});
  const u=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=u;a.download="speciale-deals-verlanglijst.json";a.click();setTimeout(()=>URL.revokeObjectURL(u),1500);
 }
 async function upload(file){
  if(!file)return;if(file.size>1000000){status("Import maximaal 1 MB.",true);return}
  try{const data=JSON.parse(await file.text());if(!Array.isArray(data.items)||data.items.length>300)throw Error("Ongeldige lijst of meer dan 300 producten");
   const known=new Set(allWishes().map(x=>x.name.toLowerCase()));let n=0;
   for(const x of data.items){const name=trim(x?.name).slice(0,150);
    if(!name||known.has(name.toLowerCase()))continue;
    const raw=x.maxPriceEUR??x.targetPriceEUR,target=Number(raw)>0&&Number(raw)<=100000?Number(raw):null;
    state.local.push({id:"local-import-"+Date.now()+"-"+n,name,category:trim(x.category)||"Overig",
     notes:trim(x.notes).slice(0,250),targetPriceEUR:target,url:urlSafe(x.productURL||x.url)});
    known.add(name.toLowerCase());n++;
   }persist();render();status(n+" lokale wensen geïmporteerd; nog niet automatisch centraal gevolgd.");
  }catch(err){status("Import mislukt: "+err.message,true)}el("importFile").value="";
 }
 async function load(){
  status("Centrale lijst en actueel winkelaanbod laden…");
  const fetchJson=async url=>{const r=await fetch(url+"?v="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);return r.json()};
  const [a,b]=await Promise.allSettled([fetchJson("../wishlist.json"),fetchJson("./signalen.json")]);
  if(a.status==="fulfilled"&&Array.isArray(a.value.items)){central=a.value.items;if(!loaded)migrate();loaded=true}
  signals=b.status==="fulfilled"&&Array.isArray(b.value.items)?b.value:null;
  if(!central.length)status("Centrale verlanglijst niet bereikbaar. Je lokale wensen blijven zichtbaar.",true);
  else if(!signals)status("Centrale verlanglijst geladen; de nieuwe radar-index is nog niet beschikbaar.",true);
  else{
   const when=signals.updatedAt?new Date(signals.updatedAt).toLocaleString("nl-NL",{timeZone:"Europe/Amsterdam"}):"onbekend";
   status("Brondata "+when+" · "+signals.shopsSeen+" winkels uit gekoppelde feeds · "+signals.candidateCount+" mogelijke productmatches. Geen volledige webshopdekking.");
  }render();
 }
 el("wishGrid").addEventListener("click",e=>{
  const b=e.target.closest("button[data-action]");if(!b)return;
  const id=b.dataset.id,action=b.dataset.action;
  if(action==="expand"){if(expanded.has(id))expanded.delete(id);else expanded.add(id);render();return}
  const w=allWishes().find(x=>x.id===id);
  if(action==="edit"&&w)edit(w);
  if(action==="remove"&&w?.local&&window.confirm("Deze lokale wens verwijderen?")){
   state.local=state.local.filter(x=>x.id!==id);persist();render();
  }
 });
 el("addToggle").onclick=()=>edit(null);el("editorClose").onclick=close;el("wishForm").onsubmit=save;
 el("reloadData").onclick=load;el("downloadList").onclick=download;
 el("importList").onclick=()=>el("importFile").click();
 el("importFile").onchange=()=>upload(el("importFile").files?.[0]);
 for(const id of ["wishSearch","wishStatus","wishSort"])
  el(id).addEventListener(id==="wishSearch"?"input":"change",render);
 el("clearWishFilters").onclick=()=>{el("wishSearch").value="";el("wishStatus").value="all";el("wishSort").value="recommended";render()};
 load().catch(e=>status("Laden mislukt: "+e.message,true));
})();
