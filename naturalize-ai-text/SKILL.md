---
name: naturalize-ai-text
description: Naturalize AI-generated or heavily AI-assisted text across fiction, essays, academic and technical writing, reports, explainers, and speeches. Use when a user asks to humanize prose, reduce template-like or machine-like writing, lower an AI-detection score, compare revisions across detectors, or generate less formulaic prose. Preserve facts, citations, disclosure duties, genre constraints, and authentic author voice. Detector results are controlled observations, never proof of human authorship or a guaranteed bypass.
---

# Naturalize AI Text

## Contract

Improve the writing first. Treat a detector score as a volatile measurement from one instrument, not as authorship evidence and not as the definition of quality.

Use this priority order:

> source integrity > facts and citations > logic or narrative continuity > disclosure and genre fit > supported voice > clarity > surface polish > detector result

Never promise a universal pass, a stable score, or a specific human percentage. A user threshold such as `human > 90%` is a named detector's sample-level experimental criterion. Report `not achieved` when it is not achieved.

Never fabricate a biography, memory, source, quotation, datum, experiment, emotion, uncertainty, or human author. Never add typos, grammar faults, homoglyphs, hidden characters, random punctuation, unrelated padding, duplicated passages, or translation-loop damage. Do not remove or defeat a watermark or provider-side provenance mechanism.

## Load only the needed references

- Read [references/integrity-and-routing.md](references/integrity-and-routing.md) for every task.
- Read [references/genre-guides.md](references/genre-guides.md) for the target genre.
- Read [references/trace-to-edit-map.md](references/trace-to-edit-map.md) before diagnosing or rewriting.
- Read [references/evaluation.md](references/evaluation.md) whenever a controlled quality budget is requested.
- Read [references/experiment-protocol.md](references/experiment-protocol.md) whenever detector testing, score reduction, comparative claims, or method generalization is requested.
- Read [references/platform-observation-schema.md](references/platform-observation-schema.md) when recording a platform result or screenshot.
- Read [references/detector-science.md](references/detector-science.md) when explaining detector principles or citing research.
- Read [references/evidence-register.md](references/evidence-register.md) before turning a platform, repository, or community claim into a skill rule.
- Read [references/platform-and-repository-notes.md](references/platform-and-repository-notes.md) when the user asks for cross-platform or GitHub research.

## Route the request

Record three independent routes before writing.

### 1. Work mode

- `revision`: a draft exists; preserve its locked meaning and authentic correct idiosyncrasies.
- `new_generation`: no draft exists; build from user constraints and notes. Do not claim to restore an author's voice unless an author sample was supplied.
- `experiment_only`: compare frozen variants; do not edit unless separately authorized.

### 2. Provenance

Record `human_draft`, `ai_assisted`, `ai_generated`, `mixed`, or `unknown`. Also record whether the user supplied author notes or a voice sample. A self-generated first draft is not an author sample.

### 3. Context

Record `private_creative`, `ordinary_publication`, or `assessed_or_high_stakes`. Preserve required AI disclosure. For assessed or high-stakes work, do not help create false authorship evidence or conceal assistance contrary to the governing rules; quality editing and transparent disclosure remain allowed.

Ask only for missing information that would materially change facts, voice, permission, or disclosure. Otherwise state assumptions and proceed.

## Freeze the text contract

Before revision, freeze:

- language, genre, audience, purpose, target length, format, and publication setting;
- facts, dates, numbers, names, definitions, quotations, citations, and technical terms;
- thesis, conclusion strength, causal direction, uncertainty, and scope;
- viewpoint, chronology, character knowledge, world rules, and required motifs;
- disclosure requirements and forbidden transformations;
- author-supplied voice evidence, if any.

For factual work, create a claim ledger with `claim`, `source`, `precise location`, `type`, `confidence`, and `locked`. Separate fact, inference, opinion, and fiction.

For new fiction, create a compact story ledger: desire, obstacle, decision, consequence, viewpoint knowledge, timeline, setting rules, and unresolved threads. Select details because the scene needs them, not merely to look specific.

## Establish V0 before editing

Save the exact input as immutable `V0` and compute its SHA-256. If detector work was requested, define the acceptance criterion and quality budget before seeing new scores. Do not inspect highlighted spans and then retroactively describe ordinary edits as detector theory.

When local files are available, run:

```powershell
python scripts/analyze_texture.py input.txt --language auto --genre fiction
python scripts/validate_text.py input.txt --format json --pretty
```

`analyze_texture.py` describes repetition, rhythm, transitions, punctuation, and layout. It is not an AI detector and a clean report predicts no commercial score. `validate_text.py` checks exact bytes and deterministic surface hazards; it cannot prove facts, continuity, spelling, or authorship.

## Diagnose observable writing problems

Use [references/trace-to-edit-map.md](references/trace-to-edit-map.md). For each proposed edit, record:

1. the exact span or document-level pattern;
2. the reader-facing problem in this genre;
3. the evidence for that diagnosis;
4. the proposed intervention;
5. the locked constraints at risk;
6. the validation needed after the edit.

Do not call a phrase an "AI word" or infer a proprietary feature from a colored highlight. Platform highlights are annotations from that platform. They reveal neither causality nor the detector's internal weights.

Common diagnoses include generic framing, paragraph-role symmetry, exhaustive but shallow coverage, redundant summaries, uniformly resolved transitions, over-explained morals, narrator/character register collapse, ornamental specificity, uniform emotional cadence, and certainty unsupported by sources. These are problems only when they harm the actual text; human writing can contain them too.

## Rewrite in content-led passes

