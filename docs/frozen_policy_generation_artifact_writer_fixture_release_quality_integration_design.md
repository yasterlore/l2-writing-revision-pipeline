# Frozen Policy Generation Artifact Writer Fixture Release-Quality Integration Design

## 1. Purpose

This document designs future release-quality wrapper integration for the
standalone artifact writer fixture validator target.

It is not a wrapper implementation. It does not implement an artifact writer,
generate artifact bodies, generate generated policy bodies, generate manifest
bodies, write files, compute metrics, evaluate performance, use real data, or
claim real-data readiness.

## 2. Current State

- The artifact writer fixture root exists.
- The artifact writer fixture validator module exists.
- The artifact writer fixture validator CLI exists.
- The artifact writer fixture validator Makefile target exists.
- The artifact writer fixture validator target is now included in the
  release-quality wrapper.
- The artifact writer implementation does not exist.
- The artifact writer runtime target does not exist.

Current standalone target:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-fixtures
```

The target validates 17 synthetic metadata-only artifact writer fixture cases
and emits a body-free fixture-root summary.

## 3. Proposed Wrapper Insertion Point

Recommended insertion point:

1. learner-state frozen policy generation scaffold fixture validation
2. learner-state frozen policy generation scaffold runtime smoke
3. learner-state frozen policy generation generator scaffold fixture validation
4. learner-state frozen policy generation generator scaffold runtime smoke
5. learner-state frozen policy generation artifact writer fixture validation
6. config and scoring smoke checks

The artifact writer fixture validator should run immediately after the
generator scaffold runtime smoke and before config and scoring smoke checks.

Reasons:

- The generator scaffold fixture and runtime checks establish the safe metadata
  contract that the artifact writer is designed to consume later.
- The artifact writer fixture contract belongs with frozen-policy-generation
  artifact checks, not with config or scoring smoke checks.
- The artifact writer runtime target does not exist yet, so only the fixture
  validator target should be staged.
- Success means fixture contract matching only. It is not artifact writer
  quality, artifact generation evidence, manifest generation evidence, or
  performance evidence.

## 4. Proposed Wrapper Command

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-fixtures
```

The wrapper should call the Makefile target instead of invoking the Python CLI
directly.

Reasons:

