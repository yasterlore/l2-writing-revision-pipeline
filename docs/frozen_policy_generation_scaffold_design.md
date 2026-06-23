# Frozen Policy Generation Scaffold Design

This document designs a future frozen policy generation scaffold for learner
state selective prediction and calibration work.

It is documentation only. It does not implement a generator, calibration,
selective prediction, a learner-state estimator, estimator training, model
logic, metric computation, GitHub Actions workflow changes, release-quality
wrapper changes, Makefile changes, Python code changes, test changes, fixture
changes, or production data handling. It is not a performance evaluation and
is not a real-data readiness claim.

The design assumes synthetic-only fixtures and metadata-only outputs. Public
docs must not include raw GitHub Actions logs, full job output, copied log
blocks, screenshots containing raw logs, frozen policy artifact bodies, JSON
bodies, policy bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, generated feature/label/manifest bodies,
private paths, raw learner text, or real participant data.

## 1. Purpose

The purpose of this document is to define how a future scaffold could safely
generate `frozen_selective_prediction_policy.json` from validated selective
prediction inputs and validation-only tuning metadata.

This design covers:

- current validation infrastructure the scaffold depends on
- scaffold responsibilities
- explicit non-goals
- input requirements
- future output artifacts
- validation-only temperature metadata
- validation-only threshold / abstention metadata
- future generation flow
- safety checks before writing an artifact
- path and output policy
- relation to the frozen policy validator and calibration scaffold
- future fixture and test planning
- release-quality staging

This step does not create any artifact file and does not compute temperature,
threshold, F1, accuracy, ECE, AURCC, calibration quality, coverage-risk curves,
or model performance.

## 2. One-Sentence Summary

The frozen policy generation scaffold is a future intermediate layer that
would consume validated selective prediction fixtures and validation-only
tuning metadata, then construct a safe frozen policy artifact before test
evaluation without exposing raw rows or using test labels for tuning.

## 3. Current Infrastructure

The scaffold should build on existing Milestone 09 and Milestone 10
infrastructure:

- selective prediction input fixture validator
- selective prediction calibration validation CLI and Makefile target
- frozen policy schema design
- frozen policy fixture root
- frozen policy validator
- frozen policy CLI
- `make check-learner-state-frozen-policy`
- release-quality wrapper integration for frozen policy validation
- public-safe remote run status marker
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)

The current infrastructure validates inputs and frozen policy artifacts. It
does not yet generate frozen policies, fit calibration, train a learner-state
estimator, or compute metrics.

## 4. Scaffold Responsibilities

The future scaffold should:

- require a passing selective prediction validator result before generation
- use the validation split as the only tuning source
- create temperature policy metadata
- create threshold / abstention policy metadata
- construct metadata that follows the frozen policy artifact schema
- populate `safety_review` fields
- create `validation_input_summary` as count-only metadata
- create `split_policy_summary` as safe metadata
- produce an artifact shape that can be passed to the frozen policy validator
- suppress content-bearing fields in public output
- reject test-derived temperature or threshold provenance
- reject inputs with labels embedded in prediction rows
- reject public summaries that would expose raw rows, logits dumps, label
  bodies, split bodies, calibration policy bodies, private paths, raw learner
  text, or performance claims

The scaffold should be a small bridge between already-validated inputs and the
already-existing frozen policy validator. It should not duplicate all
validation logic where it can call the validators directly.

## 5. What The Scaffold Does Not Do

The scaffold does not:

- train a model
- implement a learner-state estimator
- implement calibration in this design step
- compute final temperature in this design step
- compute final threshold in this design step
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- compute coverage-risk curves
- run final test evaluation
- handle real data
- deploy production data collection
- update the OT scorer
- update the candidate generator
- update scoring formulas
- update tie-break logic
- change manifest schemas
- use expected action as scoring feedback

The scaffold is a provenance and artifact-construction boundary, not evidence
that a policy is useful.

## 6. Input Requirements

Future scaffold inputs may include:

- selective prediction fixture root or a validated fixture case
- `predictions.jsonl`
- `labels.jsonl`
- `split_metadata.json`
- `calibration_policy.json`
- selective prediction validation result
- optional estimator input manifest
- optional future calibration candidate summary

Required preconditions:

