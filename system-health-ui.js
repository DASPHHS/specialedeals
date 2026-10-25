/* Recompute age in the browser so a stopped scanner cannot look healthy forever. */
(async()=>{
 const banner=document.getElementById('healthBanner'),root=document.getElementById('systemHealth');
 const add=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e};
 try{
  const response=await fetch('./system-health.json?'+Date.now(),{cache:'no-store'});if(!response.ok)throw Error(response.status);
  const data=await response.json();let issues=0;
  for(const m of data.modules){
   const age=(Date.now()-Date.parse(m.checkedAt))/3600000;
   const state=!Number.isFinite(age)||age>m.maxAgeHours||age< -1?'verouderd':m.state;
   if(state!=='werkt')issues++;
   const card=add('article','');card.className='tile';
   card.append(add('h3',m.name),add('p','Status: '+state),add('p',m.successful+' van '+m.total+' bronchecks geslaagd'));
   card.append(add('p',m.checkedAt?'Laatste controle: '+new Date(m.checkedAt).toLocaleString('nl-NL',{timeZone:'Europe/Amsterdam'}):'Nog geen controle geregistreerd'));
   root.append(card);
  }
  for(const m of data.capabilities){const c=add('article','');c.className='tile';c.append(add('h3',m.name),add('p','Status: '+m.state),add('p',m.detail));root.append(c)}
  banner.textContent=issues?issues+' van '+data.modules.length+' scanonderdelen vragen aandacht. Bekijk Scanstatus voor fouten en ontbrekende dekking.':'Alle '+data.modules.length+' scanonderdelen zijn recent uitgevoerd. Productvoorwaarden en meldingen hebben een eigen controlestatus.';
  const a=add('a',' Bekijk scanstatus');a.href='#sources';banner.append(a);
 }catch{banner.textContent='Scanstatus kon niet worden geladen. Actualiteit is niet bevestigd.';root.append(add('p','Statusbestand ontbreekt of is onbereikbaar.'))}
})();
