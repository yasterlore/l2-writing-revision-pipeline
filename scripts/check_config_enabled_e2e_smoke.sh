#!/usr/bin/env sh
set -eu

RAW_EVENTS="tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl"
EXPECTED_ACTIONS="tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl"
DEFAULT_LIKE_CONFIG="tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json"
INTENTIONAL_CONFIG="tests/fixtures/synthetic/hand_weight_configs/valid/intentional_leakage_tiny_weight_config.json"
INVALID_CONFIG="tests/fixtures/synthetic/hand_weight_configs/invalid/expected_action_tuning_policy_config.json"

NO_CONFIG_CASE="deletion_case_config_smoke_no_config"
DEFAULT_LIKE_CASE="deletion_case_config_smoke_default_like"
INTENTIONAL_CASE="deletion_case_config_smoke_intentional"
INVALID_CASE="deletion_case_config_smoke_invalid"
UNSAFE_CASE="deletion_case_config_smoke_unsafe"

NO_CONFIG_DIR="tmp/synthetic_e2e/${NO_CONFIG_CASE}"
DEFAULT_LIKE_DIR="tmp/synthetic_e2e/${DEFAULT_LIKE_CASE}"
INTENTIONAL_DIR="tmp/synthetic_e2e/${INTENTIONAL_CASE}"
INVALID_DIR="tmp/synthetic_e2e/${INVALID_CASE}"
UNSAFE_DIR="tmp/synthetic_e2e/${UNSAFE_CASE}"

safe_cksum() {
  cksum "$1" | awk '{print $1 ":" $2}'
}

require_file() {
  if [ ! -s "$1" ]; then
    echo "config_enabled_e2e_smoke: fail"
    echo "reason=missing_output"
    echo "path=$1"
    echo "content_suppressed=true"
    exit 1
  fi
}

expect_failure() {
  label=$1
  shift
  if "$@" >/tmp/config_enabled_e2e_expected_failure.out 2>&1; then
    echo "config_enabled_e2e_smoke: fail"
    echo "reason=${label}_unexpected_success"
    echo "content_suppressed=true"
    exit 1
  fi
  echo "${label}: expected_failure"
  echo "content_suppressed=true"
}

case "${NO_CONFIG_DIR} ${DEFAULT_LIKE_DIR} ${INTENTIONAL_DIR}" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "config_enabled_e2e_smoke: fail"
    echo "reason=unsafe_output_path"
    echo "content_suppressed=true"
    exit 2
    ;;
esac

echo "config_enabled_e2e_smoke: start"
echo "performance_evaluation=false"
echo "content_suppressed=true"

scripts/run_synthetic_e2e_pipeline.sh \
  "${RAW_EVENTS}" \
  "${NO_CONFIG_CASE}" \
  "${EXPECTED_ACTIONS}"
require_file "${NO_CONFIG_DIR}/candidate_scores.jsonl"
no_config_checksum_before=$(safe_cksum "${NO_CONFIG_DIR}/candidate_scores.jsonl")

scripts/run_synthetic_e2e_pipeline.sh \
  "${RAW_EVENTS}" \
  "${DEFAULT_LIKE_CASE}" \
  "${EXPECTED_ACTIONS}" \
  --weight-config "${DEFAULT_LIKE_CONFIG}"
require_file "${DEFAULT_LIKE_DIR}/candidate_scores.jsonl"

scripts/run_synthetic_e2e_pipeline.sh \
  "${RAW_EVENTS}" \
  "${INTENTIONAL_CASE}" \
  "${EXPECTED_ACTIONS}" \
  --weight-config "${INTENTIONAL_CONFIG}"
require_file "${INTENTIONAL_DIR}/candidate_scores.jsonl"

no_config_checksum_after=$(safe_cksum "${NO_CONFIG_DIR}/candidate_scores.jsonl")
if [ "${no_config_checksum_before}" != "${no_config_checksum_after}" ]; then
  echo "config_enabled_e2e_smoke: fail"
  echo "reason=no_config_output_changed"
  echo "content_suppressed=true"
  exit 1
fi

if [ "${NO_CONFIG_DIR}" = "${DEFAULT_LIKE_DIR}" ] || [ "${NO_CONFIG_DIR}" = "${INTENTIONAL_DIR}" ]; then
  echo "config_enabled_e2e_smoke: fail"
  echo "reason=output_directories_not_distinct"
  echo "content_suppressed=true"
  exit 1
fi

expect_failure "invalid_config" \
  scripts/run_synthetic_e2e_pipeline.sh \
    "${RAW_EVENTS}" \
    "${INVALID_CASE}" \
    "${EXPECTED_ACTIONS}" \
    --weight-config "${INVALID_CONFIG}"

if [ -e "${INVALID_DIR}/candidate_scores.jsonl" ]; then
  echo "config_enabled_e2e_smoke: fail"
  echo "reason=invalid_config_candidate_scores_present"
  echo "content_suppressed=true"
  exit 1
fi

expect_failure "unsafe_config_path" \
  scripts/run_synthetic_e2e_pipeline.sh \
    "${RAW_EVENTS}" \
    "${UNSAFE_CASE}" \
    --weight-config "private_data/synthetic_config.json"

scripts/check_explicit_config_ranking_diff.sh >/dev/null
echo "explicit_config_ranking_diff_smoke: ok"

echo "config_enabled_e2e_smoke: ok"
echo "no_config_case=${NO_CONFIG_CASE}"
echo "default_like_config_case=${DEFAULT_LIKE_CASE}"
echo "intentional_config_case=${INTENTIONAL_CASE}"
echo "outputs_separate=true"
echo "no_config_output_unchanged=true"
echo "invalid_config_fail_closed=true"
echo "unsafe_config_path_fail_closed=true"
echo "summary_collector_connected=false"
echo "performance_evaluation=false"
echo "content_suppressed=true"

rm -f /tmp/config_enabled_e2e_expected_failure.out
