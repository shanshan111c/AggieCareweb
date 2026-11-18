import { chromium } from "playwright";
const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
const page=await browser.newPage({locale:"en-US",viewport:{width:1440,height:900}});
const root="http://127.0.0.1:8765/AggieCareweb/";
try{
  await page.goto(root,{waitUntil:"networkidle",timeout:45000});
  const bridge=await page.evaluate(() => typeof window.__aggieEmotionHint);
  if(bridge!== "function")throw new Error("GoEmotions local inference JS failed to load");
  const noHijack=await page.evaluate(() => window.__aggieEmotionHint("I need free food"));
  if(noHijack!==null)throw new Error("Emotion model hijacks food requests");
  const box=page.locator("form.smart-search input");
  await box.waitFor({timeout:15000});
  const checks=[
    {query:"shit I Feel bad",contains:["Crisis Counseling","Acute Care Clinic"]},
    {query:"I feel like shit",contains:["Crisis Counseling","Acute Care Clinic"]},
    {query:"I feel dizzy and nauseous",contains:["Acute Care Clinic"]},
    {query:"I feel bad emotionally",contains:["Crisis Counseling"]},
    {query:"I need free food",contains:["AggieEats Food Truck"]},
    {query:"我心情很难受",contains:["Crisis Counseling"]},
    {query:"I\'m having a rough time",contains:["Crisis Counseling"]},
    {query:"我心态崩了",contains:["Crisis Counseling"]},
    {query:"I\'m crashing out",contains:["Crisis Counseling"]},
    {query:"I\'m burnt out",contains:["Crisis Counseling"]}
  ];
  for(const tc of checks){
    await box.fill(tc.query);
    await box.press("Enter");
    try { await page.waitForFunction((names)=>names.every(name=>document.body.innerText.includes(name)),tc.contains,{timeout:7000}); }
    catch(error){console.error("SEARCH RESULTS FOR",JSON.stringify(tc.query),(await page.locator("body").innerText()).slice(0,11000));throw error;}
    const content=await page.locator("body").innerText();
    if(!tc.contains.every(n=>content.includes(n))) throw new Error("Unexpected UI search output for "+tc.query);
    console.log("PASS",JSON.stringify(tc.query),"->",tc.contains.join(", "));
  }
}finally{await browser.close();}
