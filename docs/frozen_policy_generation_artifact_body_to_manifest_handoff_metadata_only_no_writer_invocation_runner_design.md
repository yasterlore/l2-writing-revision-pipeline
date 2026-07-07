# Artifact Body to Manifest Handoff Metadata-Only No-Writer-Invocation Runner Design

## 1. Scope

This document is design-only / docs-only and designs future runner behavior for the artifact body to manifest handoff metadata-only no-writer-invocation boundary.

This step does not change Python code/tests, create fixture JSON, change Makefile, change the release-quality wrapper, change workflows, change runtime implementation, or change validator implementation.

This step does not invoke manifest writer, generate manifest body, write manifest files, write artifact files, emit payload bodies, output artifact body payload, output generated policy body, or output raw stdout/stderr body.

This design does not prove production readiness, real-data readiness, or model performance.

## 2. Prior Contract Dependency

- Step647 defined the handoff boundary.
- Step648 fixed the future 8-case fixture / matrix / metadata contract.
- Step649 designs the future runner behavior for that fixed contract.
- Step649 does not create fixture JSON.
- Step649 does not implement runner.
- Step649 does not implement tests.
- Step649 does not invoke manifest writer.
- Step649 does not generate manifest body.
- Step649 does not enable file writing.
- Step649 does not remove the Step645 local/manual fallback limitation.
- Step649 does not create remote GitHub Actions evidence.

## 3. Future Runner Module Proposal

Proposed future runner module:

`python/learner_state/frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation.py`

Proposed future focused tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation.py`

These files are not created in Step649. Step650 may implement them after this design is reviewed. Step650 may also need to create the synthetic fixture root defined by Step648, unless a separate fixture-implementation step is inserted.

## 4. Future CLI Design

Proposed future CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation \
  --case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer \
  --summary-only \
  --no-manifest-writer \
  --no-file-writing \
  --fail-closed-on-forbidden-body
```

Required future flags:

- `--fixture-root`
- `--case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer`
- `--summary-only`
- `--no-manifest-writer`
- `--no-file-writing`
- `--fail-closed-on-forbidden-body`

Missing required safety flags should map to runner-level usage_error. Unsupported case selection should map to runner-level usage_error. The CLI must not include any flag that enables manifest writer invocation or file writing. The CLI must not emit payload bodies or manifest bodies.

## 5. Future Runner Input Model

The future runner should:

- read only the synthetic fixture root defined by Step648.
- select exactly the 8 cases fixed in Step648.
- process metadata-only fixture files.
- not print fixture JSON bodies.
- not print request / pointer / expected bodies.
- not print artifact body payload.
- not print generated policy body.
- not print manifest body.
- not invoke manifest writer.
- not enable file writing.
- not write artifact files.
- not write manifest files.
- not use real participant data.
- not use private / absolute path values.
- output aggregate public-safe key-value metadata by default.

The runner should treat invalid fail_closed cases as metadata-modeled unsafe categories. It must not expose unsafe body or path values. It should use count-only surrogate fields for unsafe conditions.

## 6. Future Fixture File Reading Policy

Step648 suggested future per-case files:

- `case_metadata.json`
- `expected_summary_metadata.json`
- `safe_handoff_metadata.json`

The future runner may read these files only if they are synthetic and body-free.

The future runner must fail_closed or usage_error if future fixture files contain:

- payload body values
- artifact body payload values
- generated policy body values
- manifest body values
- request / pointer / expected body values
- raw stdout/stderr body values
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data
- no-oracle forbidden fields

Step649 does not create these files. It only designs the future reading policy. Future implementation should prefer booleans/counts over placeholder body text.

## 7. Future Case Selection Algorithm

Rules:

- require `--case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer`
- require fixture root to exist
- require exactly 8 selected cases
- require exactly 3 valid metadata-only cases
- require exactly 5 invalid fail_closed cases
- require exact case IDs from Step648
- reject duplicate case IDs
- reject unknown case IDs
- reject missing required case IDs
- reject unsupported schema version
- reject unsupported matrix name
- reject unsupported handoff mode

