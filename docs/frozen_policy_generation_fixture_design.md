# Frozen Policy Generation Fixture Design

This document designs future synthetic fixtures for a frozen policy generation
scaffold.

It is documentation only. It does not implement a generator, create fixture
files, create a frozen policy artifact, implement calibration, implement
selective prediction, train a learner-state estimator, add a model, compute
metrics, change GitHub Actions workflows, change the release-quality wrapper,
change Makefile targets, change Python code, change tests, or change existing
fixtures. It is not a performance evaluation and is not a real-data readiness
claim.

The fixture design assumes synthetic-only inputs and safe metadata-only
expected results. Public docs must not include raw GitHub Actions logs, full
job output, copied log blocks, screenshots containing raw logs, frozen policy
artifact bodies, JSON bodies, policy bodies, raw rows, logits/probability
dumps, prediction row bodies, label bodies, split bodies, calibration policy
bodies, generated feature/label/manifest bodies, private paths, raw learner
text, or real participant data.

## 1. Purpose

The purpose of this document is to design a future fixture set for testing
frozen policy generation.

The future fixture set should let a generator implementation prove, using
synthetic-only inputs, that it can:

- require validated selective prediction input
- use validation-only temperature metadata
- use validation-only threshold / abstention metadata
- produce a frozen policy artifact shape that can pass the frozen policy
  validator
- refuse unsafe generation attempts fail-closed
- report only safe expected generation metadata

Step236 creates the initial synthetic fixture root and metadata files described
by this design. It still does not create generated artifacts or
validator/generator code.

## 2. One-Sentence Summary

Frozen policy generation fixtures are a future synthetic fixture set for
checking whether validated selective prediction input and generation policy
metadata can produce a safe frozen policy artifact, while unsafe generation
attempts fail closed without exposing raw rows, logits dumps, labels, policy
bodies, private paths, or performance claims.

## 3. Fixture Root Candidate

Candidate roots:

| Candidate | Assessment |
| --- | --- |
| `tests/fixtures/learner_state_frozen_policy_generation/` | Recommended; concise, learner-state scoped, and focused on generation rather than validation |
| `tests/fixtures/learner_state_frozen_policy_generator/` | Clear but names the tool rather than the fixture purpose |
| `tests/fixtures/learner_state_frozen_selective_prediction_policy_generation/` | Most explicit but too long for repeated fixture paths |
| `tests/fixtures/frozen_policy_generation/` | Short but less consistent with learner-state fixture roots |

Recommended root:

```text
tests/fixtures/learner_state_frozen_policy_generation/
```

Reason:

- keeps the learner-state namespace
- distinguishes generation fixtures from frozen policy validation fixtures
- leaves room for request, pointer, expected result, and future generated
  artifact expectations
- avoids very long path names

Step236 creates the root with initial synthetic-only fixture metadata:

- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)

## 4. Fixture Case Structure

Future valid fixture candidates:

- `valid/identity_temperature_fixed_threshold/`
- `valid/identity_temperature_fixed_abstention_rate/`
- `valid/validation_nll_temperature_metadata_only/`

Future invalid fixture candidates:

- `invalid/unvalidated_input/`
- `invalid/selective_prediction_validator_failure/`
- `invalid/test_derived_temperature/`
- `invalid/test_derived_threshold/`
- `invalid/raw_rows_carryover/`
- `invalid/logits_dump_carryover/`
- `invalid/missing_validation_split/`
- `invalid/private_path_output/`
- `invalid/performance_claim_generation/`
- `invalid/frozen_policy_validator_failure/`

The invalid fixtures are synthetic safety cases. They should be used to ensure
the generator refuses unsafe requests or unsafe generated artifacts. Step236
creates the initial valid and invalid directories as metadata-only fixture
cases.

## 5. Fixture File Set

Future per-case files:

| File | Role |
| --- | --- |
| `generation_request.json` | Safe metadata request describing temperature, threshold, output, and safety policy |
| `input_fixture_pointer.json` | Safe pointer to an existing selective prediction fixture case or root |
| `expected_frozen_policy_validation_result.json` | Safe expected result for the generated artifact after frozen policy validation |
| `expected_generation_result.json` | Safe expected result for generator behavior and failure reason matching |
| `README.md` | Optional short case or root explanation |

Step236 fixture files are safe metadata files only. They do not include
generated frozen policy artifact bodies.

The fixture files should not duplicate prediction rows, label rows, split
metadata bodies, calibration policy bodies, logits/probability dumps, frozen
policy artifact bodies, raw learner text, private paths, or generated
feature/label/manifest bodies in public docs.

## 6. `generation_request` Design

`generation_request.json` should contain safe metadata only.

