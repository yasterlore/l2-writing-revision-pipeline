# Private Real-Data Readiness Checklist

This document defines the minimum readiness checks before any real participant data is handled outside this repository.

It does not authorize real-data use in this repository. It is a planning checklist for a future private, local, or institution-approved environment.

## 1. Premise

This repository is public research software.

Current repository policy:

- use synthetic data only
- never commit real participant data
- never place real data in examples or fixtures
- never paste real text fragments into docs
- never ask Codex to read, inspect, summarize, transform, or write real participant data

Any real-data trial must happen only in a private local or institution-approved environment, after ethics, consent, storage, access-control, and deletion policies are in place.

## 2. Required Conditions Before Real Data

Do not begin any real-data trial unless all items below are satisfied.

Pipeline readiness:

- synthetic E2E pipeline passes
- synthetic summary collector passes
- GitHub Actions CI passes
- logger-web manual synthetic E2E cases pass
- Rust validation passes on synthetic fixtures
- Rust replay passes on synthetic fixtures
- no-oracle audit passes on synthetic fixtures
- safe-view export works
- Python candidate generation / features / constraints / scoring pass on synthetic outputs
- synthetic evaluation wiring is understood as a connection check, not performance evidence

Repository hygiene:

- `private_data/`, `real_data/`, `participant_data/`, `manual_outputs/`, and `tmp/` are Git-ignored
- `*.real.jsonl` and `*.private.jsonl` are Git-ignored
- `git status` is clean or contains only intentional code/docs changes
- `git check-ignore` confirms private output paths are ignored
- no real data appears in `examples/`
- no real data appears in `tests/fixtures/`
- no real data appears in docs

Research governance:

- participant consent exists
- ethics review or institutional approval exists, if required
- data minimization plan exists
- participant anonymization or pseudonymization plan exists
- participant ID mapping is stored outside this repository
- raw data storage policy exists
- access-control policy exists
- deletion request process exists
- retention policy exists
- private backup policy exists, if backups are allowed

## 3. Prohibited Actions

Never do the following:

- commit real raw event JSONL
- commit real safe-view exports
- commit real candidate sets, feature sets, constraint sets, score sets, or evaluation reports
- put participant data in `examples/`
- put participant data in `tests/fixtures/`
- paste real text fragments into docs
- paste real JSONL rows into docs
- paste real evaluation report bodies into docs
- run real data in public CI
- mix real gold labels into the synthetic expected action registry
- ask Codex to inspect real participant data
- use real participant data to tune scoring inside this public repository

## 4. Private Data Directory Policy

The following paths and file patterns are reserved for private or real data and must remain outside Git:

```text
private_data/
real_data/
participant_data/
manual_outputs/
tmp/
*.real.jsonl
*.private.jsonl
```

Before any private trial, verify ignore behavior with placeholder paths:

```bash
git check-ignore private_data/<placeholder>.jsonl
git check-ignore real_data/<placeholder>.jsonl
git check-ignore participant_data/<placeholder>.jsonl
git check-ignore private_data/<placeholder>.real.jsonl
git check-ignore private_data/<placeholder>.private.jsonl
```

Do not replace these placeholders with real file names in public documentation.

## 5. No-Oracle and Leakage Checklist

For prediction-time stages, do not allow:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- answer key
- future edit
- future context
- `local_context_after_observed`

Observed edit text:

- may appear in restricted internal observation records
- may be unsafe depending on task definition
- must not be used by default in candidate generation or scoring
- must be audited before any modeling use

Expected actions or labels:

- may be used only after scoring for evaluation
- must not flow into candidate generation
- must not flow into feature extraction
- must not flow into constraints
- must not flow into scoring
- must not change ranks

Safe-view rule:

- candidate generation should use `NoOracleSafeEpisodeView`
- `local_context_after_observed` must not appear in safe candidate input
- real safe-view exports can still contain text fragments and must not be committed

## 6. Minimal First Real-Data Trial

The first real-data trial must be deliberately small.

Recommended minimum:

- one self-pilot session
- one task
- private machine only
- private storage only
- no public CI
- no cloud upload unless institution-approved
- no public documentation of text fragments
- no repository commits of outputs

Private output policy:

- write outputs only to a Git-ignored private directory
- do not copy outputs into `examples/`
- do not copy outputs into `tests/fixtures/`
- do not paste output contents into docs
- do not ask Codex to read private output contents

Even summary-only real outputs should not be committed by default. Decide any public reporting policy through institutional guidance first.

## 7. Placeholder Command Examples

These examples use placeholders only. Do not paste real paths or real participant identifiers into public docs.

Check Git state:

```bash
git status
```

Check ignored private paths:

```bash
git check-ignore private_data/<placeholder_session>.real.jsonl
git check-ignore private_data/<placeholder_output>.private.jsonl
```

Run synthetic policy checks before switching environments:

```bash
scripts/check_synthetic_policy.sh
```

Run Rust safe-view export in a private environment only:

```bash
cargo run -q -p kslog_cli -- export-safe-view \
  private_data/<placeholder_raw_events>.real.jsonl \
  private_data/<placeholder_safe_views>.private.jsonl
```

Run no-oracle audit in a private environment only:

```bash
cargo run -q -p kslog_cli -- audit-no-oracle \
  private_data/<placeholder_raw_events>.real.jsonl
```

Do not run these real-data commands in public CI.

## 8. Ethics, Consent, and Governance

Follow the guidance of the relevant research institution, ethics board, instructor, or data steward.

Required governance topics:

- informed consent
- data minimization
- participant anonymization or pseudonymization
- participant ID mapping outside this repository
- access control
- deletion request process
- retention period
- secure storage
- secure transfer, if transfer is allowed
- incident response plan

If any governance requirement is unclear, stop and ask the responsible institution or supervisor before continuing.

## 9. Still Not Allowed

Do not proceed to:

- production evaluation
- F1 claims
- accuracy claims
- calibration
- selective prediction
- learner-state estimation
- public data release
- real gold label workflow
- model-performance claims

These require separate design, approval, leakage review, and privacy review.

## 10. Go / No-Go Checklist

### Go Conditions

All of these must be true:

- synthetic E2E pipeline passes
- synthetic summary collector passes
- CI passes
- logger-web synthetic manual E2E passes
- private data path is Git-ignored
- private output path is Git-ignored
- no real data is in the repository
- no real data is in docs
- no real data is in fixtures
- ethics and consent requirements are satisfied
- storage and retention policies are documented
- participant ID mapping is outside the repository
- Codex will not read real data

### No-Go Conditions

Stop if any of these are true:

- `git status` shows real data files
- `git check-ignore` does not ignore the intended private path
- consent or ethics approval is missing or unclear
- participant ID mapping would enter the repository
- real text would be pasted into docs
- real output would be committed
- public CI would process real data
- no-oracle boundary is unclear
- expected labels could leak into scoring
- Codex would need to read real participant content

### Stop Conditions During a Trial

Stop immediately if:

- a real file appears as untracked in Git
- output contains unexpectedly identifying text
- no-oracle forbidden fields enter prediction-time input
- private storage path is misconfigured
- a participant requests deletion and the deletion process is unclear
- any reviewer, supervisor, or data steward raises a concern

When in doubt, stop the trial and return to synthetic fixtures.

## 11. What To Read Next

Read:

- `docs/12_synthetic_data_policy.md`
- `docs/03_no_oracle_policy.md`
- `docs/security_checklist.md`
- `docs/synthetic_e2e_pipeline.md`
- `docs/milestone_01_pipeline_recap.md`
- `docs/milestone_02_synthetic_evaluation_recap.md`