- selective prediction validator pass
- validation split exists
- learner-disjoint split is preserved
- no label appears in prediction rows
- no test-derived tuning is allowed by policy
- no raw learner text appears in public output
- expected action stays label-side only or intentional invalid-fixture target
- policy metadata forbids test threshold and test temperature tuning

The scaffold should fail closed if the validator cannot run, if validation
fails, or if the input summary is missing required safety flags.

## 7. Output Artifact Design

Future scaffold outputs may include:

- `frozen_selective_prediction_policy.json`
- optional `frozen_policy_generation_summary.json`
- optional safe human summary
- optional safe manifest

This document does not create any of those files.

Output requirements:

- generated frozen policy must match the schema design
- generated frozen policy must pass the frozen policy validator before being
  accepted
- public summaries must be metadata-only and count-only
- public docs must not paste artifact bodies or JSON bodies
- generated outputs should not be committed unless a later fixture design
  explicitly creates synthetic expected-output fixtures
- `manual_outputs/` and generic `tmp/` run outputs must not be added to Git

## 8. Validation-Only Temperature Metadata Design

Temperature metadata should record provenance, not performance.

Allowed source split:

- `validation`

Initial method examples:

- `none_identity`
- `validation_nll_minimization`

Design rules:

- identity temperature should be represented explicitly, for example
  `temperature = 1.0` with `temperature_selection_method = none_identity`
- test split is forbidden as a temperature source
- temperature must be selected before any test evaluation
- public artifact and public summaries must not include raw logits dumps
- actual validation NLL calculation is future implementation work
- identity temperature does not imply calibration quality

## 9. Validation-Only Threshold Metadata Design

Threshold metadata should record the abstention policy provenance.

Allowed source split:

- `validation`

Initial method examples:

- `fixed_abstention_rate`
- `fixed_confidence_threshold`

Design rules:

- `allowed_abstention_rate` should be numeric and in the range `0.0` to `1.0`
- `threshold` should be numeric and in the range `0.0` to `1.0`
- test labels must not influence threshold selection
- threshold must be selected before any test evaluation
- actual threshold selection is future implementation work
- threshold metadata should not be described as model performance

## 10. Frozen Policy Generation Flow

Proposed future order:

1. Load the selective prediction fixture bundle.
2. Run the selective prediction validator.
3. Fail closed if the validator fails.
4. Derive validation-only calibration metadata.
5. Derive validation-only threshold metadata.
6. Construct frozen policy metadata.
7. Suppress content-bearing fields.
8. Run the frozen policy validator against the constructed artifact.
9. Write the frozen policy artifact only if validator checks pass.
10. Emit a safe summary.

This is a design flow only. No generator is implemented in this step.

## 11. Safety Checks Before Write

Before writing any future frozen policy artifact, the scaffold must verify:

- no raw rows in the artifact
- no logits/probability dump in the artifact
- no label body in the artifact
- no split body in the artifact
- no calibration policy body in the artifact
- no private paths
- no test-derived temperature
- no test-derived threshold
- no performance claim
- no `final_text`
- no `observed_after_text`
- no `gold_label`
- `content_suppressed` is true
- `no_raw_rows` is true
- `synthetic_only` is true
- `no_oracle_checked` is true
- `test_tuning_forbidden` is true

If any check fails, the scaffold should not write the artifact. Failure output
should include safe reason codes and metadata only.

## 12. Path / Output Policy

Future default output should be restricted to synthetic fixture outputs or an
explicit temporary location chosen by the implementation step.

Policy:

- automated checks should not use `manual_outputs/`
- public docs must not include artifact body
- future generated artifacts must be synthetic-only unless a private,
  institution-approved real-data review exists later
- private or real-data paths must be rejected by default
- generated output files must not be added to Git unless they are intentional
  synthetic fixture files from a later fixture step
- safe summaries should use case ids and counts, not private absolute paths

## 13. Relation To Frozen Policy Validator

The generator should call the frozen policy validator after constructing a
candidate artifact.

Relationship:

- the generator constructs metadata
- the validator independently checks the artifact contract
- the generator must not bypass the validator
- release-quality currently checks the validator contract, not generation
  quality
- future generator tests should assert that generated artifacts pass the
  frozen policy validator

The validator remains the fail-closed gate for artifact acceptance.

## 14. Relation To Calibration Scaffold

