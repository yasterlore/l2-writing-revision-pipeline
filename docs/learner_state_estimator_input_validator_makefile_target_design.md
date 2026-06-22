# Learner-State Estimator Input Validator Makefile Target Design

This document designs a future Makefile target for the learner-state estimator
input validator CLI.

It is documentation only. It does not add the Makefile target, change
release-quality wrapper behavior, change GitHub Actions workflows, implement a
learner-state estimator, implement estimator training, add selective
prediction, add calibration, add a model, or add metrics. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define how a future Makefile target should
call the safe estimator input validator CLI added in Step197.

The design covers:

- target name
- command shape
- help text
- expected behavior
- exit-code handling
- output and logging policy
- tmp/output policy
- relation to existing Makefile targets
- release-quality integration timing

The target should remain a thin local smoke command over synthetic-only
fixtures. It should not train an estimator, evaluate model performance, read
real data, create generated datasets, change scoring behavior, or change
manifest schemas.

## 2. Current State

Current state:

- `python/learner_state/estimator_input.py` exists.
- The estimator input validator Python API exists.
- The CLI exists as `python -m learner_state.estimator_input`.
- The fixture root exists at `tests/fixtures/learner_state_estimator_input/`.
- The fixture root contains one valid fixture and eight intentional invalid
  fixtures.
- Fixture-root validation currently discovers 9 cases and matches all expected
  validation results.
- CLI output is safe count/reason-code metadata only.
- Makefile target for the estimator input validator does not exist yet.
- Release-quality integration for this validator CLI does not exist yet.

The validator is not a learner-state estimator. It validates exported-shape
feature, label, and manifest inputs before any future estimator work.

## 3. Proposed Target Name

Candidate names:

| Target | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-estimator-input` | Clear, concise, aligned with the contract name | Does not explicitly say "validator" |
| `check-estimator-input` | Short | Too broad outside the learner-state context |
| `check-learner-state-estimator-input-fixtures` | Emphasizes fixture-root matching | Longer and less focused on CLI smoke |
| `check-learner-state-estimator-input-validator` | Very explicit | Long for routine local use |

Recommended name:

```text
check-learner-state-estimator-input
```

Reasoning:

- It matches the existing documentation phrase "estimator input".
- It is short enough for local use.
- It is distinct from `check-learner-state-exporter-cli`, which exercises
  generation of exported files.
- It leaves room for future narrower targets if needed, such as a
  validator-only debug target or a JSON summary smoke target.

## 4. Proposed Command

Recommended initial command:

```bash
PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input
```

Human summary should be the initial target mode.

Human summary advantages:

- developer-readable during local runs
- already count/reason-code only
- no row body output
- no generated output files
- easy to inspect without additional JSON parsing

JSON mode remains useful later for machine-readable wrapper summaries, but it
is not necessary for the first Makefile target. A later target or wrapper step
can add:

```bash
PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input --json
```

only if script-level parsing becomes useful and log safety remains clear.

## 5. Help Text

Suggested Makefile help text:

```text
check-learner-state-estimator-input  Smoke-test learner-state estimator input validation
```

The help text should avoid implying model training, estimator correctness,
performance evaluation, real-data readiness, or production data collection.

## 6. Expected Behavior

The future target should:

- call the estimator input validator CLI in fixture-root mode
- discover fixture cases deterministically
- include the valid fixture and intentional invalid fixtures
- load each `expected_input_validation_result.json`
- compare actual validation results to expected safe metadata
- pass only when all 9 fixture cases match
- fail when any case mismatches
- fail on usage errors, missing input files, malformed input, or unsafe paths
- print only safe human summary fields

Expected fixture-root summary:

- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- safe count fields
- `content_suppressed`
- `no_raw_rows`

The target should not print feature rows, label rows, manifest bodies, expected
action bodies, generated output bodies, raw learner text, or private absolute
paths.

## 7. Exit Code Behavior

The Makefile target should use the CLI exit code directly.

Recommended interpretation:

| CLI exit code | Makefile behavior | Meaning |
| --- | --- | --- |
| `0` | Pass | Validation passed, or fixture expected results all matched |
| `1` | Fail | Reserved for a future raw validation-only failure mode |
| `2` | Fail | Usage error, missing files, malformed input, unsafe path, or input error |
| `3` | Fail | Expected-result mismatch |

The Makefile target should not translate exit codes initially. Keeping the
target thin makes local CLI behavior and Makefile behavior easier to compare.

## 8. Output / Logging Policy

Allowed output:

- safe human summary
- validation status
- reason codes
- failed check names
- row counts
- sequence counts
- split counts
- matched/mismatched case counts

Forbidden output:

- feature row body
- label row body
- manifest body
- expected action body
- generated feature, label, or manifest body
- raw learner text
- teacher or human correction body
- private absolute paths
- raw GitHub Actions logs in docs
- performance metrics
- model-quality claims

The target should not `cat` fixture files or generated files. It should not add
`--json` initially unless a later integration explicitly needs parseable
machine output.

## 9. Tmp / Output Policy

The estimator input validation target should not create tmp outputs.

Policy:

- read only from `tests/fixtures/learner_state_estimator_input/`
- do not write validation result files
- do not write generated feature, label, or manifest files
- do not use `manual_outputs/`
- do not use `tmp/` unless a future implementation explicitly needs a
  temporary copied mismatch fixture for a test, not for the target
- no cleanup is needed for the Makefile target

This differs from the exporter CLI target, which writes generated exported
files under a narrow `tmp/` smoke root. The estimator input validator only
reads existing synthetic fixtures and reports safe summaries.

## 10. Relation To Existing Makefile Targets

Related targets:

- `check-learner-state-audit-fixtures`: audits learner-state sequence audit
  fixtures.
- `check-learner-state-exporter-cli`: exports synthetic valid fixtures to a
  tmp output root and audits generated outputs.
- `check-python`: runs Python unittest and compileall, including estimator
  validator and CLI tests.
- `check-fixtures`: runs existing fixture/config validation checks.
- `check-release-quality`: runs the release-quality wrapper.

Recommended initial placement:

- add only a standalone target in the future implementation step
- do not add it to `check-release-quality` yet
- do not change `check-all` unless the repository's existing target structure
  requires it
- keep the target near other learner-state Makefile checks for discoverability

This target would provide a developer-friendly smoke command for estimator
input validation. Python unittest remains the detailed regression layer.

## 11. Release-Quality Future

Release-quality integration should be a later design and implementation step.

Recommended staged path:

1. Implement standalone `check-learner-state-estimator-input`.
2. Run it locally and review log safety.
3. Confirm it produces no tmp output and no row-body output.
4. Design wrapper integration separately.
5. If integrated later, place it near learner-state audit/exporter checks.
6. Avoid direct GitHub Actions workflow edits in the first wrapper integration
   step.

The target should not be connected to release-quality in the Makefile target
implementation step.

## 12. Testing Plan For Future Implementation

Future implementation checks:

- `make help` includes `check-learner-state-estimator-input`
- `make check-learner-state-estimator-input` exits `0`
- CLI fixture-root mode reports 9 matched cases
- stdout remains safe and count/reason-code only
- no fixture rows, label rows, manifest bodies, or expected action bodies are
  printed
- no tmp output is created by the target
- Makefile diff is limited to the new target and help text
- release-quality wrapper and workflows remain unchanged
- existing Python tests still pass

This target should complement, not replace, the fixture-based unittest suite.

## 13. No-Oracle / Synthetic-Only Boundary

Safety boundary:

- fixture root is synthetic-only
- intentional invalid fixtures are allowed only as safety test cases
- expected action remains label-side, except in intentional invalid leakage
  fixtures used to verify fail-closed behavior
- no expected action is used as scoring feedback
- no label aggregates are allowed as feature inputs
- no future episode/action fields are allowed in valid features
- no raw learner text
- no real participant data
- no model performance evidence

The Makefile target should only confirm the validator CLI can exercise these
synthetic fixture contracts safely.

## 14. What This Does NOT Do

This design does not:

- implement the Makefile target
- change the Makefile
- integrate release-quality
- change GitHub Actions workflows
- change shell scripts
- implement a learner-state estimator
- implement estimator training
- implement selective prediction or calibration
- implement F1, accuracy, ECE, AURCC, or other metrics
- use real data
- create generated outputs
- change exporter code
- change exporter tests
- change audit code
- change fixture files
- change candidate generation, OT scoring, scoring formula, or tie-break logic
- change manifest schemas
- claim production readiness

## 15. Beginner Notes

A Makefile target is a named shortcut for a terminal command. Instead of
remembering the full Python command, a developer can run one stable `make`
command.

The CLI already performs validation. The Makefile target is useful because it
gives the project a common local smoke command that is easy to document and
repeat.

This target should not create `tmp/` output because the validator only reads
existing synthetic fixtures. It is checking whether input files are safe and
consistent, not generating new dataset files.

It should not be added to release-quality immediately because the project
should first review local log safety and make sure the standalone target has
the right scope.

A smoke test is a small check that confirms an important path runs. Here, it
would confirm that fixture-root estimator input validation works through the
CLI and Makefile layers.

## 16. Related Documents

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- `python/learner_state/estimator_input.py`
- `python/learner_state/tests/test_estimator_input.py`
- `python/learner_state/tests/test_estimator_input_cli.py`
- [Learner-state sequence exporter Makefile target design](learner_state_sequence_exporter_makefile_target_design.md)
- [Public release checklist](public_release_checklist.md)
