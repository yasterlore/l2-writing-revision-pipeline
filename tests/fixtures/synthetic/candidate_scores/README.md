# Synthetic CandidateScoreSet Fixtures

These fixtures are synthetic `CandidateScoreSet` JSONL examples for evaluation schema tests.

Valid candidate scores include explicit `action_type`; evaluators must not infer action type from `candidate_id`.

They are not participant data, experiment data, production data, or real scoring output. Do not place real participant score outputs in this directory.

`valid/` contains synthetic examples. `invalid/` contains intentionally unsafe examples for rejection tests.
