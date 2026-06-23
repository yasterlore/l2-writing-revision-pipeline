# Frozen Policy Generation Generator Scaffold Fixture Validator Release-Quality Integration Design

## 1. Purpose

This document designs a future release-quality integration for the frozen
policy generation generator scaffold fixture validator target.

This is not an implementation. It does not change the release-quality wrapper,
GitHub Actions workflows, the Makefile, Python code, Python tests, fixtures, or
generator code. It does not write artifacts, generate artifact bodies, compute
metrics, evaluate performance, or claim real-data readiness.

## 2. Current State

- Generator scaffold fixtures exist.
- The generator scaffold fixture validator module exists.
- Validator unit tests exist.
- The validator CLI exists.
- The standalone Makefile target exists:
  `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`.
- Release-quality integration does not exist yet.
- The generator does not exist.
- The artifact writer does not exist.

Current standalone target behavior is metadata-only:

- `total_cases=18`
- `matched_cases=18`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- no request body output
- no pointer body output
- no expected result body output
- no artifact body output
- no raw rows
- no logits
- no private paths
- no tmp output
- no artifact writing
- no generator invocation

## 3. Proposed Wrapper Insertion Point

The current learner-state portion of the release-quality wrapper runs in this
order:

- learner-state audit fixtures
- learner-state exporter CLI smoke
- learner-state estimator input validation
- learner-state selective prediction calibration validation
- learner-state frozen policy validation
- learner-state frozen policy generation validation
- learner-state frozen policy generation scaffold fixture validation
- learner-state frozen policy generation scaffold runtime smoke
- config/scoring smoke checks

The recommended insertion point is immediately after:

```text
release_quality_check: learner-state frozen policy generation scaffold runtime smoke
```

and before:

```text
release_quality_check: config and scoring smoke checks
```

This keeps the frozen policy generation sequence readable:

1. frozen policy generation validation
2. runtime scaffold fixture validation
3. runtime scaffold smoke
4. generator scaffold fixture validation
5. config/scoring smoke checks

The proposed target is generator-adjacent fixture contract validation, not
generator execution and not performance evaluation.

## 4. Proposed Wrapper Command

Use the standalone Makefile target:

```text
make check-learner-state-frozen-policy-generation-generator-scaffold-fixtures
```

The wrapper should call the Makefile target rather than the Python CLI
directly because:

- the standalone target has already been validated as the public local entry
  point
- developers and CI can use the same command
- wrapper readability stays high
- the CLI fixture-root argument is not duplicated in the wrapper
- future target-local safety checks can remain behind the Makefile entry point

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation generator scaffold fixture validation
```

This label distinguishes the target from frozen policy generation validation,
scaffold fixture validation, scaffold runtime smoke, and future generator
implementation checks.

## 6. Expected Wrapper Behavior

Expected behavior after future wrapper integration:

- target pass -> release-quality continues
- target fail -> release-quality fails
- output remains safe metadata only
- no tmp output
- no artifact writing
- no generator invocation

Expected output metadata:

- `total_cases=18`
- `matched_cases=18`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`

## 7. Failure Interpretation

The following should fail release-quality:

- CLI usage failure
- missing fixture root
- malformed fixture input
- `input_error_cases > 0`
- `mismatched_cases > 0`
- `matched_cases != 18`
- `total_cases != 18`
- request, pointer, expected-result, or artifact body leakage
- raw rows leakage
- logits leakage
- private path leakage
- `artifact_policy_checked=false`
- `body_suppression_checked=false`
- `file_writing_checked=false`
- unexpected artifact writing
- generator invocation
- internal error

These failures mean the safe fixture contract or wrapper execution path is not
healthy. They do not mean generator performance failed, because no generator is
executed and no performance evaluation is performed.

## 8. Log Safety Review

The wrapper log may contain:

- target label
- command label
- mode
- total case count
- matched case count
- mismatched case count
- input error case count
- reason-code counts
- safety flags
- artifact policy flags
- validation schema version

The wrapper log must not contain:

- request body
- pointer body
- expected result body
- artifact body
- generated policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metric body

Documentation must not copy raw GitHub Actions logs or full job output. Any
future public status marker should use pass-only and count-only metadata.

## 9. Relation To Existing Release-Quality Checks

- The runtime scaffold fixture validator target validates the runtime scaffold
  fixture contract.
- The runtime scaffold runtime smoke target validates one safe runtime CLI path
  over a valid synthetic fixture.
- The proposed generator scaffold fixture validator target validates the
  generator scaffold metadata-only fixture contract.
