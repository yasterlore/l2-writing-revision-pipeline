# Frozen Policy Generation Manifest Writer Metadata-Only File Writing Boundary Design

## 1. Purpose

This document fixes the boundary for future metadata-only manifest file
writing by the frozen policy generation manifest writer.

It is a docs-only boundary design. It is not an implementation, not fixture
creation, not release-quality integration, not artifact writer CLI
integration, not manifest body generation, and not a production readiness
claim.

The goal is to define the path policy, safe root, allowed file content,
forbidden content, failure behavior, fixture staging, validator staging,
isolated write staging, and release-quality staging before any file-writing
code is added.

## 2. Current State

- the manifest writer runtime module exists
- the runtime CLI exists
- the runtime Makefile target exists
- the runtime smoke target is in release-quality
- the runtime remote status marker exists
- the current runtime supports metadata-only no-file behavior only
- `--manifest-out` is not implemented as a supported output feature
- passing `--manifest-out` fails closed today
- manifest file writing does not exist
- manifest body generation does not exist
- artifact writer CLI integration does not exist

## 3. Proposed Future File Writing Mode

The initial future file-writing mode should write only metadata-only manifest
files.

It should not write:

- manifest body
- artifact body payload
- generated policy body
- request body
- pointer body
- expected result body
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- real participant data
- performance metric body

The written file should contain only safe manifest metadata, safe synthetic
IDs, safe reference counts or reference IDs, safety flags, count summary, and
safe summary fields.

## 4. Proposed Future CLI Expansion

Future CLI arguments may include:

- `--manifest-out`
- optional future `--overwrite-policy`

This step does not implement either argument. The current no-file runtime
behavior remains unchanged.

## 5. Safe Output Root Policy

Recommended safe root:

`tmp/frozen_policy_generation_manifest/`

Allowed output path behavior:

- output path is under the safe root
- relative path only
- `.json` extension only
- simple filename or safe subdirectory
- no overwrite unless an explicit overwrite policy allows it
- parent directory auto-create only inside the safe root

Forbidden output path behavior:

- absolute path
- parent traversal
- home path
- cloud/private marker path
- hidden private directory
- non-JSON extension
- too-long path
- unsafe filename
- normalized path outside the safe root
- symlink-sensitive output
- private path marker
- local user path
- absolute temp path in public output

The public summary should never print an absolute resolved path. It should
use safe relative path metadata or count-only fields.

## 6. Metadata-Only File Content Policy

Allowed fields:

- schema/version
- manifest ID
- artifact ID
- artifact body ID
- manifest writer mode
- validation reference IDs or count
- release-quality reference IDs or count
- safety flags
- count summary
- safe summary
- file-writing metadata, such as file written true in the result summary

Forbidden fields:

- manifest body
- manifest JSON body nesting
- artifact body payload
- generated policy body
- request body
- pointer body
- expected body
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- final text
- observed-after text
- gold labels
- scoring feedback payload
- real participant data
- performance metric body

## 7. Future Result Behavior

When metadata-only file writing succeeds:

- writer status is pass
- manifest writer mode is `metadata_only_file`
- runtime writer executed is true
- manifest body available is false
- manifest file written is true
- manifest output path available is true
- written file count is 1
- release-quality ready is false initially
- content suppressed is true
- manifest body suppressed is true
- body/payload/raw/logit/private/absolute safety flags remain true

When no-file mode is used, the existing metadata-only no-file behavior should
remain unchanged.

## 8. Fail-Closed Behavior

Future file writing should fail closed if:

- output path is unsafe
- output path is absolute
- output path uses parent traversal
- output path has a non-JSON extension
- overwrite is attempted without an explicit policy
- output would resolve outside the safe root
- manifest body is requested
- artifact body payload is detected
- generated policy body is detected
- raw rows are detected
- logits are detected
- private path marker is detected
- raw learner text is detected
- request body nesting is detected
- pointer body nesting is detected
- expected body nesting is detected
- real data marker is detected
- file content would include forbidden fields
- cleanup or residue check fails

Failure summaries should remain body-free and path-safe.

