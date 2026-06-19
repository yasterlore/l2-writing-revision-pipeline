# No-Oracle Policy

No-oracle components must operate only on information that would be available at the relevant moment in the writing process.

## Forbidden Inputs

Candidate generation, ranking, OT scoring, and learner-state estimation must not use:

- final corrected text
- observed future edits
- gold labels
- post-hoc annotations
- `observed_after_text`
- `final_text`
- teacher corrections
- human corrections after writing

## Required Design Pattern

Any no-oracle component must document:

- the exact input fields it consumes
- the timestamp or process boundary for those inputs
- fields explicitly excluded for no-oracle safety
- tests or audits used to catch leakage

## Audit Layer

The Rust `kslog_no_oracle_audit` crate will eventually provide deterministic checks for no-oracle field use and dataset splits.
