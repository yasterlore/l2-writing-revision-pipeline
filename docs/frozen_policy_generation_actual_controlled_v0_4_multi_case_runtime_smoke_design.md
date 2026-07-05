# Actual-Controlled v0.4 Multi-Case Runtime Smoke Design

## Scope

This document is the actual-controlled v0.4 multi-case runtime smoke design after the Step600 final safety review and the Step601 next-boundary planning doc.

This is a design-only / docs-only step. It does not change Python code/tests, Makefile, release-quality wrapper, workflows, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This design does not provide production readiness, real-data readiness, or model performance evidence.

## Starting Point

The current v0.4 actual-controlled runtime smoke is release-quality-integrated and has remote-status-recorded evidence. The current v0.4 smoke uses one primary valid case. The actual-controlled fixture validator covers 36 cases / 252 JSON. The runtime target currently checks the primary valid case only.

The current boundary is metadata-only / body-free / count-only where possible. Manifest writer integration remains separate. File writing remains separate. Artifact body payload correctness remains separate. Real-data readiness remains separate. Model performance remains separate.

## Decision Questions

Main question:

- How should actual-controlled v0.4 runtime smoke be expanded from one primary case to multiple cases while preserving synthetic-only / metadata-only / body-free / no-oracle safety?

Secondary questions:

- Which valid cases should be included?
- Should all 6 valid actual-controlled cases be run?
- Should selected invalid/fail-closed cases be run through the runtime, or only fixture-validated?
- Should the multi-case smoke use a new aggregation CLI mode or an external runner that loops over existing CLI?
- Should the future output be key-value text, JSON metadata summary, or line-oriented case summaries?
- How should stdout/stderr be captured and suppressed across multiple cases?
- How should residue checks work across multiple cases?
- How should safe metadata field counts be aggregated?
- How should v0.1 / v0.2 / v0.3 compatibility be rechecked?
- How should release-quality ordering change later?

## Existing Fixture Root Inventory Method

Step603 should inventory case IDs from the existing actual-controlled fixture root using metadata-only directory and file names.

Rules:

- Only list case IDs, filenames, counts, schema/mode metadata, and expected public-safe status categories.
- Do not copy fixture JSON bodies.
- Do not copy request / pointer / expected body.
- Do not copy artifact body payload.
- Do not copy manifest body.
- Do not copy generated policy body.
- Do not copy raw stdout/stderr body.
- Do not copy private / absolute path values.

Recommended method:

- Inspect `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`.
- List valid case IDs and invalid case IDs by directory / file name only.
- Confirm aggregate remains 36 cases / 252 JSON / 7 JSON per case.
- Use metadata-only case IDs in docs.

## Candidate Case-Selection Options

### Option A: All-Valid Multi-Case Smoke

Run all 6 valid actual-controlled cases through v0.4 runtime smoke.

Benefits:

- Directly addresses the primary-case limitation.
- Keeps failure expectations simple.
- Lower risk than invalid runtime execution.
- Preserves body-free / metadata-only safety.
- Good first expansion after Step600.

Risks:

- Only valid cases are runtime-executed.
- Invalid/fail-closed categories remain fixture-validator-covered but not runtime-executed.

### Option B: Curated Valid Subset Plus Selected Fail-Closed Invalid Cases

Run 3-6 valid cases plus a small selected set of invalid cases expected to fail closed.

Benefits:

- Exercises fail-closed runtime mapping.
- Better safety scan coverage.

Risks:

- Higher risk of unsafe output handling.
- Requires careful temporary-copy mutation or dedicated metadata-only invalid invocation handling.
- More complex aggregation.

### Option C: All 36 Fixture Cases Through Runtime

Run all valid and invalid actual-controlled cases through runtime.

Benefits:

- Maximum coverage.

Risks:

- Too broad for first multi-case smoke.
- Higher chance of unsafe or ambiguous output.
- Not recommended immediately after Step600.

### Option D: Aggregator Design Only, No Case Expansion Yet

Design aggregation but keep one primary case.

Benefits:

- Lowest implementation risk.

Risks:

- Does not address the Step600 limitation.

## Recommended Case-Selection Option

Recommend Option A for the next implementation chain unless Step603 finds a strong reason not to.

Use all 6 valid actual-controlled cases as the first multi-case runtime smoke boundary. Keep invalid cases covered by the actual-controlled fixture validator for now. Do not run invalid cases through runtime in the first multi-case smoke implementation. Add invalid runtime execution only after a separate fail-closed runtime matrix design. Keep all outputs public-safe / metadata-only / body-free.

