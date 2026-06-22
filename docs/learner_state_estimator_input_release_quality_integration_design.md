# Learner-State Estimator Input Release-Quality Integration Design

This document designs a future release-quality wrapper integration for the
learner-state estimator input validator Makefile target.

It is documentation only. It does not change the release-quality wrapper,
Makefile, GitHub Actions workflows, shell scripts, learner-state estimator,
estimator training, selective prediction, calibration, models, metrics,
sequence exporter, audit code, fixture files, candidate generation, OT scoring,
scoring formula, tie-break logic, or manifest schemas. It is not a performance
evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to decide how
`make check-learner-state-estimator-input` should be integrated into the
release-quality wrapper in a future step.

The design covers:

- integration candidates
- recommended wrapper position
- command choice
- expected wrapper behavior
- exit-code behavior
- output and logging policy
- tmp/output policy
- runtime and duplication analysis
- release-quality and CI implications
- risk analysis
- no-oracle and synthetic-only boundaries

This is an integration design, not an implementation step.

## 2. Current State

Current state:

- The estimator input validator Python API exists in
  `python/learner_state/estimator_input.py`.
- The CLI exists as `python -m learner_state.estimator_input`.
- The synthetic fixture root exists at
  `tests/fixtures/learner_state_estimator_input/`.
- The standalone Makefile target exists:
  `make check-learner-state-estimator-input`.
- The standalone target passes locally.
- Fixture-root validation reports 9 cases matched and 0 mismatches.
- The target creates no tmp output.
- The target prints safe human summary output only.
- Release-quality wrapper integration does not exist yet.
- GitHub Actions workflow integration does not exist yet.

The current target is a validator smoke check only. It does not train an
estimator and does not evaluate model quality.

## 3. Integration Candidates

Candidate approaches:

| Candidate | Pros | Cons |
| --- | --- | --- |
| Do not integrate yet | Keeps release-quality unchanged | Validator smoke remains outside normal wrapper |
| Add Makefile target to wrapper | Reuses local command and centralizes command policy | Adds one more wrapper step |
| Call CLI directly from wrapper | Avoids one Makefile hop | Duplicates long command and output policy |
| Add directly to CI workflow | Makes remote coverage explicit | Skips wrapper staging and requires workflow change |
| Continue standalone only | Simple and safe | Easy to forget during release checks |

Recommended future integration:

- add `make check-learner-state-estimator-input` to
  `scripts/check_release_quality.sh`
- call it through the Makefile target, not by duplicating CLI arguments
- do not change GitHub Actions workflows in the integration step
- keep the target standalone until the wrapper change is implemented and log
  safety has been reviewed

This mirrors the staged pattern already used for learner-state audit and
exporter checks.

## 4. Recommended Wrapper Position

Recommended order inside the learner-state section:

1. `make check-learner-state-audit-fixtures`
2. `make check-learner-state-exporter-cli`
3. `make check-learner-state-estimator-input`

Recommended placement relative to the full wrapper:

- after Python checks
- after learner-state audit fixture checks
- after learner-state exporter CLI smoke
- before config/scoring smoke checks
- independent of summary-flow-specific checks

Reasoning:

- audit fixtures check the no-oracle audit boundary
- exporter CLI smoke checks the generated feature/label/manifest boundary
- estimator input validation checks the exported-shape input boundary
- config/scoring smoke checks are a separate scoring infrastructure concern

This order tells a readable story in the logs without mixing estimator input
validation with scoring or performance-related checks.

## 5. Command Choice

Recommended wrapper command:

```bash
make check-learner-state-estimator-input
```

Reasons to call the Makefile target instead of the CLI directly:

- local command and wrapper command stay the same
- command changes stay localized to the Makefile
- safe output policy stays centralized
- the wrapper avoids duplicating a long CLI command
- future fixture-root changes can be handled in one place

The wrapper should not pass `--json` initially. The current human summary is
short, safe, and developer-readable.

## 6. Expected Behavior In Wrapper

Expected behavior after future integration:

- fixture-root validation discovers 9 cases
- all expected input validation results match
- wrapper continues if the target exits `0`
- mismatch, usage error, or input error fails release-quality
- output remains safe human summary only
- no tmp output is created
- no cleanup is required
- no generated output body is printed
- no fixture row body is printed
- no label or manifest body is printed

Success means the estimator input validator command path works on the
synthetic fixture root. It does not prove estimator correctness or model
performance.

## 7. Exit Code Behavior

Recommended behavior:

| Target exit code | Wrapper behavior | Meaning |
| --- | --- | --- |
| `0` | Continue | Fixture-root expected results matched |
| `1` | Fail | Reserved for future raw validation-only failure mode |
| `2` | Fail | Usage, missing file, malformed input, unsafe path, or input error |
| `3` | Fail | Expected-result mismatch |

The wrapper should not translate exit codes. It should rely on the existing
shell failure behavior, such as `set -e`, to stop on nonzero status.

## 8. Output / Logging Policy

