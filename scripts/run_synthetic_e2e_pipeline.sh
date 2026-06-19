#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name>" >&2
  echo "Runs the synthetic-only Rust + Python E2E pipeline without printing JSONL contents." >&2
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

input_path=$1
case_name=$2

if [ ! -f "$input_path" ]; then
  echo "Input raw event JSONL does not exist: $input_path" >&2
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

echo "synthetic_e2e_pipeline: ok"
echo "safe view export: ok"
echo "candidate generation: ok"
echo "feature extraction: ok"
echo "constraint generation: ok"
echo "scoring: ok"
echo "output_directory: $output_dir"
echo "content_suppressed: true"
