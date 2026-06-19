#!/usr/bin/env sh
set -eu

VALID_CONFIG="tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json"
INVALID_CONFIG="tests/fixtures/synthetic/hand_weight_configs/invalid/forbidden_field_config.json"
UNSAFE_CONFIG="private_data/fake_config.json"
SAFE_CONFIG_NAME="current_default_like_config"
CONFIG_SUMMARY_CSV="tmp/synthetic_e2e_config_summary/$SAFE_CONFIG_NAME/summary.csv"
NO_CONFIG_SUMMARY_CSV="tmp/synthetic_e2e_summary/summary.csv"
SMOKE_DIR="tmp/config_enabled_summary_smoke"
VALID_STDOUT="$SMOKE_DIR/config_summary_stdout.log"
MISSING_STDOUT="$SMOKE_DIR/missing_config_stdout.log"
INVALID_STDOUT="$SMOKE_DIR/invalid_config_stdout.log"
UNSAFE_STDOUT="$SMOKE_DIR/unsafe_config_stdout.log"
NO_CONFIG_STDOUT="$SMOKE_DIR/no_config_summary_stdout.log"

mkdir -p "$SMOKE_DIR"

safe_log_has_forbidden_body_marker() {
  path=$1
  if grep -E '[{}]|"constraint_weights"|"constraint_id"|"candidate_scores"|"candidate_id"|"config_schema_version"|raw_text|local_context_before|final_text|observed_after_text|gold_label|expected_action' "$path" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

echo "config_enabled_summary_smoke: start"
echo "performance_evaluation=false"
echo "content_suppressed=true"

if scripts/run_synthetic_e2e_config_summary.sh \
  --weight-config "$VALID_CONFIG" > "$VALID_STDOUT" 2>&1; then
  echo "config_summary_run: ok"
else
  echo "config_summary_run: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if [ ! -f "$CONFIG_SUMMARY_CSV" ]; then
  echo "config_summary_csv_exists: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if [ "$CONFIG_SUMMARY_CSV" = "$NO_CONFIG_SUMMARY_CSV" ]; then
  echo "summary_path_separation: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

summary_counts=$(
  python3 -c 'import csv, sys
path = sys.argv[1]
required = [
    "case_name",
    "config_summary_status",
    "config_name",
    "config_schema_version",
    "weight_config_path_basename",
    "pipeline_status",
    "failed_stage",
    "output_dir",
    "score_sets_count",
    "candidates_count",
    "diagnostic_summary_status",
    "diagnostic_total_constraints",
    "diagnostic_descriptive_constraint_count",
    "diagnostic_blocking_constraint_count",
    "diagnostic_safety_constraint_count",
    "diagnostic_local_pattern_constraint_count",
    "diagnostic_linguistic_placeholder_constraint_count",
    "diagnostic_non_leaky_linguistic_constraint_count",
    "content_suppressed",
]
with open(path, "r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))
if not rows:
    raise SystemExit("summary has no cases")
missing = [name for name in required if name not in rows[0]]
if missing:
    raise SystemExit("missing required columns: " + ",".join(missing))
if not all(row.get("config_name") for row in rows):
    raise SystemExit("missing config_name value")
if not all(row.get("config_schema_version") for row in rows):
    raise SystemExit("missing config_schema_version value")
if not all(row.get("content_suppressed") == "true" for row in rows):
    raise SystemExit("content_suppressed must be true")
ok_rows = sum(1 for row in rows if row.get("config_summary_status") == "ok")
if ok_rows == 0:
    raise SystemExit("no ok config summary rows")
print(f"{len(rows)},{ok_rows}")' "$CONFIG_SUMMARY_CSV"
)
summary_rows=$(echo "$summary_counts" | cut -d, -f1)
summary_ok_rows=$(echo "$summary_counts" | cut -d, -f2)

if safe_log_has_forbidden_body_marker "$VALID_STDOUT"; then
  echo "config_summary_stdout_safe: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if scripts/run_synthetic_e2e_config_summary.sh > "$MISSING_STDOUT" 2>&1; then
  echo "missing_weight_config_failure: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi
if safe_log_has_forbidden_body_marker "$MISSING_STDOUT"; then
  echo "missing_weight_config_stdout_safe: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if scripts/run_synthetic_e2e_config_summary.sh \
  --weight-config "$INVALID_CONFIG" > "$INVALID_STDOUT" 2>&1; then
  echo "invalid_config_failure: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi
if safe_log_has_forbidden_body_marker "$INVALID_STDOUT"; then
  echo "invalid_config_stdout_safe: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if scripts/run_synthetic_e2e_config_summary.sh \
  --weight-config "$UNSAFE_CONFIG" > "$UNSAFE_STDOUT" 2>&1; then
  echo "unsafe_config_failure: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi
if safe_log_has_forbidden_body_marker "$UNSAFE_STDOUT"; then
  echo "unsafe_config_stdout_safe: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if scripts/run_synthetic_e2e_summary.sh > "$NO_CONFIG_STDOUT" 2>&1; then
  echo "no_config_summary_run: ok"
else
  echo "no_config_summary_run: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

if [ ! -f "$NO_CONFIG_SUMMARY_CSV" ]; then
  echo "no_config_summary_csv_exists: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

no_config_columns=$(
  python3 -c 'import csv, sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8", newline="") as handle:
    header = next(csv.reader(handle))
config_columns = [
    name for name in header
    if name.startswith("config_") or "weight_config" in name
]
if config_columns:
    raise SystemExit("no-config summary has config columns")
print(len(header))' "$NO_CONFIG_SUMMARY_CSV"
)

if ! git check-ignore "$CONFIG_SUMMARY_CSV" >/dev/null 2>&1; then
  echo "config_summary_gitignored: fail" >&2
  echo "content_suppressed=true" >&2
  exit 1
fi

echo "config_enabled_summary_smoke: ok"
echo "summary_csv: $CONFIG_SUMMARY_CSV"
echo "no_config_summary_csv: $NO_CONFIG_SUMMARY_CSV"
echo "summary_paths_separate=true"
echo "summary_rows: $summary_rows"
echo "summary_ok_rows: $summary_ok_rows"
echo "required_columns_present=true"
echo "config_metadata_present=true"
echo "content_suppressed_values=true"
echo "missing_weight_config_expected_failure=true"
echo "invalid_config_expected_failure=true"
echo "unsafe_config_expected_failure=true"
echo "no_config_summary_config_columns=0"
echo "no_config_summary_columns: $no_config_columns"
echo "stdout_safe_summary_only=true"
echo "performance_evaluation=false"
echo "content_suppressed=true"