## Runtime Aggregation Design Options

### Option A: External Python Runner Loops Over Existing v0.4 CLI

- Add a dedicated multi-case smoke runner later.
- Runner executes the existing `frozen_policy_generation_artifact_body_generation_runtime_integration` CLI per case.
- Captures each case output internally.
- Emits only aggregate public-safe key-value summary.
- Does not expose raw stdout/stderr bodies.

Benefits:

- Does not overload existing single-case CLI.
- Keeps existing v0.4 single-case behavior unchanged.
- Allows explicit aggregation logic.

Risks:

- New module / tests needed.

### Option B: Add Multi-Case Mode To Existing Runtime Integration Module

- Extend existing module with `--fixture-case all-valid` or `--multi-case`.
- Emits aggregate summary directly.

Benefits:

- Single module surface.

Risks:

- More risk of complicating v0.1 / v0.2 / v0.3 / v0.4 single-case behavior.
- Could blur existing CLI semantics.

### Option C: Makefile Loops Over Six CLI Calls

- No new Python runner.
- Makefile target executes six direct CLI commands.

Benefits:

- Minimal Python code.

Risks:

- Harder to produce aggregate public-safe summary.
- Harder to suppress raw stdout/stderr consistently.
- Harder to count pass/fail/unsafe_signal cases.
- Not recommended.

## Recommended Aggregation Option

Recommend Option A.

Future implementation should create a dedicated runner module, for example:

- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`

Future focused tests:

- `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`

The runner should call or reuse the existing v0.4 runtime integration behavior in a controlled way. It should preserve existing single-case CLI behavior unchanged. It should output aggregate public-safe key-value metadata only. It should not write files. It should not invoke manifest writer. It should not emit artifact body payload.

If an in-process call is safer than subprocess, Step603 or Step604 should justify that. If subprocess is used, raw stdout/stderr must be captured and summarized only.

## Proposed Future Multi-Case Schema And Mode

Proposed schema:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1
```

Proposed mode:

```text
actual_controlled_v0_4_multi_case_runtime_smoke
```

Proposed invocation mode:

```text
all_valid_actual_controlled_v0_4_cases
```

These names are not implemented in Step602.

## Proposed Future CLI

Recommended future CLI for Step604 or later:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection all-valid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Required flags:

- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-unsafe-output`

Do not require a payload-emitting flag. Do not add manifest writer options.

## Proposed Aggregate Output Fields

Public-safe aggregate output fields should include at least:

- `mode=actual_controlled_v0_4_multi_case_runtime_smoke`
- `schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1`
- `status=pass`
- `reason_code=none`
- `fixture_root=tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`
- `case_selection=all-valid`
- `selected_case_count=6`
- `selected_valid_case_count=6`
- `selected_invalid_case_count=0`
- `executed_case_count=6`
- `pass_case_count=6`
- `usage_error_case_count=0`
- `fail_closed_case_count=0`
- `mismatch_case_count=0`
- `input_error_case_count=0`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `all_cases_artifact_body_runtime_invoked=True`
- `all_cases_controlled_metadata_only_invocation=True`
- `artifact_body_generation_cli_invoked_case_count=6`
- `artifact_body_generation_cli_output_scanned_case_count=6`
- `artifact_body_generation_cli_output_body_free_case_count=6`
- `artifact_body_payload_emitted_case_count=0`
- `manifest_writer_invoked_case_count=0`
- `file_writing_enabled_case_count=0`
- `artifact_file_written_case_count=0`
- `manifest_file_written_case_count=0`
- `raw_stdout_body_suppressed_case_count=6`
- `raw_stderr_body_suppressed_case_count=6`
- `request_body_detected_case_count=0`
- `pointer_body_detected_case_count=0`
- `expected_body_detected_case_count=0`
- `artifact_body_payload_detected_case_count=0`
- `manifest_body_detected_case_count=0`
- `generated_policy_body_detected_case_count=0`
- `raw_rows_detected_case_count=0`
- `logits_detected_case_count=0`
- `probabilities_detected_case_count=0`
- `private_path_detected_case_count=0`
- `absolute_path_detected_case_count=0`
- `raw_learner_text_detected_case_count=0`
- `real_data_marker_detected_case_count=0`
- `performance_metric_body_detected_case_count=0`
- `runtime_safety_scan_passed_case_count=6`
- `unsafe_signal_total_count=0`
- `residue_file_count=0`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

If exact valid case IDs are included, include only case IDs, not bodies.

## Per-Case Summary Policy

Allowed per-case summary fields:

- case_id
- status
- reason_code
- runtime_schema_version
- integration_mode
- artifact_body_runtime_invoked
- artifact_body_runtime_mode
- safe_metadata_body_field_count
- unsafe_signal_count
- residue_file_count

Forbidden per-case content:

- fixture body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw stdout/stderr body
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data

Per-case output should be optional or count-only by default. If per-case lines are emitted, they must be public-safe key-value lines.

## Failure Mapping For Future Multi-Case Smoke

### pass

- all selected valid cases pass
- all selected cases use v0.4 schema
- all selected cases use controlled metadata-only invocation
- all selected cases suppress raw stdout/stderr bodies
- all selected cases have no unsafe signals
- no manifest writer invoked
- no file writing enabled
- no residue

### usage_error

- fixture root missing
- no valid cases discovered
- invalid case-selection value
- unsupported schema / mode
- missing required flags
- selected case missing required metadata
- case ID duplicate
- unexpected non-valid case selected for all-valid mode

### fail_closed

- any selected case emits request body marker
- pointer body marker
- expected body marker
- artifact body payload marker
- manifest body marker
- generated policy body marker
- raw stdout/stderr body marker
- raw rows marker
- logits/probabilities marker
- private/absolute path marker
- raw learner text marker
- real data marker
- performance metric body marker
- file writing requested/detected
- manifest writer requested/invoked
- artifact body CLI nonzero or ambiguous
- unsafe output residue

### mismatch

- expected aggregate count mismatch
- expected per-case status mismatch
- expected schema/mode mismatch
- expected safety flag mismatch

## Residue And Output Suppression Design

Requirements:

- create no persistent output files
- use temporary directories only if needed
- clean temporary directories after each case
- aggregate `residue_file_count`
- fail closed if unexpected residue appears
- suppress raw stdout body
- suppress raw stderr body
- do not write captured stdout/stderr into docs
- do not write captured stdout/stderr into persistent files
- count only safe summary fields

## Compatibility Requirements

Future implementation must preserve:

- v0.1 `plan-only-bridge`
- v0.2 `safe-metadata-smoke`
- v0.3 `artifact-body-runtime-invocation` planned-only mode
- v0.4 single-case `artifact-body-runtime-invocation-controlled`
- existing actual-controlled fixture validator target
- existing v0.4 single-case runtime target
- existing release-quality wrapper labels

Multi-case smoke should be additive.

## Focused Tests For Future Implementation

Future tests should include at least:

- discovers all 6 valid actual-controlled cases by case ID only
- does not copy fixture JSON body
- all-valid multi-case smoke passes
- selected_case_count=6
- pass_case_count=6
- selected_invalid_case_count=0
- artifact_body_generation_cli_invoked_case_count=6
- artifact_body_generation_cli_output_body_free_case_count=6
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- raw_stdout_body_suppressed_case_count=6
- raw_stderr_body_suppressed_case_count=6
- unsafe_signal_total_count=0
- residue_file_count=0
- missing required flag maps to usage_error
- invalid case-selection maps to usage_error
- no valid cases discovered maps to usage_error
- duplicate case ID maps to usage_error
- unexpected invalid case selected maps to usage_error
- unsafe marker in one selected case maps aggregate to fail_closed
- artifact body CLI nonzero in one selected case maps aggregate to fail_closed
- residue in one selected case maps aggregate to fail_closed
- expected count mismatch maps to mismatch
- v0.4 single-case runtime target remains unchanged
- v0.3 planned-only target remains unchanged
- fixture JSON not mutated

Use temporary copies for mutation tests. Do not mutate canonical fixture JSON.

## Future Makefile Target Design

Likely future target:

```text
check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke
```

Proposed help text:

```text
Run actual-controlled v0.4 multi-case runtime smoke
```

Proposed command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection all-valid --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Makefile target implementation should be a later Step.

## Future Release-Quality Staging

Recommended sequence:

- standalone multi-case runtime CLI passes first
- focused tests pass
- Makefile target design
- Makefile target implementation
- release-quality integration design
- release-quality wrapper integration
- remote status marker
- final safety review

Do not integrate into release-quality before standalone target passes.

## Relationship To Current Single-Case Target

- Multi-case target does not replace single-case v0.4 target.
- Single-case target remains a fast primary smoke.
- Multi-case target adds broader valid-case coverage.
- Fixture validator remains responsible for invalid category coverage.
- Invalid runtime execution should be a separate future boundary.

## Non-Equivalence Cautions

- Design doc is not implementation.
- Future multi-case smoke will not prove runtime correctness generally.
- All-valid smoke will not prove invalid runtime fail-closed behavior.
- Metadata-only smoke will not prove artifact body payload correctness.
- Count-only summaries will not prove free-form body safety.
- Manifest writer validators remain separate.
- File-writing validators remain separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.

## Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- artifact body generation integration correctness is not claimed.
- artifact body generation runtime correctness generally is not claimed.
- manifest writer integration correctness is not claimed.
- manifest writer file-writing production readiness is not claimed.
- artifact body payload correctness is not claimed.
- safe-metadata free-form body safety is not claimed.
- manifest body generation correctness is not claimed.
- generated policy quality is not claimed.
- learner-state estimator correctness is not claimed.
- artifact writer CLI actual invocation correctness generally is not claimed.
- runtime actual invocation correctness generally is not claimed.

## Public-Safe Checklist

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

## Recommended Next Step

Recommended next step:

- Step603: actual-controlled v0.4 multi-case runtime smoke fixture/matrix contract design

Step603 should inventory case IDs and define the exact all-valid case matrix. Step603 should remain design-only / docs-only unless explicitly changed. Step603 should not implement Python code, modify Makefile, modify the release-quality wrapper, modify workflow, modify fixture JSON unless it explicitly becomes a fixture-contract creation step, invoke manifest writer, enable file writing, or use real data.

## Step603 Fixture Matrix Contract Reference

Step603 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_fixture_matrix_contract_design.md`
as a design-only / docs-only fixture/matrix contract for the future all-valid
multi-case runtime smoke. It records case IDs only, fixes the 6-case matrix,
and leaves implementation, Makefile, wrapper, workflow, fixture JSON, manifest
writer integration, and file writing unchanged.

