# Selective Prediction Calibration Scaffold Design

This document designs a future scaffold for selective prediction and
calibration work after the Milestone 09 validation infrastructure.

It is design documentation only. It does not implement calibration,
selective prediction, a learner-state estimator, estimator training, model
logic, metric computation, release-quality changes, workflow changes,
Makefile changes, fixture changes, or production data handling. It is not a
performance evaluation and is not a real-data readiness claim.

The scaffold described here assumes synthetic-only fixtures and safe,
metadata-only outputs. Public documentation must not include raw JSONL rows,
prediction row bodies, label row bodies, calibration policy bodies, split
metadata bodies, logits/probability dumps, generated feature/label/manifest
bodies, raw GitHub Actions logs, raw learner text, private paths, or real
participant data.

## 1. Purpose

The purpose of this document is to define the responsibilities and boundaries
for a future selective prediction / calibration scaffold before any
implementation work begins.

The scaffold design covers:

- what validated inputs it may read
- what policy and split boundaries it must enforce
- how future validation-only temperature selection should be represented
- how future validation-only threshold / abstention selection should be
  represented
- what a frozen policy artifact should contain
- what safe summaries may report
- what must remain explicitly out of scope

This document does not compute F1, accuracy, ECE, AURCC, calibration quality,
coverage-risk curves, or model performance. It does not train or evaluate a
learner-state estimator.

## 2. One-Sentence Summary

The selective prediction / calibration scaffold is a safe intermediate layer
that consumes validated prediction fixtures plus label, split, and policy
metadata, chooses future temperature and threshold settings from the validation
split only, freezes those settings into a policy artifact, and hands that
frozen policy to a later test-evaluation step without exposing raw rows or
using test labels for tuning.

## 3. Scaffold Responsibilities

The future scaffold should:

- read only fixture bundles that have passed the selective prediction
  validator
- confirm that the confidence definition is declared and supported
- use the validation split, and only the validation split, for future tuning
- hold a future temperature selection candidate
- hold a future threshold / abstention policy candidate
- construct a safe frozen policy artifact
- return a safe count-only / metadata-only summary
- reject any policy that allows test split tuning
- reject inputs with failed validation summaries
- reject split leakage before tuning decisions are made
- avoid duplicate validation logic where it can call the existing validator
- avoid printing raw rows, logits bodies, label bodies, split bodies, or
  policy bodies in public output

The scaffold should sit between fixture validation and any future estimator or
evaluation step. It should make the "what is allowed to be tuned" decision
explicit before performance evaluation exists.

## 4. What The Scaffold Does Not Do

The scaffold does not:

- train a model
- implement a learner-state estimator
- implement final selective prediction behavior over real data
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- compute coverage-risk curves
- report calibration quality
- produce final performance claims
- handle real data
- deploy production data collection
- update the OT scorer
- update the candidate generator
- update scoring formulas or tie-break behavior
- change manifest schemas
- use expected action as scoring feedback

The scaffold is infrastructure for freezing future policy choices, not proof
that those choices are good.

## 5. Input Design

Future scaffold inputs should be treated as already validated. A minimal input
bundle may include:

- validated `predictions.jsonl`
- `labels.jsonl`
- `split_metadata.json`
- `calibration_policy.json`
- selective prediction validation result summary
- optional estimator input manifest reference, if a later design needs to
  connect calibrated predictions back to an upstream synthetic estimator input
  bundle

Input roles:

- prediction rows are synthetic model-like outputs
- labels are target-side only
- split metadata controls train / validation / test separation
- calibration policy controls which tuning steps are allowed
- the validation result summary is the gate that decides whether scaffold work
  can proceed

Required precondition:

- the input bundle must pass the selective prediction validator first

The scaffold should not be a second parser that silently accepts unsafe data.
If the validator fails or cannot be run, the scaffold should fail closed.

## 6. Output Design

Future scaffold outputs may include:

- `calibration_summary.json`
- `frozen_selective_prediction_policy.json`
- optional `selective_prediction_decisions.jsonl` in a later step
- safe human summary
- safe manifest

These are candidates only. This step does not create output files or define a
final storage location.

Output constraints:

- public docs should not paste any output body
- generated files should not be committed unless a later design explicitly
  creates synthetic fixture expectations
- tmp or manual outputs should not be added to Git
- summaries should be count-only and policy-metadata-only
- no raw prediction rows, label rows, logits arrays, split bodies, policy
  bodies, raw learner text, private paths, or expected action bodies should be
  printed

