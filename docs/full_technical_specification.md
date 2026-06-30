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
| Artifact writer CLI integration runtime fixture | `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.1`, runtime result/request/pointer/case metadata schema names | runtime fixture validator/docs/fixtures | Future runtime fixture validation | Static only; runtime integration not implemented. |
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
| Artifact writer CLI integration runtime fixtures | runtime fixture root | Static future runtime fixture contract | runtime fixture validator | 30 cases / 180 JSON files confirmed by Step479/Step481 docs |
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
| Artifact writer CLI integration runtime fixture | runtime fixture validator | runtime fixture tests | runtime fixture root | runtime fixture docs | runtime fixture target | none observed | none | standalone static validation |
| Artifact writer CLI integration runtime | none observed | none | supporting runtime fixtures | runtime design docs | none | none | none | not implemented |
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
  inventory and repository scan
- artifact writer CLI integration runtime implementation design and
  implementation
- artifact body generation CLI integration design and implementation
- manifest writer integration design and implementation
- manifest body generation design, if it remains in scope
- production readiness review, separate from this research software draft
- real-data readiness review, separate and institution-approved
- external review checklist for public specification release
- exact CLI argument extraction for all Python modules
- exact Makefile command mapping appendix
- fixture count recomputation and schema catalogue validation

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

- exact CLI argument tables for every Python module require parser/help
  extraction in a later step
- exact fixture counts should be recomputed from fixture roots or validator
  summaries before treating this draft as final
- exact schema catalogue should distinguish stable schema names from synthetic
  invalid-case markers
- any component not represented in this draft should be treated as
  `not yet confirmed from repository scan` until Step-pretec-doc3 validates
  coverage

Coverage validation in the next step should compare this draft against:

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
