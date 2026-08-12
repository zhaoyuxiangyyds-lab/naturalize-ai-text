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
import re
import sys
from typing import Any, Sequence

try:
    from validate_text import validate_file
    from composition_trace import validate_trace_file
except ImportError:  # pragma: no cover - supports package-style execution
    from .validate_text import validate_file
    from .composition_trace import validate_trace_file


TOOL_NAME = "experiment-record"
TOOL_VERSION = "2.4.0"
SCHEMA_VERSION = "1.2"
SUPPORTED_SCHEMA_VERSIONS = {"1.1", SCHEMA_VERSION}
MODES = {"revision", "new_generation", "experiment_only"}
PROVENANCES = {"human_draft", "ai_assisted", "ai_generated", "mixed", "unknown"}
OBSERVATION_STATUSES = {"observed", "blocked", "contradictory", "not_evaluable"}
EVIDENCE_KINDS = {
    "visible_numeric",
    "official_export",
    "visible_label",
    "screenshot_only",
    "not_observed",
}
COMPONENT_KEYS = ("human_features", "suspected_ai", "ai_features")
PREREGISTRATION_STATES = {"not_registered", "registered", "locked", "amended"}
PREREGISTRATION_REQUIRED = (
    "question",
    "target_metric",
    "material_effect_threshold",
    "quality_budget",
    "detectors",
    "languages",
    "genres",
    "sample_selection",
    "matched_control_rule",
    "rerun_rule",
    "stop_rule",
    "intervention_family",
    "composition_process",
)
CONTROL_PROVENANCES = PROVENANCES
COMPOSITION_PROCESSES = {"new_generation", "full_reconstruction", "local_edit", "no_edit"}
INVOCATION_TYPES = {"explicit", "implicit", "not_applicable"}
QUALITY_CHECKS = (
    "source_integrity",
    "facts_and_citations",
    "logic_or_narrative_continuity",
    "language_surface",
    "genre_and_voice",
    "disclosure",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _read_json_value(path: str | Path) -> Any:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
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
    pre_registration: dict[str, Any] | None = None,
    controls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    text = Path(text_path)
    validation = validate_file(text)
    registration = {
        "status": "not_registered",
        "registered_at": None,
        "question": "",
        "target_metric": "",
        "material_effect_threshold": None,
        "quality_budget": "",
        "detectors": [],
        "languages": [language],
        "genres": [genre],
        "sample_selection": "",
        "matched_control_rule": "",
        "rerun_rule": "",
        "stop_rule": "",
        "intervention_family": "",
        "composition_process": "",
    }
    if pre_registration:
        registration.update(pre_registration)
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
            "checks": {name: "not_checked" for name in QUALITY_CHECKS},
            "notes": [],
        },
        "detector_target": {
            "description": "Name a detector-specific criterion before looking at new results.",
            "threshold": None,
        },
        "pre_registration": registration,
        "execution_provenance": {
            "skill_path": "",
            "skill_tree_sha256": "",
            "invocation": "not_applicable",
            "fresh_context": None,
            "execution_context_id": "",
            "files_read": [],
            "anchor_hashes": [],
            "composition_trace_path": "",
            "composition_trace_sha256": "",
            "output_sha256": validation["input"]["sha256"],
            "post_generation_edits": [],
            "clean_forward_test": False,
        },
        "controls": list(controls or []),
        "replication": {
            "required_runs": 2,
            "rerun_noise_threshold": None,
            "observed_runs": 0,
            "status": "not_started",
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


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _valid_url(value: Any) -> bool:
    return isinstance(value, str) and bool(re.match(r"^https?://[^\s]+$", value))


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _validate_execution_provenance(
    value: Any,
    expected_hash: str,
    *,
    require_complete: bool,
    require_composition_trace: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return (
            [{"code": "execution_provenance_not_object"}],
            [],
            {"required": require_complete, "clean_forward_test": False},
        )

    invocation = value.get("invocation", "not_applicable")
    if invocation not in INVOCATION_TYPES:
        errors.append({"code": "invalid_execution_invocation", "value": invocation})

    output_hash = value.get("output_sha256")
    if output_hash and not _valid_sha256(output_hash):
        errors.append({"code": "invalid_execution_output_hash", "value": output_hash})
    elif output_hash and expected_hash and output_hash.casefold() != expected_hash.casefold():
        errors.append(
            {
                "code": "execution_output_hash_mismatch",
                "expected": expected_hash,
                "actual": output_hash,
            }
        )

    files_read = value.get("files_read", [])
    if not isinstance(files_read, list) or not all(isinstance(item, str) and item.strip() for item in files_read):
        errors.append({"code": "invalid_execution_files_read"})

    anchor_hashes = value.get("anchor_hashes", [])
    if not isinstance(anchor_hashes, list) or not all(_valid_sha256(item) for item in anchor_hashes):
        errors.append({"code": "invalid_execution_anchor_hashes"})

    trace_path_value = value.get("composition_trace_path", "")
    trace_hash = value.get("composition_trace_sha256", "")
    trace_report: dict[str, Any] | None = None
    trace_status = "not_provided"
    if not isinstance(trace_path_value, str):
        errors.append({"code": "invalid_composition_trace_path"})
        trace_path_value = ""
    if trace_hash and not _valid_sha256(trace_hash):
        errors.append({"code": "invalid_composition_trace_sha256", "value": trace_hash})
    if trace_path_value.strip():
        trace_report = validate_trace_file(trace_path_value, require_finalized=True)
        trace_status = trace_report.get("status", "fail")
        actual_trace_hash = trace_report.get("trace_sha256")
        if not _valid_sha256(actual_trace_hash):
            errors.append({"code": "composition_trace_unreadable", "path": trace_path_value})
        elif not trace_hash:
            errors.append({"code": "composition_trace_sha256_required"})
        elif actual_trace_hash.casefold() != trace_hash.casefold():
            errors.append(
                {
                    "code": "composition_trace_hash_mismatch",
                    "expected": trace_hash,
                    "actual": actual_trace_hash,
                }
            )
        if trace_report.get("errors"):
            errors.append(
                {
                    "code": "composition_trace_invalid",
                    "details": trace_report["errors"],
                }
            )
        trace_output_hash = trace_report.get("final_output_sha256")
        if (
            _valid_sha256(trace_output_hash)
            and expected_hash
            and trace_output_hash.casefold() != expected_hash.casefold()
        ):
            errors.append(
                {
                    "code": "composition_trace_output_hash_mismatch",
                    "expected": expected_hash,
                    "actual": trace_output_hash,
                }
            )
    elif trace_hash:
        errors.append({"code": "composition_trace_path_required"})

    post_edits = value.get("post_generation_edits", [])
    if not isinstance(post_edits, list) or not all(isinstance(item, str) and item.strip() for item in post_edits):
        errors.append({"code": "invalid_post_generation_edits"})
        post_edits = []

    clean = value.get("clean_forward_test", False)
    if not isinstance(clean, bool):
        errors.append({"code": "invalid_clean_forward_test", "value": clean})
        clean = False
    if clean and post_edits:
        errors.append({"code": "post_edits_marked_clean", "count": len(post_edits)})
    if clean and value.get("fresh_context") is not True:
        errors.append({"code": "clean_test_without_fresh_context"})

    if require_complete:
        required_strings = ("skill_path", "execution_context_id")
        for field in required_strings:
            if not isinstance(value.get(field), str) or not value[field].strip():
                errors.append({"code": "missing_execution_field", "field": field})
        if not _valid_sha256(value.get("skill_tree_sha256")):
            errors.append({"code": "missing_or_invalid_skill_tree_sha256"})
        if invocation != "explicit":
            errors.append({"code": "explicit_invocation_required", "actual": invocation})
        if value.get("fresh_context") is not True:
            errors.append({"code": "fresh_context_required"})
        if not _nonempty_string_list(files_read):
            errors.append({"code": "execution_files_read_required"})
        if not _valid_sha256(output_hash):
            errors.append({"code": "execution_output_hash_required"})
        if clean is not True:
            errors.append({"code": "clean_forward_test_required"})
        if require_composition_trace:
            if not trace_path_value.strip():
                errors.append({"code": "composition_trace_required"})
            if not _valid_sha256(trace_hash):
                errors.append({"code": "composition_trace_sha256_required"})
            if trace_status != "pass":
                errors.append({"code": "composition_trace_pass_required", "actual": trace_status})

    if not require_complete and clean is False and invocation != "not_applicable":
        warnings.append({"code": "execution_not_marked_clean"})

    summary = {
        "required": require_complete,
        "invocation": invocation,
        "fresh_context": value.get("fresh_context"),
        "files_read": len(files_read) if isinstance(files_read, list) else 0,
        "anchor_count": len(anchor_hashes) if isinstance(anchor_hashes, list) else 0,
        "composition_trace_required": require_composition_trace,
        "composition_trace_status": trace_status,
        "composition_trace_event_count": (
            trace_report.get("event_count", 0) if isinstance(trace_report, dict) else 0
        ),
        "composition_trace_section_count": (
            trace_report.get("section_count", 0) if isinstance(trace_report, dict) else 0
        ),
        "post_generation_edit_count": len(post_edits),
        "clean_forward_test": clean,
    }
    return errors, warnings, summary


def _raw_components(observation: dict[str, Any]) -> tuple[Any, str | None]:
    canonical = observation.get("raw_components")
    legacy = observation.get("raw_component_scores")
    if canonical is not None and legacy is not None and canonical != legacy:
        return None, "component_score_alias_conflict"
    if canonical is not None:
        return canonical, None
    return legacy, None


def validate_observation(observation: Any, expected_hash: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(observation, dict):
        return [{"code": "observation_not_object"}]
    required = (
        "detector_name",
        "detector_url",
        "observed_at",
        "input_sha256",
        "evidence_kind",
        "status",
    )
    for field in required:
        if not observation.get(field):
            errors.append({"code": "missing_observation_field", "field": field})
    observed_hash = observation.get("input_sha256")
    if not isinstance(observed_hash, str) or observed_hash.casefold() != expected_hash.casefold():
        errors.append({"code": "observation_hash_mismatch", "expected": expected_hash, "actual": observed_hash})
    if observation.get("detector_url") and not _valid_url(observation["detector_url"]):
        errors.append({"code": "invalid_detector_url", "value": observation.get("detector_url")})
    if observation.get("observed_at") and not _valid_timestamp(observation["observed_at"]):
        errors.append({"code": "invalid_observed_at", "value": observation.get("observed_at")})
    rerun_index = observation.get("rerun_index", 1)
    if isinstance(rerun_index, bool) or not isinstance(rerun_index, int) or rerun_index < 1:
        errors.append({"code": "invalid_rerun_index", "value": rerun_index})
    if observation.get("evidence_kind") not in EVIDENCE_KINDS:
        errors.append({"code": "invalid_evidence_kind", "value": observation.get("evidence_kind")})
    if observation.get("status") not in OBSERVATION_STATUSES:
        errors.append({"code": "invalid_observation_status", "value": observation.get("status")})

    raw, alias_error = _raw_components(observation)
    if alias_error:
        errors.append({"code": alias_error})
    numeric_count = 0
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
                    numeric_count += 1
            present = [key for key in COMPONENT_KEYS if key in raw and _number(raw[key]) is not None]
            if present == list(COMPONENT_KEYS):
                total = sum(float(_number(raw[key])) for key in COMPONENT_KEYS)
                if abs(total - 100.0) > 0.51:
                    errors.append({"code": "component_sum_not_100", "sum": total, "tolerance": 0.51})
    evidence_kind = observation.get("evidence_kind")
    status = observation.get("status")
    if status == "observed" and evidence_kind == "not_observed":
        errors.append({"code": "observed_with_not_observed_evidence"})
    if evidence_kind in {"visible_numeric", "official_export"} and numeric_count == 0:
        errors.append({"code": "numeric_evidence_missing_scores"})
    if status == "observed" and evidence_kind in {"visible_numeric", "official_export", "visible_label", "screenshot_only"} and not observation.get("screenshot_or_report_path"):
        errors.append({"code": "observed_evidence_path_missing"})
    if evidence_kind == "visible_label":
        labels = observation.get("displayed_labels")
        if not isinstance(labels, list) or not any(str(label).strip() for label in labels):
            errors.append({"code": "visible_label_missing_labels"})
    if evidence_kind == "screenshot_only" and not observation.get("screenshot_or_report_path"):
        errors.append({"code": "screenshot_evidence_missing_path"})
    return errors


def _validate_preregistration(
    value: Any, *, require_registered: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [{"code": "preregistration_not_object"}], [], "invalid"
    state = value.get("status", "not_registered")
    if state not in PREREGISTRATION_STATES:
        errors.append({"code": "invalid_preregistration_status", "value": state})
        state = "invalid"
    if state == "not_registered":
        warnings.append(
            {
                "code": "preregistration_missing",
                "message": "No preregistered question, target metric, controls, and rerun rule are locked.",
            }
        )
        if require_registered:
            errors.append({"code": "preregistration_required"})
        return errors, warnings, state

    if require_registered and state != "locked":
        errors.append({"code": "preregistration_not_locked", "value": state})

    if not _valid_timestamp(value.get("registered_at")):
        errors.append({"code": "invalid_preregistration_registered_at"})
    for field in PREREGISTRATION_REQUIRED:
        field_value = value.get(field)
        if field in {"detectors", "languages", "genres"}:
            if not _nonempty_string_list(field_value):
                errors.append({"code": "preregistration_field_missing", "field": field})
        elif field == "material_effect_threshold":
            threshold = _number(field_value)
            if isinstance(field_value, dict):
                threshold = _number(field_value.get("absolute_points"))
            if threshold is None or threshold <= 0:
                errors.append({"code": "invalid_material_effect_threshold", "value": field_value})
        elif field == "composition_process":
            if field_value not in COMPOSITION_PROCESSES:
                errors.append(
                    {
                        "code": "invalid_composition_process",
                        "value": field_value,
                    }
                )
        elif not isinstance(field_value, str) or not field_value.strip():
            errors.append({"code": "preregistration_field_missing", "field": field})
    return errors, warnings, state


def _validate_quality(
    value: Any, *, require_complete: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [{"code": "quality_not_object"}], []

    hard_gates = value.get("hard_gates", "not_checked")
    if hard_gates not in {"not_checked", "passed", "failed"}:
        errors.append({"code": "invalid_quality_hard_gates", "value": hard_gates})
    elif hard_gates == "failed":
        errors.append({"code": "quality_hard_gate_failure"})
    elif hard_gates != "passed":
        warnings.append(
            {
                "code": "quality_hard_gates_not_checked",
                "message": "Facts, citations, logic, continuity, language, genre, and disclosure are not recorded as passed.",
            }
        )
        if require_complete:
            errors.append({"code": "quality_hard_gates_required"})

    blind_review = value.get("blind_review", "not_checked")
    if not isinstance(blind_review, (str, dict)):
        errors.append({"code": "invalid_blind_review", "value": blind_review})

    checks = value.get("checks", {})
    if not isinstance(checks, dict):
        errors.append({"code": "quality_checks_not_object"})
        checks = {}
    for name in QUALITY_CHECKS:
        result = checks.get(name, "not_checked")
        if result not in {"passed", "not_applicable", "not_checked", "failed"}:
            errors.append(
                {"code": "invalid_quality_check", "check": name, "value": result}
            )
        elif result == "failed":
            errors.append({"code": "quality_check_failed", "check": name})
        elif require_complete and result not in {"passed", "not_applicable"}:
            errors.append({"code": "quality_check_required", "check": name})
    return errors, warnings


def _validate_controls(
    controls: Any, expected_hash: str, *, require_controls: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(controls, list):
        return [{"code": "controls_not_list"}], []
    if not controls:
        warnings.append(
            {
                "code": "matched_control_missing",
                "message": "No rights-compatible matched control is recorded.",
            }
        )
        if require_controls:
            errors.append({"code": "matched_control_required"})
        return errors, warnings
    for index, control in enumerate(controls, start=1):
        if not isinstance(control, dict):
            errors.append({"control": index, "code": "control_not_object"})
            continue
        for field in ("control_id", "text_sha256", "language", "genre", "provenance", "relation"):
            if not isinstance(control.get(field), str) or not control[field].strip():
                errors.append({"control": index, "code": "control_field_missing", "field": field})
        if not _valid_sha256(control.get("text_sha256")):
            errors.append({"control": index, "code": "invalid_control_hash"})
        control_hash = control.get("text_sha256")
        if isinstance(control_hash, str) and control_hash.casefold() == expected_hash.casefold():
            errors.append({"control": index, "code": "control_hash_matches_target"})
        if control.get("provenance") not in CONTROL_PROVENANCES:
            errors.append({"control": index, "code": "invalid_control_provenance", "value": control.get("provenance")})
    return errors, warnings


def _validate_replication(
    replication: Any, observations: list[Any], *, require_complete: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(replication, dict):
        return [{"code": "replication_not_object"}], [], {"observed_runs": 0}
    required_runs = replication.get("required_runs", 2)
    if isinstance(required_runs, bool) or not isinstance(required_runs, int) or required_runs < 1:
        errors.append({"code": "invalid_required_runs", "value": required_runs})
        required_runs = 1
    if require_complete and required_runs < 2:
        errors.append({"code": "replication_plan_too_small", "required_runs": required_runs, "minimum": 2})
    noise = replication.get("rerun_noise_threshold")
    if noise is not None and (_number(noise) is None or _number(noise) < 0):
        errors.append({"code": "invalid_rerun_noise_threshold", "value": noise})
    seen: set[tuple[str, int]] = set()
    observed_runs = 0
    for index, observation in enumerate(observations, start=1):
        if not isinstance(observation, dict):
            continue
        if observation.get("status") == "observed":
            observed_runs += 1
        rerun_index = observation.get("rerun_index", 1)
        key = (str(observation.get("detector_name", "")), rerun_index)
        if isinstance(rerun_index, int) and key in seen:
            errors.append({"observation": index, "code": "duplicate_rerun_index", "rerun_index": rerun_index})
        elif isinstance(rerun_index, int):
            seen.add(key)
    if observed_runs < required_runs:
        warnings.append(
            {
                "code": "replication_incomplete",
                "required_runs": required_runs,
                "observed_runs": observed_runs,
            }
        )
        if require_complete:
            errors.append({"code": "replication_required", "required_runs": required_runs, "observed_runs": observed_runs})
    summary = {
        "required_runs": required_runs,
        "observed_runs": observed_runs,
        "rerun_noise_threshold": noise,
        "status": (
            "not_started"
            if observed_runs == 0
            else "single_observation"
            if observed_runs == 1
            else "replicated"
        ),
    }
    return errors, warnings, summary


def validate_manifest(
    manifest: dict[str, Any],
    text_path: str | Path | None = None,
    *,
    require_preregistration: bool = False,
    require_execution_provenance: bool = False,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    manifest_schema = manifest.get("schema_version")
    if manifest_schema not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append({"code": "unsupported_schema", "value": manifest.get("schema_version")})
    elif manifest_schema != SCHEMA_VERSION:
        warnings.append(
            {
                "code": "legacy_schema",
                "value": manifest_schema,
                "message": "Historical record is readable but cannot satisfy the current clean-forward trace standard.",
            }
        )
    for field in ("sample_id", "stage", "mode", "provenance", "language", "genre"):
        if not isinstance(manifest.get(field), str) or not manifest[field].strip():
            errors.append({"code": "missing_manifest_field", "field": field})
    if manifest.get("mode") not in MODES:
        errors.append({"code": "invalid_mode", "value": manifest.get("mode")})
    if manifest.get("provenance") not in PROVENANCES:
        errors.append({"code": "invalid_provenance", "value": manifest.get("provenance")})

    prereg_errors, prereg_warnings, prereg_state = _validate_preregistration(
        manifest.get("pre_registration", {"status": "not_registered"}),
        require_registered=require_preregistration,
    )
    errors.extend(prereg_errors)

    quality_errors, quality_warnings = _validate_quality(
        manifest.get("quality", {}),
        require_complete=require_preregistration and manifest.get("stage") in {"final", "holdout"},
    )
    errors.extend(quality_errors)
    if manifest.get("stage") in {"final", "holdout"} or manifest.get("observations"):
        warnings.extend(quality_warnings)

    expected_hash = manifest.get("text_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        errors.append({"code": "missing_or_invalid_text_sha256"})
        expected_hash = ""

    preregistration = manifest.get("pre_registration", {})
    record_requires_execution = (
        isinstance(preregistration, dict)
        and preregistration.get("execution_provenance_required") is True
    )
    composition_process = (
        preregistration.get("composition_process", "")
        if isinstance(preregistration, dict)
        else ""
    )
    trace_required = (
        manifest_schema == SCHEMA_VERSION
        and (
            manifest.get("mode") == "new_generation"
            or composition_process in {"new_generation", "full_reconstruction"}
            or (manifest.get("mode") == "revision" and composition_process != "local_edit")
        )
    )
    if (
        manifest_schema in SUPPORTED_SCHEMA_VERSIONS
        and manifest_schema != SCHEMA_VERSION
        and (require_execution_provenance or record_requires_execution)
        and (
            manifest.get("mode") == "new_generation"
            or composition_process in {"new_generation", "full_reconstruction"}
            or (manifest.get("mode") == "revision" and composition_process != "local_edit")
        )
    ):
        errors.append(
            {
                "code": "legacy_schema_cannot_prove_current_clean_forward_test",
                "value": manifest_schema,
            }
        )
    execution_errors, execution_warnings, execution_summary = _validate_execution_provenance(
        manifest.get("execution_provenance", {}),
        expected_hash,
        require_complete=require_execution_provenance or record_requires_execution,
        require_composition_trace=trace_required,
    )
    errors.extend(execution_errors)
    if manifest.get("stage") in {"final", "holdout"} or manifest.get("observations"):
        warnings.extend(execution_warnings)

    manifest_text_path = manifest.get("text_path")
    if text_path is None and (not isinstance(manifest_text_path, str) or not manifest_text_path.strip()):
        errors.append({"code": "missing_text_path"})
    else:
        path = Path(text_path) if text_path is not None else Path(manifest_text_path)
        if not path.exists() or not path.is_file():
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
    if prereg_warnings and (observations or manifest.get("stage") in {"final", "holdout"} or require_preregistration):
        warnings.extend(prereg_warnings)
    for index, observation in enumerate(observations, start=1):
        for error in validate_observation(observation, expected_hash):
            errors.append({"observation": index, **error})

    control_errors, control_warnings = _validate_controls(
        manifest.get("controls", []),
        expected_hash,
        require_controls=require_preregistration and manifest.get("stage") in {"final", "holdout"},
    )
    errors.extend(control_errors)
    if manifest.get("stage") in {"final", "holdout"} or observations:
        warnings.extend(control_warnings)

    replication_errors, replication_warnings, replication_summary = _validate_replication(
        manifest.get("replication", {"required_runs": 2}),
        observations,
        require_complete=require_preregistration and manifest.get("stage") in {"final", "holdout"},
    )
    errors.extend(replication_errors)
    if observations or manifest.get("stage") in {"final", "holdout"}:
        warnings.extend(replication_warnings)

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
        "preregistration_status": prereg_state,
        "replication": replication_summary,
        "execution_provenance": execution_summary,
        "control_count": len(manifest.get("controls", [])) if isinstance(manifest.get("controls", []), list) else 0,
        "status": status,
        "disclaimer": "A valid record proves bookkeeping only; detector output cannot prove authorship.",
    }


def add_observation(manifest: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    if "rerun_index" not in observation:
        detector_name = observation.get("detector_name", "")
        prior = [
            item.get("rerun_index", 0)
            for item in manifest.get("observations", [])
            if isinstance(item, dict) and item.get("detector_name", "") == detector_name
        ]
        observation["rerun_index"] = max(prior, default=0) + 1
    if "raw_components" not in observation and "raw_component_scores" in observation:
        observation["raw_components"] = observation["raw_component_scores"]
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
    init_parser.add_argument("--pre-registration-file")
    init_parser.add_argument("--controls-file")
    init_parser.add_argument("-o", "--output", required=True)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("manifest")
    validate_parser.add_argument("--text")
    validate_parser.add_argument("--pretty", action="store_true")
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.add_argument(
        "--require-preregistration",
        action="store_true",
        help="Treat missing locked preregistration, matched controls, or required reruns as errors.",
    )
    validate_parser.add_argument(
        "--require-execution-provenance",
        action="store_true",
        help="Require a frozen skill hash, explicit invocation, fresh context, files-read trace, and unedited output hash.",
    )
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
            pre_registration = None
            controls = None
            if args.pre_registration_file:
                pre_registration = _read_json_value(args.pre_registration_file)
                if not isinstance(pre_registration, dict):
                    raise ValueError("pre-registration JSON root must be an object")
            if args.controls_file:
                controls = _read_json_value(args.controls_file)
                if not isinstance(controls, list):
                    raise ValueError("controls JSON root must be a list")
            manifest = init_manifest(
                args.text,
                sample_id=args.sample_id,
                stage=args.stage,
                mode=args.mode,
                provenance=args.provenance,
                language=args.language,
                genre=args.genre,
                pre_registration=pre_registration,
                controls=controls,
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
        report = validate_manifest(
            manifest,
            args.text,
            require_preregistration=args.require_preregistration,
            require_execution_provenance=args.require_execution_provenance,
        )
        _write_output(report, args.output, args.pretty)
        return 1 if args.strict and report["errors"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
