import { readFileSync } from "node:fs";
import { aggieColloquialRoute } from "../src/colloquial-intent.mjs";
const cases=JSON.parse(readFileSync(new URL("../data/help-query-benchmarks.json",import.meta.url),"utf8"));
let failed=0;
for(const {query,expected_ids} of cases){
  const actual=aggieColloquialRoute(query)?.map(x=>x.id)??null;
  if(JSON.stringify(actual)!==JSON.stringify(expected_ids)){
    console.error("FAIL",JSON.stringify(query),{expected_ids,actual});failed++;
  }
}
console.log(`AggieCare colloquial intents: ${cases.length-failed}/${cases.length} passed`);
if(failed)process.exitCode=1;
