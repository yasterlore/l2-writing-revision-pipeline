# Security Checklist

Use this checklist when adding implementation.

- [ ] Uses synthetic data only.
- [ ] Does not read or write real participant data.
- [ ] Treats JSONL input as untrusted.
- [ ] Rejects malformed and oversized input where applicable.
- [ ] Adds tests for invalid and adversarial input where applicable.
- [ ] Does not hard-code secrets or personal data.
- [ ] Does not introduce network access unless explicitly required.
- [ ] Explains any new dependency.
- [ ] Avoids unsafe Rust, or justifies it explicitly.
- [ ] Avoids `innerHTML`, `eval`, and unsafe dynamic code in TypeScript.
- [ ] Avoids `eval`, `exec`, unsafe deserialization, and unsafe pickle loading in Python.
- [ ] Runs formatting, linting, tests, and audits where available.
