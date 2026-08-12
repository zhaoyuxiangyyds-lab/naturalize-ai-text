# Composition and Reconstruction

## Contents

1. Core rule
2. Shared preparation
3. Revision-depth gate
4. Traced bounded drafting
5. New-generation protocol
6. Full-reconstruction protocol
7. Failed-candidate retry protocol
8. Preserve/local-edit protocol
9. Coherence without uniformity
10. Failure checks

## 1. Core rule

Create natural variation by making real writing decisions. Do not imitate a statistical profile or manufacture mistakes, false starts, personal history, emotional claims, or arbitrary inconsistency. Uneven depth, local repetition, an abrupt turn, a plain sentence, or an unelaborated point may remain only when the material, voice, audience, or genre causes it.

Represent a real writing process through sourced material, explicit selection, provisional organization, carried state, and revision after discovery. Do not simulate that process by narrating fake hesitation, inventing discarded ideas, or leaving artificial draft traces in the finished prose.

Treat possible detector benefit as an unverified consequence. The workflow must still be defensible if no detector is ever used.

## 2. Shared preparation

Build a writing contract before prose:

```yaml
mode: new_generation|revision
revision_depth: full_reconstruction|local_edit
route_reason:
preserve: []
bounded_defects: []
reconstruction_triggers: []
language:
genre:
audience:
purpose:
target_length:
format:
destination:
voice_basis: source_draft|approved_samples|explicit_constraints|combined
locked_exact_strings: []
locked_meaning_units: []
locked_relations: []
required_disclosure:
unknowns: []
forbidden_additions: []
```

For factual prose, assign each material unit an identifier and record its source, exact location, claim type, certainty, conditions, exceptions, citation attachment, and whether it is locked. For fiction, record viewpoint, character knowledge, desire, pressure, choice, consequence, chronology, setting rules, clues, and unresolved threads. For all prose, record required terminology, voice evidence, genre obligations, and formatting.

For every relation whose scope or force must survive, use a compact record such as:

```yaml
- relation_id: R1
  source_or_basis:
  subject:
  predicate:
  object:
  scope:
  negation:
  modality_or_certainty:
  required_qualifiers: []
  forbidden_inferences: []
  final_text_evidence: []
```

Separate predicates that are easy to collapse. A state such as `unclaimed` describes the item's current status only; without separate authority it does not establish who owns it, who does not own it, how anyone obtained it, or who previously kept or transferred it. Preserve a supplied compound such as `prepaid urgent` as two required qualifiers of the same claim; neither `prepaid` nor `urgent` may stand in for the other. Apply the same discipline to negation, quantities, dates, comparison classes, causal direction, evidence strength, permissions, obligations, and viewpoint knowledge.

Do not turn missing material into plausible detail. Ask when the missing choice would materially change the result; otherwise narrow the claim, retain the uncertainty, or omit the unsupported branch.

### Reader-visible relation-coverage gate

Run this gate on the exact final prose after drafting and again after every reconciliation edit. Planning records are inputs to the check, not evidence that the reader received the relation.

1. For each locked relation, quote the smallest final-text span or spans that expose the correct subject, predicate, scope, negation, certainty, and every required qualifier. Natural wording is allowed unless an exact string is locked.
2. If a relation is intentionally unknown or unsupported, inspect every candidate assertion that touches it. Passing requires that the prose keep it unresolved; an empty `final_text_evidence` field cannot prove absence by itself.
3. Map every new assertion in the candidate back to an authoritative input or an allowed fictional invention. Reject an assertion that converts status into ownership, possibility into fact, temporal proximity into causation, payment into urgency, urgency into a deadline, or one qualifier into a complete compound claim.
4. Read the mapped spans in context. Reject technically present words whose syntax attaches them to the wrong subject, object, time, claim, or degree of certainty.
5. Record `pass`, `fail`, or `not_applicable` for every relation. Do not accept a candidate with an unmapped locked relation, a missing qualifier, a forbidden inference, or a trace-only claim.

This is a semantic coverage check, not a requirement to repeat prompt wording or expose every constraint as dialogue. Integrate relations where the genre naturally carries them, but keep them verifiable in the reader-facing text.

