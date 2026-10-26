/** Owner-entered private on-device saving confirmations.
 * A projection or coupon opportunity is NEVER automatically recorded.
 */
export function normalizeEntry(raw, todayISO){
 const date=String(raw.date||"");
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date)|| date>todayISO || date<"2000-01-01")
   return null;
 const description=String(raw.description||"").trim();
 const category=String(raw.category||"");
 const allowed=["Internet & tv","Mobiel","Energie","Verzorging","Premiumproducten","Overig"];
 if(!description||description.length>100||!allowed.includes(category))return null;
 const before=Number(raw.usualPrice),paid=Number(raw.paidPrice);
 if(![before,paid].every(x=>Number.isFinite(x)&&x>=0&&x<=100000))return null;
 // Explicit proof of the user's own actual receipt or bill, not an untested idea.
 if(raw.confirmed!==true||before<=paid)return null;
 const amount=Math.round((before-paid)*100)/100;
 return {id:String(raw.id||""),date,description,category,
   usualPrice:Math.round(before*100)/100,paidPrice:Math.round(paid*100)/100,
   savedEUR:amount,confirmation:"self_reported",isProjected:false};
}
export function addSavings(entries,raw,todayISO){
 const item=normalizeEntry(raw,todayISO);
 if(!item)return {entries,added:false,reason:"invalid"};
 const dupe=entries.some(x=>x.date===item.date &&
   String(x.description).toLocaleLowerCase("nl-NL")===item.description.toLocaleLowerCase("nl-NL") &&
   x.usualPrice===item.usualPrice && x.paidPrice===item.paidPrice);
 if(dupe)return {entries,added:false,reason:"duplicate"};
 return {entries:[...entries,item].slice(-100),added:true,reason:"ok"};
}
export function totalSaved(entries){
 return Math.round(entries.reduce((total,row)=>total+(Number(row.savedEUR)||0),0)*100)/100;
}
