# Frozen Policy Generation Artifact Body Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle contract
fixtures for future frozen policy generation artifact body generation.

These fixtures do not implement artifact body generation, do not implement a
validator, do not write artifact files, do not write manifest files, do not
generate manifest bodies, do not compute metrics, and do not prove real-data
or production readiness.

## Fixture Purpose

The fixtures define the future artifact body generation boundary before any
body generator is implemented. They describe safe valid metadata-only body
states and fail-closed invalid states using safe labels, booleans, counts,
reason codes, and schema names.

## Synthetic-Only / Metadata-Only / No-Oracle Boundary

The fixtures use only synthetic safe labels. They must not contain real
participant data, raw learner text, raw rows, logits, probabilities, private
paths, request bodies, pointer bodies, expected result bodies, generated
policy bodies, artifact body payloads, manifest bodies, or performance metric
bodies.

## File Layout

Each case contains:

- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `expected_artifact_body_result.json`

The files are fixture contract metadata only. This README intentionally does
not include JSON body examples.

## Valid Cases

- `valid/minimal_suppressed_metadata_only_body`
- `valid/safe_metadata_body_summary`
- `valid/safe_reason_code_body_summary`
- `valid/safe_validation_reference_body_summary`

Valid cases expect `validation_status=pass`, no reason codes, no failed
checks, safe metadata-only output, no raw rows, no logits, no private paths,
no performance claims, no request/pointer/expected bodies, no manifest body,
and no artifact or manifest file writing.

## Invalid Cases

- `invalid/raw_learner_text_in_artifact_body`
- `invalid/raw_rows_in_artifact_body`
- `invalid/logits_dump_in_artifact_body`
- `invalid/private_path_in_artifact_body`
- `invalid/performance_claim_in_artifact_body`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/expected_result_body_leakage`
- `invalid/generated_policy_body_leakage`
- `invalid/manifest_body_leakage`
- `invalid/unsafe_artifact_body_schema`
- `invalid/missing_synthetic_notice`
- `invalid/missing_no_oracle_notice`
- `invalid/unknown_artifact_body_schema_version`

Invalid cases expect `validation_status=fail`, `body_status=fail_closed`, one
safe reason code, one failed check, body output suppressed, and no artifact or
manifest file writing.

## Safe Marker Policy

Invalid fixtures use safe marker booleans to indicate simulated unsafe
conditions. The unsafe payload itself must not appear in the fixture.

Allowed marker examples include:

- `raw_learner_text_marker_present`
- `raw_rows_marker_present`
- `logits_dump_marker_present`
- `private_path_marker_present`
- `performance_claim_marker_present`
- `request_body_marker_present`
- `pointer_body_marker_present`
- `expected_result_body_marker_present`
- `generated_policy_body_marker_present`
- `manifest_body_marker_present`
- `unsafe_schema_marker_present`
- `missing_synthetic_notice_marker_present`
- `missing_no_oracle_notice_marker_present`
- `unknown_schema_version_marker_present`

## Forbidden Payload Policy

The fixture root must not contain actual raw learner text, actual rows, actual
logits, actual probabilities, actual private paths, actual request bodies,
actual pointer bodies, actual expected result bodies, actual generated policy
bodies, actual artifact body payloads, actual manifest bodies, GitHub raw
logs, full job output, or performance metric bodies.

## Expected Aggregate Counts

- valid_cases: 4
- invalid_cases: 14
- total_cases: 18
- expected matched_cases: 18
- expected mismatched_cases: 0
- expected input_error_cases: 0
- expected JSON files: 54

## What This Does Not Test

These fixtures do not test artifact body generation correctness, artifact
writer implementation quality, manifest writer behavior, file writing,
generated policy quality, calibration quality, model performance, real-data
readiness, or production readiness.

## Future Validator Plan

A future validator should discover the 18 cases, check the three required
files per case, parse JSON, validate schema versions, check required fields,
scan safe marker flags, compare expected metadata results, scan for forbidden
body leakage, and emit a deterministic metadata-only aggregate summary.

The validator should not output request bodies, pointer bodies, expected
result bodies, artifact bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

The future validator design is documented in:

`docs/frozen_policy_generation_artifact_body_fixture_validator_design.md`

That design is docs-only. It does not implement validator code, validator
CLI, Makefile targets, release-quality integration, artifact body generation,
file writing, metrics, real-data use, or production readiness claims.

## Validator Implementation

Step326 implements the metadata-only fixture validator in:

`python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py`

The validator checks this fixture root without generating artifact bodies,
writing artifact files, writing manifest files, changing fixture JSON,
computing metrics, using real data, or claiming production readiness.
It emits safe metadata, counts, reason code names, schema names, and flags
only.

## Future Validator CLI Design

Step327 designs the future CLI for safely running the validator from a
terminal:

`docs/frozen_policy_generation_artifact_body_fixture_validator_cli_design.md`

That design does not implement CLI code, Makefile targets, release-quality
integration, artifact body generation, file writing, metrics, real-data use,
or production readiness claims. Future CLI output must remain metadata-only
and must not print fixture bodies or artifact body payloads.

## Validator CLI Implementation

Step328 implements the validator CLI in:

`python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py`

The CLI validates this fixture root through the existing validator API and
prints safe metadata-only summaries. It does not add Makefile targets,
release-quality integration, workflow changes, fixture JSON changes, artifact
body generation, file writing, metrics, real-data use, or production
readiness claims.

## Future Validator Makefile Target Design

Step329 designs the future standalone Makefile target for this validator CLI:

`docs/frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md`

That design keeps the target synthetic-only, metadata-only, and no-oracle. It
does not implement the Makefile target, integrate release-quality, change
workflow YAML, change Python code or tests, change fixture JSON, implement
artifact body generation, write files, compute metrics, use real data, or
claim production readiness.

## Validator Makefile Target Implementation

Step330 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The target runs the existing validator CLI against this fixture root and
prints safe metadata-only output. It does not integrate release-quality,
change workflow YAML, change Python code or tests, change fixture JSON,
implement artifact body generation, write files, compute metrics, use real
data, or claim production readiness.

## Future Release-Quality Integration Design

Step331 designs future release-quality integration for the standalone target:

`docs/frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md`

That design does not change the release-quality wrapper, workflow YAML,
Makefile, Python code or tests, fixture JSON, implement artifact body
generation, write files, compute metrics, use real data, or claim production
readiness.

## Release-Quality Wrapper Integration

Step332 integrates the standalone artifact body fixture validator target into
the release-quality wrapper:

`make check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The wrapper now checks this synthetic-only, metadata-only, no-oracle fixture
boundary after artifact writer runtime smoke and before config/scoring smoke
checks. This does not change fixture JSON, generate artifact bodies, generate
policy bodies, generate manifest bodies, write files, compute metrics, use
real data, or claim production readiness.

