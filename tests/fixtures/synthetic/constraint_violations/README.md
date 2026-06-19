# Synthetic ConstraintViolationSet Fixtures

These fixtures are synthetic `ConstraintViolationSet` JSONL examples for weighted OT scorer prototype tests.

They are not participant data, experiment data, or production data. Do not place real participant constraint outputs in this directory.

`valid/` contains no-oracle-safe examples. `invalid/` contains intentionally unsafe examples for rejection tests.

The current valid fixture uses `ot_constraint_schema_v0_2`, which adds
structural descriptive constraints derived from `CandidateFeatureSet` metadata.
These records are for interpretation only. They have `violation_count=0` and do
not add to weighted scores.
