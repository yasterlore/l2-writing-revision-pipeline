# Learner-State Frozen Policy Generation Fixtures

This fixture root contains synthetic-only metadata fixtures for future frozen
policy generation scaffold work.

The fixtures are not generator outputs and do not include generated frozen
policy artifact bodies. They describe future generation requests, safe pointers
to selective prediction fixtures, expected generation results, and expected
frozen policy validation status.

Valid cases describe validation-only temperature and threshold metadata that a
future generator should be able to convert into a safe frozen policy artifact.
Invalid cases intentionally describe unsafe generation attempts so a future
generator can fail closed.

Input pointers are used instead of copying prediction, label, split, or
calibration policy bodies. Expected results are safe metadata only. These
fixtures do not contain raw learner text, real participant data, raw rows,
logits dumps, generated feature/label/manifest bodies, or performance
evidence.
