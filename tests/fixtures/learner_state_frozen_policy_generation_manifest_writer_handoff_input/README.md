# Manifest Writer Handoff Input Fixtures

This fixture root supports the manifest writer handoff input validation runner.
It is synthetic-only, metadata-only, body-free, and no-oracle.

Matrix identity:

- matrix_name=manifest_writer_handoff_input_contract_matrix
- case_selection=manifest-writer-handoff-input-contract
- schema_version=learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1
- contract_name=manifest_writer_handoff_input_contract
- handoff_input_mode=manifest_writer_handoff_input_metadata_only_no_invocation

Contract shape:

- selected_case_count=23
- selected_valid_case_count=3
- selected_invalid_case_count=20
- selected_fail_closed_case_count=11
- selected_usage_error_case_count=5
- selected_mismatch_case_count=4

Each case contains only metadata files:

- handoff_input_metadata.json
- expected_summary_metadata.json
- safety_expectations.json

Invalid cases model unsafe or non-matching categories with metadata-only fields.
The canonical fixtures do not invoke manifest writer, generate manifest body,
write files, emit payload bodies, expose artifact body payload, expose generated
policy body, or store raw logs.

This fixture root does not prove manifest writer correctness, file-writing
readiness, manifest body correctness, payload correctness, production readiness,
real-data readiness, or model performance.

Step663 creates
`docs/frozen_policy_generation_manifest_writer_handoff_input_validation_makefile_target_design.md`
as design-only / docs-only Makefile target design for the direct CLI runner.
This fixture root and fixture JSON remain unchanged.

Step664 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation`
for the direct CLI runner. This fixture root and fixture JSON remain unchanged,
and the target is not release-quality integrated yet.

Step665 creates
`docs/frozen_policy_generation_manifest_writer_handoff_input_validation_release_quality_integration_design.md`
as design-only / docs-only planning for future release-quality wrapper
integration of the Step664 standalone target. This fixture root and fixture JSON
remain unchanged.

Step666 adds the Step664 standalone target to `scripts/check_release_quality.sh`
as `release_quality_check: learner-state frozen policy generation manifest writer
handoff input validation`. This fixture root and fixture JSON remain unchanged,
and no manifest writer is invoked, no manifest body is generated, no files are
written, and no payload bodies are emitted.
