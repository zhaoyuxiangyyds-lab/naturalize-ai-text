import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_relation_coverage import validate_coverage  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def span(text: str, value: str, evidence_id: str) -> dict:
    start = text.index(value)
    return {
        "evidence_id": evidence_id,
        "start": start,
        "end": start + len(value),
        "text": value,
    }


class RelationCoverageTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict]:
        source_text = (
            "The film envelope is unclaimed and marked 2016.7. "
            "Another customer is waiting for prepaid urgent ID photos."
        )
        final_text = (
            "The envelope is still unclaimed. "
            "The other customer's ID photos were prepaid and remain urgent."
        )
        source = root / "brief.txt"
        final = root / "final.txt"
        source.write_text(source_text, encoding="utf-8", newline="\n")
        final.write_text(final_text, encoding="utf-8", newline="\n")
        value = {
            "schema_version": "1.0",
            "text_sha256": sha256(final),
            "source_inventory_status": "complete",
            "candidate_assertion_inventory_status": "complete",
            "declared_relation_count": 2,
            "sources": [
                {
                    "source_id": "SRC1",
                    "path": "brief.txt",
                    "sha256": sha256(source),
                    "inventory_status": "complete",
                    "relation_ids": ["R1", "R2"],
                }
            ],
            "invention_boundaries": [],
            "relations": [
                {
                    "relation_id": "R1",
                    "source_ids": ["SRC1"],
                    "subject": "film envelope",
                    "predicate": "has current status",
                    "object": "unclaimed",
                    "scope": "status only",
                    "negation": "none",
                    "modality_or_certainty": "supplied fact",
                    "required_qualifiers": ["unclaimed"],
                    "forbidden_inferences": ["ownership", "custody_history"],
                    "source_evidence": [
                        {
                            **span(source_text, "The film envelope is unclaimed", "R1-S1"),
                            "source_id": "SRC1",
                        }
                    ],
                },
                {
                    "relation_id": "R2",
                    "source_ids": ["SRC1"],
                    "subject": "other customer's ID photos",
                    "predicate": "have supplied claim weight",
                    "object": "waiting claim",
                    "scope": "complete supplied weight",
                    "negation": "none",
                    "modality_or_certainty": "supplied fact",
                    "required_qualifiers": ["prepaid", "urgent"],
                    "forbidden_inferences": ["invented_deadline"],
                    "source_evidence": [
                        {
                            **span(source_text, "prepaid urgent ID photos", "R2-S1"),
                            "source_id": "SRC1",
                        }
                    ],
                },
            ],
            "coverage": [
                {
                    "relation_id": "R1",
                    "status": "pass",
                    "final_text_evidence": [
                        span(final_text, "The envelope is still unclaimed", "R1-F1")
                    ],
                    "qualifier_coverage": [
                        {"qualifier": "unclaimed", "evidence_ids": ["R1-F1"]}
                    ],
                    "forbidden_inference_review": [
                        {
                            "inference": "ownership",
                            "status": "absent",
                            "notes": "No ownership assertion occurs in the candidate.",
                        },
                        {
                            "inference": "custody_history",
                            "status": "absent",
                            "notes": "No custody history occurs in the candidate.",
                        },
                    ],
                },
                {
                    "relation_id": "R2",
                    "status": "pass",
                    "final_text_evidence": [
                        span(
                            final_text,
                            "The other customer's ID photos were prepaid and remain urgent",
                            "R2-F1",
                        )
                    ],
                    "qualifier_coverage": [
                        {"qualifier": "prepaid", "evidence_ids": ["R2-F1"]},
                        {"qualifier": "urgent", "evidence_ids": ["R2-F1"]},
                    ],
                    "forbidden_inference_review": [
                        {
                            "inference": "invented_deadline",
                            "status": "absent",
                            "notes": "No reason or deadline is added.",
                        }
                    ],
                },
            ],
            "candidate_relation_assertions": [
                {
                    "assertion_id": "A1",
                    "summary": "The envelope remains unclaimed.",
                    "final_text_evidence": [
                        span(final_text, "The envelope is still unclaimed", "A1-F1")
                    ],
                    "touches_relation_ids": ["R1"],
                    "relation_effect": "preserves",
                    "changes_comparative_weight": False,
                    "authority_kind": "authoritative_source",
                    "authority_ids": ["SRC1"],
                },
                {
                    "assertion_id": "A2",
                    "summary": "The other claim remains prepaid and urgent.",
                    "final_text_evidence": [
                        span(
                            final_text,
                            "The other customer's ID photos were prepaid and remain urgent",
                            "A2-F1",
                        )
                    ],
                    "touches_relation_ids": ["R2"],
                    "relation_effect": "preserves",
                    "changes_comparative_weight": False,
                    "authority_kind": "authoritative_source",
                    "authority_ids": ["SRC1"],
                },
            ],
            "review_status": "pass",
        }
        return final, value

    def test_complete_relation_coverage_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)

            report = validate_coverage(value, final, base_dir=root)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["relation_count"], 2)

    def test_source_inventory_catches_omitted_unclaimed_relation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)
            value["relations"] = [value["relations"][1]]
            value["declared_relation_count"] = 1
            value["coverage"] = [value["coverage"][1]]
            value["candidate_relation_assertions"] = [
                value["candidate_relation_assertions"][1]
            ]

            report = validate_coverage(value, final, base_dir=root)

            codes = {item["code"] for item in report["errors"]}
            self.assertIn("source_inventory_unknown_relations", codes)

    def test_missing_urgent_half_of_prepaid_urgent_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)
            value["coverage"][1]["qualifier_coverage"] = [
                {"qualifier": "prepaid", "evidence_ids": ["R2-F1"]}
            ]

            report = validate_coverage(value, final, base_dir=root)

            mismatches = [
                item
                for item in report["errors"]
                if item["code"] == "qualifier_coverage_mismatch"
            ]
            self.assertEqual(mismatches[0]["missing"], ["urgent"])

    def test_declared_ownership_inference_from_unclaimed_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)
            assertion = value["candidate_relation_assertions"][0]
            assertion["summary"] = "The status proves the envelope is not hers."
            assertion["relation_effect"] = "forbidden_inference"

            report = validate_coverage(value, final, base_dir=root)

            codes = {item["code"] for item in report["errors"]}
            self.assertIn("candidate_assertion_is_forbidden_inference", codes)

    def test_declared_custody_invention_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)
            value["invention_boundaries"] = [
                {
                    "boundary_id": "B1",
                    "source_ids": ["SRC1"],
                    "scope": "ordinary scene action that does not alter locked relations",
                }
            ]
            assertion = value["candidate_relation_assertions"][0]
            assertion.update(
                {
                    "summary": "An invented custody history is attached to the envelope.",
                    "relation_effect": "source_authorized_extension",
                    "authority_kind": "declared_fictional_invention",
                    "invention_id": "I1",
                    "boundary_id": "B1",
                    "invention_basis": "scene invention",
                }
            )
            assertion.pop("authority_ids")

            report = validate_coverage(value, final, base_dir=root)

            codes = {item["code"] for item in report["errors"]}
            self.assertIn("candidate_invention_extends_locked_relation", codes)

    def test_text_edit_invalidates_hash_and_exact_span(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final, value = self._fixture(root)
            final.write_text(
                final.read_text(encoding="utf-8").replace("still", "currently"),
                encoding="utf-8",
                newline="\n",
            )

            report = validate_coverage(value, final, base_dir=root)

            codes = {item["code"] for item in report["errors"]}
            self.assertIn("text_sha256_mismatch", codes)
            self.assertIn("evidence_text_mismatch", codes)


if __name__ == "__main__":
    unittest.main()
