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

Current fixture families:

- `valid/minimal_single_participant/`: minimal valid synthetic input fixture.
- `valid/past_window_boundary_reset/`: valid edge fixture for future
  past-only window reset tests across task boundaries.
- `invalid/`: synthetic edge fixtures for future fail-closed exporter tests.

Invalid fixtures are intentionally unsafe or incomplete in one narrow way.
They are not performance evidence, and their expected failures should be
reported with safe reason codes rather than row bodies.