## Step604 Implementation Reference

Step604 implements the direct CLI-only all-valid 6-case runner at `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py` with focused tests. The runner follows this design's public-safe aggregate boundary and remains outside Makefile and release-quality integration.

## Step605 Makefile Target Design Reference

Step605 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_makefile_target_design.md` as a design-only / docs-only handoff for adding the Step604 runner as a future standalone Makefile target. This multi-case runtime smoke design remains unchanged.

## Step606 Makefile Target Implementation Reference

Step606 adds the standalone Makefile target for the Step604 runner. The target remains outside release-quality integration and does not change Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step607 Release-Quality Integration Design Reference

Step607 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_integration_design.md` as a design-only / docs-only handoff for future wrapper integration of the Step606 standalone target. This multi-case runtime smoke design remains unchanged.

## Step608 Release-Quality Integration Reference

Step608 integrates the Step606 standalone multi-case target into `scripts/check_release_quality.sh` after the actual-controlled v0.4 single-case smoke. This multi-case runtime smoke design remains unchanged; Step608 does not change Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step609 Remote Run Record Workflow Reference

Step609 adds a design-only / docs-only workflow for a future public-safe status marker after Step608 wrapper integration. This multi-case runtime smoke design remains unchanged; Step609 does not create the marker or change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step610 Remote Status Marker Reference

Step610 adds the public-safe status marker for the Step608 wrapper-integrated multi-case check. This multi-case runtime smoke design remains unchanged; Step610 does not change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step611 Final Safety Review Reference

Step611 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_chain_final_safety_review.md` as a final-safety-review-only / docs-only review for the Step602-Step610 all-valid multi-case runtime smoke chain. This multi-case runtime smoke design remains unchanged; Step611 does not change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step612 Next Boundary Planning Reference

Step612 adds `docs/frozen_policy_generation_runtime_chain_post_multi_case_final_safety_review_next_boundary_planning.md` as a planning-only / docs-only comparison after the Step611 final safety review. This multi-case runtime smoke design remains unchanged; Step612 does not change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step613 Invalid-Case Matrix Design Reference

Step613 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_matrix_design.md` as a design-only / docs-only plan for a future invalid-case runtime fail-closed smoke. This all-valid multi-case runtime smoke design remains unchanged; Step613 does not execute invalid cases or change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step614 Fixture Matrix Contract Reference

Step614 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_fixture_matrix_contract_design.md` as a design-only / docs-only contract for the future invalid-case runtime fail-closed smoke. This all-valid multi-case runtime smoke design remains unchanged; Step614 does not execute invalid cases or change wrapper, Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step615 Implementation Status Reference

Step615 implements a separate direct CLI-only invalid-case fail-closed runner and focused tests. This all-valid runtime smoke design remains unchanged and is not replaced by the invalid-case runner. Step615 does not add Makefile or release-quality integration, change fixture JSON, invoke manifest writer, or enable file writing.