Status mapping:

- missing fixture root => usage_error
- unsupported case selection => usage_error
- unsupported schema => usage_error or mismatch depending on whether the contract is readable
- selected count not 8 => mismatch or usage_error depending on whether the contract is readable
- duplicate case ID => usage_error
- missing required case ID => mismatch
- unknown case ID => mismatch

## 8. Future Per-Case Classification Algorithm

Valid metadata-only cases:

- `expected_status=pass`
- `expected_category=valid_metadata_only`
- `writer_invoked=false`
- `manifest_body_generated=false`
- `manifest_file_written=false`
- `artifact_file_written=false`
- `payload_body_emitted=false`
- `generated_policy_body_emitted=false`
- `artifact_body_payload_output=false`
- `private_path_detected=false`
- `absolute_path_detected=false`
- `residue_file_count=0`

Invalid fail_closed cases:

- `expected_status=fail_closed`
- `expected_category=invalid_fail_closed`
- unsafe condition is represented as metadata category
- unsafe body values must not be printed
- future runner may count the case as observed_fail_closed
- future aggregate unsafe output counts must remain 0 if no forbidden content was emitted

Important distinction:

- `observed_fail_closed_case_count=5` means the five invalid cases were classified as fail_closed categories.
- It does not mean forbidden body content was emitted.
- `forbidden_body_detected_count=0` means no forbidden body was emitted or observed in output.
- It does not mean the matrix has no unsafe-category cases.

## 9. Future Aggregate Output Contract

Required aggregate fields:

- `mode=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`
- `schema_version=learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_v0.1`
- `status`
- `reason_code`
- `matrix_name=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_matrix`
- `case_selection=artifact-body-to-manifest-handoff-metadata-only-no-writer`
- `selected_case_count=8`
- `selected_valid_metadata_only_case_count=3`
- `selected_invalid_fail_closed_case_count=5`
- `expected_pass_case_count=3`
- `observed_pass_case_count`
- `expected_fail_closed_case_count=5`
- `observed_fail_closed_case_count`
- `expected_usage_error_case_count=0`
- `observed_usage_error_case_count`
- `expected_mismatch_case_count=0`
- `observed_mismatch_case_count`
- `processed_case_count`
- `input_error_case_count`
- `manifest_writer_invoked_count`
- `manifest_body_generated_count`
- `manifest_body_output_count`
- `manifest_file_written_count`
- `artifact_file_written_count`
- `file_writing_enabled_count`
- `payload_body_emitted_count`
- `generated_policy_body_emitted_count`
- `artifact_body_payload_output_count`
- `request_body_output_count`
- `pointer_body_output_count`
- `expected_body_output_count`
- `raw_stdout_body_suppressed_count`
- `raw_stderr_body_suppressed_count`
- `forbidden_body_detected_count`
- `private_path_detected_count`
- `absolute_path_detected_count`
- `raw_learner_text_detected_count`
- `real_data_marker_detected_count`
- `no_oracle_forbidden_field_detected_count`
- `residue_file_count`
- `content_suppressed`
- `body_suppressed`
- `metadata_only_checked`
- `synthetic_only_checked`
- `no_oracle_checked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

Expected pass aggregate values:

- `status=pass`
- `reason_code=none`
- `processed_case_count=8`
- `observed_pass_case_count=3`
- `observed_fail_closed_case_count=5`
- `observed_usage_error_case_count=0`
- `observed_mismatch_case_count=0`
- `input_error_case_count=0`
- `manifest_writer_invoked_count=0`
- `manifest_body_generated_count=0`
- `manifest_body_output_count=0`
- `manifest_file_written_count=0`
- `artifact_file_written_count=0`
- `file_writing_enabled_count=0`
- `payload_body_emitted_count=0`
- `generated_policy_body_emitted_count=0`
- `artifact_body_payload_output_count=0`
- `request_body_output_count=0`
- `pointer_body_output_count=0`
- `expected_body_output_count=0`
- `raw_stdout_body_suppressed_count=8`
- `raw_stderr_body_suppressed_count=8`
- `forbidden_body_detected_count=0`
- `private_path_detected_count=0`
- `absolute_path_detected_count=0`
- `raw_learner_text_detected_count=0`
- `real_data_marker_detected_count=0`
- `no_oracle_forbidden_field_detected_count=0`
- `residue_file_count=0`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

`status=pass` means the metadata-only handoff fixture contract matched. It does not mean manifest writer correctness, file-writing readiness, manifest body correctness, or payload correctness.

## 10. Future Per-Case Output Policy

Default output should be aggregate-only.

If future debugging exposes per-case summaries, allowed fields only:

- `case_id`
- `expected_status`
- `observed_status`
- `expected_category`
- `observed_category`
- `reason_code`
- `unsafe_condition_category`
- `writer_invoked`
- `manifest_body_generated`
- `manifest_file_written`
- `artifact_file_written`
- `payload_body_emitted`
- `generated_policy_body_emitted`
- `artifact_body_payload_output`
- `request_body_output`
- `pointer_body_output`
- `expected_body_output`
- `raw_stdout_body_suppressed`
- `raw_stderr_body_suppressed`
- `forbidden_body_detected`
- `private_path_detected`
- `absolute_path_detected`
- `raw_learner_text_detected`
- `real_data_marker_detected`
- `no_oracle_forbidden_field_detected`
- `residue_file_count`
- `content_suppressed`
- `body_suppressed`
- `metadata_only_checked`
- `synthetic_only_checked`
- `no_oracle_checked`

Forbidden per-case output:

- payload body
- artifact body payload
- generated policy body
- manifest body
- manifest JSON body
- request body
- pointer body
- expected body
- raw stdout body
- raw stderr body
- raw rows
- logits/probability values
- private path values
- absolute path values
- raw learner text
- real participant data
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotations
- scoring feedback payload

## 11. Future Status Semantics

### pass

`pass` means:

- selected 8 cases match the Step648 fixture contract.
- 3 valid metadata-only cases pass.
- 5 invalid fail_closed cases are classified safely.
- manifest writer is not invoked.
- manifest body is not generated or emitted.
- files are not written.
- payload / generated policy / artifact body payload is not emitted.
- forbidden body output count is 0.
- residue file count is 0.

### usage_error

`usage_error` means:

- missing required CLI flag
- unsupported case selection
- missing fixture root
- malformed metadata contract
- unknown schema
- duplicate case ID
- unsafe classification cannot be completed safely

### mismatch

`mismatch` means:

- selected case count differs from 8
- selected case IDs differ from contract
- selected valid / invalid counts differ from contract
- expected pass/fail_closed counts differ from observed counts
- schema / mode / matrix differs from contract
- aggregate counts disagree with per-case metadata

### fail_closed

`fail_closed` means:

- manifest writer was invoked
- manifest body was generated or emitted
- manifest file was written
- artifact file was written
- file writing was enabled
- payload body was emitted
- generated policy body was emitted
- artifact body payload was output
- request / pointer / expected body was output
- raw stdout/stderr body was output
- private / absolute path was emitted
- raw learner text or real data marker was detected
- no-oracle forbidden field was detected
- residue file was created
- unsafe output scan failed

## 12. Failure Mapping Design

Exact future mappings:

- missing `--summary-only` => usage_error
- missing `--no-manifest-writer` => usage_error
- missing `--no-file-writing` => usage_error
- missing `--fail-closed-on-forbidden-body` => usage_error
- unsupported case selection => usage_error
- missing fixture root => usage_error
- selected count not 8 => mismatch or usage_error depending on whether the contract was readable
- valid metadata-only count not 3 => mismatch
- invalid fail_closed count not 5 => mismatch
- expected pass/fail_closed counts mismatch => mismatch
- duplicate case ID => usage_error
- unknown case ID => mismatch
- missing required case ID => mismatch
- manifest writer invocation => fail_closed
- manifest body generation => fail_closed
- manifest body output => fail_closed
- manifest file written => fail_closed
- artifact file written => fail_closed
- file writing enabled => fail_closed
- payload body emitted => fail_closed
- generated policy body emitted => fail_closed
- artifact body payload output => fail_closed
- request / pointer / expected body output => fail_closed
- raw stdout/stderr body output => fail_closed
- private / absolute path output => fail_closed
- raw learner text / real data marker => fail_closed
- no-oracle forbidden field => fail_closed
- residue => fail_closed

## 13. Safety Scan Design

The future runner must scan aggregate and any allowed per-case summary for:

- payload body output
- artifact body payload output
- generated policy body output
- manifest body output
- request body output
- pointer body output
- expected body output
- raw stdout/stderr body output
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data markers
- no-oracle forbidden fields
- performance metric body
- production readiness claims
- real-data readiness claims
- model performance claims

Safety scan rules:

- scan must be metadata-only / body-free.
- scan failure must not print the offending content.
- scan failure should return fail_closed.
- scan should report only count-only flags.

## 14. Residue Policy

The future runner must:

- not create files.
- not create manifest files.
- not create artifact files.
- not create temporary payload files.
- not create output directories.
- not leave residue.

If future tests use temporary directories, they must use test-owned temp dirs and clean up after themselves.

Residue detection:

- `residue_file_count=0` required in pass state.
- any unexpected generated file => fail_closed.

## 15. Focused Tests Design for Step650

Minimum tests:

- runner direct CLI `status=pass`
- `selected_case_count=8`
- `selected_valid_metadata_only_case_count=3`
- `selected_invalid_fail_closed_case_count=5`
- `observed_pass_case_count=3`
- `observed_fail_closed_case_count=5`
- `observed_usage_error_case_count=0`
- `observed_mismatch_case_count=0`
- `manifest_writer_invoked_count=0`
- `manifest_body_generated_count=0`
- `manifest_body_output_count=0`
- `manifest_file_written_count=0`
- `artifact_file_written_count=0`
- `file_writing_enabled_count=0`
- `payload_body_emitted_count=0`
- `generated_policy_body_emitted_count=0`
- `artifact_body_payload_output_count=0`
- `forbidden_body_detected_count=0`
- `private_path_detected_count=0`
- `absolute_path_detected_count=0`
- `raw_learner_text_detected_count=0`
- `real_data_marker_detected_count=0`
- `no_oracle_forbidden_field_detected_count=0`
- `residue_file_count=0`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`
- missing `--summary-only` maps to usage_error
- missing `--no-manifest-writer` maps to usage_error
- missing `--no-file-writing` maps to usage_error
- missing `--fail-closed-on-forbidden-body` maps to usage_error
- unsupported case selection maps to usage_error
- missing fixture root maps to usage_error
- selected count mismatch maps to mismatch
- valid metadata-only count mismatch maps to mismatch
- invalid fail_closed count mismatch maps to mismatch
- duplicate case ID maps to usage_error
- unknown case ID maps to mismatch
- manifest writer invocation maps to fail_closed
- manifest body generation maps to fail_closed
- manifest body output maps to fail_closed
- manifest file written maps to fail_closed
- artifact file written maps to fail_closed
- file writing enabled maps to fail_closed
- payload body emitted maps to fail_closed
- generated policy body emitted maps to fail_closed
- request / pointer / expected body output maps to fail_closed
- private / absolute path output maps to fail_closed
- raw learner text / real data marker maps to fail_closed
- no-oracle forbidden field maps to fail_closed
- residue maps to fail_closed
- output does not include fixture JSON body
- output does not include payload body
- output does not include generated policy body
- output does not include manifest body
- output does not include private / absolute path values
- fixture JSON is not mutated
- existing payload audit runner remains unchanged