The calibration scaffold may later compute or select temperature and threshold
values. The frozen policy generation scaffold records those selected values
and their validation-only provenance in the frozen artifact.

Initial design should allow:

- identity temperature
- fixed confidence threshold
- fixed abstention rate
- validation-only provenance
- frozen policy validator compatibility

Metric computation and final evaluation remain separate from both scaffold
layers.

## 15. Future Fixture Design

Future fixture candidates:

- valid identity temperature policy generation
- valid fixed abstention rate policy generation
- invalid generator attempt with test-derived threshold
- invalid generator attempt with test-derived temperature
- invalid generator attempt with logits dump
- invalid generator attempt with raw row carryover
- invalid generator attempt with missing validation split

This step does not create fixture files.

Step235 expands this fixture planning in the
[frozen policy generation fixture design](frozen_policy_generation_fixture_design.md).
It defines the future fixture root, valid/invalid case structure, request and
pointer files, expected generation result metadata, and reason-code mapping
without creating fixtures.

Step236 creates the initial fixture metadata under
`tests/fixtures/learner_state_frozen_policy_generation/` without adding
generator code, generated policy artifacts, or release-quality integration.

## 16. Testing Plan For Future Implementation

Future tests should cover:

- generator refuses unvalidated input
- generator refuses selective prediction validator failure
- identity temperature frozen policy validates
- fixed threshold frozen policy validates
- test-derived temperature is rejected
- test-derived threshold is rejected
- no raw rows in output
- no logits dump in output
- generated policy passes frozen policy validator
- safe summary only
- no performance claim
- no private path in stdout, stderr, or JSON output

Tests should use synthetic fixtures only.

## 17. Release-Quality Future

Do not add generator checks to release-quality yet.

Recommended staging:

1. Design the generator scaffold.
2. Design synthetic generator fixtures. Step235 adds the docs-only fixture
   design for this stage.
3. Create initial synthetic generator fixtures. Step236 adds metadata-only
   fixture files for this stage.
4. Design generation fixture validation. Step237 adds the docs-only validation
   design for this stage.
5. Implement minimal generation fixture validation. Step238 adds
   the safe fixture validator implementation.
6. Design the safe generation validator CLI. Step239 adds the docs-only CLI
   design for this stage.
7. Implement the safe generation validator CLI. Step240 adds the minimal CLI
   implementation and tests for this stage.
8. Implement minimal generator with fixture tests after validator behavior is
   stable.
9. Add a standalone Makefile target.
10. Review output/log safety.
11. Integrate into release-quality only after standalone safety is stable.
12. Record a public-safe remote/manual run status if integrated later.

This mirrors the Milestone 10 pattern and keeps release-quality from running
unstable generation code too early.

## 18. What This Does Not Do

This design does not:

- implement a generator
- create a frozen policy artifact
- compute temperature
- compute threshold
- calibrate a model
- run selective prediction
- train an estimator
- compute metrics
- use real data
- prove performance
- change release-quality
- change GitHub Actions workflows
- change Makefile targets
- change Python code
- change tests
- change fixtures

## 19. Beginner Notes

A frozen policy generation scaffold is the future piece that would write the
metadata file saying which temperature and abstention threshold are fixed
before test evaluation.

The generator comes after the validator because unsafe prediction, label,
split, or policy inputs should be rejected before any frozen policy is made.

The generated frozen policy should then be passed through the frozen policy
validator because constructing a file and trusting a file are separate safety
steps. A generator bug should not automatically make an artifact acceptable.

Validation split only means that tuning choices are made from a held-out
validation portion of the synthetic fixture, not from the final test split.
This avoids using test labels to choose a better-looking policy.

Success would mean that the scaffold followed the artifact contract. It would
not mean the model is accurate, calibrated, useful, production-ready, or
real-data-ready.

## 20. Step277 Metadata-Only Generator Scaffold Boundary

Step277 updates this scaffold design after the runtime infrastructure and
artifact policy work. The initial generator scaffold should now be understood
as a metadata-only generation planning layer, not as a body-producing generator
and not as an artifact writer.

Current state:

- runtime skeleton exists
- artifact policy design exists
- scaffold fixture validator exists
- release-quality runtime smoke exists
- generator is not implemented
- artifact body generation is not allowed yet
- artifact file writing is not allowed yet
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`

The generator scaffold is distinct from:

- runtime scaffold: the outer safety shell that loads request/pointer metadata
- generator scaffold: the future metadata-only generation planning layer
- artifact writer: a future file-writing component, not part of this stage
- artifact validator: a future metadata/body safety checker
- frozen policy validator: the existing frozen policy fixture validator
- frozen policy generation validator: the existing generation contract checker
- selective prediction validator: the existing calibration safety validator
- learner-state estimator: separate estimator work, not part of this scaffold

Initial generator scaffold responsibilities:

- read generation request metadata
- read input pointer metadata
- reference validated metadata only
- verify safety, no-oracle, and synthetic-only flags
- verify validation references
- build an artifact metadata plan
- return a safe metadata-only generation result
- return fail-closed results for invalid input
- return deterministic reason codes and failed checks
- return JSON serializable safe summaries

Initial generator scaffold non-goals:

- artifact body generation
- policy JSON body generation
- artifact file writing
- output directory creation
- real data loading
- raw row loading
- logits dump loading
- learner text loading
- calibration fitting
- threshold tuning from test data
- model training
- metric computation
- performance reporting
- estimator training
- release-quality generator integration

Allowed input metadata:

- generation request metadata
- input pointer metadata
- validation reference IDs
- frozen policy validation status
- selective prediction validation status
- split policy label
- calibration policy label
- threshold policy label
- abstention policy label
- synthetic fixture labels
- schema version
- safe IDs
- count-only summaries

Forbidden input and output content:

- request or pointer body payloads
- raw rows
- logits/probability dumps
- generated policy bodies
- artifact bodies
- full policy JSON bodies
- calibration bodies
- label bodies
- split bodies
- raw learner text
- `final_text`
- `observed_after_text`
- `gold_label`
- expected action used as scoring feedback
- private paths
- real participant data
- performance metric bodies

Allowed output metadata:

- generation status
- request ID
- pointer ID
- policy ID
- artifact ID
- generator version
- validation reference IDs
- reason codes
- failed checks
- safety flags
- artifact flags
- count-only summary
- safe summary label
- schema version

Docs-only data model candidates:

- `FrozenPolicyGeneratorScaffoldRequest`
- `FrozenPolicyGeneratorInputPointer`
- `FrozenPolicyGeneratorMetadataPlan`
- `FrozenPolicyGeneratorArtifactMetadata`
- `FrozenPolicyGeneratorScaffoldResult`
- `FrozenPolicyGeneratorSafetySummary`
- `FrozenPolicyGeneratorScaffoldError`

Docs-only API candidates:

- `build_frozen_policy_generation_metadata_plan(request, pointer)`
- `validate_frozen_policy_generation_metadata_plan(plan)`
- `run_frozen_policy_generation_metadata_scaffold(request_path, pointer_path)`
- `summarize_frozen_policy_generation_metadata_result(result)`
- `audit_frozen_policy_generation_artifact_metadata(result)`

Initial artifact flags:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=false`
- `artifact_validation_summary_available=true` only for safe metadata-only
  validation summaries

Candidate fail-closed reason codes:

- `missing_validation_reference`
- `unvalidated_input`
- `unsafe_path`
- `raw_rows_carryover`
- `logits_dump_carryover`
- `generated_artifact_body_leakage`
- `artifact_file_writing_not_allowed`
- `private_path_output`
- `test_temperature_tuning`
- `test_threshold_tuning`
- `scoring_feedback_violation`
- `performance_claim_in_generated_policy`
- `request_body_leakage`
- `pointer_body_leakage`
- `unknown_schema_version`
- `missing_required_field`

No-oracle policy:

- no `observed_after_text`
- no `final_text`
- no `gold_label`
- no expected action as scoring feedback
- no test-derived tuning
- no validation/test leakage into generation
- no scoring feedback loop
- no oracle labels in metadata plans
- fail closed if any forbidden field appears

Synthetic-only policy:

- initial generator scaffold uses synthetic fixtures only
- no real data
- no participant data
- no private data
- no `manual_outputs`
- no real output directory
- all public generator outputs are metadata-only

Artifact body suppression policy:

- generator scaffold does not create bodies
- CLI must not print bodies
- docs must not show bodies
- release-quality must not log bodies
- status markers must not store bodies
- tests must scan for absence of body-like fields
- body generation requires a separate milestone

