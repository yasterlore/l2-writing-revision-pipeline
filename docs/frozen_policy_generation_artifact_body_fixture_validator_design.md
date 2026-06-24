# Frozen Policy Generation Artifact Body Fixture Validator Design

This document designs a future validator for frozen policy generation artifact
body fixtures. It is docs-only. It does not implement the validator, implement
a validator CLI, implement artifact body generation, write files, evaluate
performance, use real data, or claim real-data or production readiness.

## 1. Purpose

The purpose of this document is to define the validator responsibility,
inputs, outputs, comparison rules, safe marker scan, forbidden payload scan,
aggregate summary, and fail-closed behavior for the artifact body fixture
root.

This is not:

- validator implementation
- validator CLI implementation
- artifact body generation implementation
- generated policy body generation
- manifest body generation
- artifact file writing
- manifest file writing
- performance evaluation
- real-data readiness
- production readiness

## 2. Current State

- Artifact body generation design exists.
- Artifact body fixture design exists.
- Artifact body fixtures exist.
- The fixture root has 18 cases and 54 JSON files.
- Artifact body validator does not exist.
- Artifact body validator CLI does not exist.
- Makefile target does not exist.
- Release-quality integration does not exist.

## 3. Proposed Module

Proposed future module:

```text
python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py
```

This module is not implemented in this step.

## 4. Validator Responsibility

The future validator should:

- discover fixture cases
- ensure required files exist
- parse JSON
- check schema versions
- check required fields
- validate valid and invalid category expectations
- compare actual derived metadata with expected result metadata
- scan safe marker policy
- scan forbidden body and payload leakage
- compute aggregate summary
- print safe metadata-only summary in a future CLI
- never print JSON bodies, artifact body payloads, request bodies, pointer
  bodies, or expected result bodies

## 5. Input Files Per Case

Each case has three files:

- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `expected_artifact_body_result.json`

The validator should treat these as structured metadata inputs. It should not
echo their bodies in stdout, stderr, docs, or error summaries.

## 6. Expected Schema Versions

Expected schema versions:

- request: `learner_state_frozen_policy_generation_artifact_body_request_v0.1`
- writer result pointer:
  `learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1`
- expected result:
  `learner_state_frozen_policy_generation_artifact_body_expected_result_v0.1`
- result: `learner_state_frozen_policy_generation_artifact_body_result_v0.1`
- future validation summary:
  `learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1`

## 7. Proposed Dataclasses

Future dataclass candidates:

- `ArtifactBodyFixtureCase`
- `ArtifactBodyFixtureValidationResult`
- `ArtifactBodyFixtureRootValidationResult`
- `ArtifactBodyFixtureSafetySummary`
- `ArtifactBodyFixtureInputError`
- `ArtifactBodyFixtureComparisonResult`
- `ArtifactBodyForbiddenScanResult`
- `ArtifactBodySafeMarkerScanResult`

These names describe validator structure only. They are not implemented in
this step.

## 8. Proposed APIs

Future API candidates:

- `discover_fixture_cases(root: Path) -> list[ArtifactBodyFixtureCase]`
- `load_artifact_body_request(path: Path) -> dict`
- `load_writer_result_pointer(path: Path) -> dict`
- `load_expected_artifact_body_result(path: Path) -> dict`
- `validate_artifact_body_fixture_case(case: ArtifactBodyFixtureCase) -> ArtifactBodyFixtureValidationResult`
- `validate_artifact_body_fixture_root(root: Path) -> ArtifactBodyFixtureRootValidationResult`
- `compare_expected_result(actual: dict, expected: dict) -> ArtifactBodyFixtureComparisonResult`
- `scan_safe_markers(payload: Mapping[str, Any]) -> ArtifactBodySafeMarkerScanResult`
- `scan_forbidden_payload(payload: Mapping[str, Any]) -> ArtifactBodyForbiddenScanResult`
- `summarize_fixture_root(result: ArtifactBodyFixtureRootValidationResult) -> dict`

The APIs should return safe metadata summaries and should not return raw
payload bodies.

## 9. Case Discovery Behavior

Discovery rules:

- root contains `valid/` and `invalid/`
- each case directory must contain exactly the required files
- `case_id` derives from category and relative path
- ordering is deterministic and sorted
- missing required file becomes `input_error`
- malformed JSON becomes `input_error`
- extra JSON file fails closed with reason `unexpected_fixture_file`

The future validator should not scan outside the fixture root.

## 10. Valid Behavior

A valid case should match:

- validation_status=`pass`
- body_status is `suppressed_metadata_only` or `generated_safe_metadata_body`
- reason_codes=[]
- failed_checks=[]
- all safety flags true
- all forbidden counts are zero
- body output is safe or suppressed
- artifact file writing is false
- manifest file writing is false
- no forbidden marker is present except explicitly false safe marker fields

The validator should compare only safe metadata fields.

## 11. Invalid Behavior

An invalid case should match:

- validation_status=`fail`
- body_status=`fail_closed`
- expected reason code is present
- expected failed check is present
- body output is suppressed
- no raw payload is emitted
- safe marker boolean is present
- artifact file writing is false
- manifest file writing is false
- forbidden payload scan does not expose payload text

Invalid cases prove fail-closed behavior by metadata only.

## 12. Safe Marker Scan

Allowed safe marker names:

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

The scan should ensure:

- marker fields are boolean
- only one expected marker is true for single-reason invalid cases
- no actual payload values are stored
- no string payloads pretend to be markers
- marker names themselves are not treated as leakage

## 13. Forbidden Payload Scan

The scan should reject:

- raw_learner_text
- raw_rows
- logits
- probabilities
- private_path
- absolute_path
- request_body
- pointer_body
- expected_result_body
- generated_policy_body
- artifact_body_payload
- manifest_body
- final_text
- observed_after_text
- gold_label
- expected_action
- scoring_feedback_payload
- performance_metrics
- GitHub raw log markers
- local absolute paths

Safe marker field names are allowed exceptions. Actual payload keys or values
are not allowed.

## 14. Comparison Rules

Comparison rules:

- expected result and actual result compare only safe metadata fields
- reason_codes are sorted before comparison
- failed_checks are sorted before comparison
- list ordering is deterministic or normalized where specified
- count_summary is an exact match
- safety_flags is an exact match
- schema_version is an exact match
- case_id is an exact match
- body payload fields are not compared because body payload output is not
  allowed

Mismatch should be reported without printing input or expected bodies.

## 15. Aggregate Summary

Expected future root summary:

- mode=`fixture_root`
- validation_schema_version=
  `learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1`
- total_cases=18
- valid_cases=4
- invalid_cases=14
- matched_cases=18
- mismatched_cases=0
- input_error_cases=0
- content_suppressed=true
- no_raw_rows=true
- no_logits_dump=true
- no_private_paths=true
- no_performance_claims=true
- synthetic_only_checked=true
- no_oracle_checked=true
- artifact_policy_checked=true
- body_suppression_checked=true
- artifact_body_audit_checked=true
- request_body_count=0
- pointer_body_count=0
- expected_body_count=0
- raw_row_count=0
- logits_dump_count=0
- private_path_count=0
- performance_metric_count=0
- manifest_body_count=0
- reason_code_counts summarized count-only

The summary should remain parseable, deterministic, and metadata-only.

## 16. Error Handling

Error handling rules:

- malformed JSON -> input_error
- missing required file -> input_error
- unknown schema version -> expected invalid only for the unknown-schema case,
  otherwise mismatch or fail
- missing required field -> mismatch or fail
- forbidden payload -> fail closed without echoing payload
- unexpected file -> fail closed
- internal exception -> nonzero in a future CLI

This document does not implement CLI exit behavior.

## 17. Output Safety

Future validator and CLI output must not include:

- request body
- pointer body
- expected result body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body
- raw logs

Future output may include:

- counts
- reason code names
- case IDs
- schema versions
- safe flags
- marker booleans summarized count-only

## 18. Future CLI Design Notes

