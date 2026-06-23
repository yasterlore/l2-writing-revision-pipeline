# Frozen Policy Generation Scaffold Runtime Fixture Alignment Design

This document checks the alignment between the future frozen policy generation
scaffold runtime API contract and the existing scaffold fixture validator
contract.

It is documentation only. It does not implement runtime code, generator code,
CLI behavior, Makefile targets, release-quality wrapper changes, workflow
changes, tests, fixtures, calibration, selective prediction, learner-state
estimation, estimator training, metric computation, or model code. It is not a
performance evaluation and not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected scaffold result bodies, generated frozen policy
artifact bodies, frozen policy artifact bodies, JSON bodies, policy bodies, raw
rows, logits/probability dumps, label bodies, split bodies, calibration policy
bodies, private paths, raw learner text, manual output bodies, tmp output
bodies, or real participant data.

## 1. Purpose

The purpose of this document is to confirm the contract alignment between:

- future `FrozenPolicyGenerationScaffoldResult` output
- existing `expected_scaffold_result.json` fixture metadata
- existing scaffold fixture validator comparison behavior

This is an implementation-prep document. It does not change fixtures, does not
change the validator, does not implement the runtime, and does not implement a
generator.

## 2. Current Contracts

Current fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`

Current fixture case files:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_scaffold_result.json`

Contract summaries:

- `generation_request.json` contract:
  request schema metadata, generation mode metadata, policy metadata,
  synthetic-only marker, no-oracle marker, body-suppression markers, and
  expected failure marker fields only.
- `input_fixture_pointer.json` contract:
  pointer schema metadata, validation status metadata, split availability
  metadata, relative fixture labels, synthetic-only marker, no-oracle marker,
  and metadata-only marker fields only.
- `expected_scaffold_result.json` contract:
  expected scaffold status, reason codes, failed checks, schema/status fields,
  safety flags, dry-run artifact metadata, and metadata-only markers only.
- validator result summary contract:
  mode, total cases, matched cases, mismatched cases, input error cases,
  reason-code counts, and safety flags only.
- runtime API result contract:
  future `FrozenPolicyGenerationScaffoldResult` safe metadata only, compatible
  with expected scaffold result fields.

This document lists field names only. It does not copy fixture JSON bodies.

## 3. Field Alignment Table

