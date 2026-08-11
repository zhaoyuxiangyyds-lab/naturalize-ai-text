import json
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


class ExperimentRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.text_path = self.root / "sample.txt"
        self.text_path.write_text("标题\n\n这是第一句。这里还有第二句，内容足够用于记录。\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        self.temp.cleanup()

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
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
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
            "observed_at": "2026-08-11T00:00:00Z",
            "input_sha256": manifest["text_sha256"],
            "evidence_kind": "visible_numeric",
            "status": "observed",
            "raw_component_scores": {"human_features": 90, "suspected_ai": 9, "ai_features": 9},
        })
        report = validate_manifest(manifest, self.text_path)
        self.assertTrue(any(item["code"] == "component_sum_not_100" for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
