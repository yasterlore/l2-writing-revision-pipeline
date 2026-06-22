# Learner-State Sequence Exporter Fixtures

This fixture root contains small synthetic-only inputs for a future
learner-state sequence exporter.

These are exporter input fixtures, not audit fixtures. The exporter will later
read these upstream inputs and generate feature, label, and manifest outputs
that can be checked by the learner-state sequence audit.

Fixture policy:

- synthetic-only
- no raw learner text
- no real participant data
- no private paths
- no fixture body copied into docs
- no performance evidence

The initial fixture is `valid/minimal_single_participant/`.
