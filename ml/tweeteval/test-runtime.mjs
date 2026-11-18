import fs from "node:fs";import vm from "node:vm";import assert from "node:assert/strict";
const model=JSON.parse(fs.readFileSync("models/tweeteval-sadness-v1.json","utf8"));
const ctx={};vm.runInNewContext(fs.readFileSync("docs/tweeteval-affect.js","utf8"),ctx);
assert.equal(typeof ctx.__aggieTweetAffectHint,"function");
for(const q of ["I want to kill myself","I need free food","I need condoms","I feel nauseous","I need a doctor","I feel bad for him","I don't feel bad","I need housing","I'm hungry","My roommate threatened me","我心态崩了"]){
 assert.equal(ctx.__aggieTweetAffectHint(q),null,"Unsafe override "+q);
}
for(const q of ["I'm feeling sad","I'm stressed out","I feel lonely"]){
 const r=ctx.__aggieTweetAffectHint(q);assert.ok(r===null||r.length===1&&r[0].id==="counseling");
}
assert.ok(Object.keys(model.weights).length>100);
console.log("TweetEval runtime safeguards passed, enabled:",model.enabled);
