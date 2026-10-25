import assert from 'node:assert/strict';
import {eligibleNL, priority} from './contest-ranking.mjs';
const base = {category:'Reizen', value:4000, deadline:'2026-10-29', conditions:'18+, Nederland, gratis deelname',
  free:true, purchaseRequired:false, newsletterRequired:false, minutes:3, winners:1, entrants:null};
assert.equal(eligibleNL(base),true);
assert.equal(eligibleNL({...base,conditions:'Only US residents',eligibleFromNetherlands:false}),false);
assert.equal(eligibleNL({...base,conditions:'US residents only'}),false);
assert.equal(eligibleNL({...base,conditions:'Worldwide entrants welcome'}),true);
const now='2026-10-25';
const good=priority(base,now);
assert.ok(good.score>0);
assert.equal(good.oddsKnown,false);
assert.equal(priority({...base,deadline:'2026-10-26'},now).score>good.score,true);
assert.equal(priority({...base,newsletterRequired:true},now).score<good.score,true);
assert.equal(priority({...base,purchaseRequired:true},now).score,-999);
assert.equal(priority({...base,conditions:'UK only',eligibleCountries:['GB']},now).score,-999);
assert.equal(priority({...base,entrants:1000,winners:1},now).oddsKnown,true);
console.log('Winactie ranking checks passed.');
