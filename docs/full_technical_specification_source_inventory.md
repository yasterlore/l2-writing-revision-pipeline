# Full Technical Specification Source Inventory And Coverage Audit

Step-pretec-doc1 creates a source inventory and coverage audit for a later
full technical specification. It is not the full technical specification.

This document is docs-only. It does not change implementation code, fixtures,
Makefile targets, workflows, tests, or release-quality behavior. It does not
prove production readiness, real-data readiness, model performance, F1,
accuracy, ECE, AURCC, generated policy quality, learner-state estimator
correctness, or runtime integration correctness.

This inventory is based on repository scans of the current source tree. It is
intended to reduce omissions in the next specification step. It does not claim
that every possible repository fact is exhaustively covered.

## 1. Purpose

The purpose of this document is to map the repository sources that should feed
a future full technical specification:

- source code and package metadata
- docs and status markers
- Makefile targets
- shell scripts
- GitHub Actions workflows
- Python validators and CLIs
- Rust crates and CLI entrypoints
- TypeScript logger-web app files
- fixture roots and fixture README files
- schema and result-version naming surfaces
- public-safe, synthetic-only, metadata-only, no-oracle policies

This document is a coverage-audit inventory, not a complete specification.
Unknown or incompletely confirmed items are marked `not yet confirmed from
repository scan`.

## 2. Repository Scan Scope

The scan covered these repository areas:

| Area | Evidence path | Coverage note |
| --- | --- | --- |
| Root files | `README.md`, `SECURITY.md`, `LICENSE`, `Cargo.toml`, `Cargo.lock`, `Makefile` | Root documentation, Rust workspace, and Makefile orchestration were scanned. |
| Shell scripts | `scripts/` | Release-quality wrapper, synthetic E2E scripts, config/scoring smoke scripts, manifest schema helper, and synthetic policy script were scanned. |
| GitHub Actions | `.github/workflows/ci.yml`, `.github/workflows/release-quality.yml` | CI and manual Release Quality workflows were scanned. |
| Python packages | `python/candidate_generation/`, `python/evaluation/`, `python/ot_scorer/`, `python/learner_state/`, `python/test_support/`, `python/visualization/` | Python modules, tests, validators, CLIs, and support helpers were scanned. `python/visualization/` currently contains a placeholder only. |
| Rust crates | `crates/kslog_schema/`, `crates/kslog_validate/`, `crates/kslog_replay/`, `crates/kslog_extract/`, `crates/kslog_micro_episode/`, `crates/kslog_no_oracle_audit/`, `crates/kslog_cli/` | Workspace crates, crate READMEs, explained docs, libs, and CLI main were scanned. |
| Logger web app | `apps/logger-web/` | TypeScript, Vite, npm scripts, raw event app source, tests, package files, and generated build/dependency directories were scanned. |
| Fixtures | `tests/fixtures/` | Top-level fixture roots and fixture README files were scanned. Fixture JSON bodies are not copied here. |
| Docs | `docs/` | Architecture docs, policies, design docs, release-quality workflow docs, public checklist, milestone recaps, and schema docs were scanned. |
| Status markers | `docs/status/` | Public-safe status markers and status README were scanned. |

Generated or dependency directories such as Rust `target/`, logger-web
`node_modules/`, `dist/`, `dist-test/`, Python `__pycache__`, and project
`tmp/` were observed as non-source operational artifacts and should be treated
separately from source specification inputs.

## 3. Language And Runtime Inventory

| Language/runtime | Used in | Purpose | Main evidence paths | Full specification coverage |
| --- | --- | --- | --- | --- |
| Python | `python/` | Candidate generation, evaluation, OT-inspired scoring, learner-state validation/export, frozen policy generation scaffolds, artifact/body/manifest validators, safe output helper, CLIs, unit tests | `python/candidate_generation/`, `python/evaluation/`, `python/ot_scorer/`, `python/learner_state/`, `python/test_support/` | Include package layout, module responsibilities, CLI surfaces, validator contracts, summary schemas, and safety restrictions. |
| Rust | `crates/` | Keystroke log schema, validation, replay, extraction, micro-episode construction, no-oracle audit, CLI wrapper | `Cargo.toml`, `crates/*/Cargo.toml`, `crates/kslog_cli/src/main.rs` | Include workspace members, crate boundaries, Rust CLI commands, schema/replay/extract/audit flow, tests, and CI checks. |
| TypeScript | `apps/logger-web/src/`, `apps/logger-web/tests/` | Browser-side synthetic raw event logger and raw event tests | `apps/logger-web/src/main.ts`, `apps/logger-web/src/rawEvent.ts`, `apps/logger-web/tests/rawEvent.test.ts` | Include app purpose, event model, browser constraints, test/build commands, and synthetic-only limits. |
| JavaScript / Node / npm | `apps/logger-web/` | Vite build/test runtime, npm scripts | `apps/logger-web/package.json`, `apps/logger-web/package-lock.json` | Include Node setup, npm scripts, Vite, TypeScript build and test flow. |
| Shell | `scripts/` | Pipeline smoke runs, release-quality wrapper, summary manifest/schema checks, synthetic policy and config/scoring checks | `scripts/check_release_quality.sh`, `scripts/run_synthetic_e2e_summary.sh`, `scripts/lib/summary_manifest_schema.sh` | Include script categories, safe-output behavior, tmp/residue policy, and sequential execution constraints. |
| Makefile | `Makefile` | Thin entrypoints over scripts, validators, Rust checks, logger checks, and release-quality | `Makefile` | Include all targets, command mappings, target grouping, standalone vs release-quality inclusion, and nonparallel policy. |
| GitHub Actions YAML | `.github/workflows/` | CI and manual release-quality execution | `.github/workflows/ci.yml`, `.github/workflows/release-quality.yml` | Include workflow names, jobs, setup actions, versions, commands, and non-proof statements. |
| Markdown | `README.md`, `SECURITY.md`, `docs/`, `crates/*/README.md`, fixture READMEs | Project, policy, design, status, and recap documentation | `docs/README.md`, `docs/status/README.md`, fixture READMEs | Include documentation taxonomy and source-of-truth relationships. |
| JSON / JSONL / CSV | fixtures, synthetic outputs, schema docs | Fixture inputs/expected metadata, synthetic raw event formats, summary manifests, diagnostics, config, result summaries | `tests/fixtures/`, `docs/schemas/summary_manifest_schema_v1.json` | Include data formats and schema/result version names without copying payload bodies. |
| HTML/CSS/Vite | `apps/logger-web/` | Browser logger UI/build shell | `apps/logger-web/index.html`, `apps/logger-web/src/styles.css`, `apps/logger-web/vite.config.ts` | Include UI/build architecture and synthetic-only browser logging boundary. |

## 4. Architecture Inventory

