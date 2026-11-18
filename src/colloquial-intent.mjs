function aggieColloquialRoute(query) {
  const s=String(query||"").normalize("NFKC").toLowerCase()
    .replace(/[’‘]/g,"'").replace(/[^\p{L}\p{N}'\s-]/gu," ")
    .replace(/\s+/g," ").trim();
  if(!s)return null;
  // Guard against idioms, negations, explicit non-health needs and high-priority safety routes.
  if(/\b(?:i\s+)?(?:don't|dont|do not|never)\s+feel\s+(?:so\s+)?(?:bad|awful|terrible)\b/.test(s) ||
     /\b(?:feel|feeling)\s+bad\s+(?:for|about|at)\b/.test(s) ||
     /\bmy\s+(?:app|phone|laptop|website|code|game)\b/.test(s) ||
     /\b(?:im|i'm|i am)\s+cooked\s+for\s+(?:finals|exams?|class|school)\b/.test(s) ||
     /\bsick\s+of\s+(?:school|class|finals|studying|my\s+(?:boyfriend|girlfriend|partner))\b/.test(s) ||
     /\b(?:hungry|no\s+food|need\s+food|groceries|pantry|haven't\s+eaten|havent\s+eaten|can't\s+afford\s+food|cant\s+afford\s+food|need\s+condoms?|need\s+a\s+helmet)\b/.test(s) ||
     /\b(?:kill\s+myself|hurt\s+myself|self\s*harm|suicid(?:e|al)|want\s+to\s+die|rape|raped|assault|stalk(?:ing)?|harass(?:ment)?|abuse|threat(?:ened|ening)?)\b/.test(s) ||
     /自杀|自殺|想死|不想活|活不下去|自残|自殘|性侵|强奸|強姦|家暴|骚扰|騷擾|跟踪|跟蹤|暴力/.test(s))return null;
  const campusDistress=/\b(?:i(?:'m|m| am)\s+(?:(?:so|really|lowkey|fr|legit|completely)\s+)?(?:burn(?:ed|t)\s*out|stressed\s+(?:af|out)|crashing\s+out|freaking\s+out|losing\s+it|spiraling|emotionally\s+cooked|mentally\s+fried|barely\s+holding\s+on)|i(?:'m|m| am)\s+overwhelmed\s+(?:by|with)\s+(?:my\s+)?(?:classes?|finals?|exams?|homework|assignments?|school|college)|i\s+(?:(?:really|legit|honestly)\s+)?(?:can't|cant|cannot)\s+(?:stop\s+stressing|cope\s+anymore|deal\s+with\s+this\s+anymore|sleep\s+from\s+stress)|i(?:'m|m| am)\s+drowning\s+in\s+(?:my\s+)?(?:assignments?|schoolwork|homework)|i\s+feel\s+(?:mentally\s+fried|totally\s+burned\s+out))\b/i.test(s);
  const physical=/\b(?:fever|nausea|nauseous|vomit(?:ing)?|throwing\s+up|dizz(?:y|iness)|faint(?:ing)?|stomach(?:ache)?|headache|migraine|chest\s+pain|breathing\s+trouble|sore\s+throat|injured|injury|physically|physical\s+pain|sick|medical|body\s+ache|my\s+(?:head|stomach|back|chest)\s+hurts?)\b|身体|生病|发烧|發燒|头晕|頭暈|头痛|頭痛|胃|肚子|腹痛|恶心|噁心|想吐|胸痛|呼吸困难|呼吸困難/.test(s);
  const emotional=/\b(?:i\s+(?:am|feel)\s+sad|i'm\s+sad|i'm\s+(?:so\s+)?(?:lonely|anxious|depressed|overwhelmed)|i\s+(?:am\s+)?(?:panicking|crying)|can't\s+stop\s+crying|cant\s+stop\s+crying|can't\s+do\s+this\s+anymore|cant\s+do\s+this\s+anymore|can't\s+take\s+it\s+anymore|cant\s+take\s+it\s+anymore|mental\s+health\s+is\s+(?:bad|tanking)|emotionally|i\s+feel\s+(?:empty|hopeless|alone|depressed|anxious)|i'm\s+(?:so\s+)?cooked|im\s+(?:so\s+)?cooked|lowkey\s+(?:freaking\s+out|spiraling)|i(?:'m|m| am)\s+having\s+a\s+rough\s+time|i(?:'m|m| am)\s+having\s+a\s+hard\s+time\s+(?:emotionally|mentally)|i(?:'m|m| am)\s+(?:mentally\s+exhausted|spiraling|emotionally\s+drained|falling\s+apart|at\s+my\s+limit)|i\s+feel\s+(?:emotionally\s+drained|mentally\s+exhausted|like\s+i(?:'m|m| am)\s+falling\s+apart))\b|心态崩了|心態崩了|撑不住了|撐不住了|压力爆炸|壓力爆炸|心情|情绪|情緒|心理|崩溃|崩潰|焦虑|焦慮|抑郁|抑鬱|绷不住|繃不住|撑不下去|撐不下去|想哭|压力好大|壓力好大|心好累|我快疯了|我快瘋了/.test(s);
  const vague=/\b(?:i\s+(?:feel|am)\s+(?:so\s+|really\s+)?(?:bad|awful|terrible|not\s+(?:okay|ok|well|good))|i'm\s+(?:not\s+(?:okay|ok)|feeling\s+(?:bad|awful|terrible))|i\s+feel\s+like\s+(?:shit|crap|garbage)|i\s+feel\s+so\s+off|i\s+don't\s+feel\s+(?:good|okay|ok|well)|im\s+not\s+(?:okay|ok)|not\s+feeling\s+(?:good|okay|ok|well)|feeling\s+(?:like\s+)?(?:shit|crap|awful|terrible)|me\s+siento\s+(?:mal|fatal|horrible)|estoy\s+(?:mal|fatal))\b|我.{0,8}(?:好|很|太|有点|有點)?(?:难受|難受|不舒服)|(?:难受|難受)死了|状态很差|狀態很差|感觉不对劲|感覺不對勁/.test(s);
  if(!physical&&!emotional&&!campusDistress&&!vague)return null;
  if(physical&&(emotional||campusDistress))return[{id:"counseling",score:185},{id:"acute-care",score:180}];
  if(physical)return[{id:"acute-care",score:185}];
  if(emotional||campusDistress)return[{id:"counseling",score:185}];
  return[{id:"counseling",score:170},{id:"acute-care",score:155}];
}

export { aggieColloquialRoute };