- The frozen policy generation validator target validates the frozen policy
  generation validation fixture root.
- The proposed target does not execute a generator.
- Success is not generator quality evidence.
- Success is not artifact generation evidence.
- Success is not performance evidence.

## 10. Makefile / Workflow Status

- The Makefile target already exists.
- The release-quality wrapper is not changed by this design.
- GitHub Actions workflows are not changed by this design.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML should remain unchanged unless a future implementation finds a
  concrete wrapper invocation limitation.

## 11. Testing Plan For Future Implementation

Future implementation should verify:

- standalone target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- output includes `total_cases=18`
- output includes `matched_cases=18`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `no_logits_dump=true`
- output includes `no_private_paths=true`
- output includes `artifact_policy_checked=true`
- output includes `body_suppression_checked=true`
- output includes `file_writing_checked=true`
- no request, pointer, expected-result, or artifact body leakage
- no raw rows, logits, or private path leakage
- wrapper diff is limited
- workflow diff is none
- all Python tests pass
- all existing checks pass

The checks should remain metadata-only and should not paste raw logs into docs.

## 12. Release-Quality Status Marker Future

After wrapper integration and a successful remote/manual Release Quality run, a
future status marker may be added.

That marker should record count-only and pass-only metadata such as:

- target included: yes
- total cases: 18
- matched cases: 18
- mismatched cases: 0
- input error cases: 0
- content suppressed: true
- no raw rows: true
- no logits dump: true
- no private paths: true
- artifact policy checked: true
- body suppression checked: true
- file writing checked: true

The marker must not record request body, pointer body, expected result body,
artifact body, raw rows, logits, private paths, raw learner text, or copied
raw logs.

## 13. No-Oracle / Synthetic-Only Boundary

The target uses metadata-only synthetic fixtures.

It must not use:

- real data
- participant data
- raw learner text
- final text
- observed-after text
- gold label
- expected action as scoring feedback
- test-derived tuning payload
- artifact body
- logits
- raw rows
- private paths

Invalid fixtures remain safe marker cases. They verify fail-closed metadata
behavior without including unsafe payload bodies.

## 14. What This Does NOT Do

This design did not initially:

- integrate the release-quality wrapper
- change GitHub Actions workflows
- change the Makefile
- change Python code
- change Python tests
- change fixtures
- execute a generator
- write artifacts
- generate artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

Step287 implements the planned wrapper integration with the standalone target
only. The wrapper now runs:

```text
release_quality_check: learner-state frozen policy generation generator scaffold fixture validation
command: make check-learner-state-frozen-policy-generation-generator-scaffold-fixtures
```

The integration is placed after scaffold runtime smoke and before
config/scoring smoke checks. It does not change GitHub Actions workflows, the
Makefile, Python code, Python tests, fixtures, generator code, artifact
writing, or artifact body generation.

## 15. Beginner-Friendly Explanation

Release-quality is the project’s broad local/CI check bundle. It runs many
small safety and regression checks in a known order.

The standalone Makefile target is already useful on its own. Adding it to
release-quality later means every release-quality run would also confirm that
the generator scaffold fixtures still follow the safe metadata-only contract.

The runtime scaffold fixture validator checks the older runtime scaffold
contract. The runtime smoke checks one safe runtime CLI path. The generator
scaffold fixture validator checks the newer generator-adjacent fixture
contract, but it still does not run a generator.

A successful release-quality run would mean the fixture contract is intact. It
would not mean the generator is implemented, that generated policies are good,
or that model performance has been evaluated.

A remote/manual status marker should be separate because it records an actual
remote run identity and result. That record must stay pass-only and count-only,
without copied logs or fixture bodies.

## 16. Next Recommended Steps

Recommended next steps after Step287:

1. Confirm remote/manual Release Quality success.
2. Design or add a public-safe status marker if
   needed.

Generator implementation, artifact writing, artifact body generation,
calibration work, estimator work, and metric computation should remain
separate future milestones.

## 17. Docs Update

This Step286 document records the release-quality integration design for the
metadata-only generator scaffold fixture validator target.

Step287 records the corresponding minimal wrapper integration. The added
wrapper section calls the standalone Makefile target and keeps output
metadata-only.

Related docs:

- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)

## 18. Update History

- Step286: initial docs-only release-quality integration design for the
  generator scaffold fixture validator target.
- Step287: recorded minimal release-quality wrapper integration status; no
  workflow, Makefile, Python, test, fixture, generator, artifact-writing, or
  artifact-body changes are introduced.
