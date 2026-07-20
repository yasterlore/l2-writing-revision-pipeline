# Full Technical Specification Draft

This document is a full technical specification draft for the
L2 writing revision pipeline repository. It is based on
[Full Technical Specification Source Inventory And Coverage Audit](full_technical_specification_source_inventory.md),
created in Step-pretec-doc1.

This draft is docs-only. It does not change implementation code, fixture JSON,
Makefile targets, scripts, workflows, package files, tests, or release-quality
behavior. It is a consolidated technical description based on repository
evidence, not a claim that every possible technical detail is covered.

This draft does not prove production readiness, real-data readiness, model
performance, F1, accuracy, ECE, AURCC, privacy/legal/IRB readiness, generated
policy quality, learner-state estimator correctness, or runtime integration
correctness. Items not confirmed from the repository scan are explicitly
marked `not yet confirmed from repository scan` or `to be verified in a later
step`.

Step-pretec-doc3 adds a separate
[coverage validation report](full_technical_specification_coverage_validation.md)
that compares this draft with the source inventory. Step-pretec-doc4 fixed the
recorded medium-priority gaps, and Step-pretec-doc5 reduced low-priority gaps
at external-review summary level. This draft should still not be treated as an
absolute guarantee of no omissions.

Step-pretec-doc6 adds a
[final safety and non-proof review](full_technical_specification_final_safety_review.md)
for this documentation set. That review supports external review readiness with
caveats; it is not external review completion, production readiness,
real-data readiness, or model-performance evidence.

## 1. Document Position

This document is the Step-pretec-doc2 full technical specification draft. It
uses the Step-pretec-doc1 inventory as its primary coverage guide.

The document describes:

- repository architecture
- language/runtime surfaces
- data and schema families
- CLI, Makefile, script, workflow, fixture, validator, and status-marker
  surfaces
- synthetic-only, metadata-only, body-free, and no-oracle boundaries
- implementation status and known non-proofs

The document does not:

- implement new behavior
- add or modify fixtures
- modify CI, Makefile, wrapper, package files, or runtime code
- copy raw logs, full job output, fixture JSON bodies, request bodies, pointer
  bodies, expected bodies, written file bodies, manifest bodies, artifact body
  payloads, generated policy bodies, raw rows, logits/probabilities, private
  path values, absolute local path values, or raw learner text
- claim production readiness, real-data readiness, or model-performance
  evidence

## 2. Software Purpose

The repository implements research software for an L2 English writing revision
process pipeline. The pipeline starts from keystroke-level logging and moves
through validation, replay, revision-event extraction, micro-episode
construction, candidate generation, OT-inspired scoring, and learner-state
validation infrastructure.

The current repository posture is synthetic-only. The public fixtures,
validators, CLIs, release-quality checks, and status markers are designed to
exercise metadata and public-safe summaries without using real participant
data.

The software supports infrastructure for:

- keystroke-level event schemas and validation
- synthetic safe views
- text replay and revision-event extraction
- micro-episode construction
- candidate generation and scoring over synthetic examples
- learner-state sequence audit and exporter checks
- estimator input validation
- selective prediction validation
- frozen policy validation and generation validation
- frozen policy generation scaffold and generator scaffold boundaries
- artifact writer, artifact body, and manifest writer metadata-only checks
- release-quality orchestration and public-safe remote status markers

Real participant data readiness is not proven. Production use, deployment,
institutional review, privacy/legal approval, and model performance validation
are outside the current demonstrated scope.

## 3. Overall Architecture

The repository is organized into cooperating runtime, validation, fixture, and
documentation layers.

| Layer | Main paths | Role |
| --- | --- | --- |
| Browser logger | `apps/logger-web/` | TypeScript/Vite synthetic raw event logger surface and tests. |
| Rust processing crates | `crates/` | Raw event schema, validation, replay, revision extraction, micro episodes, no-oracle audit, and CLI wrapper. |
| Python research pipeline | `python/` | Candidate generation, evaluation, OT-inspired scoring, learner-state validators/exporters, and frozen policy generation infrastructure. |
| Shell orchestration | `scripts/` | Synthetic E2E summaries, release-quality wrapper, summary manifest checks, config/scoring smoke checks, and synthetic policy checks. |
| Makefile | `Makefile` | Thin sequential entrypoints over scripts, Python CLIs, Rust checks, logger checks, and release-quality. |
| Fixtures | `tests/fixtures/` | Synthetic raw event, scoring, learner-state, frozen policy, artifact, body, and manifest fixtures. |
| Documentation | `docs/` | Architecture, policy, design, fixture contracts, validator designs, release-quality plans, status workflows, recaps, and checklist docs. |
| Status markers | `docs/status/` | Public-safe pass-only/count-only remote/manual run records and milestone status records. |
| Workflows | `.github/workflows/` | GitHub Actions CI and manual Release Quality workflow. |

### Data Flow Overview

The technical flow is:

1. A synthetic browser logger or synthetic raw event fixture represents
   keystroke-level events.
2. Rust schema and validation checks ensure raw event structure is acceptable.
3. Replay reconstructs event-derived state while suppressing content in public
   outputs.
4. Revision extraction identifies revision-like actions.
5. Micro-episode construction groups revision context into synthetic training
   units.
6. Candidate generation and feature extraction produce candidate/action
   representations from safe synthetic inputs.
7. OT-inspired constraints and scoring generate synthetic candidate scores and
   diagnostics.
8. Synthetic E2E scripts create summary CSV/manifest outputs.
9. Learner-state audit and exporter infrastructure validates sequence
   separation and no-oracle constraints.
10. Estimator input, selective prediction, frozen policy, and frozen policy
    generation validators check metadata-only fixture contracts.
11. Frozen policy generation scaffold, generator scaffold, artifact writer,
    artifact body, and manifest writer components validate or smoke-test
    metadata-only runtime boundaries.
12. Release Quality runs an ordered wrapper over these checks and records only
    safe high-level status in docs/status markers when requested.

### Safety Boundaries

The architecture is built around these boundaries:

- synthetic-only public fixtures and checks
- metadata-only artifact and manifest summaries
- body-free public output
- no raw rows or raw learner text in public docs
- no logits/probability dumps in public docs
- no private path values or absolute local path values
- no final corrected text, observed-after text, or gold label fields
- no post-hoc annotation, test-set tuning, or scoring feedback payload leakage
- opt-in file writing with safe-root and cleanup/residue checks where
  applicable

## 4. Execution Environment, Languages, And Runtimes

| Runtime | Used in | Purpose | Main files | Validation method | Notes |
| --- | --- | --- | --- | --- | --- |
| Python | `python/` | Pipeline modules, validators, CLIs, tests | `python/candidate_generation/`, `python/evaluation/`, `python/ot_scorer/`, `python/learner_state/`, `python/test_support/` | `PYTHONPATH=python python3 -m unittest discover -s python`, `compileall`, Makefile targets | Uses synthetic fixtures and safe summaries. |
| Rust | `crates/` | Event schema, validation, replay, extraction, micro episodes, no-oracle audit, CLI | root `Cargo.toml`, crate `Cargo.toml` files | `cargo fmt`, `cargo test`, `cargo clippy` | Workspace edition is Rust 2021. |
| TypeScript | `apps/logger-web/src/`, tests | Browser logger and raw event tests | `apps/logger-web/src/main.ts`, `src/rawEvent.ts`, tests | `npm run typecheck`, `npm test`, `npm run build` | Built with Vite. |
| JavaScript/Node/npm | `apps/logger-web/` | Package runtime and scripts | `package.json`, `package-lock.json` | npm scripts and GitHub Actions setup-node | `npm run dev` is local only; release-quality uses typecheck/test/build. |
| Shell | `scripts/` | Wrapper and smoke checks | `scripts/check_release_quality.sh`, synthetic E2E and config scripts | shell syntax checks and Makefile wrapper | Major checks should be run sequentially. |
| Makefile | root `Makefile` | Thin task orchestration | `Makefile` | `make` targets | `.NOTPARALLEL` is present. |
| GitHub Actions YAML | `.github/workflows/` | CI and manual release-quality | `ci.yml`, `release-quality.yml` | Ruby YAML parse, remote workflow execution | Raw logs are not specification content. |
| Markdown | root/docs/crate/fixture READMEs | Specs, policies, designs, recaps, status | `README.md`, `SECURITY.md`, `docs/` | docs review and link/navigation checks | Documentation must remain public-safe. |
| JSON/JSONL/CSV | fixtures and synthetic outputs | Synthetic raw events, expected actions, candidate scores, manifests, summaries, validators | `tests/fixtures/`, `docs/schemas/summary_manifest_schema_v1.json` | validators, scripts, schema checks | Body examples are not included in this spec. |
| HTML/CSS/Vite | logger-web app | Browser UI shell and styling | `index.html`, `src/styles.css`, `vite.config.ts` | npm build | Browser app remains synthetic-only. |

## 5. Directory Structure

| Path | Description |
| --- | --- |
| `apps/logger-web/` | Synthetic-only TypeScript/Vite web logger app, tests, npm package files, and build config. |
| `crates/` | Rust workspace crates for raw event schema, validation, replay, extraction, micro episodes, no-oracle audit, and CLI. |
| `python/` | Python modules for candidate generation, evaluation, OT-inspired scoring, learner-state validation/export, frozen policy generation, and safe output support. |
| `scripts/` | Shell scripts for release-quality, synthetic E2E summaries, summary manifest checks, config/scoring smoke checks, and synthetic policy. |
| `tests/fixtures/` | Synthetic fixture roots for raw events, scoring, learner-state, frozen policy, scaffold, artifact, body, and manifest flows. |
| `docs/` | Architecture, policy, design, fixture contract, validator, Makefile target, release-quality, workflow, recap, and checklist docs. |
| `docs/status/` | Public-safe status markers and status index. |
| `.github/workflows/` | CI and manual Release Quality workflow definitions. |
| Root files | `README.md`, `SECURITY.md`, `LICENSE`, `Cargo.toml`, `Cargo.lock`, `Makefile`, `.gitignore` | Project entrypoints, policy, license placeholder, workspace/package config, and task orchestration. |

Generated/dependency outputs such as `target/`, `tmp/`, `node_modules/`,
`dist/`, `dist-test/`, and Python bytecode caches are operational artifacts,
not primary source specification inputs.

## 6. Data Models And Processing Flow

### Raw Events And Safe Views

Raw events are represented by the logger web app and Rust schema crate. The
raw event schema and safe view boundaries are documented in
`docs/04_raw_event_schema.md`, implemented in `crates/kslog_schema/`, and
connected to TypeScript definitions in `apps/logger-web/src/rawEvent.ts`.

Safe views are intended to suppress content that would violate no-oracle or
public-safety rules. They are validated in Rust and exercised by synthetic
fixtures under `tests/fixtures/synthetic/`.

### Replay, Validation, Extraction, And Micro Episodes

Rust crates provide:

- schema validation: `crates/kslog_validate/`
- replay: `crates/kslog_replay/`
- revision event extraction: `crates/kslog_extract/`
- micro-episode construction: `crates/kslog_micro_episode/`
- no-oracle audit: `crates/kslog_no_oracle_audit/`
- command wrapper: `crates/kslog_cli/`

These components are tested by Rust unit tests and CI/release-quality Rust
checks. Public summaries must suppress raw learner text and content-bearing
payloads.

### Candidate Generation, Feature Extraction, And Scoring

Python packages provide:

- candidate generation: `python/candidate_generation/`
- evaluation: `python/evaluation/`
- OT-inspired scoring and diagnostics: `python/ot_scorer/`

The OT-inspired scoring flow includes constraint building, feature loading,
violation loading, score calculation, hand weight config validation, diagnostic
summaries, fixture locks, and config ranking diff checks.

### Synthetic E2E Summary And Manifest

Shell scripts under `scripts/` run synthetic E2E summaries and manifest checks:

- `scripts/run_synthetic_e2e_summary.sh`
- `scripts/run_synthetic_e2e_pipeline.sh`
- `scripts/run_synthetic_e2e_config_summary.sh`
- `scripts/check_summary_manifest_schema_sync.sh`
- `scripts/check_synthetic_diagnostic_distribution.sh`
- `scripts/lib/summary_manifest_schema.sh`

These scripts use synthetic fixtures, produce safe summaries, and are covered
by Makefile targets and release-quality ordering.

### Learner-State Chain

The learner-state chain includes:

- sequence audit: `python/learner_state/sequence_audit.py`
- sequence exporter: `python/learner_state/sequence_exporter.py`
- estimator input validation: `python/learner_state/estimator_input.py`
- selective prediction validation:
  `python/learner_state/selective_prediction_validation.py`
- frozen policy validation:
  `python/learner_state/frozen_policy_validation.py`
- frozen policy generation validation:
  `python/learner_state/frozen_policy_generation_validation.py`

This chain validates synthetic fixtures and metadata-only summaries. It does
not prove learner-state estimator correctness or metric achievement.

### Frozen Policy Generation Scaffold And Generator Scaffold

The scaffold runtime is implemented in
`python/learner_state/frozen_policy_generation.py`. The generator scaffold is
implemented in
`python/learner_state/frozen_policy_generation_generator_scaffold.py`.

Both are metadata-only boundaries. The generator scaffold returns safe
metadata summaries and does not prove generated policy quality.

### Artifact Writer And Artifact Writer CLI Integration Fixture Validation

The artifact writer runtime and fixtures are implemented around:

- `python/learner_state/frozen_policy_generation_artifact_writer.py`
- `python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`
- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`
- `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`
- `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/`

Artifact writer CLI integration fixture validation is included in
release-quality. Artifact writer CLI integration runtime is not implemented.
Runtime fixture validation exists as a standalone static target:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`
- `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

### Artifact Body Generation And File Writing

Artifact body generation is implemented in
`python/learner_state/frozen_policy_generation_artifact_body.py` with
suppressed and safe-metadata smoke modes. Artifact body fixture, file-writing,
and isolated-write validation are handled by dedicated fixture roots and
validators.

Artifact body generation CLI integration as a broader chained runtime flow is
not implemented.

### Manifest Writer And File Writing

The manifest writer is implemented in
`python/learner_state/frozen_policy_generation_manifest_writer.py` and
validated through fixture, runtime fixture, file-writing fixture,
isolated-write, production file-writing fixture, runtime smoke, and runtime
file-writing smoke targets.

Manifest writer runtime file writing is metadata-only, opt-in, and checked for
safe output paths, parseability, content policy, and residue cleanup.

Manifest writer integration beyond the current writer runtime is not
implemented. Manifest body generation is not implemented.

## 7. Schema And Data Format Reference

This section lists schema families and representative version names. It does
not include JSON body examples.

| Family | Representative schema/version names | Evidence | Role | Safety restrictions |
| --- | --- | --- | --- | --- |
| Raw event | `kslog.raw_event.v1`, raw event schema docs | `crates/kslog_schema/`, `docs/04_raw_event_schema.md` | Browser/Rust event validation | No no-oracle forbidden fields in public safe views. |
| Safe view | safe synthetic views | `tests/fixtures/synthetic/safe_views/`, Rust tests | Content-suppressed event-derived views | No after-observed context in public output. |
| Summary manifest | `summary_manifest_schema_v1`, manifest schema version `1.0` | `docs/schemas/summary_manifest_schema_v1.json`, `scripts/lib/summary_manifest_schema.sh` | Synthetic summary manifest contract | Unknown keys and forbidden content are checked by scripts. |
| Candidate/evaluation/scoring | `candidate_feature_schema_v0_3`, `evaluation_report_schema_v0_1`, `diagnostic_summary_schema_v0_1`, `hand_weight_config_schema_v0_1` | `python/ot_scorer/`, scoring docs | Candidate features, diagnostics, configs, reports | No performance claim from smoke outputs. |
| Learner-state sequence | sequence audit result and manifest schema names | `python/learner_state/sequence_audit.py`, fixtures | Audit/exporter validation | No future leakage, raw rows, or label leakage. |
| Estimator input | `learner_state_estimator_input_validation_v0.1` | `python/learner_state/estimator_input.py` | Input fixture validation | No estimator correctness claim. |
| Selective prediction | `learner_state_selective_prediction_validation_v0.1` | `python/learner_state/selective_prediction_validation.py` | Calibration fixture validation | No metric achievement claim. |
| Frozen policy | `frozen_selective_prediction_policy_schema_v0_1`, `learner_state_frozen_policy_validation_v0.1` | frozen policy module/docs/fixtures | Frozen policy fixture validation | No test tuning or performance body. |
| Frozen policy generation | `frozen_policy_generation_request_schema_v0_1`, `frozen_policy_generation_input_pointer_schema_v0_1`, `learner_state_frozen_policy_generation_validation_v0.1` | generation modules/docs/fixtures | Generation fixture validation | No generated policy body leakage. |
| Scaffold runtime | `frozen_policy_generation_scaffold_runtime_schema_v0_1` | scaffold runtime module/docs | Metadata-only runtime scaffold | No artifact body or generated artifact writing. |
| Generator scaffold | `frozen_policy_generation_generator_scaffold_result_v0.1`, fixture validation schema | generator scaffold module/docs | Metadata-only generator scaffold | No generated policy body payload. |
| Artifact writer | artifact writer request/pointer/result/expected schema names | artifact writer module/docs/fixtures | Metadata-only artifact writer result | Body and manifest body suppressed. |
| Artifact writer CLI integration fixture | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_result_v0.1` | CLI integration validator/docs/fixtures | Static fixture validation | No artifact body or manifest integration execution. |
| Artifact writer CLI actual invocation fixture | `learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_*_v0.1` metadata schema family; `learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1` | Step498 fixture root and README; Step500 validator module/tests | Static fixture validation | Metadata-only sentinels; no payload bodies or actual invocation correctness claim. |
| Artifact writer CLI integration runtime fixture | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`, runtime v0.1 plan-only metadata schema names, and Step509 v0.2 actual-invocation fixture schema family names | runtime fixture validator/docs/fixtures/tests | Static runtime fixture validation plus Step513 explicit runtime mode support | Static fixture root includes 54 cases / 324 JSON files; Step511 validator v0.2 support accepts v0.1 and v0.2 fixture schemas, and Step513 adds explicit `actual_invocation_metadata_only` runtime summary support without file writing or downstream generation integration. |
| Artifact body | artifact body expected/result/generation schema names | artifact body modules/docs/fixtures | Suppressed and safe-metadata body generation | No body payload in public summaries. |
| Manifest writer | manifest writer request/result/runtime/file-writing/isolated/production schema names | manifest writer modules/docs/fixtures | Metadata-only manifest writer and file-writing checks | No manifest body; safe-root file writing only. |
| Status markers | public-safe run status docs | `docs/status/` | Remote/manual pass-only/count-only traceability | No raw logs or full job output. |

Synthetic invalid-case marker identifiers also appear in fixtures and docs.
They should be separated from stable schema names in future coverage
validation.

## 8. CLI Specification

| CLI | Implementation | Purpose | Input | Output | File writing | Makefile/release-quality relation | Proof boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cargo run -p kslog_cli -- validate ...` | `crates/kslog_cli/` | Validate synthetic raw event fixtures | synthetic JSONL fixture path | status/safe diagnostics | no for validation | CI uses it; Rust checks in release-quality | Validates selected synthetic fixture paths only. |
| `python -m candidate_generation.generate` | `python/candidate_generation/generate.py` | Candidate generation | synthetic input paths | candidate outputs/summaries | not yet confirmed from repository scan | not directly in wrapper | Does not prove model performance. |
| `python -m evaluation.evaluate` | `python/evaluation/evaluate.py` | Synthetic evaluation reports | candidate/expected fixtures | report summary | not yet confirmed from repository scan | not directly in wrapper | Does not prove real-world accuracy. |
| `python -m evaluation.expected_action_registry` | `python/evaluation/expected_action_registry.py` | Expected-action registry checks | synthetic registry data | safe registry status | no confirmed write behavior | not directly in wrapper | Registry validation only. |
| `python -m ot_scorer.features` | `python/ot_scorer/features.py` | Feature CLI | synthetic inputs | feature summary/output | not yet confirmed from repository scan | used through scripts/tests | Feature generation only. |
| `python -m ot_scorer.constraints` | `python/ot_scorer/constraints.py` | Constraint CLI | synthetic features/config | constraint summary/output | not yet confirmed from repository scan | used through scripts/tests | Constraint generation only. |
| `python -m ot_scorer.score` | `python/ot_scorer/score.py` | Score candidates | synthetic candidates/violations/config | candidate score outputs | writes caller-controlled synthetic outputs in smoke scripts | config/scoring smoke checks | No performance evaluation. |
| `python -m ot_scorer.summarize_diagnostics` | `python/ot_scorer/summarize_diagnostics.py` | Summarize diagnostics | synthetic diagnostic inputs | count/status summary | not yet confirmed from repository scan | summary scripts | Count-only diagnostics. |
| `python -m ot_scorer.validate_weight_config` | `python/ot_scorer/validate_weight_config.py` | Validate hand weight configs | synthetic config files | validation status | no | `check-fixtures` scripts | Config validation only. |
| `python -m ot_scorer.score_fixture_lock` | `python/ot_scorer/score_fixture_lock.py` | Compare generated and expected scores | synthetic score fixtures | mismatch summary | no | `check-fixtures` scripts | Fixture lock only. |
| `python -m ot_scorer.config_ranking_diff` | `python/ot_scorer/config_ranking_diff.py` | Compare config scoring behavior | synthetic config/score outputs | diff summary | writes synthetic tmp outputs through script | config/scoring smoke | No model metric proof. |
| `python -m learner_state.sequence_audit` | `sequence_audit.py` | Audit sequence fixtures | fixture root/case/dataset metadata | safe audit summary | no by default | Makefile and release-quality | No-oracle fixture audit. |
| `python -m learner_state.sequence_exporter` | `sequence_exporter.py` | Export synthetic learner-state sequence files | synthetic input fixture, output dir | safe summary and separated outputs | yes to caller output dir | Makefile and release-quality | Synthetic export smoke only. |
| `python -m learner_state.estimator_input` | `estimator_input.py` | Validate estimator input fixtures | fixture root/case | safe summary | no | Makefile and release-quality | No estimator model proof. |
| `python -m learner_state.selective_prediction_validation` | `selective_prediction_validation.py` | Validate selective prediction fixtures | fixture root/case | safe summary | no | Makefile and release-quality | No ECE/AURCC achievement. |
| `python -m learner_state.frozen_policy_validation` | `frozen_policy_validation.py` | Validate frozen policy fixtures | fixture root/case | safe summary | no | Makefile and release-quality | Policy fixture validation only. |
| `python -m learner_state.frozen_policy_generation_validation` | `frozen_policy_generation_validation.py` | Validate frozen policy generation fixtures | fixture root/case | safe summary | no | Makefile and release-quality | No generated policy quality proof. |
| `python -m learner_state.frozen_policy_generation` | `frozen_policy_generation.py` | Metadata-only scaffold runtime smoke | request/pointer metadata | safe runtime summary | no artifact writing | Makefile and release-quality | Runtime scaffold only. |
| `python -m learner_state.frozen_policy_generation_generator_scaffold` | generator scaffold module | Metadata-only generator scaffold | request/pointer metadata | safe summary | no body writing | Makefile and release-quality | No generated policy body. |
| `python -m learner_state.frozen_policy_generation_artifact_writer` | artifact writer module | Metadata-only artifact writer smoke | request/pointer metadata | safe summary | no body writing | Makefile and release-quality | No CLI integration runtime proof. |
| `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | CLI integration fixture validator | Static CLI integration fixture validation | fixture root/case | count-only summary | no | Makefile and release-quality | Fixture contract only. |
| `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | runtime fixture validator | Static future runtime fixture validation | fixture root/case | count-only summary | no | standalone Makefile target; not wrapper-integrated as of scan | No runtime execution. |
| `python -m learner_state.frozen_policy_generation_artifact_body` | artifact body module | Suppressed or safe-metadata body generation smoke | metadata-only request/pointer | safe summary | optional safe output in dedicated smoke path | Makefile and release-quality for current smoke checks | No payload disclosure. |
| Manifest writer CLIs | manifest writer module and validators | Runtime/fixture/file-writing validation | metadata-only request/pointers/fixture roots | safe summaries | opt-in safe path for writer runtime file smoke | Makefile and release-quality | Metadata-only manifest checks. |
| Shell scripts | `scripts/*.sh` | Summary, release-quality, policy, config/scoring checks | synthetic fixtures/config | safe status/count summaries | controlled tmp outputs | Makefile and wrapper | Smoke/check evidence only. |
| npm scripts | `apps/logger-web/package.json` | logger typecheck/test/build/dev | TypeScript app source | build/test status | build outputs generated files | release-quality uses typecheck/test/build | App build/test evidence only. |