Persist this review as `relation-coverage.json`. Set `source_inventory_status: complete`, give every authoritative source an exact path, SHA-256, `inventory_status: complete`, and the relation IDs extracted from it, and set `declared_relation_count` to the complete relation inventory. Each relation must include exact source evidence. Each coverage record must include exact final-text character spans, one qualifier map entry for every required qualifier, and one forbidden-inference review for every forbidden inference. Set `candidate_assertion_inventory_status: complete` and inventory every final-text assertion that touches a locked relation or changes comparative weight. Map it to an authoritative source or to a declared fictional-invention boundary; a fictional invention may preserve or clarify a locked relation but may not extend it or change comparative weight.

Run:

```powershell
python scripts/validate_relation_coverage.py relation-coverage.json --text final.txt --strict --pretty
```

The validator catches missing declared records, bad hashes or spans, incomplete qualifier maps, uncleared forbidden inferences, and unsupported declared assertions. It cannot discover a source relation the reviewer failed to inventory or a semantic assertion the reviewer mislabeled. Read the exact source and final prose after the script passes; do not treat the artifact as authorship or detector evidence.

## 3. Revision-depth gate

For revision, diagnose before rewriting. Provenance records disclosure and evidence boundaries; it does not determine revision depth.

1. Record what already works at document level: governing question or pressure, order of necessary relations, functional paragraphs or scenes, evidence attachment, voice, useful repetition, genre obligations, and closure.
2. Separate bounded defects from scaffold defects. A bounded defect has a responsible span that can change while the document's governing movement stays intact. A scaffold defect changes what the document selects, groups, orders, develops, or concludes.
3. Select `local_edit` when the working structure and voice outweigh scaffold defects. Preserve correct text verbatim where possible; an unchanged result is permitted.
4. Select `full_reconstruction` only when a named scaffold defect cannot be repaired locally without retaining the same failed movement, or when an explicit blank-page request survives integrity and exact-evidence checks.

Do not use an AI provenance label, a detector category, surface regularity, or an abstract desire for stronger naturalization as the route reason. If the exact source hash already has a valid favorable observation and passes quality review, treat exact preservation as the first candidate; any changed candidate starts with no detector evidence.

An unfavorable observation for an exact candidate is a reason to freeze that hash as a failed control, not a text-level reconstruction trigger. Do not infer what wording caused the result. For a same-task retry, require `retry_basis: explicit_blank_page` or a named scaffold trigger established independently of the score. The failed control then changes what material may remain visible during drafting; it does not license random edits.

Record the gate before prose. Do not reverse-engineer a route reason after seeing a candidate or detector result.

## 4. Traced bounded drafting

Use a compact composition trace for `new_generation` and `full_reconstruction`. Its purpose is to make the skill's process inspectable and to prevent a generic complete answer from being produced before content decisions are made. It is not a transcript of private reasoning and must not contain hidden chain-of-thought. Store only commitments that another reviewer can verify against the materials and draft.

Start the trace before visible prose. Give every source, ledger, story-beat, or authorized invention unit a stable ID. Record events in execution order:

```yaml
schema_version: "1.0"
mode: new_generation|full_reconstruction
language:
genre:
started_before_prose: true
events:
  - sequence: 1
    phase: material_commit
    unit_ids: [M1, M2]
    decision: central|support|boundary|omit
  - sequence: 2
    phase: section_commit
    section_id: S1
    unit_ids: [M1]
    state_before: concise reader, argument, or story state
    decision: the functional job committed before drafting
  - sequence: 3
    phase: section_result
    section_id: S1
    unit_ids: [M1]
    state_change: what the written unit actually established or changed
  - sequence: 4
    phase: reconciliation
    unit_ids: [M1, M2]
    decision: what was restored, merged, or removed
    state_change: final integrity state
```

The example shows field shape, not a required event count or document structure. Outside Chinese fiction and narrative, add one `section_commit` immediately before each functional unit and one matching `section_result` immediately after it. Add a `route_change` before the affected unit when a newly exposed premise, constraint, or emphasis changes the provisional route. Do not manufacture a route change for variety.

Outside the Chinese-fiction exception below, bound each drafting step:

1. Select the next unit from unresolved material and the current reader, argument, or story state.
2. Commit its allowed material IDs and one functional job before drafting it.
3. Draft only that unit. Do not generate later units in the same pass.
4. Record the actual state change, including a failed or partial result when that is what occurred.
5. Choose the next unit from the updated state, not from a universal outline or a target paragraph count.

### Chinese fiction continuous-scene-span exception

Only when `language: zh` and the genre is fiction or narrative, treat a functional unit as a continuous scene span, not an individual beat, sentence, exchange, gesture, or paragraph. Keep the same `section_commit` and `section_result` schema so the trace remains interoperable, but use one pair for the whole span. Keep other languages and genres on their existing language-specific bounded-unit route.

