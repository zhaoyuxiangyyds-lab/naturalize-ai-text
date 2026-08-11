# Quality Evaluation and Controlled Budget

## Quality scorecard

Use a genre-qualified blind reader where possible. Hide provenance, version labels, detector scores, and the desired outcome. Score each dimension from 1 to 5, but do not report false precision from a small ordinal sample.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Accuracy or source fidelity | Material error or unsupported claim | Mostly correct with local uncertainty | Every checkable claim is accurate and bounded |
| Logic or narrative continuity | Contradiction, broken causality, or viewpoint leak | Understandable with a local gap | Complete argument or scene causality |
| Clarity | Hard to parse at target level | Generally clear with minor friction | Precise and easy to follow |
| Genre fit | Wrong convention, register, or pacing | Usable but generic | Form, register, and pacing fit the task |
| Voice | Uniform, synthetic, or misplaced | Some distinct choices | Consistent and source-supported voice |
| Information value | Filler dominates | Mixed density | Every unit advances evidence, action, scene, or reflection |
| Concision | Repetitive or bloated | Minor redundancy | No removable repetition except functional recurrence |
| Surface correctness | Frequent grammar, spelling, or format defects | Minor defects | Clean grammar, spelling, reference, and formatting |

Report each reader's scores, median, range, and disagreements. Self-assessment is useful for a draft log but is not independent blind evidence.

## Hard gates

Reject a revision regardless of detector change if it causes:

- a factual, numerical, citation, quotation, attribution, definition, method, or scope error;
- altered causal direction, conclusion strength, chronology, viewpoint, character knowledge, or world rules;
- any known spelling or grammar error, unstable terminology, bad punctuation pair, or corrupted formatting;
- fabricated experience, source, evidence, uncertainty, emotion, identity, or author claim;
- hidden/control characters, homoglyphs, random punctuation, unrelated padding, or duplicated passages;
- missing required disclosure or a violation of the destination's integrity rules.

`validate_text.py` can detect several byte and Unicode hazards, but it cannot prove facts, continuity, spelling, or authorship. Those require a separate manual or source-backed check.

## Controlled-quality-budget rules

Enable Tier 2 only after the user permits a small tradeoff. Start with the best quality-preserving version and change one factor per candidate. Possible costs are reduced polish, visual symmetry, transition explicitness, rhetorical completeness, or local elegance. Never spend the budget on truth, logic, task-level clarity, grammar, spelling, terminology, continuity, disclosure, or source integrity.

Retain a candidate only when:

1. all hard gates pass;
2. the target genre remains readable without new ambiguity or rereading for essential information;
3. the quality change is described honestly, including when it is detector-motivated rather than reader-positive;
4. the mean or median blind quality change stays within the pre-registered budget;
5. no hard dimension declines; a soft dimension may decline by at most one minor rubric step only if the user agreed;
6. the detector effect meets a pre-registered material threshold and exceeds observed rerun noise;
7. the effect reproduces in comparable runs or independent tools when resources permit;
8. the exact final hash is tested before a result is claimed.

If no independent reader is available, label the result `self_review_only` and do not call it a validated quality improvement. If no valid detector output is available, label the candidate `insufficient_evidence` rather than infer success from a local style metric.

## Intervention catalog

### Usually quality-positive

- verified specifics instead of generic abstraction;
- content-led paragraph or scene order;
- removal of redundant transitions and summaries;
- calibrated certainty and source-backed limits;
- character-, speaker-, or domain-specific diction;
- varied sentence function where repetition is accidental;
- stable terminology and direct verbs.

### Potentially budgeted

- uneven paragraph lengths when content warrants it;
- limited key-term repetition instead of ornamental synonyms;
- a plain correct local phrase;
- a fragment or interruption in a genre that supports it;
- reduced signposting when the relation remains clear;
- a non-exhaustive close that preserves the required implication;
- a correct author-supplied roughness.

### Always reject

Typos, grammar faults, random synonyms, shuffled logic, fake anecdotes, fake citations, altered data, translation loops without verification, homoglyphs, zero-width characters, unusual whitespace, repeated corpus padding, and detector-score cherry picking.

## Reporting template

```yaml
variant:
intervention:
reader_facing_reason:
hard_gates_passed:
blind_review:
quality_delta_from_best:
detector_observations:
control_observations:
repeatability:
exact_final_hash_tested:
decision: keep|revert|insufficient_evidence
notes:
```

## Interpretation

Quality and detector results are separate axes. A lower score with worse prose is a failed revision. A good revision with a high detector score is still a good revision, and the detector result must be reported as a limitation rather than repaired with synthetic defects.
