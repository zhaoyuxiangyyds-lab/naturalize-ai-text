#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest for a skill directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence


TOOL_NAME = "hash-skill-tree"
TOOL_VERSION = "1.0.0"


def _included(path: Path, excluded: set[Path]) -> bool:
    return (
        path.is_file()
        and path.resolve() not in excluded
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
    )


def _resolve_excludes(root: Path, values: Iterable[str | Path]) -> set[Path]:
    excluded: set[Path] = set()
    for value in values:
        path = Path(value)
        resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"excluded path is outside the skill directory: {resolved}") from exc
        excluded.add(resolved)
    return excluded


def build_manifest(
    root_path: str | Path,
    *,
    exclude_paths: Iterable[str | Path] = (),
) -> dict[str, Any]:
    root = Path(root_path).resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    excluded = _resolve_excludes(root, exclude_paths)
    files: list[dict[str, Any]] = []
    canonical_lines: list[str] = []
    for path in sorted(
        (item for item in root.rglob("*") if _included(item, excluded)),
        key=lambda item: item.as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        files.append({"path": relative, "bytes": len(raw), "sha256": digest})
        canonical_lines.append(f"{digest}  {relative}")
    manifest_bytes = (("\n".join(canonical_lines) + "\n") if canonical_lines else "").encode("utf-8")
    return {
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "root": str(root),
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "tree_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "canonical_manifest": (
            "sha256 + two spaces + POSIX relative path + LF; sorted by relative path; "
            "excludes __pycache__, .pyc, and requested output/exclude paths"
        ),
        "excluded_paths": sorted(
            path.relative_to(root).as_posix() for path in excluded
        ),
        "files": files,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hash a skill tree with a deterministic per-file manifest.")
    parser.add_argument("skill_dir")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--expect-tree-sha256")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("-o", "--output")
    return parser.parse_args(argv)


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"tree_sha256 {result['tree_sha256']}",
        f"file_count {result['file_count']}",
        f"total_bytes {result['total_bytes']}",
    ]
    lines.extend(f"{item['sha256']}  {item['path']}" for item in result["files"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = Path(args.skill_dir).resolve()
        excludes = list(args.exclude)
        if args.output:
            output_path = Path(args.output)
            resolved_output = (
                output_path.resolve()
                if output_path.is_absolute()
                else (Path.cwd() / output_path).resolve()
            )
            try:
                relative_output = resolved_output.relative_to(root)
            except ValueError:
                pass
            else:
                excludes.append(relative_output)
        result = build_manifest(args.skill_dir, exclude_paths=excludes)
    except (OSError, ValueError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    rendered = (
        json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n"
        if args.format == "json"
        else _render_text(result)
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)
    if args.expect_tree_sha256 and result["tree_sha256"].casefold() != args.expect_tree_sha256.casefold():
        print(
            f"{TOOL_NAME}: tree hash mismatch: expected {args.expect_tree_sha256}, got {result['tree_sha256']}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