## Future Remote Status Marker Workflow

Step333 designs the future public-safe remote/manual Release Quality run
record workflow for this fixture validation:

`docs/frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md`

The future marker path is expected to be:

`docs/status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md`

## Remote Status Marker

Step334 creates the public-safe remote/manual Release Quality status marker:

`docs/status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md`

The marker uses pass-only and count-only metadata and does not copy fixture
bodies, artifact body payloads, raw logs, raw rows, logits, private paths, raw
learner text, real participant data, or performance metric bodies.

## Artifact Body Generation Implementation

Step335 adds a safe metadata-only artifact body generation API. These fixtures
remain unchanged and continue to define the validation boundary for generated
body safety. The implementation does not write artifact files, generate
manifest bodies, write manifests, change release-quality, use real data,
compute metrics, or claim production readiness.

## Future Artifact Body Generation CLI Design

Step336 designs a future CLI for calling the artifact body generation API:

`docs/frozen_policy_generation_artifact_body_generation_cli_design.md`

The CLI design keeps stdout and stderr body-free and summary-only. It does not
implement the CLI, modify fixture JSON, write artifact files, generate
manifest bodies, change release-quality, compute metrics, use real data, or
claim production readiness.

## Artifact Body Generation CLI Implementation

Step337 implements the separate artifact body generation CLI. These fixture
JSON files remain unchanged. The CLI can consume synthetic request/pointer
metadata and emit only body-free safe summaries in human or JSON form. It does
not print artifact body payloads, write artifact files, generate manifest
bodies, change release-quality, compute metrics, use real data, or claim
production readiness.

## Future Artifact Body Generation Makefile Target Design

Step338 designs a future standalone Makefile target for the generation CLI:

`docs/frozen_policy_generation_artifact_body_generation_makefile_target_design.md`

The design keeps the fixture JSON files unchanged and recommends an initial
default suppressed-mode smoke. It does not implement the Makefile target,
change release-quality, write artifact files, generate manifest bodies,
compute metrics, use real data, or claim production readiness.

## Artifact Body Generation Makefile Target Implementation

Step339 implements the standalone default suppressed-mode Makefile target for
the generation CLI:

`check-learner-state-frozen-policy-generation-artifact-body-generation`

The target consumes the existing valid synthetic request/pointer metadata
from this fixture root and emits only a body-free safe summary. Fixture JSON
files remain unchanged. The target is not added to release-quality in this
step, does not add a safe-metadata target, does not write artifact files, does
not generate manifest bodies, does not use real data, and does not compute
metrics.

## Future Artifact Body Generation Release-Quality Integration

Step340 designs future release-quality integration for the standalone artifact
body generation target:

`docs/frozen_policy_generation_artifact_body_generation_release_quality_integration_design.md`

The design keeps this fixture root unchanged. It proposes running fixture
validation first and then the default suppressed-mode generation CLI smoke in
a later wrapper step. It does not change fixture JSON, does not add a
safe-metadata target, does not write artifact files, does not generate
manifest bodies, does not use real data, and does not compute metrics.

## Artifact Body Generation Release-Quality Wrapper Integration

Step341 adds the standalone artifact body generation CLI smoke to the
release-quality wrapper after artifact body fixture validation. The wrapper
uses the existing default suppressed-mode target and this fixture root remains
unchanged.

The integration does not add a safe-metadata target, does not modify fixture
JSON, does not write artifact files, does not generate manifest bodies, does
not use real data, and does not compute metrics.

## Future Artifact Body Generation Remote Status Marker Workflow

Step342 designs how a future remote/manual Release Quality run should be
recorded after the artifact body generation CLI smoke is included in the
wrapper:

`docs/frozen_policy_generation_artifact_body_generation_release_quality_remote_run_record_workflow.md`

The future marker path is expected to be:

`docs/status/learner_state_frozen_policy_generation_artifact_body_generation_release_quality_remote_run_status.md`

This is separate from the artifact body fixture validation status marker. It
should record only public-safe pass-only and count-only metadata for the
default suppressed-mode generation smoke. It must not copy fixture bodies,
request bodies, pointer bodies, artifact body payloads, manifest bodies, raw
logs, raw rows, logits, private paths, raw learner text, real participant
data, or performance metric bodies.
