# Frozen Policy Generation Artifact Writer Runtime Release-Quality Integration Design

## 1. Purpose

This document designs future release-quality wrapper integration for the
standalone frozen policy generation artifact writer runtime Makefile target.

Step318 created this as a docs-only design. Step319 implements the wrapper
integration described here. The implementation does not change GitHub Actions
workflows, change the Makefile, change Python code, change tests, change
fixture JSON, generate artifact bodies, generate generated policy bodies,
generate manifest bodies, write files, compute metrics, evaluate performance,
or claim real-data readiness.

The goal is to define where and how
`check-learner-state-frozen-policy-generation-artifact-writer-runtime` enters
`make check-release-quality` safely.

## 2. Current State

- The artifact writer metadata-only skeleton exists.
- The artifact writer CLI exists.
- The artifact writer runtime Makefile target exists.
- The artifact writer fixture validator target is already included in
  release-quality.
- The artifact writer runtime target is included in release-quality as of
  Step319.
- Artifact body generation does not exist.
- Manifest generation does not exist.
- Artifact file writing and manifest file writing do not exist.

Current standalone runtime target:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

Current standalone target behavior is metadata-only:

- uses one valid synthetic fixture
- `mode=artifact_writer`
- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- artifact body unavailable or suppressed
- manifest body unavailable or suppressed
- artifact writing false
- manifest writing false
- no generated policy body output
- no raw rows
- no logits
- no private paths
- no performance metric body
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
- no target-specific tmp output
- no artifact file
- no manifest file
- no performance evidence

## 3. Proposed Wrapper Insertion Point

Recommended insertion point:

- immediately after artifact writer fixture validation
- before config and scoring smoke checks

Recommended relevant order:

1. learner-state frozen policy generation generator scaffold fixture validation
2. learner-state frozen policy generation generator scaffold runtime smoke
3. learner-state frozen policy generation artifact writer fixture validation
4. learner-state frozen policy generation artifact writer runtime smoke
5. config and scoring smoke checks

Reasons:

- Fixture contract validation should run before runtime smoke.
- Artifact writer runtime smoke is easier to interpret after generator
  scaffold checks and artifact writer fixture validation.
- Frozen-policy-generation artifact writer checks remain grouped before the
  separate config and scoring smoke checks.
- Success means artifact writer runtime safe pass only. It is not artifact
  generation evidence, manifest generation evidence, artifact writer quality
  evidence, model performance evidence, or real-data readiness evidence.

## 4. Proposed Wrapper Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

The wrapper should call the Makefile target instead of invoking the Python CLI
directly.

Reasons:

- The standalone target is already the shared developer entrypoint.
- The wrapper stays readable.
- Long CLI arguments remain centralized in the Makefile.
- Future target-local command changes remain localized to the Makefile.

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation artifact writer runtime smoke
```

The label should say `runtime smoke`, not writer quality, artifact generation,
manifest generation, model evaluation, calibration, or real-data readiness.

## 6. Expected Wrapper Behavior

If the target passes, release-quality should continue. If the target fails,
release-quality should fail.

Expected output includes:

- `mode=artifact_writer`
- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`
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
- artifact body suppressed or unavailable
- manifest body suppressed or unavailable
- artifact writing false
- manifest writing false

The output must remain safe metadata only. The target should not create tmp
output, write artifacts, write manifests, output artifact bodies, output
generated policy bodies, output manifest bodies, or provide performance
evidence.

## 7. Failure Interpretation

The following should be interpreted as release-quality failures:

- missing request path
- missing pointer path
- malformed JSON
- CLI usage failure
- `writer_status` not equal to `pass` for the selected valid runtime fixture
- `reason_codes` not equal to `none`
- `failed_checks` not equal to `none`
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

These failures are runtime smoke or safety-boundary failures. They are not
artifact writer implementation quality failures, artifact generation quality
failures, manifest quality failures, model performance failures, or real-data
readiness failures.

## 8. Log Safety Review

Allowed in release-quality logs:

- target label
- command label
- `mode`
- `writer_status`
- `reason_codes`
- `failed_checks`
- safe request, pointer, artifact, and manifest IDs
- artifact flags
- safety flags
- count summary
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

- Artifact writer fixture validation validates the 17-case artifact writer
  fixture contract.
- Artifact writer runtime smoke runs one valid synthetic request/pointer pair.
- Generator scaffold fixture validation validates the 18-case generator
  scaffold fixture contract.
- Generator scaffold runtime smoke runs one valid synthetic generator scaffold
  fixture.
- Runtime scaffold fixture validation validates the 11-case runtime scaffold
  fixture contract.
- Runtime scaffold smoke runs one valid synthetic runtime scaffold fixture.

Success for the proposed target is not artifact writer quality, artifact
generation evidence, manifest generation evidence, generated policy quality,
or performance evidence.

