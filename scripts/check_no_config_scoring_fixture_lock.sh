#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/check_no_config_scoring_fixture_lock.sh [expected_candidate_scores.jsonl] [generated_candidate_scores.jsonl]" >&2
  echo "With no arguments, checks deletion_case, selection_edit_case, and cursor_movement_case." >&2
  echo "With path arguments, checks one explicit expected/generated pair." >&2
  echo "This is not performance evaluation." >&2
}

if [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

check_pair() {
  case_name=$1
  expected=$2
  generated=$3

  case "$expected" in
    *manual_outputs* | *private_data* | *real_data* | *participant_data* )
      echo "case_name=${case_name}"
      echo "lock_status=fail"
      echo "reason=unsafe_path"
      echo "content_suppressed=true"
      exit 2
      ;;
  esac

  case "$generated" in
    *manual_outputs* | *private_data* | *real_data* | *participant_data* )
      echo "case_name=${case_name}"
      echo "lock_status=fail"
      echo "reason=unsafe_path"
      echo "content_suppressed=true"
      exit 2
      ;;
  esac

  PYTHONPATH=python python3 -m ot_scorer.score_fixture_lock \
    --expected "$expected" \
    --generated "$generated" \
    --case-name "$case_name"
}

if [ "$#" -eq 0 ]; then
  check_pair \
    "deletion_case" \
    "tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl" \
    "tmp/synthetic_e2e/deletion_case/candidate_scores.jsonl"
  check_pair \
    "selection_edit_case" \
    "tests/fixtures/synthetic/candidate_scores/valid/selection_edit_candidate_scores.jsonl" \
    "tmp/synthetic_e2e/selection_edit_case/candidate_scores.jsonl"
  check_pair \
    "cursor_movement_case" \
    "tests/fixtures/synthetic/candidate_scores/valid/cursor_movement_candidate_scores.jsonl" \
    "tmp/synthetic_e2e/cursor_movement_case/candidate_scores.jsonl"
  echo "no_config_scoring_fixture_lock: ok"
  echo "cases_checked=3"
  echo "content_suppressed=true"
  exit 0
fi

expected=$1
generated=${2:-tmp/synthetic_e2e/deletion_case/candidate_scores.jsonl}
check_pair "custom" "$expected" "$generated"
