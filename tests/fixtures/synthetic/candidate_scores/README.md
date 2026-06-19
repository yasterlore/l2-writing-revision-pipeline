# Synthetic CandidateScoreSet Fixtures

These fixtures are synthetic `CandidateScoreSet` JSONL examples for evaluation
schema tests and no-config scoring fixture lock checks.

Valid candidate scores include explicit `action_type`; evaluators must not infer action type from `candidate_id`.

They are not participant data, experiment data, production data, or real
scoring output. Do not place real participant score outputs in this directory.

The initial no-config scoring lock fixtures are:

- `valid/deletion_candidate_scores.jsonl`
- `valid/selection_edit_candidate_scores.jsonl`
- `valid/cursor_movement_candidate_scores.jsonl`

They should match the synthetic E2E outputs generated under
`tmp/synthetic_e2e/<case_name>/candidate_scores.jsonl` when no scorer config is
supplied. Do not paste their JSONL bodies into docs or stdout.

`valid/` contains synthetic examples. `invalid/` contains intentionally unsafe examples for rejection tests.