Before selecting a route through the supplied event, establish a viewpoint substrate. Record only material another reviewer can inspect:

- a preexisting routine, task, or social relation that is already in motion when the central pressure arrives;
- the character's durable attention field: what this person habitually names precisely, notices first, leaves unexamined, or treats as ordinary;
- an ordinary unfinished concern that would still exist if the prompt's central object or dilemma never appeared;
- the character's register, forms of address, and limits on what the narration may explain in words the character would not use.

Use supplied material when it already provides this substrate. Otherwise invent only what the declared fictional frame allows. Do not add a biography dump, decorative quirk, one-off sensory flourish, or sympathy-weighting circumstance. The substrate must not change ownership, urgency, entitlement, vulnerability, or the morally comparative weight of the supplied choice. Its job is to give the character a life and a way of attending before the brief asks the character to carry a plot.

Before the span, record only:

- the viewpoint character's current place and time, available knowledge, immediate aim or pressure, active uncertainty, and the live parts of the viewpoint substrate;
- continuity and viewpoint boundaries that cannot be crossed;
- supplied ownership, custody, evidence, entitlement, and comparative-stake relations that must not be silently reassigned or strengthened;
- the story or ledger IDs the span may use, without assigning them to predetermined paragraph positions;
- a drafting commitment to remain in the present scene, not a promised reveal, turn, decision, consequence, payoff, or closing image.

Draft a meaningful uninterrupted passage in one pass. It may contain several connected actions, perceptions, dialogue turns, pauses, and paragraphs. Follow what the viewpoint character attends to while handling the situation. Let the supplied pressure interrupt, compete with, or temporarily displace the ongoing life; do not let it erase that life on arrival. Ordinary scene business may remain when the character, place, and moment support it even if it never becomes a clue or payoff. Keep it connected through attention, relationship, or ongoing use rather than by forcing a later symbolic return. Do not insert such material as filler, deliberate inefficiency, random texture, or a detector proxy, and do not assign every included detail a future function.

After the span, record what actually changed in knowledge, pressure, relationship, available action, risk, or unresolved consequence. Only then choose whether another span is needed and what its starting state is. Start a new span because the scene's locus, time, governing pressure, or available action materially changed, or because the requested form requires a practical drafting boundary; never split by a sentence, paragraph, beat, or word-count quota.

Before accepting the span, run an open-choice integrity check. List every invented fact that changes who appears entitled, urgent, vulnerable, blameworthy, or deserving. Keep it only when the prompt, source, established character history, or ordinary scene causality requires it; otherwise remove the weighting fact and let the choice remain genuinely comparative. Do not solve an open dilemma by inventing a job interview, hospital visit, child dependent, eviction, exam, disability, death, poverty signal, institutional deadline, or similar high-weight circumstance for one side. These facts are allowed when supplied or independently necessary to the story, not as a device for making the decision virtuous.

Then run a prompt-capture audit at passage and document level:

- Summarize what the character is doing and attending to without using the prompt's central object or decision. If nothing remains, the viewpoint substrate did not survive into prose.
- Check whether nearly every passage merely introduces, explains, weighs, decides, or tidies one supplied condition. If so, reject the task-shaped movement even when the prose is fluent.
- Check whether weather, props, gestures, memories, and secondary characters have all been recruited as evidence, symbols, moral weights, or witnesses for the central choice. Restore only independently motivated scene life; do not add random countertexture.
- Check whether dialogue has become a complete cross-examination of the brief, with each speaker asking exactly the question needed to expose a constraint. Give each speaker a local conversational aim and allow motivated evasion, partial answers, practical talk, or misunderstanding without withholding facts the reader needs.
- Check whether removing the central dilemma would erase the viewpoint character's language, relations, and unfinished life. If it would, restart from a stronger substrate rather than patching individual sentences.

This audit diagnoses narrative capture, not an AI score. Do not turn it into quotas for digressions, dialogue, mundane detail, sentence shape, or unresolved threads.

Review closure separately from plot completeness. The story may end after the requested decision and its immediate practical state are clear without returning to the most conspicuous object, exact date, opening image, or bodily gesture. A recurring object may return only because the character still handles, sees, or must account for it in the scene. When the ongoing life naturally resumes, it may carry the ending without explaining how the central event changed the character. Reject a close built chiefly to mirror the opening, hide the central object, preserve it for later revelation, convert it into a symbol, or leave a polished emotional tableau. This is not a rule to end abruptly or incompletely; satisfy locked consequences and continuity, then stop at the scene's actual stopping place.

