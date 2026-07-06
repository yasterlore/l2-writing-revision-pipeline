# Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Runner Design

## 1. Title

Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Runner Design

## 2. Scope

This document designs a future metadata-only / body-free / count-only runner for the actual-controlled v0.4 artifact body payload audit without payload emission.

This is design-only / docs-only. Step637 does not implement a payload audit runner, emit payload bodies, output artifact body payloads, output generated policy bodies, output manifest bodies, implement manifest writer integration, perform file writing, change Python code/tests, change Makefile, change the release-quality wrapper, change workflow files, change fixture JSON, change runtime implementation, or change validator implementation.

This runner design is not proof of production readiness, real-data readiness, model performance, runtime correctness generally, all invalid-case behavior, payload correctness, artifact body quality, free-form body safety, manifest writer correctness, file-writing readiness, generated policy quality, or learner-state estimator correctness.

## 3. Prior Chain Dependency

This runner design depends on:

- Step633 accepted the fixed 4 deferred invalid usage_error / mismatch release-quality boundary.
- Step634 recommended payload audit without payload emission as the next boundary.
- Step635 designed the payload audit boundary as metadata-only / body-free / count-only.
- Step636 fixed the fixture / matrix / metadata contract for Surface A + Surface C.

Step636 fixed the future matrix:

```text
matrix_name=actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
case_selection=payload-audit-without-payload-emission
selected_case_count=36
selected_valid_case_count=6
selected_invalid_case_count=30
selected_fail_closed_invalid_case_count=26
selected_deferred_invalid_case_count=4
expected_payload_capable_case_count=6
expected_payload_not_applicable_case_count=30
```

Step637 translates that fixed contract into a future runner design. It does not implement the runner.

## 4. Runner Goal

The future runner should read only metadata needed to satisfy the Step636 count-only contract and emit only an aggregate public-safe summary.

The runner should:

- select the fixed 36-case metadata contract
- classify selected cases into valid, fail_closed invalid, usage_error, and mismatch categories
- classify payload-capable versus no-payload-expected categories
- confirm payload output remains suppressed
- confirm forbidden body emission counts remain zero
- confirm manifest writer invocation remains zero
- confirm file writing remains zero
- confirm residue remains zero
- emit a single aggregate summary

The runner should not:

- inspect artifact body payload content
- emit artifact body payload content
- inspect or emit generated policy body content
- inspect or emit manifest body content
- inspect or emit fixture JSON body
- inspect or emit request / pointer / expected bodies
- invoke manifest writer integration
- enable file writing

## 5. Proposed Future Module And CLI

Future module path:

```text
python/learner_state/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py
```

Future focused test path:

```text
python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py
```

Future direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection payload-audit-without-payload-emission \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-forbidden-body
```

Step637 does not create this module, test file, or CLI.

## 6. CLI Contract

Required future options:

- `--fixture-root`
- `--case-selection payload-audit-without-payload-emission`
- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-forbidden-body`

Forbidden future options for this runner:

- options that print payload body content
- options that print generated policy body content
- options that print manifest body content
- options that write artifact files
- options that write manifest files
- options that include raw stdout/stderr body
- options that include raw fixture JSON body

If a future CLI receives an unsupported case selection or conflicting body-output option, it should return runner-level `usage_error`.

## 7. Selection Algorithm

The future runner should select cases from the Step636 contract rather than broad discovery.

Recommended algorithm:

1. Parse CLI options.
2. Confirm `--summary-only`, `--no-file-writing`, and `--no-manifest-writer` are present.
3. Confirm the case selection equals `payload-audit-without-payload-emission`.
4. Resolve the fixture root as a directory.
5. Load only metadata needed for directory/category selection and expected status category counts.
6. Select the fixed accepted matrices:
   - 6 valid all-valid cases
   - 26 invalid fail_closed cases
   - 4 deferred invalid usage_error / mismatch cases
7. Refuse to select any extra category not covered by Step636.
8. Build in-memory metadata-only records.
9. Classify records into aggregate counts.
10. Emit only an aggregate summary.

The future runner should not inspect fixture JSON body content to determine selection.

## 8. Classification Algorithm

The future runner should classify each selected metadata record into these categories:

- valid pass expected
- invalid fail_closed expected
- invalid usage_error expected
- invalid mismatch expected

Payload category classification:

- valid pass expected cases count as payload-capable metadata cases
- invalid fail_closed, usage_error, and mismatch cases count as payload-not-applicable cases
- all 36 selected cases count as payload-suppressed cases
- all 36 selected cases count as body-free cases

Expected classification counts:

```text
selected_case_count=36
selected_valid_case_count=6
selected_invalid_case_count=30
selected_fail_closed_invalid_case_count=26
selected_deferred_invalid_case_count=4
selected_usage_error_case_count=3
selected_mismatch_case_count=1
expected_payload_capable_case_count=6
expected_payload_not_applicable_case_count=30
expected_payload_availability_checked_case_count=6
expected_payload_suppressed_case_count=36
expected_payload_body_free_case_count=36
expected_pass_case_count=6
expected_fail_closed_case_count=26
expected_usage_error_case_count=3
expected_mismatch_case_count=1
```

