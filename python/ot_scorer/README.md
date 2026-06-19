# Candidate Feature Schema and Leakage Audit

This module prepares simple no-oracle structural features, constraint violations, and prototype weighted scores for future OT-inspired scoring experiments.

It does not implement evaluation, F1, calibration, selective prediction, or learner-state estimation.

## Purpose

The module defines `CandidateFeature` and `CandidateFeatureSet` as a stable boundary between candidate generation and future scoring.

It also performs a lightweight leakage audit before features are written.

## Input

Input is JSONL with one `CandidateSet` per line, produced by `python/candidate_generation/`.

The loader rejects forbidden no-oracle fields such as:

- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- `inserted_text_observed`
- `deleted_text_observed`

## Output

Output is JSONL with one `CandidateFeatureSet` per episode.

Each candidate feature contains:

- `candidate_id`
- `episode_id`
- `action_type`
- `generation_rule`
- `no_oracle_safe`
- `uses_observed_edit_text`
- `action_family`
- `candidate_metadata_complete`
- `has_generation_rule`
- `has_action_family`
- `is_safety_relevant_candidate`
- `is_placeholder_candidate`
- `is_grammar_family_candidate`
- `is_local_edit_family_candidate`
- `is_hold_candidate`
- `candidate_family_bucket`
- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`
- `is_placeholder`
- `is_hold`
- `is_local_edit`
- `is_grammar_placeholder`
- `candidate_description_length`
- `feature_notes_count`
- `leakage_flags`

The structural fields are derived from candidate metadata, safety flags, and
no-oracle-safe pre-edit metadata. `candidate_feature_schema_v0_3` adds local
pattern features as coarse booleans and buckets. These fields are intended for
later constraint refinement and debugging, not for performance claims.

The feature output does not include candidate descriptions, proposed edit
payloads, raw `local_context_before` text, post-edit context, or observed edit
text.

## Running

From the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.features \
  --input tests/fixtures/synthetic/candidate_sets/valid/deletion_candidate_set.jsonl \
  --output tmp/candidate_features.jsonl
```

Write generated outputs to `tmp/`, `manual_outputs/`, or another Git-ignored synthetic-output location.

## Leakage Audit

The audit rejects forbidden field names recursively.

It also flags:

- `candidate_set_not_no_oracle_safe`
- `candidate_set_uses_observed_edit_text`
- `candidate_not_no_oracle_safe`
- `candidate_uses_observed_edit_text`

Flagged candidates can still be represented in feature output for synthetic testing, but downstream scoring should treat leakage flags as blocking until a task-specific policy says otherwise.

## No-Oracle Policy

The module does not use:

- post-edit context
- final text
- gold labels
- teacher corrections
- observed edit text
- future edits

It uses only structural properties of the candidate object and pre-edit local
pattern metadata, such as action type, rule name, description length, note
count, cursor-position buckets, selection buckets, and final-character classes.
It does not copy raw local context text into feature output.

## Tests

```bash
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
```

`ruff` and `pytest` are not required in this first version to keep dependencies minimal.

## Constraint Schema

The constraint prototype reads `CandidateFeatureSet` JSONL and writes `ConstraintViolationSet` JSONL.

Run it from the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.constraints \
  --input tests/fixtures/synthetic/candidate_features/valid/deletion_candidate_features.jsonl \
  --output tmp/constraint_violations.jsonl
