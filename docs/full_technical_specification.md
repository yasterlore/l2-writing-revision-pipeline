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
that compares this draft with the source inventory. The report found no
high-severity gaps, but medium and low follow-up gaps remain; this draft should
not be treated as an absolute guarantee of no omissions.

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
  inventory and repository scan, completed as a docs-only report
- Step-pretec-doc4: medium-priority coverage gap appendices, completed with
  Python CLI, Makefile target, schema/version, fixture count, and external
  review checklist appendices
- artifact writer CLI integration runtime implementation design and
  implementation
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
| `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py` | `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation` | `--fixture-root`, `--fixture-case`, `--json` | Future runtime fixture validation | fixture root/case to count-only summary | no | standalone Makefile target; not wrapper-integrated as of scan | does not execute runtime integration |
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
| `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures` | runtime fixture validator root mode | Runtime fixture validation | count-only summary | standalone | artifact writer CLI integration runtime fixtures | no runtime execution |
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
| `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.1`, `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_result_v0.1` | artifact writer CLI integration runtime fixture | runtime fixture validator | validator/fixtures/docs | static fixture validation; no runtime execution |
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
| `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/` | future runtime fixture validation | 30 | 6 / 24 | 180 | 6 | runtime fixture validator/standalone target | standalone only | does not execute runtime integration |
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
- Confirm artifact writer CLI integration runtime remains marked not
  implemented until a separate runtime implementation step exists.
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
