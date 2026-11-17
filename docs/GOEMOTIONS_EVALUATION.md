# GoEmotions affect hint training evaluation

**Training completed on official filtered GoEmotions splits** (Google Research).
The task is **not** crisis or clinical classification. Source: https://github.com/google-research/google-research/tree/master/goemotions

| Metric | Value |
|---|---|
| Train / dev / test | 43,410 / 5,426 / 5,427 |
| Positive labels | disappointment, fear, grief, nervousness, sadness |
| Held-out test ROC-AUC | 0.8291 |
| Held-out test precision | 0.7321 |
| Held-out test recall | 0.1062 |
| Held-out test F1 | 0.1855 |
| Validation precision | 0.7647 |
| Validation recall | 0.0973 |
| Decision threshold | 0.9900 |
| Features exported | 6,655 |
| Optional browser model enabled | True |

The feature is limited to English first-person affect queries with clear emotional
context, never overrides explicit emergency, health, food, safety, or housing needs,
and never sends a user's query to an external service. The original multilingual
rule-based search remains the default. Emotions in Reddit comments **do not**
measure health needs, suicidality, risk level, or clinical diagnosis.

Training examples are **not** copied into this repository. The original project
describes demographic, cultural, and annotator bias. See the original model card
and license before further distribution. Cite: Demszky et al., ACL 2020,
*GoEmotions: A Dataset of Fine-Grained Emotions*.