| Component | Exists in repository | Evidence paths | Specification coverage required |
| --- | --- | --- | --- |
| Web logger | yes | `apps/logger-web/` | Browser event collection surface, raw event shape, synthetic-only scope, TypeScript/Vite build/test commands. |
| Raw event schema | yes | `crates/kslog_schema/`, `docs/04_raw_event_schema.md`, `apps/logger-web/src/rawEvent.ts` | Event types, safe fields, schema constraints, and Rust/TypeScript relationship. |
| Replay | yes | `crates/kslog_replay/`, `docs/05_text_replay_spec.md` | Replay model and constraints; no raw learner text copied into public docs. |
| Validation | yes | `crates/kslog_validate/`, `python/*_validation.py` | Rust event validation plus Python fixture validators. |
| No-oracle audit | yes | `crates/kslog_no_oracle_audit/`, `docs/03_no_oracle_policy.md`, `python/learner_state/sequence_audit.py` | No future information, no final/gold labels, no scoring feedback leakage. |
| Revision event extraction | yes | `crates/kslog_extract/`, `docs/06_revision_event_spec.md` | Extraction flow and synthetic fixtures. |
| Micro episode construction | yes | `crates/kslog_micro_episode/`, `docs/07_micro_episode_spec.md` | Episode construction and no-oracle boundary. |
| Candidate generation | yes | `python/candidate_generation/`, `docs/08_candidate_generation_spec.md` | CLI/module inputs and outputs, synthetic examples, no production claims. |
| Feature extraction | yes | `python/ot_scorer/features.py`, `python/ot_scorer/feature_builder.py` | Feature schema and local pattern docs. |
| OT-inspired scoring | yes | `python/ot_scorer/`, `docs/09_ot_scoring_spec.md` | Constraint/violation scoring, hand weights, diagnostic summaries. |
| Hand weight config | yes | `python/ot_scorer/weight_config.py`, `python/ot_scorer/validate_weight_config.py`, `tests/fixtures/synthetic/hand_weight_configs/` | Config schema, validation, ranking diff checks, safe examples. |
| Synthetic E2E summary | yes | `scripts/run_synthetic_e2e_summary.sh`, `docs/synthetic_e2e_pipeline.md` | Synthetic pipeline, output manifests, tmp behavior. |
| Summary manifest | yes | `scripts/lib/summary_manifest_schema.sh`, `docs/schemas/summary_manifest_schema_v1.json` | Manifest schema, sync checks, allowed-key hardening plans. |
| Diagnostic distribution | yes | `scripts/check_synthetic_diagnostic_distribution.sh`, `python/ot_scorer/diagnostic_summary.py` | Count-only diagnostic summary checks. |
| Learner-state sequence audit | yes | `python/learner_state/sequence_audit.py`, `tests/fixtures/learner_state_sequence_audit/` | Fixture/root modes, audit result schema, no-oracle constraints. |
| Learner-state sequence exporter | yes | `python/learner_state/sequence_exporter.py`, `tests/fixtures/learner_state_sequence_exporter/` | Exporter CLI, separated outputs, tmp output policy. |
| Learner-state estimator input | yes | `python/learner_state/estimator_input.py`, `tests/fixtures/learner_state_estimator_input/` | Input validation only; no estimator model correctness claim. |
| Selective prediction validation | yes | `python/learner_state/selective_prediction_validation.py`, `tests/fixtures/learner_state_selective_prediction/` | Calibration fixture validation; no metric achievement claim. |
| Frozen policy validation | yes | `python/learner_state/frozen_policy_validation.py`, `tests/fixtures/learner_state_frozen_selective_prediction_policy/` | Frozen policy fixture validation and CLI. |
| Frozen policy generation validation | yes | `python/learner_state/frozen_policy_generation_validation.py`, `tests/fixtures/learner_state_frozen_policy_generation/` | Generation fixture validation only. |
| Frozen policy generation scaffold runtime | yes | `python/learner_state/frozen_policy_generation.py`, `tests/fixtures/learner_state_frozen_policy_generation_scaffold/` | Metadata-only runtime scaffold and smoke target. |
| Generator scaffold | yes | `python/learner_state/frozen_policy_generation_generator_scaffold.py`, fixture validator and fixture root | Metadata-only generator scaffold skeleton; no generated policy quality claim. |
| Artifact writer | yes | `python/learner_state/frozen_policy_generation_artifact_writer.py`, artifact writer fixture validator/root | Metadata-only writer runtime/fixtures; artifact body remains suppressed. |
| Artifact writer CLI integration fixture validation | yes | `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`, fixture root | Static fixture validation integrated into release-quality. |
| Artifact writer CLI integration runtime fixtures | yes | `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`, validator module | Static runtime fixture validation target exists; runtime integration is not implemented and not release-quality integrated yet. |
| Artifact writer CLI actual invocation fixtures | yes | `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/` | Step498 fixture root; Step500 static validator implemented; actual invocation implementation is not implemented. |
| Artifact body generation | yes | `python/learner_state/frozen_policy_generation_artifact_body.py` | Suppressed and safe-metadata CLI smoke; no body payload copied. |
| Artifact body file writing | yes | fixture validator roots/modules and Makefile targets | File-writing fixture validation and smoke boundaries. |
| Artifact body isolated write validation | yes | `python/learner_state/frozen_policy_generation_artifact_body_isolated_write_validation.py` | Isolated safe write validation and residue checks. |
| Manifest writer | yes | `python/learner_state/frozen_policy_generation_manifest_writer.py` | Metadata-only manifest writer runtime; manifest body generation remains separate. |
| Manifest writer runtime | yes | runtime fixture validator/root and runtime smoke | No-file runtime smoke and runtime fixture validation. |
| Manifest writer file writing | yes | file-writing fixture validator/root and runtime file-writing smoke | Opt-in safe path, metadata-only file writing, cleanup. |
| Manifest writer isolated write validation | yes | isolated write validator/root | Safe-root and residue policy. |
| Manifest writer production file writing fixtures | yes | production file-writing fixture validator/root | Fixture validation only; no production readiness claim. |
| Release-quality chain | yes | `scripts/check_release_quality.sh`, `Makefile` | Ordered wrapper, labels, commands, proof/non-proof boundaries. |
| Public release checklist | yes | `docs/public_release_checklist.md` | Public safety gates and documentation review. |
| Security/privacy policy | yes | `SECURITY.md`, `docs/security_checklist.md`, policy docs | Synthetic-only, privacy, public-safe reporting rules. |

## 5. CLI Inventory

The future full specification should include the following command surfaces.
Inputs and outputs must be described as metadata-only or synthetic-only where
applicable. Body payload examples should not be copied.

