#!/usr/bin/env python3
"""Train a non-clinical negative-affect *search hint* on official GoEmotions splits.

Never treat a GoEmotions label as a suicide-risk label or medical diagnosis.
All data stays on the CI runner; only coefficients and aggregate metrics ship.
"""
from __future__ import annotations
import io
import json
import math
import os
import re
import urllib.request
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data/"
EMOTIONS = {9:"disappointment", 14:"fear", 16:"grief", 19:"nervousness", 25:"sadness"}
SEED = 42

def load(name):
    with urllib.request.urlopen(BASE + name + ".tsv", timeout=50) as response:
        raw = response.read().decode("utf-8")
    texts, binary = [], []
    for line in io.StringIO(raw):
        columns = line.rstrip("\n").split("\t")
        if len(columns) < 2:
            continue
        labels = {int(t) for t in columns[1].split(",") if t}
        texts.append(columns[0])
        binary.append(int(bool(labels & EMOTIONS.keys())))
    return texts, np.asarray(binary, dtype=np.int8)

def metric(y, p, threshold):
    predicted = p >= threshold
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, predicted, average="binary", zero_division=0
    )
    return {"precision":round(float(precision),4),
            "recall":round(float(recall),4),
            "f1":round(float(f1),4),
            "predicted_positive":int(predicted.sum())}

