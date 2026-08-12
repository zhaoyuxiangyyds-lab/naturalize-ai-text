from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from hash_skill_tree import build_manifest, main  # noqa: E402


class HashSkillTreeTests(unittest.TestCase):
    def test_manifest_is_stable_and_sorted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "z.txt").write_text("z\n", encoding="utf-8", newline="\n")
            (root / "a.txt").write_text("a\n", encoding="utf-8", newline="\n")
            cache = root / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "ignored.pyc").write_bytes(b"ignored")

            first = build_manifest(root)
            second = build_manifest(root)

            self.assertEqual(first["tree_sha256"], second["tree_sha256"])
            self.assertEqual([item["path"] for item in first["files"]], ["a.txt", "z.txt"])
            self.assertEqual(first["file_count"], 2)

    def test_content_change_changes_tree_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "SKILL.md"
            path.write_text("first\n", encoding="utf-8", newline="\n")
            before = build_manifest(root)["tree_sha256"]
            path.write_text("second\n", encoding="utf-8", newline="\n")
            after = build_manifest(root)["tree_sha256"]
            self.assertNotEqual(before, after)

    def test_expected_hash_mismatch_returns_one(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("text\n", encoding="utf-8", newline="\n")
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main([str(root), "--expect-tree-sha256", "0" * 64])

            self.assertEqual(status, 1)
            self.assertIn('"tree_sha256"', stdout.getvalue())
            self.assertIn("tree hash mismatch", stderr.getvalue())

    def test_internal_output_manifest_is_excluded_and_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("text\n", encoding="utf-8", newline="\n")
            output = root / "tree.json"

            first_status = main([str(root), "--pretty", "--output", str(output)])
            first = output.read_text(encoding="utf-8")
            second_status = main([str(root), "--pretty", "--output", str(output)])
            second = output.read_text(encoding="utf-8")

            self.assertEqual(first_status, 0)
            self.assertEqual(second_status, 0)
            self.assertEqual(first, second)
            self.assertIn('"excluded_paths": [', first)
            self.assertIn('"tree.json"', first)
            self.assertNotIn('"path": "tree.json"', first)

    def test_explicit_exclude_omits_named_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("text\n", encoding="utf-8", newline="\n")
            (root / "generated.json").write_text("{}\n", encoding="utf-8", newline="\n")

            result = build_manifest(root, exclude_paths=["generated.json"])

            self.assertEqual([item["path"] for item in result["files"]], ["SKILL.md"])
            self.assertEqual(result["excluded_paths"], ["generated.json"])


if __name__ == "__main__":
    unittest.main()