The future runner should compute observed counts from metadata-only records and compare them to these fixed expectations.

## 9. Payload Audit Checks Without Emission

The future runner may check only metadata and count-only signals.

Allowed checks:

- payload-capable case count
- payload-not-applicable case count
- payload availability checked count
- payload suppressed count
- body-free case count
- forbidden body emitted count
- artifact body payload emitted count
- generated policy body emitted count
- manifest body emitted count
- stdout/stderr body suppression counts

Forbidden checks:

- payload body equality
- payload body substring inspection
- payload body hashing
- generated policy body inspection
- manifest body inspection
- request / pointer / expected body inspection
- fixture JSON body inspection
- raw stdout/stderr body inspection

Hashing or fingerprinting payload content is forbidden because it still depends on body content.

## 10. Aggregate Summary Contract

The future runner should emit only this aggregate public-safe summary shape:

```text
mode=actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_v0.1
status=pass
reason_code=none
matrix_name=actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
case_selection=payload-audit-without-payload-emission
selected_case_count=36
selected_valid_case_count=6
selected_invalid_case_count=30
selected_fail_closed_invalid_case_count=26
selected_deferred_invalid_case_count=4
selected_usage_error_case_count=3
selected_mismatch_case_count=1
expected_payload_capable_case_count=6
expected_payload_not_applicable_case_count=30
expected_payload_availability_checked_case_count=6
expected_payload_suppressed_case_count=36
expected_payload_body_free_case_count=36
observed_payload_capable_case_count=6
observed_payload_not_applicable_case_count=30
observed_payload_availability_checked_case_count=6
observed_payload_suppressed_case_count=36
observed_payload_body_free_case_count=36
expected_pass_case_count=6
observed_pass_case_count=6
expected_fail_closed_case_count=26
observed_fail_closed_case_count=26
expected_usage_error_case_count=3
observed_usage_error_case_count=3
expected_mismatch_case_count=1
observed_mismatch_case_count=1
artifact_body_payload_emitted_case_count=0
generated_policy_body_emitted_case_count=0
manifest_body_emitted_case_count=0
forbidden_body_emitted_case_count=0
raw_stdout_body_suppressed_case_count=36
raw_stderr_body_suppressed_case_count=36
manifest_writer_invoked_case_count=0
file_writing_enabled_case_count=0
artifact_file_written_case_count=0
manifest_file_written_case_count=0
residue_file_count=0
content_suppressed=True
body_suppressed=True
metadata_only_checked=True
synthetic_only_checked=True
no_oracle_checked=True
payload_body_emitted=False
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

If the future runner emits body field count distribution fields, those fields must remain count-only and should be documented in the implementation step.

## 11. Runner-Level Status Semantics

Future runner-level status values:

- `pass`
- `usage_error`
- `input_error`
- `mismatch`
- `fail_closed`

`status=pass` means only that the runner satisfied the metadata-only count contract and suppression checks.

`status=pass` does not mean:

- artifact body payload content is correct
- generated policy body content is correct
- invalid cases individually passed
- payload correctness is proven
- runtime correctness is proven generally

Per-case expected categories remain distinct from runner-level status.

## 12. Failure Mapping

Future runner-level `usage_error`:

- missing required CLI argument
- unsupported case selection
- body-output option requested
- file-writing option requested
- manifest-writer option requested
- incompatible summary mode

Future runner-level `input_error`:

- fixture root is unavailable
- selected case metadata cannot be resolved without reading forbidden body content
- required accepted matrix metadata is unavailable
- category metadata is malformed in a way that prevents safe count-only classification

Future runner-level `mismatch`:

- selected case count differs from 36
- valid case count differs from 6
- invalid case count differs from 30
- fail_closed invalid count differs from 26
- deferred invalid count differs from 4
- usage_error count differs from 3
- mismatch count differs from 1
- payload-capable count differs from 6
- payload-not-applicable count differs from 30
- observed category counts differ from expected category counts

Future runner-level `fail_closed`:

- artifact body payload emitted count is non-zero
- generated policy body emitted count is non-zero
- manifest body emitted count is non-zero
- forbidden body emitted count is non-zero
- raw stdout/stderr body suppression counts are incomplete
- manifest writer invocation count is non-zero
- file-writing enabled count is non-zero
- artifact or manifest file written count is non-zero
- residue file count is non-zero
- synthetic-only / metadata-only / no-oracle flags are missing or false
- production / real-data / performance claim flags are true

## 13. Safe Scanner Design

The future runner should include a safe scanner over its own public output only.

The scanner should detect count-only unsafe signals such as:

- forbidden body emission marker
- payload emitted marker
- generated policy body emitted marker
- manifest body emitted marker
- raw stdout/stderr body emitted marker
- manifest writer invoked marker
- file writing enabled marker
- residue detected marker

The scanner should not scan payload body content, generated policy body content, manifest body content, request body, pointer body, expected body, fixture JSON body, or raw stdout/stderr body.

## 14. Residue Policy

The future runner should use an isolated temporary observation area only if required, and it should clean it before returning.

Expected residue summary:

```text
residue_file_count=0
```

Any non-zero residue count should be runner-level `fail_closed`.

The future runner must not write artifact files or manifest files.

## 15. Focused Test Design For Step638

Future focused tests should cover:

- CLI usage errors
- unsupported case selection
- fixed 36-case selection count
- valid / invalid / fail_closed / deferred count classification
- payload-capable versus payload-not-applicable count classification
- expected versus observed category matching
- mismatch behavior when counts differ
- fail_closed behavior on forbidden body emission flags
- fail_closed behavior on manifest writer invocation flags
- fail_closed behavior on file-writing flags
- residue count failure
- aggregate summary output only
- absence of payload body fields in public output

Focused tests must not include fixture JSON bodies, payload bodies, generated policy bodies, manifest bodies, raw stdout/stderr bodies, raw rows, logits/probabilities, private paths, absolute paths, raw learner text, real participant data, or performance metric bodies.

## 16. Relationship To Existing Boundaries

- Planned-only v0.3 remains not actual-controlled invocation.
- Actual-controlled v0.4 single-case smoke remains the primary controlled metadata-only invocation smoke.
- Actual-controlled v0.4 all-valid multi-case smoke remains the 6-case pass matrix.
- Actual-controlled v0.4 invalid fail_closed smoke remains the fixed 26-case fail_closed matrix.
- Actual-controlled v0.4 deferred usage_error / mismatch smoke remains the fixed 4-case expected-category matrix.
- Step637 designs a runner that uses their accepted counts as metadata contract inputs.
- Step637 does not reopen or broaden any accepted boundary.
- Step637 does not replace any release-quality chain or remote status marker.

## 17. Future Implementation Handoff

Recommended next step:

```text
Step638: actual-controlled v0.4 artifact body payload audit without payload emission runner implementation
```

Step638 should:

- add the future runner module
- add focused tests
- keep output aggregate, metadata-only, body-free, and count-only
- not change fixture JSON
- not change Makefile
- not change release-quality wrapper
- not change workflows
- not invoke manifest writer integration
- not enable file writing

Step638 should not proceed if the runner cannot preserve body-free public output.

## 18. Boundaries Explicitly Not Selected Now

Do not select now:

- payload audit runner implementation
- payload body emission
- artifact body payload output
- generated policy body output
- manifest body output
- payload correctness evaluation
- artifact body quality evaluation
- free-form body safety proof
- manifest writer integration
- manifest body generation
- file writing
- production file-writing path
- Makefile target implementation
- release-quality wrapper integration
- real-data readiness check
- model performance check

## 19. Non-Equivalence Cautions

- Runner design is not runner implementation.
- Aggregate metadata is not payload correctness evidence.
- Count-only body field metadata is not free-form body safety proof.
- Payload-capable counts are not artifact body quality evidence.
- Body suppression checks are not generated policy quality evidence.
- Combining accepted matrix counts does not prove runtime correctness generally.
- Future runner pass would not prove runtime correctness generally.
- Future runner pass would not prove artifact body payload correctness.
- Future runner pass would not prove manifest writer correctness.
- Future runner pass would not prove file-writing readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.

## 20. Non-Claims

- Production readiness is not claimed.
- Real-data readiness is not claimed.
- Model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- Runtime correctness generally is not claimed.
- All invalid-case runtime behavior is not claimed.
- Payload correctness is not claimed.
- Artifact body quality is not claimed.
- Free-form body safety is not claimed.
- Manifest writer correctness is not claimed.
- File-writing readiness is not claimed.
- Manifest body generation correctness is not claimed.
- Generated policy quality is not claimed.
- Learner-state estimator correctness is not claimed.

## 21. Public-Safe Checklist

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

## 22. Recommended Next Step

Recommended next step:

```text
Step638: actual-controlled v0.4 artifact body payload audit without payload emission runner implementation
```

Step638 should remain body-free, metadata-only, and count-only. It should not emit payload bodies, change fixture JSON, add Makefile target integration, add release-quality wrapper integration, invoke manifest writer integration, or enable file writing.

## 23. Step638 Implementation Status Reference

Step638 implements the designed direct CLI-only runner as `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py` with focused tests in `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py`. The implemented CLI uses `--fixture-root`, `--case-selection payload-audit-without-payload-emission`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-forbidden-body`.

The implementation remains standalone direct CLI-only. It does not add a Makefile target, does not add release-quality wrapper integration, does not change workflow files, does not change fixture JSON, does not emit payload bodies, does not invoke manifest writer integration, and does not enable file writing.

## 24. Step639 Makefile Target Design Reference

Step639 adds `docs/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_makefile_target_design.md` as a design-only / docs-only plan for a future standalone Makefile target around the Step638 direct CLI. It does not change Makefile, release-quality wrapper, workflow files, Python code/tests, fixture JSON, payload body emission, manifest writer integration, or file writing.

## 25. Step640 Makefile Target Implementation Reference

Step640 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission` for the Step638 direct CLI. It does not add release-quality wrapper integration, workflow changes, Python code/tests changes, fixture JSON changes, payload body emission, manifest writer integration, or file writing.
