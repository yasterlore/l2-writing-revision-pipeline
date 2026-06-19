# Synthetic CandidateFeatureSet Fixtures

These fixtures are synthetic `CandidateFeatureSet` JSONL examples for OT constraint-schema tests.

They are not participant data, experiment data, or production data. Do not place real participant feature outputs in this directory.

`valid/` contains no-oracle-safe examples. `invalid/` contains intentionally unsafe examples for rejection tests.

The current valid fixture uses `candidate_feature_schema_v0_2`, which adds
structural metadata fields such as `candidate_metadata_complete`,
`is_safety_relevant_candidate`, and `candidate_family_bucket`. These fields are
synthetic, no-oracle-safe metadata and do not contain candidate descriptions,
proposed edit payloads, local context text, or observed edit text.
