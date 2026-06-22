# Frozen Selective Prediction Policy Fixture Design

This document designs future synthetic fixtures for validating frozen
selective prediction policy artifacts.

It is design documentation only. It does not create fixture files, implement a
frozen policy validator, implement calibration or selective prediction, create
`frozen_selective_prediction_policy.json`, train a learner-state estimator,
compute metrics, change release-quality, change workflows, change Makefile, or
change existing fixtures. It is not a performance evaluation and is not a
real-data readiness claim.

Public documentation must not include frozen policy artifact bodies, raw JSONL
rows, prediction row bodies, label row bodies, calibration policy bodies,
split metadata bodies, logits/probability dumps, generated feature/label/
manifest bodies, raw GitHub Actions logs, raw learner text, private paths, or
real participant data.

## 1. Purpose

The purpose of this document is to design a future synthetic-only fixture root
for frozen selective prediction policy validation.

The design covers:

- fixture root candidates
- valid and invalid fixture case structure
- fixture file set
- expected validation result contract
- failure reason codes
- future validation checks
- relationship to the frozen policy schema, scaffold, and selective prediction
  validator

This document does not create fixture files and does not implement validation
code.

## 2. One-Sentence Fixture Summary

A frozen policy fixture is a synthetic fixture set that pairs a
validation-only frozen policy artifact with an expected validation result so a
future validator can fail closed on test-derived tuning, forbidden body
fields, unsafe paths, malformed schema, and performance-claim leakage without
using real data or exposing raw rows.

## 3. Fixture Root Candidate

Fixture root candidates:

| Candidate | Assessment |
| --- | --- |
| `tests/fixtures/learner_state_frozen_selective_prediction_policy/` | Recommended; names learner-state scope, frozen status, and selective prediction policy clearly |
| `tests/fixtures/frozen_selective_prediction_policy/` | Clear but less connected to learner-state fixture naming |
| `tests/fixtures/learner_state_selective_prediction_policy/` | Too broad; does not emphasize frozen policy artifact validation |
| `tests/fixtures/learner_state_calibration_policy/` | Too narrow and may be confused with existing `calibration_policy.json` fixture inputs |

Recommended root:

- `tests/fixtures/learner_state_frozen_selective_prediction_policy/`

Reason:

- follows learner-state fixture naming
- separates frozen output policy fixtures from selective prediction input
  fixtures
- avoids confusing source `calibration_policy.json` with frozen policy output
- leaves room for artifact validator tests without modifying existing fixture
  roots

This step does not create the directory.

## 4. Fixture Case Structure

Future valid case:

- `valid/minimal_validation_only_policy/`

Future invalid cases:

- `invalid/test_derived_temperature/`
- `invalid/test_derived_threshold/`
- `invalid/missing_schema_version/`
- `invalid/unknown_schema_version/`
- `invalid/raw_rows_in_policy/`
- `invalid/logits_dump_in_policy/`
- `invalid/private_path_in_policy/`
- `invalid/non_numeric_threshold/`
- `invalid/out_of_range_abstention_rate/`
- `invalid/missing_required_field/`
- `invalid/performance_claim_in_policy/`

These cases are representative, not exhaustive. They are designed to cover
the first fail-closed boundary before adding broader fixture variants.

This step does not create any directories.

## 5. Fixture File Set

Each future fixture case should contain:

- `frozen_selective_prediction_policy.json`
- `expected_frozen_policy_validation_result.json`

Optional:

- `README.md`

File roles:

- `frozen_selective_prediction_policy.json` is the synthetic artifact under
  validation
- `expected_frozen_policy_validation_result.json` stores safe metadata about
  the expected pass/fail result
- optional README explains fixture intent without copying artifact bodies

Docs should name files and describe fields, but must not paste full artifact
bodies.

## 6. Valid Fixture Design

Initial valid fixture:

- `valid/minimal_validation_only_policy/`

Requirements:

- known schema version:
  `frozen_selective_prediction_policy_schema_v0_1`
- `synthetic_only` is true
- `content_suppressed` is true
- `no_raw_rows` is true
- `no_oracle_checked` is true
- `test_tuning_forbidden` is true
- `confidence_definition` is `max_softmax_probability`
- temperature source split is `validation` or explicit identity
  `none_identity`
