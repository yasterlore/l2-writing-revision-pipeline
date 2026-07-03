# Full Technical Specification External Review Checklist

This checklist supports external review of
`docs/full_technical_specification.md` after Step-pretec-doc5 hardening. It is
a review aid, not an implementation change, not a production readiness
certification, not a real-data readiness certification, and not model
performance evidence.

The checklist should be used with:

- `docs/full_technical_specification_source_inventory.md`
- `docs/full_technical_specification.md`
- `docs/full_technical_specification_coverage_validation.md`
- `docs/full_technical_specification_final_safety_review.md`
- repository evidence in `Makefile`, `.github/workflows/`, `scripts/`,
  `python/`, `crates/`, `apps/logger-web/`, `tests/fixtures/`, and
  `docs/status/`

## 1. Review Scope

Confirm that the full technical specification is treated as a consolidated
technical specification draft based on repository scan evidence. It should not
be treated as an absolute guarantee of no omissions.

Reviewers should verify:

- source inventory coverage is traceable
- implementation status is explicit
- non-proofs are explicit
- unresolved or unconfirmed areas are marked as `not yet confirmed from
  repository scan` or `next step verification required`
- no implementation, workflow, fixture, or runtime behavior is inferred beyond
  repository evidence

## 2. Coverage Against Inventory

Check the full specification against the source inventory:

- root files and package/workspace metadata
- README and SECURITY posture
- Makefile targets
- release-quality wrapper labels
- GitHub Actions workflows
- Python module CLIs and validators
- Rust crates and CLI
- logger-web TypeScript/Vite app
- fixture root families and fixture READMEs
- schema/version families
- docs/status marker families
- safety and no-oracle policies

Any missing component should be recorded as a coverage follow-up, not silently
filled by inference.

## 3. Implementation Status Matrix

Confirm that each major component is categorized correctly:

- implemented
- fixture-only
- validator-only
- standalone Makefile target
- release-quality integrated
- remote status recorded
- docs-only
- not implemented
- future work

Pay special attention that the following remain marked with their current
implementation boundaries:

- artifact writer CLI integration runtime: initial metadata-only runtime
  module exists after Step489, with a Step491 standalone Makefile smoke target
  and Step493 release-quality wrapper inclusion
- artifact body generation CLI integration
- manifest writer integration
- manifest body generation
- production readiness review
- real-data readiness review

## 4. Non-Proofs

Confirm that the specification does not claim:

- production readiness
- real-data readiness
- model performance
- F1 achievement
- accuracy achievement
- ECE achievement
- AURCC achievement
- learner-state estimator correctness
- generated policy quality
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- privacy/legal/IRB readiness

## 5. Public-Safe Documentation Review

Confirm that public docs do not contain:

- raw GitHub Actions logs
- full job output
- fixture JSON body examples
- request body examples
- pointer body examples
- expected body examples
- written file JSON body examples
- manifest body examples
- artifact body payload examples
- generated policy body examples
- raw rows
- logits or probabilities
- private path examples
- absolute local path examples
- raw learner text
- real participant data
- screenshots containing raw logs

Field names, schema names, target names, status labels, reason-code names, and
safe count-only summaries may be used when they remain body-free.

## 6. CLI / Makefile / CI Coverage

Confirm that the specification covers:

- Python module CLI argument families
- Rust `kslog` CLI command families
- shell script checks
- npm scripts for logger-web
- Makefile target command mapping
- release-quality wrapper order
- CI workflow setup and action versions
- Release Quality workflow setup and action versions

Reviewers should verify that command examples remain command-level only and do
not include raw logs or body payload examples.

## 7. Fixture / Validator / Schema Coverage

Confirm that the specification covers:

- fixture root family purpose and counts where safely confirmed
- validator module and CLI relation
- Makefile target relation
- release-quality inclusion where confirmed
- schema/result/validation version families
- separation between stable schema names and synthetic invalid markers
- no-oracle, synthetic-only, metadata-only, and body-free restrictions

Fixture JSON bodies must not be copied into the specification or checklist.

## 8. Status Marker Review

Confirm that status markers are summarized as public-safe records:

- marker path
- related component
- status type
- raw logs stored: no
- what the marker proves
- what the marker does not prove

Run identities may be referenced only when already recorded in public-safe
marker docs and should not be expanded with raw logs.

## 9. Logger-Web Review

Confirm logger-web coverage against repository evidence:

- TypeScript and Vite package metadata
- npm scripts
- raw event helper tests
- in-memory synthetic event recording
- download behavior
- no server send / no localStorage / no console text logging statements in
  repository docs
- limitations and non-readiness claims

