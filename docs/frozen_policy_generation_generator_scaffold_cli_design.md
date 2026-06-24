# Frozen Policy Generation Generator Scaffold CLI Design

This document defines the Step292 docs-only design for a future command-line
interface over the metadata-only frozen policy generation generator scaffold.

The CLI should run the implemented skeleton on one synthetic request and input
pointer pair, then print only safe metadata. It must not print request bodies,
pointer bodies, expected result bodies, policy bodies, artifact bodies, raw
rows, logits, private paths, raw learner text, or performance metric bodies.

This is not an implementation. It does not add Python code, Python tests,
fixtures, Makefile targets, release-quality wrapper changes, GitHub Actions
workflow changes, artifact writing, artifact body generation, generated policy
body generation, metric computation, performance evaluation, or real-data
readiness.

## 1. Document Purpose

The purpose of this document is to design a safe future CLI for the implemented
generator scaffold skeleton.

The design covers:

- CLI entrypoint
- required arguments
- safe example commands
- expected pass and fail-closed behavior
- exit-code interpretation
- safe human output
- safe JSON output
- no-body-leakage policy
- relationship to skeleton APIs and fixture validator CLI
- future CLI tests
- future Makefile, release-quality, and status-marker staging

This document is not:

- CLI implementation
- artifact writer implementation
- artifact body generation
- generated policy body generation
- performance evaluation
- calibration implementation
- selective prediction implementation
- learner-state estimator implementation
- metric computation
- real-data readiness claim
- production readiness claim

## 2. Current State

Current state:

- skeleton module exists at
  `python/learner_state/frozen_policy_generation_generator_scaffold.py`
- skeleton tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_generator_scaffold.py`
- fixture validator exists
- fixture validator CLI exists
- fixture validator Makefile target exists
- fixture validator release-quality wrapper integration exists
- skeleton CLI does not exist yet
- skeleton Makefile target does not exist yet
- skeleton release-quality integration does not exist yet
- artifact writer does not exist

Current skeleton behavior:

- valid 3 generator scaffold fixture cases return pass metadata
- invalid 15 generator scaffold fixture cases return expected fail-closed
  metadata
- results are compatible with `expected_generator_scaffold_result.json`
  metadata
- output is deterministic and JSON serializable
- no artifact body is generated
- no generated policy body is generated
- no files are written
- no tmp output is created

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold
```

Rationale:

- it matches the implemented module name
- it directly invokes the generator scaffold skeleton boundary
- it stays distinct from the generator scaffold fixture validator CLI
- it remains inside the existing `learner_state` namespace
- it is suitable for a future standalone Makefile target

The initial CLI should not add a separate executable script.

## 4. Proposed CLI Arguments

Minimum arguments:

- `--request`
- `--pointer`
- `--json`
- `--help`

Argument rules:

- `--request` and `--pointer` are both required
- supplying only `--request` is a usage error
- supplying only `--pointer` is a usage error
- supplying neither is a usage error
- `--json` is optional
- default output is a safe human summary
- no output-file option is included in the initial CLI
- no artifact body output option is included
- no artifact file writing option is included
- no manifest writing option is included

Path arguments should be treated as untrusted input. Public output should use
safe IDs and labels instead of echoing private or absolute paths.

## 5. Example Commands

Valid metadata-only fixture:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/input_fixture_pointer.json
```

Valid metadata-only fixture with safe JSON output:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/input_fixture_pointer.json --json
```

Invalid fixture expected to fail closed:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/invalid/test_temperature_tuning/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/invalid/test_temperature_tuning/input_fixture_pointer.json
```

These examples identify synthetic fixture files only. They do not show file
bodies, generated policy bodies, artifact bodies, raw rows, logits, private
paths, or performance metric content.

## 6. Expected Behavior

Valid case:

- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- exit code `0`
- no artifact body
- no generated policy body
- no file writing

Invalid expected fail-closed case:

- `generation_status=fail`
- expected reason code is shown
- `safe_summary=fail_closed_metadata_only_generator_scaffold_result`
- exit code `0` when a safe fail-closed result is produced as expected
- no artifact body
- no generated policy body
- no file writing

Malformed or missing input:

- safe input-error result or usage error
- exit code `2`
- no raw input body echo
- no private path echo

Unexpected mismatch or safety-audit mismatch:

- exit code `3` when a result is produced but violates the metadata contract
  or safety audit

Unexpected internal error:

- exit code `1`
- safe error category only

## 7. Exit Code Design

Recommended exit codes:

- `0`: skeleton ran and returned an expected safe metadata result
- `2`: usage error or input error
- `3`: metadata result mismatch or safety audit mismatch
- `1`: unexpected internal error

Interpretation:

- expected invalid fixtures can exit `0` because they are safe fail-closed
  contract examples
- unsafe payload detected and safely rejected can exit `0` when it matches the
  fixture expectation
- malformed unreadable input exits `2`
- generated artifact body requests and file-writing attempts must fail closed
  without writing files
- the CLI should not turn mismatches into success

## 8. Safe Human Output

Allowed human output fields:

- `mode=generator_scaffold`
- `generation_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- artifact flags
- safety flags
- `count_summary`
- `safe_summary`
- `schema_version`