| CLI category | Command/location | Purpose | Input type | Output type | Writes files | Makefile/release-quality status |
| --- | --- | --- | --- | --- | --- | --- |
| Rust CLI | `cargo run -p kslog_cli -- validate ...`, `crates/kslog_cli/src/main.rs` | Validate and process synthetic keystroke log fixtures | synthetic fixture paths | command status and safe diagnostics | no for validation path | CI uses validation command; release-quality uses cargo checks. |
| Candidate generation | `python -m candidate_generation.generate` | Generate candidates from synthetic inputs | fixture/config paths | candidate outputs/summaries | not yet fully inventoried; not yet confirmed from repository scan | not directly visible in release-quality wrapper. |
| Evaluation | `python -m evaluation.evaluate` and `python -m evaluation.expected_action_registry` | Evaluate synthetic expected actions and registries | fixture paths | reports/counts | not yet confirmed from repository scan | not directly visible in release-quality wrapper. |
| OT scorer tools | `python -m ot_scorer.features`, `constraints`, `score`, `summarize_diagnostics`, `validate_weight_config`, `score_fixture_lock`, `config_ranking_diff` | Feature/constraint/scoring/config diagnostics | synthetic fixture/config paths | safe summaries or validation status | some scripts write synthetic summaries under controlled paths | Makefile config/scoring smoke targets and release-quality wrapper include related scripts. |
| Learner-state sequence audit | `python -m learner_state.sequence_audit` | Validate sequence audit fixtures or datasets | fixture root/case or dataset metadata | safe audit summary | no by default | Makefile and release-quality included. |
| Learner-state exporter | `python -m learner_state.sequence_exporter` | Export synthetic learner-state sequence artifacts | synthetic fixture metadata and output dirs | separated feature/label/manifest outputs plus safe summary | yes, to caller-provided safe tmp dirs | Makefile and release-quality included. |
| Estimator input | `python -m learner_state.estimator_input` | Validate estimator input fixtures | fixture root/case | safe summary | no | Makefile and release-quality included. |
| Selective prediction validation | `python -m learner_state.selective_prediction_validation` | Validate selective prediction/calibration fixtures | fixture root/case | safe summary | no | Makefile and release-quality included. |
| Frozen policy validation | `python -m learner_state.frozen_policy_validation` | Validate frozen policy fixtures | fixture root/case | safe summary | no | Makefile and release-quality included. |
| Frozen policy generation validation | `python -m learner_state.frozen_policy_generation_validation` | Validate frozen policy generation fixtures | fixture root/case | safe summary | no | Makefile and release-quality included. |
| Frozen policy generation scaffold runtime | `python -m learner_state.frozen_policy_generation` | Run metadata-only scaffold runtime | request/pointer metadata | safe runtime summary | no artifact writing | Makefile and release-quality included. |
| Generator scaffold runtime | `python -m learner_state.frozen_policy_generation_generator_scaffold` | Run metadata-only generator scaffold | request/pointer metadata | safe summary | no artifact body/file writing | Makefile and release-quality included. |
| Artifact writer runtime | `python -m learner_state.frozen_policy_generation_artifact_writer` | Run metadata-only artifact writer runtime smoke | metadata-only request/pointer | safe summary | no body writing | Makefile and release-quality included. |
| Artifact writer CLI integration fixture validator | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | Static validation of CLI integration fixture contract | fixture root/case | safe count-only summary | no | Makefile and release-quality included. |
| Artifact writer CLI integration runtime fixture validator | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | Static validation of future runtime fixture contract | fixture root/case | safe count-only summary | no | Step511 validator schema v0.2 supports the 54-case / 324-JSON mixed v0.1/v0.2 fixture root through the existing Makefile target and wrapper check. |
| Artifact body runtime/generation | `python -m learner_state.frozen_policy_generation_artifact_body` | Body-suppressed and safe-metadata generation smoke | metadata-only request/pointer | safe summary | no body payload output | Makefile and release-quality included. |
| Artifact body file/isolated validation | dedicated `learner_state` validation modules | Validate file-writing and isolated-write fixture contracts | fixture roots | safe summary | validator writes no files; smoke targets may use tmp safely | Makefile and release-quality included for fixture/isolation targets. |
| Manifest writer runtime | `python -m learner_state.frozen_policy_generation_manifest_writer` | Metadata-only manifest writer runtime and runtime file-writing smoke | metadata-only request/pointer | safe summary | opt-in safe path only for file-writing smoke | Makefile and release-quality included. |
| Manifest writer validators | dedicated `learner_state` validation modules | Validate manifest writer fixture/runtime/file-writing/isolated/production contracts | fixture roots | safe summary | validators write no files | Makefile and release-quality included. |
| Shell scripts | `scripts/*.sh` | E2E synthetic summaries, release-quality, policy and smoke checks | repository fixtures/config | safe status/count summaries | controlled tmp outputs for E2E summaries | Makefile/release-quality include key scripts. |
| npm scripts | `npm run typecheck`, `npm test`, `npm run build`, `npm run dev` in `apps/logger-web` | TypeScript typecheck, test, build, local dev server | logger-web source | build/test output | build writes `dist/`/`dist-test/` | Release-quality includes typecheck/test/build, not dev. |

## 6. Makefile Target Inventory

`Makefile` is marked `.NOTPARALLEL`, and several user-facing instructions
also require major checks to be run sequentially. The full specification should
copy target names and command intent, not command output bodies.

| Target group | Targets | Release-quality inclusion |
| --- | --- | --- |
| Release-quality and summary | `check-release-quality`, `check-summary`, `check-manifest-sync`, `check-diagnostic-distribution`, `check-summary-flow`, `check-config-smoke`, `check-all` | `check-release-quality` runs wrapper; summary/config components are also called by wrapper or grouped Make targets. |
| Language checks | `check-python`, `check-rust`, `check-logger`, `check-policy`, `check-fixtures` | Wrapper runs Python unittest/compileall, Rust fmt/test/clippy, synthetic policy, logger typecheck/test/build, and fixture checks by explicit target. |
| Learner-state core | `check-learner-state-audit-fixtures`, `check-learner-state-exporter-cli`, `check-learner-state-estimator-input`, `check-learner-state-selective-prediction` | Included in release-quality. |
| Frozen policy core | `check-learner-state-frozen-policy`, `check-learner-state-frozen-policy-generation` | Included in release-quality. |
| Scaffold/generator scaffold | `check-learner-state-frozen-policy-generation-scaffold-fixtures`, `check-learner-state-frozen-policy-generation-scaffold-runtime`, `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`, `check-learner-state-frozen-policy-generation-generator-scaffold-runtime` | Included in release-quality. |
| Artifact writer | `check-learner-state-frozen-policy-generation-artifact-writer-fixtures`, `check-learner-state-frozen-policy-generation-artifact-writer-runtime`, `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`, `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`, `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime` | Fixture/runtime/static validation targets are in release-quality where noted; Step493 adds the runtime smoke target to release-quality. |
| Artifact body | `check-learner-state-frozen-policy-generation-artifact-body-fixtures`, `check-learner-state-frozen-policy-generation-artifact-body-generation`, `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`, `check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`, `check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`, `check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation` | Fixture/generation/safe-metadata/file-writing/isolated validation targets are in release-quality; file-writing smoke target is present but release-quality inclusion is not yet confirmed from wrapper scan. |
| Manifest writer | `check-learner-state-frozen-policy-generation-manifest-writer-fixtures`, `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`, `check-learner-state-frozen-policy-generation-manifest-writer-runtime`, `check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`, `check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`, `check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`, `check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing` | Included in release-quality. |

