# Platform and Repository Notes

Checked: 2026-08-11. These notes record public claims and research leads, not bypass instructions.

## Platform boundaries

| Platform | Publicly stated or visible boundary | Evidence status for Chinese experiments |
|---|---|---|
| Tencent Zhuque | Describes an ensemble of text detection, feature extraction, semantic analysis, and large-data training; official page warns of false positives, model updates, and common-expression genres. Visible output may include human/suspected-AI/AI feature shares. | `A2` for page behavior and warnings; exact Chinese accuracy and calibration not independently established |
| GPTZero | Describes document/sentence classification and segment highlighting; acknowledges false positives/negatives and stronger reliability on longer text, with training dominated by adult English prose. | `A2` for product claims; Chinese is exploratory unless a current language-specific report is available |
| Turnitin | Current FAQ limits AI-writing detection to supported languages and eligible long-form prose; low percentages may be suppressed rather than shown exactly. | `A2`; Chinese short fiction is `not_evaluable` under the documented limits |
| Copyleaks | Vendor describes language modeling, deep learning, and linguistic/statistical features; claims broad multilingual support and publishes a vendor test methodology. | `A2` for support and methodology; vendor English aggregate accuracy is not a Chinese holdout result |
| Originality | Defines AI score as a prediction/probability-like product metric and publishes a multilingual model release and vendor benchmark. | `A2`; do not treat aggregate Chinese vendor figures as genre-specific calibration |
| ZeroGPT | Describes a multi-stage classifier using token patterns, burstiness, entropy, and highlighting; language and accuracy claims lack independently auditable per-language confusion matrices. | `A2` for product description; exploratory only |

Do not average percentages across these products. Their units may be probability, document share, span share, confidence category, or an opaque product metric.

## Open-source research leads

Use repositories to understand detector families or reproduce a local baseline, not to promise platform portability. Pin a commit and inspect license, data provenance, model access, preprocessing, and language coverage before running code.

| Project | Family | Bounded use |
|---|---|---|
| [GLTR](https://github.com/HendrikStrobelt/detecting-fake-text) | token rank/probability visualization | Explain a statistical cue in an old GPT-2 setup |
| [HC3](https://github.com/Hello-SimpleAI/chatgpt-comparison-detection) | bilingual human/ChatGPT corpus and classifiers | Study matched Chinese/English data; do not treat early QA data as a 2026 fiction benchmark |
| [DetectGPT](https://github.com/eric-mitchell/detect-gpt) | probability curvature | Research white-box scoring assumptions |
| [Fast-DetectGPT](https://github.com/baoguangsheng/fast-detect-gpt) | efficient conditional curvature | Compare computation and model mismatch locally |
| [DetectLLM](https://github.com/mbzuai-nlp/DetectLLM) | rank/perturbation baselines | Separate fast rank methods from perturbation methods |
| [Binoculars](https://github.com/ahans30/Binoculars) | cross-model perplexity ratio | Recalibrate by language; repository warns against blind fixed thresholds |
| [Ghostbuster](https://github.com/vivek3141/ghostbuster) | feature search over weaker language models | Note its documented short/non-English/domain-outside limits |
| [RADAR](https://github.com/IBM/RADAR) | adversarially trained detector | Study robustness training, not text obfuscation instructions |
| [M4](https://github.com/mbzuai-nlp/M4) | multilingual/multidomain/multigenerator benchmark | Design generator and domain holdouts |
| [RAID](https://github.com/liamdugan/raid) | large robust detector benchmark | Evaluate detector drift and attack sensitivity; do not use it as a rewrite engine |

These are `B` research leads only after a pinned, reproducible local run. A repository README or forum recipe is not evidence that a prose edit will transfer to a commercial platform.

## Community and forum claims

Claims such as “raise burstiness,” “avoid AI words,” “add typos,” “translate twice,” or “randomize punctuation” are `C` hypotheses at best and `D` when they damage text or conceal provenance. Convert a permissible claim into a preregistered, one-factor, quality-gated experiment. Retain negative results and stop when the effect is single-platform, unstable, or quality-negative.