Forbidden human output:

- request body
- pointer body
- expected result body
- policy body
- generated policy body
- artifact body
- manifest body
- raw rows
- logits
- probabilities
- raw learner text
- final text
- observed-after text
- gold text
- private paths
- performance metric body

Human output should be short and deterministic enough for tests. It should not
print serialized input files.

## 9. Safe JSON Output

Safe JSON output should contain the same safe fields as the human summary.

Requirements:

- parseable JSON object
- deterministic field set and ordering where practical
- safe scalar values, booleans, IDs, reason codes, flag summaries, and count
  summaries
- no request body
- no pointer body
- no expected result body
- no policy body
- no generated policy body
- no artifact body
- no raw rows
- no logits
- no private paths

JSON output is a machine-readable safe summary. It is not permission to print
fixture bodies or generated artifact content.

## 10. No-Body-Leakage Policy

CLI stdout and stderr must not include:

- `generation_request.json` body
- `input_fixture_pointer.json` body
- `expected_generator_scaffold_result.json` body
- generated policy body
- artifact body
- manifest body
- raw rows
- logits or probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold text
- performance metric body

Error messages should report safe categories such as `usage_error`,
`input_error`, `metadata_mismatch`, `safety_audit_mismatch`, or
`internal_error`, plus safe reason codes and IDs where available.

## 11. Relation To Skeleton APIs

The CLI should be thin.

It should call:

- `run_frozen_policy_generation_generator_scaffold`
- `summarize_frozen_policy_generation_generator_result`
- `audit_frozen_policy_generation_generator_safety`

The CLI should not:

- duplicate core generator scaffold logic
- write files
- emit artifact bodies
- emit generated policy bodies
- compute metrics
- execute an artifact writer
- inspect raw rows
- inspect logits
- inspect real data

## 12. Relation To Fixture Validator CLI

The fixture validator CLI checks the fixture contract for a root or case.

The generator scaffold CLI should run the skeleton on one request and pointer
pair. It should return the skeleton's safe metadata result, not revalidate the
entire fixture root.

Current staging:

- fixture validator CLI is implemented
- fixture validator target is included in release-quality
- generator scaffold CLI is not implemented
- generator scaffold runtime smoke is not release-quality integrated

Expected-result comparison can stay in tests and fixture validation helpers.
The initial skeleton CLI should not add an expected-result comparison option.

## 13. Future CLI Tests

Future CLI implementation tests should include:

- `--help` exits `0`
- no arguments exit `2`
- request only exits `2`
- pointer only exits `2`
- valid case human output exits `0`
- valid case JSON output exits `0` and is parseable
- invalid expected fail-closed human output exits `0`
- invalid expected fail-closed JSON output exits `0`
- malformed request exits `2`
- missing pointer exits `2`
- generated artifact body request fails closed without writing
- artifact file-writing request fails closed without writing
- stdout and stderr contain no request body
- stdout and stderr contain no pointer body
- stdout and stderr contain no policy body
- stdout and stderr contain no artifact body
- stdout and stderr contain no raw rows
- stdout and stderr contain no logits
- stdout and stderr contain no private paths
- output is deterministic

Tests should use only synthetic fixtures or synthetic temp inputs. They should
not print fixture bodies and should not create artifacts.

## 14. Future Makefile Strategy

Do not add a Makefile target in the CLI implementation step.

Recommended staging:

- implement CLI and tests
- design a standalone generator scaffold CLI smoke target
- run one valid synthetic fixture
- optionally run one invalid expected fail-closed fixture
- confirm no-body-leakage in stdout and stderr
- only then consider target implementation

The standalone target should not write files, create tmp outputs, generate
artifact bodies, or run performance evaluation.

## 15. Future Release-Quality Strategy

Do not add generator scaffold CLI/runtime smoke to release-quality immediately.

Current release-quality already includes generator scaffold fixture validation.
That checks the fixture contract, not skeleton runtime execution.

Future release-quality staging should be:

- implement CLI and tests
- implement standalone Makefile smoke target
- run no-body-leakage review
- design release-quality integration
- integrate only after standalone target passes

Success would mean the skeleton metadata result is safe. It would still not
mean generator quality, artifact generation evidence, performance evidence, or
real-data readiness.

## 16. Status Marker Future

A future remote status marker may record generator scaffold skeleton runtime
smoke after CLI, Makefile target, and release-quality integration exist.

