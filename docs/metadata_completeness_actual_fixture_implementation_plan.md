# Metadata Completeness Actual Fixture Implementation Plan

This document describes a future implementation plan for an actual metadata
completeness explicit config fixture.

It is implementation planning documentation only. It does not create the
fixture, add a weight config file, choose final weight values, create an
approval record, change scorer logic, change the scoring formula, change
deterministic tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to define the implementation plan that should be
followed before entering a future actual fixture implementation step.

This plan preserves these boundaries:

- actual fixture is not created here
- actual weight is not chosen here
- approval record is not created here
- no-config default remains unchanged
- scorer logic remains unchanged
- this is not performance evaluation
- this is not expected-action tuning

The plan is a guardrail for a later implementation step, not the implementation
itself.

## 2. Preconditions

Before any actual fixture implementation begins, confirm:

- readiness checklist is complete
- approval record is private/local or separately reviewed
- final value selection is separately approved using
  [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- any proposed value candidate has been reviewed from
  [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
  or a later equivalent proposal
- the proposed value candidate approval checklist has been completed using
  [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- the fixture preflight check is complete using
  [Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md)
- no-config fixture lock is current and passing
- config validation is expected to pass
- output safety requirements are understood
- rollback criteria are documented
- implementation will not change scorer logic

If any precondition is missing, stop before creating the fixture.

## 3. Files That May Be Changed In A Future Implementation Step

The following files or areas may be changed in a future implementation step, if
approved.

Do not change them in this planning step.

- `tests/fixtures/synthetic/hand_weight_configs/valid/metadata_completeness_tiny_weight_config.json`
- `tests/fixtures/synthetic/hand_weight_configs/invalid/...`, only if a new
  invalid fixture is needed for validation coverage
- `docs/metadata_completeness_config_fixture_design.md`
- `docs/metadata_completeness_tiny_weight_selection_design.md`
- `docs/README.md`
- config validation test fixture documentation, if needed

Even in the future implementation step, scorer logic should remain unchanged.
The fixture should exercise the existing explicit config path.

## 4. Files And Areas Not To Change

The future implementation step should not change:

- scorer algorithm
- scoring formula
- deterministic tie-break policy
- no-config fixture expected outputs
- no-config summary behavior
- `scripts/run_synthetic_e2e_summary.sh` no-config behavior
- raw event fixtures, unless a separate reason and review exist
- real data
- private data
- manual output data
- participant data
- actual filled observation notes in the public repository
- actual approval records in the public repository unless separately reviewed

If the future fixture requires changing scorer logic, it is no longer this
experiment.

## 5. Planned Fixture Contents

A future metadata completeness fixture should include:

- `config_schema_version`
- `config_name`
- `created_for`
- `synthetic_only_notice`
- `expected_action_usage_policy`
- `forbidden_information_policy`
- active constraints only from metadata completeness candidates
- tiny positive weights only
- no blocking constraints beyond existing safety policy declarations
- rationale per constraint
- `no_oracle_safe_reason` per constraint
- `tests_required` per constraint
- `risk_note` per constraint

Candidate active constraints may include only:

- `CANDIDATE-METADATA-COMPLETE`
- `HAS-GENERATION-RULE`
- `HAS-ACTION-FAMILY`
- `CANDIDATE-FAMILY-BUCKET`

The config JSON body should not be pasted into docs beyond the fixture file
itself.

## 6. Future Implementation Verification Order

Use this order in the future implementation step:

1. Create the fixture.
2. Run config validation first.
3. Run no-config fixture lock.
4. Run explicit config ranking diff.
5. Run config-enabled E2E smoke.
6. Run config-enabled summary smoke.
7. Run synthetic diagnostic distribution check.
8. Run full Python checks.
9. Run full Rust checks.
10. Run full TypeScript checks.
11. Verify safe stdout.
12. Verify Git-ignored `tmp/` outputs.
13. Verify no raw/config body was pasted into docs.

If config validation fails, stop before running ranking or E2E checks.

## 7. Expected Result

Expected future implementation result:

- config validation passes
- no-config output remains unchanged
- explicit config path may produce count-only diff
- config-enabled output remains separate
- config-enabled summary remains separate
- no performance claim
- no expected-action tuning
- no grammar correctness claim
- no raw JSONL body in docs or stdout
- no config body pasted into docs

The fixture should demonstrate explicit config wiring and safe review
boundaries. It should not prove better ranking.

## 8. Stop / Rollback Criteria

Stop or roll back if:

- no-config fixture lock changes
- config validation fails
- unsafe stdout appears
- output separation breaks
- metadata weight dominates ranking
- expected-action tuning appears
- performance claim appears
- rationale is incomplete
- config body is copied into docs
- JSONL body is copied into docs
- summary body is copied into docs
- reviewer approval is missing

Rollback should remove or disable the explicit fixture without changing the
default no-config path.

## 9. Public Documentation Policy

Public docs may describe:

- fixture purpose
- synthetic-only scope
- no-oracle rationale
- test plan
- count-only expected effect
- rollback criteria

Public docs must not paste:

- config JSON body
- score rows
- summary CSV body
- diagnostic summary body
- raw JSONL body
- expected action details
- raw learner text
- private/manual/real paths

The fixture file itself may exist under synthetic fixtures only after approved
implementation.

Actual approval records remain private/local unless separately reviewed for
public sharing.

## 10. Beginner Explanation

### What Is An Implementation Plan?

An implementation plan explains how a future change should be made and checked.

It is not the change itself.

### Why Not Create The Fixture Yet?

The fixture can affect explicit-config scoring behavior. It should only be
created after readiness, approval, and value-selection reviews are complete.

### Why Not Change Scorer Logic?

This experiment is about testing an explicit config fixture, not changing the
scorer algorithm.

If scorer logic changes, it becomes a different project step.

### Why Check No-Config Fixture Lock First?

The no-config path is the baseline.

If no-config output changes, the explicit config experiment has leaked into
default behavior.

### Why Run Config Validation First?

Config validation catches schema, rationale, forbidden-field, and unknown
constraint problems before scoring or E2E output is generated.

Failing early keeps the experiment safer and easier to roll back.

## 11. Related Documents

- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- [Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
