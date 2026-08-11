import hashlib
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_text import validate_bytes  # noqa: E402


class ValidateTextTests(unittest.TestCase):
    def test_exact_hash_and_clean_text(self):
        raw = "标题\n\n这是一个完整的句子。第二个句子也很清楚。\n".encode("utf-8")
        report = validate_bytes(raw)
        self.assertEqual(report["input"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(report["hard_errors"], [])
        self.assertEqual(report["status"], "pass")

    def test_format_and_control_characters_are_hard_errors(self):
        raw = "他说：“好\u200b”。\n".encode("utf-8")
        report = validate_bytes(raw)
        codes = {item["code"] for item in report["hard_errors"]}
        self.assertIn("forbidden_control_or_format_character", codes)

    def test_mismatched_delimiter_is_hard_error(self):
        report = validate_bytes("（未闭合。\n".encode("utf-8"))
        self.assertIn("unbalanced_delimiters", {item["code"] for item in report["hard_errors"]})

    def test_repetition_is_review_warning_not_authorship_finding(self):
        paragraph = "这是一个足够长的段落，用来检查意外重复，而不是判断作者身份；它还包含足够的上下文，避免把短语误当成长段落。"
        report = validate_bytes(f"{paragraph}\n\n{paragraph}\n".encode("utf-8"))
        warning_codes = {item["code"] for item in report["warnings"]}
        self.assertIn("repeated_long_paragraphs", warning_codes)
        self.assertNotIn("ai", " ".join(warning_codes).lower())

    def test_expected_hash_mismatch_fails(self):
        report = validate_bytes(b"plain text\n", expected_sha256="0" * 64)
        self.assertEqual(report["status"], "fail")
        self.assertIn("sha256_mismatch", {item["code"] for item in report["hard_errors"]})


if __name__ == "__main__":
    unittest.main()