## 9. Makefile Target Specification

`Makefile` provides sequential task entrypoints. It is `.NOTPARALLEL`.

| Group | Targets | Command family | Purpose | Safe output | Release-quality inclusion | Non-proof |
| --- | --- | --- | --- | --- | --- | --- |
| General/release | `help`, `check-release-quality`, `check-all` | wrapper or help text | Run or describe project checks | status/count lines | release-quality target is wrapper entrypoint | Not a production gate. |
| Summary-flow | `check-summary`, `check-manifest-sync`, `check-diagnostic-distribution`, `check-summary-flow`, `check-config-smoke` | synthetic summary and manifest scripts | Generate/check synthetic summaries | count/status summaries | summary and config scripts are in wrapper | No performance evidence. |
| Python | `check-python` | unittest discover and compileall | Run Python tests and compile modules | test/compile status | wrapper runs equivalent commands | Unit tests only. |
| Rust | `check-rust` | cargo fmt/test/clippy | Rust formatting/tests/lints | check status | wrapper includes Rust checks | Rust synthetic tests only. |
| Logger | `check-logger` | npm typecheck/test/build | TypeScript logger checks | build/test status | wrapper includes logger checks | Not browser deployment proof. |
| Policy | `check-policy` | synthetic policy script | Check tracked synthetic policy | policy status | wrapper includes synthetic policy | Not legal/privacy approval. |
| Fixtures/scoring | `check-fixtures` | scoring fixture lock, hand weight validation, ranking diff | Validate synthetic scoring/config fixtures | count/status summary | related scripts in wrapper | No model metric achievement. |
| Learner-state | audit/exporter/estimator/selective targets | Python learner_state CLIs | Validate/export synthetic learner-state fixtures | safe summaries | included | No estimator correctness. |
| Frozen policy | frozen policy and frozen policy generation targets | Python validators | Validate policy/generation fixtures | safe summaries | included | No generated quality proof. |
| Scaffold/generator | scaffold/generator fixture and runtime targets | Python validators/runtimes | Validate and smoke-test metadata-only scaffold/generator | safe summaries | included | No artifact body generation. |
| Artifact writer | writer fixture/runtime/CLI integration fixture/runtime fixture targets | Python validators/runtimes | Validate writer contracts and smoke metadata-only writer | safe summaries | first three included; runtime fixture target standalone | Runtime integration not proven. |
| Artifact body | body fixture/generation/safe-metadata/file-writing/isolated targets | Python validators/runtimes | Validate body-suppressed and file-writing boundaries | safe summaries | most target families included as wrapper labels | No artifact payload public output. |
| Manifest writer | manifest writer fixture/runtime/file-writing/isolated/production/runtime-file-writing targets | Python validators/runtimes | Validate manifest writer metadata-only and safe write boundaries | safe summaries | included | No manifest body generation. |

Each target's exact command should be treated as the Makefile source of truth.
Command output should not be copied into docs.

## 10. GitHub Actions / CI Specification

### CI Workflow

Workflow file: `.github/workflows/ci.yml`

- workflow name: `CI`
- job: `rust` / `Rust workspace`
- setup: checkout and stable Rust with rustfmt/clippy
- commands: Rust formatting, tests, clippy, synthetic policy, selected Rust
  CLI validation and synthetic E2E checks
- evidence scope: Rust workspace and selected synthetic pipeline checks
- does not prove: production readiness, real-data readiness, model
  performance, privacy/legal readiness

### Release Quality Workflow

Workflow file: `.github/workflows/release-quality.yml`

- workflow name: `Release Quality`
- job: `release-quality` / `Release quality`
- setup: checkout, Python 3.11, stable Rust with rustfmt/clippy, Node 22,
  npm cache and install for logger-web
- command: `scripts/check_release_quality.sh`
- evidence scope: manual wrapper execution in GitHub Actions
- raw logs: raw workflow logs and full job output are not specification
  content and should not be copied into docs
- does not prove: production readiness, real-data readiness, metric
  achievement, or integrations not included in the wrapper

## 11. Fixtures Specification

All fixture roots are synthetic-only unless a future scan proves otherwise.
Fixture bodies are not reproduced in this document.

| Fixture category | Roots | Purpose | Validator/target | Confirmed counts |
| --- | --- | --- | --- | --- |
| Synthetic raw/scoring fixtures | `tests/fixtures/synthetic/` subroots | Raw events, expected actions, candidate scores/features/sets, violations, hand weight configs, safe views | Rust/Python scripts, scoring checks | not fully enumerated in this draft |
| Learner-state fixtures | sequence audit/exporter/estimator/selective roots | Audit/export/input/selective validation | learner_state modules | counts vary by validator; see status/check output |
| Frozen policy fixtures | frozen selective policy and generation roots | Frozen policy and generation validation | frozen policy validators | counts vary by validator |
| Scaffold fixtures | scaffold and generator scaffold roots | Fixture and runtime compatibility | scaffold/generator validators | scaffold and generator counts documented by validators/status |
| Artifact writer fixtures | artifact writer root | Metadata-only artifact writer contract | artifact writer fixture validator | 17 cases confirmed by release-quality status/check output |
| Artifact writer CLI integration fixtures | CLI integration root | Static generator-to-artifact-writer fixture contract | CLI integration validator | 28 cases / 168 JSON files confirmed |
| Artifact writer CLI integration runtime fixtures | runtime fixture root | Static future runtime fixture contract | runtime fixture validator v0.2 support implemented in Step511 | 54 cases / 324 JSON files; original 30 v0.1 plan-only cases preserved and 24 v0.2 actual-invocation metadata-only cases accepted |
| Artifact writer CLI actual invocation fixtures | actual invocation fixture root | Future metadata-only actual invocation fixture contract | Step500 static validator implemented | 32 cases / 192 JSON files confirmed by validator CLI smoke |
| Artifact body fixtures | artifact body roots | Body-suppressed body generation and file-writing boundaries | artifact body validators | artifact body fixture count 18; file-writing 29; isolated-write 22 from release-quality status/check output |
| Manifest writer fixtures | manifest writer roots | Manifest writer fixture/runtime/file-writing/isolated/production boundaries | manifest writer validators | counts include 30, 31, 39, 25, 32 from release-quality status/check output |

Fixture policy:

- use synthetic IDs and metadata
- use controlled invalid markers for fail-closed cases
- do not use real participant data
- do not include public body payload examples in docs
- keep no-oracle and suppression flags visible in metadata
- keep file-writing cases safe-root/opt-in where applicable

## 12. Validators Specification

Validators are Python modules that statically validate fixture roots or run
metadata-only smoke behavior. Their public summaries should be body-free.

