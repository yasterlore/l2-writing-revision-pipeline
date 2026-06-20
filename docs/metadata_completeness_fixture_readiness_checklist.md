# Metadata Completeness Fixture Readiness Checklist

This checklist is for reviewing readiness before creating any actual metadata
completeness explicit config fixture.

It is documentation only. It does not create a fixture, choose an actual weight,
change scorer behavior, change the scoring formula, change deterministic
tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this checklist is to make sure a future metadata completeness
config fixture is reviewed before implementation.

This checklist confirms readiness for a later implementation step. It does not:

- create the actual fixture
- choose the actual weight
- modify any config file
- change no-config default behavior
- evaluate performance
- tune against expected actions

The default no-config path must remain unchanged.

## 2. Prerequisite Documents

Read these documents before using this checklist:

- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Score-active family selection revisit](score_active_family_selection_revisit.md)

If these documents disagree, stop and revise the design before creating a
fixture.

For the future implementation-step sequence, read
[Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md).
For the future final value approval process, read
[Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md).
Before any actual fixture implementation begins, use
[Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md).

## 3. Readiness Checklist

Use this as a pre-implementation checklist.

### Design Readiness

- [ ] fixture identity candidate defined
- [ ] target constraints defined
- [ ] non-target constraints defined
- [ ] tiny positive / no-blocking policy defined
- [ ] grammar correctness claim avoided
- [ ] expected effect is count-only
- [ ] no-config default unchanged requirement documented
- [ ] explicit `--weight-config` only requirement documented

### No-Oracle Readiness

- [ ] no expected action tuning
- [ ] no `final_text`
- [ ] no `observed_after_text`
- [ ] no `gold_label`
- [ ] no teacher correction
- [ ] no raw learner text
- [ ] no private data
- [ ] no real participant data
- [ ] candidate generation/ranking time availability confirmed

### Weight Rationale Readiness

- [ ] rationale per constraint
- [ ] tiny range justification
- [ ] why small
- [ ] why not blocking
- [ ] risk if too large
- [ ] why not performance optimization
- [ ] why not expected-action matching
- [ ] why not grammar correctness

### Config Schema Readiness

- [ ] current schema version confirmed
- [ ] required fields known
- [ ] rationale fields required
- [ ] no forbidden fields
- [ ] no unsafe path strings
- [ ] active constraints known
- [ ] validation expected to fail closed
- [ ] unknown active constraints rejected

### Output Safety Readiness

- [ ] no config body in stdout or docs
- [ ] no JSONL body in stdout or docs
- [ ] no summary body in docs
- [ ] no diagnostic summary body in docs
- [ ] no candidate score rows in docs
- [ ] safe path summary only
- [ ] `tmp/` outputs ignored
- [ ] no filled observation notes

### Test Readiness

- [ ] hand weight config validation
- [ ] no-config fixture lock unchanged
- [ ] explicit config ranking diff
- [ ] config-enabled E2E smoke
- [ ] config-enabled summary smoke
- [ ] synthetic diagnostic distribution check
- [ ] Python checks
- [ ] Rust checks
- [ ] TypeScript checks
- [ ] synthetic policy check
- [ ] `git diff --check`
- [ ] Markdown link check

### Rollback Readiness

- [ ] reject if no-config output changes
- [ ] reject if config validation fails
- [ ] reject if output separation breaks
- [ ] reject if unsafe stdout appears
- [ ] reject if expected-action tuning appears
- [ ] reject if performance claim appears
- [ ] reject if metadata weight dominates ranking
- [ ] reject if rationale incomplete
- [ ] rollback plan removes or disables only the explicit fixture
- [ ] rollback plan preserves no-config default behavior

### Reviewer Approval Readiness

- [ ] reviewer identified
- [ ] review date recorded outside this template or in a future approval record
- [ ] branch or commit context available
- [ ] blockers listed
- [ ] decision is `proceed`, `revise`, or `stop`
- [ ] approval is not based on performance metrics
- [ ] approval is not based on expected-action matching

## 4. Design Readiness Details

Before creating an actual fixture, confirm:

- fixture identity candidate is defined
- target constraints are limited to metadata completeness candidates
- non-target constraints are explicitly excluded
- tiny positive / no-blocking policy is documented
- grammar correctness claims are avoided
- expected effect is count-only

Target candidates may include:

- `CANDIDATE-METADATA-COMPLETE`
- `HAS-GENERATION-RULE`
- `HAS-ACTION-FAMILY`
- `CANDIDATE-FAMILY-BUCKET`

The fixture must not include unrelated diagnostic families.

## 5. No-Oracle Readiness Details

The fixture must not use:

- expected actions
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- raw learner text
- private data
- real participant data

All active constraints must be available at candidate generation or ranking
time.

## 6. Weight Rationale Readiness Details

Each active constraint needs a rationale that explains:

- why this constraint is included
- why the weight range is tiny
- why the constraint is not blocking
- what can go wrong if the weight is too large
- why this is not performance optimization
- why this is not expected-action matching

The rationale should describe auditability and traceability, not grammar
quality.

## 7. Schema / Output Safety / Test Readiness

Schema readiness requires:

- current config schema version confirmed
- required fields known
- rationale fields present
- no forbidden fields
- no unsafe path strings
- active constraints are known
- validation fails closed

Output safety readiness requires:

- no config body in stdout or docs
- no JSONL body in stdout or docs
- no summary body in docs
- no candidate score rows in docs
- safe path summaries only
- generated outputs under ignored paths

Test readiness requires the standard synthetic and config checks before and
after any future fixture implementation.

## 8. Rollback Readiness

Reject or roll back the fixture if:

- no-config output changes
- config validation fails
- output separation breaks
- unsafe stdout appears
- expected-action tuning appears
- performance claim appears
- metadata weight dominates ranking
- rationale is incomplete

Rollback should remove or disable the explicit fixture without changing the
default scorer path, no-config summaries, or no-config fixture locks.

## 9. Approval Record Template

For a dedicated blank template, use
[Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md).

Do not fill the template in this document. The shape below is a reminder for a
future approval record.

```text
reviewer:
date:
branch:
commit:
fixture_name_candidate:
config_name_candidate:
checklist_completed: yes/no
blockers:
decision: proceed / revise / stop
notes: count-only only
```

Actual approval records should not include config bodies, JSONL bodies, summary
bodies, score rows, raw text, expected action details, private paths, or
performance claims.

## 10. Beginner Explanation

### What Is A Readiness Checklist?

A readiness checklist is a pre-flight review before creating something that can
affect scoring behavior when explicitly used.

It helps catch design, privacy, no-oracle, and output-safety problems before
code or config changes happen.

### Why Is It Needed Before The Actual Fixture?

Even an explicit config fixture can change ranking when used.

The team should agree on rationale, tests, and rollback conditions first.

### Why Is The No-Config Fixture Lock Important?

The no-config path is the protected baseline.

If no-config output changes, the experiment has leaked into default behavior.

### Why Is Reviewer Approval Needed?

Reviewer approval ensures the fixture is understandable, no-oracle safe,
synthetic-only, and not justified by performance metrics.

### Why Not Judge By Performance Metrics?

This fixture would be a design experiment, not a model evaluation.

Performance metrics such as F1, accuracy, and calibration are out of scope at
this stage.

## 11. Related Documents

- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Score-active family selection revisit](score_active_family_selection_revisit.md)
