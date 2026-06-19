# Security Policy

## Scope

This project handles keystroke-level writing process data. Treat every JSONL input as untrusted, even when the file is synthetic.

## Data Restrictions

- Use synthetic data only for development and testing.
- Do not commit real participant data.
- Do not ask Codex to read, inspect, transform, summarize, or write real participant data.
- Keep real-data testing outside this repository unless a private local or institution-approved environment has been established.

## Implementation Restrictions

- Do not hard-code secrets, API keys, passwords, tokens, or personal data.
- Do not introduce network access unless it is explicitly required and documented.
- Do not add dependencies unless necessary. Record the reason in the relevant component README.
- Avoid unsafe Rust unless explicitly justified in code comments and documentation.
- Avoid unsafe DOM APIs in TypeScript, including `innerHTML`, `eval`, and unsafe dynamic code execution.
- Avoid `eval`, `exec`, unsafe deserialization, and unsafe pickle loading in Python.

## Testing Expectations

When implementation begins, add tests for malformed, adversarial, and invalid inputs wherever applicable.

After each implementation step, run available formatting, linting, tests, and dependency or security audits.

## Reporting

Until a formal disclosure process exists, document suspected security issues privately and do not include sensitive details in public issues or commits.
