import fs from "node:fs";
import vm from "node:vm";
import assert from "node:assert/strict";
const js = fs.readFileSync("docs/goemotions-affect.js", "utf8");
const model = JSON.parse(fs.readFileSync("models/goemotions-affect-v1.json", "utf8"));
const context = vm.createContext({});
vm.runInContext(js, context);
assert.equal(typeof context.__aggieEmotionHint, "function");
const safeSkips = [
  "I need free food", "I don't feel bad", "I feel bad for him",
  "I want to kill myself", "I feel bad because I have a fever",
  "My ex threatened me", "I need condoms", "我心情很难受",
  "I'm cooked for finals", "i'm excited about my exam",
  "I need a doctor", "I feel dizzy", "I have no place to live"
];
for (const sentence of safeSkips)
  assert.equal(context.__aggieEmotionHint(sentence), null, "Unsafe override: "+sentence);
for (const sentence of ["I'm feeling miserable", "I'm having a really hard time", "I feel so lost"]) {
  const v = context.__aggieEmotionHint(sentence);
  assert.ok(v === null || Array.isArray(v));
  if (v) assert.deepEqual(Array.from(v, x => x.id), ["counseling"]);
}
assert.equal(model.version, 1);
assert.ok(Object.keys(model.weights).length > 150);
console.log("GoEmotions browser runtime safeguards:",safeSkips.length,"skip tests passed; emitted model enabled:",model.enabled);