Allowed marker content:

- pass-only status
- count-only metadata
- safe IDs and labels
- fixed artifact flags
- fixed safety flags
- no raw logs
- no request or pointer body
- no policy body
- no artifact body
- no performance metric body

The existing generator scaffold fixture validation remote status marker should
remain separate from any future skeleton runtime marker.

## 17. No-Oracle / Synthetic-Only Boundary

The CLI boundary remains synthetic-only and no-oracle.

It must not use or print:

- real data
- participant data
- raw learner text
- final text
- gold text
- observed-after text
- expected action scoring feedback payload
- test-derived tuning payload
- artifact body
- generated policy body
- logits
- raw rows
- private paths

Marker labels may appear only as safe reason codes, failed checks, fixture
labels, or safe notes when they do not carry payload content.

## 18. What This Does NOT Do

This document does not:

- add a Makefile target
- integrate release-quality
- change workflows
- write artifacts
- generate policy bodies
- generate artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 19. Beginner-Friendly Explanation

A CLI is a terminal command. The future generator scaffold CLI would let a
developer run the metadata-only skeleton on one synthetic request and pointer
pair without opening Python directly.

This design comes before implementation so the command's safety rules are
clear before it can print anything. The safest first version prints only
metadata: status, reason codes, IDs, flags, counts, and safe summaries.

The fixture validator CLI and skeleton CLI are different. The fixture validator
checks whether the fixture set is shaped correctly. The skeleton CLI runs the
skeleton on one request and pointer pair.

An invalid fixture can still exit `0` when it safely fails closed for the
expected reason. That means the skeleton did the safe thing.

The initial CLI should not include output-file options because file writing is
a separate artifact-writer boundary. Keeping the first CLI read-only makes the
safety contract easier to review.

## 20. Next Recommended Steps

Recommended next steps:

- Step293: generator scaffold CLI implementation
- Step294: generator scaffold Makefile target design
- Step295: generator scaffold Makefile target implementation
- Step296: generator scaffold release-quality integration design
- Step297: generator scaffold release-quality integration implementation

Keep artifact writing, generated policy bodies, calibration work, performance
evaluation, and real-data readiness separate.

## 21. Step293 Implementation Status

Step293 implements the safe CLI entrypoint in
`python/learner_state/frozen_policy_generation_generator_scaffold.py` and adds
focused CLI tests in
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_cli.py`.

The implementation:

- accepts `--request`, `--pointer`, `--json`, and `--help`
- requires `--request` and `--pointer` together
- returns safe human output by default
- returns parseable safe JSON with `--json`
- exits `0` for valid pass metadata and expected fail-closed invalid metadata
- exits `2` for usage or input errors
- reserves `3` for safety-audit mismatch
- exits `1` for unexpected internal errors
- calls the existing skeleton APIs instead of duplicating core logic
- does not write artifacts
- does not generate artifact bodies
- does not generate policy bodies
- does not add a Makefile target
- does not change release-quality
- does not change workflows
- does not change fixtures

## 22. Step294 Makefile Target Design Status

Step294 designs a future standalone Makefile target for the implemented safe
generator scaffold CLI:
[Frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md).

The design recommends a valid-only runtime smoke target named
`check-learner-state-frozen-policy-generation-generator-scaffold-runtime`.
It remains docs-only: no Makefile target, release-quality wrapper change,
workflow change, Python change, test change, fixture change, artifact body,
generated policy body, or file-writing behavior is added.

## 23. Step295 Makefile Target Implementation Status

Step295 implements the standalone Makefile runtime smoke target:
`check-learner-state-frozen-policy-generation-generator-scaffold-runtime`.

The target runs the safe generator scaffold CLI on one valid synthetic
request/pointer pair and prints only the body-free metadata summary. It is not
added to release-quality in Step295, and it does not change workflows, Python
code, tests, fixtures, artifact writing, artifact bodies, generated policy
bodies, manifest writing, metrics, or real-data readiness status.

## 24. Step296 Release-Quality Integration Design Status

Step296 designs future release-quality integration for that standalone runtime
smoke target:
[Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md).

The design keeps wrapper implementation, workflow changes, Python changes,
test changes, fixture changes, artifact writing, generated policy bodies,
artifact bodies, metrics, and real-data readiness out of scope.

## 25. Step297 Release-Quality Wrapper Integration Status

Step297 adds the generator scaffold runtime smoke target to the
release-quality wrapper:
`make check-learner-state-frozen-policy-generation-generator-scaffold-runtime`.

The CLI remains a thin metadata-only wrapper over the skeleton APIs. The
release-quality integration does not add output-file options, artifact writing,
artifact bodies, generated policy bodies, manifest writing, metrics, or
real-data readiness claims.

## Related Documents

- [Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
