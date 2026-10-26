import assert from "node:assert/strict";
import {selectActionable} from "./action-queue.mjs";
const now=new Date("2026-10-26T07:00:00Z");
const date="2026-10-26";
const good={id:"c1",title:"Win geld",organizer:"Bank",prize:"€5.000",category:"Geld",
  deadline:"2026-10-27",startsAt:"2026-10-01",
  verifiedAt:"2026-10-25T07:00:00Z",sourceUrl:"https://example.com/contest",
  termsUrl:"https://example.com/terms",free:true,purchaseRequired:false,
  conditions:"Nederland, 18+",evidence:"Officiële voorwaarden bekeken",value:5000};
const expired={...good,id:"c2",deadline:"2026-10-25"};
const rejected={...good,id:"c3",conditions:"US only",eligibleFromNetherlands:false};
const stale={...good,id:"c4",verifiedAt:"2026-10-01T07:00:00Z"};
const beforeStart={...good,id:"c5",startsAt:"2026-11-01"};
const requiresBuy={...good,id:"c6",purchaseRequired:true};
const sample={title:"Sample Sale Herenkleding",startDate:"2026-10-29",endDate:"2026-10-31",
 url:"https://example.com/sale",city:"Rotterdam",priority:80,
 lastSeenAt:"2026-10-25T09:00:00Z",sizes:"XL niet bevestigd"};
const result=selectActionable([good,expired,rejected,stale,beforeStart,requiresBuy],[sample],date,now);
assert.equal(result.length,2);
assert.ok(result.some(x=>x.kind==="contest"));
assert.ok(result.some(x=>x.kind==="sample"));
assert.equal(result.find(x=>x.kind==="contest").remaining,1);
assert.equal(result.find(x=>x.kind==="sample").location,"Rotterdam");
assert.equal(selectActionable([good],[],date,now,0).length,0);
assert.equal(selectActionable([{...good,free:false}],[],date,now).length,0);
assert.equal(selectActionable([],[{...sample,lastSeenAt:"2026-08-01T09:00:00Z"}],date,now).length,0);
console.log("Deadline action queue checks passed.");
