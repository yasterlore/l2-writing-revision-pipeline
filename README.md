# L2 Writing Revision Pipeline

Research software for studying keystroke-level L2 English free-writing
revision processes.

The repository currently focuses on synthetic-only development and validation.
It connects browser-side keystroke logging concepts to deterministic replay,
revision-event extraction, micro-episode construction, no-oracle candidate
selection, scoring experiments, learner-state validation scaffolds, and frozen
policy generation artifact/manifest scaffolds.

This repository is not a production data-processing system and is not a
repository for real participant data.

## Current Purpose

The current pipeline supports public-safe research-software development around:

- RawEvent-style keystroke logging data shapes
- deterministic validation and replay
- `revision_event` extraction
- `micro_episode` construction
- no-oracle safe views for candidate generation and ranking experiments
- synthetic candidate generation and OT-style scoring prototypes
- learner-state estimator input validation scaffolds
- frozen selective-prediction policy validation
- frozen policy generation scaffold, generator scaffold, artifact writer,
  artifact body, and manifest writer metadata-only checks
- runtime metadata-only manifest file writing smoke checks under a controlled
  output root
- synthetic metadata-only fixture roots for future artifact writer CLI actual
  invocation boundary validation

All public fixtures and checks are synthetic-only. The project is not at the
stage of handling real participant data or raw learner text.

## Language Architecture

TypeScript is used for the web logger:

- browser-side event collection UI
- local logger-web typecheck, test, and build checks
- no authoritative replay, extraction, ranking, or learner-state estimation

Rust is the deterministic keystroke-processing layer:

- raw-event schema and validation
- deterministic replay
- revision-event extraction
- micro-episode construction
- no-oracle audit and safe-view export
- CLI tools for validation and safe summaries

Python is used for research scaffolds and validation prototypes:

- candidate generation prototypes
- candidate feature extraction
- constraint violation and OT-style scoring experiments
- synthetic evaluation and diagnostic scaffolds
- learner-state audit/exporter/estimator-input validation
- selective prediction and frozen policy validation
- frozen policy generation scaffold, generator scaffold, artifact writer,
  artifact body, and manifest writer metadata-only validation
- artifact writer CLI integration fixture/runtime-fixture static validators and
  an initial metadata-only artifact writer CLI integration runtime boundary
- an expanded synthetic metadata-only runtime fixture root for future artifact
  writer CLI actual invocation metadata-only mode cases
- metadata-only runtime smoke checks, including opt-in manifest file writing
- actual-controlled v0.4 artifact body payload audit without payload emission
  as a standalone Makefile-targeted count-only metadata runner
- artifact body to manifest handoff metadata-only no-writer-invocation runner
  as a direct CLI-only synthetic 8-case contract check

## Safety Posture

The public repository is intentionally constrained:

- synthetic-only development and tests
- metadata-only outputs where applicable
- body suppression for artifact, manifest, request, pointer, and expected
  result content
- public-safe summaries instead of raw data dumps
- no raw rows, logits/probabilities, private paths, absolute local paths, raw
  learner text, generated policy bodies, artifact body payloads, manifest
  bodies, or written file JSON bodies in public output
- no real participant data in fixtures, examples, docs, logs, or CI

Real-data trials, if they ever happen, must be private/local or
institution-approved and must follow the
[private real-data readiness checklist](docs/private_real_data_readiness_checklist.md).

## No-Oracle Principle

Candidate generation, scoring, ranking, runtime validation, and learner-state
work must not use information that would only be available after the writing
moment being modeled.

Do not use these as generation, ranking, feature, validation-runtime, or
scoring inputs:

- `observed_after_text`
- `final_text`
- `gold_label`
- teacher corrections
- human corrections after writing
- future edits
- post-hoc annotations
- answer keys
- `local_context_after_observed`

Synthetic expected actions are allowed only as downstream synthetic evaluation
fixtures. They must not flow into candidate generation, feature extraction,
constraints, scoring, ranking, or runtime validation.

## Current Release-Quality Chain

The normal local release-quality wrapper is:

```bash
make check-release-quality
```

At a high level, it runs:

- whitespace and conflict-marker checks
- shell syntax checks
- synthetic no-config summary and diagnostic distribution checks
- Python `unittest` discovery and `compileall`
- learner-state audit, exporter, estimator-input, selective-prediction, frozen
  policy, and frozen policy generation validation
- frozen policy generation scaffold and generator scaffold fixture/runtime
  checks
- artifact writer fixture and runtime checks
- artifact writer CLI integration fixture/runtime-fixture checks; the initial
  artifact writer CLI integration runtime smoke target remains standalone and
  metadata-only until a later release-quality step
