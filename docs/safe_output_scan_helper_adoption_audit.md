# Safe Output Scan Helper Adoption Audit

This document audits where the `safe_output_scan` test helper should be used,
where it should not be used, and how future hardening should keep output-safety
checks strict.

This is audit and design documentation. It does not change implementation logic,
test code, shell scripts, scorer weights, scoring formula, deterministic
tie-break behavior, E2E pipeline behavior, or fixtures.

This is not performance evaluation.

## 1. Purpose

The purpose of this audit is to clarify adoption boundaries for the test-only
safe-output scan helper.

The audit should:

- identify stdout/stderr checks that may benefit from path normalization
- reduce false positives caused by environment-dependent absolute paths
- preserve strict detection of raw body leaks
- avoid broad whitelisting of forbidden terms
- keep performance metrics out of scope
- keep expected actions out of scoring feedback

The helper is not a privacy waiver. It is a way to separate path metadata from
content bodies during tests.

## 2. Current Helper State

The helper lives in `python/test_support/safe_output_scan.py`.

It currently provides:

- `normalize_environment_paths_for_scan(...)`
- `assert_no_forbidden_fragments(...)`
- normalization for temporary paths, project-root prefixes, home prefixes, and
  CI workspace prefixes
- whole-token replacement for temporary absolute paths
- project-root prefix replacement that keeps project-controlled basenames
  visible

Current adoption is intentionally narrow.

It is used by stdout/stderr-oriented safe-output assertions in Python tests,
including:

- score CLI failure-output checks
- config ranking diff CLI safe-summary checks
- score fixture lock CLI safe-summary checks
- hand-weight config validation CLI safe-output checks
- evaluation CLI summary checks for forbidden metric labels

It is not applied to generated file bodies as a blanket rule.

## 3. Targets Where The Helper Should Be Used

The helper is appropriate for text that represents command output or test
failure output and may contain environment-dependent paths.

Use it for:

- CLI stdout
- CLI stderr
- test failure message text
- subprocess captured output
- shell command captured output, if later wrapped in Python
- safe summary output that includes absolute output paths
- environment-dependent path-containing diagnostic text
- temporary path-containing failure summaries

The main question should be: "Is this text command output that may include a
machine-generated absolute path?"

If yes, path normalization may be appropriate before forbidden-fragment scans.

## 4. Targets Where The Helper Should Not Be Used

Do not use this helper to hide or normalize content bodies.

Do not apply it to:

- raw JSONL bodies
- summary CSV bodies
- diagnostic summary JSON bodies
- config JSON bodies
- candidate score rows
- committed docs body
- actual fixture contents
- generated report body that must be scanned as content
- expected action fixture bodies
- raw event fixture bodies
- approval record bodies
- observation note bodies

These should remain direct content scans. If forbidden content is present in a
file body, normalization should not make it pass.

## 5. Adoption Audit Checklist

When adding or reviewing a forbidden-term scan, ask:

- Is the scan over stdout or stderr?
- Is the scan over subprocess captured output?
- Can the text include an OS-generated temporary absolute path?
- Can the text include a user home path or CI workspace path?
- Is the scan currently checking broad fragments such as metric labels,
  no-oracle field names, or private path terms?
- Would normalizing paths preserve the actual content being checked?
- Are project-controlled basenames still visible after normalization?
- Is this instead a raw file body scan that should remain strict?
- Is this a committed docs scan that should not be path-normalized?
- Does the test still fail when the forbidden term appears in actual output
  body text?

Review these categories:

- Python tests using broad forbidden-term assertions
- shell scripts grepping captured output
- docs checks
- synthetic policy checks
- public release checks
- config summary checks
- observation note checks
- approval/checklist docs

## 6. Candidate Future Adoption Points

The current codebase already uses the helper in the main Python stdout/stderr
assertions that caused the path false-positive risk.

Future adoption may be considered for:

- Python tests that add new subprocess `stdout` or `stderr` forbidden-fragment
  scans
- Python tests that expand `test_diagnostic_summary.py` from field/body checks
  into stdout/stderr forbidden-term scans
- future Python wrappers around shell smoke scripts that inspect captured output
- future release-quality tests that scan command output containing absolute
  paths
- future approval or observation-note safety tests that inspect safe command
  summaries rather than note bodies

No code changes are made in this audit.

## 7. No-Go Adoption Points

Do not adopt the helper for:

- raw file content scans
- committed docs body scans
- actual config fixture validation
- JSONL leak checks
- candidate score row leak checks
- summary body leak checks
- diagnostic summary body leak checks
- expected action body validation
- raw event fixture validation
- no-oracle forbidden field validation

Using the helper in these places would be dangerous because it could make a
real content leak look like path noise.

## 8. Future Hardening Roadmap

Recommended future steps:

1. Apply the helper to remaining Python stdout/stderr tests if new broad scans
   are added.
2. Consider a shell-wrapper normalization approach only for captured stdout or
   stderr, not for file bodies.
3. Add central documentation for safe-output scan policy if multiple packages
   start using the helper.
4. Keep raw body scans strict.
5. Add regression tests whenever a new broad forbidden-term scan is introduced.
6. Review project-controlled basenames separately instead of treating all paths
   as harmless.

The goal is targeted hardening, not weaker safety.

## 9. Safety Policy

Normalization is not a whitelist.

Normalization is not permission to output:

- raw JSONL bodies
- config bodies
- summary bodies
- diagnostic summary bodies
- candidate score rows
- raw text
- final text
- observed-after text
- gold labels
- expected action details
- real participant identifiers

Absolute paths are environment metadata, not content bodies. Project-controlled
basenames may still matter because they can encode policy-relevant names.

Forbidden-term checks remain active.

## 10. Beginner Explanation

### What Is An Adoption Audit?

An adoption audit is a careful review of where a helper should be used and
where it should not be used.

Here, the helper is useful for command output that may include random temporary
paths.

### Why Not Use The Helper Everywhere?

Because some checks inspect real file content. If a file body contains unsafe
content, the test should fail.

Using path normalization everywhere would risk hiding real leaks.

### Why Not Normalize Raw File Bodies?

Raw file bodies are the actual content being tested. They should be inspected
directly.

Path normalization is only for environment-dependent path strings in command
output.

### Stdout/Stderr Versus File Body

Stdout and stderr are what commands print. They often include output paths or
temporary paths.

A file body is the content saved inside a file. It must remain strict because
that is where raw JSONL, config bodies, or score rows could leak.

### Why Separate Path False Positives From Content Leaks?

A path false positive is noise from the machine environment.

A content leak is a real safety problem.

The helper reduces the first without weakening detection of the second.

## 11. Related Documents

- [Forbidden-term path-safety test hardening design](forbidden_term_path_safety_test_hardening_design.md)
- [Public release checklist](public_release_checklist.md)
- [Public-safe approval existence marker design](public_safe_approval_existence_marker_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
