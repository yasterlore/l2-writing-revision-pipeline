# Candidate Generation Explained

## 1. Beginner summary

This component reads safe episode views and creates a small list of possible edit actions for each episode.

The candidates are placeholders. They say what kind of action might be considered later, not which answer is correct.

## 2. What this component does

It loads `NoOracleSafeEpisodeView` JSONL, checks that forbidden no-oracle fields are absent, and writes `CandidateSet` JSONL.

Each episode always receives a `hold` candidate. Revision-like episodes may also receive local edit and grammar-placeholder candidates.

## 3. What this component does not do

It does not score candidates, rank candidates, evaluate correctness, estimate learner state, or use final corrected text.

It does not validate raw browser events. Rust remains the authoritative validation and transformation layer.

## 4. Input and output

Input: one safe episode view per JSONL line.

Output: one candidate set per JSONL line.

The output is intended for later Python OT scorer experiments, but those experiments are not implemented yet.

## 5. Step-by-step mechanism

1. Read a JSONL file line by line.
2. Parse each line as a JSON object.
3. Reject forbidden field names such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and `local_context_after_observed`.
4. Confirm the object is marked `no_oracle_safe_view=true`.
5. Generate deterministic placeholder candidates.
6. Write one candidate set per episode.

## 6. Important data structures

`Candidate` describes one possible action, including `action_type`, `proposed_edit`, `generation_rule`, and no-oracle flags.

`CandidateSet` groups all candidates for one episode.

`ACTION_TYPES` defines the initial candidate taxonomy.

## 7. Theory behind the implementation

Candidate generation is separated from ranking. This keeps the first stage broad and transparent.

The prototype uses only information available before or at the observed edit boundary. It avoids future text, teacher corrections, and gold labels.

## 8. Mathematical formulas, if any

No mathematical formulas are used in this version.

## 9. Meaning of each variable in the formula

There are no formulas or formula variables in this version.

## 10. Weighting rationale, if weights are used

No weights are used. The generator does not rank candidates.

## 11. Ranking rationale, if ranking is used

No ranking is used. Ranking belongs to a later OT scorer or ranking step.

## 12. Why this design was selected over alternatives

A deterministic placeholder generator is easier to audit than an early grammar-correction model.

It gives later experiments a stable input format without pretending to know the correct correction.

## 13. Security and privacy considerations

Use synthetic data only in this repository.

The loader rejects forbidden no-oracle field names recursively. It does not use `pickle`, `eval`, or `exec`, and it does not perform network access.

Generated candidate outputs may still contain metadata derived from writing-process data. Real-data-derived outputs must not be committed.

## 14. Tests added

Tests cover JSONL loading, forbidden field rejection, `local_context_after_observed` rejection, candidate-set generation, required no-oracle flags, default ignoring of observed edit text, CLI output writing, and a source scan for `eval`, `exec`, and `pickle`.

## 15. Known limitations

The candidates are placeholders and may be broad. The generator does not inspect grammar deeply and does not know which candidate is best.

Observed edit text is ignored by default even when present. Task-specific leakage audits are still needed before using candidate outputs for modeling.

## 16. What to read next

Read `docs/08_candidate_generation_spec.md`, `docs/03_no_oracle_policy.md`, and `crates/kslog_cli/README.md`.
