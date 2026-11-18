# US campus-language study notes

## Actual model data

[Cardiff NLP TweetEval emotion](https://github.com/cardiffnlp/tweeteval) provides original tweet text plus anger/joy/optimism/sadness labels with fixed official train/validation/test splits. This model **does not** know that participants are American or university students. We only train a small optional English sadness-language search hint, never a clinical risk score. Data are fetched in CI and not redistributed.

## Confirmed American-university-origin slang resources (not trained on)

- [University of Kentucky UKY Slang Collection Project](https://uknowledge.uky.edu/lewis-honor-data/1/): original college student recordings and written language. Machine-learning training and redistribution permissions not established.
- [Ohio State University Slang Journals](https://cfs.osu.edu/archives/collections/slang-journals): over 1,840 entries. Full collection must be requested by email from the Center for Folklore Studies.
- [Georgetown University GUM](https://gucorpling.org/gum/): multi-genre corpus annotated by students; not a dedicated help-seeking student language corpus, some subcorpora have different licenses.

No university-origin text was copied or used for fitting here.

## Student-oriented domain tests

`data/us-campus-slang-regression.json` contains **29 synthesized, researcher-authored examples** describing slang and help-resource confusions. They are not quotes from actual students. We check emotional overwhelm vs studying frustration, broken technology, food insecurity, physical illness and explicit emergencies. Model output cannot override specific campus-resource or safety rules.

## Release gate

The TweetEval model is trained on the official source splits; validation chooses a conservative threshold; held-out test provides independent precision/recall metrics. If quality thresholds fail, the optional model automatically disables itself. The authored campus slang rules can still be deployed separately after complete browser regressions. No user queries or student mental-health records are collected.
