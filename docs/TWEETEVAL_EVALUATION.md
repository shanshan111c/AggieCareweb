# TweetEval sadness-language benchmark (non-clinical)

TweetEval emotion dataset: https://github.com/cardiffnlp/tweeteval

This is **social-media language, not verified American university student data**.
Labels: anger(0), joy(1), optimism(2), sadness(3). Model: binary unigram/bigram logistic regression for sadness versus other three labels. Uses official train, validation and untouched test splits; threshold chosen by validation; test provides a release gate.

| Metric | Value |
|---|---|
| Train / validation / test | 3257 / 374 / 1421 |
| Held-out test ROC-AUC | 0.8344 |
| Held-out test precision | 0.8371 |
| Held-out test recall | 0.3901 |
| Held-out test F1 | 0.5321 |
| Validation precision | 0.7959 |
| Validation recall | 0.4382 |
| Model enabled | True |
| Threshold | 0.7200 |
| Features | 4094 |

No raw tweets copied to the repo; only fitted features, coefficients, and aggregate results. **Some TweetEval component tasks and the original platform have reuse restrictions.** The source README requests checking those terms. Emotions are not clinical diagnoses, intent to seek help, or suicide risk indicators. The browser hint is only a conservative optional route and cannot override concrete needs. The GoEmotions cross-domain number in training logs is not a directly comparable task benchmark.
