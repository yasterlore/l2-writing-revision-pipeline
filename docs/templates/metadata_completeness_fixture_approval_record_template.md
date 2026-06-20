# Metadata Completeness Fixture Approval Record Template

This is a blank template.

It is not an actual approval record. Do not commit filled approval records
without separate review. This template does not approve an actual config
fixture, choose a final weight value, evaluate performance, or authorize real
data use.

## 1. Record Status

- [ ] This is a blank template.
- [ ] This is not an actual approval record.
- [ ] No filled approval record is included here.
- [ ] No performance claim is included.
- [ ] No real participant data is included.
- [ ] No expected action tuning is included.
- [ ] Do not commit filled approval records without separate review.

## 2. Metadata

```text
reviewer:
repository_owner:
date:
branch:
commit_hash:
related_issue_or_pr:
fixture_name_candidate:
config_name_candidate:
config_schema_version_candidate:
```

## 3. Referenced Design Docs Checklist

- [ ] [Metadata completeness explicit config experiment design](../metadata_completeness_explicit_config_experiment_design.md)
- [ ] [Metadata completeness config fixture design](../metadata_completeness_config_fixture_design.md)
- [ ] [Metadata completeness tiny weight selection design](../metadata_completeness_tiny_weight_selection_design.md)
- [ ] [Metadata completeness fixture readiness checklist](../metadata_completeness_fixture_readiness_checklist.md)
- [ ] [Metadata completeness actual fixture implementation plan](../metadata_completeness_actual_fixture_implementation_plan.md)
- [ ] [Synthetic hand-weight rationale examples](../synthetic_hand_weight_rationale_examples.md)
- [ ] [Hand-weight config schema plan](../hand_weight_config_schema_plan.md)
- [ ] [Score-active family selection revisit](../score_active_family_selection_revisit.md)

## 4. Design Readiness Confirmation

- [ ] fixture identity defined
- [ ] target constraints defined
- [ ] non-target constraints defined
- [ ] tiny positive / no-blocking policy confirmed
- [ ] no grammar correctness claim
- [ ] count-only expected effect
- [ ] no-config default unchanged
- [ ] explicit `--weight-config` only

Notes, count-only only:

```text

```

## 5. No-Oracle Confirmation

- [ ] no expected action tuning
- [ ] no `final_text`
- [ ] no `observed_after_text`
- [ ] no `gold_label`
- [ ] no teacher correction
- [ ] no raw learner text
- [ ] no private data
- [ ] no real participant data
- [ ] candidate generation/ranking time availability confirmed

Notes, count-only only:

```text

```

## 6. Weight Rationale Confirmation

- [ ] rationale per target constraint
- [ ] tiny range justified
- [ ] why small
- [ ] why not blocking
- [ ] why not performance optimization
- [ ] why not expected-action matching
- [ ] risk if too large
- [ ] no grammar correctness claim

Notes, count-only only:

```text

```

## 7. Schema / Validation Confirmation

- [ ] current schema confirmed
- [ ] required fields known
- [ ] rationale fields present
- [ ] no forbidden fields
- [ ] no unsafe path strings
- [ ] validation expected to fail closed
- [ ] unknown active constraints rejected

Notes, count-only only:

```text

```

## 8. Output Safety Confirmation

- [ ] no config body in stdout or docs
- [ ] no JSONL body in stdout or docs
- [ ] no summary body in docs
- [ ] no diagnostic summary JSON body in docs
- [ ] no candidate score rows
- [ ] safe path summary only
- [ ] `tmp/` outputs ignored
- [ ] no filled observation notes

Notes, count-only only:

```text

```

## 9. Test Plan Confirmation

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

Notes, count-only only:

```text

```

## 10. Rollback / Rejection Confirmation

- [ ] reject if no-config output changes
- [ ] reject if config validation fails
- [ ] reject if output separation breaks
- [ ] reject if unsafe stdout appears
- [ ] reject if expected-action tuning appears
- [ ] reject if performance claim appears
- [ ] reject if metadata weight dominates ranking
- [ ] reject if rationale incomplete

Rollback notes, count-only only:

```text

```

## 11. Decision

```text
decision: proceed / revise / stop
blockers:
required_follow_up:
reviewer_signature_or_name:
repository_owner_approval:
date:
```

## 12. Do Not Include

Do not include:

- actual config JSON body
- raw JSONL body
- summary CSV body
- diagnostic summary JSON body
- candidate score rows
- expected action details
- `final_text`
- `observed_after_text`
- `gold_label`
- real participant identifiers
- private/manual/real paths
- performance claims
- F1
- accuracy
- calibration
- learner-state estimates

## 13. Beginner Notes

An approval record is a review format. It is not performance evaluation.

Filled approval records are private/local by default. If a filled record ever
needs to be placed in the public repository, it requires a separate public
sharing review.

This template does not approve the fixture by itself. It only gives a safe
structure for a future review.
