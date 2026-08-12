# Detector Science and Limits

Checked: 2026-08-12.

## Bottom line

AI-text detectors do not share one universal signal or score. Research systems and commercial tools may use token likelihood, probability curvature, learned embeddings, stylometry, discourse features, active watermarks, retrieval, provenance records, or opaque ensembles. Results depend on language, genre, length, generator, decoding, training distribution, threshold, formatting, editing, and detector version.

A detector can be useful as a noisy instrument in a controlled experiment. It cannot prove who wrote an individual text. A low score on one platform does not imply a low score elsewhere.

## Signal families

| Family | What it measures | Important boundary |
|---|---|---|
| Token likelihood, rank, entropy, or perplexity | Whether tokens are unusually probable under a reference model | Changes with language, domain, decoding, length, and reference-model fit; low-perplexity human prose can be flagged |
| Probability curvature | Likelihood of the original relative to meaning-preserving perturbations | Requires suitable scoring and perturbation models; model and language mismatch matter |
| Supervised classifiers or embeddings | Patterns learned from labeled human and generated corpora | Can learn collection artifacts and lose accuracy on unseen domains, languages, or generators |
| Stylometry and discourse | Sentence, syntax, punctuation, vocabulary, coherence, and repetition distributions | These are correlational; formal and templated human writing may share them |
| Active watermark | A generator deliberately biases token choices and a keyed test detects the bias | Not universal and conceptually different from passive style detection; do not remove or defeat it |
| Retrieval or provenance | Text matches stored generations or provider-side records | Surface rewriting cannot guarantee avoidance; do not frame naturalization as defeating provenance |
| Opaque commercial ensemble | Undisclosed combination of models and features | A score or highlight cannot reveal causality; versions and thresholds may change silently or explicitly |

## Working design hypothesis

Treat after-the-fact surface perturbation as a weak and potentially self-defeating hypothesis. A document may retain its original content selection, discourse order, paragraph-function repetition, semantic transitions, and uniform information density after words or sentence lengths change. A supervised classifier may also learn patterns associated with common paraphrasers or formulaic humanization prompts. Conversely, random or quota-driven disruption can create a different but still repeated style while harming readers.

This does not establish what Tencent Zhuque or another proprietary detector measures. It justifies a safer design choice: generate from material and writing decisions at the outset, or reconstruct an existing draft from a locked semantic ledger and a new document route. Any detector effect remains sample-specific until tested.

## Primary research evidence