Do not backfill the trace after a complete draft. If persistence is unavailable, keep the same bounded sequence in structured scratch state and disclose that clean execution provenance is unavailable. A trace can show that required steps were recorded; it cannot prove authorship, cognition, or detector benefit.

## 5. New-generation protocol

### Build the material board

Work in notes before drafting sentences:

- list verified facts, sources, examples, observations, definitions, and constraints;
- identify the reader's actual question, decision, conflict, or desired experience;
- separate central material, supporting material, boundaries, and material to omit;
- choose a stance or narrative pressure supported by the task;
- record unresolved questions and prevent the draft from silently answering them.

Do not aim for exhaustive coverage. Give depth to material that changes understanding, evidence, action, character choice, or emotional consequence. Keep necessary but secondary matter brief. Omit decorative branches that exist only to make the piece look complete.

### Choose a provisional route

Order material by relations that already exist: cause, time, evidence strength, dependence, contrast, decision, spatial movement, or tension. Assign each section or scene a distinct job, but do not make every job equally visible or equally long. A route is provisional; it may change when drafting reveals a better emphasis.

Do not use universal skeletons such as context-thesis-three reasons-counterargument-summary, definition-three features-example-conclusion, or setup-three attempts-lesson. Use a conventional structure when the genre or destination genuinely requires it.

### Draft progressively

Draft from the board in traced functional units, using the continuous-scene-span exception above only for Chinese fiction and narrative. Outside that route, decide what the reader knows now, what arrives next, and why that unit belongs there. Within a Chinese fiction span, stay with the viewpoint and present situation without interrupting prose to optimize each local move. Carry newly established terms, facts, motives, and open questions forward. Do not repeatedly regenerate the entire document to make it smoother; global regeneration tends to erase local choices and restore uniform coverage.

Let sentence and paragraph form follow function. A definition may be compact, evidence may need qualification, a scene turn may be short, and a difficult mechanism may need sustained explanation. Do not alternate forms according to a schedule.

### Complete the document

After the first coherent draft, review the whole movement. Repair missing premises, unearned transitions, viewpoint leaks, duplicated functions, unsupported examples, and endings that merely restate or moralize. Keep useful recurrence and stable terms. Stop when the reader's task is fulfilled; do not add a ceremonial final paragraph.

The first complete draft is the detector baseline for a generation experiment. Do not create and score multiple hidden variants before choosing it.

## 6. Full-reconstruction protocol

Use this only after the revision-depth gate records a qualifying scaffold defect or an authorized blank-page requirement. AI or AI-assisted provenance alone never qualifies.

### Freeze and extract

Save the exact source as `V0` and compute its SHA-256. Build a semantic ledger without yet rewriting:

```yaml
- unit_id:
  source_location:
  kind: claim|evidence|definition|condition|exception|stance|event|dialogue|motif|constraint
  meaning:
  source_or_basis:
  certainty:
  locked: true|false
  exact_text_required: true|false
  relations: []
  candidate_location:
  disposition: retain|merge|omit_redundant|authorized_addition
  reason:
```

Extract the document's movement separately from its wording: what question it answers, how evidence or events accumulate, where the stance changes, which sections do real work, and which merely package or repeat. Record voice evidence such as register, preferred level of directness, stable vocabulary, characteristic syntax, narrative distance, and rhetorical restraint. Do not infer biography from style.

### Quarantine the old scaffold

After extraction, stop consulting the original sentence and paragraph sequence while producing the first reconstruction draft. Keep exact quotations, citations, formulas, commands, names, and required terms available in the ledger. This prevents sentence-by-sentence paraphrase while preserving material that must remain exact.

Do not preserve one candidate paragraph for every source paragraph. Do not rotate synonyms, shuffle source sentences, or retain the same claim-example-recap sequence under new wording.

Create a route sheet containing only candidate section jobs, their governing relations, and the ledger units they need. Do not copy source headings, paragraph counts, or paragraph summaries into it. Before drafting, compare the two movements at the level of function: if the candidate jobs still correspond one-for-one to the source in substantially the same order, and chronology, method, citation, or another locked relation does not require that order, discard the route sheet and choose a different anchor, grouping, or progression.

### Re-architect from meaning

