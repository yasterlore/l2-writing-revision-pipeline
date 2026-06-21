# Shell Script Inventory And Task Category Design

This document inventories the current `scripts/*.sh` entrypoints and groups
them into task categories before any Makefile, justfile, or other task runner is
introduced.

It is design documentation only. It does not change scripts, workflows, tests,
summary generation, scorer logic, manifest schema, or fixture data. It is not a
performance evaluation.

## 1. Purpose

The purpose of this document is to:

- list the existing shell scripts
- describe each script's role at a safe high level
- identify task categories and ordering dependencies
- classify output-safety expectations
- identify future task-runner target candidates
- provide input for a later Makefile / justfile design step

The inventory intentionally avoids copying full script bodies or generated file
bodies.

## 2. Inventory Method

Inventory method:

- list `scripts/*.sh` and `scripts/lib/*.sh`
- read only enough script context to identify purpose, dependencies, and output
  safety
- record script name, purpose, category, dependencies, output-safety stance,
  task-runner entrypoint candidacy, and migration candidacy
- do not paste raw JSONL, summary CSV body, manifest JSON body, config body,
  candidate score rows, or generated output bodies

The current inventory command is:

```bash
find scripts -maxdepth 2 -type f -name "*.sh" | sort
```

## 3. Script Inventory

| Script | Purpose | Category | Main dependencies | Output safety | Entrypoint candidate | Migration candidate |
| --- | --- | --- | --- | --- | --- | --- |
| `scripts/check_release_quality.sh` | Runs the normal success-path release-quality bundle sequentially. | release-quality wrapper | most other checks; Python, Rust, Node tooling | safe stage headings and command status; should not print file bodies | high | medium: may later become task-runner target implementation detail |
| `scripts/run_synthetic_e2e_summary.sh` | Generates no-config synthetic E2E count-only summary and manifest. | synthetic E2E summary generation | `scripts/run_synthetic_e2e_pipeline.sh`, synthetic fixtures, manifest schema constants | safe summary/status only; may generate `tmp/` outputs | high | medium: keep shell initially, consider structured orchestrator later |
| `scripts/check_summary_manifest_schema_sync.sh` | Checks generated no-config summary manifest against shared schema constants. | manifest/schema sync check | `scripts/lib/summary_manifest_schema.sh`, generated manifest | safe metadata/count output only | high | medium: JSON validation could move to Python/Rust helper later |
| `scripts/check_synthetic_diagnostic_distribution.sh` | Checks count-only diagnostic distribution from no-config summary. | diagnostic distribution check | generated no-config summary and manifest | safe count-only output; no body dumps | high | medium: can remain shell with Python parser, or move later |
| `scripts/run_synthetic_e2e_pipeline.sh` | Runs one synthetic Rust + Python E2E case without printing JSONL contents. | synthetic E2E pipeline glue | Rust CLI, Python modules, synthetic fixture paths | safe status/path output; generates `tmp/` outputs | medium | medium: complex glue candidate for future orchestrator |
| `scripts/run_synthetic_e2e_config_summary.sh` | Runs explicit config-enabled synthetic E2E summary to a separate output root. | config-enabled summary generation | `run_synthetic_e2e_pipeline.sh`, explicit safe config fixture | safe count-only output; separate `tmp/` output root | medium | medium: keep separate from no-config path |
| `scripts/check_config_enabled_summary_smoke.sh` | Smokes config-enabled summary behavior and no-config separation. | config-enabled smoke | config summary script, no-config summary script, safe-output checks | safe status/count output; captures logs under `tmp/` | medium | low-to-medium: expected-failure checks may later be structured |
| `scripts/check_config_enabled_e2e_smoke.sh` | Smokes no-config/default-like/intentional explicit config E2E behavior. | config-enabled smoke | E2E pipeline script, synthetic config fixtures | safe status/path/count output; generates `tmp/` outputs | medium | low-to-medium |
| `scripts/check_no_config_scoring_fixture_lock.sh` | Compares generated no-config candidate scores against synthetic fixture locks. | no-config fixture lock | generated candidate scores, synthetic expected lock fixtures, Python module | safe mismatch counts/status only | medium | low: stable validation wrapper |
| `scripts/check_hand_weight_config_validation.sh` | Validates valid and invalid synthetic hand-weight config fixtures. | hand-weight config validation | Python validator, synthetic config fixtures | safe status/count output; temp failure capture under `/tmp` | medium | low: stable smoke/validation wrapper |
| `scripts/check_explicit_config_ranking_diff.sh` | Checks default-like zero diff and intentional weighted-score diff for explicit config path. | explicit config ranking diff | Python scorer/diff modules, synthetic constraints/configs | safe count/diff-status output; generated `tmp/` outputs | medium | medium: generated fixture mutation could move to helper |
| `scripts/check_synthetic_policy.sh` | Checks for private/real-data-looking paths and forbidden no-oracle fields in public synthetic fixtures. | synthetic policy | repository file tree, grep | safe path/status output; no generated bodies | high | low: shell/grep is suitable |
| `scripts/lib/summary_manifest_schema.sh` | Shared shell constants for no-config summary manifest schema. | helper/library shell file | sourced by manifest generator/checkers | no output when sourced | low as user-facing target | low: keep as compatibility constants until schema source changes |

