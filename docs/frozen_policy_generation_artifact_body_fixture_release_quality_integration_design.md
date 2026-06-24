# Frozen Policy Generation Artifact Body Fixture Release-Quality Integration Design

## 1. Purpose

This document designs future release-quality integration for the frozen policy
generation artifact body fixture validator target.

This is a docs-only design. It is not a wrapper implementation, not a
workflow change, not artifact body generation implementation, not file
writing, not performance evaluation, and not a real-data readiness claim.

The design keeps the boundary synthetic-only, metadata-only, and no-oracle.
It defines the proposed wrapper insertion point, command, label, expected
safe behavior, failure interpretation, log safety, testing plan, and future
status marker policy.

## 2. Current State

- Artifact body fixtures exist.
- The artifact body fixture validator API exists.
- The artifact body fixture validator CLI exists.
- CLI tests exist.
- The standalone Makefile target exists.
- The standalone Makefile target passes.
- Release-quality integration does not exist.
- Artifact body generation does not exist.
- Manifest body generation does not exist.
- Artifact file writing does not exist.
- Manifest file writing does not exist.

Current standalone target:

`make check-learner-state-frozen-policy-generation-artifact-body-fixtures`

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body`

The fixture root contains 18 synthetic metadata cases: 4 valid cases and 14
invalid expected fail-closed cases.

## 3. Proposed Wrapper Insertion Point

Candidate A:

Insert artifact body fixture validation immediately after artifact writer
runtime smoke and before config/scoring smoke checks.

Candidate B:

Insert artifact body fixture validation immediately after artifact writer
fixture validation and before artifact writer runtime smoke.

Candidate C:

Insert artifact body fixture validation after config/scoring smoke checks.

Recommended insertion point:

Candidate A, after artifact writer runtime smoke and before config/scoring
smoke checks.

Expected future order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- config and scoring smoke checks

Reasons:

- Artifact writer fixture validation and artifact writer runtime smoke should
  pass before checking the artifact body boundary fixtures.
- The frozen policy generation artifact writer safety checks can close before
  the separate config/scoring smoke checks begin.
- Artifact body fixture validation is not artifact body generation, but it is
  easier to read when placed immediately after the writer runtime smoke.
- Config/scoring smoke checks are a separate subsystem, so the artifact
  writer and artifact body checks should stay grouped before them.

## 4. Proposed Wrapper Command

Future wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-body-fixtures
```

## 5. Proposed Wrapper Label

Recommended wrapper label:

```text
release_quality_check: learner-state frozen policy generation artifact body fixture validation
```

## 6. Expected Wrapper Behavior

The future wrapper behavior should be:

- target pass -> release-quality continues
- target fail -> release-quality fails
- output remains safe metadata only
- no tmp output is created by this target
- no artifact file is created
- no manifest file is created
- no artifact body payload is emitted
- no generated policy body is emitted
- no manifest body is emitted
- no performance evidence is emitted

Expected target output includes:

- `mode=fixture_root`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1`
- `total_cases=18`
- `valid_cases=4`
- `invalid_cases=14`
- `matched_cases=18`
- `mismatched_cases=0`
- `input_error_cases=0`
- count-only `reason_code_counts`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `artifact_body_audit_checked=true`
- `request_body_count=0`
- `pointer_body_count=0`
- `expected_body_count=0`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `manifest_body_count=0`

## 7. Failure Interpretation

The future release-quality wrapper should fail if any of these occur:

- missing fixture root
- missing fixture file
- malformed JSON
- unexpected fixture file
- validation mismatch
- `input_error_cases > 0`
- `mismatched_cases > 0`
- `matched_cases != 18`
- `total_cases != 18`
- `valid_cases != 4`
- `invalid_cases != 14`
- safety flag false
- `request_body_count > 0`
- `pointer_body_count > 0`
- `expected_body_count > 0`
- `raw_row_count > 0`
- `logits_dump_count > 0`
- `private_path_count > 0`
- `performance_metric_count > 0`
- `manifest_body_count > 0`
- artifact body payload leakage
- generated policy body leakage
- manifest body leakage
- raw learner text leakage
- private path leakage
- internal error

These failures mean the fixture validation contract or safety boundary failed.
They do not mean artifact body generator quality failed, artifact writer
quality failed, or model performance failed.

## 8. Log Safety Review

Future wrapper logs may include:

- label
- command
- mode
- validation schema version
- total, valid, invalid, matched, mismatched, and input-error counts
- count-only reason code counts
- safety flags
- zero counts
- schema names

Future wrapper logs must not include:

- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- `expected_artifact_body_result` body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- expected action payload
- scoring feedback payload
- performance metric body
- GitHub raw logs
- full job output copied into docs

Docs must not copy raw wrapper logs or full job output.

## 9. Relation To Existing Release-Quality Checks

- Artifact writer fixture validation validates the writer result metadata
  contract.
- Artifact writer runtime smoke runs the writer CLI on one valid synthetic
  request/pointer pair.
- Artifact body fixture validation validates artifact body boundary fixtures.
- Artifact body fixture validation does not generate artifact bodies.
- Artifact body fixture validation does not validate artifact body generator
  quality.
- Generator scaffold checks remain separate.
- Config/scoring smoke checks remain separate.
- Success is not artifact generation evidence.
- Success is not manifest generation evidence.
- Success is not performance evidence.
- Success is not real-data readiness.

## 10. Makefile And Workflow Status

- The Makefile target already exists.
- The release-quality wrapper is not changed yet.
- Workflow YAML should not need changes if the workflow already calls the
  release-quality wrapper.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML diff should remain none unless a concrete wrapper invocation
  gap is discovered.

## 11. Testing Plan For Future Implementation

Future wrapper integration should verify:

- standalone target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- output includes `mode=fixture_root`
- output includes `total_cases=18`
- output includes `matched_cases=18`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes safety flags
- output includes zero counts
- no request, pointer, expected, artifact, or manifest body leakage
- no raw rows, logits, or private path leakage
- no tmp output from this target
- no artifact writing
- no manifest writing
- wrapper diff is limited
- workflow diff is none
- all Python tests pass
- all existing checks pass

## 12. Release-Quality Status Marker Future

After wrapper integration and remote/manual Release Quality success, a future
status marker may be added.

The status marker should record pass-only and count-only metadata. It must
not copy raw logs.

Artifact body fixture validation status can record:

- target included yes/no
- `mode=fixture_root`
- `total_cases=18`
- `valid_cases=4`
- `invalid_cases=14`
- `matched_cases=18`
- `mismatched_cases=0`
- `input_error_cases=0`
- count-only reason code counts
- safety flags
- zero counts

The status marker must not record request bodies, pointer bodies, expected
result bodies, artifact bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

## 13. No-Oracle And Synthetic-Only Boundary

The future release-quality target uses synthetic fixture metadata only.

It must not use:

- real data
- participant data
- raw learner text
- final text
- gold labels
- observed-after text
- expected action payloads
- scoring feedback payloads
- artifact body payloads
- generated policy bodies
- manifest bodies
- logits
- raw rows
- private paths

## 14. What This Does Not Do

This design does not:

- integrate the wrapper
- change workflow YAML
- change the Makefile
- change Python code or tests
- change fixture JSON
- generate artifact bodies
- write artifacts
- generate manifest bodies
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project command bundle used to check whether the
repository is in a broadly safe state before release-style work continues.

The standalone target exists first so it can be verified by itself. Adding it
to release-quality later makes the broader check run the same safe command
automatically.

Artifact writer fixture validation checks expected writer metadata contracts.
Artifact writer runtime smoke checks that the writer CLI can safely run one
valid synthetic request/pointer pair. Artifact body fixture validation checks
the boundary for future artifact body generation fixtures. It does not create
artifact bodies.

Invalid fixtures can still be part of a passing release-quality check because
they are expected fail-closed cases. A pass means the validator returned the
expected safe metadata for those unsafe synthetic markers.

Success is not artifact body generation evidence because no artifact body is
generated. It is only evidence that the fixture validator boundary stayed
safe.

The remote/manual status marker stays separate so a later GitHub Actions run
can be recorded with public-safe pass-only and count-only metadata, without
copying logs.

## 16. Next Recommended Steps

- Step333 artifact body fixture validator remote/manual run record workflow
  design
- Step334 artifact body fixture validator remote/manual run status marker

Artifact body generation remains separate.

## 17. Step331 Status

Step331 creates this docs-only artifact body fixture release-quality
integration design. It does not change the release-quality wrapper, change
workflow YAML, change the Makefile, change Python code or tests, change
fixture JSON, implement artifact body generation, generate policy bodies,
generate manifest bodies, write files, compute metrics, use real data, or
claim production readiness.

## 18. Step332 Implementation Status

Step332 integrates the standalone artifact body fixture validator target into
the release-quality wrapper immediately after artifact writer runtime smoke
and before config/scoring smoke checks.

The wrapper label is:

`release_quality_check: learner-state frozen policy generation artifact body fixture validation`

The wrapper command is:

`make check-learner-state-frozen-policy-generation-artifact-body-fixtures`

This integration makes `make check-release-quality` validate the artifact
body fixture boundary contract as part of the normal release-quality command
bundle. It remains synthetic-only, metadata-only, and no-oracle.

Step332 does not change workflow YAML, change the Makefile, change Python code
or tests, change fixture JSON, implement artifact body generation, generate
policy bodies, generate manifest bodies, write artifact or manifest files,
add output-file options, compute metrics, use real data, or claim production
readiness.

## Related Documents

- [Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body fixture validator design](frozen_policy_generation_artifact_body_fixture_validator_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
