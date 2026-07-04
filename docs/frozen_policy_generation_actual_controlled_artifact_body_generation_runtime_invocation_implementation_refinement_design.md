# Actual-Controlled Artifact Body Generation Runtime Invocation Implementation Refinement Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Implementation Refinement Design

## 2. Scope

This document is the final refinement design before a future v0.4
actual-controlled artifact body generation runtime invocation implementation
step.

This is design-only / docs-only. It does not change Python code/tests,
Makefile, release-quality wrapper, workflow files, fixture JSON, validator
implementation, runtime implementation, artifact body generation
implementation, artifact body generation integration, manifest writer
integration, manifest body generation, generated policy body generation,
artifact body file writing, or manifest file writing.

This step does not run actual artifact body generation runtime invocation,
does not invoke manifest writer, and does not write files. It is not evidence
of production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

Step569 through Step574 completed the planned-only runtime invocation fixture,
validator, and standalone target chain for the metadata-only fixture root.

Step575 through Step579 completed the planned-only v0.3 runtime mode and
standalone target chain. The v0.3 mode records runtime invocation as planned
but not invoked.

Step580 through Step583 completed release-quality integration and a public-safe
remote status marker for the planned-only chain. Step584 completed the final
safety review for that planned-only release-quality boundary.

Step585 introduced the actual-controlled invocation design. Step586 defined
the actual-controlled fixture/schema contract. Step587 created the separate
actual-controlled fixture root. Step588 designed the actual-controlled fixture
validator. Step589 added the standalone validator. Step590 designed the
standalone Makefile target. Step591 added the standalone target.

Step591 provides standalone validation of the v0.4 fixture root. The
actual-controlled runtime invocation behavior remains future work.

## 4. Implementation Decision To Refine

Main question:

- How should Step593 add v0.4 actual-controlled artifact body generation
  runtime invocation behavior while preserving v0.1 / v0.2 / v0.3
  compatibility and maintaining public-safe / metadata-only / body-free /
  synthetic-only / no-oracle safety?

Secondary questions:

- Should Step593 extend the existing runtime integration module or create a
  dedicated runtime module?
- Should artifact body generation be invoked through a controlled subprocess
  or an in-process function call?
- Which fixture case should be the primary smoke case?
- What exact CLI should Step593 expose?
- What fields should v0.4 output?
- How should stdout/stderr be captured and scanned?
- How should fail-closed behavior be mapped?
- What existing targets must remain unchanged?
- What remains out of scope until later steps?

## 5. Option Comparison

### Option A: Extend Existing Runtime Integration Module With v0.4 Controlled Mode

Benefits:

- Reuses the established CLI boundary in
  `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`.
- Keeps v0.1 / v0.2 / v0.3 and v0.4 modes in one explicit schema/mode table.
- Allows focused compatibility tests to prove older modes remain unchanged
  within their selected-case boundaries.
- Avoids new module surface area and additional routing docs.

Risks:

- The existing module must keep planned-only v0.3 semantics separate from
  actual-controlled v0.4 semantics.
- A careless `--actual-invocation` implementation could broaden older modes.

Complexity:

- Moderate. Adds a new schema, mode, flag enforcement, controlled invocation
  path, output scan, and focused tests.

Safety boundary clarity:

- Strong if v0.4 has explicit schema/mode separation and `--actual-invocation`
  is allowed only for the v0.4 controlled mode.

### Option B: Dedicated Actual-Controlled Runtime Invocation Module

Benefits:

- Creates a visibly separate boundary for actual-controlled behavior.
- Reduces risk of accidentally changing v0.1 / v0.2 / v0.3 code paths.

Risks:

- Adds a new CLI surface, new docs, and later Makefile/release-quality staging.
- Duplicates runtime fixture loading and safety scan behavior unless carefully
  shared.

Complexity:

- Higher than Option A because it creates a second runtime path.

Safety boundary clarity:

- Clear module-level separation, but more moving parts to verify.

### Option C: Reuse v0.3 Planned-Only Mode With `--actual-invocation`

Benefits:

- Lower code churn.

Risks:

- Blurs the meaning of v0.3, where `artifact_body_runtime_invoked=False`.
- Makes older remote markers and docs harder to interpret.
- Increases compatibility risk.

Complexity:

- Low short-term complexity, higher long-term ambiguity.

Safety boundary clarity:

- Weak. This option is not recommended.

