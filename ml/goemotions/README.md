# AggieCare experimental emotion-model enhancement

This is a conservative **emotion-language** enhancement, not an emergency risk detector. Training fetches Google's official GoEmotions filtered dataset: 43,410 train / 5,426 dev / 5,427 test. Five original emotion labels (sadness, grief, fear, nervousness, disappointment) become the weak binary training target "negative affect in Reddit". This target is NOT synonymous with psychological distress or help seeking.

## Intended behaviors
- Keep existing hand-curated crisis and campus-resource rules at highest priority.
- Only consider the trained hint for English, first-person, explicit affect context.
- Reject requests about concrete needs (food, medical issues, safety, supplies), idioms, or negated affect, and never infer danger or severity from ML.
- Route optional positive learned signals to the **general UC Davis counseling information card**, not a clinical diagnosis.
- Never collect, store or transmit user-entered queries or location data for this model.
- Continue using rule-based multilingual routing (no multilingual claims from English-only training).

## Evaluation
Training job writes `docs/GOEMOTIONS_EVALUATION.md` with held-out test set metrics and automatic validation cutoff. If confidence or performance gates fail, the learned hint disables itself automatically. Synthetic local regression and real-browser checks must pass before publication.

## Source, limitations and attribution
[Google Research GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions), Demszky et al., ACL 2020. Source README warns about Reddit demographics, offensive-language filtering and annotator bias. It is **not** a clinical dataset, suicide-risk classifier, or a substitute for academic clinical review. Original comments are not redistributed.

## For future maintenance
The existing AggieCare site is an exported Next.js build. When original source becomes available, migrate this bridge into the original React app and rebuild rather than editing an exported chunk.
