# Detector Experiment Protocol

## 1. Pre-registration

Before looking at a new result, write:

```yaml
experiment_id:
question:
target_metric:
material_effect_threshold:
quality_budget:
detectors:
languages:
genres:
sample_selection:
matched_control_rule:
rerun_rule:
stop_rule:
```

Treat a user request such as `human > 90%` and `suspected_ai + ai < 10%` as a target for a named platform, exact text, displayed version, and date. It is not a universal definition of humanity.

## 2. Corpus design

Use complete, non-repeated text in the format the reader will see. Match controls by:

- language and script;
- genre and audience;
- approximate length and heading/paragraph format;
- publication or assessment setting;
- where possible, topic and level of formality.

Use rights-compatible human controls. Record provenance and do not call a control "human" merely because a detector labeled it so. For a new fiction task with no human draft, the human control is a calibration sample, not evidence about the target author's identity.

Recommended split:

| Split | Purpose |
|---|---|
| `smoke` | Catch workflow and parser errors; no portability claim |
| `development` | Select at most one-factor candidates; do not reuse as holdout |
| `holdout` | Freeze the skill and test unseen prompts, samples, generators, domains, and lengths |
| `drift` | Recheck fixed sentinels after a detector/model update |

Minimum axes for a generalization claim are separate measurements, not pooled scores: Simplified Chinese and English; fiction, essay, explainer, and academic/technical writing; AI-only, source-assisted, mixed, and human controls; Codex/GPT plus other legitimately available model families; at least two permitted detectors.

## 3. Versioning and exact input

Save every variant as immutable bytes:

| Version | Allowed change |
|---|---|
| `V0` | Original draft or generated baseline |
| `V1` | Verified content/evidence or scene changes |
| `V2` | Structure only |
| `V3` | Stance, voice, and uncertainty only |
| `V4` | Sentence rhythm and surface only |
| `V5` | Integrated quality-preserving final |
| `V5a+` | One explicitly labeled controlled-quality-budget factor |

Compute SHA-256 over the exact bytes submitted. Do not normalize line endings, add a title, or change whitespace after hashing. If the submitted bytes change, the old detector observation is attached to the old version only.

## 4. Detector record

For each run, retain:

```yaml
experiment_id:
sample_id:
version:
text_sha256:
language:
genre:
length_units:
format:
provenance:
detector_name:
detector_url:
detector_threat_model:
displayed_model_or_version:
displayed_update_date:
settings:
observed_at:
raw_component_scores:
displayed_labels:
highlighted_spans:
warnings:
evidence_kind: visible_numeric|official_export|visible_label|screenshot_only|not_observed
screenshot_or_report_path:
captcha_or_quota:
quality_before_detector:
notes:
```

Accept as a numeric observation only a value visibly shown in the page or an official export/report. A screenshot is evidence of what was displayed, not of hidden calibration. If a page returns a label without a percentage, record the label exactly. If a page shows components, record all components; do not infer a missing component. For percentages that are meant to partition 100, check the displayed sum within a documented rounding tolerance.

Never infer severity from CSS classes (`danger`, `warning`, and similar), DOM order, color, internal network fields, or source code unless the platform documents that mapping.

## 5. Quality gate before detector review

Run deterministic checks and then blind human review without showing detector results. Hard failures include:

- changed facts, citations, numbers, definitions, causal direction, scope, or chronology;
- broken narrative viewpoint, world rules, character knowledge, or continuity;
- any known typo, grammar fault, bad punctuation pair, unstable term, or formatting corruption;
- fabricated detail, experience, source, uncertainty, attribution, or identity;
- hidden/control characters, homoglyphs, random punctuation, duplicated text, or unrelated padding;
- missing required AI disclosure.

Do not use the detector score in the blind quality score. Report the number and provenance of readers, disagreement, and unresolved items. A self-score is not an independent blind review.

## 6. Ablation and acceptance

Change one intervention family at a time. Define a material detector effect before testing. Unless a study provides a calibrated alternative, use an absolute score change of at least 5 points on a 0-100 scale or one lower displayed category, and require the change to exceed observed rerun variation. A one-run deterministic result is `single observation`, not replication.

Retain a controlled variant only if:

1. every hard gate passes;
2. the target genre remains readable and correct;
3. any soft quality loss is small, explicitly recorded, and within the agreed budget;
4. the effect reproduces in comparable runs or independent tools when resources permit;
5. no control or holdout evidence contradicts the proposed rule;
6. the exact final hash, not a near-final hash, is tested before claiming a result.

If results disagree across platforms, keep the disagreement. Do not optimize toward the lowest number by cycling through unregistered variants.

## 7. Matched-control interpretation

Report target and control together. A target that meets a threshold while genuine controls fail it is not evidence of a useful human criterion. A target that misses the threshold while controls also miss it may indicate poor calibration for that language/genre, not a writing defect. Do not degrade the target to compensate for a detector's false-positive behavior.

## 8. Generalization labels

Use one of these labels:

- `not_evaluable`: too short, blocked, missing exact input, or no valid output;
- `single_observation`: one exact run with no qualifying replication;
- `sample_level_replicated`: same sample and intervention reproduced under the preregistered rule;
- `portable_evidence`: held-out samples across every claimed axis meet the quality and replication criteria.

Never call a document-level observation a corpus result, and never call a corpus result proof of authorship.

## 9. Failure and stop reporting

Retain and report CAPTCHA, quota exhaustion, login block, timeout, contradictory labels, missing percentages, detector update, and input-format failure. Stop when the next change has no reader-facing benefit or reproducible effect, quality leaves the budget, a provenance/disclosure rule is at risk, or the platform forbids the test.

## 10. Final statement

Detector output is sensitive to language, genre, length, generator, detector version, threshold, and input construction. It cannot prove human authorship and cannot support a universal bypass guarantee.
