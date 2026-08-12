# Evidence Register

## Purpose

Research claims about detectors, writing patterns, repositories, and community techniques vary sharply in reliability. Store the claim and its boundary before adding any behavior to the skill.

## Grades

| Grade | Evidence | Permitted use |
|---|---|---|
| `A1` | Peer-reviewed primary study or official benchmark paper with identifiable corpus, metrics, and conditions | Supports a bounded scientific claim; retain population and setup limits |
| `A2` | Official detector documentation, visible UI, terms, changelog, or exported report | Supports what the product says or displayed on that date; not hidden internals or independent accuracy |
| `B` | Versioned, licensed, reproducible open-source implementation with code, model/data details, and rerun record | Supports implementation and local reproduction; performance remains setup-specific |
| `C` | Forum post, blog, video, vendor comparison, prompt recipe, or unreplicated anecdote | Hypothesis-generation only; must pass controlled forward tests before any local use |
| `D` | Deliberate errors, hidden characters, homoglyphs, padding, fake biography/evidence, watermark defeat, disclosure evasion, or quality-damaging obfuscation | Rejected; document only to enforce a prohibition |

Secondary surveys may organize a field but should point to primary evidence for performance claims.

## Required fields

```yaml
claim_id:
claim:
grade: A1|A2|B|C|D
source_title:
source_url:
authors_or_owner:
publication_or_version:
date_published:
date_checked:
language:
genre_or_domain:
generator_models:
detectors:
sample_size:
metric_and_threshold:
intervention:
quality_evaluation:
detector_effect:
replication:
known_limits:
status: accepted_bounded|experiment_candidate|rejected|expired
```

## Promotion rules

A claim may enter the permanent method only when:

1. its source and conditions are recorded;
2. it is not a Grade D technique;
3. the proposed edit has a content, evidence, voice, genre, or reader-facing rationale;
4. it passes all hard quality gates;
5. a Grade C or B lead is reproduced on complete texts, not fragments;
6. development results are not reused as holdout results;
7. the rule succeeds on untouched samples across the exact axes claimed;
8. failures and negative effects are retained and reported;
9. an integrated composition result is not used to claim that one surface feature caused the effect.

Platform-specific observations expire when the displayed detector version changes or after six months without a drift check, whichever comes first. An undocumented platform may require a shorter expiry.

## Repository review checklist

Before using GitHub code, record:

- repository owner, commit SHA, license, release date, and maintenance status;
- whether weights and data are available and legally usable;
- languages, domains, generators, text lengths, and train/test split;
- whether reported tests used seen or unseen generators;
- threshold and false-positive rate, not accuracy alone;
- preprocessing, tokenizer, reference model, and hardware requirements;
- whether the tool is a detector, obfuscator, paraphraser, watermark test, or dataset;
- whether the method damages meaning, readability, citations, formatting, or disclosure.

Do not execute an unreviewed repository against user text or install it into the skill merely because it claims to reduce an AI score.

## Community-claim protocol

Record forum and platform recipes verbatim as claims, not instructions. Reject them if they rely on random errors, fake experience, hidden characters, padding, uncontrolled translation, fixed surface quotas, or cherry-picked screenshots. A reader-positive process claim may be tested on a complete integrated candidate; a claim about one causal feature requires a one-factor ablation. A favorable run remains sample-specific until held-out replication.
