# Frozen Policy Generation Artifact Writer CLI Integration Runtime Fixture Validator Design

## 1. Scope

This document is the Step480 design for a future validator over the Step479
artifact writer CLI integration runtime fixture root.

This is design-only. It does not implement a validator, implement a runtime,
add a Makefile target, change the release-quality wrapper, change workflow
YAML, change Python code/tests, or change fixture JSON.

This is not artifact body generation integration, manifest writer integration,
production readiness evidence, real-data readiness evidence, or model
performance evidence.

## 2. Prior Completed Chain

- Step477 created the artifact writer CLI integration runtime design. It fixed
  the future runtime boundary, proposed runtime contract, CLI flow, fail-closed
  behavior, and public-safe checklist.
- Step478 created the runtime fixture contract design. It proposed the fixture
  root, case layout, case counts, metadata contracts, validator implications,
  and status mapping.
- Step479 created the synthetic metadata-only runtime fixture root with 30 case
  directories, 6 valid cases, 24 invalid cases, 6 JSON files per case, and 180
  JSON case files.

Step479 creates fixture contracts only. It does not prove runtime correctness
or validator correctness.

## 3. Target Fixture Root

The future validator should inspect:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Expected counts:

- total_cases: 30
- valid_cases: 6
- invalid_cases: 24
- json_files_per_case: 6
- total_json_files: 180

Required files per case:

- `case_metadata.json`
- `request_metadata.json`
- `pointer_metadata.json`
- `artifact_writer_cli_metadata.json`
- `expected_runtime_summary.json`
- `expected_error.json`

## 4. Proposed Module And CLI

Future module path:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

Future CLI shape:

`python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation`

Suggested CLI arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Step480 does not create this module or CLI.

## 5. Proposed Validation Phases

The future validator should run these phases in deterministic order:

1. Root existence check.
2. Case discovery under `valid/` and `invalid/`.
3. Required file presence check.
4. JSON parse check.
5. `schema_version` check.
6. `case_id` consistency check.
7. Valid / invalid case count check.
8. Expected status / reason-code alignment check.
9. Exit-code category alignment check.
10. Forbidden key scan.
11. Forbidden string scan.
12. Raw/body/payload sentinel policy check.
13. No-oracle field scan.
14. Synthetic-only / metadata-only flag check.
15. Path safety check.
16. File-writing disabled/default policy check.
17. Artifact body / manifest writer separation check.
18. Suppression flag consistency check.
19. Residue expectation check.
20. Duplicate case id check.
21. Deterministic ordering check.
22. Expected summary field completeness check.
23. Safe aggregate summary construction.

The validator should not execute the artifact writer CLI integration runtime.

## 6. Forbidden Content Policy

The validator should fail closed when fixture files or public output contain
prohibited content rather than controlled metadata-only sentinel fields.

Forbidden content categories include:

- raw learner text
- raw rows
- logits
- probabilities
- private paths
- absolute paths
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation
- request body
- pointer body
- expected body
- written file JSON body
- manifest body
- artifact body payload
- generated policy body
- raw GitHub Actions logs
- full job output

The validator design does not include examples of prohibited payloads.

## 7. Sentinel Policy

Step479 invalid cases represent prohibited field presence with controlled
metadata-only sentinels.

The future validator should enforce this policy:

- Prohibited field presence may be represented by controlled sentinel fields.
- Actual prohibited body values must not appear.
- Sentinel field names may be allowed only in expected invalid cases.
- Sentinel values must remain body-free.
- Private path and absolute path cases must not store actual path strings.
- Artifact body, manifest body, and generated policy body cases must not store
  body payloads.
- Raw learner text, raw rows, logits, and probability cases must not store raw
  content.
- Valid cases must not contain sentinel fields for prohibited content.

This allows safe invalid-case coverage without adding sensitive or body-bearing
fixture content.

## 8. Expected Summary Schema

The future validator should emit a public-safe, count-only summary. Proposed
field names and meanings:

- `mode`: identifies runtime fixture validation.
- `validation_schema_version`: validator summary schema version.
- `fixture_root`: safe relative fixture root identifier.
- `total_cases`: discovered total case count.
- `valid_cases`: discovered valid case count.
- `invalid_cases`: discovered invalid case count.
- `total_json_files`: discovered JSON file count.
- `json_files_per_case`: expected JSON files per case.
- `matched_cases`: cases matching expected status and reason.
- `mismatched_cases`: cases with unexpected validation outcome.
- `input_error_cases`: malformed root, file, or CLI input count.
- `pass_cases`: expected pass case count.
- `usage_error_cases`: expected usage-error case count.
- `fail_closed_cases`: expected fail-closed case count.
- `duplicate_case_id_cases`: duplicate case id count.
- `missing_required_file_cases`: missing required file count.
- `content_suppressed`: aggregate content suppression flag.
- `body_suppressed`: aggregate body suppression flag.
- `no_raw_rows`: aggregate raw-row absence flag.
- `no_logits_dump`: aggregate logits/probability absence flag.
- `no_private_paths`: aggregate private path absence flag.
- `no_absolute_paths`: aggregate absolute path absence flag.
- `no_generated_policy_body`: aggregate generated policy body absence flag.
- `no_artifact_body_payload`: aggregate artifact body payload absence flag.
- `no_manifest_body`: aggregate manifest body absence flag.
- `no_request_body`: aggregate request body absence flag.
- `no_pointer_body`: aggregate pointer body absence flag.
- `no_expected_body`: aggregate expected body absence flag.
- `no_oracle_checked`: no-oracle policy validation flag.
- `synthetic_only_checked`: synthetic-only policy validation flag.
- `metadata_only_checked`: metadata-only policy validation flag.
- `file_writing_checked`: file-writing disabled/default validation flag.
- `artifact_writer_cli_integration_runtime_checked`: runtime fixture contract
  validation flag.
- `artifact_body_generation_integration_checked`: separation validation flag.
- `manifest_writer_integration_checked`: separation validation flag.
- `production_readiness_claimed`: should remain false.
- `real_data_readiness_claimed`: should remain false.
- `performance_claims_present`: should remain false.
- `root_errors`: body-free error categories for root-level validation.

The summary must not include fixture JSON bodies, body payloads, private paths,
absolute paths, or raw content.

## 9. Expected Counts

Expected fixture counts:

- total_cases: 30
- valid_cases: 6
- invalid_cases: 24
- total_json_files: 180
- json_files_per_case: 6

Expected status categories:

- `pass_cases`: 6 valid cases.
- `usage_error_cases`: root or case-structure cases, such as missing required
  metadata, mismatched expected status, duplicate case id, malformed schema, or
  invalid case identity.
- `fail_closed_cases`: prohibited content, no-oracle, path safety, body
  suppression, artifact body generation separation, manifest writer separation,
  file-writing ambiguity, or residue-risk cases.

The exact usage-error / fail-closed counts should be derived from the fixture
metadata during implementation and compared to expected contract constants.

## 10. Exit-Code Behavior

Future CLI exit-code behavior should be:

- Root valid and all expected results matched: exit 0.
- Expected fail-closed / usage-error cases matched: exit 0.
- Actual mismatch: nonzero.
- Malformed root or input error: nonzero.
- Invalid CLI arguments: nonzero.
- Forbidden content detection: nonzero.
- Public output leakage detection: nonzero.

Expected negative cases are successful validator matches only when the expected
failure category and reason code align.

## 11. CLI Modes

Future CLI modes:

- Root mode: validate the full fixture root and emit aggregate summary.
- Single case mode: validate one case by safe relative case id.
- JSON summary mode: emit parseable public-safe summary fields only.
- Human summary mode: emit body-free count/status lines only.

All modes must avoid fixture bodies, request bodies, pointer bodies, expected
bodies, generated policy bodies, artifact body payloads, manifest bodies, raw
rows, logits/probabilities, private paths, absolute paths, raw learner text,
and raw logs.

## 12. Focused Tests Plan

Future focused tests should cover:

- Root summary counts.
- Single valid case pass.
- Single invalid fail-closed case matched.
- Usage-error case matched.
- Required file missing in a temporary fixture copy.
- Duplicate case id in a temporary fixture copy.
- Forbidden field scan.
- Forbidden string scan.
- Path safety scan.
- Sentinel policy.
- Schema version mismatch.
- Expected reason-code mismatch.
- Safe JSON summary.
- Safe human summary.
- Deterministic ordering.
- No fixture body leakage.
- No runtime execution.
- No file-writing residue.

Tests should use synthetic metadata-only fixture copies where mutation is
needed.

## 13. Relationship To Step477 / Step478 / Step479

- Step477 defines the future runtime boundary and contract.
- Step478 defines the runtime fixture contract for that boundary.
- Step479 creates the runtime fixture root described by the contract.
- Step480 designs a future static validator for the Step479 fixture root.

Step480 is not runtime implementation and does not validate runtime
correctness. It only fixes the proposed validator behavior for future work.

## 14. Planned Follow-Up Steps

Suggested future sequence:

- Step481: runtime fixture validator module / CLI / focused tests implementation
- Step482: standalone Makefile target design
- Step483: standalone Makefile target implementation
- Step484: release-quality integration design
- Step485: release-quality wrapper integration
- Step486: remote/manual run record workflow design
- Step487: remote status marker
- Step488: artifact writer CLI integration runtime implementation design

The numbering is a proposal. Step480 does not advance into these steps.

## 14.1 Step481 Validator Implementation Status

Step481 implements the static validator module, CLI, and focused tests proposed
by this design:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

The implementation validates the Step479 synthetic metadata-only fixture root
and emits body-free public-safe summaries. It does not execute runtime
integration, call artifact writer CLI integration runtime, connect artifact
body generation, connect manifest writer integration, add a Makefile target,
change release-quality wrapper/workflow files, change fixture JSON, use real
data, compute metrics, or claim production readiness.

## 14.2 Step482 Makefile Target Design Status

Step482 adds the docs-only standalone Makefile target design for running the
Step481 validator CLI:

[Frozen policy generation artifact writer CLI integration runtime fixture validator Makefile target design](frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validator_makefile_target_design.md)

The design does not implement the target, change release-quality wrapper or
workflow files, change Python code/tests, change fixture JSON, execute runtime
integration, use real data, compute metrics, or claim production readiness.

## 14.3 Step483 Standalone Makefile Target Status

Step483 implements the standalone Makefile target for this validator:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`

The target remains standalone in Step483. Step485 adds it to the
release-quality wrapper. The target does not change workflow files, Python
code/tests, fixture JSON, execute runtime integration, use real data, compute
metrics, or claim production readiness.

## 14.4 Step484 Release-Quality Integration Design Status

Step484 adds the docs-only release-quality integration design for the
standalone runtime fixture validator target:

[Frozen policy generation artifact writer CLI integration runtime fixture release-quality integration design](frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_integration_design.md)

The design proposes future wrapper placement after the earlier artifact writer
CLI integration fixture validation and before artifact body checks. It does
not change the wrapper, workflow files, Makefile, Python code/tests, fixture
JSON, execute runtime integration, use real data, compute metrics, or claim
production readiness.

## 14.5 Step485 Wrapper Integration Status

Step485 adds the standalone runtime fixture validator target to
`scripts/check_release_quality.sh` in the Step484 insertion point. The wrapper
now runs the static fixture validator after artifact writer CLI integration
fixture validation and before artifact body fixture validation. Step485 does
not change workflow files, Makefile targets, Python code/tests, fixture JSON,
execute runtime integration, use real data, compute metrics, or claim
production readiness.

## 14.6 Step486 Remote Run Record Workflow Design Status

Step486 adds the docs-only public-safe remote/manual run record workflow design
for the Step485 wrapper check:

[Frozen policy generation artifact writer CLI integration runtime fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_remote_run_record_workflow.md)

The design does not create a remote status marker, change workflow files,
change the wrapper, change Makefile targets, change Python code/tests, change
fixture JSON, execute runtime integration, use real data, compute metrics, or
claim production readiness.

## 15. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- validator implementation
- runtime implementation

## 16. Public-Safe Checklist

- no raw logs
- no full job output
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no manifest body
- no artifact body payload
- no generated policy body
- no raw rows
- no logits or probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims

## 17. Step487 Remote Status Marker Status

Step487 creates the public-safe pass-only/count-only remote/manual status
marker for the Step485 release-quality wrapper check:

[Learner-state frozen policy generation artifact writer CLI integration runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_remote_run_status.md)

The marker records static fixture validator wrapper inclusion and the 30-case /
180-JSON count summary. It does not store raw logs, full job output, fixture
JSON bodies, request/pointer/expected bodies, runtime integration evidence,
real-data readiness evidence, model-performance evidence, or production
readiness evidence.

## 18. Step488 Runtime Implementation Design Status

Step488 adds the design-only / planning-only implementation design for a
future artifact writer CLI integration runtime:

[Frozen policy generation artifact writer CLI integration runtime implementation design](frozen_policy_generation_artifact_writer_cli_integration_runtime_implementation_design.md)

The design uses this validator chain as static guardrails. It does not replace
the Step481 validator, change fixture JSON, add runtime code, add a CLI, change
Makefile, change the release-quality wrapper, execute artifact body generation
integration, execute manifest writer integration, or claim production
readiness.

## 19. Step489 Runtime Implementation Status

Step489 implements the initial standalone metadata-only runtime module, CLI,
and focused tests. The Step481 fixture validator remains a static validator
and is not replaced.

- runtime module:
  `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- focused tests:
  `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime.py`

The runtime does not write files, invoke artifact body generation, invoke
manifest writer, generate manifest bodies, generate policy bodies, or claim
production readiness.
