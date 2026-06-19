#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name> [expected_actions.jsonl] [--weight-config <config.json>]" >&2
  echo "Runs the synthetic-only Rust + Python E2E pipeline without printing JSONL contents." >&2
  echo "If expected_actions.jsonl is provided, runs synthetic-only evaluation after scoring." >&2
  echo "If --weight-config is provided, it must be explicit and named." >&2
}

unsafe_config_path() {
  case "$1" in
    *manual_outputs/* | *private_data/* | *real_data/* | *participant_data/* )
      return 0
      ;;
    * )
      return 1
      ;;
  esac
}

if [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

input_path=$1
case_name=$2
shift 2

expected_actions=""
weight_config=""

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
      if [ -n "$expected_actions" ]; then
        echo "Unexpected positional argument: $1" >&2
        usage
        exit 2
      fi
      expected_actions=$1
      shift
      ;;
  esac
done

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

if [ -n "$weight_config" ]; then
  if unsafe_config_path "$weight_config"; then
    echo "Unsafe weight config path: $weight_config" >&2
    echo "content_suppressed: true" >&2
    usage
    exit 2
  fi
  if [ ! -f "$weight_config" ]; then
    echo "Weight config JSON does not exist: $weight_config" >&2
    usage
    exit 2
  fi
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
if [ -n "$weight_config" ]; then
  echo "weight_config: requested"
  echo "weight_config_path: $weight_config"
  echo "config_enabled_e2e: explicit"
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

if [ -n "$weight_config" ]; then
  rm -f "$candidate_scores"
  run_step "scoring" \
    env PYTHONPATH=python python3 -m ot_scorer.score \
      --input "$constraint_violations" \
      --output "$candidate_scores" \
      --weight-config "$weight_config"
else
  run_step "scoring" \
    env PYTHONPATH=python python3 -m ot_scorer.score \
      --input "$constraint_violations" \
      --output "$candidate_scores"
fi

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
if [ -n "$weight_config" ]; then
  echo "weight_config: used"
fi
if [ -n "$expected_actions" ]; then
  echo "evaluation: ok"
  echo "evaluation_report: $evaluation_report"
else
  echo "evaluation: skipped"
fi
echo "output_directory: $output_dir"
echo "content_suppressed: true"
