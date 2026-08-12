import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from experiment_record import (  # noqa: E402
    add_observation,
    init_manifest,
    validate_manifest,
)
from composition_trace import append_event, finalize_trace, start_trace  # noqa: E402


class ExperimentRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.text_path = self.root / "sample.txt"
        self.text_path.write_text("标题\n\n这是第一句。这里还有第二句，内容足够用于记录。\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        self.temp.cleanup()

    def _observation(self, manifest, *, rerun_index=1, score=91):
        return {
            "detector_name": "Example",
            "detector_url": "https://example.test/detect",
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "screenshot_or_report_path": str(self.root / f"result-{rerun_index}.png"),
            "rerun_index": rerun_index,
            "raw_components": {
                "human_features": score,
                "suspected_ai": 6,
                "ai_features": 100 - score - 6,
            },
        }

    def _lock_preregistration(self, manifest):
        manifest["pre_registration"].update(
            {
                "status": "locked",
                "registered_at": "2026-08-11T00:00:00Z",
                "question": "Does the registered intervention reduce the named detector's AI-feature share?",
                "target_metric": "Tencent Zhuque displayed AI features",
                "material_effect_threshold": 5,
                "quality_budget": "No hard-gate loss; at most one minor soft-rubric step.",
                "detectors": ["Tencent Zhuque"],
                "languages": ["zh"],
                "genres": ["fiction"],
                "sample_selection": "Complete, non-repeated development sample frozen before testing.",
                "matched_control_rule": "Same language, genre, approximate length, and display format.",
                "rerun_rule": "Repeat the exact hash with unchanged settings twice when the platform permits.",
                "stop_rule": "Stop on any hard-gate failure or an effect within rerun noise.",
                "intervention_family": "content-led full-document reconstruction",
                "composition_process": "full_reconstruction",
            }
        )
        manifest["controls"] = [
            {
                "control_id": "control-01",
                "text_sha256": "0" * 64,
                "language": "zh",
                "genre": "fiction",
                "provenance": "human_draft",
                "relation": "matched language, genre, length, and format control",
            }
        ]
        manifest["quality"]["hard_gates"] = "passed"
        manifest["quality"]["blind_review"] = "self_review_only"
        manifest["quality"]["checks"] = {
            "source_integrity": "passed",
            "facts_and_citations": "passed",
            "logic_or_narrative_continuity": "passed",
            "language_surface": "passed",
            "genre_and_voice": "passed",
            "disclosure": "passed",
        }
        manifest["replication"]["required_runs"] = 2
        return manifest

    def _write_trace(self, *, mode="new_generation", text_path=None):
        trace = start_trace(mode=mode, language="zh", genre="fiction")
        append_event(
            trace,
            phase="material_commit",
            unit_ids=["M1"],
            decision="Use the only verified material unit.",
        )
        append_event(
            trace,
            phase="section_commit",
            section_id="S1",
            unit_ids=["M1"],
            state_before="The reader does not have the central fact.",
            decision="Establish the central fact.",
        )
        append_event(
            trace,
            phase="section_result",
            section_id="S1",
            unit_ids=["M1"],
            state_change="The central fact is established.",
        )
        append_event(
            trace,
            phase="reconciliation",
            unit_ids=["M1"],
            decision="Reconcile the final unit.",
            state_change="The unit is present and unchanged.",
        )
        finalize_trace(trace, text_path or self.text_path)
        path = self.root / "composition-trace.json"
        path.write_text(
            json.dumps(trace, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_init_and_validate_exact_hash(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-01",
            stage="V0",
            mode="new_generation",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        report = validate_manifest(manifest, self.text_path)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["status"], "pass")

    def test_observation_must_match_exact_hash_and_components(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-02",
            stage="final",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        observation = {
            "detector_name": "Example",
            "detector_url": "https://example.test/detect",
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "screenshot_or_report_path": str(self.root / "result.png"),
            "rerun_index": 1,
            "raw_component_scores": {
                "human_features": 91.0,
                "suspected_ai": 6.0,
                "ai_features": 3.0,
            },
        }
        add_observation(manifest, observation)
        report = validate_manifest(manifest, self.text_path)
        self.assertEqual(report["errors"], [])

        changed = self.root / "changed.txt"
        changed.write_text(self.text_path.read_text(encoding="utf-8") + "改动。\n", encoding="utf-8", newline="\n")
        changed_report = validate_manifest(manifest, changed)
        self.assertTrue(any(item["code"] == "text_hash_mismatch" for item in changed_report["errors"]))

    def test_component_sum_is_checked(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-03",
            stage="V1",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        add_observation(manifest, {
            "detector_name": "Example",
            "detector_url": "https://example.test/detect",
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "screenshot_or_report_path": str(self.root / "result.png"),
            "rerun_index": 1,
            "raw_component_scores": {"human_features": 90, "suspected_ai": 9, "ai_features": 9},
        })
        report = validate_manifest(manifest, self.text_path)
        self.assertTrue(any(item["code"] == "component_sum_not_100" for item in report["errors"]))

    def test_empty_numeric_observation_is_rejected(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-04",
            stage="final",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        add_observation(manifest, {
            "detector_name": "Example",
            "detector_url": "https://example.test/detect",
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "screenshot_or_report_path": str(self.root / "result.png"),
            "rerun_index": 1,
            "raw_component_scores": {},
        })
        report = validate_manifest(manifest, self.text_path)
        self.assertTrue(any(item["code"] == "numeric_evidence_missing_scores" for item in report["errors"]))

    def test_missing_text_path_is_reported_without_exception(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-05",
            stage="V0",
            mode="revision",
            provenance="human_draft",
            language="en",
            genre="essay",
        )
        manifest["text_path"] = ""
        report = validate_manifest(manifest)
        self.assertTrue(any(item["code"] == "missing_text_path" for item in report["errors"]))

    def test_invalid_route_values_are_rejected(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-06",
            stage="V0",
            mode="revision",
            provenance="human_draft",
            language="zh",
            genre="report",
        )
        manifest["mode"] = "rewrite_everything"
        manifest["provenance"] = "detector_says_human"
        report = validate_manifest(manifest, self.text_path)
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("invalid_mode", codes)
        self.assertIn("invalid_provenance", codes)

    def test_strict_mode_requires_locked_preregistration_and_controls(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-07",
            stage="final",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        report = validate_manifest(
            manifest,
            self.text_path,
            require_preregistration=True,
        )
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("preregistration_required", codes)
        self.assertIn("matched_control_required", codes)
        self.assertIn("replication_required", codes)
        self.assertIn("quality_hard_gates_required", codes)

    def test_locked_record_with_two_runs_and_quality_gates_passes_strict_mode(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-08",
            stage="final",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        self._lock_preregistration(manifest)
        add_observation(manifest, self._observation(manifest))
        add_observation(manifest, self._observation(manifest, rerun_index=2, score=90))
        report = validate_manifest(
            manifest,
            self.text_path,
            require_preregistration=True,
        )
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["replication"]["observed_runs"], 2)
        self.assertEqual(report["replication"]["status"], "replicated")
        self.assertEqual(report["control_count"], 1)

    def test_one_run_remains_single_observation_and_fails_strict_mode(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-08b",
            stage="final",
            mode="revision",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        self._lock_preregistration(manifest)
        add_observation(manifest, self._observation(manifest))

        report = validate_manifest(
            manifest,
            self.text_path,
            require_preregistration=True,
        )

        self.assertIn("replication_required", {item["code"] for item in report["errors"]})
        self.assertEqual(report["replication"]["status"], "single_observation")

    def test_strict_mode_rejects_unchecked_quality_even_with_two_runs(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-08c",
            stage="final",
            mode="revision",
            provenance="ai_generated",
            language="zh",
            genre="report",
        )
        self._lock_preregistration(manifest)
        manifest["quality"]["hard_gates"] = "not_checked"
        add_observation(manifest, self._observation(manifest))
        add_observation(manifest, self._observation(manifest, rerun_index=2, score=90))

        report = validate_manifest(
            manifest,
            self.text_path,
            require_preregistration=True,
        )

        self.assertIn("quality_hard_gates_required", {item["code"] for item in report["errors"]})

    def test_duplicate_detector_rerun_index_is_rejected(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-09",
            stage="V1",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        add_observation(manifest, self._observation(manifest, rerun_index=1))
        add_observation(manifest, self._observation(manifest, rerun_index=1, score=90))
        report = validate_manifest(manifest, self.text_path)
        self.assertTrue(any(item["code"] == "duplicate_rerun_index" for item in report["errors"]))

    def test_add_observation_normalizes_legacy_component_alias(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-10",
            stage="V1",
            mode="experiment_only",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        observation = {
            "detector_name": "Example",
            "detector_url": "https://example.test/detect",
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "screenshot_or_report_path": str(self.root / "result.png"),
            "raw_component_scores": {"human_features": 91, "suspected_ai": 6, "ai_features": 3},
        }
        add_observation(manifest, observation)
        self.assertEqual(manifest["observations"][0]["raw_components"], observation["raw_component_scores"])

    def test_clean_forward_test_requires_traceable_execution(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-11",
            stage="final",
            mode="new_generation",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )

        incomplete = validate_manifest(
            manifest,
            self.text_path,
            require_execution_provenance=True,
        )
        incomplete_codes = {item["code"] for item in incomplete["errors"]}
        self.assertIn("missing_or_invalid_skill_tree_sha256", incomplete_codes)
        self.assertIn("explicit_invocation_required", incomplete_codes)
        self.assertIn("fresh_context_required", incomplete_codes)
        self.assertIn("execution_files_read_required", incomplete_codes)
        self.assertIn("clean_forward_test_required", incomplete_codes)
        self.assertIn("composition_trace_required", incomplete_codes)

        trace_path, trace_hash = self._write_trace()

        manifest["execution_provenance"].update(
            {
                "skill_path": "C:/skills/naturalize-ai-text",
                "skill_tree_sha256": "a" * 64,
                "invocation": "explicit",
                "fresh_context": True,
                "execution_context_id": "fresh-thread-01",
                "files_read": ["SKILL.md", "references/editorial-anchors.md"],
                "anchor_hashes": ["b" * 64],
                "composition_trace_path": str(trace_path),
                "composition_trace_sha256": trace_hash,
                "output_sha256": manifest["text_sha256"],
                "post_generation_edits": [],
                "clean_forward_test": True,
            }
        )
        complete = validate_manifest(
            manifest,
            self.text_path,
            require_execution_provenance=True,
        )
        self.assertEqual(complete["errors"], [])
        self.assertTrue(complete["execution_provenance"]["clean_forward_test"])
        self.assertEqual(complete["execution_provenance"]["composition_trace_status"], "pass")
        self.assertEqual(complete["execution_provenance"]["composition_trace_section_count"], 1)

    def test_clean_forward_test_rejects_tampered_composition_trace(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-11b",
            stage="final",
            mode="new_generation",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        trace_path, trace_hash = self._write_trace()
        manifest["execution_provenance"].update(
            {
                "skill_path": "C:/skills/naturalize-ai-text",
                "skill_tree_sha256": "a" * 64,
                "invocation": "explicit",
                "fresh_context": True,
                "execution_context_id": "fresh-thread-02",
                "files_read": ["SKILL.md", "references/composition-and-reconstruction.md"],
                "composition_trace_path": str(trace_path),
                "composition_trace_sha256": trace_hash,
                "output_sha256": manifest["text_sha256"],
                "post_generation_edits": [],
                "clean_forward_test": True,
            }
        )
        trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
        trace_data["events"][1]["decision"] = "Changed after finalization."
        trace_path.write_text(
            json.dumps(trace_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        report = validate_manifest(
            manifest,
            self.text_path,
            require_execution_provenance=True,
        )
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("composition_trace_hash_mismatch", codes)
        self.assertIn("composition_trace_invalid", codes)

    def test_post_generation_edit_cannot_be_marked_clean(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-12",
            stage="V1",
            mode="revision",
            provenance="ai_generated",
            language="en",
            genre="explanation",
        )
        manifest["execution_provenance"].update(
            {
                "invocation": "explicit",
                "fresh_context": True,
                "post_generation_edits": ["Main task rewrote the final paragraph."],
                "clean_forward_test": True,
            }
        )

        report = validate_manifest(manifest, self.text_path)
        self.assertIn("post_edits_marked_clean", {item["code"] for item in report["errors"]})

    def test_legacy_schema_is_readable_but_cannot_pass_current_clean_forward_standard(self):
        manifest = init_manifest(
            self.text_path,
            sample_id="s-13",
            stage="final",
            mode="new_generation",
            provenance="ai_generated",
            language="zh",
            genre="fiction",
        )
        manifest["schema_version"] = "1.1"
        manifest["execution_provenance"].update(
            {
                "skill_path": "C:/skills/naturalize-ai-text",
                "skill_tree_sha256": "a" * 64,
                "invocation": "explicit",
                "fresh_context": True,
                "execution_context_id": "legacy-thread",
                "files_read": ["SKILL.md"],
                "output_sha256": manifest["text_sha256"],
                "post_generation_edits": [],
                "clean_forward_test": True,
            }
        )

        ordinary = validate_manifest(manifest, self.text_path)
        self.assertNotIn("unsupported_schema", {item["code"] for item in ordinary["errors"]})
        self.assertIn("legacy_schema", {item["code"] for item in ordinary["warnings"]})

        strict = validate_manifest(
            manifest,
            self.text_path,
            require_execution_provenance=True,
        )
        self.assertIn(
            "legacy_schema_cannot_prove_current_clean_forward_test",
            {item["code"] for item in strict["errors"]},
        )


if __name__ == "__main__":
    unittest.main()
