# Learner-State Sequence Audit Fixtures

These fixtures are synthetic-only inputs for a future learner-state sequence
no-oracle audit.

They are intentionally small and reviewable. Valid fixtures should pass the
future audit. Invalid fixtures each target one primary failure boundary and
should fail with the reason code recorded in `expected_audit_result.json`.

Do not add real participant data, private paths, generated `tmp/` output, or
manual-run output content here. Public documentation should describe these
fixtures by case name and reason code only, not by copying row bodies.
