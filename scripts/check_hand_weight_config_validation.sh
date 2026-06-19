#!/usr/bin/env sh
set -eu

VALID_DIR="tests/fixtures/synthetic/hand_weight_configs/valid"
INVALID_DIR="tests/fixtures/synthetic/hand_weight_configs/invalid"

echo "hand_weight_config_validation_check: start"
echo "content_suppressed: true"

valid_count=0
for config in "${VALID_DIR}"/*.json; do
  valid_count=$((valid_count + 1))
  PYTHONPATH=python python3 -m ot_scorer.validate_weight_config --config "${config}"
done

invalid_count=0
for config in "${INVALID_DIR}"/*.json; do
  invalid_count=$((invalid_count + 1))
  if PYTHONPATH=python python3 -m ot_scorer.validate_weight_config --config "${config}" >/tmp/hand_weight_config_invalid_check.out 2>&1; then
    echo "invalid_config_expected_failure: fail"
    echo "config_file: ${config}"
    echo "content_suppressed: true"
    exit 1
  fi
  if grep -q 'validation_status=fail' /tmp/hand_weight_config_invalid_check.out; then
    echo "invalid_config_expected_failure: ok"
    echo "config_file: ${config}"
  else
    echo "invalid_config_expected_failure: fail"
    echo "config_file: ${config}"
    echo "content_suppressed: true"
    exit 1
  fi
done

rm -f /tmp/hand_weight_config_invalid_check.out

echo "hand_weight_config_validation_check: ok"
echo "valid_configs_checked: ${valid_count}"
echo "invalid_configs_checked: ${invalid_count}"
echo "scorer_connected: false"
echo "score_output_generated: false"
echo "content_suppressed: true"
