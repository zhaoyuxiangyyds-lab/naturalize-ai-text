#!/usr/bin/env python3
"""Create and validate a compact, tamper-evident composition trace.

The trace records auditable writing commitments, not private reasoning. It can
show that a declared event sequence is internally consistent; it cannot prove
authorship, cognition, contemporaneous intent, or detector benefit.
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


TOOL_NAME = "composition-trace"
TOOL_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"
MODES = {"new_generation", "full_reconstruction"}
PHASES = {
    "material_commit",
    "section_commit",
    "section_result",
    "route_change",
    "reconciliation",
}
ZERO_HASH = "0" * 64


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", value))


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _read(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("trace root must be an object")
    return value


def _write(path: str | Path, value: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f"{target.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(target)


def start_trace(*, mode: str, language: str, genre: str) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if not language.strip() or not genre.strip():
        raise ValueError("language and genre must be non-empty")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "created_at": _now(),
        "mode": mode,
        "language": language,
        "genre": genre,
        "started_before_prose": True,
        "events": [],
        "final_output": {"path": "", "sha256": ""},
        "status": "active",
    }


def append_event(
    trace: dict[str, Any],
    *,
    phase: str,
    unit_ids: list[str] | None = None,
    section_id: str = "",
    decision: str = "",
    state_before: str = "",
    state_change: str = "",
) -> dict[str, Any]:
    if trace.get("status") != "active":
        raise ValueError("only an active trace can receive events")
    if phase not in PHASES:
        raise ValueError(f"unsupported phase: {phase}")
    events = trace.setdefault("events", [])
    if not isinstance(events, list):
        raise ValueError("events must be a list")

    cleaned_ids = [item.strip() for item in (unit_ids or []) if item.strip()]
    event: dict[str, Any] = {
        "sequence": len(events) + 1,
        "recorded_at": _now(),
        "phase": phase,
        "previous_event_sha256": events[-1]["event_sha256"] if events else ZERO_HASH,
    }
    if cleaned_ids:
        event["unit_ids"] = cleaned_ids
    if section_id.strip():
        event["section_id"] = section_id.strip()
    if decision.strip():
        event["decision"] = decision.strip()
    if state_before.strip():
        event["state_before"] = state_before.strip()
    if state_change.strip():
        event["state_change"] = state_change.strip()
    event["event_sha256"] = _event_hash(event)
    events.append(event)
    return trace


def finalize_trace(trace: dict[str, Any], text_path: str | Path) -> dict[str, Any]:
    text = Path(text_path)
    if not text.is_file():
        raise ValueError(f"final text does not exist: {text}")
    report = validate_trace(trace, require_finalized=True)
    blocking = [
        item
        for item in report["errors"]
        if item.get("code") not in {"trace_not_finalized", "final_output_missing"}
    ]
    if blocking:
        raise ValueError(f"trace cannot be finalized: {blocking}")
    trace["final_output"] = {"path": str(text), "sha256": _sha256(text)}
    trace["finalized_at"] = _now()
    trace["status"] = "finalized"
    return trace


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _required_fields(event: dict[str, Any], phase: str) -> tuple[str, ...]:
    return {
        "material_commit": ("unit_ids", "decision"),
        "section_commit": ("section_id", "unit_ids", "state_before", "decision"),
        "section_result": ("section_id", "unit_ids", "state_change"),
        "route_change": ("state_before", "decision"),
        "reconciliation": ("unit_ids", "decision", "state_change"),
    }.get(phase, ())


def validate_trace(
    trace: Any,
    text_path: str | Path | None = None,
    *,
    require_finalized: bool = True,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if not isinstance(trace, dict):
        return {
            "errors": [{"code": "trace_not_object"}],
            "warnings": [],
            "status": "fail",
        }

    if trace.get("schema_version") != SCHEMA_VERSION:
        errors.append({"code": "unsupported_trace_schema", "value": trace.get("schema_version")})
    if trace.get("mode") not in MODES:
        errors.append({"code": "invalid_trace_mode", "value": trace.get("mode")})
    for field in ("language", "genre"):
        if not isinstance(trace.get(field), str) or not trace[field].strip():
            errors.append({"code": "missing_trace_field", "field": field})
    if trace.get("started_before_prose") is not True:
        errors.append({"code": "trace_not_started_before_prose"})

    created_at = trace.get("created_at")
    if not _valid_timestamp(created_at):
        errors.append({"code": "invalid_trace_created_at", "value": created_at})
        prior_time = None
    else:
        prior_time = _timestamp(created_at)

    events = trace.get("events", [])
    if not isinstance(events, list):
        errors.append({"code": "trace_events_not_list"})
        events = []
    if not events:
        errors.append({"code": "trace_events_missing"})

    previous_hash = ZERO_HASH
    commits: dict[str, dict[str, Any]] = {}
    results: dict[str, dict[str, Any]] = {}
    material_seen = False
    reconciliation_seen = False
    open_section_id: str | None = None

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            errors.append({"event": index, "code": "trace_event_not_object"})
            continue
        if event.get("sequence") != index:
            errors.append(
                {"event": index, "code": "trace_sequence_mismatch", "actual": event.get("sequence")}
            )
        phase = event.get("phase")
        if phase not in PHASES:
            errors.append({"event": index, "code": "invalid_trace_phase", "value": phase})
        if open_section_id is not None and phase != "section_result":
            errors.append(
                {
                    "event": index,
                    "code": "section_result_not_immediate",
                    "section_id": open_section_id,
                    "actual_phase": phase,
                }
            )
            open_section_id = None
        if reconciliation_seen:
            errors.append({"event": index, "code": "event_after_reconciliation"})

        recorded_at = event.get("recorded_at")
        if not _valid_timestamp(recorded_at):
            errors.append({"event": index, "code": "invalid_trace_event_time", "value": recorded_at})
        elif prior_time is not None:
            current_time = _timestamp(recorded_at)
            if current_time < prior_time:
                errors.append({"event": index, "code": "trace_time_reversed"})
            prior_time = current_time

        if event.get("previous_event_sha256") != previous_hash:
            errors.append({"event": index, "code": "trace_chain_previous_hash_mismatch"})
        actual_event_hash = _event_hash(event)
        if event.get("event_sha256") != actual_event_hash:
            errors.append({"event": index, "code": "trace_event_hash_mismatch"})
        previous_hash = event.get("event_sha256", "")

        for field in _required_fields(event, str(phase)):
            value = event.get(field)
            valid = _nonempty_string_list(value) if field == "unit_ids" else isinstance(value, str) and bool(value.strip())
            if not valid:
                errors.append({"event": index, "code": "trace_event_field_missing", "field": field})

        if phase == "material_commit":
            material_seen = True
        elif phase == "section_commit":
            section_id = event.get("section_id")
            if not material_seen:
                errors.append({"event": index, "code": "section_commit_before_material"})
            if isinstance(section_id, str):
                if section_id in commits:
                    errors.append({"event": index, "code": "duplicate_section_commit", "section_id": section_id})
                commits[section_id] = event
                open_section_id = section_id
        elif phase == "section_result":
            section_id = event.get("section_id")
            if isinstance(section_id, str):
                if open_section_id != section_id:
                    errors.append(
                        {
                            "event": index,
                            "code": "section_result_not_for_open_commit",
                            "expected": open_section_id,
                            "actual": section_id,
                        }
                    )
                if section_id not in commits:
                    errors.append({"event": index, "code": "section_result_without_commit", "section_id": section_id})
                if section_id in results:
                    errors.append({"event": index, "code": "duplicate_section_result", "section_id": section_id})
                results[section_id] = event
                commit = commits.get(section_id)
                if commit and commit.get("unit_ids") != event.get("unit_ids"):
                    errors.append({"event": index, "code": "section_unit_ids_changed", "section_id": section_id})
                open_section_id = None
        elif phase == "reconciliation":
            reconciliation_seen = True

    if events and isinstance(events[0], dict) and events[0].get("phase") != "material_commit":
        errors.append({"code": "first_event_not_material_commit"})
    for section_id in commits:
        if section_id not in results:
            errors.append({"code": "section_result_missing", "section_id": section_id})
    if open_section_id is not None:
        errors.append({"code": "section_result_missing", "section_id": open_section_id})
    if results and set(results) - set(commits):
        errors.append({"code": "unmatched_section_results"})
    if require_finalized and not commits:
        errors.append({"code": "section_commit_missing"})
    if require_finalized and not reconciliation_seen:
        errors.append({"code": "reconciliation_event_missing"})

    trace_status = trace.get("status")
    if require_finalized and trace_status != "finalized":
        errors.append({"code": "trace_not_finalized", "value": trace_status})

    final_output = trace.get("final_output")
    final_hash = ""
    if not isinstance(final_output, dict):
        errors.append({"code": "final_output_not_object"})
    else:
        final_hash = final_output.get("sha256", "")
        if require_finalized and not _valid_sha256(final_hash):
            errors.append({"code": "final_output_missing"})
        if final_hash and not _valid_sha256(final_hash):
            errors.append({"code": "invalid_final_output_hash", "value": final_hash})

    if text_path is not None:
        text = Path(text_path)
        if not text.is_file():
            errors.append({"code": "trace_text_file_missing", "path": str(text)})
        else:
            actual = _sha256(text)
            if final_hash and actual.casefold() != final_hash.casefold():
                errors.append(
                    {"code": "trace_output_hash_mismatch", "expected": final_hash, "actual": actual}
                )

    if trace_status == "finalized":
        finalized_at = trace.get("finalized_at")
        if not _valid_timestamp(finalized_at):
            errors.append({"code": "invalid_trace_finalized_at", "value": finalized_at})
        elif prior_time is not None and _timestamp(finalized_at) < prior_time:
            errors.append({"code": "trace_finalized_before_last_event"})

    warnings.append(
        {
            "code": "trace_scope_limit",
            "message": "A self-declared trace proves record consistency only, not authorship, cognition, or detector effect.",
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION, "deterministic": True},
        "trace_sha256": None,
        "final_output_sha256": final_hash,
        "event_count": len(events),
        "section_count": len(commits),
        "errors": errors,
        "warnings": warnings,
        "status": "fail" if errors else "pass",
        "disclaimer": "Trace consistency is not authorship or detector evidence.",
    }


def validate_trace_file(
    trace_path: str | Path,
    text_path: str | Path | None = None,
    *,
    require_finalized: bool = True,
) -> dict[str, Any]:
    path = Path(trace_path)
    if not path.is_file():
        return {
            "errors": [{"code": "trace_file_missing", "path": str(path)}],
            "warnings": [],
            "status": "fail",
            "trace_sha256": None,
            "final_output_sha256": "",
            "event_count": 0,
            "section_count": 0,
        }
    try:
        trace = _read(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "errors": [{"code": "trace_file_invalid", "message": str(exc)}],
            "warnings": [],
            "status": "fail",
            "trace_sha256": _sha256(path),
            "final_output_sha256": "",
            "event_count": 0,
            "section_count": 0,
        }
    report = validate_trace(trace, text_path, require_finalized=require_finalized)
    report["trace_sha256"] = _sha256(path)
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
        Path(output).write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and validate a compact composition trace.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--mode", required=True, choices=sorted(MODES))
    start.add_argument("--language", required=True)
    start.add_argument("--genre", required=True)
    start.add_argument("-o", "--output", required=True)

    event = sub.add_parser("event")
    event.add_argument("trace")
    event.add_argument("--phase", required=True, choices=sorted(PHASES))
    event.add_argument("--unit-id", action="append", default=[])
    event.add_argument("--section-id", default="")
    event.add_argument("--decision", default="")
    event.add_argument("--state-before", default="")
    event.add_argument("--state-change", default="")

    finalize = sub.add_parser("finalize")
    finalize.add_argument("trace")
    finalize.add_argument("--text", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("trace")
    validate.add_argument("--text")
    validate.add_argument("--strict", action="store_true")
    validate.add_argument("--pretty", action="store_true")
    validate.add_argument("-o", "--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "start":
            trace = start_trace(mode=args.mode, language=args.language, genre=args.genre)
            _write(args.output, trace)
            return 0
        if args.command == "event":
            trace = _read(args.trace)
            append_event(
                trace,
                phase=args.phase,
                unit_ids=args.unit_id,
                section_id=args.section_id,
                decision=args.decision,
                state_before=args.state_before,
                state_change=args.state_change,
            )
            _write(args.trace, trace)
            return 0
        if args.command == "finalize":
            trace = _read(args.trace)
            finalize_trace(trace, args.text)
            _write(args.trace, trace)
            return 0
        report = validate_trace_file(args.trace, args.text, require_finalized=True)
        _write_output(report, args.output, args.pretty)
        return 1 if args.strict and report["errors"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"{TOOL_NAME}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