Do not treat logger-web checks as deployment readiness or real participant
collection readiness.

## 9.1 Step498 Fixture Root Review

Confirm the Step498 artifact writer CLI actual invocation fixture root is
covered as fixture-only evidence:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/`
- 32 case directories
- 192 metadata-only JSON files
- 1 fixture README
- Step500 static validator module / CLI / focused tests implemented
- Step502 standalone Makefile target implemented
- Step504 release-quality wrapper check added
- runtime actual invocation not implemented
- workflow unchanged

Do not treat this fixture root as artifact writer CLI actual invocation
correctness, artifact body generation integration correctness, manifest writer
integration correctness, production readiness, real-data readiness, or model
performance evidence.

## 9.2 Step500 Fixture Validator Review

Confirm the Step500 artifact writer CLI actual invocation fixture validator
checks only the Step498 synthetic metadata-only fixture root and emits
public-safe summary-only output. Reviewers should check the 32 case / 192 JSON
aggregate counts, expected status and reason-code mapping, sentinel policy,
path-safety policy, downstream boundary checks, malformed JSON handling, and
missing-root handling.

Do not treat this validator as artifact writer CLI actual invocation
correctness, artifact body generation integration correctness, manifest writer
integration correctness, production readiness, real-data readiness, or model
performance evidence.

## 9.3 Step502 Makefile Target Review

Confirm the Step502 standalone Makefile target runs only the Step500 static
validator CLI:

- `check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`

Reviewers should confirm the target output remains public-safe summary-only,
matches the 32 case / 192 JSON aggregate counts, and does not change
release-quality wrapper behavior or workflow files. Do not treat the target as
artifact writer CLI actual invocation correctness evidence, artifact body
generation integration evidence, manifest writer integration evidence,
production readiness evidence, real-data readiness evidence, or model
performance evidence.

## 9.4 Step504 Release-Quality Wrapper Review

Confirm the Step504 release-quality wrapper check invokes only the standalone
static fixture validator target:

- label: `release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation fixture validation`
- command: `make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`
- insertion point: after artifact writer CLI integration runtime smoke and
  before artifact body fixture validation

Do not treat this wrapper check as artifact writer CLI actual invocation
correctness evidence, artifact body generation integration evidence, manifest
writer integration evidence, production readiness evidence, real-data
readiness evidence, or model performance evidence.

## 9.5 Step509 Runtime Fixture Root Update Review

Confirm the Step509 artifact writer CLI integration runtime fixture root update
preserves the original 30 v0.1 plan-only cases and adds 24 v0.2 synthetic
metadata-only `actual_invocation_metadata_only` cases. Reviewers should check
the 54 case / 324 JSON aggregate counts, the six-file layout, the v0.2 schema
family, sentinel-only invalid cases, and the Step511 static validator v0.2
support.

Confirm the Step511 validator module / CLI / focused tests use validator
schema
`learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`,
accept both v0.1 plan-only and v0.2 actual-invocation metadata-only fixture
schema families, and report only public-safe aggregate counts, reason codes,
and safety flags.

Confirm the Step513 runtime module update keeps plan-only behavior as the
default and only enables `actual_invocation_metadata_only` with an explicit
flag. Reviewers should check the new CLI flags, runtime schema v0.2 summary
fields, stdout/stderr suppression, fail-closed sentinel handling,
no-file-writing boundary, and absence of artifact body generation or manifest
writer integration.

Confirm the Step515 standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`
runs only the valid v0.2 `actual_invocation_metadata_only` runtime smoke case
with `--actual-invocation --summary-only --no-file-writing`. Reviewers should
confirm Step517 adds it to `scripts/check_release_quality.sh` with label
`release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation runtime smoke`
after static actual invocation fixture validation and before artifact body
fixture validation. Reviewers should also confirm it does not change workflow
files, fixture JSON, Python code/tests, artifact body generation integration,
manifest writer integration, file writing, or production readiness claims.

Do not treat this fixture update as artifact writer CLI actual invocation
correctness, runtime actual invocation correctness, artifact body generation
integration correctness, manifest writer integration correctness, production
readiness, real-data readiness, or model performance evidence.

