# Candidate Generation Spec

This file defines the documentation home for no-oracle candidate generation.

No candidate generation logic is implemented yet.

## Planned Responsibility

Candidate generators will propose possible revision candidates from information available at the current process point.

## No-Oracle Requirement

Candidate generation must not use final corrected text, future edits, gold labels, post-hoc annotations, `observed_after_text`, `final_text`, teacher corrections, or human corrections after writing.

## Planned Location

Python prototypes live under `python/candidate_generation/`. Production deterministic audits belong in Rust.