Future validation strategy:

- valid metadata plan passes
- invalid raw rows fail
- invalid logits fail
- invalid private path fails
- invalid body leakage fails
- invalid test tuning fails
- invalid scoring feedback fails
- missing validation reference fails
- output is deterministic
- summary is JSON serializable
- stdout/stderr have no body leakage
- no file writing occurs
- no tmp output is created by the generator scaffold path

Future fixture root candidate:

- `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`

Candidate valid fixture cases:

- `valid/minimal_metadata_only_generation_plan`
- `valid/validated_fixed_threshold_metadata_plan`
- `valid/validated_fixed_abstention_rate_metadata_plan`

Candidate invalid fixture cases:

- `invalid/missing_validation_reference`
- `invalid/raw_rows_carryover`
- `invalid/logits_dump_carryover`
- `invalid/generated_artifact_body_leakage`
- `invalid/artifact_file_writing_attempt`
- `invalid/private_path_output`
- `invalid/test_temperature_tuning`
- `invalid/test_threshold_tuning`
- `invalid/scoring_feedback_violation`
- `invalid/performance_claim_in_generated_policy`

The generator scaffold should build on the runtime scaffold and artifact
policy. It should not weaken runtime suppression, should keep release-quality
runtime smoke separate from future generator checks, and should not enter
release-quality until no-body-leakage tests exist.

This design does not prove that a generator works, that artifact bodies exist,
that policy quality is good, that model performance is acceptable, that
calibration or selective prediction is correct, that the learner-state
estimator is correct, or that the system is real-data-ready or
production-ready.

Next recommended steps:

- generator scaffold fixture design
- generator scaffold validator design
- generator scaffold skeleton implementation
- generator scaffold CLI design

Step278 adds the fixture design for that next step at
[Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md).
It keeps fixture creation, generator code, artifact body generation, artifact
file writing, metrics, real-data use, and release-quality generator integration
out of scope.

Step279 creates the metadata-only generator scaffold fixture root at
`tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.
The fixture root is still not a generator implementation and does not add
artifact body generation, artifact file writing, metrics, or real-data
readiness.

## 21. Update History

- Step234: initial frozen policy generation scaffold design creation.
- Step235: linked the frozen policy generation fixture design as the next
  docs-only planning step.
- Step236: linked the initial frozen policy generation fixture root.
- Step237: linked the frozen policy generation validation design.
- Step238: linked the minimal frozen policy generation fixture validator
  implementation.
- Step239: linked the frozen policy generation validator CLI design.
- Step240: linked the minimal frozen policy generation validator CLI
  implementation.
- Step241: linked the frozen policy generation validator Makefile target
  design.
- Step242: linked the standalone generation validator Makefile target
  implementation status; generator scaffold remains unimplemented.
- Step243: linked the release-quality integration design; generator scaffold
  remains unimplemented.
- Step244: linked the release-quality wrapper integration status; generator
  scaffold remains unimplemented.
- Step248: linked the frozen policy generation scaffold implementation design;
  scaffold code and generator code remain unimplemented.
- Step277: added the metadata-only generator scaffold boundary after artifact
  policy design; generator code, artifact body generation, artifact writing,
  metrics, release-quality generator integration, and real-data behavior remain
  out of scope.
- Step278: linked the metadata-only generator scaffold fixture design;
  fixture files, generator code, artifact body generation, artifact writing,
  metrics, release-quality generator integration, and real-data behavior remain
  out of scope.
- Step279: linked the created metadata-only generator scaffold fixture root;
  generator code, fixture validator code, artifact body generation, artifact
  writing, metrics, release-quality generator integration, and real-data
  behavior remain out of scope.
- Step280: linked the metadata-only generator scaffold fixture validator
  design; validator code, generator code, artifact body generation, artifact
  writing, metrics, release-quality generator integration, and real-data
  behavior remain out of scope.

## Related Documents

- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Frozen policy generation release-quality integration design](frozen_policy_generation_release_quality_integration_design.md)
- [Milestone 09 selective prediction validation infrastructure recap](milestone_09_selective_prediction_validation_infrastructure_recap.md)
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation validator Makefile target design](frozen_policy_generation_validator_makefile_target_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
- [Frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md)
- [Public release checklist](public_release_checklist.md)