### Option D: Postpone Implementation And Add Another Design Layer

Benefits:

- Safest if invocation path details remain unresolved.
- Gives room to decide subprocess versus in-process behavior later.

Risks:

- Slows the chain without adding executable coverage.
- Step591 already provides the fixture validator target needed for a narrow
  implementation step.

Complexity:

- Low now, deferred later.

Safety boundary clarity:

- Strong for docs, but no implementation progress.

## 6. Recommended Direction

Prefer Option A if the existing module can keep explicit schema/mode
separation. Step593 should extend
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
with a new v0.4 schema and `artifact-body-runtime-invocation-controlled`
mode.

Keep v0.3 `artifact-body-runtime-invocation` planned-only behavior unchanged.
Do not reinterpret v0.3 as actual invocation. Use the Step587 actual-controlled
fixture root and primary case `valid/valid_actual_controlled_safe_metadata_invocation`.

The future v0.4 path should invoke artifact body generation through a
controlled metadata-only path, capture stdout/stderr internally, scan summary
output, suppress raw stdout/stderr body, and emit only public-safe key-value
metadata.

The future path must not emit request / pointer / expected / artifact /
manifest / generated policy bodies. It must not invoke manifest writer. It
must not enable file writing. Release-quality wrapper integration should be
deferred until a standalone runtime target exists and passes.

## 7. Proposed v0.4 Runtime Schema And Mode

