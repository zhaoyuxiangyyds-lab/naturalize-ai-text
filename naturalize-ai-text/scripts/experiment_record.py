#!/usr/bin/env python3
"""Create and validate exact-hash detector experiment records.

The tool validates provenance and observable-result bookkeeping. It never
queries a detector and never converts a detector score into authorship proof.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence

try:
    from validate_text import validate_file
except ImportError:  # pragma: no cover - supports package-style execution
    from .validate_text import validate_file


TOOL_NAME = "experiment-record"
TOOL_VERSION = "2.0.0"
SCHEMA_VERSION = "1.0"
EVIDENCE_KINDS = {
    "visible_numeric",
    "official_export",
    "visible_label",
    "screenshot_only",
    "not_observed",
}
COMPONENT_KEYS = ("human_features", "suspected_ai", "ai_features")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _write_json(path: str | Path, value: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def init_manifest(
    text_path: str | Path,
    *,
    sample_id: str,
    stage: str,
    mode: str,
    provenance: str,
    language: str,
    genre: str,
) -> dict[str, Any]:
    text = Path(text_path)
    validation = validate_file(text)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "created_at": _now(),
        "experiment_id": f"{sample_id}-{stage}",
        "sample_id": sample_id,
        "stage": stage,
        "mode": mode,
        "provenance": provenance,
        "language": language,
        "genre": genre,
        "text_path": str(text),
        "text_sha256": validation["input"]["sha256"],
        "text_counts": validation["counts"],
        "quality": {
            "hard_gates": "not_checked",
            "blind_review": "not_checked",
            "notes": [],
        },
        "detector_target": {
            "description": "Name a detector-specific criterion before looking at new results.",
            "threshold": None,
        },
        "observations": [],
        "status": "draft",
    }


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.rstrip("%"))
        except ValueError:
            return None
    return None


def validate_observation(observation: Any, expected_hash: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(observation, dict):
        return [{"code": "observation_not_object"}]
    required = ("detector_name", "observed_at", "input_sha256", "evidence_kind", "status")
    for field in required:
        if not observation.get(field):
            errors.append({"code": "missing_observation_field", "field": field})
    if observation.get("input_sha256", "").casefold() != expected_hash.casefold():
        errors.append({"code": "observation_hash_mismatch", "expected": expected_hash, "actual": observation.get("input_sha256")})
    if observation.get("evidence_kind") not in EVIDENCE_KINDS:
        errors.append({"code": "invalid_evidence_kind", "value": observation.get("evidence_kind")})

    raw = observation.get("raw_component_scores")
    if raw is not None:
        if not isinstance(raw, dict):
            errors.append({"code": "component_scores_not_object"})
        else:
            numbers: list[float] = []
            for key, value in raw.items():
                number = _number(value)
                if number is None or not 0 <= number <= 100:
                    errors.append({"code": "component_score_out_of_range", "component": key, "value": value})
                else:
                    numbers.append(number)
            present = [key for key in COMPONENT_KEYS if key in raw and _number(raw[key]) is not None]
            if present == list(COMPONENT_KEYS):
                total = sum(float(_number(raw[key])) for key in COMPONENT_KEYS)
                if abs(total - 100.0) > 0.51:
                    errors.append({"code": "component_sum_not_100", "sum": total, "tolerance": 0.51})
    if observation.get("evidence_kind") in {"visible_numeric", "official_export"} and raw is None:
        errors.append({"code": "numeric_evidence_missing_scores"})
    return errors


def validate_manifest(manifest: dict[str, Any], text_path: str | Path | None = None) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append({"code": "unsupported_schema", "value": manifest.get("schema_version")})
    expected_hash = manifest.get("text_sha256")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        errors.append({"code": "missing_or_invalid_text_sha256"})
        expected_hash = ""
    path = Path(text_path) if text_path is not None else Path(manifest.get("text_path", ""))
    if not path or not str(path):
        errors.append({"code": "missing_text_path"})
    elif not path.exists():
        errors.append({"code": "text_file_missing", "path": str(path)})
    else:
        actual_hash = _sha256(path)
        if expected_hash and actual_hash.casefold() != expected_hash.casefold():
            errors.append({"code": "text_hash_mismatch", "expected": expected_hash, "actual": actual_hash})
        validation = validate_file(path)
        if validation["hard_errors"]:
            errors.append({"code": "text_hard_gate_failure", "details": validation["hard_errors"]})
        if validation["warnings"]:
            warnings.append({"code": "text_review_warnings", "details": validation["warnings"]})

    observations = manifest.get("observations", [])
    if not isinstance(observations, list):
        errors.append({"code": "observations_not_list"})
        observations = []
    for index, observation in enumerate(observations, start=1):
        for error in validate_observation(observation, expected_hash):
            errors.append({"observation": index, **error})

    if manifest.get("stage") in {"final", "holdout"} and not observations:
        warnings.append({"code": "exact_detector_result_missing", "message": "No detector observation is attached; final score claims are not validated."})

    status = "fail" if errors else ("review" if warnings else "pass")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "manifest_id": manifest.get("experiment_id"),
        "text_sha256": expected_hash,
        "errors": errors,
        "warnings": warnings,
        "observation_count": len(observations),
        "status": status,
        "disclaimer": "A valid record proves bookkeeping only; detector output cannot prove authorship.",
    }


def add_observation(manifest: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    manifest.setdefault("observations", []).append(observation)
    manifest["status"] = "observed"
    return manifest


def _write_output(value: Any, output: str | None, pretty: bool) -> None:
    rendered = json.dumps(value, ensure_ascii=False, indent=2 if pretty else None, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and validate exact-hash experiment records.")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("text")
    init_parser.add_argument("--sample-id", required=True)
    init_parser.add_argument("--stage", required=True)
    init_parser.add_argument("--mode", required=True)
    init_parser.add_argument("--provenance", required=True)
    init_parser.add_argument("--language", required=True)
    init_parser.add_argument("--genre", required=True)
    init_parser.add_argument("-o", "--output", required=True)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("manifest")
    validate_parser.add_argument("--text")
    validate_parser.add_argument("--pretty", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument("-o", "--output")

    add_parser = sub.add_parser("add")
    add_parser.add_argument("manifest")
    add_parser.add_argument("--observation-file", required=True)
    add_parser.add_argument("-o", "--output")

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "init":
            manifest = init_manifest(
                args.text,
                sample_id=args.sample_id,
                stage=args.stage,
                mode=args.mode,
                provenance=args.provenance,
                language=args.language,
                genre=args.genre,
            )
            _write_json(args.output, manifest)
            return 0
        if args.command == "add":
            manifest = _read_json(args.manifest)
            observation = _read_json(args.observation_file)
            manifest = add_observation(manifest, observation)
            _write_json(args.output or args.manifest, manifest)
            return 0
        manifest = _read_json(args.manifest)
        report = validate_manifest(manifest, args.text)
        _write_output(report, args.output, args.pretty)
        return 1 if args.strict and report["errors"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
