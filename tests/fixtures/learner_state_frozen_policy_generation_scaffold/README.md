# Frozen Policy Generation Scaffold Fixtures

This fixture root contains synthetic-only metadata fixtures for a future
frozen policy generation scaffold.

The fixtures are for scaffold API and CLI behavior. They are separate from
`tests/fixtures/learner_state_frozen_policy_generation/`, which exercises the
generation validation bridge contract.

Each fixture case contains:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_scaffold_result.json`

Valid cases:

- `valid/minimal_fixed_threshold_dry_run`
- `valid/minimal_fixed_abstention_rate_dry_run`
- `valid/validation_nll_temperature_metadata_only_dry_run`

Invalid cases:

- `invalid/missing_validation_split`
- `invalid/test_temperature_tuning`
- `invalid/test_threshold_tuning`
- `invalid/raw_rows_carryover`
- `invalid/logits_dump_carryover`
- `invalid/generated_artifact_body_leakage`
- `invalid/private_path_output`
- `invalid/scoring_feedback_violation`

Future invalid cases not yet implemented:

- `missing_request`
- `malformed_request`
- `missing_pointer`
- `malformed_pointer`
- `unvalidated_input`
- `selective_prediction_validator_failure`
- `frozen_policy_validator_failure`
- `performance_claim_generation`
- `body_dump_requested`
- `real_data_path`
- `participant_data_path`
- `manual_output_path`
- `no_oracle_violation`

All files are metadata-only. They do not contain raw rows, logits/probability
dumps, label bodies, split bodies, calibration policy bodies, generated policy
artifact bodies, private paths, raw learner text, or real participant data.

Passing these fixtures in a future scaffold does not prove generator quality,
model performance, calibration quality, real-data readiness, or production
readiness.