```

### Constraint Taxonomy

Penalty constraints record violations that future scoring should treat as blocking until a task-specific policy says otherwise:

- `NO-LEAKAGE-FLAG`: violation when candidate `leakage_flags` is not empty.
- `NO-OBSERVED-EDIT-TEXT`: violation when `uses_observed_edit_text=true`.
- `NO-UNSAFE-CANDIDATE`: violation when `no_oracle_safe=false`.

Descriptive constraints record candidate type without adding a penalty in this version:

- `HOLD-CANDIDATE`
- `LOCAL-EDIT-CANDIDATE`
- `GRAMMAR-PLACEHOLDER-CANDIDATE`
- `PLACEHOLDER-CANDIDATE`
- `HAS-GENERATION-RULE`
- `HAS-ACTION-FAMILY`
- `CANDIDATE-METADATA-COMPLETE`
- `HOLD-FAMILY-CANDIDATE`
- `LOCAL-EDIT-FAMILY-CANDIDATE`
- `GRAMMAR-FAMILY-CANDIDATE`
- `PLACEHOLDER-FAMILY-CANDIDATE`
- `SAFETY-RELEVANT-CANDIDATE`
- `CANDIDATE-FAMILY-BUCKET`
- `ARTICLE-PLACEHOLDER-CANDIDATE`
- `NUMBER-PLACEHOLDER-CANDIDATE`
- `SVA-PLACEHOLDER-CANDIDATE`
- `TENSE-PLACEHOLDER-CANDIDATE`
- `PREPOSITION-PLACEHOLDER-CANDIDATE`
- `PUNCTUATION-PLACEHOLDER-CANDIDATE`
- `CONTEXT-BEFORE-EMPTY`
- `CONTEXT-BEFORE-SHORT`
- `CONTEXT-BEFORE-MEDIUM`
- `CONTEXT-BEFORE-LONG`
- `CURSOR-AT-DOCUMENT-START`
- `CURSOR-AT-DOCUMENT-END-BEFORE`
- `SELECTION-COLLAPSED-BEFORE`
- `SELECTION-NONCOLLAPSED-BEFORE`
- `SELECTION-SPAN-SHORT`
- `SELECTION-SPAN-MEDIUM`
- `SELECTION-SPAN-LONG`
- `LEFT-CONTEXT-ENDS-WITH-SPACE`
- `LEFT-CONTEXT-ENDS-WITH-PUNCTUATION`
- `LEFT-CHAR-CLASS-NONE`
- `LEFT-CHAR-CLASS-WHITESPACE`
- `LEFT-CHAR-CLASS-PUNCTUATION`
- `LEFT-CHAR-CLASS-DIGIT`
- `LEFT-CHAR-CLASS-UPPERCASE-LETTER`
- `LEFT-CHAR-CLASS-LOWERCASE-LETTER`
- `LEFT-CHAR-CLASS-OTHER-LETTER`
- `LEFT-CHAR-CLASS-OTHER`
- `ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE`
- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`
- `GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED`

These structural descriptive constraints are derived from
`CandidateFeatureSet` metadata. Their `violation_count` is always `0`, and the
weighted scorer does not add them to `weighted_score`.

The linguistic placeholder constraints record candidate families only. They do
not judge grammatical correctness.

The local pattern diagnostic constraints record `CandidateFeatureSet v0_3`
bucket, boolean, and enum features only. They do not reintroduce raw
`local_context_before` text and do not affect weighted scoring.

The non-leaky linguistic diagnostic constraints combine grammar-placeholder
candidate metadata with v0.3 abstract local pattern features. They do not judge
grammatical correctness and do not affect weighted scoring.

The output includes `violation_count`, `severity`, and `explanation`, but it does not include weights, weighted scores, ranks, candidate text, local context text, or observed edit text.

## Hand-Weight Config Schema Models

`python/ot_scorer/weight_config.py` defines schema models and strict validation
helpers for future hand-designed scoring weight configs.

The models include:

- `HandWeightConfig`
- `ConstraintWeightEntry`
- `NoOracleReviewInfo`
- `ForbiddenInformationPolicy`

The loader validates synthetic config JSON files for schema version, active
weight rationale, no-oracle-safe reason, finite numeric weights, duplicate
constraint IDs, known constraint IDs, forbidden field names, unsafe
manual/private/real path-like strings, synthetic-only notice, and an
expected-action usage policy that forbids scoring and weight tuning.

Validate a config without scoring:

```bash
PYTHONPATH=python python3 -m ot_scorer.validate_weight_config \
  --config tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json
```

