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
esac

if [ ! -f "$summary_csv" ]; then
  echo "Summary CSV does not exist: $summary_csv" >&2
  usage
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
]

numeric_columns = [
    "diagnostic_total_constraints",
    "diagnostic_descriptive_constraint_count",
    "diagnostic_blocking_constraint_count",
    "diagnostic_safety_constraint_count",
    "diagnostic_local_pattern_constraint_count",
    "diagnostic_linguistic_placeholder_constraint_count",
]

with summary_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    missing_columns = [name for name in required_columns if name not in (reader.fieldnames or [])]
    if missing_columns:
        print(
            "synthetic_diagnostic_distribution_check: fail",
            file=sys.stderr,
        )
        print(
            "missing_columns: " + ",".join(missing_columns),
            file=sys.stderr,
        )
        sys.exit(1)
    rows = list(reader)

if not rows:
    print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
    print("reason: no_cases", file=sys.stderr)
    sys.exit(1)

ok_rows = []
numeric_totals = {name: 0 for name in numeric_columns}

for index, row in enumerate(rows, start=1):
    case_name = row.get("case_name", "")
    status = row.get("diagnostic_summary_status", "")
    if not status:
        print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
        print(f"reason: missing diagnostic_summary_status at row {index}", file=sys.stderr)
        sys.exit(1)

    for column in numeric_columns:
        raw_value = row.get(column, "")
        if raw_value == "":
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: empty {column} for case {case_name}", file=sys.stderr)
            sys.exit(1)
        try:
            parsed = int(raw_value)
        except ValueError:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: non_numeric {column} for case {case_name}", file=sys.stderr)
            sys.exit(1)
        if parsed < 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: negative {column} for case {case_name}", file=sys.stderr)
            sys.exit(1)
        numeric_totals[column] += parsed

    if status == "ok":
        ok_rows.append(row)
        if int(row["diagnostic_total_constraints"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: zero diagnostic_total_constraints for ok case {case_name}", file=sys.stderr)
            sys.exit(1)
        if int(row["diagnostic_descriptive_constraint_count"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: zero diagnostic_descriptive_constraint_count for ok case {case_name}", file=sys.stderr)
            sys.exit(1)
        if int(row["diagnostic_local_pattern_constraint_count"]) <= 0:
            print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
            print(f"reason: zero diagnostic_local_pattern_constraint_count for ok case {case_name}", file=sys.stderr)
            sys.exit(1)

if not ok_rows:
    print("synthetic_diagnostic_distribution_check: fail", file=sys.stderr)
    print("reason: no diagnostic_summary_status=ok rows", file=sys.stderr)
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
print("performance_metrics_included: false")
print("content_suppressed: true")
PY
