# Editorial Anchors

## Purpose and boundary

An editorial anchor is a complete, approved text used to condition writing decisions. It is not a detector target, a phrase bank, a human-authorship certificate, or evidence that a described experience occurred. A reference may be human-drafted, AI-assisted, AI-generated, mixed, or unknown-origin; record that provenance instead of guessing from style.

Use this route when lowering a detector result is an explicit priority and the user can supply or approve one or more same-language, same-genre texts with enough complete context to show editorial decisions. Prefer a small, varied set over a large undifferentiated corpus. Do not use a memorized public example, a vendor demo, or a detector-labelled sample as a human control without provenance and rights review.

If no suitable anchor exists, say so in the writing contract and use the normal material-board or semantic-ledger route at lower confidence. Do not invent an anchor profile from sentence statistics, detector advice, or a generic idea of what human prose should look like.

## Freeze the anchor set

Before drafting, record for each anchor:

```yaml
anchor_id:
path_or_source:
sha256:
language:
genre:
audience_or_destination:
provenance: human_draft|ai_assisted|ai_generated|mixed|unknown
permission_or_rights_basis:
role: primary|contrast|calibration
```

Hash the exact UTF-8 bytes. Keep the anchor files separate from the target text and from detector controls. A text produced in the same task can guide later choices, but it is not an independent control or proof of a real author's identity.

Use one primary anchor whose reader, language, genre, and purpose are closest to the task. Add at most a few contrast anchors when they reveal a genuine alternative in emphasis or closure. Do not average several anchors into a smooth composite; preserve meaningful differences and choose deliberately.

## Extract an editorial profile

Read each complete anchor as a reader before examining individual sentences. Record observations with short source locations and confidence. Describe decisions, not scores:

- where the text starts and what it deliberately postpones;
- what receives concrete detail, what stays compressed, and what is omitted;
- how definitions, evidence, examples, caveats, and consequences are placed;
- when a term or image is repeated, shortened, replaced by a referent, or left implicit;
- how agency, certainty, distance, emotion, and responsibility are expressed;
- which transitions are made explicit and which relations the reader is trusted to infer;
- where paragraphs open, turn, stop, or leave a supported residue rather than restating the thesis;
- stable register, terminology, punctuation conventions, and narrative or argumentative stance.

Do not turn these observations into quotas. Do not count sentence lengths, punctuation proportions, transition frequency, vocabulary rarity, perplexity, or burstiness. A profile is a set of inspectable choices with examples, not a statistical target.

Use genre-specific questions only when they fit the material:

| Genre | Editorial questions |
|---|---|
| Chinese fiction | Whose limited knowledge controls the scene? Which ordinary detail earns space? Where does action outrun explanation? What consequence or unresolved residue closes the scene? |
| Chinese explanation or popular science | Which observation or question opens the explanation? Where is the mechanism made concrete? Which condition or exception changes the advice? What can remain implicit without losing safety? |
| Chinese argument or report | What claim is actually being made, at what scope? Which evidence earns space? Where are uncertainty, responsibility, thresholds, and counter-considerations attached? What action follows, if any? |
| English explanation, essay, or report | How direct is the opening? Where are qualifications attached? Which terms recur exactly? How does the ending narrow, act, or stop instead of adding a ceremonial summary? |

These questions guide selection and emphasis. They do not require every text to contain every feature.

## Apply the profile during composition

### New generation

1. Build the ordinary material board first and freeze facts, sources, constraints, and unknowns.
2. Add a short anchor profile that names the selected editorial choices and the places where this task should intentionally differ because its content or audience differs.
3. Choose a route from the material and reader need. Use the anchor to decide what deserves depth, what can be omitted, and how the ending may behave; do not copy its topic, outline, or paragraph count.
4. Draft from the board and route on a blank page. Return to the anchor only to check whether the candidate has made deliberate editorial choices, not to substitute phrases.

### Full reconstruction

1. Freeze `V0`, extract its semantic and evidence ledger, and keep locked strings separate.
2. Use the anchor profile as an external editorial comparator. It may suggest a different starting point, grouping, qualification placement, or closure, but it cannot authorize a new fact or override a locked relation.
3. Quarantine both the `V0` sentence sequence and the anchor wording. Draft from the ledger and the profile, then reconcile every candidate unit back to `V0` or an authorized source.
4. If the candidate becomes a polished average of the source and anchor, stop and reselect the governing relation. A blended surface is not an authored decision.

## Prevent accidental copying

Run the bundled overlap check against every anchor before delivery:

```powershell
python scripts/check_overlap.py final.txt --reference anchor.txt --language auto --strict --format json --pretty
```

The check reports long contiguous word or Han-character spans and exact hashes. Review every reported span. Allow only required quotations, standardized terms, titles, or other explicitly authorized strings through an allow file; never use a lower threshold to hide a match. A clean overlap report does not prove originality, and a reported match does not by itself prove plagiarism; it is a drafting guard.

Do not paraphrase an anchor sentence by sentence to evade the check. Change the underlying selection, grouping, explanation, or scene pressure when the candidate is too close. Preserve exact quotations and required terminology only when their source and purpose are recorded.

## Reconcile and report

Before detector submission, verify the target against its own ledger and quality gates, then record the target hash and every anchor hash. Report anchor provenance, role, permission basis, and any post-draft edits. Do not describe an anchor as a "real human sample" unless that provenance is independently established. Detector results remain exact-sample observations and must never be inherited by a different target hash.
