#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: scripts/check_no_config_scoring_fixture_lock.sh [expected_candidate_scores.jsonl] [generated_candidate_scores.jsonl]" >&2
  echo "Checks no-config synthetic CandidateScoreSet fixture lock. This is not performance evaluation." >&2
}

if [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

expected=${1:-tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl}
generated=${2:-tmp/synthetic_e2e/deletion_case/candidate_scores.jsonl}

case "$expected" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "lock_status=fail"
    echo "reason=unsafe_path"
    echo "content_suppressed=true"
    exit 2
    ;;
esac

case "$generated" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "lock_status=fail"
    echo "reason=unsafe_path"
    echo "content_suppressed=true"
    exit 2
    ;;
esac

PYTHONPATH=python python3 -m ot_scorer.score_fixture_lock \
  --expected "$expected" \
  --generated "$generated"
