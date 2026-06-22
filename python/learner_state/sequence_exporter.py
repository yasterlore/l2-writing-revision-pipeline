"""Minimal synthetic learner-state sequence exporter.

The exporter reads synthetic-only upstream fixture inputs and writes separated
feature, label, and manifest outputs. It keeps results safe/count-only and runs
the learner-state sequence audit before returning success.
"""

from __future__ import annotations

import json
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

FEATURES_OUTPUT_FILE = "features.jsonl"
LABELS_OUTPUT_FILE = "labels.jsonl"
MANIFEST_OUTPUT_FILE = "manifest.json"

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
    expected_output_contract = load_expected_output_contract(case_dir)

    _validate_exporter_inputs(
        safe_episodes=safe_episodes,
        candidate_scores=candidate_scores,
        labels_source=labels_source,
        synthetic_metadata=synthetic_metadata,
        split_metadata=split_metadata,
    )

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
    return _load_json(
        Path(input_case_dir) / EXPECTED_OUTPUT_CONTRACT_FILE,
        "expected_output_contract",
    )


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


def _build_feature_rows(bundle: ExporterInputBundle) -> list[dict[str, Any]]:
    candidate_by_episode = {
        _episode_key(row): row for row in bundle.candidate_scores
    }
    labels_by_episode = {_episode_key(row): row for row in bundle.labels_source}
    split_by_participant = _split_by_participant(bundle.split_metadata)
    diagnostic_counts = bundle.diagnostic_summary.get("diagnostic_counts", {})
    if not isinstance(diagnostic_counts, dict):
        diagnostic_counts = {}

    seen_family_counts: dict[str, int] = {}
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
        top_family = candidate.get("top_ranked_candidate_family")
        top_family_str = top_family if isinstance(top_family, str) else "unknown"
        previous_count = seen_family_counts.get(top_family_str, 0)

        row = {
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "synthetic_participant_id": participant_id,
            "synthetic_session_id": _required_str(episode, "synthetic_session_id"),
            "synthetic_task_id": _required_str(episode, "synthetic_task_id"),
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
                "previous_episode_count": len(rows),
                "previous_same_top_family_count": previous_count,
            },
        }
        rows.append(row)
        seen_family_counts[top_family_str] = previous_count + 1

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
        raise AssertionError("empty_safe_episodes")
    if not candidate_scores:
        raise AssertionError("empty_candidate_scores")
    if not labels_source:
        raise AssertionError("empty_labels_source")
    if synthetic_metadata.get("synthetic_only") is not True:
        raise AssertionError("synthetic_metadata_not_synthetic_only")
    if synthetic_metadata.get("content_suppressed") is not True:
        raise AssertionError("synthetic_metadata_not_content_suppressed")
    if split_metadata.get("label_derived") is True:
        raise AssertionError("split_metadata_label_derived")
    if split_metadata.get("outcome_derived") is True:
        raise AssertionError("split_metadata_outcome_derived")
    for row in safe_episodes:
        _assert_no_forbidden_feature_keys(row, "safe_episodes")
    for row in candidate_scores:
        _assert_no_forbidden_feature_keys(row, "candidate_scores")


def _load_jsonl(path: Path, file_role: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise AssertionError(f"missing_{file_role}")
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise AssertionError(f"malformed_{file_role}")
                rows.append(row)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"malformed_{file_role}") from exc
    if not rows:
        raise AssertionError(f"empty_{file_role}")
    return rows


def _load_json(path: Path, file_role: str) -> dict[str, Any]:
    if not path.exists():
        raise AssertionError(f"missing_{file_role}")
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"malformed_{file_role}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"malformed_{file_role}")
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
        safe_names = ",".join(sorted(forbidden))
        raise AssertionError(f"forbidden_feature_key:{file_role}:{safe_names}")


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
