# Security Policy

## Scope

This project handles keystroke-level writing process data. Treat every JSONL input as untrusted, even when the file is synthetic.

## Data Restrictions

- Use synthetic data only for development and testing.
- Do not commit real participant data.
- Do not ask Codex to read, inspect, transform, summarize, or write real participant data.
- Keep real-data testing outside this repository unless a private local or institution-approved environment has been established.
- Do not process real data in public CI.
- Do not paste JSONL rows, participant text, or evaluation report bodies into docs.
- Keep `manual_outputs/`, `tmp/`, `private_data/`, `real_data/`, and `participant_data/` out of Git.

Before any private real-data trial, review `docs/private_real_data_readiness_checklist.md`.

## No-Oracle Restrictions

Candidate generation, scoring, ranking, and learner-state work must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- answer key
- future context
- `local_context_after_observed`

Synthetic expected actions are evaluation-time fixtures only. They must not be passed into candidate generation, feature extraction, constraints, scoring, or ranking.

## Implementation Restrictions

- Do not hard-code secrets, API keys, passwords, tokens, or personal data.
- Do not introduce network access unless it is explicitly required and documented.
- Do not add dependencies unless necessary. Record the reason in the relevant component README.
- Avoid unsafe Rust unless explicitly justified in code comments and documentation.
- Avoid unsafe DOM APIs in TypeScript, including `innerHTML`, `eval`, and unsafe dynamic code execution.
- Avoid `eval`, `exec`, unsafe deserialization, and unsafe pickle loading in Python.

## Testing Expectations

Add tests for malformed, adversarial, and invalid inputs wherever applicable.

After each implementation step, run available formatting, linting, tests, and dependency or security audits.

Current baseline checks:

```bash
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
scripts/check_synthetic_policy.sh
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
```

## Reporting

Until a formal disclosure process exists, document suspected security issues privately and do not include sensitive details in public issues or commits.
