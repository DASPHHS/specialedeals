/* Pure, evidence-aware filters for the Speciale Deals discovery page.
   Browser + Node compatible. Never upgrades a candidate to a verified deal. */
(function (root, factory) {
  "use strict";
  const api=factory();
  if (typeof module==="object" && module.exports) module.exports=api;
  if (root) root.DealFilters=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const finite=n=>Number.isFinite(Number(n))?Number(n):0;
  function isVerifiedDeal(x,now=Date.now()){
    const age=now-Date.parse(x?.verifiedAt||"");
    return x?.kind==="deals"&&x.priceVerified===true&&
      finite(x.discountPercent)>=10&&Number.isFinite(age)&&
      age>=0&&age<=36*3600000;
  }
  function discount(x,now=Date.now()){
    return isVerifiedDeal(x,now)?finite(x.discountPercent):0;
  }
  function savings(x,now=Date.now()){
    return isVerifiedDeal(x,now)?Math.max(0,finite(x.savingsEUR)):0;
  }
  function daysLeft(x,now=Date.now()){
    const end=x?.endDate||x?.deadline||x?.dateEnd;
    if(typeof end!=="string"||!/^\d{4}-\d{2}-\d{2}$/.test(end))return null;
    const d=Date.parse(end+"T23:59:59");
    return Number.isFinite(d)?Math.ceil((d-now)/86400000):null;
  }
  function isOpportunity(x,now=Date.now()){
    if(isVerifiedDeal(x,now))return discount(x,now)>=20||savings(x,now)>=75;
    if(x?.kind==="contests"){
      const ends=daysLeft(x,now);
      return finite(x.prizeValueEUR)>=1000&&Boolean(x.verifiedAt)&&
        (ends===null||ends>=0);
    }
    // Sample sales are not automatically "verified purchase deals".
    return x?.kind==="sales"&&x.organizerVerified===true&&
      finite(x.score)>=90&&(daysLeft(x,now)===null||daysLeft(x,now)>=0);
  }
  function isRecent(x,now=Date.now()){
    const age=now-Date.parse(x?.discoveredAt||"");
    return Number.isFinite(age)&&age>=0&&age<=7*86400000;
  }
  function matchesLens(x,lens="all",now=Date.now()){
    const left=daysLeft(x,now);
    switch(lens){
      case "opportunities":return isOpportunity(x,now);
      case "discount20":return discount(x,now)>=20;
      case "ending":return left!==null&&left>=0&&left<=7;
      case "wishlist":return Array.isArray(x?.wishlistMatches)&&x.wishlistMatches.length>0;
      case "recent":return isRecent(x,now);
      default:return true;
    }
  }
  function compare(a,b,sort="rank",now=Date.now()){
    const score=x=>finite(x?.score);
    if(sort==="discount")return discount(b,now)-discount(a,now)||score(b)-score(a);
    if(sort==="saving")return savings(b,now)-savings(a,now)||score(b)-score(a);
    if(sort==="deadline"){
      const da=daysLeft(a,now),db=daysLeft(b,now);
      return (da===null?Infinity:da)-(db===null?Infinity:db)||score(b)-score(a);
    }
    if(sort==="fresh")return String(b.discoveredAt||"").localeCompare(String(a.discoveredAt||""));
    if(sort==="az")return String(a.title||"").localeCompare(String(b.title||""),"nl");
    return score(b)-score(a);
  }
  return {isVerifiedDeal,discount,savings,daysLeft,isOpportunity,isRecent,matchesLens,compare};
});