def main():
    X_train, y_train = load("train")
    X_dev, y_dev = load("dev")
    X_test, y_test = load("test")
    print("SPLITS", len(X_train), len(X_dev), len(X_test), flush=True)
    assert (len(X_train),len(X_dev),len(X_test)) == (43410,5426,5427)
    vectorizer = CountVectorizer(binary=True, lowercase=True,
                                 strip_accents="unicode", ngram_range=(1,2),
                                 max_features=7000, min_df=4)
    xx_train = vectorizer.fit_transform(X_train)
    clf = LogisticRegression(solver="liblinear", random_state=SEED,
                             class_weight="balanced", max_iter=250, C=0.7)
    clf.fit(xx_train, y_train)
    # Small, auditable, first-party model parameter file; no user comments.
    coef = clf.coef_.ravel().copy()
    coef[np.abs(coef)<0.05] = 0
    used = np.flatnonzero(coef)
    raw_weights = {vectorizer.get_feature_names_out()[i]: round(float(coef[i]),6) for i in used}
    weights = {term:w for term,w in raw_weights.items() if w != 0}
    bias = float(clf.intercept_[0])
    def predict(texts):
        z = vectorizer.transform(texts) @ coef + bias
        return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(z).ravel(),-40,40)))
    dev_scores = predict(X_dev)
    # Train and validation are used to fit/select the cutoff. Test is held out.
    candidates = np.arange(0.6,0.995,0.005)
    choices = [(float(t),metric(y_dev,dev_scores,float(t))) for t in candidates]
    qualified = [(t,m) for t,m in choices if m["precision"]>=0.72 and m["recall"]>=0.02]
    if qualified:
        threshold, val_m = max(qualified,key=lambda z:(z[1]["recall"],z[1]["f1"]))
        enabled = True
    else:
        threshold, val_m, enabled = 1.01, metric(y_dev,dev_scores,1.01), False
    test_scores = predict(X_test)
    test_m = metric(y_test,test_scores,threshold)
    test_m["roc_auc"] = round(float(roc_auc_score(y_test,test_scores)),4)
    # Additional release guard: a model trained on Reddit must not be a
    # source of broad false-positive campus support recommendations.
    enabled = bool(enabled and test_m["precision"] >= 0.68)
    if not enabled: threshold = 1.01
    report = {
        "model_id":"aggiecare-goemotions-negative-affect-v1",
        "source":"google-research/google-research/goemotions",
        "source_file":"official filtered train/dev/test.tsv",
        "train_n":len(X_train), "dev_n":len(X_dev),"test_n":len(X_test),
        "train_positives":int(y_train.sum()),
        "positive_emotions":list(EMOTIONS.values()),
        "vectorizer":"binary unigram/bigram, lowercase, unicode accents stripped, max_features=7000,min_df=4",
        "model":"sklearn LogisticRegression(liblinear,C=.7,class_weight=balanced,seed=42)",
        "nonzero_features":len(weights), "threshold":round(float(threshold),5),
        "validation":val_m,"test":test_m,"enabled":enabled,
        "usage":"OPTIONAL non-clinical English first-person affect search hint only, not clinical triage"
    }
    print("EVALUATION",json.dumps(report,sort_keys=True),flush=True)
    model = {"version":1,"bias":round(bias,6),"threshold":round(float(threshold),5),
             "enabled":enabled,"weights":weights}
    (ROOT/"models").mkdir(exist_ok=True)
    (ROOT/"models/goemotions-affect-v1.json").write_text(
        json.dumps(model,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    # NOTE: The regular expression guard is essential; high confidence about
    # Reddit emotions does not imply knowledge of urgency or help-seeking intent.
    js = r"""/* AggieCare optional GoEmotions affect hint. No outbound API calls. */
(function(root) {
  "use strict";
  const MODEL = __AGGIE_MODEL__;
  const BLOCK = /\b(?:kill\s+myself|want\s+to\s+die|suicid(?:e|al)|self\s*harm|hurt\s+myself|hurt\s+someone|threat|assault|abuse|rape|harass|stalk|condoms?|pantry|grocer(?:y|ies)|hungr(?:y|y)|food|rent|homeless|fever|nausea|vomit|dizzy|injur(?:y|ed)|headache|stomach|doctor|clinic|medical|broken\s+(?:phone|app|code))\b/i;
  const IDIOM = /\b(?:don't|dont|do\s+not|never)\s+(?:feel\s+)?(?:bad|sad|awful|terrible)\b|\bfeel\s+bad\s+(?:for|about|at)\b|\b(?:i'm|im|i\s+am)\s+cooked\s+for\s+(?:finals|exams?|school|class)\b|\bsick\s+of\s+(?:school|class|studying)\b/i;
  const FIRST_PERSON = /(?:^|\s)(?:i|i'm|im|i\s+am|i've|ive|my)\b/i;
  const AFFECT_CONTEXT = /\b(?:feel|feeling|felt|struggling|overwhelmed|miserable|upset|scared|lonely|sad|anxious|hopeless|rough|horrible|terrible|awful|worried|drained|crying|stressed|breaking\s+down|going\s+through|can'?t\s+cope|not\s+okay|hard\s+time)\b/i;
  root.__aggieEmotionHint = function(query) {
    if (!MODEL.enabled || typeof query !== "string" || query.length > 180 ||
        !FIRST_PERSON.test(query) || !AFFECT_CONTEXT.test(query) ||
        BLOCK.test(query) || IDIOM.test(query) || /[^\u0000-\u007f]/.test(query)) return null;
    const normalized = query.normalize("NFKD").toLowerCase().replace(/[\u0300-\u036f]/g, "");
    const tokens = normalized.match(/[a-z0-9_]{2,}/g) || [];
    if (!tokens.length) return null;
    const features = new Set(tokens);
    for (let i = 0; i + 1 < tokens.length; i++) features.add(tokens[i] + " " + tokens[i + 1]);
    let logit = MODEL.bias;
    for (const word of features) if (Object.prototype.hasOwnProperty.call(MODEL.weights,word))
      logit += MODEL.weights[word];
    const probability = 1 / (1 + Math.exp(-Math.max(-40,Math.min(40,logit))));
    return probability >= MODEL.threshold ? [{id:"counseling",score:85}] : null;
  };
})(typeof window !== "undefined" ? window : globalThis);
""".replace("__AGGIE_MODEL__",json.dumps(model,ensure_ascii=False,separators=(",",":")))
    (ROOT/"docs/goemotions-affect.js").write_text(js,encoding="utf-8")
    (ROOT/"goemotions-affect.js").write_text(js,encoding="utf-8")
    note = f"""# GoEmotions affect hint training evaluation

**Training completed on official filtered GoEmotions splits** (Google Research).
The task is **not** crisis or clinical classification. Source: https://github.com/google-research/google-research/tree/master/goemotions

| Metric | Value |
|---|---|
| Train / dev / test | {len(X_train):,} / {len(X_dev):,} / {len(X_test):,} |
| Positive labels | {", ".join(EMOTIONS.values())} |
| Held-out test ROC-AUC | {test_m["roc_auc"]:.4f} |
| Held-out test precision | {test_m["precision"]:.4f} |
| Held-out test recall | {test_m["recall"]:.4f} |
| Held-out test F1 | {test_m["f1"]:.4f} |
| Validation precision | {val_m["precision"]:.4f} |
| Validation recall | {val_m["recall"]:.4f} |
| Decision threshold | {threshold:.4f} |
| Features exported | {len(weights):,} |
| Optional browser model enabled | {enabled} |

The feature is limited to English first-person affect queries with clear emotional
context, never overrides explicit emergency, health, food, safety, or housing needs,
and never sends a user's query to an external service. The original multilingual
rule-based search remains the default. Emotions in Reddit comments **do not**
measure health needs, suicidality, risk level, or clinical diagnosis.

Training examples are **not** copied into this repository. The original project
describes demographic, cultural, and annotator bias. See the original model card
and license before further distribution. Cite: Demszky et al., ACL 2020,
*GoEmotions: A Dataset of Fine-Grained Emotions*.
"""
    (ROOT/"docs/GOEMOTIONS_EVALUATION.md").write_text(note,encoding="utf-8")
    # Non-identifying sample expressions for a quick developer smoke review.
    probes = ["I'm feeling miserable","I'm having a really hard time","I feel defeated",
              "I feel so lost","I'm scared about everything","I'm struggling lately"]
    for example,proba in zip(probes,predict(probes)):
        print("SYNTHETIC_PROBE",repr(example),round(float(proba),4),flush=True)

if __name__=="__main__":
    main()
