# Frozen Policy Generation Artifact Body Generation Runtime Invocation Fixture Validator Design

## 1. Title

Frozen Policy Generation Artifact Body Generation Runtime Invocation Fixture
Validator Design

## 2. Scope

This document is the fixture validator design for the runtime invocation
fixture root created in Step570.

This is design-only / docs-only. It does not implement a validator, change
Python code/tests, change Makefile, change the release-quality wrapper, change
workflows, change fixture JSON, change runtime implementation, implement actual
artifact body generation runtime invocation, implement manifest writer
integration, or perform file writing.

This design is not proof of production readiness, real-data readiness, or
model performance.

## 3. Target Fixture Root

- fixture root path:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation`
- root status: created in Step570; planned validator not implemented
- valid cases: 6
- invalid cases: 24
- total cases: 30
- JSON files per case: 7
- total JSON files: 210
- root README: available
- fixture JSON: created in Step570
- validator: not yet implemented
- release-quality integration: not yet integrated

## 4. Target Layout

Each case is expected to contain exactly these seven metadata-only JSON files:

- `case_metadata.json`
- `safe_metadata_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_invocation_metadata.json`
- `expected_runtime_invocation_summary.json`
- `expected_error.json`

The future validator should check that every case has exactly these files, no
required file is missing, no unexpected JSON file is present, all JSON files
parse, the case id matches the directory name, the case group matches `valid`
or `invalid`, schema versions match expectations, and expected status / reason
mappings are consistent.

## 5. Proposed Validator Module / CLI

Proposed module:

- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`

Proposed test file:

- `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`

Proposed CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation
```

These files and commands are not implemented in Step571.

## 6. Proposed Validation Schema and Mode

- validation schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
- validator mode:
  `artifact_body_generation_runtime_invocation_fixture_validation`
- fixture schema accepted:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_v0.1`
- future runtime schema reference:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- future integration mode reference:
  `artifact-body-runtime-invocation`

## 7. Expected Aggregate Output

The future validator output should be public-safe and count-only. Proposed
aggregate fields:

- `mode=artifact_body_generation_runtime_invocation_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
- `fixture_root=tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation`
- `total_cases=30`
- `valid_cases=6`
- `invalid_cases=24`
- `total_json_files=210`
- `json_files_per_case=7`
- `matched_cases=30`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=1`
- `fail_closed_cases=22`
- `mismatch_cases=1`
- `missing_required_file_cases=0`
- `unexpected_json_file_cases=0`
- `content_suppressed=true`
- `body_suppressed=true`
- `metadata_only_checked=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_artifact_body_payload=true`
- `no_manifest_body=true`
- `no_generated_policy_body=true`
- `no_raw_stdout_body=true`
- `no_raw_stderr_body=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_probabilities_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_raw_learner_text=true`
- `no_real_participant_data=true`
- `no_performance_metric_body=true`
- `file_writing_checked=true`
- `manifest_writer_integration_checked=true`
- `artifact_body_generation_runtime_invocation_checked=true`
- `production_readiness_claimed=false`
- `real_data_readiness_claimed=false`
- `performance_claims_present=false`

Proposed reason-code counts:

- `none`: 6
- `unsupported_schema`: 1
- `mismatched_expected_status`: 1
- all other invalid unsafe reasons: 1 each

Raw reason payloads are not required and should not be emitted.

## 8. Validation Checks

Root-level checks:

- root exists
- `valid/` and `invalid/` directories exist
- root README exists
- total case count is 30
- valid case count is 6
- invalid case count is 24
- total JSON count is 210
- no unexpected top-level directories

Case-level checks:

- required 7 files exist
- no unexpected JSON files
- case id matches directory
- case group matches parent directory
- valid cases expect pass / none
- invalid cases expect usage_error / fail_closed / mismatch
- expected error is absent for valid cases
- expected error is present as metadata-only summary for invalid cases
- metadata file count equals 7
- unsafe signal count mapping is consistent

Schema checks:

- fixture schema v0.1
- future runtime schema v0.3
- future integration mode `artifact-body-runtime-invocation`
- expected validation schema v0.1 references

Safety checks:

- no request body
- no pointer body
- no expected body
- no artifact body payload
- no manifest body
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private / absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no production / real-data / model performance claims
- no file writing
- no manifest writer invocation

## 9. Expected Status / Reason Mapping

Pass:

- valid cases
- status: `pass`
- reason_code: `none`
- unsafe_signal_count: 0

Usage error:

- `invalid_unsupported_schema`
- reason_code: `unsupported_schema`

Mismatch:

- `invalid_mismatched_expected_status`
- reason_code: `mismatched_expected_status`

Fail-closed:

- `invalid_request_body_present`
- `invalid_pointer_body_present`
- `invalid_expected_body_present`
- `invalid_artifact_body_payload_present`
- `invalid_manifest_body_present`
- `invalid_generated_policy_body_present`
- `invalid_raw_stdout_body_present`
- `invalid_raw_stderr_body_present`
- `invalid_raw_rows_present`
- `invalid_logits_present`
- `invalid_probabilities_present`
- `invalid_private_path_present`
- `invalid_absolute_path_present`
- `invalid_raw_learner_text_present`
- `invalid_real_data_marker_present`
- `invalid_performance_metric_body_present`
- `invalid_file_writing_requested`
- `invalid_manifest_writer_requested`
- `invalid_unsafe_artifact_body_runtime_mode`
- `invalid_no_oracle_forbidden_field`
- `invalid_unsafe_output_residue_risk`
- `invalid_active_root_merge_attempted`

## 10. Public-Safe Output Policy

Validator output may include:

- mode
- schema
- fixture root path as repository-relative path
- case counts
- JSON counts
- status class counts
- reason-code counts
- boolean safety checks
- root errors as an empty list or count-only summary

Validator output must not include:

- fixture JSON body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw stdout/stderr body
- raw rows
- logits/probabilities
- private/absolute path values
- raw learner text
- real participant data
- performance metric body

## 11. Proposed Focused Tests for Future Implementation

Future tests should cover:

- aggregate counts
- exact 7-file layout
- all JSON parse
- valid cases map to pass
- invalid unsupported schema maps to usage_error
- invalid mismatched expected status maps to mismatch
- other invalid unsafe markers map to fail_closed
- no raw body fields emitted in validator output
- no private / absolute path values emitted
- missing root maps to input error
- missing required file maps to usage_error
- unexpected JSON file maps to usage_error
- duplicate case id maps to input error
- existing fixture root remains unchanged
- active root validator still passes
- planned safe-metadata validator still passes

The usage_error choice for missing required file and unexpected JSON file keeps
the future CLI failure public-safe while preserving a count-only error surface.

## 12. Relationship to Existing Validators

- active artifact body generation integration fixture validator remains separate
- planned safe-metadata v0.2 fixture validator remains separate
- artifact body fixture validator remains separate
- artifact body file-writing validators remain separate
- manifest writer validators remain separate
- this future validator does not replace any of them
- this future validator only validates the new runtime invocation fixture contract

## 13. Future Staging

Suggested chain:

- Step572: artifact body generation runtime invocation fixture validator implementation
- Step573: Makefile target design
- Step574: standalone Makefile target implementation
- Step575: runtime invocation implementation design
- Step576: runtime invocation implementation
- Step577: release-quality integration design
- Step578: release-quality wrapper integration
- Step579: remote/manual run record workflow design
- Step580: remote status marker
- Step581: final safety review

If implementation risk is high, insert Step572a as validator implementation
refinement design before code.

## 14. Recommended Next Step

Recommended next step: Step572 artifact body generation runtime invocation
fixture validator implementation.

Reason: Step570 already created a bounded metadata-only / body-free root with a
stable seven-file layout and explicit expected status mapping. The next safe
step is a separate validator implementation over that fixture root, still
without runtime invocation, manifest writer integration, file writing, Makefile
target integration, or release-quality wrapper integration.

If future reviewers decide the validator scope is too broad, Step572 can be
narrowed to a validator implementation refinement design before code.

## 15. Non-Equivalence Cautions

- fixture validator design is not validator implementation
- future fixture validator pass is not runtime invocation correctness generally
- future fixture validator pass is not artifact body generation runtime correctness generally
- fixture contract validation is not artifact body payload correctness
- artifact body generation safe-metadata CLI smoke is not equivalent to runtime invocation
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 16. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact body generation integration correctness
- artifact body generation runtime correctness generally
- manifest writer integration correctness
- manifest writer file-writing production readiness
- artifact body payload correctness
- safe-metadata free-form body safety
- manifest body generation correctness
- generated policy quality
- learner-state estimator correctness
- artifact writer CLI actual invocation correctness generally
- runtime actual invocation correctness generally

## 17. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no manifest body
- no artifact body payload
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims

## 18. Step572 Implementation Status

Step572 implements the validator module
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`
and focused tests
`python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`.

The CLI validates the Step570 fixture root as 30 cases / 210 JSON files with
6 pass, 1 usage-error, 22 fail-closed, and 1 mismatch case. Step574 adds a
standalone Makefile target for the validator. The implementation remains
separate from release-quality wrapper integration, workflow changes, runtime
invocation, manifest writer integration, and file-writing paths.

Step573 follow-up status: the Makefile target design is available at
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validator_makefile_target_design.md`.
It proposes a future standalone target for this validator without changing
Makefile, wrapper, workflow, Python code/tests, fixture JSON, runtime
implementation, artifact body generation runtime invocation, manifest writer
integration, or file writing.

Step574 implements that standalone Makefile target as
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`.
The target runs the Step572 validator against the Step570 planned root and is
not yet release-quality integrated. It still does not invoke artifact body
generation runtime, invoke manifest writer, or write files.

Step575 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_implementation_design.md`
as a design-only / docs-only runtime invocation implementation design. It does
not change runtime implementation, Python code/tests, Makefile, wrapper,
workflow, fixture JSON, validator implementation, manifest writer integration,
or file writing.
