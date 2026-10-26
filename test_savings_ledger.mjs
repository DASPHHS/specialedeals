import assert from "node:assert/strict";
import {normalizeEntry,addSavings,totalSaved} from "./savings-ledger.mjs";
const today="2026-10-26";
const entry={id:"one",date:today,description:"Koffiebonen besteld",
 category:"Verzorging",usualPrice:40,paidPrice:29.95,confirmed:true};
const result=addSavings([],entry,today);
assert.equal(result.added,true);
assert.equal(result.entries[0].savedEUR,10.05);
assert.equal(totalSaved(result.entries),10.05);
assert.equal(addSavings(result.entries,{...entry,id:"another"},today).added,false);
assert.equal(normalizeEntry({...entry,confirmed:false},today),null);
assert.equal(normalizeEntry({...entry,paidPrice:41},today),null);
assert.equal(normalizeEntry({...entry,paidPrice:""},today),null);
assert.equal(normalizeEntry({...entry,usualPrice:""},today),null);
assert.equal(normalizeEntry({...entry,date:"2026-10-27"},today),null);
assert.equal(normalizeEntry({...entry,category:"Andere"},today),null);
assert.equal(totalSaved([...result.entries,{savedEUR:5.10}]),15.15);
console.log("Private confirmed savings ledger checks passed.");
