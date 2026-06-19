#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/run_synthetic_e2e_summary.sh [input_dir] [registry.json]" >&2
  echo "Runs synthetic raw-event fixtures through the E2E pipeline and prints summary only." >&2
}

if [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

input_dir=${1:-tests/fixtures/synthetic/raw_events/valid}
registry_path=${2:-tests/fixtures/synthetic/expected_actions/registry.json}

case "$input_dir" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "Refusing non-synthetic or private-looking input directory: $input_dir" >&2
    exit 2
    ;;
esac

if [ ! -d "$input_dir" ]; then
  echo "Input directory does not exist: $input_dir" >&2
  usage
  exit 2
fi

if [ ! -f "$registry_path" ]; then
  echo "Expected action registry does not exist: $registry_path" >&2
  usage
  exit 2
fi

summary_dir="tmp/synthetic_e2e_summary"
summary_csv="$summary_dir/summary.csv"
file_list="$summary_dir/input_files.txt"
mkdir -p "$summary_dir"

find "$input_dir" -maxdepth 1 -type f -name '*.jsonl' -print | sort > "$file_list"

if [ ! -s "$file_list" ]; then
  echo "No .jsonl files found in input directory: $input_dir" >&2
  exit 2
fi

printf '%s\n' "case_name,pipeline_status,failed_stage,output_dir,score_sets_count,candidates_count,blocked_candidates_count,unblocked_candidates_count,rank1_available,evaluation_status,expected_action_status,expected_action_path,evaluation_report_exists,evaluation_summary_available,evaluation_episodes_total,evaluation_episodes_evaluated,evaluation_exact_match_count,evaluation_expected_found_count,evaluation_blocked_expected_count,diagnostic_summary_status,diagnostic_summary_path,diagnostic_total_constraints,diagnostic_descriptive_constraint_count,diagnostic_blocking_constraint_count,diagnostic_safety_constraint_count,diagnostic_local_pattern_constraint_count,diagnostic_linguistic_placeholder_constraint_count,diagnostic_non_leaky_linguistic_constraint_count,content_suppressed" > "$summary_csv"

echo "synthetic_e2e_summary: start"
echo "input_dir: $input_dir"
echo "expected_action_registry: $registry_path"
echo "summary_csv: $summary_csv"
echo "content_suppressed: true"
printf '%-32s %-8s %-22s %-5s %-10s %-8s %-10s %-8s %-18s %-8s %-10s %s\n' \
  "case_name" "status" "failed_stage" "sets" "candidates" "blocked" "unblocked" "rank1" "evaluation" "expected" "diagnostic" "output_dir"

overall_status=0

while IFS= read -r input_file; do
  file_name=$(basename "$input_file")
  case_name=${file_name%.jsonl}
  output_dir="tmp/synthetic_e2e/$case_name"
  log_file="$summary_dir/$case_name.log"
  failed_stage="none"
  score_sets_count="0"
  candidates_count="0"
  blocked_candidates_count="0"
  unblocked_candidates_count="0"
  rank1_available="false"
  evaluation_status="skipped_no_registry"
  expected_action_status="missing"
  expected_action_path=""
  evaluation_report_exists="false"
  evaluation_summary_available="false"
  evaluation_episodes_total="0"
  evaluation_episodes_evaluated="0"
  evaluation_exact_match_count="0"
  evaluation_expected_found_count="0"
  evaluation_blocked_expected_count="0"
  diagnostic_summary_status="skipped_missing_constraints"
  diagnostic_summary_path="$output_dir/diagnostic_summary.json"
  diagnostic_total_constraints="0"
  diagnostic_descriptive_constraint_count="0"
  diagnostic_blocking_constraint_count="0"
  diagnostic_safety_constraint_count="0"
  diagnostic_local_pattern_constraint_count="0"
  diagnostic_linguistic_placeholder_constraint_count="0"
  diagnostic_non_leaky_linguistic_constraint_count="0"

  lookup_result=$(
    env PYTHONPATH=python python3 -m evaluation.expected_action_registry lookup \
      --registry "$registry_path" \
      --case-name "$case_name"
  ) || {
    pipeline_status="fail"
    failed_stage="expected_action_registry"
    overall_status=1
    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true\n' \
      "$case_name" \
      "$pipeline_status" \
      "$failed_stage" \
      "$output_dir" \
      "$score_sets_count" \
      "$candidates_count" \
      "$blocked_candidates_count" \
      "$unblocked_candidates_count" \
      "$rank1_available" \
      "fail" \
      "error" \
      "" \
      "$evaluation_report_exists" \
      "$evaluation_summary_available" \
      "$evaluation_episodes_total" \
      "$evaluation_episodes_evaluated" \
      "$evaluation_exact_match_count" \
      "$evaluation_expected_found_count" \
      "$evaluation_blocked_expected_count" \
      "$diagnostic_summary_status" \
      "$diagnostic_summary_path" \
      "$diagnostic_total_constraints" \
      "$diagnostic_descriptive_constraint_count" \
      "$diagnostic_blocking_constraint_count" \
      "$diagnostic_safety_constraint_count" \
      "$diagnostic_local_pattern_constraint_count" \
      "$diagnostic_linguistic_placeholder_constraint_count" \
      "$diagnostic_non_leaky_linguistic_constraint_count" >> "$summary_csv"
    printf '%-32s %-8s %-22s %-5s %-10s %-8s %-10s %-8s %-18s %-8s %-10s %s\n' \
      "$case_name" \
      "$pipeline_status" \
      "$failed_stage" \
      "$score_sets_count" \
      "$candidates_count" \
      "$blocked_candidates_count" \
      "$unblocked_candidates_count" \
      "$rank1_available" \
      "fail" \
      "error" \
      "$diagnostic_summary_status" \
      "$output_dir"
    continue
  }
  expected_action_status=$(printf '%s\n' "$lookup_result" | cut -f1)
  expected_action_path=$(printf '%s\n' "$lookup_result" | cut -f2)

  case "$expected_action_status" in
    active )
      evaluation_status="fail"
      ;;
    pending )
      evaluation_status="skipped_pending"
      ;;
    missing )
      evaluation_status="skipped_missing"
      ;;
    * )
      evaluation_status="fail"
      ;;
  esac

  if [ "$expected_action_status" = "active" ]; then
    pipeline_command_status=0
    scripts/run_synthetic_e2e_pipeline.sh \
      "$input_file" \
      "$case_name" \
      "$expected_action_path" > "$log_file" 2>&1 || pipeline_command_status=$?
  else
    pipeline_command_status=0
    scripts/run_synthetic_e2e_pipeline.sh "$input_file" "$case_name" > "$log_file" 2>&1 || pipeline_command_status=$?
  fi

  if [ "$pipeline_command_status" -eq 0 ]; then
    pipeline_status="ok"
    if [ "$expected_action_status" = "active" ]; then
      if [ -f "$output_dir/evaluation_report.json" ]; then
        evaluation_status="ok"
        evaluation_report_exists="true"
        evaluation_counts=$(
          python3 -c 'import json, sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    report = json.load(handle)
print(",".join(str(report.get(key, 0)) for key in (
    "episodes_total",
    "episodes_evaluated",
    "exact_match_count",
    "expected_found_in_candidates_count",
    "blocked_expected_count",
)))' \
            "$output_dir/evaluation_report.json"
        )
        evaluation_summary_available="true"
        evaluation_episodes_total=$(echo "$evaluation_counts" | cut -d, -f1)
        evaluation_episodes_evaluated=$(echo "$evaluation_counts" | cut -d, -f2)
        evaluation_exact_match_count=$(echo "$evaluation_counts" | cut -d, -f3)
        evaluation_expected_found_count=$(echo "$evaluation_counts" | cut -d, -f4)
        evaluation_blocked_expected_count=$(echo "$evaluation_counts" | cut -d, -f5)
      else
        evaluation_status="fail"
        overall_status=1
      fi
    fi
    if [ -f "$output_dir/candidate_scores.jsonl" ]; then
      counts=$(
        python3 -c 'import json, sys
path = sys.argv[1]
score_sets = 0
candidates = 0
blocked = 0
rank1 = False
with open(path, "r", encoding="utf-8") as handle:
    for line in handle:
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        score_sets += 1
        for score in row.get("candidate_scores", []):
            candidates += 1
            if score.get("blocked") is True:
                blocked += 1
            if score.get("rank") == 1:
                rank1 = True
print(f"{score_sets},{candidates},{blocked},{candidates - blocked},{str(rank1).lower()}")' \
          "$output_dir/candidate_scores.jsonl"
      )
      score_sets_count=$(echo "$counts" | cut -d, -f1)
      candidates_count=$(echo "$counts" | cut -d, -f2)
      blocked_candidates_count=$(echo "$counts" | cut -d, -f3)
      unblocked_candidates_count=$(echo "$counts" | cut -d, -f4)
      rank1_available=$(echo "$counts" | cut -d, -f5)
    fi
    if [ -f "$output_dir/constraint_violations.jsonl" ]; then
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
        overall_status=1
      fi
    fi
  else
    pipeline_status="fail"
    overall_status=1
    failed_stage=$(grep -m 1 ': fail' "$log_file" | sed 's/: fail.*//' || true)
    if [ -z "$failed_stage" ]; then
      failed_stage="unknown"
    fi
  fi

  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true\n' \
    "$case_name" \
    "$pipeline_status" \
    "$failed_stage" \
    "$output_dir" \
    "$score_sets_count" \
    "$candidates_count" \
    "$blocked_candidates_count" \
    "$unblocked_candidates_count" \
    "$rank1_available" \
    "$evaluation_status" \
    "$expected_action_status" \
    "$expected_action_path" \
    "$evaluation_report_exists" \
    "$evaluation_summary_available" \
    "$evaluation_episodes_total" \
    "$evaluation_episodes_evaluated" \
    "$evaluation_exact_match_count" \
    "$evaluation_expected_found_count" \
    "$evaluation_blocked_expected_count" \
    "$diagnostic_summary_status" \
    "$diagnostic_summary_path" \
    "$diagnostic_total_constraints" \
    "$diagnostic_descriptive_constraint_count" \
    "$diagnostic_blocking_constraint_count" \
    "$diagnostic_safety_constraint_count" \
    "$diagnostic_local_pattern_constraint_count" \
    "$diagnostic_linguistic_placeholder_constraint_count" \
    "$diagnostic_non_leaky_linguistic_constraint_count" >> "$summary_csv"

  printf '%-32s %-8s %-22s %-5s %-10s %-8s %-10s %-8s %-18s %-8s %-10s %s\n' \
    "$case_name" \
    "$pipeline_status" \
    "$failed_stage" \
    "$score_sets_count" \
    "$candidates_count" \
    "$blocked_candidates_count" \
    "$unblocked_candidates_count" \
    "$rank1_available" \
    "$evaluation_status" \
    "$expected_action_status" \
    "$diagnostic_summary_status" \
    "$output_dir"
done < "$file_list"

echo "synthetic_e2e_summary: complete"
echo "summary_csv: $summary_csv"
echo "content_suppressed: true"
echo "evaluation_metrics_included: false"
echo "evaluation_report_contents_suppressed: true"

exit "$overall_status"
