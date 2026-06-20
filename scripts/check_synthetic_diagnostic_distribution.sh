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
    echo "expected_summary_csv=tmp/synthetic_e2e_summary/summary.csv" >&2
    echo "content_suppressed=true" >&2
    exit 2
    ;;
esac

if [ ! -f "$summary_csv" ]; then
  echo "synthetic_diagnostic_distribution_check: fail" >&2
  echo "failure_kind=precondition" >&2
  echo "reason=missing_summary_csv" >&2
  echo "summary_csv=$summary_csv" >&2
  echo "expected_summary_csv=tmp/synthetic_e2e_summary/summary.csv" >&2
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

python3 - "$summary_csv" <<'PY'
import csv
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])

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
        print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
        print("failure_kind=precondition", file=sys.stderr)
        print("reason=missing_header", file=sys.stderr)
        print(f"summary_csv={summary_path}", file=sys.stderr)
        print("next_step=scripts/run_synthetic_e2e_summary.sh", file=sys.stderr)
        print("content_suppressed=true", file=sys.stderr)
        sys.exit(2)
    missing_columns = [name for name in required_columns if name not in fieldnames]
    if missing_columns:
        print(
            "synthetic_diagnostic_distribution_check: fail",
            file=sys.stderr,
        )
        print("failure_kind=precondition", file=sys.stderr)
        print("reason=malformed_header", file=sys.stderr)
        print(f"summary_csv={summary_path}", file=sys.stderr)
        print(f"missing_required_columns_count={len(missing_columns)}", file=sys.stderr)
        print("content_suppressed=true", file=sys.stderr)
        sys.exit(2)
    rows = list(reader)

if not rows:
    print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
    print("failure_kind=precondition", file=sys.stderr)
    print("reason=no_cases", file=sys.stderr)
    print(f"summary_csv={summary_path}", file=sys.stderr)
    print("case_rows=0", file=sys.stderr)
    print("next_step=scripts/run_synthetic_e2e_summary.sh", file=sys.stderr)
    print("content_suppressed=true", file=sys.stderr)
    sys.exit(2)

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
print(f"cases: {len(rows)}")
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
