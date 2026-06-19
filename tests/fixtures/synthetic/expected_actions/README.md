# Synthetic Expected Action Fixtures

These fixtures are synthetic expected actions for evaluation schema tests.

They are not real gold labels, teacher corrections, participant data, or production evaluation data.

`registry.json` maps synthetic case names to expected action fixture paths.
`active` entries can be used for optional synthetic evaluation. `pending`
entries are known synthetic cases whose expected action fixtures have not been
defined yet and must be skipped for evaluation.

`valid/` contains synthetic examples. `invalid/` contains intentionally unsafe examples for rejection tests.