The full specification should include each target's exact command from
`Makefile`, expected safe output type, write behavior, and release-quality
status. It should not include raw command output.

## 7. GitHub Actions / CI Inventory

| Workflow | Jobs | Setup | Commands | What it proves | What it does not prove |
| --- | --- | --- | --- | --- | --- |
| `.github/workflows/ci.yml` (`CI`) | `rust` / `Rust workspace` | checkout, stable Rust with rustfmt and clippy | cargo fmt/test/clippy, synthetic policy, `kslog_cli validate`, invalid validation smoke, synthetic E2E pipeline | Rust workspace and selected synthetic validation paths run in CI | It does not prove production readiness, real-data readiness, or model performance. |
| `.github/workflows/release-quality.yml` (`Release Quality`) | `release-quality` / `Release quality` | checkout, Python 3.11, stable Rust with rustfmt/clippy, Node 22 with npm cache, `npm ci` for logger-web | `scripts/check_release_quality.sh` | Manual Release Quality wrapper executes ordered checks in GitHub Actions | It does not prove real-data readiness, production deployment, runtime integrations that are not included in wrapper, or metric achievement. |

## 8. Fixture Inventory

Fixture JSON bodies are not copied here. Case counts should be taken from
fixture README files or validators where available; otherwise the full
specification should compute them safely from file counts.

| Fixture root | Purpose | Validator/target | Release-quality status |
| --- | --- | --- | --- |
| `tests/fixtures/synthetic/` and subroots | Synthetic raw events, expected actions, candidate scores/features/sets, constraint violations, hand weight configs, safe views | Rust/Python scripts and scoring checks | Used by CI/release-quality scripts. |
| `tests/fixtures/learner_state_sequence_audit/` | Sequence audit fixtures | `learner_state.sequence_audit`, `check-learner-state-audit-fixtures` | included. |
| `tests/fixtures/learner_state_sequence_exporter/` | Exporter input/edge fixtures | `learner_state.sequence_exporter`, `check-learner-state-exporter-cli` | included. |
| `tests/fixtures/learner_state_estimator_input/` | Estimator input validation fixtures | `learner_state.estimator_input`, `check-learner-state-estimator-input` | included. |
| `tests/fixtures/learner_state_selective_prediction/` | Selective prediction/calibration fixtures | `learner_state.selective_prediction_validation`, `check-learner-state-selective-prediction` | included. |
| `tests/fixtures/learner_state_frozen_selective_prediction_policy/` | Frozen policy fixtures | `learner_state.frozen_policy_validation`, `check-learner-state-frozen-policy` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation/` | Frozen policy generation validation fixtures | `learner_state.frozen_policy_generation_validation`, `check-learner-state-frozen-policy-generation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_scaffold/` | Scaffold fixtures | `learner_state.frozen_policy_generation_scaffold_fixture_validation`, scaffold runtime tests | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/` | Generator scaffold fixtures | `learner_state.frozen_policy_generation_generator_scaffold_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/` | Artifact writer contract fixtures | `learner_state.frozen_policy_generation_artifact_writer_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/` | Artifact writer CLI integration fixture contract | `learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/` | Artifact writer CLI integration runtime fixture contract; 54 cases, 324 JSON files; original 30 v0.1 plan-only cases preserved and 24 v0.2 actual-invocation metadata-only cases added | `learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation`, `learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime`, Makefile target, release-quality wrapper check | Step511 release-quality integrated static validation supports v0.1/v0.2 fixture schemas; Step513 runtime module supports explicit v0.2 metadata-only summary mode without file writing or downstream generation integration. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/` | Future artifact writer CLI actual invocation fixture contract; 32 cases, 192 JSON files, metadata-only sentinel fixtures | Step500 static validator module/CLI and focused tests; Step502 standalone Makefile target; Step504 release-quality wrapper check | fixture root and wrapper-integrated static validation; actual invocation not implemented. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body/` | Artifact body fixture contract | `learner_state.frozen_policy_generation_artifact_body_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/` | Artifact body file-writing fixture contract | `learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/` | Artifact body isolated write validation | `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/` | Manifest writer fixture contract | `learner_state.frozen_policy_generation_manifest_writer_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/` | Manifest writer runtime fixture contract | `learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/` | Manifest writer file-writing fixture contract | `learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/` | Manifest writer isolated write validation | `learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation` | included. |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing/` | Manifest writer production-file-writing fixture validation | `learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation` | included; fixture validation only, not production readiness. |

Forbidden content policy across fixture roots: fixtures are synthetic-only and
must not include prohibited payload bodies, raw learner text, raw rows, logits,
probabilities, private path values, absolute path values, real participant
data, final corrected text, observed-after text, gold labels, post-hoc
annotation, test-set tuning, or scoring feedback payloads. Invalid cases use
controlled markers and reason codes rather than actual prohibited payloads.

## 9. Validator Inventory

| Validator/module | Test path | Fixture root | Mode/schema surface | Makefile target | Release-quality |
| --- | --- | --- | --- | --- | --- |
| `learner_state.sequence_audit` | `python/learner_state/tests/test_sequence_audit*.py` | `tests/fixtures/learner_state_sequence_audit/` | sequence audit result/manifest schemas | `check-learner-state-audit-fixtures` | included |
| `learner_state.sequence_exporter` | `python/learner_state/tests/test_sequence_exporter*.py` | `tests/fixtures/learner_state_sequence_exporter/` | sequence manifest/export output schemas | `check-learner-state-exporter-cli` | included |
| `learner_state.estimator_input` | `python/learner_state/tests/test_estimator_input*.py` | `tests/fixtures/learner_state_estimator_input/` | `learner_state_estimator_input_validation_v0.1` | `check-learner-state-estimator-input` | included |
| `learner_state.selective_prediction_validation` | `python/learner_state/tests/test_selective_prediction_validation*.py` | `tests/fixtures/learner_state_selective_prediction/` | `learner_state_selective_prediction_validation_v0.1` | `check-learner-state-selective-prediction` | included |
| `learner_state.frozen_policy_validation` | `python/learner_state/tests/test_frozen_policy_validation*.py` | `tests/fixtures/learner_state_frozen_selective_prediction_policy/` | `learner_state_frozen_policy_validation_v0.1` | `check-learner-state-frozen-policy` | included |
| `learner_state.frozen_policy_generation_validation` | `python/learner_state/tests/test_frozen_policy_generation_validation*.py` | `tests/fixtures/learner_state_frozen_policy_generation/` | `learner_state_frozen_policy_generation_validation_v0.1` | `check-learner-state-frozen-policy-generation` | included |
| `learner_state.frozen_policy_generation_scaffold_fixture_validation` | scaffold fixture validation tests | `tests/fixtures/learner_state_frozen_policy_generation_scaffold/` | `learner_state_frozen_policy_generation_scaffold_fixture_validation_v0.1` | scaffold fixture target | included |
| `learner_state.frozen_policy_generation_generator_scaffold_fixture_validation` | generator scaffold fixture tests | generator scaffold fixture root | `learner_state_frozen_policy_generation_generator_scaffold_fixture_validation_v0.1` | generator scaffold fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_fixture_validation` | artifact writer fixture tests | artifact writer fixture root | `learner_state_frozen_policy_generation_artifact_writer_fixture_validation_v0.1` | artifact writer fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | CLI integration fixture tests | artifact writer CLI integration fixture root | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1` | CLI integration fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | runtime fixture validator tests | artifact writer CLI integration runtime fixture root | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2` | runtime fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime` | runtime focused tests | artifact writer CLI integration runtime fixture root | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1` and explicit `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2` mode | `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime` | wrapper included after Step493 |
| `learner_state.frozen_policy_generation_artifact_body_generation_integration_fixture_validation` | focused validator tests | `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/` | `learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validation_v0.1` and fixture metadata family | none | not yet included |
| `learner_state.frozen_policy_generation_artifact_body_fixture_validation` | artifact body fixture tests | artifact body fixture root | `learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1` | artifact body fixture target | included |
| `learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation` | file-writing fixture tests | artifact body file-writing root | file-writing validation schema | artifact body file-writing target | included |
| `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation` | isolated write tests | artifact body isolated write root | isolated write validation schema | artifact body isolated write target | included |
| `learner_state.frozen_policy_generation_manifest_writer_fixture_validation` | manifest writer fixture tests | manifest writer fixture root | manifest writer fixture validation schema | manifest writer fixture target | included |
| `learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation` | runtime fixture tests | manifest writer runtime root | runtime fixture validation schema | manifest writer runtime fixture target | included |
| `learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation` | file-writing fixture tests | manifest writer file-writing root | file-writing fixture validation schema | manifest writer file-writing target | included |
| `learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation` | isolated write tests | manifest writer isolated write root | isolated write validation schema | manifest writer isolated write target | included |
| `learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation` | production file-writing fixture tests | manifest writer production file-writing root | production file-writing validation schema | manifest writer production file-writing target | included |

