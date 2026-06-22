# Learner-State Sequence Audit CLI Integration Design

This document designs how the learner-state sequence audit CLI should be
integrated into local task entrypoints, release-quality checks, and CI over
time.

This is integration design documentation only. It does not change Makefile
targets, the release-quality wrapper, GitHub Actions workflows, shell scripts,
audit code, fixture files, candidate generation, OT scoring, scoring formula,
tie-break behavior, existing manifest schemas, or production data handling. It
does not add a sequence exporter, learner-state estimator, model, metric, F1,
accuracy, calibration, ECE, or AURCC. It is not a performance evaluation.

## 1. Purpose

The purpose of this document is to plan how the existing learner-state sequence
audit CLI should connect to:

- the Makefile command surface
- the release-quality wrapper
- CI or manual workflow checks

The plan keeps the audit's safe output and no-oracle boundaries intact. The CLI
should remain a small verification tool for synthetic fixtures, not a research
performance claim and not a production data gate.

## 2. Current State

Current state:

- the audit module exists in `python/learner_state/sequence_audit.py`
- the CLI exists as `python -m learner_state.sequence_audit`
- fixture tests exist under `python/learner_state/tests/`
- CLI tests exist under `python/learner_state/tests/`
- synthetic audit fixtures live under
  [`tests/fixtures/learner_state_sequence_audit/`](../tests/fixtures/learner_state_sequence_audit/README.md)
- the CLI supports dataset mode, fixture-case mode, fixture-root mode, and
  `--json`
- output is safe/count-only
- Makefile has no learner-state audit fixture target yet
- release-quality wrapper integration has not been added
- CI workflow integration has not been added

The normal Python unittest command already exercises the module and CLI tests.
The remaining question is when to expose the CLI through higher-level project
entrypoints.

## 3. Integration Candidates

| Candidate | Description | Pros | Cons | Fit now |
| --- | --- | --- | --- | --- |
| A. Makefile target only | Add a local target that runs fixture-root mode | Easy to discover, low blast radius, no workflow change | Adds another top-level target | Best first step |
| B. Release-quality wrapper | Add CLI fixture-root check to the success-path bundle | Makes release checks include CLI behavior | Wrapper change increases release-quality surface | Good after Makefile target is stable |
| C. CI workflow direct command | Add CLI command directly to GitHub Actions | Immediate remote enforcement | Bypasses local entrypoint policy and duplicates unittest coverage | Too early |
| D. Makefile target -> wrapper -> CI | Stage integration through local, release, then remote checks | Keeps risk small and behavior observable | Takes more steps | Recommended |
| E. Python unittest only | Leave coverage in test suite | No new integration surface | CLI remains less visible to developers | Acceptable short pause, but not final |

Recommended candidate: D, staged integration from Makefile target to
release-quality wrapper to CI consideration.

## 4. Recommended Integration Order

Recommended order:

1. Step 169: add a Makefile target named
   `check-learner-state-audit-fixtures`.
2. Step 170: review or implement release-quality wrapper integration after the
   Makefile target is stable.
3. Step 171: consider CI or manual workflow integration after local and wrapper
   behavior is predictable.
4. Later: keep sequence exporter, selective prediction, and estimator work in
   separate research-pipeline steps.

Do not add the CLI directly to release-quality or CI first. The CLI is new, and
the safest path is to expose it locally, confirm logs stay safe, then decide
whether it belongs in the wrapper and remote workflows.

## 5. Proposed Makefile Target

Proposed target:

```bash
make check-learner-state-audit-fixtures
```

Proposed command:

```bash
PYTHONPATH=python python3 -m learner_state.sequence_audit --fixture-root tests/fixtures/learner_state_sequence_audit
```

Initial target policy:

- use human-readable safe summary output
- do not use `--json` initially
- do not print JSONL rows
- do not print label bodies
- do not print manifest bodies
- do not print raw learner text
- do not print expected action body
- treat invalid fixtures as success only when expected results match
- treat any nonzero CLI exit as target failure

The target should be a thin wrapper over the CLI. It should not duplicate audit
logic or read fixture files itself.

## 6. Release-Quality Integration Considerations

The current release-quality wrapper represents the normal success path. The
learner-state audit CLI fixture-root mode can fit that model because invalid
fixtures are expected failures and return success when expected results match.