The validation CLI prints a safe summary only: validation status, config path,
schema version, config name, and count fields. It does not print the config JSON
body, scoring output, ranking output, exact-match/evaluation output, expected
action details, JSONL content, or raw text.

For repository smoke checks, run:

```bash
scripts/check_hand_weight_config_validation.sh
```

The smoke script expects the valid synthetic config to pass and invalid
synthetic configs to fail. Expected invalid failures are treated as a successful
validation wiring check.

The config schema is connected to scoring only when `score.py --weight-config`
is supplied explicitly. No-config scoring remains the default, default weights
are unchanged, scoring formula is unchanged, and tie-break behavior is
unchanged.

## Diagnostic Summary Tool

The diagnostic summary CLI reads `ConstraintViolationSet` JSONL and writes a
count-only JSON summary.

Run it from the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.summarize_diagnostics \
  --constraints tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl \
  --output tmp/diagnostic_summary/deletion_diagnostic_summary.json
```

The summary includes aggregate counts such as `total_constraint_sets`,
`total_candidates`, `constraint_id_counts`, `local_pattern_constraint_counts`,
`linguistic_placeholder_constraint_counts`, and
`non_leaky_linguistic_constraint_counts`.

It does not include raw JSONL lines, per-episode text detail, candidate
descriptions, proposed edit payloads, local context text, observed edit text,
final text, expected actions, F1, accuracy, calibration, or learner-state
estimates. Empty input produces a valid zero-count summary.

## Synthetic Data Only

All fixtures are synthetic. Do not commit feature outputs derived from real participant data.

## Weighted OT Scorer Prototype

The scorer prototype reads `ConstraintViolationSet` JSONL and writes `CandidateScoreSet` JSONL.

Run it from the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.score \
  --input tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl \
  --output tmp/candidate_scores.jsonl
```

Explicit config scoring is available only through `--weight-config`:

```bash
PYTHONPATH=python python3 -m ot_scorer.score \
  --constraints tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl \
  --output tmp/candidate_scores_with_config.jsonl \
  --weight-config tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json
```

No-config scoring remains the default. `--config` is not an alias, config files
are not discovered implicitly, and environment variables are not used to load
config.

Each candidate score contains:

- `candidate_id`
- `episode_id`
- `action_type`
- `generation_rule`
- `action_family`
- `weighted_score`
- `blocked`
- `block_reasons`
- `rank`
- `constraint_contributions`
- `scoring_policy_version`
- `no_oracle_safe`

`candidate_id` is only an identifier. `action_type` is the explicit candidate
classification copied from the constraint-violation input and is used by the
synthetic evaluation prototype. It is not a gold label, expected answer, or
teacher correction.

`generation_rule` and `action_family` are copied through from candidate
generation and feature extraction for interpretability and debugging. They are
no-oracle-safe metadata in this prototype and do not change the weighted score,
blocking constraints, or deterministic tie-break policy.

### Weighted Score

The prototype uses:

```text
weighted_score(candidate) = sum(weight(constraint_id) * violation_count)
```

Blocking constraints have weight `1_000_000.0` and are treated as safety blockers:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

Descriptive constraints have weight `0.0`:

- `HOLD-CANDIDATE`
- `LOCAL-EDIT-CANDIDATE`
- `GRAMMAR-PLACEHOLDER-CANDIDATE`
- `PLACEHOLDER-CANDIDATE`

These weights are hand-designed safety defaults, not learned values.

### Blocking and Ranking Policy

If a blocking constraint has `violation_count > 0`, the candidate is marked `blocked=true` and placed after unblocked candidates.

Among unblocked candidates with the same score, tie-break is deterministic:

1. hold
2. local edit
3. grammar placeholder
4. other placeholder
5. other

This rank is not a correctness prediction. It is a deterministic prototype order for later experiments.

Candidate score outputs derived from real participant data must not be committed to this repository.

