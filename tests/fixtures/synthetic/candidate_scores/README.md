# Synthetic CandidateScoreSet Fixtures

These fixtures are synthetic `CandidateScoreSet` JSONL examples for evaluation
schema tests and no-config scoring fixture lock checks.

Valid candidate scores include explicit `action_type`; evaluators must not infer action type from `candidate_id`.

They are not participant data, experiment data, production data, or real
scoring output. Do not place real participant score outputs in this directory.

`valid/deletion_candidate_scores.jsonl` is also the initial no-config scoring
lock fixture. It should match the synthetic E2E output generated at
`tmp/synthetic_e2e/deletion_case/candidate_scores.jsonl` when no scorer config
is supplied. Do not paste its JSONL body into docs or stdout.

`valid/` contains synthetic examples. `invalid/` contains intentionally unsafe examples for rejection tests.
