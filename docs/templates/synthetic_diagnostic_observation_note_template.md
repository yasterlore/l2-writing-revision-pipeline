# Synthetic Diagnostic Observation Note Template

Use this template for human review of synthetic diagnostic distribution outputs.

This note is count-only. Do not paste raw JSONL, generated report bodies,
candidate text, writing text, or per-episode text details into this file.

## 1. Review Metadata

- Date:
- Reviewer:
- Git commit hash:
- Command used:
  - `scripts/run_synthetic_e2e_summary.sh`
- Input source:
  - `tests/fixtures/synthetic/raw_events/valid/`
- Synthetic-only confirmation:
  - [ ] Confirmed that only synthetic fixture outputs were reviewed.
  - [ ] Confirmed that no real participant data was used.
  - [ ] Confirmed that no `manual_outputs/`, `private_data/`, `real_data/`, or `participant_data/` files were reviewed.

## 2. Files Reviewed

Record paths only. Do not paste file contents.

- Summary CSV path:
  - `tmp/synthetic_e2e_summary/summary.csv`
- Diagnostic summary JSON paths:
  - `tmp/synthetic_e2e/<case_name>/diagnostic_summary.json`
- Git ignored output confirmation:
  - [ ] Confirmed generated outputs are under `tmp/`.
  - [ ] Confirmed generated outputs are not staged for Git.

## 3. Safe Count-Only Observations

Record count-only observations. Do not include report bodies or raw rows.

- Cases reviewed:
- Cases with `diagnostic_summary_status=ok`:
- Cases with `diagnostic_summary_status=fail`:
- Cases with `diagnostic_summary_status=skipped_missing_constraints`:
- Total constraints pattern:
- Descriptive constraints pattern:
- Blocking constraints pattern:
- Safety constraints pattern:
- Local pattern diagnostic constraints pattern:
- Linguistic placeholder diagnostic constraints pattern:
- Top constraint ID counts, if manually summarized without raw body:

## 4. Per-Case Observation

Copy this section once per synthetic case. Keep notes count-only.

### Case: `<case_name>`

- `diagnostic_summary_status`:
- `diagnostic_total_constraints`:
- `diagnostic_descriptive_constraint_count`:
- `diagnostic_blocking_constraint_count`:
- `diagnostic_safety_constraint_count`:
- `diagnostic_local_pattern_constraint_count`:
- `diagnostic_linguistic_placeholder_constraint_count`:
- Local pattern diagnostic present:
  - yes / no / unclear
- Linguistic placeholder diagnostic present:
  - yes / no / unclear
- Safety or blocking count unexpected:
  - yes / no / unclear
- Count-only notes:
- Follow-up classification:
  - wiring issue / diagnostic emission issue / documentation issue / fixture coverage issue / defer to future design / no action

## 5. Do Not Record

Do not record any of the following:

- raw JSONL body
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
- per-episode text details
- diagnostic summary JSON body
- summary CSV body

## 6. Interpretation Guardrails

This note is not:

- model performance
- accuracy
- F1
- calibration
- grammatical correctness
- learner-state quality
- real-data readiness
- publication-level evidence

Do not change scoring weights, scoring formula, tie-break policy, candidate
ranking, or candidate generation based on this note alone.

Expected actions are evaluation-only. Do not use expected action details as
feedback for scoring, diagnostic design, or ranking.

## 7. Follow-Up Classification

Choose one or more:

- [ ] Wiring issue
- [ ] Diagnostic emission issue
- [ ] Documentation issue
- [ ] Fixture coverage issue
- [ ] Defer to future design
- [ ] No action

Short count-only rationale:

## 8. Final Decision

Choose one:

- [ ] Proceed
- [ ] Revise diagnostics
- [ ] Revise docs
- [ ] Add synthetic fixture
- [ ] Stop and investigate

Decision notes, count-only only:

## 9. Privacy and No-Oracle Confirmation

- [ ] No raw writing text was recorded.
- [ ] No JSONL body was recorded.
- [ ] No diagnostic summary body was pasted.
- [ ] No evaluation report body was pasted.
- [ ] No final text, observed-after text, gold label, or teacher correction was used.
- [ ] No expected action was used as scoring feedback.
- [ ] No real participant data was used.