- runtime schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- integration mode: `artifact-body-runtime-invocation-controlled`
- primary fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`
- primary fixture case: `valid/valid_actual_controlled_safe_metadata_invocation`

Mode differences:

- v0.1 `plan-only-bridge`: no actual invocation
- v0.2 `safe-metadata-smoke`: no actual artifact body runtime invocation
- v0.3 `artifact-body-runtime-invocation`: planned-only marker,
  `artifact_body_runtime_invoked=False`
- v0.4 `artifact-body-runtime-invocation-controlled`: controlled
  metadata-only actual invocation, `artifact_body_runtime_invoked=True`,
  body-free output

## 8. Proposed Step593 CLI

Future Step593 CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --fixture-case valid/valid_actual_controlled_safe_metadata_invocation \
  --mode artifact-body-runtime-invocation-controlled \
  --actual-invocation \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Rules:

- `--actual-invocation` is allowed only with v0.4 actual-controlled mode.
- `--actual-invocation` must not affect v0.1 / v0.2 / v0.3 behavior.
- `--summary-only` must be required.
- `--no-file-writing` must be required.
- `--no-manifest-writer` must be required.
- Unsupported combinations must map to `usage_error` or `fail_closed`.

## 9. Artifact Body Generation Invocation Path

Recommended approach:

- Use controlled subprocess invocation of the existing artifact body generation
  CLI in safe-metadata mode if that keeps boundaries clearer.
- The subprocess command should use fixture metadata paths only.
- Capture stdout/stderr internally.
- Parse only public-safe key-value summary output.
- Suppress raw stdout/stderr body.
- Scan for forbidden body/value markers.
- Do not write raw stdout/stderr to docs or files.
- Do not invoke manifest writer.
- Do not write artifact or manifest files.

Alternative:

- An in-process call may be acceptable only if it reuses existing safe-metadata
  generation logic without broadening output surfaces.
- If an in-process call is selected in Step593, document why it is safer or
  simpler than a subprocess in the implementation notes.

Step592 does not implement either path.

## 10. Expected v0.4 Pass Output

Expected public-safe key-value metadata for the primary valid case:

- `mode=artifact_body_generation_runtime_integration`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_actual_controlled_safe_metadata_invocation`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `artifact_body_runtime_invoked=True`
- `artifact_body_runtime_invocation_planned=False`
- `artifact_body_runtime_mode=controlled_metadata_only_invocation`
- `artifact_body_generation_cli_invoked=True`
- `artifact_body_generation_cli_exit_code_category=zero`
- `artifact_body_generation_cli_output_scanned=True`
- `artifact_body_generation_cli_output_body_free=True`
- `artifact_body_payload_available=False`
- `artifact_body_payload_emitted=False`
- `artifact_body_payload_detected=False`
- `safe_metadata_body_available=True`
- `safe_metadata_body_field_count=<count-only value>`
- `content_suppressed=True`
- `body_suppressed=True`
- `summary_only=True`
- `request_body_detected=False`
- `pointer_body_detected=False`
- `expected_body_detected=False`
- `manifest_body_detected=False`
- `generated_policy_body_detected=False`
- `raw_stdout_body_suppressed=True`
- `raw_stderr_body_suppressed=True`
- `raw_rows_detected=False`
- `logits_detected=False`
- `probabilities_detected=False`
- `private_path_detected=False`
- `absolute_path_detected=False`
- `raw_learner_text_detected=False`
- `real_data_marker_detected=False`
- `performance_metric_body_detected=False`
- `file_writing_enabled=False`
- `file_writing_detected=False`
- `manifest_writer_invoked=False`
- `artifact_file_written=False`
- `manifest_file_written=False`
- `runtime_safety_scan_passed=True`
- `runtime_fail_closed=False`
- `residue_file_count=0`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`
- `metadata_file_count=7`
- `unsafe_signal_count=0`

## 11. Failure Mapping For Step593

### pass

- valid actual-controlled case
- v0.4 schema
- `artifact_body_runtime_invoked=True`
- controlled metadata-only invocation succeeds
- stdout/stderr scanned and body-free
- no unsafe markers
- no manifest writer
- no file writing
- no residue

### usage_error

- missing fixture root
- missing fixture case
- missing required metadata file
- malformed JSON
- unsupported fixture schema
- unsupported runtime schema
- unsupported mode
- missing `--actual-invocation` for v0.4 controlled mode
- `--actual-invocation` used with v0.1 / v0.2 / v0.3 mode
- missing `--summary-only`
- missing `--no-file-writing`
- missing `--no-manifest-writer`
- invalid mode / fixture mismatch

### fail_closed

- request body present
- pointer body present
- expected body present
- artifact body payload present
- manifest body present
- generated policy body present
- raw stdout/stderr body present
- raw rows present
- logits/probabilities present
- private/absolute path present
- raw learner text present
- real data marker present
- performance metric body present
- file writing requested/detected
- manifest writer requested/invoked
- unsafe artifact body runtime mode
- no-oracle forbidden field
- unsafe output residue risk
- artifact body CLI nonzero exit if unsafe or ambiguous
- artifact body CLI output not body-free
- unexpected artifact body generation request

### mismatch

- expected status mismatch
- expected reason mismatch
- expected field mismatch
- expected invocation flag mismatch
- expected count mismatch

## 12. Safety Scan Requirements

Step593 scan logic should cover:

- fixture metadata
- runtime request metadata
- pointer metadata
- artifact body generation CLI metadata
- captured stdout summary
- captured stderr summary
- expected runtime invocation summary
- residue policy metadata
- runtime output summary

The scan must detect only public-safe markers and suppress raw values.

It must verify:

- no request body values
- no pointer body values
- no expected body values
- no artifact body payload values
- no manifest body values
- no generated policy body values
- no raw stdout/stderr body values
- no raw rows
- no logits/probabilities
- no private/absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no file writing
- no manifest writer invocation
- no unexpected residue

## 13. Focused Tests For Step593

Future focused tests should include:

- v0.4 primary valid case passes
- v0.4 schema emitted
- v0.4 integration mode emitted
- `artifact_body_runtime_invoked=True`
- `artifact_body_runtime_invocation_planned=False`
- `artifact_body_runtime_mode=controlled_metadata_only_invocation`
- artifact body generation CLI invoked in controlled metadata-only mode
- CLI output scanned
- CLI output body-free flag true
- safe metadata body available true
- artifact body payload emitted false
- raw stdout/stderr body suppressed
- `manifest_writer_invoked=False`
- `file_writing_enabled=False`
- `residue_file_count=0`
- `unsafe_signal_count=0`
- unsupported schema maps to `usage_error`
- missing required metadata maps to `usage_error`
- malformed JSON maps to `usage_error`
- missing `--actual-invocation` maps to `usage_error`
- `--actual-invocation` with v0.3 planned-only mode maps to `usage_error`
- missing `--summary-only` maps to `usage_error`
- missing `--no-file-writing` maps to `usage_error`
- missing `--no-manifest-writer` maps to `usage_error`
- request body marker maps to `fail_closed`
- artifact body payload marker maps to `fail_closed`
- manifest body marker maps to `fail_closed`
- generated policy body marker maps to `fail_closed`
- raw stdout/stderr body marker maps to `fail_closed`
- private/absolute path marker maps to `fail_closed`
- raw learner text marker maps to `fail_closed`
- real data marker maps to `fail_closed`
- file writing requested/detected maps to `fail_closed`
- manifest writer requested/invoked maps to `fail_closed`
- CLI nonzero exit maps to `fail_closed` if unsafe or ambiguous
- mismatched expected status maps to `mismatch`
- v0.3 planned-only behavior remains unchanged
- v0.2 safe-metadata-smoke behavior remains unchanged
- v0.1 plan-only-bridge behavior remains unchanged
- actual-controlled fixture validator target still passes
- planned-only fixture validator target still passes
- artifact body generation safe-metadata CLI smoke still passes
- no fixture JSON mutation
- no residue files created

Use temporary copies for mutation tests.

## 14. Relationship To Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The future Step593 implementation:

- may add v0.4 runtime CLI behavior
- should not add a Makefile target yet
- should not alter existing Makefile targets
- should not add release-quality wrapper integration
- should not alter workflows
- should not alter fixture JSON
- should not invoke manifest writer
- should not write files

## 15. Step593 Implementation Plan

Step593 should:

- update `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- update focused tests in
  `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- add v0.4 schema constant
- add `artifact-body-runtime-invocation-controlled` mode
- add or enforce `--actual-invocation`
- preserve v0.1 / v0.2 / v0.3 behavior
- use Step587 actual-controlled fixture root
- validate the primary valid case
- invoke artifact body generation in controlled metadata-only mode
- capture and scan stdout/stderr summary
- emit public-safe key-value metadata only
- not add Makefile target
- not update release-quality wrapper
- not update workflows
- not modify fixture JSON
- update root README and full technical specification related docs because
  Step593 is an implementation step

## 16. Validation Commands For Step593

Step593 should run:

- direct v0.4 runtime CLI
- focused runtime tests
- actual-controlled fixture validator target
- actual-controlled direct fixture validator CLI
- planned-only fixture validator target
- planned-only v0.3 runtime target
- safe-metadata runtime target
- artifact body generation safe-metadata CLI smoke
- active root validator
- planned safe-metadata validator
- `make check-python`
- `PYTHONPATH=python python3 -m compileall python`
- fixture JSON diff check
- code/docs safety scan
- forbidden target diff check
- residue check

Do not run these in Step592 unless needed for docs safety.

## 17. Non-Equivalence Cautions

- implementation refinement design is not implementation
- future v0.4 pass will not prove runtime correctness generally
- future v0.4 pass will not prove artifact body payload correctness
- controlled metadata-only invocation is not production readiness
- planned-only v0.3 pass remains not actual invocation
- artifact body generation safe-metadata CLI smoke is not equivalent to
  actual-controlled runtime invocation
- count-only metadata is not free-form body safety proof
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 18. Non-Claims

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

## 19. Public-Safe Checklist

- [x] no raw logs
- [x] no full job output
- [x] no copied GitHub log blocks
- [x] no screenshots containing raw logs
- [x] no fixture JSON body
- [x] no request body
- [x] no pointer body
- [x] no expected body
- [x] no written file JSON body
- [x] no manifest body
- [x] no artifact body payload
- [x] no generated policy body
- [x] no raw stdout/stderr body
- [x] no raw rows
- [x] no logits/probabilities
- [x] no private paths
- [x] no absolute paths
- [x] no raw learner text
- [x] no real participant data
- [x] no performance claims
- [x] no production readiness claims
- [x] no real-data readiness claims

## 20. Recommended Next Step

Recommended next step:

- Step593: actual-controlled runtime implementation

Step593 should implement only direct runtime CLI behavior and focused tests. It
should not add a Makefile target, should not add release-quality wrapper
integration, should not change workflows, should not invoke manifest writer,
and should not enable file writing.

## Step593 Implementation Status

Step593 implements the direct v0.4 runtime CLI behavior in `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py` with mode `artifact-body-runtime-invocation-controlled` and `--actual-invocation`. The implementation keeps output public-safe / metadata-only / body-free / summary-only, preserves v0.1/v0.2/v0.3 behavior, and does not change Makefile, release-quality wrapper, workflows, fixture JSON, manifest writer integration, or file writing.

## Step594 Makefile Target Design Status

Step594 adds `docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_makefile_target_design.md` as a design-only plan for a future standalone Makefile target around the Step593 v0.4 runtime CLI. It does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.
