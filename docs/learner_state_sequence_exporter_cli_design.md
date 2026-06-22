# Learner-State Sequence Exporter CLI Design

This document designs the safe command-line interface for the learner-state
sequence exporter.

This was design documentation before Step 183. Step 183 implements the minimal
CLI described here, while leaving Makefile, workflow, release-quality wrapper,
shell script, audit code, fixture, estimator, model, and metric behavior
unchanged. It is not a performance evaluation and is not a real-data readiness
claim.

## 1. Purpose

The purpose of this document is to define how a future
`python -m learner_state.sequence_exporter` command should call the existing
exporter module safely.

The design separates:

- exporter module responsibilities
- CLI argument parsing and exit behavior
- output directory handling
- audit-after-export behavior
- expected output contract checking
- safe human and JSON summaries
- no-oracle and synthetic-only boundaries

The CLI should remain a thin interface over the module. It should not duplicate
export logic or introduce model, metric, scoring, or real-data behavior.

## 2. Current Exporter State

Current state:

- `python/learner_state/sequence_exporter.py` exists.
- `valid/minimal_single_participant/` exists as the minimal valid fixture.
- Exporter edge-case fixtures exist under
  `tests/fixtures/learner_state_sequence_exporter/`.
- Exporter tests exist under `python/learner_state/tests/`.
- Edge-case tests cover the initial valid edge fixture and invalid fail-closed
  fixtures.
- The exporter can write separated `features.jsonl`, `labels.jsonl`, and
  `manifest.json` to a caller-provided output directory.
- Generated outputs are audited by `learner_state.sequence_audit`.
- Step 183 adds the minimal `python -m learner_state.sequence_exporter` CLI.
- No Makefile target or release-quality integration exists for the exporter
  CLI.

## Step 183 Implementation Status

Step 183 implements the minimal CLI entrypoint in
`python/learner_state/sequence_exporter.py` and CLI tests in
`python/learner_state/tests/test_sequence_exporter_cli.py`.

Implemented scope:

- `--input-fixture <case_dir>`
- `--output-dir <dir>`
- `--json`
- `--help`
- explicit output directory requirement
- fail-closed handling for existing generated output files
- fail-closed handling for fixture-root and unsafe output paths
- safe human summaries
- safe JSON summaries
- contract and audit result reporting through safe metadata only

The CLI still does not add a Makefile target, release-quality integration, CI
workflow integration, shell wrapper, learner-state estimator, model, metric, or
real-data handling. Public docs must continue to avoid generated JSONL bodies,
label bodies, manifest bodies, malformed-line bodies, private paths, and raw
logs.

## 3. CLI Use Cases

Candidate use cases:

| Use case | Value | Initial scope? |
| --- | --- | --- |
| Single input fixture export | Exercises existing fixture contract and exporter module | Yes |
| Explicit input files export | Useful later for non-fixture inputs | No, defer |
| Output directory export | Required to avoid writing generated outputs into fixture dirs | Yes |
| Temp output mode | Convenient for smoke checks | Defer unless implementation remains simple |
| Contract check mode | Confirms safe expected-output metadata | Yes, default for fixtures |
| Audit-after-export mode | Confirms generated feature/label/manifest outputs are safe | Yes, default |
| Safe JSON summary | Machine-readable wrapper/test output | Yes |
| Human safe summary | Local developer use | Yes |

Implemented initial CLI scope is:

- one `--input-fixture` directory
- one explicit `--output-dir`
- default contract check when a fixture contract exists
- default audit-after-export
- optional `--json` safe summary
- no explicit input-file mode yet
- no Makefile or release-quality integration yet

## 4. CLI Commands / Arguments Design

Recommended initial command shape:

```bash
python -m learner_state.sequence_exporter --input-fixture <case_dir> --output-dir <dir>
```

Optional JSON summary:

```bash
python -m learner_state.sequence_exporter --input-fixture <case_dir> --output-dir <dir> --json
```

Future argument candidates:

- `--check-contract`
- `--audit-after-export`
- `--summary-only`
- `--no-color`
- `--overwrite`
- `--fail-if-output-exists`

Initial recommendation:

- `--input-fixture` required
- `--output-dir` required
- `--json` optional
- audit-after-export always enabled
- contract check enabled when `expected_output_contract.json` is present
- default behavior should fail if output files already exist
- no color output initially
- no explicit `--overwrite` initially unless tests need it

The first implementation keeps the CLI small and easy to review.

## 5. Output Directory Policy

Output policy:

- require an explicit `--output-dir` in the first implementation
- do not write generated outputs into fixture directories
- do not write to `manual_outputs/`
- reject obviously private or real-data-looking output paths
- avoid `tmp/` as a default public command output unless the caller explicitly
  provides it
- generated outputs must not be committed from temporary or private directories
- fail if output files already exist, unless a future explicit overwrite flag is
  added
- atomic write can be considered later

The CLI should summarize output path status safely. It should not print private
absolute paths or dump generated file contents.

## 6. Output Format Design

Human summary should contain only safe fields such as:

- mode
- export status
- feature row count
- label row count
- participant/session/task/episode counts
- manifest status
- audit status
- reason codes, if any
- content suppressed flag
- no raw rows flag
- synthetic-only flag

JSON summary should use safe `ExportResult.to_safe_dict()` style fields only.
For failures, it should use safe `ExportFailureSummary.to_safe_dict()` style
fields only.

