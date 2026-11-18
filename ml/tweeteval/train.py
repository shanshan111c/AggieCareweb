#!/usr/bin/env python3
"""Train on official TweetEval emotion splits, not on verified college students.
The output is a guarded, non-clinical browser search hint only."""
import json, urllib.request
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support,roc_auc_score
R=Path(__file__).resolve().parents[2]
U="https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/emotion/"
def load(split):
    def get(path):
        with urllib.request.urlopen(U+path,timeout=60) as response:
            return response.read().decode("utf-8").splitlines()
    a=get(split+"_text.txt")
    b=get(split+"_labels.txt")
    assert len(a)==len(b)
    return a,np.array([int(v)==3 for v in b],dtype=np.int8) # sadness=3
def score(y,p,t):
    pred=p>=t
    pr,re,f1,_=precision_recall_fscore_support(y,pred,average="binary",zero_division=0)
    return {"precision":round(float(pr),4),"recall":round(float(re),4),"f1":round(float(f1),4),"predicted_positive":int(pred.sum())}
def sig(x):
    return 1/(1+np.exp(-np.clip(np.asarray(x).ravel(),-40,40)))
def main():
    xtr,ytr=load("train");xva,yva=load("val");xte,yte=load("test")
    assert len(xtr)>2500 and len(xva)>300 and len(xte)>1000
    vec=CountVectorizer(binary=True,lowercase=True,strip_accents="unicode",
        ngram_range=(1,2),max_features=4800,min_df=2)
    xx=vec.fit_transform(xtr)
    clf=LogisticRegression(solver="liblinear",class_weight="balanced",C=0.65,random_state=42,max_iter=350).fit(xx,ytr)
    coeff=clf.coef_[0].copy();coeff[np.abs(coeff)<0.05]=0.
    intercept=float(clf.intercept_[0])
    words={k:round(float(w),6) for k,w in zip(vec.get_feature_names_out(),coeff) if abs(w)>1e-10}
    pv=sig(vec.transform(xva)@coeff+intercept)
    viable=[(float(t),score(yva,pv,float(t))) for t in np.arange(.55,.995,.005)]
    viable=[(t,m) for t,m in viable if m["precision"]>=.74 and m["recall"]>=.08]
    threshold,vm=max(viable,key=lambda x:(x[1]["recall"],x[1]["f1"])) if viable else (1.01,score(yva,pv,1.01))
    pt=sig(vec.transform(xte)@coeff+intercept)
    tm=score(yte,pt,threshold)
    tm["roc_auc"]=round(float(roc_auc_score(yte,pt)),4)
    enabled=bool(threshold<1 and tm["precision"]>=.70 and tm["recall"]>=.05)
    if not enabled: threshold=1.01
    baseline={}
    g=R/"models/goemotions-affect-v1.json"
    if g.exists():
        prev=json.loads(g.read_text())
        old=CountVectorizer(binary=True,ngram_range=(1,2),strip_accents="unicode",
            vocabulary={k:i for i,k in enumerate(prev["weights"])})
        s=sig(old.transform(xte)@np.asarray(list(prev["weights"].values()))+float(prev["bias"]))
        baseline={"goemotions_roc_auc_for_tweeteval_sadness":round(float(roc_auc_score(yte,s)),4),
                  "warning":"Different original labels; this is only a cross-domain diagnostic"}
    stats={"train":len(xtr),"validation":len(xva),"test":len(xte),
           "test_positive":int(yte.sum()),"sadness_label_index":3,
           "train_domain":"TweetEval social-media posts, no verified student ages or US residency",
           "validation_metrics":vm,"test_metrics":tm,
           "decision_threshold":round(float(threshold),4),"enabled":enabled,
           "terms":len(words),"cross_domain_baseline":baseline}
    print("TRAINING_STATS",json.dumps(stats,sort_keys=True),flush=True)
    model={"version":1,"enabled":enabled,"threshold":round(float(threshold),4),
           "bias":round(intercept,6),"weights":words}
    (R/"models").mkdir(exist_ok=True)
    (R/"models/tweeteval-sadness-v1.json").write_text(json.dumps(model,separators=(",",":"))+"\n")
    js=r"""/* Non-clinical, local-only TweetEval sadness language hint */
(function(root) {
"use strict";
const M=__MODEL__;
const BLOCK=/\b(?:kill\s+myself|want\s+to\s+die|suicid(?:e|al)|self\s*harm|hurt\s+myself|hurt\s+someone|assault|abuse|harass|stalk|rape|threat|hungry|food|pantry|groceries|rent|housing|homeless|condoms?|helmet|fever|vomit|nausea|dizzy|doctor|nurse|clinic|injur(?:y|ed)|stomach|breathing\s+trouble)\b/i;
const NEG=/\b(?:don't|dont|do\s+not|never)\s+(?:feel|feel\s+bad|be|am)\b|\bfeel\s+bad\s+(?:for|about|at)\b/i;
const FIRST=/(?:^|\s)(?:i|i'm|im|i\s+am|my)\b/i;
const AFFECT=/\b(?:feel(?:ing)?|felt|sad|lonely|overwhelmed|stressed|stressing|struggling|crying|depressed|anxious|scared|worried|miserable|hopeless|burn(?:ed|t)\s+out|crashing\s+out|spiraling|freaking\s+out|can't\s+cope|cant\s+cope|rough\s+time)\b/i;
root.__aggieTweetAffectHint=function(query) {
 if(!M.enabled || typeof query!=="string" || query.length>200 ||
    !/^[\x00-\x7f]*$/.test(query)||!FIRST.test(query)||
    !AFFECT.test(query)||BLOCK.test(query)||NEG.test(query)) return null;
 const t=query.normalize("NFKD").toLowerCase().match(/[a-z0-9_]{2,}/g)||[];
 const features=new Set(t);for(let i=0;i+1<t.length;i++)features.add(t[i]+" "+t[i+1]);
 let value=M.bias;for(const word of features)if(Object.prototype.hasOwnProperty.call(M.weights,word))value+=M.weights[word];
 const p=1/(1+Math.exp(-Math.max(-40,Math.min(40,value))));
 return p>=M.threshold?[{id:"counseling",score:75}]:null;
};
})(typeof window!=="undefined"?window:globalThis);
""".replace("__MODEL__",json.dumps(model,separators=(",",":")))
    (R/"docs/tweeteval-affect.js").write_text(js)
    (R/"tweeteval-affect.js").write_text(js)
    note=f"""# TweetEval sadness-language benchmark (non-clinical)

TweetEval emotion dataset: https://github.com/cardiffnlp/tweeteval

This is **social-media language, not verified American university student data**.
Labels: anger(0), joy(1), optimism(2), sadness(3). Model: binary unigram/bigram logistic regression for sadness versus other three labels. Uses official train, validation and untouched test splits; threshold chosen by validation; test provides a release gate.

| Metric | Value |
|---|---|
| Train / validation / test | {len(xtr)} / {len(xva)} / {len(xte)} |
| Held-out test ROC-AUC | {tm["roc_auc"]} |
| Held-out test precision | {tm["precision"]} |
| Held-out test recall | {tm["recall"]} |
| Held-out test F1 | {tm["f1"]} |
| Validation precision | {vm["precision"]} |
| Validation recall | {vm["recall"]} |
| Model enabled | {enabled} |
| Threshold | {threshold:.4f} |
| Features | {len(words)} |

No raw tweets copied to the repo; only fitted features, coefficients, and aggregate results. **Some TweetEval component tasks and the original platform have reuse restrictions.** The source README requests checking those terms. Emotions are not clinical diagnoses, intent to seek help, or suicide risk indicators. The browser hint is only a conservative optional route and cannot override concrete needs. The GoEmotions cross-domain number in training logs is not a directly comparable task benchmark.
"""
    (R/"docs/TWEETEVAL_EVALUATION.md").write_text(note)
if __name__=="__main__": main()
