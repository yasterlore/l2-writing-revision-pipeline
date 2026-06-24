# Learner-State Frozen Policy Generation Artifact Writer Fixtures

This fixture root contains synthetic-only, metadata-only fixture contracts for
the future frozen policy generation artifact writer.

The fixtures are contract data only. They do not implement the artifact writer,
do not implement a validator, do not generate artifact bodies, do not generate
generated policy bodies, do not generate manifest bodies, and do not write
artifact or manifest files.

## Fixture Root

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`

## Total Cases

- total cases: 17
- valid cases: 3
- invalid cases: 14
- JSON files: 51

## File Layout

Each case directory contains:

- `artifact_writer_request.json`
- `generator_result_pointer.json`
- `expected_artifact_writer_result.json`

## Valid Cases

- `valid/minimal_metadata_only_artifact_plan`
- `valid/metadata_manifest_summary_only`
- `valid/synthetic_generator_result_reference`

Valid cases expect `writer_status=pass`, no reason codes, no failed checks, no
artifact body, no generated policy body, no manifest body, and no file writing.

## Invalid Cases

- `invalid/generated_policy_body_leakage`
- `invalid/generated_artifact_body_leakage`
- `invalid/manifest_body_leakage`
- `invalid/raw_rows_carryover`
- `invalid/logits_dump_carryover`
- `invalid/private_path_output`
- `invalid/artifact_file_writing_not_allowed`
- `invalid/manifest_file_writing_not_allowed`
- `invalid/non_synthetic_input`
- `invalid/no_oracle_violation`
- `invalid/scoring_feedback_violation`
- `invalid/performance_claim_in_artifact`
- `invalid/missing_required_field`
- `invalid/unknown_schema_version`

Invalid cases use minimal safe marker fields only. They do not include body
payloads, raw rows, logits, probabilities, private paths, raw learner text, or
real participant data.

## Safety Policy

These fixtures must remain:

- synthetic-only
- metadata-only
- body-free
- no-oracle
- free of raw rows
- free of logits or probability dumps
- free of private paths
- free of raw learner text
- free of performance metric bodies

Expected result files must also remain body-free. They may contain only safe
metadata, reason codes, flags, and count-only summaries.

## Future Validator Note

A future artifact writer fixture validator should check case discovery,
required files, JSON parseability, schema versions, expected reason-code
alignment, forbidden marker handling, and safe summary metadata. It should not
execute an artifact writer unless a later design explicitly adds that behavior.

The validator design is tracked in:

- `docs/frozen_policy_generation_artifact_writer_fixture_validator_design.md`

That design keeps validation metadata-only. It checks the fixture contract,
safe marker policy, flags, count-only summaries, and expected result metadata
without generating artifact bodies, generated policy bodies, manifest bodies,
or writing artifact or manifest files.

Step304 implements the metadata-only fixture validator in:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

The validator checks this fixture contract only. It does not execute an
artifact writer, expose a CLI, add a Makefile target, integrate release-quality,
generate artifact bodies, generate generated policy bodies, generate manifest
bodies, or write artifact/manifest files.

Step305 designs the future validator CLI in:

`docs/frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md`

That design keeps the CLI metadata-only. It covers root mode, case mode, safe
human output, safe JSON output, exit codes, and future Makefile staging without
executing an artifact writer or writing artifact/manifest files.

Step306 implements that safe validator CLI in:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

The CLI still checks fixture contracts only. It does not execute an artifact
writer, add a Makefile target, integrate release-quality, generate artifact
bodies, generate generated policy bodies, generate manifest bodies, or write
artifact/manifest files.

Step307 designs a future standalone Makefile target for running that CLI over
this fixture root:

`docs/frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md`

That design remains docs-only. It does not add a Makefile target, integrate
release-quality, execute an artifact writer, generate artifact bodies,
generate generated policy bodies, generate manifest bodies, or write
artifact/manifest files.

Step308 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

The target runs the metadata-only validator CLI over this fixture root. It does
not execute an artifact writer, integrate release-quality, generate artifact
bodies, generate generated policy bodies, generate manifest bodies, or write
artifact/manifest files.

Step309 designs future release-quality wrapper placement for this standalone
target in:

`docs/frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md`

That design remains docs-only. It does not change fixture JSON, release-quality
wrapper scripts, workflow YAML, Makefile behavior, Python code, Python tests,
execute an artifact writer, generate artifact bodies, generate generated
policy bodies, generate manifest bodies, or write artifact/manifest files.

Step310 adds the standalone Makefile target to the release-quality wrapper.
The fixture JSON files remain unchanged, and the wrapper still runs only
metadata-only fixture contract validation. It does not execute an artifact
writer, generate artifact bodies, generate generated policy bodies, generate
manifest bodies, or write artifact/manifest files.

## What This Does Not Prove

These fixtures do not prove artifact writer correctness, generated policy
quality, artifact generation correctness, model performance, calibration
quality, real-data readiness, or production readiness.
