# AggieCare colloquial help-query patch (2026-11-16)

## Incident
Query `shit I Feel bad` was tokenized into `shit`, `feel`, `bad`, producing unrelated results. For an ambiguous expression of distress, present **both** non-diagnostic entry points: UC Davis Counseling and SHCS Acute Care.

## Routing design
- Explicit self-harm, threat, assault, food, material needs and medical symptoms keep priority in the existing search engine.
- Vague expressions (including slang, Mandarin and Spanish) return mental-health and medical options without diagnosing the user.
- Clearly emotional expressions route to counseling; clearly physical ones route to acute care.
- Negation and common idioms are guarded against false positives.
- Empty/ambiguous queries do not trigger automatic emergency calls or share user searches. GitHub Pages runs this rule client-side.
- The patched production files are `docs/_next/static/chunks/app/page-ed393d88a196cbaa.js` and its root mirror. The canonical readable helper is in `src/colloquial-intent.mjs`.

## Reproducible checks
Run `node scripts/test-colloquial-intents.mjs`. This uses a **synthetic, curated** set of test phrases, not a scraped database of private users and not an ML model trained on personal crisis posts. The existing app is a static build, so no supervised model training has been run. This is an auditable rule patch with regression tests.

## Official UC Davis resource checks
- Crisis Consultation (530-752-0871, same-day request, after-hours prompts), 988 and RELATE to 741741: https://shcs.ucdavis.edu/crisis-care-and-urgent-help-resources
- Medical Acute Care / Advice Nurse (530-752-2349); posted acute-care charges and free same-day mental-health crisis appointments: https://shcs.ucdavis.edu/services/acute-crisis-care
- Counseling services and crisis appointments: https://shcs.ucdavis.edu/services/counseling-services
- Campus locations and hours: https://shcs.ucdavis.edu/locations-hours
- Food insecurity, meals, pantry: https://aggiecompass.ucdavis.edu/food-security

## Data quality
The app estimates open/closed from published schedules; it does not call a live-hours provider. User-facing text was changed to avoid claiming real-time verification. Local lists and hours may change: official source links remain authoritative.

## Scope and caveats
The runtime is an exported/minified Next.js build, not the complete editable source project. Future full-source exports must port `src/colloquial-intent.mjs` into the real source search code and regenerate the release bundle. Production UI E2E testing is separate from these pure-function regression checks.