Step650 may need to create the synthetic fixture root and fixture JSON if no separate fixture implementation step is inserted. Future fixture JSON must be body-free and metadata-only. If the team wants to keep fixture creation separate, Step650 should be split into fixture implementation and runner implementation.

## 16. Relationship to Step648 Contract

- Step649 implements no code.
- Step649 designs runner behavior for Step648's fixed contract.
- Step649 should not revise the 8-case contract unless it identifies a safety problem.
- If any change to Step648 contract is needed, document it as a future contract revision, not as a silent change.

## 17. Relationship to Payload Audit Boundary

- This future handoff runner is downstream of the payload audit without payload emission boundary.
- It does not replace the payload audit runner.
- It does not remove the Step645 local/manual fallback limitation.
- It does not create remote evidence.
- It does not prove payload correctness.
- It does not prove artifact body payload quality.

## 18. Relationship to Manifest Writer / File-Writing Boundaries

- Future runner must not invoke manifest writer.
- Future runner must not generate manifest body.
- Future runner must not write files.
- Manifest writer integration remains future work.
- File-writing readiness remains future work.
- Production file-writing path remains out of scope.

## 19. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no artifact body payload
- no generated policy body
- no manifest body
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

## 20. Non-Equivalence Cautions

- Runner design is not runner implementation.
- Runner design is not fixture implementation.
- Handoff runner is not manifest writer integration.
- No-writer-invocation runner is not manifest writer correctness.
- No-file-writing runner is not file-writing readiness.
- Metadata-only runner is not manifest body correctness.
- Count-only surrogate fields are not manifest body payloads.
- Payload audit pass is not payload correctness.
- Local/manual fallback is not remote GitHub Actions evidence.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.