### Pass 1: information or scene

Remove correct but non-contributing filler. Add only sourced facts or fictionally coherent details that change action, inference, atmosphere, or choice. In new fiction, avoid making every prop foreshadow the ending; selective unused texture may remain when it belongs naturally to the setting.

### Pass 2: structure

Give each paragraph or scene a distinct job. Arrange it by evidence strength, cause, time, decision, or tension. Do not force equal section lengths, mirrored paragraph counts, three-part lists, or a lesson-shaped ending when the material does not require them.

### Pass 3: stance and voice

Separate observation, evidence, inference, and opinion. Match certainty to sources. Keep narrator knowledge within viewpoint. Differentiate speakers through goals, vocabulary, implication, interruption, and what they avoid saying, not through random quirks.

### Pass 4: sentence and paragraph form

Vary form because functions differ: decisions may be short, conditions may be long, dialogue may interrupt, and evidence may require stable terminology. Remove redundant transitions and recaps. Keep functional repetition. Do not randomize length, punctuation, or syntax.

### Pass 5: surface audit

Check reference, grammar, spelling, punctuation pairs, terminology, names, numbers, quotations, formatting, and accidental reuse. Preserve correct author-specific roughness only when it came from the source or an author sample. Do not manufacture imperfection.

## Controlled quality budget

Use only when the user explicitly requests or permits it. Begin from the best quality-preserving version, then change one intervention family per variant.

Permitted candidates include:

- removing a polished but redundant transition or recap;
- allowing paragraph density to follow content rather than visual symmetry;
- retaining correct lexical repetition instead of forced synonyms;
- choosing a plainer correct phrase over generic ornamental polish;
- preserving an author-supplied fragment, interruption, qualification, or mild rough edge that works in context;
- leaving a nonessential implication unstated when target readers can follow it without ambiguity.

The budget may spend a small amount of elegance, symmetry, transition smoothness, or rhetorical completeness. It may not spend truth, citations, logic, chronology, task-level clarity, grammar, spelling, stable terminology, narrative continuity, disclosure, or identity integrity.

Apply [references/evaluation.md](references/evaluation.md). Reject a candidate on any hard-gate failure even if a detector improves.

## Detector experiment workflow

Use [references/experiment-protocol.md](references/experiment-protocol.md) exactly.

Minimum rules:

1. Declare the detector threat model when known: likelihood, curvature, trained classifier, watermark, retrieval/provenance, or opaque commercial ensemble.
2. Use complete, non-repeated text in its real format. If too short, record `not evaluable`; never duplicate or pad.
3. Include a genuine, rights-compatible human control matched by language, genre, approximate length, and publication setting. Test the control before interpreting the target.
4. Preserve immutable versions. Prefer one-factor ablations. Keep development samples separate from holdout samples.
5. Record exact bytes, SHA-256, counts, detector URL, displayed model/date, settings, time, all visible component scores and labels, warnings, highlighted spans, and screenshot/report paths.
6. Accept only visible numeric output, visible labels, official exported reports, or screenshots. Never infer severity from CSS class names, colors, network field names, or undocumented code.
7. A score belongs only to the exact tested hash. Any edit, including punctuation or whitespace if submitted, invalidates it. A near-final score is not a final score.
8. Keep every run, contradiction, CAPTCHA interruption, quota failure, and unfavorable result. Do not select only the best score.
9. Measure rerun variation where quota permits. A deterministic repeat is replication of the service response, not independent evidence.
10. Stop when a hard gate fails, quality exceeds budget, effects do not exceed noise, controls reveal unacceptable false positives, or results conflict without a reproducible direction.

Create and validate an experiment record with:

```powershell
python scripts/experiment_record.py init final.txt --sample-id sample-01 --stage final --mode new_generation --provenance ai_generated --language zh --genre fiction -o sample-01.json
python scripts/experiment_record.py validate sample-01.json --text final.txt
```

## Evidence and generalization

Grade claims with [references/evidence-register.md](references/evidence-register.md): peer-reviewed or official primary evidence outranks reproducible repositories; community anecdotes are hypotheses only; degradation and integrity violations are rejected.

Do not promote a document-specific intervention into this skill unless it passes quality gates on multiple complete samples and then succeeds on untouched holdout samples across the claimed languages, genres, generators, and detector versions. Report sample counts, failures, control behavior, and uncertainty. One successful story cannot establish model or platform universality; one failed holdout disproves a guarantee.

## Final validation

Before delivery:

- compare the revision with the frozen contract and claim/story ledger;
- verify every changed fact, number, name, quotation, citation, and technical term;
- run a separate spelling and grammar pass, including Chinese homophones, near-form characters, missing/duplicated characters, and input-method substitutions;
- run `validate_text.py` on the final bytes;
- check argument validity or narrative continuity manually;
- use blind readers when feasible; hide provenance, version labels, and detector scores;
- test the exact final hash if and only if detector testing was requested and permitted;
- mark every automated check, manual check, unavailable check, and unresolved item.

## Deliver

Return:

1. the final text and exact SHA-256 when files are used;
2. a compact change log tied to diagnosed problems;
3. fact/citation or narrative-continuity results;
4. spelling, grammar, Unicode, duplication, and formatting results, distinguishing automated from manual checks;
5. blind quality results and every accepted quality-budget tradeoff;
6. the complete detector record, including matched controls, failures, exact-final status, and whether the user's threshold was achieved;
7. the evidence level of any reusable claim;
8. this limitation: detector outputs depend on language, genre, length, generator, detector version, threshold, and input construction; they cannot prove human authorship.