### Explicit Config-Aware Function

`python/ot_scorer/scorer.py` also exposes
`score_constraint_violation_set_with_config(violation_set, config)` for
unit-tested synthetic config experiments. It accepts a validated
`HandWeightConfig` object and uses only active constraint weights from that
object.

This function is connected to `score.py` only through explicit
`--weight-config`. It is not connected to the synthetic E2E pipeline or the
summary collector. The default scorer path still does not load, discover, or
import config at runtime, and default `CandidateScoreSet` output does not
include config fields.

Unit tests cover default snapshot stability, default-like config equivalence,
explicit active weight behavior, inactive weight ignoring, unchanged tie-break
and blocking behavior, output schema stability, and absence of forbidden fields.
The no-config fixture lock remains the regression guard for E2E-derived locked
score fixtures.

### No-Config Scoring Fixture Lock

After generating the synthetic E2E outputs, run:

```bash
scripts/check_no_config_scoring_fixture_lock.sh
```

The default lock checks `deletion_case`, `selection_edit_case`, and
`cursor_movement_case`. It compares the default no-config `CandidateScoreSet`
output against synthetic lock fixtures. It prints safe summary only and does
not print score rows, JSONL bodies, raw text, expected actions, or evaluation
results. It is a regression guard, not a performance evaluation or ranking
correctness claim.

### Explicit Config Ranking Diff Smoke

To smoke-check explicit config wiring without changing default E2E behavior,
run:

```bash
scripts/check_explicit_config_ranking_diff.sh
```

The script generates no-config and explicit-config synthetic score outputs,
checks that the current-default-like config has zero diff, and checks that an
intentional synthetic tiny-weight config produces at least one
`weighted_score_changed` diff. It prints safe summary only and does not print
JSONL bodies, score rows, config bodies, raw text, expected actions, evaluation
results, F1, accuracy, calibration, or learner-state estimates.

This smoke check is not connected to the synthetic E2E pipeline or summary
collector, and it is not a performance evaluation.

For planned refinements and non-goals, read `../../docs/scoring_policy_refinement_plan.md`.
For the future linguistic placeholder constraint boundary, read
`../../docs/linguistic_placeholder_constraint_plan.md`.
For the no-oracle-safe local pattern feature design, read
`../../docs/local_pattern_feature_plan.md`.
For the implemented v0.3 local pattern field schema, read
`../../docs/local_pattern_feature_schema_v0_3_plan.md`.
For descriptive diagnostics derived from those fields, read
`../../docs/local_pattern_diagnostic_constraint_plan.md`.
For future non-leaky linguistic diagnostic design, read
`../../docs/non_leaky_linguistic_constraint_design_plan.md`.
For planned summary-only diagnostic aggregation, read
`../../docs/diagnostic_summary_tooling_plan.md`.
For the boundary between diagnostics and future scoring policy, read
`../../docs/diagnostic_to_scoring_boundary_review.md`.
For future hand-designed weight principles, read
`../../docs/hand_weight_policy_design.md`.
For future score-target constraint family selection, read
`../../docs/score_target_constraint_family_selection_plan.md`.
For future hand-weight config schema design, read
`../../docs/hand_weight_config_schema_plan.md`.
For the default-unchanged boundary before any future scorer config connection,
read `../../docs/default_unchanged_config_support_design.md`.
For the planned no-config scoring fixture lock, read
`../../docs/no_config_scoring_fixture_lock_plan.md`.
For the future explicit-config ranking diff boundary, read
`../../docs/explicit_config_ranking_diff_plan.md`.
For the future config-aware scorer function boundary, read
`../../docs/config_aware_scorer_function_design.md`.
For the future explicit scorer config CLI boundary, read
`../../docs/explicit_config_cli_option_design.md`.
For optional explicit config-enabled E2E design, read
`../../docs/config_enabled_e2e_design.md`.
For future separate config-enabled summary collector design, read
`../../docs/config_enabled_summary_collector_design.md`.
