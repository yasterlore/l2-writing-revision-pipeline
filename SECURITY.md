# Security Policy

## Scope

This project studies keystroke-level L2 writing revision processes. Treat every
input as untrusted, including synthetic fixtures.

The public repository is currently for synthetic-only, metadata-only where
applicable, no-oracle development and validation. It is not approved for real
participant data processing, production deployment, or public dataset release.

## Data Restrictions

- Use synthetic data only for development, fixtures, tests, examples, and
  public CI.
- Do not commit real participant data.
- Do not ask Codex or other tools to read, inspect, transform, summarize, or
  write real participant data in this repository.
- Do not paste raw learner text, raw JSONL rows, fixture JSON bodies, request
  bodies, pointer bodies, expected-result bodies, written file JSON bodies,
  manifest bodies, artifact body payloads, generated policy bodies, summary
  CSV bodies, diagnostic summary bodies, config bodies, candidate score rows,
  logits/probability dumps, or performance metric bodies into public docs.
- Do not publish private paths, absolute local paths, absolute temp paths,
  screenshots containing raw logs, copied GitHub log blocks, or full job
  output.
- Keep `manual_outputs/`, `tmp/`, `private_notes/`, `local_notes/`,
  `private_data/`, `real_data/`, and `participant_data/` out of Git.

Before any private real-data trial, review
`docs/private_real_data_readiness_checklist.md`. Real-data work requires a
separate ethics, consent, institutional, and private security review.

## No-Oracle Restrictions

Candidate generation, scoring, ranking, runtime validation, and learner-state
work must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction after writing
- post-hoc annotation
- answer key
- future edits or future context
- `local_context_after_observed`

Synthetic expected actions are evaluation-time fixtures only. They must not be
passed into candidate generation, feature extraction, constraints, config
tuning, scoring, ranking, or runtime validation.

Weight config support must remain explicit-only. Do not auto-discover config
files, load configs from environment variables, or use hidden default configs.

## Public Output Policy

Public output should be body-free and summary-only. Where artifact writer,
artifact body, manifest writer, fixture validators, or runtime file-writing
paths are involved, public output should include only safe labels, counts,
status flags, reason codes, schema names, and safety flags.

Public output must not include:

- raw rows
- raw learner text
- logits or probabilities
- private paths or absolute local paths
- generated policy bodies
- artifact body payloads
- manifest bodies
- request, pointer, fixture, or expected-result bodies
- written file JSON bodies
- performance metric bodies
- real participant data

## Safe Path Policy

File-writing paths must be treated as untrusted input.

Safe file-writing behavior uses controlled output roots, safe relative paths,
body-free stdout/stderr, parse/scan/finalize checks, cleanup, and residue
checks. Public output must not expose absolute resolved paths.

Path handling must reject or fail closed for:

- absolute paths
- parent traversal
- user home paths
- cloud/private marker paths
- hidden private directories
- unsafe filenames
- non-JSON output where JSON is required
- too-long paths
- symlink-sensitive outputs
- output outside the controlled root

Manifest writer runtime file writing is opt-in only through the implemented
metadata-only runtime path. It writes under the controlled manifest output root,
emits body-free summaries, parses and scans written JSON, finalizes safely,
and cleans up target-owned smoke output in smoke checks.

## Implementation Restrictions

- Do not hard-code secrets, API keys, passwords, tokens, or personal data.
- Do not introduce network access unless explicitly required and documented.
- Do not add dependencies unless necessary. Record the reason in the relevant
  component documentation.
- Avoid unsafe Rust unless explicitly justified in code comments and
  documentation.
- Avoid unsafe DOM APIs in TypeScript, including `innerHTML`, `eval`, and
  unsafe dynamic code execution.
- Avoid `eval`, `exec`, unsafe deserialization, and unsafe pickle loading in
  Python.
- Do not connect artifact writer CLI integration, artifact body generation CLI
  integration, production deployment, or real-data workflows without a separate
  design and review step.

## Testing Expectations

Add tests for malformed, adversarial, invalid, leakage, and path-safety inputs
where applicable.

Current baseline checks include:

```bash
make check-release-quality
make check-python
make check-rust
make check-logger
make check-fixtures
make check-policy
```

Summary-flow checks should be run sequentially:

```bash
make check-summary-flow
```

Do not run summary-flow, release-quality, policy, or exporter smoke checks in
parallel when they may share generated output directories.

## Release-Quality and Logs

Release-quality output and status markers must stay public-safe:

- no raw GitHub Actions logs in docs
- no full job output in docs
- no copied log blocks in docs
- no screenshots containing raw logs
- no fixture, request, pointer, expected, written file, manifest, artifact
  body, or generated policy bodies
- no private paths, absolute local paths, raw learner text, real participant
  data, or performance evidence

Remote/manual status markers are pass-only or count-only metadata summaries.
They are not production-readiness, real-data-readiness, or model-performance
evidence.

## Reporting

Until a formal disclosure process exists, document suspected security issues,
data leakage, or accidental sensitive-data exposure privately. Do not include
sensitive details in public issues, public docs, commits, screenshots, or logs.
