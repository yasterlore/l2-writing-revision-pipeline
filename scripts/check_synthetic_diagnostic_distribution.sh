#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/check_synthetic_diagnostic_distribution.sh [summary.csv]" >&2
  echo "Checks count-only synthetic diagnostic summary wiring. This is not performance evaluation." >&2
}

if [ "$#" -gt 1 ]; then
  usage
  exit 2
fi

summary_csv=${1:-tmp/synthetic_e2e_summary/summary.csv}
expected_summary_csv="tmp/synthetic_e2e_summary/summary.csv"
summary_manifest="tmp/synthetic_e2e_summary/summary.manifest.json"

case "$summary_csv" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "Refusing private-looking summary path: $summary_csv" >&2
    exit 2
    ;;
  *synthetic_e2e_config_summary* )
    echo "synthetic_diagnostic_distribution_check: fail" >&2
    echo "failure_kind=precondition" >&2
    echo "reason=config_enabled_summary_not_supported" >&2
    echo "summary_csv=$summary_csv" >&2
    echo "expected_summary_csv=$expected_summary_csv" >&2
    echo "content_suppressed=true" >&2
    exit 2
    ;;
esac

if [ ! -f "$summary_csv" ]; then
  echo "synthetic_diagnostic_distribution_check: fail" >&2
  echo "failure_kind=precondition" >&2
  echo "reason=missing_summary_csv" >&2
  echo "summary_csv=$summary_csv" >&2
  echo "expected_summary_csv=$expected_summary_csv" >&2
  echo "next_step=scripts/run_synthetic_e2e_summary.sh" >&2
  echo "content_suppressed=true" >&2
  usage
  exit 2
fi

if [ ! -s "$summary_csv" ]; then
  echo "synthetic_diagnostic_distribution_check: fail" >&2
  echo "failure_kind=precondition" >&2
  echo "reason=empty_summary_csv" >&2
  echo "summary_csv=$summary_csv" >&2
  echo "next_step=scripts/run_synthetic_e2e_summary.sh" >&2
  echo "content_suppressed=true" >&2
  exit 2
fi

python3 - "$summary_csv" "$summary_manifest" "$expected_summary_csv" <<'PY'
import csv
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
marker_path = Path(sys.argv[2])
expected_summary_path = sys.argv[3]

forbidden_marker_keys = {
    "raw_summary_body",
    "diagnostic_summary_body",
    "jsonl_body",
    "candidate_score_rows",
    "raw_text",
    "expected_action_details",
    "config_body",
    "final_text",
    "observed_after_text",
    "gold_label",
    "performance_metrics",
    "f1",
    "accuracy",
    "calibration",
}


def fail_precondition(reason, **details):
    print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
    print("failure_kind=precondition", file=sys.stderr)
    print(f"reason={reason}", file=sys.stderr)
    for key, value in details.items():
        print(f"{key}={value}", file=sys.stderr)
    print("content_suppressed=true", file=sys.stderr)
    sys.exit(2)

required_columns = [
    "case_name",
    "pipeline_status",
    "diagnostic_summary_status",
    "diagnostic_summary_path",
    "diagnostic_total_constraints",
    "diagnostic_descriptive_constraint_count",
    "diagnostic_blocking_constraint_count",
    "diagnostic_safety_constraint_count",
    "diagnostic_local_pattern_constraint_count",
    "diagnostic_linguistic_placeholder_constraint_count",
    "diagnostic_non_leaky_linguistic_constraint_count",
]

numeric_columns = [
    "diagnostic_total_constraints",
    "diagnostic_descriptive_constraint_count",
    "diagnostic_blocking_constraint_count",
    "diagnostic_safety_constraint_count",
    "diagnostic_local_pattern_constraint_count",
    "diagnostic_linguistic_placeholder_constraint_count",
    "diagnostic_non_leaky_linguistic_constraint_count",
]

with summary_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames or []
    if not fieldnames:
        fail_precondition(
            "missing_header",
            summary_csv=summary_path,
            next_step="scripts/run_synthetic_e2e_summary.sh",
        )
    missing_columns = [name for name in required_columns if name not in fieldnames]
    if missing_columns:
        fail_precondition(
            "malformed_header",
            summary_csv=summary_path,
            missing_required_columns_count=len(missing_columns),
        )
    rows = list(reader)

if not rows:
    fail_precondition(
        "no_cases",
        summary_csv=summary_path,
        case_rows=0,
        next_step="scripts/run_synthetic_e2e_summary.sh",
    )

if not marker_path.is_file():
    fail_precondition(
        "missing_summary_manifest",
        summary_csv=summary_path,
        summary_manifest=marker_path,
        next_step="scripts/run_synthetic_e2e_summary.sh",
    )

try:
    with marker_path.open("r", encoding="utf-8") as handle:
        marker = json.load(handle)