- artifact body generation integration fixture validation, included through a
  standalone Makefile target and release-quality wrapper check
- actual-controlled v0.4 artifact body payload audit without payload emission,
  available through the standalone Makefile target and release-quality wrapper
  check
  `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission`
  and direct runner
  `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py`;
  it checks the 36-case synthetic metadata-only root with aggregate
  count-only output, emits no payload bodies, invokes no manifest writer,
  writes no files, and runs after the deferred invalid-case usage_error /
  mismatch smoke and before artifact body fixture / CLI checks
- artifact body generation runtime integration plan-only bridge, available as
  `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
  over `valid/valid_minimal_suppressed_metadata_only_bridge` with no artifact
  body runtime invocation, no manifest writer, and no file writing; Step537
  adds standalone target
  `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`
  and Step539 adds that target to the release-quality wrapper after static
  artifact body generation integration fixture validation
- artifact body fixture, generation, safe-metadata generation, file-writing
  fixture, and isolated write checks
- manifest writer fixture, runtime fixture, no-file runtime, file-writing
  fixture, isolated write, production file-writing fixture, and runtime
  file-writing smoke checks
- config/scoring smoke checks
- Rust fmt/test/clippy
- synthetic policy checks
- logger-web typecheck/test/build

These checks are validation and safety gates. They are not model-performance
claims, production-readiness evidence, or real-data-readiness evidence.

## Common Commands

Run the full release-quality wrapper:

```bash
make check-release-quality
```

Run focused bundles:

```bash
make check-python
make check-rust
make check-logger
make check-fixtures
make check-policy
make check-summary-flow
```

Run manifest writer file-writing checks:

```bash
make check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures
make check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing
```

Run the direct actual-controlled v0.4 payload audit without payload emission:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection payload-audit-without-payload-emission --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-forbidden-body
```

Run the same audit through the standalone Makefile target:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission
```

Run the direct artifact body to manifest handoff metadata-only no-writer-invocation
check:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation --case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer --summary-only --no-manifest-writer --no-file-writing --fail-closed-on-forbidden-body
```

Run the same handoff check through the standalone Makefile target:

```bash
make check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation
```

This direct runner emits aggregate public-safe metadata only. It does not emit
artifact body payloads, generated policy bodies, manifest bodies, fixture JSON
bodies, raw stdout/stderr bodies, raw rows, logits/probabilities, private or
absolute path values, raw learner text, real participant data, or performance
metric bodies.

Run one synthetic E2E case:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
```

Generated outputs go under `tmp/`, which is Git-ignored. Do not copy generated
data bodies or raw logs into documentation.

## Implemented Scope

Currently implemented:

- TypeScript logger-web foundation
- Rust raw-event schema, validation, replay, extraction, micro-episode, and
  no-oracle audit crates
- Rust CLI validation and safe-view tooling
- Python candidate generation, feature, constraint, scoring, and synthetic
  evaluation scaffolds
- learner-state audit/exporter/estimator-input/selective-prediction/frozen
  policy validation scaffolds
- frozen policy generation scaffold and generator scaffold metadata-only
  runtimes
- frozen policy generation artifact writer metadata-only fixture and runtime
  checks
- artifact writer CLI integration static fixture validation, including the
  runtime fixture validator for the 54-case / 324-JSON synthetic
  metadata-only root with v0.1 plan-only and v0.2 actual-invocation fixture
  schema support
- artifact body suppressed and safe-metadata generation CLI checks
- artifact body generation runtime integration plan-only bridge CLI with schema
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`
  and standalone Makefile target
  `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`
  now included in the release-quality wrapper as a metadata-only selected-case
  smoke
- artifact body safe-metadata file writing and isolated write validation
- manifest writer metadata-only no-file runtime
- manifest writer metadata-only runtime file writing through opt-in
  `--manifest-out` under a controlled output root
- manifest writer file-writing, isolated-write, production fixture, and runtime
  file-writing smoke validation in the release-quality chain
- public-safe status markers for completed remote/manual Release Quality runs
  where markers exist

## Not Implemented

Not currently implemented or not claimed:

- production deployment
- public dataset release
- real participant data processing
- raw learner text public handling
- real gold-label workflow
- final learner-state estimation model
- automatic weight learning
- model-performance evidence
- F1, accuracy, ECE, AURCC, calibration, or risk-coverage results
- artifact writer CLI integration runtime
- production artifact/manifest deployment workflow
- public release readiness
- production readiness
- real-data readiness

## Documentation Map

