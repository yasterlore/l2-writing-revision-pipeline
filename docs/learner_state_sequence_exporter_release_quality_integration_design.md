# Learner-State Sequence Exporter Release-Quality Integration Design

This document records the release-quality wrapper integration plan and Step187
implementation status for the learner-state sequence exporter CLI Makefile
target.

This was integration design documentation before Step 187. Step 187 implements
the wrapper integration described here, while leaving the Makefile, CI
workflows, exporter code, exporter tests, audit code, and fixture files
unchanged. It is not a performance evaluation and is not a real-data readiness
claim.

## 1. Purpose

The purpose of this document is to define how `make
check-learner-state-exporter-cli` is integrated into the release-quality
wrapper while preserving safe output and synthetic-only boundaries.

The design covers:

- integration options
- recommended wrapper position
- command choice
- success and failure interpretation
- `tmp/` output and cleanup policy
- safe output and logging policy
- duplication with Python unittest
- CI and manual workflow considerations
- no-oracle and synthetic-only boundaries

The integration should remain a release smoke check over synthetic fixtures. It
must not introduce a learner-state estimator, model, metric, real-data path,
production pipeline, or scoring feedback from expected actions.

## 2. Current State

Current state:

- `python/learner_state/sequence_exporter.py` exists.
- The exporter CLI exists as `python -m learner_state.sequence_exporter`.
- Exporter unit tests and CLI tests exist under `python/learner_state/tests/`.
- `make check-learner-state-exporter-cli` exists.
- The target passes locally.
- The target exports two synthetic valid fixtures:
  - `valid/minimal_single_participant`
  - `valid/past_window_boundary_reset`
- The target writes generated outputs under
  `tmp/learner_state_sequence_exporter_smoke/`.
- The target relies on exporter CLI audit-after-export and expected-output
  contract checks.
- Step 187 adds release-quality wrapper integration through the Makefile
  target.
- CI workflow integration does not exist yet.

## Step 187 Implementation Status

Step 187 adds a `learner-state exporter CLI smoke` section to
`scripts/check_release_quality.sh`.

Implemented wrapper behavior:

- calls `make check-learner-state-exporter-cli`
- runs after `make check-learner-state-audit-fixtures`
- runs before config and scoring smoke checks
- relies on the Makefile target for narrow cleanup of
  `tmp/learner_state_sequence_exporter_smoke/`
- prints only the exporter CLI safe human summaries
- does not cat generated `features.jsonl`, `labels.jsonl`, or `manifest.json`

The integration does not change CI workflows, Makefile target behavior,
exporter code, exporter tests, audit code, fixture files, learner-state
estimator behavior, models, metrics, candidate generation, scoring, tie-breaks,
or manifest schemas.

## 3. Integration Candidates

Candidate approaches:

| Candidate | Pros | Cons |
| --- | --- | --- |
| Do not integrate yet | Keeps release-quality runtime unchanged | Standalone target may be skipped by reviewers |
| Add Makefile target to wrapper | Reuses local command and centralizes output policy | Adds one more release-quality smoke step |
| Call exporter CLI directly in wrapper | Short path to command | Duplicates orchestration and tmp policy |
| Add direct CI workflow step | Makes remote coverage explicit | Bypasses wrapper and adds CI churn |
| Continue standalone Makefile operation | Low-risk local workflow | No release-quality enforcement |

Recommended option:

```text
Add `make check-learner-state-exporter-cli` to the release-quality wrapper by
calling the Makefile target rather than the CLI directly. Step187 implements
this integration.
```

Rationale:

- The standalone target is already the developer-facing entrypoint.
- The Makefile target centralizes the narrow cleanup and output root policy.
- Future command changes remain localized to the Makefile.
- The wrapper should not duplicate exporter CLI arguments.
- The wrapper logs remain short because the CLI prints safe summaries only.

The integration remains staged: Step187 adds the target to the wrapper only,
without CI workflow edits.

## 4. Recommended Wrapper Position

Recommended position:

1. Python unittest and compileall
2. learner-state audit fixture check
3. learner-state exporter CLI smoke check
4. config and scoring smoke checks
5. Rust checks
6. synthetic policy
7. logger-web checks

Reasoning:

- Python checks verify the exporter module and CLI tests first.
- The learner-state audit fixture check verifies the audit surface before
  exporter-generated outputs are smoke checked.
- The exporter CLI smoke check is related to learner-state infrastructure, not
  config/scoring smoke checks.
- Summary flow remains independent and should stay earlier in the wrapper.
- Config/scoring smoke checks are broader pipeline checks and should not be
  interleaved with learner-state exporter output setup.

The wrapper section label should be clear, for example:

```text
release_quality_check: learner-state exporter CLI smoke
```

## 5. Command Choice

Recommended command:

```bash
make check-learner-state-exporter-cli
```

The wrapper should not call `python -m learner_state.sequence_exporter`
directly.

Reasons:

- Local developer command and wrapper command stay identical.
- `tmp/learner_state_sequence_exporter_smoke/` cleanup stays in one place.
- CLI arguments stay in one place.
- Future fixture additions or output-root changes are localized.
- The wrapper remains an orchestrator, not an exporter implementation surface.

## 6. Success / Failure Interpretation

Exit interpretation:

- `0`: exporter CLI smoke passed for the configured synthetic valid fixtures.
- Nonzero: release-quality failure.

Success means:

- the Makefile target can invoke the exporter CLI
- the minimal valid fixture exports successfully
- the past-window valid fixture exports successfully
- generated outputs pass audit-after-export
- expected-output contract checks pass
- output remains safe summary only

Success does not mean:

- model performance evidence
- learner-state estimator correctness
- real-data readiness
- production data collection readiness
- F1, accuracy, calibration, ECE, or AURCC evidence
- scoring model improvement

## 7. Tmp Output / Cleanup Policy

The Makefile target uses:

```text
tmp/learner_state_sequence_exporter_smoke/
```

Policy:

- The target removes only this dedicated output root.
- The wrapper should not separately delete broader `tmp/` paths.
- The wrapper should not delete fixture directories.
- The wrapper should not touch `manual_outputs/`.
- The wrapper should not write into `private_data/`, `real_data/`, or
  `participant_data/`.
- Generated outputs remain ignored by Git and are not release artifacts.
- The target can overwrite its own prior smoke outputs by narrow cleanup.

The wrapper should treat generated outputs as temporary local smoke artifacts,
not public documentation or release assets.

## 8. Output / Logging Policy

Initial wrapper integration should use the Makefile target default output.

Policy:

- safe human summary only
- no `--json` initially
- no generated feature rows
- no generated label rows
- no generated manifest body
- no candidate score row body
- no raw rows
- no malformed-line bodies
- no private paths
- no expected action body
- no performance metrics
- no `cat` of generated files
- no GitHub Actions raw logs copied into public docs

The wrapper should print the command being run, as it does for other checks, but
should not print generated file contents.

## 9. Duplication With Python Unittest

Python tests already cover:

- exporter module behavior
- exporter CLI success paths
- invalid fixture fail-closed behavior
- safe stdout and stderr behavior

The Makefile target adds:

- developer-facing command coverage
- release wrapper command-path coverage if integrated
- confirmation that the smoke output root and cleanup policy work outside
  unittest temporary directories

This duplication is acceptable because the Makefile target is short and uses
safe summaries. Invalid fixture smoke should not be added to the wrapper
initially because Python tests already provide more precise failure assertions
without increasing release logs.

## 10. CI Considerations

The manual release-quality workflow runs the wrapper. If the wrapper calls
`make check-learner-state-exporter-cli`, the remote manual workflow will inherit
the exporter CLI smoke check.

Recommended CI posture:

- do not edit CI workflows directly in the first integration
- integrate through the wrapper only
- run the wrapper locally first
- review logs for raw row/body/private path exposure
- if merged, run the existing manual release-quality workflow
- record only public-safe remote status if a remote run is reviewed

Direct CI workflow edits should wait until wrapper integration has been stable
and the team decides the additional direct CI signal is worth the maintenance
cost.

## 11. Risk Analysis

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Generated tmp output clutter | Local workspace noise | Keep cleanup limited to `tmp/learner_state_sequence_exporter_smoke/` |
| Accidental output into fixture root | Fixture pollution | Use Makefile target path only; CLI rejects fixture-root output |
| Raw output exposure | Public log safety issue | Do not cat generated files; rely on safe CLI summaries |
| Runtime increase | Slower release-quality runs | Keep to two valid fixtures initially |
| Duplicate checks | More log lines | Avoid invalid fixture smoke in wrapper initially |
| Contract mismatch blocks release-quality | Release gate failure | Treat as desired fail-closed behavior; inspect safe reason only |
| Future schema drift | Smoke failures after schema updates | Update contracts and docs together in a later reviewed step |

## 12. No-Oracle / Synthetic-Only Review

The wrapper integration must preserve:

- synthetic valid fixture inputs only
- generated features without expected action fields
- labels separated from features
- expected action as evaluation-only label data
- audit-after-export
- no real participant data
- no raw learner text
- no future leakage
- no expected action as scoring feedback
- no candidate generation changes
- no OT scorer changes
- no scoring formula or tie-break changes
- no manifest schema changes
- no production readiness claim

The smoke target confirms the exporter CLI command path, not learner-state model
quality.

## 13. Implementation Roadmap

Recommended next steps:

1. Step 187: implement release-quality wrapper integration by adding
   `make check-learner-state-exporter-cli` to `scripts/check_release_quality.sh`.
2. Step 188: run local `make check-release-quality` and review output safety.
3. Step 189: optionally run the existing remote/manual release-quality workflow
   and create a public-safe run record.
4. Later: review whether direct CI integration is useful.
5. Later: broaden exporter fixtures or design learner-state estimator work.

The next implementation should not change Makefile target behavior, exporter
code, tests, fixtures, CI workflows, or shell wrappers beyond the
release-quality wrapper line needed for orchestration.

## 14. Beginner Notes

The release-quality wrapper is the script that runs the project checks as a
bundle before release-style review.

Calling the Makefile target from the wrapper is safer than repeating the long
Python command because the target already knows where to put temporary outputs
and how to run the two smoke fixtures.

The target writes to `tmp/` because generated exporter outputs are temporary.
They are not source fixtures and should not be committed.

Generated files are not displayed because logs can become public and row bodies
are unnecessary for this check. Status, counts, and pass/fail are enough.

A successful wrapper smoke check means the command path works for synthetic
fixtures. It does not say anything about learner-state estimator quality or
model performance.

## 15. Related Documents

- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence exporter CLI design](learner_state_sequence_exporter_cli_design.md)
- [Learner-state sequence exporter Makefile target design](learner_state_sequence_exporter_makefile_target_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Public release checklist](public_release_checklist.md)
