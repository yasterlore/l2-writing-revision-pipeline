# Frozen Policy Generation Artifact Writer CLI Integration Fixture Release-Quality Integration Design

## 1. Purpose

This document designs future release-quality wrapper integration for the
standalone artifact writer CLI integration fixture validator target.

This is a docs-only design. It does not change the release-quality wrapper,
change GitHub Actions workflow YAML, change the Makefile, change Python code or
tests, change fixture JSON, implement artifact writer CLI integration runtime,
connect artifact body generation CLI, connect manifest writer runtime, generate
manifest bodies, use real data, compute metrics, or claim production readiness.

The goal is to define where and how
`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`
should later enter `make check-release-quality` safely.

## 2. Current State

- The artifact writer CLI integration fixture root exists.
- The fixture root has 28 synthetic metadata-only cases and 168 JSON files.
- The validator module exists.
- The validator CLI exists.
- Focused validator tests exist.
- The standalone Makefile target exists.
- Release-quality wrapper integration does not exist.
- Remote status marker evidence does not exist.
- Artifact writer CLI integration runtime does not exist.
- Artifact body generation CLI integration does not exist.
- Manifest writer integration does not exist.
- Manifest body generation does not exist.

Standalone target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

Standalone command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures
```

## 3. Proposed Label

Recommended release-quality label:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation
```

The label says fixture validation because the target validates a static fixture
contract. It should not imply runtime integration, artifact body generation,
manifest writer integration, model performance, real-data readiness, or
production readiness.

## 4. Proposed Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures
```

The wrapper should call the standalone Makefile target rather than duplicating
the validator CLI command. This keeps the shared developer entrypoint in one
place and keeps future target-local command changes localized to the Makefile.

## 5. Proposed Insertion Point

Recommended insertion point:

- after artifact writer fixture validation
- after artifact writer runtime smoke
- before artifact body fixture validation
- before artifact body generation checks
- before manifest writer checks
- before runtime file writing smoke

Recommended local order:

1. `release_quality_check: learner-state frozen policy generation artifact writer fixture validation`
2. `release_quality_check: learner-state frozen policy generation artifact writer runtime smoke`
3. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`
4. `release_quality_check: learner-state frozen policy generation artifact body fixture validation`

Reasons:

- Artifact writer standalone contract validation runs first.
- Artifact writer standalone runtime smoke runs next.
- The generator scaffold CLI -> artifact writer CLI integration fixture
  contract is then checked statically.
- Artifact body generation and manifest writer chains remain separate and
  later.
- Existing targets are not replaced.

## 6. Expected Release-Quality Output

The expected output is body-free and count-only:

- `mode=artifact_writer_cli_integration_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`
- `total_cases=28`
- `valid_cases=6`
- `invalid_cases=22`
- `total_json_files=168`
- `json_files_per_case=6`
- `matched_cases=28`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=9`
- `fail_closed_cases=13`
- `content_suppressed=true`
- `body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_generated_policy_body=true`
- `no_artifact_body_payload=true`
- `no_manifest_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `file_writing_checked=true`
- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

Reason-code counts may be printed as controlled metadata. They must not include
fixture bodies, request bodies, pointer bodies, expected bodies, raw rows,
logits, private paths, absolute local paths, raw learner text, or performance
metric bodies.

## 7. Failure Interpretation

Release-quality should fail if the target fails because of:

- fixture root missing
- required file missing
- extra JSON file
- malformed JSON
- case count mismatch
- schema mismatch
- case_id mismatch
- case_group mismatch
- expected status mismatch
- expected reason mismatch
- forbidden content
- no-oracle violation
- file-writing flag true
- artifact body generation flag true
- manifest writer flag true
- public output leakage

These failures mean the static integration fixture contract is not safe or not
internally consistent. They do not imply model performance failure or
production readiness failure.

## 8. Relation To Existing Release-Quality Chain

This proposed check:

- does not replace artifact writer fixture validation
- does not replace artifact writer runtime smoke
- does not run artifact body generation
- does not run manifest writer code
- does not run runtime integration
- validates only the artifact writer CLI integration fixture contract

The existing artifact writer fixture and runtime targets remain the first two
artifact writer checks. The proposed target adds a separate static integration
fixture layer before artifact body checks begin.

## 9. Relation To Artifact Body And Manifest Writer

Artifact body generation remains later and separate. Manifest writer
integration remains later and separate. Manifest body generation remains later
and separate.

The target should keep:

- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `release_quality_ready=false`

Those flags mean the boundaries were checked as disabled or separated. They do
not mean artifact body generation CLI integration, manifest writer integration,
or production readiness exists.

## 10. Release-Quality Safety Policy

Allowed in wrapper output:

- label
- command
- mode
- validation schema version
- case counts
- pass / usage-error / fail-closed counts
- safety flags
- controlled reason-code counts
- `release_quality_ready=false`

Forbidden in wrapper output and docs:

- raw logs
- full job output copied into docs
- fixture JSON bodies
- request bodies
- pointer bodies
- expected-result bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw rows
- logits or probability dumps
- private paths
- absolute local or temp paths
- raw learner text
- final text
- observed-after text
- gold labels
- scoring feedback payloads
- real participant data
- performance metric bodies

## 11. Wrapper Implementation Plan For Next Step

Future Step474 should:

- update `scripts/check_release_quality.sh`
- add the proposed label and command in the proposed insertion point
- not change GitHub Actions workflow YAML
- not change the Makefile
- not change Python code or tests
- not change fixture JSON
- run the standalone target
- run `make check-release-quality`
- confirm the new label appears
- confirm output remains body-free
- confirm wrapper diff contains only the new label and command block

## 12. Remote Marker Staging

After wrapper integration:

- run Release Quality remotely on `main`
- collect safe metadata only
- do not copy raw logs
- do not copy full job output
- create a remote/manual run record workflow design
- then create a remote status marker

The future marker should remain pass-only / count-only and should not include
fixture JSON bodies, request bodies, pointer bodies, artifact body payloads,
manifest bodies, raw rows, logits, private paths, absolute paths, raw learner
text, or performance evidence.

## 13. Docs Safety Policy

Docs may include:

- target names
- command names
- labels
- field names
- reason code names
- counts and boolean safety flags

Docs must not include:

- JSON body examples
- raw logs
- private or absolute path examples
- raw learner text examples
- written body examples
- artifact body payload examples
- manifest body examples
- generated policy body examples

## 14. What This Does Not Do

This design does not:

- change the release-quality wrapper
- modify workflow YAML
- modify the Makefile
- modify Python code or tests
- modify fixture JSON
- implement artifact writer CLI integration runtime
- connect artifact body generation CLI
- connect manifest writer runtime
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness

## 15. Next Recommended Steps

- Step474 wrapper integration
- Step475 remote/manual run record workflow design
- Step476 remote status marker

## 16. Step474 Wrapper Integration Status

Step474 implements the release-quality wrapper integration described in this
design. `scripts/check_release_quality.sh` now includes the standalone fixture
validator target with this label and command:

- `release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`
- `make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

The block is placed after artifact writer fixture validation and artifact
writer runtime smoke, and before artifact body fixture validation. This keeps
the check limited to static CLI integration fixture contract validation and
does not connect artifact body generation CLI, manifest writer runtime, or
runtime integration.

Step474 does not change workflow YAML, change the Makefile, change Python code
or tests, change fixture JSON, use real data, compute metrics, or claim
production readiness.