Allowed output:

- safe human summary
- total/matched/mismatched case counts
- input error count
- reason-code counts
- `content_suppressed`
- `no_raw_rows`
- synthetic/no-oracle check flags

Forbidden output:

- raw JSONL rows
- feature row bodies
- label row bodies
- manifest bodies
- expected action bodies
- generated feature, label, or manifest bodies
- raw learner text
- private absolute paths
- raw GitHub Actions logs in public docs
- performance metrics
- model-quality claims
- artifacts

The wrapper should not use `--json` initially and should not `cat` fixture
files or validation result files.

## 9. Tmp / Output Policy

The estimator input validation target creates no tmp output.

Wrapper policy:

- do not add cleanup for this step
- do not delete broad `tmp/` paths
- do not write validation result files
- do not write artifacts
- do not cat fixture files
- do not create generated feature, label, or manifest outputs

This differs from `check-learner-state-exporter-cli`, which writes generated
outputs under `tmp/learner_state_sequence_exporter_smoke/`. Estimator input
validation reads existing synthetic fixtures only.

## 10. Runtime / Duplication Analysis

Python unittest already validates the estimator input API and CLI behavior.
The Makefile target validates the release command path.

Adding the target to release-quality introduces some duplication, but it is
acceptable because:

- the fixture root has only 9 small cases
- runtime is expected to be small
- output is short and safe
- the wrapper command path is valuable to exercise
- the Makefile target is the developer-facing smoke command

If wrapper logs become noisy later, the target can remain standalone or move to
a more selective release-quality profile.

## 11. Release-Quality / CI Implications

After future wrapper integration:

- local `make check-release-quality` will include estimator input validation
- the manual Release Quality GitHub Actions workflow will include it indirectly
  because it runs the wrapper
- no direct workflow change should be made in the first integration step
- a remote/manual run record may be useful after integration
- any public record should include only safe metadata, not raw logs

Direct CI workflow edits should be separately designed only after wrapper
integration and local log-safety review.

## 12. Risk Analysis

Risks and mitigations:

| Risk | Mitigation |
| --- | --- |
| Log exposure | CLI prints safe summaries only; wrapper should not cat files |
| Expected-result mismatch blocks release-quality | This is intended fail-closed behavior |
| Schema drift | Fixture expected-result matching surfaces drift early |
| Duplicate checks | Accept small duplication for wrapper path coverage |
| Accidental future tmp output | Target currently creates none; docs require no wrapper cleanup |
| Confusion with exporter tmp output | Keep estimator target after exporter but document no tmp output |
| Summary-flow tmp collision | Continue running `check-release-quality` and `check-summary-flow` sequentially |

The integration should be reviewed locally before any remote/manual workflow
record is created.

## 13. No-Oracle / Synthetic-Only Boundary

Safety boundary:

- fixture root is synthetic-only
- expected action remains label-side, except in intentional invalid leakage
  fixtures used as fail-closed test targets
- no expected action is used as scoring feedback
- no raw learner text
- no real participant data
- no generated dataset body in logs
- no model performance evidence
- no production or real-data readiness claim

The target validates input safety boundaries. It does not make the inputs
production-ready.

## 14. Implementation Roadmap

Recommended next steps:

1. Step201: release-quality wrapper integration implementation.
2. Step202: local release-quality run and log safety review.
3. Step203: optional remote/manual release-quality run record.
4. Step204: Milestone 08 recap or selective prediction/calibration design.

The wrapper integration should remain small: add the Makefile target command
near the existing learner-state audit/exporter checks and leave workflows
unchanged.

## 15. What This Does NOT Do

This design does not:

- implement wrapper integration
- change `scripts/check_release_quality.sh`
- change the Makefile
- change GitHub Actions workflows
- change shell scripts
- train a learner-state estimator
- evaluate a model
- implement selective prediction or calibration
- implement F1, accuracy, ECE, AURCC, or other metrics
- use real data
- change sequence exporter code
- change exporter tests
- change audit code
- change fixture files
- change candidate generation, OT scoring, scoring formula, or tie-break logic
- change manifest schemas
- claim production readiness

## 16. Beginner Notes

The release-quality wrapper is the script that runs the project's normal
release-readiness checks in one place.

The standalone Makefile target already proves the command works locally. This
design step exists before wrapper integration so the project can decide where
the command belongs, what it should print, and what success does or does not
mean.

Calling the Makefile target from the wrapper keeps the local command and the
release command identical. That reduces drift and avoids copying long command
arguments into multiple places.

Success is not performance evidence. It only means the validator read
synthetic fixture-shaped estimator inputs, matched the expected validation
contracts, and kept output safe.

## 17. Related Documents

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md)
- [Learner-state estimator input validator Makefile target design](learner_state_estimator_input_validator_makefile_target_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- [Learner-state sequence exporter release-quality integration design](learner_state_sequence_exporter_release_quality_integration_design.md)
- [Public release checklist](public_release_checklist.md)
