from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_texture.py"
SPEC = importlib.util.spec_from_file_location("analyze_texture", SCRIPT)
assert SPEC and SPEC.loader
analyze_texture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analyze_texture)


class AnalyzeTextureTests(unittest.TestCase):
    def test_empty_text(self) -> None:
        report = analyze_texture.analyze_text("")
        self.assertEqual(report["counts"]["sentences"], 0)
        self.assertEqual(report["counts"]["paragraphs"], 0)
        self.assertIsNone(report["sentence_lengths"]["mean"])
        self.assertIn("sample_too_small", [flag["code"] for flag in report["review_flags"]])

    def test_chinese_sentence_splitting_keeps_closing_quotes(self) -> None:
        paragraphs = analyze_texture.split_paragraphs(
            "\u7532\u95ee\uff1a\u201c\u53bb\u5417\uff1f\u201d\u4e59\u7b54\uff1a\u201c\u53bb\u3002\u201d\u540e\u6765\u4e0b\u96e8\u4e86\u3002"
        )
        sentences = analyze_texture.extract_sentences(paragraphs)
        self.assertEqual(len(sentences), 3)
        self.assertTrue(sentences[0].endswith("\uff1f\u201d"))
        self.assertTrue(sentences[1].endswith("\u3002\u201d"))

    def test_english_abbreviation_and_decimal(self) -> None:
        report = analyze_texture.analyze_text(
            "Dr. Li measured 3.14 units. The result was stable.", language="en"
        )
        self.assertEqual(report["counts"]["sentences"], 2)
        self.assertEqual(report["counts"]["number_tokens"], 1)

    def test_nfkc_and_casefold_duplicate_sentence(self) -> None:
        report = analyze_texture.analyze_text(
            "\uff21 plan works today. A PLAN WORKS TODAY!", language="en"
        )
        groups = report["duplicates"]["groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["count"], 2)

    def test_chinese_repeated_ngram(self) -> None:
        report = analyze_texture.analyze_text(
            "\u6625\u98ce\u53c8\u7eff\u6c5f\u5357\u5cb8\u3002\u4eca\u591c\u6625\u98ce\u53c8\u7eff\u6c5f\u5357\u5cb8\u3002",
            language="zh",
        )
        grams = report["repetition"]["ngrams"]["top_ngrams"]
        repeated = next(item for item in grams if item["ngram"] == "\u6625\u98ce\u53c8\u7eff\u6c5f\u5357\u5cb8")
        self.assertEqual(repeated["n"], 7)
        self.assertEqual(repeated["sentence_span"], 2)

    def test_english_repeated_ngram(self) -> None:
        report = analyze_texture.analyze_text(
            "The model follows a clear process. The team follows a clear process.",
            language="en",
        )
        phrases = {item["ngram"] for item in report["repetition"]["ngrams"]["top_ngrams"]}
        self.assertIn("follows a clear process", phrases)

    def test_chinese_ngram_does_not_cross_punctuation(self) -> None:
        report = analyze_texture.analyze_text("\u7532\u4e59\uff0c\u4e19\u4e01\u3002\u7532\u4e59\u4e19\u4e01\u3002", language="zh")
        phrases = {item["ngram"] for item in report["repetition"]["ngrams"]["top_ngrams"]}
        self.assertNotIn("\u4e59\u4e19\u4e01", phrases)

    def test_repeated_sentence_openers(self) -> None:
        text = "".join(
            [
                "\u9996\u5148\u6211\u4eec\u5206\u6790\u7532\u3002",
                "\u9996\u5148\u6211\u4eec\u5206\u6790\u4e59\u3002",
                "\u9996\u5148\u6211\u4eec\u5206\u6790\u4e19\u3002",
                "\u5176\u6b21\u53ef\u4ee5\u8ba8\u8bba\u4e01\u3002",
                "\u7136\u540e\u8fd8\u8981\u8ba8\u8bba\u620a\u3002",
                "\u6570\u636e\u672c\u8eab\u9700\u8981\u590d\u6838\u3002",
                "\u7ed3\u8bba\u5c1a\u5f85\u8865\u5145\u8bba\u8bc1\u3002",
                "\u9644\u5f55\u5217\u51fa\u4e86\u539f\u59cb\u503c\u3002",
            ]
        )
        report = analyze_texture.analyze_text(text, language="zh")
        groups = report["repetition"]["openers"]["groups"]
        self.assertEqual(groups[0]["opener"], "\u9996\u5148\u6211\u4eec")
        self.assertEqual(groups[0]["count"], 3)

    def test_longest_transition_match_wins(self) -> None:
        profile = analyze_texture.transition_profile(
            ["\u53e6\u4e00\u65b9\u9762\uff0c\u8fd9\u4e2a\u7ed3\u679c\u4ecd\u9700\u590d\u6838\u3002"], "zh", 15
        )
        self.assertEqual(profile["total"], 1)
        self.assertEqual(profile["by_phrase"][0]["phrase"], "\u53e6\u4e00\u65b9\u9762")

    def test_paragraph_modes(self) -> None:
        text = "First line.\nSecond line."
        self.assertEqual(len(analyze_texture.split_paragraphs(text, "blank")), 1)
        self.assertEqual(len(analyze_texture.split_paragraphs(text, "line")), 2)

    def test_heading_and_list_density(self) -> None:
        profile = analyze_texture.structure_profile("# \u6807\u9898\n\n1. \u7b2c\u4e00\u9879\n2. \u7b2c\u4e8c\u9879")
        self.assertEqual(profile["heading_lines"], 3)
        self.assertEqual(profile["list_lines"], 2)
        self.assertEqual(profile["structured_lines"], 3)

    def test_ellipsis_is_one_occurrence(self) -> None:
        profile = analyze_texture.punctuation_profile("\u7b49\u7b49\u2026\u2026\u771f\u7684\uff1f\uff01")
        self.assertEqual(profile["counts"]["ellipsis"], 1)
        self.assertEqual(profile["counts"]["question"], 1)
        self.assertEqual(profile["counts"]["exclamation"], 1)
        self.assertEqual(sum(profile["counts"].values()), profile["total"])

    def test_json_cli_is_byte_deterministic(self) -> None:
        text = "A varied sentence appears here. Another sentence is shorter."
        command = [sys.executable, str(SCRIPT), "-", "--language", "en", "--format", "json"]
        first = subprocess.run(command, input=text.encode(), stdout=subprocess.PIPE, check=True)
        second = subprocess.run(command, input=text.encode(), stdout=subprocess.PIPE, check=True)
        self.assertEqual(first.stdout, second.stdout)
        payload = json.loads(first.stdout)
        self.assertFalse(payload["disclaimer"]["authorship_inference"])
        serialized = first.stdout.decode().casefold()
        self.assertNotIn("ai_score", serialized)
        self.assertNotIn("human_score", serialized)
        self.assertNotIn("probability_of_ai", serialized)

    def test_output_file_is_valid_utf8_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.txt"
            output_path = Path(directory) / "report.json"
            input_path.write_text("\u8fd9\u662f\u4e00\u6bb5\u7b80\u77ed\u6587\u672c\u3002", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(input_path),
                    "--format",
                    "json",
                    "--pretty",
                    "-o",
                    str(output_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["input"]["language_detected"], "zh")


if __name__ == "__main__":
    unittest.main()