- The standalone target is already the shared developer and CI entrypoint.
- The wrapper stays readable.
- CLI arguments remain centralized in the Makefile target.
- Future target-level safety changes do not need duplicated wrapper edits.

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation artifact writer fixture validation
```

## 6. Expected Wrapper Behavior

If the target passes, release-quality should continue. If the target fails,
release-quality should fail.

Expected output includes:

- `mode=fixture_root`
- `total_cases=17`
- `valid_cases=3`
- `invalid_cases=14`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `manifest_body_suppression_checked=true`
- `output_path_safety_checked=true`
- validation schema version present

The output must remain safe metadata only. The target should not create tmp
output, write artifacts, write manifests, output artifact bodies, output
generated policy bodies, output manifest bodies, or provide performance
evidence.

## 7. Failure Interpretation

The following should be interpreted as release-quality failures:

- CLI usage failure
- missing fixture root
- missing required case file
- malformed JSON
- `total_cases` not equal to 17
- `matched_cases` not equal to 17
- `mismatched_cases` not equal to 0
- `input_error_cases` not equal to 0
- body, raw row, logit, or private path leakage
- `artifact_policy_checked=false`
- `body_suppression_checked=false`
- `file_writing_checked=false`
- `manifest_body_suppression_checked=false`
- `output_path_safety_checked=false`
- artifact body output
- generated policy body output
- manifest body output
- artifact writing
- manifest writing
- unexpected tmp output by this target
- internal error

These failures are fixture-contract or safety-check failures. They are not
artifact writer implementation failures, artifact quality failures, manifest
quality failures, generator quality failures, or performance failures.

## 8. Log Safety Review

Allowed in release-quality logs:

- target label
- command label
- mode
- total case count
- valid and invalid case counts
- matched, mismatched, and input-error counts
- reason-code counts
- safety flags
- validation schema version

Forbidden in release-quality logs and docs:

- artifact writer request body
- generator result pointer body
- expected artifact writer result body
- request body
- pointer body
- expected result body
- policy body
- generated policy body
- artifact body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metric body
- raw GitHub Actions logs
- full job output copied into docs

## 9. Relation to Existing Release-Quality Checks

- The generator scaffold fixture validation target validates the 18-case
  generator scaffold fixture contract.
- The generator scaffold runtime target validates one valid synthetic
  generator scaffold runtime smoke.
- The artifact writer fixture target validates the 17-case artifact writer
  fixture contract.
- The artifact writer runtime target does not exist yet.
- The artifact writer implementation does not exist yet.

Success for the proposed target is not artifact writer quality, artifact
generation evidence, manifest generation evidence, generated policy quality, or
performance evidence.

## 10. Makefile / Workflow Status

- The Makefile target already exists.
- The release-quality wrapper now includes this target as of Step310.
- GitHub Actions workflow YAML is not changed by this document.
- If the workflow already calls the release-quality wrapper, future integration
  should only need the wrapper change when possible.
- Workflow YAML diffs should remain none unless a separate requirement appears.

## 11. Testing Plan for Future Implementation

Future wrapper implementation should verify:

- standalone target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- output includes `mode=fixture_root`
- output includes `total_cases=17`
- output includes `matched_cases=17`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes the required safety flags
- no request, pointer, expected, artifact, policy, or manifest body leakage
- no raw row, logit, or private path leakage
- no tmp output
- no artifact writing
- no manifest writing
- wrapper diff is limited
- workflow diff is none
- all Python tests pass
- all existing checks pass

## 12. Release-Quality Status Marker Future

After wrapper integration and a remote or manual Release Quality success, a
future status marker may record pass-only and count-only metadata.

A future marker may record:

- target included: yes or no
- `total_cases=17`
- `valid_cases=3`
- `invalid_cases=14`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- safety flags

The marker must not copy raw logs, request bodies, pointer bodies, expected
result bodies, policy bodies, artifact bodies, manifest bodies, raw rows,
logits, private paths, raw learner text, or performance metric bodies.

## 13. No-Oracle / Synthetic-Only Boundary

The target uses synthetic fixture metadata only.

It must not use:

- real data
- participant data
- raw learner text
- final, gold, or observed-after text
- expected-action scoring feedback
- test-derived tuning payloads
- artifact bodies
- generated policy bodies
- manifest bodies
- logits
- raw rows
- private paths

## 14. What This Does NOT Do

This document does not:

- change workflow YAML
- change the Makefile
- change Python code or tests
- change fixture JSON
- execute an artifact writer
- write artifacts
- write manifests
- generate policy bodies
- generate artifact bodies
- generate manifest bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project-level safety check wrapper. It runs a curated
set of validation commands before a change is treated as release-ready.

A standalone Makefile target is useful first because it proves the check can be
run locally with one short command. After that, release-quality can call the
same command instead of duplicating the CLI details.

A fixture validator target checks that fixture files match an expected
contract. A runtime smoke target runs runtime code on a small safe input. This
artifact writer target is only a fixture validator target. It does not run an
artifact writer.

It is still useful before the artifact writer implementation because the
fixtures define the safety contract the future writer must satisfy. Passing the
target only means that the contract is internally consistent and body-free.

A status marker should be a later step because it should record a real
remote/manual Release Quality result after wrapper integration, using only
pass-only and count-only metadata.

## 16. Next Recommended Steps

Recommended next steps:

1. Step311: remote/manual run record workflow design. Complete:
   [Frozen policy generation artifact writer fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_record_workflow.md).
2. Step312: remote/manual run status marker.
3. Keep artifact writer implementation separate.

## 17. Step310 Wrapper Integration Status

Step310 implements the minimal release-quality wrapper integration in:

`scripts/check_release_quality.sh`

The wrapper now runs:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-fixtures
```

with the label:

```text
release_quality_check: learner-state frozen policy generation artifact writer fixture validation
```

The section is placed immediately after learner-state frozen policy generation
generator scaffold runtime smoke and before config and scoring smoke checks.

Step310 does not change GitHub Actions workflow YAML, Makefile target behavior,
Python code, Python tests, fixture JSON, artifact writer implementation,
artifact body generation, generated policy body generation, manifest body
generation, artifact file writing, manifest file writing, metric computation,
performance evaluation, real-data use, or production readiness.

## 18. Step311 Remote Run Record Workflow Design Status

Step311 designs the future public-safe recording workflow for a remote/manual
Release Quality run that includes artifact writer fixture validation:
[Frozen policy generation artifact writer fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_record_workflow.md).

The actual status marker is not created in Step311. The workflow design records
only pass-only/count-only metadata and keeps raw logs, request/pointer/expected
bodies, policy bodies, generated policy bodies, artifact bodies, manifest
bodies, raw rows, logits, private paths, raw learner text, and performance
metric bodies out of docs.

## Related Documents

- [Frozen policy generation artifact writer fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md)
- [Frozen policy generation artifact writer fixture validator design](frozen_policy_generation_artifact_writer_fixture_validator_design.md)
- [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
