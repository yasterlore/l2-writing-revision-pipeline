# Learner-State Frozen Selective Prediction Policy Fixtures

These fixtures are synthetic-only examples for future frozen selective
prediction policy artifact validation.

Each case contains a synthetic `frozen_selective_prediction_policy.json` and a
safe `expected_frozen_policy_validation_result.json`. The frozen policy is a
metadata artifact for validation-only temperature and threshold provenance.

Valid fixtures show the safe shape expected from a future scaffold. Invalid
fixtures intentionally target one fail-closed reason each, such as test-derived
tuning, raw-row leakage, logits dumps, unsafe paths, malformed schema, or
performance claims.

Expected validation results contain safe metadata only. They do not include
raw rows, logits dumps, label bodies, frozen policy bodies, raw learner text,
private paths, or model-performance evidence.