Choose a new route from purpose and material. Decide which unit should anchor the reader, which evidence deserves space, which claims need an adjacent limit, what can merge, and what redundant packaging can disappear. Preserve chronology, methods order, citation proximity, and other fixed relations where they are meaningful constraints.

Write a blank-page candidate from the ledger and approved voice evidence. Recreate each passage as part of the new document rather than as a local substitute for source wording. Add only sourced factual material or authorized fictional material. Any omission or merge must have a reader-facing reason and remain traceable.

Draft the candidate through the bounded trace in Section 4. Outside Chinese fiction and narrative, a `section_commit` must name ledger or story IDs rather than source paragraph numbers. A Chinese fiction `section_commit` must name allowed story-ledger IDs and scene boundaries without allocating them to microbeats. Its `state_before` and matching `section_result` must describe the reader, argument, decision, or scene state, not how many source paragraphs have been covered.

### Reconcile in both directions

Compare only after the independent candidate exists:

1. Map every locked `V0` unit to the candidate. Restore missing meaning, exact strings, conditions, exceptions, and citations.
2. Map every candidate factual unit back to `V0` or an authorized source. Remove unsupported additions.
3. Run the reader-visible relation-coverage gate. Verify negation, quantity, modality, causality, chronology, status, ownership, custody, complete qualifier sets, viewpoint knowledge, evidence-to-claim links, and conclusion strength against actual candidate spans; a correct ledger or trace is insufficient.
4. Verify voice and genre without restoring the old template.
5. Read the candidate as one composition and repair visible seams caused by reconstruction.
6. Recheck the functional movement after restoring omissions. If reconciliation recreated an unlocked one-for-one source scaffold, re-architect the affected passage rather than paraphrasing it again.

For long documents, reconstruct section by section but maintain one global ledger. Recheck terminology, cross-references, assumptions, and argument or narrative state after each section.

## 7. Failed-candidate retry protocol

Use this stricter protocol only when a prior exact candidate has an unfavorable observation, another same-task attempt is authorized, and the retry basis passes the gate in Section 3.

### Freeze controls and authority

1. Freeze every failed candidate's exact bytes, SHA-256, visible observation, and evidence path. Keep it as a control, never as proof of authorship.
2. List authoritative inputs: raw brief, original source, citations, exact required strings, user constraints, approved voice evidence, and later authorized facts.
3. If an original source must be revised, read it once to build the semantic ledger, verify the ledger against the source, then close the source wording before route design.
4. Do not read failed intermediate candidates while building the new route or prose. If a failed candidate contains a necessary fact not present in an authoritative input, obtain separate authorization before adding it to the ledger.

The frozen ledger must be material-only. Record claims, evidence, conditions, exceptions, stance, chronology, viewpoint knowledge, required terms, disclosure, and authorized fictional possibilities. Do not record source paragraph summaries, candidate scene summaries, transition language, metaphors, punch lines, or a ready-made ending.

Before prose, record any genuinely viable route options exposed by the authoritative material. Give each option a positive content or genre reason and identify its governing pressure, question, evidence relation, or decision locus. Do not prewrite its outcome or ending, manufacture options to satisfy a count, or consult controls while making the register. Select one option and freeze that commitment before drafting. Unselected options remain available only as independently derived restart points.

### Compose without the failed movement

Create the route and trace from the material-only ledger. Do not preserve, invert, or cosmetically shuffle a failed candidate's paragraph order, scene or event chain, objection sequence, rhetorical arc, symbolic progression, decision staging, or ending. Deliberate inversion is still dependence on the failed scaffold. Select the next unit from the current reader, argument, or story state and an independently defensible content or genre reason.

For same-prompt new generation, return to the raw brief and declared invention boundary. Prior candidate inventions are not locked story facts. For revision, draft from the verified ledger rather than from source sentences or any later candidate. Do not use a detector-highlighted span, a surface metric, or a synonym list to choose prose.

### Reopen only for audit

After the independent draft is complete and frozen provisionally:

1. Reconcile every ledger unit and exact string against authoritative inputs, then map every locked relation and required qualifier to reader-visible candidate spans.
2. Map every factual or constrained candidate unit back to an authoritative input; remove unsupported material, scope changes, and forbidden inferences.
3. Run a long-overlap check against each failed candidate and review all matches. Required names and exact strings may remain; unexplained prose borrowing must not.
4. In an audit context, reduce the candidate and each control to concise functional signatures. Mark every field `authority_locked`, `unlocked`, or `not_applicable`; compare functions and state changes, not phrases. Keep the audit labels short and do not copy prose, motifs, or closing images into them.
5. Treat a long-overlap pass as necessary but insufficient. If the candidate recreates a failed control's unlocked causal, decision, consequence, and closure sequence, or its corresponding argument movement, freeze it as rejected even when every sentence is new.
6. Do not patch, invert, or recompose in a context that has now inspected the controls. Preserve the rejected candidate and audit. Start a fresh drafting context with the authoritative ledger and one unused positive route option that was recorded before prose; do not expose control prose, the rejected draft, or their functional signatures. If no independently justified option remains, stop and report that the prompt or locked material constrains the same scaffold.
7. Run meaning, continuity, genre, voice, disclosure, spelling, grammar, Unicode, and duplication checks.
8. Freeze the resulting bytes as a new unverified hash. Do not claim improvement until that exact hash receives a valid observation.

The genre guide defines the signature fields. Do not turn them into a similarity score or quota. A match forced by the raw brief, chronology, method, citation order, or another locked relation is not a recurrence defect by itself; the audit must identify the unlocked combination that was independently chosen again.

Do not combine this retry family with sentence-length quotas, synonym recipes, phrase blacklists, random punctuation, scheduled colloquialism, fabricated detail, deliberate errors, hidden characters, translation loops, padding, or duplicate passages.

## 8. Preserve/local-edit protocol

Use this route when the source's governing movement, functional units, voice, and genre work remain usable. Preserve them deliberately rather than treating retained text as work left undone. Identify each concrete reader-facing problem, its cause, and the smallest responsible span. Preserve surrounding wording and report that the result remains a local edit, not a whole-document reconstruction.

When no authorized defect survives review, return the exact source bytes and record `route_reason: preserve_working_document`. When edits are needed, avoid whole-document smoothing, synonym refreshes, uniform transition cleanup, or speculative improvements outside the defect list. Re-run meaning and language checks on changed spans and their joins.

Do not select local editing merely because it is faster, and do not reject it merely because the source is AI-generated. Select it because the preservation inventory and defect scope support it.

## 9. Coherence without uniformity

Preserve document-level coherence through recurring objects, stable terms, causal links, chronology, question development, or a consistent stance. Do not obtain coherence by giving every paragraph the same internal shape or by explaining every connection.

Check for authored selection:

- depth follows importance, evidence, difficulty, or scene pressure;
- repeated terms or motifs have a stable function;
- transitions appear where the relation would otherwise be ambiguous;
- examples are chosen because they test or clarify the claim;
- ordinary details in fiction belong to viewpoint and setting rather than serving as random texture;
- the ending changes, narrows, resolves, acts, or deliberately leaves a supported residue.

These are questions, not a checklist that every document must visibly satisfy.

## 10. Failure checks

Reject the candidate when:

- revision depth was selected from provenance or detector category rather than a recorded text-level diagnosis;
- a working source was globally rewritten without a named scaffold defect, destroying supported voice, structure, or exact-sample evidence;
- it preserves the source macrostructure and merely rewrites sentences;
- it replaces one formula with another or applies the same rhythm recipe across genres;
- a locked unit is missing, duplicated, detached from its source or condition, or changed in force;
- a new factual unit lacks a source or a fictional addition breaks the declared frame;
- local variation has no content, voice, or genre reason;
- the text contains fabricated personal detail or unverified specificity;
- correct terminology is replaced for lexical variety;
- clarity, grammar, spelling, citation form, continuity, disclosure, or normal language quality declines for a detector score;
- the candidate can be described only by surface statistics rather than by better content selection and document decisions.
- a complete polished draft was produced first and the composition trace was reconstructed afterward;
- section commitments merely enumerate the source paragraphs or a generic outline instead of recording content-bounded jobs and resulting state changes.
- a Chinese fiction span silently changes ownership, custody, evidence, entitlement, or comparative stakes supplied by the task;
- an invented high-weight circumstance makes an otherwise open Chinese fiction choice morally predetermined;
- a Chinese fiction ending returns to the conspicuous opening object or image chiefly to produce a mirrored, symbolic, or polished residue;
- a same-task retry consults failed-candidate prose during route design or drafting;
- a failed candidate contributes a fact, event, example, metaphor, or conclusion that is not independently authorized;
- the retry merely inverts, shuffles, or paraphrases the failed movement;
- an unfavorable detector category is presented as a sentence diagnosis, authorship proof, or sufficient reconstruction trigger;
- a successful exact hash from another sample is regenerated solely because this sample failed.