Forbidden output:

- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body
- raw rows
- malformed input lines
- private paths
- expected action body
- candidate score rows
- raw learner text
- performance metrics
- raw stack trace with row content

## 7. Exit Code Design

Implemented exit code policy:

- `0`: export succeeded, audit passed, and contract check passed when required
- `1`: export or audit failed due to input safety, no-oracle, or audit violation
- `2`: usage error, missing required argument, missing path, or malformed input
- `3`: expected output contract mismatch

- missing input files and malformed input map to `2`
- other fail-closed exporter validation errors map to `1`
- unsafe output paths and existing output files map to `1`
- contract mismatches map to `3`

The command must not silently pass unknown failures.

## 8. Audit Integration

Audit behavior should be default-on.

Policy:

- generated `features.jsonl`, `labels.jsonl`, and `manifest.json` are audited
  after export
- audit failure exits nonzero
- audit result is summarized with safe/count-only metadata
- raw generated rows are not printed
- audit fixture-root mode is separate from exporter CLI mode
- exporter output audit uses the generated output files, not audit fixtures

The CLI should call exporter module APIs rather than invoking the audit CLI as a
subprocess.

## 9. Expected Output Contract Handling

If the input fixture has `expected_output_contract.json`, the CLI should check:

- feature row count
- label row count
- participant/session/task/episode counts
- schema version expectations
- audit status
- content suppression
- no-raw-rows flag

Contract mismatch should exit with code `3`.

If no contract exists, initial implementation options are:

- fail closed for fixture mode
- or skip with a safe warning

Recommended initial policy: fail closed for `--input-fixture` mode when the
contract is missing. This keeps fixture smoke checks deterministic.

The CLI should not compare or print full generated bodies.

## 10. Failure Behavior

The CLI should fail nonzero for:

- missing input file
- malformed JSON
- malformed JSONL
- empty required input
- unknown input schema version
- feature-side expected action leakage
- audit failure after export
- expected output contract mismatch
- unsafe input or output path
- unexpected exception

Failure summaries should include safe reason codes only. They should not include
raw row bodies, malformed-line bodies, label bodies, manifest bodies, private
paths, or full stack traces with content.

## 11. Path Safety

Path policy:

- reject input/output paths containing real-data or private-data path segments
- reject `real_data`, `participant_data`, and `private_data` as input/output
  sources
- avoid `manual_outputs/` as a generated output location
- do not expose private absolute paths in stdout/stderr
- summarize paths by safe role or sanitized case label
- fixture paths under `tests/fixtures/learner_state_sequence_exporter/` are
  synthetic-only test inputs

Future real-data handling, if ever considered, needs a separate readiness
review and should not reuse this public fixture CLI path.

## 12. Tests

CLI tests now cover:

- `--help`
- minimal fixture export exits `0`
- `past_window_boundary_reset` exits `0`
- invalid fixtures exit expected nonzero
- `--json` output is parseable safe JSON
- existing output directory behavior
- missing required arguments exit nonzero
- unsafe output path failure
- stdout/stderr do not contain raw rows
- stdout/stderr do not contain malformed-line bodies
- stdout/stderr do not contain label bodies or manifest bodies
- stdout/stderr do not expose private absolute paths

The tests use temporary output directories only.

## 13. Makefile / Release-Quality Future Plan

Recommended staged plan:

1. Step 183: exporter CLI implementation and CLI tests.
2. Step 184: Makefile target design.
3. Step 185: Makefile target implementation.
4. Step 186: release-quality integration review.
5. Later: optional release-quality wrapper integration after CLI behavior
   remains stable.

The exporter CLI should not be added directly to release-quality until the
command behavior, exit codes, and log safety have stabilized.

## 14. No-Oracle / Synthetic-Only Policy

The CLI must preserve:

- synthetic-only fixture inputs
- separated feature and label outputs
- expected action as evaluation-only label data
- no expected action in features
- no expected action as scorer or ranking feedback
- no future episode leakage
- no final outcome features
- no raw learner text
- no real participant data
- no production data pipeline behavior

The CLI does not change candidate generation, scoring formulas, tie-breaks,
diagnostics, or manifest schemas.

## 15. Public Docs / Logging Policy

Public docs may show command shapes, argument names, safe field names, and
policy summaries.

Public docs and logs must not include:

- generated JSONL bodies
- generated manifest bodies
- label bodies
- raw logs
- raw learner text
- malformed-line contents
- private paths
- expected action bodies
- performance claims

Public summaries should remain count-only or status-only.

## 16. Beginner Notes

A CLI is a command-line interface. It lets a developer run the exporter from a
terminal instead of calling Python functions directly.

The exporter module does the real work: reading safe inputs, generating
features and labels, writing a manifest, and auditing the result. The CLI should
only parse arguments, call the module, and print a safe summary.

An output directory is required so generated files do not accidentally overwrite
fixtures or get committed from the wrong location.

The audit runs after export because generated files need a safety check before
they are used by later research code.

Generated bodies are not printed because command output and docs can become
public. Counts, status, and reason codes are enough for this stage.

## 17. Related Documents

- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence exporter input fixture design](learner_state_sequence_exporter_input_fixture_design.md)
- [Learner-state sequence exporter edge fixture design](learner_state_sequence_exporter_edge_fixture_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit CLI design](learner_state_sequence_audit_cli_design.md)
- [Public release checklist](public_release_checklist.md)
