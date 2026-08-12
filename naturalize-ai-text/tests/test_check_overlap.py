import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from check_overlap import analyze, main  # noqa: E402


class CheckOverlapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def _write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def test_chinese_long_span_is_reported(self):
        candidate = self._write("candidate-zh.txt", "开头。校园服务需要保留清晰可达的人工纠错渠道，不能把失败留给使用者。结尾。")
        reference = self._write("anchor-zh.txt", "说明。校园服务需要保留清晰可达的人工纠错渠道，不能把失败留给使用者。结束。")

        result = analyze(candidate, [reference], language="zh", minimum_units=12)

        self.assertEqual(result["status"], "overlap_found")
        self.assertGreater(result["match_count"], 0)
        self.assertIn("校园服务需要保留清晰可达", result["references"][0]["matches"][0]["text"])
        self.assertEqual(len(result["candidate"]["sha256"]), 64)

    def test_english_match_keeps_word_boundaries(self):
        candidate = self._write("candidate-en.txt", "A checklist helps people remember the few steps that matter most.")
        reference = self._write("anchor-en.txt", "A checklist helps people remember the few steps that matter most under pressure.")

        result = analyze(candidate, [reference], language="en", minimum_units=8)

        self.assertEqual(result["status"], "overlap_found")
        self.assertIn("checklist helps people remember", result["references"][0]["matches"][0]["text"])

    def test_unrelated_text_passes(self):
        candidate = self._write("candidate.txt", "A newly selected example changes the reader's question.")
        reference = self._write("anchor.txt", "The original example describes a different question entirely.")
        result = analyze(candidate, [reference], language="en", minimum_units=6)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["match_count"], 0)

    def test_allow_file_clears_an_existing_exact_match(self):
        copied = self._write("copied.txt", "A checklist helps people remember the few steps that matter most.")
        matching_reference = self._write(
            "matching-anchor.txt",
            "A checklist helps people remember the few steps that matter most under pressure.",
        )
        without_allow = analyze(copied, [matching_reference], language="en", minimum_units=6)
        self.assertEqual(without_allow["status"], "overlap_found")
        self.assertGreater(without_allow["match_count"], 0)

        allow = self._write("allow.txt", "A checklist helps people remember the few steps that matter most")
        allowed_result = analyze(copied, [matching_reference], language="en", minimum_units=6, allow_path=allow)
        self.assertEqual(allowed_result["status"], "pass")
        self.assertEqual(allowed_result["match_count"], 0)

    def test_explicit_language_rejects_reference_in_another_language(self):
        candidate = self._write("candidate-zh.txt", "这是一段用于检查参考材料语言的中文说明文字。")
        reference = self._write(
            "anchor-en.txt",
            "This reference is clearly written in English and should not be treated as Chinese.",
        )

        with self.assertRaisesRegex(ValueError, "language mismatch for reference"):
            analyze(candidate, [reference], language="zh", minimum_units=6)

    def test_strict_cli_returns_failure_for_match(self):
        candidate = self._write("candidate.txt", "A checklist helps people remember the few steps that matter most.")
        reference = self._write("anchor.txt", "A checklist helps people remember the few steps that matter most under pressure.")
        output = self.root / "result.json"

        old_stdout = sys.stdout
        try:
            from io import StringIO

            sys.stdout = StringIO()
            status = main(
                [
                    str(candidate),
                    "--reference",
                    str(reference),
                    "--language",
                    "en",
                    "--min-units",
                    "8",
                    "--strict",
                    "--format",
                    "json",
                ]
            )
            rendered = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(status, 1)
        self.assertEqual(json.loads(rendered)["status"], "overlap_found")

    def test_long_chinese_inputs_complete_and_find_embedded_span(self):
        prefix = "甲乙丙丁戊己庚辛壬癸" * 120
        copied = "这段连续文字用于确认长篇内容里的重合仍然能够被准确发现"
        candidate = self._write("long-candidate.txt", prefix + copied + "终点")
        reference = self._write("long-anchor.txt", ("春夏秋冬东西南北" * 150) + copied + "结束")

        result = analyze(candidate, [reference], language="zh", minimum_units=12)

        self.assertEqual(result["status"], "overlap_found")
        self.assertTrue(any(copied in match["text"] for match in result["references"][0]["matches"]))


if __name__ == "__main__":
    unittest.main()
