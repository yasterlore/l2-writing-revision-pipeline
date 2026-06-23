# Frozen Policy Generation Scaffold Runtime CLI Design

## 1. Purpose

This document designs the command-line boundary for running the frozen policy
generation scaffold runtime from a terminal.

This is a docs-only design. It does not implement the CLI, generator code,
artifact writing, metric computation, performance evaluation, or real-data
readiness.

The CLI should be a thin wrapper around the existing runtime API. It should
return safe metadata-only human or JSON summaries and must not print request
bodies, pointer bodies, artifact bodies, raw rows, logits, private paths, raw
learner text, or performance claims.

## 2. Current State

- Runtime API skeleton exists at `python/learner_state/frozen_policy_generation.py`.
- Runtime compatibility tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`.
- The runtime skeleton is compatible with the current scaffold fixture contract
  for valid 3 and invalid 8 synthetic cases.
- Runtime CLI does not exist.
- Runtime Makefile target does not exist.
- Runtime release-quality integration does not exist.
- Generator implementation does not exist.
- Artifact file writing does not exist.

## 3. Proposed CLI Entrypoint

Candidate A:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation`

Candidate B:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold`

Candidate C:

- a dedicated wrapper script

Recommended entrypoint:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation`

Rationale:

- It matches the proposed and implemented runtime module.
- It keeps the generation-facing API and CLI in the same namespace.
- It is close to the existing `learner_state.frozen_policy_generation_validation`
  naming pattern while remaining distinct from the fixture validator.
- A future generator mode can fit naturally under the same generation namespace
  without making the scaffold fixture validator own runtime behavior.

## 4. CLI Modes / Arguments

Initial arguments:

- `--request path/to/generation_request.json`
- `--pointer path/to/input_fixture_pointer.json`
- `--json`
- `--help`

Argument rules:

- `--request` and `--pointer` are both required for scaffold run mode.
- Supplying only `--request` is a usage error.
- Supplying only `--pointer` is a usage error.
- Supplying neither is a usage error.
- `--json` requests safe JSON summary output.
- The default output is a safe human-readable summary.
- No output file option should be added in the initial CLI.
- No artifact writing option should be added in the initial CLI.
- No generator mode should be added in the initial CLI.

## 5. Expected Behavior

Valid request and pointer:

- exit code `0`
- `scaffold_status=pass`
- safe metadata-only output

Invalid request and pointer that safely fail the scaffold contract:

- exit code `0`
- `scaffold_status=fail`
- expected reason code in `reason_codes`
- safe metadata-only output

Recommended behavior for invalid fixture-style inputs is exit code `0` when the
runtime successfully returns a safe fail-closed result. The CLI is not an
expected-result validator; it runs the runtime and reports the runtime result.
Compatibility tests and future fixture-oriented targets should handle expected
matching.

Usage, missing file, malformed input, or unsafe path before a safe result can
be built:

- exit code `2`
- safe usage or input-error message only
- no private path echo

Future expected-output comparison mismatch:

- exit code `3`
- reserved for a future optional comparison mode

Unexpected internal error:

- exit code `1`
- safe error category only

## 6. Exit Code Design

Recommended exit codes:

- `0`: scaffold executed and returned a safe result, including
  `scaffold_status=pass` or `scaffold_status=fail`
- `2`: usage error, missing file, malformed JSON, or path-before-load safety
  error before a safe runtime result can be built
- `3`: reserved for a future expected-output comparison mode mismatch
- `1`: unexpected internal error

Boundary for unsafe paths:

- Path-before-load safety error: exit `2`
- Loaded metadata that describes unsafe output behavior: safe fail result and
  exit `0`

This keeps command execution errors separate from expected runtime fail-closed
results.

## 7. Safe Human Output

Allowed human output fields:

- `mode`
- `scaffold_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `validation_reference_ids`
- `content_suppressed`
- `artifact_body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `generated_artifact_written`
- `generated_artifact_body_available`
- `safe_summary`
- `validation_schema_version`

Forbidden human output:

- request body
- pointer body
- expected result body
- artifact body
- raw rows
- logits or probability dumps
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance claims

## 8. Safe JSON Output

Safe JSON output should contain the same safe fields as the human summary.

Requirements:

- parseable
- deterministic enough for tests
- safe metadata only
- no request body
- no pointer body
- no expected result body
- no artifact body
- no raw rows
- no logits or probability dump
- no private paths
- no raw learner text
- no performance metric body

The JSON summary is a machine-readable safe summary, not a serialized copy of
the input files or generated policy content.

## 9. Path Safety

The CLI should reject paths that indicate real or private data before loading:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Path safety rules:

- Do not echo absolute private paths.
- Report a safe reason code or safe error category only.
- Prefer safe labels and IDs in output.
- Path-before-load safety errors exit `2`.
- Loaded metadata that requests unsafe output behavior should return
  `scaffold_status=fail` with `private_path_output` or `unsafe_path`, depending
  on the runtime reason-code vocabulary.

## 10. Relation To Runtime API

The CLI should be thin:

- call `run_frozen_policy_generation_scaffold(request_path, pointer_path)`
- call `summarize_frozen_policy_generation_scaffold_result(result)`
- format the safe summary as human or JSON output

The CLI should not:

- duplicate runtime safety logic
- run the generator
- write artifact files
- create artifact bodies
- compute metrics
- inspect real data

## 11. Relation To Fixture Validator

The runtime CLI is not the scaffold fixture validator.

The fixture validator checks fixture root structure, expected result metadata,
reason-code alignment, and safe fixture contracts. The runtime CLI returns a
runtime result for one request and pointer pair.

