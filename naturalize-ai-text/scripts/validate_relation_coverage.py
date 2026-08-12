#!/usr/bin/env python3
"""Validate declared source-to-text relation coverage.

This tool checks hashes, exact spans, inventory completeness, qualifier maps,
and declared assertion authority. It cannot infer whether an undeclared
semantic relation was omitted or whether a reviewer mislabeled an assertion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Sequence


TOOL_NAME = "validate-relation-coverage"
TOOL_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"
ASSERTION_EFFECTS = {
    "preserves",
    "clarifies",
    "source_authorized_extension",
    "forbidden_inference",
}


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_nonempty(item) for item in value)
        and len(value) == len(set(value))
    )


def _resolve(path_value: str, base_dir: Path) -> Path:
    path = Path(path_value)
    return path.resolve() if path.is_absolute() else (base_dir / path).resolve()


def _add(errors: list[dict[str, Any]], code: str, **details: Any) -> None:
    errors.append({"code": code, **details})


def _exact_spans(
    value: Any,
    content: str,
    errors: list[dict[str, Any]],
    *,
    owner: str,
    field: str,
) -> dict[str, dict[str, Any]]:
    spans: dict[str, dict[str, Any]] = {}
    if not isinstance(value, list) or not value:
        _add(errors, "evidence_spans_required", owner=owner, field=field)
        return spans
    for index, span in enumerate(value, start=1):
        location = f"{owner}.{field}[{index}]"
        if not isinstance(span, dict):
            _add(errors, "evidence_span_not_object", location=location)
            continue
        evidence_id = span.get("evidence_id")
        if not _nonempty(evidence_id):
            _add(errors, "evidence_id_missing", location=location)
            continue
        if evidence_id in spans:
            _add(errors, "duplicate_evidence_id", location=location, evidence_id=evidence_id)
            continue
        start = span.get("start")
        end = span.get("end")
        expected = span.get("text")
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or start < 0
            or end <= start
            or end > len(content)
        ):
            _add(errors, "invalid_evidence_range", location=location, start=start, end=end)
            continue
        if not _nonempty(expected):
            _add(errors, "evidence_text_missing", location=location)
            continue
        actual = content[start:end]
        if actual != expected:
            _add(
                errors,
                "evidence_text_mismatch",
                location=location,
                expected=expected,
                actual=actual,
            )
            continue
        spans[evidence_id] = span
    return spans


def validate_coverage(
    value: Any,
    text_path: str | Path,
    *,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    base = Path(base_dir).resolve() if base_dir is not None else Path.cwd().resolve()
    text = Path(text_path).resolve()
    if not text.is_file():
        return {
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
            "errors": [{"code": "text_file_missing", "path": str(text)}],
            "warnings": [],
            "status": "fail",
        }
    content = text.read_text(encoding="utf-8")
    actual_text_hash = _sha256(text)
    if not isinstance(value, dict):
        return {
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
            "errors": [{"code": "coverage_root_not_object"}],
            "warnings": [],
            "status": "fail",
        }

    if value.get("schema_version") != SCHEMA_VERSION:
        _add(errors, "unsupported_schema", value=value.get("schema_version"))
    expected_text_hash = value.get("text_sha256")
    if not _valid_sha256(expected_text_hash):
        _add(errors, "text_sha256_missing_or_invalid")
    elif expected_text_hash.casefold() != actual_text_hash.casefold():
        _add(
            errors,
            "text_sha256_mismatch",
            expected=expected_text_hash,
            actual=actual_text_hash,
        )
    if value.get("source_inventory_status") != "complete":
        _add(errors, "source_inventory_not_complete")
    if value.get("candidate_assertion_inventory_status") != "complete":
        _add(errors, "candidate_assertion_inventory_not_complete")

    sources: dict[str, dict[str, Any]] = {}
    source_contents: dict[str, str] = {}
    source_relation_ids: set[str] = set()
    raw_sources = value.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        _add(errors, "sources_required")
        raw_sources = []
    for index, source in enumerate(raw_sources, start=1):
        owner = f"sources[{index}]"
        if not isinstance(source, dict):
            _add(errors, "source_not_object", source=index)
            continue
        source_id = source.get("source_id")
        if not _nonempty(source_id):
            _add(errors, "source_id_missing", source=index)
            continue
        if source_id in sources:
            _add(errors, "duplicate_source_id", source_id=source_id)
            continue
        if source.get("inventory_status") != "complete":
            _add(errors, "source_relation_inventory_not_complete", source_id=source_id)
        relation_ids = source.get("relation_ids")
        if not _string_list(relation_ids):
            _add(errors, "source_relation_ids_required", source_id=source_id)
            relation_ids = []
        source_relation_ids.update(relation_ids)
        path_value = source.get("path")
        if not _nonempty(path_value):
            _add(errors, "source_path_missing", source_id=source_id)
            continue
        source_path = _resolve(path_value, base)
        if not source_path.is_file():
            _add(errors, "source_file_missing", source_id=source_id, path=str(source_path))
            continue
        expected_hash = source.get("sha256")
        actual_hash = _sha256(source_path)
        if not _valid_sha256(expected_hash):
            _add(errors, "source_sha256_missing_or_invalid", source_id=source_id)
        elif expected_hash.casefold() != actual_hash.casefold():
            _add(
                errors,
                "source_sha256_mismatch",
                source_id=source_id,
                expected=expected_hash,
                actual=actual_hash,
            )
        try:
            source_contents[source_id] = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            _add(errors, "source_not_utf8", source_id=source_id, message=str(exc))
            continue
        sources[source_id] = source

    boundaries: dict[str, dict[str, Any]] = {}
    raw_boundaries = value.get("invention_boundaries", [])
    if not isinstance(raw_boundaries, list):
        _add(errors, "invention_boundaries_not_list")
        raw_boundaries = []
    for index, boundary in enumerate(raw_boundaries, start=1):
        if not isinstance(boundary, dict):
            _add(errors, "invention_boundary_not_object", boundary=index)
            continue
        boundary_id = boundary.get("boundary_id")
        if not _nonempty(boundary_id):
            _add(errors, "invention_boundary_id_missing", boundary=index)
            continue
        if boundary_id in boundaries:
            _add(errors, "duplicate_invention_boundary_id", boundary_id=boundary_id)
            continue
        source_ids = boundary.get("source_ids")
        if not _string_list(source_ids) or any(item not in sources for item in source_ids):
            _add(errors, "invention_boundary_source_invalid", boundary_id=boundary_id)
        if not _nonempty(boundary.get("scope")):
            _add(errors, "invention_boundary_scope_missing", boundary_id=boundary_id)
        boundaries[boundary_id] = boundary

    relations: dict[str, dict[str, Any]] = {}
    raw_relations = value.get("relations")
    if not isinstance(raw_relations, list) or not raw_relations:
        _add(errors, "relations_required")
        raw_relations = []
    declared_count = value.get("declared_relation_count")
    if isinstance(declared_count, bool) or not isinstance(declared_count, int):
        _add(errors, "declared_relation_count_missing")
    elif declared_count != len(raw_relations):
        _add(
            errors,
            "declared_relation_count_mismatch",
            declared=declared_count,
            actual=len(raw_relations),
        )
    for index, relation in enumerate(raw_relations, start=1):
        owner = f"relations[{index}]"
        if not isinstance(relation, dict):
            _add(errors, "relation_not_object", relation=index)
            continue
        relation_id = relation.get("relation_id")
        if not _nonempty(relation_id):
            _add(errors, "relation_id_missing", relation=index)
            continue
        if relation_id in relations:
            _add(errors, "duplicate_relation_id", relation_id=relation_id)
            continue
        for field in ("subject", "predicate", "scope", "negation", "modality_or_certainty"):
            if not _nonempty(relation.get(field)):
                _add(errors, "relation_field_missing", relation_id=relation_id, field=field)
        if not isinstance(relation.get("object"), str):
            _add(errors, "relation_field_missing", relation_id=relation_id, field="object")
        source_ids = relation.get("source_ids")
        if not _string_list(source_ids):
            _add(errors, "relation_source_ids_required", relation_id=relation_id)
            source_ids = []
        elif any(item not in sources for item in source_ids):
            _add(errors, "relation_source_id_unknown", relation_id=relation_id)
        qualifiers = relation.get("required_qualifiers", [])
        forbidden = relation.get("forbidden_inferences", [])
        if not _string_list(qualifiers, allow_empty=True):
            _add(errors, "required_qualifiers_invalid", relation_id=relation_id)
        if not _string_list(forbidden, allow_empty=True):
            _add(errors, "forbidden_inferences_invalid", relation_id=relation_id)
        source_evidence = relation.get("source_evidence")
        if not isinstance(source_evidence, list) or not source_evidence:
            _add(errors, "relation_source_evidence_required", relation_id=relation_id)
        else:
            seen_evidence: set[str] = set()
            for evidence_index, evidence in enumerate(source_evidence, start=1):
                location = f"{owner}.source_evidence[{evidence_index}]"
                if not isinstance(evidence, dict):
                    _add(errors, "source_evidence_not_object", location=location)
                    continue
                source_id = evidence.get("source_id")
                if source_id not in source_contents or source_id not in source_ids:
                    _add(errors, "source_evidence_source_invalid", location=location)
                    continue
                valid = _exact_spans(
                    [evidence],
                    source_contents[source_id],
                    errors,
                    owner=owner,
                    field="source_evidence",
                )
                overlap = seen_evidence.intersection(valid)
                if overlap:
                    _add(errors, "duplicate_source_evidence_id", relation_id=relation_id)
                seen_evidence.update(valid)
        relations[relation_id] = relation

    relation_ids = set(relations)
    if source_relation_ids != relation_ids:
        if relation_ids - source_relation_ids:
            _add(
                errors,
                "source_inventory_missing_relations",
                relation_ids=sorted(relation_ids - source_relation_ids),
            )
        if source_relation_ids - relation_ids:
            _add(
                errors,
                "source_inventory_unknown_relations",
                relation_ids=sorted(source_relation_ids - relation_ids),
            )

    coverage_by_id: dict[str, dict[str, Any]] = {}
    raw_coverage = value.get("coverage")
    if not isinstance(raw_coverage, list):
        _add(errors, "coverage_not_list")
        raw_coverage = []
    for index, coverage in enumerate(raw_coverage, start=1):
        owner = f"coverage[{index}]"
        if not isinstance(coverage, dict):
            _add(errors, "coverage_not_object", coverage=index)
            continue
        relation_id = coverage.get("relation_id")
        if relation_id not in relations:
            _add(errors, "coverage_relation_unknown", relation_id=relation_id)
            continue
        if relation_id in coverage_by_id:
            _add(errors, "duplicate_relation_coverage", relation_id=relation_id)
            continue
        if coverage.get("status") != "pass":
            _add(errors, "relation_coverage_not_passed", relation_id=relation_id)
        final_spans = _exact_spans(
            coverage.get("final_text_evidence"),
            content,
            errors,
            owner=owner,
            field="final_text_evidence",
        )
        expected_qualifiers = set(relations[relation_id].get("required_qualifiers", []))
        qualifier_records = coverage.get("qualifier_coverage")
        if not isinstance(qualifier_records, list):
            _add(errors, "qualifier_coverage_not_list", relation_id=relation_id)
            qualifier_records = []
        actual_qualifiers: set[str] = set()
        for qualifier_record in qualifier_records:
            if not isinstance(qualifier_record, dict):
                _add(errors, "qualifier_coverage_not_object", relation_id=relation_id)
                continue
            qualifier = qualifier_record.get("qualifier")
            evidence_ids = qualifier_record.get("evidence_ids")
            if not _nonempty(qualifier) or qualifier in actual_qualifiers:
                _add(errors, "qualifier_coverage_invalid", relation_id=relation_id, qualifier=qualifier)
                continue
            actual_qualifiers.add(qualifier)
            if not _string_list(evidence_ids) or any(item not in final_spans for item in evidence_ids):
                _add(
                    errors,
                    "qualifier_evidence_invalid",
                    relation_id=relation_id,
                    qualifier=qualifier,
                )
        if actual_qualifiers != expected_qualifiers:
            _add(
                errors,
                "qualifier_coverage_mismatch",
                relation_id=relation_id,
                missing=sorted(expected_qualifiers - actual_qualifiers),
                extra=sorted(actual_qualifiers - expected_qualifiers),
            )
        expected_forbidden = set(relations[relation_id].get("forbidden_inferences", []))
        reviews = coverage.get("forbidden_inference_review")
        if not isinstance(reviews, list):
            _add(errors, "forbidden_inference_review_not_list", relation_id=relation_id)
            reviews = []
        actual_forbidden: set[str] = set()
        for review in reviews:
            if not isinstance(review, dict):
                _add(errors, "forbidden_inference_review_not_object", relation_id=relation_id)
                continue
            inference = review.get("inference")
            status = review.get("status")
            if not _nonempty(inference) or inference in actual_forbidden:
                _add(errors, "forbidden_inference_review_invalid", relation_id=relation_id)
                continue
            actual_forbidden.add(inference)
            if status not in {"absent", "source_authorized"}:
                _add(
                    errors,
                    "forbidden_inference_not_cleared",
                    relation_id=relation_id,
                    inference=inference,
                    status=status,
                )
            if not _nonempty(review.get("notes")):
                _add(
                    errors,
                    "forbidden_inference_review_notes_missing",
                    relation_id=relation_id,
                    inference=inference,
                )
            if status == "source_authorized":
                authority_ids = review.get("authority_ids")
                if not _string_list(authority_ids) or any(item not in sources for item in authority_ids):
                    _add(
                        errors,
                        "forbidden_inference_authority_invalid",
                        relation_id=relation_id,
                        inference=inference,
                    )
        if actual_forbidden != expected_forbidden:
            _add(
                errors,
                "forbidden_inference_review_mismatch",
                relation_id=relation_id,
                missing=sorted(expected_forbidden - actual_forbidden),
                extra=sorted(actual_forbidden - expected_forbidden),
            )
        coverage_by_id[relation_id] = coverage

    coverage_ids = set(coverage_by_id)
    if coverage_ids != relation_ids:
        if relation_ids - coverage_ids:
            _add(
                errors,
                "relation_coverage_missing",
                relation_ids=sorted(relation_ids - coverage_ids),
            )
        if coverage_ids - relation_ids:
            _add(
                errors,
                "relation_coverage_extra",
                relation_ids=sorted(coverage_ids - relation_ids),
            )

    assertion_relation_ids: set[str] = set()
    assertion_ids: set[str] = set()
    invention_ids: set[str] = set()
    assertions = value.get("candidate_relation_assertions")
    if not isinstance(assertions, list) or not assertions:
        _add(errors, "candidate_relation_assertions_required")
        assertions = []
    for index, assertion in enumerate(assertions, start=1):
        owner = f"candidate_relation_assertions[{index}]"
        if not isinstance(assertion, dict):
            _add(errors, "candidate_assertion_not_object", assertion=index)
            continue
        assertion_id = assertion.get("assertion_id")
        if not _nonempty(assertion_id) or assertion_id in assertion_ids:
            _add(errors, "candidate_assertion_id_invalid", assertion_id=assertion_id)
            continue
        assertion_ids.add(assertion_id)
        if not _nonempty(assertion.get("summary")):
            _add(errors, "candidate_assertion_summary_missing", assertion_id=assertion_id)
        _exact_spans(
            assertion.get("final_text_evidence"),
            content,
            errors,
            owner=owner,
            field="final_text_evidence",
        )
        touches = assertion.get("touches_relation_ids")
        if not _string_list(touches) or any(item not in relations for item in touches):
            _add(errors, "candidate_assertion_relations_invalid", assertion_id=assertion_id)
            touches = []
        assertion_relation_ids.update(touches)
        effect = assertion.get("relation_effect")
        if effect not in ASSERTION_EFFECTS:
            _add(errors, "candidate_assertion_effect_invalid", assertion_id=assertion_id, value=effect)
        if effect == "forbidden_inference":
            _add(errors, "candidate_assertion_is_forbidden_inference", assertion_id=assertion_id)
        if not isinstance(assertion.get("changes_comparative_weight"), bool):
            _add(errors, "comparative_weight_flag_required", assertion_id=assertion_id)
        authority_kind = assertion.get("authority_kind")
        if authority_kind == "authoritative_source":
            authority_ids = assertion.get("authority_ids")
            if not _string_list(authority_ids) or any(item not in sources for item in authority_ids):
                _add(errors, "candidate_assertion_authority_invalid", assertion_id=assertion_id)
        elif authority_kind == "declared_fictional_invention":
            invention_id = assertion.get("invention_id")
            if not _nonempty(invention_id) or invention_id in invention_ids:
                _add(errors, "candidate_invention_id_invalid", assertion_id=assertion_id)
            else:
                invention_ids.add(invention_id)
            boundary_id = assertion.get("boundary_id")
            if boundary_id not in boundaries:
                _add(errors, "candidate_invention_boundary_invalid", assertion_id=assertion_id)
            if not _nonempty(assertion.get("invention_basis")):
                _add(errors, "candidate_invention_basis_missing", assertion_id=assertion_id)
            if effect not in {"preserves", "clarifies"}:
                _add(errors, "candidate_invention_extends_locked_relation", assertion_id=assertion_id)
            if assertion.get("changes_comparative_weight") is True:
                _add(errors, "unauthorized_comparative_weight_invention", assertion_id=assertion_id)
        else:
            _add(errors, "candidate_assertion_authority_kind_invalid", assertion_id=assertion_id)

    if assertion_relation_ids != relation_ids:
        if relation_ids - assertion_relation_ids:
            _add(
                errors,
                "candidate_assertion_inventory_missing_relations",
                relation_ids=sorted(relation_ids - assertion_relation_ids),
            )
        if assertion_relation_ids - relation_ids:
            _add(
                errors,
                "candidate_assertion_inventory_unknown_relations",
                relation_ids=sorted(assertion_relation_ids - relation_ids),
            )

    if value.get("review_status") != "pass":
        _add(errors, "coverage_review_not_passed", value=value.get("review_status"))
    elif errors:
        _add(errors, "declared_pass_has_validation_errors")

    warnings.append(
        {
            "code": "semantic_scope_limit",
            "message": (
                "This validator proves declared hash, span, inventory, qualifier, and authority "
                "consistency only. A reviewer must still detect omitted or mislabeled semantics."
            ),
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "text_sha256": actual_text_hash,
        "source_count": len(sources),
        "relation_count": len(relations),
        "covered_relation_count": len(coverage_by_id),
        "candidate_assertion_count": len(assertion_ids),
        "errors": errors,
        "warnings": warnings,
        "status": "fail" if errors else "pass",
        "disclaimer": "Declared relation coverage is not authorship or detector evidence.",
    }


def validate_coverage_file(
    coverage_path: str | Path,
    text_path: str | Path,
) -> dict[str, Any]:
    path = Path(coverage_path).resolve()
    if not path.is_file():
        return {
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
            "errors": [{"code": "coverage_file_missing", "path": str(path)}],
            "warnings": [],
            "status": "fail",
        }
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
            "errors": [{"code": "coverage_file_invalid", "message": str(exc)}],
            "warnings": [],
            "status": "fail",
        }
    report = validate_coverage(value, text_path, base_dir=path.parent)
    report["coverage_file_sha256"] = _sha256(path)
    return report


def _write_output(value: dict[str, Any], output: str | None, pretty: bool) -> None:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
    ) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate declared source-to-text relation coverage.")
    parser.add_argument("coverage")
    parser.add_argument("--text", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("-o", "--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = validate_coverage_file(args.coverage, args.text)
    _write_output(report, args.output, args.pretty)
    return 1 if args.strict and report.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
