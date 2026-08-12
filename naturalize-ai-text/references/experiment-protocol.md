# Detector Experiment Protocol

## 1. Pre-registration

Before looking at a new result, write:

```yaml
experiment_id:
registration_status: not_registered|registered|locked|amended
registered_at:
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
intervention_family:
composition_process: new_generation|full_reconstruction|local_edit|no_edit
anchor_basis: approved_corpus|source_draft|combined|none
execution_provenance_required: true|false
```

Set `registration_status: locked` and record `registered_at` before viewing a new detector result. An amendment creates a new registration state and must explain what changed; do not silently rewrite the original question or threshold.

Treat a user request such as `human > 90%` and `suspected_ai + ai < 10%` as a target for a named platform, exact text, displayed version, and date. It is not a universal definition of humanity.

## 2. Corpus design

Use complete, non-repeated text in the format the reader will see. Match controls by:

- language and script;
- genre and audience;
- approximate length and heading/paragraph format;
- publication or assessment setting;
- where possible, topic and level of formality.

Use rights-compatible controls. Human, AI-assisted, AI-generated, mixed, and unknown-origin controls are all usable when their provenance is recorded; do not call a control "human" merely because a detector labeled it so. For a new fiction task with no human draft, a human-origin control is a calibration sample, not evidence about the target author's identity. Keep control hashes separate from the target hash.

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

| Version | Meaning |
|---|---|
| `V0` | Frozen source draft for revision, or the first complete content-led draft for generation |
| `M0` | Semantic, evidence, voice, or story ledger; not detector input |
| `A0` | Provisional document route; not detector input |
| `C1` | Integrated blank-page generation or reconstruction candidate |
| `C1a+` | One registered ablation branched from `C1` when causal attribution matters |
| `F` | Exact quality-approved final text |

Compute SHA-256 over the exact bytes submitted. Do not normalize line endings, add a title, or change whitespace after hashing. If the submitted bytes change, the old detector observation is attached to the old version only.

### Clean forward-test provenance

When a result is meant to evaluate a skill change, freeze the skill directory before authoring and retain a manifest or tree hash. Record the exact skill path, the explicit invocation used, the fresh execution-context identifier, the skill and reference files actually read, the anchor hashes (if any), the contemporaneous composition-trace path and hash for generation or full reconstruction, the output hash, and every edit made after generation. A main task that authored or revised the skill and then wrote the sample is useful development evidence, but it is not an independent forward test. If any post-generation edit occurs, mark the sample as an authoring pass and preserve the pre-edit hash separately.

If an artifact manifest is stored inside the artifact directory it describes, freeze the payload first and explicitly exclude the manifest file from its own entries. Never place a manifest's own digest inside that same manifest; the bytes would become self-referential and the recorded value stale as soon as it is written. When the manifest itself needs integrity evidence, hash it from an external parent record after it is complete.

Create the canonical tree hash with the bundled script and retain its JSON output beside the request. Use `--output` rather than shell redirection. If the output is inside the hashed tree, the tool records and excludes that exact output path so repeated runs remain stable; use `--exclude` only for another explicitly named generated artifact:

```powershell
python scripts/hash_skill_tree.py . --format json --pretty --output ..\skill-tree.json
```

For `new_generation` or `full_reconstruction`, start the trace before prose, append each unit commitment before drafting that unit and its result immediately afterward, then reconcile and finalize it against the exact output:

```powershell
python scripts/composition_trace.py start --mode full_reconstruction --language zh-Hans --genre explanation -o trace.json
python scripts/composition_trace.py event trace.json --phase material_commit --unit-id M1 --decision "M1 is central"
python scripts/composition_trace.py event trace.json --phase section_commit --section-id S1 --unit-id M1 --state-before "Reader has the observation" --decision "Establish the mechanism"
# Draft only S1 here.
python scripts/composition_trace.py event trace.json --phase section_result --section-id S1 --unit-id M1 --state-change "Mechanism established"
# Repeat commit, draft, and result for the remaining functional units.
python scripts/composition_trace.py event trace.json --phase reconciliation --unit-id M1 --decision "Reconcile locked material" --state-change "All units accounted for"
python scripts/composition_trace.py finalize trace.json --text final.txt
python scripts/composition_trace.py validate trace.json --text final.txt --strict --pretty
```

The trace contains short, inspectable commitments rather than private reasoning. Its hash chain exposes later alteration, but timestamps and self-declared events do not independently prove contemporaneous intent or authorship.

Use this record for a clean forward sample:

```yaml
execution_provenance:
  skill_path:
  skill_tree_sha256:
  invocation: explicit|implicit|not_applicable
  fresh_context: true|false
  execution_context_id:
  files_read: []
  anchor_hashes: []
  composition_trace_path:
  composition_trace_sha256:
  output_sha256:
  post_generation_edits: []
  clean_forward_test: true|false
```

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
raw_components:
displayed_labels:
highlighted_spans:
warnings:
evidence_kind: visible_numeric|official_export|visible_label|screenshot_only|not_observed
screenshot_or_report_path:
captcha_or_quota:
rerun_index:
quality_before_detector:
notes:
execution_provenance:
```

`raw_component_scores` is accepted only as a legacy alias by the bundled validator; new records should use `raw_components`. For an observed numeric or label result, include the exact text hash, detector URL, rerun index, and a user-returned screenshot or official report path. A missing percentage stays missing.

Accept as a numeric observation only a value visibly shown in the page or an official export/report. A screenshot is evidence of what was displayed, not of hidden calibration. If a page returns a label without a percentage, record the label exactly. If a page shows components, record all components; do not infer a missing component. For percentages that are meant to partition 100, check the displayed sum within a documented rounding tolerance.

Never infer severity from CSS classes (`danger`, `warning`, and similar), DOM order, color, internal network fields, or source code unless the platform documents that mapping.

### User-submitted evidence workflow

1. Freeze the final bytes and compute the SHA-256 locally.
2. Give the exact text and named platform to the user; do not upload it automatically or bypass login, CAPTCHA, quota, or site controls.
3. Have the user submit it and return the visible result or screenshot.
4. Record the displayed fields exactly, attach the returned evidence path, and validate the record against the same hash.
5. If the user returns no valid numeric result, mark the observation `not_evaluable`; do not infer a reduction from local texture metrics.

## 5. Quality gate before detector review

Run deterministic checks and then blind human review without showing detector results. Record `quality.checks` for source integrity, facts and citations, logic or narrative continuity, language surface, genre and voice, and disclosure. Use `not_applicable` only when a dimension truly does not exist. Mark `quality.hard_gates` as `passed` only after every applicable check passes; a final or holdout record with `not_checked` cannot pass strict validation. Hard failures include:

- changed facts, citations, numbers, definitions, causal direction, scope, or chronology;
- broken narrative viewpoint, world rules, character knowledge, or continuity;
- any known typo, grammar fault, bad punctuation pair, unstable term, or formatting corruption;
- fabricated detail, experience, source, uncertainty, attribution, or identity;
- hidden/control characters, homoglyphs, random punctuation, duplicated text, or unrelated padding;
- missing required AI disclosure.

Do not use the detector score in the blind quality score. Report the number and provenance of readers, disagreement, and unresolved items. A self-score is not an independent blind review.

## 6. Integrated candidates, ablation, and acceptance

An ordinary `new_generation` or `full_reconstruction` candidate may integrate linked decisions about selection, structure, stance, voice, and language. Register the whole composition process as its intervention family and evaluate the complete text. Do not decompose normal writing into detector-directed serial edits.

If the question is which single method caused a score change, branch one ablation at a time from the frozen integrated candidate. Define a material effect using the named platform's resolution and observed rerun variation; do not assume a universal five-point threshold. Record `rerun_index` for every same-hash repeat and do not reuse an index for the same detector. One observed run is `single_observation`, never replication.

Retain a controlled variant only if:

1. every hard gate passes;
2. the target genre remains readable and correct;
3. every material change has a content, evidence, voice, genre, or reader-facing reason;
4. the result reproduces in at least one same-hash rerun when the platform permits;
5. no control or holdout evidence contradicts the proposed rule;
6. the exact final hash, not a near-final hash, is tested before claiming a result.

If results disagree across platforms, keep the disagreement. Do not optimize toward the lowest number by cycling through unregistered variants. A strict final or holdout record is valid only after `pre_registration` is locked, the composition process is identified, matched controls are recorded, hard gates are marked `passed`, and at least two required runs are present unless the platform made a rerun impossible and the record remains `single_observation`.

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

Retain and report CAPTCHA, quota exhaustion, login block, timeout, contradictory labels, missing percentages, detector update, and input-format failure. Stop when the next change has no content or reader-facing reason, quality fails the acceptance rules, a provenance or disclosure rule is at risk, or the platform forbids the test.

## 10. Final statement

Detector output is sensitive to language, genre, length, generator, detector version, threshold, and input construction. It cannot prove human authorship and cannot support a universal bypass guarantee.