Compatibility tests should continue to handle expected matching by comparing
runtime summaries with `expected_scaffold_result.json` through the fixture
validator comparison helper.

A future `--expected` comparison mode may be designed separately. It should not
be part of the initial runtime CLI.

## 12. Relation To Release Quality

The runtime CLI should not be added to release-quality immediately.

Recommended staging:

- implement standalone runtime CLI tests
- design and implement a runtime Makefile target
- perform log safety review
- design release-quality integration
- only then consider wrapper integration

Release-quality success for this CLI would mean runtime scaffold safety and
compatibility checks passed. It would not be generator performance evidence.

## 13. Tests For Future Implementation

Future CLI tests should cover:

- `--help` exits `0`
- no args exits `2`
- request only exits `2`
- pointer only exits `2`
- valid request and pointer human output exits `0`
- valid request and pointer JSON output exits `0` and is parseable
- invalid request and pointer returns `scaffold_status=fail`, expected reason
  code, and exit `0`
- malformed request exits `2` or returns safe `input_error` according to the
  final implementation boundary
- malformed pointer exits `2` or returns safe `input_error` according to the
  final implementation boundary
- missing request path exits `2`
- missing pointer path exits `2`
- unsafe path is rejected without echoing the path
- stdout and stderr contain no body leakage
- output ordering is deterministic enough for tests

## 14. No-Oracle / Synthetic-Only Boundary

Initial CLI tests should use only synthetic scaffold fixtures.

The CLI must not use or print:

- real data
- raw learner text
- final text
- observed-after text
- gold labels
- expected action as scoring feedback
- test-derived tuning
- artifact bodies
- logits dumps
- raw rows

## 15. What This Does NOT Do

This design does not:

- write artifacts
- implement generator code
- add a Makefile target
- integrate release-quality
- change GitHub Actions workflows
- change fixtures
- compute metrics
- use real data
- prove performance

Step268 implementation status:

The minimal runtime CLI now exists in
`python/learner_state/frozen_policy_generation.py` and is exercised by
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`.
The entrypoint is `PYTHONPATH=python python3 -m
learner_state.frozen_policy_generation`. It supports `--request`, `--pointer`,
`--json`, and `--help`, and emits only safe metadata-only summaries.

The implementation still does not add a runtime Makefile target,
release-quality runtime integration, GitHub Actions workflow changes, fixture
changes, generator code, artifact file writing, artifact body generation,
metric computation, real-data use, or performance claims.

Step269 follow-up:

[Frozen policy generation scaffold runtime Makefile target design](frozen_policy_generation_scaffold_runtime_makefile_target_design.md)
defines the future standalone Makefile smoke target around this CLI. It keeps
the target docs-only, recommends a single synthetic valid fixture pair for the
initial smoke command, and keeps release-quality runtime integration as a later
step.

Step270 implementation status:

The standalone runtime CLI Makefile target now exists as
`check-learner-state-frozen-policy-generation-scaffold-runtime`. It runs this
CLI over the synthetic `valid/minimal_fixed_threshold_dry_run` request and
pointer pair and emits the safe human summary. Release-quality runtime
integration remains a later step.

Step271 follow-up:

[Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
defines the future wrapper placement for this CLI smoke target after scaffold
fixture validation and before config/scoring smoke checks. It remains
docs-only and does not change the wrapper, workflows, Makefile, Python code,
tests, fixtures, generator behavior, artifact writing, metrics, real-data use,
or performance claims.

Step272 implementation status:

The release-quality wrapper now calls
`make check-learner-state-frozen-policy-generation-scaffold-runtime` through
the wrapper label `release_quality_check: learner-state frozen policy
generation scaffold runtime smoke`. The CLI remains a safe metadata-only
runtime smoke path and still does not invoke a generator or write artifacts.

## 16. Beginner-Friendly Explanation

A CLI is the command a developer can run in a terminal. For this runtime, the
CLI would let a developer provide a safe generation request file and a safe
input pointer file, then receive a safe scaffold result.

The runtime CLI differs from the validator CLI. The runtime CLI runs the
scaffold logic for one request and pointer pair. The validator CLI checks a
fixture root and confirms that expected outcomes match fixture design.

An invalid fixture can still exit `0` because the command succeeded if it
returned a safe fail-closed runtime result. The failure belongs to the scaffold
status, not necessarily to the shell command.

JSON output still must not include bodies because JSON can leak data just as
easily as human text. The JSON mode is for safe metadata, not raw input or
artifact payloads.

The CLI should not enter release-quality immediately because its standalone
tests and logging behavior need to settle first.

## 17. Next Recommended Steps

Recommended next step:

- runtime release-quality wrapper integration implementation

Then proceed with:

- remote/manual status marker design if needed

Generator implementation should remain a separate later stage.

## 18. Update History

- Step267: initial docs-only frozen policy generation scaffold runtime CLI
  design.
- Step268: recorded the minimal runtime CLI implementation status.
- Step269: linked the docs-only runtime CLI Makefile target design.
- Step270: recorded the standalone runtime CLI Makefile target implementation
  status.
- Step271: linked the docs-only runtime release-quality integration design.
- Step272: recorded release-quality wrapper integration status for the runtime
  smoke target.

## Related Documents

- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold runtime Makefile target design](frozen_policy_generation_scaffold_runtime_makefile_target_design.md)
- [Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation scaffold runtime release-quality remote run record workflow](frozen_policy_generation_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- `python/learner_state/frozen_policy_generation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`
- [Public release checklist](public_release_checklist.md)