| Validator | CLI | Fixtures | Tests | Schema/mode | Makefile | Release-quality |
| --- | --- | --- | --- | --- | --- | --- |
| `learner_state.sequence_audit` | yes | sequence audit root | sequence audit tests | sequence audit result/manifest | audit fixture target | included |
| `learner_state.sequence_exporter` | yes | exporter root | exporter tests | sequence export metadata | exporter CLI target | included |
| `learner_state.estimator_input` | yes | estimator input root | estimator input tests | estimator input validation | estimator target | included |
| `learner_state.selective_prediction_validation` | yes | selective prediction root | selective tests | selective prediction validation | selective target | included |
| `learner_state.frozen_policy_validation` | yes | frozen policy root | frozen policy tests | frozen policy validation | frozen policy target | included |
| `learner_state.frozen_policy_generation_validation` | yes | generation root | generation tests | generation validation | generation target | included |
| `learner_state.frozen_policy_generation_scaffold_fixture_validation` | yes | scaffold root | scaffold tests | scaffold fixture validation | scaffold fixture target | included |
| `learner_state.frozen_policy_generation_generator_scaffold_fixture_validation` | yes | generator scaffold root | generator fixture tests | generator fixture validation | generator fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_fixture_validation` | yes | artifact writer root | writer tests | artifact writer fixture validation | writer fixture target | included |
| `learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | yes | CLI integration root | CLI integration tests | CLI integration fixture validation | CLI integration target | included |
| `learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | yes | runtime fixture root | runtime fixture tests | runtime fixture validation | runtime fixture target | standalone |
| `learner_state.frozen_policy_generation_artifact_body_fixture_validation` | yes | artifact body root | body tests | artifact body fixture validation | body fixture target | included |
| `learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation` | yes | body file-writing root | body file-writing tests | file-writing fixture validation | body file-writing target | included |
| `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation` | yes | body isolated root | isolated tests | isolated write validation | isolated target | included |
| `learner_state.frozen_policy_generation_manifest_writer_fixture_validation` | yes | manifest writer root | manifest fixture tests | manifest fixture validation | manifest fixture target | included |
| `learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation` | yes | manifest runtime root | runtime fixture tests | runtime fixture validation | runtime fixture target | included |
| `learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation` | yes | manifest file-writing root | file-writing tests | file-writing fixture validation | manifest file-writing target | included |
| `learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation` | yes | manifest isolated root | isolated tests | isolated write validation | isolated target | included |
| `learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation` | yes | production file-writing root | production file-writing tests | production file-writing validation | production target | included |

Validators should enforce schema identity, case identity, expected status and
reason-code alignment, forbidden content scanning, no-oracle flags, synthetic
and metadata-only flags, path safety, file-writing suppression/defaults, and
safe aggregate summaries.

## 13. Release-Quality Chain Specification

The current wrapper is `scripts/check_release_quality.sh`. It runs checks in a
fixed order with `release_quality_check:` labels.

| Position | Label | Command family | Purpose | Safe output | What it proves | What it does not prove |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | git diff whitespace | `git diff --check` | whitespace/diff hygiene | status only | diff whitespace clean | no runtime correctness |
| 2 | conflict marker grep | internal grep | conflict marker scan | content suppressed | no conflict markers in scanned paths | no semantic validation |
| 3 | shell syntax | `sh -n` scripts | script syntax check | status | scripts parse | no runtime success |
| 4 | no-config synthetic summary | synthetic summary script | generate synthetic summary | count/status | synthetic summary path works | no performance evidence |
| 5 | summary manifest schema sync | manifest sync script | compare manifest schema constants | schema/count status | manifest schema alignment | no production guarantee |
| 6 | synthetic diagnostic distribution | diagnostic checker | diagnostic distribution count check | count summary | diagnostic counts satisfy check | no model metric |
| 7 | markdown link check | manual marker | records no project command | manual reason | no automated proof | no link validation |
| 8 | python checks | unittest/compileall | Python test/compile | test status | Python tests pass | not end-user readiness |
| 9 | learner-state audit fixtures | Make target | audit fixture validation | safe summary | fixture audit passes | no real data proof |
| 10 | learner-state exporter CLI smoke | Make target | exporter smoke | safe summary | synthetic export path works | no production export readiness |
| 11 | estimator input validation | Make target | estimator input fixtures | safe summary | fixture validation passes | no estimator correctness |
| 12 | selective prediction calibration validation | Make target | selective fixtures | safe summary | fixture validation passes | no ECE/AURCC achievement |
| 13 | frozen policy validation | Make target | frozen policy fixtures | safe summary | fixture validation passes | no policy quality proof |
| 14 | frozen policy generation validation | Make target | generation fixtures | safe summary | fixture validation passes | no generated quality proof |
| 15 | scaffold fixture validation | Make target | scaffold fixture validation | safe summary | fixture contract passes | no runtime integration proof |
| 16 | scaffold runtime smoke | Make target | metadata-only scaffold runtime | safe summary | scaffold smoke passes | no artifact generation |
| 17 | generator scaffold fixture validation | Make target | generator fixture validation | safe summary | fixture contract passes | no generated policy body proof |
| 18 | generator scaffold runtime smoke | Make target | metadata-only generator scaffold | safe summary | smoke passes | no artifact body |
| 19 | artifact writer fixture validation | Make target | artifact writer fixture contract | safe summary | fixture contract passes | no CLI integration runtime |
| 20 | artifact writer runtime smoke | Make target | artifact writer metadata-only runtime | safe summary | writer smoke passes | no production writing |
| 21 | artifact writer CLI integration fixture validation | Make target | static integration fixture validation | count-only summary | fixture contract passes | no runtime integration execution |
| 22 | artifact body fixture validation | Make target | body fixture contract | safe summary | fixture contract passes | no body payload proof |
| 23 | artifact body generation CLI smoke | Make target | suppressed body generation | safe summary | suppressed smoke passes | no payload public output |
| 24 | artifact body generation safe-metadata CLI smoke | Make target | safe-metadata mode smoke | safe summary | safe-metadata smoke passes | no integration chain |
| 25 | artifact body file writing fixture validation | Make target | file-writing fixture contract | safe summary | fixture validation passes | no production output readiness |
| 26 | artifact body isolated write validation | Make target | isolated write validation | residue/count summary | isolated write checks pass | no production readiness |
| 27 | manifest writer fixture validation | Make target | manifest writer fixtures | safe summary | fixture validation passes | no manifest body generation |
| 28 | manifest writer runtime fixture validation | Make target | runtime fixture contract | safe summary | fixture validation passes | no full integration |
| 29 | manifest writer runtime smoke | Make target | no-file metadata-only runtime | safe summary | runtime smoke passes | no production readiness |
| 30 | manifest writer file writing fixture validation | Make target | file-writing fixture contract | safe summary | fixture validation passes | no public body output |
| 31 | manifest writer isolated write validation | Make target | isolated write validation | residue/count summary | isolated write checks pass | no production readiness |
| 32 | manifest writer production file writing fixture validation | Make target | production-shaped fixture validation | safe summary | fixture validation passes | no production readiness |
| 33 | manifest writer runtime file writing smoke | Make target | opt-in metadata-only file writing smoke | safe summary/residue count | safe file-writing smoke passes | no body generation |
| 34 | config and scoring smoke checks | shell scripts | config/scoring smoke | count/status | synthetic config checks pass | no metric achievement |
| 35 | rust checks | cargo fmt/test/clippy | Rust lint/test | status | Rust checks pass | no real data proof |
| 36 | synthetic policy | policy script | tracked synthetic policy | status | policy scan passes | no legal approval |
| 37 | logger-web checks | npm typecheck/test/build | TypeScript app checks | status | app checks pass | no deployment proof |
| 38 | complete | final marker | wrapper completion | status | wrapper completed | no production readiness |

Raw wrapper output is not copied into this specification.

## 14. Security, Privacy, And No-Oracle Specification

Repository policy requires:

- synthetic-only public fixtures and examples
- metadata-only public summaries for artifact/manifest/frozen-policy
  generation flows
- body-free public output
- no raw rows in public docs or summaries
- no logits/probability dumps in public docs or summaries
- no private path values or absolute local path values in public docs or
  summaries
- no raw learner text in public docs, fixtures, or status markers
- no final corrected text, observed-after text, or gold labels
- no post-hoc annotation
- no test-set tuning
- no scoring feedback payload leakage
- file-writing safe-root and opt-in behavior
- cleanup and residue checks for write-smoke and isolated-write targets
- public-safe remote status markers
- no raw GitHub Actions logs or full job output in docs

Primary evidence paths include `SECURITY.md`, `docs/03_no_oracle_policy.md`,
`docs/10_data_quality_policy.md`, `docs/11_public_release_policy.md`,
`docs/12_synthetic_data_policy.md`, `docs/public_release_checklist.md`,
`docs/status/README.md`, fixture README files, validator modules, and status
markers.

## 15. File-Writing Specification

Default behavior is no file writing for most validators and runtime smokes.
File writing is opt-in and constrained to safe paths where implemented.

| Area | Behavior | Safety requirements |
| --- | --- | --- |
| Sequence exporter | Writes separated synthetic outputs to caller-provided output dirs | Synthetic fixture input, safe output dir, audit after export. |
| Synthetic E2E scripts | Write synthetic summaries and generated candidate outputs under `tmp/` | Content-suppressed status and generated operational artifacts. |
| Artifact body file writing | Fixture validation and smoke surfaces exist | Body payload must remain suppressed; unsafe paths fail closed. |
| Artifact body isolated write validation | Uses isolated temp/safe root behavior | Cleanup and residue count checks. |
| Manifest writer file writing | Metadata-only file-writing fixtures and runtime smoke | Safe root, no absolute/private output, parse/scan/finalize/cleanup. |
| Manifest writer isolated write validation | Isolated safe write validation | Residue checks and output path policy. |
| Manifest writer production file writing fixtures | Production-shaped fixture validation only | Not production readiness. |

Public output must not include written file bodies, manifest bodies, artifact
body payloads, request/pointer/expected bodies, raw rows, logits, private path
values, absolute path values, or raw learner text.

## 16. Artifact And Manifest Specification

| Component | Current behavior | Body-free boundary | Not implemented / not proven |
| --- | --- | --- | --- |
| Generator scaffold output | Metadata-only generator scaffold summary | Generated body unavailable/suppressed | Generated policy quality not proven. |
| Artifact writer result | Metadata-only artifact writer result and fixture/runtime checks | Artifact body suppressed; manifest body suppressed | Artifact writer CLI integration runtime not implemented. |
| Artifact writer CLI integration fixture validation | Static fixture contract validation from generator scaffold to artifact writer boundary | Count-only summary | Runtime integration not executed. |
| Artifact writer CLI integration runtime fixture validation | Static future runtime fixture validation | Count-only summary | Release-quality integration and runtime implementation not present as of scan. |
| Artifact body generation suppressed mode | Suppressed metadata-only CLI smoke | No body payload in public output | Broader integration flow not implemented. |
| Artifact body generation safe-metadata mode | Safe metadata summary smoke | No payload body | Not production output readiness. |
| Manifest writer result | Metadata-only manifest writer runtime and fixture checks | No manifest body output | Manifest body generation not implemented. |
| Manifest writer runtime file writing | Opt-in metadata-only file writing smoke | Written body not copied to docs; residue checked | Production readiness not proven. |

## 17. Logger-Web Specification

`apps/logger-web/` is a TypeScript/Vite browser logger application for
synthetic-only raw event collection and testing.

| Aspect | Specification |
| --- | --- |
| Runtime | Node/npm with Vite and TypeScript. |
| Source files | `apps/logger-web/src/main.ts`, `apps/logger-web/src/rawEvent.ts`, `apps/logger-web/src/styles.css`, `index.html`. |
| Package files | `apps/logger-web/package.json`, `package-lock.json`, TypeScript configs, Vite config. |
| Scripts | `npm run dev`, `npm run build`, `npm run typecheck`, `npm test`. |
| Release-quality | typecheck, test, and build are included. |
| Schema relation | Raw event shape is related to Rust raw event schema and docs. |
| Limitations | Not a deployment proof; real participant data collection readiness is not proven. |

## 18. Rust Crates Specification

The Rust workspace is defined in root `Cargo.toml`.

| Crate | Role |
| --- | --- |
| `kslog_schema` | Raw event schema types and validation of forbidden no-oracle fields. |
| `kslog_validate` | JSONL/raw event validation logic and validation error behavior. |
| `kslog_replay` | Replay behavior and safe diagnostics. |
| `kslog_extract` | Revision-like event extraction. |
| `kslog_micro_episode` | Micro-episode construction from replay/extraction context. |
| `kslog_no_oracle_audit` | No-oracle audit checks for safe view and related metadata. |
| `kslog_cli` | CLI wrapper over validation, replay diagnostics, extraction, micro episodes, audit, and safe view export. |

Rust checks:

- `cargo fmt --all -- --check`
- `cargo test --workspace`
- `cargo clippy --workspace -- -D warnings`

These checks prove Rust formatting/tests/lints pass for the repository state
where they are run. They do not prove production readiness or real-data
readiness.

## 19. Python Package Specification

| Package | Role | Key modules |
| --- | --- | --- |
| `candidate_generation` | Synthetic candidate generation | `generate.py`, `generator.py`, `loader.py`, `models.py` |
| `evaluation` | Synthetic expected-action evaluation and registry checks | `evaluate.py`, `evaluator.py`, `expected_action_registry.py`, `loader.py`, `models.py` |
| `ot_scorer` | Feature/constraint/scoring/diagnostic/config tools | `features.py`, `constraints.py`, `score.py`, `diagnostic_summary.py`, `validate_weight_config.py`, `score_fixture_lock.py`, `config_ranking_diff.py` |
| `learner_state` | Learner-state validation/export/frozen policy generation infrastructure | listed below |
| `test_support` | Safe output scan helper | `safe_output_scan.py` |
| `visualization` | Placeholder directory | `.gitkeep`; implementation not yet confirmed from repository scan |

### Learner-State Modules

| Module | Role |
| --- | --- |
| `sequence_audit.py` | Static audit of learner-state sequence fixtures and no-oracle constraints. |
| `sequence_exporter.py` | Synthetic sequence exporter with audit integration. |
| `estimator_input.py` | Estimator input fixture validation. |
| `selective_prediction_validation.py` | Selective prediction/calibration fixture validation. |
| `frozen_policy_validation.py` | Frozen selective prediction policy fixture validation. |
| `frozen_policy_generation_validation.py` | Frozen policy generation fixture validation. |
| `frozen_policy_generation.py` | Metadata-only scaffold runtime and CLI. |
| `frozen_policy_generation_generator_scaffold.py` | Metadata-only generator scaffold runtime and CLI. |
| `frozen_policy_generation_artifact_writer.py` | Metadata-only artifact writer runtime and CLI. |
| `frozen_policy_generation_artifact_writer_fixture_validation.py` | Artifact writer fixture validator. |
| `frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py` | Artifact writer CLI integration fixture validator. |
| `frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py` | Artifact writer CLI integration runtime fixture validator; static only. |
| `frozen_policy_generation_artifact_body.py` | Artifact body suppressed/safe-metadata generation CLI. |
| artifact body validation modules | Fixture, file-writing, and isolated-write validation. |
| `frozen_policy_generation_manifest_writer.py` | Manifest writer runtime and metadata-only file-writing smoke. |
| manifest writer validation modules | Fixture, runtime fixture, file-writing, isolated-write, and production-file-writing validation. |

## 20. Status Markers And Documentation Specification

Status markers under `docs/status/` are public-safe records. They are
pass-only or count-only metadata summaries and do not copy raw logs, full job
output, fixture bodies, request/pointer/expected bodies, manifest bodies,
artifact body payloads, generated policy bodies, raw rows, logits, private
path values, absolute path values, raw learner text, or performance evidence.

Documentation categories include:

- project overview and beginner docs
- architecture and processing specs
- no-oracle, synthetic data, data quality, and public release policy docs
- fixture contract docs
- validator design docs
- Makefile target design docs
- release-quality integration design docs
- remote/manual run record workflow docs
- remote status marker docs
- milestone recaps
- public release checklist
- source inventory and this full technical specification draft

The Step-pretec-doc1 inventory is the coverage source for this draft. This
draft should be validated in Step-pretec-doc3 or later.

## 21. Implementation Status Matrix

| Component | Implemented | Fixture-only | Validator-only | Standalone Makefile | Release-quality integrated | Remote status recorded | Docs-only | Not implemented / future |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logger web | yes | no | no | `check-logger` | yes | no | no | deployment/real data readiness |
| Rust crates | yes | no | no | `check-rust` | yes | no | no | production readiness |
| Candidate/evaluation/scoring | yes | synthetic fixtures | some validators/checks | summary/config/fixture targets | partial through scripts | no | no | metric achievement |
| Learner-state audit/exporter | yes | yes | yes | yes | yes | yes | no | real-data readiness |
| Estimator input | validator implemented | yes | yes | yes | yes | yes | no | estimator correctness |
| Selective prediction | validator implemented | yes | yes | yes | yes | yes | no | ECE/AURCC achievement |
| Frozen policy | validator implemented | yes | yes | yes | yes | yes | no | policy quality |
| Frozen policy generation | validator implemented | yes | yes | yes | yes | yes | no | generated policy quality |
| Scaffold runtime | yes metadata-only | yes | yes | yes | yes | yes | no | generator quality |
| Generator scaffold | yes metadata-only | yes | yes | yes | yes | yes | no | artifact body generation |
| Artifact writer | yes metadata-only | yes | yes | yes | yes | yes | no | CLI integration runtime |
| Artifact writer CLI integration fixture validation | validator implemented | yes | yes | yes | yes | yes | no | runtime correctness |
| Artifact writer CLI integration runtime fixture validation | static validator implemented | yes | yes | yes | no observed | no | no | runtime implementation |
| Artifact writer CLI integration runtime | no | supporting fixtures exist | supporting validator exists | supporting target exists | no | no | design docs exist | not implemented |
| Artifact writer CLI actual invocation fixtures | static validator implemented | yes, Step498 fixture root | focused tests | standalone target | yes | no | contract docs exist | wrapper-integrated static validation; actual invocation not implemented |
| Artifact body generation runtime integration plan-only bridge | selected-case runtime implemented | existing Step523 fixture root | focused tests | standalone target | yes | no | Step532-Step539 docs exist | Step535 CLI emits metadata-only selected-case summary; Step537 adds a standalone target; Step539 adds the release-quality wrapper label after static integration fixture validation; no artifact body runtime invocation, manifest writer, or file writing |
| Artifact body generation runtime invocation fixture root | standalone validator implemented | 30-case Step570 root | focused validator tests | standalone target | yes | no | Step569-Step581 docs plus fixture README | Step581 adds the Step574 public-safe validator target to the release-quality wrapper after safe-metadata runtime smoke and before the planned-only v0.3 runtime smoke; runtime implementation, actual artifact body generation runtime invocation, manifest writer integration, and file writing are not implemented |
| Artifact body generation runtime invocation planned-only mode | selected-case runtime mode implemented | Step570 primary valid case | focused runtime integration tests | standalone target | yes | no | Step575-Step581 docs plus fixture README | Step581 adds the Step579 planned-only v0.3 smoke to the release-quality wrapper immediately after the runtime invocation fixture validator and before artifact body fixture validation; it records invocation as planned but not invoked, with no manifest writer invocation and no file writing |
| Artifact body generation | safe/suppressed smokes | yes | yes | yes | yes | yes | no | broader CLI integration |
| Artifact body generation CLI integration | no | partial supporting fixtures | no full integration | no | no | no | design fragments | not implemented |
| Manifest writer | yes metadata-only | yes | yes | yes | yes | yes | no | broader integration |
| Manifest writer integration | no beyond current runtime | supporting fixtures | supporting validators | partial writer targets | current writer checks only | writer markers | design docs | not implemented |
| Manifest body generation | no | no | no | no | no | no | docs mention boundary | not implemented |
| Production readiness | no | no | no | no | no | no | public checklist only | not proven |
| Real-data readiness | no | no | no | no | no | no | private checklist docs only | not proven |

## 22. Traceability Table

| Component | Implementation files | Tests | Fixtures | Docs | Makefile target | Release-quality label | Status marker | Current status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Logger web | `apps/logger-web/src/` | `apps/logger-web/tests/` | none | app README/EXPLAINED | `check-logger` | logger-web checks | none | implemented app checks |
| Rust kslog | `crates/*/src/` | Rust crate tests | synthetic fixtures | crate docs and core specs | `check-rust` | rust checks | none | implemented checks |
| Synthetic summary/scoring | `scripts/`, `python/ot_scorer/` | Python tests | synthetic fixture roots | summary/config/scoring docs | summary/config targets | config and scoring smoke checks | none | implemented synthetic checks |
| Learner-state audit | `sequence_audit.py` | sequence audit tests | sequence audit fixtures | audit docs | audit target | learner-state audit fixtures | audit marker | implemented validator |
| Sequence exporter | `sequence_exporter.py` | exporter tests | exporter fixtures | exporter docs | exporter CLI target | exporter CLI smoke | exporter marker | implemented synthetic exporter |
| Estimator input | `estimator_input.py` | estimator input tests | estimator fixtures | estimator docs | estimator target | estimator input validation | estimator marker | validator-only |
| Selective prediction | `selective_prediction_validation.py` | selective tests | selective fixtures | selective docs | selective target | selective prediction validation | selective marker | validator-only |
| Frozen policy | `frozen_policy_validation.py` | policy tests | frozen policy fixtures | frozen policy docs | frozen policy target | frozen policy validation | frozen policy marker | validator-only |
| Frozen policy generation | `frozen_policy_generation_validation.py` | generation tests | generation fixtures | generation docs | generation target | generation validation | generation marker | validator-only |
| Scaffold runtime | `frozen_policy_generation.py` | scaffold runtime tests | scaffold fixtures | scaffold docs | scaffold runtime target | scaffold runtime smoke | scaffold runtime marker | metadata-only runtime |
| Generator scaffold | generator scaffold module | generator tests | generator fixtures | generator docs | generator targets | generator labels | generator markers | metadata-only scaffold |
| Artifact writer | artifact writer module and validator | writer tests | writer fixtures | writer docs | writer targets | writer labels | writer markers | metadata-only writer |
| Artifact writer CLI integration fixture | CLI integration validator | CLI integration tests | CLI integration fixtures | CLI integration docs | CLI integration fixture target | CLI integration fixture validation | CLI integration marker | release-quality integrated static validation |
| Artifact writer CLI integration runtime fixture | runtime fixture validator | runtime fixture tests | runtime fixture root | runtime fixture docs | runtime fixture target | runtime fixture validation | runtime fixture marker | release-quality integrated static validation |
| Artifact writer CLI integration runtime | `frozen_policy_generation_artifact_writer_cli_integration_runtime.py` | runtime focused tests | supporting runtime fixtures | runtime design docs | none | none | none | metadata-only runtime boundary; standalone CLI |
| Artifact writer CLI actual invocation fixture | `frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py` | actual invocation fixture validator focused tests | actual invocation fixture root | actual invocation design / contract / validator docs | `check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures` | actual invocation fixture validation | none | release-quality integrated static validation in Step504; actual invocation not implemented |
| Artifact body generation runtime integration plan-only bridge | `frozen_policy_generation_artifact_body_generation_runtime_integration.py` | runtime integration focused tests | existing integration fixture root selected case | Step532-Step539 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration` | artifact body generation runtime integration plan-only bridge smoke | none | selected-case `plan-only-bridge` CLI with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`; standalone target added in Step537 and wrapper label added in Step539; no artifact body runtime invocation, manifest writer, or file writing |
| Artifact body generation runtime invocation fixture root | `frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py` | focused validator tests | `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/` | Step569-Step581 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures` | artifact body generation runtime invocation fixture validation | none | release-quality wrapper now runs the metadata-only / body-free fixture validation before planned-only v0.3 runtime smoke; no actual artifact body generation runtime invocation, manifest writer integration, or file writing |
| Artifact body generation runtime invocation planned-only mode | `frozen_policy_generation_artifact_body_generation_runtime_integration.py` | runtime integration focused tests | Step570 primary valid case | Step575-Step581 docs and fixture README | `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation` | artifact body generation runtime invocation planned-only v0.3 smoke | none | selected-case v0.3 CLI mode `artifact-body-runtime-invocation`; release-quality wrapper now runs it after fixture validation, with runtime invocation planned but not invoked, no manifest writer invocation, and no file writing |
| Artifact body | artifact body module/validators | body tests | body fixture roots | body docs | body targets | body labels | body markers | body-suppressed checks |
| Manifest writer | manifest writer module/validators | manifest writer tests | manifest fixture roots | manifest docs | manifest targets | manifest labels | manifest markers | metadata-only writer/file-writing checks |
| Release Quality | wrapper script/workflow | wrapper execution | not applicable | release-quality docs | `check-release-quality` | wrapper labels | status markers | implemented wrapper |

## 23. Limitations And Non-Proofs

This draft does not prove:

- model performance
- F1, accuracy, ECE, or AURCC achievement
- production readiness
- real-data readiness
- privacy/legal/IRB readiness
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- manifest body generation correctness
- generated policy quality
- learner-state estimator correctness
- production data collection validity

Release-quality success means the wrapper checks passed in the environment
where they ran. It does not convert synthetic metadata-only validation into
real-data readiness or production evidence.

## 24. Future Work

Recommended next steps:

- Step-pretec-doc3: coverage validation for this draft against the source
  inventory and repository scan, completed as a docs-only report
- Step-pretec-doc4: medium-priority coverage gap appendices, completed with
  Python CLI, Makefile target, schema/version, fixture count, and external
  review checklist appendices
- artifact writer CLI integration runtime release-quality integration staging
  after the Step491 standalone Makefile target
- artifact body generation CLI integration design and implementation
- manifest writer integration design and implementation
- manifest body generation design, if it remains in scope
- production readiness review, separate from this research software draft
- real-data readiness review, separate and institution-approved
- external review checklist for public specification release
- low-priority hardening for dependency/version tables, per-status-marker
  index, Rust crate API detail, logger-web UI behavior, and workflow action
  version tables, completed at external-review summary level in
  Step-pretec-doc5
- final safety and non-proof review, completed as Step-pretec-doc6 docs-only
  review before external reviewer pass

## 25. Coverage And Evidence Appendix

Primary inventory source:

- `docs/full_technical_specification_source_inventory.md`

Scan scope from Step-pretec-doc1:

- root files and package/workspace metadata
- README and SECURITY
- Makefile and scripts
- `.github/workflows/`
- Python packages and tests
- Rust crates
- logger-web app
- fixture roots and fixture READMEs
- docs and status markers
- schema/version names
- release-quality labels
- CLI entrypoints
- safety flags and public-safe policies

Known uncertainty:

- Python CLI arguments, Makefile command families, stable schema/result
  families, and fixture root counts are covered in Appendices A-D as of
  Step-pretec-doc4
- dependency/version tables, per-status-marker indexing, Rust crate API
  review notes, logger-web UI behavior notes, and workflow action version
  tables are summarized at external-review level in Appendices F-I as of
  Step-pretec-doc5
- any component not represented in this draft should be treated as
  `not yet confirmed from repository scan` unless a later coverage validation
  or external review confirms it

Future coverage validation or external review should compare this draft
against:

- `docs/full_technical_specification_source_inventory.md`
- `Makefile`
- `scripts/check_release_quality.sh`
- `.github/workflows/ci.yml`
- `.github/workflows/release-quality.yml`
- `python/`
- `crates/`
- `apps/logger-web/`
- `tests/fixtures/`
- `docs/status/`

## Appendix A. Python CLI Argument Catalogue

Step-pretec-doc4 adds this appendix to close the medium-priority CLI argument
coverage gap found in Step-pretec-doc3. The catalogue is based on repository
source scans of Python modules that define `argparse` parsers. It records
argument names only; it does not copy fixture bodies, request bodies, pointer
bodies, expected bodies, raw rows, raw learner text, logits, probabilities, or
generated policy/artifact/manifest bodies.

| Module path | Command | Args | Purpose | Input / output | File writing behavior | Makefile / release-quality relation | Safety note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `python/candidate_generation/generate.py` | `python -m candidate_generation.generate` | `--input`, `--output` | Candidate generation CLI | synthetic input path to candidate output | writes caller-selected output | not directly in release-quality wrapper | synthetic-only; no performance claim |
| `python/evaluation/evaluate.py` | `python -m evaluation.evaluate` | `--scores`, `--expected`, `--output` | Synthetic expected-action evaluation | candidate scores and expected-action metadata to report output | writes caller-selected output | not directly in wrapper | not model-performance evidence |
| `python/evaluation/expected_action_registry.py` | `python -m evaluation.expected_action_registry` | `--registry`, `--case-name` | Expected-action registry inspection | registry metadata to safe status | no confirmed write behavior | not directly in wrapper | synthetic registry only |
| `python/ot_scorer/features.py` | `python -m ot_scorer.features` | `--input`, `--output` | Feature generation | synthetic input to feature output | writes caller-selected output | used through scripts/tests | no raw learner text in public docs |
| `python/ot_scorer/constraints.py` | `python -m ot_scorer.constraints` | `--input`, `--output` | Constraint generation | synthetic feature input to constraint output | writes caller-selected output | used through scripts/tests | no oracle fields in public output |
| `python/ot_scorer/score.py` | `python -m ot_scorer.score` | `--input` / `--constraints`, `--output`, `--weight-config` | OT-inspired scoring | synthetic candidates/constraints/config to score output | writes caller-selected output | config/scoring smoke scripts | no metric achievement claim |
| `python/ot_scorer/summarize_diagnostics.py` | `python -m ot_scorer.summarize_diagnostics` | `--constraints`, `--output` | Diagnostic summary generation | synthetic constraints to summary output | writes caller-selected output | summary/check scripts | count-only diagnostics |
| `python/ot_scorer/validate_weight_config.py` | `python -m ot_scorer.validate_weight_config` | `--config` | Hand weight config validation | synthetic config to validation status | no | `check-fixtures` scripts | config validation only |
| `python/ot_scorer/score_fixture_lock.py` | `python -m ot_scorer.score_fixture_lock` | `--expected`, `--generated`, `--case-name` | Fixture score lock comparison | expected/generated synthetic score paths to mismatch status | no | `check-fixtures` scripts | mismatch summaries only |
| `python/ot_scorer/config_ranking_diff.py` | `python -m ot_scorer.config_ranking_diff` | `--no-config`, `--config`, `--case-name`, `--expect-zero-diff`, `--expect-weighted-score-diff` | Config ranking diff check | synthetic score outputs/config metadata to diff status | no direct writing; scripts may create controlled outputs | config/scoring smoke scripts | no model-performance claim |
| `python/learner_state/sequence_audit.py` | `python -m learner_state.sequence_audit` | `--features`, `--labels`, `--manifest`, `--fixture-case`, `--fixture-root`, `--json` | Sequence audit validation | dataset metadata or fixture root/case to safe audit summary | no | `check-learner-state-audit-fixtures`; wrapper included | no-oracle audit; no raw rows |
| `python/learner_state/sequence_exporter.py` | `python -m learner_state.sequence_exporter` | `--input-fixture`, `--output-dir`, `--json` | Sequence export smoke | synthetic fixture to separated output files and safe summary | writes caller output dir | `check-learner-state-exporter-cli`; wrapper included | synthetic-only export; path safety checked |
| `python/learner_state/estimator_input.py` | `python -m learner_state.estimator_input` | `--fixture-case`, `--fixture-root`, `--json` | Estimator input fixture validation | fixture case/root to safe summary | no | `check-learner-state-estimator-input`; wrapper included | no estimator correctness claim |
| `python/learner_state/selective_prediction_validation.py` | `python -m learner_state.selective_prediction_validation` | `--fixture-case`, `--fixture-root`, `--json` | Selective prediction fixture validation | fixture case/root to safe summary | no | `check-learner-state-selective-prediction`; wrapper included | no ECE/AURCC achievement |
| `python/learner_state/frozen_policy_validation.py` | `python -m learner_state.frozen_policy_validation` | `--fixture-case`, `--fixture-root`, `--json` | Frozen policy fixture validation | fixture case/root to safe summary | no | `check-learner-state-frozen-policy`; wrapper included | no policy quality proof |
| `python/learner_state/frozen_policy_generation_validation.py` | `python -m learner_state.frozen_policy_generation_validation` | `--fixture-case`, `--fixture-root`, `--json` | Frozen policy generation fixture validation | fixture case/root to safe summary | no | `check-learner-state-frozen-policy-generation`; wrapper included | no generated policy quality proof |
| `python/learner_state/frozen_policy_generation.py` | `python -m learner_state.frozen_policy_generation` | `--request`, `--pointer`, `--json` | Scaffold runtime smoke | metadata-only request/pointer to safe summary | no artifact writing | scaffold runtime target; wrapper included | artifact body suppressed |
| `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_scaffold_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Scaffold fixture validation | fixture root/case to safe summary | no | scaffold fixture target; wrapper included | metadata-only validation |
| `python/learner_state/frozen_policy_generation_generator_scaffold.py` | `python -m learner_state.frozen_policy_generation_generator_scaffold` | `--request`, `--pointer`, `--json` | Generator scaffold smoke | metadata-only request/pointer to safe summary | no body/file writing | generator runtime target; wrapper included | no generated policy body |
| `python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Generator scaffold fixture validation | fixture root/case to safe summary | no | generator fixture target; wrapper included | no body leakage |
| `python/learner_state/frozen_policy_generation_artifact_writer.py` | `python -m learner_state.frozen_policy_generation_artifact_writer` | `--request`, `--pointer`, `--json` | Artifact writer runtime smoke | metadata-only request/pointer to safe summary | no body writing | artifact writer runtime target; wrapper included | artifact/manifest bodies suppressed |
| `python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Artifact writer fixture validation | fixture root/case to safe summary | no | artifact writer fixture target; wrapper included | metadata-only fixture validation |
| `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Artifact writer CLI integration fixture validation | fixture root/case to count-only summary | no | CLI integration fixture target; wrapper included | static fixture contract only |
| `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Future runtime fixture validation | fixture root/case to count-only summary | no | standalone Makefile target; wrapper included for static validation | does not execute runtime integration |
| `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py` | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime` | `--fixture-root`, `--fixture-case`, `--request-metadata`, `--pointer-metadata`, `--artifact-writer-cli-metadata`, `--json`, `--actual-invocation`, `--plan-only`, `--summary-only`, `--no-file-writing`, `--fail-closed-on-unsafe-output`, `--artifact-writer-cli-module`, `--timeout-seconds` | Metadata-only artifact writer CLI integration runtime boundary | fixture case or explicit metadata paths to public-safe runtime summary; Step513 adds explicit `actual_invocation_metadata_only` summary mode; Step515 adds a standalone smoke target for one valid v0.2 case | no | plan-only target included after Step493; Step517 adds the actual invocation metadata-only target after static actual invocation fixture validation and before artifact body fixture validation | plan-only remains default; actual invocation mode captures/suppresses output, scans safety metadata, and does not invoke artifact body generation or manifest writer |
| `python/learner_state/frozen_policy_generation_artifact_body.py` | `python -m learner_state.frozen_policy_generation_artifact_body` | `--request`, `--pointer`, `--mode`, `--artifact-body-out`, `--json` | Artifact body suppressed/safe-metadata smoke | metadata-only request/pointer to safe summary or opt-in safe output | optional safe output for file-writing smoke | body generation and safe-metadata targets; wrapper included | no artifact body payload in public output |
| `python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_body_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Artifact body fixture validation | fixture root/case to safe summary | no | body fixture target; wrapper included | body suppressed |
| `python/learner_state/frozen_policy_generation_artifact_body_file_writing_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Artifact body file-writing fixture validation | fixture root/case to safe summary | no | body file-writing target; wrapper included | validates safe writing policy |
| `python/learner_state/frozen_policy_generation_artifact_body_isolated_write_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation` | `--fixture-root`, `--fixture-case`, `--json` | Artifact body isolated write validation | fixture root/case to safe summary | controlled isolated validation only | isolated write target; wrapper included | residue checks; no body leakage |
| `python/learner_state/frozen_policy_generation_manifest_writer.py` | `python -m learner_state.frozen_policy_generation_manifest_writer` | `--request`, `--artifact-result`, `--artifact-body-result`, `--json`, `--manifest-out`, `--allow-overwrite` | Manifest writer runtime and file-writing smoke | metadata-only inputs to safe summary or opt-in safe output | optional safe-root file writing | runtime and runtime-file-writing targets; wrapper included | no manifest body generation |
| `python/learner_state/frozen_policy_generation_manifest_writer_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_manifest_writer_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Manifest writer fixture validation | fixture root/case to safe summary | no | manifest writer fixture target; wrapper included | metadata-only validation |
| `python/learner_state/frozen_policy_generation_manifest_writer_runtime_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Manifest writer runtime fixture validation | fixture root/case to safe summary | no | runtime fixture target; wrapper included | runtime fixture contract only |
| `python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Manifest writer file-writing fixture validation | fixture root/case to safe summary | no | file-writing fixture target; wrapper included | safe-root policy validation |
| `python/learner_state/frozen_policy_generation_manifest_writer_isolated_write_validation.py` | `python -m learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation` | `--fixture-root`, `--fixture-case`, `--json` | Manifest writer isolated write validation | fixture root/case to safe summary | controlled isolated validation only | isolated write target; wrapper included | residue checks |
| `python/learner_state/frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Production-shaped manifest writer file-writing fixture validation | fixture root/case to safe summary | no | production fixture target; wrapper included | not production readiness |

## Appendix B. Makefile Target Command Mapping

Step-pretec-doc4 adds this appendix to close the medium-priority Makefile
command mapping gap. Commands are summarized from `Makefile`; long multi-line
smoke bodies are represented as command families, not copied as raw output or
logs.

| Target | Command or command family | Purpose | Output type | Inclusion | Related component | Safety note |
| --- | --- | --- | --- | --- | --- | --- |
| `help` | `echo` help lines | List available targets | text help | standalone | Makefile | no runtime execution |
| `check-release-quality` | `scripts/check_release_quality.sh` | Run wrapper | ordered status summaries | wrapper entrypoint | release-quality | content-suppressed checks |
| `check-summary` | `scripts/run_synthetic_e2e_summary.sh` | Synthetic E2E summary | count/status summary | wrapper component | synthetic summary | writes controlled `tmp/` outputs |
| `check-manifest-sync` | `scripts/check_summary_manifest_schema_sync.sh` | Manifest schema sync | schema/status summary | wrapper component | summary manifest | body-free output |
| `check-diagnostic-distribution` | `scripts/check_synthetic_diagnostic_distribution.sh` | Diagnostic distribution check | count/status summary | wrapper component | diagnostics | no performance claim |
| `check-summary-flow` | summary, manifest sync, diagnostic scripts | Run summary-flow bundle | safe summaries | standalone bundle | summary-flow | do not parallelize |
| `check-config-smoke` | config-enabled summary and E2E scripts | Config smoke bundle | status/count summary | wrapper component | scoring/config | synthetic-only |
| `check-python` | unittest discover and compileall | Python tests/compile | test status | wrapper equivalent | Python | no implementation change |
| `check-rust` | cargo fmt/test/clippy | Rust format/test/lint | check status | wrapper included | Rust crates | synthetic tests only |
| `check-logger` | npm typecheck/test/build in `apps/logger-web` | Logger web checks | build/test status | wrapper included | logger-web | not deployment proof |
| `check-policy` | `scripts/check_synthetic_policy.sh` | Synthetic policy scan | policy status | wrapper included | safety policy | no legal/privacy approval |
| `check-fixtures` | score lock, hand weight config, ranking diff scripts | Fixture/config checks | count/status summary | wrapper component | scoring fixtures | no metric achievement |
| `check-learner-state-audit-fixtures` | `python -m learner_state.sequence_audit --fixture-root ...` | Audit fixture validation | safe summary | wrapper included | learner-state audit | no raw rows |
| `check-learner-state-exporter-cli` | cleanup plus two `sequence_exporter` runs | Exporter smoke | safe summary and controlled outputs | wrapper included | sequence exporter | controlled tmp output |
| `check-learner-state-estimator-input` | `python -m learner_state.estimator_input --fixture-root ...` | Estimator input validation | safe summary | wrapper included | estimator input | no estimator correctness proof |
| `check-learner-state-selective-prediction` | selective prediction validator root mode | Selective prediction validation | safe summary | wrapper included | selective prediction | no ECE/AURCC claim |
| `check-learner-state-frozen-policy` | frozen policy validator root mode | Frozen policy validation | safe summary | wrapper included | frozen policy | no policy quality proof |
| `check-learner-state-frozen-policy-generation` | generation validator root mode | Generation fixture validation | safe summary | wrapper included | frozen policy generation | no generated quality proof |
| `check-learner-state-frozen-policy-generation-scaffold-fixtures` | scaffold fixture validator root mode | Scaffold fixture validation | safe summary | wrapper included | scaffold | metadata-only |
| `check-learner-state-frozen-policy-generation-scaffold-runtime` | scaffold runtime with request/pointer fixtures | Scaffold runtime smoke | safe summary | wrapper included | scaffold runtime | no artifact writing |
| `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures` | generator fixture validator root mode | Generator fixture validation | safe summary | wrapper included | generator scaffold | no body leakage |
| `check-learner-state-frozen-policy-generation-generator-scaffold-runtime` | generator scaffold runtime with request/pointer fixtures | Generator runtime smoke | safe summary | wrapper included | generator scaffold | no generated policy body |
| `check-learner-state-frozen-policy-generation-artifact-writer-fixtures` | artifact writer fixture validator root mode | Artifact writer fixture validation | safe summary | wrapper included | artifact writer | metadata-only |
| `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures` | CLI integration fixture validator root mode | CLI integration fixture validation | count-only summary | wrapper included | artifact writer CLI integration | static contract only |
| `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures` | runtime fixture validator root mode | Runtime fixture validation | count-only summary | release-quality included | artifact writer CLI integration runtime fixtures | no runtime execution |
| `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime` | runtime CLI valid fixture smoke | Runtime smoke | body-free public-safe summary | release-quality included after Step493 | artifact writer CLI integration runtime | no artifact writer CLI actual invocation, no file writing |
| `check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime` | runtime CLI v0.2 valid actual invocation metadata-only fixture smoke | Runtime smoke | body-free public-safe v0.2 summary | release-quality wrapper included after Step517 | `valid/valid_actual_invocation_minimal_metadata_only` | no file writing, no artifact body generation, no manifest writer; expected safe output includes `runtime_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`, `invocation_mode=actual_invocation_metadata_only`, `artifact_writer_cli_output_body_free=True`, and `file_writing_enabled=False` |
| `check-learner-state-frozen-policy-generation-artifact-writer-runtime` | artifact writer runtime with request/pointer fixtures | Artifact writer runtime smoke | safe summary | wrapper included | artifact writer | no body writing |
| `check-learner-state-frozen-policy-generation-artifact-body-fixtures` | artifact body fixture validator root mode | Artifact body fixture validation | safe summary | wrapper included | artifact body | body suppressed |
| `check-learner-state-frozen-policy-generation-artifact-body-generation` | artifact body CLI suppressed mode | Artifact body smoke | safe summary | wrapper included | artifact body generation | payload suppressed |
| `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata` | artifact body CLI safe-metadata mode | Safe-metadata body smoke | safe summary | wrapper included | artifact body generation | no payload public output |
| `check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures` | artifact body file-writing fixture validator root mode | File-writing fixture validation | safe summary | wrapper included | artifact body file writing | validates safe write policy |
| `check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke` | multi-step safe-metadata write smoke under controlled tmp | Artifact body write smoke | parse/safety/cleanup status | standalone as of wrapper scan | artifact body file writing | cleanup and safety scan |
| `check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation` | artifact body isolated write validator root mode | Isolated write validation | residue/count summary | wrapper included | artifact body isolated writing | controlled residue checks |
| `check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation` | manifest writer isolated write validator root mode | Manifest isolated write validation | residue/count summary | wrapper included | manifest writer | safe-root policy |
| `check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures` | manifest writer file-writing fixture validator root mode | File-writing fixture validation | safe summary | wrapper included | manifest writer | metadata-only |
| `check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures` | production-shaped file-writing fixture validator root mode | Production-shaped fixture validation | safe summary | wrapper included | manifest writer | not production readiness |
| `check-learner-state-frozen-policy-generation-manifest-writer-fixtures` | manifest writer fixture validator root mode | Manifest fixture validation | safe summary | wrapper included | manifest writer | no manifest body |
| `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures` | runtime fixture validator root mode | Runtime fixture validation | safe summary | wrapper included | manifest writer runtime | static fixture validation |
| `check-learner-state-frozen-policy-generation-manifest-writer-runtime` | manifest writer runtime no-file smoke | Runtime smoke | safe summary | wrapper included | manifest writer runtime | no file writing |
| `check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing` | multi-step manifest writer safe file-writing smoke | Runtime file-writing smoke | safe summary and residue status | wrapper included | manifest writer runtime file writing | safe-root, parse, scan, cleanup |
| `check-all` | depends on `check-release-quality` | Run wrapper | wrapper status | wrapper entrypoint | release-quality | same as wrapper |

## Appendix C. Schema / Result Version Catalogue

Step-pretec-doc4 adds this appendix to close the medium-priority schema
catalogue gap. It separates stable schema/result/version names from synthetic
invalid markers and reason-code markers. It lists names and families only; it
does not include schema bodies or JSON payload examples.

### Stable Schema And Result Version Names

| Name | Family | Related component | Evidence | Safety relevance |
| --- | --- | --- | --- | --- |
| `kslog.raw_event.v1` | raw event schema | logger/Rust raw events | raw event docs and Rust schema crate | no-oracle forbidden fields rejected |
| `summary_manifest_schema_v1` / manifest schema version `1.0` | summary manifest | synthetic E2E summary | `docs/schemas/summary_manifest_schema_v1.json`, scripts | allowed/forbidden key sync |
| `candidate_feature_schema_v0_3` | candidate/scoring | OT scorer features | `python/ot_scorer/`, feature docs | feature-only; no raw text examples |
| `evaluation_report_schema_v0_1` | evaluation | expected-action evaluation | evaluation modules/docs | not performance evidence |
| `diagnostic_summary_schema_v0_1` | diagnostics | OT scorer diagnostics | diagnostic module/docs | count-only diagnostics |
| `hand_weight_config_schema_v0_1` | scoring config | hand weight config | config validator/fixtures | synthetic config validation |
| `ot_constraint_schema_v0_1`, `ot_constraint_schema_v0_2` | scoring constraints | OT scorer constraints | scorer modules/docs | no model metric claim |
| `learner_state_sequence_audit_result_v0_1` | learner-state audit | sequence audit | audit module/fixtures | no-oracle audit summary |
| `learner_state_sequence_manifest_v0.1`, `learner_state_sequence_manifest_v0_1` | sequence exporter | sequence exporter | exporter module/fixtures | separated outputs |
| `learner_state_estimator_input_validation_v0.1`, `learner_state_estimator_input_validation_result_v0.1` | estimator input | estimator input validator | validator module/fixtures | no estimator correctness claim |
| `learner_state_selective_prediction_validation_v0.1` | selective prediction | selective prediction validator | validator module/fixtures | no ECE/AURCC claim |
| `frozen_selective_prediction_policy_schema_v0_1`, `learner_state_frozen_policy_validation_v0.1` | frozen policy | frozen policy validator | module/docs/fixtures | no test tuning |
| `frozen_policy_generation_request_schema_v0_1`, `frozen_policy_generation_input_pointer_schema_v0_1`, `learner_state_frozen_policy_generation_validation_v0.1` | frozen policy generation | generation validator | generation modules/fixtures | no generated policy body |
| `frozen_policy_generation_scaffold_request_schema_v0_1`, `frozen_policy_generation_scaffold_pointer_schema_v0_1`, `frozen_policy_generation_scaffold_result_schema_v0_1`, `frozen_policy_generation_scaffold_runtime_schema_v0_1` | scaffold | scaffold validator/runtime | scaffold modules/fixtures | metadata-only runtime |
| `frozen_policy_generation_generator_scaffold_result_v0.1`, `learner_state_frozen_policy_generation_generator_scaffold_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_generator_scaffold_result_v0.1` | generator scaffold | generator scaffold | generator modules/fixtures | generated body suppressed |
| `learner_state_frozen_policy_generation_artifact_writer_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_result_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_expected_result_v0.1`, `artifact_writer_result_pointer_v0.1` | artifact writer | artifact writer | writer modules/fixtures | metadata-only artifact result |
| `learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_result_v0.1` | artifact writer CLI integration fixture | CLI integration validator | validator/fixtures/docs | static fixture validation |
| `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_result_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_*_v0.2` fixture metadata family | artifact writer CLI integration runtime fixture | runtime fixture validator plus Step509 fixture root update and Step511 v0.2 validator support | validator/fixtures/tests/docs | static fixture validation; no runtime actual invocation correctness claim |
| `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2` | artifact writer CLI integration runtime | runtime module/tests/docs | implementation/tests/docs | v0.1 plan-only remains default; v0.2 supports explicit `actual_invocation_metadata_only` public-safe summaries with no file writing, no artifact body generation integration, and no manifest writer integration |
| `learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_body_generation_integration_*_v0.1` fixture metadata family | artifact body generation integration fixture root and validator | Step523 fixture root plus Step525 validator module/CLI/tests, Step527 standalone Makefile target, and Step529 wrapper check | fixture JSON/docs/Python/Makefile/wrapper | synthetic metadata-only bridge fixture validation; 28 cases / 196 JSON; wrapper label `release_quality_check: learner-state frozen policy generation artifact body generation integration fixture validation`; no artifact body generation integration correctness claim |
| `learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_body_result_v0.1`, `learner_state_frozen_policy_generation_artifact_body_expected_result_v0.1`, `learner_state_frozen_policy_generation_artifact_body_generation_result_v0.1` | artifact body | artifact body module/fixtures | body modules/fixtures/docs | body payload suppressed |
| `learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_body_file_write_expected_result_v0.1`, `file_writing_fixture_validation_v0.1`, `file_writing_expected_result_v0.1` | artifact body file writing | artifact body file-writing validator | validator/fixtures/docs | safe-root and no body payload |
| `learner_state_frozen_policy_generation_artifact_body_isolated_write_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_body_isolated_write_expected_result_v0.1`, `isolated_write_validation_v0.1`, `isolated_write_expected_result_v0.1` | artifact body isolated write | isolated write validator | validator/fixtures/docs | residue checks |
| `learner_state_frozen_policy_generation_manifest_writer_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_expected_result_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_metadata_only_manifest_v0.1` | manifest writer | manifest writer | manifest modules/fixtures/docs | no manifest body |
| `learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_runtime_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_runtime_expected_result_v0.1` | manifest writer runtime | runtime fixture/smoke | runtime modules/fixtures/docs | metadata-only runtime |
| `learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_file_writing_expected_result_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_file_writing_request_v0.1` | manifest writer file writing | file-writing validator | validator/fixtures/docs | safe-root file writing |
| `learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_isolated_write_expected_result_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_isolated_write_request_v0.1` | manifest writer isolated write | isolated validator | validator/fixtures/docs | residue checks |
| `learner_state_frozen_policy_generation_manifest_writer_production_file_writing_validation_v0.1`, `learner_state_frozen_policy_generation_manifest_writer_production_file_writing_expected_result_v0.1`, `production_file_writing_validation_v0.1`, `production_file_writing_expected_result_v0.1` | manifest writer production file-writing fixtures | production-shaped validator | validator/fixtures/docs | not production readiness |

### Synthetic Invalid Markers And Reason-Code Markers

Repository scans also find synthetic invalid-case marker names, unknown-schema
sentinels, and reason-code-like identifiers. Examples include unknown version
sentinels, leakage markers, path-safety markers, and expected-failure marker
names in fixture metadata. These are not stable public schema contracts. They
exist to exercise validator fail-closed or usage-error behavior while keeping
fixtures synthetic-only and body-free.

The full specification should keep this separation:

- stable schema/result/validation names describe component contracts
- fixture schema names describe fixture metadata and expected summaries
- synthetic invalid markers describe controlled negative cases
- reason-code markers describe expected validation failures

## Appendix D. Fixture Root Counts Catalogue

Step-pretec-doc4 adds this appendix to close the medium-priority fixture count
gap. Counts are derived from fixture root layout by counting case directories
and JSON files only. Fixture JSON bodies are not copied.

| Fixture root | Purpose | Cases | Valid / invalid | JSON files | JSON files per case | Validator / Makefile relation | Release-quality inclusion | Safety note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/fixtures/synthetic/` | synthetic raw/scoring/config/safe-view fixtures | not yet confirmed from repository scan | mixed subroots | 11 JSON, 32 JSONL observed | mixed | Rust/Python scripts and scoring checks | used by CI/wrapper scripts | synthetic-only; no body examples here |
| `tests/fixtures/learner_state_sequence_audit/` | sequence audit fixtures | 9 | 1 / 8 | 2 | mixed | `sequence_audit`, audit target | included | no raw rows |
| `tests/fixtures/learner_state_sequence_exporter/` | sequence exporter fixtures | 7 | 2 / 5 | 28 | 4 | `sequence_exporter`, exporter target | included | controlled export outputs |
| `tests/fixtures/learner_state_estimator_input/` | estimator input validation fixtures | 9 | 1 / 8 | 18 | 2 | `estimator_input`, estimator target | included | no estimator correctness claim |
| `tests/fixtures/learner_state_selective_prediction/` | selective prediction validation fixtures | 8 | 1 / 7 | 24 | 3 | `selective_prediction_validation`, selective target | included | no metric achievement |
| `tests/fixtures/learner_state_frozen_selective_prediction_policy/` | frozen policy fixtures | 12 | 1 / 11 | 24 | 2 | `frozen_policy_validation`, frozen policy target | included | no test tuning |
| `tests/fixtures/learner_state_frozen_policy_generation/` | frozen policy generation fixtures | 13 | 3 / 10 | 52 | 4 | `frozen_policy_generation_validation`, generation target | included | no generated policy body |
| `tests/fixtures/learner_state_frozen_policy_generation_scaffold/` | scaffold fixture validation | 11 | 3 / 8 | 33 | 3 | scaffold fixture validator/target | included | metadata-only |
| `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/` | generator scaffold fixtures | 18 | 3 / 15 | 54 | 3 | generator fixture validator/target | included | body suppressed |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/` | artifact writer fixtures | 17 | 3 / 14 | 51 | 3 | artifact writer fixture validator/target | included | artifact body suppressed |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/` | artifact writer CLI integration fixtures | 28 | 6 / 22 | 168 | 6 | CLI integration fixture validator/target | included | static fixture contract only |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/` | future runtime fixture validation | 54 | 12 / 42 | 324 | 6 | runtime fixture validator v0.2 support/Makefile target | release-quality static validation | supports mixed v0.1 plan-only and v0.2 actual-invocation metadata-only fixture validation; no runtime actual invocation correctness claim |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/` | artifact writer CLI actual invocation fixture validation | 32 | 6 / 26 | 192 | 6 | Step500 validator module/CLI, focused tests, Step502 Makefile target, and Step504 wrapper check | release-quality static validation | metadata-only/body-free sentinel fixtures; no actual invocation correctness claim |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/` | artifact body generation integration fixture root | 28 | 6 / 22 | 196 | 7 | Step525 validator module/CLI/focused tests plus Step527 standalone fixture target and Step537 selected-case runtime target `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`; schema `learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validation_v0.1` and runtime schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1` | Step529 wrapper check covers static fixture validation; Step539 wrapper check covers the selected-case runtime target after static integration fixture validation | metadata-only sentinel fixtures connecting runtime summary metadata to artifact body boundary metadata; pass 6 / usage_error 1 / fail_closed 20 / mismatch 1; runtime target uses selected valid case only; no artifact body generation integration correctness claim |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body/` | artifact body fixtures | 18 | 4 / 14 | 54 | 3 | artifact body fixture validator/target | included | body payload suppressed |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/` | artifact body file-writing fixtures | 29 | 5 / 24 | 116 | 4 | file-writing fixture validator/target | included | safe-root policy |
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/` | artifact body isolated write fixtures | 22 | 5 / 17 | 110 | 5 | isolated write validator/target | included | residue checks |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/` | manifest writer fixtures | 30 | 5 / 25 | 150 | 5 | manifest writer fixture validator/target | included | no manifest body |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/` | manifest writer runtime fixtures | 31 | 5 / 26 | 155 | 5 | runtime fixture validator/target | included | metadata-only runtime |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/` | manifest writer file-writing fixtures | 39 | 6 / 33 | 195 | 5 | file-writing fixture validator/target | included | safe-root output |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/` | manifest writer isolated write fixtures | 25 | 6 / 19 | 150 | 6 | isolated write validator/target | included | residue checks |
| `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing/` | production-shaped manifest writer file-writing fixtures | 32 | 8 / 24 | 160 | 5 | production file-writing validator/target | included | not production readiness |

## Appendix E. Remaining Low-Priority Gaps And External Review Checklist

The medium gaps from Step-pretec-doc3 are addressed by Appendices A-D. Low
priority gaps are reduced at external-review summary level by Appendices F-I
and the standalone external review checklist. This appendix does not claim
absolute coverage or external-review completion.

### Remaining Low-Priority Gaps

| Gap | Status after Step-pretec-doc5 | Suggested follow-up |
| --- | --- | --- |
| Dependency/version tables | reduced by Appendix F | External reviewer may request deeper dependency tables without lockfile body copying. |
| Per-status-marker index | reduced by Appendix G | External reviewer may request more status-marker metadata, still without raw logs. |
| Rust crate API details | reduced by Appendix H | External reviewer may request crate-level API detail from source/README evidence only. |
| Logger-web UI behavior | reduced by Appendix I | External reviewer may request UI interaction details without raw event payload examples. |
| Exact workflow action versions | reduced by Appendix F | External reviewer may request a more granular workflow action matrix from YAML. |

### External Review Checklist

- Confirm the appendix data still matches `Makefile`, Python parser sources,
  fixture root layout, and schema/version scans.
- Confirm no JSON body examples, fixture bodies, request bodies, pointer
  bodies, expected bodies, written file bodies, manifest bodies, artifact body
  payloads, generated policy bodies, raw rows, logits/probabilities, private
  path values, absolute local path values, raw learner text, or raw logs are
  copied into public docs.
- Confirm artifact writer CLI integration runtime remains marked as an
  initial metadata-only runtime with a release-quality smoke target, not
  artifact writer CLI actual invocation proof or production readiness proof.
- Confirm artifact body generation CLI integration, manifest writer
  integration, and manifest body generation remain marked not implemented
  where appropriate.
- Confirm production readiness, real-data readiness, model performance, F1,
  accuracy, ECE, and AURCC are not claimed.
- Confirm future external-review-ready versions still cite evidence paths and
  mark unknowns as `not yet confirmed from repository scan` or
  `next step verification required`.

## Appendix F. Dependency, Runtime, Package, And Workflow Version Catalogue

Step-pretec-doc5 adds this appendix to reduce the dependency/version and
workflow-action low-priority gaps from Step-pretec-doc3. It is based on
repository files only: `.github/workflows/ci.yml`,
`.github/workflows/release-quality.yml`, `Cargo.toml`,
`crates/*/Cargo.toml`, and `apps/logger-web/package.json`. It does not copy
lockfile bodies or raw workflow logs.

### Runtime And Workflow Setup

| Area | Repository evidence | Confirmed value or version | Use in repository | Review note |
| --- | --- | --- | --- | --- |
| CI workflow runner | `.github/workflows/ci.yml` | `ubuntu-latest` | Rust workspace checks, synthetic policy, Rust CLI smoke, synthetic E2E smoke | Runner image resolution is controlled by GitHub Actions and is not pinned in the workflow file. |
| Release Quality runner | `.github/workflows/release-quality.yml` | `ubuntu-latest` | Release-quality wrapper | Runner image resolution is controlled by GitHub Actions and is not pinned in the workflow file. |
| Python setup | `.github/workflows/release-quality.yml` | `actions/setup-python@v6`, `python-version: "3.11"` | Release-quality Python checks and validators | Exact patch version comes from the runner/tool cache and is not fixed in the workflow file. |
| Rust toolchain | both workflow files | `dtolnay/rust-toolchain@stable`, components `rustfmt`, `clippy` | Cargo format, tests, clippy | Stable channel is used; exact compiler patch version is not fixed in workflow YAML. |
| Node setup | `.github/workflows/release-quality.yml` | `actions/setup-node@v6`, `node-version: "22"` | logger-web npm checks | Exact patch version comes from setup-node resolution and is not fixed in workflow YAML. |
| npm cache | `.github/workflows/release-quality.yml` | cache `npm`, cache dependency path `apps/logger-web/package-lock.json` | logger-web dependency install | Lockfile body is not reproduced in this specification. |
| checkout action | both workflow files | `actions/checkout@v7` | source checkout | Version is confirmed from workflow YAML. |

### Cargo Workspace And Rust Crate Dependencies

| Package or workspace | Evidence path | Confirmed package metadata | Dependency summary | Review note |
| --- | --- | --- | --- | --- |
| Cargo workspace | `Cargo.toml` | resolver `2`, workspace edition `2021` | members are the seven `kslog_*` crates | Workspace package version policy beyond edition is not separately specified. |
| `kslog_schema` | `crates/kslog_schema/Cargo.toml` | version `0.1.0` | `serde` with derive; dev `serde_json` | Shared schema types for synthetic logs. |
| `kslog_validate` | `crates/kslog_validate/Cargo.toml` | version `0.1.0` | `kslog_schema`, `serde_json` | Deterministic JSONL validation. |
| `kslog_replay` | `crates/kslog_replay/Cargo.toml` | version `0.1.0` | `kslog_schema`; dev `kslog_validate`, `serde_json` | Deterministic replay over validated synthetic events. |
| `kslog_extract` | `crates/kslog_extract/Cargo.toml` | version `0.1.0` | `kslog_schema`, `kslog_replay`; dev `kslog_validate`, `serde_json` | Revision-event extraction. |
| `kslog_micro_episode` | `crates/kslog_micro_episode/Cargo.toml` | version `0.1.0` | `kslog_extract`, `kslog_schema`, `serde`; dev `kslog_validate`, `serde_json` | Micro-episode construction. |
| `kslog_no_oracle_audit` | `crates/kslog_no_oracle_audit/Cargo.toml` | version `0.1.0` | `kslog_extract`, `kslog_micro_episode`, `kslog_schema`, `serde`; dev `kslog_validate`, `serde_json` | No-oracle checks and safe-view boundaries. |
| `kslog_cli` | `crates/kslog_cli/Cargo.toml` | version `0.1.0`, binary `kslog` | all Rust pipeline crates plus `serde_json` | CLI wrapper for deterministic synthetic checks. |

### Logger-Web Package Metadata

| Area | Evidence path | Confirmed value | Purpose | Review note |
| --- | --- | --- | --- | --- |
| package name | `apps/logger-web/package.json` | `kslog-logger-web` | browser logger package | Package is private. |
| package version | `apps/logger-web/package.json` | `0.1.0` | package metadata | Not a public release version claim. |
| dev server script | `apps/logger-web/package.json` | `npm run dev` -> `vite --host 127.0.0.1` | local synthetic logger dev server | Local development only. |
| build script | `apps/logger-web/package.json` | `npm run build` -> `vite build` | production-style bundle build check | Build success is not deployment readiness. |
| typecheck script | `apps/logger-web/package.json` | `npm run typecheck` -> `tsc --noEmit` | TypeScript check | Included in `make check-logger`. |
| test script | `apps/logger-web/package.json` | `npm test` -> TypeScript test compile and Node raw event test | raw event helper tests | Included in `make check-logger`. |
| TypeScript dependency | `apps/logger-web/package.json` | `typescript` declared as `^5.6.3` | TypeScript compilation | Exact installed resolution is determined by lockfile, not copied here. |
| Vite dependency | `apps/logger-web/package.json` | `vite` declared as `^8.0.16` | dev server and build | Exact installed resolution is determined by lockfile, not copied here. |

## Appendix G. Status Marker Index

Step-pretec-doc5 adds this index to reduce the per-status-marker low-priority
gap. The index lists marker paths and public-safe interpretation only. It does
not copy run logs, full job output, fixture JSON bodies, or raw workflow
payloads.

| Marker path | Related component | Status type | Raw logs stored | What it proves | What it does not prove |
| --- | --- | --- | --- | --- | --- |
| `docs/status/milestone_04_status.md` | Milestone 04 docs-only release review | milestone marker | no | Public-safe milestone status was recorded. | Does not prove production or real-data readiness. |
| `docs/status/milestone_05_status.md` | Milestone 05 Makefile orchestration | milestone marker | no | Public-safe milestone status was recorded. | Does not prove production or real-data readiness. |
| `docs/status/learner_state_audit_release_quality_remote_run_status.md` | learner-state audit | remote/manual run marker | no | Release-quality inclusion/status was recorded safely. | Does not prove learner-state estimator correctness. |
| `docs/status/learner_state_exporter_release_quality_remote_run_status.md` | learner-state exporter | remote/manual run marker | no | Exporter check status was recorded safely. | Does not prove real-data export readiness. |
| `docs/status/learner_state_estimator_input_release_quality_remote_run_status.md` | estimator input | remote/manual run marker | no | Estimator input validation status was recorded safely. | Does not prove estimator model correctness. |
| `docs/status/learner_state_selective_prediction_release_quality_remote_run_status.md` | selective prediction | remote/manual run marker | no | Selective prediction validation status was recorded safely. | Does not prove model performance, ECE, or AURCC. |
| `docs/status/learner_state_frozen_policy_release_quality_remote_run_status.md` | frozen policy validation | remote/manual run marker | no | Frozen policy validation status was recorded safely. | Does not prove policy quality. |
| `docs/status/learner_state_frozen_policy_generation_release_quality_remote_run_status.md` | frozen policy generation validation | remote/manual run marker | no | Generation validation status was recorded safely. | Does not prove generated policy quality. |
| `docs/status/learner_state_frozen_policy_generation_scaffold_fixture_release_quality_remote_run_status.md` | scaffold fixture validation | remote/manual run marker | no | Fixture validation inclusion/status was recorded safely. | Does not prove runtime generation correctness. |
| `docs/status/learner_state_frozen_policy_generation_scaffold_runtime_release_quality_remote_run_status.md` | scaffold runtime smoke | remote/manual run marker | no | Metadata-only runtime smoke inclusion/status was recorded safely. | Does not prove production runtime readiness. |
| `docs/status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md` | generator scaffold fixture validation | remote/manual run marker | no | Fixture validation inclusion/status was recorded safely. | Does not prove generated policy body correctness. |
| `docs/status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md` | generator scaffold runtime smoke | remote/manual run marker | no | Metadata-only runtime smoke inclusion/status was recorded safely. | Does not prove artifact body or manifest integration. |
| `docs/status/learner_state_frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_status.md` | artifact writer fixture validation | remote/manual run marker | no | Artifact writer fixture validation status was recorded safely. | Does not prove CLI integration runtime correctness. |
| `docs/status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md` | artifact writer runtime smoke | remote/manual run marker | no | Metadata-only artifact writer smoke status was recorded safely. | Does not prove artifact body generation integration. |
| `docs/status/learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_remote_run_status.md` | artifact writer CLI integration fixture validation | remote/manual run marker | no | CLI integration fixture validation status was recorded safely. | Does not prove artifact writer CLI integration runtime correctness. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md` | artifact body fixture validation | remote/manual run marker | no | Artifact body fixture validation status was recorded safely. | Does not prove artifact body payload quality. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_generation_release_quality_remote_run_status.md` | artifact body generation suppressed smoke | remote/manual run marker | no | Suppressed smoke status was recorded safely. | Does not prove artifact body generation integration correctness. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md` | artifact body safe-metadata smoke | remote/manual run marker | no | Safe-metadata smoke status was recorded safely. | Does not prove production artifact body writing readiness. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md` | artifact body file-writing fixtures | remote/manual run marker | no | File-writing fixture validation status was recorded safely. | Does not prove production file-writing readiness. |
| `docs/status/learner_state_frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_status.md` | artifact body isolated write validation | remote/manual run marker | no | Isolated write validation status was recorded safely. | Does not prove production output readiness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md` | manifest writer fixture validation | remote/manual run marker | no | Manifest writer fixture validation status was recorded safely. | Does not prove manifest writer integration correctness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md` | manifest writer runtime smoke | remote/manual run marker | no | Runtime smoke status was recorded safely. | Does not prove production manifest readiness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md` | manifest writer runtime fixture validation | remote/manual run marker | no | Runtime fixture validation status was recorded safely. | Does not prove manifest body generation. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md` | manifest writer file-writing fixtures | remote/manual run marker | no | File-writing fixture validation status was recorded safely. | Does not prove production readiness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_status.md` | manifest writer isolated write validation | remote/manual run marker | no | Isolated write validation status was recorded safely. | Does not prove production file-writing readiness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_status.md` | production-shaped manifest writer file-writing fixtures | remote/manual run marker | no | Production-shaped fixture validation status was recorded safely. | Does not prove production readiness. |
| `docs/status/learner_state_frozen_policy_generation_manifest_writer_runtime_file_writing_release_quality_remote_run_status.md` | manifest writer runtime file-writing smoke | remote/manual run marker | no | Runtime file-writing smoke status was recorded safely. | Does not prove production data collection validity. |

## Appendix H. Rust Crate API Review Notes

Step-pretec-doc5 adds these review notes to reduce the Rust crate API
low-priority gap. The table uses confirmed crate names, descriptions,
dependencies, README scope, and test/build commands. It does not reproduce Rust
source bodies or infer unconfirmed API signatures.

| Crate | Role | Public-facing behavior confirmed from repository | Tests/check relation | No-oracle / safe-view relation | Non-claim |
| --- | --- | --- | --- | --- | --- |
| `kslog_schema` | shared synthetic raw event schema types | Deserializes and serializes synthetic raw event structures used by the Rust pipeline. | covered by `cargo test --workspace` and `check-rust` | rejects no-oracle forbidden unknown fields in tests | Not a real-data schema approval. |
| `kslog_validate` | deterministic JSONL validation | Validates synthetic raw event JSONL and rejects malformed or unsafe sequences. | covered by Rust tests and CLI validation smoke | includes forbidden no-oracle field checks | Not legal/privacy readiness. |
| `kslog_replay` | deterministic replay | Replays validated synthetic events and exposes safe diagnostics behavior. | covered by Rust tests and CLI replay/diagnose commands | diagnostics suppress content and emphasize counts/metadata | Not proof that replay handles all real-world inputs. |
| `kslog_extract` | revision-event extraction | Extracts revision-event summaries from validated synthetic event sequences. | covered by Rust tests and CLI extract command | downstream input to no-oracle audited views | Not a complete linguistic revision model. |
| `kslog_micro_episode` | micro-episode construction | Builds synthetic micro-episodes from revision events with deterministic IDs and local context policies. | covered by Rust tests and CLI build command | feeds no-oracle audit and safe-view creation | Not learner-state estimator correctness. |
| `kslog_no_oracle_audit` | no-oracle audit and safe-view field boundaries | Defines forbidden field sets and safe-view field boundaries used for candidate-generation safety. | covered by Rust tests and CLI audit/make-safe-view/export-safe-view commands | central no-oracle / safe-view component | Not a guarantee that every future task is leakage-free. |
| `kslog_cli` | Rust command-line wrapper | Provides `kslog` commands for validate, replay, diagnostics, extraction, micro-episode construction, no-oracle audit, safe view, and safe-view export. | covered by Rust tests, CI smoke, and `check-rust` | summaries suppress final text and unsafe context by default | Not production or real-data readiness. |

## Appendix I. Logger-Web UI Behavior And External Review Notes

Step-pretec-doc5 adds this summary to reduce the logger-web UI behavior
low-priority gap. It is based on `apps/logger-web/README.md`,
`apps/logger-web/package.json`, `apps/logger-web/src/`, and
`apps/logger-web/tests/`. It does not copy raw event JSONL or user text.

| Area | Confirmed behavior | Evidence path | Review note |
| --- | --- | --- | --- |
| Framework/runtime | Vite + TypeScript browser app with npm scripts for dev, build, typecheck, and tests | `apps/logger-web/package.json`, `apps/logger-web/vite.config.ts` | Local app checks do not prove deployment readiness. |
| UI surface | Minimal page with one writing textarea, event summary elements, download button, and clear button | `apps/logger-web/src/main.ts`, `apps/logger-web/README.md` | UI behavior is summarized, not exhaustively specified. |
| Event construction | Uses TypeScript raw event helpers to build synthetic raw event records and JSONL output | `apps/logger-web/src/rawEvent.ts`, `apps/logger-web/tests/rawEvent.test.ts` | Raw event bodies are not copied into docs. |
| Browser event handling | Handles before/input/composition/selection/mouse/key-related snapshots for synthetic sessions | `apps/logger-web/src/main.ts` | This is not privacy or real participant readiness. |
| Download behavior | In-memory synthetic events can be downloaded as JSONL | `apps/logger-web/README.md`, `apps/logger-web/src/main.ts` | Downloaded files must not be committed if they contain real or private data. |
| Storage/network posture | README states no server send, no localStorage, and no console logging of text or JSONL | `apps/logger-web/README.md` | External review should confirm this remains true after future UI changes. |
| Checks | `npm run typecheck`, `npm test`, and `npm run build` are wired through `make check-logger` | `apps/logger-web/package.json`, `Makefile` | Build/test success is not production deployment evidence. |

## Appendix J. External Review Checklist Link

The standalone external review checklist is
`docs/full_technical_specification_external_review_checklist.md`. Reviewers
should use it with this specification, the source inventory, and the coverage
validation report. The checklist is a review aid, not a production readiness,
real-data readiness, or model-performance certification.

The final safety and non-proof review is
`docs/full_technical_specification_final_safety_review.md`. It records that
the documentation set is an external-review-ready draft with caveats, not a
guarantee of no omissions and not a production, real-data, model-performance,
or external-approval claim.

## Appendix K. Step547 Planned Safe-Metadata Fixture Root Update

Step547 adds a planned safe-metadata v0.2 fixture root at
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`.
The planned root contains metadata-only / body-free safe-metadata runtime
integration fixture cases using the seven-file layout. It is intentionally
outside the active Step523 fixture root so the existing static validator and
release-quality wrapper remain unchanged until a later validator update step.

