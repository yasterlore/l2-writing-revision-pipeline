# Learner-State Sequence Audit Release-Quality Integration Design

This document designs how the existing learner-state sequence audit Makefile
target may be integrated into the release-quality wrapper in a future step.

This is integration design documentation only. It does not change
`scripts/check_release_quality.sh`, the Makefile, GitHub Actions workflows,
shell scripts, audit code, fixture files, candidate generation, OT scoring,
scoring formula, tie-break behavior, manifest schemas, or production data
handling. It does not add a sequence exporter, learner-state estimator, model,
metric, F1, accuracy, calibration, ECE, or AURCC. It is not a performance
evaluation.

## 1. Purpose

The purpose of this document is to decide whether and how the learner-state
audit Makefile target should be added to the release-quality wrapper later.

The design focuses on:

- confirming the target is safe before wrapper integration
- preserving no-oracle and synthetic-only boundaries
- keeping release-quality logs safe and count-only
- avoiding a research performance claim
- avoiding direct CI workflow changes in the initial integration

## 2. Current State

Current state:

- the audit module exists in `python/learner_state/sequence_audit.py`
- the CLI exists as `python -m learner_state.sequence_audit`
- CLI tests exist under `python/learner_state/tests/`
- fixture tests exist under `python/learner_state/tests/`
- the Makefile target `check-learner-state-audit-fixtures` exists
- the target runs fixture-root mode over
  `tests/fixtures/learner_state_sequence_audit`
- release-quality wrapper integration has not been added
- CI workflow integration has not been added

The target currently gives developers a local command path for the same safe
CLI behavior tested by Python unittest.

## 3. Integration Decision

Candidate decisions:

| Option | Description | Pros | Cons | Recommendation |
| --- | --- | --- | --- | --- |
| Do not integrate yet | Keep the target manual-only | Lowest release-quality surface | Release checks do not exercise the Makefile target | Acceptable short pause |
| Wrapper calls Makefile target | Add `make check-learner-state-audit-fixtures` to the wrapper | Reuses local entrypoint, keeps command centralized | Adds one more wrapper section | Recommended next implementation |
| Wrapper calls CLI directly | Add the Python CLI command directly | Avoids nested make invocation | Duplicates command string and bypasses Makefile entrypoint | Not preferred |
| CI workflow direct command | Add direct CLI command to workflow | Remote enforcement | Too early, duplicates tests, bypasses wrapper | Not recommended now |

Recommended decision: integrate through the Makefile target, not by calling the
CLI directly and not by editing CI first.

## 4. Recommended Wrapper Position

Possible wrapper positions:

| Position | Fit | Notes |
| --- | --- | --- |
| Before Python checks | Weak | CLI depends on Python module import and should run after Python sanity checks |
| After Python checks | Strong | unittest and compileall confirm Python code shape first |
| Near fixture/config smoke checks | Strong | learner-state audit fixtures are fixture-oriented synthetic checks |
| Before summary flow | Weak | unrelated to summary generation and shared `tmp/` preconditions |
| Near synthetic policy checks | Medium | both are safety checks, but fixture expected-result matching fits better near fixture checks |

Recommended position: after the existing Python checks and before or at the
start of the current config and scoring smoke section.

Reasoning:

- Python unittest and compileall should pass before running the CLI command.
- The target is fixture-oriented and belongs near other fixture/config checks.
- It does not depend on synthetic E2E summary `tmp/` outputs.
- It should not be interleaved into the summary flow.

Possible future wrapper section name:

```text
release_quality_check: learner-state audit fixtures
```

## 5. Command Choice

Recommended command:

```bash
make check-learner-state-audit-fixtures
```

Do not call the CLI directly from the wrapper initially.

Reasons to call the Makefile target:

- local developer command and wrapper command remain the same
- future CLI command changes stay localized in the Makefile
- wrapper stays focused on release-quality orchestration
- command discovery remains available through `make help`
- target output has already been verified as safe human summary output

The wrapper should not use `--json` initially. Human-readable safe summary is
enough for release-quality logs.

## 6. Success / Failure Interpretation

Expected interpretation:

| Result | Meaning | Wrapper behavior |
| --- | --- | --- |
| exit `0` | fixture expected results matched | continue |
| nonzero | mismatch, usage error, malformed input, missing input, or unsafe unexpected state | fail |

Important details:

- invalid expected-fail fixtures are success only when expected results match
- expected-result mismatch should fail the wrapper
- malformed input should fail the wrapper
- missing fixture files should fail the wrapper
- direct invalid dataset mode should not be used in the wrapper

