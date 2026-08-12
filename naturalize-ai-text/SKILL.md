---
name: naturalize-ai-text
description: Generate or reconstruct AI-generated, AI-assisted, mixed, or human prose in Chinese or English so it reads as deliberate, genre-appropriate writing rather than templated model output. Use for fiction, essays, academic or technical writing, reports, explainers, commentary, and speeches when asked to humanize text, reduce machine-like regularity, lower an AI-detection result, write naturally from the outset, or fully rewrite an existing AI draft. Preserve facts, citations, logic, continuity, genre, approved voice evidence of any provenance, required disclosure, and normal language quality. Treat detector results as exact-sample observations, never authorship proof or a guaranteed bypass.
---

# Naturalize AI Text

Package version: 3.0.0

## Operating Contract

Write through content decisions, not through statistical decoration. Make variation emerge from what the text needs to notice, establish, qualify, emphasize, omit, or leave unresolved. Never target a sentence-length distribution, transition count, punctuation mix, perplexity value, or other proxy. Never apply fixed recipes such as alternating long and short sentences, inserting colloquialisms at intervals, rotating paragraph openings, or replacing words from a synonym list.

Use this priority order:

> source integrity > facts and citations > logic or narrative continuity > disclosure and genre > supported voice > reader value > language quality > detector result

Keep every checkable fact, number, source, quotation, definition, causal direction, uncertainty, chronology, viewpoint boundary, required term, and formatting constraint. Never fabricate real experiences, identities, emotions, sources, data, quotations, citations, or process evidence. Fiction may invent within its declared fictional frame. Never add spelling or grammar errors, gibberish, homoglyphs, hidden or control characters, random punctuation, translation loops, unrelated padding, or duplicate passages. Do not remove watermarks or provider-side provenance.

Detector benefit from any writing method is a hypothesis until the exact final bytes receive a valid result. Do not promise `human features > 90%`, `AI features < 5%`, or any other threshold before that observation exists.

## Route The Task

Record:

- `mode`: `new_generation`, `revision`, or `experiment_only`;
- `revision_depth`: `full_reconstruction` or `local_edit`;
- `route_reason`: the document-level defect or preservation reason that selected that depth;
- language, genre, audience, purpose, length, format, and destination;
- `provenance`: `human_draft`, `ai_assisted`, `ai_generated`, `mixed`, or `unknown`;
- `anchor_basis`: `approved_corpus`, `source_draft`, `combined`, or `none`;
- source files, approved voice samples, locked facts, locked relations and qualifiers, citations, disclosure, and forbidden changes;
- `failed_candidate_controls`: exact hashes and observations for prior same-task candidates that must not be reused as drafting sources;
- `retry_basis`: `none`, `explicit_blank_page`, or a named document-level reconstruction trigger;
- whether detector testing is authorized and third-party submission is safe.

Use approved material of any provenance as content, structure, or voice evidence. It does not independently prove a real person's identity, experience, or unaided authorship. Keep provenance and revision depth separate: AI origin is not itself a defect and never selects `full_reconstruction` by itself. Diagnose the existing document before editing. Use `local_edit`, including an unchanged preservation outcome, when its governing movement, paragraph or scene jobs, voice, genre function, and factual relations already work and any defects are bounded. Use `full_reconstruction` only when the document-level scaffold is itself the problem and cannot be repaired responsibly in place, or when the user explicitly requires a blank-page rewrite and no locked constraint makes that unsafe. In `experiment_only`, freeze the input and do not edit.

If the exact source bytes already have a valid detector observation and pass current integrity and quality review, preserve that hash unless a real reader, factual, genre, disclosure, or task defect requires an edit. Any edit creates a new unverified sample. Do not trade away an observed exact-text advantage merely because the source was AI-generated, and do not generalize that observation to other text.

If an exact candidate receives an unfavorable detector observation and the user requests another attempt on the same task, freeze that candidate as a failed exact-hash control. The result does not diagnose a sentence defect, prove AI authorship, or by itself select `full_reconstruction`. Retry only when the user authorizes a blank-page recomposition or an independent document-level trigger already supports reconstruction. Preserve successful exact hashes from other samples and genres; a failure elsewhere is not a reason to regenerate them.

Read [references/integrity-and-routing.md](references/integrity-and-routing.md) for every task. Then read:

- [references/composition-and-reconstruction.md](references/composition-and-reconstruction.md) for every `new_generation` or `revision` task;
- [references/genre-guides.md](references/genre-guides.md) for the selected genre;
- [references/chinese-naturalness.md](references/chinese-naturalness.md) for Chinese text;
- [references/english-naturalness.md](references/english-naturalness.md) for English text;
- [references/trace-to-edit-map.md](references/trace-to-edit-map.md) only when diagnosing a supplied draft;
- [references/evaluation.md](references/evaluation.md) for quality review or a controlled tradeoff;
- [references/experiment-protocol.md](references/experiment-protocol.md) and [references/platform-observation-schema.md](references/platform-observation-schema.md) for detector tests;
- [references/detector-science.md](references/detector-science.md), [references/evidence-register.md](references/evidence-register.md), and [references/platform-and-repository-notes.md](references/platform-and-repository-notes.md) before converting research or community claims into reusable rules.

For every `new_generation` or `full_reconstruction`, create the compact composition trace defined in `composition-and-reconstruction.md` before drafting visible prose. Outside Chinese fiction and narrative, record selected material IDs, the next functional unit committed before it is written, and the reader, argument, or story state changed afterward. For Chinese fiction and narrative only, use the continuous-scene-span exception: establish a viewpoint substrate before choosing the event route, then commit current scene state, continuity boundaries, and allowed material before an uninterrupted scene passage. Record the actual story state only after that span. Do not stop to optimize each beat, exchange, paragraph, or detail. Record decisions, not hidden chain-of-thought. A finished document followed by a retrospective explanation is not a traced writing process. If a trace cannot be persisted, continue the writing task but do not describe the result as a clean forward test of this skill.

When detector reduction is an explicit priority and an approved same-language, same-genre complete text is available, read [references/editorial-anchors.md](references/editorial-anchors.md). Freeze each anchor's exact hash and provenance, extract editorial decisions, and use them as a content-selection comparator. An anchor is not proof of human authorship and never licenses phrase copying. If no suitable anchor exists, record `anchor_basis: none` and treat detector benefit as lower-confidence and unverified.

## Execute One Writing Mode

### New Generation

Do not create a generic complete draft and humanize it afterward. Start with a material board containing only verified or user-authorized content, unresolved questions, genre constraints, and voice evidence. Decide what matters most to this reader, what receives depth, what remains brief, and what should be omitted. Build a provisional route from evidence, causality, time, tension, or decision; do not force comprehensive or symmetrical coverage.

If an editorial anchor is available, add its decision profile to the material board before choosing the route. Use it to make deliberate choices about emphasis, omission, qualification, and closure; do not imitate its topic, outline, paragraph count, or wording.

Draft from the material board. Carry forward local discoveries and constraints rather than regenerating the whole document into a smoother template. Let paragraph and sentence form follow the material and genre. Finish only after the text has a coherent document-level movement and a genre-appropriate close.

Outside Chinese fiction and narrative, commit and draft one functional unit at a time. Before each unit, record which material IDs it may use, its job, and the state from which it starts. After writing it, record what actually changed and which constraint now governs the next choice. For Chinese fiction and narrative only, draft one continuous scene span at a time under the narrower precommitment in `composition-and-reconstruction.md`; review state after the span rather than assigning every local detail a plot job. Before selecting how the supplied event unfolds, establish the viewpoint character's durable attention, existing social relation or routine, and an ordinary unfinished concern that would exist without the prompt's central object. Let the supplied pressure interrupt or coexist with that life instead of making every sentence adjudicate the brief. Preserve supplied ownership, custody, evidence, uncertainty, and comparative stakes exactly. Do not invent a deadline, illness, child, financial hardship, public duty, or other decisive sympathy weight merely to make one open choice morally obvious. Do not pre-compose a complete polished answer and backfill these records.

### Full Reconstruction

Enter this mode only after the revision-depth gate identifies a document-level reconstruction trigger. Freeze the source as `V0` and hash its exact bytes. Extract a semantic ledger: claims, evidence, citations, definitions, conditions, uncertainty, stance, chronology, narrative events, viewpoint knowledge, required language, voice traits, and unresolved threads. Separate exact strings that must survive from prose that may be rebuilt.

After the ledger is complete, stop using the source sentence sequence as the drafting scaffold. Design a new document route from purpose, reader need, evidence, causality, or scene pressure, then write a blank-page candidate from the ledger and approved voice evidence. Do not paraphrase sentence by sentence, preserve paragraph correspondence, or perform synonym substitution. Compare the candidate with `V0` only after the independent draft exists; restore omissions and exact material without restoring the old generated frame.

For an authorized retry after a failed exact-hash observation, use the stricter failed-candidate quarantine in `composition-and-reconstruction.md`. Build an authoritative material-only ledger from the raw brief, frozen source, citations, approved voice evidence, and later authorized facts. Do not read or imitate failed-candidate wording, paragraph order, scene or event chain, rhetorical arc, or ending while drafting. A failed candidate may contribute material only when that material is independently present in an authoritative source or separately authorized. Reopen failed candidates only after the independent draft exists, for overlap and functional-signature review. A long-overlap pass is not enough: reject a candidate that recreates the same unlocked decision, consequence, and closure sequence. Do not patch or invert it in the now-exposed context. Restart only in a fresh context from the frozen ledger and an independently justified route option recorded before prose. The retry is a new unverified hash.