- [Documentation index](docs/README.md)
- [Status markers](docs/status/README.md)
- [Public release checklist](docs/public_release_checklist.md)
- [Security policy](SECURITY.md)
- [No-oracle policy](docs/03_no_oracle_policy.md)
- [Synthetic data policy](docs/12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](docs/synthetic_e2e_pipeline.md)
- [Private real-data readiness checklist](docs/private_real_data_readiness_checklist.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](docs/milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Artifact writer CLI integration design](docs/frozen_policy_generation_artifact_writer_cli_integration_design.md)
- [Artifact writer CLI actual invocation fixture contract design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_contract_design.md)
- [Artifact writer CLI actual invocation fixture validator design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_design.md)
- [Artifact writer CLI actual invocation fixture validator Makefile target design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_makefile_target_design.md)
- [Artifact writer CLI actual invocation fixture validator release-quality integration design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_integration_design.md)
- [Artifact writer CLI actual invocation runtime implementation refinement design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_implementation_refinement_design.md)
- [Artifact writer CLI actual invocation runtime Makefile target design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_makefile_target_design.md)
- [Artifact writer CLI actual invocation runtime release-quality integration design](docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_integration_design.md)
- [Artifact body generation integration fixtures](tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/README.md)
- [Artifact body generation integration fixture validator Makefile target design](docs/frozen_policy_generation_artifact_body_generation_integration_fixture_validator_makefile_target_design.md)
- [Artifact body generation integration fixture validator release-quality integration design](docs/frozen_policy_generation_artifact_body_generation_integration_fixture_validator_release_quality_integration_design.md)
- [Artifact body generation runtime integration fixture update design](docs/frozen_policy_generation_artifact_body_generation_runtime_integration_fixture_update_design.md)
- [Artifact body generation runtime integration plan-only bridge Makefile target design](docs/frozen_policy_generation_artifact_body_generation_runtime_integration_plan_only_bridge_makefile_target_design.md)
- [Artifact body generation runtime integration plan-only bridge release-quality integration design](docs/frozen_policy_generation_artifact_body_generation_runtime_integration_plan_only_bridge_release_quality_integration_design.md)
- [Artifact body generation runtime integration planned safe-metadata v0.2 fixtures](tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/README.md): Step547 metadata-only/body-free planned fixture cases outside the active validator root; later steps add separate validator and metadata handoff runtime checks while keeping the active root separate.
- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`: Step549 public-safe validator CLI for the planned safe-metadata v0.2 root; validates 24 cases / 168 JSON with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`; Step551 adds a standalone Makefile target and Step553 adds the planned-root validator check to the release-quality wrapper.
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`: Step551 standalone Makefile target for the Step549 planned-root safe-metadata v0.2 validator CLI; expected aggregate is 24 cases / 168 JSON with 4 pass, 1 usage-error, 18 fail-closed, and 1 mismatch case. Step553 adds the target to the release-quality wrapper after the plan-only bridge smoke and before artifact body fixture validation.
- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`: Step559 adds `safe-metadata-smoke` as a metadata handoff only runtime mode with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`; it reads the planned primary case and emits public-safe body-free summary output without artifact body generation runtime invocation, manifest writer invocation, or file writing. Step561 adds a standalone Makefile target, and Step563 adds that target to the release-quality wrapper.
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`: Step561 standalone Makefile target for the Step559 `safe-metadata-smoke` runtime CLI; it remains metadata handoff only. Step563 adds the target to the release-quality wrapper after the safe-metadata v0.2 fixture validation check and before artifact body fixture validation.
- [Artifact body generation runtime invocation fixtures](tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/README.md): Step570 creates a planned metadata-only / body-free fixture root for a future artifact body generation runtime invocation boundary. The root contains 30 cases / 210 JSON files with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_v0.1`; validator implementation, runtime implementation, Makefile target, release-quality integration, artifact body generation runtime invocation, manifest writer integration, and file writing are not implemented in this step.
- [Actual-controlled artifact body generation runtime invocation fixtures](tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/README.md): Step587 creates a future v0.4 actual-controlled metadata-only fixture root with 36 cases / 252 parseable JSON files and schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_v0.1`; validator implementation, runtime implementation, actual runtime invocation, manifest writer integration, and file writing remain out of scope.
- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`: Step572 public-safe validator CLI for the Step570 runtime invocation fixture root; validates 30 cases / 210 JSON with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`. Step574 adds a standalone Makefile target while keeping release-quality integration, runtime integration, manifest writer integration, and file writing out of scope.
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`: Step574 standalone Makefile target for the Step572 runtime invocation fixture validator CLI; expected aggregate is 30 cases / 210 JSON with 6 pass, 1 usage-error, 22 fail-closed, and 1 mismatch case. Step581 adds this target to the release-quality wrapper after safe-metadata runtime smoke and before the planned-only v0.3 runtime invocation smoke; it does not invoke artifact body generation runtime, invoke manifest writer, or write files.
- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`: Step577 adds planned-only `artifact-body-runtime-invocation` mode with runtime schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`; the CLI reads the Step570 primary fixture case and emits a public-safe metadata-only summary with `artifact_body_runtime_invocation_planned=True` and `artifact_body_runtime_invoked=False`. Actual artifact body generation runtime invocation, manifest writer invocation, file writing, Makefile changes, release-quality changes, workflow changes, fixture JSON changes, validator changes, real-data use, metric use, and production readiness claims remain out of scope.
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`: Step579 standalone Makefile target for the Step577 planned-only v0.3 runtime invocation smoke; it runs the Step570 primary case and emits the same public-safe metadata-only summary. Step581 adds this target to the release-quality wrapper immediately after the runtime invocation fixture validator and before artifact body fixture validation; it does not invoke actual artifact body generation runtime, invoke manifest writer, or write files.