Future CLI arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`

Default output should be a safe human summary.

Future exit-code design:

- 0: all requested fixtures matched
- 2: usage or input error
- 3: mismatch
- 1: internal error

The CLI is not implemented in this step.

## 19. Future Makefile / Release-Quality Staging

Recommended future staging:

- Step326 validator implementation
- Step327 validator CLI design
- Step328 validator CLI implementation
- Step329 Makefile target design
- Step330 Makefile target implementation
- Step331 release-quality integration design
- Step332 wrapper integration
- Step333 remote/manual run record workflow design
- Step334 remote/manual run status marker

Release-quality integration should wait until standalone validator behavior,
CLI output safety, and Makefile target behavior are all checked.

## 20. Relation To Artifact Body Generation

The validator should exist before artifact body generation implementation.
It should first validate fixtures independent of a generator. Later generator
implementation can be tested against the same safe contract.

The default writer CLI remains body-free.

## 21. Relation To Current Artifact Writer Fixtures

Artifact writer fixtures validate writer metadata result. Artifact body
fixtures validate the body boundary. The roots should remain separate, and
the validator modules should remain separate.

## 22. Docs Safety Policy

Docs should include only:

- field names
- reason codes
- counts
- API names
- schema names
- safe status descriptions

Docs must not include:

- JSON examples
- artifact body examples
- raw payload examples
- log examples
- request bodies
- pointer bodies
- expected result bodies
- manifest bodies

## 23. Beginner-Friendly Explanation

A validator is the checker that reads fixture files and decides whether each
case matches the expected safe result. The fixture root now exists, so the
next step is to design the checker before writing code.

Safe marker scan checks whether an invalid case uses allowed boolean markers
to describe a simulated unsafe condition. Forbidden payload scan checks that
the unsafe content itself is absent.

The validator should report counts and reason codes rather than payloads so
that failures are understandable without exposing raw content or body data.

## 24. What This Does Not Do

This design does not:

- implement validator
- implement CLI
- add Makefile target
- integrate release-quality
- implement artifact body generation
- generate artifact body
- change fixtures
- change Python code or tests
- change workflow YAML
- change release-quality wrapper
- use real data
- compute metrics

## 25. Step325 Status

Step325 creates this docs-only artifact body fixture validator design. It does
not implement validator code, validator CLI, Makefile targets, release-quality
integration, artifact body generation, generated policy body generation,
manifest body generation, file writing, Python tests, fixture JSON changes,
metrics, real-data use, or production readiness claims.

## 26. Step326 Implementation Status

Step326 implements the metadata-only artifact body fixture validator module:

`python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py`

It also adds focused unit tests under `python/learner_state/tests/`. The
validator discovers the 18 synthetic fixture cases, validates required files
and schema versions, checks valid and invalid case expectations, scans safe
marker booleans, scans for forbidden payload keys and path/log markers,
compares safe metadata fields, and returns aggregate counts and reason-code
summaries only.

Step326 does not implement a validator CLI, Makefile target, release-quality
integration, artifact body generation, generated policy body generation,
manifest body generation, artifact or manifest file writing, fixture JSON
changes, metrics, real-data use, or production readiness claims.

## 27. Step327 CLI Design Status

Step327 designs the future CLI for this implemented validator:

[Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md).

The CLI design defines the future entrypoint, arguments, default fixture root,
human output, JSON output, exit codes, single-case behavior, error handling,
output safety, future tests, Makefile target candidate, and release-quality
staging. It does not implement CLI code, Makefile targets, release-quality
integration, artifact body generation, file writing, Python code or tests,
fixture JSON changes, metrics, real-data use, or production readiness claims.

## 28. Step328 CLI Implementation Status

Step328 implements the artifact body fixture validator CLI in the existing
validator module. The CLI is a thin entrypoint that calls the validator APIs,
supports default root validation and single-case validation, and emits safe
metadata-only human or JSON summaries.

It does not add a Makefile target, integrate release-quality, change workflow
YAML, change fixture JSON, implement artifact body generation, generate
policy bodies, generate manifest bodies, write files, compute metrics, use
real data, or claim production readiness.

## 29. Step329 Makefile Target Design Status

Step329 designs the future Makefile target for running the implemented CLI:

[Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md).

The design is docs-only. It defines the future target name, command, help
text, expected safe output, exit-code interpretation, log safety, future
target tests, and release-quality staging. It does not change the Makefile,
release-quality wrapper, workflow YAML, Python code or tests, fixture JSON,
artifact body generation, file writing, metrics, real-data use, or production
readiness claims.

## 30. Step330 Makefile Target Implementation Status

Step330 implements the standalone Makefile target for the artifact body
fixture validator CLI:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The target validates the synthetic artifact body fixture root with safe
metadata-only output. It does not integrate release-quality, change workflow
YAML, change Python code or tests, change fixture JSON, implement artifact
body generation, write files, compute metrics, use real data, or claim
production readiness.

## 31. Step331 Release-Quality Integration Design Status

Step331 designs future release-quality integration for the standalone target:

[Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md).

The design is docs-only and recommends a wrapper insertion point after
artifact writer runtime smoke and before config/scoring smoke checks. It does
not change the release-quality wrapper, workflow YAML, Makefile, Python code
or tests, fixture JSON, artifact body generation, file writing, metrics,
real-data use, or production readiness claims.

## 32. Step332 Release-Quality Wrapper Integration Status

Step332 integrates the artifact body fixture validator target into the
release-quality wrapper after artifact writer runtime smoke and before
config/scoring smoke checks.

The validator remains a fixture-boundary checker only. It does not generate
artifact bodies, generated policy bodies, manifest bodies, write files,
compute metrics, use real data, or claim production readiness.

## 33. Step333 Remote Run Record Workflow Design Status

Step333 designs the future remote/manual Release Quality run record workflow
for artifact body fixture validation:

[Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md).

The workflow design records only future public-safe metadata and does not
create a status marker, change workflow YAML, change wrapper code, change
fixtures, implement body generation, write files, compute metrics, use real
data, or claim production readiness.

## 34. Step334 Remote Run Status Marker Status

Step334 creates the public-safe remote/manual Release Quality status marker
for artifact body fixture validation:

[Learner-state frozen policy generation artifact body fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md).

The marker records count-only validation metadata and safety review
statements. It does not copy raw logs, fixture bodies, artifact body payloads,
raw rows, logits, private paths, raw learner text, real participant data, or
performance metric bodies.

## 35. Step335 Artifact Body Generation Implementation Status

Step335 adds the first safe metadata-only artifact body generation API. The
fixture validator remains unchanged and continues to validate the 18-case
fixture contract. The generator implementation is separate from the validator:
it does not modify fixture JSON, does not write artifact files, does not
generate manifest bodies, and does not add release-quality behavior.

## Related Documents

- [Learner-state frozen policy generation artifact body fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact writer runtime release-quality integration design](frozen_policy_generation_artifact_writer_runtime_release_quality_integration_design.md)
- [Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