| expected_scaffold_result.json field | FrozenPolicyGenerationScaffoldResult field | source API / source object | required or optional | safe output allowed | notes |
| --- | --- | --- | --- | --- | --- |
| `scaffold_status` | `scaffold_status` | `validate_frozen_policy_generation_plan` / result | required | yes | Use `pass` for valid fixtures and `fail` for expected invalid fixtures. |
| `reason_codes` | `reason_codes` | plan validation / scaffold errors | required | yes | Normalize deterministic ordering. Valid cases use an empty list. |
| `failed_checks` | `failed_checks` | plan validation / scaffold errors | required | yes | Must align with reason codes and avoid body text. |
| `request_id` | `request_id` | `FrozenPolicyGenerationRequest` | recommended | yes | Runtime should provide a stable safe identifier; fixture expected result may need matching metadata. |
| `pointer_id` | `pointer_id` | `FrozenPolicyGenerationInputPointer` | recommended | yes | Runtime should provide a stable safe identifier; avoid raw paths. |
| `validation_reference_ids` | `validation_reference_ids` | pointer validation reference / plan | optional initially | yes | Safe IDs only; no pointer body or private path. |
| `generation_request_schema_version` | `generation_request_schema_version` | request loader | required by fixture contract | yes | Runtime may expose this as request schema metadata. |
| `pointer_schema_version` | `pointer_schema_version` | pointer loader | required by fixture contract | yes | Runtime may expose this as pointer schema metadata. |
| `input_validation_status` | `input_validation_status` | pointer / plan | required by fixture contract | yes | Should match pointer metadata. |
| `selective_prediction_validation_status` | `selective_prediction_validation_status` | pointer / plan | required by fixture contract | yes | Metadata-only status. |
| `frozen_policy_validation_status` | `frozen_policy_validation_status` | pointer / plan | required by fixture contract | yes | Metadata-only status. |
| `validation_split_available` | `validation_split_available` | pointer split policy / plan | required by fixture contract | yes | Missing validation split maps to expected failure. |
| `temperature_policy_status` | `temperature_policy_status` | request policy metadata / plan | required by fixture contract | yes | Must detect test-derived tuning. |
| `threshold_policy_status` | `threshold_policy_status` | request policy metadata / plan | required by fixture contract | yes | Must detect test-derived tuning. |
| `abstention_policy_status` | `abstention_policy_status` | request policy metadata / plan | required by fixture contract | yes | Metadata only. |
| `output_policy_status` | `output_policy_status` | request output/artifact policy / plan | required by fixture contract | yes | Must reject unsafe output policy. |
| `safety_status` | `safety_status` | safety scans | required by fixture contract | yes | Should be scalar safe metadata. |
| `content_suppressed` | `content_suppressed` | safety summary | required | yes | Should always be true for public output. |
| `artifact_body_suppressed` | `artifact_body_suppressed` | artifact policy / safety summary | required | yes | Should always be true initially. |
| `no_raw_rows` | `no_raw_rows` | safety summary | required | yes | Should always be true. |
| `no_logits_dump` | `no_logits_dump` | safety summary | required | yes | Should always be true. |
| `no_private_paths` | `no_private_paths` | path safety scan | required | yes | Fixture contract currently checks private path scan; runtime should expose this flag. |
| `no_performance_claims` | `no_performance_claims` | performance claim scan | recommended | yes | If fixture uses `performance_claim_scan_checked`, runtime should map to both scan status and no-claim status. |
| `synthetic_only_checked` | `synthetic_only_checked` | request/pointer scans | required | yes | Must be true for accepted synthetic fixtures. |
| `no_oracle_checked` | `no_oracle_checked` | request/pointer/plan scans | required | yes | Must be true when no-oracle checks ran. |
| `test_tuning_checked` | `test_tuning_checked` | plan safety scan | required | yes | Must be true even when the result is fail for test tuning. |
| `scoring_feedback_checked` | `scoring_feedback_checked` | plan safety scan | recommended | yes | Aligns with `scoring_feedback_violation`; fixture may need explicit expected field before implementation. |
| `private_path_scan_checked` | `private_path_scan_checked` | path safety scan | required by fixture contract | yes | Runtime can expose scan status separately from `no_private_paths`. |
| `performance_claim_scan_checked` | `performance_claim_scan_checked` | performance claim scan | required by fixture contract | yes | Runtime can expose scan status separately from `no_performance_claims`. |
| `no_request_body` | `no_request_body` | output formatter / safety summary | required by fixture contract | yes | Runtime summary must not include request body. |
| `no_generated_artifact_body` | `no_generated_artifact_body` | artifact policy / safety summary | required by fixture contract | yes | Runtime result should map this to artifact body suppression. |
| `generated_artifact_written` | `generated_artifact_written` | artifact policy / result | required for runtime | yes | Should default to false initially. |
| `generated_artifact_body_available` | `generated_artifact_body_available` | artifact policy / result | required for runtime | yes | Should default to false initially. |
| `would_write_artifact` | `would_write_artifact` | artifact policy / plan | required by fixture contract | yes | Current dry-run fixtures expect false. |
| `artifact_write_mode` | `artifact_write_mode` | artifact policy / plan | required by fixture contract | yes | Safe label only, such as dry-run metadata-only mode. |
| `metadata_only` | `metadata_only` | safety summary / formatter | required by fixture contract | yes | Should always be true. |
| `safe_summary` | `safe_summary` | summarizer | optional initially | yes, metadata-only | Must be short and body-free if implemented. |
| `validation_schema_version` | `validation_schema_version` | result schema / formatter | optional if applicable | yes | Decide before implementation whether this is separate from scaffold schema version. |

## 4. Reason-Code Alignment

Current invalid case mapping:

| invalid case | expected reason code | runtime error category | alias needed |
| --- | --- | --- | --- |
| `missing_validation_split` | `missing_validation_split` | `missing_validation_split` | no |
| `test_temperature_tuning` | `test_temperature_tuning` | `test_temperature_tuning` | no |
| `test_threshold_tuning` | `test_threshold_tuning` | `test_threshold_tuning` | no |
| `raw_rows_carryover` | `raw_rows_carryover` | `raw_rows_carryover` | no |
| `logits_dump_carryover` | `logits_dump_carryover` | `logits_dump_carryover` | no |
| `generated_artifact_body_leakage` | `generated_artifact_body_leakage` | `generated_artifact_body_leakage` | no |
| `private_path_output` | `private_path_output` | `private_path_output` | no |
| `scoring_feedback_violation` | `scoring_feedback_violation` | `scoring_feedback_violation` | no |

No alias is recommended for the current invalid eight. Runtime implementation
should use the exact reason-code strings already used by the scaffold fixture
validator.

Future reason codes may be added, but they should be added to the validator
mapping before fixtures or runtime tests depend on them.

## 5. Status Alignment

Expected status behavior:

- valid fixture case should produce `scaffold_status=pass`
- invalid fixture case should produce `scaffold_status=fail`
- invalid fixture case should include the expected reason code
- malformed request input should be `input_error`, not scaffold fail
- malformed pointer input should be `input_error`, not scaffold fail
- unsafe fixture path should be `input_error` when the path prevents safe
  loading
- unsafe output plan should be `scaffold_status=fail` with a safe reason code

Recommended boundary:

- loader and parser failures are input errors
- path rejection before metadata is loaded is an input error
- loaded metadata that describes unsafe behavior is scaffold fail

This keeps malformed fixture infrastructure separate from intentional invalid
fixture behavior.

## 6. Safety Flag Alignment

Safety flags should align across expected result, runtime result, and summary:

- `content_suppressed`: true in expected result, runtime result, and summary
- `artifact_body_suppressed`: true in expected result, runtime result, and
  summary
- `no_raw_rows`: true in expected result, runtime result, and summary
- `no_logits_dump`: true in expected result, runtime result, and summary
- `no_private_paths`: true in runtime result and summary; map to
  `private_path_scan_checked=true` in existing fixture expectations
- `no_performance_claims`: true in runtime result and summary; map to
  `performance_claim_scan_checked=true` in existing fixture expectations
- `synthetic_only_checked`: true once request and pointer synthetic markers are
  checked
- `no_oracle_checked`: true once no-oracle fields and scoring-feedback boundary
  are checked
- `test_tuning_checked`: true once validation/test split tuning source is
  checked
- `scoring_feedback_checked`: true once expected-action-as-feedback is checked

Runtime should set these booleans explicitly. Avoid implicit defaults.

## 7. Validator Compatibility Requirements

Runtime implementation must satisfy:

- result can be compared to `expected_scaffold_result.json`
- summary output contains no body fields
- JSON output is safe and parseable
- reason-code vocabulary matches the validator
- field naming is stable
- ordering is deterministic
- valid fixtures pass
- invalid fixtures fail for expected reasons
- no raw request body appears in CLI/logs
- no input pointer body appears in CLI/logs
- no expected result body appears in CLI/logs
- no artifact body appears in CLI/logs
- no raw rows, logits, private paths, learner text, or performance claims
  appear in CLI/logs

The validator should remain the fixture-contract oracle for runtime behavior.

## 8. Mismatch Risks

Implementation risks to avoid:

- runtime result field name differs from expected JSON field
- `validation_schema_version` is omitted when tests expect it
- reason-code order differs from expected deterministic order
- runtime uses an alias instead of the expected reason code
- input error versus scaffold fail boundary differs from validator
- `safe_summary` accidentally includes body-like content
- private path rejection leaks the rejected path
- `generated_artifact_written` default is unclear
- `generated_artifact_body_available` default is unclear
- `artifact_body_suppressed` is not consistently true
- `content_suppressed` is not consistently true
- `no_private_paths` and `private_path_scan_checked` are treated as the same
  field without a mapping decision
- `no_performance_claims` and `performance_claim_scan_checked` are treated as
  the same field without a mapping decision

These risks should be resolved before runtime code is added.

## 9. Recommended Implementation Constraints

Future runtime implementation should:

- use shared constants for reason codes where possible
- normalize reason-code ordering
- use explicit boolean defaults
- keep `safe_summary` short and metadata-only
- never include original JSON bodies in results
- never echo input paths except safe labels
- separate input errors from expected scaffold failures
- keep `generated_artifact_written=false` initially
- keep `generated_artifact_body_available=false` initially
- keep `artifact_body_suppressed=true`
- keep `content_suppressed=true`
- keep `no_raw_rows=true`
- keep `no_logits_dump=true`
- keep `no_private_paths=true`
- keep `no_performance_claims=true`

The first implementation should prefer a minimal skeleton that returns safe
metadata over a broad runtime that tries to behave like a generator.

## 10. Testing Implications

Future tests should cover:

- each existing valid fixture maps to pass
- each existing invalid fixture maps to expected fail
- exact reason-code match
- exact safety flag match
- deterministic JSON summary
- malformed request produces input error
- malformed pointer produces input error
- unsafe path returns a safe category without leaking the path
- human output has no body leakage
- JSON output has no body leakage
- `safe_summary` is metadata-only

The runtime fixture compatibility tests should run after the runtime API tests
and before any runtime CLI or Makefile target is added.

## 11. Release-Quality Implications

Current release-quality validates fixture contract only.

Runtime implementation should not be added to release-quality until:

- runtime API tests pass
- runtime fixture compatibility tests pass
- human output safety is reviewed
- JSON output safety is reviewed
- no body leakage is confirmed

Even after future runtime integration, release-quality success would not be
performance evidence.

## 12. What This Does NOT Do

This design does not:

- change fixtures
- change the validator
- implement runtime code
- implement generator code
- compute metrics
- use real data
- change Makefile targets
- change release-quality wrapper behavior
- change GitHub Actions workflows
- claim production readiness

## 13. Beginner-Friendly Explanation

A fixture contract is the agreement between test fixture files and the code
that checks them. It says which field names exist, which statuses are expected,
and which safety flags must stay true.

The runtime result is what future runtime code will return. The expected result
is what the existing fixture says the runtime should return. The validator acts
as the test oracle by comparing those two safe metadata summaries.

The alignment table exists before implementation so code does not accidentally
choose different field names, different reason codes, or a different meaning
for pass/fail.

Reason codes must match exactly because intentional invalid fixtures are only
successful when they fail for the expected reason.

## 14. Next Recommended Steps

Recommended sequence:

- runtime API minimal skeleton implementation
- runtime API tests
- runtime fixture compatibility tests

The safest next step is a minimal skeleton implementation rather than a broad
runtime implementation. The skeleton should load safe metadata, return safe
results, and align with the existing fixture contract before any generator or
artifact behavior exists.

Step264 follow-up:

The minimal scaffold runtime API skeleton has been added in
`python/learner_state/frozen_policy_generation.py`. It follows this alignment
design by returning safe metadata-only result fields, deterministic reason-code
ordering, explicit safety booleans, and suppressed artifact-body flags. Focused
runtime tests cover the current synthetic valid and invalid scaffold fixture
cases without changing fixture files or adding generator behavior.

Step265 follow-up:

[Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
turns this field/reason-code alignment into a future test plan. The planned
tests should use the scaffold fixture validator contract as the runtime test
oracle while keeping output body-free and synthetic-only.

Step266 follow-up:

The runtime fixture compatibility tests have been implemented in
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`.
They use the existing scaffold fixture validator comparison helper as the test
oracle for the runtime summary, while keeping assertions limited to safe case
labels, reason codes, statuses, deterministic summaries, and safety flags.

Step267 follow-up:

[Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
keeps this alignment boundary intact by designing the future CLI as a thin
runtime API wrapper. The CLI design does not add expected-result comparison to
the initial runtime command; compatibility tests remain responsible for
fixture/expected matching.

## 15. Update History

- Step263: initial docs-only runtime API and scaffold fixture validator
  alignment design.
- Step264: linked the minimal scaffold runtime API skeleton implementation
  status.
- Step265: linked the docs-only runtime fixture compatibility test design.
- Step266: linked the runtime fixture compatibility tests implementation.
- Step267: linked the runtime CLI design.

## Related Documents

- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- [Learner-state frozen policy generation scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_scaffold_fixture_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
