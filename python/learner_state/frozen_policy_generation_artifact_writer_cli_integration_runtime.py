"""Metadata-only artifact writer CLI integration runtime boundary.

This module builds a safe runtime summary from synthetic metadata-only
artifact writer CLI integration runtime fixtures. It does not call artifact
body generation, call the manifest writer, generate policy bodies, write
files, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation import (
    ARTIFACT_WRITER_CLI_METADATA_FILE,
    ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION,
    DEFAULT_FIXTURE_ROOT,
    POINTER_METADATA_FILE,
    POINTER_METADATA_SCHEMA_VERSION,
    REQUEST_METADATA_FILE,
    REQUEST_METADATA_SCHEMA_VERSION,
)

MODE = "artifact_writer_cli_integration_runtime"
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "runtime_v0.1"
)
DEFAULT_FIXTURE_CASE = "valid/valid_minimal_metadata_runtime_pass"

USAGE_ERROR_REASONS = frozenset(
    {
        "ambiguous_file_writing_target",
        "duplicate_case_id",
        "mismatched_expected_status",
        "missing_required_metadata_file",
        "unsupported_schema_version",
        "case_id_mismatch",
        "malformed_json_metadata",
        "missing_cli_argument",
        "unsafe_fixture_case_selector",
        "fixture_case_missing",
    }
)

REQUEST_SENTINEL_FIELDS = (
    "request_body_present",
    "expected_body_present",
    "artifact_body_payload_present",
    "manifest_body_present",
    "generated_policy_body_present",
    "final_text_present",
    "observed_after_text_present",
    "gold_label_present",
    "post_hoc_annotation_present",
)
POINTER_SENTINEL_FIELDS = (
    "pointer_body_present",
    "raw_learner_text_present",
    "raw_rows_present",
    "logits_present",
    "probabilities_present",
    "private_path_present",
    "absolute_path_present",
)
CLI_SENTINEL_FIELDS = (
    "artifact_body_generation_requested",
    "manifest_writer_requested",
    "ambiguous_file_writing_target",
)

FORBIDDEN_ACTUAL_KEYS = frozenset(
    {
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "artifact_body_payload",
        "generated_policy_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "raw_learner_text",
        "real_participant_data",
        "performance_metric_body",
    }
)


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationRuntimeSummary:
    status: str
    reason_code: str
    exit_code_category: str
    case_id: str | None
    command_label: str | None
    summary_mode: str
    mismatch_reasons: tuple[str, ...] = ()
    mode: str = MODE
    runtime_schema_version: str = RUNTIME_SCHEMA_VERSION
    content_suppressed: bool = True
    body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_generated_policy_body: bool = True
    no_artifact_body_payload: bool = True
    no_manifest_body: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_oracle_checked: bool = True
    synthetic_only_checked: bool = True
    metadata_only_checked: bool = True
    file_writing_enabled: bool = False
    residue_expected: bool = False
    runtime_executed: bool = True
    artifact_writer_cli_invoked: bool = False
    artifact_writer_cli_invocation_planned: bool = True
    artifact_body_generation_invoked: bool = False
    manifest_writer_invoked: bool = False
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False

    @property
    def return_code(self) -> int:
        if self.status == "pass":
            return 0
        if self.status == "usage_error":
            return 2
        return 1

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "runtime_schema_version": self.runtime_schema_version,
            "status": self.status,
            "reason_code": self.reason_code,
            "exit_code_category": self.exit_code_category,
            "case_id": self.case_id,
            "command_label": self.command_label,
            "summary_mode": self.summary_mode,
            "content_suppressed": self.content_suppressed,
            "body_suppressed": self.body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_manifest_body": self.no_manifest_body,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_oracle_checked": self.no_oracle_checked,
            "synthetic_only_checked": self.synthetic_only_checked,
            "metadata_only_checked": self.metadata_only_checked,
            "file_writing_enabled": self.file_writing_enabled,
            "residue_expected": self.residue_expected,
            "runtime_executed": self.runtime_executed,
            "artifact_writer_cli_invoked": self.artifact_writer_cli_invoked,
            "artifact_writer_cli_invocation_planned": (
                self.artifact_writer_cli_invocation_planned
            ),
            "artifact_body_generation_invoked": (
                self.artifact_body_generation_invoked
            ),
            "manifest_writer_invoked": self.manifest_writer_invoked,
            "production_readiness_claimed": self.production_readiness_claimed,
            "real_data_readiness_claimed": self.real_data_readiness_claimed,
            "performance_claims_present": self.performance_claims_present,
            "mismatch_reasons": list(self.mismatch_reasons),
        }


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationRuntimeInputs:
    request_metadata_path: Path
    pointer_metadata_path: Path
    artifact_writer_cli_metadata_path: Path
    case_id: str | None = None


def run_artifact_writer_cli_integration_runtime_for_fixture_case(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
    fixture_case: str = DEFAULT_FIXTURE_CASE,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    if _unsafe_fixture_case_selector(fixture_case):
        return _safe_error("usage_error", "unsafe_fixture_case_selector")

    case_dir = Path(fixture_root) / fixture_case
    if not case_dir.is_dir():
        return _safe_error("usage_error", "fixture_case_missing", case_id=fixture_case)

    return run_artifact_writer_cli_integration_runtime(
        request_metadata_path=case_dir / REQUEST_METADATA_FILE,
        pointer_metadata_path=case_dir / POINTER_METADATA_FILE,
        artifact_writer_cli_metadata_path=case_dir
        / ARTIFACT_WRITER_CLI_METADATA_FILE,
    )


def run_artifact_writer_cli_integration_runtime(
    *,
    request_metadata_path: str | Path,
    pointer_metadata_path: str | Path,
    artifact_writer_cli_metadata_path: str | Path,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    inputs = ArtifactWriterCliIntegrationRuntimeInputs(
        request_metadata_path=Path(request_metadata_path),
        pointer_metadata_path=Path(pointer_metadata_path),
        artifact_writer_cli_metadata_path=Path(artifact_writer_cli_metadata_path),
    )
    missing = [
        path
        for path in (
            inputs.request_metadata_path,
            inputs.pointer_metadata_path,
            inputs.artifact_writer_cli_metadata_path,
        )
        if not path.is_file()
    ]
    if missing:
        return _safe_error("usage_error", "missing_required_metadata_file")

    try:
        request_metadata = _load_json_object(inputs.request_metadata_path)
        pointer_metadata = _load_json_object(inputs.pointer_metadata_path)
        artifact_writer_cli_metadata = _load_json_object(
            inputs.artifact_writer_cli_metadata_path
        )
    except (OSError, json.JSONDecodeError, ValueError):
        return _safe_error("usage_error", "malformed_json_metadata")

    return _summarize_metadata(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )


def _summarize_metadata(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    case_id = _common_case_id(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )
    command_label = _safe_string(
        artifact_writer_cli_metadata.get("command_label")
    )
    summary_mode = _safe_string(
        artifact_writer_cli_metadata.get("summary_mode")
    ) or "public_safe_count_only"
    mismatch_reasons: list[str] = []

    _detect_forbidden_actual_keys(
        (request_metadata, pointer_metadata, artifact_writer_cli_metadata),
        mismatch_reasons,
    )
    if mismatch_reasons:
        return _safe_error(
            "fail_closed",
            "forbidden_field_detected",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
            mismatch_reasons=tuple(mismatch_reasons),
        )

    if not case_id:
        return _safe_error(
            "usage_error",
            "case_id_mismatch",
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if (
        request_metadata.get("schema_version") != REQUEST_METADATA_SCHEMA_VERSION
        or pointer_metadata.get("schema_version") != POINTER_METADATA_SCHEMA_VERSION
        or artifact_writer_cli_metadata.get("schema_version")
        != ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION
    ):
        return _safe_error(
            "usage_error",
            "unsupported_schema_version",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if request_metadata.get("synthetic_only") is not True:
        return _safe_error(
            "fail_closed",
            "synthetic_only_violation",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )
    if request_metadata.get("metadata_only") is not True:
        return _safe_error(
            "fail_closed",
            "metadata_only_violation",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    reason_code = _first_runtime_reason(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )
    if reason_code != "none":
        status = "usage_error" if reason_code in USAGE_ERROR_REASONS else "fail_closed"
        return _safe_error(
            status,
            reason_code,
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if request_metadata.get("file_writing_requested") is not False:
        return _safe_error(
            "fail_closed",
            "file_writing_requested_unexpectedly",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if artifact_writer_cli_metadata.get("safe_mode") != "metadata_only":
        return _safe_error(
            "fail_closed",
            "safe_mode_not_metadata_only",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    return ArtifactWriterCliIntegrationRuntimeSummary(
        status="pass",
        reason_code="none",
        exit_code_category="zero",
        case_id=case_id,
        command_label=command_label,
        summary_mode=summary_mode,
    )


def _safe_error(
    status: str,
    reason_code: str,
    *,
    case_id: str | None = None,
    command_label: str | None = None,
    summary_mode: str = "public_safe_count_only",
    mismatch_reasons: tuple[str, ...] = (),
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    return ArtifactWriterCliIntegrationRuntimeSummary(
        status=status,
        reason_code=reason_code,
        exit_code_category="nonzero",
        case_id=case_id,
        command_label=command_label,
        summary_mode=summary_mode,
        mismatch_reasons=mismatch_reasons,
        artifact_writer_cli_invocation_planned=False,
    )


def _load_json_object(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("metadata_json_not_object")
    return payload


def _common_case_id(*payloads: Mapping[str, Any]) -> str | None:
    case_ids = {_safe_string(payload.get("case_id")) for payload in payloads}
    case_ids.discard(None)
    if len(case_ids) != 1:
        return None
    return next(iter(case_ids))


def _first_runtime_reason(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
) -> str:
    for payload in (request_metadata, pointer_metadata, artifact_writer_cli_metadata):
        marker = _safe_string(payload.get("forbidden_marker"))
        if marker and marker != "none":
            return marker

    for field in REQUEST_SENTINEL_FIELDS:
        if request_metadata.get(field) is True:
            return field
    for field in POINTER_SENTINEL_FIELDS:
        if pointer_metadata.get(field) is True:
            return field
    if artifact_writer_cli_metadata.get("artifact_body_generation_requested") is True:
        return "unexpected_artifact_body_generation_request"
    if artifact_writer_cli_metadata.get("manifest_writer_requested") is True:
        return "unexpected_manifest_writer_request"
    if artifact_writer_cli_metadata.get("ambiguous_file_writing_target") is True:
        return "ambiguous_file_writing_target"
    return "none"


def _detect_forbidden_actual_keys(
    payloads: Sequence[Mapping[str, Any]],
    mismatch_reasons: list[str],
) -> None:
    for payload in payloads:
        for key in payload:
            if key in FORBIDDEN_ACTUAL_KEYS:
                mismatch_reasons.append(f"forbidden_actual_key:{key}")


def _safe_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _unsafe_fixture_case_selector(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or ".." in path.parts or value.startswith("/")


def _format_human(summary: ArtifactWriterCliIntegrationRuntimeSummary) -> str:
    payload = summary.to_public_dict()
    ordered_keys = (
        "mode",
        "runtime_schema_version",
        "status",
        "reason_code",
        "exit_code_category",
        "case_id",
        "command_label",
        "summary_mode",
        "content_suppressed",
        "body_suppressed",
        "file_writing_enabled",
        "runtime_executed",
        "artifact_writer_cli_invoked",
        "artifact_writer_cli_invocation_planned",
        "artifact_body_generation_invoked",
        "manifest_writer_invoked",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
    )
    return "\n".join(f"{key}={payload[key]}" for key in ordered_keys) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the metadata-only artifact writer CLI integration runtime "
            "boundary over fixture metadata."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Synthetic runtime fixture root.",
    )
    parser.add_argument(
        "--fixture-case",
        default=DEFAULT_FIXTURE_CASE,
        help="Relative fixture case selector used when explicit metadata paths are omitted.",
    )
    parser.add_argument("--request-metadata", help="Request metadata JSON path.")
    parser.add_argument("--pointer-metadata", help="Pointer metadata JSON path.")
    parser.add_argument(
        "--artifact-writer-cli-metadata",
        help="Artifact writer CLI metadata JSON path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a public-safe JSON summary.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    explicit_paths = (
        args.request_metadata,
        args.pointer_metadata,
        args.artifact_writer_cli_metadata,
    )
    if any(explicit_paths) and not all(explicit_paths):
        summary = _safe_error("usage_error", "missing_cli_argument")
    elif all(explicit_paths):
        summary = run_artifact_writer_cli_integration_runtime(
            request_metadata_path=args.request_metadata,
            pointer_metadata_path=args.pointer_metadata,
            artifact_writer_cli_metadata_path=args.artifact_writer_cli_metadata,
        )
    else:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            fixture_root=args.fixture_root,
            fixture_case=args.fixture_case,
        )

    if args.json:
        print(json.dumps(summary.to_public_dict(), indent=2, sort_keys=True))
    else:
        print(_format_human(summary), end="")
    return summary.return_code


if __name__ == "__main__":
    sys.exit(main())
