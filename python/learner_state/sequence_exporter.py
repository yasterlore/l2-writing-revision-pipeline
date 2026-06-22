"""Minimal synthetic learner-state sequence exporter.

The exporter reads synthetic-only upstream fixture inputs and writes separated
feature, label, and manifest outputs. It keeps results safe/count-only and runs
the learner-state sequence audit before returning success.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from learner_state.sequence_audit import AuditResult, audit_sequence_dataset

FEATURE_SCHEMA_VERSION = "learner_state_feature_v0.1"
LABEL_SCHEMA_VERSION = "learner_state_label_v0.1"
MANIFEST_SCHEMA_VERSION = "learner_state_sequence_manifest_v0.1"

SAFE_EPISODES_FILE = "safe_episodes.jsonl"
CANDIDATE_SCORES_FILE = "candidate_scores.jsonl"
DIAGNOSTIC_SUMMARY_FILE = "diagnostic_summary.json"
LABELS_SOURCE_FILE = "labels_source.jsonl"
SYNTHETIC_METADATA_FILE = "synthetic_metadata.json"
SPLIT_METADATA_FILE = "split_metadata.json"
EXPECTED_OUTPUT_CONTRACT_FILE = "expected_output_contract.json"
EXPECTED_FAILURE_CONTRACT_FILE = "expected_failure_contract.json"

FEATURES_OUTPUT_FILE = "features.jsonl"
LABELS_OUTPUT_FILE = "labels.jsonl"
MANIFEST_OUTPUT_FILE = "manifest.json"
OUTPUT_FILE_NAMES = frozenset(
    {
        FEATURES_OUTPUT_FILE,
        LABELS_OUTPUT_FILE,
        MANIFEST_OUTPUT_FILE,
    }
)
EXPORTER_FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_exporter")
UNSAFE_CLI_PATH_PARTS = frozenset(
    {
        "manual_outputs",
        "private_data",
        "real_data",
        "participant_data",
    }
)

SAFE_EPISODE_INPUT_SCHEMA_VERSION = "exporter_input_safe_episode_v0.1"
CANDIDATE_SCORE_SCHEMA_VERSION = "candidate_score_summary_v0.1"
LABEL_SOURCE_SCHEMA_VERSION = "synthetic_label_source_v0.1"
SYNTHETIC_METADATA_SCHEMA_VERSION = "exporter_synthetic_metadata_v0.1"
SPLIT_METADATA_SCHEMA_VERSION = "synthetic_split_metadata_v0.1"

FORBIDDEN_FEATURE_KEYS = {
    "expected_action",
    "expected_action_family",
    "expected_action_type",
    "label_source",
    "final_text",
    "observed_after_text",
    "gold_label",
    "teacher_correction",
    "human_correction",
    "post_hoc_annotation",
    "raw_text",
    "future_episode",
    "future_edit",
    "next_episode_action",
}


@dataclass(frozen=True)
class ExporterInputBundle:
    safe_episodes: list[dict[str, Any]]
    candidate_scores: list[dict[str, Any]]
    diagnostic_summary: dict[str, Any]
    labels_source: list[dict[str, Any]]
    synthetic_metadata: dict[str, Any]
    split_metadata: dict[str, Any]
    expected_output_contract: dict[str, Any]


@dataclass(frozen=True)
class ExportResult:
    export_status: str
    features_path: Path
    labels_path: Path
    manifest_path: Path
    feature_row_count: int
    label_row_count: int
    participant_count: int
    session_count: int
    task_count: int
    episode_count: int
    audit_status: str
    audit_reason_codes: list[str] = field(default_factory=list)
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "export_status": self.export_status,
            "feature_row_count": self.feature_row_count,
            "label_row_count": self.label_row_count,
            "participant_count": self.participant_count,
            "session_count": self.session_count,
            "task_count": self.task_count,
            "episode_count": self.episode_count,
            "audit_status": self.audit_status,
            "audit_reason_codes": self.audit_reason_codes,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only": self.synthetic_only,
        }


@dataclass(frozen=True)
class ExportFailureSummary:
    export_status: str
    reason_codes: list[str]
    failure_categories: list[str]
    stage: str
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "export_status": self.export_status,
            "reason_codes": self.reason_codes,
            "failure_categories": self.failure_categories,
            "stage": self.stage,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
        }


class ExporterFailure(Exception):
    """Safe fail-closed exporter failure without raw input content."""

    def __init__(
        self,
        reason_code: str,
        failure_category: str,
        stage: str = "input_validation",
    ) -> None:
        self.summary = ExportFailureSummary(
            export_status="fail",
            reason_codes=[reason_code],
            failure_categories=[failure_category],
            stage=stage,
        )
        super().__init__(
            "sequence_export_failed:"
            f"stage={stage};category={failure_category};reason={reason_code}"
        )


def export_sequence_from_fixture(
    input_case_dir: str | Path,
    output_dir: str | Path,
) -> ExportResult:
    """Load a synthetic fixture case, export sequence files, and audit them."""

    bundle = load_exporter_input_fixture(input_case_dir)
    result = write_sequence_outputs(bundle, output_dir)
    compare_export_result_to_contract(result, bundle.expected_output_contract)
    return result


def load_exporter_input_fixture(input_case_dir: str | Path) -> ExporterInputBundle:
    case_dir = Path(input_case_dir)
    safe_episodes = _load_jsonl(case_dir / SAFE_EPISODES_FILE, "safe_episodes")
    candidate_scores = _load_jsonl(case_dir / CANDIDATE_SCORES_FILE, "candidate_scores")
    diagnostic_summary = _load_json(
        case_dir / DIAGNOSTIC_SUMMARY_FILE,
        "diagnostic_summary",
    )
    labels_source = _load_jsonl(case_dir / LABELS_SOURCE_FILE, "labels_source")
    synthetic_metadata = _load_json(
        case_dir / SYNTHETIC_METADATA_FILE,
        "synthetic_metadata",
    )
    split_metadata = _load_json(case_dir / SPLIT_METADATA_FILE, "split_metadata")

    _validate_exporter_inputs(
        safe_episodes=safe_episodes,
        candidate_scores=candidate_scores,
        labels_source=labels_source,
        synthetic_metadata=synthetic_metadata,
        split_metadata=split_metadata,
    )
    expected_output_contract = load_expected_output_contract(case_dir)

    return ExporterInputBundle(
        safe_episodes=safe_episodes,
        candidate_scores=candidate_scores,
        diagnostic_summary=diagnostic_summary,
        labels_source=labels_source,
        synthetic_metadata=synthetic_metadata,
        split_metadata=split_metadata,
        expected_output_contract=expected_output_contract,
    )


def load_expected_output_contract(input_case_dir: str | Path) -> dict[str, Any]:
    path = Path(input_case_dir) / EXPECTED_OUTPUT_CONTRACT_FILE
    if not path.exists():
        _fail("missing_contract", "expected_output_contract")
    return _load_json(path, "expected_output_contract")


def load_expected_failure_contract(input_case_dir: str | Path) -> dict[str, Any]:
    path = Path(input_case_dir) / EXPECTED_FAILURE_CONTRACT_FILE
    if not path.exists():
        _fail("missing_contract", "expected_failure_contract")
    return _load_json(path, "expected_failure_contract")


def write_sequence_outputs(
    bundle: ExporterInputBundle,
    output_dir: str | Path,
) -> ExportResult:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    features = _build_feature_rows(bundle)
    labels = _build_label_rows(bundle)
    manifest = _build_manifest(bundle, features, labels)

    features_path = output_path / FEATURES_OUTPUT_FILE
    labels_path = output_path / LABELS_OUTPUT_FILE
    manifest_path = output_path / MANIFEST_OUTPUT_FILE

    _write_jsonl(features_path, features)
    _write_jsonl(labels_path, labels)
    _write_json(manifest_path, manifest)

    audit_result = audit_sequence_dataset(features_path, labels_path, manifest_path)
    if audit_result.audit_status != "pass":
        raise AssertionError(
            "sequence_export_audit_failed: "
            f"status={audit_result.audit_status};"
            f"reason_codes={','.join(audit_result.reason_codes)}"
        )

    return _build_export_result(
        bundle=bundle,
        features_path=features_path,
        labels_path=labels_path,
        manifest_path=manifest_path,
        feature_row_count=len(features),
        label_row_count=len(labels),
        audit_result=audit_result,
    )


def compare_export_result_to_contract(
    result: ExportResult,
    contract: dict[str, Any],
) -> None:
    mismatches: list[str] = []

    checks = {
        "expected_feature_row_count": result.feature_row_count,
        "expected_label_row_count": result.label_row_count,
        "expected_participant_count": result.participant_count,
        "expected_session_count": result.session_count,
        "expected_task_count": result.task_count,
        "expected_episode_count": result.episode_count,
        "expected_audit_status": result.audit_status,
        "expected_manifest_content_suppressed": result.content_suppressed,
        "expected_no_raw_rows": result.no_raw_rows,
        "expected_manifest_synthetic_only": result.synthetic_only,
    }

    for expected_key, actual_value in checks.items():
        if expected_key in contract and contract[expected_key] != actual_value:
            mismatches.append(expected_key)

    expected_versions = contract.get("expected_schema_versions")
    if isinstance(expected_versions, dict):
        version_checks = {
            "feature": FEATURE_SCHEMA_VERSION,
            "label": LABEL_SCHEMA_VERSION,
            "manifest": MANIFEST_SCHEMA_VERSION,
        }
        for key, expected_value in expected_versions.items():
            if version_checks.get(key) != expected_value:
                mismatches.append(f"expected_schema_versions.{key}")

    expected_absent_codes = contract.get("expected_absent_reason_codes", [])
    if isinstance(expected_absent_codes, list):
        for reason_code in expected_absent_codes:
            if isinstance(reason_code, str) and reason_code in result.audit_reason_codes:
                mismatches.append("expected_absent_reason_codes")

    if mismatches:
        safe_summary = {
            "mismatches": sorted(set(mismatches)),
            "export_status": result.export_status,
            "audit_status": result.audit_status,
            "feature_row_count": result.feature_row_count,
            "label_row_count": result.label_row_count,
        }
        raise AssertionError(f"export_expected_contract_mismatch: {safe_summary}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export a synthetic learner-state sequence fixture to separated "
            "features, labels, and manifest files."
        )
    )
    parser.add_argument(
        "--input-fixture",
        required=True,
        help="Synthetic exporter fixture case directory.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for generated sequence outputs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a safe JSON summary instead of a human summary.",
    )
    args = parser.parse_args(argv)
    return _run_cli(args)


def _run_cli(args: argparse.Namespace) -> int:
    input_fixture = Path(args.input_fixture)
    output_dir = Path(args.output_dir)
    json_output = bool(args.json)

    path_failure = _validate_cli_paths(input_fixture, output_dir)
    if path_failure is not None:
        _emit_cli_summary(path_failure.to_safe_dict(), json_output)
        return 1

    try:
        result = export_sequence_from_fixture(input_fixture, output_dir)
    except ExporterFailure as exc:
        summary = exc.summary.to_safe_dict()
        _emit_cli_summary(summary, json_output)
        return _failure_exit_code(exc.summary)
    except AssertionError as exc:
        summary = _assertion_failure_summary(exc).to_safe_dict()
        _emit_cli_summary(summary, json_output)
        reason_codes = summary.get("reason_codes", [])
        if isinstance(reason_codes, list) and "contract_mismatch" in reason_codes:
            return 3
        return 1

    _emit_cli_summary(_success_cli_summary(result), json_output)
    return 0


def _validate_cli_paths(
    input_fixture: Path,
    output_dir: Path,
) -> ExportFailureSummary | None:
    if _has_unsafe_cli_path_part(input_fixture):
        return _cli_failure_summary("unsafe_input_path", "path_safety")
    if _has_unsafe_cli_path_part(output_dir):
        return _cli_failure_summary("unsafe_output_path", "path_safety")
    if _is_under_exporter_fixture_root(output_dir):
        return _cli_failure_summary("unsafe_output_path", "path_safety")
    for file_name in sorted(OUTPUT_FILE_NAMES):
        if (output_dir / file_name).exists():
            return _cli_failure_summary("existing_output_files", "output_directory")
    return None


def _success_cli_summary(result: ExportResult) -> dict[str, Any]:
    summary = result.to_safe_dict()
    summary["mode"] = "export"
    summary["reason_codes"] = result.audit_reason_codes
    summary["path_safety_checked"] = True
    return summary


def _assertion_failure_summary(exc: AssertionError) -> ExportFailureSummary:
    message = str(exc)
    if message.startswith("export_expected_contract_mismatch"):
        return _cli_failure_summary(
            "contract_mismatch",
            "expected_output_contract",
            stage="contract_check",
        )
    if message.startswith("sequence_export_audit_failed"):
        return _cli_failure_summary(
            "audit_failed_after_export",
            "output_audit",
            stage="audit",
        )
    return _cli_failure_summary("export_failed", "export")


def _cli_failure_summary(
    reason_code: str,
    failure_category: str,
    *,
    stage: str = "cli",
) -> ExportFailureSummary:
    return ExportFailureSummary(
        export_status="fail",
        reason_codes=[reason_code],
        failure_categories=[failure_category],
        stage=stage,
    )


def _failure_exit_code(summary: ExportFailureSummary) -> int:
    usage_like_codes = {
        "missing_input_file",
        "malformed_input",
    }
    if any(reason_code in usage_like_codes for reason_code in summary.reason_codes):
        return 2
    return 1


def _emit_cli_summary(summary: dict[str, Any], json_output: bool) -> None:
    safe_summary = {"mode": "export", **summary}
    if json_output:
        sys.stdout.write(json.dumps(safe_summary, sort_keys=True))
        sys.stdout.write("\n")
        return
    for key in _human_summary_keys(safe_summary):
        sys.stdout.write(f"{key}={_format_summary_value(safe_summary.get(key))}\n")


def _human_summary_keys(summary: dict[str, Any]) -> list[str]:
    preferred = [
        "mode",
        "export_status",
        "feature_row_count",
        "label_row_count",
        "audit_status",
        "reason_codes",
        "content_suppressed",
        "no_raw_rows",
        "synthetic_only",
        "synthetic_only_checked",
        "path_safety_checked",
        "stage",
    ]
    return [key for key in preferred if key in summary]


def _format_summary_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ",".join(str(item) for item in value) if value else "none"
    if value is None:
        return "none"
    return str(value)


def _has_unsafe_cli_path_part(path: Path) -> bool:
    return bool(set(path.parts) & UNSAFE_CLI_PATH_PARTS)


def _is_under_exporter_fixture_root(output_dir: Path) -> bool:
    fixture_root = EXPORTER_FIXTURE_ROOT.resolve(strict=False)
    resolved_output = output_dir.resolve(strict=False)
    return resolved_output == fixture_root or fixture_root in resolved_output.parents


def _build_feature_rows(bundle: ExporterInputBundle) -> list[dict[str, Any]]:
    candidate_by_episode = {
        _episode_key(row): row for row in bundle.candidate_scores
    }
    labels_by_episode = {_episode_key(row): row for row in bundle.labels_source}
    split_by_participant = _split_by_participant(bundle.split_metadata)
    diagnostic_counts = bundle.diagnostic_summary.get("diagnostic_counts", {})
    if not isinstance(diagnostic_counts, dict):
        diagnostic_counts = {}

    seen_task_episode_counts: dict[tuple[str, str, str], int] = {}
    seen_family_counts: dict[tuple[str, str, str, str], int] = {}
    rows: list[dict[str, Any]] = []

    for episode in sorted(
        bundle.safe_episodes,
        key=lambda row: (
            str(row.get("synthetic_participant_id", "")),
            str(row.get("synthetic_session_id", "")),
            str(row.get("synthetic_task_id", "")),
            int(row.get("episode_order_index", 0)),
        ),
    ):
        _assert_no_forbidden_feature_keys(episode, "safe_episodes")
        key = _episode_key(episode)
        candidate = candidate_by_episode.get(key)
        if candidate is None:
            raise AssertionError("missing_candidate_scores_for_episode")
        _assert_no_forbidden_feature_keys(candidate, "candidate_scores")

        label = labels_by_episode.get(key)
        if label is None:
            raise AssertionError("missing_label_source_for_episode")

        participant_id = _required_str(episode, "synthetic_participant_id")
        session_id = _required_str(episode, "synthetic_session_id")
        task_id = _required_str(episode, "synthetic_task_id")
        top_family = candidate.get("top_ranked_candidate_family")
        top_family_str = top_family if isinstance(top_family, str) else "unknown"
        task_key = (participant_id, session_id, task_id)
        family_key = (*task_key, top_family_str)
        previous_task_episode_count = seen_task_episode_counts.get(task_key, 0)
        previous_count = seen_family_counts.get(family_key, 0)

        row = {
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "synthetic_participant_id": participant_id,
            "synthetic_session_id": session_id,
            "synthetic_task_id": task_id,
            "micro_episode_id": _required_str(episode, "micro_episode_id"),
            "episode_order_index": _required_int(episode, "episode_order_index"),
            "split_id": split_by_participant.get(participant_id, "train"),
            "boundary": episode.get("boundary", {}),
            "safe_episode_features": episode.get("safe_episode_features", {}),
            "candidate_family_score_summary": candidate.get(
                "candidate_family_score_summary",
                {},
            ),
            "top_ranked_candidate_family": top_family_str,
            "top_k_candidate_family_summary": candidate.get(
                "top_k_candidate_family_summary",
                [],
            ),
            "blocked_candidate_count": _required_int(
                candidate,
                "blocked_candidate_count",
            ),
            "diagnostic_count_features": diagnostic_counts,
            "past_only_window_features": {
                "previous_episode_count": previous_task_episode_count,
                "previous_same_top_family_count": previous_count,
            },
        }
        rows.append(row)
        seen_task_episode_counts[task_key] = previous_task_episode_count + 1
        seen_family_counts[family_key] = previous_count + 1

    return rows


def _build_label_rows(bundle: ExporterInputBundle) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for label in sorted(
        bundle.labels_source,
        key=lambda row: (
            str(row.get("synthetic_participant_id", "")),
            str(row.get("synthetic_session_id", "")),
            str(row.get("synthetic_task_id", "")),
            int(row.get("episode_order_index", 0)),
        ),
    ):
        rows.append(
            {
                "label_schema_version": LABEL_SCHEMA_VERSION,
                "synthetic_participant_id": _required_str(
                    label,
                    "synthetic_participant_id",
                ),
                "synthetic_session_id": _required_str(label, "synthetic_session_id"),
                "synthetic_task_id": _required_str(label, "synthetic_task_id"),
                "micro_episode_id": _required_str(label, "micro_episode_id"),
                "episode_order_index": _required_int(label, "episode_order_index"),
                "expected_action_family": _required_str(
                    label,
                    "evaluation_label_family",
                ),
                "expected_action_type": _required_str(label, "evaluation_label_type"),
                "label_source": _required_str(label, "label_source"),
                "evaluation_only": label.get("evaluation_only") is True,
            }
        )
    return rows


def _build_manifest(
    bundle: ExporterInputBundle,
    features: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, Any]:
    participant_ids = {
        _required_str(row, "synthetic_participant_id") for row in features
    }
    session_ids = {_required_str(row, "synthetic_session_id") for row in features}
    task_ids = {_required_str(row, "synthetic_task_id") for row in features}
    split_counts = bundle.split_metadata.get("split_counts", {})
    if not isinstance(split_counts, dict):
        split_counts = {}

    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "dataset_schema_version": "learner_state_sequence_dataset_v0.1",
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "synthetic_only": True,
        "content_suppressed": True,
        "feature_row_count": len(features),
        "label_row_count": len(labels),
        "synthetic_participant_count": len(participant_ids),
        "synthetic_session_count": len(session_ids),
        "synthetic_task_count": len(task_ids),
        "episode_count": len(features),
        "input_source_categories": [
            "safe_episodes",
            "candidate_scores",
            "diagnostic_summary",
            "labels_source",
            "synthetic_metadata",
            "split_metadata",
        ],
        "output_file_roles": {
            "features": FEATURES_OUTPUT_FILE,
            "labels": LABELS_OUTPUT_FILE,
            "manifest": MANIFEST_OUTPUT_FILE,
        },
        "join_key_fields": [
            "synthetic_participant_id",
            "synthetic_session_id",
            "synthetic_task_id",
            "micro_episode_id",
            "episode_order_index",
        ],
        "split_counts": split_counts,
        "split_membership": _split_membership(bundle.split_metadata),
        "export_status": "pass",
        "audit_status": "planned",
        "no_raw_rows": True,
        "source_text_suppressed": True,
        "candidate_rows_included": False,
        "label_contents_included": False,
    }


def _build_export_result(
    *,
    bundle: ExporterInputBundle,
    features_path: Path,
    labels_path: Path,
    manifest_path: Path,
    feature_row_count: int,
    label_row_count: int,
    audit_result: AuditResult,
) -> ExportResult:
    metadata = bundle.synthetic_metadata
    participants = metadata.get("participants", [])
    sessions = metadata.get("sessions", [])
    tasks = metadata.get("tasks", [])
    return ExportResult(
        export_status="pass",
        features_path=features_path,
        labels_path=labels_path,
        manifest_path=manifest_path,
        feature_row_count=feature_row_count,
        label_row_count=label_row_count,
        participant_count=len(participants) if isinstance(participants, list) else 0,
        session_count=len(sessions) if isinstance(sessions, list) else 0,
        task_count=len(tasks) if isinstance(tasks, list) else 0,
        episode_count=feature_row_count,
        audit_status=audit_result.audit_status,
        audit_reason_codes=audit_result.reason_codes,
    )


def _validate_exporter_inputs(
    *,
    safe_episodes: list[dict[str, Any]],
    candidate_scores: list[dict[str, Any]],
    labels_source: list[dict[str, Any]],
    synthetic_metadata: dict[str, Any],
    split_metadata: dict[str, Any],
) -> None:
    if not safe_episodes:
        _fail("empty_input", "input_cardinality")
    if not candidate_scores:
        _fail("empty_input", "input_cardinality")
    if not labels_source:
        _fail("empty_input", "input_cardinality")
    if synthetic_metadata.get("synthetic_only") is not True:
        _fail("exporter_forbidden_field", "synthetic_metadata")
    if synthetic_metadata.get("content_suppressed") is not True:
        _fail("exporter_forbidden_field", "synthetic_metadata")
    if split_metadata.get("label_derived") is True:
        _fail("exporter_split_leakage", "split_metadata")
    if split_metadata.get("outcome_derived") is True:
        _fail("exporter_split_leakage", "split_metadata")
    _assert_schema_version(
        synthetic_metadata,
        "metadata_schema_version",
        SYNTHETIC_METADATA_SCHEMA_VERSION,
    )
    _assert_schema_version(
        split_metadata,
        "split_schema_version",
        SPLIT_METADATA_SCHEMA_VERSION,
    )
    for row in safe_episodes:
        _assert_schema_version(
            row,
            "input_schema_version",
            SAFE_EPISODE_INPUT_SCHEMA_VERSION,
        )
        _assert_no_forbidden_feature_keys(row, "safe_episodes")
    for row in candidate_scores:
        _assert_schema_version(
            row,
            "candidate_score_schema_version",
            CANDIDATE_SCORE_SCHEMA_VERSION,
        )
        _assert_no_forbidden_feature_keys(row, "candidate_scores")
    for row in labels_source:
        _assert_schema_version(
            row,
            "label_schema_version",
            LABEL_SOURCE_SCHEMA_VERSION,
        )


def _load_jsonl(path: Path, file_role: str) -> list[dict[str, Any]]:
    if not path.exists():
        _fail("missing_input_file", "input_file_presence")
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    _fail("malformed_input", "jsonl_parse")
                rows.append(row)
    except json.JSONDecodeError as exc:
        raise ExporterFailure("malformed_input", "jsonl_parse") from exc
    if not rows:
        _fail("empty_input", "input_cardinality")
    return rows


def _load_json(path: Path, file_role: str) -> dict[str, Any]:
    if not path.exists():
        _fail("missing_input_file", "input_file_presence")
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ExporterFailure("malformed_input", "json_parse") from exc
    if not isinstance(data, dict):
        _fail("malformed_input", "json_parse")
    return data


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _episode_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _required_str(row, "synthetic_participant_id"),
        _required_str(row, "synthetic_session_id"),
        _required_str(row, "synthetic_task_id"),
        _required_str(row, "micro_episode_id"),
    )


def _required_str(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise AssertionError(f"missing_or_invalid_{key}")
    return value


def _required_int(row: dict[str, Any], key: str) -> int:
    value = row.get(key)
    if not isinstance(value, int):
        raise AssertionError(f"missing_or_invalid_{key}")
    return value


def _split_by_participant(split_metadata: dict[str, Any]) -> dict[str, str]:
    assignments = split_metadata.get("split_assignments", [])
    if not isinstance(assignments, list):
        return {}
    split_by_participant: dict[str, str] = {}
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        participant_id = assignment.get("synthetic_participant_id")
        split_id = assignment.get("split_id")
        if isinstance(participant_id, str) and isinstance(split_id, str):
            split_by_participant[participant_id] = split_id
    return split_by_participant


def _split_membership(split_metadata: dict[str, Any]) -> dict[str, list[str]]:
    membership: dict[str, list[str]] = {}
    for participant_id, split_id in _split_by_participant(split_metadata).items():
        membership.setdefault(split_id, []).append(participant_id)
    return {key: sorted(value) for key, value in sorted(membership.items())}


def _assert_no_forbidden_feature_keys(row: dict[str, Any], file_role: str) -> None:
    keys = set(_nested_keys(row))
    forbidden = keys & FORBIDDEN_FEATURE_KEYS
    if forbidden:
        label_keys = {
            "expected_action",
            "expected_action_family",
            "expected_action_type",
            "label_source",
        }
        category = (
            "label_in_feature_input"
            if forbidden & label_keys
            else f"{file_role}_forbidden_field"
        )
        _fail("exporter_forbidden_field", category)


def _assert_schema_version(
    row: dict[str, Any],
    key: str,
    expected_version: str,
) -> None:
    if row.get(key) != expected_version:
        _fail("unknown_input_schema_version", "schema_version")


def _fail(
    reason_code: str,
    failure_category: str,
    stage: str = "input_validation",
) -> None:
    raise ExporterFailure(reason_code, failure_category, stage)


def _nested_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                keys.append(key)
            keys.extend(_nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_nested_keys(child))
    return keys


if __name__ == "__main__":
    raise SystemExit(main())
