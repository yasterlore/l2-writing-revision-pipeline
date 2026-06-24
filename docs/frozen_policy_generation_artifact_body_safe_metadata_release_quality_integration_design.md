# Frozen Policy Generation Artifact Body Safe-Metadata Release-Quality Integration Design

## 1. Purpose

This document designs a future release-quality wrapper integration for the
standalone safe-metadata artifact body generation Makefile target.

This is a docs-only design. It is not wrapper implementation, not workflow
change, not artifact file writing, not a manifest writer, not artifact writer
CLI integration, not performance evaluation, and not a real-data readiness
claim.

The goal is to define where and how the safe-metadata CLI smoke could be
included in `make check-release-quality` while preserving synthetic-only,
metadata-only, no-oracle, body-free output boundaries.

## 2. Current State

- Artifact body generation API exists.
- Artifact body generation CLI exists.
- Default suppressed Makefile target exists.
- Default suppressed target is included in release-quality.
- Safe-metadata Makefile target exists.
- Safe-metadata target passes standalone.
- Safe-metadata target is not included in release-quality.
- Artifact file writing does not exist.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

The standalone safe-metadata target is:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

## 3. Proposed Wrapper Insertion Point

Candidate A: after the default suppressed artifact body generation CLI smoke
and before config/scoring smoke checks.

Candidate B: after artifact body fixture validation and before the default
suppressed generation smoke.

Candidate C: after config/scoring smoke checks.

Recommendation: Candidate A.

Recommended order:

1. artifact writer fixture validation
2. artifact writer runtime smoke
3. artifact body fixture validation
4. artifact body generation CLI smoke
5. artifact body generation safe-metadata CLI smoke
6. config and scoring smoke checks

Rationale:

- The order reads naturally as fixture validation, suppressed generation
  smoke, then safe-metadata generation smoke.
- The suppressed smoke remains the minimal safe path; safe-metadata becomes
  an additional safe path.
- Config/scoring smoke checks are separate and should remain after the
  artifact body generation safety checks.
- The safe-metadata smoke still does not write artifact files or manifest
  files, so it can be treated as a safe metadata-only smoke check.

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation artifact body generation safe-metadata CLI smoke`

## 6. Expected Wrapper Behavior

Expected wrapper behavior:

- target pass continues release-quality
- target fail fails release-quality
- output includes `mode=artifact_body_generation`
- output includes `body_status=generated_safe_metadata_body`
- output includes `generation_status=pass`
- output includes `validation_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes `artifact_file_written=false`
- output includes `manifest_file_written=false`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `no_logits_dump=true`
- output includes `no_private_paths=true`
- output includes `no_performance_claims=true`
- output includes `synthetic_only_checked=true`
- output includes `no_oracle_checked=true`
- output includes `artifact_policy_checked=true`
- output includes `body_suppression_checked=true`
- output includes `raw_row_count=0`
- output includes `logits_dump_count=0`
- output includes `private_path_count=0`
- output includes `performance_metric_count=0`
- output includes `request_body_count=0`
- output includes `pointer_body_count=0`
- output includes `expected_body_count=0`
- output includes `manifest_body_count=0`
- output is safe metadata only
- no artifact body payload is printed
- no request body is printed
- no pointer body is printed
- no generated policy body is printed
- no manifest body is printed
- no artifact file is written
- no manifest file is written
- no performance evidence is emitted

The target may report that safe metadata is available as a summary flag. That
does not permit printing the artifact body payload.

## 7. Failure Interpretation

The following should fail release-quality:

- missing safe-metadata request fixture
- missing safe-metadata pointer fixture
- malformed JSON
- unknown request or pointer schema
- CLI usage error
- safety audit fail-closed result
- internal error
- `body_status` is not `generated_safe_metadata_body`
- `generation_status` is not `pass`
- `validation_status` is not `pass`
- `reason_codes` is not `none`
- `failed_checks` is not `none`
- `artifact_file_written` is true
- `manifest_file_written` is true
- any required safety flag is false
- `raw_row_count > 0`
- `logits_dump_count > 0`
- `private_path_count > 0`
- `performance_metric_count > 0`
- `request_body_count > 0`
- `pointer_body_count > 0`
- `expected_body_count > 0`
- `manifest_body_count > 0`
- artifact body payload leakage
- request body leakage
- pointer body leakage
- generated policy body leakage
- manifest body leakage
- raw learner text leakage
- private path leakage