## 9. Fixture Staging

Future fixture root proposal:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/`

Future case categories:

- `pass_metadata_file_written`
- `pass_metadata_no_file`
- `usage_error_no_write`
- `fail_closed_no_write`

Required files proposal:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_file_writing_result.json`

The future fixtures should remain synthetic-only, metadata-only, and
no-oracle. They should not include body payloads or private paths.

## 10. Validator Staging

Future validator module proposal:

`learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation`

Purpose:

- validate file-writing fixture contracts statically
- not write files
- check path policy
- check content policy
- check no-oracle and synthetic-only notices
- check expected result contracts
- emit count-only body-free summaries

## 11. Isolated Write Staging

Future isolated write validation should:

- write only to a temporary isolated safe root
- verify output file count
- verify parseable JSON
- verify forbidden field count is 0
- verify cleanup and residue count is 0
- avoid printing raw body content to stdout or stderr

The isolated write target should be separate from static fixture validation
and separate from the current no-file runtime smoke.

## 12. Makefile / Release-Quality Staging

Recommended future staging:

- file-writing fixture contract design
- fixture JSON creation
- fixture validator design
- fixture validator implementation
- standalone Makefile target for fixture validator
- release-quality integration for fixture validator
- file-writing runtime implementation
- focused runtime tests
- standalone file-writing smoke target
- isolated write validation
- release-quality integration
- remote status marker

The existing no-file runtime target should not be modified as part of this
boundary design.

## 13. Relation To Existing Runtime Smoke

The existing runtime smoke is no-file only.

Runtime smoke success is not file-writing readiness. File writing requires
separate fixtures, separate tests, and isolated write validation.

The existing runtime target should remain unchanged until a dedicated future
file-writing implementation step is scheduled.

## 14. Relation To Artifact Writer / Artifact Body

Manifest writer file writing should consume safe metadata and safe pointers
only.

It should not:

- run the artifact writer CLI
- run the artifact body generation CLI
- embed artifact body payload
- generate manifest body
- infer artifact writer CLI integration readiness

Artifact writer CLI integration remains a later separate phase.

## 15. Safety Interpretation

Future file-writing success would mean only that metadata-only manifest JSON
can be written to an isolated safe root under the defined path/content policy.

It would not mean production output readiness. It would not mean real-data
readiness. It would not mean artifact writer CLI integration. It would not
mean manifest body generation. It would not mean model performance.

## 16. Beginner-Friendly Explanation

File writing is separate from the no-file runtime because writing files adds
path, overwrite, cleanup, residue, and privacy risks.

A safe root is needed so the writer has one controlled place where output is
allowed. This prevents accidental writes to user, private, or unrelated
locations.

The first file-writing step should be metadata-only because metadata can
prove the path and write mechanics without introducing manifest bodies,
artifact body payloads, or generated policy bodies.

Isolated write validation is needed because static fixture checks cannot
prove that a real write stays inside the safe root, creates the expected
number of files, and cleans up correctly.

## 17. Docs Safety Policy

Docs may include field names, count names, target names, command shapes, path
policy, and summary policy.

Docs must not include:

- JSON body examples
- manifest body examples
- request/pointer body examples
- artifact body payload examples
- raw logs
- private path examples
- raw learner text
- real participant data
- performance metric bodies

## 18. What This Does Not Do

- does not implement file writing
- does not add `--manifest-out`
- does not create fixtures
- does not modify runtime code
- does not modify Makefile
- does not modify the release-quality wrapper
- does not modify workflow YAML
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 19. Next Recommended Steps

- Step409: file-writing fixture contract design
- Step410: file-writing fixture JSON creation
- Step411: fixture validator design
- Step412: fixture validator implementation
- later: isolated write validation
- later: runtime file-writing implementation

## 20. Step409 Fixture Contract Design Status

Step409 adds the docs-only fixture contract design for future metadata-only
manifest file writing fixtures:

[Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md).

The boundary remains design-only. Step409 does not create fixture JSON,
implement `--manifest-out`, write manifest files, change runtime code, change
Makefile, change the release-quality wrapper, change workflow YAML, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 21. Step410 Fixture JSON Creation Status