The planned taxonomy adds four valid cases and twenty invalid cases for a
future `safe-metadata-smoke` runtime mode and future runtime schema v0.2.
Validator update, runtime implementation, Makefile integration,
release-quality wrapper integration, workflow updates, artifact body
generation runtime invocation, manifest writer integration, and file writing
are not implemented in Step547. This addition does not prove production
readiness, real-data readiness, model performance, artifact body generation
correctness generally, runtime correctness generally, manifest writer
integration correctness, generated policy quality, learner-state estimator
correctness, or safe-metadata free-form body safety.

## Appendix L. Step549 Safe-Metadata v0.2 Fixture Validator Implementation

Step549 adds
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`
and focused tests for the planned safe-metadata v0.2 fixture root. The CLI is:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2`

The validator uses schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`,
output mode `safe_metadata_fixture_validation`, and validates the planned root
as 24 cases / 168 JSON files: 4 pass cases, 1 usage-error case, 18
fail-closed cases, and 1 mismatch case. It remains separate from the active
28-case validator. Step551 adds a standalone Makefile target, and Step553 adds
release-quality wrapper integration for that target.

Step549 does not implement safe-metadata runtime behavior, invoke artifact body
generation runtime, invoke manifest writer integration, write files, change
fixture JSON, or claim production readiness, real-data readiness, model
performance, runtime correctness generally, manifest writer correctness, or
safe-metadata free-form body safety.

## Appendix M. Step551 Safe-Metadata v0.2 Fixture Validator Makefile Target

Step551 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`
for the Step549 planned-root validator CLI. The target runs:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2`

The expected public-safe aggregate remains 24 cases / 168 JSON files with 4
pass cases, 1 usage-error case, 18 fail-closed cases, and 1 mismatch case.
The target is separate from the active 28-case validator target. Step553 adds
the release-quality wrapper label
`release_quality_check: learner-state frozen policy generation artifact body generation runtime integration safe-metadata v0.2 fixture validation`
and command
`make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`
after the plan-only bridge smoke and before artifact body fixture validation.

Step553 does not change workflow files, Makefile, Python code/tests, fixture
JSON, validator implementation, runtime implementation, artifact body
generation runtime invocation, manifest writer integration, or file writing.

## Appendix N. Step559 Safe-Metadata Runtime Implementation

Step559 adds `safe-metadata-smoke` to
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
as a metadata handoff only runtime mode. The mode reads the planned
safe-metadata v0.2 primary case
`valid/valid_safe_metadata_explicit_runtime_bridge` from
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`
and emits runtime schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`.

The output surface is public-safe, metadata-only, body-free, and count-only.
It records safety flags, safe metadata availability/count fields, no artifact
body generation runtime invocation, no manifest writer invocation, and no file
writing. Unsafe body, payload, raw-output, path, data, performance,
file-writing, and manifest-writer markers fail closed. Missing or unsupported
inputs return usage-error summaries, and expected-status mismatches return
mismatch summaries.

Step559 updates focused runtime tests but does not add a Makefile target,
release-quality wrapper integration, workflow changes, fixture JSON changes,
artifact body generation implementation, manifest writer integration, file
writing, real-data use, metric use, or production readiness status.

## Appendix O. Step561 Safe-Metadata Runtime Makefile Target

Step561 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
for the Step559 `safe-metadata-smoke` runtime CLI. The target command runs the
planned safe-metadata v0.2 primary case
`valid/valid_safe_metadata_explicit_runtime_bridge` and emits schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
with public-safe metadata-only / body-free / count-only summary output.

Step563 adds the standalone target to the release-quality wrapper with label
`release_quality_check: learner-state frozen policy generation artifact body generation runtime integration safe-metadata runtime smoke`.
The wrapper check runs after safe-metadata v0.2 fixture validation and before
artifact body fixture validation.

The check remains metadata handoff only. Step563 does not change workflow
files, Makefile, Python code/tests, fixture JSON, runtime implementation,
validator implementation, artifact body generation implementation, manifest
writer integration, file writing, real-data use, metric use, or production
readiness status.

## Appendix P. Step570 Runtime Invocation Fixture Root

Step570 creates the planned fixture root
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/`
from the Step569 contract. The root contains 6 valid cases, 24 invalid cases,
30 total cases, 7 metadata-only / body-free JSON files per case, and 210 total
JSON files.