These failures indicate the safe-metadata release-quality smoke check failed.
They do not prove artifact body generation correctness failure, artifact
writer correctness failure, model performance failure, or production
readiness failure.

## 8. Log Safety Review

Allowed in logs:

- label
- command
- mode
- safe IDs
- body status
- generation status
- validation status
- reason code names
- failed check names
- safety flags
- count summary
- file-written false flags
- safe summary label

Forbidden in logs:

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

## 9. Relation To Existing Release-Quality Checks

- Artifact body fixture validation validates 18 body boundary fixture
  contracts.
- Default suppressed generation CLI smoke validates one suppressed-mode,
  body-free generation path.
- Safe-metadata generation CLI smoke would validate one safe-metadata,
  body-free generation path.
- Safe-metadata smoke does not print body payload.
- Safe-metadata smoke does not write files.
- Safe-metadata smoke does not prove artifact body correctness.
- Artifact writer runtime remains separate.
- Manifest writer remains separate.
- Config/scoring smoke remains separate.

## 10. Makefile / Workflow Status

- The safe-metadata Makefile target already exists.
- The release-quality wrapper is not changed by this document.
- Workflow YAML is not changed by this document.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML diff should remain empty unless a future requirement makes it
  unavoidable.

## 11. Testing Plan For Future Implementation

Future implementation should verify:

- standalone safe-metadata target passes
- `make check-release-quality` includes the new safe-metadata label
- `make check-release-quality` passes
- output includes `body_status=generated_safe_metadata_body`
- output includes `generation_status=pass`
- output includes `validation_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes file-written false flags
- output includes safety flags
- output includes zero counts
- no request body leakage
- no pointer body leakage
- no artifact body payload leakage
- no manifest body leakage
- no raw row leakage
- no logits leakage
- no private path leakage
- no temporary output from this target
- no artifact writing
- no manifest writing
- wrapper diff is limited
- workflow diff is empty
- all Python tests pass
- all existing checks pass

## 12. Release-Quality Status Marker Future

After wrapper integration and a successful remote/manual Release Quality run,
a future status marker may be added.

The future marker should record pass-only and count-only metadata. Raw logs
must not be copied.

Safe-metadata CLI smoke status can record:

- target included yes/no
- label
- command
- `body_status=generated_safe_metadata_body`
- `generation_status=pass`
- `validation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `artifact_file_written=false`
- `manifest_file_written=false`
- safety flags
- zero counts

The marker must not record request bodies, pointer bodies, artifact body
payloads, generated policy bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

## 13. No-Oracle / Synthetic-Only Boundary

- The target uses one synthetic metadata request/pointer pair.
- It uses no real data.
- It uses no participant data.
- It includes no raw learner text.
- It includes no final, gold, or observed-after text.
- It includes no expected action payload.
- It includes no scoring feedback payload.
- It includes no artifact body payload.
- It includes no generated policy body.
- It includes no manifest body.
- It includes no logits.
- It includes no raw rows.
- It includes no private paths.

## 14. What This Does Not Do

This document does not:

- integrate the wrapper
- change workflow YAML
- change Makefile
- change Python code or tests
- change fixture JSON
- generate printable artifact body payload
- write artifacts
- generate manifest bodies
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project's combined safety and regression check. Adding
a target to it means the target runs whenever the normal release-quality
bundle runs.

The standalone target comes first because it lets the project verify the
command and its log safety before making it part of the larger bundle.

Suppressed mode is the smallest generation path: it confirms the CLI can run
while keeping the artifact body unavailable. Safe-metadata mode exercises a
broader path where safe metadata is available internally, but stdout/stderr
still stay summary-only and body-free.

Even in safe-metadata mode, the artifact body payload should not be printed.
Release-quality logs are not the place to inspect bodies.

Success means one synthetic safe-metadata smoke path produced a safe summary.
It does not prove artifact body correctness, artifact writer correctness,
model performance, real-data readiness, or production readiness.

## 16. Next Recommended Steps

- Step347: safe-metadata release-quality wrapper integration
- Step348: safe-metadata remote/manual run record workflow design
- Step349: safe-metadata remote/manual run status marker

Artifact file writing, manifest writer, output file options, artifact writer
CLI integration, and real-data readiness remain separate future work.
