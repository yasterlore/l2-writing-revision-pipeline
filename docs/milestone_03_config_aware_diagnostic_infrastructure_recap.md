# Milestone 03 Config-Aware Diagnostic Infrastructure Recap

This document summarizes the config-aware diagnostic infrastructure added and
documented across Steps 38-86.

It is a beginner-friendly recap of what now exists, why it exists, and what is
still intentionally out of scope.

This milestone is not performance evaluation, not real-data readiness, not
production evaluation, and not learner-state estimation.

## 1. Milestone 03 Purpose

Milestone 03 organizes the infrastructure needed before any careful future
scoring-policy refinement.

The goals were to:

- improve public repository quality and safety documentation
- clarify the LICENSE placeholder and release metadata status
- expand diagnostic records without changing ranking behavior
- add no-oracle-safe local pattern features
- add count-only diagnostic summary tooling
- design and validate explicit hand-weight config schemas
- add config-aware scoring infrastructure while protecting no-config defaults
- add explicit config-enabled E2E paths without changing default E2E behavior
- keep no-config and config-enabled summary outputs separate
- define observation note templates, storage policy, and public-sharing checks

The milestone keeps a strict boundary: diagnostics and config-enabled smoke
checks are infrastructure and wiring checks. They do not prove model quality.

## 2. Step 38-86 Flow

The broad flow was:

1. Public GitHub quality pass
2. LICENSE placeholder and repository metadata clarification
3. Private real-data readiness and public-release safety planning
4. Scoring policy refinement design
5. Structural candidate features and descriptive constraints
6. Linguistic placeholder diagnostic constraints
7. No-oracle-safe local pattern feature design and CandidateFeatureSet v0.3
8. Local pattern diagnostic descriptive constraints
9. Count-only diagnostic summary tooling
10. Diagnostic distribution smoke checks and observation note templates
11. Non-leaky linguistic diagnostic constraints
12. Diagnostic-to-scoring boundary review
13. Hand-weight policy and score-target family selection design
14. Hand-weight config schema models and validation CLI
15. No-config scoring fixture lock
16. Config-aware scorer function and unit-test hardening
17. Explicit `score.py --weight-config` support
18. Explicit config ranking diff smoke
19. Optional explicit config-enabled E2E path
20. Separate config-enabled summary collector and smoke check
21. Observation note storage workflow and public-sharing checklist

Each step was designed to preserve no-oracle boundaries and avoid performance
claims from synthetic-only diagnostics.

## 3. Current Pipeline Map

The default no-config synthetic path remains:

```text
synthetic RawEvent JSONL
  -> Rust validation/replay/extraction/micro-episode/safe view
  -> Python CandidateSet
  -> Python CandidateFeatureSet
  -> Python ConstraintViolationSet
  -> Python CandidateScoreSet
  -> optional synthetic expected-action evaluation
  -> no-config synthetic summary collector
```

Config-enabled paths are explicit-only:

```text
ConstraintViolationSet
  -> score.py --weight-config <config.json>
  -> CandidateScoreSet
```

and:

```text
run_synthetic_e2e_pipeline.sh ... --weight-config <config.json>
```

The config-enabled summary collector is separate:

```text
run_synthetic_e2e_config_summary.sh --weight-config <config.json>
  -> tmp/synthetic_e2e_config_summary/<safe_config_name>/summary.csv
```

The default no-config summary remains:

```text
tmp/synthetic_e2e_summary/summary.csv
```

These two summary locations are intentionally separate.

## 4. What Works Now

The repository can now:

- run the synthetic no-config E2E pipeline
- run optional synthetic expected-action evaluation for active registry cases
- collect no-config summary-only output
- generate candidate features with structural and local pattern abstractions
- emit descriptive diagnostic constraints
- generate count-only diagnostic summaries
- smoke-check diagnostic distribution columns and counts
- validate hand-weight config fixtures
- reject unsafe or malformed hand-weight configs
- lock no-config scoring fixtures for selected synthetic cases
- run config-aware scorer code through explicit unit tests
- run `score.py --weight-config <config.json>` explicitly
- compare no-config and explicit-config scoring outputs with safe diff counts
- run config-enabled E2E only when `--weight-config` is explicitly supplied
- run config-enabled E2E smoke checks
- generate separate config-enabled summary output
- smoke-check config-enabled summary separation and safe columns
- use count-only observation note templates
- follow storage and public-sharing workflows for observation notes

These are wiring, safety, and regression checks.

## 5. What Still Does Not Exist

Not implemented:

- production evaluation
- real participant data processing
- real gold-label workflow
- real teacher correction workflow
- private validation
- F1
- accuracy claims
- calibration
- selective prediction
- learner-state estimation
- automatic weight learning
- learned OT weights
- publication-level performance claims
- real-data readiness

The repository remains synthetic-only.

## 6. No-Oracle And Privacy Policy

Candidate generation, diagnostics, config-aware scoring, and summary tooling
must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit or future context
- real participant data

`local_context_after_observed` remains unsafe for candidate generation,
constraint generation, scoring, ranking, and learner-state estimation.

Synthetic expected actions are evaluation-time information only. They may be
used after scoring for synthetic checks, but they must not tune configs,
weights, diagnostics, candidates, scoring, or ranking.

Docs and stdout must not include:

