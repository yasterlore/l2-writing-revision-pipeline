# OT Scoring Spec

This file defines the documentation home for OT-inspired ranking and scoring experiments.

No scoring logic is implemented yet.

## Planned Responsibility

OT-inspired scorers will rank candidates using explicit constraints and documented weights.

## Required Documentation

Any scorer must document:

- constraints
- formulas
- variable meanings
- weighting rationale
- ranking rationale
- no-oracle input boundary
- leakage tests

## No-Oracle Requirement

Scoring and ranking must not use final corrected text, future edits, gold labels, post-hoc annotations, `observed_after_text`, `final_text`, teacher corrections, or human corrections after writing.
