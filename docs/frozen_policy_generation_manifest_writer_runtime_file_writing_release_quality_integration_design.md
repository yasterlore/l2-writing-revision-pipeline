# Frozen Policy Generation Manifest Writer Runtime File Writing Release-Quality Integration Design

## 1. Purpose

This document fixes the docs-only design for adding the manifest writer
runtime metadata-only file writing smoke target to the Release Quality wrapper.
It is a release-quality integration design only.

This document does not implement the wrapper change, does not modify workflow
YAML, does not connect artifact writer CLI, does not call artifact body
generation CLI, does not generate manifest bodies, and does not claim
production readiness.

## 2. Current State

- Runtime metadata-only file writing exists.
- `--manifest-out` exists.
- `--allow-overwrite` exists.
- The standalone Makefile smoke target exists:
  `check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing`.
- The smoke target passes locally and writes one metadata-only file during its
  target-owned smoke run.
- The smoke target parses and scans the written JSON, removes the smoke path,
  and reports zero smoke residue.
- Release-quality integration for this runtime file writing smoke target does
  not exist yet.
- Artifact writer CLI integration does not exist.

## 3. Wrapper Label

Proposed wrapper label:

`release_quality_check: learner-state frozen policy generation manifest writer runtime file writing smoke`

## 4. Wrapper Command

Proposed wrapper command:

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing`

The wrapper should call the standalone target only. It should not add
additional file-writing behavior, should not pass extra runtime flags, and
should not execute artifact writer or artifact body generation CLIs.

## 5. Recommended Insertion Point

Add the wrapper section after:

`release_quality_check: learner-state frozen policy generation manifest writer production file writing fixture validation`

and before:

`release_quality_check: config and scoring smoke checks`

Recommended manifest writer chain order:

- manifest writer fixture validation
- manifest writer runtime fixture validation
- manifest writer runtime smoke
- manifest writer file writing fixture validation
- manifest writer isolated write validation
- manifest writer production file writing fixture validation
- manifest writer runtime file writing smoke
- config and scoring smoke checks

This ordering keeps the file-writing readiness chain readable: no-file runtime
contract, no-file runtime smoke, broad static file-writing contract, isolated
temp-root write harness, production/public-output-root static contract, then
actual `metadata_only_file` runtime smoke.

## 6. Expected Wrapper Output

The wrapper output should remain body-free and count-only. Expected safe
fields include:

- `mode=manifest_writer`
- `result_schema_version=learner_state_frozen_policy_generation_manifest_writer_result_v0.1`
- `writer_status=pass`
- `manifest_writer_mode=metadata_only_file`
- `runtime_writer_executed=true`
- `manifest_file_written=true`
- `written_file_count=1`
- `manifest_output_path_available=true`
- `manifest_body_available=false`
- `manifest_body_suppressed=true`
- `file_writing_checked=true`
- `output_path_safety_checked=true`
- `content_policy_checked=true`
- `no_manifest_body=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `release_quality_ready=false`
- `safe_summary=metadata_only_manifest_writer_result`
- `manifest_writer_runtime_file_writing_smoke=ok`
- `smoke_residue_file_count=0`

The output must not include the written JSON body, request body, pointer body,
fixture JSON body, manifest body, artifact body payload, generated policy body,
raw rows, logits, private paths, absolute local or temp paths, raw learner
text, real participant data, or performance metric body.

## 7. Expected Wrapper Behavior

- Target pass lets release-quality continue.
- Target failure fails release-quality.
- The target writes exactly one metadata-only file during the smoke.
- The target removes its target-owned smoke path after validation.
- The target leaves `tmp/frozen_policy_generation_manifest/smoke` residue 0.
- The target does not write a manifest body.
- The target does not print the written JSON body.
- The target does not print an absolute resolved output path.
- The target does not execute artifact writer CLI.
- The target does not execute artifact body generation CLI.

## 8. Failure Interpretation

Treat any of the following as a Release Quality failure:

- target exits nonzero
- runtime exits nonzero
- `manifest_file_written` is not true
- `written_file_count` is not 1
- written file is missing during smoke validation
- written file is malformed JSON
- forbidden field or value appears in the written JSON
- stdout or stderr leaks body content
- stdout or stderr includes an absolute resolved output path
- output path escapes the safe root
- cleanup fails
- smoke residue remains
- artifact writer CLI is invoked unexpectedly
- artifact body generation CLI is invoked unexpectedly

## 9. Log Safety

Allowed in public logs and docs:

- wrapper label
- wrapper command
- mode
- result schema version
- writer status
- manifest writer mode
- count fields
- safety flags
- smoke status
- smoke residue count

Forbidden in public logs and docs:

- written file JSON body
- fixture JSON body
- request body
- pointer body
- expected body
- manifest body
- artifact body payload
- generated policy body
- raw rows
- logits or probability dumps
- private paths
- absolute local paths
- absolute temp paths
- raw learner text
- final text
- observed-after text
- gold labels
- scoring feedback payload
- real participant data
- performance metric body
- raw GitHub Actions logs
- full job output

