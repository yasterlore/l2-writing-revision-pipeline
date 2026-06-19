#!/usr/bin/env sh
set -eu

CONSTRAINTS="tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl"
DEFAULT_CONFIG="tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json"
INTENTIONAL_CONFIG="tests/fixtures/synthetic/hand_weight_configs/valid/intentional_leakage_tiny_weight_config.json"

NO_CONFIG_OUT="tmp/score_cli_no_config/deletion_candidate_scores.jsonl"
DEFAULT_CONFIG_OUT="tmp/score_cli_with_default_like_config/deletion_candidate_scores.jsonl"

INTENTIONAL_DIR="tmp/explicit_config_ranking_diff"
INTENTIONAL_CONSTRAINTS="${INTENTIONAL_DIR}/deletion_constraint_violations_with_leakage.jsonl"
INTENTIONAL_NO_CONFIG_OUT="${INTENTIONAL_DIR}/no_config_candidate_scores.jsonl"
INTENTIONAL_CONFIG_OUT="${INTENTIONAL_DIR}/intentional_config_candidate_scores.jsonl"

case "${NO_CONFIG_OUT} ${DEFAULT_CONFIG_OUT} ${INTENTIONAL_DIR}" in
  *manual_outputs* | *private_data* | *real_data* | *participant_data* )
    echo "explicit_config_ranking_diff_check: fail"
    echo "reason=unsafe_path"
    echo "content_suppressed=true"
    exit 2
    ;;
esac

mkdir -p "tmp/score_cli_no_config" "tmp/score_cli_with_default_like_config" "${INTENTIONAL_DIR}"

echo "explicit_config_ranking_diff_check: start"
echo "content_suppressed=true"
echo "performance_evaluation=false"

PYTHONPATH=python python3 -m ot_scorer.score \
  --constraints "${CONSTRAINTS}" \
  --output "${NO_CONFIG_OUT}"

PYTHONPATH=python python3 -m ot_scorer.score \
  --constraints "${CONSTRAINTS}" \
  --output "${DEFAULT_CONFIG_OUT}" \
  --weight-config "${DEFAULT_CONFIG}"

PYTHONPATH=python python3 -m ot_scorer.config_ranking_diff \
  --no-config "${NO_CONFIG_OUT}" \
  --config "${DEFAULT_CONFIG_OUT}" \
  --case-name "deletion_case_default_like_config" \
  --expect-zero-diff

PYTHONPATH=python python3 -c 'import json,sys; source,dest=sys.argv[1],sys.argv[2]; rows=[]; changed=False
for line in open(source, encoding="utf-8"):
    if not line.strip():
        continue
    row=json.loads(line)
    for candidate in row["candidate_violations"]:
        for violation in candidate["violations"]:
            if not changed and violation["constraint_id"] == "NO-LEAKAGE-FLAG":
                violation["violation_count"] = 1
                violation["observed"] = True
                changed=True
    rows.append(row)
with open(dest, "w", encoding="utf-8") as handle:
    for row in rows:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
if not changed:
    raise SystemExit(2)' "${CONSTRAINTS}" "${INTENTIONAL_CONSTRAINTS}"

PYTHONPATH=python python3 -m ot_scorer.score \
  --constraints "${INTENTIONAL_CONSTRAINTS}" \
  --output "${INTENTIONAL_NO_CONFIG_OUT}"

PYTHONPATH=python python3 -m ot_scorer.score \
  --constraints "${INTENTIONAL_CONSTRAINTS}" \
  --output "${INTENTIONAL_CONFIG_OUT}" \
  --weight-config "${INTENTIONAL_CONFIG}"

PYTHONPATH=python python3 -m ot_scorer.config_ranking_diff \
  --no-config "${INTENTIONAL_NO_CONFIG_OUT}" \
  --config "${INTENTIONAL_CONFIG_OUT}" \
  --case-name "deletion_case_intentional_config" \
  --expect-weighted-score-diff

echo "explicit_config_ranking_diff_check: ok"
echo "default_like_zero_diff: ok"
echo "intentional_weighted_score_diff: ok"
echo "content_suppressed=true"
