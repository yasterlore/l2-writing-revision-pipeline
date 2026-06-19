# Security Checklist

Use this checklist when adding implementation.

- [ ] Uses synthetic data only.
- [ ] Does not read or write real participant data.
- [ ] Treats JSONL input as untrusted.
- [ ] Rejects malformed and oversized input where applicable.
- [ ] For raw event JSONL, validates one JSON object per line.
- [ ] For raw event JSONL, rejects no-oracle forbidden fields such as `final_text`, `observed_after_text`, and `gold_label`.
- [ ] For raw event JSONL, checks basic `seq`, timestamp, cursor, and selection invariants before replay.
- [ ] Runs no-oracle audit before candidate generation, ranking, OT scoring, or learner-state estimation.
- [ ] Ensures `local_context_after_observed` is not used as candidate-generation or ranking input.
- [ ] Uses `NoOracleSafeEpisodeView` or an equivalent narrowed view before candidate generation, ranking, or OT scoring.
- [ ] Excludes observed edit text from safe views when the prediction target is the edit text itself.
- [ ] Adds tests for invalid and adversarial input where applicable.
- [ ] Does not hard-code secrets or personal data.
- [ ] Does not introduce network access unless explicitly required.
- [ ] Explains any new dependency.
- [ ] CI passes formatting, tests, clippy, synthetic-only policy checks, and CLI smoke tests.
- [ ] CI checks no-oracle forbidden fields in public examples and valid synthetic fixtures.
- [ ] CI does not inspect or process real/private participant data.
- [ ] Avoids unsafe Rust, or justifies it explicitly.
- [ ] Avoids `innerHTML`, `eval`, and unsafe dynamic code in TypeScript.
- [ ] Avoids `eval`, `exec`, unsafe deserialization, and unsafe pickle loading in Python.
- [ ] Runs formatting, linting, tests, and audits where available.