- raw JSONL bodies
- raw writing text
- summary CSV bodies
- diagnostic summary bodies
- config JSON bodies
- candidate score rows
- evaluation report bodies
- private/manual/real paths

Observation notes are private/local by default.

## 7. Config-Aware Infrastructure Boundary

The config-aware infrastructure is intentionally explicit and fail-closed.

Current boundaries:

- no-config default scoring remains protected by fixture locks
- `--weight-config` is explicit-only
- there is no `--config` alias
- no implicit config discovery
- no environment-variable config loading
- no hidden default config
- invalid configs fail before scoring
- unsafe config paths fail closed
- config-enabled E2E requires explicit `--weight-config`
- default E2E remains no-config
- default no-config summary remains separate
- config-enabled summary writes to a separate config-specific location
- default output schemas are not changed to include config bodies

Config support is for controlled synthetic smoke checks and future design
experiments, not for automatic tuning or performance claims.

## 8. Diagnostic Infrastructure Boundary

Diagnostic infrastructure is descriptive and count-only.

Diagnostic counts are not:

- accuracy
- F1
- calibration
- ranking quality
- grammatical correctness
- learner-state quality
- real-data readiness
- model performance

Local pattern diagnostics and linguistic diagnostics are descriptive records.
They help future design review, but they are not scoring active by default.

Observation notes are not tuning signals. A note alone must not change:

- scoring weights
- scoring formula
- tie-break policy
- candidate ranking
- config policy
- candidate generation

## 9. Public Repository Readiness

Milestone 03 improved public repository safety posture:

- README and docs emphasize synthetic-only development
- SECURITY and release-readiness materials define data-safety expectations
- public release checklist exists
- private real-data readiness checklist exists
- LICENSE remains a placeholder until a final license is selected
- real data is excluded from the repository
- `tmp/`, manual outputs, private data paths, and local/private note folders are
  ignored
- generated reports and summaries stay out of Git
- observation note templates are blank and count-only
- filled observation notes are private/local by default

This is public-repository hygiene. It is not permission to process real
participant data.

## 10. Beginner Explanation

### What Is Config-Aware Scoring?

Config-aware scoring means the scorer can be called with an explicit weight
configuration file.

In this repository, config-aware scoring is opt-in:

```bash
python3 -m ot_scorer.score --constraints <constraints.jsonl> --output <scores.jsonl> --weight-config <config.json>
```

If no config is supplied, the default scoring path remains unchanged.

### Why Protect The Default Path?

The default path is the baseline synthetic pipeline. If config support changed
the default path accidentally, it would become hard to tell whether a later
ranking difference came from a deliberate config or from an unintended
regression.

Fixture locks protect the no-config path so future experiments do not silently
change existing behavior.

### Diagnostic Summary Versus Performance Evaluation

A diagnostic summary counts what kinds of constraints or diagnostic records
appeared.

It answers questions like:

- did the diagnostic records get emitted?
- are count fields present?
- did a synthetic E2E case produce expected files?

It does not answer:

- is the model accurate?
- is the ranking correct?
- is the grammar correction good?
- is the system ready for real data?

### Why Not Put Observation Notes In The Public Repo?

Filled observation notes are working notes. They may accidentally include
generated output, local paths, private context, or wording that sounds like a
performance claim.

Therefore:

- blank templates may live in docs
- workflow docs may live in docs
- filled notes stay private/local by default
- public sharing requires an additional checklist and repository-owner approval

## 11. Useful Commands

No-config synthetic summary:

```bash
scripts/run_synthetic_e2e_summary.sh
```

Diagnostic distribution smoke:

```bash
scripts/check_synthetic_diagnostic_distribution.sh
```

Hand-weight config validation smoke:

```bash
scripts/check_hand_weight_config_validation.sh
```

No-config scoring fixture lock:

```bash
scripts/check_no_config_scoring_fixture_lock.sh
```

Explicit config ranking diff smoke:

```bash
scripts/check_explicit_config_ranking_diff.sh
```

Config-enabled E2E smoke:

```bash
scripts/check_config_enabled_e2e_smoke.sh
```

Config-enabled summary smoke:

```bash
scripts/check_config_enabled_summary_smoke.sh
```

These commands are synthetic-only checks and should not be interpreted as
performance evaluation.

## 12. Good Next Candidates

Possible next steps:

- milestone 03 release quality check
- config-enabled summary smoke expansion
- synthetic-only hand-weight rationale examples
- score-active family selection revisit
- default-path regression review before any future config expansion
- private validation design later
- continued public repository safety review

Real participant data remains out of the public repository.

## 13. Related Documents

- [Milestone 01 pipeline recap](milestone_01_pipeline_recap.md)
- [Milestone 02 synthetic evaluation recap](milestone_02_synthetic_evaluation_recap.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Diagnostic summary tooling plan](diagnostic_summary_tooling_plan.md)
- [Diagnostic-to-scoring boundary review](diagnostic_to_scoring_boundary_review.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Config-enabled E2E design](config_enabled_e2e_design.md)
- [Config-enabled summary collector design](config_enabled_summary_collector_design.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
- [Filled observation note public-sharing checklist](filled_observation_note_public_sharing_checklist.md)
- [Private real-data readiness checklist](private_real_data_readiness_checklist.md)
- [Public release checklist](public_release_checklist.md)