## 10. Cleanup and Residue Policy

- The target owns only the safe smoke subdirectory
  `tmp/frozen_policy_generation_manifest/smoke`.
- The target should clean that smoke path before the run.
- The target should clean that smoke path after validation.
- The final residue count for that smoke path must be 0.
- The target must not delete unrelated output outside the smoke path.
- The wrapper should fail if smoke residue remains.

## 11. Relation to Existing No-File Runtime Smoke

The existing runtime smoke checks default `metadata_only_no_file` behavior. The
runtime file writing smoke checks opt-in `metadata_only_file` behavior. They
should remain separate labels, and the default no-file smoke should remain
before the file-writing smoke.

## 12. Relation to Production Fixture Validator

The production file writing fixture validator is static contract validation for
future production/public-output-root behavior. The runtime file writing smoke
checks actual file write behavior for one synthetic metadata-only smoke run.
The static production fixture validator should remain before the runtime file
writing smoke. Neither check alone proves production readiness.

## 13. Relation to Isolated Write Validation

Isolated write validation writes inside a validator-owned temporary root. The
runtime file writing smoke writes inside a project-controlled target-owned
smoke path under the safe root. They are separate safety layers and should
remain separate wrapper labels.

## 14. Relation to Artifact Writer CLI Integration

The runtime file writing smoke target must not execute artifact writer CLI and
must not execute artifact body generation CLI. Artifact writer CLI integration
remains a separate future step.

## 15. Relation to Release-Quality Staging

Recommended future sequence:

- Step444: this docs-only integration design
- Step445: release-quality wrapper integration
- Step446: remote/manual run record workflow design
- Step447: remote status marker
- artifact writer CLI integration remains separate

## 16. Docs Safety Policy

Docs may include target names, command names, the safe relative smoke path,
field names, count names, and safety flags.

Docs must not include JSON body examples, written output examples, raw logs,
fixture bodies, request bodies, pointer bodies, expected bodies, manifest
bodies, artifact body payloads, generated policy bodies, private path examples,
absolute path examples, raw learner text, real participant data, or performance
evidence.

## 17. What This Does Not Do

This design does not:

- modify the release-quality wrapper
- modify workflow YAML
- modify Makefile
- modify Python code or tests
- modify fixtures JSON
- connect artifact writer CLI
- call artifact body generation CLI
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness

## 18. Next Recommended Steps

- artifact writer CLI integration remains separate

## 19. Step445 Wrapper Integration Status

Step445 adds the runtime metadata-only file writing smoke target to the
release-quality wrapper with the label:

`release_quality_check: learner-state frozen policy generation manifest writer runtime file writing smoke`

The wrapper command is:

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing`

The new wrapper section is placed after production file writing fixture
validation and before config/scoring smoke checks. It keeps the wrapper output
body-free and count-only, relies on the smoke target cleanup policy, and does
not change workflow YAML, Makefile, Python code/tests, fixtures JSON, artifact
writer CLI integration, artifact body generation CLI integration, manifest
body generation, real-data use, metrics, or production readiness.

Step445 does not create a remote/manual run record workflow or status marker.
Those remain separate future steps.

## 20. Step446 Remote Run Record Workflow Design Status

Step446 adds the docs-only workflow design for recording a future remote/manual
Release Quality run that includes the runtime file writing smoke target:

[Frozen policy generation manifest writer runtime file writing release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_file_writing_release_quality_remote_run_record_workflow.md).

The design fixes the future status marker path, public-safe metadata to record,
metadata not to record, status marker structure, runtime file writing smoke
summary, written file safety summary, cleanup/residue summary, related chain
checks, safety review, interpretation, failure handling, and next actions.

Step446 does not run GitHub Actions, create the status marker, change workflow
YAML, change the release-quality wrapper, change Makefile, modify Python
code/tests, modify fixtures JSON, connect artifact writer CLI, call artifact
body generation CLI, generate manifest bodies, use real data, compute metrics,
or prove production readiness.

## 21. Step447 Remote Status Marker Status

Step447 records the successful remote/manual Release Quality run that included
the runtime metadata-only file writing smoke target:

[Learner-state frozen policy generation manifest writer runtime file writing release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_file_writing_release_quality_remote_run_status.md).

The status marker is public-safe, pass-only/count-only, and body-free. It
records that the wrapper included
`release_quality_check: learner-state frozen policy generation manifest writer runtime file writing smoke`
and that the smoke target wrote one metadata-only file during the run, parsed
and scanned it, and cleaned the target-owned smoke path with residue count 0.

Step447 does not change workflow YAML, release-quality wrapper, Makefile,
Python code/tests, fixtures JSON, artifact writer CLI integration, artifact
body generation CLI integration, manifest body generation, real-data use,
metrics, or production readiness.
