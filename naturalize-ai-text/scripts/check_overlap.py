#!/usr/bin/env python3
"""Find long contiguous overlaps between a candidate and approved anchors.

This is a drafting guard, not a plagiarism detector or an authorship test. It
compares exact decoded text after language-appropriate tokenization and reports
the bytes' SHA-256 values so a review can be reproduced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Sequence


TOOL_NAME = "check-overlap"
TOOL_VERSION = "1.0.1"
_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_WORD_RE = re.compile(r"[^\W_]+(?:['’.-][^\W_]+)*", re.UNICODE)
_LANGUAGES = {"auto", "zh", "en"}


def _read(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    return raw, raw.decode("utf-8-sig")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _detected_language(text: str) -> str:
    han = len(_CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if not han and not latin:
        return "unknown"
    if han and not latin:
        return "zh"
    if latin and not han:
        return "en"
    if han >= latin * 2:
        return "zh"
    if latin >= han * 2:
        return "en"
    return "mixed"


def _language(text: str, requested: str) -> str:
    if requested != "auto":
        return requested
    detected = _detected_language(text)
    if detected in {"zh", "en"}:
        return detected
    han = len(_CJK_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "zh" if han >= latin else "en"


def _require_compatible_language(path: Path, text: str, expected: str, *, role: str) -> str:
    detected = _detected_language(text)
    if detected in {"zh", "en"} and detected != expected:
        raise ValueError(
            f"language mismatch for {role} {path}: expected={expected}, detected={detected}"
        )
    return detected


def _units(text: str, language: str) -> list[str]:
    if language == "zh":
        # Keep only Han characters. This catches copied Chinese wording even
        # when a copied span has harmless differences in spaces or punctuation.
        return _CJK_RE.findall(text)
    return [match.group(0).casefold() for match in _WORD_RE.finditer(text)]


def _display(units: Sequence[str], language: str) -> str:
    return "".join(units) if language == "zh" else " ".join(units)


def _longest_matches(
    candidate: Sequence[str],
    reference: Sequence[str],
    minimum: int,
    language: str,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Return long exact common spans using a minimum-window index.

    Indexing minimum-sized windows avoids a quadratic full-document table. A
    matching window is extended left and right, then duplicate contained spans
    are collapsed so the output stays reviewable.
    """

    if len(candidate) < minimum or len(reference) < minimum:
        return []
    reference_windows: dict[tuple[str, ...], list[int]] = {}
    for reference_start in range(len(reference) - minimum + 1):
        window = tuple(reference[reference_start:reference_start + minimum])
        reference_windows.setdefault(window, []).append(reference_start)

    found_set: set[tuple[int, int, int]] = set()
    for candidate_window_start in range(len(candidate) - minimum + 1):
        window = tuple(candidate[candidate_window_start:candidate_window_start + minimum])
        for reference_window_start in reference_windows.get(window, []):
            candidate_start = candidate_window_start
            reference_start = reference_window_start
            while (
                candidate_start > 0
                and reference_start > 0
                and candidate[candidate_start - 1] == reference[reference_start - 1]
            ):
                candidate_start -= 1
                reference_start -= 1
            length = minimum + (candidate_window_start - candidate_start)
            while (
                candidate_start + length < len(candidate)
                and reference_start + length < len(reference)
                and candidate[candidate_start + length] == reference[reference_start + length]
            ):
                length += 1
            found_set.add((length, candidate_start, reference_start))

    found = list(found_set)

    found.sort(key=lambda item: (-item[0], item[1], item[2]))
    selected: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    for length, candidate_start, reference_start in found:
        candidate_end = candidate_start + length
        if any(candidate_start >= start and candidate_end <= end for start, end in occupied):
            continue
        selected.append(
            {
                "units": length,
                "candidate_start": candidate_start,
                "reference_start": reference_start,
                "text": _display(candidate[candidate_start:candidate_end], language),
            }
        )
        occupied.append((candidate_start, candidate_end))
        if len(selected) >= limit:
            break
    return selected


def _load_allow_file(path: Path | None, language: str) -> set[str]:
    if path is None:
        return set()
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    allowed: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            allowed.add(_display(_units(stripped, language), language))
    return allowed


def _filter_allowed(matches: Iterable[dict[str, Any]], allowed: set[str]) -> list[dict[str, Any]]:
    if not allowed:
        return list(matches)
    return [match for match in matches if match["text"] not in allowed]


def analyze(
    candidate_path: str | Path,
    reference_paths: Iterable[str | Path],
    *,
    language: str = "auto",
    minimum_units: int | None = None,
    allow_path: str | Path | None = None,
) -> dict[str, Any]:
    candidate = Path(candidate_path)
    candidate_raw, candidate_text = _read(candidate)
    resolved_language = _language(candidate_text, language)
    candidate_detected_language = _require_compatible_language(
        candidate,
        candidate_text,
        resolved_language,
        role="candidate",
    )
    minimum = minimum_units if minimum_units is not None else (12 if resolved_language == "zh" else 8)
    if minimum < 2:
        raise ValueError("minimum units must be at least 2")
    candidate_units = _units(candidate_text, resolved_language)
    allowed = _load_allow_file(Path(allow_path) if allow_path else None, resolved_language)
    references: list[dict[str, Any]] = []
    for raw_reference in reference_paths:
        reference = Path(raw_reference)
        reference_raw, reference_text = _read(reference)
        reference_detected_language = _require_compatible_language(
            reference,
            reference_text,
            resolved_language,
            role="reference",
        )
        matches = _longest_matches(
            candidate_units,
            _units(reference_text, resolved_language),
            minimum,
            resolved_language,
        )
        references.append(
            {
                "path": str(reference),
                "sha256": _sha256(reference_raw),
                "detected_language": reference_detected_language,
                "matches": _filter_allowed(matches, allowed),
            }
        )
    remaining = sum(len(item["matches"]) for item in references)
    return {
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "candidate": {"path": str(candidate), "sha256": _sha256(candidate_raw)},
        "language": resolved_language,
        "candidate_detected_language": candidate_detected_language,
        "minimum_units": minimum,
        "allow_file": str(allow_path) if allow_path else None,
        "references": references,
        "match_count": remaining,
        "status": "overlap_found" if remaining else "pass",
        "disclaimer": "A pass does not prove originality or human authorship; review reported spans and source permissions.",
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report long contiguous overlaps with approved reference texts.")
    parser.add_argument("candidate")
    parser.add_argument("--reference", action="append", required=True, dest="references")
    parser.add_argument("--language", choices=sorted(_LANGUAGES), default="auto")
    parser.add_argument("--min-units", type=int)
    parser.add_argument("--allow-file")
    parser.add_argument("--strict", action="store_true", help="return a non-zero status when matches remain")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"{result['status']} ({result['match_count']} matches; language={result['language']}; min_units={result['minimum_units']})",
        f"candidate: {result['candidate']['path']} {result['candidate']['sha256']}",
    ]
    for reference in result["references"]:
        lines.append(f"reference: {reference['path']} {reference['sha256']}")
        for match in reference["matches"]:
            lines.append(f"  {match['units']} units: {match['text']}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = analyze(
            args.candidate,
            args.references,
            language=args.language,
            minimum_units=args.min_units,
            allow_path=args.allow_file,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    else:
        sys.stdout.write(_render_text(result))
    return 1 if args.strict and result["match_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
