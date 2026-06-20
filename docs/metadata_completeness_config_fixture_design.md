# Metadata Completeness Config Fixture Design

This document designs a possible future explicit config fixture for metadata
completeness.

It is design documentation only. It does not create the fixture, choose actual
weights, change scorer behavior, change the scoring formula, change deterministic
tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to specify what a future metadata completeness
explicit config fixture should look like if it is approved later.

This document does not:

- create an actual fixture
- add a weight config file
- choose exact weight values
- change no-config default scoring
- change config validation
- change E2E behavior
- claim accuracy, F1, calibration, grammatical correctness, or ranking quality

The fixture, if ever created, should be synthetic-only and explicit-config only.

Before selecting any concrete tiny value for that fixture, read
[Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md).
Before creating an actual fixture, use
[Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md).

## 2. Proposed Fixture Identity

Possible future fixture identity:

```text
fixture file name candidate:
  metadata_completeness_tiny_weight_config.json

config_name candidate:
  metadata_completeness_tiny_weight

created_for:
  synthetic_metadata_completeness_explicit_config_experiment

config_schema_version:
  current hand-weight config schema version at implementation time
```

This step does not create that file.

The name should not imply:

- production readiness
- real-data validation
- grammar correctness
- performance improvement
- expected-action fitting

## 3. Candidate Constraints

The following constraints are possible future candidates.

### `CANDIDATE-METADATA-COMPLETE`

Possible score-active status:

- candidate for a tiny explicit-config preference, if ever implemented

Weight direction:

- tiny positive preference for complete representation

Magnitude range:

- tiny and conservative only
- exact values are not selected in this document

Educational rationale:

- a candidate with complete metadata is easier to audit and explain

No-oracle-safe reason:

- uses candidate representation metadata available at scoring time

Risk note:

- completeness may be mistaken for quality or grammatical correctness

### `HAS-GENERATION-RULE`

Possible score-active status:

- candidate for a tiny explicit-config preference, if ever implemented

Weight direction:

- tiny positive preference for recorded provenance

Magnitude range:

- tiny and conservative only
- exact values are not selected in this document

Educational rationale:

- a recorded generation rule helps explain how the candidate was produced

No-oracle-safe reason:

- uses candidate metadata, not future text or expected actions

Risk note:

- may reward implementation bookkeeping rather than candidate usefulness

### `HAS-ACTION-FAMILY`

Possible score-active status:

- candidate for a tiny explicit-config preference, if ever implemented

Weight direction:

- tiny positive preference for interpretable action-family metadata

Magnitude range:

- tiny and conservative only
- exact values are not selected in this document

Educational rationale:

- action-family metadata makes the candidate's intended revision behavior easier
  to describe

No-oracle-safe reason:

- uses candidate metadata available before evaluation

Risk note:

- broad action-family metadata can become a shortcut if overweighted

### `CANDIDATE-FAMILY-BUCKET`

Possible score-active status:

- candidate for a tiny explicit-config preference only after extra review

Weight direction:

- tiny positive preference for coarse family-bucket metadata, if used at all

Magnitude range:

- tiny and conservative only
- exact values are not selected in this document

Educational rationale:

- family bucket metadata can support auditability and candidate grouping

No-oracle-safe reason:

- uses abstract candidate metadata, not raw text or expected actions

Risk note:

- bucket-level scoring can accidentally become a family-level ranking preference

## 4. Recommended Weight Policy

Recommended policy for any future fixture:

- tiny positive weight only, if ever implemented
- no blocking
- no large magnitude
- no performance-tuned magnitude
- no expected-action-tuned magnitude
- no grammar correctness claim
- no exact values selected in this design document
- rationale required per constraint
- no hidden defaults
- explicit `--weight-config` only
- no-config output must remain identical

The proposed meaning of the weight should be:

```text
prefer auditable candidate representation very slightly
```

It should not mean:

```text
prefer grammatically correct candidates
```

or:

```text
prefer candidates that match expected actions
```

## 5. Constraints Not To Make Score-Active

This fixture should not include:

- local pattern diagnostics
- linguistic placeholder diagnostics
- non-leaky linguistic diagnostics
- diagnostic summary counts
- observation note labels
- expected actions
- evaluation metrics
- exact-match results
- raw text-derived outputs
- final text
- observed-after text
- gold labels
- teacher or human corrections

Those require separate review or must remain permanently out of scoring.

## 6. Expected Effect, Count-Only

Expected effect of a future fixture:

- ranking diff may change candidate order only under explicit config
- weighted score may change only under explicit config
- no-config output must remain identical
- no-config fixture locks must remain passing
- diff review should be count-only
- stdout should remain safe summary only
- no raw candidate score rows should be printed
- no raw JSONL body should be printed or pasted into docs
- no config body should be printed or pasted into docs
- no performance claim should be made
- no grammatical correctness claim should be made

The purpose is to inspect whether the explicit config path works as expected,
not whether the ranking is better.

## 7. Required Tests For Future Fixture Implementation

Before any future fixture is added, require:

- weight config validation
- no-config fixture lock unchanged
- explicit config ranking diff
- config-enabled E2E smoke
- config-enabled summary smoke
- synthetic diagnostic distribution check
- safe stdout check
- no raw JSONL body in stdout or docs
- no config body in stdout or docs
- no summary body in docs
- no candidate score rows in docs
- Git-ignored `tmp/` outputs
- docs updated
- expected-action tuning absent
- performance claim absent

The future fixture should fail closed if validation fails.

## 8. Rollback / Rejection Criteria

Reject or roll back the fixture if:

- config validation fails
- no-config fixture lock changes
- unsafe stdout appears
- output path separation breaks
- config body appears in stdout or docs
- JSONL body appears in stdout or docs
- summary body appears in docs
- candidate score rows appear in docs
- weight rationale is incomplete
- expected-action tuning appears
- performance claim appears
- metadata weight dominates ranking
- interpretability is unclear
- reviewers cannot explain the weight without calling it correctness

Rollback should remove or disable the explicit config fixture without changing
the no-config default path.

## 9. Review Checklist Before Creating The Actual Fixture

Before creating any actual fixture, confirm:

- rationale complete
- leakage risk reviewed
- no-oracle safe
- no expected-action tuning
- no performance metric tuning
- tiny weight range justified
- no-config default protection confirmed
- rollback plan written
- reviewer approval recorded
- output safety requirements documented
- config-enabled outputs remain separate from no-config outputs

Approval should be about whether the experiment is safe and interpretable, not
whether it improves a metric.

## 10. Beginner Explanation

### What Is A Config Fixture?

A config fixture is a small example config file used in tests or smoke checks.

It helps verify that config loading and scoring behavior work as intended.

### Why Not Create The Fixture Immediately?

Even a small fixture can affect score output when used explicitly.

The team should first agree on the rationale, risks, tests, and rollback
conditions before creating it.

### Why Tiny Weight?

Metadata completeness is about auditability. It is a weak signal and should not
overpower safety, candidate family behavior, or diagnostic interpretation.

### Why Not Blocking?

Missing metadata is not the same as unsafe output.

Blocking is reserved for safety and leakage constraints.

### Why Not Grammar Correctness?

Complete metadata does not prove that a candidate is grammatically correct.

It only means the candidate is easier to describe.

### Why Is The No-Config Fixture Lock Important?

The no-config path is the protected baseline.

If a future explicit config fixture accidentally changes no-config output, it
breaks the experiment boundary.

## 11. Related Documents

- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Score-active family selection revisit](score_active_family_selection_revisit.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