except json.JSONDecodeError:
    fail_precondition(
        "malformed_summary_manifest_json",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

if not isinstance(marker, dict):
    fail_precondition(
        "invalid_summary_manifest_shape",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

forbidden_present = sorted(forbidden_marker_keys.intersection(marker))
if forbidden_present:
    fail_precondition(
        "forbidden_summary_manifest_key",
        summary_csv=summary_path,
        summary_manifest=marker_path,
        forbidden_keys_count=len(forbidden_present),
        first_forbidden_key=forbidden_present[0],
    )

if marker.get("content_suppressed") is not True:
    fail_precondition(
        "summary_manifest_content_suppressed_not_true",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

if marker.get("no_config_summary") is not True:
    fail_precondition(
        "summary_manifest_no_config_summary_not_true",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

case_count = marker.get("case_count")
if not isinstance(case_count, int) or isinstance(case_count, bool) or case_count <= 0:
    fail_precondition(
        "summary_manifest_invalid_case_count",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

diagnostic_summary_count = marker.get("diagnostic_summary_count")
if (
    not isinstance(diagnostic_summary_count, int)
    or isinstance(diagnostic_summary_count, bool)
    or diagnostic_summary_count < 0
):
    fail_precondition(
        "summary_manifest_invalid_diagnostic_summary_count",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

if marker.get("summary_path") != expected_summary_path:
    fail_precondition(
        "summary_manifest_unexpected_summary_path",
        summary_csv=summary_path,
        summary_manifest=marker_path,
        expected_summary_csv=expected_summary_path,
    )

if marker.get("generator_script") != "scripts/run_synthetic_e2e_summary.sh":
    fail_precondition(
        "summary_manifest_unexpected_generator_script",
        summary_csv=summary_path,
        summary_manifest=marker_path,
    )

if case_count != len(rows):
    fail_precondition(
        "summary_manifest_case_count_mismatch",
        summary_csv=summary_path,
        summary_manifest=marker_path,
        marker_case_count=case_count,
        summary_data_rows=len(rows),
    )

ok_rows = []
numeric_totals = {name: 0 for name in numeric_columns}

for index, row in enumerate(rows, start=1):
    case_name = row.get("case_name", "")
    status = row.get("diagnostic_summary_status", "")
    if not status:
        print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
        print("failure_kind=distribution", file=sys.stderr)
        print(f"reason=missing_diagnostic_summary_status", file=sys.stderr)
        print(f"row_number={index}", file=sys.stderr)
        print("content_suppressed=true", file=sys.stderr)
        sys.exit(1)

    for column in numeric_columns:
        raw_value = row.get(column, "")
        if raw_value == "":
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print(f"reason=empty_count_field", file=sys.stderr)
            print(f"field={column}", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)
        try:
            parsed = int(raw_value)
        except ValueError:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print(f"reason=non_numeric_count_field", file=sys.stderr)
            print(f"field={column}", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)
        if parsed < 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print(f"reason=negative_count_field", file=sys.stderr)
            print(f"field={column}", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)
        numeric_totals[column] += parsed

    if status == "ok":
        ok_rows.append(row)
        if int(row["diagnostic_total_constraints"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print("reason=zero_diagnostic_total_constraints_for_ok_case", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)
        if int(row["diagnostic_descriptive_constraint_count"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print("reason=zero_diagnostic_descriptive_constraint_count_for_ok_case", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)
        if int(row["diagnostic_local_pattern_constraint_count"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print("failure_kind=distribution", file=sys.stderr)
            print("reason=zero_diagnostic_local_pattern_constraint_count_for_ok_case", file=sys.stderr)
            print(f"case_name={case_name}", file=sys.stderr)
            print("content_suppressed=true", file=sys.stderr)
            sys.exit(1)

if not ok_rows:
    print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
    print("failure_kind=distribution", file=sys.stderr)
    print("reason=no_diagnostic_summary_status_ok_rows", file=sys.stderr)
    print(f"case_rows={len(rows)}", file=sys.stderr)
    print("content_suppressed=true", file=sys.stderr)
    sys.exit(1)

print("synthetic_diagnostic_distribution_check: ok")
print(f"summary_csv: {summary_path}")
print(f"summary_manifest: {marker_path}")
print(f"cases: {len(rows)}")
print(f"marker_case_count: {case_count}")
print(f"diagnostic_ok_cases: {len(ok_rows)}")
print(f"diagnostic_total_constraints: {numeric_totals['diagnostic_total_constraints']}")
print(
    "diagnostic_descriptive_constraint_count: "
    f"{numeric_totals['diagnostic_descriptive_constraint_count']}"
)
print(
    "diagnostic_blocking_constraint_count: "
    f"{numeric_totals['diagnostic_blocking_constraint_count']}"
)
print(
    "diagnostic_safety_constraint_count: "
    f"{numeric_totals['diagnostic_safety_constraint_count']}"
)
print(
    "diagnostic_local_pattern_constraint_count: "
    f"{numeric_totals['diagnostic_local_pattern_constraint_count']}"
)
print(
    "diagnostic_linguistic_placeholder_constraint_count: "
    f"{numeric_totals['diagnostic_linguistic_placeholder_constraint_count']}"
)
print(
    "diagnostic_non_leaky_linguistic_constraint_count: "
    f"{numeric_totals['diagnostic_non_leaky_linguistic_constraint_count']}"
)
print("performance_metrics_included: false")
print("content_suppressed: true")
PY