Confirm the Step523 artifact body generation integration fixture root is
covered as fixture-only evidence, Step525 static validator evidence, Step527
standalone Makefile target evidence, and Step529 wrapper check evidence:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`
- 28 case directories
- 196 metadata-only JSON files
- 7 JSON files per case
- 1 fixture README
- v0.1 integration metadata schema family
- validator module:
  `python/learner_state/frozen_policy_generation_artifact_body_generation_integration_fixture_validation.py`
- validation schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validation_v0.1`
- aggregate split: pass 6 / usage_error 1 / fail_closed 20 / mismatch 1
- standalone target:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures`
- wrapper label:
  `release_quality_check: learner-state frozen policy generation artifact body generation integration fixture validation`
- insertion point: after actual invocation runtime smoke and before artifact
  body fixture validation

Do not treat this fixture root as artifact body generation integration
correctness, manifest writer integration correctness, production readiness,
real-data readiness, or model performance evidence.

Confirm the Step535 artifact body generation runtime integration plan-only
bridge is documented and scoped:

- module:
  `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- focused tests:
  `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- selected fixture case:
  `valid/valid_minimal_suppressed_metadata_only_bridge`
- supported mode: `plan-only-bridge`
- reserved modes: `suppressed-smoke`, `safe-metadata-smoke`
- runtime schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`

Confirm this CLI emits selected-case public-safe metadata-only summaries only,
requires no-file-writing and no-manifest-writer flags for pass, and does not
invoke artifact body generation runtime, call manifest writer code, write
files, change fixture JSON, change validators, change Makefile, change the
release-quality wrapper, change workflow files, use real data, compute
metrics, or claim production readiness.

Confirm Step537 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`
with help text `Run artifact body generation runtime integration plan-only
bridge smoke`. Reviewers should confirm it runs the Step535 CLI over
`valid/valid_minimal_suppressed_metadata_only_bridge`, remains outside the
release-quality wrapper, and does not change workflow files, Python
code/tests, fixture JSON, validators, runtime implementation, artifact body
generation runtime invocation, manifest writer integration, file writing, or
production readiness claims.

Confirm Step539 adds the release-quality wrapper check
`release_quality_check: learner-state frozen policy generation artifact body generation runtime integration plan-only bridge smoke`
with command
`make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`.
Reviewers should confirm it is inserted after artifact body generation
integration fixture validation and before artifact body fixture validation,
and that it does not change workflow files, Makefile, Python code/tests,
fixture JSON, validators, runtime implementation, artifact body generation
runtime invocation, manifest writer integration, file writing, or production
readiness claims.

Confirm Step547 adds planned safe-metadata v0.2 fixture cases outside the
active artifact body generation integration validator root at
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`.
Reviewers should confirm the planned cases are metadata-only / body-free,
preserve the seven-file layout, remain validator/runtime/release-quality
unintegrated, and do not include raw payloads, raw logs, real data, file
writing, manifest writer invocation, model performance evidence, or production
readiness claims.

Confirm Step549 adds the separate planned safe-metadata v0.2 fixture validator
module and focused tests. Reviewers should confirm it validates 24 cases / 168
JSON files, emits only public-safe aggregate output, keeps the active root
validator separate, and does not add Makefile target, release-quality wrapper
integration, workflow changes, runtime implementation, artifact body generation
runtime invocation, manifest writer integration, file writing, model
performance evidence, or production readiness claims.

Confirm Step551 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`
for the planned-root validator CLI. Reviewers should confirm the target emits
the same public-safe aggregate output, remains separate from the active root
target, and does not add release-quality wrapper integration, workflow
changes, runtime implementation, artifact body generation runtime invocation,
manifest writer integration, file writing, model performance evidence, or
production readiness claims.

Confirm Step553 adds the release-quality wrapper label
`release_quality_check: learner-state frozen policy generation artifact body generation runtime integration safe-metadata v0.2 fixture validation`
and command
`make check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`.
Reviewers should confirm it is placed after plan-only bridge smoke and before
artifact body fixture validation, and that it does not change workflow files,
Makefile, Python code/tests, fixture JSON, runtime implementation, artifact
body generation runtime invocation, manifest writer integration, file writing,
model performance evidence, or production readiness claims.

Confirm Step559 adds `safe-metadata-smoke` runtime behavior as metadata
handoff only in
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`.
Reviewers should confirm the mode emits schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
for `valid/valid_safe_metadata_explicit_runtime_bridge`, keeps artifact body
generation runtime invocation false, keeps manifest writer invocation false,
keeps file writing disabled, fail-closes unsafe markers, and is not yet
Makefile-targeted or release-quality wrapper integrated as a runtime smoke.