## 21. Non-Claims

- Does not claim production readiness.
- Does not claim real-data readiness.
- Does not claim model performance.
- Does not claim F1 / accuracy / ECE / AURCC achievement.
- Does not claim runtime correctness generally.
- Does not claim all invalid-case runtime behavior.
- Does not claim payload correctness.
- Does not claim artifact body payload quality.
- Does not claim manifest writer correctness.
- Does not claim file-writing readiness.
- Does not claim generated policy quality.
- Does not claim learner-state estimator correctness.
- Does not claim educational validity.

## 22. Recommended Next Step

Recommended:

`Step650: artifact body to manifest handoff metadata-only no-writer-invocation runner implementation`

Step650 should implement the future runner and focused tests. Step650 may create the synthetic fixture root and body-free fixture JSON if no separate fixture implementation step is inserted. Step650 should not change Makefile, release-quality wrapper, or workflow. Step650 should not invoke manifest writer, generate manifest body, enable file writing, or emit payload bodies. Step650 should update root README and full technical specification related docs because it is an implementation Step.

## 23. Step654 Release-Quality Integration Status

Step654 integrates the Step652 standalone Makefile target into `scripts/check_release_quality.sh` after artifact body generation safe-metadata CLI smoke and before artifact body file-writing / manifest writer checks.

The wrapper check runs the existing runner through `make check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation`. It preserves the runner's metadata-only / body-free / no-writer-invocation contract and does not change Python code/tests, fixture JSON, runtime implementation, validator implementation, manifest writer invocation, manifest body generation, file writing, or payload body emission.

## 24. Step655 Remote/Manual Run Record Workflow Design

Step655 adds a design-only / docs-only workflow for a future public-safe status marker after the Step654 wrapper integration. The future status marker should record only remote/manual metadata and aggregate count-only handoff summary fields, use `not available from provided public-safe metadata` for missing values, and avoid raw logs, fixture bodies, payload bodies, manifest bodies, manifest writer invocation, and file-writing evidence.

## 25. Step656 Remote Status Marker

Step656 creates the remote status marker for the Step654 wrapper-integrated handoff check. The marker records public-safe remote metadata and aggregate count-only runner summary only; it does not change runner code/tests, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.

## 26. Step657 Final Safety Review

Step657 creates `docs/frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_release_quality_chain_final_safety_review.md` as the final-safety-review-only / docs-only review for the handoff chain. It accepts the fixed 8-case count-only metadata boundary and does not change runner behavior, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.
