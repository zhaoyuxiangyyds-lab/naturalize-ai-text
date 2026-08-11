# Platform Observation Schema

Use this schema for every detector observation. It is deliberately platform-neutral; do not coerce incompatible score meanings into one number.

```yaml
platform:
product:
url:
detector_threat_model: likelihood|curvature|classifier|stylometry|watermark|retrieval|opaque_ensemble|unknown
displayed_model_or_version:
displayed_update_date:
checked_at:
account_or_settings:
language:
genre:
input_format:
input_sha256:
input_length:
minimum_length_status: evaluable|too_short|unknown
raw_components:
  human_features:
  suspected_ai:
  ai_features:
raw_score_unit: percent_of_characters|percent_of_spans|probability|document_share|label_only|unknown
displayed_labels: []
highlighted_spans:
  - location:
    visible_label:
warnings: []
evidence_kind: visible_numeric|official_export|visible_label|screenshot_only|not_observed
screenshot_or_report_path:
captcha_or_quota:
rerun_index:
status: observed|blocked|contradictory|not_evaluable
interpretation:
```

## Platform-specific notes

### Tencent Zhuque

Record the visible component names exactly. A `human features` percentage, `suspected AI` percentage, and `AI features` percentage describe the platform's displayed classification of the submitted text or spans. They are not calibrated probabilities that a human or AI authored the document. The official page says the result is auxiliary and warns about false positives in common web fiction and school compositions.

Do not infer meaning from undocumented classes such as `danger` or `warning`. If the page exposes only a label or a colored segment, record only that visible fact.

### Turnitin

The current official FAQ limits AI writing detection to supported languages and eligible long-form prose and may suppress exact values in a low-percentage band. Mark Chinese or ineligible short text `not_evaluable`; do not treat a blank or asterisk as zero.

### GPTZero, ZeroGPT, Copyleaks, and Originality

Record the product's own score definition, language support, minimum length, model/version, and whether the number is a probability, document share, or vendor-specific category. Vendor accuracy claims are Grade A2 product claims, not independent validation. Do not average their percentages.

## Evidence rules

- A DOM or screenshot is evidence of what a user could see at a time; it is not evidence of hidden calibration.
- A downloaded official report is stronger than a manually copied number, but still belongs to the named detector/version.
- Missing version, missing hash, or post-edit input means `not_validated` for the final text.
- A CAPTCHA or quota block is a recorded failure, not a score and not permission to bypass the site's controls.