The fixture schema is
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_v0.1`.
The planned validation schema is
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`,
and the proposed mode is `artifact-body-runtime-invocation`.

Step570 creates fixture JSON and the fixture README only. It does not add a
validator, runtime implementation, Makefile target, release-quality wrapper
integration, workflow change, artifact body generation runtime invocation,
manifest writer integration, file writing, real-data use, metric use,
production readiness, real-data readiness, model performance evidence, or
safe-metadata free-form body safety evidence.

Step579 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
for the Step577 planned-only v0.3 direct CLI. The target uses the same primary
fixture case, runtime schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`,
and public-safe metadata-only / body-free output policy. It is not connected
to the release-quality wrapper and does not perform actual artifact body
generation runtime invocation, invoke manifest writer, write files, use real
data, compute metrics, or provide production readiness, real-data readiness,
model performance, runtime correctness generally, artifact body generation
correctness generally, or safe-metadata free-form body safety evidence.

Step572 adds the standalone validator module
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`
and focused tests. The CLI emits mode
`artifact_body_generation_runtime_invocation_fixture_validation` with schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
and validates the Step570 fixture root as 30 cases / 210 JSON files with 6
pass, 1 usage-error, 22 fail-closed, and 1 mismatch case.

Step574 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
for the Step572 validator CLI. The target runs the Step570 root and preserves
the public-safe aggregate of 30 cases / 210 JSON files with 6 pass, 1
usage-error, 22 fail-closed, and 1 mismatch case.

