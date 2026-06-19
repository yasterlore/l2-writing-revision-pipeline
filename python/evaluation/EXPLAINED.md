# Synthetic Evaluation Explained

## 1. Beginner summary

This component checks prototype candidate scores against synthetic expected actions.

It is like a small wiring test for evaluation data structures. It is not a real study result.

## 2. What this component does

It reads `CandidateScoreSet` JSONL and synthetic expected action JSONL, matches them by `episode_id`, and writes an `EvaluationReport`.

It records exact match, whether the expected action appears among candidates, and whether the expected action is blocked.

## 3. What this component does not do

It does not evaluate real participant data, calculate F1, calculate calibration, perform selective prediction, estimate learner state, or use teacher corrections.

## 4. Input and output

Input:

- `CandidateScoreSet` JSONL
- synthetic expected action JSONL

Output:

- `EvaluationReport` JSON

## 5. Step-by-step mechanism

1. Load candidate score sets.
2. Load synthetic expected actions.
3. Reject forbidden fields.
4. Match score sets and expected actions by `episode_id`.
5. Select top-1 from unblocked candidates.
6. Compare top-1 action type with the synthetic expected action type.
7. Write summary and per-episode results.

## 6. Important data structures

`ExpectedAction` describes one synthetic expected action.

`EpisodeEvaluation` describes one episode-level comparison.

`EvaluationReport` groups summary counts, rates, and per-episode records.

## 7. Theory behind the implementation

Evaluation belongs after scoring. Expected actions must never change candidate generation or ranking.

This keeps a clean boundary between prediction-time information and evaluation-time information.

## 8. Mathematical formulas, if any

```text
exact_match_rate = exact_match_count / episodes_evaluated
```

If `episodes_evaluated = 0`, `exact_match_rate = 0.0`.

## 9. Weighting/ranking rationale, if any

This module does not assign weights or change ranks.

It reads ranks produced by the scorer and compares the unblocked rank-1 action with the synthetic expected action.

Blocked candidates are not allowed to count as exact matches.

## 10. Why this design was selected over alternatives

Using synthetic expected actions gives the repository a way to test evaluation mechanics without real gold labels or participant data.

The design avoids names like F1 or accuracy because this is not yet a research-performance evaluation.

## 11. Security and privacy considerations

Use synthetic data only in this repository.

The loader rejects forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, and `teacher_correction`.

The module does not use `pickle`, `eval`, `exec`, unsafe deserialization, or network access.

## 12. Tests added

Tests cover loading score sets, loading expected actions, exact-match calculation, expected-rank detection, missing expected actions, blocked expected candidates, ranking immutability, forbidden field rejection, absence of F1/accuracy/calibration fields, and source scanning for `eval`, `exec`, and `pickle`.

## 13. Known limitations

Candidate action type is currently derived from the synthetic prototype `candidate_id` convention when no explicit `action_type` field is present in score output.

This is acceptable for the prototype but should become an explicit score-schema field before serious evaluation work.

## 14. What to read next

Read `docs/evaluation_spec.md`, `docs/09_ot_scoring_spec.md`, and `docs/03_no_oracle_policy.md`.