Release-quality integration should wait until the Makefile target is stable.
When added, the wrapper should run fixture-root mode, not direct invalid
dataset mode. Direct invalid dataset mode intentionally exits `1`, so it would
be a poor fit for the wrapper's success-path command bundle.

Expected wrapper behavior:

- fixture-root match -> wrapper continues
- expected result mismatch -> wrapper fails
- malformed or missing fixture input -> wrapper fails
- CLI usage error -> wrapper fails
- safe summary only in logs

The wrapper should not include `--json` unless a future machine-readable
release summary requires it.

## 7. CI Integration Considerations

Python unittest already covers fixture and CLI behavior. A direct CI command
would duplicate part of that coverage.

If remote integration is added later, prefer one of these paths:

1. CI calls the release-quality wrapper after the wrapper includes the CLI
   check.
2. CI calls a Makefile target if project policy has moved CI entrypoints toward
   Makefile.

Avoid adding a long direct CLI command to CI before local and wrapper entrypoints
settle. CI logs must remain safe and count-only, with no raw fixture body,
label body, manifest body, private path, or expected action body.

## 8. Output / Logging Policy

Initial integration should use human-readable safe summary output.

Allowed output:

- audit status
- fixture case counts
- matched and mismatched counts
- reason code counts
- `content_suppressed`
- `no_raw_rows`

Forbidden output:

- raw rows
- JSONL body
- label body
- manifest body
- candidate score rows
- raw learner text
- expected action body
- private absolute paths
- raw stack traces with row content
- performance metrics

`--json` should remain optional for manual debugging or future machine-readable
integration, not the default release-quality log format.

## 9. Exit Code Interpretation

Current CLI exit code policy:

| Exit code | Meaning | Integration interpretation |
| --- | --- | --- |
| 0 | Audit passed, or fixture expected pass/fail results matched | Success |
| 1 | Audit completed with safety violations | Failure in dataset mode; not expected in fixture-root mode |
| 2 | Usage error, malformed input, missing input, or empty input | Failure |
| 3 | Fixture expected-result mismatch | Failure |

Makefile and release-quality should treat any nonzero exit as failure. The
important detail is that expected-fail invalid fixtures are represented by
fixture-root mode returning `0` only when expected results match.

## 10. No-Oracle / Synthetic-Only Review

Integration must preserve these boundaries:

- fixture-root mode uses synthetic-only fixtures
- expected action remains label/evaluation-side metadata
- expected action is not scoring feedback
- expected action is not candidate generation input
- CLI integration does not change scorer logic
- CLI integration does not change candidate generation
- CLI integration does not change OT weights or tie-break behavior
- no real participant data is introduced
- no production or data-collection readiness is claimed

The CLI is an audit support tool. Passing it means synthetic fixture safety
expectations matched; it does not validate learner-state models or research
performance.

## 11. Future Implementation Roadmap

Recommended next steps:

1. Step 169: implement Makefile target
   `check-learner-state-audit-fixtures`.
2. Step 170: design or implement release-quality wrapper integration.
3. Step 171: update docs/status or perform CI integration review.
4. Later: consider CI integration through wrapper or Makefile.
5. Later: design or implement a minimal sequence exporter.
6. Later: design selective prediction and calibration.
7. Later: prototype a learner-state estimator.

Each step should keep implementation changes narrow and rerun the safe-output
checks before broader integration.

## 12. Beginner Notes

Integration means connecting a tool that already works by itself to the common
commands developers and CI run.

The CLI exists now, but that does not mean it should immediately become a
remote CI requirement. A small local Makefile target is easier to inspect and
adjust before it becomes part of release-quality or remote workflows.

A Makefile target is a named command shortcut. It helps developers run the same
safe command without memorizing the full Python invocation.

Expected-fail fixtures are intentionally unsafe synthetic examples. They count
as success in fixture-root mode only when the audit catches the intended
problem and the expected result matches.

Output safety matters because command output is often copied into issues, docs,
and CI summaries. The integration should reinforce the habit of safe
count-only logs before any real-data readiness work is considered.

## Related Documents

- [Learner-state sequence audit CLI design](learner_state_sequence_audit_cli_design.md)
- [Learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Learner-state sequence audit fixture files](../tests/fixtures/learner_state_sequence_audit/README.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Public release checklist](public_release_checklist.md)