The full specification should include each validator's CLI args, summary
fields, expected counts, error categories, safe marker policy, and no-oracle
policy. Some exact expected counts are documented in status markers and fixture
READMEs; counts not documented should be recomputed safely during the full
specification step.

## 10. Schema And Data Format Inventory

Repository scans found schema/result/version names in Python modules, fixture
metadata, docs, and schema files. The full specification should group them
without copying JSON bodies.

| Schema/data family | Examples observed | Evidence paths |
| --- | --- | --- |
| Raw event and safe view | raw event schema docs, safe synthetic views | `docs/04_raw_event_schema.md`, `crates/kslog_schema/`, `tests/fixtures/synthetic/safe_views/` |
| Summary manifest | `summary_manifest_schema_v1`, manifest sync helper constants | `docs/schemas/summary_manifest_schema_v1.json`, `scripts/lib/summary_manifest_schema.sh` |
| Candidate/evaluation/scoring | `candidate_feature_schema_v0_3`, `evaluation_report_schema_v0_1`, `diagnostic_summary_schema_v0_1`, `hand_weight_config_schema_v0_1`, OT constraint schemas | `python/ot_scorer/`, `docs/local_pattern_feature_schema_v0_3_plan.md`, `docs/hand_weight_config_schema_plan.md` |
| Learner-state audit/exporter | learner-state sequence manifest/result schema names | `python/learner_state/sequence_audit.py`, `python/learner_state/sequence_exporter.py`, fixture roots |
| Estimator/selective prediction | `learner_state_estimator_input_validation_v0.1`, `learner_state_selective_prediction_validation_v0.1` | `python/learner_state/estimator_input.py`, `python/learner_state/selective_prediction_validation.py` |
| Frozen policy | `frozen_selective_prediction_policy_schema_v0_1`, `learner_state_frozen_policy_validation_v0.1` | `python/learner_state/frozen_policy_validation.py`, frozen policy fixtures |
| Frozen policy generation | `frozen_policy_generation_request_schema_v0_1`, `frozen_policy_generation_input_pointer_schema_v0_1`, `learner_state_frozen_policy_generation_validation_v0.1` | `python/learner_state/frozen_policy_generation*.py` |
| Scaffold/generator scaffold | scaffold request/pointer/result/runtime schema names, generator scaffold result schema names | scaffold and generator scaffold modules/fixtures/docs |
| Artifact writer | artifact writer expected/result/pointer schema names and fixture validation schema | artifact writer modules/fixtures/docs |
| Artifact writer CLI integration | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_result_v0.1`, runtime fixture validator schema `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`, and runtime fixture v0.2 metadata-only schema family added by Step509 | CLI integration fixture validator/root/docs/tests |
| Artifact writer CLI integration runtime fixtures | runtime fixture validation/result/request/pointer/case metadata schema names | runtime fixture validator/root/docs |
| Artifact writer CLI actual invocation fixtures | actual invocation case/request/pointer/invocation/expected-summary/error metadata schema names | Step498 fixture root and README |
| Artifact body generation integration fixtures | integration fixture validation schema plus case/runtime-summary/request/pointer/generation/expected-summary/error metadata schema names | Step523 fixture root, Step525 validator module/tests/README, Step527 standalone Makefile target, and Step529 wrapper check |
| Artifact body | artifact body expected/result/generation/pointer schema names | artifact body modules/fixtures/docs |
| Manifest writer | manifest writer request/result/runtime/file-writing/isolated/production schema names | manifest writer modules/fixtures/docs |
| Release-quality status markers | run-status marker docs with pass-only/count-only metadata | `docs/status/` |

Schema scan produced many additional synthetic invalid-case marker names. The
full specification should separate stable schema names from synthetic invalid
case identifiers and reason-code markers.

## 11. Safety / Privacy / No-Oracle Inventory

The full specification must include these policies:

- synthetic-only repository and fixture posture
- metadata-only summaries for artifact/manifest/frozen-policy generation flows
- body-free public output policy
- no raw rows in public docs or summaries
- no logits or probability dumps in public docs or summaries
- no private path values or absolute local path values in public docs or
  summaries
- no raw learner text in docs, fixtures, markers, or public summaries
- no `final_text`, `observed_after_text`, or gold labels
- no post-hoc annotation
- no test-set tuning
- no scoring feedback payload leakage
- opt-in safe-root policy for file-writing flows
- cleanup/residue checks for write-smoke or isolated-write targets
- public release policy and status marker policy
- raw logs and full job output are excluded from docs/status markers

Evidence paths include `SECURITY.md`, `docs/03_no_oracle_policy.md`,
`docs/10_data_quality_policy.md`, `docs/11_public_release_policy.md`,
`docs/12_synthetic_data_policy.md`, `docs/public_release_checklist.md`,
`docs/status/README.md`, validator modules, fixture READMEs, and status
markers.

## 12. Release-Quality Chain Inventory

`scripts/check_release_quality.sh` runs ordered checks with
`release_quality_check:` section labels. The full specification should include
the exact wrapper order, command, safe output type, and non-proof boundaries.

| Position | Label | Command/purpose | Safe output expectation |
| --- | --- | --- | --- |
| 1 | git diff whitespace | `git diff --check` | whitespace status only |
| 2 | conflict marker grep | internal grep with suppressed content | file/line locations only on failure, content suppressed |
| 3 | shell syntax | `sh -n` for summary and diagnostic scripts | syntax status |
| 4 | no-config synthetic summary | synthetic E2E summary script | synthetic summary status |
| 5 | summary manifest schema sync | schema sync script | schema sync status |
| 6 | synthetic diagnostic distribution | diagnostic distribution checker | count/status summary |
| 7 | markdown link check | manual marker | no automated proof |
| 8 | python checks | unittest discover and compileall | test/compile status |
| 9-18 | learner-state and frozen policy validation chain | learner-state audit/exporter/estimator/selective/frozen/generation/scaffold/generator checks | safe count-only summaries |
| 19 | artifact writer fixture validation | artifact writer fixture target | static metadata-only fixture validation |
| 20 | artifact writer runtime smoke | artifact writer runtime target | metadata-only runtime smoke summary |
| 21 | artifact writer CLI integration fixture validation | CLI integration fixture target | static count-only fixture validation |
| 22-27 | artifact body checks | fixture, generation, safe-metadata, file-writing, isolated-write checks | body-suppressed count/status summaries |
| 28-34 | manifest writer checks | fixture/runtime/file-writing/isolated/production/runtime-file-writing checks | metadata-only summaries and safe write-smoke status |
| 35 | config and scoring smoke checks | config-enabled summary/E2E, fixture lock, weight config, ranking diff | synthetic status/count summaries |
| 36 | rust checks | cargo fmt/test/clippy | Rust check status |
| 37 | synthetic policy | `scripts/check_synthetic_policy.sh` | policy status |
| 38 | logger-web checks | npm typecheck/test/build | TypeScript app status |
| 39 | complete | wrapper success marker | `content_suppressed=true` |

This chain proves that the wrapper checks completed in order in the local or
remote environment where it ran. It does not prove production readiness,
real-data readiness, model performance, or integrations not included in the
wrapper. The artifact writer CLI integration runtime fixture target is in the
wrapper as static validation. Step493 adds the artifact writer CLI integration
runtime smoke target to the wrapper after that static validation check.

## 13. Status Marker Inventory

Available status markers include milestone markers and release-quality remote
run markers under `docs/status/`.

| Marker family | Examples | Scope | Raw logs excluded |
| --- | --- | --- | --- |
| Milestone markers | `milestone_04_status.md`, `milestone_05_status.md` | Public-safe milestone documentation state | yes |
| Learner-state core | audit, exporter, estimator input, selective prediction, frozen policy, frozen policy generation markers | Release-quality wrapper inclusion and success metadata | yes |
| Scaffold/generator scaffold | scaffold fixture/runtime and generator scaffold fixture/runtime markers | Fixture/runtime target inclusion and pass-only metadata | yes |
| Artifact writer | artifact writer fixture/runtime and artifact writer CLI integration fixture markers | Fixture/runtime/CLI integration fixture validation inclusion | yes |
| Artifact body | artifact body fixture/generation/safe-metadata/file-writing/isolated-write markers | Body-suppressed and count-only validation/smoke evidence | yes |
| Manifest writer | manifest writer fixture/runtime/file-writing/isolated/production/runtime-file-writing markers | Metadata-only validation and safe file-writing smoke evidence | yes |

Each marker should be treated as a public-safe status record for its stated
scope only. Markers do not copy raw workflow logs, full job output, fixture
bodies, request/pointer/expected bodies, manifest bodies, artifact body
payloads, generated policy bodies, private path values, absolute path values,
raw learner text, or performance evidence.

## 14. Documentation Inventory

| Doc category | Evidence paths | Full specification use |
| --- | --- | --- |
| Project overview and beginner architecture | `docs/00_project_overview.md` through `docs/12_synthetic_data_policy.md` | Baseline architecture, policies, data-quality, and public release posture. |
| Pipeline/spec docs | raw event, replay, revision event, micro episode, candidate generation, OT scoring, evaluation docs | Core technical flow chapters. |
| Config/scoring docs | config-aware scorer, explicit config, diagnostic, summary manifest, hand weight docs | Scoring/config chapters and script relationships. |
| Learner-state docs | audit, exporter, estimator input, selective prediction, frozen policy docs | Learner-state validation/export chapters. |
| Frozen policy generation docs | scaffold/generator/artifact writer/artifact body/manifest writer design, fixture, validator, Makefile, release-quality, remote workflow docs | Artifact/manifest/generation infrastructure chapters. |
| Runtime fixture docs | artifact writer CLI integration runtime design/fixture/validator/Makefile target docs | Current future-runtime fixture validation status and boundaries. |
| Status docs | `docs/status/` | Public-safe remote/manual status evidence and non-proof boundaries. |
| Milestone recaps | `docs/milestone_*.md` | Historical implementation status and public-safe summary context. |
| Public/security docs | `docs/public_release_checklist.md`, `docs/security_checklist.md`, `SECURITY.md` | Public safety, privacy, and release checklist chapters. |

Docs with planned or design-only status should be clearly distinguished from
implemented modules, Makefile targets, release-quality integration, and remote
status markers.

## 15. Implementation Status Matrix

| Component | Current status from scan |
| --- | --- |
| Web logger | implemented TypeScript app with npm typecheck/test/build. |
| Rust schema/validate/replay/extract/micro-episode/no-oracle/CLI | implemented crates with CI checks. |
| Python candidate generation/evaluation/OT scoring | implemented modules and tests; release-quality inclusion varies by script/target. |
| Synthetic E2E summary and manifest checks | implemented shell scripts and Makefile/release-quality targets. |
| Learner-state audit/exporter/estimator input/selective prediction/frozen policy/frozen policy generation | implemented validators/CLIs/fixtures with Makefile and release-quality integration. |
| Frozen policy generation scaffold runtime | implemented metadata-only runtime scaffold with Makefile/release-quality/status marker. |
| Generator scaffold | implemented metadata-only scaffold and validation/smoke chain. |
| Artifact writer fixture/runtime | implemented metadata-only fixture validator and runtime smoke. |
| Artifact writer CLI integration fixture validation | implemented validator, standalone Makefile target, release-quality integration, and remote status marker. |
| Artifact writer CLI integration runtime fixture validation | fixture root, validator module/CLI/tests, and standalone Makefile target exist; release-quality integration not observed in wrapper; runtime integration not implemented. |
| Artifact writer CLI integration runtime | not implemented. |
| Artifact body generation | implemented suppressed and safe-metadata smoke boundaries; CLI integration beyond current safe boundary not claimed. |
| Artifact body generation CLI integration | not implemented as a broader integration flow. |
| Manifest writer fixture/runtime/file-writing/isolated/production file-writing validation | implemented metadata-only validators/smokes with release-quality coverage and status markers. |
| Manifest writer integration beyond current writer runtime | not implemented. |
| Manifest body generation | not implemented. |
| Production readiness | not proven. |
| Real-data readiness | not proven. |
| Model performance or metric achievement | not proven. |

## 16. Full Technical Specification Coverage Checklist

The next full specification should include at least these chapters:

- purpose and non-goals
- repository layout
- execution environment
- languages, runtimes, and dependencies
- Rust workspace and crates
- Python packages and modules
- TypeScript/logger-web app
- shell scripts and Makefile orchestration
- data model and schema inventory
- raw event, replay, revision event, and micro-episode flow
- candidate generation and evaluation
- OT-inspired scoring and hand weight configuration
- synthetic E2E summary and summary manifest
- learner-state audit/exporter/input/selective/frozen policy chain
- frozen policy generation scaffold/generator/artifact/manifest chain
- artifact body and manifest file-writing policies
- CLI inventory
- Makefile target inventory
- fixture roots and validator inventory
- release-quality wrapper and GitHub Actions workflows
- status markers and remote/manual run recording policy
- safety, privacy, synthetic-only, metadata-only, body-free, and no-oracle rules
- output files, safe summaries, and residue cleanup
- limitations, non-proofs, and future work

## 17. Traceability Table

| Component | Implementation files | Tests | Fixtures | Docs | Makefile target | Release-quality label | Status marker | Current status | Include in full spec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logger web | `apps/logger-web/src/` | `apps/logger-web/tests/` | not applicable | app README/EXPLAINED | `check-logger` | logger-web checks | none | implemented app checks | yes |
| Rust kslog pipeline | `crates/*/src/` | Rust crate tests | `tests/fixtures/synthetic/` | crate READMEs, core specs | `check-rust` | rust checks | none | implemented Rust checks | yes |
| Synthetic summary/config scoring | `scripts/`, `python/ot_scorer/` | Python tests | synthetic fixture roots | summary/config/scoring docs | summary/config targets | config and scoring smoke checks | none | implemented scripts/checks | yes |
| Learner-state audit | `python/learner_state/sequence_audit.py` | sequence audit tests | sequence audit fixtures | audit docs | audit fixture target | learner-state audit fixtures | audit marker | implemented | yes |
| Sequence exporter | `sequence_exporter.py` | exporter tests | exporter fixtures | exporter docs | exporter CLI target | exporter CLI smoke | exporter marker | implemented | yes |
| Estimator input | `estimator_input.py` | estimator input tests | estimator fixtures | estimator docs | estimator target | estimator input validation | estimator marker | validator-only | yes |
| Selective prediction | `selective_prediction_validation.py` | selective tests | selective fixtures | selective docs | selective target | selective prediction calibration validation | selective marker | validator-only | yes |
| Frozen policy | `frozen_policy_validation.py` | frozen policy tests | frozen policy fixtures | frozen policy docs | frozen policy target | frozen policy validation | frozen policy marker | validator-only | yes |
| Frozen policy generation | `frozen_policy_generation_validation.py` | generation validation tests | generation fixtures | generation docs | generation target | frozen policy generation validation | generation marker | validator-only | yes |
| Scaffold runtime | `frozen_policy_generation.py` | scaffold runtime tests | scaffold fixtures | scaffold runtime docs | scaffold runtime target | scaffold runtime smoke | scaffold runtime marker | metadata-only runtime | yes |
| Generator scaffold | `frozen_policy_generation_generator_scaffold.py` | generator tests | generator fixture root | generator docs | generator fixture/runtime targets | generator scaffold labels | generator markers | metadata-only scaffold | yes |
| Artifact writer | `frozen_policy_generation_artifact_writer.py` and fixture validator | artifact writer tests | artifact writer fixtures | artifact writer docs | artifact writer fixture/runtime targets | artifact writer fixture/runtime labels | artifact writer markers | metadata-only writer/smoke | yes |
| Artifact writer CLI integration fixture | CLI integration fixture validator | CLI integration tests | CLI integration fixtures | CLI integration docs | CLI integration fixture target | CLI integration fixture validation | CLI integration fixture marker | release-quality integrated fixture validation | yes |
| Artifact writer CLI integration runtime fixture | runtime fixture validator | runtime fixture validator tests | runtime fixture root | runtime fixture docs | runtime fixture target | none observed | none | standalone static validation | yes |
| Artifact writer CLI integration runtime | `frozen_policy_generation_artifact_writer_cli_integration_runtime.py` | runtime focused tests | runtime fixture root | runtime design docs | plan-only target plus Step515 actual invocation metadata-only target | plan-only runtime label plus Step517 actual invocation runtime smoke label | plan-only remote marker only | metadata-only runtime boundary; Step517 wrapper check runs the v0.2 smoke after static actual invocation fixture validation and before artifact body fixture validation, with no file writing or downstream integration | yes |
| Artifact writer CLI actual invocation fixture | static validator module | focused validator tests | actual invocation fixture root | actual invocation fixture docs | standalone validator target | actual invocation fixture validation | none | Step504 wrapper-integrated static validation; actual invocation not implemented | yes |
| Artifact body generation integration fixture | static validator module | focused validator tests | integration fixture root | Step522-Step529 docs and fixture README | standalone fixture validator target | artifact body generation integration fixture validation | none | Step525 validates 28-case / 196-JSON metadata-only fixture root; Step527 adds standalone Makefile target; Step529 adds wrapper check before artifact body fixture validation | yes |
| Artifact body generation runtime integration plan-only bridge | `frozen_policy_generation_artifact_body_generation_runtime_integration.py` | runtime integration focused tests | existing integration fixture root selected case | Step532-Step539 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration` | artifact body generation runtime integration plan-only bridge smoke | none | Step535 selected-case public-safe `plan-only-bridge` CLI over `valid/valid_minimal_suppressed_metadata_only_bridge`; Step537 standalone target available; Step539 wrapper label added after static integration fixture validation; no artifact body runtime invocation, no manifest writer, and no file writing | yes |
| Artifact body generation runtime integration safe-metadata handoff | `frozen_policy_generation_artifact_body_generation_runtime_integration.py` and `frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py` | runtime integration focused tests plus focused planned-root validator tests | planned safe-metadata v0.2 fixture root | Step544-Step563 docs and planned fixture README | planned-root validator target plus `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime` | safe-metadata v0.2 fixture validation plus safe-metadata runtime smoke | safe-metadata fixture validator remote marker only | Step559 implements `safe-metadata-smoke` as metadata handoff only with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`; Step561 adds a standalone runtime Makefile target; Step563 adds the runtime smoke to the wrapper after fixture validation and before artifact body fixture validation; no artifact body runtime invocation, no manifest writer, and no file writing | yes |
| Artifact body generation runtime invocation fixture root | `frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py` | focused validator tests | Step570 planned runtime invocation fixture root | Step569-Step581 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures` | artifact body generation runtime invocation fixture validation | none | Step581 adds the Step574 target to the release-quality wrapper after safe-metadata runtime smoke and before planned-only v0.3 runtime smoke; it validates 30 metadata-only / body-free cases and 210 JSON files with public-safe CLI output and does not invoke artifact body generation runtime, manifest writer, or file writing | yes |
| Artifact body generation runtime invocation planned-only mode | `frozen_policy_generation_artifact_body_generation_runtime_integration.py` | runtime integration focused tests | Step570 primary valid case | Step575-Step581 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation` | artifact body generation runtime invocation planned-only v0.3 smoke | none | Step581 adds the Step579 planned-only v0.3 smoke to the release-quality wrapper immediately after fixture validation; runtime invocation remains planned but not invoked, with no manifest writer invocation and no file writing | yes |
| Actual-controlled v0.4 artifact body payload audit without payload emission | `frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py` | focused payload audit tests | Step587 actual-controlled fixture root | Step635-Step638 docs and fixture README | none | none | none | Step638 adds a standalone direct CLI-only metadata-only / body-free / count-only runner over the 36-case actual-controlled root; it is not Makefile-targeted or release-quality integrated, emits no payload body, invokes no manifest writer, and writes no files | yes |
| Artifact body | artifact body modules/validators | artifact body tests | artifact body fixture roots | artifact body docs | artifact body targets | artifact body labels | artifact body markers | body-suppressed checks | yes |
| Manifest writer | manifest writer modules/validators | manifest writer tests | manifest writer fixture roots | manifest writer docs | manifest writer targets | manifest writer labels | manifest writer markers | metadata-only writer/file-writing checks | yes |
| Release Quality | wrapper script/workflow | wrapper execution | not applicable | release-quality docs | `check-release-quality` | all wrapper labels | status markers | implemented wrapper | yes |

## 18. Uncertainty And Follow-Up

Items for the full specification step:

- Exact CLI argument tables for every Python module should be generated from
  each parser or help output; this inventory confirms parser presence but does
  not reproduce every argument.
- Exact Makefile command bodies should be copied from `Makefile` into the full
  specification in a body-free way; this inventory groups targets and status.
- Exact fixture case counts should be recomputed from fixture roots or copied
  from fixture README/validator summaries where safe.
- Exact schema-name catalogue should separate stable schema versions from
  synthetic invalid-case marker identifiers.
- Rust crate API details should be summarized from each crate README and
  source module; this inventory identifies crate boundaries.
- Logger-web event type and UI details should be summarized from TypeScript
  source without copying raw event payload examples.
- Any component not explicitly listed here should be treated as `not yet
  confirmed from repository scan` until the full specification step verifies
  it.

## Step587 Source Inventory Addendum

Step587 adds the fixture root `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/README.md` and 252 parseable metadata-only JSON fixture files under the same root. The root follows the Step586 contract with 6 valid cases, 30 invalid cases, and the 7-file layout. No Python source, Makefile, workflow, release-quality wrapper, runtime implementation, validator implementation, manifest writer implementation, or existing fixture JSON outside the new root is added or changed.


## Step589 Source Inventory Addendum

Step589 adds `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py` and `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`. The validator is standalone only and targets the Step587 fixture root with public-safe aggregate output. No Makefile, workflow, release-quality wrapper, fixture JSON, runtime implementation, artifact body generation implementation, or manifest writer implementation is added or changed.

## Step591 Source Inventory Addendum

Step591 adds the Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures` for the Step589 validator CLI. It also updates README/docs status references. No release-quality wrapper, workflow, Python code/tests, fixture JSON, runtime implementation, artifact body generation implementation, or manifest writer implementation is added or changed.

## Step593 Source Inventory Addendum

Step593 updates `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py` and `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration.py` for the v0.4 actual-controlled runtime CLI boundary. README/docs references are updated. No Makefile, release-quality wrapper, workflow, fixture JSON, validator implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step595 Source Inventory Addendum

Step595 updates `Makefile` with the standalone target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`. README/docs references are updated. No release-quality wrapper, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, or manifest writer implementation is added or changed.

## Step597 Source Inventory Addendum

Step597 updates `scripts/check_release_quality.sh` to run the Step591 actual-controlled fixture validator target and the Step595 v0.4 runtime smoke target in adjacent order after the planned-only v0.3 runtime invocation smoke. README/docs references are updated. No Makefile, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, or manifest writer implementation is added or changed.

Step604 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py` and `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`. README/docs references are updated. No Makefile, release-quality wrapper, workflow, fixture JSON, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step606 Source Inventory Addendum

Step606 updates `Makefile` with the standalone target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`. README/docs references are updated. No release-quality wrapper, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step608 Source Inventory Addendum

Step608 updates `scripts/check_release_quality.sh` to run the Step606 standalone multi-case target after the actual-controlled v0.4 single-case smoke and before artifact body fixture / CLI checks. README/docs references are updated. No Makefile, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step615 Source Inventory Addendum

Step615 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py` and `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`. README/docs references are updated. No Makefile, release-quality wrapper, workflow, fixture JSON, validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step617 Source Inventory Addendum

Step617 updates `Makefile` with the standalone target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`. README/docs references are updated. No release-quality wrapper, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step619 Source Inventory Addendum

Step619 updates `scripts/check_release_quality.sh` to run the Step617 standalone invalid-case target after the all-valid multi-case runtime smoke and before artifact body fixture / CLI checks. README/docs references are updated. No Makefile, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step626 Source Inventory Addendum

Step626 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py` and `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py`. README/docs references are updated. No Makefile, release-quality wrapper, workflow, fixture JSON, existing runtime implementation, existing validator implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step628 Source Inventory Addendum

Step628 updates `Makefile` with the standalone target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke`. README/docs references are updated. No release-quality wrapper, workflow, Python code/tests, fixture JSON, existing runtime implementation, existing validator implementation, payload audit implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step630 Source Inventory Addendum

Step630 updates `scripts/check_release_quality.sh` to run the Step628 standalone deferred invalid-case usage_error / mismatch target after the invalid fail_closed smoke and before artifact body fixture / CLI checks. README/docs references are updated. No Makefile, workflow, Python code/tests, fixture JSON, existing runtime implementation, existing validator implementation, payload audit implementation, artifact body generation implementation, manifest writer implementation, artifact body file writing, or manifest file writing is added or changed.

## Step638 Source Inventory Addendum

Step638 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py` and `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py`. README/docs/full technical specification references are updated in Step638b. No Makefile, release-quality wrapper, workflow, fixture JSON, existing runtime implementation, existing validator implementation, payload body emission, artifact body payload output, generated policy body output, manifest body output, manifest writer integration, artifact body file writing, or manifest file writing is added or changed.
