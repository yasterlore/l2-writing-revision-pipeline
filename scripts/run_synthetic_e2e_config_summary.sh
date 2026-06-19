#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/run_synthetic_e2e_config_summary.sh --weight-config <config.json> [input_dir]" >&2
  echo "Runs config-enabled synthetic E2E cases and writes a separate count-only summary." >&2
}

unsafe_path() {
  case "$1" in
    *manual_outputs/* | *private_data/* | *real_data/* | *participant_data/* )
      return 0
      ;;
    * )
      return 1
      ;;
  esac
}

safe_name() {
  python3 -c 'import re, sys
raw = sys.argv[1]
name = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._-")
if not name:
    raise SystemExit(2)
print(name)' "$1"
}

append_csv_row() {
  python3 - "$summary_csv" "$@" <<'PY'
import csv
import sys

path = sys.argv[1]
row = sys.argv[2:]
with open(path, "a", encoding="utf-8", newline="") as handle:
    csv.writer(handle).writerow(row)
PY
}

weight_config=""
input_dir="tests/fixtures/synthetic/raw_events/valid"
input_dir_set="false"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --weight-config )
      shift
      if [ "$#" -eq 0 ] || [ "${1#--}" != "$1" ]; then
        echo "--weight-config requires a config path" >&2
        usage
        exit 2
      fi
      if [ -n "$weight_config" ]; then
        echo "--weight-config may be provided only once" >&2
        usage
        exit 2
      fi
      weight_config=$1
      shift
      ;;
    --* )
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
    * )
      if [ "$input_dir_set" = "true" ]; then
        echo "Unexpected positional argument: $1" >&2
        usage
        exit 2
      fi
      input_dir=$1
      input_dir_set="true"
      shift
      ;;
  esac
done

if [ -z "$weight_config" ]; then
  echo "Missing required --weight-config option" >&2
  usage
  exit 2
fi

if unsafe_path "$weight_config"; then
  echo "Unsafe weight config path" >&2
  echo "content_suppressed: true" >&2
  exit 2
fi

if unsafe_path "$input_dir"; then
  echo "Unsafe input directory" >&2
  echo "content_suppressed: true" >&2
  exit 2
fi

if [ ! -f "$weight_config" ]; then
  echo "Weight config JSON does not exist" >&2
  echo "content_suppressed: true" >&2
  exit 2
fi

if [ ! -d "$input_dir" ]; then
  echo "Input directory does not exist: $input_dir" >&2
  usage
  exit 2
fi

weight_config_basename=$(basename "$weight_config")
config_stem=${weight_config_basename%.*}
safe_config_name=$(safe_name "$config_stem") || {
  echo "Weight config name cannot be converted to a safe directory name" >&2
  echo "content_suppressed: true" >&2
  exit 2
}

metadata_file=$(mktemp "${TMPDIR:-/tmp}/synthetic_config_summary_meta.XXXXXX")
if ! env PYTHONPATH=python python3 -c 'import sys
from ot_scorer.weight_config import WeightConfigError, load_hand_weight_config

try:
    config = load_hand_weight_config(sys.argv[1])
except WeightConfigError:
    print("config_validation_status=fail", file=sys.stderr)
    print("safe_error=config validation failed", file=sys.stderr)
    print("content_suppressed=true", file=sys.stderr)
    raise SystemExit(2)
print(f"config_name={config.config_name}")
print(f"config_schema_version={config.config_schema_version}")' "$weight_config" > "$metadata_file"; then
  rm -f "$metadata_file"
  echo "config_summary_status=fail" >&2
  echo "failed_stage=config_validation" >&2
  echo "content_suppressed: true" >&2
  exit 2
fi

config_name=$(sed -n 's/^config_name=//p' "$metadata_file")
config_schema_version=$(sed -n 's/^config_schema_version=//p' "$metadata_file")
rm -f "$metadata_file"

summary_root="tmp/synthetic_e2e_config_summary/$safe_config_name"
summary_csv="$summary_root/summary.csv"
file_list="$summary_root/input_files.txt"
log_dir="$summary_root/logs"
diagnostic_root="$summary_root/diagnostics"

mkdir -p "$summary_root" "$log_dir" "$diagnostic_root"
find "$input_dir" -maxdepth 1 -type f -name '*.jsonl' -print | sort > "$file_list"

if [ ! -s "$file_list" ]; then
  echo "No .jsonl files found in input directory: $input_dir" >&2
  exit 2
fi

printf '%s\n' "case_name,config_summary_status,config_name,config_schema_version,weight_config_path_basename,pipeline_status,failed_stage,output_dir,score_sets_count,candidates_count,diagnostic_summary_status,diagnostic_total_constraints,diagnostic_descriptive_constraint_count,diagnostic_blocking_constraint_count,diagnostic_safety_constraint_count,diagnostic_local_pattern_constraint_count,diagnostic_linguistic_placeholder_constraint_count,diagnostic_non_leaky_linguistic_constraint_count,content_suppressed" > "$summary_csv"

echo "synthetic_e2e_config_summary: start"
echo "input_dir: $input_dir"
echo "weight_config_path_basename: $weight_config_basename"
echo "safe_config_name: $safe_config_name"
echo "summary_csv: $summary_csv"
echo "content_suppressed: true"
printf '%-32s %-8s %-18s %-5s %-10s %-10s %s\n' \
  "case_name" "status" "failed_stage" "sets" "candidates" "diagnostic" "output_dir"

overall_status=0

while IFS= read -r input_file; do
  file_name=$(basename "$input_file")
  case_name=${file_name%.jsonl}
  case_run_name="${case_name}__config_${safe_config_name}"
  output_dir="tmp/synthetic_e2e/$case_run_name"
  log_file="$log_dir/$case_name.log"
  diagnostic_summary_path="$diagnostic_root/$case_name/diagnostic_summary.json"

  config_summary_status="ok"
  pipeline_status="ok"
  failed_stage="none"
  score_sets_count="0"
  candidates_count="0"
  diagnostic_summary_status="skipped_missing_constraints"
  diagnostic_total_constraints="0"
  diagnostic_descriptive_constraint_count="0"
  diagnostic_blocking_constraint_count="0"
  diagnostic_safety_constraint_count="0"
  diagnostic_local_pattern_constraint_count="0"
  diagnostic_linguistic_placeholder_constraint_count="0"
  diagnostic_non_leaky_linguistic_constraint_count="0"

  pipeline_command_status=0
  scripts/run_synthetic_e2e_pipeline.sh \
    "$input_file" \
    "$case_run_name" \
    --weight-config "$weight_config" > "$log_file" 2>&1 || pipeline_command_status=$?

  if [ "$pipeline_command_status" -eq 0 ] && [ -f "$output_dir/candidate_scores.jsonl" ]; then
    counts=$(
      python3 -c 'import json, sys
path = sys.argv[1]
score_sets = 0
candidates = 0
with open(path, "r", encoding="utf-8") as handle:
    for line in handle:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        score_sets += 1
        candidates += len(row.get("candidate_scores", []))
print(f"{score_sets},{candidates}")' \
        "$output_dir/candidate_scores.jsonl"
    ) || {
      pipeline_status="fail"
      failed_stage="score_count"
      config_summary_status="fail"
      overall_status=1
    }
    if [ "$pipeline_status" = "ok" ]; then
      score_sets_count=$(echo "$counts" | cut -d, -f1)
      candidates_count=$(echo "$counts" | cut -d, -f2)
    fi
  else
    pipeline_status="fail"
    config_summary_status="fail"
    overall_status=1
    failed_stage=$(grep -m 1 ': fail' "$log_file" | sed 's/: fail.*//' || true)
    if [ -z "$failed_stage" ]; then
      failed_stage="scoring"
    fi
  fi

  if [ "$pipeline_status" = "ok" ] && [ -f "$output_dir/constraint_violations.jsonl" ]; then
    mkdir -p "$(dirname "$diagnostic_summary_path")"
    diagnostic_command_status=0
    env PYTHONPATH=python python3 -m ot_scorer.summarize_diagnostics \
      --constraints "$output_dir/constraint_violations.jsonl" \
      --output "$diagnostic_summary_path" >> "$log_file" 2>&1 || diagnostic_command_status=$?
    if [ "$diagnostic_command_status" -eq 0 ] && [ -f "$diagnostic_summary_path" ]; then
      diagnostic_summary_status="ok"
      diagnostic_counts=$(
        python3 -c 'import json, sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    summary = json.load(handle)
local_count = sum(summary.get("local_pattern_constraint_counts", {}).values())
linguistic_count = sum(summary.get("linguistic_placeholder_constraint_counts", {}).values())
non_leaky_linguistic_count = sum(summary.get("non_leaky_linguistic_constraint_counts", {}).values())
print(",".join(str(value) for value in (
    summary.get("total_constraints", 0),
    summary.get("descriptive_constraint_count", 0),
    summary.get("blocking_constraint_count", 0),
    summary.get("safety_constraint_count", 0),
    local_count,
    linguistic_count,
    non_leaky_linguistic_count,
)))' \
          "$diagnostic_summary_path"
      )
      diagnostic_total_constraints=$(echo "$diagnostic_counts" | cut -d, -f1)
      diagnostic_descriptive_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f2)
      diagnostic_blocking_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f3)
      diagnostic_safety_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f4)
      diagnostic_local_pattern_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f5)
      diagnostic_linguistic_placeholder_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f6)
      diagnostic_non_leaky_linguistic_constraint_count=$(echo "$diagnostic_counts" | cut -d, -f7)
    else
      diagnostic_summary_status="fail"
      config_summary_status="fail"
      overall_status=1
    fi
  fi

  append_csv_row \
    "$case_name" \
    "$config_summary_status" \
    "$config_name" \
    "$config_schema_version" \
    "$weight_config_basename" \
    "$pipeline_status" \
    "$failed_stage" \
    "$output_dir" \
    "$score_sets_count" \
    "$candidates_count" \
    "$diagnostic_summary_status" \
    "$diagnostic_total_constraints" \
    "$diagnostic_descriptive_constraint_count" \
    "$diagnostic_blocking_constraint_count" \
    "$diagnostic_safety_constraint_count" \
    "$diagnostic_local_pattern_constraint_count" \
    "$diagnostic_linguistic_placeholder_constraint_count" \
    "$diagnostic_non_leaky_linguistic_constraint_count" \
    "true"

  printf '%-32s %-8s %-18s %-5s %-10s %-10s %s\n' \
    "$case_name" \
    "$config_summary_status" \
    "$failed_stage" \
    "$score_sets_count" \
    "$candidates_count" \
    "$diagnostic_summary_status" \
    "$output_dir"
done < "$file_list"

echo "synthetic_e2e_config_summary: complete"
echo "summary_csv: $summary_csv"
echo "no_config_summary_changed: false"
echo "content_suppressed: true"
echo "performance_metrics_included: false"

exit "$overall_status"
