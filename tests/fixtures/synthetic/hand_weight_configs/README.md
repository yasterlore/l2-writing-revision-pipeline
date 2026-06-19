# Synthetic Hand-Weight Config Fixtures

These fixtures exercise the hand-weight config schema and validator.

They are synthetic design fixtures only. They are never auto-loaded by default
scoring. Some valid fixtures may be passed explicitly to `score.py
--weight-config` for smoke checks, but they must not be treated as learned
weights, performance results, or real-data configuration.

Valid fixtures may describe current-default-like behavior or explicit
synthetic smoke-test behavior with a documented rationale. They are still
synthetic-only and must not be treated as learned weights or performance
policies.

Invalid fixtures intentionally contain malformed or unsafe config shapes for
validator tests.
