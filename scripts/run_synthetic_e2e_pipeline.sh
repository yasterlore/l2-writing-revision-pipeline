#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name> [expected_actions.jsonl]" >&2
  echo "Runs the synthetic-only Rust + Python E2E pipeline without printing JSONL contents." >&2
  echo "If expected_actions.jsonl is provided, runs synthetic-only evaluation after scoring." >&2
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  usage
  exit 2
fi

input_path=$1
case_name=$2
expected_actions=${3:-}

if [ ! -f "$input_path" ]; then
  echo "Input raw event JSONL does not exist: $input_path" >&2
  usage
  exit 2
fi

if [ -n "$expected_actions" ] && [ ! -f "$expected_actions" ]; then
  echo "Expected action JSONL does not exist: $expected_actions" >&2
  usage
  exit 2
fi

case "$case_name" in
  *[!A-Za-z0-9._-]* | "" )
    echo "case_name must contain only letters, numbers, dot, underscore, or hyphen: $case_name" >&2
    exit 2
    ;;
esac

output_dir="tmp/synthetic_e2e/$case_name"
safe_views="$output_dir/safe_views.jsonl"
candidate_sets="$output_dir/candidate_sets.jsonl"
candidate_features="$output_dir/candidate_features.jsonl"
constraint_violations="$output_dir/constraint_violations.jsonl"
candidate_scores="$output_dir/candidate_scores.jsonl"
evaluation_report="$output_dir/evaluation_report.json"

mkdir -p "$output_dir"

run_step() {
  label=$1
  shift
  echo "$label: running"
  if "$@" >/dev/null; then
    echo "$label: ok"
  else
    status=$?
    echo "$label: fail" >&2
    echo "content_suppressed: true" >&2
    echo "output_directory: $output_dir" >&2
    exit "$status"
  fi
}

echo "synthetic_e2e_pipeline: start"
echo "input_raw_events: $input_path"
echo "output_directory: $output_dir"
echo "overwrite_policy: existing files with the same names may be overwritten"
if [ -n "$expected_actions" ]; then
  echo "evaluation: requested"
else
  echo "evaluation: skipped"
fi
echo "content_suppressed: true"

run_step "safe view export" \
  cargo run -q -p kslog_cli -- export-safe-view "$input_path" "$safe_views"

run_step "candidate generation" \
  env PYTHONPATH=python python3 -m candidate_generation.generate \
    --input "$safe_views" \
    --output "$candidate_sets"

run_step "feature extraction" \
  env PYTHONPATH=python python3 -m ot_scorer.features \
    --input "$candidate_sets" \
    --output "$candidate_features"

run_step "constraint generation" \
  env PYTHONPATH=python python3 -m ot_scorer.constraints \
    --input "$candidate_features" \
    --output "$constraint_violations"

run_step "scoring" \
  env PYTHONPATH=python python3 -m ot_scorer.score \
    --input "$constraint_violations" \
    --output "$candidate_scores"

if [ -n "$expected_actions" ]; then
  run_step "evaluation" \
    env PYTHONPATH=python python3 -m evaluation.evaluate \
      --scores "$candidate_scores" \
      --expected "$expected_actions" \
      --output "$evaluation_report"
fi

echo "synthetic_e2e_pipeline: ok"
echo "safe view export: ok"
echo "candidate generation: ok"
echo "feature extraction: ok"
echo "constraint generation: ok"
echo "scoring: ok"
if [ -n "$expected_actions" ]; then
  echo "evaluation: ok"
  echo "evaluation_report: $evaluation_report"
else
  echo "evaluation: skipped"
fi
echo "output_directory: $output_dir"
echo "content_suppressed: true"
