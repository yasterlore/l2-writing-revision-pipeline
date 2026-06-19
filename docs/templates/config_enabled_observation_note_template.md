# Config-Enabled Observation Note Template

Use this template for human review of config-enabled synthetic summary outputs.

This note is count-only. Do not paste config JSON bodies, raw JSONL, summary
CSV bodies, candidate score rows, generated report bodies, writing text, or
per-episode details into this file.

For storage and sharing policy, see
[`../observation_note_storage_and_review_workflow.md`](../observation_note_storage_and_review_workflow.md).

This note is not model performance evaluation.

## 1. Review Metadata

- Date:
- Reviewer:
- Git commit hash:
- Command used:
  - `scripts/run_synthetic_e2e_config_summary.sh --weight-config <config.json>`
- Weight config path basename:
- `config_name`:
- `config_schema_version`:
- Synthetic-only confirmation:
  - [ ] Confirmed that only synthetic fixture outputs were reviewed.
  - [ ] Confirmed that only synthetic config fixtures were reviewed.
  - [ ] Confirmed that no real participant data was used.
  - [ ] Confirmed that no `manual_outputs/`, `private_data/`, `real_data/`, or `participant_data/` files were reviewed.

## 2. Files Reviewed

Record paths only. Do not paste file contents.

- Config-enabled summary CSV path:
  - `tmp/synthetic_e2e_config_summary/<safe_config_name>/summary.csv`
- No-config summary CSV path, comparison reference only:
  - `tmp/synthetic_e2e_summary/summary.csv`
- Config-enabled case output directories:
  - `tmp/synthetic_e2e/<case_name>__config_<safe_config_name>/`
- Git ignored output confirmation:
  - [ ] Confirmed generated outputs are under `tmp/`.
  - [ ] Confirmed generated outputs are not staged for Git.

## 3. Safe Count-Only Observations

Record count-only observations. Do not include config bodies, report bodies,
raw rows, or score rows.

- Cases reviewed:
- Cases with `config_summary_status=ok`:
- Cases with `config_summary_status=fail`:
- Cases with `pipeline_status=ok`:
- Cases with `pipeline_status=fail`:
- Total `score_sets_count` pattern:
- Total `candidates_count` pattern:
- Cases with `diagnostic_summary_status=ok`:
- Cases with `diagnostic_summary_status=fail`:
- `diagnostic_total_constraints` pattern:
- `diagnostic_descriptive_constraint_count` pattern:
- `diagnostic_blocking_constraint_count` pattern:
- `diagnostic_safety_constraint_count` pattern:
- `diagnostic_local_pattern_constraint_count` pattern:
- `diagnostic_linguistic_placeholder_constraint_count` pattern:
- `diagnostic_non_leaky_linguistic_constraint_count` pattern:
- Ranking diff category counts, if generated separately and count-only:

## 4. Config Metadata Observations

Record metadata only. Do not paste the config body.

- `config_name`:
- `config_schema_version`:
- `weight_config_path_basename`:
- Active weights count, if available from safe validation summary:
- Config validation status, if checked separately:
- Count-only config notes:

## 5. Per-Case Observation

Copy this section once per synthetic case. Keep notes count-only.

### Case: `<case_name>`

- `config_summary_status`:
- `pipeline_status`:
- Output directory basename only:
- `score_sets_count`:
- `candidates_count`:
- `diagnostic_summary_status`:
- `diagnostic_total_constraints`:
- `diagnostic_descriptive_constraint_count`:
- `diagnostic_blocking_constraint_count`:
- `diagnostic_safety_constraint_count`:
- `diagnostic_local_pattern_constraint_count`:
- `diagnostic_linguistic_placeholder_constraint_count`:
- `diagnostic_non_leaky_linguistic_constraint_count`:
- Safety or blocking count unexpected:
  - yes / no / unclear
- Count-only notes:
- Follow-up classification:
  - config wiring issue / summary separation issue / diagnostic emission issue / config validation issue / documentation issue / fixture coverage issue / defer to future design / no action

## 6. Do Not Record

Do not record any of the following:

- config JSON body
- raw JSONL body
- summary CSV body
- candidate score rows
- raw `local_context_before`
- candidate descriptions
- `proposed_edit`
- expected action details
- evaluation report body
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher or human correction
- real participant identifiers
- private/manual/real paths
- per-episode text details
- diagnostic summary JSON body

## 7. Interpretation Guardrails

This note is not:

- model performance
- accuracy
- F1
- calibration
- grammatical correctness
- learner-state quality
- real-data readiness
- publication-level evidence
- ranking quality proof

Do not change scoring weights, scoring formula, tie-break policy, candidate
ranking, config policy, or candidate generation based on this note alone.

Expected actions are evaluation-only. Do not use expected action details as
feedback for config design, scoring, diagnostics, or ranking.

## 8. Follow-Up Classification

Choose one or more:

- [ ] Config wiring issue
- [ ] Summary separation issue
- [ ] Diagnostic emission issue
- [ ] Config validation issue
- [ ] Documentation issue
- [ ] Fixture coverage issue
- [ ] Defer to future design
- [ ] No action

Short count-only rationale:

## 9. Final Decision

Choose one:

- [ ] Proceed
- [ ] Revise config-enabled summary
- [ ] Revise docs
- [ ] Add synthetic fixture
- [ ] Revise config validation
- [ ] Stop and investigate

Decision notes, count-only only:

## 10. Privacy and No-Oracle Confirmation

- [ ] No config JSON body was recorded.
- [ ] No raw writing text was recorded.
- [ ] No JSONL body was recorded.
- [ ] No summary CSV body was pasted.
- [ ] No candidate score rows were pasted.
- [ ] No diagnostic summary body was pasted.
- [ ] No evaluation report body was pasted.
- [ ] No final text, observed-after text, gold label, or teacher correction was used.
- [ ] No expected action was used as scoring or config feedback.
- [ ] No real participant data was used.