Step410 creates the synthetic metadata-only file writing fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/`

The root contains 39 cases and 195 JSON files. It remains contract fixture
data only: no validator, no runtime file writing, no `--manifest-out`, no
isolated write validation, no Makefile/wrapper/workflow change, no artifact
writer CLI integration, no real data, no metrics, and no production readiness
claim.

## 22. Step411 Fixture Validator Design Status

Step411 adds the docs-only static validator design for the 39-case / 195-JSON
file writing fixture root:

[Frozen policy generation manifest writer metadata-only file writing fixture validator design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_design.md).

The boundary remains unchanged. Step411 does not implement the validator,
write manifest files, add `--manifest-out`, run isolated writes, change
fixture JSON, change Makefile, change the release-quality wrapper, change
workflow YAML, connect artifact writer CLI, use real data, compute metrics, or
claim production readiness.

## 23. Step412 Fixture Validator Implementation Status

Step412 implements the static file writing fixture validator:

`python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`

The boundary remains unchanged. The validator is a no-write checker for
fixture contracts only: it does not implement manifest file writing, add
`--manifest-out`, run isolated writes, change Makefile, change the
release-quality wrapper, change workflow YAML, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## 24. Step413 Makefile Target Design Status

Step413 adds the docs-only Makefile target design for a future standalone
validator target:

[Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md).

The boundary remains unchanged. Step413 does not modify Makefile, add
release-quality integration, change workflow YAML, change Python code/tests,
change fixture JSON, write manifest files, implement `--manifest-out`, run
isolated writes, connect artifact writer CLI, use real data, compute metrics,
or claim production readiness.

## 25. Step414 Makefile Target Implementation Status

Step414 implements the standalone Makefile target for the static file writing
fixture validator:

`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

The boundary remains unchanged. The target does not write manifest files,
implement `--manifest-out`, run isolated writes, run the manifest writer
runtime, connect artifact writer CLI, change fixture JSON, change workflow
YAML, add release-quality integration, use real data, compute metrics, or
claim production readiness.

## 26. Related Documents

- [Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator implementation](../python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator tests](../python/learner_state/tests/test_frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer runtime Makefile target design](frozen_policy_generation_manifest_writer_runtime_makefile_target_design.md)
- [Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md)
- [Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 27. Step415 Release-Quality Integration Design Status

Step415 adds the docs-only release-quality integration design for the
standalone file writing fixture validator target:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md).

The file writing boundary remains unchanged. Step415 does not add wrapper
integration, change workflow YAML, change Makefile, change Python code/tests,
change fixture JSON, write manifest files, implement `--manifest-out`, run
isolated writes, connect artifact writer CLI, use real data, compute metrics,
or claim production readiness.

## 28. Step416 Wrapper Integration Status

Step416 adds the standalone file writing fixture validator target to the
release-quality wrapper. The boundary remains unchanged: the target validates
fixture contracts statically and does not write manifest files.

Step416 does not change workflow YAML, Makefile, Python code/tests, fixture
JSON, runtime implementation, `--manifest-out`, isolated write validation,
artifact writer CLI integration, metrics, real data use, or production
readiness claims.

## 29. Step417 Remote Run Record Workflow Design Status

Step417 adds the docs-only remote/manual run record workflow for a future
public-safe status marker:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The file writing boundary remains unchanged. Step417 does not create a status
marker, run remote workflows, change workflow YAML, change the wrapper, change
Makefile, change Python code/tests, change fixture JSON, write manifest files,
implement `--manifest-out`, run isolated writes, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## 30. Step418 Remote Status Marker Status

Step418 creates the public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation manifest writer file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md).

The file writing boundary remains unchanged. The marker is evidence only that
the static metadata-only file writing fixture validator target was included in
and passed Release Quality. It is not manifest file writing evidence, not
`--manifest-out` evidence, not isolated write validation evidence, not
artifact writer CLI integration evidence, not real-data readiness, not
performance evidence, and not a production-readiness claim.