Step574 does not add release-quality wrapper integration, workflow change,
runtime implementation, actual artifact body generation runtime invocation,
manifest writer integration, file writing, real-data use, metric use,
production readiness, real-data readiness, model performance evidence, or
safe-metadata free-form body safety evidence.

Step577 adds planned-only v0.3 `artifact-body-runtime-invocation` support to
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`.
The selected primary fixture case is
`valid/valid_minimal_safe_metadata_runtime_invocation`, and the runtime schema
is
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`.

The Step577 CLI output remains public-safe, metadata-only, body-free, and
count-only where applicable. It records `artifact_body_runtime_invocation_planned`
as true and `artifact_body_runtime_invoked` as false, keeps manifest writer
invocation false, and keeps file writing disabled. Step577 adds focused tests
for pass, usage-error, fail-closed, mismatch, public-safe output, no residue,
and existing mode compatibility. It does not add Makefile targets,
release-quality wrapper integration, workflow changes, fixture JSON changes,
validator changes, actual artifact body generation runtime invocation,
manifest writer integration, file writing, real-data use, metric use,
production readiness, real-data readiness, model performance evidence, or
safe-metadata free-form body safety evidence.

## Appendix Q. Step587 Actual-Controlled Runtime Invocation Fixture Root

Step587 creates the fixture root `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/` for a future v0.4 actual-controlled artifact body generation runtime invocation chain. The root contains 6 valid cases, 30 invalid cases, 36 total cases, 7 parseable metadata-only JSON files per case, and 252 total JSON files. The fixture schema is `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_v0.1`; the validation schema is `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`; the future runtime schema is `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`; and the future integration mode is `artifact-body-runtime-invocation-controlled`. Step587 does not implement a validator, runtime invocation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, or safe-metadata free-form body safety evidence.


## Appendix R. Step589 Actual-Controlled Fixture Validator Implementation

Step589 adds a standalone validator module for the Step587 actual-controlled fixture root: `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`. The CLI mode is `artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation`, with validation schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`. It validates the 36-case / 252-JSON root, exact 7-file layout, case taxonomy, expected status/reason classes, metadata marker cases, and physical mutation input-error behavior through focused tests. It does not add Makefile integration, release-quality integration, runtime implementation, actual artifact body generation runtime invocation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, or artifact body payload correctness evidence.

## Appendix S. Step591 Actual-Controlled Fixture Validator Makefile Target

Step591 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures` for the Step589 validator. The target runs `python -m learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation` over the Step587 fixture root and keeps the expected aggregate at 36 cases / 252 JSON, 6 pass, 3 usage-error, 26 fail-closed, and 1 mismatch case. This is standalone target integration only; release-quality wrapper integration, workflow changes, runtime implementation, actual artifact body generation runtime invocation, manifest writer integration, file writing, production readiness, real-data readiness, and model performance evidence remain out of scope.

## Appendix T. Step593 Actual-Controlled Runtime Invocation Implementation

Step593 extends `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py` with runtime schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`, mode `artifact-body-runtime-invocation-controlled`, and the `--actual-invocation` flag. The selected Step587 primary case is `valid/valid_actual_controlled_safe_metadata_invocation`. The implementation invokes the existing safe-metadata artifact body generation CLI in a controlled metadata-only path, scans public key-value summary output, suppresses raw stdout/stderr bodies, and emits only public-safe runtime summary fields. It does not change Makefile, release-quality wrapper, workflows, fixture JSON, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, or safe-metadata free-form body safety evidence.

## Appendix U. Step595 Actual-Controlled Runtime Invocation Makefile Target

Step595 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation` for the Step593 v0.4 runtime CLI. The target runs the selected Step587 primary case with runtime schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` and mode `artifact-body-runtime-invocation-controlled`, expects public-safe summary output with `artifact_body_runtime_invoked=True` and `safe_metadata_body_field_count=5`, remains outside release-quality, does not invoke manifest writer, does not write files, and does not provide production readiness, real-data readiness, or model performance evidence.

## Appendix V. Step597 Actual-Controlled Runtime Invocation Release-Quality Integration

Step597 adds two release-quality wrapper checks to `scripts/check_release_quality.sh`: `learner-state frozen policy generation actual-controlled artifact body generation runtime invocation fixture validation` followed by `learner-state frozen policy generation actual-controlled artifact body generation runtime invocation smoke`. The first runs the Step591 target with expected aggregate 36 cases / 252 JSON, 6 pass, 3 usage-error, 26 fail-closed, and 1 mismatch case. The second runs the Step595 v0.4 runtime smoke with schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`, mode `artifact-body-runtime-invocation-controlled`, `artifact_body_runtime_invoked=True`, `safe_metadata_body_field_count=5`, `manifest_writer_invoked=False`, and `file_writing_enabled=False`. Step597 does not change Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, manifest writer integration, file writing, production readiness, real-data readiness, or model performance evidence.

## Appendix W. Step604 Actual-Controlled v0.4 Multi-Case Runtime Smoke

Step604 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py` and focused tests for a direct CLI-only all-valid multi-case v0.4 runtime smoke. The runner uses schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1`, discovers 6 valid cases from the Step587 root by directory name, executes them through the existing v0.4 controlled metadata-only helper, and emits aggregate public-safe key-value fields including selected/executed/pass counts, body-suppression counts, safe-metadata count-only distribution, residue count, and safety flags. Step604 does not add a Makefile target, release-quality wrapper integration, workflow changes, fixture JSON changes, manifest writer integration, file writing, production readiness, real-data readiness, or model performance evidence.

## Appendix X. Step606 Actual-Controlled v0.4 Multi-Case Runtime Smoke Makefile Target

Step606 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke` for the Step604 runner. The target runs `python -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke` with `--case-selection all-valid`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-unsafe-output`. It expects aggregate public-safe output with 6 selected / executed / pass cases, unsafe signal count 0, residue count 0, runtime schema `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`, and mode `artifact-body-runtime-invocation-controlled`. Step606 does not change release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, manifest writer integration, file writing, production readiness, real-data readiness, or model performance evidence.

## Appendix Y. Step608 Actual-Controlled v0.4 Multi-Case Runtime Smoke Release-Quality Integration

Step608 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 multi-case runtime smoke` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`, inserted after the actual-controlled v0.4 single-case runtime smoke and before artifact body fixture / CLI checks. The check runs the Step604 runner through the Step606 standalone target over the all-valid matrix with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1`, expects aggregate public-safe metadata for 6 selected / executed / pass cases with unsafe signal count 0 and residue count 0, and keeps manifest writer invocation and file writing disabled. Step608 does not change Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, production readiness, real-data readiness, or model performance evidence.

## Appendix Z. Step615 Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Smoke

Step615 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py` and focused tests for a direct CLI-only invalid-case v0.4 runtime fail-closed smoke. The runner uses schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1`, mode `actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke`, matrix `actual_controlled_v0_4_invalid_fail_closed_runtime_smoke`, and `--case-selection fail-closed-invalid`. It selects the 26 invalid fail_closed case IDs fixed by Step614, defers the 4 non-fail_closed invalid cases, executes the selected cases through the existing controlled metadata-only v0.4 helper, and emits aggregate public-safe key-value fields only. The canonical aggregate records 26 selected / executed / observed fail_closed cases, unsafe signal total 26, residue count 0, artifact body payload emitted count 0, manifest writer invocation count 0, and file-writing enabled count 0. Step615 does not add a Makefile target, release-quality wrapper integration, workflow changes, fixture JSON changes, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, or runtime correctness generally evidence.

## Appendix AA. Step617 Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Makefile Target

Step617 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke` for the Step615 runner. The target runs `python -m learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke` with `--case-selection fail-closed-invalid`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-unsafe-output`. It is placed after the all-valid multi-case target and expects aggregate public-safe output with 26 selected / executed / observed fail_closed cases, 4 deferred cases, `unsafe_signal_total_count=26`, `forbidden_body_emitted_case_count=0`, `residue_file_count=0`, artifact body payload emitted count 0, manifest writer invocation count 0, and file-writing enabled count 0. Step617 does not change release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, or runtime correctness generally evidence.

## Appendix AB. Step619 Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Release-Quality Integration

Step619 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 invalid-case runtime fail-closed smoke` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`, inserted after the actual-controlled v0.4 all-valid multi-case runtime smoke and before artifact body fixture / CLI checks. The check runs the Step615 runner through the Step617 standalone target over the fixed invalid fail_closed matrix with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1`, expects aggregate public-safe metadata for 26 selected / executed / observed fail_closed cases, 4 deferred cases, `unsafe_signal_total_count=26`, `forbidden_body_emitted_case_count=0`, and `residue_file_count=0`, and keeps manifest writer invocation and file writing disabled. `unsafe_signal_total_count=26` is expected for this invalid fail-closed smoke and is not raw body emission. Step619 does not change Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer implementation, production readiness, real-data readiness, or model performance evidence.

## Appendix AC. Step626 Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Runner

Step626 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py` and focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py`. The runner is direct CLI-only with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1`, mode `actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke`, matrix `actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke`, and `--case-selection deferred-invalid-usage-error-mismatch`.

The runner processes the 4 deferred non-fail_closed invalid cases from the Step625 contract using safe preflight / contract observation rather than requiring full runtime invocation. It uses `processed_case_count=4` as the primary count, expects 3 per-case usage_error categories and 1 per-case mismatch category, and emits aggregate public-safe key-value metadata only. The canonical aggregate records zero fail_closed cases, zero pass cases, zero payload emission, zero manifest writer invocation, zero file-writing enablement, and zero residue. Step626 does not add a Makefile target, release-quality wrapper integration, workflow changes, fixture JSON changes, payload audit implementation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, all invalid-case runtime behavior evidence, or runtime correctness generally evidence.

## Appendix AD. Step628 Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Makefile Target

Step628 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke` for the Step626 runner. The target runs `python -m learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke` with `--case-selection deferred-invalid-usage-error-mismatch`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-unsafe-output`.

The target is placed after the accepted invalid fail_closed target and before unrelated artifact body / manifest writer targets. It expects aggregate public-safe output with 4 selected / processed deferred invalid cases, 3 expected and observed usage_error categories, 1 expected and observed mismatch category, `processed_case_count=4`, zero fail_closed cases, zero pass cases, zero payload emission, zero manifest writer invocation, zero file-writing enablement, zero forbidden body emission, and zero residue. Step628 does not change release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, payload audit implementation, artifact body generation implementation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, all invalid-case runtime behavior evidence, usage_error / mismatch behavior generally evidence, or runtime correctness generally evidence.

## Appendix AE. Step630 Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Release-Quality Integration

Step630 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke`, inserted after the actual-controlled v0.4 invalid-case fail_closed smoke and before artifact body fixture / CLI checks.

The check runs the Step626 runner through the Step628 standalone target over the fixed deferred invalid usage_error / mismatch matrix with schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1`, mode `actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke`, and `processed_case_count=4`. It expects aggregate public-safe metadata for 4 selected / processed deferred invalid cases, 3 expected and observed usage_error categories, 1 expected and observed mismatch category, zero fail_closed cases, zero pass cases, zero payload emission, zero manifest writer invocation, zero file-writing enablement, zero forbidden body emission, and zero residue. Step630 does not change Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, payload audit implementation, artifact body generation implementation, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, all invalid-case runtime behavior evidence, usage_error / mismatch behavior generally evidence, or runtime correctness generally evidence.

## Appendix AF. Step638 Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Runner

Step638 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py` and focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission.py`. The runner is direct CLI-only with mode `actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission`, schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_v0.1`, matrix `actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission`, and `case_selection=payload-audit-without-payload-emission`.