Confirm Step561 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`.
Reviewers should confirm the target runs the Step559 `safe-metadata-smoke`
runtime CLI over the planned primary case, emits the v0.2 public-safe metadata
handoff summary, and remains metadata handoff only.

Confirm Step563 adds wrapper label
`release_quality_check: learner-state frozen policy generation artifact body generation runtime integration safe-metadata runtime smoke`
after safe-metadata v0.2 fixture validation and before artifact body fixture
validation. Reviewers should confirm the check remains metadata handoff only
and does not invoke artifact body generation runtime, invoke manifest writer,
write files, use real data, compute metrics, or claim production readiness.

Confirm Step570 adds
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/`
as a planned metadata-only / body-free fixture root with 6 valid cases, 24
invalid cases, 30 total cases, 7 JSON files per case, and 210 total JSON files.
Reviewers should confirm this fixture root creation does not add validator
implementation, runtime implementation, Makefile target integration,
release-quality wrapper integration, workflow changes, artifact body
generation runtime invocation, manifest writer integration, file writing,
real-data use, metric use, or production readiness claims.

Confirm Step572 adds standalone validator module
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`
and focused tests for the Step570 root. Reviewers should confirm the CLI emits
schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
and validates 30 cases / 210 JSON files without adding release-quality wrapper
integration, workflow changes, runtime implementation, artifact body generation
runtime invocation, manifest writer integration, file writing, model
performance evidence, or production readiness claims.

Confirm Step574 adds standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
for the Step572 validator CLI. Reviewers should confirm the target is not yet
release-quality integrated and does not change workflow files, Python
code/tests, fixture JSON, runtime implementation, artifact body generation
runtime invocation, manifest writer integration, file writing, model
performance evidence, or production readiness claims.

Confirm Step577 adds planned-only v0.3 `artifact-body-runtime-invocation`
support in the existing runtime integration module. Reviewers should confirm
that CLI output is public-safe, metadata-only, and body-free; that it records
runtime invocation as planned but not invoked; and that Makefile targets,
release-quality wrapper checks, workflow files, fixture JSON, validator
implementation, actual artifact body generation runtime invocation, manifest
writer integration, file writing, model performance evidence, and production
readiness claims are unchanged.

Confirm Step579 adds standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
with help text `Run artifact body generation runtime invocation planned-only smoke`.
Reviewers should confirm the target runs the Step577 planned-only v0.3 direct
CLI, emits public-safe metadata-only / body-free output, is not connected to
the release-quality wrapper, does not change workflow files, Python code/tests,
fixture JSON, runtime implementation, validator implementation, actual
artifact body generation runtime invocation, manifest writer integration, file
writing, model performance evidence, or production readiness claims.

Confirm Step581 adds the two runtime invocation checks to
`scripts/check_release_quality.sh` in adjacent order:

- `learner-state frozen policy generation artifact body generation runtime invocation fixture validation`
- `learner-state frozen policy generation artifact body generation runtime invocation planned-only v0.3 smoke`

Reviewers should confirm the checks run after safe-metadata runtime smoke and
before artifact body fixture validation. The fixture validator must run before
the planned-only v0.3 smoke. Confirm Step581 does not change workflow files,
Makefile, Python code/tests, fixture JSON, runtime implementation, validator
implementation, actual artifact body generation runtime invocation, manifest
writer integration, file writing, model performance evidence, or production
readiness claims.

## 10. Rust Crate Review

Confirm Rust coverage against workspace and crate evidence:

- `kslog_schema`
- `kslog_validate`
- `kslog_replay`
- `kslog_extract`
- `kslog_micro_episode`
- `kslog_no_oracle_audit`
- `kslog_cli`

Review crate roles, tests/checks, CLI relation, and no-oracle/safe-view
relation. Do not infer API signatures that are not confirmed by source or
README files.

## 11. Final Review Notes

Before treating the specification as external-review-ready, confirm:

- high and medium coverage gaps remain closed or explicitly reopened
- low-priority hardening is summarized at external-review level
- the final safety and non-proof review has been read
- no raw payloads or raw logs are introduced during review
- unresolved items remain listed
- future runtime integration work remains separate

This checklist does not itself prove production readiness, real-data readiness,
model performance, or legal/privacy readiness.

## Step587 Actual-Controlled Fixture Root Review

For Step587, confirm the actual-controlled fixture root exists with 6 valid cases, 30 invalid cases, 36 total cases, 252 parseable metadata-only JSON files, and the exact 7-file layout. Confirm the root is separate from the Step570 planned-only root and does not implement validators, runtime invocation, manifest writer integration, file writing, production readiness, real-data readiness, or model performance evidence.


## Step589 Actual-Controlled Fixture Validator Review

Confirm the Step589 validator CLI exists, is standalone, and targets the Step587 actual-controlled fixture root. Confirm the focused tests validate the expected 36-case / 252-JSON aggregate and public-safe output policy. Confirm no Makefile target, release-quality wrapper integration, workflow change, fixture JSON change, runtime implementation, manifest writer integration, file writing, production readiness, real-data readiness, or model performance claim is added by this step.