## 10. Makefile / Workflow Status

- The Makefile runtime target already exists.
- The release-quality wrapper is not yet changed for this runtime target.
- GitHub Actions workflow YAML should not need a change if the workflow already
  calls the release-quality wrapper.
- Future implementation should modify only the wrapper when possible.
- Workflow YAML diffs should remain none unless a separate requirement appears.

## 11. Testing Plan for Future Implementation

Future wrapper implementation should verify:

- standalone runtime target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- output includes `mode=artifact_writer`
- output includes `writer_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes required safety flags
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
- `mode=artifact_writer`
- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- artifact writing false
- manifest writing false
- artifact body suppressed true
- manifest body suppressed true
- safety flags

The marker must not copy raw logs, request bodies, pointer bodies, expected
result bodies, policy bodies, artifact bodies, manifest bodies, raw rows,
logits, private paths, raw learner text, or performance metric bodies.

## 13. No-Oracle / Synthetic-Only Boundary

The target uses one valid synthetic fixture's metadata only.

It must not use:

- real data
- participant data
- raw learner text
- final, gold, or observed-after text
- expected action scoring feedback
- test-derived tuning payload
- artifact body
- generated policy body
- manifest body
- logits
- raw rows
- private paths

## 14. What This Does NOT Do

This design does not:

- change workflow YAML
- generate artifact bodies
- write artifacts
- generate manifest bodies
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project's larger safety/check wrapper. Adding a target
there means the target becomes part of the normal release-quality gate.

The standalone runtime target comes first so its command and output can be
reviewed by itself. After that, release-quality integration can safely reuse
the same target rather than duplicating the long CLI command.

The fixture validator target and runtime smoke target are different. The
fixture validator checks the 17-case expected metadata contract. The runtime
smoke target runs one valid request/pointer pair through the writer CLI and
checks that the terminal path returns a safe pass summary.

The runtime smoke uses one valid fixture because broad valid and invalid
coverage already lives in tests and fixture validation. The smoke target is a
fast command-boundary check.

Success is not artifact writer quality. It only means the metadata-only
runtime command returned a safe pass summary for one synthetic fixture. It
does not prove artifact generation, manifest generation, performance, or
production readiness.

The status marker remains a separate step because remote/manual run metadata
should be recorded only after wrapper integration actually lands and passes.

## 16. Next Recommended Steps

- Step321 remote/manual run status marker

## 17. Step319 Runtime Release-Quality Wrapper Integration Status

Step319 implements the wrapper integration designed here. The
release-quality wrapper now runs:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

The section is placed immediately after artifact writer fixture validation and
before config and scoring smoke checks. Its label is:

```text
release_quality_check: learner-state frozen policy generation artifact writer runtime smoke
```

This integration keeps the runtime smoke metadata-only. It does not change
workflow YAML, change the Makefile, change Python code or tests, change
fixture JSON, generate artifact bodies, generate generated policy bodies,
generate manifest bodies, write artifact or manifest files, compute metrics,
use real data, or claim real-data readiness.

The runtime smoke success is interpreted only as a safe terminal-path pass for
one valid synthetic request/pointer pair. It is not artifact writer quality,
artifact generation quality, manifest generation quality, performance
evidence, real-data readiness, or production readiness.

## 18. Step320 Remote Run Record Workflow Design Status

Step320 designs the future remote/manual Release Quality run recording
workflow for this runtime smoke:

[Frozen policy generation artifact writer runtime release-quality remote run record workflow](frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_record_workflow.md).

The Step320 workflow design does not create the status marker, run a remote
workflow, change workflow YAML, change this wrapper integration, change the
Makefile, change Python code or tests, change fixture JSON, generate artifact
bodies, generate generated policy bodies, generate manifest bodies, write
artifact or manifest files, compute metrics, use real data, or claim
real-data readiness.

The future marker path is:

`docs/status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md`

## 19. Step321 Runtime Status Marker Creation Status

Step321 creates that public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md).

The marker records only safe run identity metadata, pass-only artifact writer
runtime smoke fields, count-only fixture validation fields, related
learner-state check summaries, and safety review statements. It does not
change workflow YAML, change the wrapper, change Makefile targets, change
Python code or tests, change fixture JSON, generate artifact bodies, generate
generated policy bodies, generate manifest bodies, write artifact or manifest
files, compute metrics, use real data, or claim real-data readiness.

## 20. Step322 Artifact Body Generation Design Status

Step322 designs future artifact body generation as a separate docs-only
boundary:

[Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md).

Release-quality remains unchanged in Step322. Artifact body generation should
not be added to release-quality until separate body fixtures, validation, CLI
behavior, Makefile target design, and log safety review exist. Step322 does
not generate bodies, write files, change workflow YAML, change wrapper
scripts, change Makefile targets, change Python code or tests, change fixture
JSON, compute metrics, use real data, or claim production readiness.
