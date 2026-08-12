#!/usr/bin/env python3
"""Deterministic surface descriptions for Chinese and English text.

This tool reports repetition, rhythm, punctuation, and document structure. It
does not detect AI authorship, prescribe a target distribution, or produce an
AI/human score.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
import unicodedata
from typing import Any, Iterable, Sequence


TOOL_NAME = "analyze-texture"
TOOL_VERSION = "1.3.0"
SCHEMA_VERSION = "1.2"

GENRES = (
    "general",
    "fiction",
    "essay",
    "academic",
    "technical",
    "report",
    "explanation",
    "argument",
    "speech",
    "poetry",
    "mixed",
)

HAN_PATTERN = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
HAN_RE = re.compile(f"[{HAN_PATTERN}]")
HAN_RUN_RE = re.compile(f"[{HAN_PATTERN}]+")
EN_WORD_RE = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")
EN_TOKEN_RE = re.compile(
    r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*|\d+(?:\.\d+)?"
)
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

ZH_TRANSITIONS = (
    "值得注意的是",
    "需要指出的是",
    "与此同时",
    "相较之下",
    "综上所述",
    "尽管如此",
    "另一方面",
    "一方面",
    "由此可见",
    "换言之",
    "基于此",
    "首先",
    "其次",
    "再次",
    "最后",
    "此外",
    "另外",
    "同时",
    "因此",
    "所以",
    "然而",
    "但是",
    "不过",
    "总之",
    "例如",
    "比如",
    "从而",
)

EN_TRANSITIONS = (
    "it is important to note",
    "it should be noted",
    "on the other hand",
    "on the one hand",
    "in conclusion",
    "in addition",
    "in summary",
    "for example",
    "for instance",
    "as a result",
    "by contrast",
    "to conclude",
    "nevertheless",
    "nonetheless",
    "furthermore",
    "additionally",
    "consequently",
    "meanwhile",
    "moreover",
    "therefore",
    "however",
    "finally",
    "firstly",
    "secondly",
    "overall",
    "hence",
    "thus",
)

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



def _rounded(value: float | None) -> float | None:
    if value is None:
        return None
    result = round(float(value), 6)
    return 0.0 if result == -0.0 else result


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return 0.0
    return _rounded(float(numerator) / float(denominator)) or 0.0


def normalize_text(text: str) -> str:
    text = text.removeprefix("\ufeff")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFKC", text)


def is_content_character(character: str) -> bool:
    return unicodedata.category(character)[:1] in {"L", "N"}


def content_character_count(text: str) -> int:
    return sum(1 for character in text if is_content_character(character))


def language_profile(text: str, requested: str = "auto") -> dict[str, Any]:
    han_count = len(HAN_RE.findall(text))
    latin_count = sum(1 for char in text if char.isascii() and char.isalpha())
    signal_total = han_count + latin_count
    han_share = _ratio(han_count, signal_total)
    latin_share = _ratio(latin_count, signal_total)

    if requested != "auto":
        detected = requested
    elif signal_total == 0:
        detected = "unknown"
    elif han_share >= 0.30:
        detected = "zh"
    else:
        detected = "en"

    return {
        "requested": requested,
        "detected": detected,
        "signal_characters": signal_total,
        "han_share": han_share,
        "latin_share": latin_share,
    }


def split_paragraphs(text: str, mode: str = "blank") -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    if mode == "line":
        return [line.strip() for line in stripped.splitlines() if line.strip()]
    return [
        block.strip()
        for block in re.split(r"\n[ \t]*\n+", stripped)
        if block.strip()
    ]


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


def split_sentences(block: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    index = 0
    while index < len(block):
        character = block[index]
        if character not in SENTENCE_ENDS:
            index += 1
            continue
        if character == "." and not _period_is_boundary(block, index):
            index += 1
            continue

        end = index + 1
        while end < len(block) and block[end] in SENTENCE_ENDS:
            end += 1
        while end < len(block) and block[end] in CLOSING_MARKS:
            end += 1
        fragment = block[start:end].strip()
        if fragment and content_character_count(fragment):
            sentences.append(fragment)
        start = end
        index = end

    tail = block[start:].strip()
    if tail and content_character_count(tail):
        sentences.append(tail)
    return sentences


def extract_sentences(paragraphs: Sequence[str]) -> list[str]:
    sentences: list[str] = []
    for paragraph in paragraphs:
        sentences.extend(split_sentences(paragraph))
    return sentences


def english_tokens(text: str) -> list[str]:
    return [match.group(0).casefold() for match in EN_TOKEN_RE.finditer(text)]


def analysis_length(text: str, language: str) -> int:
    if language == "en":
        return len(english_tokens(text))
    return content_character_count(text)


def summary_stats(values: Sequence[int]) -> dict[str, Any]:
    if not values:
        return {
            "values": [],
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "pstdev": None,
            "cv": None,
        }
    mean = statistics.fmean(values)
    deviation = statistics.pstdev(values)
    return {
        "values": list(values),
        "min": min(values),
        "max": max(values),
        "mean": _rounded(mean),
        "median": _rounded(statistics.median(values)),
        "pstdev": _rounded(deviation),
        "cv": _rounded(deviation / mean) if mean else None,
    }


def _normalized_sentence(sentence: str, language: str) -> str:
    normalized = normalize_text(sentence).casefold()
    if language == "en":
        return " ".join(english_tokens(normalized))
    return "".join(char for char in normalized if is_content_character(char))


def _preview(text: str, limit: int = 120) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def duplicate_profile(sentences: Sequence[str], language: str) -> dict[str, Any]:
    minimum_length = 4 if language == "en" else 6
    grouped: dict[str, list[int]] = defaultdict(list)
    examples: dict[str, str] = {}
    for index, sentence in enumerate(sentences, start=1):
        if analysis_length(sentence, language) < minimum_length:
            continue
        normalized = _normalized_sentence(sentence, language)
        grouped[normalized].append(index)
        examples.setdefault(normalized, sentence)

    repeated = [
        (normalized, indices)
        for normalized, indices in grouped.items()
        if len(indices) >= 2
    ]
    repeated.sort(key=lambda item: (-len(item[1]), item[1][0], item[0]))
    groups = [
        {
            "normalized": normalized,
            "count": len(indices),
            "sentence_indices": indices,
            "example": _preview(examples[normalized]),
        }
        for normalized, indices in repeated
    ]
    excess = sum(group["count"] - 1 for group in groups)
    return {
        "minimum_length_units": minimum_length,
        "group_count": len(groups),
        "excess_count": excess,
        "excess_ratio": _ratio(excess, len(sentences)),
        "groups": groups,
    }


def _sentence_ngram_segments(sentence: str, language: str) -> list[list[str]]:
    if language == "en":
        return [english_tokens(sentence)]
    return [list(run) for run in HAN_RUN_RE.findall(normalize_text(sentence))]


def _contains_sequence(longer: Sequence[str], shorter: Sequence[str]) -> bool:
    if len(shorter) > len(longer):
        return False
    width = len(shorter)
    return any(tuple(longer[pos : pos + width]) == tuple(shorter) for pos in range(len(longer) - width + 1))


def ngram_profile(
    sentences: Sequence[str],
    language: str,
    analysis_units: int,
    minimum_occurrences: int = 2,
    top: int = 20,
) -> dict[str, Any]:
    locations: dict[int, dict[tuple[str, ...], list[tuple[int, int, int]]]] = {
        size: defaultdict(list) for size in range(3, 9)
    }
    for sentence_index, sentence in enumerate(sentences):
        for segment_index, units in enumerate(_sentence_ngram_segments(sentence, language)):
            for size in range(3, 9):
                for start in range(0, len(units) - size + 1):
                    gram = tuple(units[start : start + size])
                    locations[size][gram].append((sentence_index, segment_index, start))

    candidates: list[dict[str, Any]] = []
    repeated_positions: set[tuple[int, int, int]] = set()
    candidate_count_by_n: dict[str, int] = {}
    for size in range(3, 9):
        size_candidates = 0
        for units, positions in locations[size].items():
            if len(positions) < minimum_occurrences:
                continue
            size_candidates += 1
            sentence_set = tuple(sorted({position[0] for position in positions}))
            for sentence_index, segment_index, start in positions:
                for offset in range(size):
                    repeated_positions.add((sentence_index, segment_index, start + offset))
            candidates.append(
                {
                    "units": units,
                    "n": size,
                    "positions": positions,
                    "sentence_set": sentence_set,
                    "occurrences": len(positions),
                    "excess_unit_coverage": (len(positions) - 1) * size,
                }
            )
        candidate_count_by_n[str(size)] = size_candidates

    maximal: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda item: (-item["n"], item["units"])):
        suppressed = any(
            longer["n"] > candidate["n"]
            and longer["occurrences"] == candidate["occurrences"]
            and longer["sentence_set"] == candidate["sentence_set"]
            and _contains_sequence(longer["units"], candidate["units"])
            for longer in candidates
        )
        if not suppressed:
            maximal.append(candidate)

    maximal.sort(
        key=lambda item: (
            -item["excess_unit_coverage"],
            -item["n"],
            -item["occurrences"],
            item["positions"][0],
            item["units"],
        )
    )
    long_size = 4 if language == "en" else 6
    long_group_count = sum(1 for item in maximal if item["n"] >= long_size)

    def display(item: dict[str, Any]) -> dict[str, Any]:
        separator = " " if language == "en" else ""
        return {
            "ngram": separator.join(item["units"]),
            "n": item["n"],
            "occurrences": item["occurrences"],
            "sentence_span": len(item["sentence_set"]),
            "sentence_indices": [index + 1 for index in item["sentence_set"]],
            "excess_unit_coverage": item["excess_unit_coverage"],
        }

    return {
        "ngram_unit": "word" if language == "en" else "character",
        "ngram_range": [3, 8],
        "minimum_occurrences": minimum_occurrences,
        "candidate_count_by_n": candidate_count_by_n,
        "repeated_unit_coverage": _ratio(len(repeated_positions), analysis_units),
        "long_ngram_size": long_size,
        "long_repeated_group_count": long_group_count,
        "top_ngrams": [display(item) for item in maximal[:top]],
    }


def opener_profile(sentences: Sequence[str], language: str) -> dict[str, Any]:
    width = 3 if language == "en" else 4
    grouped: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, sentence in enumerate(sentences, start=1):
        if language == "en":
            units = english_tokens(sentence)
        else:
            units = [char for char in normalize_text(sentence) if is_content_character(char)]
        if len(units) >= width:
            grouped[tuple(units[:width])].append(index)

    repeated = [(units, indices) for units, indices in grouped.items() if len(indices) >= 2]
    repeated.sort(key=lambda item: (-len(item[1]), item[1][0], item[0]))
    covered = {index for _, indices in repeated for index in indices}
    separator = " " if language == "en" else ""
    return {
        "unit_size": width,
        "repeated_sentence_coverage": _ratio(len(covered), len(sentences)),
        "groups": [
            {
                "opener": separator.join(units),
                "count": len(indices),
                "sentence_indices": indices,
            }
            for units, indices in repeated
        ],
    }


def _transition_matches(text: str, language: str) -> list[tuple[int, int, str]]:
    matches: list[tuple[int, int, str]] = []
    if language == "en":
        for phrase in EN_TRANSITIONS:
            pattern = re.compile(
                r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])",
                re.IGNORECASE,
            )
            matches.extend((match.start(), match.end(), phrase) for match in pattern.finditer(text))
    else:
        for phrase in ZH_TRANSITIONS:
            start = 0
            while True:
                index = text.find(phrase, start)
                if index < 0:
                    break
                matches.append((index, index + len(phrase), phrase))
                start = index + 1

    matches.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    selected: list[tuple[int, int, str]] = []
    occupied_until = -1
    for match in matches:
        if match[0] >= occupied_until:
            selected.append(match)
            occupied_until = match[1]
    return selected


def transition_profile(
    sentences: Sequence[str], language: str, analysis_units: int
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    covered_sentences = 0
    for sentence in sentences:
        matches = _transition_matches(normalize_text(sentence).casefold(), language)
        if matches:
            covered_sentences += 1
            counts.update(match[2] for match in matches)
    total = sum(counts.values())
    return {
        "lexicon_version": f"{'en' if language == 'en' else 'zh'}-1.0",
        "total": total,
        "per_100_units": _rounded(total * 100.0 / analysis_units) if analysis_units else 0.0,
        "sentence_coverage": _ratio(covered_sentences, len(sentences)),
        "by_phrase": [
            {"phrase": phrase, "count": count}
            for phrase, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def punctuation_profile(text: str) -> dict[str, Any]:
    category_sets = {
        "comma": set(",\uff0c\u3001"),
        "full_stop": set(".\u3002"),
        "question": set("?\uff1f"),
        "exclamation": set("!\uff01"),
        "semicolon": set(";\uff1b"),
        "colon": set(":\uff1a"),
        "quote": set("\"'\u2018\u2019\u201c\u201d\u300c\u300d\u300e\u300f\u00ab\u00bb"),
        "bracket": set("()[]{}\uff08\uff09\u3010\u3011\u3014\u3015\u3008\u3009\u300a\u300b"),
        "slash": set("/\\"),
    }
    counts: Counter[str] = Counter()
    index = 0
    while index < len(text):
        if text.startswith("...", index):
            end = index + 3
            while end < len(text) and text[end] == ".":
                end += 1
            counts["ellipsis"] += 1
            index = end
            continue
        if text[index] == "\u2026":
            end = index + 1
            while end < len(text) and text[end] == "\u2026":
                end += 1
            counts["ellipsis"] += 1
            index = end
            continue
        if text.startswith("--", index) or text[index] in "\u2013\u2014":
            end = index + (2 if text.startswith("--", index) else 1)
            while end < len(text) and text[end] in "-\u2013\u2014":
                end += 1
            counts["dash"] += 1
            index = end
            continue

        character = text[index]
        if character == "." and index and index + 1 < len(text):
            if text[index - 1].isdigit() and text[index + 1].isdigit():
                index += 1
                continue
        if character == "-" and index and index + 1 < len(text):
            if text[index - 1].isalnum() and text[index + 1].isalnum():
                index += 1
                continue

        matched = False
        for category, characters in category_sets.items():
            if character in characters:
                counts[category] += 1
                matched = True
                break
        if not matched and unicodedata.category(character).startswith("P"):
            counts["other"] += 1
        index += 1

    categories = (
        "comma",
        "full_stop",
        "question",
        "exclamation",
        "semicolon",
        "colon",
        "ellipsis",
        "dash",
        "quote",
        "bracket",
        "slash",
        "other",
    )
    complete_counts = {category: counts.get(category, 0) for category in categories}
    total = sum(complete_counts.values())
    non_whitespace = sum(1 for char in text if not char.isspace())
    return {
        "total": total,
        "counts": complete_counts,
        "shares": {category: _ratio(count, total) for category, count in complete_counts.items()},
        "per_1000_non_whitespace_chars": {
            category: _rounded(count * 1000.0 / non_whitespace) if non_whitespace else 0.0
            for category, count in complete_counts.items()
        },
    }


MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
CHAPTER_HEADING_RE = re.compile(r"^\u7b2c[0-9\u4e00-\u9fff]+[\u7ae0\u8282\u90e8\u5206\u7bc7\u5377]")
OUTLINE_HEADING_RE = re.compile(
    r"^(?:[\u4e00-\u9fff]+|\d+(?:\.\d+)*)[\u3001.\uff0e]\s*\S+"
)
LIST_RE = re.compile(
    r"^(?:[-*+\u2022]\s+|\[[ xX]\]\s+|"
    r"(?:\d+|[A-Za-z]|[\u4e00-\u9fff]+)[.)\u3001\uff0e]\s*|"
    r"[\uff08(](?:\d+|[\u4e00-\u9fff]+)[\uff09)]\s*)"
)


def structure_profile(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    nonempty = [(index + 1, line.strip()) for index, line in enumerate(lines) if line.strip()]
    heading_indices: list[int] = []
    list_indices: list[int] = []
    for index, line in nonempty:
        outline_heading = (
            OUTLINE_HEADING_RE.match(line)
            and content_character_count(line) <= 30
            and not re.search(r"[\u3002\uff01\uff1f.!?;\uff1b]\s*$", line)
        )
        if MARKDOWN_HEADING_RE.match(line) or CHAPTER_HEADING_RE.match(line) or outline_heading:
            heading_indices.append(index)
        if LIST_RE.match(line):
            list_indices.append(index)
    structured = sorted(set(heading_indices) | set(list_indices))
    return {
        "lines_total": len(lines),
        "lines_nonempty": len(nonempty),
        "heading_lines": len(heading_indices),
        "list_lines": len(list_indices),
        "structured_lines": len(structured),
        "heading_line_indices": heading_indices,
        "list_line_indices": list_indices,
        "heading_density": _ratio(len(heading_indices), len(nonempty)),
        "list_density": _ratio(len(list_indices), len(nonempty)),
        "structured_line_density": _ratio(len(structured), len(nonempty)),
    }



def analyze_text(
    text: str,
    *,
    language: str = "auto",
    genre: str = "general",
    paragraph_mode: str = "blank",
    top: int = 20,
    minimum_ngram_occurrences: int = 2,
    source_sha256: str | None = None,
) -> dict[str, Any]:
    original = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalize_text(original)
    language_info = language_profile(normalized, language)
    detected_language = language_info["detected"]
    metric_language = "en" if detected_language == "en" else "zh"
    paragraphs = split_paragraphs(normalized, paragraph_mode)
    sentences = extract_sentences(paragraphs)
    unit_name = "word" if metric_language == "en" else "content_character"
    analysis_units = analysis_length(normalized, metric_language)
    sentence_lengths = [analysis_length(sentence, metric_language) for sentence in sentences]
    paragraph_lengths = [analysis_length(paragraph, metric_language) for paragraph in paragraphs]
    structure = structure_profile(normalized)

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "deterministic": True,
        },
        "disclaimer": {
            "purpose": "surface_style_diagnostics",
            "authorship_inference": False,
            "optimization_target": False,
            "randomization_authorized": False,
            "message": (
                "These metrics describe surface form. Do not optimize them, infer authorship, "
                "or create random variation from them."
            ),
        },
        "input": {
            "sha256": source_sha256 or hashlib.sha256(original.encode("utf-8")).hexdigest(),
            "language_requested": language,
            "language_detected": detected_language,
            "language_signal": {
                "han_share": language_info["han_share"],
                "latin_share": language_info["latin_share"],
                "signal_characters": language_info["signal_characters"],
            },
            "genre": genre,
            "paragraph_mode": paragraph_mode,
        },
        "counts": {
            "characters_total": len(original),
            "characters_non_whitespace": sum(1 for char in original if not char.isspace()),
            "han_characters": len(HAN_RE.findall(original)),
            "english_words": len(EN_WORD_RE.findall(original)),
            "number_tokens": len(NUMBER_RE.findall(original)),
            "lines_total": structure["lines_total"],
            "lines_nonempty": structure["lines_nonempty"],
            "paragraphs": len(paragraphs),
            "sentences": len(sentences),
            "analysis_unit": unit_name,
            "analysis_units": analysis_units,
        },
        "sentence_lengths": {
            "unit": unit_name,
            **summary_stats(sentence_lengths),
        },
        "paragraph_lengths": {
            "unit": unit_name,
            **summary_stats(paragraph_lengths),
        },
        "duplicates": duplicate_profile(sentences, metric_language),
        "repetition": {
            "ngrams": ngram_profile(
                sentences,
                metric_language,
                analysis_units,
                minimum_occurrences=minimum_ngram_occurrences,
                top=top,
            ),
            "openers": opener_profile(sentences, metric_language),
        },
        "transitions": transition_profile(sentences, metric_language, analysis_units),
        "punctuation": punctuation_profile(original),
        "structure": structure,
        "review_flags": [],
        "genre_context": {
            "genre": genre,
            "heuristic_only": True,
            "authorship_inference": False,
            "message": (
                "No automated style thresholds are applied. Inspect raw measurements "
                "only after diagnosing a reader-facing problem."
            ),
            "sample_gate": None,
            "expected_patterns": [],
        },
    }
    return report


def render_text(report: dict[str, Any]) -> str:
    counts = report["counts"]
    sentence_stats = report["sentence_lengths"]
    paragraph_stats = report["paragraph_lengths"]
    repetition = report["repetition"]
    lines = [
        "STYLE DIAGNOSTICS ONLY",
        "This report describes repetition, rhythm, punctuation, and document structure.",
        "It does not detect AI authorship and cannot establish who or what wrote the text.",
        "",
        f"Language: {report['input']['language_detected']} (requested: {report['input']['language_requested']})",
        f"Genre context: {report['input']['genre']}",
        f"Characters: {counts['characters_total']} total; {counts['characters_non_whitespace']} non-whitespace",
        f"Words/scripts: {counts['english_words']} English words; {counts['han_characters']} Han characters",
        f"Structure: {counts['paragraphs']} paragraphs; {counts['sentences']} sentences; {counts['lines_nonempty']} non-empty lines",
        f"Sentence length ({counts['analysis_unit']}): mean={sentence_stats['mean']}, pstdev={sentence_stats['pstdev']}, cv={sentence_stats['cv']}",
        f"Paragraph length ({counts['analysis_unit']}): mean={paragraph_stats['mean']}, pstdev={paragraph_stats['pstdev']}, cv={paragraph_stats['cv']}",
        f"Duplicate sentences: {report['duplicates']['group_count']} groups; excess ratio={report['duplicates']['excess_ratio']}",
        f"Repeated n-gram coverage: {repetition['ngrams']['repeated_unit_coverage']}",
        f"Repeated opener coverage: {repetition['openers']['repeated_sentence_coverage']}",
        f"Transition density: {report['transitions']['per_100_units']} per 100 {counts['analysis_unit']} units",
        f"Structured line density: {report['structure']['structured_line_density']}",
        "",
        "Review notices:",
    ]
    lines.append("- None; this tool does not apply style thresholds.")
    expected_patterns = report["genre_context"]["expected_patterns"]
    lines.extend(["", "Genre-expected patterns (context only):"])
    if expected_patterns:
        for flag in expected_patterns:
            lines.append(f"- [{flag['code']}] {flag['message']}")
            lines.append(f"  Genre context: {flag['genre_reason']}")
    else:
        lines.append("- None; raw genre context is descriptive only.")
    lines.extend(
        [
            "",
            "Raw measurements are not authorship findings, targets, or pass/fail criteria.",
        ]
    )
    return "\n".join(lines) + "\n"


def _positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic surface-style diagnostics; not AI-authorship detection."
    )
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 text file, or - for stdin")
    parser.add_argument("--language", choices=("auto", "zh", "en"), default="auto")
    parser.add_argument("--genre", choices=GENRES, default="general")
    parser.add_argument("--paragraph-mode", choices=("blank", "line"), default="blank")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--top", type=_positive_integer, default=20)
    parser.add_argument("--min-ngram-occurrences", type=_positive_integer, default=2)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("-o", "--output")
    return parser.parse_args(argv)


def _read_source(source: str) -> tuple[bytes, str]:
    raw = sys.stdin.buffer.read() if source == "-" else Path(source).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("input must be UTF-8 text") from exc
    return raw, text


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        raw, text = _read_source(args.input)
    except (OSError, ValueError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2

    report = analyze_text(
        text,
        language=args.language,
        genre=args.genre,
        paragraph_mode=args.paragraph_mode,
        top=args.top,
        minimum_ngram_occurrences=args.min_ngram_occurrences,
        source_sha256=hashlib.sha256(raw).hexdigest(),
    )
    if args.format == "json":
        if args.pretty:
            output = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        else:
            output = json.dumps(
                report, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ) + "\n"
    else:
        output = render_text(report)

    try:
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8", newline="\n")
        else:
            sys.stdout.write(output)
    except OSError as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
