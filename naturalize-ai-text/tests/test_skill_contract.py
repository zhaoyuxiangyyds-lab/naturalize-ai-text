import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def _read(self, path):
        return (SKILL_ROOT / path).read_text(encoding="utf-8")

    def test_material_of_any_provenance_can_guide_voice_without_authorship_claim(self):
        skill = self._read("SKILL.md")
        routing = self._read("references/integrity-and-routing.md")

        self.assertIn("approved material of any provenance", skill)
        self.assertIn("may all guide content, structure, style, or target voice", routing)
        self.assertIn("does not independently prove a real person's identity", skill)
        self.assertIn("wrote without AI", routing)

    def test_new_generation_and_revision_have_distinct_processes(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("### New Generation", skill)
        self.assertIn("### Full Reconstruction", skill)
        self.assertIn("Do not create a generic complete draft", skill)
        self.assertIn("stop using the source sentence sequence", skill)
        self.assertIn("### Draft progressively", process)
        self.assertIn("### Quarantine the old scaffold", process)
        self.assertIn("### Reconcile in both directions", process)
        self.assertIn("Do not simulate that process", process)
        self.assertIn("correspond one-for-one to the source", process)
        self.assertIn("recreated an unlocked one-for-one source scaffold", process)

    def test_generation_and_reconstruction_require_genre_specific_composition_trace(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        genres = self._read("references/genre-guides.md")
        protocol = self._read("references/experiment-protocol.md")

        self.assertIn("create the compact composition trace", skill)
        self.assertIn("A finished document followed by a retrospective explanation", skill)
        self.assertIn("## 3. Revision-depth gate", process)
        self.assertIn("## 4. Traced bounded drafting", process)
        self.assertIn("Outside Chinese fiction and narrative", process)
        self.assertIn("add one `section_commit` immediately before each functional unit", process)
        self.assertIn("Draft only that unit", process)
        self.assertIn("### Chinese fiction continuous-scene-span exception", process)
        self.assertIn("use one pair for the whole span", process)
        self.assertIn("Do not backfill the trace after a complete draft", process)
        self.assertIn("genre-specific state", genres)
        self.assertIn("composition_trace.py", protocol)
        self.assertIn("composition_trace_sha256", protocol)

    def test_language_routes_audit_repeated_packaging_without_phrase_blacklist(self):
        chinese = self._read("references/chinese-naturalness.md")
        english = self._read("references/english-naturalness.md")

        self.assertIn("inspect repeated rhetorical packaging rather than banning individual phrases", chinese)
        self.assertIn("Do not replace them from a phrase list", chinese)
        self.assertIn("audit repeated premise packaging rather than blacklisting phrases", english)
        self.assertIn("Repair the underlying selection or relation", english)

    def test_revision_depth_is_diagnosed_not_inferred_from_ai_provenance(self):
        skill = self._read("SKILL.md")
        routing = self._read("references/integrity-and-routing.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("AI origin is not itself a defect", skill)
        self.assertIn("Select revision depth from the text, task, and genre", routing)
        self.assertIn("Provenance records disclosure and evidence boundaries", process)
        self.assertIn("exact source bytes", skill)
        self.assertIn("return the exact source unchanged", routing)
        self.assertNotIn("default to `full_reconstruction`", skill)
        self.assertNotIn("default to `full_reconstruction`", routing)
        self.assertIn("Do not paraphrase sentence by sentence", skill)

    def test_english_route_preserves_a_working_source_and_exact_hash_advantage(self):
        skill = self._read("SKILL.md")
        guide = self._read("references/english-naturalness.md")

        self.assertIn("Do not trade away an observed exact-text advantage", skill)
        self.assertIn("inventory the source's governing movement", guide)
        self.assertIn("return the exact source unchanged", guide)
        self.assertIn("do not erase it with an unnecessary rewrite", guide)

    def test_fiction_uses_continuous_scene_spans_before_retrospective_state_review(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")
        english = self._read("references/english-naturalness.md")

        self.assertIn("For Chinese fiction and narrative only, use the continuous-scene-span exception", skill)
        self.assertIn("meaningful uninterrupted passage", process)
        self.assertIn("Only then choose whether another span is needed", process)
        self.assertIn("do not pre-solve the character's final decision", genre)
        self.assertIn("draft a continuous scene span", genre)
        self.assertIn("do not stop after each microbeat", genre)
        self.assertIn("Do not privately finish the whole moral arc", chinese)
        self.assertIn("only after the span should the trace update", chinese)
        self.assertIn("without prewriting the final choice", english)

    def test_fiction_scene_span_does_not_weaken_other_genre_processes(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")

        english = self._read("references/english-naturalness.md")

        self.assertIn("Outside Chinese fiction and narrative, commit and draft one functional unit at a time", skill)
        self.assertIn("Outside the Chinese-fiction exception below, bound each drafting step", process)
        self.assertIn("Draft only that unit", process)
        self.assertIn("let the next unit answer the current unresolved pressure in the argument", genre)
        self.assertIn("identify the one decision, exception, bottleneck, or handoff", genre)
        self.assertIn("for other languages, retain the language-specific drafting process", genre)
        self.assertIn("without prewriting the final choice", english)

    def test_fiction_scene_span_rejects_random_or_detector_facing_texture(self):
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")

        self.assertIn("not insert such material as filler, deliberate inefficiency, random texture, or a detector proxy", process)
        self.assertIn("not from random texture, deliberate inefficiency, filler, or detector targeting", genre)
        self.assertIn("never add filler, random sensory texture, deliberate inefficiency, or detector-facing disturbance", chinese)

    def test_chinese_fiction_preserves_open_choice_integrity(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")

        self.assertIn("Preserve supplied ownership, custody, evidence, uncertainty, and comparative stakes exactly", skill)
        self.assertIn("run an open-choice integrity check", process)
        self.assertIn("changes who appears entitled, urgent, vulnerable, blameworthy, or deserving", process)
        self.assertIn("do not turn `unclaimed`, `unknown`, `possible`, `prepaid`", genre)
        self.assertIn("invented moral weighting", chinese)

    def test_chinese_fiction_rejects_engineered_object_closure_without_forcing_abruptness(self):
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")

        self.assertIn("Review closure separately from plot completeness", process)
        self.assertIn("This is not a rule to end abruptly or incompletely", process)
        self.assertIn("Read the ending once without the last sentence or paragraph", genre)
        self.assertIn("brings back the opening object, date, weather, sound, or gesture", chinese)

    def test_chinese_fiction_builds_viewpoint_substrate_before_event_route(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")

        self.assertIn("establish a viewpoint substrate before choosing the event route", skill)
        self.assertIn("a preexisting routine, task, or social relation", process)
        self.assertIn("the character's durable attention field", process)
        self.assertIn("an ordinary unfinished concern", process)
        self.assertIn("do not derive all of them from the inciting object", genre)
        self.assertIn("what this person would leave unnamed or unexplained", chinese)

    def test_chinese_fiction_rejects_prompt_capture_without_random_countertexture(self):
        process = self._read("references/composition-and-reconstruction.md")
        genre = self._read("references/genre-guides.md")
        chinese = self._read("references/chinese-naturalness.md")

        self.assertIn("run a prompt-capture audit", process)
        self.assertIn("reject the task-shaped movement", process)
        self.assertIn("do not add random countertexture", process)
        self.assertIn("nearly every passage is one more step in restating, weighing, or settling the brief", genre)
        self.assertIn("a perfectly ordered interrogation of the premise", chinese)
        self.assertIn("rather than inserting random digressions", chinese)

    def test_commentary_and_reports_have_separate_routes(self):
        chinese = self._read("references/chinese-naturalness.md")
        genre = self._read("references/genre-guides.md")

        self.assertIn("### Commentary and argument", chinese)
        self.assertIn("### Reports", chinese)
        self.assertNotIn("### Commentary, argument, and reports", chinese)
        self.assertIn("do not precommit a `claim-support-objection-summary` sequence", genre)
        self.assertIn("do not turn an operational report into commentary", genre)

    def test_fixed_surface_recipes_are_rejected(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        evaluation = self._read("references/evaluation.md")
        analyzer = self._read("scripts/analyze_texture.py")

        self.assertIn("Never target a sentence-length distribution", skill)
        self.assertIn("Do not alternate forms according to a schedule", process)
        self.assertIn("fixed quotas for sentence length", evaluation)
        self.assertNotIn("uniform_sentence_cv_below", analyzer)
        self.assertNotIn("thresholds_applied", analyzer)

    def test_chinese_route_covers_generation_reconstruction_and_genres(self):
        skill = self._read("SKILL.md")
        guide_path = SKILL_ROOT / "references" / "chinese-naturalness.md"
        guide = guide_path.read_text(encoding="utf-8")

        self.assertTrue(guide_path.exists())
        self.assertIn("references/chinese-naturalness.md", skill)
        self.assertIn("## 3. New generation", guide)
        self.assertIn("## 4. Full reconstruction", guide)
        for heading in (
            "### Fiction and narrative",
            "### Explanation and popular science",
            "### Commentary and argument",
            "### Reports",
            "### Academic and technical prose",
            "### Literary essay and memoir",
            "### Speech",
        ):
            self.assertIn(heading, guide)
        self.assertFalse((SKILL_ROOT / "references" / "chinese-information-order.md").exists())

    def test_chinese_explanation_uses_hinge_route_instead_of_factor_scaffold(self):
        guide = self._read("references/chinese-naturalness.md")
        genre = self._read("references/genre-guides.md")
        guide_normalized = " ".join(guide.split())
        genre_normalized = " ".join(genre.split())

        self.assertIn("governing hinge", guide_normalized)
        self.assertIn("one equally weighted paragraph per factor", guide_normalized)
        self.assertIn(
            "Do not force every explanation through the same hinge",
            guide_normalized,
        )
        self.assertIn("Quarantine the source's list order", guide_normalized)
        self.assertIn("one-paragraph-per-factor scaffolding", guide_normalized)
        self.assertIn("common prediction fail", genre_normalized)
        self.assertIn("not a universal explanation template", genre_normalized)

    def test_english_has_dedicated_generation_and_reconstruction_route(self):
        skill = self._read("SKILL.md")
        guide = self._read("references/english-naturalness.md")

        self.assertIn("references/english-naturalness.md", skill)
        self.assertIn("## 3. New generation", guide)
        self.assertIn("## 4. Full reconstruction", guide)
        self.assertIn("Do not use sentence-by-sentence paraphrase", guide)

    def test_every_public_genre_has_generation_guidance(self):
        guide = self._read("references/genre-guides.md")

        sections = guide.split("\n## ")[2:]
        genre_sections = [
            section
            for section in sections
            if not section.startswith("1. General")
            and not section.startswith("10. Mixed")
        ]
        for section in genre_sections:
            with self.subTest(section=section.splitlines()[0]):
                self.assertIn("### Generate", section)

    def test_detector_workflow_uses_integrated_candidate_then_registered_ablation(self):
        skill = self._read("SKILL.md")
        protocol = self._read("references/experiment-protocol.md")

        self.assertIn("integrated generation or reconstruction", skill)
        self.assertIn("one-factor ablations only in a later registered experiment", skill)
        self.assertIn("Integrated candidates, ablation, and acceptance", protocol)
        self.assertIn("user-returned screenshot", protocol)
        self.assertIn("raw_components", protocol)

    def test_detector_threshold_is_not_claimed_without_exact_result(self):
        skill = self._read("SKILL.md")

        self.assertIn("Detector benefit from any writing method is a hypothesis", skill)
        self.assertIn("Never upload user text automatically", skill)
        self.assertIn("A label without the required numeric components is not evaluable", skill)

    def test_failed_candidate_retry_uses_material_only_recomposition(self):
        skill = self._read("SKILL.md")
        routing = self._read("references/integrity-and-routing.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("failed_candidate_controls", skill)
        self.assertIn("retry_basis", skill)
        self.assertIn("does not diagnose a sentence defect", skill)
        self.assertIn("authoritative material-only ledger", skill)
        self.assertIn("unavailable_during_drafting", routing)
        self.assertIn("## 7. Failed-candidate retry protocol", process)
        self.assertIn("The frozen ledger must be material-only", process)
        self.assertIn("Reopen only for audit", process)
        self.assertIn("new unverified hash", process)

    def test_failed_result_does_not_override_route_or_successful_hashes(self):
        skill = self._read("SKILL.md")
        routing = self._read("references/integrity-and-routing.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("does not diagnose a sentence defect, prove AI authorship", skill)
        self.assertIn("Preserve successful exact hashes", skill)
        self.assertIn("Do not route to reconstruction from the detector label alone", routing)
        self.assertIn("does not license random edits", process)
        self.assertIn("a successful exact hash from another sample", process)

    def test_retry_guidance_is_genre_specific_without_inversion_recipe(self):
        genre = self._read("references/genre-guides.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("return to the raw brief and declared fictional frame", genre)
        self.assertIn("extract propositions, criteria, risks, thresholds", genre)
        self.assertIn("Do not deliberately reverse the old choice", genre)
        self.assertIn("Deliberate inversion is still dependence", process)
        self.assertIn("sentence-length quotas", process)

    def test_failed_retry_audits_functional_signature_and_restarts_fresh(self):
        skill = self._read("SKILL.md")
        genre = self._read("references/genre-guides.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("functional-signature review", skill)
        self.assertIn("A long-overlap pass is not enough", skill)
        self.assertIn("independently justified route option recorded before prose", skill)
        self.assertIn("record any genuinely viable route options", process)
        self.assertIn("Treat a long-overlap pass as necessary but insufficient", process)
        self.assertIn("freeze it as rejected", process)
        self.assertIn("Start a fresh drafting context", process)
        self.assertIn("do not expose control prose", process)
        self.assertIn("Do not turn them into a similarity score or quota", process)
        self.assertIn("decision owner, alternatives, selected action", genre)
        self.assertIn("title concept, initiating pressure", genre)
        self.assertIn("opening anchor, governing criterion, evidence grouping", genre)

    def test_editorial_anchor_route_is_explicit_and_traceable(self):
        skill = self._read("SKILL.md")
        anchors = self._read("references/editorial-anchors.md")
        routing = self._read("references/integrity-and-routing.md")
        protocol = self._read("references/experiment-protocol.md")

        self.assertIn("references/editorial-anchors.md", skill)
        self.assertIn("anchor_basis", skill)
        self.assertIn("Freeze the anchor set", anchors)
        self.assertIn("Do not average several anchors", anchors)
        self.assertIn("check_overlap.py", anchors)
        self.assertIn("anchor_records", routing)
        self.assertIn("Clean forward-test provenance", protocol)
        self.assertIn("post_generation_edits", protocol)
        self.assertIn("hash_skill_tree.py", protocol)

    def test_ui_metadata_matches_generation_and_reconstruction_scope(self):
        metadata = self._read("agents/openai.yaml")

        self.assertIn("Naturalize AI Text", metadata)
        self.assertIn("generate", metadata.lower())
        self.assertIn("reconstruct", metadata.lower())
        self.assertIn("preserve", metadata.lower())
        self.assertIn("genre-specific document diagnosis", metadata.lower())
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_package_is_labeled_v3(self):
        skill = self._read("SKILL.md")
        metadata = self._read("agents/openai.yaml")

        self.assertIn("Package version: 3.0.0", skill)
        self.assertIn('display_name: "Naturalize AI Text v3.0"', metadata)

    def test_fiction_can_invent_inside_frame_without_faking_real_experience(self):
        skill = self._read("SKILL.md")
        evaluation = self._read("references/evaluation.md")

        self.assertIn("Fiction may invent within its declared fictional frame", skill)
        self.assertIn("coherent declared fictional frame", evaluation)

    def test_locked_relations_require_reader_visible_bidirectional_coverage(self):
        skill = self._read("SKILL.md")
        routing = self._read("references/integrity-and-routing.md")
        process = self._read("references/composition-and-reconstruction.md")

        self.assertIn("locked relations and qualifiers", skill)
        self.assertIn("reader-visible relation-coverage gate", skill)
        self.assertIn("A material board, trace, or reviewer intention does not satisfy a lock", skill)
        self.assertIn("Represent a locked relation separately from a required word", routing)
        self.assertIn("### Reader-visible relation-coverage gate", process)
        self.assertIn("A state such as `unclaimed` describes the item's current status only", process)
        self.assertIn("Preserve a supplied compound such as `prepaid urgent`", process)
        self.assertIn("map every locked relation and required qualifier to reader-visible candidate spans", process)
        self.assertIn("Map every new assertion in the candidate back to an authoritative input", process)

    def test_artifact_manifest_cannot_hash_itself(self):
        protocol = self._read("references/experiment-protocol.md")
        hasher = self._read("scripts/hash_skill_tree.py")

        self.assertIn("explicitly exclude the manifest file from its own entries", protocol)
        self.assertIn("Never place a manifest's own digest inside that same manifest", protocol)
        self.assertIn("hash it from an external parent record", protocol)
        self.assertIn('parser.add_argument("-o", "--output")', hasher)
        self.assertIn('parser.add_argument("--exclude"', hasher)

    def test_relation_coverage_gate_has_executable_validator(self):
        skill = self._read("SKILL.md")
        process = self._read("references/composition-and-reconstruction.md")
        validator = self._read("scripts/validate_relation_coverage.py")

        self.assertIn("validate_relation_coverage.py", skill)
        self.assertIn("source_inventory_status: complete", process)
        self.assertIn("candidate_assertion_inventory_status: complete", process)
        self.assertIn("declared_relation_count", process)
        self.assertIn("semantic_scope_limit", validator)
        self.assertIn("relation_coverage_missing", validator)
        self.assertIn("qualifier_coverage_mismatch", validator)
        self.assertIn("candidate_assertion_is_forbidden_inference", validator)


if __name__ == "__main__":
    unittest.main()