## 7. Temperature Scaling Scaffold Design

Future temperature scaling, if implemented, should use validation split logits
and validation split labels only.

The future scaffold may represent a temperature candidate `T` that transforms
logits `z_i` into calibrated probabilities:

```text
p_i = softmax(z_i / T)
```

Selection policy:

- choose `T` by minimizing validation negative log-likelihood only
- record `temperature_source_split: validation`
- never use the test split to choose or adjust `T`
- store the selected `T` in the frozen policy artifact
- do not recompute or adjust `T` using test labels

This document does not implement temperature scaling and does not compute
validation NLL.

## 8. Threshold / Abstention Scaffold Design

Future threshold selection should use calibrated confidence on the validation
split only.

Initial recommended policy:

- use an allowed abstention rate `r`
- choose a confidence threshold from validation predictions only
- freeze that threshold before test evaluation
- abstain on future examples whose confidence is below the frozen threshold

Required boundary:

- test split labels must not influence the threshold

The future scaffold should record:

- the confidence definition used
- the threshold selection method
- the allowed abstention rate
- the selected threshold source split
- the fact that the policy is frozen

This document does not implement abstention, threshold selection, coverage,
risk, or evaluation metrics.

## 9. Frozen Policy Artifact Design

A future frozen policy artifact should contain safe metadata only.

Candidate fields:

- `policy_schema_version`
- `source_fixture_id`
- `confidence_definition`
- `temperature_value`
- `temperature_source_split`
- `threshold_value`
- `threshold_source_split`
- `allowed_abstention_rate`
- `selected_by`
- `frozen_at_step`
- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_forbidden`
- `content_suppressed`

Forbidden artifact content:

- raw prediction rows
- raw label rows
- logits or probability dumps
- label body
- expected action body
- test label tuning trace
- raw learner text
- real data path
- private absolute path
- generated feature/label/manifest bodies

The frozen policy is a reproducibility artifact for future synthetic-only
experiments. It is not a performance certificate.

Step220 expands this section in the
[frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md).
That follow-up document defines the recommended filename, schema version,
required fields, optional fields, forbidden fields, validation-only provenance,
and future artifact validation checks. It does not create an artifact file or
implement scaffold code.

## 10. Safe Reporting Design

Safe scaffold reporting should include only:

- input validation status
- checked file count
- prediction row count
- label row count
- split counts
- confidence definition
- selected policy metadata
- temperature source split
- threshold source split
- allowed abstention rate
- frozen policy status
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`

Safe reporting must not include:

- row bodies
- label bodies
- logits/probability dumps
- calibration policy body dumps
- split metadata body dumps
- raw learner text
- private paths
- real participant data
- F1, accuracy, ECE, AURCC, or performance claims

Metric names may be discussed as future evaluation concepts, but scaffold
success must not be framed as metric evidence.

## 11. Validation Boundary

The scaffold must only run after selective prediction validation passes.

Blocking conditions:

- validator result is fail
- required input file is missing or malformed
- policy allows test tuning
- policy source split is test for temperature
- policy source split is test for threshold
- split leakage is detected
- validation split is missing
- label appears in a prediction row
- future label/action aggregate appears in a prediction row
- raw learner text appears in public output

If any blocking condition occurs, the scaffold should fail closed and return a
safe reason-code summary only.

## 12. Split Policy

Split roles:

- training split: reserved for future estimator training design
- validation split: allowed source for temperature and threshold selection
- test split: final frozen policy evaluation only

Rules:

- no test labels during tuning
- no same learner across train / validation / test by default
- no label-dependent split assignment
- no outcome-dependent split assignment
- no post-hoc threshold change after seeing test behavior

The scaffold should preserve the learner-disjoint default introduced by the
fixture validation infrastructure.

## 13. No-Oracle / Leakage Policy

The scaffold must reject or refuse to proceed if it detects:

- test threshold tuning
- test temperature tuning
- expected action in prediction rows
- expected action aggregates in prediction rows
- future label aggregates
- future action summaries
- `final_text` in model-side inputs
- `observed_after_text` in model-side inputs
- `gold_label` in model-side inputs
- raw learner text in public output
- scoring feedback derived from expected action
- post-hoc teacher or human correction fields

Intentional invalid fixtures may contain some forbidden fields as test targets,
but the scaffold should report only safe reason codes and should not expose
the field bodies.

## 14. Relation To Milestone 09 Infrastructure

Milestone 09 already provides:

- selective prediction / calibration design
- synthetic fixture root
- prediction / label / split / policy fixture files
- fail-closed validator / loader
- fixture-based tests
- CLI
- Makefile target
- release-quality wrapper integration
- remote/manual run status marker

The scaffold should reuse this infrastructure rather than bypass it:

- call or require the selective prediction validator before scaffold work
- consume validated fixture metadata
- avoid duplicating row-level validation logic when possible
- keep expected action label-side only
- preserve no-test-tuning and no-oracle checks
- keep safe output defaults consistent with the CLI and release-quality logs

The scaffold is the next layer after validation and before estimator
prototype or evaluation work.

## 15. Implementation Roadmap

Recommended future order:

1. Step220: frozen policy artifact schema design.
2. Step221: frozen policy fixture design.
3. Step222: frozen policy validator design.
4. Step223: minimal frozen policy validator implementation.
5. Step224: calibration scaffold fixture design.
6. Step225: minimal validation-only calibration scaffold implementation.
7. Step226: threshold policy scaffold implementation.

Keep these steps narrow. Do not combine scaffold implementation, estimator
training, metric computation, release-quality integration, and real-data
readiness in one step.

Step220 adds the
[frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
as a docs-only schema plan for `frozen_selective_prediction_policy.json`.
It still does not implement calibration, selective prediction, frozen policy
generation, estimator training, or metric computation.

Step221 adds the
[frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
as a docs-only plan for future valid and invalid frozen policy fixtures. It
does not create fixture files, implement a frozen policy validator, or
generate artifacts.

Step222 creates the initial synthetic fixture root at
`tests/fixtures/learner_state_frozen_selective_prediction_policy/` so future
frozen policy validation can be tested against one valid fixture and eleven
intentional invalid fixtures without using real data, raw rows, logits dumps,
or performance claims.

Step223 adds the
[frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
as a docs-only fail-closed plan for validating frozen policy artifacts before
future scaffold outputs are consumed by test evaluation.

Step224 adds the minimal `python/learner_state/frozen_policy_validation.py`
validator for synthetic frozen policy fixtures. Future scaffold work should
call this boundary before treating a frozen policy artifact as safe.

## 16. Testing Plan For Future Implementation

Future tests should cover:

- validator failure blocks scaffold
- validation-only temperature source is accepted
- test temperature source is rejected
- validation-only threshold source is accepted
- test threshold source is rejected
- frozen policy safe JSON is produced
- no raw rows appear in output
- no logits dump appears in public summary
- no label body appears in public summary
- no policy or split body appears in public summary
- learner-disjoint split is preserved
- no metric claims appear in safe summaries
- expected action is not used as scoring feedback

These tests should use synthetic-only fixtures and safe count/reason-code
assertions.

## 17. What This Does Not Prove

This scaffold design does not prove:

- model performance
- calibration quality
- selective prediction correctness
- learner-state estimator correctness
- real-data readiness
- production data collection validity
- F1 evidence
- accuracy evidence
- ECE evidence
- AURCC evidence
- scoring model improvement

It only defines how future scaffold work should keep tuning boundaries and
public output safe.

## 18. Beginner Notes

A scaffold is a small support layer that connects already-validated inputs to
the next stage without doing the full final job yet.

The validator answers, "Is this fixture safe to trust as an input?" The
scaffold answers, "Given a safe input, what calibration or abstention policy
would be frozen before any test evaluation?"

Temperature changes the shape of model probabilities so confidence can become
less overconfident or underconfident. Thresholds decide when confidence is too
low and the system should abstain. Both must be chosen from validation data,
not test data, because the test set is supposed to remain an honest final
check.

A frozen policy is a saved decision. Once temperature and threshold are
selected from validation data, the policy is frozen and passed to a later test
step. It should not be adjusted after looking at test labels.

Scaffold success is not performance evidence. It only means the future
calibration/selective prediction path respected input validation, split
boundaries, no-oracle policy, and safe output rules.

## 19. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
- [Selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
- [Selective prediction calibration release-quality integration design](selective_prediction_calibration_release_quality_integration_design.md)
- [Selective prediction release-quality remote run record workflow](selective_prediction_release_quality_remote_run_record_workflow.md)
- [Learner-state selective prediction release-quality remote run status](status/learner_state_selective_prediction_release_quality_remote_run_status.md)
- [Milestone 09 selective prediction validation infrastructure recap](milestone_09_selective_prediction_validation_infrastructure_recap.md)
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
