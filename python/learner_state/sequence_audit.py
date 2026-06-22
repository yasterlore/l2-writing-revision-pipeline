"""No-oracle audit for synthetic learner-state sequence fixtures.

This module intentionally returns safe, count-only results. It does not keep
raw rows, raw text, label bodies, or candidate score rows in ``AuditResult``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

AUDIT_SCHEMA_VERSION = "learner_state_sequence_audit_result_v0_1"

FEATURE_SCHEMA_FIELD = "feature_schema_version"
LABEL_SCHEMA_FIELD = "label_schema_version"
MANIFEST_SCHEMA_FIELD = "manifest_schema_version"

FORBIDDEN_FIELD_NAMES = {
    "final_text",
    "observed_after_text",
    "gold_label",
    "teacher_correction",
    "human_correction",
    "post_hoc_annotation",
    "raw_text",
    "final_essay_outcome",
}

LABEL_IN_FEATURE_NAMES = {
    "expected_action",
    "expected_action_family",
    "expected_action_type",
    "label_source",
}

FEATURE_IN_LABEL_NAMES = {
    "candidate_family_score_summary",
    "top_ranked_candidate_family",
    "top_k_candidate_family_summary",
    "blocked_candidate_count",
    "diagnostic_count_features",
    "past_only_window_features",
    "safe_episode_features",
}

FUTURE_LEAKAGE_NAMES = {
    "next_episode_action",
    "future_action_summary",
    "future_edit_count",
    "future_episode",
    "future_edit",
    "final_essay_outcome",
}

MANIFEST_BODY_LEAKAGE_NAMES = {
    "row_dump",
    "row_body",
    "rows",
    "feature_rows",
    "label_body",
    "label_rows",
    "candidate_score_rows",
    "raw_body",
    "raw_rows",
}

UNSAFE_PATH_SEGMENTS = {
    "real_data",
    "private_data",
    "participant_data",
    "manual_outputs",
}

UNSAFE_ABSOLUTE_PREFIXES = (
    "/Users/",
    "/home/",
)

REAL_PARTICIPANT_ID = "real_participant_id"


@dataclass(frozen=True)
class FailedCheck:
    category: str
    reason_code: str
    file_role: str
    check: str

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "reason_code": self.reason_code,
            "file_role": self.file_role,
            "check": self.check,
        }


@dataclass(frozen=True)
class AuditResult:
    audit_schema_version: str = AUDIT_SCHEMA_VERSION
    audit_status: str = "pass"
    violation_count: int = 0
    violation_categories: dict[str, int] = field(default_factory=dict)
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, str]] = field(default_factory=list)
    checked_files_count: int = 0
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    path_safety_checked: bool = True

    @classmethod
    def from_failed_checks(
        cls,
        failed_checks: Iterable[FailedCheck],
        *,
        checked_files_count: int,
    ) -> "AuditResult":
        checks = list(failed_checks)
        categories: dict[str, int] = {}
        for check in checks:
            categories[check.category] = categories.get(check.category, 0) + 1
        reason_codes = sorted({check.reason_code for check in checks})
        return cls(
            audit_status="fail" if checks else "pass",
            violation_count=len(checks),
            violation_categories=dict(sorted(categories.items())),
            reason_codes=reason_codes,
            failed_checks=[check.to_dict() for check in checks],
            checked_files_count=checked_files_count,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_schema_version": self.audit_schema_version,
            "audit_status": self.audit_status,
            "violation_count": self.violation_count,
            "violation_categories": self.violation_categories,
            "reason_codes": self.reason_codes,
            "failed_checks": self.failed_checks,
            "checked_files_count": self.checked_files_count,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_safety_checked": self.path_safety_checked,
        }


def audit_sequence_dataset(
    features_path: str | Path,
    labels_path: str | Path,
    manifest_path: str | Path,
) -> AuditResult:
    """Audit a feature/label/manifest trio and return safe metadata only."""

    failed_checks: list[FailedCheck] = []
    checked_files_count = 0

    features, ok = _load_jsonl(Path(features_path), "features", failed_checks)
    checked_files_count += 1 if ok else 0
    labels, ok = _load_jsonl(Path(labels_path), "labels", failed_checks)
    checked_files_count += 1 if ok else 0
    manifest, ok = _load_json(Path(manifest_path), "manifest", failed_checks)
    checked_files_count += 1 if ok else 0

    if features is not None:
        _audit_feature_rows(features, failed_checks)
    if labels is not None:
        _audit_label_rows(labels, failed_checks)
    if manifest is not None:
        _audit_manifest(manifest, failed_checks)
        _audit_path_safety(manifest, failed_checks)
    if features is not None:
        _audit_split_leakage(features, manifest, failed_checks)

    return AuditResult.from_failed_checks(
        failed_checks,
        checked_files_count=checked_files_count,
    )


def audit_fixture_case(case_dir: str | Path) -> AuditResult:
    case_path = Path(case_dir)
    return audit_sequence_dataset(
        case_path / "features.jsonl",
        case_path / "labels.jsonl",
        case_path / "manifest.json",
    )


def load_expected_audit_result(case_dir: str | Path) -> dict[str, Any]:
    expected_path = Path(case_dir) / "expected_audit_result.json"
    with expected_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError("expected_audit_result_not_object")
    return data


def compare_audit_result_to_expected(
    actual: AuditResult,
    expected: dict[str, Any],
) -> None:
    """Raise AssertionError when a safe AuditResult mismatches expectation."""

    actual_dict = actual.to_dict()
    mismatches: list[str] = []

    expected_status = expected.get("audit_status")
    if actual.audit_status != expected_status:
        mismatches.append("audit_status")

    expected_code = expected.get("expected_failure_code")
    if expected_code and expected_code not in actual.reason_codes:
        mismatches.append("expected_failure_code")

    expected_category = expected.get("expected_violation_category")
    if expected_category and expected_category not in actual.violation_categories:
        mismatches.append("expected_violation_category")

    expected_min = expected.get("expected_violation_count_min")
    if isinstance(expected_min, int) and actual.violation_count < expected_min:
        mismatches.append("expected_violation_count_min")

    if actual.content_suppressed != expected.get("content_suppressed"):
        mismatches.append("content_suppressed")

    if actual.no_raw_rows != expected.get("no_raw_rows"):
        mismatches.append("no_raw_rows")

    if mismatches:
        safe_summary = {
            "mismatches": sorted(mismatches),
            "audit_status": actual.audit_status,
            "reason_codes": actual.reason_codes,
            "violation_categories": actual.violation_categories,
            "violation_count": actual.violation_count,
            "content_suppressed": actual_dict["content_suppressed"],
            "no_raw_rows": actual_dict["no_raw_rows"],
        }
        raise AssertionError(f"audit_expected_result_mismatch: {safe_summary}")


def _load_jsonl(
    path: Path,
    file_role: str,
    failed_checks: list[FailedCheck],
) -> tuple[list[dict[str, Any]] | None, bool]:
    if not path.exists():
        failed_checks.append(
            _failed("input", "missing_input", file_role, "file_presence")
        )
        return None, False

    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    failed_checks.append(
                        _failed("input", "malformed_input", file_role, "jsonl_parse")
                    )
                    return None, False
                if not isinstance(row, dict):
                    failed_checks.append(
                        _failed("input", "malformed_input", file_role, "jsonl_object")
                    )
                    return None, False
                rows.append(row)
                if line_number < 1:
                    raise AssertionError("unreachable")
    except OSError:
        failed_checks.append(
            _failed("input", "malformed_input", file_role, "file_read")
        )
        return None, False

    if not rows:
        failed_checks.append(_failed("input", "empty_input", file_role, "non_empty"))
        return rows, True
    return rows, True


def _load_json(
    path: Path,
    file_role: str,
    failed_checks: list[FailedCheck],
) -> tuple[dict[str, Any] | None, bool]:
    if not path.exists():
        failed_checks.append(
            _failed("input", "missing_input", file_role, "file_presence")
        )
        return None, False

    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        failed_checks.append(
            _failed("input", "malformed_input", file_role, "json_parse")
        )
        return None, False
    if not isinstance(data, dict):
        failed_checks.append(
            _failed("input", "malformed_input", file_role, "json_object")
        )
        return None, False
    return data, True


def _audit_feature_rows(
    rows: list[dict[str, Any]],
    failed_checks: list[FailedCheck],
) -> None:
    for row in rows:
        keys = set(_nested_keys(row))
        if FEATURE_SCHEMA_FIELD not in row:
            failed_checks.append(
                _failed(
                    "schema_version",
                    "missing_schema_version",
                    "features",
                    "feature_schema_version",
                )
            )
        if keys & FORBIDDEN_FIELD_NAMES:
            failed_checks.append(
                _failed("forbidden_field", "forbidden_field", "features", "field_name")
            )
        if keys & LABEL_IN_FEATURE_NAMES:
            failed_checks.append(
                _failed(
                    "label_feature_separation",
                    "label_in_feature",
                    "features",
                    "label_field",
                )
            )
        if keys & FUTURE_LEAKAGE_NAMES:
            failed_checks.append(
                _failed(
                    "future_leakage",
                    "future_leakage",
                    "features",
                    "future_field",
                )
            )
        if REAL_PARTICIPANT_ID in keys:
            failed_checks.append(
                _failed(
                    "join_key_safety",
                    "unsafe_join_key",
                    "features",
                    "real_participant_id",
                )
            )


def _audit_label_rows(
    rows: list[dict[str, Any]],
    failed_checks: list[FailedCheck],
) -> None:
    for row in rows:
        keys = set(_nested_keys(row))
        if LABEL_SCHEMA_FIELD not in row:
            failed_checks.append(
                _failed(
                    "schema_version",
                    "missing_schema_version",
                    "labels",
                    "label_schema_version",
                )
            )
        if keys & FEATURE_IN_LABEL_NAMES:
            failed_checks.append(
                _failed(
                    "label_feature_separation",
                    "feature_in_label",
                    "labels",
                    "feature_field",
                )
            )
        if REAL_PARTICIPANT_ID in keys:
            failed_checks.append(
                _failed(
                    "join_key_safety",
                    "unsafe_join_key",
                    "labels",
                    "real_participant_id",
                )
            )


def _audit_manifest(
    manifest: dict[str, Any],
    failed_checks: list[FailedCheck],
) -> None:
    keys = set(_nested_keys(manifest))
    if MANIFEST_SCHEMA_FIELD not in manifest:
        failed_checks.append(
            _failed(
                "schema_version",
                "missing_schema_version",
                "manifest",
                "manifest_schema_version",
            )
        )
    if keys & MANIFEST_BODY_LEAKAGE_NAMES:
        failed_checks.append(
            _failed(
                "manifest_leakage",
                "manifest_body_leakage",
                "manifest",
                "body_like_field",
            )
        )
    if manifest.get("content_suppressed") is not True:
        failed_checks.append(
            _failed(
                "manifest_leakage",
                "manifest_body_leakage",
                "manifest",
                "content_suppressed",
            )
        )
    if manifest.get("synthetic_only") is not True:
        failed_checks.append(
            _failed(
                "synthetic_only_path",
                "unsafe_path",
                "manifest",
                "synthetic_only",
            )
        )
    join_key_fields = manifest.get("join_key_fields")
    if isinstance(join_key_fields, list) and REAL_PARTICIPANT_ID in join_key_fields:
        failed_checks.append(
            _failed(
                "join_key_safety",
                "unsafe_join_key",
                "manifest",
                "join_key_fields",
            )
        )


def _audit_path_safety(
    manifest: dict[str, Any],
    failed_checks: list[FailedCheck],
) -> None:
    for value in _nested_string_values(manifest):
        if _is_unsafe_path_like(value):
            failed_checks.append(
                _failed(
                    "synthetic_only_path",
                    "unsafe_path",
                    "manifest",
                    "path_safety",
                )
            )
            return


def _audit_split_leakage(
    rows: list[dict[str, Any]],
    manifest: dict[str, Any] | None,
    failed_checks: list[FailedCheck],
) -> None:
    participant_splits: dict[str, set[str]] = {}
    for row in rows:
        participant_id = row.get("synthetic_participant_id")
        split_id = row.get("split_id")
        if isinstance(participant_id, str) and isinstance(split_id, str):
            participant_splits.setdefault(participant_id, set()).add(split_id)
    for splits in participant_splits.values():
        if _has_split_overlap(splits):
            failed_checks.append(
                _failed(
                    "split_leakage",
                    "split_leakage",
                    "features",
                    "participant_split_overlap",
                )
            )
            return

    if manifest is None:
        return
    split_membership = manifest.get("split_membership")
    if isinstance(split_membership, dict):
        seen: dict[str, set[str]] = {}
        for split_name, members in split_membership.items():
            if not isinstance(split_name, str) or not isinstance(members, list):
                continue
            for member in members:
                if isinstance(member, str):
                    seen.setdefault(member, set()).add(split_name)
        for splits in seen.values():
            if _has_split_overlap(splits):
                failed_checks.append(
                    _failed(
                        "split_leakage",
                        "split_leakage",
                        "manifest",
                        "split_membership_overlap",
                    )
                )
                return


def _has_split_overlap(splits: set[str]) -> bool:
    relevant = {"train", "validation", "val", "test"}
    return len(splits & relevant) > 1


def _nested_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                yield key
            yield from _nested_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nested_keys(child)


def _nested_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _nested_string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nested_string_values(child)


def _is_unsafe_path_like(value: str) -> bool:
    normalized = value.replace("\\", "/")
    segments = {segment for segment in normalized.split("/") if segment}
    if segments & UNSAFE_PATH_SEGMENTS:
        return True
    return normalized.startswith(UNSAFE_ABSOLUTE_PREFIXES)


def _failed(
    category: str,
    reason_code: str,
    file_role: str,
    check: str,
) -> FailedCheck:
    return FailedCheck(
        category=category,
        reason_code=reason_code,
        file_role=file_role,
        check=check,
    )