Use the same language-and-genre-specific trace as new generation. Outside Chinese fiction and narrative, a reconstruction unit must identify its ledger IDs before prose is written and record its resulting reader, argument, or story state afterward. A Chinese fiction reconstruction span must identify allowed ledger IDs and viewpoint or continuity boundaries before prose, then record the resulting story state only after the uninterrupted span. If the next unit or span changes because drafting exposed a missing premise, conflict, or better emphasis, record that route change before drafting it.

When an approved editorial anchor is used, quarantine its wording as well as the `V0` scaffold. Let its decision profile inform grouping and depth, then reconcile every candidate unit to `V0` or an authorized source.

### Preserve Or Local Edit

Keep the source's successful movement and voice. List concrete reader-facing, factual, genre, or language defects, change only the smallest responsible spans, and leave correct passages alone. Returning the unchanged source is valid when no authorized change improves it. Do not perform a global polish pass merely to make authorship provenance less visible, and do not treat preservation or local editing as a reconstructed document.

Detailed procedures and stop conditions are in [references/composition-and-reconstruction.md](references/composition-and-reconstruction.md).

## Validate The Candidate

Run three separate reviews:

1. **Meaning and continuity:** reconcile every ledger item, citation, number, term, condition, inference, timeline event, viewpoint fact, and disclosure. Then run the reader-visible relation-coverage gate in `composition-and-reconstruction.md`: map each locked relation and every required qualifier to the smallest final-text span that makes it readable, and map every candidate assertion back to authority. A material board, trace, or reviewer intention does not satisfy a lock when the final prose omits it or changes its scope.
2. **Reader and genre:** check selection, emphasis, paragraph jobs, progression, voice, useful repetition, information depth, and ending. Reject manufactured quirks and unexplained local disruption.
3. **Surface integrity:** check spelling, Chinese near-form or homophone substitutions, English usage, grammar, punctuation pairs, Unicode, formatting, and accidental duplication.

When files are available, run:

```powershell
python scripts/validate_text.py final.txt --format json --pretty --strict
python scripts/analyze_texture.py final.txt --language auto --genre fiction --format json --pretty
python scripts/validate_relation_coverage.py relation-coverage.json --text final.txt --strict --pretty
```

`analyze_texture.py` reports reviewable surface patterns. It is not an AI detector, score optimizer, or target specification. Never revise merely to move one of its metrics.

Run `validate_relation_coverage.py` whenever the task has locked relations or qualifiers. It deterministically checks declared source hashes, complete inventory status, exact source and final-text spans, qualifier coverage, forbidden-inference review, and assertion authority. Its pass is record consistency only; manually audit whether the inventory omitted or mislabeled any semantic relation.

When an editorial anchor was used, also run `scripts/check_overlap.py` against every anchor and review every reported span:

```powershell
python scripts/check_overlap.py final.txt --reference anchor.txt --language auto --strict --format json --pretty
```

## Record Detector Evidence

An integrated generation or reconstruction may make several linked content decisions at once. Do not claim which decision caused a score change. Use one-factor ablations only in a later registered experiment when causal attribution matters; do not force ordinary writing into serial detector steering.

Never upload user text automatically. When testing is authorized, provide the exact final text and SHA-256 for the user to submit, especially to Tencent Zhuque, then record the returned screenshot or official report against that hash. Record every visible component and detector update date. A label without the required numeric components is not evaluable for a numeric threshold.

For a clean forward test, freeze the skill tree before the request, record its tree hash and the references actually read, use an explicit skill invocation in a fresh execution context, save and hash the contemporaneous composition trace, and record any post-generation edits. A main task that changes the skill and then writes the test text is an authoring pass, not an independent forward test. A self-declared trace improves auditability but does not prove that an internal mental process occurred.

```powershell
python scripts/experiment_record.py init final.txt --sample-id sample-01 --stage final --mode revision --provenance ai_generated --language zh --genre fiction -o sample-01.json
python scripts/experiment_record.py validate sample-01.json --text final.txt --strict --require-preregistration --require-execution-provenance
```

Do not use repeated unregistered submissions, highlighted-span chasing, local metrics, or favorable screenshots from a different hash as evidence. Report absent or conflicting results as `not_evaluable` or `single_observation`, not success.

## Deliver

Return the finished text first. Then report mode and reconstruction depth, locked-content reconciliation, unresolved risks, surface checks, and exact hash when files are used. Include detector evidence only when it belongs to the exact final bytes. State that results depend on language, genre, length, generator, detector version, threshold, and input construction and cannot prove human authorship.
