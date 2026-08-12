import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from composition_trace import (  # noqa: E402
    append_event,
    finalize_trace,
    start_trace,
    validate_trace,
    validate_trace_file,
)


class CompositionTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.text = self.root / "final.txt"
        self.text.write_text("Title\n\nA complete test paragraph.\n", encoding="utf-8", newline="\n")

    def tearDown(self):
        self.temp.cleanup()

    def _complete_trace(self):
        trace = start_trace(mode="full_reconstruction", language="en", genre="explanation")
        append_event(
            trace,
            phase="material_commit",
            unit_ids=["M1", "M2"],
            decision="M1 is central; M2 is a boundary.",
        )
        append_event(
            trace,
            phase="section_commit",
            section_id="S1",
            unit_ids=["M1"],
            state_before="The reader has the observation but not the mechanism.",
            decision="Establish the minimum mechanism.",
        )
        append_event(
            trace,
            phase="section_result",
            section_id="S1",
            unit_ids=["M1"],
            state_change="The mechanism is established; its boundary remains open.",
        )
        append_event(
            trace,
            phase="reconciliation",
            unit_ids=["M1", "M2"],
            decision="Restore the boundary beside the claim.",
            state_change="All committed units are present and scoped.",
        )
        finalize_trace(trace, self.text)
        return trace

    def test_complete_trace_passes_and_matches_text(self):
        trace = self._complete_trace()
        report = validate_trace(trace, self.text)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["section_count"], 1)
        self.assertEqual(report["event_count"], 4)

    def test_tampered_event_breaks_hash_chain(self):
        trace = self._complete_trace()
        trace["events"][1]["decision"] = "Retrospectively changed."
        report = validate_trace(trace, self.text)
        self.assertIn("trace_event_hash_mismatch", {item["code"] for item in report["errors"]})

    def test_result_requires_prior_matching_commit(self):
        trace = start_trace(mode="new_generation", language="zh-Hans", genre="fiction")
        append_event(trace, phase="material_commit", unit_ids=["B1"], decision="Use the pressure beat.")
        append_event(
            trace,
            phase="section_result",
            section_id="S1",
            unit_ids=["B1"],
            state_change="The choice narrows.",
        )
        report = validate_trace(trace, require_finalized=False)
        self.assertIn("section_result_without_commit", {item["code"] for item in report["errors"]})

    def test_commit_and_result_unit_ids_must_match(self):
        trace = start_trace(mode="new_generation", language="zh-Hans", genre="report")
        append_event(trace, phase="material_commit", unit_ids=["M1", "M2"], decision="Select evidence.")
        append_event(
            trace,
            phase="section_commit",
            section_id="S1",
            unit_ids=["M1"],
            state_before="Decision is unresolved.",
            decision="Establish the decision fact.",
        )
        append_event(
            trace,
            phase="section_result",
            section_id="S1",
            unit_ids=["M2"],
            state_change="A different unit was used.",
        )
        report = validate_trace(trace, require_finalized=False)
        self.assertIn("section_unit_ids_changed", {item["code"] for item in report["errors"]})

    def test_commit_must_be_followed_immediately_by_its_result(self):
        trace = start_trace(mode="new_generation", language="zh-Hans", genre="fiction")
        append_event(trace, phase="material_commit", unit_ids=["B1", "B2"], decision="Select two beats.")
        append_event(
            trace,
            phase="section_commit",
            section_id="S1",
            unit_ids=["B1"],
            state_before="The choice is open.",
            decision="Narrow the choice.",
        )
        append_event(
            trace,
            phase="section_commit",
            section_id="S2",
            unit_ids=["B2"],
            state_before="The consequence is unknown.",
            decision="Show the consequence.",
        )
        report = validate_trace(trace, require_finalized=False)
        self.assertIn("section_result_not_immediate", {item["code"] for item in report["errors"]})

    def test_reconciliation_must_be_last_event(self):
        trace = self._complete_trace()
        trace["status"] = "active"
        trace["final_output"] = {"path": "", "sha256": ""}
        trace.pop("finalized_at", None)
        append_event(
            trace,
            phase="route_change",
            state_before="The document was already reconciled.",
            decision="Attempt a late route change.",
        )
        report = validate_trace(trace, require_finalized=False)
        self.assertIn("event_after_reconciliation", {item["code"] for item in report["errors"]})

    def test_finalized_trace_requires_reconciliation(self):
        trace = start_trace(mode="new_generation", language="en", genre="speech")
        append_event(trace, phase="material_commit", unit_ids=["M1"], decision="Use the verified stake.")
        append_event(
            trace,
            phase="section_commit",
            section_id="S1",
            unit_ids=["M1"],
            state_before="The audience lacks the stake.",
            decision="State the stake.",
        )
        append_event(
            trace,
            phase="section_result",
            section_id="S1",
            unit_ids=["M1"],
            state_change="The stake is audible.",
        )
        trace["status"] = "finalized"
        trace["finalized_at"] = trace["events"][-1]["recorded_at"]
        trace["final_output"] = {"path": str(self.text), "sha256": "a" * 64}
        report = validate_trace(trace, require_finalized=True)
        self.assertIn("reconciliation_event_missing", {item["code"] for item in report["errors"]})

    def test_trace_file_reports_exact_hash(self):
        trace_path = self.root / "trace.json"
        trace_path.write_text(
            json.dumps(self._complete_trace(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        report = validate_trace_file(trace_path, self.text)
        self.assertEqual(report["status"], "pass")
        self.assertRegex(report["trace_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