| Source | Supported finding | Skill consequence |
|---|---|---|
| Gehrmann, Strobelt, and Rush (2019), [GLTR](https://aclanthology.org/P19-3019/) | Token rank, probability, and entropy visualizations helped people identify generated text in a controlled study | Probability texture is a forensic clue, not a universal rewrite rule |
| Ippolito et al. (2020), [Automatic Detection of Generated Text is Easiest when Humans are Fooled](https://aclanthology.org/2020.acl-main.164/) | Humans and automatic classifiers used different cues; length and decoding affected detection | Keep human quality review separate from machine scores; test full real-length texts |
| Mitchell et al. (2023), [DetectGPT](https://proceedings.mlr.press/v202/mitchell23a.html) | Probability curvature worked strongly in a particular white-box, domain-specific setup | Record scoring model, perturbation model, domain, and length; do not generalize to Chinese or closed models |
| Kirchenbauer et al. (2023), [A Watermark for Large Language Models](https://proceedings.mlr.press/v202/kirchenbauer23a.html) | Active token-selection watermarking enables a keyed statistical test | Keep watermark removal outside the skill's scope |
| Sadasivan et al. (2023), [Can AI-Generated Text be Reliably Detected?](https://arxiv.org/abs/2303.11156) | Paraphrasing degraded several detectors with a measured quality tradeoff; detection has theoretical limits as distributions converge | Use uncertainty and quality stop rules; do not install paraphrase loops |
| Krishna et al. (2023), [Paraphrasing evades detectors, but retrieval is an effective defense](https://arxiv.org/abs/2303.13408) | Passive detector results changed under a specific paraphraser, while provider-side retrieval remained effective | Separate passive classification from provenance; document setup-specific numbers only |
| Liang et al. (2023), [GPT detectors are biased against non-native English writers](https://doi.org/10.1016/j.patter.2023.100779) | Seven detectors had high false positives on a small corpus of English essays by non-native writers | Use matched human controls; do not transfer this result to Chinese without direct evidence |
| Weber-Wulff et al. (2023), [Testing of detection tools for AI-generated text](https://doi.org/10.1007/s40979-023-00146-z) | Tested tools were not accurate or reliable enough for definitive judgments; obfuscation worsened performance | Retain contradictions and failures; never use a score as adjudication |
| Macko et al. (2023), [MULTITuDE](https://aclanthology.org/2023.emnlp-main.616/) | A 74,081-text, 11-language benchmark including Chinese showed weaker cross-language generalization than same-language performance | Validate Chinese directly; do not import English thresholds or edit recipes |
| Wang et al. (2024), [M4GT-Bench](https://aclanthology.org/2024.acl-long.218/) | Black-box detectors generally benefited from matching domains and generators; mixed authorship is distinct | Use domain/generator holdouts and preserve mixed provenance |
| Dugan et al. (2024), [RAID](https://aclanthology.org/2024.acl-long.674/) | Six-million-plus generations showed sensitivity to attacks, sampling, repetition penalties, unseen generators, and thresholds | Store detector threshold/version and matched human false-positive behavior |
| Macko et al. (2024), [Multilingual authorship obfuscation](https://aclanthology.org/2024.findings-emnlp.369/) | Many obfuscations changed detector results, while several damaged readability or even language | Typos, homoglyphs, translation loops, and quality damage are hard failures |

Use Wu et al. (2025), [A Survey on LLM-Generated Text Detection](https://doi.org/10.1162/coli_a_00549), as a taxonomy source, not as a substitute for the primary experiments above.

## Official Tencent Zhuque observations

Official page: [Tencent Zhuque AI Detection Assistant](https://matrix.tencent.com/ai-detect/), checked 2026-08-12. The page displayed text-model update date `2026-07-21` and benchmark-data update date `2026-06-30`.

Tencent describes an ensemble involving text detection, feature extraction, semantic understanding, and large-data analysis trained on generated and human data. This is a high-level product description, not enough information to reverse-engineer feature weights.

Tencent explicitly states that:

- accuracy cannot reach 100 percent and false positives remain possible;
- web fiction and elementary-school compositions with common expressions are examples prone to false positives;
- training data cannot represent every style or niche context;
- detectors may lag new generators and generation strategies;
- the same sample may change after algorithm updates;
- results are auxiliary and must not be the sole basis for review, punishment, truth, or copyright decisions.

The official page also publishes benchmark and overall-accuracy marketing claims. Do not transfer aggregate benchmark accuracy to an individual text, and do not treat the platform's component percentages as calibrated authorship probabilities without a published calibration method.

## Interpretation rules

1. Name the exact detector, date, displayed version, language, genre, length, and settings.
2. Describe the output with the platform's own visible labels and numbers.
3. Do not translate one product's `human`, `mixed`, `suspected`, or `AI` component into another product's categories.
4. Do not infer internal features from colored spans, CSS classes, or undocumented fields.
5. Compare against matched genuine human controls before interpreting a target score.
6. Separate false-positive behavior from target-text behavior.
7. A changed hash is a new test item. A historical score may be reported only with its original hash and date.
8. Generalization requires untouched holdouts across every claimed model, language, genre, and detector axis.

## What research does not justify

- a universal `human > 90%` promise;
- a blacklist of supposedly AI-only words;
- randomizing sentence lengths or punctuation to maximize a style metric;
- treating a descriptive style metric as a target distribution;
- claiming that whole-document reconstruction is a proven detector countermeasure before exact-platform evidence exists;
- deliberate errors or fake personal detail;
- pooling incompatible detector scores into an average;
- claiming that three samples or two genres establish model-wide portability;
- presenting successful evasion research as proof of quality, authorship, or durable real-world performance.
