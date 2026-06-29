# Frozen Policy Generation Artifact Writer CLI Integration Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle fixture
contracts for future artifact writer CLI integration.

The fixtures cover only the first integration boundary:

- generator scaffold CLI -> artifact writer CLI

They do not implement the integration runtime, execute artifact body
generation, execute the manifest writer, generate manifest bodies, write files,
or claim production readiness.

## Fixture Root

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/`

## Scope

- artifact writer CLI integration fixture contract only
- generator scaffold to artifact writer boundary only
- no artifact body generation CLI integration
- no manifest writer integration
- no manifest body generation
- no file writing
- body-free public summaries only
- `release_quality_ready=false`

## Case Counts

- total cases: 28
- valid cases: 6
- invalid cases: 22
- JSON files per case: 6
- total JSON case files: 168

## File Contract

Each case directory contains exactly these files:

- `case_metadata.json`
- `generator_request.json`
- `generator_input_fixture_pointer.json`
- `artifact_writer_request.json`
- `generator_result_pointer.json`
- `expected_artifact_writer_cli_integration_result.json`

All files are metadata-only. They may include safe ids, schema/version names,
reason codes, counters, and boolean safety flags. They must not include raw
body payloads, raw rows, logits/probabilities, private paths, absolute local or
temporary paths, raw learner text, real participant data, or performance metric
bodies.

## Valid Cases

- `valid/minimal_generator_to_artifact_writer_metadata_only`
- `valid/generator_with_validation_references_metadata_only`
- `valid/generator_with_release_quality_reference_metadata_only`
- `valid/artifact_writer_preserves_safe_ids_metadata_only`
- `valid/no_file_writing_default_metadata_only`
- `valid/body_suppressed_metadata_only`

Valid cases expect `integration_status=pass`, generator scaffold execution,
artifact writer execution, no artifact body generation, no manifest writer
execution, no file writing, and no body output.

## Invalid Cases

- `invalid/missing_generator_request`
- `invalid/missing_generator_input_pointer`
- `invalid/missing_artifact_writer_request`
- `invalid/missing_generator_result_pointer`
- `invalid/malformed_generator_result_pointer`
- `invalid/unknown_generator_result_schema`
- `invalid/unvalidated_generator_result`
- `invalid/generated_policy_body_leakage`
- `invalid/artifact_body_payload_leakage`
- `invalid/manifest_body_leakage`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/raw_rows_leakage`
- `invalid/logits_dump_leakage`
- `invalid/private_path_leakage`
- `invalid/absolute_path_leakage`
- `invalid/raw_learner_text_leakage`
- `invalid/performance_claim_in_artifact`
- `invalid/non_synthetic_input`
- `invalid/no_oracle_violation`
- `invalid/unsupported_file_writing_mode`
- `invalid/unsupported_artifact_body_generation_integration`

Invalid cases use controlled safe marker fields and reason codes only. They do
not include real body content, raw learner text, private paths, absolute paths,
real participant data, or metric bodies.

## Forbidden Content Policy

These fixtures must not contain:

- raw learner text
- raw rows
- logits or probability dumps
- generated policy body payloads
- artifact body payloads
- manifest bodies or manifest JSON bodies
- request, pointer, or expected-result body payloads
- private paths
- absolute local or temporary paths
- performance metric bodies
- real participant data
- final corrected text, observed-after text, gold labels, or scoring feedback

Controlled reason-code strings and safe boolean marker fields may appear in
invalid cases so a future validator can detect boundary failures without
copying unsafe content.

## No-Oracle Policy

The fixture root is no-oracle. It must not contain future information,
observed-after text, final corrected text, gold labels, post-hoc annotations,
test-set tuning payloads, generated body leakage, or scoring feedback payloads.

## File-Writing Policy

No case represents actual file writing. Expected results keep:

- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`

Any future file-writing integration must be a separate opt-in design.

## Relation To Artifact Body Generation

Artifact body generation is not part of this fixture root. The
`unsupported_artifact_body_generation_integration` case documents that boundary
without executing artifact body generation or including artifact body payloads.

## Relation To Manifest Writer

Manifest writer integration is not part of this fixture root. Expected results
keep `manifest_writer_executed=false` and `manifest_file_written=false`.
Manifest writer chaining remains separate future work.

## Relation To Future Validator

A future validator should check case discovery, required files, JSON parsing,
schema versions, case ids, expected statuses, reason code alignment, safety
flags, controlled invalid markers, file-writing suppression, body suppression,
and no-oracle metadata. The validator should not implement the integration
runtime.

Step469 designs that future validator in:

`docs/frozen_policy_generation_artifact_writer_cli_integration_fixture_validator_design.md`

The design remains docs-only. It does not implement a validator, add Python
tests, change fixture JSON, add a Makefile target, integrate release-quality,
change workflow YAML, implement artifact writer CLI integration runtime,
connect artifact body generation CLI, connect manifest writer runtime, use
real data, compute metrics, or claim production readiness.

Step470 implements that static validator in:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`

The validator checks this fixture root only and emits body-free summaries. It
does not execute artifact writer CLI integration runtime, connect artifact
body generation CLI, connect manifest writer runtime, write files, change
fixture JSON, add a Makefile target, integrate release-quality, use real data,
compute metrics, or claim production readiness.

Step471 designs the future standalone Makefile target for running that
validator CLI:

`docs/frozen_policy_generation_artifact_writer_cli_integration_fixture_validator_makefile_target_design.md`

The proposed target is
`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`.
Step471 does not implement the target, change this fixture root, integrate
release-quality, execute runtime integration, use real data, compute metrics,
or claim production readiness.

Step472 implements that standalone Makefile target. It runs the Step470
validator CLI against this fixture root and emits a body-free count-only
summary. Step472 does not change fixture JSON, add release-quality integration,
execute runtime integration, connect artifact body generation CLI, connect
manifest writer runtime, use real data, compute metrics, or claim production
readiness.

Step473 designs future release-quality wrapper integration for that standalone
target:

`docs/frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_integration_design.md`

The design keeps this fixture validator separate from artifact body generation
and manifest writer checks. Step473 does not change the wrapper, workflow,
Makefile, Python code/tests, fixture JSON, runtime integration, real-data use,
metrics, or production readiness claims.

Step474 adds the standalone validator target to the release-quality wrapper
after artifact writer fixture validation and artifact writer runtime smoke, and
before artifact body fixture validation. The wrapper integration keeps this
fixture root as metadata-only contract input and does not change fixture JSON,
execute runtime integration, connect artifact body generation CLI, connect
manifest writer runtime, use real data, compute metrics, or claim production
readiness.

Step475 designs the future public-safe remote/manual Release Quality recording
workflow for that wrapper check. The future status marker path is planned as
`docs/status/learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_remote_run_status.md`,
but the marker is not yet created. The planned marker must not copy fixture
JSON bodies, request/pointer/expected bodies, artifact body payloads, manifest
bodies, generated policy bodies, raw logs, private paths, absolute paths, raw
learner text, real data, metrics, or production readiness claims.

Step476 creates that public-safe status marker after a successful remote/manual
Release Quality run. The marker records only wrapper inclusion and count-only
static fixture validation success; it does not change fixture JSON, execute
runtime integration, connect artifact body generation CLI, connect manifest
writer runtime, use real data, compute metrics, or claim production readiness.

## What This Fixture Root Does Not Prove

This fixture root does not prove artifact writer CLI integration correctness,
artifact body generation integration, manifest writer integration, manifest
body generation, runtime file output readiness, model performance, real-data
readiness, or production readiness.

## Release Quality Note

`release_quality_ready=false` remains part of the fixture contract. Release
quality integration is present as a wrapper check for the standalone static
fixture validator, but this does not make the fixture root production-ready or
real-data-ready.