## 4. Task Categories

Current task categories:

- release-quality wrapper:
  `scripts/check_release_quality.sh`
- synthetic E2E summary generation:
  `scripts/run_synthetic_e2e_summary.sh`
- synthetic E2E pipeline glue:
  `scripts/run_synthetic_e2e_pipeline.sh`
- manifest/schema sync check:
  `scripts/check_summary_manifest_schema_sync.sh`
- diagnostic distribution check:
  `scripts/check_synthetic_diagnostic_distribution.sh`
- config-enabled smoke and summary:
  `scripts/run_synthetic_e2e_config_summary.sh`,
  `scripts/check_config_enabled_summary_smoke.sh`,
  `scripts/check_config_enabled_e2e_smoke.sh`
- no-config fixture lock:
  `scripts/check_no_config_scoring_fixture_lock.sh`
- hand-weight config validation:
  `scripts/check_hand_weight_config_validation.sh`
- explicit config ranking diff:
  `scripts/check_explicit_config_ranking_diff.sh`
- synthetic policy:
  `scripts/check_synthetic_policy.sh`
- helper/library shell files:
  `scripts/lib/summary_manifest_schema.sh`
- logger/frontend checks:
  no dedicated shell script currently; commands run directly under
  `apps/logger-web`
- expected-failure smoke:
  currently embedded inside dedicated smoke scripts rather than exposed as a
  separate top-level script

## 5. Dependency And Order Classification

Critical dependent order:

```bash
scripts/run_synthetic_e2e_summary.sh
scripts/check_summary_manifest_schema_sync.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

This order must not be parallelized. The manifest sync and diagnostic
distribution checks depend on a generated no-config summary and manifest.

Other dependent relationships:

- `scripts/check_release_quality.sh` depends on the normal success-path command
  bundle and should remain fail-fast.
- `scripts/check_config_enabled_summary_smoke.sh` depends on both the
  config-enabled summary and no-config summary paths staying separate.
- `scripts/check_config_enabled_e2e_smoke.sh` depends on
  `scripts/run_synthetic_e2e_pipeline.sh`.
- `scripts/check_no_config_scoring_fixture_lock.sh` depends on generated
  synthetic E2E candidate-score outputs existing for the selected cases.
- `scripts/check_summary_manifest_schema_sync.sh` and
  `scripts/check_synthetic_diagnostic_distribution.sh` depend on
  `scripts/lib/summary_manifest_schema.sh`.

Mostly independent checks:

- `scripts/check_synthetic_policy.sh`
- `scripts/check_hand_weight_config_validation.sh`
- Python unit tests and compile checks
- Rust fmt/test/clippy checks
- logger-web typecheck/test/build checks

Even independent checks should be sequenced in the release-quality wrapper until
a task runner explicitly defines safe parallelism.

## 6. Safety Classification

Safety expectations across all scripts:

- use synthetic fixtures only
- reject or avoid private/real-data-looking paths
- print safe status, path, count, and reason metadata only
- do not print raw JSONL bodies
- do not print summary CSV bodies
- do not print manifest JSON bodies
- do not print diagnostic summary bodies
- do not print config bodies
- do not print candidate score rows
- do not print raw learner text
- do not treat expected actions as scoring feedback

Scripts that generate `tmp/` outputs:

- `scripts/run_synthetic_e2e_pipeline.sh`
- `scripts/run_synthetic_e2e_summary.sh`
- `scripts/run_synthetic_e2e_config_summary.sh`
- `scripts/check_config_enabled_summary_smoke.sh`
- `scripts/check_config_enabled_e2e_smoke.sh`
- `scripts/check_explicit_config_ranking_diff.sh`

Scripts that should remain count/status-only validators:

- `scripts/check_summary_manifest_schema_sync.sh`
- `scripts/check_synthetic_diagnostic_distribution.sh`
- `scripts/check_no_config_scoring_fixture_lock.sh`
- `scripts/check_hand_weight_config_validation.sh`
- `scripts/check_synthetic_policy.sh`

`tmp/` outputs and smoke logs must remain ignored and must not be added to Git.

## 7. Task Runner Target Candidates

Future Makefile / justfile target candidates:

- `check-release-quality`: call `scripts/check_release_quality.sh`
- `check-summary`: call `scripts/run_synthetic_e2e_summary.sh`
- `check-manifest-sync`: call `scripts/check_summary_manifest_schema_sync.sh`
- `check-diagnostic-distribution`: call
  `scripts/check_synthetic_diagnostic_distribution.sh`
- `check-summary-flow`: run summary, manifest sync, diagnostic distribution in
  the required order
- `check-config-smoke`: run config-enabled summary and E2E smoke scripts
- `check-no-config-lock`: run no-config scoring fixture lock
- `check-hand-weight-config`: run hand-weight config validation
- `check-explicit-config-diff`: run explicit config ranking diff
- `check-policy`: run synthetic policy
- `check-python`: run Python unit tests and compileall
- `check-rust`: run Rust fmt/test/clippy
- `check-logger`: run logger-web typecheck/test/build
- `check-all`: run the normal success-path release-quality bundle or compose
  its targets carefully

The first task-runner design should prefer targets that call existing scripts,
not targets that duplicate script logic.

## 8. Scripts To Keep As Shell

Good candidates to keep as shell for now:

- `scripts/check_synthetic_policy.sh`: small grep/find policy check
- `scripts/check_release_quality.sh`: stable compatibility wrapper until a task
  runner exists
- `scripts/lib/summary_manifest_schema.sh`: shared constants for shell scripts
- `scripts/check_hand_weight_config_validation.sh`: simple fixture validation
  loop
- small smoke scripts that mainly call existing CLIs and print safe summaries

Keeping these as shell avoids churn while the task-runner shape is still being
designed.

## 9. Scripts To Consider Moving Later

Potential later migration candidates:

- complex JSON validation currently embedded through Python snippets
- manifest/schema introspection
- generated summary and manifest consistency checks
- structured stage summary generation
- retry or failure classification logic
- scripts whose conditional logic continues to grow

These should move only when the replacement improves clarity without weakening
output safety.

## 10. Migration Priority

High priority:

- top-level entrypoint organization
- required summary flow target:
  `summary -> manifest-sync -> diagnostic-distribution`
- release-quality wrapper discoverability

Medium priority:

- repeated safe-output checks
- manifest/schema validation helpers
- config-enabled expected-failure smoke classification
- structured stage status summaries

Low priority:

- stable low-level smoke scripts
- simple grep/find policy checks
- shell syntax checks
- shared shell constants until a schema source-of-truth change is planned

## 11. Relation To Makefile / Justfile

This inventory is input to the next task-runner design step.
The Makefile vs justfile selection is documented in
[task runner selection design](task_runner_selection_design.md).

The recommended migration model is:

- do not delete existing shell scripts
- introduce top-level task targets that call existing scripts
- keep shell scripts as compatibility and CI-friendly layers
- preserve safe stdout and generated-output suppression
- migrate internal logic later only when complexity justifies it

A future Makefile or justfile should not become a performance report and should
not change scorer behavior, manifest schema, or fixture data.

## 12. Beginner Notes

A script inventory is a map of the scripts that already exist. It answers:
what does this script do, what does it depend on, and should it become a
top-level command?

The inventory comes before a Makefile or justfile because it is easier to design
good task names after seeing the whole command surface.

Shell scripts should not be removed immediately. They are already tested by
local and CI workflows, and a task runner can call them as stable building
blocks.

The goal is to make common commands easier to discover while preserving the
safe synthetic-only behavior that already works.

## Related Documents

- [Orchestration modernization design](orchestration_modernization_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Summary manifest sync check release integration design](summary_manifest_sync_check_release_integration_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Public release checklist](public_release_checklist.md)