The runner checks the Step636 36-case count-only metadata contract over the existing actual-controlled v0.4 fixture root. It expects 6 selected valid cases, 30 selected invalid cases, 26 fail_closed invalid cases, 4 deferred invalid cases, 6 payload-capable cases, and 30 payload-not-applicable cases. The CLI accepts `--fixture-root`, `--case-selection`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-forbidden-body`, then emits aggregate public-safe key-value metadata only.

The aggregate summary includes selected case counts, payload-capable / payload-not-applicable counts, payload availability checked counts, payload suppressed counts, payload body-free counts, expected/observed pass, fail_closed, usage_error, and mismatch counts, artifact body payload emitted count 0, generated policy body emitted count 0, manifest body emitted count 0, forbidden body emitted count 0, raw stdout/stderr suppression counts, manifest writer invocation count 0, file-writing enabled count 0, artifact/manifest file-written counts 0, residue count 0, and safety flags for content suppression, body suppression, metadata-only, synthetic-only, no-oracle, no production readiness, no real-data readiness, and no performance claims.

Step638 does not add a Makefile target, release-quality wrapper integration, workflow changes, fixture JSON changes, existing runtime implementation changes, validator implementation changes, payload body emission, artifact body payload output, generated policy body output, manifest body output, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, artifact body payload correctness evidence, artifact body payload quality evidence, safe-metadata free-form body safety evidence, or runtime correctness generally evidence.

## Appendix AG. Step640 Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Makefile Target

Step640 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission` for the Step638 direct CLI. The target runs `python -m learner_state.frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission` with `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`, `--case-selection payload-audit-without-payload-emission`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-forbidden-body`.

The target is placed after the actual-controlled v0.4 deferred invalid-case usage_error / mismatch target and before unrelated artifact body generation / manifest writer targets. It expects aggregate public-safe output for the 36-case count-only metadata contract: 6 selected valid cases, 30 selected invalid cases, 26 fail_closed invalid cases, 4 deferred invalid cases, 6 expected and observed payload-capable cases, 30 expected and observed payload-not-applicable cases, zero artifact body payload emission, zero generated policy body emission, zero manifest body emission, zero manifest writer invocation, zero file-writing enablement, and zero residue.

Step640 does not add release-quality wrapper integration, workflow changes, Python code/tests changes, fixture JSON changes, existing runtime implementation changes, validator implementation changes, payload body emission, artifact body payload output, generated policy body output, manifest body output, manifest writer integration, file writing, production readiness, real-data readiness, model performance evidence, payload correctness evidence, artifact body payload quality evidence, safe-metadata free-form body safety evidence, or runtime correctness generally evidence.

## Appendix AH. Step642 Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Release-Quality Integration

Step642 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 artifact body payload audit without payload emission` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission`, inserted after the actual-controlled v0.4 deferred invalid-case usage_error / mismatch smoke and before artifact body fixture / CLI checks.

The check runs the Step638 runner through the Step640 standalone target over the existing 36-case actual-controlled v0.4 fixture root. It expects mode `actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission`, schema `learner_state_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_v0.1`, matrix `actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission`, and `case_selection=payload-audit-without-payload-emission`. The expected aggregate remains count-only and body-free: 36 selected cases, 6 selected valid cases, 30 selected invalid cases, 26 fail_closed invalid cases, 4 deferred invalid cases, 6 expected and observed payload-capable cases, 30 expected and observed payload-not-applicable cases, `processed_case_count=36`, 6 pass cases, 3 usage_error cases, 26 fail_closed cases, 1 mismatch case, input-error count 0, zero payload body emission, zero artifact body payload output, zero generated policy body output, zero manifest body output, zero request / pointer / expected body output, raw stdout/stderr body suppression counts 36, zero manifest writer invocation, zero file-writing enablement, zero artifact/manifest files written, zero residue, and public-safe safety flags for content suppression, body suppression, metadata-only, synthetic-only, no-oracle, no production readiness claim, no real-data readiness claim, and no performance claims.

`status=pass` means the 36-case count-only metadata contract matched. It does not prove payload correctness, artifact body payload quality, free-form body safety, manifest writer readiness, file-writing readiness, runtime correctness generally, production readiness, real-data readiness, or model performance.

Step642 does not change Makefile, workflows, Python code/tests, fixture JSON, existing runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, artifact body file writing, manifest file writing, payload body emission, artifact body payload output, generated policy body output, or manifest body output.

## Appendix AI. Step650 Artifact Body to Manifest Handoff Metadata-Only No-Writer-Invocation Runner

Step650 adds `python/learner_state/frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation.py`, focused tests, and the synthetic fixture root `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`.

The runner implements a direct CLI-only check for `case_selection=artifact-body-to-manifest-handoff-metadata-only-no-writer` over the Step648 8-case body-free contract: 3 valid metadata-only cases, 5 invalid fail_closed metadata-category cases, 3 expected and observed pass cases, 5 expected and observed fail_closed cases, zero expected usage_error / mismatch cases, zero manifest writer invocation, zero manifest body generation/output, zero file writing, zero payload body emission, zero generated policy body emission, zero artifact body payload output, zero forbidden body detection, and zero residue for the canonical fixture.

Step650 does not add Makefile target integration, release-quality wrapper integration, workflow changes, existing runtime implementation changes, existing validator implementation changes, manifest writer invocation, manifest body generation, artifact or manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AJ. Step652 Artifact Body to Manifest Handoff Metadata-Only No-Writer-Invocation Makefile Target

Step652 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation` for the Step650 direct CLI. The target runs `python -m learner_state.frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation` with `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`, `--case-selection artifact-body-to-manifest-handoff-metadata-only-no-writer`, `--summary-only`, `--no-manifest-writer`, `--no-file-writing`, and `--fail-closed-on-forbidden-body`.

The target is placed after the artifact body generation safe-metadata CLI smoke and before artifact body file-writing / manifest writer checks. It expects aggregate public-safe output for the 8-case metadata-only handoff contract: 3 selected valid metadata-only cases, 5 selected invalid fail_closed metadata-category cases, 3 observed pass cases, 5 observed fail_closed cases, zero manifest writer invocation, zero manifest body generation/output, zero file writing, zero payload body emission, zero generated policy body emission, zero artifact body payload output, zero forbidden body detection, zero private / absolute path detection, zero raw learner text / real data marker detection, and zero residue.

Step652 does not add release-quality wrapper integration, workflow changes, Python code/tests changes, fixture JSON changes, existing runtime implementation changes, validator implementation changes, manifest writer invocation, manifest body generation, artifact or manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AK. Step654 Artifact Body to Manifest Handoff Metadata-Only No-Writer-Invocation Release-Quality Integration

Step654 adds `release_quality_check: learner-state frozen policy generation artifact body to manifest handoff metadata-only no-writer-invocation` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation`, inserted after artifact body generation safe-metadata CLI smoke and before artifact body file-writing / manifest writer checks.

The check runs the Step650 runner through the Step652 standalone target over the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`. It expects mode `artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation`, schema `learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_v0.1`, matrix `artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_matrix`, and `case_selection=artifact-body-to-manifest-handoff-metadata-only-no-writer`. The expected aggregate remains count-only and body-free: 8 selected / processed cases, 3 selected valid metadata-only cases, 5 selected invalid fail_closed metadata-category cases, 3 expected and observed pass cases, 5 expected and observed fail_closed cases, zero expected and observed usage_error / mismatch cases, zero manifest writer invocation, zero manifest body generation/output, zero file writing, zero payload body emission, zero generated policy body emission, zero artifact body payload output, zero request / pointer / expected body output, raw stdout/stderr body suppression counts 8, zero forbidden body detection, zero private / absolute path detection, zero raw learner text / real data marker detection, zero no-oracle forbidden field detection, and zero residue.

`status=pass` means the 8-case metadata-only handoff fixture contract matched. It does not prove manifest writer correctness, file-writing readiness, manifest body correctness, payload correctness, production readiness, real-data readiness, model performance, or any change to the Step645 local/manual fallback limitation.

Step654 does not change Makefile, workflows, Python code/tests, fixture JSON, existing runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest body generation, artifact body file writing, manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, or model performance evidence.

## Appendix AL. Step662 Manifest Writer Handoff Input Validator / Runner

Step662 adds `python/learner_state/frozen_policy_generation_manifest_writer_handoff_input_validation.py`, focused tests at `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_handoff_input_validation.py`, and the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input/`.

The runner implements a direct CLI-only check for `case_selection=manifest-writer-handoff-input-contract` over the Step660 fixed 23-case metadata-only contract. It expects 3 selected valid cases, 20 selected invalid cases, 11 fail_closed metadata-category cases, 5 usage_error metadata-category cases, 4 mismatch metadata-category cases, 3 expected and observed pass cases, 11 expected and observed fail_closed cases, 5 expected and observed usage_error cases, and 4 expected and observed mismatch cases. The canonical aggregate keeps manifest writer invocation requested / invoked counts 0, manifest body generation / output counts 0, artifact / manifest file-writing counts 0, payload body emission counts 0, artifact body payload output count 0, generated policy body emitted count 0, request / pointer / expected body output counts 0, forbidden body / private path / absolute path / raw learner text / real data marker / no-oracle forbidden field / raw log counts 0, and residue count 0.

Step662 does not add Makefile target integration, release-quality wrapper integration, workflow changes, existing runtime implementation changes, existing validator implementation changes, manifest writer invocation, manifest body generation, artifact or manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, manifest body correctness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AM. Step664 Manifest Writer Handoff Input Validation Makefile Target

Step664 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation` for the Step662 direct CLI runner. The target runs `python -m learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation` with `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input`, `--case-selection manifest-writer-handoff-input-contract`, `--summary-only`, `--no-manifest-writer`, `--no-file-writing`, and `--fail-closed-on-forbidden-body`.

The target is placed after the artifact body to manifest handoff metadata-only no-writer-invocation target and before manifest writer / file-writing checks. It expects aggregate public-safe output for the 23-case metadata-only handoff input contract: 3 selected valid cases, 20 selected invalid cases, 11 fail_closed category cases, 5 usage_error category cases, 4 mismatch category cases, matching expected / observed status counts, zero manifest writer invocation requested / invoked counts, zero manifest body generation / output counts, zero artifact / manifest file-writing counts, zero payload body emission counts, zero artifact body payload output, zero generated policy body output, zero forbidden body detection, zero private / absolute path detection, zero raw learner text / real data marker detection, zero raw log count, and zero residue.

Step664 does not add release-quality wrapper integration, workflow changes, Python code/tests changes, fixture JSON changes, existing runtime implementation changes, existing validator implementation changes, manifest writer invocation, manifest body generation, artifact or manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, manifest body correctness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AN. Step666 Manifest Writer Handoff Input Validation Release-Quality Integration

Step666 adds `release_quality_check: learner-state frozen policy generation manifest writer handoff input validation` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation`, inserted after the artifact body to manifest handoff metadata-only no-writer-invocation check and before artifact / manifest file-writing and manifest writer checks.

The check runs the Step662 runner through the Step664 standalone target over the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input`. It expects mode `manifest_writer_handoff_input_validation`, schema `learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1`, contract `manifest_writer_handoff_input_contract`, matrix `manifest_writer_handoff_input_contract_matrix`, and `case_selection=manifest-writer-handoff-input-contract`. The expected aggregate remains metadata-only and public-safe: 23 selected / processed cases, 3 selected valid cases, 20 selected invalid cases, 11 selected fail_closed cases, 5 selected usage_error cases, 4 selected mismatch cases, matching observed pass / fail_closed / usage_error / mismatch counts, zero manifest writer invocation requested / invoked counts, zero manifest body generation / output counts, zero artifact / manifest file-writing counts, zero payload body emission counts, zero artifact body payload output, zero generated policy body output, zero forbidden body detection, zero private / absolute path detection, zero raw learner text / real data marker detection, zero no-oracle forbidden field detection, zero raw log count, and zero residue.

`status=pass` means the 23-case metadata-only manifest writer handoff input contract matched. It does not prove manifest writer correctness, file-writing readiness, manifest body correctness, payload correctness, production readiness, real-data readiness, model performance, or any change to the Step645 payload audit limitation.

Step666 does not change Makefile, workflows, Python code/tests, fixture JSON, existing runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest writer invocation, manifest body generation, artifact body file writing, manifest file writing, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, or model performance evidence.

## Appendix AO. Step675 Manifest Writer Dry-Run No-Body No-File-Writing Validator / Runner

Step675 adds `python/learner_state/frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_validation.py`, focused tests at `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_validation.py`, and the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing/`.

The runner implements a direct CLI-only check for `case_selection=manifest-writer-dry-run-no-body-no-file-writing-contract` and `dry_run_mode=manifest_writer_dry_run_no_body_no_file_writing` over the Step673 fixed 34-case metadata-only contract. Required flags are `--summary-only`, `--no-manifest-writer`, `--no-manifest-body`, `--no-generated-policy-body`, `--no-file-writing`, `--no-output-directory`, `--fail-closed-on-forbidden-body`, and `--fail-closed-on-file-writing`. The expected aggregate remains public-safe and body-free: 34 selected / processed cases, 4 selected valid cases, 30 selected invalid cases, 20 selected fail_closed cases, 5 selected usage_error cases, 5 selected mismatch cases, matching observed pass / fail_closed / usage_error / mismatch counts, zero manifest writer invocation allowed / invoked counts, zero manifest body generation / output counts, zero generated policy body output counts, zero artifact body payload output counts, zero payload body emission counts, zero request / pointer / expected body output counts, zero artifact / manifest file-writing counts, zero file-writing enabled counts, zero output directory creation counts, zero forbidden body / private path / absolute path / raw learner text / real data marker / no-oracle forbidden field / raw log / performance metric body counts, and zero residue.

Step675 does not add Makefile target integration, release-quality wrapper integration, workflow changes, existing runtime implementation changes, existing validator implementation changes, manifest writer invocation, manifest body generation/output, artifact or manifest file writing, file-writing enablement, output directory creation, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, manifest body correctness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AP. Step677 Manifest Writer Dry-Run No-Body No-File-Writing Makefile Target

Step677 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-manifest-writer-dry-run-no-body-no-file-writing-validation` for the Step675 direct CLI runner. The target runs `python -m learner_state.frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_validation` with `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing`, `--case-selection manifest-writer-dry-run-no-body-no-file-writing-contract`, `--summary-only`, `--dry-run-mode manifest_writer_dry_run_no_body_no_file_writing`, `--no-manifest-writer`, `--no-manifest-body`, `--no-generated-policy-body`, `--no-file-writing`, `--no-output-directory`, `--fail-closed-on-forbidden-body`, and `--fail-closed-on-file-writing`.

The target is placed after manifest writer handoff input validation and before broader manifest writer / file-writing checks. It expects aggregate public-safe output for the 34-case metadata-only dry-run contract: 4 selected valid cases, 30 selected invalid cases, 20 fail_closed category cases, 5 usage_error category cases, 5 mismatch category cases, matching observed status counts, zero manifest writer invocation allowed / invoked counts, zero manifest body generation / output counts, zero generated policy body output counts, zero artifact body payload output counts, zero payload body emission counts, zero request / pointer / expected body output counts, zero artifact / manifest file-writing counts, zero file-writing enabled counts, zero output directory creation counts, zero forbidden body / private path / absolute path / raw learner text / real data marker / no-oracle forbidden field / raw log / performance metric body counts, and zero residue.

Step677 does not add release-quality wrapper integration, workflow changes, Python code/tests changes, fixture JSON changes, existing runtime implementation changes, existing validator implementation changes, manifest writer invocation, manifest body generation/output, artifact or manifest file writing, file-writing enablement, output directory creation, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, model performance evidence, manifest writer correctness evidence, file-writing readiness evidence, manifest body correctness evidence, payload correctness evidence, or artifact body payload quality evidence.

## Appendix AQ. Step679 Manifest Writer Dry-Run No-Body No-File-Writing Release-Quality Integration

Step679 adds `release_quality_check: learner-state frozen policy generation manifest writer dry-run no-body no-file-writing validation` to `scripts/check_release_quality.sh`. The command is `make check-learner-state-frozen-policy-generation-manifest-writer-dry-run-no-body-no-file-writing-validation`, inserted after manifest writer handoff input validation and before artifact / manifest file-writing and broader manifest writer checks.