- `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`: Step589 standalone public-safe validator CLI for the Step587 actual-controlled fixture root. It validates 36 cases / 252 JSON with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`; focused tests live at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`. Makefile target integration, release-quality wrapper integration, runtime implementation, manifest writer integration, and file writing remain out of scope; Step590 is expected to design the standalone Makefile target.
- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`: Step591 standalone Makefile target for the Step589 actual-controlled fixture validator. It runs the validator over the Step587 root with expected aggregate 36 cases / 252 JSON, 6 pass, 3 usage-error, 26 fail-closed, and 1 mismatch case. It is not release-quality integrated and does not invoke actual artifact body generation runtime, invoke manifest writer, or write files.
- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`: Step593 adds direct v0.4 actual-controlled runtime CLI behavior for `artifact-body-runtime-invocation-controlled` with `--actual-invocation`. The selected case is `valid/valid_actual_controlled_safe_metadata_invocation`; output remains public-safe, summary-only, body-free, no-oracle, and count-only where applicable, with no manifest writer invocation or file writing. The target is not release-quality integrated in Step593.
- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`: Step595 standalone Makefile target for the Step593 v0.4 actual-controlled runtime CLI. It runs the selected Step587 primary case with `--actual-invocation`, expects public-safe v0.4 summary output, remains outside release-quality, does not invoke manifest writer, and does not write files.
- `scripts/check_release_quality.sh`: Step597 adds the Step591 actual-controlled fixture validator target and the Step595 v0.4 runtime smoke target to release-quality in that order, immediately after the planned-only v0.3 runtime invocation smoke. The checks remain public-safe, metadata-only / body-free, do not invoke manifest writer, and do not write files.
- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`: Step604 adds a direct CLI-only all-valid multi-case v0.4 runtime smoke runner with focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`. It discovers the 6 valid Step587 cases by directory name, emits aggregate public-safe key-value metadata with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1`, does not add a Makefile target or release-quality integration yet, does not invoke manifest writer, and does not write files.
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`: Step606 standalone Makefile target for the Step604 all-valid v0.4 multi-case runtime smoke runner. It emits aggregate public-safe metadata for 6 selected / executed / pass cases, remains outside release-quality, does not change Python code/tests or fixture JSON, does not invoke manifest writer, and does not write files.
- `scripts/check_release_quality.sh`: Step608 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 multi-case runtime smoke` after the actual-controlled v0.4 single-case smoke and before artifact body fixture / CLI checks. The check runs `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`, emits aggregate public-safe metadata, does not change Makefile, Python code/tests, or fixture JSON, does not invoke manifest writer, and does not write files.
- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`: Step615 adds a direct CLI-only invalid-case v0.4 fail-closed runtime smoke runner with focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`. It selects the fixed 26 invalid fail_closed cases from the Step614 matrix, defers 4 non-fail_closed invalid cases, emits aggregate public-safe metadata with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1`, does not add a Makefile target or release-quality integration yet, does not change fixture JSON, does not invoke manifest writer, and does not write files.
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`: Step617 standalone Makefile target for the Step615 invalid-case v0.4 fail-closed runtime smoke runner. It runs the `fail-closed-invalid` matrix with 26 selected invalid cases and 4 deferred invalid cases, expects aggregate public-safe metadata with 26 observed fail_closed cases, `unsafe_signal_total_count=26`, `forbidden_body_emitted_case_count=0`, and `residue_file_count=0`, remains outside release-quality, does not change Python code/tests or fixture JSON, does not invoke manifest writer, and does not write files.
- `scripts/check_release_quality.sh`: Step619 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 invalid-case runtime fail-closed smoke` after the all-valid multi-case runtime smoke and before artifact body fixture / CLI checks. The check runs `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`, expects aggregate public-safe metadata for 26 observed fail_closed cases with `unsafe_signal_total_count=26` and `forbidden_body_emitted_case_count=0`, does not change Makefile, Python code/tests, or fixture JSON, does not invoke manifest writer, and does not write files.
- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py`: Step626 adds a direct CLI-only deferred invalid-case usage_error / mismatch runner with focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py`. It processes the 4 deferred non-fail_closed invalid cases with `--case-selection deferred-invalid-usage-error-mismatch`, uses `processed_case_count=4` as the primary count, expects 3 usage_error and 1 mismatch per-case categories, emits aggregate public-safe metadata only, is not Makefile-targeted or release-quality integrated yet, does not change fixture JSON, does not invoke manifest writer, and does not write files.
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke`: Step628 standalone Makefile target for the Step626 deferred invalid-case usage_error / mismatch runner. It runs the `deferred-invalid-usage-error-mismatch` matrix with 4 processed deferred invalid cases, expects 3 usage_error and 1 mismatch per-case categories, remains outside release-quality, does not change Python code/tests or fixture JSON, does not implement payload audit, does not invoke manifest writer, and does not write files.
- `scripts/check_release_quality.sh`: Step630 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke` after the invalid fail_closed smoke and before artifact body fixture / CLI checks. The check runs `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke`, expects aggregate public-safe metadata for 4 processed deferred invalid cases with 3 observed usage_error categories and 1 observed mismatch category, does not change Makefile, Python code/tests, or fixture JSON, does not implement payload audit, does not invoke manifest writer, and does not write files.
- `scripts/check_release_quality.sh`: Step642 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 artifact body payload audit without payload emission` after the actual-controlled v0.4 deferred invalid-case usage_error / mismatch smoke and before artifact body fixture / CLI checks. The check runs the Step640 standalone target, expects the 36-case count-only metadata contract, emits no payload bodies, invokes no manifest writer, writes no files, and does not claim payload correctness, artifact body payload quality, production readiness, real-data readiness, or model performance.
- `scripts/check_release_quality.sh`: Step654 adds `release_quality_check: learner-state frozen policy generation artifact body to manifest handoff metadata-only no-writer-invocation` after artifact body generation safe-metadata CLI smoke and before artifact body file-writing / manifest writer checks. The check runs the Step652 standalone target, expects the 8-case metadata-only handoff contract, invokes no manifest writer, generates no manifest body, writes no files, emits no payload bodies, and does not remove the Step645 local/manual fallback limitation.
- `python/learner_state/frozen_policy_generation_manifest_writer_handoff_input_validation.py`: Step662 adds a direct CLI-only manifest writer handoff input validator with focused tests and synthetic fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input/`. It validates the fixed 23-case metadata-only contract, emits aggregate public-safe output, invokes no manifest writer, generates no manifest body, writes no files, emits no payload bodies, and is not Makefile-targeted or release-quality integrated yet.
- `check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation`: Step664 standalone Makefile target for the Step662 manifest writer handoff input validator. It runs the 23-case metadata-only contract with summary-only, no-manifest-writer, no-file-writing, and fail-closed-on-forbidden-body flags; it is not release-quality integrated yet and does not invoke manifest writer, generate manifest body, write files, or emit payload bodies.
- `scripts/check_release_quality.sh`: Step666 adds `release_quality_check: learner-state frozen policy generation manifest writer handoff input validation` after the artifact body to manifest handoff no-writer-invocation check and before artifact / manifest file-writing and manifest writer checks. The check runs the Step664 standalone target, expects the 23-case metadata-only handoff input contract, invokes no manifest writer, generates no manifest body, writes no files, emits no payload bodies, and does not remove the Step645 payload audit limitation.

## CI

GitHub Actions and local release-quality checks use synthetic fixtures only.
They must not process real participant data and must not publish raw logs,
fixture bodies, raw learner text, private paths, absolute local paths, or
performance evidence.

## License

The license is not finalized yet.

This project is under active research-software development. `LICENSE` is a
placeholder, not a final open-source license. Until a final license is selected
and the placeholder is replaced, reuse terms are not finalized.

A final license must be chosen before formal public release. See the
[public release checklist](docs/public_release_checklist.md).

## Security and Privacy

See [SECURITY.md](SECURITY.md). Treat all input as untrusted, keep real data
out of this repository, and do not publish logs, screenshots, generated
outputs, or reports that may contain participant text or private paths.
