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
- artifact body generation integration fixture root metadata, added as
  fixture-only contract evidence with a standalone validator module but without
  Makefile or release-quality integration
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