The check runs the Step675 runner through the Step677 standalone target over the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing`. It expects mode `manifest_writer_dry_run_no_body_no_file_writing_validation`, schema `learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_v0.1`, contract `manifest_writer_dry_run_no_body_no_file_writing_contract`, matrix `manifest_writer_dry_run_no_body_no_file_writing_contract_matrix`, and `case_selection=manifest-writer-dry-run-no-body-no-file-writing-contract`. The expected aggregate remains metadata-only and public-safe: 34 selected / processed cases, 4 selected valid cases, 30 selected invalid cases, 20 selected fail_closed cases, 5 selected usage_error cases, 5 selected mismatch cases, matching observed pass / fail_closed / usage_error / mismatch counts, zero manifest writer invocation allowed / invoked counts, zero manifest body generation / output counts, zero generated policy body output counts, zero artifact body payload output counts, zero payload body emission counts, zero request / pointer / expected body output counts, zero artifact / manifest file-writing counts, zero file-writing enabled counts, zero output directory creation counts, zero forbidden body / private path / absolute path / raw learner text / real data marker / no-oracle forbidden field / raw log / performance metric body counts, and zero residue.

`status=pass` means the 34-case metadata-only dry-run no-body no-file-writing contract matched. It does not prove manifest writer correctness, manifest body correctness, file-writing readiness, payload correctness, production readiness, real-data readiness, model performance, or any change to the Step669 or Step645 limitations.

Step679 does not change Makefile, workflows, Python code/tests, fixture JSON, existing runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest writer invocation, manifest body generation/output, artifact body file writing, manifest file writing, file-writing enablement, output directory creation, payload body emission, artifact body payload output, generated policy body output, production readiness, real-data readiness, or model performance evidence.

## Appendix AR. Web Logger Durability / Unicode / Hash Safety Design

`docs/web_logger_durability_unicode_hash_safety_design.md` records a design-only / docs-only pre-collection blocker for the Web logger and Rust replay boundary.

The design fixes the intended future policy for three risks: event data durability under network/browser lifecycle failures, UTF-16 code unit position interpretation across TypeScript and Rust, and SHA-256 text hash canonicalization over exact UTF-8 stored strings. It proposes client queue and IndexedDB persistence, batch ack/retry, event_id deduplication, client seq reconciliation, server-side idempotency, client-seq authoritative ordering, safe JSONL partial-write handling, UTF-16 to UTF-8 validated conversion, no Unicode or newline normalization by default, shared synthetic test vectors, failure injection tests, TypeScript / Rust integration tests, and Go / No-Go criteria before collection.

This appendix is not implementation evidence. It does not change TypeScript, Rust, Python, fixtures, CI workflows, Makefile, release-quality wrapper, package metadata, schema implementation, runtime implementation, or validator implementation. It does not authorize data collection and does not claim production readiness, real-data readiness, model performance, perfect event delivery, completed Unicode implementation, or completed hash compatibility implementation.

## Appendix AS. Web Logger Durability / Unicode / Hash Current Implementation Audit

`docs/web_logger_durability_unicode_hash_current_implementation_audit.md` records an audit-only / docs-only inventory of current Web logger, Rust schema/validation/replay, docs, and tests against Appendix AR.

The audit finds partial current support for in-memory event recording, `session_id`, `seq`, basic JSONL validation, sequence-gap validation, cursor/selection range validation, replay diagnostics, and placeholder-aware replay hash checks. It also records gaps: no durable client queue, no IndexedDB persistence, no server batch/ack/retry/dedup/reconciliation path, no `event_id`, no schema-declared UTF-16 position unit, no Rust UTF-16 code unit to UTF-8 byte conversion helper, no SHA-256 TypeScript/Rust canonical hash implementation, and no shared TypeScript / Rust Unicode/hash vectors.

This appendix is audit evidence only. It does not change TypeScript, Rust, Python, tests, fixture JSON, Makefile, release-quality wrapper, workflow files, package files, Cargo files, schema implementation, runtime implementation, or validator implementation. It recommends Step-web-logger-002 schema clarification for position units and hash canonicalization before queue / IndexedDB implementation.

## Appendix AT. Web Logger Position Unit and Hash Schema Clarification

`docs/web_logger_position_unit_and_hash_schema_clarification.md` records a schema-clarification / docs-only policy for the Step-web-logger-001 P0 gaps around position units and hash canonicalization.

The clarification fixes intended future schema semantics: browser-originated selection, cursor, and edit span offsets use UTF-16 code unit offsets; schema should expose or document `position_unit=utf16_code_unit`; Rust must convert those offsets to UTF-8 byte indices through a validated future helper; invalid offsets fail closed; stored strings are preserved without Unicode or newline normalization; and `text_hash_before` / `text_hash_after` use SHA-256 over exact UTF-8 stored text with lowercase hex output.

This appendix is policy clarification only. It does not implement TypeScript hash helpers, Rust hash helpers, Rust UTF-16 conversion helpers, tests, fixture JSON, CI, Makefile targets, release-quality checks, schema implementation, runtime implementation, validator implementation, event durability queueing, IndexedDB, acknowledgement, retry, or deduplication.

## Appendix AU. Web Logger Shared Unicode and Hash Test Vector Design

`docs/web_logger_shared_unicode_hash_test_vector_design.md` records a test-vector-design / docs-only plan for future shared TypeScript / Rust Unicode and hash vectors.

The design proposes a future `tests/fixtures/web_logger_unicode_hash_vectors/` root, top-level vector metadata, per-vector fields, offset case fields, canonical `position_unit=utf16_code_unit` / SHA-256 / UTF-8 / no-normalization metadata, required Unicode categories, an initial 15-vector set, invalid vector categories, cross-language validation expectations, future Makefile and release-quality labels, and a reviewed hash generation procedure.

This appendix is design only. It does not create fixture JSON, compute hash values, implement TypeScript or Rust helpers, add tests, add CI, change Makefile, change release-quality wrapper, change schema/runtime/validator implementation, or implement event durability.

## Appendix AV. Web Logger Shared Unicode and Hash Vector Fixtures

`tests/fixtures/web_logger_unicode_hash_vectors/` records fixture-data implementation for the Step-web-logger-003 vector design.

The root contains `README.md` and `vectors.json`. The vector file declares `vector_schema_version=web_logger_unicode_hash_vectors_v0.1`, `position_unit=utf16_code_unit`, `hash_algorithm=SHA-256`, `hash_encoding=UTF-8`, no Unicode normalization, no newline normalization, trailing-newline preservation, lowercase hex output, `real_data_allowed=false`, and 15 synthetic vectors. The vectors cover empty string, ASCII, Japanese, full-width alphanumerics, emoji surrogate pairs, Japanese plus emoji, combining sequences, precomposed accents, LF, CRLF, trailing newline, tab, invalid surrogate boundary, invalid beyond-length, and compact mixed Unicode cases.

This appendix records fixture data only. It does not implement TypeScript helpers, Rust helpers, Python code, test code, schema implementation, runtime implementation, validator implementation, Makefile targets, CI workflows, release-quality checks, package metadata changes, Cargo metadata changes, or event durability queue / IndexedDB / acknowledgement / retry / deduplication.

## Appendix AW. Web Logger Unicode and Hash Vector Fixture Validator

`python/web_logger_unicode_hash_vector_validation.py` implements a Python validator for `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`. Focused tests live at `python/test_support/tests/test_web_logger_unicode_hash_vector_validation.py`.

The validator checks the fixed vector schema version, top-level metadata, vector IDs and required fields, UTF-16 code unit lengths, UTF-8 byte lengths, code point counts, SHA-256 UTF-8 lowercase-hex hashes over decoded source text, valid offset mappings, expected invalid offset records, conservative forbidden marker counts, and public-safe summary output. The direct CLI is `PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only`.

This appendix records fixture validator implementation only. It does not implement TypeScript helper code, Rust UTF-16 conversion helper code, Rust hash helper code, event durability queue / IndexedDB / acknowledgement / retry / deduplication, Makefile targets, release-quality integration, CI workflow changes, schema implementation changes, replay/runtime changes, production readiness, real-data readiness, or model performance evidence.

## Appendix AX. Web Logger Unicode and Hash Vector Validator Makefile Target

`check-web-logger-unicode-hash-vector-fixtures` is added as a standalone Makefile target for the Step-web-logger-006 Python validator.

The target runs `PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only`. It validates the shared synthetic Unicode/hash vector fixture metadata, SHA-256 hashes over decoded UTF-8 source text, UTF-16 code unit lengths, UTF-8 byte lengths, offset mappings, expected invalid offset records, and public-safe summary output.

This appendix records Makefile target integration only. It does not add release-quality integration, CI workflow integration, TypeScript helper code, Rust UTF-16 conversion helper code, Rust hash helper code, fixture JSON changes, schema implementation changes, replay/runtime changes, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix AY. Web Logger Unicode and Hash Vector Validator Release-Quality Check

`scripts/check_release_quality.sh` adds `release_quality_check: web logger unicode hash vector fixture validation` for the Step-web-logger-008 Makefile target.

The wrapper calls `make check-web-logger-unicode-hash-vector-fixtures` after Python checks and before learner-state target groups. The check validates the shared synthetic Unicode/hash vector fixture through the Python validator, including fixture metadata, SHA-256 hashes over decoded UTF-8 source text, UTF-16 code unit lengths, UTF-8 byte lengths, offset mappings, expected invalid offset records, and public-safe summary output.

This appendix records release-quality wrapper integration only. It does not add CI workflow integration, TypeScript helper code, Rust UTF-16 conversion helper code, Rust hash helper code, fixture JSON changes, schema implementation changes, replay/runtime changes, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix AZ. Web Logger Rust UTF-16 Offset Conversion Helper

`crates/kslog_replay/src/utf16_offsets.rs` adds a focused Rust utility for converting browser-originated UTF-16 code unit offsets into UTF-8 byte offsets at valid Rust char boundaries. `crates/kslog_replay/tests/utf16_offsets.rs` adds focused Rust tests for the helper.

The helper exposes `utf16_code_unit_offset_to_utf8_byte_index` and `utf16_code_unit_range_to_utf8_byte_range`. It preserves Unicode and newline content without normalization, rejects offsets beyond the UTF-16 code unit length, rejects surrogate-pair internal offsets, rejects `start > end`, permits valid empty ranges, returns byte ranges suitable for Rust string slicing, and exposes public-safe reason codes without including raw text in error display output.

The focused tests cover empty strings, ASCII, Japanese, full-width alphanumerics, emoji surrogate pairs, mixed Japanese plus emoji, combining sequences, precomposed accents, LF, CRLF, trailing newline, tab, range conversion, empty ranges, stable reason codes, public-safe error text, and direct shared vector offset cases from `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`.

This appendix records focused helper and test implementation only. It does not add broad replay / validate / extract / micro_episode runtime integration, TypeScript helper code, Rust SHA-256 helper code, TypeScript/Rust cross-language vector checks, fixture JSON changes, Makefile targets, release-quality wrapper changes, CI workflow integration, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix BA. Web Logger Rust UTF-16 Offset Conversion Helper Makefile Target

`check-web-logger-rust-utf16-offset-conversion` is added as a standalone Makefile target for the Step-web-logger-015 focused Rust helper tests.

The target runs:

```bash
cargo test -p kslog_replay utf16
```

It exercises the `kslog_replay` UTF-16 code unit offset to UTF-8 byte offset helper tests, including shared synthetic vector reuse. The target is placed near the existing Web logger Unicode/hash vector fixture target.

This appendix records Makefile target integration only. It does not change Rust helper code, focused Rust tests, fixture JSON, release-quality wrapper integration, CI workflow integration, broader replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper code, TypeScript SHA-256 helper code, TypeScript/Rust cross-language vector checks, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix BB. Web Logger Rust UTF-16 Offset Conversion Helper Release-Quality Check

`scripts/check_release_quality.sh` adds `release_quality_check: web logger Rust UTF-16 offset conversion helper` for the Step-web-logger-017 Makefile target.

The wrapper calls:

```bash
make check-web-logger-rust-utf16-offset-conversion
```

The check runs the Step-web-logger-015 focused Rust helper tests through Makefile, after the Web logger Unicode/hash vector fixture validation check and before learner-state audit fixtures. It exercises UTF-16 code unit offset to UTF-8 byte offset conversion behavior, including fail-closed behavior for surrogate-pair internal offsets, offsets beyond length, and `start > end` cases through the focused test target.

This appendix records release-quality wrapper integration only. It does not change Makefile, Rust helper code, focused Rust tests, fixture JSON, CI workflow integration, broader replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper code, TypeScript SHA-256 helper code, TypeScript/Rust cross-language vector checks, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix BC. Web Logger Rust UTF-16 Offset Replay Integration

`crates/kslog_replay/src/lib.rs` adds replay-focused integration for the existing Rust UTF-16 offset conversion helper.

Replay now resolves browser-originated cursor and selection offsets from UTF-16 code units to UTF-8 byte ranges before string slicing or replacement. Replay document length checks use UTF-16 code unit counts, cursor-after metadata is validated against the updated text state, and invalid surrogate-pair internal offsets, offsets beyond length, and `start > end` fail closed with public-safe reason_code behavior.

Focused `utf16` replay tests cover ASCII preservation, Japanese cursor insertion, emoji selection replacement, mixed Japanese/emoji valid offsets, surrogate-pair internal offset failure, beyond-length failure, inverted selection failure, and diagnostics content suppression.

This appendix records `kslog_replay` replay-focused integration only. It does not change `kslog_validate`, `kslog_extract`, `kslog_micro_episode`, `kslog_schema`, fixture JSON, Makefile, release-quality wrapper, CI workflow, Rust SHA-256 helper code, TypeScript SHA-256 helper code, TypeScript/Rust cross-language vector checks, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix BD. Web Logger Rust UTF-16 Makefile Target Help Text Alignment

Step-web-logger-026 updates the visible help text for the existing `check-web-logger-rust-utf16-offset-conversion` target to:

```text
Run Rust UTF-16 offset conversion and replay integration tests
```

The target name and command remain unchanged:

```bash
cargo test -p kslog_replay utf16
```

This records Makefile-visible wording alignment after Step-web-logger-024. The target now describes both helper-focused UTF-16 tests and replay-focused UTF-16 tests selected by the `utf16` filter. No new target is added, `scripts/check_release_quality.sh` is unchanged, and the Step-web-logger-021 remote status marker remains helper-focused pre-Step-web-logger-024 evidence rather than replay-focused remote status.

This appendix does not change Rust code, tests, fixture JSON, release-quality wrapper behavior, CI workflow, `kslog_validate`, `kslog_extract`, `kslog_micro_episode`, `kslog_schema`, schema-level position_unit behavior, Rust SHA-256 helper code, TypeScript SHA-256 helper code, TypeScript/Rust cross-language vector checks, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence.

## Appendix BE. Web Logger Rust UTF-16 Release-Quality Label Alignment

Step-web-logger-028 updates the existing release-quality wrapper label from:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

to:

```text
release_quality_check: web logger Rust UTF-16 offset conversion and replay integration
```

The wrapper command remains unchanged:

```bash
make check-web-logger-rust-utf16-offset-conversion
```

The check remains ordered after `release_quality_check: web logger unicode hash vector fixture validation` and before `release_quality_check: learner-state audit fixtures`. The wrapper still calls the Makefile target and does not duplicate `cargo test -p kslog_replay utf16`.

This appendix records release-quality visible label wording only. It does not change Makefile, Rust code, tests, fixture JSON, CI workflow, `kslog_validate`, `kslog_extract`, `kslog_micro_episode`, `kslog_schema`, schema-level position_unit behavior, Rust SHA-256 helper code, TypeScript SHA-256 helper code, TypeScript/Rust cross-language vector checks, event durability queue / IndexedDB / acknowledgement / retry / deduplication, production readiness, real-data readiness, or model performance evidence. The Step-web-logger-021 status marker remains focused-helper evidence and is not reinterpreted as replay-focused remote status.

## Step-web-logger-034 Schema-Level Position Unit Fixture Appendix

Step-web-logger-034 adds the synthetic fixture root
`tests/fixtures/web_logger_position_unit_schema/` for future Web logger
schema-level `position_unit=utf16_code_unit` policy checks.

The root contains README guidance, `case_index.json`, 5 valid JSONL cases,
11 invalid JSONL cases, and 1 legacy JSONL case. The fixtures are intended for
future schema / validator work and do not implement schema behavior, validation
behavior, fixture validator CLI, Makefile target, release-quality wrapper
changes, Rust / TypeScript / Python code changes, validate / extract /
micro_episode integration, Rust / TypeScript SHA-256 helpers, TypeScript/Rust
cross-language vector checks, event durability queue / IndexedDB /
acknowledgement / retry / deduplication, production readiness, real-data
readiness, or model performance evidence.

## Step-web-logger-036 Schema-Level Position Unit Fixture Validator Appendix

Step-web-logger-036 adds
`python/web_logger_position_unit_fixture_validation.py` and focused tests at
`python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`.

The CLI
`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
validates the Step-web-logger-034 fixture contract with public-safe key=value
summary output. It checks fixed case counts, JSONL records, position-unit
policy metadata, bounded UTF-16 metadata expectations, expected reason-code
counts, and no-oracle safety markers. It does not implement Rust
`kslog_schema` / `kslog_validate` behavior, add Makefile target,
release-quality wrapper integration, validate / extract / micro_episode
integration, Rust / TypeScript SHA-256 helpers, TypeScript/Rust checks, event
durability, production readiness, real-data readiness, or model performance
evidence.

## Step-web-logger-038 Schema-Level Position Unit Fixture Validator Makefile Target Appendix

Step-web-logger-038 adds Makefile target
`check-web-logger-position-unit-fixtures` for the Step-web-logger-036
position-unit fixture contract validator.

The target help text is:

`Run Web logger position_unit fixture contract validation`

The target command is:

`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`

The target runs the validator CLI only. It does not run focused tests, mutate
fixtures, regenerate metadata, add release-quality wrapper integration,
implement Rust `kslog_schema` / `kslog_validate` behavior, change validate /
extract / micro_episode behavior, add Rust / TypeScript SHA-256 helpers, add
TypeScript/Rust checks, implement event durability, or provide production
readiness, real-data readiness, or model performance evidence.

## Step-web-logger-040 Schema-Level Position Unit Fixture Validator Release-Quality Appendix

Step-web-logger-040 adds release-quality wrapper check
`release_quality_check: web logger position_unit fixture contract validation`.

The wrapper command is:

`make check-web-logger-position-unit-fixtures`

The check is inserted after Web logger Unicode/hash fixture validation and
before Rust UTF-16 offset conversion and replay integration. The wrapper calls
the Makefile target rather than duplicating the Python command. This remains
fixture contract validation only and does not implement Rust `kslog_schema` /
`kslog_validate` behavior, change validate / extract / micro_episode behavior,
create a status marker, create a final safety review, add Rust / TypeScript
SHA-256 helpers, add TypeScript/Rust checks, implement event durability, or
provide production readiness, real-data readiness, or model performance
evidence.

## Step-web-logger-045 Rust Schema Position Unit Parser Boundary Appendix

Step-web-logger-045 updates `kslog_schema::RawEvent` so the Rust schema layer
can receive optional raw `position_unit` and optional `research_schema_target`
metadata while preserving unknown-field rejection. It adds typed,
body-suppressed parser/accessor functions that classify supported
`utf16_code_unit`, missing position_unit, unsupported position_unit, schema
mismatch, and unknown schema version using stable reason codes.

Focused `kslog_schema` tests cover deserialization, unsupported-value
preservation, reason-code stability, unknown-field rejection, and schema
deserialization of the Step034 fixture records. This appendix is limited to
the Rust schema parser boundary. Rust validator policy enforcement, UTF-16
numeric metadata validation, validate / extract / micro_episode integration,
TypeScript logger changes, fixture changes, Makefile changes, wrapper changes,
Rust / TypeScript SHA-256 helpers, TypeScript/Rust vector checks, event
durability, production readiness, real-data readiness, and model performance
evidence remain future work.

## Step-web-logger-047 Rust Validator Phase 1 Position Unit Appendix

Step-web-logger-047 updates `kslog_validate` with bounded Phase 1
position-unit enforcement. After `RawEvent` deserialization, fixture-targeted
Web logger v0.2-style records require explicit
`position_unit=utf16_code_unit`; missing, unsupported, schema-mismatch, and
unknown-version cases fail with stable body-free reason codes. Existing legacy
synthetic records are not made subject to a global position-unit requirement.

This appendix is limited to presence / value / schema-version gating. UTF-16
numeric metadata validation, `kslog_replay::utf16_offsets` dependency,
extract / micro_episode integration, TypeScript logger changes, fixture JSON
changes, Makefile changes, wrapper changes, Rust / TypeScript SHA-256 helpers,
TypeScript/Rust checks, event durability, production readiness, real-data
readiness, and model performance evidence remain future work.

## Step-web-logger-049 Rust Validator Phase 1 Makefile Target Appendix

Step-web-logger-049 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase1`.

The target help text is:

`Run Rust validator position_unit Phase 1 policy tests`

The target command is:

`cargo test -p kslog_validate position_unit_phase1`

Step-web-logger-059 corrects this command from the broader `position_unit`
substring filter to the Phase 1-only `position_unit_phase1` filter after
Phase 2 tests were added. The target runs focused Rust validator Phase 1 tests
only. It does not run full validator tests, workspace tests, the Python fixture
contract validator, replay checks, extract / micro_episode checks, or Phase 2
focused tests. TypeScript logger changes, fixture JSON changes, Rust /
TypeScript SHA-256 helpers, TypeScript/Rust checks, event durability,
production readiness, real-data readiness, and model performance evidence
remain future work.

## Step-web-logger-051 Rust Validator Phase 1 Release-Quality Integration Appendix

Step-web-logger-051 adds release-quality wrapper integration for the Rust
validator Phase 1 target.

Added label:

`release_quality_check: web logger Rust validator position_unit Phase 1 policy`

Added command:

`make check-web-logger-rust-validator-position-unit-phase1`

The check is inserted after the Web logger position_unit fixture contract
validation check and before the Rust UTF-16 offset conversion and replay
integration check. The wrapper calls the Makefile target and does not
duplicate the Cargo command directly.

This remains Rust validator Phase 1 focused-test coverage only. Phase 2
UTF-16 numeric metadata validation, extract / micro_episode integration,
TypeScript logger changes, fixture JSON changes, Rust / TypeScript SHA-256
helpers, TypeScript/Rust checks, event durability, release-quality status
marker, final safety review, production readiness, real-data readiness, and
model performance evidence remain future work.

## Step-web-logger-056 Shared UTF-16 Helper Extraction Appendix

Step-web-logger-056 adds `kslog_schema::utf16_offsets` as the reusable helper
for UTF-16 code unit length and UTF-16 offset/range to UTF-8 byte offset
conversion. `kslog_replay::utf16_offsets` remains as a compatibility re-export
of the shared helper so existing replay behavior and helper paths remain
stable.

This does not implement `kslog_validate` Phase 2 UTF-16 numeric metadata
enforcement, does not add a `kslog_validate -> kslog_replay` dependency, and
does not change Makefile, release-quality wrapper, fixtures, TypeScript/Python
code, SHA-256 helper work, TypeScript/Rust vector checks, event durability,
production readiness, real-data readiness, or model performance evidence.

## Step-web-logger-057 Rust Validator Phase 2 UTF-16 Numeric Metadata Appendix

Step-web-logger-057 adds bounded Phase 2 UTF-16 numeric metadata validation to
`kslog_validate`. The check runs only after Phase 1 accepts a Web logger
v0.2-style event with `position_unit=utf16_code_unit`, and it uses
`kslog_schema::utf16_offsets` for UTF-16 code unit length and offset/range
boundary checks. No `kslog_validate -> kslog_replay` dependency is added.

The validator now emits body-free Phase 2 reason codes for
`doc_len_before_utf16_mismatch`, `doc_len_after_utf16_mismatch`,
`start_greater_than_end`, `offset_beyond_utf16_length`,
`offset_inside_surrogate_pair`, and `invalid_utf16_boundary`. Focused tests
cover the five valid position-unit fixtures and the Phase 2 invalid fixtures.
Detectable byte-index misuse is limited to metadata that conflicts with
UTF-16 length or scalar boundaries.

This appendix does not add a Phase 2 Makefile target, does not add Phase 2
release-quality wrapper integration, does not change fixtures, does not change
replay behavior, does not implement extract / micro_episode integration, does
not change TypeScript logger behavior, does not add SHA-256 helpers or
TypeScript/Rust vector checks, and does not provide production readiness,
real-data readiness, or model performance evidence.

## Step-web-logger-059 Rust Validator Phase 2 Makefile Target Appendix

Step-web-logger-059 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric` for the
Step057 focused Phase 2 validator tests.

The target help text is:

`Run Rust validator position_unit Phase 2 UTF-16 numeric metadata tests`

The target command is:

`cargo test -p kslog_validate position_unit_phase2`

The target is placed after the corrected Phase 1 target and before
`check-web-logger-rust-utf16-offset-conversion`. Step-web-logger-059 does not
change the release-quality wrapper, Rust code/tests, fixture JSON, replay
behavior, TypeScript/Python code, Cargo/package metadata, workflows, extract /
micro_episode integration, SHA-256 helper work, TypeScript/Rust vector checks,
event durability, production readiness, real-data readiness, or model
performance evidence.

## Step-web-logger-061 Rust Validator Phase 2 Release-Quality Integration

Step-web-logger-061 adds release-quality wrapper coverage for the Phase 2
validator target with label:

`release_quality_check: web logger Rust validator position_unit Phase 2 UTF-16 numeric metadata`

The wrapper command is:

`make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`

The wrapper calls the Makefile target rather than duplicating
`cargo test -p kslog_validate position_unit_phase2` directly. The check is
inserted after the Phase 1 validator label and before Rust UTF-16 replay
integration. Phase 1 label / command remain unchanged.

This is release-quality wrapper integration only. It does not change Makefile,
Rust code/tests, fixture JSON, replay behavior, TypeScript/Python code,
Cargo/package metadata, workflows, Phase 2 run record workflow, status marker,
final safety review, extract / micro_episode integration, SHA-256 helper work,
TypeScript/Rust vector checks, event durability, production readiness,
real-data readiness, or model performance evidence.