- threshold source split is `validation`
- `allowed_abstention_rate` is numeric and in range
- `split_policy_summary` says test is not used for tuning
- required `safety_review` booleans are true
- no raw prediction rows
- no raw label rows
- no logits/probability dumps
- no label body
- no calibration policy body dump
- no split metadata body dump
- no private paths
- no performance claims
- expected validation status: pass

The valid fixture should be small and synthetic-only. It should prove only
that the artifact shape and safety metadata are acceptable, not that
calibration is good.

## 7. Invalid Fixture Design

Future invalid fixture cases:

| Fixture | Intent | Expected Failure Reason |
| --- | --- | --- |
| `invalid/test_derived_temperature/` | Temperature source or provenance indicates test split use | `test_temperature_tuning` |
| `invalid/test_derived_threshold/` | Threshold source or provenance indicates test split use | `test_threshold_tuning` |
| `invalid/missing_schema_version/` | Artifact omits explicit schema version | `missing_schema_version` |
| `invalid/unknown_schema_version/` | Artifact declares an unsupported schema version | `unknown_schema_version` |
| `invalid/raw_rows_in_policy/` | Artifact embeds prediction or label rows | `raw_rows_in_policy` |
| `invalid/logits_dump_in_policy/` | Artifact embeds logits/probability dumps | `logits_dump_in_policy` |
| `invalid/private_path_in_policy/` | Artifact embeds private or unsafe paths | `unsafe_path` |
| `invalid/non_numeric_threshold/` | Threshold is not numeric | `invalid_threshold` |
| `invalid/out_of_range_abstention_rate/` | Abstention rate is outside the safe numeric range | `invalid_abstention_rate` |
| `invalid/missing_required_field/` | Required schema field is absent | `missing_required_field` |
| `invalid/performance_claim_in_policy/` | Artifact includes final performance claims | `performance_claim_in_policy` |

Invalid fixtures may intentionally include unsafe fields as test targets, but
expected validation output should report only safe reason codes and should not
print field bodies.

## 8. Expected Validation Result Design

Expected result file:

- `expected_frozen_policy_validation_result.json`

Safe metadata fields:

- `validation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_policy_schema_version`
- `expected_policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_checked`

Forbidden expected result content:

- frozen policy body
- raw rows
- logits/probability dumps
- label body
- calibration policy body
- split metadata body
- private paths
- performance metrics
- raw learner text
- expected action body

Valid fixture expected result may omit failure reason or set it to null.
Invalid fixture expected results should name exactly the expected safe failure
reason.

## 9. Failure Reason Code Design

Initial reason code candidates:

| Reason Code | Meaning |
| --- | --- |
| `test_temperature_tuning` | Temperature was selected from or adjusted by test data |
| `test_threshold_tuning` | Threshold was selected from or adjusted by test data |
| `missing_schema_version` | `policy_schema_version` is missing |
| `unknown_schema_version` | `policy_schema_version` is unsupported |
| `raw_rows_in_policy` | Artifact embeds raw prediction or label rows |
| `logits_dump_in_policy` | Artifact embeds logits or probability dumps |
| `unsafe_path` | Artifact contains private or unsafe path values |
| `invalid_threshold` | Threshold is missing, non-numeric, non-finite, or out of confidence range |
| `invalid_abstention_rate` | Abstention rate is missing, non-numeric, non-finite, or out of range |
| `missing_required_field` | Required schema field is absent |
| `performance_claim_in_policy` | Artifact includes final performance claims or metric evidence |
| `malformed_input` | Artifact JSON cannot be parsed |
| `missing_input_file` | Required fixture file is missing |
| `empty_input` | Required artifact file is empty |
| `forbidden_field` | A forbidden field appears outside a more specific category |
| `policy_count_mismatch` | Expected-result counts or status do not match validation output |

Future validator tests should assert these reason codes without printing
artifact bodies.

## 10. Future Validation Checks

A future frozen policy validator should check:

- path safety
- required file presence
- JSON parse
- non-empty artifact input
- known schema version
- required fields
- recursive forbidden field scan
- no private paths
- no raw rows
- no logits/probability dumps
- no label body
- no calibration policy body dump
- no split metadata body dump
- no test-derived temperature
- no test-derived threshold
- numeric ranges for temperature, threshold, and abstention rate
- required safety review booleans
- split policy summary
- expected-result matching

Validation should fail closed. Mismatches should report safe reason codes,
counts, and status only.

## 11. Relation To Frozen Policy Schema Design

The
[frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
defines the artifact fields and safety boundaries.

This fixture design instantiates that schema as future valid and invalid
synthetic cases.

Relationship:

- Step220 defines the schema
- Step221 designs future fixtures for that schema
- future validator checks schema compliance
- fixtures do not compute calibration
- fixtures do not evaluate performance
- fixtures do not use real data

## 12. Relation To Selective Prediction Validator And Scaffold

Relationship:

- selective prediction validator checks prediction / label / split / policy
  fixture inputs
- scaffold will create a frozen policy only after validator pass
- frozen policy fixture validator will check frozen output artifact safety
- future test evaluation will consume only a valid frozen policy
- all of these remain synthetic-only at the current stage

The frozen policy validator should not replace the existing selective
prediction validator. It checks a different boundary: the safety of the frozen
output policy artifact.

## 13. Output Safety

Public docs should describe fields, cases, expected statuses, and reason
codes only.

Do not include:

- full future artifact body
- raw rows
- prediction row body
- label row body
- logits/probability dump
- calibration policy body
- split metadata body
- expected action body
- private paths
- raw learner text
- performance claims
- raw GitHub Actions logs

Fixture validation output should follow the same safe summary posture:
status, reason codes, counts, and safety booleans only.

## 14. Implementation Roadmap

Recommended future order:

1. Step222: create initial frozen policy fixtures. Completed with one valid
   synthetic fixture, eleven intentional invalid fixtures, and safe expected
   validation result metadata under
   `tests/fixtures/learner_state_frozen_selective_prediction_policy/`.
2. Step223: frozen policy validation design.
3. Step224: minimal frozen policy validator implementation. Completed with
   `python/learner_state/frozen_policy_validation.py` and fixture-based tests.
4. Step225: frozen policy validator CLI design. Completed in
   [frozen policy validator CLI design](frozen_policy_validator_cli_design.md).
5. Step226: minimal frozen policy validator CLI implementation. Completed in
   `python/learner_state/frozen_policy_validation.py` with CLI tests.
6. Step227: frozen policy validator Makefile target design. Completed as
   docs-only in
   [frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md).
7. Step228: Makefile target implementation / release-quality integration
   design.
8. Step229: calibration scaffold fixture design.

Keep each step narrow. Do not combine fixture creation, validator
implementation, scaffold implementation, estimator training, metric
computation, and real-data readiness in one step.

## 15. What This Does Not Do

This fixture design does not:

- implement a validator
- implement calibration
- implement selective prediction
- create a frozen policy artifact from model output
- train a learner-state estimator
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- prove performance
- claim real-data readiness

## 16. Beginner Notes

A frozen policy fixture is a small synthetic example of a saved policy. It is
used to test whether a future validator can tell the difference between a safe
policy and an unsafe policy.

Valid fixtures show the shape the project wants to accept. Invalid fixtures
are intentional traps: they contain one kind of problem, such as test-derived
temperature or a logits dump, so the validator can prove it fails closed.

Test-derived temperature and threshold are invalid because test data should be
reserved for final checking after choices are frozen. If the policy is tuned
using test labels, the final test is no longer honest.

Raw rows and logits dumps are forbidden because the frozen policy only needs
to remember the decision and safe provenance. Storing rows or logits in the
policy increases leakage risk and makes public records harder to keep safe.

Fixture validation success is not performance evidence. It only means the
future policy artifact matched the expected schema and safety boundaries.

## 17. Related Documents

- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Milestone 09 selective prediction validation infrastructure recap](milestone_09_selective_prediction_validation_infrastructure_recap.md)
- [Frozen selective prediction policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