Fixture-root mode is the correct wrapper command because it converts expected
invalid cases into a safe success-path check when the audit catches them as
expected.

## 7. Output / Logging Policy

Wrapper integration should use safe human summary output only.

Allowed output:

- aggregate audit status
- total case count
- matched and mismatched counts
- reason code counts
- `content_suppressed`
- `no_raw_rows`

Forbidden output:

- raw rows
- JSONL body
- label body
- manifest body
- fixture file body
- candidate score rows
- raw learner text
- expected action body
- private absolute paths
- performance metrics
- raw stack traces with content

The wrapper should not `cat` fixture files, JSONL files, manifests, labels, or
expected-result files.

## 8. Duplication With Python Unittest

Python unittest already checks the audit module, fixture expected-result
matching, and CLI behavior.

Adding the Makefile target to release-quality still has value because it tests:

- the actual top-level developer command
- the CLI command path outside unittest subprocess helpers
- wrapper compatibility with the Makefile target
- release-quality log safety for the command

The duplication is acceptable if the output stays short. If logs become noisy,
keep the target manual-only or reconsider wrapper placement.

## 9. CI Considerations

The manual release-quality workflow already runs the wrapper. If the wrapper
later includes the Makefile target, manual workflow runs will inherit this check
without direct workflow edits.

Initial CI policy:

- do not edit CI workflows first
- do not add a direct long CLI command to CI
- prefer wrapper or Makefile entrypoint if remote integration is needed
- monitor runtime and log safety after wrapper integration
- keep direct CI integration as a later review item

If the check proves redundant or noisy in wrapper logs, it can remain a
manual-only Makefile target.

## 10. Risk Analysis

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Raw output exposure | Sensitive or row-like content could enter logs | Use Makefile target safe summary only; do not `cat` fixture files |
| Expected-fail confusion | Invalid fixtures may look like release failures | Document that fixture-root mode succeeds when expected failures match |
| Duplicated checks | unittest and wrapper both exercise fixtures | Accept short redundancy because wrapper tests the top-level command path |
| Target failure blocks release-quality | New fixture expectation mismatch could fail release checks | Treat this as intended fail-closed behavior after integration |
| Future schema changes break fixtures | Fixture expected results may require updates | Update fixture expectations with schema changes in a scoped step |
| CI log noise | Remote workflow logs may become too verbose | Start local/wrapper first; avoid direct CI command initially |

## 11. No-Oracle / Synthetic-Only Review

The proposed wrapper integration preserves these boundaries:

- fixture-root uses synthetic fixtures only
- expected action remains label/evaluation-side metadata
- expected action is not scoring feedback
- expected action is not candidate generation input
- scorer logic remains unchanged
- candidate generation remains unchanged
- OT scoring formula and tie-break behavior remain unchanged
- no real participant data is introduced
- no production or data-collection readiness is claimed

Passing the check means fixture expected results matched. It does not validate
learner-state models, research performance, or data-collection readiness.

## 12. Implementation Roadmap

Recommended next steps:

1. Step 171: implement release-quality wrapper integration by adding a wrapper
   section that calls `make check-learner-state-audit-fixtures`.
2. Step 172: run release-quality locally and record only safe/count-only
   results in docs if documentation is needed.
3. Step 173: consider docs/status update or remote manual workflow check.
4. Later: review CI integration after wrapper behavior is stable.
5. Later: continue sequence exporter planning separately.

The implementation step should not edit CI workflows or audit code.

## 13. Beginner Notes

The release-quality wrapper is a script that runs the normal set of checks used
before treating the repository as release-ready.

Calling the Makefile target from the wrapper keeps one common command for local
developers and release checks. If the command changes later, the Makefile can be
updated without rewriting the wrapper command.

Expected-fail fixtures are intentionally unsafe synthetic examples. They are
successful in fixture-root mode only when the audit catches the intended
problem and the expected result file agrees.

Log safety matters because release-quality output may be copied into issues,
summaries, or remote workflow logs. The wrapper should show only safe status and
counts, never fixture bodies.

CI workflow edits should wait because the wrapper already gives a controlled
place to test the integration locally and through the manual release-quality
workflow later.

## Related Documents

- [Learner-state sequence audit CLI integration design](learner_state_sequence_audit_cli_integration_design.md)
- [Learner-state sequence audit CLI design](learner_state_sequence_audit_cli_design.md)
- [Learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture files](../tests/fixtures/learner_state_sequence_audit/README.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Public release checklist](public_release_checklist.md)
