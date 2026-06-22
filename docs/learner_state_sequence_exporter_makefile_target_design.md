# Learner-State Sequence Exporter Makefile Target Design

This document designs a future Makefile target for the learner-state sequence
exporter CLI.

This was design documentation before Step 185. Step 185 implements the
standalone Makefile target described here, while leaving the release-quality
wrapper, CI workflows, shell scripts, exporter code, tests, audit code, and
fixture files unchanged. It is not a performance evaluation and is not a
real-data readiness claim.

## 1. Purpose

The purpose of this document is to define how a future Makefile target should
call the safe exporter CLI added in Step 183.

The design covers:

- target name
- target scope
- output directory policy
- cleanup policy
- Git safety
- safe output and logging
- relation to existing Makefile targets
- release-quality integration timing

The target should remain a thin local smoke command. It should not introduce a
learner-state estimator, model, metric, real-data path, production pipeline, or
new scoring behavior.

Step 186 follow-up: see
[Learner-state sequence exporter release-quality integration design](learner_state_sequence_exporter_release_quality_integration_design.md)
for the docs-only plan for future wrapper integration. That design recommends
calling this Makefile target from the wrapper after Python checks and the
learner-state audit fixture check, while keeping generated output under the
same narrow `tmp/` smoke root and avoiding direct CI edits initially.

Step 187 follow-up: the release-quality wrapper now calls
`make check-learner-state-exporter-cli` after the learner-state audit fixture
check and before config/scoring smoke checks. The Makefile target behavior is
unchanged, and CI workflows are still unchanged.

## 2. Current State

Current state:

- `python/learner_state/sequence_exporter.py` exists.
- The exporter CLI exists as `python -m learner_state.sequence_exporter`.
- Exporter CLI tests exist under `python/learner_state/tests/`.
- The CLI supports `--input-fixture`, `--output-dir`, and `--json`.
- The CLI writes separated `features.jsonl`, `labels.jsonl`, and
  `manifest.json` to a caller-provided output directory.
- The CLI runs audit-after-export and checks safe expected-output contract
  metadata.
- Step 185 adds the standalone `check-learner-state-exporter-cli` Makefile
  target for exporter CLI smoke checks.
- Step187 adds release-quality wrapper integration by calling the Makefile
  target from `scripts/check_release_quality.sh`.
- No CI workflow integration exists for the exporter CLI.

## Step 185 Implementation Status

Step 185 adds `check-learner-state-exporter-cli` to the Makefile.

Implemented target behavior:

- removes only `tmp/learner_state_sequence_exporter_smoke`
- exports `valid/minimal_single_participant`
- exports `valid/past_window_boundary_reset`
- writes generated outputs under `tmp/learner_state_sequence_exporter_smoke/`
- relies on the exporter CLI to run audit-after-export and contract checks
- prints only the CLI safe human summaries

The target remains the single Makefile entrypoint for exporter CLI smoke
checks. Step187 wires it into the release-quality wrapper, but does not change
the target command, exporter code, tests, audit code, fixture files,
learner-state estimator behavior, models, metrics, candidate generation,
scoring, tie-breaks, manifest schemas, or CI workflows.

## 3. Makefile Target Use Cases

Candidate use cases:

| Use case | Value | Initial target scope? |
| --- | --- | --- |
| Smoke export of minimal fixture | Exercises the smallest valid CLI path | Yes |
| Smoke export of past-window fixture | Exercises task-boundary window reset path | Yes |
| Invalid fixture failure smoke | Confirms nonzero behavior, but more command plumbing | Later |
| All exporter fixture smoke | Useful eventually, but may duplicate Python unittest | Later |
| JSON mode smoke | Useful machine-readable check, but not required initially | Later |

Initial target scope should be:

- export `valid/minimal_single_participant`
- export `valid/past_window_boundary_reset`
- use CLI default safe human summary
- rely on CLI audit-after-export and contract checks
- write only under a dedicated `tmp/` output root
- do not inspect or print generated file bodies

Invalid fixture smoke can be added later if the project wants Makefile-level
coverage of fail-closed CLI exits. Python unittest already covers invalid
fixtures more precisely.

## 4. Proposed Target Name

Candidate names:

| Target | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-exporter` | Short and readable | Could imply module tests rather than CLI smoke |
| `check-learner-state-exporter-cli` | Explicitly names CLI path | Slightly narrower than generated-output audit behavior |
| `check-learner-state-exporter-fixtures` | Mirrors fixture-oriented behavior | Less explicit that CLI is being exercised |
| `check-learner-state-sequence-exporter` | Fully descriptive | Long |

Recommended name:

```text
check-learner-state-exporter-cli
```

Reasoning:

- It clearly identifies the command path being checked.
- It avoids implying that all exporter fixtures are exhaustively tested.
- It is distinct from `check-learner-state-audit-fixtures`, which audits
  existing audit fixtures rather than exporting sequence outputs.
- It leaves room for a future broader target such as
  `check-learner-state-exporter-fixtures` if fixture discovery becomes useful.

Suggested help text:

```text
Run learner-state exporter CLI smoke checks
```

## 5. Command Design

Recommended initial commands:

```bash
PYTHONPATH=python python3 -m learner_state.sequence_exporter --input-fixture tests/fixtures/learner_state_sequence_exporter/valid/minimal_single_participant --output-dir tmp/learner_state_sequence_exporter_smoke/minimal_single_participant
```

```bash
PYTHONPATH=python python3 -m learner_state.sequence_exporter --input-fixture tests/fixtures/learner_state_sequence_exporter/valid/past_window_boundary_reset --output-dir tmp/learner_state_sequence_exporter_smoke/past_window_boundary_reset
```

Recommended initial target behavior:

- remove or prepare only the dedicated smoke output directories before running
  the CLI commands
- run the minimal fixture export
- run the past-window fixture export
- use default human output, not `--json`
- rely on CLI exit codes
- do not `cat` generated files

JSON mode can be added later if a wrapper or CI integration needs a
machine-readable summary.

## 6. Output Directory Policy

Recommended output root:

```text
tmp/learner_state_sequence_exporter_smoke/
```

Policy:

- write generated outputs only under this dedicated `tmp/` root
- never write into `tests/fixtures/learner_state_sequence_exporter/`
- never write into `manual_outputs/`
- never use `private_data/`, `real_data/`, or `participant_data/`
- never commit generated output files
- do not use user-private absolute paths in target commands

Existing output policy:

- The CLI fails closed if `features.jsonl`, `labels.jsonl`, or `manifest.json`
  already exists in the output directory.
- The Makefile target therefore needs a cleanup or fresh-output strategy.

Recommended cleanup strategy:

- remove only the dedicated smoke output root before running the two valid
  fixture smoke exports
- avoid broad cleanup patterns
- do not delete fixture directories
- do not delete `manual_outputs/`
- do not add a separate clean target initially unless repeated local use shows
  it is needed

If shell cleanup is added, it should be narrow and auditable. A future target
should avoid printing or staging generated files.

## 7. Safe Output / Logging

The Makefile target should allow only the CLI safe human summaries.

Forbidden logging behavior:

- no generated feature row body
- no generated label row body
- no generated manifest body
- no candidate score row body
- no malformed-line body
- no raw learner text
- no expected action body
- no private paths
- no performance metrics
- no raw GitHub Actions logs in public docs
- no `cat` of generated files

The target should not pass `--json` initially. Human summaries are easier to
read locally and still remain safe/count-only.

## 8. Success / Failure Interpretation

Success means:

- the exporter CLI can be invoked through the Makefile path
- the minimal valid fixture exports successfully
- the past-window valid fixture exports successfully
- generated outputs pass the learner-state sequence audit
- expected output contracts match
- CLI summaries remain safe

Failure means:

- any CLI command exits nonzero
- output directory preparation fails
- audit-after-export fails
- expected output contract matching fails
- path safety rejects the target output location

This target does not prove:

- model performance
- learner-state estimator correctness
- real-data readiness
- production data collection validity
- F1, accuracy, calibration, ECE, or AURCC evidence
- scoring model improvement

## 9. Relation To Existing Targets

Related targets:

- `check-learner-state-audit-fixtures`: audits synthetic audit fixture cases.
- `check-python`: runs Python unittest and compileall, including exporter CLI
  tests.
- `check-fixtures`: runs existing fixture/config validation checks.
- `check-release-quality`: runs the release-quality wrapper.
- `check-all`: currently delegates to `check-release-quality`.

Initial recommendation:

- add `check-learner-state-exporter-cli` as a standalone target only
- do not add it to `check-all` immediately
- do not add it to `check-release-quality` immediately
- do not modify CI workflows immediately

Reasoning:

- Python unittest already exercises exporter CLI success and invalid cases.
- A standalone target gives developers a direct local smoke command.
- Release-quality integration should wait until log safety and repeated local
  runtime are reviewed.
- Direct CI workflow edits would bypass the Makefile entrypoint and make future
  command changes harder to localize.

## 10. Release-Quality Future Plan

Recommended sequence:

1. Add the standalone Makefile target.
2. Run it locally and verify safe output.
3. Record any output/log safety notes in public-safe docs.
4. Design release-quality wrapper integration separately.
5. Integrate through the Makefile target if still useful.
6. Avoid direct CI workflow edits unless the wrapper strategy changes.

The release-quality wrapper should not call invalid fixture dataset mode
directly. If invalid fixture smoke is desired, it should be handled by a
dedicated safe command or by Python tests.

## 11. No-Oracle / Synthetic-Only Policy

The future target must preserve:

- synthetic-only input fixtures
- separated generated features and labels
- expected action as evaluation-only label data
- no expected action in generated features
- audit-after-export
- no real participant data
- no raw learner text
- no future leakage
- no scoring feedback from expected actions
- no changes to candidate generation, OT scoring, scoring formulas, tie-breaks,
  or manifest schema

Generated outputs are temporary smoke artifacts only. They are not production
datasets and must not be treated as real-data readiness evidence.

## 12. Tests Future Plan

Future coverage options:

- run the standalone Makefile target manually after adding it
- keep Python unittest as the primary detailed CLI behavior test
- optionally add a JSON output parsing smoke later
- optionally add invalid fixture nonzero smoke later
- avoid excessive release-quality duplication until the standalone target has
  proven stable

The initial Makefile target should not replace Python unit tests. It should
exercise the real CLI command path from a developer-facing entrypoint.

## 13. Beginner Notes

A Makefile target is a named command shortcut. Instead of remembering a long
Python command, a developer can run one `make ...` command.

The exporter CLI already works, but putting it immediately into
release-quality would make every release-quality run depend on this new smoke
path. A standalone target lets the team observe it first.

The output directory should be under `tmp/` because generated files are
temporary smoke artifacts. They are not source fixtures and should not be
committed.

Generated files should not be printed with `cat` because rows can become noisy
and public logs should stay safe. Counts and status are enough for this check.

A smoke test is a quick check that the main path works. It does not prove every
edge case, model quality, or production readiness.

## 14. Related Documents

- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence exporter CLI design](learner_state_sequence_exporter_cli_design.md)
- [Learner-state sequence exporter edge fixture design](learner_state_sequence_exporter_edge_fixture_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Public release checklist](public_release_checklist.md)
