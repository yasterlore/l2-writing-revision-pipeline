# Artifact Body to Manifest Handoff Metadata-Only No-Writer-Invocation Fixture Contract Design

## 1. Scope

This document is design-only / docs-only and fixes the future fixture / matrix / metadata contract for the artifact body to manifest handoff metadata-only no-writer-invocation boundary.

This step is fixture contract design only. It does not create fixture JSON, change Python code/tests, change Makefile, change the release-quality wrapper, change workflows, change runtime implementation, or change validator implementation.

This step does not invoke manifest writer, generate manifest body, write manifest files, write artifact files, emit payload bodies, output artifact body payload, output generated policy body, or output raw stdout/stderr body.

This design does not prove production readiness, real-data readiness, or model performance.

## 2. Prior Design Dependency

- Step647 defined the no-writer-invocation handoff boundary.
- Step648 fixes the future fixture / matrix / metadata contract for that boundary.
- Step648 does not implement fixtures.
- Step648 does not implement runner.
- Step648 does not invoke manifest writer.
- Step648 does not generate manifest body.
- Step648 does not enable file writing.
- Step648 does not remove the Step645 local/manual fallback limitation.
- Step648 does not create remote GitHub Actions evidence.

## 3. Future Fixture Root

Future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`

This fixture root is not created in Step648. It is a future contract location. Future fixtures must be synthetic-only and must not contain raw learner text, payload bodies, manifest bodies, private paths, or absolute paths.

## 4. Future Matrix Identity

Required fields:

- `matrix_name=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_matrix`
- `case_selection=artifact-body-to-manifest-handoff-metadata-only-no-writer`
- `schema_version=learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_v0.1`
- `handoff_mode=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`

These are metadata contract identifiers. They do not represent manifest writer implementation, manifest body correctness, or file-writing readiness.

## 5. Future Selected Case Contract

Required aggregate counts:

- `selected_case_count=8`
- `selected_valid_metadata_only_case_count=3`
- `selected_invalid_fail_closed_case_count=5`
- `selected_usage_error_case_count=0`
- `selected_mismatch_case_count=0`
- `expected_pass_case_count=3`
- `expected_fail_closed_case_count=5`
- `expected_usage_error_case_count=0`
- `expected_mismatch_case_count=0`
- `expected_manifest_writer_invoked_count=0`
- `expected_manifest_body_generated_count=0`
- `expected_manifest_file_written_count=0`
- `expected_artifact_file_written_count=0`
- `expected_payload_body_emitted_count=0`
- `expected_generated_policy_body_emitted_count=0`
- `expected_artifact_body_payload_output_count=0`
- `expected_forbidden_body_detected_count=0`
- `expected_private_path_detected_count=0`
- `expected_absolute_path_detected_count=0`
- `expected_residue_file_count=0`

Invalid fail_closed cases are expected to be detected safely without printing forbidden content. Expected writer/file/body counts remain 0 in the public-safe aggregate summary. A future runner may internally classify fail_closed conditions, but must not emit forbidden body values.

## 6. Future Cases

Use exactly these case IDs for the initial future contract:

1. `valid/valid_handoff_metadata_minimal_no_writer`
   - `expected_status=pass`
   - `expected_category=valid_metadata_only`
   - `expected_writer_invoked=false`
   - `expected_manifest_body_generated=false`
   - `expected_file_written=false`
   - `expected_payload_body_emitted=false`
   - `expected_residue=false`

2. `valid/valid_handoff_metadata_count_only_summary`
   - `expected_status=pass`
   - `expected_category=valid_metadata_only`
   - `expected_writer_invoked=false`
   - `expected_manifest_body_generated=false`
   - `expected_file_written=false`
   - `expected_payload_body_emitted=false`
   - `expected_residue=false`

3. `valid/valid_handoff_metadata_no_residue`
   - `expected_status=pass`
   - `expected_category=valid_metadata_only`
   - `expected_writer_invoked=false`
   - `expected_manifest_body_generated=false`
   - `expected_file_written=false`
   - `expected_payload_body_emitted=false`
   - `expected_residue=false`

4. `invalid/invalid_manifest_writer_invoked`
   - `expected_status=fail_closed`
   - `expected_category=invalid_fail_closed`
   - `unsafe_condition=manifest_writer_invoked`

5. `invalid/invalid_manifest_body_generated`
   - `expected_status=fail_closed`
   - `expected_category=invalid_fail_closed`
   - `unsafe_condition=manifest_body_generated`

6. `invalid/invalid_manifest_file_written`
   - `expected_status=fail_closed`
   - `expected_category=invalid_fail_closed`
   - `unsafe_condition=manifest_file_written`

7. `invalid/invalid_artifact_or_payload_body_emitted`
   - `expected_status=fail_closed`
   - `expected_category=invalid_fail_closed`
   - `unsafe_condition=artifact_or_payload_body_emitted`

8. `invalid/invalid_private_or_absolute_path_detected`
   - `expected_status=fail_closed`
   - `expected_category=invalid_fail_closed`
   - `unsafe_condition=private_or_absolute_path_detected`

Step648 does not create these case directories, fixture JSON files, or fixture body examples. Future fixture bodies must remain synthetic and body-free.

## 7. Future Per-Case Metadata Contract

Allowed per-case metadata fields:

- `case_id`
- `expected_status`
- `expected_category`
- `unsafe_condition`
- `writer_invocation_enabled`
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
- `metadata_only_checked`
- `body_suppressed`
- `synthetic_only_checked`
- `no_oracle_checked`
- `forbidden_body_detected`
- `private_path_detected`
- `absolute_path_detected`
- `raw_learner_text_detected`
- `real_data_marker_detected`
- `no_oracle_forbidden_field_detected`
- `residue_file_count`
- `reason_code`

Forbidden per-case metadata fields:

- `payload_body`
- `artifact_body_payload`
- `generated_policy_body`
- `manifest_body`
- `manifest_json_body`
- `request_body`
- `pointer_body`
- `expected_body`
- `raw_stdout_body`
- `raw_stderr_body`
- `raw_rows`
- `logits`
- `probabilities`
- `private_path_value`
- `absolute_path_value`
- `raw_learner_text`
- `real_participant_data`
- `final_text`
- `observed_after_text`
- `gold_label`
- `post_hoc_annotation`
- `scoring_feedback_payload`

Field names representing counts or booleans are allowed. Field values containing actual forbidden content are not allowed. Future runner output should be aggregate-only by default.

## 8. Future Aggregate Metadata Contract

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

Expected safe pass aggregate values:

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

`observed_fail_closed_case_count=5` can be accepted only when unsafe conditions are represented by metadata category, not by printed forbidden content. `forbidden_body_detected_count=0` means no forbidden body was emitted in output, not that unsafe fixtures do not model unsafe categories. `pass` means the metadata-only handoff fixture contract matched. It does not mean manifest writer correctness or file-writing readiness.

## 9. Future Fixture File Shape

Suggested future per-case files, for design only:

- `case_metadata.json`
- `expected_summary_metadata.json`
- `safe_handoff_metadata.json`

Step648 does not create these files. Future files must not contain body payloads, manifest JSON bodies, request / pointer / expected bodies, private or absolute path values, or raw learner text. Future files must use synthetic placeholders only when needed, and should prefer booleans/counts over placeholder text.

## 10. Future Runner Selection Policy

Future runner selection rules:

- require `--case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer`
- select exactly 8 cases
- require the 3 valid metadata-only cases
- require the 5 invalid fail_closed cases
- fail usage_error if fixture root is missing
- fail usage_error if case selection is unsupported
- fail mismatch if selected count differs from 8 after contract is readable
- fail mismatch if expected categories differ from contract
- fail_closed if forbidden content is emitted
- fail_closed if manifest writer is invoked
- fail_closed if file writing occurs
- fail_closed if residue files are created

## 11. Future Status Semantics

### pass

`pass` means:

- selected 8 cases match the future fixture contract.
- valid metadata-only cases pass.
- invalid fail_closed cases are represented safely without emitting forbidden content.
- manifest writer is not invoked.
- manifest body is not generated.
- files are not written.
- forbidden body output count is 0.
- residue count is 0.

### usage_error

`usage_error` means:

- missing required CLI flag
- unsupported case selection
- missing fixture root
- malformed metadata contract
- unknown schema
- unsafe classification cannot be completed

### mismatch

`mismatch` means:

- selected case count differs from 8
- selected case IDs differ from contract
- expected counts differ from observed counts
- handoff metadata record count differs from expected
- schema / mode differs from contract

### fail_closed

`fail_closed` means:

- manifest writer was invoked
- manifest body was generated or emitted
- manifest file was written
- artifact file was written
- payload body was emitted
- generated policy body was emitted
- artifact body payload was output
- request / pointer / expected body was output
- private / absolute path was emitted
- raw learner text or real data marker was detected
- residue file was created
- unsafe output scan failed

## 12. Failure Mapping Contract

Exact mapping:

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
- private / absolute path output => fail_closed
- raw learner text / real data marker => fail_closed
- residue => fail_closed

## 13. Relationship to Step647 Design

- Step648 fixes the fixture contract proposed in Step647.
- Step648 remains design-only.
- Step648 does not create fixtures.
- Step648 does not implement runner.
- Step648 does not invoke manifest writer.
- Step648 does not generate manifest body.
- Step648 does not write files.
- Step648 keeps the no-writer-invocation boundary.

## 14. Relationship to Existing Payload Audit Boundary

- This handoff fixture contract is downstream of payload audit without payload emission.
- It does not replace the payload audit boundary.
- It does not remove the Step645 local/manual fallback limitation.
- It does not create remote evidence.
- It does not prove payload correctness.
- It does not prove artifact body payload quality.
- It does not imply manifest writer readiness.

## 15. Relationship to Manifest Writer / File-Writing Boundaries

- manifest writer integration remains future work.
- manifest writer invocation is explicitly out of scope.
- manifest body generation is explicitly out of scope.
- manifest file writing is explicitly out of scope.
- artifact file writing is explicitly out of scope.
- production file-writing path is explicitly out of scope.
- Step648 is a fixture contract design for a pre-writer handoff, not writer implementation.

## 16. Public-Safe Checklist

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

## 17. Non-Equivalence Cautions

- Fixture contract design is not fixture implementation.
- Fixture contract design is not runner implementation.
- Handoff fixture contract is not manifest writer integration.
- No-writer-invocation fixture contract is not manifest writer correctness.
- No-file-writing fixture contract is not file-writing readiness.
- Metadata-only fixture contract is not manifest body correctness.
- Count-only surrogate fields are not manifest body payloads.
- Payload audit pass is not payload correctness.
- Local/manual fallback is not remote GitHub Actions evidence.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.

## 18. Non-Claims

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

## 19. Recommended Next Step

Recommended:

`Step649: artifact body to manifest handoff metadata-only no-writer-invocation runner design`

Step649 should be design-only / docs-only. It should design future runner behavior from this fixture contract. It should not create fixture JSON, implement runner, invoke manifest writer, generate manifest body, enable file writing, or change Python code/tests, Makefile, wrapper, workflow, or fixture JSON.
