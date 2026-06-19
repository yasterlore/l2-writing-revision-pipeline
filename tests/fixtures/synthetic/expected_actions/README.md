# Synthetic Expected Action Fixtures

These fixtures are synthetic expected actions for evaluation schema tests.

They are not real gold labels, teacher corrections, participant data, or production evaluation data.

`registry.json` maps synthetic case names to expected action fixture paths.
`active` entries can be used for optional synthetic evaluation. `pending`
entries are known synthetic cases whose expected action fixtures have not been
defined yet and must be skipped for evaluation.

Current active synthetic fixtures:

- `deletion_case`: keeps the original conservative `hold` expectation for the first deletion smoke check.
- `selection_edit_case`: uses `local_replace_placeholder` for the central range-edit episode, because the synthetic case is intended to exercise range replacement behavior without claiming a real correction label.
- `cursor_movement_case`: uses `local_insert_placeholder` for the non-terminal cursor-edit episode, because the synthetic case is intended to exercise cursor-local insertion behavior.

`valid/` contains synthetic examples. `invalid/` contains intentionally unsafe examples for rejection tests.