Candidate fields:

- `generation_request_schema_version`
- `request_id`
- `source_selective_prediction_fixture`
- `temperature_policy`
- `threshold_policy`
- `output_policy`
- `safety_policy`
- `synthetic_only`
- `content_suppressed`

Design rules:

- request ids should be synthetic and stable
- source fixture references should be safe relative paths or case ids
- valid requests should use validation-only or identity temperature provenance
- valid requests should use validation-only threshold provenance
- output policy should forbid private paths and manual output paths
- safety policy should require no raw rows, no logits dumps, no performance
  claims, and frozen policy validator pass

Forbidden in generation requests:

- raw predictions
- raw labels
- logits dumps
- probability dumps
- private paths
- real participant identifiers
- test-derived metadata in valid cases
- raw learner text
- performance metric claims

## 7. `input_fixture_pointer` Design

`input_fixture_pointer.json` should point to existing selective prediction
fixture inputs without copying their bodies.

It should declare:

- safe relative path or fixture case id
- expected selective prediction validator status
- validation split availability
- learner-disjoint expectation
- no label in prediction row expectation
- no raw learner text in public output expectation
- no test-derived tuning expectation

Pointer rules:

- use safe relative paths only
- do not copy `predictions.jsonl` body
- do not copy `labels.jsonl` body
- do not copy `split_metadata.json` body
- do not copy `calibration_policy.json` body
- do not include private or absolute local paths

The pointer file is the bridge from input-contract fixtures to generation
fixtures. It should preserve traceability without duplicating content-bearing
rows.

## 8. `expected_generation_result` Design

`expected_generation_result.json` should contain safe metadata only.

Candidate fields:

- `generation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_output_status`
- `expected_frozen_policy_validation_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_checked`

Forbidden in expected generation results:

- generated frozen policy body
- raw rows
- logits dump
- probability dump
- label body
- split body
- calibration policy body
- private paths
- raw learner text
- performance metrics

Expected result mismatch output should remain safe: case id, expected status,
observed status, reason codes, and stage names only.

## 9. Valid Fixture Design

Future valid fixtures should show:

- selective prediction validator pass expected
- validation split available
- learner-disjoint split expected
- no label in prediction row expected
- temperature source is `validation` or identity `none_identity`
- threshold source is `validation`
- generated policy expected to pass frozen policy validator
- `content_suppressed` true
- `no_raw_rows` true
- `synthetic_only` true
- `no_oracle_checked` true
- `test_tuning_checked` true
- no private paths
- no raw rows
- no logits dump
- no performance claim

Suggested valid cases:

- `valid/identity_temperature_fixed_threshold/`: identity temperature and
  fixed validation-sourced threshold metadata.
- `valid/identity_temperature_fixed_abstention_rate/`: identity temperature
  and validation-sourced fixed abstention-rate policy.
- `valid/validation_nll_temperature_metadata_only/`: validation-sourced NLL
  selection metadata without implementing NLL computation in the fixture
  design.

Valid generation success is not performance evidence. It only means the
future generator created safe metadata and the generated artifact contract
validated.

## 10. Invalid Fixture Design

Future invalid fixtures and expected primary failure reasons:

| Fixture case | Expected failure reason | Purpose |
| --- | --- | --- |
| `invalid/unvalidated_input/` | `unvalidated_input` | Refuse generation when validator pass is absent |
| `invalid/selective_prediction_validator_failure/` | `selective_prediction_validator_failure` | Refuse generation when input validator fails |
| `invalid/test_derived_temperature/` | `test_temperature_tuning` | Refuse temperature provenance from test split |
| `invalid/test_derived_threshold/` | `test_threshold_tuning` | Refuse threshold provenance from test split |
| `invalid/raw_rows_carryover/` | `raw_rows_in_generated_policy` | Refuse generated artifact that carries row bodies |
| `invalid/logits_dump_carryover/` | `logits_dump_in_generated_policy` | Refuse generated artifact that carries logits/probability dumps |
| `invalid/missing_validation_split/` | `missing_validation_split` | Refuse generation without validation split |
| `invalid/private_path_output/` | `unsafe_path` | Refuse private or manual-output path targets |
| `invalid/performance_claim_generation/` | `performance_claim_in_generated_policy` | Refuse generated performance claims |
| `invalid/frozen_policy_validator_failure/` | `frozen_policy_validator_failure` | Refuse write/acceptance when frozen policy validator rejects output |

Invalid fixture output should include reason codes only. It should not echo
unsafe field values or artifact bodies.

## 11. Failure Reason Code Design

Recommended primary reason codes:

- `unvalidated_input`
- `selective_prediction_validator_failure`
- `test_temperature_tuning`
- `test_threshold_tuning`
- `raw_rows_in_generated_policy`
- `logits_dump_in_generated_policy`
- `missing_validation_split`
- `unsafe_path`
- `performance_claim_in_generated_policy`
- `frozen_policy_validator_failure`
- `malformed_generation_request`
- `missing_generation_file`
- `invalid_temperature_policy`
- `invalid_threshold_policy`
- `invalid_output_policy`
- `forbidden_field`

Reason code categories:

- input validation gate
- request schema
- split policy
- test tuning leakage
- forbidden body carryover
- path safety
- performance claim
- frozen policy validator gate

Future tests may assert one primary reason while still allowing additional
safe reason codes for richer diagnostics.

## 12. Future Generation Checks

Future generator validation should check:

- fixture file presence
- JSON parse
- known generation request schema version
- input pointer safety
- selective prediction validator pass
- validation split presence
- learner-disjoint split expectation
- no test-derived temperature
- no test-derived threshold
- no raw rows carryover
- no logits/probability carryover
- no private paths
- no performance claims
- generated frozen policy passes frozen policy validator
- expected-result matching

The generator should fail before writing output when a request is unsafe. If
an artifact candidate is constructed, it should be accepted only after frozen
policy validation passes.

## 13. Relation To Existing Fixtures

Existing selective prediction fixtures provide input contract examples:

- predictions
- labels
- split metadata
- calibration policy
- expected selective prediction validation result

Existing frozen policy fixtures provide output artifact contract examples:

- frozen policy metadata
- expected frozen policy validation result
- safe fail-closed invalid cases

Future generation fixtures connect those two layers. They should point to
input fixtures and expected frozen policy validation metadata without copying
raw prediction or label bodies into docs.

## 14. Relation To Frozen Policy Validator

Generated artifacts must pass the frozen policy validator before they are
accepted.

Fixture implications:

- valid generation cases should expect frozen policy validation pass
- invalid cases may intentionally trigger frozen policy validator failure
- generator expected results should record only safe validation status and
  reason codes
- generated artifact bodies should not be pasted into docs

The generator constructs candidate metadata. The frozen policy validator
decides whether that metadata is safe enough to accept.

## 15. Relation To Release-Quality

Generation fixtures are not included in release-quality yet.

Future staging:

1. Create fixture files after this design.
2. Implement generator fixture tests.
3. Implement minimal synthetic-only generator.
4. Add safe CLI.
5. Add standalone Makefile target.
6. Review stdout, stderr, and JSON output safety.
7. Integrate into release-quality only after standalone target is stable.
8. Record remote/manual run status with metadata-only summaries if integrated.

This mirrors the Milestone 10 pattern and avoids adding generation work to
release-quality before its output safety is proven.

## 16. Testing Plan For Future Implementation

Future tests should cover:

- valid generation cases pass
- invalid generation cases fail with expected reason
- all expected files are exercised
- missing files fail safely
- malformed generation request fails safely
- no raw rows in generated artifact
- no logits dump in generated artifact
- generated artifact passes frozen policy validator
- unsafe generation refuses write
- expected mismatch output is safe
- stdout and stderr do not include private paths
- JSON output is safe and metadata-only
- no performance claim is emitted

Tests should use synthetic fixtures only and should not add manual or tmp run
outputs to Git.

## 17. What This Does Not Do

This design does not:

- create fixtures
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
- change workflows
- change Makefile
- change Python code
- change tests
- change existing fixtures

## 18. Beginner Notes

A generation fixture is a small synthetic test scenario for a future
generator. It describes an input pointer, a safe generation request, and the
expected result.

Valid fixtures show the happy path. Invalid fixtures show that unsafe requests
fail closed, such as trying to tune on test data or carry raw rows into the
generated policy.

The fixture uses an input pointer instead of copying prediction bodies because
prediction and label rows are content-bearing test data. Pointing to an
existing synthetic fixture keeps the relationship clear without duplicating
row bodies in docs.

The generated artifact must pass the frozen policy validator because the
generator and validator have different jobs. The generator writes candidate
metadata; the validator checks whether that metadata is safe.

Success is not performance evidence. It means only that the future generator
followed the synthetic fixture contract and safety boundaries.

## 19. Update History

- Step235: initial frozen policy generation fixture design creation.
- Step236: initial synthetic frozen policy generation fixture files created
  under `tests/fixtures/learner_state_frozen_policy_generation/`.
- Step238: linked the minimal frozen policy generation fixture validator;
  fixture files remain unchanged.
- Step239: linked the frozen policy generation validator CLI design as the
  next docs-only interface plan.

## Related Documents

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Frozen policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Public release checklist](public_release_checklist.md)
