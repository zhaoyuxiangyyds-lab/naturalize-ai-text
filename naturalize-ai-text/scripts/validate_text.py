#!/usr/bin/env python3
"""Deterministic exact-input and surface-integrity checks.

This module is a hard-gate aid, not an AI-authorship detector, spellchecker, or
continuity checker. It reports the exact byte hash plus reviewable hazards.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from typing import Any, Sequence


TOOL_NAME = "validate-text"
TOOL_VERSION = "2.0.0"
SCHEMA_VERSION = "1.0"
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_RE = re.compile(r"[A-Za-z]")
WORD_RE = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")

ABBREVIATIONS = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "sr",
    "jr",
    "st",
    "vs",
    "etc",
    "no",
    "fig",
    "inc",
    "corp",
}
CLOSING_MARKS = set("\"'\u2019\u201d\u3009\u300b\u300d\u300f\u3011\u3015\u3017\u3019\u301b)]}")
SENTENCE_ENDS = set(".!?\u3002\uff01\uff1f")

OPEN_TO_CLOSE = {
    "(": ")",
    "[": "]",
    "{": "}",
    "（": "）",
    "［": "］",
    "｛": "｝",
    "【": "】",
    "〔": "〕",
    "〈": "〉",
    "《": "》",
    "「": "」",
    "『": "』",
    "“": "”",
    "‘": "’",
}
CLOSE_TO_OPEN = {close: open_ for open_, close in OPEN_TO_CLOSE.items()}
# ASCII apostrophes are ambiguous in contractions and possessives, so an odd
# count is not reliable evidence of an unmatched quotation mark.
SYMMETRIC_QUOTES = {'"', "`"}
SUSPICIOUS_SPACES = {
    "\u00a0": "NO-BREAK SPACE",
    "\u1680": "OGHAM SPACE MARK",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR",
    "\u2000": "EN QUAD",
    "\u2001": "EM QUAD",
    "\u2002": "EN SPACE",
    "\u2003": "EM SPACE",
    "\u2004": "THREE-PER-EM SPACE",
    "\u2005": "FOUR-PER-EM SPACE",
    "\u2006": "SIX-PER-EM SPACE",
    "\u2007": "FIGURE SPACE",
    "\u2008": "PUNCTUATION SPACE",
    "\u2009": "THIN SPACE",
    "\u200a": "HAIR SPACE",
    "\u202f": "NARROW NO-BREAK SPACE",
    "\u205f": "MEDIUM MATHEMATICAL SPACE",
}
COMMON_COMPATIBILITY_FORMS = set("，。！？；：、（）［］｛｝【】《》〈〉“”‘’「」『』")


def _content_char(char: str) -> bool:
    return unicodedata.category(char)[0] in {"L", "N"}


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n[ \t]*\n+", text.strip()) if part.strip()]


def _period_is_boundary(text: str, index: int) -> bool:
    previous = text[index - 1] if index else ""
    following = text[index + 1] if index + 1 < len(text) else ""
    if previous.isdigit() and following.isdigit():
        return False
    if text[index : index + 3] == "...":
        return True

    before = text[:index]
    token_match = re.search(r"([A-Za-z]+)$", before)
    token = token_match.group(1).casefold() if token_match else ""
    if token in ABBREVIATIONS:
        return False
    dotted = text[max(0, index - 12) : index + 1]
    if re.search(r"(?:[A-Za-z]\.){2,}$", dotted):
        return False

    next_nonspace = ""
    for character in text[index + 1 :]:
        if character not in CLOSING_MARKS and not character.isspace():
            next_nonspace = character
            break
    if len(token) == 1 and next_nonspace.isupper():
        return False
    return True


def _sentences(text: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    index = 0
    while index < len(text):
        character = text[index]
        if character not in SENTENCE_ENDS:
            index += 1
            continue
        if character == "." and not _period_is_boundary(text, index):
            index += 1
            continue

        end = index + 1
        while end < len(text) and text[end] in SENTENCE_ENDS:
            end += 1
        while end < len(text) and text[end] in CLOSING_MARKS:
            end += 1
        fragment = text[start:end].strip()
        if fragment and any(_content_char(char) for char in fragment):
            sentences.append(fragment)
        start = end
        index = end

    tail = text[start:].strip()
    if tail and any(_content_char(char) for char in tail):
        sentences.append(tail)
    return sentences


def _normalized_for_duplicate(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip().casefold()


def _duplicate_groups(values: list[str], minimum_units: int) -> list[dict[str, Any]]:
    groups: dict[str, list[int]] = {}
    examples: dict[str, str] = {}
    for index, value in enumerate(values, start=1):
        compact = _normalized_for_duplicate(value)
        if len(compact) < minimum_units:
            continue
        groups.setdefault(compact, []).append(index)
        examples.setdefault(compact, value)
    result = []
    for compact, indices in groups.items():
        if len(indices) > 1:
            result.append({
                "count": len(indices),
                "indices": indices,
                "preview": re.sub(r"\s+", " ", examples[compact])[:120],
            })
    return sorted(result, key=lambda item: (-item["count"], item["indices"][0]))


def _delimiter_check(text: str) -> list[dict[str, Any]]:
    stack: list[tuple[str, int]] = []
    issues: list[dict[str, Any]] = []
    for position, char in enumerate(text, start=1):
        if char in OPEN_TO_CLOSE:
            stack.append((char, position))
        elif char in CLOSE_TO_OPEN:
            expected = CLOSE_TO_OPEN[char]
            if not stack or stack[-1][0] != expected:
                issues.append({"position": position, "character": char, "kind": "unexpected_close"})
            else:
                stack.pop()
    for opening, position in reversed(stack):
        issues.append({"position": position, "character": opening, "kind": "unclosed_open"})

    for quote in SYMMETRIC_QUOTES:
        count = text.count(quote)
        if count % 2:
            issues.append({"character": quote, "count": count, "kind": "odd_symmetric_quote_count"})
    return issues


def validate_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    minimum_content: int | None = None,
    maximum_content: int | None = None,
) -> dict[str, Any]:
    sha256 = hashlib.sha256(raw).hexdigest()
    hard_errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    try:
        text = raw.decode("utf-8-sig")
        decode_error = None
    except UnicodeDecodeError as exc:
        text = raw.decode("utf-8", errors="replace")
        decode_error = str(exc)
        hard_errors.append({"code": "invalid_utf8", "message": decode_error})

    leading_bom = raw.startswith(b"\xef\xbb\xbf")
    if leading_bom:
        warnings.append({"code": "leading_bom", "message": "UTF-8 BOM is present; preserve it only if the target format requires it."})

    forbidden: list[dict[str, Any]] = []
    suspicious_spaces: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    for position, char in enumerate(text, start=1):
        category = unicodedata.category(char)
        category_counts[category] += 1
        if category == "Cf" or (category.startswith("C") and char not in {"\n", "\r", "\t"}):
            forbidden.append({
                "position": position,
                "codepoint": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "UNKNOWN"),
                "category": category,
            })
        if char in SUSPICIOUS_SPACES:
            suspicious_spaces.append({
                "position": position,
                "codepoint": f"U+{ord(char):04X}",
                "name": SUSPICIOUS_SPACES[char],
            })
    if forbidden:
        hard_errors.append({"code": "forbidden_control_or_format_character", "items": forbidden})
    if suspicious_spaces:
        warnings.append({"code": "unusual_whitespace", "items": suspicious_spaces})

    normalized = unicodedata.normalize("NFKC", text)
    changed_characters = [char for char in text if unicodedata.normalize("NFKC", char) != char]
    if normalized != text and any(char not in COMMON_COMPATIBILITY_FORMS for char in changed_characters):
        warnings.append({"code": "nfkc_changes_text", "message": "NFKC normalization would change one or more nonstandard compatibility forms; review mixed-width or compatibility characters."})

    delimiter_issues = _delimiter_check(text)
    if delimiter_issues:
        hard_errors.append({"code": "unbalanced_delimiters", "items": delimiter_issues})

    content_count = sum(1 for char in text if _content_char(char))
    if minimum_content is not None and content_count < minimum_content:
        warnings.append({"code": "below_minimum_content", "value": content_count, "minimum": minimum_content})
    if maximum_content is not None and content_count > maximum_content:
        warnings.append({"code": "above_maximum_content", "value": content_count, "maximum": maximum_content})

    paragraphs = _paragraphs(text)
    sentences = _sentences(text)
    duplicate_paragraphs = _duplicate_groups(paragraphs, 40)
    duplicate_sentences = _duplicate_groups(sentences, 20)
    if duplicate_paragraphs:
        warnings.append({"code": "repeated_long_paragraphs", "groups": duplicate_paragraphs, "message": "Review for accidental duplication; refrains may be intentional."})
    if duplicate_sentences:
        warnings.append({"code": "repeated_sentences", "groups": duplicate_sentences, "message": "Review for accidental repetition; quotations and refrains may be intentional."})

    text_no_bom = text
    counts = {
        "bytes": len(raw),
        "characters": len(text_no_bom),
        "non_whitespace_characters": sum(1 for char in text_no_bom if not char.isspace()),
        "content_characters": content_count,
        "han_characters": len(HAN_RE.findall(text_no_bom)),
        "latin_characters": len(LATIN_RE.findall(text_no_bom)),
        "english_words": len(WORD_RE.findall(text_no_bom)),
        "lines": len(text_no_bom.splitlines()),
        "paragraphs": len(paragraphs),
        "sentences_estimate": len(sentences),
    }
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "disclaimer": "Hard-gate and review aids only; this report does not detect AI authorship or prove human authorship.",
        "input": {
            "sha256": sha256,
            "expected_sha256": expected_sha256,
            "sha256_matches_expected": expected_sha256 is None or sha256.casefold() == expected_sha256.casefold(),
            "leading_bom": leading_bom,
            "decode_error": decode_error,
        },
        "counts": counts,
        "unicode_category_counts": dict(sorted(category_counts.items())),
        "hard_errors": hard_errors,
        "warnings": warnings,
        "manual_checks_required": [
            "facts, citations, names, numbers, and source fidelity",
            "spelling and Chinese near-form/homophone substitutions",
            "grammar, reference, and terminology",
            "argument validity or narrative continuity",
            "genre and voice fit",
            "required AI disclosure and destination rules",
        ],
        "status": "fail" if hard_errors else ("review" if warnings else "pass"),
    }
    if expected_sha256 is not None and not result["input"]["sha256_matches_expected"]:
        result["hard_errors"].append({"code": "sha256_mismatch", "expected": expected_sha256, "actual": sha256})
        result["status"] = "fail"
    return result


def validate_file(path: str | Path, **kwargs: Any) -> dict[str, Any]:
    return validate_bytes(Path(path).read_bytes(), **kwargs)


def _format_report(report: dict[str, Any]) -> str:
    lines = [
        "TEXT VALIDATION ONLY",
        report["disclaimer"],
        f"SHA-256: {report['input']['sha256']}",
        f"Status: {report['status']}",
        f"Counts: {report['counts']}",
        f"Hard errors: {len(report['hard_errors'])}",
        f"Warnings: {len(report['warnings'])}",
        "",
        "Hard errors:",
    ]
    lines.extend(f"- {item}" for item in report["hard_errors"] or ["None"])
    lines.append("Warnings:")
    lines.extend(f"- {item}" for item in report["warnings"] or ["None"])
    lines.append("Manual checks required:")
    lines.extend(f"- {item}" for item in report["manual_checks_required"])
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate exact text bytes and surface hazards; not an AI detector.")
    parser.add_argument("input", help="UTF-8 text file")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--minimum-content", type=int)
    parser.add_argument("--maximum-content", type=int)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when hard errors are present")
    parser.add_argument("-o", "--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_file(
            args.input,
            expected_sha256=args.expected_sha256,
            minimum_content=args.minimum_content,
            maximum_content=args.maximum_content,
        )
    except OSError as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        output = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    else:
        output = _format_report(report)
    try:
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(output)
    except OSError as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    return 1 if args.strict and report["hard_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
